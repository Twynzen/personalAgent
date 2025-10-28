"""
Application automation and control.

Handles:
- Opening applications
- Process management
- Window control (future)
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import psutil

from sendell.config import get_settings
from sendell.utils.errors import AutomationError
from sendell.utils.logger import get_logger

logger = get_logger(__name__)


# Common application paths on Windows
WINDOWS_APP_PATHS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ],
    "firefox": [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
    ],
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "vscode": [
        r"C:\Program Files\Microsoft VS Code\Code.exe",
        r"C:\Users\{username}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    ],
    "explorer": "explorer.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "terminal": "wt.exe",  # Windows Terminal
}


class AppController:
    """
    Cross-platform application controller.

    Handles opening apps, managing processes safely.
    """

    def __init__(self):
        """Initialize app controller"""
        self.settings = get_settings()

    def open_application(self, app_name: str, args: Optional[list] = None) -> dict:
        """
        Open an application by name.

        Args:
            app_name: Application name or path
            args: Optional command-line arguments

        Returns:
            Dict with success status and PID

        Raises:
            AutomationError: If opening app fails
        """
        try:
            # Check if app is blocked
            blocked_apps = [app.lower() for app in self.settings.agent.blocked_apps]
            if any(blocked in app_name.lower() for blocked in blocked_apps):
                raise AutomationError(f"Application '{app_name}' is blocked by privacy settings")

            # Resolve app path
            app_path = self._resolve_app_path(app_name)
            if not app_path:
                raise AutomationError(f"Application '{app_name}' not found")

            # Build command
            cmd = [app_path]
            if args:
                cmd.extend(args)

            logger.info(f"Opening application: {app_name} (path: {app_path})")

            # Launch process (shell=False for security)
            if sys.platform == "win32":
                # On Windows, use CREATE_NEW_PROCESS_GROUP to avoid signal propagation
                process = subprocess.Popen(
                    cmd,
                    shell=False,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    shell=False,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

            result = {
                "success": True,
                "app_name": app_name,
                "pid": process.pid,
                "path": app_path,
            }

            logger.info(f"Successfully opened {app_name} (PID: {process.pid})")
            return result

        except AutomationError:
            raise
        except Exception as e:
            logger.error(f"Failed to open application '{app_name}': {e}")
            raise AutomationError(f"Failed to open application '{app_name}': {e}")

    def _resolve_app_path(self, app_name: str) -> Optional[str]:
        """
        Resolve application name to executable path.

        Args:
            app_name: App name or path

        Returns:
            Full path to executable or None
        """
        # If it's already a valid path
        if os.path.exists(app_name):
            return app_name

        # Try lowercase version
        app_lower = app_name.lower()

        # Platform-specific resolution
        if sys.platform == "win32":
            return self._resolve_windows_app(app_lower)
        elif sys.platform == "darwin":
            return self._resolve_mac_app(app_lower)
        else:
            return self._resolve_linux_app(app_lower)

    def _resolve_windows_app(self, app_name: str) -> Optional[str]:
        """Resolve app path on Windows"""
        # Check common apps
        if app_name in WINDOWS_APP_PATHS:
            paths = WINDOWS_APP_PATHS[app_name]

            # Handle single path or list
            if isinstance(paths, str):
                paths = [paths]

            for path in paths:
                # Replace {username} placeholder
                if "{username}" in path:
                    username = os.environ.get("USERNAME", "")
                    path = path.format(username=username)

                # Check if exists
                if os.path.exists(path):
                    return path

                # Try without full path (let Windows find it in PATH)
                if not os.path.dirname(path):
                    return path

        # Try .exe extension
        if not app_name.endswith(".exe"):
            exe_name = f"{app_name}.exe"
            # Let Windows search PATH
            return exe_name

        return None

    def _resolve_mac_app(self, app_name: str) -> Optional[str]:
        """Resolve app path on macOS"""
        # Common macOS app locations
        app_locations = [
            f"/Applications/{app_name}.app",
            f"/System/Applications/{app_name}.app",
            f"/Applications/Utilities/{app_name}.app",
        ]

        for location in app_locations:
            if os.path.exists(location):
                # Return path to executable inside .app bundle
                return f"{location}/Contents/MacOS/{app_name}"

        return None

    def _resolve_linux_app(self, app_name: str) -> Optional[str]:
        """Resolve app path on Linux"""
        # Try common locations
        common_paths = [
            f"/usr/bin/{app_name}",
            f"/usr/local/bin/{app_name}",
            f"/bin/{app_name}",
        ]

        for path in common_paths:
            if os.path.exists(path):
                return path

        # Let shell find it in PATH
        return app_name

    def kill_process(self, pid: int, force: bool = False) -> dict:
        """
        Kill a process by PID.

        Args:
            pid: Process ID
            force: Use SIGKILL instead of SIGTERM

        Returns:
            Dict with success status

        Raises:
            AutomationError: If killing process fails
        """
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()

            # Check if process is blocked
            blocked_apps = [app.lower() for app in self.settings.agent.blocked_apps]
            if any(blocked in proc_name.lower() for blocked in blocked_apps):
                raise AutomationError(f"Cannot kill blocked process: {proc_name}")

            logger.info(f"Killing process: {proc_name} (PID: {pid})")

            if force:
                proc.kill()  # SIGKILL
            else:
                proc.terminate()  # SIGTERM

            # Wait for process to exit
            try:
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                logger.warning(f"Process {pid} did not exit gracefully, force killing")
                proc.kill()
                proc.wait(timeout=5)

            logger.info(f"Successfully killed process {pid}")
            return {"success": True, "pid": pid, "name": proc_name}

        except psutil.NoSuchProcess:
            raise AutomationError(f"Process {pid} does not exist")
        except psutil.AccessDenied:
            raise AutomationError(f"Access denied to kill process {pid}")
        except Exception as e:
            logger.error(f"Failed to kill process {pid}: {e}")
            raise AutomationError(f"Failed to kill process {pid}: {e}")
