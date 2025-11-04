"""
Simple WebSocket test - verify server is accepting connections
"""

import asyncio
import websockets
import json


async def test_connection():
    """Test basic WebSocket connection"""
    print("Testing WebSocket connection to ws://localhost:7000...")

    try:
        async with websockets.connect("ws://localhost:7000") as websocket:
            print("✓ Connected successfully!")

            # Send a test message
            test_message = {
                "id": "test_123",
                "type": "event",
                "category": "system",
                "payload": {
                    "workspaces": [
                        {
                            "name": "test",
                            "path": "C:/test"
                        }
                    ]
                },
                "timestamp": 1000
            }

            print(f"Sending test message: {test_message}")
            await websocket.send(json.dumps(test_message))

            # Wait for response
            response = await websocket.recv()
            print(f"✓ Received response: {response}")

            print("\n✓✓✓ SERVER IS WORKING CORRECTLY! ✓✓✓\n")

    except ConnectionRefusedError:
        print("✗ Connection refused - Server not running")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_connection())
