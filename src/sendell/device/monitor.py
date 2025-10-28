"""
System monitoring using psutil.

Provides cross-platform system monitoring:
- CPU, RAM, Disk usage
- Process information
- Active window tracking (platform-specific)

All methods are safe and respect privacy settings.
"""

import time
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import psutil

from sendell.config import get_settings
from sendell.utils.errors import MonitoringError
from sendell.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SystemHealth:
    """System health snapshot"""

    cpu_percent: float
    ram_percent: float
    ram_used_gb: float
    ram_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    timestamp: datetime
    cpu_count: int

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "cpu_percent": round(self.cpu_percent, 1),
            "ram_percent": round(self.ram_percent, 1),
            "ram_used_gb": round(self.ram_used_gb, 2),
            "ram_total_gb": round(self.ram_total_gb, 2),
            "disk_percent": round(self.disk_percent, 1),
            "disk_used_gb": round(self.disk_used_gb, 2),
            "disk_total_gb": round(self.disk_total_gb, 2),
            "cpu_count": self.cpu_count,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ProcessInfo:
    """Process information"""

    pid: int
    name: str
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    status: str
    num_threads: int

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "pid": self.pid,
            "name": self.name,
            "cpu_percent": round(self.cpu_percent, 2),
            "memory_mb": round(self.memory_mb, 1),
            "memory_percent": round(self.memory_percent, 2),
            "status": self.status,
            "num_threads": self.num_threads,
        }


@dataclass
class ActiveWindow:
    """Active window information"""

    title: str
    process_name: str
    pid: int
    timestamp: datetime

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "title": self.title,
            "process_name": self.process_name,
            "pid": self.pid,
            "timestamp": self.timestamp.isoformat(),
        }


