"""
Project Types and Pydantic Models

Defines project types, enums, and data structures for project management.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ProjectType(str, Enum):
    """Supported project types detected by scanner"""

    PYTHON = "python"
    NODEJS = "nodejs"
    RUST = "rust"
    GO = "go"
    JAVA = "java"
    RUBY = "ruby"
    PHP = "php"
    DOTNET = "dotnet"
    CPP = "cpp"
    UNKNOWN = "unknown"


class ProjectStatus(str, Enum):
    """Current status of a project"""

    DISCOVERED = "discovered"  # Just found, not analyzed yet
    ACTIVE = "active"  # Currently running
    STOPPED = "stopped"  # Stopped/idle
    ERROR = "error"  # Has errors
    UNKNOWN = "unknown"


class ProjectConfig(BaseModel):
    """Parsed configuration from project files"""

    name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    dependencies: Dict[str, str] = Field(default_factory=dict)
    dev_dependencies: Dict[str, str] = Field(default_factory=dict)
    scripts: Dict[str, str] = Field(default_factory=dict)
    author: Optional[str] = None
    license: Optional[str] = None
    repository: Optional[str] = None

    # Additional metadata
    python_version: Optional[str] = None  # For Python projects
    node_version: Optional[str] = None  # For Node.js projects
    go_version: Optional[str] = None  # For Go projects
    rust_edition: Optional[str] = None  # For Rust projects


class Project(BaseModel):
    """Represents a discovered development project"""

    project_id: Optional[int] = None  # Database ID (set after insertion)
    name: str
    path: Path
    project_type: ProjectType
    status: ProjectStatus = ProjectStatus.DISCOVERED

    # Configuration
    config: Optional[ProjectConfig] = None
    config_file: Optional[Path] = None  # Path to main config file

    # Metadata
    discovered_at: datetime = Field(default_factory=datetime.now)
    last_scanned_at: Optional[datetime] = None

    # Stats (filled later by monitoring)
    file_count: Optional[int] = None
    total_size_bytes: Optional[int] = None

    @field_validator("path", mode="before")
    @classmethod
    def validate_path(cls, v):
        """Ensure path is a Path object"""
        if isinstance(v, str):
            return Path(v)
        return v

    @field_validator("config_file", mode="before")
    @classmethod
    def validate_config_file(cls, v):
        """Ensure config_file is a Path object"""
        if v is None:
            return v
        if isinstance(v, str):
            return Path(v)
        return v

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            Path: str,
            datetime: lambda v: v.isoformat()
        }


class ScanResult(BaseModel):
    """Result of a directory scan operation"""

    scanned_path: Path
    projects_found: List[Project]
    scan_duration_seconds: float
    errors: List[str] = Field(default_factory=list)

    # Summary
    total_projects: int = 0
    projects_by_type: Dict[str, int] = Field(default_factory=dict)

    @field_validator("scanned_path", mode="before")
    @classmethod
    def validate_scanned_path(cls, v):
        """Ensure scanned_path is a Path object"""
        if isinstance(v, str):
            return Path(v)
        return v

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            Path: str
        }


# Project type detection markers
PROJECT_TYPE_MARKERS = {
    ProjectType.PYTHON: [
        "pyproject.toml",
        "setup.py",
        "requirements.txt",
        "Pipfile",
        "poetry.lock",
    ],
    ProjectType.NODEJS: [
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
    ],
    ProjectType.RUST: [
        "Cargo.toml",
        "Cargo.lock",
    ],
    ProjectType.GO: [
        "go.mod",
        "go.sum",
    ],
    ProjectType.JAVA: [
        "pom.xml",  # Maven
        "build.gradle",  # Gradle
        "build.gradle.kts",
    ],
    ProjectType.RUBY: [
        "Gemfile",
        "Gemfile.lock",
    ],
    ProjectType.PHP: [
        "composer.json",
        "composer.lock",
    ],
    ProjectType.DOTNET: [
        "*.csproj",
        "*.fsproj",
        "*.vbproj",
        "*.sln",
    ],
    ProjectType.CPP: [
        "CMakeLists.txt",
        "Makefile",
        "*.vcxproj",
    ],
}


# Directories to ignore during scanning
IGNORE_DIRECTORIES = {
    # Version control
    ".git",
    ".svn",
    ".hg",

    # Dependencies
    "node_modules",
    "vendor",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "virtualenv",

    # Build outputs
    "build",
    "dist",
    "target",  # Rust/Java
    "out",
    "bin",
    "obj",

    # IDE
    ".vscode",
    ".idea",
    ".vs",

    # OS
    ".DS_Store",
    "Thumbs.db",

    # Other
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    "coverage",
}


# File extensions by project type (for heuristic detection)
PROJECT_TYPE_EXTENSIONS = {
    ProjectType.PYTHON: {".py"},
    ProjectType.NODEJS: {".js", ".ts", ".jsx", ".tsx", ".mjs"},
    ProjectType.RUST: {".rs"},
    ProjectType.GO: {".go"},
    ProjectType.JAVA: {".java"},
    ProjectType.RUBY: {".rb"},
    ProjectType.PHP: {".php"},
    ProjectType.DOTNET: {".cs", ".fs", ".vb"},
    ProjectType.CPP: {".cpp", ".cc", ".cxx", ".c", ".h", ".hpp"},
}
