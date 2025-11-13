"""
Server Process Tracker

Tracks dashboard server PID to enable cleanup when Sendell closes.
Prevents orphaned server processes.
"""

import os
import psutil
from pathlib import Path
from typing import Optional
from sendell.utils.logger import get_logger

logger = get_logger(__name__)

# PID file location
PID_FILE = Path.home() / ".sendell" / "dashboard_server.pid"


def save_server_pid(pid: int):
    """
    Save server PID to file for later cleanup.

    Args:
        pid: Process ID of the dashboard server
    """
    try:
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        PID_FILE.write_text(str(pid))
        logger.info(f"Saved server PID {pid} to {PID_FILE}")
    except Exception as e:
        logger.error(f"Failed to save server PID: {e}")


def get_server_pid() -> Optional[int]:
    """
    Get saved server PID if it exists.

    Returns:
        PID if found, None otherwise
    """
    try:
        if PID_FILE.exists():
            pid_str = PID_FILE.read_text().strip()
            return int(pid_str)
    except Exception as e:
        logger.error(f"Failed to read server PID: {e}")

    return None


def kill_server():
    """
    Kill dashboard server process if it's running.
    Uses saved PID from file.
    """
    pid = get_server_pid()

    if pid is None:
        logger.info("No server PID found - nothing to kill")
        return

    try:
        # Check if process exists
        if psutil.pid_exists(pid):
            process = psutil.Process(pid)

            # Verify it's actually our uvicorn server
            cmdline = ' '.join(process.cmdline())
            if 'uvicorn' in cmdline and 'sendell.web.server' in cmdline:
                logger.info(f"Killing dashboard server process (PID {pid})...")

                # Kill process and all children
                children = process.children(recursive=True)
                for child in children:
                    logger.debug(f"Killing child process {child.pid}")
                    child.kill()

                process.kill()
                process.wait(timeout=5)

                logger.info(f"✅ Server process {pid} killed successfully")
            else:
                logger.warning(f"PID {pid} exists but is not our uvicorn server: {cmdline}")
        else:
            logger.info(f"Server process {pid} is not running (already stopped)")

    except psutil.NoSuchProcess:
        logger.info(f"Server process {pid} no longer exists")
    except psutil.TimeoutExpired:
        logger.error(f"Timeout killing server process {pid}")
    except Exception as e:
        logger.error(f"Error killing server process {pid}: {e}")
    finally:
        # Always clean up PID file
        try:
            if PID_FILE.exists():
                PID_FILE.unlink()
                logger.debug("Removed PID file")
        except Exception as e:
            logger.error(f"Failed to remove PID file: {e}")


def is_server_running() -> bool:
    """
    Check if server is currently running.

    Returns:
        True if server process exists, False otherwise
    """
    pid = get_server_pid()

    if pid is None:
        return False

    try:
        if psutil.pid_exists(pid):
            process = psutil.Process(pid)
            cmdline = ' '.join(process.cmdline())
            return 'uvicorn' in cmdline and 'sendell.web.server' in cmdline
    except:
        pass

    return False
