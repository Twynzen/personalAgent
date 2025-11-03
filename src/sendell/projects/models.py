"""
SQLAlchemy Database Models for Project Management

7 tables for comprehensive project tracking:
1. projects - Core project metadata
2. project_configs - Parsed configuration files
3. project_metrics - Resource usage metrics
4. project_logs - Aggregated logs
5. project_errors - Structured error tracking
6. project_commands - Runnable commands per project
7. project_health_checks - Health status history
"""

from datetime import datetime
from pathlib import Path

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sendell.projects.types import ProjectType, ProjectStatus

Base = declarative_base()


class ProjectModel(Base):
    """Core project metadata table"""

    __tablename__ = "projects"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Core fields
    name = Column(String(255), nullable=False)
    path = Column(String(1024), nullable=False, unique=True)  # Absolute path
    project_type = Column(SQLEnum(ProjectType), nullable=False)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DISCOVERED)

    # Metadata
    discovered_at = Column(DateTime, default=datetime.now, nullable=False)
    last_scanned_at = Column(DateTime, nullable=True)
    file_count = Column(Integer, nullable=True)
    total_size_bytes = Column(Integer, nullable=True)

    # Relationships
    configs = relationship("ProjectConfigModel", back_populates="project", cascade="all, delete-orphan")
    metrics = relationship("ProjectMetricModel", back_populates="project", cascade="all, delete-orphan")
    logs = relationship("ProjectLogModel", back_populates="project", cascade="all, delete-orphan")
    errors = relationship("ProjectErrorModel", back_populates="project", cascade="all, delete-orphan")
    commands = relationship("ProjectCommandModel", back_populates="project", cascade="all, delete-orphan")
    health_checks = relationship("ProjectHealthCheckModel", back_populates="project", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_project_type", "project_type"),
        Index("idx_project_status", "status"),
        Index("idx_project_path", "path"),
    )

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', type={self.project_type.value})>"


class ProjectConfigModel(Base):
    """Parsed configuration files (package.json, pyproject.toml, etc.)"""

    __tablename__ = "project_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Config data (stored as JSON)
    config_json = Column(JSON, nullable=False)  # Full parsed config
    config_file_path = Column(String(1024), nullable=True)  # Path to config file

    # Metadata
    parsed_at = Column(DateTime, default=datetime.now, nullable=False)

    # Relationship
    project = relationship("ProjectModel", back_populates="configs")

    __table_args__ = (
        Index("idx_config_project", "project_id"),
    )

    def __repr__(self):
        return f"<ProjectConfig(id={self.id}, project_id={self.project_id})>"


class ProjectMetricModel(Base):
    """Resource usage metrics (CPU, memory, etc.)"""

    __tablename__ = "project_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Resource metrics
    cpu_percent = Column(Float, nullable=True)
    memory_mb = Column(Float, nullable=True)
    disk_usage_mb = Column(Float, nullable=True)

    # Process info
    process_id = Column(Integer, nullable=True)  # PID if running
    is_running = Column(Boolean, default=False)

    # Timing
    uptime_seconds = Column(Float, nullable=True)  # How long has it been running
    measured_at = Column(DateTime, default=datetime.now, nullable=False)

    # Relationship
    project = relationship("ProjectModel", back_populates="metrics")

    __table_args__ = (
        Index("idx_metric_project", "project_id"),
        Index("idx_metric_measured_at", "measured_at"),
    )

    def __repr__(self):
        return f"<ProjectMetric(id={self.id}, cpu={self.cpu_percent}, mem={self.memory_mb})>"


class ProjectLogModel(Base):
    """Aggregated logs from project execution"""

    __tablename__ = "project_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Log data
    log_text = Column(Text, nullable=False)
    log_level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, DEBUG
    source = Column(String(100), nullable=True)  # stdout, stderr, file

    # Metadata
    logged_at = Column(DateTime, default=datetime.now, nullable=False)

    # Relationship
    project = relationship("ProjectModel", back_populates="logs")

    __table_args__ = (
        Index("idx_log_project", "project_id"),
        Index("idx_log_level", "log_level"),
        Index("idx_log_logged_at", "logged_at"),
    )

    def __repr__(self):
        return f"<ProjectLog(id={self.id}, level={self.log_level}, text='{self.log_text[:50]}...')>"


class ProjectErrorModel(Base):
    """Structured error tracking"""

    __tablename__ = "project_errors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Error details
    error_type = Column(String(100), nullable=False)  # SyntaxError, ImportError, etc.
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)

    # Location
    file_path = Column(String(1024), nullable=True)
    line_number = Column(Integer, nullable=True)

    # Status
    resolved = Column(Boolean, default=False)

    # Metadata
    detected_at = Column(DateTime, default=datetime.now, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    # Relationship
    project = relationship("ProjectModel", back_populates="errors")

    __table_args__ = (
        Index("idx_error_project", "project_id"),
        Index("idx_error_type", "error_type"),
        Index("idx_error_resolved", "resolved"),
    )

    def __repr__(self):
        return f"<ProjectError(id={self.id}, type={self.error_type}, resolved={self.resolved})>"


class ProjectCommandModel(Base):
    """Runnable commands for each project (npm start, pytest, etc.)"""

    __tablename__ = "project_commands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Command details
    command = Column(String(500), nullable=False)  # Actual command to run
    description = Column(String(255), nullable=True)  # Human-readable description
    command_type = Column(String(50), nullable=True)  # start, test, build, dev, etc.

    # Settings
    requires_approval = Column(Boolean, default=True)  # Needs user confirmation
    auto_restart = Column(Boolean, default=False)  # Auto-restart on failure

    # Usage stats
    times_run = Column(Integer, default=0)
    last_run_at = Column(DateTime, nullable=True)
    last_success = Column(Boolean, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # Relationship
    project = relationship("ProjectModel", back_populates="commands")

    __table_args__ = (
        Index("idx_command_project", "project_id"),
        Index("idx_command_type", "command_type"),
    )

    def __repr__(self):
        return f"<ProjectCommand(id={self.id}, cmd='{self.command}', type={self.command_type})>"


class ProjectHealthCheckModel(Base):
    """Health check history and status"""

    __tablename__ = "project_health_checks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Health status
    overall_status = Column(String(20), nullable=False)  # healthy, warning, error
    checks_json = Column(JSON, nullable=False)  # Detailed check results

    # Individual checks (for quick filtering)
    build_status = Column(Boolean, nullable=True)
    test_status = Column(Boolean, nullable=True)
    dependencies_ok = Column(Boolean, nullable=True)
    no_security_issues = Column(Boolean, nullable=True)

    # Metadata
    checked_at = Column(DateTime, default=datetime.now, nullable=False)

    # Relationship
    project = relationship("ProjectModel", back_populates="health_checks")

    __table_args__ = (
        Index("idx_health_project", "project_id"),
        Index("idx_health_status", "overall_status"),
        Index("idx_health_checked_at", "checked_at"),
    )

    def __repr__(self):
        return f"<ProjectHealthCheck(id={self.id}, status={self.overall_status})>"


# Database initialization helper
def init_database(engine):
    """
    Initialize database schema.

    Args:
        engine: SQLAlchemy engine
    """
    Base.metadata.create_all(engine)


def get_project_by_path(session, path: Path):
    """
    Get project by path.

    Args:
        session: SQLAlchemy session
        path: Project path

    Returns:
        ProjectModel or None
    """
    return session.query(ProjectModel).filter_by(path=str(path)).first()
