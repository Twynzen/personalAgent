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
        animated_art: Optional['AnimatedArt'] = None,
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
            ascii_art: Optional static ASCII art to display above message
            animated_art: Optional AnimatedArt instance for animation
            play_sound: Whether to play notification sound
            on_dismiss: Callback when user dismisses notification
            on_snooze: Callback when user snoozes notification

        Note: If both ascii_art and animated_art are provided, animated_art takes priority
        """
        self.message = message
        self.title = title
        self.level = level
        self.ascii_art = ascii_art
        self.animated_art = animated_art
        self.play_sound = play_sound
        self.on_dismiss = on_dismiss
        self.on_snooze = on_snooze

        self.root = None
        self.result = None
        self.art_label = None  # Reference to art label for animation updates
        self.animation_player = None

        has_art = (ascii_art is not None) or (animated_art is not None)
        logger.info(f"NotificationWindow created: level={level.value}, title={title}, has_art={has_art}, animated={animated_art is not None}")

    def _calculate_window_size(self, config):
        """Calculate optimal window size based on ASCII art content"""
        # Get the ASCII art text
        if self.animated_art:
            # Use first frame to calculate size
            art_text = self.animated_art.get_current_frame()
        else:
            art_text = self.ascii_art

        if not art_text:
            return "800x600"  # Default fallback

        # Split into lines and measure
        lines = art_text.split('\n')
        num_lines = len(lines)
        max_line_width = max(len(line) for line in lines) if lines else 50

        # Calculate dimensions
        # Font size 8 for Courier New: ~6 pixels wide per char, ~14 pixels high per line
        ascii_font_size = config.get("ascii_font_size", 8)
        char_width = 6 if ascii_font_size == 8 else 7
        line_height = 14 if ascii_font_size == 8 else 16

        # Calculate content dimensions
        art_width = max_line_width * char_width
        art_height = num_lines * line_height

        # Add space for title, message, buttons
        title_height = 50
        message_height = 100
        buttons_height = 80
        padding = 80

        total_width = max(art_width + padding, 600)  # Min 600px wide
        total_height = art_height + title_height + message_height + buttons_height + padding

        # Cap maximum size to screen (assume 1920x1080 min)
        max_width = 1400
        max_height = 900

        total_width = min(total_width, max_width)
        total_height = min(total_height, max_height)

        return f"{int(total_width)}x{int(total_height)}"

    def _configure_window(self):
        """Configure window appearance based on level"""

        # Check if we have ASCII art - use terminal mode for better display
        has_ascii = (self.ascii_art is not None) or (self.animated_art is not None)

        # Level-specific configurations
        configs = {
            NotificationLevel.INFO: {
                "bg_color": "#0C0C0C" if has_ascii else "#4A90E2",  # Black terminal or Blue
                "fg_color": "#00FF00" if has_ascii else "white",  # Green terminal or white
                "title_size": 16,
                "msg_size": 12,
                "ascii_font_size": 8,  # Smaller font for ASCII to fit better
                "topmost": False,
                "sound": "SystemAsterisk"  # Quiet sound
            },
            NotificationLevel.ATTENTION: {
                "bg_color": "#0C0C0C" if has_ascii else "#FFA500",  # Black terminal or Orange
                "fg_color": "#00FF00" if has_ascii else "white",  # Green terminal or white
                "title_size": 18,
                "msg_size": 13,
                "ascii_font_size": 8,
                "topmost": True,
                "sound": "SystemExclamation"  # Alert sound
            },
            NotificationLevel.URGENT: {
                "bg_color": "#0C0C0C" if has_ascii else "#DC143C",  # Black terminal or Crimson red
                "fg_color": "#FF0000" if has_ascii else "white",  # Red terminal or white
                "title_size": 20,
                "msg_size": 14,
                "ascii_font_size": 8,
                "topmost": True,
                "sound": "SystemHand"  # Stop/urgent sound
            },
            NotificationLevel.AVATAR: {
                "bg_color": "#0C0C0C" if has_ascii else "#6B46C1",  # Black terminal or Purple
                "fg_color": "#00FFFF" if has_ascii else "white",  # Cyan terminal or white
                "title_size": 18,
                "msg_size": 13,
                "ascii_font_size": 8,
                "topmost": True,
                "sound": "SystemQuestion"  # Friendly sound
            }
        }

        config = configs[self.level]

        # Calculate dynamic window size based on content
        if has_ascii:
            geometry = self._calculate_window_size(config)
        else:
            # Default sizes without ASCII art
            default_sizes = {
                NotificationLevel.INFO: "400x250",
                NotificationLevel.ATTENTION: "500x350",
                NotificationLevel.URGENT: "600x400",
                NotificationLevel.AVATAR: "500x400"
            }
            geometry = default_sizes[self.level]

        config["geometry"] = geometry

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

        # ASCII Art (static or animated)
        if self.animated_art or self.ascii_art:
            # Use config font size (8 by default for better fit)
            ascii_font_size = config.get("ascii_font_size", 8)
            ascii_font = font.Font(family="Courier New", size=ascii_font_size, weight="bold")

            # Use first frame of animation or static art
            initial_text = (
                self.animated_art.get_current_frame()
                if self.animated_art
                else self.ascii_art
            )

            self.art_label = tk.Label(
                main_frame,
                text=initial_text,
                font=ascii_font,
                bg=config["bg_color"],
                fg=config["fg_color"],
                justify="left"  # Left align for better ASCII art display
            )
            self.art_label.pack(pady=10, padx=10)

            # Start animation if animated_art is provided
            if self.animated_art:
                self._start_animation()

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

    def _start_animation(self):
        """Start the ASCII art animation"""
        if not self.animated_art or not self.art_label:
            return

        # Schedule first animation update
        delay_ms = int(self.animated_art.get_frame_delay() * 1000)
        self.root.after(delay_ms, self._update_animation_frame)

    def _update_animation_frame(self):
        """Update animation frame (called by tkinter after())"""
        if not self.animated_art or not self.art_label or not self.root:
            return

        try:
            # Get next frame
            next_frame = self.animated_art.next_frame()

            # Update label text
            self.art_label.config(text=next_frame)

            # Schedule next update
            delay_ms = int(self.animated_art.get_frame_delay() * 1000)
            self.root.after(delay_ms, self._update_animation_frame)

        except Exception as e:
            logger.error(f"Error updating animation frame: {e}")

    def _stop_animation(self):
        """Stop the animation (cleanup)"""
        # Animation will stop automatically when window is destroyed
        # No explicit cleanup needed with tkinter after()
        pass

    def _handle_dismiss(self):
        """Handle dismiss button click"""
        self.result = "dismissed"
        logger.info(f"Notification dismissed: {self.title}")

        # Stop animation if running
        self._stop_animation()

        if self.on_dismiss:
            self.on_dismiss()

        self.root.destroy()

    def _handle_snooze(self):
        """Handle snooze button click"""
        self.result = "snoozed"
        logger.info(f"Notification snoozed: {self.title}")

        # Stop animation if running
        self._stop_animation()

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


def get_art_for_context(message: str, level: NotificationLevel, prefer_animated: bool = True):
    """
    Automatically select appropriate ASCII art based on message content and level.

    Args:
        message: The notification message
        level: Notification level
        prefer_animated: If True, returns AnimatedArt when available, otherwise returns static string

    Returns:
        AnimatedArt or str: Animated or static ASCII art, or None
    """
    from .animated_ascii import get_animated_art, ANIMATED_ARTS
    from .ascii_art import get_art

    message_lower = message.lower()

    # Check for specific keywords (map to animation names)
    keywords_map = {
        # Time/Calendar
        ("meeting", "reunion", "call", "llamar", "appointment"): "alarm",
        ("timer", "tiempo", "countdown"): "timer",
        ("deadline", "due", "vence"): "hourglass",

        # Personal/Family
        ("family", "familia", "abuela", "mama", "papa", "hermano"): "heart",
        ("birthday", "cumpleanos", "aniversario"): "gift",
        ("phone", "telefono", "llamada"): "bell",  # Use bell for phone

        # Work/Tech (no animations for these yet, will use static)
        ("code", "coding", "programming", "debug", "commit"): "terminal",
        ("work", "trabajo", "project", "proyecto"): "computer",
        ("idea", "brainstorm", "think"): "lightbulb",

        # Success/Achievement
        ("done", "complete", "finished", "completado", "logrado"): "check",
        ("success", "exito", "win", "ganaste"): "trophy",
        ("great", "awesome", "excellent", "genial"): "thumbs_up",
        ("important", "importante", "key"): "star_explosion",

        # Alerts
        ("warning", "advertencia", "cuidado"): "warning",
        ("urgent", "urgente", "now", "ahora"): "fire",
        ("reminder", "recordatorio", "remember"): "bell",
        ("critical", "critico", "danger", "peligro"): "skull",
    }

    # Find matching keyword
    for keywords, art_name in keywords_map.items():
        if any(keyword in message_lower for keyword in keywords):
            # Try to get animated version first
            if prefer_animated and art_name in ANIMATED_ARTS:
                return get_animated_art(art_name)
            else:
                # Fall back to static art
                try:
                    return get_art(art_name)
                except:
                    return None

    # Default based on level
    level_defaults = {
        NotificationLevel.INFO: None,  # No art for info
        NotificationLevel.ATTENTION: "bell",
        NotificationLevel.URGENT: "fire",
        NotificationLevel.AVATAR: "sendell",
    }

    default_art = level_defaults.get(level)
    if default_art:
        if prefer_animated and default_art in ANIMATED_ARTS:
            return get_animated_art(default_art)
        else:
            try:
                return get_art(default_art)
            except:
                return None

    return None


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
    from .animation_engine import AnimatedArt

    level_enum = NotificationLevel(level)

    # Auto-select art if not provided and auto_art is True
    art_result = None
    if ascii_art is None and auto_art:
        art_result = get_art_for_context(message, level_enum, prefer_animated=True)

    # Determine if we got AnimatedArt or static art
    if isinstance(art_result, AnimatedArt):
        # Got animated art
        window = NotificationWindow(
            message,
            title,
            level_enum,
            animated_art=art_result,
            play_sound=play_sound
        )
    else:
        # Got static art or None
        window = NotificationWindow(
            message,
            title,
            level_enum,
            ascii_art=art_result if art_result else ascii_art,
            play_sound=play_sound
        )

    return window.show()
