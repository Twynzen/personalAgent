"""
Test Script for Chat → Visual Notification Integration

Tests the complete flow from creating reminders in chat to seeing
beautiful visual notifications with ASCII art and functional snooze/dismiss buttons.
"""

import asyncio
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from sendell.agent.core import SendellAgent


async def test_reminder_creation():
    """Test creating reminders from the agent's tool"""
    print("\n" + "=" * 60)
    print("TEST: Chat → Visual Notification Integration")
    print("=" * 60)
    print("\nThis test will:")
    print("1. Create a reminder using the agent's add_reminder tool")
    print("2. Wait for it to trigger (2 minutes)")
    print("3. Show the visual notification with ASCII art")
    print("4. Test snooze/dismiss functionality")
    print("\n" + "=" * 60)

    # Initialize agent
    print("\n[1/4] Initializing Sendell agent...")
    agent = SendellAgent()

    # Start proactive loop
    print("[2/4] Starting proactive loop...")
    await agent.proactive_loop.start()

    print("[3/4] Creating test reminder (will trigger in 2 minutes)...")

    # Create reminder through the agent method (simulates tool call)
    reminder = await agent.add_reminder_from_chat(
        content="Test reminder - URGENT meeting with the team!",
        minutes_from_now=2,
        actions=["visual_notification"]
    )

    print(f"\n✅ Reminder created successfully!")
    print(f"   ID: {reminder.reminder_id}")
    print(f"   Content: {reminder.content}")
    print(f"   Due at: {reminder.due_at.strftime('%I:%M:%S %p')}")
    print(f"   Importance: {reminder.importance} (auto-detected from keywords)")
    print(f"   Actions: {reminder.actions}")

    # Show importance detection info
    if reminder.importance >= 0.8:
        print(f"   Level: URGENT (red window)")
    elif reminder.importance >= 0.5:
        print(f"   Level: ATTENTION (orange window)")
    else:
        print(f"   Level: INFO (blue window)")

    print(f"\n[4/4] Waiting for reminder to trigger...")
    print(f"      Current time: {datetime.now().strftime('%I:%M:%S %p')}")
    print(f"      Will trigger at: {reminder.due_at.strftime('%I:%M:%S %p')}")
    print(f"\n      The notification window will appear automatically.")
    print(f"      Try clicking 'Snooze 5min' or 'Dismiss' to test functionality!")
    print(f"\n      (Press Ctrl+C to stop early)\n")

    try:
        # Wait for 3 minutes to ensure reminder triggers
        await asyncio.sleep(180)

        print("\n✅ Test completed!")
        print("   Check if the notification appeared and if buttons worked correctly.")

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    finally:
        print("\nStopping proactive loop...")
        await agent.proactive_loop.stop()
        print("Done!")


async def test_multiple_importance_levels():
    """Test different importance levels"""
    print("\n" + "=" * 60)
    print("TEST: Multiple Importance Levels")
    print("=" * 60)
    print("\nThis test creates 3 reminders with different importance levels.")
    print("Each will trigger 2 minutes apart so you can see the differences.\n")

    # Initialize agent
    agent = SendellAgent()
    await agent.proactive_loop.start()

    # Test 1: Low importance (generic reminder)
    print("[1/3] Creating LOW importance reminder...")
    reminder1 = await agent.add_reminder_from_chat(
        content="Take a short break",
        minutes_from_now=1,
        actions=["visual_notification"]
    )
    print(f"   ✅ Created: importance={reminder1.importance} → INFO level (blue)")

    # Test 2: Medium importance (check keyword)
    print("\n[2/3] Creating MEDIUM importance reminder...")
    reminder2 = await agent.add_reminder_from_chat(
        content="Remember to check the project status",
        minutes_from_now=3,
        actions=["visual_notification"]
    )
    print(f"   ✅ Created: importance={reminder2.importance} → ATTENTION level (orange)")

    # Test 3: High importance (urgent keyword + soon)
    print("\n[3/3] Creating HIGH importance reminder...")
    reminder3 = await agent.add_reminder_from_chat(
        content="URGENT: Important meeting starting now!",
        minutes_from_now=5,
        actions=["visual_notification"]
    )
    print(f"   ✅ Created: importance={reminder3.importance} → URGENT level (red)")

    print(f"\n⏰ Waiting for reminders to trigger...")
    print(f"   1st at {reminder1.due_at.strftime('%I:%M:%S %p')} (blue)")
    print(f"   2nd at {reminder2.due_at.strftime('%I:%M:%S %p')} (orange)")
    print(f"   3rd at {reminder3.due_at.strftime('%I:%M:%S %p')} (red)")
    print(f"\n   Watch for the different colors, sizes, and ASCII art!")
    print(f"   (Press Ctrl+C to stop early)\n")

    try:
        # Wait 7 minutes for all to trigger
        await asyncio.sleep(420)
        print("\n✅ All reminders should have triggered!")

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    finally:
        await agent.proactive_loop.stop()
        print("Done!")


