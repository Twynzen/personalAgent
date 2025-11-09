"""
Test PySide6 GPU-accelerated dashboard performance

This script tests the standalone PySide6 widget to verify 60 FPS animations
and GPU acceleration are working correctly.
"""

import sys
import time
from PySide6.QtWidgets import QApplication
from sendell.dashboard.project_control_qt import create_project_control_widget_qt


def main():
    """Test PySide6 dashboard widget"""
    print("=" * 60)
    print("PySide6 Dashboard Performance Test")
    print("=" * 60)
    print()
    print("Testing GPU-accelerated dashboard widget...")
    print("Expected: Smooth 60 FPS animations with pulse graphs")
    print()
    print("Instructions:")
    print("1. Watch the animated pulse graphs (green ECG-style lines)")
    print("2. Verify smooth animation (no lag or stuttering)")
    print("3. Check system metrics update every ~5 seconds")
    print("4. Close window when done testing")
    print()
    print("=" * 60)

    # Create Qt application
    app = QApplication(sys.argv)

    # Create widget
    widget = create_project_control_widget_qt()
    widget.setWindowTitle("Sendell Dashboard - PySide6 GPU-Accelerated Test")
    widget.show()

    # Run event loop
    start_time = time.time()
    exit_code = app.exec()
    duration = time.time() - start_time

    print()
    print("=" * 60)
    print(f"Test completed. Duration: {duration:.1f}s")
    print("If animations were smooth and fast, GPU acceleration is working!")
    print("=" * 60)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
