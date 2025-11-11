"""
Terminal Manager

Singleton manager for all terminal processes.
Coordinates terminal lifecycle and output broadcasting.
"""

from typing import Dict, Optional, List, Callable
from datetime import datetime

from sendell.terminal_manager.process import ManagedTerminalProcess
from sendell.terminal_manager.types import TerminalInfo, TerminalOutput, TerminalStatus, ProcessState
from sendell.utils.logger import get_logger

logger = get_logger(__name__)


class TerminalManager:
    """
    Singleton manager for all terminal processes.

    Maintains registry of active terminals and coordinates with WebSocket
    for real-time I/O communication.
    """

    _instance: Optional['TerminalManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.terminals: Dict[str, ManagedTerminalProcess] = {}
        self.output_callbacks: List[Callable[[TerminalOutput], None]] = []
        self._initialized = True

        logger.info("TerminalManager initialized")

    def register_output_callback(self, callback: Callable[[TerminalOutput], None]):
        """
        Register callback for terminal output.

        Callback will be called for every line of output from any terminal.
        Typically used to broadcast via WebSocket.

        Args:
            callback: Function that takes TerminalOutput
        """
        self.output_callbacks.append(callback)
        logger.debug(f"Registered output callback, total: {len(self.output_callbacks)}")

    def _broadcast_output(self, output: TerminalOutput):
        """Broadcast output to all registered callbacks"""
        for callback in self.output_callbacks:
            try:
                callback(output)
            except Exception as e:
                logger.error(f"Error in output callback: {e}")

    def create_terminal(
        self,
        project_pid: int,
        workspace_path: str,
        project_name: str
    ) -> str:
        """
        Create new terminal process.

        Args:
            project_pid: VS Code project PID (used as terminal_id)
            workspace_path: Project directory
            project_name: Project name for display

        Returns:
            terminal_id (str(project_pid))

        Raises:
            ValueError: If terminal already exists for this project
        """
        terminal_id = str(project_pid)

        if terminal_id in self.terminals:
            logger.warning(f"Terminal {terminal_id} already exists, returning existing")
            return terminal_id

        logger.info(f"Creating terminal for project {project_name} (PID: {project_pid})")

        try:
            # Create process with output callback
            terminal = ManagedTerminalProcess(
                terminal_id=terminal_id,
                workspace_path=workspace_path,
                project_name=project_name,
                output_callback=self._broadcast_output
            )

            self.terminals[terminal_id] = terminal

            logger.info(f"Terminal {terminal_id} created successfully")
            return terminal_id

        except Exception as e:
            logger.error(f"Error creating terminal: {e}")
            raise

    def get_terminal(self, terminal_id: str) -> Optional[ManagedTerminalProcess]:
        """
        Get terminal by ID.

        Args:
            terminal_id: Terminal identifier

        Returns:
            ManagedTerminalProcess or None if not found
        """
        return self.terminals.get(terminal_id)

    def get_terminal_by_workspace(self, workspace_path: str) -> Optional[ManagedTerminalProcess]:
        """
        Get terminal by workspace path.

        Args:
            workspace_path: Project workspace path

        Returns:
            ManagedTerminalProcess or None if not found
        """
        for terminal in self.terminals.values():
            if terminal.workspace_path.lower() == workspace_path.lower():
                return terminal
        return None

    def get_all_terminals(self) -> List[TerminalInfo]:
        """
        Get info for all terminals.

        Returns:
            List of TerminalInfo objects
        """
        terminals_info = []

        for terminal in self.terminals.values():
            info = terminal.get_info()
            terminals_info.append(TerminalInfo(**info))

        return terminals_info

    def send_command(self, terminal_id: str, command: str):
        """
        Send command to terminal.

        Args:
            terminal_id: Target terminal
            command: Command string

        Raises:
            ValueError: If terminal not found
            RuntimeError: If terminal not in running state
        """
        terminal = self.get_terminal(terminal_id)

        if not terminal:
            raise ValueError(f"Terminal {terminal_id} not found")

        terminal.send_command(command)
        logger.debug(f"Sent command to terminal {terminal_id}: {command[:50]}")

    def get_output_buffer(self, terminal_id: str, last_n_lines: int = 50) -> List[str]:
        """
        Get recent output from terminal.

        Args:
            terminal_id: Terminal ID
            last_n_lines: Number of recent lines

        Returns:
            List of output lines

        Raises:
            ValueError: If terminal not found
        """
        terminal = self.get_terminal(terminal_id)

        if not terminal:
            raise ValueError(f"Terminal {terminal_id} not found")

        return terminal.get_output_buffer(last_n_lines)

    def terminate_terminal(self, terminal_id: str):
        """
        Terminate terminal process.

        Args:
            terminal_id: Terminal to terminate

        Raises:
            ValueError: If terminal not found
        """
        terminal = self.get_terminal(terminal_id)

        if not terminal:
            raise ValueError(f"Terminal {terminal_id} not found")

        logger.info(f"Terminating terminal {terminal_id}")
        terminal.terminate()

        # Remove from registry
        del self.terminals[terminal_id]

        logger.info(f"Terminal {terminal_id} removed from registry")

    def terminate_all(self):
        """Terminate all terminals (cleanup on shutdown)"""
        logger.info(f"Terminating all terminals ({len(self.terminals)} active)")

        for terminal_id in list(self.terminals.keys()):
            try:
                self.terminate_terminal(terminal_id)
            except Exception as e:
                logger.error(f"Error terminating terminal {terminal_id}: {e}")

        logger.info("All terminals terminated")

    def get_terminal_status(self, terminal_id: str) -> TerminalStatus:
        """
        Get status of terminal.

        Args:
            terminal_id: Terminal ID

        Returns:
            TerminalStatus object

        Raises:
            ValueError: If terminal not found
        """
        terminal = self.get_terminal(terminal_id)

        if not terminal:
            raise ValueError(f"Terminal {terminal_id} not found")

        return TerminalStatus(
            terminal_id=terminal_id,
            state=terminal.state,
            exit_code=None if terminal.is_running() else terminal.process.poll(),
            message=None
        )

    def cleanup_dead_terminals(self):
        """Remove terminals for processes that are no longer running"""
        dead_terminals = []

        for terminal_id, terminal in self.terminals.items():
            if not terminal.is_running():
                dead_terminals.append(terminal_id)

        for terminal_id in dead_terminals:
            logger.info(f"Cleaning up dead terminal {terminal_id}")
            try:
                del self.terminals[terminal_id]
            except Exception as e:
                logger.error(f"Error cleaning up terminal {terminal_id}: {e}")

        if dead_terminals:
            logger.info(f"Cleaned up {len(dead_terminals)} dead terminals")

    def check_idle_terminals(self, idle_timeout_seconds: int = 300):
        """
        Check all terminals for idle state based on last activity.

        If a terminal has no output for idle_timeout_seconds (default 5 min),
        updates bridge.json to 'idle' state.

        This implements Opción A+D: Timeout + no output detection.

        Args:
            idle_timeout_seconds: Seconds of inactivity before marking idle
        """
        from datetime import datetime, timedelta
        from sendell.project_manager.bridge import get_terminal_status, set_terminal_idle

        current_time = datetime.now()
        idle_count = 0

        for terminal_id, terminal in self.terminals.items():
            if not terminal.is_running():
                continue

            # Check if terminal has been inactive
            time_since_activity = (current_time - terminal.last_activity).total_seconds()

            if time_since_activity > idle_timeout_seconds:
                # Check bridge status
                bridge_status = get_terminal_status(terminal.workspace_path)

                if bridge_status == 'working':
                    # Terminal was marked as working but hasn't had output in a while
                    # Update to idle
                    logger.info(
                        f"Terminal {terminal_id} idle for {time_since_activity:.0f}s, "
                        f"updating bridge.json to idle"
                    )
                    set_terminal_idle(terminal.workspace_path)
                    idle_count += 1

        if idle_count > 0:
            logger.debug(f"Marked {idle_count} terminals as idle due to inactivity")


# Singleton accessor
def get_terminal_manager() -> TerminalManager:
    """Get singleton TerminalManager instance"""
    return TerminalManager()
