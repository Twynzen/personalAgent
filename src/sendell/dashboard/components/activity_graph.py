"""
Activity Graph Widget - Animated ECG-style pulse graph

Shows activity with animated green pulse line for RUNNING projects,
or empty grid for OFFLINE projects.
"""

import random
import tkinter as tk
from typing import List

from sendell.dashboard.utils import NEON_GREEN, NEON_RED, BG_PANEL


class ActivityGraph(tk.Canvas):
    """
    Canvas widget showing animated activity pulse.

    - RUNNING: Grid + animated green line (ECG style)
    - OFFLINE: Grid only (no line)
    """

    def __init__(self, parent, width=1050, height=150, is_running=True):
        """
        Initialize activity graph.

        Args:
            parent: Parent widget
            width: Canvas width in pixels
            height: Canvas height in pixels
            is_running: True for animated pulse, False for static grid
        """
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=BG_PANEL,
            highlightthickness=0
        )

        self.width = width
        self.height = height
        self.is_running = is_running

        # Grid configuration
        self.grid_color = "#2a2a2a"  # Dark gray for grid lines
        self.grid_spacing_x = 40  # Horizontal spacing
        self.grid_spacing_y = 20  # Vertical spacing

        # Pulse line data
        self.pulse_data: List[float] = []
        self.pulse_offset = 0  # For animation scroll
        self.animation_speed = 4  # Pixels per frame (faster scroll)

        # Performance optimization
        self.num_data_points = 200  # Reduced from ~550
        self.animation_interval = 100  # 10 FPS (reduced from 20 FPS)

        # Generate initial pulse data
        self._generate_pulse_data()

        # Draw grid (always visible)
        self._draw_grid()

        # Start animation if running
        if self.is_running:
            self._animate()

    def _draw_grid(self):
        """Draw background grid lines"""
        # Vertical lines
        for x in range(0, self.width, self.grid_spacing_x):
            self.create_line(
                x, 0, x, self.height,
                fill=self.grid_color,
                width=1,
                tags="grid"
            )

        # Horizontal lines
        for y in range(0, self.height, self.grid_spacing_y):
            self.create_line(
                0, y, self.width, y,
                fill=self.grid_color,
                width=1,
                tags="grid"
            )

    def _generate_pulse_data(self):
        """Generate ECG-style pulse data points (optimized)"""
        # Reduced number of points for better performance
        self.pulse_data = []

        for i in range(self.num_data_points):
            # Create irregular pulse pattern (ECG style)
            # Random baseline with occasional spikes
            if random.random() < 0.15:  # 15% chance of spike
                # High spike
                value = random.uniform(0.2, 0.9)
            elif random.random() < 0.3:  # 30% chance of dip
                # Low dip
                value = random.uniform(0.1, 0.4)
            else:
                # Normal fluctuation around middle
                value = random.uniform(0.4, 0.6)

            self.pulse_data.append(value)

    def _draw_pulse_line(self):
        """Draw the animated pulse line (optimized)"""
        # Delete previous pulse line
        self.delete("pulse")

        if not self.is_running:
            return

        # Calculate points for the line
        points = []

        # Spacing between points (wider = fewer points drawn)
        point_spacing = 5  # Draw every 5th pixel

        for i in range(len(self.pulse_data)):
            # X position (with offset for animation)
            x = (i * point_spacing) - self.pulse_offset

            # Skip if outside visible area (with small buffer)
            if x < -20 or x > self.width + 20:
                continue

            # Y position (inverted, with margin)
            y_normalized = self.pulse_data[i]
            y = self.height - (y_normalized * (self.height - 20)) - 10

            points.append((x, y))

        # Draw the pulse line (NO smooth for better performance)
        if len(points) > 1:
            flat_points = [coord for point in points for coord in point]
            self.create_line(
                *flat_points,
                fill=NEON_GREEN,
                width=2,
                smooth=False,  # Disabled for performance
                tags="pulse"
            )

    def _animate(self):
        """Animate the pulse line (scroll effect, optimized)"""
        if not self.is_running:
            return

        # Update offset for scrolling effect
        self.pulse_offset += self.animation_speed

        # Reset offset when it scrolls too far
        max_offset = len(self.pulse_data) * 5  # Match point_spacing
        if self.pulse_offset >= max_offset:
            self.pulse_offset = 0
            # Regenerate data for variety
            self._generate_pulse_data()

        # Redraw pulse line
        self._draw_pulse_line()

        # Schedule next frame at reduced FPS for better performance
        self.after(self.animation_interval, self._animate)  # 100ms = 10 FPS

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
            self._animate()
        elif not is_running:
            # Stop animation, clear pulse line
            self.delete("pulse")


def create_activity_graph(parent, width=1050, height=150, is_running=True):
    """
    Factory function to create activity graph.

    Args:
        parent: Parent widget
        width: Canvas width
        height: Canvas height
        is_running: True for animated pulse, False for static grid

    Returns:
        ActivityGraph instance
    """
    return ActivityGraph(parent, width, height, is_running)
