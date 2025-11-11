"""
Project Manager Module

Manages VS Code projects with Claude Code integration.
Determines project states: OFFLINE (red), READY (blue), WORKING (green)
"""

from .project_states import ProjectManager, ProjectState

__all__ = ['ProjectManager', 'ProjectState']
