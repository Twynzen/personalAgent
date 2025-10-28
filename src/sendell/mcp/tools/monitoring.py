"""
MCP tools for system monitoring.

Implements:
- get_system_health: Get CPU, RAM, disk usage
- get_active_window: Get current active window info
"""

from typing import Any

from sendell.device.monitor import SystemMonitor
from sendell.security.permissions import get_permission_manager
from sendell.utils.errors import MonitoringError
from sendell.utils.logger import get_logger

logger = get_logger(__name__)


def get_system_health() -> dict[str, Any]:
    """
    Get current system health metrics.

    Returns CPU, RAM, and disk usage percentages.
    This is a read-only operation (L1+ permission).

    Returns:
        Dict with cpu_percent, ram_percent, disk_percent, etc.

    Raises:
        MonitoringError: If system monitoring fails

    Example:
        >>> health = get_system_health()
        >>> print(f"CPU: {health['cpu_percent']}%")
    """
    # Check permissions (L1+)
    pm = get_permission_manager()
    pm.require_permission("get_system_health")

    logger.info("Getting system health")

    try:
        monitor = SystemMonitor()
        health = monitor.get_system_health()

        # Convert to dict for MCP
        result = health.to_dict()

        # Add threshold warnings
        warnings = monitor.check_thresholds(health)
        if warnings:
            result["warnings"] = warnings
            logger.warning(f"System health warnings: {warnings}")

        logger.info("Successfully retrieved system health")
        return result

    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise MonitoringError(f"Failed to get system health: {e}")


def get_active_window() -> dict[str, Any]:
    """
    Get information about the currently active window.

    Returns window title, process name, and PID.
    This is a read-only operation (L1+ permission).
    Respects privacy settings (blocked apps).

    Returns:
        Dict with title, process_name, pid, timestamp

    Raises:
        MonitoringError: If getting active window fails

    Example:
        >>> window = get_active_window()
        >>> print(f"Active: {window['title']}")
    """
    # Check permissions (L1+)
    pm = get_permission_manager()
    pm.require_permission("get_active_window")

    logger.info("Getting active window")

    try:
        monitor = SystemMonitor()
        active_window = monitor.get_active_window()

        if active_window is None:
            logger.warning("No active window detected")
            return {
                "title": None,
                "process_name": None,
                "pid": None,
                "timestamp": None,
                "available": False,
            }

        # Convert to dict for MCP
        result = active_window.to_dict()
        result["available"] = True

        logger.info(f"Active window: {active_window.title}")
        return result

    except Exception as e:
        logger.error(f"Failed to get active window: {e}")
        raise MonitoringError(f"Failed to get active window: {e}")
