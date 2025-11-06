"""
Test script to open EPIC Dashboard - Cyberpunk Style Monitoring
Usage: uv run python test_dashboard.py
"""

from sendell.agent.epic_dashboard import show_epic_dashboard
from sendell.vscode_integration.manager import VSCodeIntegrationManager

print("=" * 70)
print("⚡ SENDELL EPIC DASHBOARD - Cyberpunk Monitoring Interface")
print("=" * 70)
print()
print("Initializing VS Code manager...")

try:
    # Initialize VS Code manager
    manager = VSCodeIntegrationManager()
    print("✅ VS Code manager initialized")
except Exception as e:
    print(f"⚠️  Warning: Could not initialize VS Code manager: {e}")
    print("   Dashboard will run without WebSocket data")
    manager = None

print()
print("Opening EPIC Dashboard...")
print()
print("Features:")
print("  ✨ Cyberpunk Matrix-style interface")
print("  📊 Animated graphs (CPU, RAM, Disk I/O)")
print("  ⭕ Pulsing project indicators")
print("  🔍 psutil vs WebSocket comparison")
print("  ⚡ Background thread - NO FREEZING (threading + Queue)")
print("  🎯 20 FPS smooth animations")
print("  🔄 Scans VS Code instances every 10 seconds")
print()
print("Press Ctrl+C or close window to exit")
print("=" * 70)
print()

# Open epic dashboard with manager (like expectativa.png)
show_epic_dashboard(vscode_manager=manager)
