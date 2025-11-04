"""
VS Code Integration Manager

Central manager for VS Code integration with intelligent filtering
to prevent token saturation and memory overflow.
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List

from .types import ProjectContext, TerminalSession, VSCodeEvent

logger = logging.getLogger(__name__)


class VSCodeIntegrationManager:
    """
    Manages VS Code integration state with aggressive memory optimization.

    Key features:
    - Filters dev server noise (webpack, vite, HMR, etc.)
    - Keeps only tail buffers (last 20 lines per terminal)
    - Auto-detects and extracts errors
    - Limits stored projects (max 10, LRU eviction)
    - Provides aggregated stats instead of raw text
    """

    # Dev server patterns (high-output noise)
    DEV_SERVER_PATTERNS = [
        r'webpack compiled',
        r'HMR.*update',
        r'File change detected',
        r'Compiled successfully',
        r'compiled.*successfully',
        r'vite.*hmr update',
        r'\[vite\]',
        r'waiting for file changes',
    ]

    # Error detection patterns
    ERROR_PATTERNS = [
        r'\berror\b',
        r'\bfailed\b',
        r'\bexception\b',
        r'\btraceback\b',
        r'\[ERROR\]',
        r'ERROR:',
        r'Error:',
        r'SyntaxError',
        r'TypeError',
        r'ReferenceError',
        r'ModuleNotFoundError',
    ]

    # Claude Code detection patterns
    CLAUDE_CODE_PATTERNS = [
        r'Read\(',
        r'Write\(',
        r'Edit\(',
        r'Bash\(',
        r'Grep\(',
        r'Glob\(',
    ]

    def __init__(self, max_projects: int = 10):
        """
        Initialize manager.

        Args:
            max_projects: Maximum projects to keep in memory (LRU eviction)
        """
        self.projects: Dict[str, ProjectContext] = {}
        self.max_projects = max_projects

        # Compiled regex patterns for performance
        self._dev_server_regex = re.compile(
            '|'.join(self.DEV_SERVER_PATTERNS),
            re.IGNORECASE
        )
        self._error_regex = re.compile(
            '|'.join(self.ERROR_PATTERNS),
            re.IGNORECASE
        )
        self._claude_regex = re.compile(
            '|'.join(self.CLAUDE_CODE_PATTERNS)
        )

        logger.info("VSCodeIntegrationManager initialized")

    def handle_event(self, event: VSCodeEvent) -> None:
        """
        Process event from VS Code extension.

        Routes to appropriate handler based on event category.
        """
        try:
            if event.category == 'terminal':
                self._handle_terminal_event(event)
            elif event.category == 'system':
                self._handle_system_event(event)
            elif event.category == 'claude':
                self._handle_claude_event(event)
            else:
                logger.debug(f"Unhandled event category: {event.category}")

        except Exception as e:
            logger.error(f"Error handling event: {e}", exc_info=True)

    def _handle_system_event(self, event: VSCodeEvent) -> None:
        """Handle system events (workspace registration, etc.)"""
        payload = event.payload

        if 'workspaces' in payload:
            # Extension handshake - register workspaces
            for ws in payload['workspaces']:
                workspace_path = ws.get('path', '')
                workspace_name = ws.get('name', 'unknown')

                if workspace_path not in self.projects:
                    self._add_project(workspace_path, workspace_name)
                    logger.info(f"Registered workspace: {workspace_name}")

    def _handle_terminal_event(self, event: VSCodeEvent) -> None:
        """
        Handle terminal events with intelligent filtering.

        Filters:
        - Dev server noise (only keep errors)
        - Excessive output (tail buffer only)
        - Empty/whitespace lines
        """
        payload = event.payload
        event_type = payload.get('type')

        if event_type == 'command_start':
            self._handle_command_start(payload)
        elif event_type == 'command_end':
            self._handle_command_end(payload)
        elif event_type == 'output':
            self._handle_terminal_output(payload)

    def _handle_command_start(self, payload: dict) -> None:
        """Handle command start event"""
        workspace = payload.get('workspace', 'unknown')
        terminal_name = payload.get('terminal', 'unknown')
        command = payload.get('command', '')

        session = self._get_or_create_terminal(workspace, terminal_name)
        session.last_command = command
        session.total_commands += 1

        # Detect dev server commands
        dev_server_cmds = ['npm run dev', 'vite', 'webpack-dev-server', 'ng serve']
        if any(cmd in command for cmd in dev_server_cmds):
            session.is_dev_server = True
            logger.info(f"Detected dev server: {terminal_name} in {workspace}")

    def _handle_command_end(self, payload: dict) -> None:
        """Handle command completion event"""
        workspace = payload.get('workspace', 'unknown')
        terminal_name = payload.get('terminal', 'unknown')
        exit_code = payload.get('exitCode', 0)

        session = self._get_or_create_terminal(workspace, terminal_name)
        session.last_exit_code = exit_code

        if exit_code != 0:
            logger.warning(f"Command failed in {terminal_name}: exit code {exit_code}")

    def _handle_terminal_output(self, payload: dict) -> None:
        """
        Handle terminal output with aggressive filtering.

        Strategy:
        1. If dev server output -> only keep if contains error
        2. If normal output -> keep last 20 lines
        3. Always extract and store errors separately
        """
        workspace = payload.get('workspace', 'unknown')
        terminal_name = payload.get('terminal', 'unknown')
        output = payload.get('output', '')

        if not output.strip():
            return  # Ignore empty output

        session = self._get_or_create_terminal(workspace, terminal_name)

        # Check if this is dev server noise
        is_dev_noise = session.is_dev_server and self._is_dev_server_output(output)

        if is_dev_noise:
            # Dev server noise: ONLY keep if it has errors
            if self._contains_error(output):
                logger.debug(f"Dev server error detected in {terminal_name}")
                self._extract_and_store_errors(session, output)
            # Otherwise, IGNORE the output completely
            return

        # Normal output: store in tail buffer
        session.add_output(output)

        # Extract errors if any
        if self._contains_error(output):
            self._extract_and_store_errors(session, output)

        # Update project stats
        project = self.projects.get(workspace)
        if project:
            project.update_stats()

    def _handle_claude_event(self, event: VSCodeEvent) -> None:
        """Handle Claude Code detection events"""
        payload = event.payload
        workspace = payload.get('workspace', 'unknown')
        terminal_name = payload.get('terminal', 'unknown')

        session = self._get_or_create_terminal(workspace, terminal_name)
        session.is_claude_code = True

        logger.info(f"Claude Code detected: {terminal_name} in {workspace}")

        # Update project flag
        project = self.projects.get(workspace)
        if project:
            project.has_claude_code = True

    def _is_dev_server_output(self, output: str) -> bool:
        """
        Check if output is dev server noise.

        Returns:
            True if output matches dev server patterns
        """
        return bool(self._dev_server_regex.search(output))

    def _contains_error(self, text: str) -> bool:
        """
        Check if text contains error patterns.

        Returns:
            True if any error pattern matches
        """
        return bool(self._error_regex.search(text))

    def _extract_and_store_errors(self, session: TerminalSession, output: str) -> None:
        """
        Extract error lines from output and store them.

        Only stores the actual error lines, not full output.
        """
        lines = output.split('\n')
        for line in lines:
            if self._contains_error(line) and line.strip():
                session.add_error(line.strip())

    def _get_or_create_terminal(
        self,
        workspace: str,
        terminal_name: str
    ) -> TerminalSession:
        """
        Get or create terminal session.

        Auto-creates project if it doesn't exist.
        """
        # Ensure project exists
        if workspace not in self.projects:
            self._add_project(workspace, workspace)

        project = self.projects[workspace]
        return project.add_terminal(terminal_name)

    def _add_project(self, workspace_path: str, workspace_name: str) -> None:
        """
        Add new project with LRU eviction if at capacity.
        """
        # Check if at capacity
        if len(self.projects) >= self.max_projects:
            self._evict_least_recently_used()

        self.projects[workspace_path] = ProjectContext(
            workspace_path=workspace_path,
            name=workspace_name,
        )

        logger.info(f"Added project: {workspace_name}")

    def _evict_least_recently_used(self) -> None:
        """
        Evict least recently used project.

        Based on last_activity timestamp.
        """
        if not self.projects:
            return

        oldest_key = min(
            self.projects.keys(),
            key=lambda k: self.projects[k].last_activity
        )

        evicted_name = self.projects[oldest_key].name
        del self.projects[oldest_key]

        logger.info(f"Evicted project (LRU): {evicted_name}")

    def get_project(self, name_or_path: str) -> Optional[ProjectContext]:
        """
        Get project by name or path.

        Args:
            name_or_path: Project name or workspace path

        Returns:
            ProjectContext if found, None otherwise
        """
        # Try exact match by path
        if name_or_path in self.projects:
            return self.projects[name_or_path]

        # Try match by name
        for project in self.projects.values():
            if project.name == name_or_path:
                return project

        return None

    def get_all_projects(self) -> List[ProjectContext]:
        """Get all active projects"""
        return list(self.projects.values())

    def get_terminal(
        self,
        project_name: str,
        terminal_name: str
    ) -> Optional[TerminalSession]:
        """Get specific terminal session"""
        project = self.get_project(project_name)
        if not project:
            return None

        return project.get_terminal(terminal_name)

    def cleanup_old_sessions(self, max_age_hours: int = 24) -> None:
        """
        Remove inactive terminal sessions.

        Args:
            max_age_hours: Max hours of inactivity before removal
        """
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        removed_count = 0

        for project in self.projects.values():
            inactive_terminals = [
                name for name, session in project.terminals.items()
                if session.last_activity < cutoff
            ]

            for terminal_name in inactive_terminals:
                project.remove_terminal(terminal_name)
                removed_count += 1

        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} inactive terminals")


# Global singleton instance
_manager_instance: Optional[VSCodeIntegrationManager] = None


def get_manager() -> VSCodeIntegrationManager:
    """
    Get global manager instance.

    Returns:
        Singleton VSCodeIntegrationManager instance
    """
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = VSCodeIntegrationManager()
    return _manager_instance
