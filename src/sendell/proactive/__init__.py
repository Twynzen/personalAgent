"""
Proactive Agent System for Sendell.

Enables temporal awareness, personal memory, reminders, and proactive actions.
"""

from .identity import AgentIdentity, RelationshipPhase
from .temporal_clock import TemporalClock, TimeContext
from .reminders import Reminder, ReminderType, ReminderManager
from .reminder_actions import ReminderAction, ActionType, execute_reminder_action
from .proactive_loop import ProactiveLoop

__all__ = [
    "AgentIdentity",
    "RelationshipPhase",
    "TemporalClock",
    "TimeContext",
    "Reminder",
    "ReminderType",
    "ReminderManager",
    "ReminderAction",
    "ActionType",
    "execute_reminder_action",
    "ProactiveLoop",
]
