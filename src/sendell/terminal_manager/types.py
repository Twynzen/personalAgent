"""
Terminal Manager Types

Data models for terminal management system.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class ProcessState(str, Enum):
    """Terminal process states"""
    STARTING = "starting"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class TerminalInfo(BaseModel):
    """Information about a managed terminal"""
    terminal_id: str = Field(description="Unique terminal identifier (project_pid)")
    workspace_path: str = Field(description="Project workspace path")
    project_name: str = Field(description="Project name")
    state: ProcessState = Field(description="Current process state")
    pid: Optional[int] = Field(None, description="Process ID if running")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    last_activity: datetime = Field(default_factory=datetime.now, description="Last activity timestamp")

    class Config:
        use_enum_values = True


class TerminalCommand(BaseModel):
    """Command to send to terminal"""
    command: str = Field(description="Command text to execute")
    terminal_id: str = Field(description="Target terminal ID")


class TerminalOutput(BaseModel):
    """Output from terminal"""
    terminal_id: str = Field(description="Source terminal ID")
    stream: str = Field(description="Stream type: stdout or stderr")
    data: str = Field(description="Output data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Output timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TerminalStatus(BaseModel):
    """Status update from terminal"""
    terminal_id: str = Field(description="Terminal ID")
    state: ProcessState = Field(description="Current state")
    exit_code: Optional[int] = Field(None, description="Exit code if stopped")
    message: Optional[str] = Field(None, description="Status message")

    class Config:
        use_enum_values = True
