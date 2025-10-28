"""
MCP tool for agent communication.

Implements:
- respond_to_user: Send messages to user
"""

from typing import Any

from sendell.security.permissions import get_permission_manager
from sendell.utils.logger import get_logger

logger = get_logger(__name__)


def respond_to_user(message: str, requires_approval: bool = False) -> dict[str, Any]:
    """
    Send a message to the user.

    This tool allows the agent to communicate proactively with the user.
    Messages are logged and displayed in the CLI.

    Args:
        message: Message to send to user
        requires_approval: If True, message requests user action

    Returns:
        Dict with message delivery status

    Example:
        >>> respond_to_user("CPU usage is high. Should I close some apps?", True)
        {'delivered': True, 'requires_approval': True}
    """
    # Check permissions (L1+, always allowed)
    pm = get_permission_manager()
    pm.require_permission("respond_to_user")

    logger.info(f"Responding to user (approval: {requires_approval})")

    try:
        # Validate message
        if not message or not isinstance(message, str):
            raise ValueError("message must be a non-empty string")

        # Log the message
        if requires_approval:
            logger.warning(f"[SENDELL APPROVAL REQUEST] {message}")
        else:
            logger.info(f"[SENDELL] {message}")

        # In CLI mode, messages are shown via logger
        # In future UI mode, this would send to frontend

        result = {
            "delivered": True,
            "message": message,
            "requires_approval": requires_approval,
            "timestamp": None,  # Will be added by agent
        }

        return result

    except ValueError as e:
        logger.error(f"Invalid message: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return {"delivered": False, "error": str(e)}
