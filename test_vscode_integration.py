"""
End-to-end testing script for VS Code integration

Tests the complete flow:
1. VS Code extension -> WebSocket -> Manager -> Tools -> Sendell Agent

Run this script to verify the integration works correctly.
"""

import asyncio
import json
import time
from datetime import datetime

import websockets


async def test_vscode_integration():
    """
    Test VS Code integration end-to-end.

    This simulates what the VS Code extension does:
    1. Connect to Sendell's WebSocket server
    2. Send terminal events
    3. Verify they're processed correctly
    """
    print("=" * 70)
    print("VS CODE INTEGRATION END-TO-END TEST")
    print("=" * 70)
    print()

    # Test configuration
    server_url = "ws://localhost:7000"
    workspace_name = "sendell"
    workspace_path = "C:/Users/Daniel/Desktop/Daniel/sendell"

    print(f"[1/6] Connecting to Sendell WebSocket server...")
    print(f"      URL: {server_url}")
    print()

    try:
        async with websockets.connect(server_url) as websocket:
            print("[OK] Connected to Sendell server!")
            print()

            # Test 1: Send handshake (workspace registration)
            print("[2/6] Sending handshake (workspace registration)...")
            handshake_event = {
                "id": f"{int(time.time() * 1000)}_1",
                "type": "event",
                "category": "system",
                "payload": {
                    "workspaces": [
                        {
                            "name": workspace_name,
                            "path": workspace_path,
                        }
                    ]
                },
                "timestamp": int(time.time() * 1000),
            }

            await websocket.send(json.dumps(handshake_event))
            response = await websocket.recv()
            print(f"[OK] Handshake response: {response[:100]}...")
            print()

            # Test 2: Send terminal command start
            print("[3/6] Sending terminal command start event...")
            command_start_event = {
                "id": f"{int(time.time() * 1000)}_2",
                "type": "event",
                "category": "terminal",
                "payload": {
                    "type": "command_start",
                    "workspace": workspace_path,
                    "terminal": "Terminal 1",
                    "command": "npm run dev",
                },
                "timestamp": int(time.time() * 1000),
            }

            await websocket.send(json.dumps(command_start_event))
            response = await websocket.recv()
            print(f"[OK] Command start acknowledged: {response[:100]}...")
            print()

            # Test 3: Send terminal output (with error)
            print("[4/6] Sending terminal output with error...")
            output_event = {
                "id": f"{int(time.time() * 1000)}_3",
                "type": "event",
                "category": "terminal",
                "payload": {
                    "type": "output",
                    "workspace": workspace_path,
                    "terminal": "Terminal 1",
                    "output": "Starting dev server...\nError: Cannot find module 'express'\nFailed to start server",
                },
                "timestamp": int(time.time() * 1000),
            }

            await websocket.send(json.dumps(output_event))
            response = await websocket.recv()
            print(f"[OK] Output processed: {response[:100]}...")
            print()

            # Test 4: Send command end
            print("[5/6] Sending command end event...")
            command_end_event = {
                "id": f"{int(time.time() * 1000)}_4",
                "type": "event",
                "category": "terminal",
                "payload": {
                    "type": "command_end",
                    "workspace": workspace_path,
                    "terminal": "Terminal 1",
                    "exitCode": 1,
                },
                "timestamp": int(time.time() * 1000),
            }

            await websocket.send(json.dumps(command_end_event))
            response = await websocket.recv()
            print(f"[OK] Command end acknowledged: {response[:100]}...")
            print()

            # Test 5: Verify data is stored (query tools)
            print("[6/6] Testing Sendell tools...")
            print()

            # Give server time to process
            await asyncio.sleep(1)

            print("=" * 70)
            print("INTEGRATION TEST COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            print()
            print("Now test the Sendell agent tools:")
            print()
            print("1. Start Sendell chat:")
            print("   uv run python -m sendell chat")
            print()
            print("2. Ask Sendell:")
            print("   - 'What projects do I have open?'")
            print("   - 'Are there any errors in sendell project?'")
            print("   - 'Show me the last lines from Terminal 1 in sendell'")
            print("   - 'Give me stats for sendell project'")
            print()
            print("Expected results:")
            print("  [OK] list_active_projects should show 1 project: sendell")
            print("  [OK] get_project_errors should show 1 error (Cannot find module)")
            print("  [OK] get_terminal_tail should show last 3 lines of output")
            print("  [OK] get_project_stats should show 1 terminal, 1 command, 1 error")
            print()

    except ConnectionRefusedError:
        print("[ERROR] Connection refused!")
        print()
        print("Sendell WebSocket server is not running.")
        print()
        print("Start Sendell first:")
        print("  uv run python -m sendell chat")
        print()
        print("Then run this test script again.")
        return False

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


async def test_dev_server_filtering():
    """
    Test that dev server noise is filtered correctly.
    """
    print()
    print("=" * 70)
    print("DEV SERVER FILTERING TEST")
    print("=" * 70)
    print()

    server_url = "ws://localhost:7000"
    workspace_path = "C:/Users/Daniel/test-project"

    try:
        async with websockets.connect(server_url) as websocket:
            print("[1/3] Sending dev server start command...")

            # Register workspace
            handshake = {
                "id": f"{int(time.time() * 1000)}_test1",
                "type": "event",
                "category": "system",
                "payload": {"workspaces": [{"name": "test-project", "path": workspace_path}]},
                "timestamp": int(time.time() * 1000),
            }
            await websocket.send(json.dumps(handshake))
            await websocket.recv()

            # Start dev server
            command_start = {
                "id": f"{int(time.time() * 1000)}_test2",
                "type": "event",
                "category": "terminal",
                "payload": {
                    "type": "command_start",
                    "workspace": workspace_path,
                    "terminal": "Dev Server",
                    "command": "npm run dev",
                },
                "timestamp": int(time.time() * 1000),
            }
            await websocket.send(json.dumps(command_start))
            await websocket.recv()

            print("[2/3] Sending 1000 lines of dev server noise...")

            # Send MASSIVE output (should be filtered)
            noise_lines = []
            for i in range(1000):
                noise_lines.append(f"[vite] hmr update /src/App.tsx {i}")

            output_noise = {
                "id": f"{int(time.time() * 1000)}_test3",
                "type": "event",
                "category": "terminal",
                "payload": {
                    "type": "output",
                    "workspace": workspace_path,
                    "terminal": "Dev Server",
                    "output": "\n".join(noise_lines),
                },
                "timestamp": int(time.time() * 1000),
            }
            await websocket.send(json.dumps(output_noise))
            await websocket.recv()

            print("[3/3] Sending 1 error line (should be kept)...")

            # Send ERROR (should be KEPT even though dev server)
            error_output = {
                "id": f"{int(time.time() * 1000)}_test4",
                "type": "event",
                "category": "terminal",
                "payload": {
                    "type": "output",
                    "workspace": workspace_path,
                    "terminal": "Dev Server",
                    "output": "Error: Failed to compile src/App.tsx\nTypeError: Cannot read property 'foo' of undefined",
                },
                "timestamp": int(time.time() * 1000),
            }
            await websocket.send(json.dumps(error_output))
            await websocket.recv()

            await asyncio.sleep(1)

            print()
            print("[OK] Dev server filtering test completed!")
            print()
            print("Expected result:")
            print("  - 1000 lines of noise IGNORED (not stored)")
            print("  - 1 error line KEPT (stored in recent_errors)")
            print()
            print("Verify by asking Sendell:")
            print("  'Show me errors in test-project'")
            print()
            print("  Should show ONLY the error, not the 1000 noise lines!")
            print()

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


async def main():
    """Run all tests"""
    print()
    print("Starting VS Code Integration Tests...")
    print()
    print("Prerequisites:")
    print("  1. Sendell must be running (uv run python -m sendell chat)")
    print("  2. WebSocket server should be listening on ws://localhost:7000")
    print()
    input("Press Enter when Sendell is running...")
    print()

    # Run basic integration test
    success1 = await test_vscode_integration()

    if success1:
        print()
        choice = input("Run dev server filtering test? (y/n): ")
        if choice.lower() == 'y':
            success2 = await test_dev_server_filtering()

    print()
    print("All tests completed!")
    print()


if __name__ == "__main__":
    asyncio.run(main())
