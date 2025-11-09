"""
VS Code Process Monitoring

Detect running VS Code instances, identify workspaces, and find terminal processes.
Based on investigation in investigacionvscodemonitoring.txt
"""

from sendell.vscode.process_detector import VSCodeMonitor, VSCodeInstance
from sendell.vscode.terminal_finder import TerminalFinder, TerminalInfo
from sendell.vscode.window_matcher import WindowMatcher
from sendell.vscode.workspace_parser import WorkspaceInfo, WorkspaceParser

__all__ = [
    "VSCodeMonitor",
    "VSCodeInstance",
    "WorkspaceParser",
    "WorkspaceInfo",
    "TerminalFinder",
    "TerminalInfo",
    "WindowMatcher",
]
