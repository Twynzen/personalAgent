"""
Qt-Tkinter Bridge - Embed PyQt6 widgets in tkinter

Allows embedding high-performance PyQt6 widgets inside tkinter applications.
Uses platform-specific window handle integration.
"""

import sys
import tkinter as tk
from typing import Optional

from PySide6.QtWidgets import QApplication, QWidget


class QtBridge:
    """Bridge to embed PyQt6 widgets in tkinter"""

    _qapp: Optional[QApplication] = None

    @classmethod
    def get_qapp(cls) -> QApplication:
        """Get or create QApplication instance"""
        if cls._qapp is None:
            # Create QApplication if it doesn't exist
            if not QApplication.instance():
                cls._qapp = QApplication(sys.argv)
            else:
                cls._qapp = QApplication.instance()
        return cls._qapp

    @classmethod
    def embed_widget(cls, parent_frame: tk.Frame, qt_widget: QWidget) -> tk.Frame:
        """
        Embed a PyQt6 widget inside a tkinter frame.

        Args:
            parent_frame: Tkinter frame to contain the Qt widget
            qt_widget: PyQt6 widget to embed

        Returns:
            The parent frame with embedded Qt widget
        """
        # Ensure QApplication exists
        cls.get_qapp()

        # Show the Qt widget
        qt_widget.show()

        # Embed using platform-specific methods
        if sys.platform == "win32":
            cls._embed_windows(parent_frame, qt_widget)
        else:
            # For Linux/Mac, use different approach
            cls._embed_unix(parent_frame, qt_widget)

        return parent_frame

    @classmethod
    def _embed_windows(cls, parent_frame: tk.Frame, qt_widget: QWidget):
        """Embed Qt widget in tkinter on Windows"""
        # Get window handle from Qt widget
        window_id = qt_widget.winId()

        # Get tkinter window handle
        parent_id = parent_frame.winfo_id()

        # Import Windows-specific modules
        try:
            import win32gui
            import win32con

            # Set Qt widget as child of tkinter window
            win32gui.SetParent(int(window_id), parent_id)

            # Set window style to child window
            style = win32gui.GetWindowLong(int(window_id), win32con.GWL_STYLE)
            style = style & ~win32con.WS_POPUP
            style = style | win32con.WS_CHILD
            win32gui.SetWindowLong(int(window_id), win32con.GWL_STYLE, style)

            # Position and size the Qt widget
            def resize_qt_widget(event=None):
                width = parent_frame.winfo_width()
                height = parent_frame.winfo_height()
                if width > 1 and height > 1:
                    qt_widget.setGeometry(0, 0, width, height)

            parent_frame.bind("<Configure>", resize_qt_widget)
            parent_frame.update_idletasks()
            resize_qt_widget()

        except ImportError:
            raise RuntimeError("win32gui is required for Qt-tkinter bridge on Windows")

    @classmethod
    def _embed_unix(cls, parent_frame: tk.Frame, qt_widget: QWidget):
        """Embed Qt widget in tkinter on Unix/Linux/Mac"""
        # Unix embedding using X11
        window_id = qt_widget.winId()

        # Create container frame
        container = tk.Frame(parent_frame, container=True)
        container.pack(fill="both", expand=True)

        # Embed Qt widget
        container.update()
        qt_widget.setAttribute(0x00000080)  # Qt.WA_NativeWindow
        qt_widget.show()

    @classmethod
    def process_qt_events(cls):
        """Process Qt events (call periodically from tkinter mainloop)"""
        qapp = cls.get_qapp()
        if qapp:
            qapp.processEvents()
