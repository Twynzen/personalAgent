"""REST API endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import psutil

from sendell.agent.memory import get_memory
from sendell.agent.prompts import get_system_prompt
from sendell.vscode import VSCodeMonitor

router = APIRouter()


# Models
class Fact(BaseModel):
    fact: str
    category: str = "general"


class PromptUpdate(BaseModel):
    prompt: str


# ==================== FACTS ====================

@router.get("/facts")
async def get_facts():
    """Get all facts from memory"""
    memory = get_memory()
    return {"facts": memory.get_facts()}


@router.post("/facts")
async def add_fact(fact: Fact):
    """Add a new fact"""
    memory = get_memory()
    memory.add_fact(fact.fact, fact.category)
    return {"success": True, "fact": fact}


@router.delete("/facts/{index}")
async def delete_fact(index: int):
    """Delete a fact by index"""
    memory = get_memory()
    memory.remove_fact(index)
    return {"success": True}


# ==================== PROMPTS ====================

@router.get("/prompts")
async def get_prompt():
    """Get current system prompt"""
    return {"prompt": get_system_prompt()}


@router.post("/prompts")
async def update_prompt(data: PromptUpdate):
    """Update system prompt (TODO: implement save)"""
    # TODO: Save to prompts.py
    return {"success": True, "prompt": data.prompt}


# ==================== TOOLS ====================

@router.get("/tools")
async def get_tools():
    """Get list of available tools"""
    from sendell.agent.core import get_agent

    try:
        agent = get_agent()
        tools_info = []

        for tool in agent.tools:
            tools_info.append({
                "name": tool.name if hasattr(tool, 'name') else str(tool),
                "description": tool.description if hasattr(tool, 'description') else "No description"
            })

        return {"tools": tools_info}
    except Exception as e:
        return {"tools": []}


# ==================== PROJECTS with STATES ====================

@router.get("/projects")
async def get_projects():
    """
    Get current VS Code projects with real-time states.

    States:
    - offline (red): Project detected, no terminal open
    - ready (blue): Terminal open, Claude active but idle
    - working (green): Terminal open, Claude active and working
    """
    from sendell.project_manager import ProjectManager

    pm = ProjectManager()
    projects = pm.get_projects_with_states()

    return {"projects": projects}


@router.post("/projects/open-terminal")
async def open_terminal(request: dict):
    """
    Open embedded terminal for project.

    Creates a managed terminal process that can be controlled via WebSocket.

    Body: {
        "workspace_path": "C:\\...\\project",
        "project_pid": 12345,
        "project_name": "sendell"
    }

    Returns: {
        "success": true,
        "terminal_id": "12345",
        "message": "Terminal created for sendell"
    }
    """
    from sendell.terminal_manager import get_terminal_manager

    workspace_path = request.get('workspace_path')
    project_pid = request.get('project_pid')
    project_name = request.get('project_name', 'Unknown')

    if not workspace_path:
        raise HTTPException(status_code=400, detail="workspace_path required")

    if not project_pid:
        raise HTTPException(status_code=400, detail="project_pid required")

    try:
        terminal_manager = get_terminal_manager()

        # Check if terminal already exists
        existing_terminal = terminal_manager.get_terminal(str(project_pid))
        if existing_terminal and existing_terminal.is_running():
            return {
                'success': True,
                'terminal_id': str(project_pid),
                'message': f'Terminal already exists for {project_name}',
                'already_exists': True
            }

        # Create new terminal
        terminal_id = terminal_manager.create_terminal(
            project_pid=project_pid,
            workspace_path=workspace_path,
            project_name=project_name
        )

        # CRITICAL: Wait for terminal to be ready before returning
        import asyncio
        import time

        terminal = terminal_manager.get_terminal(terminal_id)
        timeout = 5  # seconds
        start_time = time.time()

        while terminal and not terminal.is_running():
            if time.time() - start_time > timeout:
                raise HTTPException(status_code=500, detail="Terminal failed to start within timeout")
            await asyncio.sleep(0.1)

        if not terminal or not terminal.is_running():
            raise HTTPException(status_code=500, detail="Terminal creation failed")

        return {
            'success': True,
            'terminal_id': terminal_id,
            'message': f'Terminal created for {project_name}',
            'status': 'ready'  # Explicitly indicate terminal is ready
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/init-bridge")
async def init_bridge(request: dict):
    """
    Initialize .sendell/bridge.json file in project.

    Body: {"workspace_path": "C:\\...\\project"}
    """
    from sendell.project_manager import ProjectManager

    workspace_path = request.get('workspace_path')
    if not workspace_path:
        raise HTTPException(status_code=400, detail="workspace_path required")

    pm = ProjectManager()
    result = pm.create_bridge_file(workspace_path)

    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))

    return result


# ==================== METRICS (snapshot) ====================

@router.get("/metrics")
async def get_metrics():
    """Get system metrics (snapshot)"""
    return {
        "cpu": psutil.cpu_percent(interval=0),
        "ram": psutil.virtual_memory().percent,
        "terminals": len(VSCodeMonitor().find_vscode_instances())
    }


# ==================== CLAUDE CODE CONTROL ====================

@router.get("/claude/terminals")
async def get_claude_terminals():
    """
    Get list of detected Claude Code terminals

    Returns:
        {
            "terminals": [
                {
                    "pid": 17784,
                    "name": "node.exe",
                    "cwd": "C:/Users/Daniel/Desktop/Daniel/sendell",
                    "is_active": true,
                    "cpu_percent": 14.3,
                    "memory_mb": 474.09,
                    "status": "running"  # "running" or "idle"
                }
            ],
            "count": 5,
            "timestamp": "2025-11-10T17:00:10"
        }
    """
    from sendell.terminal_control import ClaudeTerminalDetector
    from datetime import datetime

    detector = ClaudeTerminalDetector()
    terminals = detector.find_claude_code_processes()

    return {
        "terminals": terminals,
        "count": len(terminals),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/claude/sessions")
async def get_claude_sessions():
    """
    Get active Claude Code sessions with state info

    Returns:
        {
            "sessions": [
                {
                    "project": "sendell",
                    "session_id": "abc123",
                    "state": "idle",  # idle, generating, executing_tool, error, inactive
                    "last_event_type": "assistant_message",
                    "event_count": 42,
                    "token_usage": {"input": 1000, "output": 500, "total": 1500},
                    "seconds_since_last_event": 120.5
                }
            ],
            "count": 3,
            "timestamp": "2025-11-10T17:00:10"
        }
    """
    from sendell.terminal_control import ClaudeTerminalDetector
    from datetime import datetime

    detector = ClaudeTerminalDetector()
    sessions = detector.find_active_sessions(max_age_minutes=60)

    return {
        "sessions": sessions,
        "count": len(sessions),
        "timestamp": datetime.now().isoformat()
    }


class CommandExecuteRequest(BaseModel):
    command: str
    cwd: str | None = None
    timeout: int = 30


@router.post("/claude/execute")
async def execute_command(request: CommandExecuteRequest):
    """
    Execute a command in a specific directory

    Body:
        {
            "command": "python --version",
            "cwd": "C:/Users/Daniel/Desktop/Daniel/sendell",  # optional
            "timeout": 30  # optional, seconds
        }

    Returns:
        {
            "success": true,
            "stdout": "Python 3.12.3\n",
            "stderr": "",
            "returncode": 0
        }
    """
    from sendell.terminal_control import CommandExecutor

    executor = CommandExecutor()
    result = executor.execute_simple(
        command=request.command,
        cwd=request.cwd,
        timeout=request.timeout
    )

    return result


@router.get("/claude/output/{pid}")
async def get_terminal_output(pid: int, lines: int = 50):
    """
    Get recent output from a specific Claude Code terminal

    Params:
        pid: Process ID of the Claude terminal
        lines: Number of recent lines to retrieve (default: 50)

    Returns:
        {
            "pid": 17784,
            "lines": ["line 1", "line 2", ...],
            "count": 50,
            "is_running": true
        }

    Note: This is a simplified version. Full implementation would require
          storing output in memory as terminals execute.
    """
    from sendell.terminal_control import ClaudeTerminalDetector
    import psutil

    detector = ClaudeTerminalDetector()
    terminals = detector.find_claude_code_processes()

    # Find terminal by PID
    terminal = next((t for t in terminals if t['pid'] == pid), None)

    if not terminal:
        raise HTTPException(status_code=404, detail=f"Terminal with PID {pid} not found")

    # Check if process is still running
    try:
        proc = psutil.Process(pid)
        is_running = proc.is_running()
    except psutil.NoSuchProcess:
        is_running = False

    # TODO: In real implementation, store output in memory/cache
    # For now, return metadata
    return {
        "pid": pid,
        "lines": [
            f"[Terminal output capture not yet implemented]",
            f"Terminal: {terminal['name']}",
            f"CWD: {terminal['cwd']}",
            f"Status: {'running' if is_running else 'stopped'}"
        ],
        "count": 4,
        "is_running": is_running
    }
