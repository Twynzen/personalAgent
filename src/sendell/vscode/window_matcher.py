"""
Window Matcher

Match terminals to their corresponding VS Code windows by analyzing CWD patterns
and process relationships.

Strategy:
- VS Code spawns all terminals from main process
- Terminals inherit CWD from the workspace they belong to
- Group terminals by CWD to identify which window they belong to
"""

from collections import defaultdict
from typing import Dict, List, Set

from sendell.utils.logger import get_logger
from sendell.vscode.terminal_finder import TerminalInfo

logger = get_logger(__name__)


class WindowMatcher:
    """
    Match terminals to VS Code windows using CWD-based heuristics.

    Since all terminals are children of the main VS Code process,
    we use working directory patterns to infer which window owns which terminals.
    """

    @staticmethod
    def group_terminals_by_workspace(
        terminals: List[TerminalInfo],
    ) -> Dict[str, List[TerminalInfo]]:
        """
        Group terminals by their working directory (CWD).

        Each unique CWD represents a different VS Code workspace window.

        Args:
            terminals: List of all terminals found

        Returns:
            Dictionary mapping CWD -> list of terminals in that directory

        Example:
            {
                'C:\\Users\\Daniel\\Desktop\\Daniel\\sendell': [terminal1, terminal2],
                'C:\\Users\\Daniel\\Desktop\\Daniel\\GSIAF': [terminal3, terminal4],
            }
        """
        grouped = defaultdict(list)

        for terminal in terminals:
            # Normalize CWD (lowercase for matching)
            cwd = terminal.cwd.strip()
            if cwd:
                grouped[cwd].append(terminal)

        return dict(grouped)

    @staticmethod
    def find_workspace_candidates(
        terminals_by_cwd: Dict[str, List[TerminalInfo]]
    ) -> List[Dict]:
        """
        Identify unique workspace candidates from terminal CWDs.

        Args:
            terminals_by_cwd: Terminals grouped by CWD

        Returns:
            List of workspace candidates with:
            - workspace_path: The CWD (likely workspace root)
            - terminal_count: Number of terminals in this workspace
            - terminals: List of TerminalInfo
        """
        candidates = []

        for cwd, terminals in terminals_by_cwd.items():
            candidates.append(
                {
                    "workspace_path": cwd,
                    "workspace_name": cwd.split("\\")[-1],  # Last folder name
                    "terminal_count": len(terminals),
                    "terminals": terminals,
                }
            )

        # Sort by terminal count (most active workspaces first)
        candidates.sort(key=lambda x: x["terminal_count"], reverse=True)

        return candidates
