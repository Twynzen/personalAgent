"""
Terminal Control Module

Provides detection and control of Claude Code terminals running in VS Code.
Based on research from investigacionterminalsguide.txt (95%+ reliability).
"""

from .detector import ClaudeTerminalDetector
from .executor import CommandExecutor

__all__ = [
    'ClaudeTerminalDetector',
    'CommandExecutor',
]
