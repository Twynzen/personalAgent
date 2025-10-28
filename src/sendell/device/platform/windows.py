"""
Windows-specific monitoring and control using win32 APIs.

Requires: pywin32
"""

import sys
from datetime import datetime
from typing import Optional

from sendell.device.monitor import ActiveWindow
from sendell.utils.errors import MonitoringError
from sendell.utils.logger import get_logger

logger = get_logger(__name__)

# Only import win32 on Windows
if sys.platform == "win32":
    try:
        import win32gui
        import win32process
        import psutil

        WIN32_AVAILABLE = True
    except ImportError as e:
        logger.warning(f"win32 APIs not available: {e}")
        WIN32_AVAILABLE = False
else:
    WIN32_AVAILABLE = False


class WindowsMonitor:
    """Windows-specific system monitoring"""

    def __init__(self):
        """Initialize Windows monitor"""
        if not WIN32_AVAILABLE:
            raise ImportError("pywin32 is required for Windows monitoring")

    def get_active_window(self) -> Optional[ActiveWindow]:
        """
        Get the currently active window on Windows.

        Returns:
            ActiveWindow with title, process info, or None

        Raises:
            MonitoringError: If getting active window fails
        """
        if not WIN32_AVAILABLE:
            return None

        try:
            # Get foreground window
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None

            # Get window title
            title = win32gui.GetWindowText(hwnd)
            if not title:
                title = "<No Title>"

            # Get process ID and name
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            try:
                proc = psutil.Process(pid)
                process_name = proc.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "<Unknown>"

            active_win = ActiveWindow(
                title=title, process_name=process_name, pid=pid, timestamp=datetime.now()
            )

            logger.debug(f"Active window: {title} ({process_name})")
            return active_win

        except Exception as e:
            logger.error(f"Failed to get active window: {e}")
            raise MonitoringError(f"Failed to get active window: {e}")
