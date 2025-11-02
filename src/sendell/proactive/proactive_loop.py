"""
Proactive Loop - Background monitoring system.

Runs continuously to:
- Check for due reminders
- Execute reminder actions
- Monitor system state
- Make proactive suggestions (future)
"""

import asyncio
from datetime import datetime
from typing import Callable, List, Optional

from sendell.proactive.identity import AgentIdentity
from sendell.proactive.reminder_actions import execute_reminder_actions
from sendell.proactive.reminders import Reminder, ReminderManager
from sendell.proactive.temporal_clock import TemporalClock
from sendell.utils.logger import get_logger

logger = get_logger(__name__)


class ProactiveLoop:
    """
    Main proactive monitoring loop.

    Runs in background to detect and act on reminders and patterns.
    """

    def __init__(
        self,
        identity: AgentIdentity,
        reminder_manager: ReminderManager,
        temporal_clock: TemporalClock,
        check_interval_seconds: int = 60,
        on_reminder_callback: Optional[Callable] = None,
    ):
        """
        Initialize proactive loop.

        Args:
            identity: Agent identity system
            reminder_manager: Reminder management system
            temporal_clock: Temporal awareness system
            check_interval_seconds: How often to check (default 60s, use 60 for testing)
            on_reminder_callback: Callback function when reminder triggers
        """
        self.identity = identity
        self.reminder_manager = reminder_manager
        self.temporal_clock = temporal_clock
        self.check_interval = check_interval_seconds
        self.on_reminder_callback = on_reminder_callback

        self.running = False
        self.loop_task: Optional[asyncio.Task] = None

        self.stats = {"cycles_run": 0, "reminders_triggered": 0, "last_check_at": None}

        logger.info(f"ProactiveLoop initialized (check every {check_interval_seconds}s)")

    async def start(self):
        """Start the proactive loop"""
        if self.running:
            logger.warning("ProactiveLoop already running")
            return

        self.running = True
        self.loop_task = asyncio.create_task(self._run_loop())
        logger.debug("ProactiveLoop started")

    async def stop(self):
        """Stop the proactive loop"""
        if not self.running:
            return

        self.running = False

        if self.loop_task:
            self.loop_task.cancel()
            try:
                await self.loop_task
            except asyncio.CancelledError:
                pass

        logger.info("ProactiveLoop stopped")

    async def _run_loop(self):
        """Main loop that runs continuously"""
        logger.debug("Proactive monitoring loop starting...")

        try:
            while self.running:
                await self._run_cycle()
                await asyncio.sleep(self.check_interval)

        except asyncio.CancelledError:
            logger.debug("Proactive loop cancelled")
        except Exception as e:
            logger.error(f"Proactive loop error: {e}", exc_info=True)
            self.running = False

    async def _run_cycle(self):
        """Run one monitoring cycle"""
        self.stats["cycles_run"] += 1
        self.stats["last_check_at"] = datetime.now()

        # Debug logging only to file (use debug level)
        logger.debug(f"Proactive cycle #{self.stats['cycles_run']} - Checking reminders...")

        try:
            # 1. Check for due reminders
            all_reminders = self.reminder_manager.get_all_reminders()
            logger.debug(f"Total reminders in manager: {len(all_reminders)}")

            due_reminders = self.reminder_manager.get_due_reminders()

            if due_reminders:
                # Only log to console when there ARE reminders to process
                logger.info(f"⏰ Processing {len(due_reminders)} reminder(s)...")

                for reminder in due_reminders:
                    await self._process_reminder(reminder)
            else:
                logger.debug(f"No reminders due yet")

            # 2. Future: Check for patterns, habits, etc.
            # await self._check_habits()
            # await self._check_patterns()

        except Exception as e:
            logger.error(f"Error in proactive cycle: {e}", exc_info=True)

    async def _process_reminder(self, reminder: Reminder):
        """
        Process a due reminder.

        Args:
            reminder: The reminder to process
        """
        logger.debug(
            f"Processing reminder: {reminder.reminder_id} - {reminder.content} (actions: {reminder.actions})"
        )

        try:
            # Get time context for appropriate messaging
            time_context = self.temporal_clock.get_current_time_context()
            greeting = self.temporal_clock.get_greeting_for_time()

            # Format reminder message
            message = f"{greeting}! Reminder: {reminder.content}"

            # Create callbacks for snooze/dismiss
            def on_dismiss_callback():
                """Called when user dismisses the notification"""
                logger.info(f"User dismissed reminder: {reminder.reminder_id}")
                self.reminder_manager.dismiss_reminder(reminder.reminder_id)

            def on_snooze_callback():
                """Called when user snoozes the notification"""
                logger.info(f"User snoozed reminder: {reminder.reminder_id} (5 minutes)")
                self.reminder_manager.snooze_reminder(reminder.reminder_id, minutes=5)

            # Execute all actions for this reminder
            results = await execute_reminder_actions(
                actions=reminder.actions,
                content=message,
                title="Sendell Reminder",
                importance=reminder.importance,
                reminder_id=reminder.reminder_id,
                on_dismiss=on_dismiss_callback,
                on_snooze=on_snooze_callback
            )

            # Log results (debug level for details)
            actions_str = ", ".join([r["action"] for r in results if r["success"]])
            logger.info(f"✅ Reminder: '{reminder.content}' → {actions_str}")

            # Check if user interacted with visual notification
            user_action = None
            for result in results:
                if not result["success"]:
                    logger.error(f"Action failed: {result['action']} - {result.get('error')}")

                # Capture user action from visual_notification
                if result.get("action") == "visual_notification" and result.get("user_action"):
                    user_action = result["user_action"]

            # Only process_sent_reminder if user didn't already handle it via UI
            # (dismiss/snooze callbacks already updated the state)
            if user_action is None:
                # No UI interaction, mark as processed normally (for legacy actions)
                self.reminder_manager.process_sent_reminder(reminder.reminder_id)

            # Update stats
            self.stats["reminders_triggered"] += 1

            # Call callback if provided (for UI updates)
            if self.on_reminder_callback:
                try:
                    await self.on_reminder_callback(reminder, results)
                except Exception as e:
                    logger.error(f"Callback error: {e}")

            logger.debug(f"Reminder processed successfully: {reminder.reminder_id}")

        except Exception as e:
            logger.error(f"Error processing reminder {reminder.reminder_id}: {e}", exc_info=True)

    def get_status(self) -> dict:
        """Get current status of the proactive loop"""
        return {
            "running": self.running,
            "check_interval_seconds": self.check_interval,
            "cycles_run": self.stats["cycles_run"],
            "reminders_triggered": self.stats["reminders_triggered"],
            "last_check_at": self.stats["last_check_at"].isoformat()
            if self.stats["last_check_at"]
            else None,
            "pending_reminders": len(self.reminder_manager.get_due_reminders()),
            "total_reminders": len(self.reminder_manager.get_all_reminders()),
        }

    async def force_check_now(self):
        """Force an immediate check (useful for testing)"""
        logger.info("Forcing immediate check...")
        await self._run_cycle()
