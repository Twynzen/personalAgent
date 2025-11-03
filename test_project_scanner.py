"""
Test Script for Project Scanner

Tests project discovery functionality with real directories.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sendell.projects import ProjectScanner


def test_scan_directory(path: str):
    """Test scanning a specific directory"""
    print("\n" + "=" * 70)
    print(f"TESTING PROJECT SCANNER")
    print("=" * 70)
    print(f"\nScanning directory: {path}\n")

    scanner = ProjectScanner(max_depth=3, timeout_seconds=30)
    result = scanner.scan_directory(Path(path))

    print(f"[RESULTS]")
    print(f"  Duration: {result.scan_duration_seconds:.2f} seconds")
    print(f"  Projects found: {result.total_projects}")
    print(f"  Errors: {len(result.errors)}")

    if result.errors:
        print(f"\n[ERRORS]")
        for error in result.errors[:5]:  # Show first 5 errors
            print(f"  - {error}")

    print(f"\n[BY TYPE]")
    for project_type, count in sorted(result.projects_by_type.items()):
        print(f"  {project_type}: {count}")

    print(f"\n[PROJECTS DETECTED]")
    for i, project in enumerate(result.projects_found, 1):
        print(f"\n  [{i}] {project.name}")
        print(f"      Type: {project.project_type.value}")
        print(f"      Path: {project.path}")

        if project.config:
            if project.config.version:
                print(f"      Version: {project.config.version}")
            if project.config.description:
                print(f"      Description: {project.config.description}")
            if project.config.dependencies:
                dep_count = len(project.config.dependencies)
                print(f"      Dependencies: {dep_count} packages")

    print("\n" + "=" * 70)


def test_multiple_paths():
    """Test scanning multiple common project locations"""
    print("\n" + "=" * 70)
    print("SCANNING MULTIPLE COMMON LOCATIONS")
    print("=" * 70)

    common_paths = [
        Path.home() / "projects",
        Path.home() / "dev",
        Path.home() / "Documents" / "projects",
        Path.home() / "Desktop",
        Path("C:/projects") if sys.platform == "win32" else Path("/projects"),
    ]

    scanner = ProjectScanner(max_depth=2, timeout_seconds=15)

    total_found = 0

    for path in common_paths:
        if path.exists():
            print(f"\n[Scanning] {path}")
            result = scanner.scan_directory(path)
            print(f"  Found: {result.total_projects} projects in {result.scan_duration_seconds:.2f}s")

            for project_type, count in result.projects_by_type.items():
                print(f"    - {project_type}: {count}")

            total_found += result.total_projects

    print(f"\n[TOTAL] {total_found} projects found across all locations")
    print("=" * 70)


def test_specific_project(path: str):
    """Test detection of a specific project directory"""
    print("\n" + "=" * 70)
    print("TESTING SPECIFIC PROJECT DETECTION")
    print("=" * 70)
    print(f"\nChecking: {path}\n")

    scanner = ProjectScanner(max_depth=0)  # Only check this directory
    result = scanner.scan_directory(Path(path))

    if result.total_projects == 0:
        print("  [!] No project detected at this path")
    else:
        project = result.projects_found[0]
        print(f"  [✓] Project detected!")
        print(f"      Name: {project.name}")
        print(f"      Type: {project.project_type.value}")
        print(f"      Config file: {project.config_file}")

        if project.config:
            print(f"\n  [CONFIG]")
            if project.config.version:
                print(f"      Version: {project.config.version}")
            if project.config.description:
                print(f"      Description: {project.config.description}")
            if project.config.author:
                print(f"      Author: {project.config.author}")

            if project.config.dependencies:
                print(f"\n  [DEPENDENCIES] ({len(project.config.dependencies)})")
                for name, version in list(project.config.dependencies.items())[:10]:
                    print(f"      {name}: {version}")
                if len(project.config.dependencies) > 10:
                    print(f"      ... and {len(project.config.dependencies) - 10} more")

            if project.config.scripts:
                print(f"\n  [SCRIPTS] ({len(project.config.scripts)})")
                for name, cmd in list(project.config.scripts.items())[:5]:
                    print(f"      {name}: {cmd}")

    print("\n" + "=" * 70)


def main():
    """Main test menu"""
    print("\n" + "=" * 70)
    print("PROJECT SCANNER TEST SUITE")
    print("=" * 70)
    print("\nChoose a test:\n")
    print("1. Scan a specific directory (you provide path)")
    print("2. Scan common project locations")
    print("3. Test specific project detection (single directory)")
    print("4. Quick test: Scan current directory")
    print("5. Quick test: Scan Sendell project")
    print("\n0. Exit")

    choice = input("\nEnter choice (1-5): ").strip()

    if choice == "1":
        path = input("\nEnter directory path to scan: ").strip()
        test_scan_directory(path)

    elif choice == "2":
        test_multiple_paths()

    elif choice == "3":
        path = input("\nEnter project directory path: ").strip()
        test_specific_project(path)

    elif choice == "4":
        test_scan_directory(".")

    elif choice == "5":
        # Test on Sendell itself
        sendell_path = Path(__file__).parent
        test_specific_project(str(sendell_path))

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
