"""
Managed Terminal Process

Wraps subprocess.Popen with real-time I/O capture and command queuing.
"""

import subprocess
import threading
import queue
import psutil
from typing import Optional, Callable, List
from datetime import datetime
from pathlib import Path

from sendell.terminal_manager.types import ProcessState, TerminalOutput
from sendell.utils.logger import get_logger

logger = get_logger(__name__)


class ManagedTerminalProcess:
    """
    Manages a single terminal process with real-time I/O.

    Uses subprocess.Popen with PIPE for stdout/stderr.
    Threading for non-blocking I/O capture.
    Queue for command input.
    """

    def __init__(
        self,
        terminal_id: str,
        workspace_path: str,
        project_name: str,
        output_callback: Optional[Callable[[TerminalOutput], None]] = None
    ):
        """
        Initialize terminal process.

        Args:
            terminal_id: Unique identifier (usually project_pid)
            workspace_path: Working directory for process
            project_name: Project name for display
            output_callback: Called for each line of output
        """
        self.terminal_id = terminal_id
        self.workspace_path = workspace_path
        self.project_name = project_name
        self.output_callback = output_callback

        self.process: Optional[subprocess.Popen] = None
        self.state = ProcessState.STARTING
        self.pid: Optional[int] = None
        self.created_at = datetime.now()
        self.last_activity = datetime.now()

        # I/O management
        self.command_queue: queue.Queue[str] = queue.Queue()
        self.output_buffer: List[str] = []  # Last N lines
        self.max_buffer_lines = 1000

        # Threading
        self.stdout_thread: Optional[threading.Thread] = None
        self.stderr_thread: Optional[threading.Thread] = None
        self.stdin_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Start process
        self._start_process()

    def _start_process(self):
        """Start cmd.exe process with PIPE for I/O"""
        try:
            logger.info(f"Starting terminal process for {self.project_name} at {self.workspace_path}")

            # Start cmd.exe in project directory
            # /Q = quiet (no version banner)
            # /K = keep open after command
            self.process = subprocess.Popen(
                ["cmd.exe", "/Q", "/K", f"cd /d {self.workspace_path}"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                cwd=self.workspace_path,
                encoding='utf-8',
                errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW  # No separate window
            )

            self.pid = self.process.pid
            self.state = ProcessState.RUNNING

            logger.info(f"Terminal process started with PID {self.pid}")

            # Start I/O threads
            self._start_io_threads()

        except Exception as e:
            logger.error(f"Error starting terminal process: {e}")
            self.state = ProcessState.ERROR
            raise

    def _start_io_threads(self):
        """Start threads for I/O handling"""
        # Stdout reader
        self.stdout_thread = threading.Thread(
            target=self._read_stdout,
            daemon=True,
            name=f"stdout-{self.terminal_id}"
        )
        self.stdout_thread.start()

        # Stderr reader
        self.stderr_thread = threading.Thread(
            target=self._read_stderr,
            daemon=True,
            name=f"stderr-{self.terminal_id}"
        )
        self.stderr_thread.start()

        # Stdin writer
        self.stdin_thread = threading.Thread(
            target=self._write_stdin,
            daemon=True,
            name=f"stdin-{self.terminal_id}"
        )
        self.stdin_thread.start()

    def _read_stdout(self):
        """Read stdout in separate thread"""
        try:
            for line in self.process.stdout:
                if self._stop_event.is_set():
                    break

                line = line.rstrip('\r\n')
                self._handle_output('stdout', line)
        except Exception as e:
            if not self._stop_event.is_set():
                logger.error(f"Error reading stdout: {e}")

    def _read_stderr(self):
        """Read stderr in separate thread"""
        try:
            for line in self.process.stderr:
                if self._stop_event.is_set():
                    break

                line = line.rstrip('\r\n')
                self._handle_output('stderr', line)
        except Exception as e:
            if not self._stop_event.is_set():
                logger.error(f"Error reading stderr: {e}")

    def _write_stdin(self):
        """Write commands to stdin from queue"""
        try:
            while not self._stop_event.is_set():
                try:
                    # Get command from queue (timeout to check stop event)
                    command = self.command_queue.get(timeout=0.5)

                    if self.process and self.process.stdin:
                        # Write command + newline
                        self.process.stdin.write(command + '\n')
                        self.process.stdin.flush()

                        self.last_activity = datetime.now()
                        logger.debug(f"Sent command to terminal {self.terminal_id}: {command[:50]}")

                    self.command_queue.task_done()

                except queue.Empty:
                    continue

        except Exception as e:
            if not self._stop_event.is_set():
                logger.error(f"Error writing to stdin: {e}")

    def _handle_output(self, stream: str, line: str):
        """Handle output line from stdout/stderr"""
        self.last_activity = datetime.now()

        # Add to buffer
        self.output_buffer.append(line)
        if len(self.output_buffer) > self.max_buffer_lines:
            self.output_buffer = self.output_buffer[-self.max_buffer_lines:]

        # Create output object
        output = TerminalOutput(
            terminal_id=self.terminal_id,
            stream=stream,
            data=line,
            timestamp=datetime.now()
        )

        # Call callback if provided
        if self.output_callback:
            try:
                self.output_callback(output)
            except Exception as e:
                logger.error(f"Error in output callback: {e}")

    def send_command(self, command: str):
        """
        Send command to terminal stdin.

        Args:
            command: Command string (without newline)
        """
        if self.state != ProcessState.RUNNING:
            raise RuntimeError(f"Cannot send command to terminal in state {self.state}")

        self.command_queue.put(command)
        logger.debug(f"Queued command for {self.terminal_id}: {command[:50]}")

    def get_output_buffer(self, last_n_lines: int = 50) -> List[str]:
        """
        Get recent output lines.

        Args:
            last_n_lines: Number of recent lines to return

        Returns:
            List of output lines
        """
        return self.output_buffer[-last_n_lines:]

    def is_running(self) -> bool:
        """Check if process is still running"""
        if not self.process:
            return False

        poll = self.process.poll()
        return poll is None

    def has_active_subprocess(self) -> bool:
        """
        Check if terminal has any active child processes (running commands).

        Uses psutil to check children of cmd.exe process.
        """
        if not self.is_running():
            return False

        try:
            parent = psutil.Process(self.pid)
            children = parent.children(recursive=True)

            # Filter out conhost.exe (always present with cmd.exe)
            active_children = [
                p for p in children
                if p.name().lower() not in ['conhost.exe']
            ]

            return len(active_children) > 0

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    def get_active_command(self) -> Optional[str]:
        """
        Get name of currently running command if any.

        Returns:
            Process name or None
        """
        if not self.has_active_subprocess():
            return None

        try:
            parent = psutil.Process(self.pid)
            children = parent.children(recursive=True)

            for child in children:
                name = child.name().lower()
                if name not in ['conhost.exe']:
                    return name

            return None

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    def terminate(self):
        """Terminate process gracefully and cleanup bridge.json"""
        if not self.process:
            return

        logger.info(f"Terminating terminal {self.terminal_id}")

        # Signal threads to stop
        self._stop_event.set()

        # Terminate process
        try:
            self.process.terminate()
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning(f"Process {self.pid} did not terminate, killing")
            self.process.kill()
        except Exception as e:
            logger.error(f"Error terminating process: {e}")

        # Update bridge.json to idle state when terminal closes
        try:
            from sendell.project_manager.bridge import set_terminal_idle
            set_terminal_idle(self.workspace_path)
            logger.debug(f"Updated bridge.json to idle for {self.workspace_path}")
        except Exception as e:
            logger.error(f"Error updating bridge.json on terminate: {e}")

        self.state = ProcessState.STOPPED
        logger.info(f"Terminal {self.terminal_id} terminated")

    def get_info(self) -> dict:
        """Get terminal info as dict"""
        return {
            'terminal_id': self.terminal_id,
            'workspace_path': self.workspace_path,
            'project_name': self.project_name,
            'state': self.state.value,
            'pid': self.pid,
            'is_running': self.is_running(),
            'has_active_subprocess': self.has_active_subprocess(),
            'active_command': self.get_active_command(),
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
        }
