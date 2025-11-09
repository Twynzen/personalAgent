"""
UI Module for Sendell

Provides visual notification windows and user interface components.
Includes static ASCII art and animated ASCII art capabilities.
"""

from .notification_window import (
    NotificationWindow,
    NotificationLevel,
    show_notification,
    get_art_for_context
)
from .ascii_art import (
    get_art,
    list_available_arts,
    get_art_by_category,
    ASCII_ART_DICT
)
from .animation_engine import (
    AnimatedArt,
    AnimationPlayer
)
from .animated_ascii import (
    get_animated_art,
    list_animated_arts,
    ANIMATED_ARTS
)

__all__ = [
    "NotificationWindow",
    "NotificationLevel",
    "show_notification",
    "get_art_for_context",
    "get_art",
    "list_available_arts",
    "get_art_by_category",
    "ASCII_ART_DICT",
    "AnimatedArt",
    "AnimationPlayer",
    "get_animated_art",
    "list_animated_arts",
    "ANIMATED_ARTS"
]
