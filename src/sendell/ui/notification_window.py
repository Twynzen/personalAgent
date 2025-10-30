"""
Notification Window System

Provides visual notification windows with different levels of urgency.
"""

import tkinter as tk
from tkinter import font
from enum import Enum
from typing import Optional, Callable
import logging

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
        on_dismiss: Optional[Callable] = None,
        on_snooze: Optional[Callable] = None
    ):
        """
        Initialize notification window.

        Args:
            message: The notification message to display
            title: Window title
            level: Urgency level (NotificationLevel enum)
            on_dismiss: Callback when user dismisses notification
            on_snooze: Callback when user snoozes notification
        """
        self.message = message
        self.title = title
        self.level = level
        self.on_dismiss = on_dismiss
        self.on_snooze = on_snooze

        self.root = None
        self.result = None

        logger.info(f"NotificationWindow created: level={level.value}, title={title}")

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
                "topmost": False
            },
            NotificationLevel.ATTENTION: {
                "geometry": "500x350",
                "bg_color": "#FFA500",  # Orange
                "fg_color": "white",
                "title_size": 16,
                "msg_size": 12,
                "topmost": True
            },
            NotificationLevel.URGENT: {
                "geometry": "600x400",
                "bg_color": "#DC143C",  # Crimson red
                "fg_color": "white",
                "title_size": 18,
                "msg_size": 14,
                "topmost": True
            },
            NotificationLevel.AVATAR: {
                "geometry": "500x400",
                "bg_color": "#6B46C1",  # Purple
                "fg_color": "white",
                "title_size": 16,
                "msg_size": 12,
                "topmost": True
            }
        }

        config = configs[self.level]

        # Apply configuration
        self.root.geometry(config["geometry"])
        self.root.configure(bg=config["bg_color"])

        if config["topmost"]:
            self.root.attributes('-topmost', True)

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


def show_notification(
    message: str,
    title: str = "Sendell Notification",
    level: str = "info"
) -> str:
    """
    Convenience function to show a notification window.

    Args:
        message: The notification message
        title: Window title
        level: Urgency level ("info", "attention", "urgent", "avatar")

    Returns:
        str: User action ("dismissed" or "snoozed")
    """
    level_enum = NotificationLevel(level)
    window = NotificationWindow(message, title, level_enum)
    return window.show()
