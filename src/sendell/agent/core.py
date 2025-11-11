"""
Sendell Agent Core using LangGraph.

Implements ReAct pattern agent with MCP tools.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from sendell.agent.memory import get_memory
from sendell.agent.prompts import get_chat_mode_prompt, get_proactive_loop_prompt, get_system_prompt
from sendell.config import get_settings
from sendell.mcp.tools.conversation import respond_to_user as respond_to_user_func
from sendell.mcp.tools.monitoring import get_active_window as get_active_window_func
from sendell.mcp.tools.monitoring import get_system_health as get_system_health_func
from sendell.mcp.tools.process import list_top_processes as list_top_processes_func
from sendell.mcp.tools.process import open_application as open_application_func
from sendell.proactive.identity import AgentIdentity
from sendell.proactive.proactive_loop import ProactiveLoop
from sendell.proactive.reminders import Reminder, ReminderManager, ReminderType
from sendell.proactive.temporal_clock import TemporalClock
from sendell.utils.logger import get_logger

logger = get_logger(__name__)


class SendellAgent:
    """
    Sendell autonomous agent using LangGraph.

    Uses ReAct pattern with MCP tools for system monitoring and control.
    """

    def __init__(self):
        """Initialize Sendell agent"""
        self.settings = get_settings()

        # Initialize OpenAI LLM
        self.llm = ChatOpenAI(
            api_key=self.settings.openai.api_key.get_secret_value(),
            model=self.settings.openai.model,
            temperature=self.settings.openai.temperature,
            max_tokens=self.settings.openai.max_tokens,
        )

        # Initialize memory system
        self.memory = get_memory()

        # Initialize or load agent identity
        if self.memory.has_agent_identity():
            identity_data = self.memory.get_agent_identity()
            self.identity = AgentIdentity.from_dict(identity_data)
            logger.info(f"Agent identity loaded: {self.identity.relationship_age_days} days old")
        else:
            # First time - create new identity
            self.identity = AgentIdentity(user_name=None)
            self.memory.set_agent_identity(self.identity.to_dict())
            logger.info("New agent identity created - this is my birth!")

        # Initialize temporal clock
        self.temporal_clock = TemporalClock()

        # Initialize reminder manager
        self.reminder_manager = ReminderManager()
        reminders_data = self.memory.get_reminders()
        if reminders_data:
            self.reminder_manager = ReminderManager.from_dict({"reminders": reminders_data})
            logger.info(f"Loaded {len(reminders_data)} reminders from memory")

        # Initialize proactive loop (don't auto-start)
        self.proactive_loop = ProactiveLoop(
            identity=self.identity,
            reminder_manager=self.reminder_manager,
            temporal_clock=self.temporal_clock,
            check_interval_seconds=60,  # Check every 60 seconds
            on_reminder_callback=self._on_reminder_triggered,
        )

        # Create tools list for LangGraph
        self.tools = self._create_tools()

        # Create ReAct agent with LangGraph
        self.agent = create_react_agent(
            self.llm,
            self.tools,
            prompt=get_system_prompt(),  # String convertido automaticamente a SystemMessage
        )

        logger.info("Sendell agent initialized with LangGraph ReAct pattern + Proactive System")

    def _create_tools(self) -> List:
        """
        Create LangChain tools from MCP functions.

        Returns:
            List of LangChain Tool objects
        """
        from langchain_core.tools import tool

        @tool
        def get_system_health() -> dict:
            """Get current system health metrics including CPU, RAM, and disk usage.
            Returns percentages and detects if any thresholds are exceeded.
            This is a read-only operation, safe to call frequently."""
            return get_system_health_func()

        @tool
        def get_active_window() -> dict:
            """Get information about the currently active window.
            Returns window title, process name, and PID.
            Useful for understanding user context.
            Respects privacy settings (blocked apps)."""
            return get_active_window_func()

        @tool
        def list_top_processes(n: int = 10, sort_by: str = "memory") -> dict:
            """List top N processes by resource usage (CPU or memory).
            Useful for identifying resource hogs and potential issues.
            Returns process name, PID, CPU%, memory usage.

            Args:
                n: Number of processes to return (1-100), defaults to 10
                sort_by: Sort by 'memory' or 'cpu', defaults to 'memory'
            """
            return list_top_processes_func(n=n, sort_by=sort_by)

        @tool
        def open_application(app_name: str, args: Optional[List[str]] = None) -> dict:
            """Open an application by name or path.
            Supports common apps like 'notepad', 'chrome', 'vscode', etc.
            Requires L3+ autonomy level.
            Respects blocked apps from privacy settings.

            Args:
                app_name: Application name or path to open
                args: Optional command-line arguments as a list
            """
            return open_application_func(app_name=app_name, args=args)

        @tool
        def respond_to_user(message: str, requires_approval: bool = False) -> dict:
            """Send a message to the user.
            Use this to communicate proactively about findings, suggestions, or requests.
            Set requires_approval=true if you need user confirmation for an action.

            Args:
                message: Message to send to user
                requires_approval: If true, message requests user action/approval
            """
            return respond_to_user_func(message=message, requires_approval=requires_approval)

        # NOTE: show_brain tool removed - replaced by open_dashboard (web interface)
        # The Angular dashboard at http://localhost:8765 now handles all GUI functionality

        @tool
        async def add_reminder(content: str, minutes_from_now: int, actions: str = "visual_notification") -> dict:
            """Add a personal reminder that will trigger at a specific time.

            This creates a reminder that will execute one or more actions when the time arrives.
            The proactive loop monitors reminders and triggers them automatically.

            Args:
                content: What to remind about (e.g., "call grandma", "take a break")
                minutes_from_now: How many minutes from now to trigger (e.g., 30, 60, 120)
                actions: Comma-separated action types:
                    - visual_notification: Rich visual window with animated ASCII art (RECOMMENDED, default)
                    - chat_message: Send message in chat
                    - popup: Simple Windows toast notification (legacy)
                    - notepad: Open notepad with message (legacy)
                    - sound: Play notification sound
                    Example: "visual_notification" or "visual_notification,sound"

            Examples:
                - "Remind me to call in 30 minutes" -> add_reminder("call", 30)
                  (Uses visual_notification by default - shows animated window with ASCII art)
                - "Remind me to take a break in 60 minutes" -> add_reminder("take a break", 60)
                  (Visual notification with auto-selected ASCII art based on content)
                - "Remind me to check project in 2 minutes" -> add_reminder("check project", 2)
                  (Urgency automatically detected, shows appropriate colors/sounds)

            Returns:
                dict: Success status, reminder details, and trigger time
            """
            try:
                # Parse actions
                actions_list = [a.strip() for a in actions.split(",")]

                # Create reminder using agent's method
                reminder = await self.add_reminder_from_chat(content, minutes_from_now, actions_list)

                # Format response
                due_time = reminder.due_at.strftime("%I:%M %p")

                return {
                    "success": True,
                    "message": f"Reminder set: '{content}' at {due_time} (in {minutes_from_now} min) with actions: {actions_list}",
                    "reminder_id": reminder.reminder_id,
                    "due_at": reminder.due_at.isoformat(),
                    "actions": actions_list,
                }
            except Exception as e:
                logger.error(f"Failed to add reminder: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "message": f"Failed to create reminder: {str(e)}"
                }

        @tool
        def list_vscode_instances() -> dict:
            """List all running VS Code instances with their open projects.

            Detects VS Code processes (stable, Insiders, VSCodium, Cursor) and extracts:
            - Which workspace/project is open
            - Full path to the project folder

            This allows you to understand Daniel's active development context.

            Returns:
                dict with:
                - success: bool
                - instances_found: int (number of VS Code windows)
                - instances: list of instance details with:
                    - pid: VS Code process ID
                    - executable: VS Code executable name
                    - workspace_name: Name of open project
                    - workspace_path: Full path to project
                    - workspace_type: 'folder', 'workspace', or 'none'

            Examples:
                - "What VS Code projects are open?"
                - "Show me my active projects"
                - "What am I working on right now?"

            Use Cases:
                - Understand user's current work context
                - Detect which projects are being worked on
                - Help user navigate between projects
            """
            try:
                from sendell.vscode import VSCodeMonitor

                monitor = VSCodeMonitor()
                instances = monitor.find_vscode_instances()

                # Format instances for response
                instances_list = []

                for instance in instances:
                    # Format instance
                    instance_info = {
                        "pid": instance.pid,
                        "executable": instance.name,
                        "is_insiders": instance.is_insiders,
                        "workspace_type": instance.workspace.workspace_type,
                        "workspace_name": instance.workspace.workspace_name,
                        "workspace_path": instance.workspace.workspace_path,
                    }

                    # Add multi-root workspace info if applicable
                    if instance.workspace.workspace_file:
                        instance_info["workspace_file"] = instance.workspace.workspace_file
                        if instance.workspace.folders:
                            instance_info["folders"] = instance.workspace.folders

                    instances_list.append(instance_info)

                return {
                    "success": True,
                    "instances_found": len(instances),
                    "instances": instances_list,
                    "message": f"Found {len(instances)} VS Code instance(s)",
                }

            except Exception as e:
                logger.error(f"Failed to list VS Code instances: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "message": f"Failed to detect VS Code: {str(e)}"
                }

        @tool
        def open_dashboard() -> dict:
            """Open the Sendell Cerebro web dashboard in the default browser.

            This opens a visual web interface where Daniel can:
            - See all active VS Code projects
            - View project states (OFFLINE/READY/WORKING)
            - Open embedded terminals for each project
            - Monitor system metrics (CPU, RAM, terminals count)
            - View Claude Code terminals
            - Access real-time activity graphs

            The dashboard provides a comprehensive view of all development projects
            and allows direct interaction with terminals through the web interface.

            Use this when Daniel asks to:
            - "open dashboard" / "abre el dashboard"
            - "show cerebro" / "muestra el cerebro"
            - "let me see my projects" / "muéstrame mis proyectos"
            - "open the visual interface" / "abre la interfaz visual"
            - "show me the web interface" / "muestra la interfaz web"

            Note: The dashboard server must be running (port 8765).
            If not running, it will attempt to auto-start.

            Returns:
                dict: Success status and dashboard URL
            """
            import webbrowser
            import socket
            import subprocess
            import os
            import time

            def is_server_running():
                """Check if server is running on port 8765"""
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(1)
                        result = s.connect_ex(('localhost', 8765))
                        return result == 0
                except:
                    return False

            dashboard_url = "http://localhost:8765"

            try:
                # Check if server is running
                if not is_server_running():
                    logger.info("Dashboard server not running, attempting to start...")

                    # Start server in background
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

                    # Use CREATE_NO_WINDOW flag to hide cmd window
                    if os.name == 'nt':  # Windows
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        startupinfo.wShowWindow = subprocess.SW_HIDE

                        subprocess.Popen(
                            ["uv", "run", "uvicorn", "sendell.web.server:app", "--port", "8765"],
                            cwd=project_root,
                            startupinfo=startupinfo,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                    else:  # Linux/Mac
                        subprocess.Popen(
                            ["uv", "run", "uvicorn", "sendell.web.server:app", "--port", "8765"],
                            cwd=project_root,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )

                    # Wait for server to start (with retry logic)
                    max_retries = 15  # 15 seconds total
                    for i in range(max_retries):
                        time.sleep(1)
                        if is_server_running():
                            break

                    # Final verify
                    if not is_server_running():
                        return {
                            "success": False,
                            "error": "Server failed to start within 15 seconds",
                            "message": "Dashboard server failed to start. Please start manually with: uv run uvicorn sendell.web.server:app --port 8765"
                        }

                    logger.info("Dashboard server started successfully")

                # Open browser
                webbrowser.open(dashboard_url)

                return {
                    "success": True,
                    "url": dashboard_url,
                    "message": f"Dashboard opened in browser at {dashboard_url}"
                }

            except Exception as e:
                logger.error(f"Failed to open dashboard: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "message": f"Failed to open dashboard: {str(e)}"
                }

        return [
            get_system_health,
            get_active_window,
            list_top_processes,
            open_application,
            respond_to_user,
            add_reminder,
            list_vscode_instances,
            open_dashboard,  # Web dashboard replaces old show_brain GUI
        ]


    async def run_proactive_cycle(self) -> dict:
        """
        Run one proactive monitoring cycle (OODA loop).

        Observe -> Orient -> Decide -> Act

        Returns:
            Dict with cycle results and any actions taken
        """
        logger.info("Running proactive monitoring cycle")

        try:
            # Inject proactive loop prompt
            messages = [
                HumanMessage(content=get_proactive_loop_prompt()),
            ]

            # Run agent
            result = await self.agent.ainvoke({"messages": messages})

            # Extract messages from result
            output_messages = result.get("messages", [])

            # Log cycle completion
            logger.info(f"Proactive cycle completed with {len(output_messages)} messages")

            return {
                "success": True,
                "messages": output_messages,
                "cycle_type": "proactive",
            }

        except Exception as e:
            logger.error(f"Proactive cycle failed: {e}")
            return {"success": False, "error": str(e), "cycle_type": "proactive"}

    async def chat(self, user_message: str, conversation_history: Optional[List] = None) -> dict:
        """
        Handle interactive chat with user.

        Args:
            user_message: User's message
            conversation_history: Previous messages (optional)

        Returns:
            Dict with agent response and updated conversation
        """
        logger.info(f"Processing chat message: {user_message[:50]}...")

        try:
            # Build message list
            messages = []

            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)

            # Add current user message
            messages.append(HumanMessage(content=user_message))

            # Run agent
            result = await self.agent.ainvoke({"messages": messages})

            # Extract response
            output_messages = result.get("messages", [])

            # Get last AI message as response
            response = None
            for msg in reversed(output_messages):
                if isinstance(msg, AIMessage):
                    response = msg.content
                    break

            if not response:
                response = "I processed your request but don't have a direct response."

            logger.info("Chat message processed successfully")

            return {
                "success": True,
                "response": response,
                "messages": output_messages,
                "conversation_history": messages + output_messages,
            }

        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": f"Sorry, I encountered an error: {str(e)}",
            }

    async def execute_command(self, command: str) -> dict:
        """
        Execute a direct command (no chat, just action).

        Args:
            command: Command to execute (e.g., "check health", "open notepad")

        Returns:
            Dict with execution result
        """
        logger.info(f"Executing command: {command}")

        try:
            # Map common commands to direct tool calls
            if command.lower() in ["check health", "system health", "health"]:
                result = get_system_health_func()
                return {"success": True, "command": command, "result": result}

            elif command.lower() in ["active window", "current window"]:
                result = get_active_window_func()
                return {"success": True, "command": command, "result": result}

            elif command.lower().startswith("open "):
                app_name = command[5:].strip()
                result = open_application_func(app_name=app_name)
                return {"success": True, "command": command, "result": result}

            else:
                # For complex commands, use chat mode
                result = await self.chat(command)
                return result

        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {"success": False, "error": str(e), "command": command}

    async def add_reminder_from_chat(
        self, content: str, minutes_from_now: int, actions: Optional[List[str]] = None
    ) -> Reminder:
        """
        Add reminder from chat conversation.

        Args:
            content: What to remind about
            minutes_from_now: Minutes from now to trigger
            actions: List of action types (visual_notification, chat_message, popup, notepad, sound)

        Returns:
            Reminder: The created reminder
        """
        if actions is None:
            actions = ["visual_notification"]

        due_at = datetime.now() + timedelta(minutes=minutes_from_now)

        # Auto-detect importance based on keywords in content
        importance = self._calculate_reminder_importance(content, minutes_from_now)

        reminder = Reminder(
            content=content,
            reminder_type=ReminderType.ONE_TIME,
            due_at=due_at,
            actions=actions,
            importance=importance,
        )

        self.reminder_manager.add_reminder(reminder)
        self.memory.set_reminders(self.reminder_manager.to_dict()["reminders"])

        logger.debug(f"Reminder added: {content} at {due_at.strftime('%I:%M %p')} (importance: {importance})")

        return reminder

    def _calculate_reminder_importance(self, content: str, minutes_from_now: int) -> float:
        """
        Calculate importance level based on content and timing.

        Args:
            content: Reminder content
            minutes_from_now: Minutes until reminder triggers

        Returns:
            float: Importance level 0.0-1.0
        """
        content_lower = content.lower()
        importance = 0.5  # Default medium

        # High importance keywords
        high_importance_keywords = [
            "urgent", "important", "critical", "asap", "immediately",
            "deadline", "meeting", "appointment", "call", "urgente",
            "importante", "critico", "reunion", "cita"
        ]

        # Medium-high importance keywords
        medium_high_keywords = [
            "remember", "don't forget", "make sure", "check", "review",
            "recordar", "no olvides", "revisar", "verificar"
        ]

        # Check for high importance
        if any(keyword in content_lower for keyword in high_importance_keywords):
            importance = 0.85

        # Check for medium-high importance
        elif any(keyword in content_lower for keyword in medium_high_keywords):
            importance = 0.65

        # Adjust based on timing (sooner = more important)
        if minutes_from_now <= 5:
            importance = min(1.0, importance + 0.15)  # Very soon = boost importance
        elif minutes_from_now <= 15:
            importance = min(1.0, importance + 0.10)
        elif minutes_from_now >= 240:  # 4+ hours
            importance = max(0.3, importance - 0.15)  # Far away = reduce importance

        return round(importance, 2)

    async def _on_reminder_triggered(self, reminder: Reminder, results: List[Dict]) -> None:
        """
        Callback when a reminder is triggered by the proactive loop.

        Args:
            reminder: The reminder that was triggered
            results: Results from executing the reminder actions
        """
        logger.debug(f"Reminder triggered callback: {reminder.content}")

        # Save updated reminder state to memory
        self.memory.set_reminders(self.reminder_manager.to_dict()["reminders"])

        # Log action results (only errors)
        for result in results:
            if not result["success"]:
                logger.warning(f"Reminder action failed: {result['action']} - {result.get('error')}")

    def get_proactive_status(self) -> dict:
        """
        Get status of proactive system.

        Returns:
            dict: Agent identity, loop status, upcoming reminders
        """
        return {
            "identity": {
                "age_days": self.identity.relationship_age_days,
                "phase": self.identity.relationship_phase.value,
                "confidence": self.identity.confidence_level,
            },
            "loop": self.proactive_loop.get_status(),
            "reminders": {
                "total": len(self.reminder_manager.get_all_reminders()),
                "due": len(self.reminder_manager.get_due_reminders()),
                "upcoming_24h": len(self.reminder_manager.get_upcoming_reminders(hours=24)),
            },
        }


# Global agent instance (singleton)
_agent: Optional[SendellAgent] = None


def get_agent() -> SendellAgent:
    """
    Get or create global Sendell agent instance.

    Returns:
        SendellAgent instance
    """
    global _agent
    if _agent is None:
        _agent = SendellAgent()
    return _agent
