"""
VS Code Process Detector

Detect running VS Code instances, identify workspaces, and find terminals.
Main orchestrator for VS Code monitoring.

Based on investigation: investigacionvscodemonitoring.txt (Part 1 + Part 5)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import psutil

from sendell.utils.logger import get_logger
from sendell.vscode.terminal_finder import TerminalFinder, TerminalInfo
from sendell.vscode.window_matcher import WindowMatcher
from sendell.vscode.workspace_parser import WorkspaceInfo, WorkspaceParser

logger = get_logger(__name__)


@dataclass
class VSCodeInstance:
    """
    Complete information about a VS Code instance.

    Combines process info, workspace info, and terminal info.
    """

    pid: int
    name: str
    executable: str
    cmdline: List[str]
    create_time: datetime
    cwd: str
    is_insiders: bool
    workspace: WorkspaceInfo
    terminals: List[TerminalInfo]


class VSCodeMonitor:
    """
    Monitor VS Code instances on Windows.

    Features:
    - Detect all running VS Code instances (stable + Insiders)
    - Identify workspace/project for each instance
    - Find terminal processes spawned by each instance
    - Filter out helper processes (renderer, gpu, etc.)

    Usage:
        monitor = VSCodeMonitor()
        instances = monitor.find_vscode_instances()

        for instance in instances:
            print(f"VS Code PID {instance.pid}")
            print(f"  Workspace: {instance.workspace.workspace_name}")
            print(f"  Terminals: {len(instance.terminals)}")
    """

    # Target VS Code executables
    TARGET_NAMES = [
        "Code.exe",  # VS Code Stable
        "Code - Insiders.exe",  # VS Code Insiders
        "VSCodium.exe",  # VSCodium (open source)
        "cursor.exe",  # Cursor editor (VS Code fork)
    ]

    def __init__(self):
        """Initialize VS Code monitor."""
        self.workspace_parser = WorkspaceParser()
        self.terminal_finder = TerminalFinder()
        logger.info("VSCodeMonitor initialized")

    def find_vscode_instances(self) -> List[VSCodeInstance]:
        """
        Find all VS Code instances with complete information.

        NEW STRATEGY (Fixed for multi-window detection):
        1. Find the MAIN VS Code process (oldest, no --type)
        2. Get ALL terminals from that main process
        3. Group terminals by their CWD (working directory)
        4. Create virtual "instances" for each unique CWD
        5. Each CWD represents a different VS Code window

        Why this works:
        - VS Code spawns all terminals from ONE main process
        - Each window opens terminals in its workspace directory
        - Grouping by CWD identifies which terminals belong to which window

        Returns:
            List of VSCodeInstance objects (one per workspace/window)
        """
        instances = []

        try:
            # Step 1: Find main VS Code process
            main_process = self._find_main_vscode_process()

            if not main_process:
                logger.warning("No main VS Code process found")
                return instances

            logger.debug(f"Found main VS Code process: PID={main_process['pid']}")

            # Step 2: Get ALL terminals from main process
            all_terminals = self.terminal_finder.find_terminals(main_process["pid"])
            logger.debug(f"Found {len(all_terminals)} total terminals")

            if not all_terminals:
                logger.info("No terminals found in VS Code")
                return instances

            # Step 3: Group terminals by CWD (working directory)
            terminal_groups = WindowMatcher.group_terminals_by_workspace(all_terminals)
            logger.debug(f"Grouped into {len(terminal_groups)} workspace(s)")

            # Step 4: Create virtual instances for each workspace
            for workspace_path, terminals in terminal_groups.items():
                workspace_name = workspace_path.split("\\")[-1] if workspace_path else "unknown"

                # Create workspace info (based on CWD)
                workspace = WorkspaceInfo(
                    workspace_type="folder",
                    workspace_path=workspace_path,
                    workspace_name=workspace_name,
                )

                # Create instance
                instance = VSCodeInstance(
                    pid=main_process["pid"],  # All share same main PID
                    name=main_process["name"],
                    executable=main_process["exe"],
                    cmdline=main_process["cmdline"],
                    create_time=main_process["create_time"],
                    cwd=workspace_path,  # Use terminal's CWD
                    is_insiders="Insiders" in main_process["name"],
                    workspace=workspace,
                    terminals=terminals,
                )

                instances.append(instance)

                logger.debug(
                    f"Created instance for workspace='{workspace_name}', "
                    f"terminals={len(terminals)}"
                )

        except Exception as e:
            logger.error(f"Error scanning for VS Code processes: {e}", exc_info=True)

        logger.info(
            f"Found {len(instances)} VS Code workspace(s) with "
            f"{sum(len(inst.terminals) for inst in instances)} terminal(s)"
        )
        return instances

    def _find_main_vscode_process(self) -> Optional[Dict]:
        """
        Find the MAIN VS Code process (not helper processes).

        Strategy:
        - Look for Code.exe without --type= argument
        - Choose the OLDEST process (earliest create_time)
        - This is the parent that spawns all terminals

        Returns:
            Dictionary with process info or None if not found
        """
        candidates = []

        try:
            for proc in psutil.process_iter(
                ["pid", "name", "exe", "cmdline", "create_time", "cwd"]
            ):
                try:
                    name = proc.info.get("name")
                    if not name or not self._is_vscode_process(name):
                        continue

                    cmdline = proc.info.get("cmdline") or []

                    # Skip helper processes
                    if self._is_helper_process(cmdline):
                        continue

                    # This is a main process candidate
                    candidates.append(
                        {
                            "pid": proc.info["pid"],
                            "name": name,
                            "exe": proc.info.get("exe", ""),
                            "cmdline": cmdline,
                            "create_time": datetime.fromtimestamp(proc.info["create_time"]),
                            "cwd": proc.info.get("cwd", ""),
                        }
                    )

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

        except Exception as e:
            logger.error(f"Error finding main VS Code process: {e}")
            return None

        if not candidates:
            return None

        # Return the OLDEST process (earliest create_time)
        # This is most likely the main parent process
        candidates.sort(key=lambda x: x["create_time"])
        return candidates[0]

    def find_instance_by_workspace(self, workspace_name: str) -> Optional[VSCodeInstance]:
        """
        Find VS Code instance by workspace name.

        Args:
            workspace_name: Name of the workspace to find

        Returns:
            VSCodeInstance if found, None otherwise
        """
        instances = self.find_vscode_instances()

        for instance in instances:
            if (
                instance.workspace.workspace_name
                and instance.workspace.workspace_name.lower() == workspace_name.lower()
            ):
                return instance

        return None

    def get_terminal_count(self) -> int:
        """
        Get total number of terminals across all VS Code instances.

        Returns:
            Total terminal count
        """
        instances = self.find_vscode_instances()
        return sum(len(inst.terminals) for inst in instances)

    def _is_vscode_process(self, process_name: str) -> bool:
        """
        Check if process name matches VS Code executable.

        Args:
            process_name: Process name from psutil

        Returns:
            True if VS Code process
        """
        return process_name in self.TARGET_NAMES

    def _is_helper_process(self, cmdline: List[str]) -> bool:
        """
        Check if process is a helper process (renderer, gpu, etc.)

        Helper processes have --type= argument.

        Args:
            cmdline: Command-line arguments

        Returns:
            True if helper process (should be filtered out)
        """
        return any("--type=" in arg for arg in cmdline)

    def print_report(self) -> None:
        """
        Print formatted report of all VS Code instances.

        Useful for debugging and CLI output.
        """
        instances = self.find_vscode_instances()

        print("\n" + "=" * 70)
        print(f"VS Code Instance Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70 + "\n")

        if not instances:
            print("No VS Code instances found.")
            return

        for i, inst in enumerate(instances, 1):
            print(f"Instance {i}:")
            print(f"  PID: {inst.pid}")
            print(f"  Executable: {inst.name}")

            if inst.workspace.workspace_name:
                print(f"  Workspace: {inst.workspace.workspace_name}")
                if inst.workspace.workspace_path:
                    print(f"  Path: {inst.workspace.workspace_path}")
                elif inst.workspace.workspace_file:
                    print(f"  Workspace File: {inst.workspace.workspace_file}")
            else:
                print("  Workspace: None (no folder open)")

            print(f"  Terminals: {len(inst.terminals)}")

            for term in inst.terminals:
                print(
                    f"    - PID {term.pid}: {term.shell_type} "
                    f"({term.status}) in {term.cwd}"
                )

            print()

        print(f"Total: {len(instances)} instance(s), {self.get_terminal_count()} terminal(s)")
        print("=" * 70)
