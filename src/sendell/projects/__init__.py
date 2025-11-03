"""
Project Management System

Discover, monitor, and manage development projects on this machine.
"""

from sendell.projects.scanner import ProjectScanner
from sendell.projects.types import ProjectType, Project, ProjectConfig

__all__ = [
    "ProjectScanner",
    "ProjectType",
    "Project",
    "ProjectConfig",
]
