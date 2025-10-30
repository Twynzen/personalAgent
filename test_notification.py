"""
Test script for notification windows

Run this to test the notification system manually.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sendell.ui import NotificationWindow, NotificationLevel


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


def main():
    """Main test menu"""
    print("=" * 50)
    print("  SENDELL NOTIFICATION WINDOW TESTER")
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
        ])
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
