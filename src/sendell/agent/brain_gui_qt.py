"""
Sendell Brain GUI - Web Dashboard Launcher

Opens the Angular dashboard in the default browser.
Backend FastAPI server runs automatically.
"""

import webbrowser
import time
import threading
from typing import List

from sendell.utils.logger import get_logger

logger = get_logger(__name__)


class BackendThread(threading.Thread):
    """Background thread to run FastAPI server"""

    def __init__(self):
        super().__init__(daemon=True)
        self.server = None

    def run(self):
        """Start uvicorn server"""
        try:
            import uvicorn
            from sendell.web.server import app

            logger.info("Starting FastAPI backend server on port 8765...")

            # Run server (this blocks until stopped)
            uvicorn.run(
                app,
                host="127.0.0.1",
                port=8765,
                log_level="info",
                access_log=False  # Reduce noise
            )

        except Exception as e:
            logger.error(f"Backend server error: {e}")


def show_brain(tools: List = None) -> str:
    """
    Show the Sendell Brain GUI (Web Dashboard).

    Opens the Angular dashboard in the default browser.
    Backend starts automatically in background thread.

    Args:
        tools: List of available tools (passed but not used - Angular gets via API)

    Returns:
        Success message
    """
    logger.info("Opening Sendell Brain Dashboard...")

    # Start backend in background thread
    logger.info("Starting backend server thread...")
    backend_thread = BackendThread()
    backend_thread.start()

    # Wait for server to start (3 seconds should be enough)
    logger.info("Waiting for backend to initialize...")
    time.sleep(3)

    # Open browser
    url = "http://localhost:8765"
    logger.info(f"Opening browser at {url}")

    try:
        webbrowser.open(url)
        logger.info("Browser opened successfully")
        return f"Brain Dashboard opened at {url}"
    except Exception as e:
        logger.error(f"Failed to open browser: {e}")
        return f"Backend running at {url} - Please open manually in your browser"
