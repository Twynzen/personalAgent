"""
Project State Manager - SIMPLIFIED VERSION

Efficiently determines project states using TerminalManager + bridge.json:
- OFFLINE (red): VS Code project detected, NO terminal connected from dashboard
- READY (blue): Terminal connected from dashboard, status='idle' in bridge.json
- WORKING (green): Terminal connected from dashboard, status='working' in bridge.json

Architecture:
1. TerminalManager = Source of truth for terminal existence
2. bridge.json = Source of truth for terminal activity state
3. NO external process detection (ClaudeTerminalDetector removed)
"""

from typing import Dict, List, Literal

from sendell.vscode import VSCodeMonitor
from sendell.terminal_manager import get_terminal_manager
from sendell.project_manager.bridge import get_terminal_status, create_bridge_file
from sendell.utils.logger import get_logger

logger = get_logger(__name__)

ProjectState = Literal['offline', 'ready', 'working']


class ProjectManager:
    """
    Manages VS Code projects and determines their states.

    State detection logic (SIMPLIFIED):
    1. Get VS Code instances from VSCodeMonitor
    2. For each project:
       - Check if TerminalManager has terminal for this project (by PID)
       - If NO terminal → OFFLINE
       - If terminal exists:
         - Read bridge.json for status
         - If status='working' → WORKING
         - If status='idle' or no bridge → READY
    """

    def __init__(self):
        self.vscode_monitor = VSCodeMonitor()
        self.terminal_manager = get_terminal_manager()

    def get_projects_with_states(self) -> List[Dict]:
        """
        Get all VS Code projects with their current states.

        Returns:
            List of projects with state information:
            [
                {
                    'pid': 12345,
                    'name': 'sendell',
                    'workspace_path': 'C:\\...\\sendell',
                    'workspace_type': 'folder',
                    'state': 'offline|ready|working',
                    'has_terminal': bool,
                    'bridge_status': 'idle|working|error',
                    'current_task': str | None
                }
            ]
        """
        # Get VS Code instances
        vscode_instances = self.vscode_monitor.find_vscode_instances()

        projects_with_states = []

        for instance in vscode_instances:
            workspace_path = instance.workspace.workspace_path
            project_pid = instance.pid

            # Determine state
            state_info = self._determine_project_state(project_pid, workspace_path)

            project = {
                'pid': project_pid,
                'name': instance.workspace.workspace_name,
                'workspace_path': workspace_path,
                'workspace_type': instance.workspace.workspace_type,
                'state': state_info['state'],
                'has_terminal': state_info['has_terminal'],
                'bridge_status': state_info['bridge_status'],
                'current_task': state_info['current_task']
            }

            projects_with_states.append(project)

        return projects_with_states

    def _determine_project_state(
        self,
        project_pid: int,
        workspace_path: str
    ) -> Dict:
        """
        Determine state of a single project.

        Logic:
        1. Check if TerminalManager has terminal for this project_pid
        2. If NO terminal → OFFLINE
        3. If terminal exists:
           - Read bridge.json for status
           - status='working' → WORKING
           - status='idle' → READY
           - no bridge or error → READY (default)

        Args:
            project_pid: VS Code process PID
            workspace_path: Project workspace path

        Returns:
            {
                'state': 'offline|ready|working',
                'has_terminal': bool,
                'bridge_status': 'idle|working|error',
                'current_task': str | None
            }
        """
        # Default state
        state_info = {
            'state': 'offline',
            'has_terminal': False,
            'bridge_status': 'idle',
            'current_task': None
        }

        # Step 1: Check if terminal exists in TerminalManager
        terminal_id = str(project_pid)
        terminal = self.terminal_manager.get_terminal(terminal_id)

        if not terminal:
            # No terminal connected from dashboard → OFFLINE
            logger.debug(f"Project {project_pid} has no terminal → OFFLINE")
            return state_info

        # Step 2: Terminal exists → has_terminal = True
        state_info['has_terminal'] = True

        # Check if terminal is actually running
        if not terminal.is_running():
            # Terminal died but not cleaned up yet → OFFLINE
            logger.debug(f"Project {project_pid} terminal not running → OFFLINE")
            state_info['has_terminal'] = False
            return state_info

        # Step 3: Read bridge.json for activity status
        bridge_status = get_terminal_status(workspace_path)
        state_info['bridge_status'] = bridge_status

        # Get current task from bridge if available
        from sendell.project_manager.bridge import read_bridge_file
        bridge_data = read_bridge_file(workspace_path)
        if bridge_data:
            state_info['current_task'] = bridge_data.get('current_task')

        # Step 4: Determine final state based on bridge status
        if bridge_status == 'working':
            state_info['state'] = 'working'
            logger.debug(f"Project {project_pid} terminal working → WORKING")
        else:
            # 'idle' or 'error' → READY
            state_info['state'] = 'ready'
            logger.debug(f"Project {project_pid} terminal idle → READY")

        return state_info

    def create_bridge_file(self, workspace_path: str, project_name: str = "Unknown") -> Dict:
        """
        Create .sendell/bridge.json file in project if it doesn't exist.

        Args:
            workspace_path: Full path to the project
            project_name: Name of the project

        Returns:
            {'success': bool, 'path': str, 'created': bool}
        """
        return create_bridge_file(workspace_path, project_name)
