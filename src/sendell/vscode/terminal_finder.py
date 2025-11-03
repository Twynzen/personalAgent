"""
Terminal Finder

Find terminal child processes spawned by VS Code instances.
Detects PowerShell, CMD, Bash, WSL terminals.

Based on investigation: investigacionvscodemonitoring.txt (Part 1, lines 124-166)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List

import psutil

from sendell.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TerminalInfo:
    """Information about a terminal process"""

    pid: int
    name: str
    shell_type: str  # 'powershell', 'cmd', 'bash', 'wsl', 'unknown'
    cmdline: List[str]
    cwd: str
    create_time: datetime
    status: str


class TerminalFinder:
    """
    Find terminal processes spawned by VS Code.

    Detects common shells:
    - PowerShell (powershell.exe, pwsh.exe)
    - Command Prompt (cmd.exe)
    - Bash (bash.exe, sh.exe)
    - WSL (wsl.exe)
    """

    # Terminal process names to detect
    TERMINAL_NAMES = [
        "powershell.exe",
        "pwsh.exe",  # PowerShell Core
        "cmd.exe",  # Command Prompt
        "bash.exe",  # Git Bash, WSL Bash
        "sh.exe",  # Shell
        "wsl.exe",  # Windows Subsystem for Linux
    ]

    @staticmethod
    def find_terminals(vscode_pid: int) -> List[TerminalInfo]:
        """
        Find terminal processes spawned by a VS Code instance.

        Args:
            vscode_pid: PID of VS Code main process

        Returns:
            List of TerminalInfo for all detected terminals

        Notes:
            - Uses recursive process tree traversal
            - Handles AccessDenied and NoSuchProcess errors gracefully
            - Returns empty list if parent process doesn't exist
        """
        terminals = []

        try:
            parent = psutil.Process(vscode_pid)

            # Recursively find all child processes
            for child in parent.children(recursive=True):
                try:
                    name = child.name().lower()

                    # Check if it's a terminal process
                    if name in TerminalFinder.TERMINAL_NAMES:
                        shell_type = TerminalFinder._detect_shell_type(name)

                        terminals.append(
                            TerminalInfo(
                                pid=child.pid,
                                name=child.name(),
                                shell_type=shell_type,
                                cmdline=child.cmdline(),
                                cwd=child.cwd(),
                                create_time=datetime.fromtimestamp(child.create_time()),
                                status=child.status(),
                            )
                        )

                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    # Terminal may have closed or we don't have permission
                    logger.debug(f"Could not access child process: {e}")
                    continue

        except psutil.NoSuchProcess:
            logger.warning(f"VS Code process {vscode_pid} not found")
        except psutil.AccessDenied:
            logger.warning(f"Access denied to VS Code process {vscode_pid}")
        except Exception as e:
            logger.error(f"Error finding terminals for PID {vscode_pid}: {e}")

        return terminals

    @staticmethod
    def _detect_shell_type(process_name: str) -> str:
        """
        Detect shell type from process name.

        Args:
            process_name: Process name (lowercase)

        Returns:
            Shell type string: 'powershell', 'cmd', 'bash', 'wsl', 'unknown'
        """
        if "powershell" in process_name or "pwsh" in process_name:
            return "powershell"
        elif "cmd" in process_name:
            return "cmd"
        elif "bash" in process_name or "sh" in process_name:
            return "bash"
        elif "wsl" in process_name:
            return "wsl"
        else:
            return "unknown"

    @staticmethod
    def get_shell_info(shell_type: str) -> dict:
        """
        Get shell-specific information (syntax, commands, etc.)

        Args:
            shell_type: Shell type string

        Returns:
            Dictionary with shell-specific information
        """
        SHELL_INFO = {
            "powershell": {
                "newline": "\r\n",
                "list_dir": "Get-ChildItem",
                "change_dir": "Set-Location",
                "env_var": "$env:VAR_NAME",
                "comment": "#",
            },
            "cmd": {
                "newline": "\r\n",
                "list_dir": "dir",
                "change_dir": "cd",
                "env_var": "%VAR_NAME%",
                "comment": "REM",
            },
            "bash": {
                "newline": "\n",
                "list_dir": "ls -la",
                "change_dir": "cd",
                "env_var": "$VAR_NAME",
                "comment": "#",
            },
            "wsl": {
                "newline": "\n",
                "list_dir": "ls -la",
                "change_dir": "cd",
                "env_var": "$VAR_NAME",
                "comment": "#",
            },
        }

        return SHELL_INFO.get(shell_type, SHELL_INFO["bash"])
