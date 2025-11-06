"""
VS Code Process Monitoring

Detect running VS Code instances and identify their open workspaces.
Uses terminal processes internally to detect workspaces (not exposed in API).
"""

from sendell.vscode.process_detector import VSCodeMonitor, VSCodeInstance
from sendell.vscode.workspace_parser import WorkspaceInfo, WorkspaceParser

__all__ = [
    "VSCodeMonitor",
    "VSCodeInstance",
    "WorkspaceParser",
    "WorkspaceInfo",
]
