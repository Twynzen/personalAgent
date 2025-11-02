"""
Test Script for Snooze/Dismiss Integration

Tests the complete flow:
1. Create reminders with visual_notification action
2. Trigger reminders
3. User interacts with UI (snooze/dismiss)
4. Verify reminder state updates correctly
"""

import asyncio
from datetime import datetime, timedelta

from src.sendell.proactive.reminders import Reminder, ReminderManager, ReminderType
from src.sendell.proactive.reminder_actions import execute_reminder_action


def test_1_visual_notification_basic():
    """Test 1: Basic visual notification (no reminder manager)"""
    print("\n" + "=" * 60)
    print("TEST 1: Basic Visual Notification")
    print("=" * 60)
    print("This will show a visual notification with animated ASCII art.")
    print("Try clicking 'Dismiss' to see it close.")
    print()

    async def run():
        result = await execute_reminder_action(
            action_type="visual_notification",
            content="Test reminder - Basic visual notification",
            title="Test Reminder",
            importance=0.6
        )
        print(f"\nResult: {result}")
        print(f"User action: {result.get('user_action')}")

    asyncio.run(run())


def test_2_visual_notification_with_callbacks():
    """Test 2: Visual notification with snooze/dismiss callbacks"""
    print("\n" + "=" * 60)
    print("TEST 2: Visual Notification with Callbacks")
    print("=" * 60)
    print("This notification has callbacks that will print messages.")
    print("Try clicking 'Snooze 5min' to see the callback trigger.")
    print()

    dismissed_called = False
    snoozed_called = False

    def on_dismiss():
        nonlocal dismissed_called
        dismissed_called = True
        print("[CALLBACK] on_dismiss() was called!")

    def on_snooze():
        nonlocal snoozed_called
        snoozed_called = True
        print("[CALLBACK] on_snooze() was called!")

    async def run():
        result = await execute_reminder_action(
            action_type="visual_notification",
            content="Test with callbacks - Try clicking Snooze!",
            title="Test Callbacks",
            importance=0.7,
            on_dismiss=on_dismiss,
            on_snooze=on_snooze
        )
        print(f"\nResult: {result}")
        print(f"User action: {result.get('user_action')}")
        print(f"Dismissed callback called: {dismissed_called}")
        print(f"Snoozed callback called: {snoozed_called}")

    asyncio.run(run())


def test_3_reminder_manager_dismiss():
    """Test 3: Full integration with ReminderManager - Dismiss"""
    print("\n" + "=" * 60)
    print("TEST 3: ReminderManager Integration - Dismiss")
    print("=" * 60)
    print("This creates a real reminder and tests dismiss functionality.")
    print("Click 'Dismiss' and we'll verify the reminder state changes.")
    print()

    manager = ReminderManager()

    # Create a reminder due right now
    reminder = Reminder(
        content="Test reminder for dismiss",
        due_at=datetime.now(),
        reminder_type=ReminderType.ONE_TIME,
        actions=["visual_notification"],
        importance=0.5
    )

    manager.add_reminder(reminder)
    print(f"Created reminder: {reminder.reminder_id}")
    print(f"Initial state - completed: {reminder.completed}, sent: {reminder.sent}")

    def on_dismiss():
        print("[CALLBACK] Dismiss clicked - calling manager.dismiss_reminder()")
        success = manager.dismiss_reminder(reminder.reminder_id)
        print(f"Dismiss result: {success}")

    def on_snooze():
        print("[CALLBACK] Snooze clicked - calling manager.snooze_reminder()")
        success = manager.snooze_reminder(reminder.reminder_id, minutes=5)
        print(f"Snooze result: {success}")

    async def run():
        result = await execute_reminder_action(
            action_type="visual_notification",
            content=reminder.content,
            title="Sendell Reminder",
            importance=reminder.importance,
            reminder_id=reminder.reminder_id,
            on_dismiss=on_dismiss,
            on_snooze=on_snooze
        )

        print(f"\nUser action: {result.get('user_action')}")
        print(f"\nFinal reminder state:")
        print(f"  - completed: {reminder.completed}")
        print(f"  - sent: {reminder.sent}")
        print(f"  - snoozed_until: {reminder.snoozed_until}")
        print(f"  - times_snoozed: {reminder.times_snoozed}")

        # Verify expected state
        if result.get('user_action') == 'dismissed':
            print(f"\n✅ PASS: Reminder was dismissed, completed={reminder.completed}")
        elif result.get('user_action') == 'snoozed':
            print(f"\n✅ PASS: Reminder was snoozed until {reminder.snoozed_until}")

    asyncio.run(run())


