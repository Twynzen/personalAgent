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
    ASCII_ART_DICT,
    get_animated_art,
    list_animated_arts,
    ANIMATED_ARTS
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


def test_all_animated_arts():
    """Test all 10 animated ASCII arts"""
    print("\n=== Testing ALL 10 Animated ASCII Arts ===")

    animations = list_animated_arts()
    print(f"\nTotal animations available: {len(animations)}")
    print(f"Animations: {', '.join(animations)}\n")

    for anim_name in animations:
        print(f"\n--- Testing: {anim_name} ---")
        animated_art = get_animated_art(anim_name)

        print(f"Frames: {animated_art.total_frames}")
        print(f"FPS: {animated_art.fps}")
        print(f"Duration: {animated_art.duration:.2f}s")
        print(f"Loop: {animated_art.loop}")

        input("Press Enter to show animation...")

        window = NotificationWindow(
            message=f"Testing {anim_name} animation!",
            title=f"Animated: {anim_name}",
            level=NotificationLevel.ATTENTION,
            animated_art=animated_art,
            play_sound=False
        )
        result = window.show()
        print(f"Result: {result}")


def test_specific_animations():
    """Test specific key animations"""
    print("\n=== Testing KEY Animations ===")

    key_animations = [
        ("sendell_blink", "Sendell blinking and winking"),
        ("heart_beat", "Heart beating rhythm"),
        ("fire_burning", "Fire flames animating"),
        ("hourglass_sand", "Sand falling through hourglass"),
        ("star_explosion", "Star exploding celebration")
    ]

    for anim_name, description in key_animations:
        print(f"\n{description}")
        input("Press Enter to show...")

        animated_art = get_animated_art(anim_name)

        window = NotificationWindow(
            message=description,
            title=f"Animation: {anim_name}",
            level=NotificationLevel.AVATAR,
            animated_art=animated_art,
            play_sound=True
        )
        result = window.show()
        print(f"Result: {result}")


def test_animated_reminder_scenarios():
    """Test real scenarios with animated arts"""
    print("\n=== Testing Animated REMINDER Scenarios ===")

    scenarios = [
        {
            "message": "Time to call your grandmother!",
            "title": "Family Reminder",
            "animation": "heart_beat",
            "level": "attention"
        },
        {
            "message": "Meeting starts in 5 minutes!",
            "title": "Calendar Alert",
            "animation": "clock_ticking",
            "level": "attention"
        },
        {
            "message": "URGENT: Server on fire!",
            "title": "Critical Alert",
            "animation": "fire_burning",
            "level": "urgent"
        },
        {
            "message": "Congratulations! Task completed!",
            "title": "Achievement Unlocked",
            "animation": "star_explosion",
            "level": "info"
        },
        {
            "message": "Deadline approaching fast!",
            "title": "Time Running Out",
            "animation": "hourglass_sand",
            "level": "urgent"
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['title']}")
        print(f"   Message: {scenario['message']}")
        print(f"   Animation: {scenario['animation']}")
        input("   Press Enter to show...")

        animated_art = get_animated_art(scenario["animation"])

        window = NotificationWindow(
            message=scenario["message"],
            title=scenario["title"],
            level=NotificationLevel(scenario["level"]),
            animated_art=animated_art,
            play_sound=True
        )
        result = window.show()
        print(f"   Result: {result}")


def test_animation_comparison():
    """Compare static vs animated art side by side"""
    print("\n=== Comparing STATIC vs ANIMATED ===")

    print("\n1. Static Sendell")
    input("Press Enter...")
    window = NotificationWindow(
        message="This is static Sendell art",
        title="Static Art",
        level=NotificationLevel.AVATAR,
        ascii_art=get_art("sendell"),
        play_sound=False
    )
    window.show()

    print("\n2. Animated Sendell (blinking)")
    input("Press Enter...")
    window = NotificationWindow(
        message="This is ANIMATED Sendell art!",
        title="Animated Art",
        level=NotificationLevel.AVATAR,
        animated_art=get_animated_art("sendell_blink"),
        play_sound=False
    )
    window.show()

    print("\nNotice the difference? Animated = LIFE!")


def test_all_levels():
    """Test all 4 notification levels in sequence"""
    print("\n=== Testing ALL 4 Levels ===")

    levels = [
        ("INFO", "info", "This is an informational message."),
        ("ATTENTION", "attention", "Please pay attention to this!"),
        ("URGENT", "urgent", "URGENT: This requires immediate action!"),
        ("AVATAR", "avatar", "Hello! It's me, Sendell.")
    ]

    for name, level, msg in levels:
        print(f"\n--- {name} Level ---")
        input("Press Enter to show...")
        result = show_notification(
            message=msg,
            level=level,
            auto_art=True,
            play_sound=True
        )
        print(f"Result: {result}")


def main():
    """Main test menu - SIMPLIFIED"""
    print("=" * 60)
    print("  SENDELL NOTIFICATION TESTER")
    print("  Animated ASCII Art + Dynamic Window Sizing")
    print("=" * 60)

    tests = {
        "1": ("Test ALL 4 levels (INFO, ATTENTION, URGENT, AVATAR)", test_all_levels),
        "2": ("Test KEY animations (5 best)", test_specific_animations),
        "3": ("Test REAL reminder scenarios", test_animated_reminder_scenarios),
        "4": ("Test Sendell avatar animation", test_notification_with_art),
        "5": ("Compare STATIC vs ANIMATED", test_animation_comparison),
    }

    while True:
        print("\n" + "=" * 60)
        print("SELECT A TEST:")
        for key, (desc, _) in tests.items():
            print(f"  {key}. {desc}")
        print("  q. Quit")
        print("=" * 60)

        choice = input("\nYour choice: ").strip().lower()

        if choice == 'q':
            print("\nExiting... Goodbye!")
            break

        if choice in tests:
            _, test_func = tests[choice]
            try:
                test_func()
                print("\n" + "-" * 60)
                print("Test completed successfully!")
                print("-" * 60)
            except Exception as e:
                print(f"\nERROR: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("\nInvalid choice! Please select 1-5 or 'q' to quit.")


if __name__ == "__main__":
    main()
