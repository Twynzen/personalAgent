"""
Sendell Agent Core using LangGraph.

Implements ReAct pattern agent with MCP tools.
"""

import json
from typing import Any, Dict, List, Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from sendell.agent.prompts import get_chat_mode_prompt, get_proactive_loop_prompt, get_system_prompt
from sendell.config import get_settings
from sendell.mcp.tools.conversation import respond_to_user as respond_to_user_func
from sendell.mcp.tools.monitoring import get_active_window as get_active_window_func
from sendell.mcp.tools.monitoring import get_system_health as get_system_health_func
from sendell.mcp.tools.process import list_top_processes as list_top_processes_func
from sendell.mcp.tools.process import open_application as open_application_func
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

        # Create tools list for LangGraph
        self.tools = self._create_tools()

        # Create ReAct agent with LangGraph
        self.agent = create_react_agent(
            self.llm,
            self.tools,
            prompt=get_system_prompt(),  # String convertido automaticamente a SystemMessage
        )

        logger.info("Sendell agent initialized with LangGraph ReAct pattern")

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

        @tool
        def show_brain() -> dict:
            """Open the Sendell Brain GUI to view and manage memory, prompts, and tools.

            This opens a visual interface where Daniel can:
            - View and edit learned facts about him
            - View memory statistics
            - Edit the system prompt
            - See all available tools/actions

            Use this when Daniel asks to:
            - "show me your brain"
            - "let me see your memory"
            - "open brain interface"
            - "configure your memory"
            """
            try:
                import threading
                from sendell.agent.brain_gui import show_brain as show_brain_gui

                # Run GUI in separate thread to not block agent
                gui_thread = threading.Thread(target=lambda: show_brain_gui(self.tools))
                gui_thread.daemon = True
                gui_thread.start()

                return {
                    "success": True,
                    "message": "Brain GUI opened. Check the new window to manage my memory and settings."
                }
            except Exception as e:
                logger.error(f"Failed to open brain GUI: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to open Brain GUI. Check logs for details."
                }

        return [
            get_system_health,
            get_active_window,
            list_top_processes,
            open_application,
            respond_to_user,
            show_brain,
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
