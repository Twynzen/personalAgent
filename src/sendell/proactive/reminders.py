"""
Reminder System - Personal reminders with actions.

Supports:
- One-time reminders: "Remind me to call doctor tomorrow 10am"
- Recurring reminders: "Remind me to call grandma every Sunday 5pm"
- Action-based reminders: popup, notepad, sound
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class ReminderType(str, Enum):
    """Type of reminder"""

    ONE_TIME = "one_time"  # Single occurrence
    RECURRING = "recurring"  # Repeats (daily, weekly, monthly)
    CONDITIONAL = "conditional"  # Based on context (not implemented in v0.2)


class RecurrencePattern(str, Enum):
    """How often recurring reminders repeat"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Reminder(BaseModel):
    """
    A personal reminder with executable actions.

    Examples:
    - "Remind me to call doctor tomorrow 10am" (one-time, chat message)
    - "Remind me to call grandma every Sunday 5pm" (recurring, popup)
    - "Remind me to exercise 3x week" (recurring, notepad)
    """

    reminder_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique ID")
    user_id: str = Field(default="default_user", description="User this reminder belongs to")

    # Content
    content: str = Field(..., description="What to remind about")
    importance: float = Field(default=0.5, description="Importance 0-1", ge=0.0, le=1.0)

    # Type and timing
    reminder_type: ReminderType = Field(default=ReminderType.ONE_TIME)
    due_at: datetime = Field(..., description="When to trigger this reminder")

    # Recurring settings
    recurrence: Optional[RecurrencePattern] = Field(default=None, description="Recurrence pattern")
    recurrence_day: Optional[str] = Field(
        default=None, description="For weekly: monday, sunday, etc."
    )

    # Action to take (list of action types)
    actions: List[str] = Field(
        default=["chat_message"], description="Actions to execute: chat_message, popup, notepad, sound"
    )

    # State
    sent: bool = Field(default=False, description="Has this reminder been sent?")
    snoozed_until: Optional[datetime] = Field(default=None, description="Snoozed until this time")
    times_snoozed: int = Field(default=0, description="How many times user snoozed")
    completed: bool = Field(default=False, description="User marked as completed")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    last_sent_at: Optional[datetime] = Field(default=None)

    def is_due_now(self) -> bool:
        """Check if reminder is due right now"""
        now = datetime.now()

        # If snoozed, check snooze time
        if self.snoozed_until and now < self.snoozed_until:
            return False

        # If already sent (one-time) or completed, not due
        if self.reminder_type == ReminderType.ONE_TIME:
            if self.sent or self.completed:
                return False

        # Check if due time has passed
        return now >= self.due_at

    def mark_sent(self) -> None:
        """Mark reminder as sent"""
        self.sent = True
        self.last_sent_at = datetime.now()

    def snooze(self, minutes: int = 30) -> None:
        """Snooze reminder for N minutes"""
        self.snoozed_until = datetime.now() + timedelta(minutes=minutes)
        self.times_snoozed += 1

    def complete(self) -> None:
        """Mark reminder as completed"""
        self.completed = True

    def get_next_occurrence(self) -> Optional[datetime]:
        """
        For recurring reminders, calculate next occurrence.

        Returns:
            datetime: Next time this should trigger, or None if one-time
        """
        if self.reminder_type != ReminderType.RECURRING or not self.recurrence:
            return None

        now = datetime.now()
        current_due = self.due_at

        if self.recurrence == RecurrencePattern.DAILY:
            # Next day, same time
            next_due = current_due + timedelta(days=1)
            while next_due <= now:
                next_due += timedelta(days=1)
            return next_due

        elif self.recurrence == RecurrencePattern.WEEKLY:
            # Next week, same day and time
            next_due = current_due + timedelta(weeks=1)
            while next_due <= now:
                next_due += timedelta(weeks=1)
            return next_due

        elif self.recurrence == RecurrencePattern.MONTHLY:
            # Next month, same day and time
            if current_due.month == 12:
                next_due = current_due.replace(year=current_due.year + 1, month=1)
            else:
                next_due = current_due.replace(month=current_due.month + 1)

            while next_due <= now:
                if next_due.month == 12:
                    next_due = next_due.replace(year=next_due.year + 1, month=1)
                else:
                    next_due = next_due.replace(month=next_due.month + 1)

            return next_due

        return None

    def reset_for_next_occurrence(self) -> None:
        """Reset state for recurring reminder's next occurrence"""
        if self.reminder_type == ReminderType.RECURRING:
            next_due = self.get_next_occurrence()
            if next_due:
                self.due_at = next_due
                self.sent = False
                self.snoozed_until = None
                # Don't reset times_snoozed - keep historical data

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON storage"""
        return {
            "reminder_id": self.reminder_id,
            "user_id": self.user_id,
            "content": self.content,
            "importance": self.importance,
            "reminder_type": self.reminder_type.value,
            "due_at": self.due_at.isoformat(),
            "recurrence": self.recurrence.value if self.recurrence else None,
            "recurrence_day": self.recurrence_day,
            "actions": self.actions,
            "sent": self.sent,
            "snoozed_until": self.snoozed_until.isoformat() if self.snoozed_until else None,
            "times_snoozed": self.times_snoozed,
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),
            "last_sent_at": self.last_sent_at.isoformat() if self.last_sent_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Reminder":
        """Create from dictionary (JSON)"""
        return cls(
            reminder_id=data["reminder_id"],
            user_id=data.get("user_id", "default_user"),
            content=data["content"],
            importance=data.get("importance", 0.5),
            reminder_type=ReminderType(data["reminder_type"]),
            due_at=datetime.fromisoformat(data["due_at"]),
            recurrence=RecurrencePattern(data["recurrence"]) if data.get("recurrence") else None,
            recurrence_day=data.get("recurrence_day"),
            actions=data.get("actions", ["chat_message"]),
            sent=data.get("sent", False),
            snoozed_until=datetime.fromisoformat(data["snoozed_until"])
            if data.get("snoozed_until")
            else None,
            times_snoozed=data.get("times_snoozed", 0),
            completed=data.get("completed", False),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_sent_at=datetime.fromisoformat(data["last_sent_at"])
            if data.get("last_sent_at")
            else None,
        )


class ReminderManager:
    """Manages all reminders for the user"""

    def __init__(self):
        self.reminders: Dict[str, Reminder] = {}

    def add_reminder(self, reminder: Reminder) -> str:
        """
        Add a new reminder.

        Returns:
            str: reminder_id
        """
        self.reminders[reminder.reminder_id] = reminder
        return reminder.reminder_id

    def get_reminder(self, reminder_id: str) -> Optional[Reminder]:
        """Get reminder by ID"""
        return self.reminders.get(reminder_id)

    def get_all_reminders(self) -> List[Reminder]:
        """Get all reminders"""
        return list(self.reminders.values())

    def get_due_reminders(self) -> List[Reminder]:
        """Get all reminders that are due now"""
        return [r for r in self.reminders.values() if r.is_due_now()]

    def get_upcoming_reminders(self, hours: int = 24) -> List[Reminder]:
        """Get reminders due in next N hours"""
        now = datetime.now()
        cutoff = now + timedelta(hours=hours)

        upcoming = []
        for reminder in self.reminders.values():
            if not reminder.completed and not reminder.sent:
                if now <= reminder.due_at <= cutoff:
                    upcoming.append(reminder)

        return sorted(upcoming, key=lambda r: r.due_at)

    def delete_reminder(self, reminder_id: str) -> bool:
        """Delete a reminder"""
        if reminder_id in self.reminders:
            del self.reminders[reminder_id]
            return True
        return False

    def process_sent_reminder(self, reminder_id: str) -> None:
        """
        Process a reminder that was just sent.

        For one-time: mark as sent
        For recurring: reset for next occurrence
        """
        reminder = self.get_reminder(reminder_id)
        if not reminder:
            return

        reminder.mark_sent()

        # If recurring, schedule next occurrence
        if reminder.reminder_type == ReminderType.RECURRING:
            reminder.reset_for_next_occurrence()

    def snooze_reminder(self, reminder_id: str, minutes: int = 5) -> bool:
        """
        Snooze a reminder for N minutes.

        Args:
            reminder_id: ID of reminder to snooze
            minutes: How many minutes to snooze (default 5)

        Returns:
            bool: True if snoozed successfully
        """
        reminder = self.get_reminder(reminder_id)
        if not reminder:
            return False

        reminder.snooze(minutes)
        return True

    def dismiss_reminder(self, reminder_id: str) -> bool:
        """
        Dismiss (complete) a reminder.

        For one-time reminders: marks as completed
        For recurring reminders: advances to next occurrence

        Args:
            reminder_id: ID of reminder to dismiss

        Returns:
            bool: True if dismissed successfully
        """
        reminder = self.get_reminder(reminder_id)
        if not reminder:
            return False

        if reminder.reminder_type == ReminderType.ONE_TIME:
            # One-time reminder: mark as completed (will not trigger again)
            reminder.complete()
        else:
            # Recurring reminder: advance to next occurrence
            reminder.reset_for_next_occurrence()

        return True

    def to_dict(self) -> dict:
        """Convert all reminders to dict for JSON storage"""
        return {"reminders": [r.to_dict() for r in self.reminders.values()]}

    @classmethod
    def from_dict(cls, data: dict) -> "ReminderManager":
        """Load reminders from dict (JSON)"""
        manager = cls()
        for reminder_data in data.get("reminders", []):
            reminder = Reminder.from_dict(reminder_data)
            manager.add_reminder(reminder)
        return manager
