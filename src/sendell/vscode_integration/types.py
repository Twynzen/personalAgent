"""
Type definitions for VS Code integration

Memory-efficient data structures with automatic eviction.
"""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Deque, List, Dict, Optional


@dataclass
class ErrorEvent:
    """
    Represents a single error detected in terminal output.

    Stored for quick error lookup without keeping full terminal history.
    """
    timestamp: datetime
    line: str  # Max 200 chars
    terminal: str
    workspace: str

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'line': self.line[:200],  # Cap at 200 chars
            'terminal': self.terminal,
            'workspace': self.workspace,
        }


@dataclass
class TerminalSession:
    """
    Represents a single terminal session within a workspace.

    Uses deque with maxlen for automatic FIFO eviction of old lines.
    Only stores recent data to minimize memory usage.
    """
    workspace: str
    name: str

    # Tail buffer: Only last 20 lines (auto-evicts old ones)
    tail_buffer: Deque[str] = field(default_factory=lambda: deque(maxlen=20))

    # Recent errors: Only last 5 errors
    recent_errors: List[ErrorEvent] = field(default_factory=list)

    # Metadata
    last_command: str = ""
    last_exit_code: int = 0
    is_dev_server: bool = False  # npm run dev, vite, webpack-dev-server, etc.
    is_claude_code: bool = False  # Detected Claude Code session
    last_activity: datetime = field(default_factory=datetime.now)

    # Statistics (counters only, no text storage)
    total_commands: int = 0
    total_errors: int = 0
    total_output_lines: int = 0  # For monitoring, not storage

    def add_output(self, output: str) -> None:
        """
        Add output to tail buffer.

        Only stores last 20 lines automatically (deque maxlen).
        """
        lines = output.split('\n')
        for line in lines:
            if line.strip():  # Ignore empty lines
                self.tail_buffer.append(line)
                self.total_output_lines += 1

        self.last_activity = datetime.now()

    def add_error(self, error_line: str) -> None:
        """
        Add error to recent errors list.

        Keeps only last 5 errors to minimize memory.
        """
        error = ErrorEvent(
            timestamp=datetime.now(),
            line=error_line[:200],  # Cap at 200 chars
            terminal=self.name,
            workspace=self.workspace,
        )

        self.recent_errors.append(error)

        # Keep only last 5 errors
        if len(self.recent_errors) > 5:
            self.recent_errors.pop(0)

        self.total_errors += 1
        self.last_activity = datetime.now()

    def get_tail(self, lines: int = 20) -> str:
        """Get last N lines from tail buffer"""
        lines = min(lines, 50)  # Cap at 50
        tail_lines = list(self.tail_buffer)[-lines:]
        return '\n'.join(tail_lines)

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict (compact)"""
        return {
            'name': self.name,
            'last_command': self.last_command[:100],  # Cap
            'exit_code': self.last_exit_code,
            'is_dev_server': self.is_dev_server,
            'is_claude_code': self.is_claude_code,
            'last_activity': self.last_activity.isoformat(),
            'stats': {
                'commands': self.total_commands,
                'errors': self.total_errors,
                'output_lines': self.total_output_lines,
            },
        }


@dataclass
class ProjectContext:
    """
    Represents a VS Code workspace with multiple terminals.

    Aggregates information from all terminals in the workspace.
    """
    workspace_path: str
    name: str

    # Active terminals (key: terminal name)
    terminals: Dict[str, TerminalSession] = field(default_factory=dict)

    # Aggregated stats (no text storage)
    total_terminals: int = 0
    total_errors: int = 0
    total_commands: int = 0
    has_claude_code: bool = False

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

    def add_terminal(self, terminal_name: str) -> TerminalSession:
        """Add or get terminal session"""
        if terminal_name not in self.terminals:
            self.terminals[terminal_name] = TerminalSession(
                workspace=self.name,
                name=terminal_name,
            )
            self.total_terminals = len(self.terminals)

        self.last_activity = datetime.now()
        return self.terminals[terminal_name]

    def get_terminal(self, terminal_name: str) -> Optional[TerminalSession]:
        """Get terminal by name"""
        return self.terminals.get(terminal_name)

    def remove_terminal(self, terminal_name: str) -> None:
        """Remove closed terminal"""
        if terminal_name in self.terminals:
            del self.terminals[terminal_name]
            self.total_terminals = len(self.terminals)
            self.last_activity = datetime.now()

    def update_stats(self) -> None:
        """Recalculate aggregated stats from terminals"""
        self.total_errors = sum(t.total_errors for t in self.terminals.values())
        self.total_commands = sum(t.total_commands for t in self.terminals.values())
        self.has_claude_code = any(t.is_claude_code for t in self.terminals.values())

    def get_all_errors(self, max_errors: int = 10) -> List[ErrorEvent]:
        """Get recent errors from all terminals"""
        all_errors = []
        for terminal in self.terminals.values():
            all_errors.extend(terminal.recent_errors)

        # Sort by timestamp, most recent first
        all_errors.sort(key=lambda e: e.timestamp, reverse=True)

        return all_errors[:max_errors]

    def to_dict(self, include_terminals: bool = False) -> dict:
        """
        Convert to JSON-serializable dict.

        Args:
            include_terminals: Include detailed terminal info (increases size)
        """
        result = {
            'name': self.name,
            'path': self.workspace_path,
            'stats': {
                'terminals': self.total_terminals,
                'commands': self.total_commands,
                'errors': self.total_errors,
            },
            'has_claude_code': self.has_claude_code,
            'last_activity': self.last_activity.isoformat(),
        }

        if include_terminals:
            result['terminals'] = [t.to_dict() for t in self.terminals.values()]

        return result


@dataclass
class VSCodeEvent:
    """
    Represents an event from VS Code extension.

    Used for WebSocket message parsing.
    """
    id: str
    type: str  # 'event', 'request', 'response'
    category: str  # 'terminal', 'file', 'git', 'diagnostic', 'claude', 'system'
    payload: dict
    timestamp: int

    @classmethod
    def from_dict(cls, data: dict) -> 'VSCodeEvent':
        """Parse from WebSocket message"""
        return cls(
            id=data['id'],
            type=data['type'],
            category=data['category'],
            payload=data['payload'],
            timestamp=data['timestamp'],
        )

    def to_dict(self) -> dict:
        """Convert to WebSocket message"""
        return {
            'id': self.id,
            'type': self.type,
            'category': self.category,
            'payload': self.payload,
            'timestamp': self.timestamp,
        }
