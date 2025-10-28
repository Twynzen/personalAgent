"""
Custom exceptions for Sendell.

All errors inherit from SendellError for easy catching.
"""


class SendellError(Exception):
    """Base exception for all Sendell errors"""

    pass


class ConfigurationError(SendellError):
    """Raised when configuration is invalid or missing"""

    pass


class PermissionDeniedError(SendellError):
    """Raised when action requires higher autonomy level"""

    def __init__(self, action: str, required_level: int, current_level: int):
        self.action = action
        self.required_level = required_level
        self.current_level = current_level
        super().__init__(
            f"Action '{action}' requires L{required_level} but current level is L{current_level}"
        )


class MonitoringError(SendellError):
    """Raised when system monitoring fails"""

    pass


class AutomationError(SendellError):
    """Raised when automation/control action fails"""

    pass


class MCPError(SendellError):
    """Raised when MCP protocol errors occur"""

    pass


class AgentError(SendellError):
    """Raised when agent execution fails"""

    pass


class MemoryError(SendellError):
    """Raised when memory operations fail"""

    pass
