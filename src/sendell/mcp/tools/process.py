"""
MCP tools for process management.

Implements:
- list_top_processes: List processes by resource usage
- open_application: Open an application
"""

from typing import Any, Optional

from sendell.device.automation import AppController
from sendell.device.monitor import SystemMonitor
from sendell.security.permissions import get_permission_manager
from sendell.utils.errors import AutomationError, MonitoringError
from sendell.utils.logger import get_logger

logger = get_logger(__name__)


def list_top_processes(n: int = 10, sort_by: str = "memory") -> dict[str, Any]:
    """
    List top N processes by resource usage.

    Args:
        n: Number of processes to return (default: 10)
        sort_by: Sort by 'memory' or 'cpu' (default: 'memory')

    Returns:
        Dict with processes list and summary

    Raises:
        MonitoringError: If process enumeration fails

    Example:
        >>> result = list_top_processes(5, "cpu")
        >>> for proc in result['processes']:
        ...     print(f"{proc['name']}: {proc['cpu_percent']}%")
    """
    # Check permissions (L1+)
    pm = get_permission_manager()
    pm.require_permission("list_top_processes")

    logger.info(f"Listing top {n} processes by {sort_by}")

    try:
        # Validate inputs
        if n < 1 or n > 100:
            raise ValueError("n must be between 1 and 100")

        if sort_by not in ["memory", "cpu"]:
            raise ValueError("sort_by must be 'memory' or 'cpu'")

        monitor = SystemMonitor()
        processes = monitor.get_top_processes(n=n, sort_by=sort_by)

        # Convert to dicts
        process_list = [p.to_dict() for p in processes]

        # Calculate totals
        total_memory_mb = sum(p.memory_mb for p in processes)
        total_cpu_percent = sum(p.cpu_percent for p in processes)

        result = {
            "processes": process_list,
            "count": len(process_list),
            "sort_by": sort_by,
            "total_memory_mb": round(total_memory_mb, 1),
            "total_cpu_percent": round(total_cpu_percent, 1),
        }

        logger.info(f"Retrieved {len(process_list)} processes")
        return result

    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to list processes: {e}")
        raise MonitoringError(f"Failed to list processes: {e}")


def open_application(app_name: str, args: Optional[list] = None) -> dict[str, Any]:
    """
    Open an application by name.

    Requires L3+ autonomy level (Safe Actions).
    Respects blocked apps from privacy settings.

    Args:
        app_name: Application name or path to open
        args: Optional command-line arguments

    Returns:
        Dict with success status, PID, and app info

    Raises:
        AutomationError: If opening application fails
        PermissionDeniedError: If insufficient autonomy level

    Example:
        >>> result = open_application("notepad")
        >>> print(f"Opened with PID: {result['pid']}")
    """
    # Check permissions (L3+)
    pm = get_permission_manager()
    pm.require_permission("open_application")

    logger.info(f"Opening application: {app_name}")

    try:
        # Validate app_name
        if not app_name or not isinstance(app_name, str):
            raise ValueError("app_name must be a non-empty string")

        controller = AppController()
        result = controller.open_application(app_name, args=args)

        logger.info(f"Successfully opened {app_name} (PID: {result['pid']})")
        return result

    except AutomationError:
        raise
    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to open application: {e}")
        raise AutomationError(f"Failed to open application: {e}")
