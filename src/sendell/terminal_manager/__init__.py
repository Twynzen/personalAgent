"""
Terminal Manager Module

Manages embedded terminal processes for Sendell Dashboard.
Each terminal is a subprocess.Popen instance that can be controlled
via WebSocket bidirectional communication.
"""

from sendell.terminal_manager.manager import TerminalManager, get_terminal_manager
from sendell.terminal_manager.process import ManagedTerminalProcess, ProcessState
from sendell.terminal_manager.types import (
    TerminalInfo,
    TerminalCommand,
    TerminalOutput,
    TerminalStatus
)

__all__ = [
    "TerminalManager",
    "get_terminal_manager",
    "ManagedTerminalProcess",
    "ProcessState",
    "TerminalInfo",
    "TerminalCommand",
    "TerminalOutput",
    "TerminalStatus",
]
