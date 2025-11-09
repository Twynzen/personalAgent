"""
WebSocket Server for VS Code Extension Communication

Asyncio-based WebSocket server that receives events from VS Code extension
and forwards them to the VSCodeIntegrationManager.
"""

import asyncio
import json
import logging
from typing import Set
import websockets
from websockets.server import WebSocketServerProtocol

from .types import VSCodeEvent
from .manager import get_manager

logger = logging.getLogger(__name__)


class VSCodeWebSocketServer:
    """
    WebSocket server for VS Code extension communication.

    Listens on ws://localhost:7000 and processes events from extension.
    """

    def __init__(self, host: str = 'localhost', port: int = 7000):
        """
        Initialize WebSocket server.

        Args:
            host: Host to bind to (default: localhost)
            port: Port to listen on (default: 7000)
        """
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.manager = get_manager()
        self.server = None  # Will be set in start()
        self._running = False

        logger.info(f"VSCodeWebSocketServer initialized (ws://{host}:{port})")

    async def handler(self, websocket: WebSocketServerProtocol) -> None:
        """
        Handle WebSocket connection.

        Args:
            websocket: Connected WebSocket client
        """
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self.clients.add(websocket)
        logger.info(f"Client connected: {client_id}")

        try:
            async for message in websocket:
                await self._handle_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")

        except Exception as e:
            logger.error(f"Error in handler: {e}", exc_info=True)

        finally:
            self.clients.discard(websocket)

    async def _handle_message(
        self,
        websocket: WebSocketServerProtocol,
        message: str
    ) -> None:
        """
        Process incoming WebSocket message.

        Args:
            websocket: Source websocket
            message: JSON message from extension
        """
        try:
            data = json.loads(message)

            # Parse as VSCodeEvent
            event = VSCodeEvent.from_dict(data)

            # Log event (compact)
            logger.debug(
                f"Event: {event.category}/{event.type} "
                f"from {event.payload.get('workspace', 'unknown')}"
            )

            # Forward to manager
            self.manager.handle_event(event)

            # Send acknowledgment
            await self._send_ack(websocket, event.id)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {e}")
            await self._send_error(websocket, "Invalid JSON")

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            await self._send_error(websocket, str(e))

    async def _send_ack(self, websocket: WebSocketServerProtocol, event_id: str) -> None:
        """Send acknowledgment to client"""
        try:
            response = {
                'id': event_id,
                'type': 'ack',
                'timestamp': int(asyncio.get_event_loop().time() * 1000),
            }
            await websocket.send(json.dumps(response))

        except Exception as e:
            logger.error(f"Failed to send ack: {e}")

    async def _send_error(
        self,
        websocket: WebSocketServerProtocol,
        error_message: str
    ) -> None:
        """Send error response to client"""
        try:
            response = {
                'type': 'error',
                'message': error_message,
                'timestamp': int(asyncio.get_event_loop().time() * 1000),
            }
            await websocket.send(json.dumps(response))

        except Exception as e:
            logger.error(f"Failed to send error: {e}")

    async def broadcast(self, message: dict) -> None:
        """
        Broadcast message to all connected clients.

        Args:
            message: Message to broadcast
        """
        if not self.clients:
            logger.debug("No clients connected for broadcast")
            return

        message_json = json.dumps(message)
        disconnected = set()

        for client in self.clients:
            try:
                await client.send(message_json)

            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)

            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                disconnected.add(client)

        # Remove disconnected clients
        self.clients -= disconnected

    async def send_command_to_terminal(
        self,
        workspace: str,
        terminal: str,
        command: str
    ) -> bool:
        """
        Send command to specific terminal in VS Code.

        Args:
            workspace: Workspace name/path
            terminal: Terminal name
            command: Command to execute

        Returns:
            True if sent successfully, False otherwise
        """
        message = {
            'type': 'command',
            'category': 'terminal',
            'payload': {
                'action': 'send_text',
                'workspace': workspace,
                'terminal': terminal,
                'text': command,
            },
            'timestamp': int(asyncio.get_event_loop().time() * 1000),
        }

        try:
            await self.broadcast(message)
            logger.info(f"Sent command to {workspace}/{terminal}: {command[:50]}")
            return True

        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            return False

    async def start(self) -> None:
        """
        Start WebSocket server.

        Runs indefinitely until stopped.
        """
        if self._running:
            logger.warning("Server already running")
            return

        logger.info(f"Starting WebSocket server on ws://{self.host}:{self.port}")

        try:
            # Create server
            self.server = await websockets.serve(self.handler, self.host, self.port)
            self._running = True
            logger.info("WebSocket server started and ready")

            # Run forever (until cancelled)
            await asyncio.Future()

        except OSError as e:
            if e.errno == 10048:  # Address already in use (Windows)
                logger.error(f"Port {self.port} already in use!")
                raise RuntimeError(
                    f"Port {self.port} is already in use. "
                    "Stop the other process or change the port."
                )
            else:
                raise

        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            raise

        finally:
            self._running = False

    async def stop(self) -> None:
        """Stop WebSocket server"""
        logger.info("Stopping WebSocket server...")

        # Close all client connections
        for client in list(self.clients):
            await client.close()

        self.clients.clear()

        # Close server
        if self.server:
            self.server.close()
            await self.server.wait_closed()

        self._running = False

        logger.info("WebSocket server stopped")

    def is_running(self) -> bool:
        """Check if server is running"""
        return self._running

    def get_stats(self) -> dict:
        """
        Get server statistics.

        Returns:
            Dict with server stats
        """
        return {
            'running': self._running,
            'host': self.host,
            'port': self.port,
            'connected_clients': len(self.clients),
            'total_projects': len(self.manager.projects),
            'total_terminals': sum(
                len(p.terminals) for p in self.manager.projects.values()
            ),
        }


# Global server instance
_server_instance: VSCodeWebSocketServer = None


def get_server() -> VSCodeWebSocketServer:
    """
    Get global server instance.

    Returns:
        Singleton VSCodeWebSocketServer instance
    """
    global _server_instance
    if _server_instance is None:
        _server_instance = VSCodeWebSocketServer()
    return _server_instance


async def start_server_async() -> None:
    """
    Start WebSocket server (async entry point).

    Use this for starting server in async context.
    """
    server = get_server()
    await server.start()


def start_server_background() -> asyncio.Task:
    """
    Start WebSocket server in background task.

    Returns:
        asyncio.Task running the server

    Example:
        >>> task = start_server_background()
        >>> # Server runs in background
        >>> # Later...
        >>> task.cancel()
    """
    loop = asyncio.get_event_loop()
    server = get_server()
    task = loop.create_task(server.start())

    logger.info("WebSocket server started in background")
    return task
