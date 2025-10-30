"""
Test script for notification windows

Run this to test the notification system manually.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sendell.ui import (
    NotificationWindow,
    NotificationLevel,
    show_notification,
    get_art,
    get_art_for_context,
    list_available_arts,
    ASCII_ART_DICT
)


def test_info_notification():
    """Test INFO level notification"""
    print("\n=== Testing INFO Notification ===")
    print("- Small blue window")
    print("- Only Dismiss button")
    print("- Not topmost")

    window = NotificationWindow(
        message="This is an INFO level notification. Just a friendly heads up!",
        title="Info Test",
        level=NotificationLevel.INFO
    )

    result = window.show()
    print(f"Result: {result}")


def test_attention_notification():
    """Test ATTENTION level notification"""
    print("\n=== Testing ATTENTION Notification ===")
    print("- Medium orange window")
    print("- Dismiss and Snooze buttons")
    print("- Stays on top")

    window = NotificationWindow(
        message="This is an ATTENTION level notification. Please take a moment to check this.",
        title="Attention Test",
        level=NotificationLevel.ATTENTION
    )

    result = window.show()
    print(f"Result: {result}")


def test_urgent_notification():
    """Test URGENT level notification"""
    print("\n=== Testing URGENT Notification ===")
    print("- Large red window")
    print("- Dismiss and Snooze buttons")
    print("- Stays on top")

    window = NotificationWindow(
        message="This is an URGENT level notification! You need to see this right away!",
        title="Urgent Test",
        level=NotificationLevel.URGENT
    )

    result = window.show()
    print(f"Result: {result}")


def test_avatar_notification():
    """Test AVATAR level notification"""
    print("\n=== Testing AVATAR Notification ===")
    print("- Medium purple window")
    print("- Only Dismiss button")
    print("- Stays on top")
    print("- (Later will show Sendell ASCII art)")

    window = NotificationWindow(
        message="Hello! It's me, Sendell. Just checking in with you!",
        title="Sendell",
        level=NotificationLevel.AVATAR
    )

    result = window.show()
    print(f"Result: {result}")


def test_with_callbacks():
    """Test notification with callbacks"""
    print("\n=== Testing Callbacks ===")

    def on_dismiss():
        print("CALLBACK: User dismissed the notification")

    def on_snooze():
        print("CALLBACK: User snoozed the notification")

    window = NotificationWindow(
        message="This notification has callbacks. Try clicking Dismiss or Snooze!",
        title="Callback Test",
        level=NotificationLevel.ATTENTION,
        on_dismiss=on_dismiss,
        on_snooze=on_snooze
    )

    result = window.show()
    print(f"Result: {result}")


def test_print_all_ascii_arts():
    """Print all available ASCII arts to console"""
    print("\n=== Testing ASCII Arts Library ===")
    print(f"Total arts: {len(ASCII_ART_DICT)}")
    print(f"Available: {', '.join(sorted(list_available_arts()))}\n")

    for name in sorted(list_available_arts()):
        print("=" * 50)
        print(f"ART: {name.upper()}")
        print("=" * 50)
        print(get_art(name))
        input("Press Enter for next art...")


def test_ascii_art_in_notification():
    """Test ASCII art inside notification window"""
    print("\n=== Testing ASCII Art in Notification ===")

    # Let user select art
    arts = sorted(list_available_arts())
    print("\nAvailable arts:")
    for i, art_name in enumerate(arts, 1):
        print(f"  {i}. {art_name}")

    try:
        choice = int(input("\nSelect art number: "))
        if 1 <= choice <= len(arts):
            art_name = arts[choice - 1]
            art = get_art(art_name)

            print(f"\nShowing notification with '{art_name}' art...")

            # Create notification window (note: ASCII art not yet integrated into window)
            # For now, just print it
            print("\n[Preview - ASCII art will be integrated in next branch]")
            print(art)
            print("\nNotification window would show above art")

        else:
            print("Invalid choice!")
    except ValueError:
        print("Invalid input!")


def test_notification_with_art():
    """Test notification with ASCII art"""
    print("\n=== Testing Notification WITH ASCII Art ===")

    # Test with Sendell avatar
    print("\n1. Testing AVATAR level with Sendell art...")
    window = NotificationWindow(
        message="Hello! I'm Sendell, your AI assistant!",
        title="Meet Sendell",
        level=NotificationLevel.AVATAR,
        ascii_art=get_art("sendell"),
        play_sound=True
    )
    result = window.show()
    print(f"Result: {result}")


def test_notification_with_sound():
    """Test notifications with different sounds"""
    print("\n=== Testing Notifications WITH Sounds ===")

    levels = [
        (NotificationLevel.INFO, "INFO: Quiet asterisk sound"),
        (NotificationLevel.ATTENTION, "ATTENTION: Exclamation sound"),
        (NotificationLevel.URGENT, "URGENT: Hand/stop sound"),
        (NotificationLevel.AVATAR, "AVATAR: Question sound"),
    ]

    for level, desc in levels:
        print(f"\n{desc}")
        input("Press Enter to show notification...")

        window = NotificationWindow(
            message=f"This is a {level.value.upper()} level notification with sound!",
            title=f"{level.value.capitalize()} Sound Test",
            level=level,
            play_sound=True
        )
        result = window.show()
        print(f"Result: {result}")


def test_auto_art_selection():
    """Test automatic ASCII art selection based on message content"""
    print("\n=== Testing AUTO ASCII Art Selection ===")

    test_messages = [
        ("Don't forget your meeting in 5 minutes!", "attention"),
        ("Llamar a la abuela", "attention"),
        ("Great work on completing the project!", "info"),
        ("URGENT: Critical system error!", "urgent"),
        ("Time for your daily code review", "attention"),
    ]

    for message, level in test_messages:
        print(f"\nMessage: '{message}'")
        print(f"Level: {level}")

        # Get auto-selected art
        level_enum = NotificationLevel(level)
        art = get_art_for_context(message, level_enum)

        if art:
            print(f"Auto-selected art preview:")
            print(art[:100] + "..." if len(art) > 100 else art)
        else:
            print("No art auto-selected")

        input("Press Enter to show notification...")

        result = show_notification(
            message=message,
            level=level,
            auto_art=True,
            play_sound=True
        )
        print(f"Result: {result}")


def test_reminder_scenarios():
    """Test real reminder scenarios"""
    print("\n=== Testing Real REMINDER Scenarios ===")

    scenarios = [
        {
            "message": "Time to call your grandmother!",
            "title": "Family Reminder",
            "level": "attention",
            "art": get_art("heart"),
        },
        {
            "message": "Meeting with team starts in 10 minutes",
            "title": "Calendar Alert",
            "level": "attention",
            "art": get_art("alarm"),
        },
        {
            "message": "DEADLINE: Project submission due NOW!",
            "title": "Urgent Deadline",
            "level": "urgent",
            "art": get_art("fire"),
        },
        {
            "message": "Great job! You completed all your tasks today!",
            "title": "Achievement",
            "level": "info",
            "art": get_art("trophy"),
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['title']}")
        print(f"   Message: {scenario['message']}")
        input("   Press Enter to show...")

        window = NotificationWindow(
            message=scenario["message"],
            title=scenario["title"],
            level=NotificationLevel(scenario["level"]),
            ascii_art=scenario["art"],
            play_sound=True
        )
        result = window.show()
        print(f"   Result: {result}")


def main():
    """Main test menu"""
    print("=" * 50)
    print("  SENDELL NOTIFICATION WINDOW TESTER")
    print("  NOW WITH ASCII ART + SOUNDS!")
    print("=" * 50)

    tests = {
        "1": ("Test INFO notification", test_info_notification),
        "2": ("Test ATTENTION notification", test_attention_notification),
        "3": ("Test URGENT notification", test_urgent_notification),
        "4": ("Test AVATAR notification", test_avatar_notification),
        "5": ("Test with callbacks", test_with_callbacks),
        "6": ("Test ALL levels (one by one)", lambda: [
            test_info_notification(),
            test_attention_notification(),
            test_urgent_notification(),
            test_avatar_notification()
        ]),
        "7": ("Print all ASCII arts", test_print_all_ascii_arts),
        "8": ("Test ASCII art in notification (preview)", test_ascii_art_in_notification),
        "9": ("Test notification WITH ASCII art", test_notification_with_art),
        "10": ("Test notifications WITH sounds", test_notification_with_sound),
        "11": ("Test AUTO art selection", test_auto_art_selection),
        "12": ("Test REAL reminder scenarios", test_reminder_scenarios),
    }

    while True:
        print("\nSelect a test:")
        for key, (desc, _) in tests.items():
            print(f"  {key}. {desc}")
        print("  q. Quit")

        choice = input("\nYour choice: ").strip().lower()

        if choice == 'q':
            print("Exiting...")
            break

        if choice in tests:
            _, test_func = tests[choice]
            try:
                test_func()
            except Exception as e:
                print(f"ERROR: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()
