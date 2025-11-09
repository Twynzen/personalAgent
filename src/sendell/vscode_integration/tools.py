"""
LangChain Tools for VS Code Integration

Token-optimized tools that provide targeted information about VS Code
projects and terminals without overwhelming the LLM with excessive data.
"""

import json
import logging
from langchain_core.tools import tool

from .manager import get_manager
from .websocket_server import get_server

logger = logging.getLogger(__name__)


@tool
def list_active_projects() -> str:
    """
    List all active VS Code projects with executive summary.

    Returns compact overview of projects without detailed terminal output.
    Use this tool when user asks about projects, workspaces, or what's running.

    Returns:
        JSON string with project summaries (max ~500 tokens)

    Example output:
        [
          {
            "name": "sendell",
            "terminals": 3,
            "errors": 2,
            "has_claude_code": true,
            "last_activity": "2025-11-03T20:30:00"
          }
        ]
    """
    manager = get_manager()
    projects = manager.get_all_projects()

    if not projects:
        return json.dumps({
            "message": "No active VS Code projects found",
            "projects": []
        }, indent=2)

    summaries = []
    for project in projects:
        summaries.append(project.to_dict(include_terminals=False))

    result = {
        "total_projects": len(projects),
        "projects": summaries
    }

    return json.dumps(result, indent=2)


@tool
def get_project_errors(project_name: str, max_errors: int = 5) -> str:
    """
    Get recent errors from a specific project.

    Returns ONLY error lines, not full terminal output.
    Use this when user asks about errors, failures, or problems.

    Args:
        project_name: Name of the project (from list_active_projects)
        max_errors: Maximum errors to return (default 5, max 10)

    Returns:
        JSON string with recent errors (max ~1000 tokens)

    Example output:
        {
          "project": "sendell",
          "total_errors": 2,
          "errors": [
            {
              "terminal": "Terminal 1",
              "time": "2025-11-03T20:25:30",
              "error": "TypeError: Cannot read property 'foo' of undefined"
            }
          ]
        }
    """
    manager = get_manager()
    project = manager.get_project(project_name)

    if not project:
        return json.dumps({
            "error": f"Project '{project_name}' not found",
            "available_projects": [p.name for p in manager.get_all_projects()]
        }, indent=2)

    # Cap max_errors
    max_errors = min(max_errors, 10)

    # Get errors
    errors = project.get_all_errors(max_errors=max_errors)

    result = {
        "project": project.name,
        "total_errors": project.total_errors,
        "recent_errors": len(errors),
        "errors": [e.to_dict() for e in errors]
    }

    return json.dumps(result, indent=2)


@tool
def get_terminal_tail(
    project_name: str,
    terminal_name: str,
    lines: int = 20
) -> str:
    """
    Get last N lines from a specific terminal.

    Returns tail of terminal output, not entire history.
    Use this when user asks about specific terminal output or recent activity.

    Args:
        project_name: Name of the project
        terminal_name: Name of the terminal (e.g., "Terminal 1")
        lines: Number of lines to return (default 20, max 50)

    Returns:
        Terminal output tail (max ~2000 tokens)

    Example output:
        {
          "project": "sendell",
          "terminal": "Terminal 1",
          "lines_returned": 20,
          "last_command": "npm run dev",
          "exit_code": 0,
          "output": "...[last 20 lines]..."
        }
    """
    manager = get_manager()
    session = manager.get_terminal(project_name, terminal_name)

    if not session:
        # Try to find available terminals
        project = manager.get_project(project_name)
        if project:
            available = list(project.terminals.keys())
            return json.dumps({
                "error": f"Terminal '{terminal_name}' not found in project '{project_name}'",
                "available_terminals": available
            }, indent=2)
        else:
            return json.dumps({
                "error": f"Project '{project_name}' not found"
            }, indent=2)

    # Cap lines
    lines = min(lines, 50)

    # Get tail
    tail = session.get_tail(lines)

    result = {
        "project": project_name,
        "terminal": terminal_name,
        "lines_returned": len(tail.split('\n')),
        "last_command": session.last_command,
        "exit_code": session.last_exit_code,
        "is_dev_server": session.is_dev_server,
        "is_claude_code": session.is_claude_code,
        "output": tail
    }

    return json.dumps(result, indent=2)


@tool
def get_project_stats(project_name: str) -> str:
    """
    Get statistics for a project (numbers only, no text).

    Returns aggregated stats without terminal output.
    Use this when user asks about project status, activity, or overview.

    Args:
        project_name: Name of the project

    Returns:
        JSON string with statistics (max ~300 tokens)

    Example output:
        {
          "name": "sendell",
          "stats": {
            "terminals": 3,
            "commands": 45,
            "errors": 2
          },
          "has_claude_code": true,
          "terminals": [
            {
              "name": "Terminal 1",
              "last_command": "npm run dev",
              "exit_code": 0,
              "errors": 1,
              "is_dev_server": true
            }
          ]
        }
    """
    manager = get_manager()
    project = manager.get_project(project_name)

    if not project:
        return json.dumps({
            "error": f"Project '{project_name}' not found",
            "available_projects": [p.name for p in manager.get_all_projects()]
        }, indent=2)

    # Get full project dict with terminal details
    result = project.to_dict(include_terminals=True)

    return json.dumps(result, indent=2)


@tool
def send_terminal_command(
    project_name: str,
    terminal_name: str,
    command: str
) -> str:
    """
    Send a command to a specific terminal in VS Code.

    REQUIRES L3+ AUTONOMY LEVEL.
    Use this when user explicitly asks to run a command in a terminal.

    Args:
        project_name: Name of the project
        terminal_name: Name of the terminal
        command: Command to execute

    Returns:
        JSON confirmation or error

    Example:
        send_terminal_command("sendell", "Terminal 1", "npm test")
    """
    import asyncio

    # Verify terminal exists
    manager = get_manager()
    session = manager.get_terminal(project_name, terminal_name)

    if not session:
        return json.dumps({
            "success": False,
            "error": f"Terminal '{terminal_name}' not found in '{project_name}'"
        }, indent=2)

    # Send command via WebSocket server
    server = get_server()

    try:
        # Create async task to send command
        loop = asyncio.get_event_loop()
        success = loop.run_until_complete(
            server.send_command_to_terminal(project_name, terminal_name, command)
        )

        if success:
            logger.info(f"Sent command to {project_name}/{terminal_name}: {command}")
            return json.dumps({
                "success": True,
                "project": project_name,
                "terminal": terminal_name,
                "command": command
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": "Failed to send command (no VS Code connection?)"
            }, indent=2)

    except Exception as e:
        logger.error(f"Error sending command: {e}", exc_info=True)
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


# Tool list for easy import
VSCODE_TOOLS = [
    list_active_projects,
    get_project_errors,
    get_terminal_tail,
    get_project_stats,
    send_terminal_command,
]
