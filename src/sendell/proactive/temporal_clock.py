"""
Temporal Clock - Agent's understanding of time.

The agent knows what time it is and what that means contextually.
"""

from datetime import datetime, time
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TimeContext(str, Enum):
    """Contextual meaning of current time"""

    MORNING_ROUTINE = "morning_routine"  # 6am-9am: Waking up, breakfast
    WORK_HOURS = "work_hours"  # 9am-12pm, 2pm-6pm: Focused work time
    LUNCH_TIME = "lunch_time"  # 12pm-2pm: Break, lunch
    EVENING_ROUTINE = "evening_routine"  # 6pm-9pm: Winding down, dinner
    NIGHT_TIME = "night_time"  # 9pm-11pm: Relaxation, prep for sleep
    SLEEP_TIME = "sleep_time"  # 11pm-6am: Should not disturb


class TemporalClock(BaseModel):
    """
    Agent's temporal awareness system.

    Knows:
    - What time it is
    - What that time means contextually
    - Optimal timing for interventions
    """

    user_timezone: str = "America/Bogota"  # Default, can be configured

    def get_current_time(self) -> datetime:
        """Get current time"""
        return datetime.now()

    def get_current_time_context(self) -> TimeContext:
        """
        Determine what the current time means contextually.

        Returns:
            TimeContext: The contextual meaning of current time
        """
        now = self.get_current_time()
        current_hour = now.hour

        if 6 <= current_hour < 9:
            return TimeContext.MORNING_ROUTINE
        elif 9 <= current_hour < 12:
            return TimeContext.WORK_HOURS
        elif 12 <= current_hour < 14:
            return TimeContext.LUNCH_TIME
        elif 14 <= current_hour < 18:
            return TimeContext.WORK_HOURS
        elif 18 <= current_hour < 21:
            return TimeContext.EVENING_ROUTINE
        elif 21 <= current_hour < 23:
            return TimeContext.NIGHT_TIME
        else:  # 23-6
            return TimeContext.SLEEP_TIME

    def is_good_time_to_interrupt(self) -> bool:
        """
        Determine if current time is appropriate for proactive intervention.

        Returns:
            bool: True if it's a good time to reach out
        """
        context = self.get_current_time_context()

        # Never interrupt during sleep
        if context == TimeContext.SLEEP_TIME:
            return False

        # Morning and evening routines are good times (user more relaxed)
        if context in [TimeContext.MORNING_ROUTINE, TimeContext.EVENING_ROUTINE]:
            return True

        # Lunch time is okay for non-urgent things
        if context == TimeContext.LUNCH_TIME:
            return True

        # Work hours: only for important things
        if context == TimeContext.WORK_HOURS:
            return False  # Conservative: don't interrupt work unless urgent

        # Night time: only for urgent reminders
        if context == TimeContext.NIGHT_TIME:
            return False  # Let user relax

        return True

    def get_optimal_reminder_time(self, importance: float) -> Optional[datetime]:
        """
        Calculate optimal time to send a reminder based on importance.

        Args:
            importance: 0-1, how important the reminder is

        Returns:
            datetime: When to send the reminder, or None if send now
        """
        context = self.get_current_time_context()
        now = self.get_current_time()

        # Critical importance (>0.8): send now regardless
        if importance > 0.8:
            return None

        # Sleep time: defer to morning
        if context == TimeContext.SLEEP_TIME:
            # Set to 8am tomorrow
            tomorrow_morning = now.replace(hour=8, minute=0, second=0, microsecond=0)
            if tomorrow_morning <= now:
                tomorrow_morning = tomorrow_morning.replace(day=tomorrow_morning.day + 1)
            return tomorrow_morning

        # Work hours: defer to lunch or evening unless important
        if context == TimeContext.WORK_HOURS and importance < 0.6:
            if now.hour < 12:
                # Defer to lunch (12:30pm)
                return now.replace(hour=12, minute=30, second=0, microsecond=0)
            else:
                # Defer to evening (6pm)
                return now.replace(hour=18, minute=0, second=0, microsecond=0)

        # Good time: send now
        return None

    def get_time_description(self) -> str:
        """Get human-readable description of current time context"""
        context = self.get_current_time_context()
        now = self.get_current_time()

        descriptions = {
            TimeContext.MORNING_ROUTINE: "It's morning - good time for planning the day",
            TimeContext.WORK_HOURS: "It's work hours - you're likely focused",
            TimeContext.LUNCH_TIME: "It's lunch time - good moment for a break",
            TimeContext.EVENING_ROUTINE: "It's evening - time to wind down",
            TimeContext.NIGHT_TIME: "It's night - relaxation time",
            TimeContext.SLEEP_TIME: "It's late - you should be sleeping",
        }

        time_str = now.strftime("%I:%M %p")
        return f"{time_str} - {descriptions[context]}"

    def should_be_gentle(self) -> bool:
        """
        Determine if agent should be extra gentle/non-intrusive.

        Returns:
            bool: True if should be cautious about interrupting
        """
        context = self.get_current_time_context()

        # Be gentle during work hours, night, and sleep
        return context in [TimeContext.WORK_HOURS, TimeContext.NIGHT_TIME, TimeContext.SLEEP_TIME]

    def get_greeting_for_time(self) -> str:
        """Get appropriate greeting based on time of day"""
        context = self.get_current_time_context()

        greetings = {
            TimeContext.MORNING_ROUTINE: "Good morning",
            TimeContext.WORK_HOURS: "Hello",
            TimeContext.LUNCH_TIME: "Hi",
            TimeContext.EVENING_ROUTINE: "Good evening",
            TimeContext.NIGHT_TIME: "Good evening",
            TimeContext.SLEEP_TIME: "Hello",  # Shouldn't happen, but just in case
        }

        return greetings[context]