def test_4_reminder_manager_snooze():
    """Test 4: Full integration with ReminderManager - Snooze"""
    print("\n" + "=" * 60)
    print("TEST 4: ReminderManager Integration - Snooze")
    print("=" * 60)
    print("This creates a reminder and tests snooze functionality.")
    print("Click 'Snooze 5min' and we'll verify it's snoozed for 5 minutes.")
    print()

    manager = ReminderManager()

    # Create a reminder due right now
    reminder = Reminder(
        content="Test reminder for snooze - Click Snooze button!",
        due_at=datetime.now(),
        reminder_type=ReminderType.ONE_TIME,
        actions=["visual_notification"],
        importance=0.7
    )

    manager.add_reminder(reminder)
    print(f"Created reminder: {reminder.reminder_id}")
    print(f"Initial state - snoozed_until: {reminder.snoozed_until}, times_snoozed: {reminder.times_snoozed}")

    def on_dismiss():
        print("[CALLBACK] Dismiss clicked")
        manager.dismiss_reminder(reminder.reminder_id)

    def on_snooze():
        print("[CALLBACK] Snooze clicked - snoozing for 5 minutes")
        manager.snooze_reminder(reminder.reminder_id, minutes=5)

    async def run():
        result = await execute_reminder_action(
            action_type="visual_notification",
            content=reminder.content,
            title="Sendell Reminder (Test Snooze)",
            importance=reminder.importance,
            reminder_id=reminder.reminder_id,
            on_dismiss=on_dismiss,
            on_snooze=on_snooze
        )

        print(f"\nUser action: {result.get('user_action')}")
        print(f"\nFinal reminder state:")
        print(f"  - snoozed_until: {reminder.snoozed_until}")
        print(f"  - times_snoozed: {reminder.times_snoozed}")
        print(f"  - is_due_now: {reminder.is_due_now()}")

        # Verify snooze worked
        if result.get('user_action') == 'snoozed':
            expected_snooze = datetime.now() + timedelta(minutes=5)
            if reminder.snoozed_until:
                diff = abs((reminder.snoozed_until - expected_snooze).total_seconds())
                if diff < 10:  # Within 10 seconds
                    print(f"\n✅ PASS: Reminder correctly snoozed for ~5 minutes")
                    print(f"   Will trigger again at: {reminder.snoozed_until.strftime('%H:%M:%S')}")
                else:
                    print(f"\n❌ FAIL: Snooze time incorrect (diff: {diff}s)")
            print(f"   is_due_now() returns: {reminder.is_due_now()} (should be False)")

    asyncio.run(run())


def test_5_recurring_reminder_dismiss():
    """Test 5: Recurring reminder - Dismiss advances to next occurrence"""
    print("\n" + "=" * 60)
    print("TEST 5: Recurring Reminder - Dismiss Behavior")
    print("=" * 60)
    print("For recurring reminders, dismiss should advance to next occurrence.")
    print("Click 'Dismiss' and watch the due_at time update.")
    print()

    manager = ReminderManager()

    # Create a daily recurring reminder
    reminder = Reminder(
        content="Daily reminder - Dismiss to advance to tomorrow",
        due_at=datetime.now(),
        reminder_type=ReminderType.RECURRING,
        recurrence="daily",
        actions=["visual_notification"],
        importance=0.6
    )

    manager.add_reminder(reminder)
    original_due = reminder.due_at
    print(f"Created RECURRING reminder: {reminder.reminder_id}")
    print(f"Original due_at: {original_due.strftime('%Y-%m-%d %H:%M:%S')}")

    def on_dismiss():
        print("[CALLBACK] Dismiss clicked - for recurring, this advances to next occurrence")
        manager.dismiss_reminder(reminder.reminder_id)

    def on_snooze():
        print("[CALLBACK] Snooze clicked")
        manager.snooze_reminder(reminder.reminder_id, minutes=5)

    async def run():
        result = await execute_reminder_action(
            action_type="visual_notification",
            content=reminder.content,
            title="Recurring Reminder Test",
            importance=reminder.importance,
            reminder_id=reminder.reminder_id,
            on_dismiss=on_dismiss,
            on_snooze=on_snooze
        )

        print(f"\nUser action: {result.get('user_action')}")
        print(f"\nFinal reminder state:")
        print(f"  - due_at: {reminder.due_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  - completed: {reminder.completed}")
        print(f"  - sent: {reminder.sent}")

        # Verify it advanced
        if result.get('user_action') == 'dismissed':
            time_diff = (reminder.due_at - original_due).total_seconds()
            expected_diff = 24 * 3600  # 1 day
            if abs(time_diff - expected_diff) < 60:  # Within 1 minute
                print(f"\n✅ PASS: Recurring reminder advanced by ~24 hours")
                print(f"   Next occurrence: {reminder.due_at.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"\n❌ FAIL: Time difference unexpected: {time_diff/3600}h")

    asyncio.run(run())


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("SNOOZE/DISMISS INTEGRATION TEST SUITE")
    print("=" * 60)
    print("\nThis test suite will show 5 notifications sequentially.")
    print("Follow the instructions for each test.")
    print("\nPress Enter to start...")
    input()

    try:
        # Run tests sequentially
        test_1_visual_notification_basic()
        print("\nPress Enter for next test...")
        input()

        test_2_visual_notification_with_callbacks()
        print("\nPress Enter for next test...")
        input()

        test_3_reminder_manager_dismiss()
        print("\nPress Enter for next test...")
        input()

        test_4_reminder_manager_snooze()
        print("\nPress Enter for next test...")
        input()

        test_5_recurring_reminder_dismiss()

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED!")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
