"""
Project Scanner

Discover development projects by scanning directories for configuration files
and project markers.
"""

import time
from pathlib import Path
from typing import List, Optional, Set

from sendell.projects.parsers import parse_project_config
from sendell.projects.types import (
    Project,
    ProjectConfig,
    ProjectType,
    ScanResult,
    PROJECT_TYPE_MARKERS,
    IGNORE_DIRECTORIES,
)
from sendell.utils.logger import get_logger

logger = get_logger(__name__)


class ProjectScanner:
    """
    Scanner for discovering development projects in file system.

    Features:
    - Recursive directory scanning
    - Project type detection via configuration files
    - Configuration parsing
    - Ignore patterns for optimization
    """

    def __init__(
        self,
        max_depth: int = 3,
        ignore_dirs: Optional[Set[str]] = None,
        timeout_seconds: int = 30,
    ):
        """
        Initialize project scanner.

        Args:
            max_depth: Maximum recursion depth (default 3)
            ignore_dirs: Additional directories to ignore
            timeout_seconds: Max time for entire scan operation
        """
        self.max_depth = max_depth
        self.timeout_seconds = timeout_seconds

        # Combine default ignore dirs with custom ones
        self.ignore_dirs = IGNORE_DIRECTORIES.copy()
        if ignore_dirs:
            self.ignore_dirs.update(ignore_dirs)

        logger.info(f"ProjectScanner initialized (max_depth={max_depth}, timeout={timeout_seconds}s)")

    def scan_directory(self, path: Path) -> ScanResult:
        """
        Scan directory recursively to discover projects.

        Args:
            path: Directory path to scan

        Returns:
            ScanResult with discovered projects
        """
        start_time = time.time()
        projects: List[Project] = []
        errors: List[str] = []

        # Validate path
        if not isinstance(path, Path):
            path = Path(path)

        if not path.exists():
            error_msg = f"Path does not exist: {path}"
            logger.error(error_msg)
            return ScanResult(
                scanned_path=path,
                projects_found=[],
                scan_duration_seconds=0.0,
                errors=[error_msg],
                total_projects=0,
                projects_by_type={},
            )

        if not path.is_dir():
            error_msg = f"Path is not a directory: {path}"
            logger.error(error_msg)
            return ScanResult(
                scanned_path=path,
                projects_found=[],
                scan_duration_seconds=0.0,
                errors=[error_msg],
                total_projects=0,
                projects_by_type={},
            )

        logger.info(f"Scanning directory: {path}")

        try:
            # Recursive scan
            self._scan_recursive(path, depth=0, projects=projects, errors=errors, start_time=start_time)

        except TimeoutError as e:
            error_msg = f"Scan timeout after {self.timeout_seconds}s"
            logger.warning(error_msg)
            errors.append(error_msg)

        except Exception as e:
            error_msg = f"Scan error: {e}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)

        # Calculate summary
        duration = time.time() - start_time
        projects_by_type = {}
        for project in projects:
            type_name = project.project_type.value
            projects_by_type[type_name] = projects_by_type.get(type_name, 0) + 1

        result = ScanResult(
            scanned_path=path,
            projects_found=projects,
            scan_duration_seconds=duration,
            errors=errors,
            total_projects=len(projects),
            projects_by_type=projects_by_type,
        )

        logger.info(
            f"Scan complete: {result.total_projects} projects found in {duration:.2f}s"
        )

        return result

    def _scan_recursive(
        self,
        current_path: Path,
        depth: int,
        projects: List[Project],
        errors: List[str],
        start_time: float,
    ):
        """
        Recursive scanning implementation.

        Args:
            current_path: Current directory being scanned
            depth: Current recursion depth
            projects: List to append discovered projects
            errors: List to append errors
            start_time: Scan start time for timeout check
        """
        # Check timeout
        if time.time() - start_time > self.timeout_seconds:
            raise TimeoutError()

        # Check max depth
        if depth > self.max_depth:
            return

        # Check if directory should be ignored
        if current_path.name in self.ignore_dirs:
            return

        try:
            # Try to detect project in current directory
            project = self.detect_project(current_path)
            if project:
                projects.append(project)
                logger.debug(f"Found project: {project.name} ({project.project_type.value}) at {current_path}")
                # Don't scan subdirectories of detected projects (avoid nested detection)
                return

            # Scan subdirectories if no project detected here
            try:
                for item in current_path.iterdir():
                    if item.is_dir() and item.name not in self.ignore_dirs:
                        self._scan_recursive(
                            item,
                            depth=depth + 1,
                            projects=projects,
                            errors=errors,
                            start_time=start_time,
                        )
            except PermissionError:
                error_msg = f"Permission denied: {current_path}"
                logger.debug(error_msg)
                errors.append(error_msg)

        except Exception as e:
            error_msg = f"Error scanning {current_path}: {e}"
            logger.warning(error_msg)
            errors.append(error_msg)

    def detect_project(self, path: Path) -> Optional[Project]:
        """
        Detect if a directory contains a project by checking for marker files.

        Args:
            path: Directory path to check

        Returns:
            Project object if detected, None otherwise
        """
        # Check each project type's markers
        for project_type, markers in PROJECT_TYPE_MARKERS.items():
            for marker in markers:
                # Handle glob patterns (e.g., *.csproj)
                if "*" in marker:
                    matches = list(path.glob(marker))
                    if matches:
                        config_file = matches[0]
                        return self._create_project(path, project_type, config_file)
                else:
                    config_file = path / marker
                    if config_file.exists():
                        return self._create_project(path, project_type, config_file)

        return None

    def _create_project(
        self,
        path: Path,
        project_type: ProjectType,
        config_file: Path,
    ) -> Project:
        """
        Create a Project object from detected directory.

        Args:
            path: Project directory path
            project_type: Detected project type
            config_file: Path to configuration file

        Returns:
            Project object
        """
        # Parse configuration
        config = parse_project_config(config_file)

        # Determine project name
        if config and config.name:
            name = config.name
        else:
            # Fall back to directory name
            name = path.name

        # Create Project object
        project = Project(
            name=name,
            path=path,
            project_type=project_type,
            config=config,
            config_file=config_file,
        )

        return project

    def scan_multiple_paths(self, paths: List[Path]) -> List[ScanResult]:
        """
        Scan multiple paths and return results for each.

        Args:
            paths: List of directory paths to scan

        Returns:
            List of ScanResult objects
        """
        results = []

        for path in paths:
            result = self.scan_directory(path)
            results.append(result)

        return results
