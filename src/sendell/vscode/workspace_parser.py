"""
Workspace Parser

Parse VS Code command-line arguments to extract workspace information.
Handles single folders, multi-root workspaces, and URI encoding.

Based on investigation: investigacionvscodemonitoring.txt (Part 2, lines 192-353)
"""

import json
import os
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from sendell.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class WorkspaceInfo:
    """Information about a VS Code workspace"""

    workspace_type: str  # 'none', 'folder', 'workspace'
    workspace_path: Optional[str] = None
    workspace_name: Optional[str] = None
    workspace_file: Optional[str] = None  # For multi-root workspaces
    folders: Optional[List[Dict]] = None  # For multi-root workspaces


class WorkspaceParser:
    """
    Parse VS Code workspace information from command-line arguments.

    VS Code supports three workspace modes:
    1. Single Folder: One directory opened
    2. Multi-Root Workspace: Multiple folders in .code-workspace file
    3. No Folder: VS Code opened without workspace
    """

    @staticmethod
    def parse_from_cmdline(cmdline: List[str]) -> WorkspaceInfo:
        """
        Parse workspace information from VS Code command-line arguments.

        Args:
            cmdline: Command-line arguments list from process

        Returns:
            WorkspaceInfo with parsed workspace data

        Examples:
            # Single folder (path)
            ['Code.exe', 'C:\\Projects\\MyApp']

            # Single folder (URI)
            ['Code.exe', '--folder-uri=file:///C:/Projects/MyApp']

            # Multi-root workspace
            ['Code.exe', 'C:\\Projects\\MyWorkspace.code-workspace']
        """
        workspace_info = WorkspaceInfo(workspace_type="none")

        if not cmdline or len(cmdline) < 2:
            return workspace_info

        # Check for --folder-uri or --file-uri arguments
        for arg in cmdline:
            if arg.startswith("--folder-uri="):
                uri = arg.split("=", 1)[1]
                path = WorkspaceParser._uri_to_path(uri)
                if path:
                    workspace_info.workspace_type = "folder"
                    workspace_info.workspace_path = path
                    workspace_info.workspace_name = os.path.basename(path)
                return workspace_info

            if arg.startswith("--file-uri="):
                uri = arg.split("=", 1)[1]
                path = WorkspaceParser._uri_to_path(uri)
                if path and path.endswith(".code-workspace"):
                    workspace_info.workspace_type = "workspace"
                    workspace_info.workspace_file = path
                    workspace_info.workspace_name = os.path.splitext(
                        os.path.basename(path)
                    )[0]
                    # Parse workspace file
                    workspace_info.folders = WorkspaceParser._parse_workspace_file(path)
                return workspace_info

        # Check for positional path arguments
        for arg in cmdline[1:]:
            if arg.startswith("--") or arg.startswith("-"):
                continue

            if os.path.exists(arg):
                if arg.endswith(".code-workspace"):
                    workspace_info.workspace_type = "workspace"
                    workspace_info.workspace_file = arg
                    workspace_info.workspace_name = os.path.splitext(
                        os.path.basename(arg)
                    )[0]
                    workspace_info.folders = WorkspaceParser._parse_workspace_file(arg)
                elif os.path.isdir(arg):
                    workspace_info.workspace_type = "folder"
                    workspace_info.workspace_path = arg
                    workspace_info.workspace_name = os.path.basename(arg)
                return workspace_info

        return workspace_info

    @staticmethod
    def _uri_to_path(uri: str) -> Optional[str]:
        """
        Convert file:/// URI to Windows file path.

        Args:
            uri: File URI string (e.g., file:///C:/path/to/folder)

        Returns:
            Windows file path or None if invalid

        Examples:
            'file:///C:/Projects/App' -> 'C:\\Projects\\App'
            'file:///C:/My%20Projects/App' -> 'C:\\My Projects\\App'
        """
        if not uri.startswith("file:///"):
            return None

        # Remove file:/// prefix
        path = uri[8:]

        # URL decode (handles %20, %23, etc.)
        path = urllib.parse.unquote(path)

        # Convert forward slashes to backslashes (Windows)
        path = path.replace("/", "\\")

        return path if path else None

    @staticmethod
    def _parse_workspace_file(workspace_file: str) -> List[Dict]:
        """
        Parse .code-workspace file to extract folder information.

        .code-workspace files are JSON:
        {
          "folders": [
            {"path": "folder1", "name": "Project 1"},
            {"path": "C:\\absolute\\path\\folder2", "name": "Project 2"}
          ],
          "settings": {}
        }

        Args:
            workspace_file: Path to .code-workspace file

        Returns:
            List of folder dictionaries with 'path' and 'name'
        """
        try:
            with open(workspace_file, "r", encoding="utf-8") as f:
                workspace_data = json.load(f)

            folders = []
            for folder in workspace_data.get("folders", []):
                folder_path = folder.get("path", "")

                # Resolve relative paths
                if not os.path.isabs(folder_path):
                    workspace_dir = os.path.dirname(workspace_file)
                    folder_path = os.path.normpath(os.path.join(workspace_dir, folder_path))

                folders.append(
                    {
                        "path": folder_path,
                        "name": folder.get("name", os.path.basename(folder_path)),
                    }
                )

            return folders

        except Exception as e:
            logger.error(f"Failed to parse workspace file {workspace_file}: {e}")
            return []
