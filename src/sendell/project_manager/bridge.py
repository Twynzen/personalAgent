"""
Bridge.json Management

Handles creation, reading, and updating of .sendell/bridge.json files
for project-level state communication between Sendell and Claude Code.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Literal
from datetime import datetime

from sendell.utils.logger import get_logger

logger = get_logger(__name__)

TerminalStatus = Literal['idle', 'working', 'error']


def get_bridge_path(workspace_path: str) -> Path:
    """
    Get path to bridge.json for a workspace.

    Args:
        workspace_path: Project workspace directory

    Returns:
        Path to .sendell/bridge.json
    """
    return Path(workspace_path) / '.sendell' / 'bridge.json'


def ensure_sendell_dir(workspace_path: str) -> Path:
    """
    Ensure .sendell directory exists in workspace.

    Args:
        workspace_path: Project workspace directory

    Returns:
        Path to .sendell directory
    """
    sendell_dir = Path(workspace_path) / '.sendell'
    sendell_dir.mkdir(exist_ok=True)
    return sendell_dir


def create_bridge_file(workspace_path: str, project_name: str = "Unknown") -> Dict:
    """
    Create bridge.json with initial state.

    Creates .sendell/bridge.json with default values.
    Safe to call multiple times - will not overwrite existing file.

    Args:
        workspace_path: Project workspace directory
        project_name: Name of the project

    Returns:
        {'success': bool, 'path': str, 'created': bool}
    """
    try:
        ensure_sendell_dir(workspace_path)
        bridge_path = get_bridge_path(workspace_path)

        # If file exists, don't overwrite
        if bridge_path.exists():
            logger.debug(f"Bridge file already exists: {bridge_path}")
            return {
                'success': True,
                'path': str(bridge_path),
                'created': False
            }

        # Create initial bridge data
        initial_data = {
            "_readme": "🤖 This file enables Sendell ↔ Claude Code collaboration. Claude: you can read 'task_request' and update 'status' to communicate progress.",

            "project_path": workspace_path,
            "project_name": project_name,

            "terminal_status": "idle",
            "current_task": None,
            "last_command": None,
            "last_updated": datetime.now().isoformat(),

            "task_request": None,
            "sendell_notes": "You can communicate with Sendell by updating this file",

            "claude_active": False,
            "claude_last_seen": None
        }

        # Write file
        with open(bridge_path, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Created bridge file: {bridge_path}")

        return {
            'success': True,
            'path': str(bridge_path),
            'created': True
        }

    except Exception as e:
        logger.error(f"Error creating bridge file: {e}")
        return {
            'success': False,
            'error': str(e),
            'created': False
        }


def read_bridge_file(workspace_path: str) -> Optional[Dict]:
    """
    Read bridge.json from workspace.

    Args:
        workspace_path: Project workspace directory

    Returns:
        Bridge data dict or None if file doesn't exist or error
    """
    try:
        bridge_path = get_bridge_path(workspace_path)

        if not bridge_path.exists():
            return None

        with open(bridge_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data

    except Exception as e:
        logger.error(f"Error reading bridge file: {e}")
        return None


def update_bridge_file(
    workspace_path: str,
    terminal_status: Optional[TerminalStatus] = None,
    current_task: Optional[str] = None,
    last_command: Optional[str] = None,
    task_request: Optional[str] = None,
    sendell_notes: Optional[str] = None,
    claude_active: Optional[bool] = None
) -> bool:
    """
    Update bridge.json with new values.

    Only updates fields that are provided (not None).
    Automatically updates 'last_updated' timestamp.

    Args:
        workspace_path: Project workspace directory
        terminal_status: 'idle', 'working', or 'error'
        current_task: Description of current task
        last_command: Last command executed
        task_request: Task request from Sendell to Claude
        sendell_notes: Notes from Sendell
        claude_active: Whether Claude Code is active

    Returns:
        True if successful, False otherwise
    """
    try:
        bridge_path = get_bridge_path(workspace_path)

        # Read existing data or create new
        if bridge_path.exists():
            with open(bridge_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            # Create with defaults if doesn't exist
            create_result = create_bridge_file(workspace_path)
            if not create_result['success']:
                return False
            with open(bridge_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

        # Update fields that were provided
        if terminal_status is not None:
            data['terminal_status'] = terminal_status
        if current_task is not None:
            data['current_task'] = current_task
        if last_command is not None:
            data['last_command'] = last_command
        if task_request is not None:
            data['task_request'] = task_request
        if sendell_notes is not None:
            data['sendell_notes'] = sendell_notes
        if claude_active is not None:
            data['claude_active'] = claude_active
            if claude_active:
                data['claude_last_seen'] = datetime.now().isoformat()

        # Always update timestamp
        data['last_updated'] = datetime.now().isoformat()

        # Write back
        with open(bridge_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.debug(f"Updated bridge file: {bridge_path}")
        return True

    except Exception as e:
        logger.error(f"Error updating bridge file: {e}")
        return False


def get_terminal_status(workspace_path: str) -> TerminalStatus:
    """
    Get terminal status from bridge.json.

    Args:
        workspace_path: Project workspace directory

    Returns:
        Terminal status ('idle', 'working', or 'error')
        Defaults to 'idle' if file doesn't exist or error
    """
    data = read_bridge_file(workspace_path)

    if not data:
        return 'idle'

    return data.get('terminal_status', 'idle')


def set_terminal_idle(workspace_path: str) -> bool:
    """
    Set terminal status to idle.

    Convenience function for marking terminal as idle.
    Called when terminal closes or command finishes.

    Args:
        workspace_path: Project workspace directory

    Returns:
        True if successful
    """
    return update_bridge_file(
        workspace_path,
        terminal_status='idle',
        current_task=None
    )


def set_terminal_working(workspace_path: str, task_description: str = "Executing command") -> bool:
    """
    Set terminal status to working.

    Convenience function for marking terminal as actively working.

    Args:
        workspace_path: Project workspace directory
        task_description: Description of what's being done

    Returns:
        True if successful
    """
    return update_bridge_file(
        workspace_path,
        terminal_status='working',
        current_task=task_description
    )
