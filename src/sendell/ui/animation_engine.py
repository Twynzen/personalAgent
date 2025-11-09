"""
Animation Engine for ASCII Arts

Provides animation playback capabilities for ASCII art frames.
Based on techniques from asciiguia.txt - timing, frame management, and looping.
"""

import time
import threading
from typing import List, Optional, Callable
from dataclasses import dataclass


@dataclass
class AnimatedArt:
    """
    Represents an animated ASCII art with multiple frames.

    Attributes:
        name: Unique identifier for the animation
        frames: List of ASCII art frames (strings)
        fps: Frames per second (1-30 typical for ASCII)
        loop: Whether to loop the animation infinitely
    """
    name: str
    frames: List[str]
    fps: int = 10
    loop: bool = True

    def __post_init__(self):
        """Validate animation data"""
        if not self.frames:
            raise ValueError(f"Animation '{self.name}' has no frames")
        if self.fps <= 0 or self.fps > 30:
            raise ValueError(f"FPS must be between 1-30, got {self.fps}")

        self.current_frame_index = 0
        self._is_playing = False

    def get_current_frame(self) -> str:
        """Get the current frame without advancing"""
        return self.frames[self.current_frame_index]

    def next_frame(self) -> str:
        """Advance to next frame and return it"""
        frame = self.frames[self.current_frame_index]

        # Advance index
        self.current_frame_index += 1

        # Handle looping
        if self.current_frame_index >= len(self.frames):
            if self.loop:
                self.current_frame_index = 0
            else:
                self.current_frame_index = len(self.frames) - 1  # Stay on last frame

        return frame

    def reset(self):
        """Reset animation to first frame"""
        self.current_frame_index = 0

    def get_frame_delay(self) -> float:
        """Get delay in seconds between frames"""
        return 1.0 / self.fps

    @property
    def total_frames(self) -> int:
        """Total number of frames in animation"""
        return len(self.frames)

    @property
    def duration(self) -> float:
        """Total duration of one animation cycle in seconds"""
        return self.total_frames / self.fps


class AnimationPlayer:
    """
    Plays animated ASCII art with proper timing and thread management.

    Handles:
    - Frame timing and synchronization
    - Thread-safe playback
    - Callback on frame updates
    """

    def __init__(
        self,
        animated_art: AnimatedArt,
        on_frame_update: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize animation player.

        Args:
            animated_art: The AnimatedArt to play
            on_frame_update: Callback function called with each new frame
        """
        self.animated_art = animated_art
        self.on_frame_update = on_frame_update

        self._playing = False
        self._thread = None
        self._stop_event = threading.Event()

    def start(self):
        """Start playing the animation in background thread"""
        if self._playing:
            return

        self._playing = True
        self._stop_event.clear()
        self.animated_art.reset()

        self._thread = threading.Thread(target=self._play_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the animation playback"""
        self._playing = False
        self._stop_event.set()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _play_loop(self):
        """Internal animation loop (runs in thread)"""
        frame_delay = self.animated_art.get_frame_delay()

        while self._playing and not self._stop_event.is_set():
            # Get next frame
            frame = self.animated_art.next_frame()

            # Call update callback if provided
            if self.on_frame_update:
                try:
                    self.on_frame_update(frame)
                except Exception as e:
                    # Don't crash animation thread on callback errors
                    print(f"Error in frame update callback: {e}")

            # Wait for next frame (compensate for callback time)
            self._stop_event.wait(timeout=frame_delay)

    @property
    def is_playing(self) -> bool:
        """Check if animation is currently playing"""
        return self._playing


def create_simple_toggle(name: str, frame1: str, frame2: str, fps: int = 5) -> AnimatedArt:
    """
    Helper to create simple 2-frame toggle animation.

    Args:
        name: Animation name
        frame1: First frame
        frame2: Second frame
        fps: Frames per second

    Returns:
        AnimatedArt with 2 frames
    """
    return AnimatedArt(
        name=name,
        frames=[frame1, frame2],
        fps=fps,
        loop=True
    )


def create_cycle_animation(
    name: str,
    frames: List[str],
    fps: int = 10,
    loop: bool = True
) -> AnimatedArt:
    """
    Helper to create multi-frame cycle animation.

    Args:
        name: Animation name
        frames: List of frames
        fps: Frames per second
        loop: Whether to loop

    Returns:
        AnimatedArt instance
    """
    return AnimatedArt(
        name=name,
        frames=frames,
        fps=fps,
        loop=loop
    )
