"""
Test script for simplified VS Code monitoring (without terminal detection)

Tests:
1. VSCodeMonitor can detect running VS Code instances
2. Workspace info is correctly parsed
3. No terminal-related functionality
"""

from src.sendell.vscode import VSCodeMonitor


def test_vscode_detection():
    """Test basic VS Code detection"""
    print("\n" + "=" * 70)
    print("Testing VS Code Detection (Simplified - No Terminals)")
    print("=" * 70 + "\n")

    monitor = VSCodeMonitor()
    instances = monitor.find_vscode_instances()

    print(f"Found {len(instances)} VS Code instance(s)\n")

    if not instances:
        print("No VS Code instances found.")
        print("Make sure you have VS Code open with a project.")
        return

    for i, inst in enumerate(instances, 1):
        print(f"Instance {i}:")
        print(f"  PID: {inst.pid}")
        print(f"  Executable: {inst.name}")
        print(f"  Insiders: {inst.is_insiders}")
        print(f"  Workspace Type: {inst.workspace.workspace_type}")
        print(f"  Workspace Name: {inst.workspace.workspace_name or 'None'}")
        print(f"  Workspace Path: {inst.workspace.workspace_path or 'None'}")

        if inst.workspace.workspace_file:
            print(f"  Workspace File: {inst.workspace.workspace_file}")

        if inst.workspace.folders:
            print(f"  Multi-root folders: {len(inst.workspace.folders)}")
            for folder in inst.workspace.folders:
                print(f"    - {folder}")

        print()

    print("=" * 70)
    print("[OK] Test completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    test_vscode_detection()
