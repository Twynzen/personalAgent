"""
Test script for Claude Code control endpoints
Run this after server is restarted with: uv run python test_claude_endpoints.py
"""

import requests
import json

BASE_URL = "http://localhost:8765/api"


def test_endpoint(name, url, method="GET", data=None):
    """Test a single endpoint"""
    print(f"\n{'=' * 70}")
    print(f"TEST: {name}")
    print(f"{'=' * 70}")
    print(f"URL: {url}")
    print(f"Method: {method}")

    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Response:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"[ERROR] {response.text}")
            return False

    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def main():
    print("=" * 70)
    print("TESTING CLAUDE CODE CONTROL ENDPOINTS")
    print("=" * 70)
    print("Make sure FastAPI server is running on port 8765")
    print()

    results = {}

    # TEST 1: Get Claude terminals
    results['terminals'] = test_endpoint(
        "GET /api/claude/terminals",
        f"{BASE_URL}/claude/terminals"
    )

    # TEST 2: Get Claude sessions
    results['sessions'] = test_endpoint(
        "GET /api/claude/sessions",
        f"{BASE_URL}/claude/sessions"
    )

    # TEST 3: Execute simple command
    results['execute'] = test_endpoint(
        "POST /api/claude/execute",
        f"{BASE_URL}/claude/execute",
        method="POST",
        data={"command": "echo Hello from Sendell", "timeout": 5}
    )

    # TEST 4: Get terminal output (use first PID if any)
    # This will likely fail since we don't have real output capture yet
    print("\n" + "=" * 70)
    print("TEST: GET /api/claude/output/{pid}")
    print("=" * 70)
    print("Skipping - requires a valid Claude Code PID")
    print("You can test manually with: curl http://localhost:8765/api/claude/output/17784")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for name, passed in results.items():
        status = "[OK]" if passed else "[FAILED]"
        print(f"{status} {name}")

    total = len(results)
    passed = sum(results.values())
    print(f"\nPassed: {passed}/{total}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
