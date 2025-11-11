"""Background tasks for async scanning"""

import asyncio
import psutil
from sendell.vscode import VSCodeMonitor
from sendell.web.websocket import WebSocketManager
from sendell.terminal_manager import get_terminal_manager
from sendell.utils.logger import get_logger

logger = get_logger(__name__)


async def start_vscode_scanner(ws_manager: WebSocketManager):
    """
    Background task that scans VS Code instances every 10 seconds
    and broadcasts updates via WebSocket
    """
    logger.info("Starting VS Code scanner (background task)")
    monitor = VSCodeMonitor()

    while True:
        try:
            # Scan VS Code instances
            instances = monitor.find_vscode_instances()

            # Get system metrics
            cpu = psutil.cpu_percent(interval=0)
            ram = psutil.virtual_memory().percent

            # Build projects data
            projects = []
            for inst in instances:
                projects.append({
                    "pid": inst.pid,
                    "name": inst.name,
                    "workspace_name": inst.workspace.workspace_name or "Unknown",
                    "workspace_path": inst.workspace.workspace_path or "",
                    "workspace_type": inst.workspace.workspace_type,
                    "is_running": "sendell" in (inst.workspace.workspace_name or "").lower() or
                                 "gsiaf" in (inst.workspace.workspace_name or "").lower()
                })

            # Broadcast to all WebSocket clients
            await ws_manager.broadcast({
                "type": "update",
                "data": {
                    "projects": projects,
                    "metrics": {
                        "cpu": cpu,
                        "ram": ram,
                        "terminals": len(instances)
                    }
                }
            })

        except Exception as e:
            logger.error(f"Error in VS Code scanner: {e}")

        # Wait 10 seconds before next scan
        await asyncio.sleep(10)


async def start_idle_checker():
    """
    Background task that checks for idle terminals every 60 seconds.

    Implements timeout-based idle detection (Opción A+D):
    - If terminal has no output for 5 minutes → mark as idle in bridge.json
    """
    logger.info("Starting idle terminal checker (background task)")
    terminal_manager = get_terminal_manager()

    while True:
        try:
            # Check all terminals for idle state (5 min timeout)
            terminal_manager.check_idle_terminals(idle_timeout_seconds=300)

            # Also cleanup dead terminals
            terminal_manager.cleanup_dead_terminals()

        except Exception as e:
            logger.error(f"Error in idle terminal checker: {e}")

        # Check every 60 seconds
        await asyncio.sleep(60)
