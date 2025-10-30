"""
ASCII Art Library for Sendell

Collection of ASCII art for visual notifications.
All art uses only ASCII characters for Windows compatibility.
"""

# ============================================================
# SENDELL AVATAR - The agent's persona
# ============================================================

SENDELL_AVATAR = r"""
     ___________
    /           \
   |  O     O   |
   |     ^      |
   |   \___/    |
    \___________/
       |     |
      /|     |\
     / |     | \
    Sendell AI
"""

SENDELL_HAPPY = r"""
     ___________
    /           \
   |  ^     ^   |
   |     v      |
   |   \___/    |
    \___________/
       |     |
    Happy Sendell!
"""

SENDELL_THINKING = r"""
     ___________
    /     ?     \
   |  o     o   |
   |     ~      |
   |    ---     |
    \___________/
     Thinking...
"""

# ============================================================
# TIME & REMINDERS
# ============================================================

CLOCK = r"""
     _____
    /     \
   |  12   |
   | 9  3  |
   |   6   |
    \_____/
      ||
     /  \
"""

ALARM_CLOCK = r"""
    __/\__/\__
   /          \
  |  >>>  <<<  |
  |   11:30    |
  |  ALARM!    |
   \__________/
     ||    ||
"""

TIMER = r"""
      .---.
     /     \
    |  3:00 |
    | [====]|
     \     /
      `---'
  Time's up!
"""

HOURGLASS = r"""
    \      /
     \    /
      \__/
      /  \
     /    \
    /______\
   Tick tock...
"""

# ============================================================
# URGENCY & ALERTS
# ============================================================

WARNING = r"""
       /\
      /  \
     / !! \
    /______\
   ATTENTION!
"""

FIRE = r"""
      (  )
     ( () )
    (  ()  )
   (   ()   )
    \ /  \ /
     |    |
     |    |
    URGENT!
"""

BELL = r"""
      .-.
     (   )
      '-'
     /   \
    /_____\
   DING DING!
"""

EXCLAMATION = r"""
      ___
     | ! |
     | ! |
     | ! |
     |___|
       O
"""

# ============================================================
# POSITIVE & SUCCESS
# ============================================================

CHECKMARK = r"""
            __
           /  )
          /  /
         /  /
     /\ /  /
    (  \  (
     \  ) )
      \/\/
    SUCCESS!
"""

STAR = r"""
        *
       ***
      *****
     *******
      *****
       ***
        *
   IMPORTANT!
"""

TROPHY = r"""
      ___
     |   |
     | # |
    /|___|\
   /       \
  |_________|
   ACHIEVED!
"""

THUMBS_UP = r"""
       ___
      /   \
     |  ^  |
      \___/
        |
     ___|___
    |       |
    GREAT!
"""

# ============================================================
# PERSONAL & FAMILY
# ============================================================

HEART = r"""
    **   **
   *  * *  *
  *    *    *
   *       *
    *     *
     *   *
      * *
       *
   PERSONAL
"""

PHONE = r"""
    .-------.
   /         \
  |  [CALL]  |
  |   NOW    |
   \_________/
     |     |
    Call reminder
"""

GIFT = r"""
    .-------.
    |  ___  |
    | |   | |
    | |___| |
    '--._.--'
      |_|
   Special day!
"""

# ============================================================
# TECH & WORK
# ============================================================

COMPUTER = r"""
   ___________
  |           |
  |  WORK     |
  |___________|
   |_______|
      | |
    _|   |_
"""

TERMINAL = r"""
   ___________
  |  $> _     |
  |           |
  |  DEV      |
  |___________|
    Code time!
"""

LIGHTBULB = r"""
      .-.
     ( o )
    (  -  )
     \   /
      | |
      | |
     _|_|_
     IDEA!
"""

# ============================================================
# CRITICAL
# ============================================================

SKULL = r"""
     .---.
    / o o \
   |   ^   |
   |  ___  |
    \_____/
      |||
   CRITICAL!
"""

STOP = r"""
    .-------.
   / STOP!  \
  |   !!!    |
   \ !!!!! /
    '-----'
   ACTION NEEDED
"""

# ============================================================
# HELPER FUNCTIONS
# ============================================================

# Dictionary mapping names to art
ASCII_ART_DICT = {
    # Sendell personas
    "sendell": SENDELL_AVATAR,
    "sendell_happy": SENDELL_HAPPY,
    "sendell_thinking": SENDELL_THINKING,

    # Time & reminders
    "clock": CLOCK,
    "alarm": ALARM_CLOCK,
    "timer": TIMER,
    "hourglass": HOURGLASS,

    # Urgency & alerts
    "warning": WARNING,
    "fire": FIRE,
    "bell": BELL,
    "exclamation": EXCLAMATION,

    # Positive
    "check": CHECKMARK,
    "star": STAR,
    "trophy": TROPHY,
    "thumbs_up": THUMBS_UP,

    # Personal
    "heart": HEART,
    "phone": PHONE,
    "gift": GIFT,

    # Tech & work
    "computer": COMPUTER,
    "terminal": TERMINAL,
    "lightbulb": LIGHTBULB,

    # Critical
    "skull": SKULL,
    "stop": STOP,
}


def get_art(name: str) -> str:
    """
    Get ASCII art by name.

    Args:
        name: Name of the art (e.g., "sendell", "clock", "warning")

    Returns:
        str: The ASCII art string, or a default if not found
    """
    art = ASCII_ART_DICT.get(name.lower())

    if art is None:
        # Default art if not found
        return f"""
        ???
       (??)
        ???
    Art '{name}' not found
"""

    return art


def list_available_arts() -> list:
    """
    Get list of all available ASCII art names.

    Returns:
        list: List of art names
    """
    return sorted(ASCII_ART_DICT.keys())


def get_art_by_category(category: str) -> dict:
    """
    Get all arts in a category.

    Args:
        category: Category name ("sendell", "time", "alert", "positive", "personal", "tech", "critical")

    Returns:
        dict: Dictionary of art names and their ASCII art
    """
    categories = {
        "sendell": ["sendell", "sendell_happy", "sendell_thinking"],
        "time": ["clock", "alarm", "timer", "hourglass"],
        "alert": ["warning", "fire", "bell", "exclamation"],
        "positive": ["check", "star", "trophy", "thumbs_up"],
        "personal": ["heart", "phone", "gift"],
        "tech": ["computer", "terminal", "lightbulb"],
        "critical": ["skull", "stop"],
    }

    art_names = categories.get(category.lower(), [])
    return {name: ASCII_ART_DICT[name] for name in art_names if name in ASCII_ART_DICT}


# ============================================================
# TESTING/DEMO FUNCTION
# ============================================================

def print_all_arts():
    """Print all available ASCII arts (for testing)"""
    for name in sorted(ASCII_ART_DICT.keys()):
        print(f"\n{'='*50}")
        print(f"ART: {name.upper()}")
        print('='*50)
        print(ASCII_ART_DICT[name])


if __name__ == "__main__":
    print("ASCII Art Library for Sendell")
    print(f"\nTotal arts available: {len(ASCII_ART_DICT)}")
    print(f"\nArt names: {', '.join(sorted(ASCII_ART_DICT.keys()))}")
    print("\n" + "="*50)
    print("Printing all arts...")
    print("="*50)
    print_all_arts()
