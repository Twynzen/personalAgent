"""
Project State Manager

Efficiently determines project states using psutil:
- OFFLINE (red): VS Code project detected, no terminal open
- READY (blue): Terminal open, Claude may or may not be active
- WORKING (green): Terminal open, Claude active and working

Event-driven approach - no unnecessary polling.
"""

import json
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Literal
from datetime import datetime

from sendell.vscode import VSCodeMonitor
from sendell.terminal_control import ClaudeTerminalDetector

ProjectState = Literal['offline', 'ready', 'working']


class ProjectManager:
    """
    Manages VS Code projects and determines their states efficiently.

    State detection logic:
    1. OFFLINE: No terminal process found in project path
    2. READY: Terminal exists, Claude active, bridge.json shows not working
    3. WORKING: Terminal exists, Claude active, bridge.json shows working
    """

    def __init__(self):
        self.vscode_monitor = VSCodeMonitor()
        self.claude_detector = ClaudeTerminalDetector()

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
                    'claude_active': bool,
                    'claude_working': bool
                }
            ]
        """
        # Get VS Code instances
        vscode_instances = self.vscode_monitor.find_vscode_instances()

        # Get Claude processes once (for efficiency)
        claude_processes = self.claude_detector.find_claude_code_processes()

        projects_with_states = []

        for instance in vscode_instances:
            workspace_path = instance.workspace.workspace_path

            # Determine state
            state_info = self._determine_project_state(
                workspace_path,
                claude_processes
            )

            project = {
                'pid': instance.pid,
                'name': instance.workspace.workspace_name,
                'workspace_path': workspace_path,
                'workspace_type': instance.workspace.workspace_type,
                'state': state_info['state'],
                'has_terminal': state_info['has_terminal'],
                'claude_active': state_info['claude_active'],
                'claude_working': state_info['claude_working']
            }

            projects_with_states.append(project)

        return projects_with_states

    def _determine_project_state(
        self,
        workspace_path: str,
        claude_processes: List[Dict]
    ) -> Dict:
        """
        Determine state of a single project.

        Logic:
        1. Check if terminal exists in project path
        2. Check if Claude is active in that terminal
        3. Read bridge.json to see if Claude is working

        Returns:
            {
                'state': 'offline|ready|working',
                'has_terminal': bool,
                'claude_active': bool,
                'claude_working': bool
            }
        """
        # Default state
        state_info = {
            'state': 'offline',
            'has_terminal': False,
            'claude_active': False,
            'claude_working': False
        }

        # Check if Claude is active in this workspace
        claude_in_workspace = [
            proc for proc in claude_processes
            if proc['cwd'] and workspace_path.lower() in proc['cwd'].lower()
        ]

        if not claude_in_workspace:
            # No Claude detected -> OFFLINE
            return state_info

        # Claude detected -> terminal exists and Claude is active
        state_info['has_terminal'] = True
        state_info['claude_active'] = True

        # Check bridge.json to see if working
        bridge_file = Path(workspace_path) / '.sendell' / 'bridge.json'

        if bridge_file.exists():
            try:
                with open(bridge_file, 'r', encoding='utf-8') as f:
                    bridge_data = json.load(f)

                if bridge_data.get('claude_working', False):
                    state_info['state'] = 'working'
                    state_info['claude_working'] = True
                else:
                    state_info['state'] = 'ready'
            except Exception:
                # Error reading file -> assume READY
                state_info['state'] = 'ready'
        else:
            # No bridge file -> just detected, assume READY
            state_info['state'] = 'ready'

        return state_info

    def open_terminal_in_project(self, workspace_path: str) -> Dict:
        """
        Open a terminal in the specified project path.

        Args:
            workspace_path: Full path to the project

        Returns:
            {'success': bool, 'message': str}
        """
        import subprocess

        try:
            # Open cmd in the project directory
            # start cmd /k keeps terminal open and changes directory
            subprocess.Popen(
                f'start cmd /k "cd /d {workspace_path}"',
                shell=True
            )

            return {
                'success': True,
                'message': f'Terminal opened in {workspace_path}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error opening terminal: {str(e)}'
            }

    def create_bridge_file(self, workspace_path: str) -> Dict:
        """
        Create .sendell/bridge.json file in project if it doesn't exist.

        Args:
            workspace_path: Full path to the project

        Returns:
            {'success': bool, 'path': str}
        """
        try:
            sendell_dir = Path(workspace_path) / '.sendell'
            sendell_dir.mkdir(exist_ok=True)

            bridge_file = sendell_dir / 'bridge.json'

            if not bridge_file.exists():
                initial_data = {
                    'project_path': workspace_path,
                    'claude_working': False,
                    'last_task_result': None,
                    'timestamp': datetime.now().isoformat(),
                    'sendell_notes': 'This file is used for Sendell <-> Claude communication'
                }

                with open(bridge_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_data, f, indent=2)

            return {
                'success': True,
                'path': str(bridge_file)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def read_bridge_file(self, workspace_path: str) -> Optional[Dict]:
        """Read bridge.json from project."""
        bridge_file = Path(workspace_path) / '.sendell' / 'bridge.json'

        if not bridge_file.exists():
            return None

        try:
            with open(bridge_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def write_bridge_file(self, workspace_path: str, data: Dict) -> bool:
        """Write to bridge.json in project."""
        try:
            bridge_file = Path(workspace_path) / '.sendell' / 'bridge.json'

            with open(bridge_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            return True
        except Exception:
            return False
