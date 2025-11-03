"""
Test Script for VS Code Monitor

Tests VS Code process detection, workspace identification, and terminal discovery.
Based on investigation: investigacionvscodemonitoring.txt (Part 5)
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sendell.vscode import VSCodeMonitor


def test_vscode_detection():
    """Test VS Code process detection and report"""
    print("\n" + "=" * 70)
    print("VS CODE MONITOR TEST")
    print("=" * 70)

    print("\n[INITIALIZING] VSCodeMonitor...")
    monitor = VSCodeMonitor()

    print("[SCANNING] Looking for VS Code instances...\n")
    instances = monitor.find_vscode_instances()

    if not instances:
        print("❌ No VS Code instances found.")
        print("\nTroubleshooting:")
        print("  1. Make sure VS Code is running")
        print("  2. Open a project/folder in VS Code")
        print("  3. Open some integrated terminals")
        print("  4. Re-run this script")
        return

    print(f"✅ Found {len(instances)} VS Code instance(s)\n")

    # Print detailed report
    for i, instance in enumerate(instances, 1):
        print(f"{'─' * 70}")
        print(f"INSTANCE {i}")
        print(f"{'─' * 70}")
        print(f"  PID:        {instance.pid}")
        print(f"  Executable: {instance.name}")
        print(f"  Insiders:   {instance.is_insiders}")
        print(f"  Started:    {instance.create_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Workspace info
        print(f"\n  WORKSPACE:")
        ws = instance.workspace
        print(f"    Type: {ws.workspace_type}")

        if ws.workspace_name:
            print(f"    Name: {ws.workspace_name}")
        else:
            print(f"    Name: (no workspace open)")

        if ws.workspace_path:
            print(f"    Path: {ws.workspace_path}")

        if ws.workspace_file:
            print(f"    File: {ws.workspace_file}")

        if ws.folders:
            print(f"\n    Multi-root workspace with {len(ws.folders)} folder(s):")
            for folder in ws.folders:
                print(f"      - {folder['name']}: {folder['path']}")

        # Terminals info
        print(f"\n  TERMINALS ({len(instance.terminals)}):")

        if not instance.terminals:
            print(f"    (no terminals detected)")
        else:
            for j, term in enumerate(instance.terminals, 1):
                print(f"\n    Terminal {j}:")
                print(f"      PID:    {term.pid}")
                print(f"      Type:   {term.shell_type}")
                print(f"      Status: {term.status}")
                print(f"      CWD:    {term.cwd}")
                print(f"      Started: {term.create_time.strftime('%H:%M:%S')}")

        print()

    # Summary
    total_terminals = sum(len(inst.terminals) for inst in instances)
    print(f"{'─' * 70}")
    print(f"SUMMARY")
    print(f"{'─' * 70}")
    print(f"  Total VS Code Instances: {len(instances)}")
    print(f"  Total Terminals:         {total_terminals}")

    # Breakdown by shell type
    shell_counts = {}
    for instance in instances:
        for term in instance.terminals:
            shell_counts[term.shell_type] = shell_counts.get(term.shell_type, 0) + 1

    if shell_counts:
        print(f"\n  Terminals by type:")
        for shell_type, count in sorted(shell_counts.items()):
            print(f"    {shell_type}: {count}")

    print(f"{'─' * 70}\n")


def test_specific_workspace(workspace_name: str):
    """Test finding a specific workspace by name"""
    print(f"\n[SEARCH] Looking for workspace: '{workspace_name}'...")

    monitor = VSCodeMonitor()
    instance = monitor.find_instance_by_workspace(workspace_name)

    if instance:
        print(f"✅ Found workspace '{workspace_name}'")
        print(f"   PID: {instance.pid}")
        print(f"   Path: {instance.workspace.workspace_path}")
        print(f"   Terminals: {len(instance.terminals)}")
    else:
        print(f"❌ Workspace '{workspace_name}' not found")
        print("\nAvailable workspaces:")
        instances = monitor.find_vscode_instances()
        for inst in instances:
            if inst.workspace.workspace_name:
                print(f"  - {inst.workspace.workspace_name}")


def main():
    """Main test menu"""
    print("\n" + "=" * 70)
    print("VS CODE MONITOR TEST SUITE")
    print("=" * 70)
    print("\nChoose a test:\n")
    print("1. Full detection test (recommended)")
    print("2. Search for specific workspace")
    print("3. Quick scan (just count instances)")
    print("\n0. Exit")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        test_vscode_detection()

    elif choice == "2":
        workspace_name = input("\nEnter workspace name: ").strip()
        test_specific_workspace(workspace_name)

    elif choice == "3":
        print("\n[QUICK SCAN]")
        monitor = VSCodeMonitor()
        instances = monitor.find_vscode_instances()
        terminals = monitor.get_terminal_count()
        print(f"  VS Code instances: {len(instances)}")
        print(f"  Total terminals:   {terminals}")

    elif choice == "0":
        print("Goodbye!")

    else:
        print("Invalid choice!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback

        traceback.print_exc()