class SystemMonitor:
    """
    Cross-platform system monitor using psutil.

    Respects privacy settings and blocked apps.
    """

    def __init__(self):
        """Initialize system monitor"""
        self.settings = get_settings()
        self._platform_monitor = None

        # Try to load platform-specific monitor
        try:
            import platform
            if platform.system() == "Windows":
                from sendell.device.platform.windows import WindowsMonitor
                self._platform_monitor = WindowsMonitor()
                logger.info("Initialized Windows-specific monitoring")
        except ImportError as e:
            logger.warning(f"Platform-specific monitoring not available: {e}")

    def get_system_health(self) -> SystemHealth:
        """
        Get current system health snapshot.

        Returns:
            SystemHealth with CPU, RAM, disk metrics

        Raises:
            MonitoringError: If monitoring fails
        """
        try:
            # CPU (interval=1 for more accurate reading)
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Memory
            memory = psutil.virtual_memory()
            ram_percent = memory.percent
            ram_used_gb = memory.used / (1024**3)
            ram_total_gb = memory.total / (1024**3)

            # Disk (main partition)
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent
            disk_used_gb = disk.used / (1024**3)
            disk_total_gb = disk.total / (1024**3)

            health = SystemHealth(
                cpu_percent=cpu_percent,
                ram_percent=ram_percent,
                ram_used_gb=ram_used_gb,
                ram_total_gb=ram_total_gb,
                disk_percent=disk_percent,
                disk_used_gb=disk_used_gb,
                disk_total_gb=disk_total_gb,
                timestamp=datetime.now(),
                cpu_count=cpu_count,
            )

            logger.debug(f"System health: CPU={cpu_percent}%, RAM={ram_percent}%")
            return health

        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            raise MonitoringError(f"Failed to get system health: {e}")

    def get_top_processes(
        self, n: int = 10, sort_by: str = "memory"
    ) -> List[ProcessInfo]:
        """
        Get top N processes by resource usage.

        Args:
            n: Number of processes to return
            sort_by: Sort by 'memory' or 'cpu'

        Returns:
            List of ProcessInfo sorted by usage

        Raises:
            MonitoringError: If process enumeration fails
        """
        try:
            processes = []
            blocked_apps = [app.lower() for app in self.settings.agent.blocked_apps]

            for proc in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_info", "memory_percent", "status", "num_threads"]
            ):
                try:
                    pinfo = proc.info
                    proc_name = pinfo["name"].lower()

                    # Skip blocked apps (privacy)
                    if any(blocked in proc_name for blocked in blocked_apps):
                        continue

                    # Get memory in MB
                    memory_mb = pinfo["memory_info"].rss / (1024 * 1024)

                    process_info = ProcessInfo(
                        pid=pinfo["pid"],
                        name=pinfo["name"],
                        cpu_percent=pinfo["cpu_percent"] or 0.0,
                        memory_mb=memory_mb,
                        memory_percent=pinfo["memory_percent"] or 0.0,
                        status=pinfo["status"],
                        num_threads=pinfo["num_threads"] or 0,
                    )
                    processes.append(process_info)

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Sort processes
            if sort_by == "cpu":
                processes.sort(key=lambda p: p.cpu_percent, reverse=True)
            else:  # memory
                processes.sort(key=lambda p: p.memory_mb, reverse=True)

            top_n = processes[:n]
            logger.debug(f"Got top {n} processes by {sort_by}")
            return top_n

        except Exception as e:
            logger.error(f"Failed to get top processes: {e}")
            raise MonitoringError(f"Failed to get top processes: {e}")

    def get_active_window(self) -> Optional[ActiveWindow]:
        """
        Get currently active window.

        Uses platform-specific implementation if available.

        Returns:
            ActiveWindow info or None if not available

        Raises:
            MonitoringError: If getting active window fails
        """
        try:
            if self._platform_monitor:
                return self._platform_monitor.get_active_window()

            logger.warning("Active window tracking not available on this platform")
            return None

        except Exception as e:
            logger.error(f"Failed to get active window: {e}")
            raise MonitoringError(f"Failed to get active window: {e}")

    def check_thresholds(self, health: SystemHealth) -> List[str]:
        """
        Check if system health exceeds configured thresholds.

        Args:
            health: SystemHealth to check

        Returns:
            List of warning messages
        """
        warnings = []

        if health.cpu_percent > self.settings.monitoring.cpu_threshold:
            warnings.append(
                f"CPU usage high: {health.cpu_percent}% "
                f"(threshold: {self.settings.monitoring.cpu_threshold}%)"
            )

        if health.ram_percent > self.settings.monitoring.ram_threshold:
            warnings.append(
                f"RAM usage high: {health.ram_percent}% "
                f"(threshold: {self.settings.monitoring.ram_threshold}%)"
            )

        if health.disk_percent > self.settings.monitoring.disk_threshold:
            warnings.append(
                f"Disk usage high: {health.disk_percent}% "
                f"(threshold: {self.settings.monitoring.disk_threshold}%)"
            )

        return warnings

    def find_process_by_name(self, name: str) -> Optional[ProcessInfo]:
        """
        Find a process by name.

        Args:
            name: Process name to search for (case-insensitive)

        Returns:
            ProcessInfo if found, None otherwise
        """
        name_lower = name.lower()

        try:
            for proc in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_info", "memory_percent", "status", "num_threads"]
            ):
                try:
                    if name_lower in proc.info["name"].lower():
                        memory_mb = proc.info["memory_info"].rss / (1024 * 1024)
                        return ProcessInfo(
                            pid=proc.info["pid"],
                            name=proc.info["name"],
                            cpu_percent=proc.info["cpu_percent"] or 0.0,
                            memory_mb=memory_mb,
                            memory_percent=proc.info["memory_percent"] or 0.0,
                            status=proc.info["status"],
                            num_threads=proc.info["num_threads"] or 0,
                        )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            return None

        except Exception as e:
            logger.error(f"Failed to find process '{name}': {e}")
            return None
