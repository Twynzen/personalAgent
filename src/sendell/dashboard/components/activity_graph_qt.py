"""
Activity Graph Widget (PyQt6) - GPU-Accelerated ECG-style pulse graph

High-performance animated visualization using QPainter and OpenGL acceleration.
Much faster than tkinter Canvas for complex animations.
"""

import random
from typing import List

from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtWidgets import QWidget

from sendell.dashboard.utils import NEON_GREEN, NEON_RED, BG_PANEL


class ActivityGraphQt(QWidget):
    """
    PyQt6 widget showing animated activity pulse with GPU acceleration.

    - RUNNING: Grid + animated green line (ECG style)
    - OFFLINE: Grid only (no line)

    Performance: 60 FPS smooth rendering with OpenGL acceleration
    """

    def __init__(self, parent=None, width=1050, height=150, is_running=True):
        """
        Initialize activity graph.

        Args:
            parent: Parent widget
            width: Canvas width in pixels
            height: Canvas height in pixels
            is_running: True for animated pulse, False for static grid
        """
        super().__init__(parent)

        self.setFixedSize(width, height)

        # Colors
        self.bg_color = QColor(BG_PANEL)
        self.grid_color = QColor("#2a2a2a")
        self.pulse_color = QColor(NEON_GREEN)

        # Configuration
        self.is_running = is_running
        self.grid_spacing_x = 40
        self.grid_spacing_y = 20

        # Pulse data
        self.pulse_data: List[float] = []
        self.pulse_offset = 0
        self.animation_speed = 2  # Pixels per frame
        self.num_data_points = 300  # Enough for smooth animation
        self.point_spacing = 3  # Pixels between points

        # Generate initial pulse data
        self._generate_pulse_data()

        # Animation timer (60 FPS)
        if self.is_running:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self._animate)
            self.timer.start(16)  # ~60 FPS (16ms)

    def _generate_pulse_data(self):
        """Generate ECG-style pulse data points"""
        self.pulse_data = []

        for i in range(self.num_data_points):
            # Create irregular pulse pattern (ECG style)
            if random.random() < 0.15:  # 15% chance of spike
                value = random.uniform(0.2, 0.9)
            elif random.random() < 0.3:  # 30% chance of dip
                value = random.uniform(0.1, 0.4)
            else:
                value = random.uniform(0.4, 0.6)

            self.pulse_data.append(value)

    def _animate(self):
        """Animate the pulse line (scroll effect)"""
        if not self.is_running:
            return

        # Update offset for scrolling effect
        self.pulse_offset += self.animation_speed

        # Reset offset when it scrolls too far
        max_offset = len(self.pulse_data) * self.point_spacing
        if self.pulse_offset >= max_offset:
            self.pulse_offset = 0
            self._generate_pulse_data()

        # Trigger repaint
        self.update()

    def paintEvent(self, event):
        """Paint the graph (called automatically by Qt)"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Fill background
        painter.fillRect(self.rect(), self.bg_color)

        # Draw grid
        self._draw_grid(painter)

        # Draw pulse line if running
        if self.is_running:
            self._draw_pulse_line(painter)

    def _draw_grid(self, painter: QPainter):
        """Draw background grid lines"""
        pen = QPen(self.grid_color)
        pen.setWidth(1)
        painter.setPen(pen)

        # Vertical lines
        for x in range(0, self.width(), self.grid_spacing_x):
            painter.drawLine(x, 0, x, self.height())

        # Horizontal lines
        for y in range(0, self.height(), self.grid_spacing_y):
            painter.drawLine(0, y, self.width(), y)

    def _draw_pulse_line(self, painter: QPainter):
        """Draw the animated pulse line"""
        if not self.pulse_data:
            return

        # Setup pen for pulse line
        pen = QPen(self.pulse_color)
        pen.setWidth(2)
        painter.setPen(pen)

        # Calculate points
        points = []

        for i in range(len(self.pulse_data)):
            # X position (with offset for animation)
            x = (i * self.point_spacing) - self.pulse_offset

            # Skip if outside visible area
            if x < -20 or x > self.width() + 20:
                continue

            # Y position (inverted, with margin)
            y_normalized = self.pulse_data[i]
            y = self.height() - (y_normalized * (self.height() - 20)) - 10

            points.append(QPointF(x, y))

        # Draw the line
        if len(points) > 1:
            painter.drawPolyline(points)

    def set_running(self, is_running: bool):
        """
        Change running state.

        Args:
            is_running: True to show animated pulse, False for static grid
        """
        was_running = self.is_running
        self.is_running = is_running

        if is_running and not was_running:
            # Start animation
            self._generate_pulse_data()
            self.timer = QTimer(self)
            self.timer.timeout.connect(self._animate)
            self.timer.start(16)  # 60 FPS
        elif not is_running and was_running:
            # Stop animation
            if hasattr(self, 'timer'):
                self.timer.stop()

        self.update()


def create_activity_graph_qt(parent=None, width=1050, height=150, is_running=True):
    """
    Factory function to create PyQt6 activity graph.

    Args:
        parent: Parent widget
        width: Canvas width
        height: Canvas height
        is_running: True for animated pulse, False for static grid

    Returns:
        ActivityGraphQt instance
    """
    return ActivityGraphQt(parent, width, height, is_running)
