"""
Permission and autonomy level management.

Implements L1-L5 autonomy levels:
- L1: Monitor Only
- L2: Ask Permission (default)
- L3: Safe Actions
- L4: Modify State
- L5: Full Autonomy
"""

from enum import Enum
from typing import Optional

from sendell.config import AutonomyLevel, get_settings
from sendell.utils.errors import PermissionDeniedError
from sendell.utils.logger import get_logger

logger = get_logger(__name__)


class ActionCategory(str, Enum):
    """Categories of actions with different risk levels"""

    OBSERVE = "observe"  # Read-only, no side effects (L1+)
    QUERY = "query"  # Simple queries, no changes (L1+)
    SAFE_ACTION = "safe_action"  # Open apps, show info (L3+)
    MODIFY_STATE = "modify_state"  # Close apps, move files (L4+)
    SYSTEM_CHANGE = "system_change"  # Install software, change settings (L5)


# Map actions to required autonomy levels
ACTION_REQUIREMENTS = {
    # L1+ (Monitor Only)
    "get_system_health": (ActionCategory.OBSERVE, AutonomyLevel.L1_MONITOR_ONLY),
    "get_active_window": (ActionCategory.OBSERVE, AutonomyLevel.L1_MONITOR_ONLY),
    "list_top_processes": (ActionCategory.OBSERVE, AutonomyLevel.L1_MONITOR_ONLY),
    "respond_to_user": (ActionCategory.QUERY, AutonomyLevel.L1_MONITOR_ONLY),
    # L3+ (Safe Actions)
    "open_application": (ActionCategory.SAFE_ACTION, AutonomyLevel.L3_SAFE_ACTIONS),
    "find_process": (ActionCategory.OBSERVE, AutonomyLevel.L1_MONITOR_ONLY),
    # L4+ (Modify State)
    "kill_process": (ActionCategory.MODIFY_STATE, AutonomyLevel.L4_MODIFY_STATE),
    "close_application": (ActionCategory.MODIFY_STATE, AutonomyLevel.L4_MODIFY_STATE),
    # L5 (Full Autonomy)
    "install_software": (ActionCategory.SYSTEM_CHANGE, AutonomyLevel.L5_FULL_AUTONOMY),
    "change_system_settings": (ActionCategory.SYSTEM_CHANGE, AutonomyLevel.L5_FULL_AUTONOMY),
}


class PermissionManager:
    """
    Manages permissions and autonomy levels.

    Validates actions against current autonomy level and
    handles user approval workflow.
    """

    def __init__(self):
        """Initialize permission manager"""
        self.settings = get_settings()
        self.current_level = self.settings.agent.autonomy_level
        logger.info(f"Permission manager initialized at {self.current_level.name}")

    def check_permission(
        self, action: str, require_approval: bool = False
    ) -> tuple[bool, Optional[str]]:
        """
        Check if action is permitted at current autonomy level.

        Args:
            action: Action name to check
            require_approval: Force user approval even if auto-allowed

        Returns:
            (allowed: bool, reason: str or None)

        Example:
            >>> pm = PermissionManager()
            >>> allowed, reason = pm.check_permission("open_application")
            >>> if not allowed:
            ...     print(reason)
        """
        # Get action requirements
        if action not in ACTION_REQUIREMENTS:
            logger.warning(f"Unknown action: {action}")
            return (False, f"Unknown action: {action}")

        category, required_level = ACTION_REQUIREMENTS[action]

        # Check if current level meets requirement
        if self.current_level < required_level:
            reason = (
                f"Action '{action}' requires {required_level.name} "
                f"but current level is {self.current_level.name}"
            )
            logger.warning(reason)
            return (False, reason)

        # L2 (Ask Permission) - always require approval unless L3+
        if self.current_level == AutonomyLevel.L2_ASK_PERMISSION:
            if category in [
                ActionCategory.SAFE_ACTION,
                ActionCategory.MODIFY_STATE,
                ActionCategory.SYSTEM_CHANGE,
            ]:
                return (False, f"Action '{action}' requires user approval (L2 mode)")

        # If explicitly requiring approval
        if require_approval:
            return (False, f"Action '{action}' requires user approval")

        # Allowed
        logger.debug(f"Action '{action}' permitted at {self.current_level.name}")
        return (True, None)

    def require_permission(self, action: str) -> None:
        """
        Check permission and raise error if denied.

        Args:
            action: Action to check

        Raises:
            PermissionDeniedError: If action not permitted

        Example:
            >>> pm = PermissionManager()
            >>> pm.require_permission("open_application")  # Raises if not allowed
        """
        allowed, reason = self.check_permission(action)
        if not allowed:
            category, required_level = ACTION_REQUIREMENTS.get(
                action, (ActionCategory.QUERY, AutonomyLevel.L1_MONITOR_ONLY)
            )
            raise PermissionDeniedError(action, required_level.value, self.current_level.value)

    def request_user_approval(self, action: str, details: dict) -> bool:
        """
        Request user approval for an action.

        This is a placeholder for future interactive approval workflow.
        In MVP, we'll implement this via CLI prompts.

        Args:
            action: Action requesting approval
            details: Action details to show user

        Returns:
            True if approved, False if denied

        TODO: Implement interactive CLI approval in v0.1
        TODO: Implement web UI approval in v1.0
        """
        logger.info(f"User approval requested for '{action}': {details}")

        # For now, return False (require manual execution)
        # In full implementation, this would prompt user via CLI or UI
        return False

    def get_action_info(self, action: str) -> dict:
        """
        Get information about an action's requirements.

        Args:
            action: Action name

        Returns:
            Dict with action category, required level, description
        """
        if action not in ACTION_REQUIREMENTS:
            return {
                "action": action,
                "known": False,
                "category": None,
                "required_level": None,
            }

        category, required_level = ACTION_REQUIREMENTS[action]
        allowed, reason = self.check_permission(action)

        return {
            "action": action,
            "known": True,
            "category": category.value,
            "required_level": required_level.value,
            "required_level_name": required_level.name,
            "current_level": self.current_level.value,
            "current_level_name": self.current_level.name,
            "allowed": allowed,
            "reason": reason,
        }

    def set_autonomy_level(self, level: AutonomyLevel) -> None:
        """
        Change autonomy level (requires restart in production).

        Args:
            level: New autonomy level

        Note:
            In production, changing autonomy level should require
            configuration file change and restart for security.
        """
        old_level = self.current_level
        self.current_level = level
        logger.warning(
            f"Autonomy level changed: {old_level.name} -> {level.name} "
            "(This should require restart in production)"
        )


# Global permission manager instance
_permission_manager: Optional[PermissionManager] = None


def get_permission_manager() -> PermissionManager:
    """
    Get or create global permission manager.

    Returns:
        PermissionManager instance
    """
    global _permission_manager
    if _permission_manager is None:
        _permission_manager = PermissionManager()
    return _permission_manager
