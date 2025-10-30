"""
UI Module for Sendell

Provides visual notification windows and user interface components.
"""

from .notification_window import NotificationWindow, NotificationLevel
from .ascii_art import (
    get_art,
    list_available_arts,
    get_art_by_category,
    ASCII_ART_DICT
)

__all__ = [
    "NotificationWindow",
    "NotificationLevel",
    "get_art",
    "list_available_arts",
    "get_art_by_category",
    "ASCII_ART_DICT"
]
