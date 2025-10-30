"""
Notification Window System

Provides visual notification windows with different levels of urgency.
Includes ASCII art display and sound notifications.
"""

import tkinter as tk
from tkinter import font
from enum import Enum
from typing import Optional, Callable
import logging
import winsound

logger = logging.getLogger(__name__)


class NotificationLevel(Enum):
    """Notification urgency levels"""
    INFO = "info"
    ATTENTION = "attention"
    URGENT = "urgent"
    AVATAR = "avatar"


class NotificationWindow:
    """
    Visual notification window with configurable urgency levels.

    Levels:
    - INFO: Small, blue, quiet
    - ATTENTION: Medium, orange, with sound
    - URGENT: Large, red, demanding attention
    - AVATAR: Special, shows Sendell avatar
    """

    def __init__(
        self,
        message: str,
        title: str = "Sendell Notification",
        level: NotificationLevel = NotificationLevel.INFO,
        ascii_art: Optional[str] = None,
        play_sound: bool = True,
        on_dismiss: Optional[Callable] = None,
        on_snooze: Optional[Callable] = None
    ):
        """
        Initialize notification window.

        Args:
            message: The notification message to display
            title: Window title
            level: Urgency level (NotificationLevel enum)
            ascii_art: Optional ASCII art to display above message
            play_sound: Whether to play notification sound
            on_dismiss: Callback when user dismisses notification
            on_snooze: Callback when user snoozes notification
        """
        self.message = message
        self.title = title
        self.level = level
        self.ascii_art = ascii_art
        self.play_sound = play_sound
        self.on_dismiss = on_dismiss
        self.on_snooze = on_snooze

        self.root = None
        self.result = None

        logger.info(f"NotificationWindow created: level={level.value}, title={title}, has_art={ascii_art is not None}")

    def _configure_window(self):
        """Configure window appearance based on level"""

        # Level-specific configurations
        configs = {
            NotificationLevel.INFO: {
                "geometry": "400x250",
                "bg_color": "#4A90E2",  # Blue
                "fg_color": "white",
                "title_size": 14,
                "msg_size": 11,
                "topmost": False,
                "sound": "SystemAsterisk"  # Quiet sound
            },
            NotificationLevel.ATTENTION: {
                "geometry": "500x350",
                "bg_color": "#FFA500",  # Orange
                "fg_color": "white",
                "title_size": 16,
                "msg_size": 12,
                "topmost": True,
                "sound": "SystemExclamation"  # Alert sound
            },
            NotificationLevel.URGENT: {
                "geometry": "600x400",
                "bg_color": "#DC143C",  # Crimson red
                "fg_color": "white",
                "title_size": 18,
                "msg_size": 14,
                "topmost": True,
                "sound": "SystemHand"  # Stop/urgent sound
            },
            NotificationLevel.AVATAR: {
                "geometry": "500x400",
                "bg_color": "#6B46C1",  # Purple
                "fg_color": "white",
                "title_size": 16,
                "msg_size": 12,
                "topmost": True,
                "sound": "SystemQuestion"  # Friendly sound
            }
        }

        config = configs[self.level]

        # Adjust geometry if ASCII art is present (needs more height)
        if self.ascii_art:
            width, height = config["geometry"].split("x")
            new_height = int(height) + 200  # Add 200px for ASCII art
            config["geometry"] = f"{width}x{new_height}"

        # Apply configuration
        self.root.geometry(config["geometry"])
        self.root.configure(bg=config["bg_color"])

        if config["topmost"]:
            self.root.attributes('-topmost', True)

        # Play sound if enabled
        if self.play_sound and "sound" in config:
            try:
                winsound.PlaySound(config["sound"], winsound.SND_ALIAS | winsound.SND_ASYNC)
                logger.debug(f"Played sound: {config['sound']}")
            except Exception as e:
                logger.warning(f"Failed to play sound: {e}")

        return config

    def _build_ui(self, config):
        """Build the UI components"""

        # Main frame
        main_frame = tk.Frame(self.root, bg=config["bg_color"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title label
        title_font = font.Font(family="Arial", size=config["title_size"], weight="bold")
        title_label = tk.Label(
            main_frame,
            text=self.title,
            font=title_font,
            bg=config["bg_color"],
            fg=config["fg_color"]
        )
        title_label.pack(pady=(0, 20))

        # ASCII Art (if provided)
        if self.ascii_art:
            ascii_font = font.Font(family="Courier", size=9)
            art_label = tk.Label(
                main_frame,
                text=self.ascii_art,
                font=ascii_font,
                bg=config["bg_color"],
                fg=config["fg_color"],
                justify="center"
            )
            art_label.pack(pady=10)

        # Message label
        msg_font = font.Font(family="Arial", size=config["msg_size"])
        msg_label = tk.Label(
            main_frame,
            text=self.message,
            font=msg_font,
            bg=config["bg_color"],
            fg=config["fg_color"],
            wraplength=450,
            justify="center"
        )
        msg_label.pack(pady=20, expand=True)

        # Buttons frame
        button_frame = tk.Frame(main_frame, bg=config["bg_color"])
        button_frame.pack(pady=(20, 0))

        # Dismiss button
        dismiss_btn = tk.Button(
            button_frame,
            text="Dismiss",
            command=self._handle_dismiss,
            width=12,
            height=2,
            font=font.Font(family="Arial", size=10, weight="bold"),
            bg="white",
            fg="#333333",
            relief="raised",
            cursor="hand2"
        )
        dismiss_btn.pack(side="left", padx=5)

        # Snooze button (only for ATTENTION and URGENT)
        if self.level in [NotificationLevel.ATTENTION, NotificationLevel.URGENT]:
            snooze_btn = tk.Button(
                button_frame,
                text="Snooze 5min",
                command=self._handle_snooze,
                width=12,
                height=2,
                font=font.Font(family="Arial", size=10),
                bg="#EEEEEE",
                fg="#333333",
                relief="raised",
                cursor="hand2"
            )
            snooze_btn.pack(side="left", padx=5)

    def _handle_dismiss(self):
        """Handle dismiss button click"""
        self.result = "dismissed"
        logger.info(f"Notification dismissed: {self.title}")

        if self.on_dismiss:
            self.on_dismiss()

        self.root.destroy()

    def _handle_snooze(self):
        """Handle snooze button click"""
        self.result = "snoozed"
        logger.info(f"Notification snoozed: {self.title}")

        if self.on_snooze:
            self.on_snooze()

        self.root.destroy()

    def show(self) -> str:
        """
        Show the notification window.

        Returns:
            str: "dismissed" or "snoozed" depending on user action
        """
        try:
            # Create root window
            self.root = tk.Tk()
            self.root.title(self.title)

            # Configure window
            config = self._configure_window()

            # Build UI
            self._build_ui(config)

            # Center window on screen
            self._center_window()

            # Handle window close button (X)
            self.root.protocol("WM_DELETE_WINDOW", self._handle_dismiss)

            logger.info(f"Showing notification window: {self.title}")

            # Start main loop
            self.root.mainloop()

            return self.result or "dismissed"

        except Exception as e:
            logger.error(f"Error showing notification window: {e}")
            return "error"

    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()

        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Get window dimensions
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        # Calculate position
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        self.root.geometry(f"+{x}+{y}")


def get_art_for_context(message: str, level: NotificationLevel) -> Optional[str]:
    """
    Automatically select appropriate ASCII art based on message content and level.

    Args:
        message: The notification message
        level: Notification level

    Returns:
        str: ASCII art name to use, or None
    """
    from .ascii_art import get_art

    message_lower = message.lower()

    # Check for specific keywords
    keywords_map = {
        # Time/Calendar
        ("meeting", "reunion", "call", "llamar", "appointment"): "alarm",
        ("timer", "tiempo", "countdown"): "timer",
        ("deadline", "due", "vence"): "hourglass",

        # Personal/Family
        ("family", "familia", "abuela", "mama", "papa", "hermano"): "heart",
        ("birthday", "cumpleanos", "aniversario"): "gift",
        ("phone", "telefono", "llamada"): "phone",

        # Work/Tech
        ("code", "coding", "programming", "debug", "commit"): "terminal",
        ("work", "trabajo", "project", "proyecto"): "computer",
        ("idea", "brainstorm", "think"): "lightbulb",

        # Success/Achievement
        ("done", "complete", "finished", "completado", "logrado"): "check",
        ("success", "exito", "win", "ganaste"): "trophy",
        ("great", "awesome", "excellent", "genial"): "thumbs_up",
        ("important", "importante", "key"): "star",

        # Alerts
        ("warning", "advertencia", "cuidado"): "warning",
        ("urgent", "urgente", "now", "ahora"): "fire",
        ("reminder", "recordatorio", "remember"): "bell",
        ("critical", "critico", "danger", "peligro"): "skull",
    }

    # Find matching keyword
    for keywords, art_name in keywords_map.items():
        if any(keyword in message_lower for keyword in keywords):
            return get_art(art_name)

    # Default based on level
    level_defaults = {
        NotificationLevel.INFO: None,  # No art for info
        NotificationLevel.ATTENTION: get_art("bell"),
        NotificationLevel.URGENT: get_art("fire"),
        NotificationLevel.AVATAR: get_art("sendell"),
    }

    return level_defaults.get(level)


def show_notification(
    message: str,
    title: str = "Sendell Notification",
    level: str = "info",
    ascii_art: Optional[str] = None,
    auto_art: bool = True,
    play_sound: bool = True
) -> str:
    """
    Convenience function to show a notification window.

    Args:
        message: The notification message
        title: Window title
        level: Urgency level ("info", "attention", "urgent", "avatar")
        ascii_art: Optional ASCII art to display (overrides auto_art)
        auto_art: Automatically select art based on message content
        play_sound: Whether to play notification sound

    Returns:
        str: User action ("dismissed" or "snoozed")
    """
    level_enum = NotificationLevel(level)

    # Auto-select art if not provided and auto_art is True
    if ascii_art is None and auto_art:
        ascii_art = get_art_for_context(message, level_enum)

    window = NotificationWindow(
        message,
        title,
        level_enum,
        ascii_art=ascii_art,
        play_sound=play_sound
    )
    return window.show()
