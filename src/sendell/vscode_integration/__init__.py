"""
VS Code Integration Module

Deep integration with VS Code via WebSocket for multi-project management.
Optimized for minimal token usage and memory efficiency.
"""

from .types import ErrorEvent, TerminalSession, ProjectContext
from .manager import VSCodeIntegrationManager
from .websocket_server import VSCodeWebSocketServer
from .tools import (
    list_active_projects,
    get_project_errors,
    get_terminal_tail,
    get_project_stats,
)

__all__ = [
    'ErrorEvent',
    'TerminalSession',
    'ProjectContext',
    'VSCodeIntegrationManager',
    'VSCodeWebSocketServer',
    'list_active_projects',
    'get_project_errors',
    'get_terminal_tail',
    'get_project_stats',
]