async def test_family_keywords():
    """Test ASCII art auto-selection based on content"""
    print("\n" + "=" * 60)
    print("TEST: ASCII Art Auto-Selection")
    print("=" * 60)
    print("\nThis test creates reminders with different keywords.")
    print("The system will auto-select appropriate ASCII art!\n")

    agent = SendellAgent()
    await agent.proactive_loop.start()

    test_cases = [
        ("Call grandma on Sunday", 1, "heart"),
        ("Important meeting in 10 minutes", 3, "alarm"),
        ("Project deadline approaching!", 5, "fire"),
        ("Great work today!", 7, "trophy"),
    ]

    for i, (content, minutes, expected_art) in enumerate(test_cases, 1):
        print(f"[{i}/4] Creating: '{content}'")
        reminder = await agent.add_reminder_from_chat(
            content=content,
            minutes_from_now=minutes,
            actions=["visual_notification"]
        )
        print(f"   ✅ Will show ~{expected_art} ASCII art")
        print(f"   Triggers at: {reminder.due_at.strftime('%I:%M:%S %p')}\n")

    print("⏰ Waiting for reminders...")
    print("   Watch how each notification has appropriate ASCII art!")
    print("   (Press Ctrl+C to stop early)\n")

    try:
        await asyncio.sleep(480)  # 8 minutes
        print("\n✅ All reminders triggered!")
    except KeyboardInterrupt:
        print("\n\nInterrupted")
    finally:
        await agent.proactive_loop.stop()


def main():
    """Main test menu"""
    print("\n" + "=" * 60)
    print("CHAT → VISUAL NOTIFICATION TEST SUITE")
    print("=" * 60)
    print("\nChoose a test to run:\n")
    print("1. Basic Test (1 reminder, 2 minutes)")
    print("2. Importance Levels Test (3 reminders, different colors)")
    print("3. ASCII Art Auto-Selection Test (4 reminders, different arts)")
    print("4. Quick Test (1 reminder, 30 seconds) - for rapid testing")
    print("\n0. Exit")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        asyncio.run(test_reminder_creation())
    elif choice == "2":
        asyncio.run(test_multiple_importance_levels())
    elif choice == "3":
        asyncio.run(test_family_keywords())
    elif choice == "4":
        # Quick test
        async def quick_test():
            agent = SendellAgent()
            await agent.proactive_loop.start()
            reminder = await agent.add_reminder_from_chat(
                "Quick test reminder!",
                minutes_from_now=0.5,  # 30 seconds
                actions=["visual_notification"]
            )
            print(f"\n✅ Reminder created - will trigger in 30 seconds!")
            print(f"   Importance: {reminder.importance}")
            await asyncio.sleep(60)
            await agent.proactive_loop.stop()

        asyncio.run(quick_test())
    elif choice == "0":
        print("Goodbye!")
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
