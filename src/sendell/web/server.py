"""
FastAPI server for Sendell Brain Dashboard
Provides REST API + WebSocket for real-time updates
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import logging
import json
from pathlib import Path
from typing import Dict

from sendell.web.routes import router
from sendell.web.websocket import WebSocketManager
from sendell.web.background import start_vscode_scanner, start_idle_checker
from sendell.terminal_manager import get_terminal_manager, TerminalOutput
from sendell.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="Sendell Brain API", version="0.3.0")

# CORS para Angular (dev: 4200, prod: 8765)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:8765"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager for broadcast updates
ws_manager = WebSocketManager()

# Terminal WebSocket connections registry
# {terminal_id: [WebSocket, WebSocket, ...]}
terminal_websockets: Dict[str, list[WebSocket]] = {}

# Include REST routes
app.include_router(router, prefix="/api")


# WebSocket endpoint for project updates (existing)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


# WebSocket endpoint for individual terminals
@app.websocket("/ws/terminal/{project_pid}")
async def terminal_websocket(websocket: WebSocket, project_pid: int):
    """
    WebSocket endpoint for terminal I/O.

    Bidirectional communication:
    - Server -> Client: Output from terminal (stdout/stderr)
    - Client -> Server: Commands to execute
    """
    terminal_id = str(project_pid)
    await websocket.accept()

    logger.info(f"Terminal WebSocket connected for project {project_pid}")

    # Register connection
    if terminal_id not in terminal_websockets:
        terminal_websockets[terminal_id] = []
    terminal_websockets[terminal_id].append(websocket)

    try:
        while True:
            # Receive commands from client
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get('type') == 'input':
                # Send command to terminal
                terminal_manager = get_terminal_manager()
                command = message.get('data', '')

                try:
                    terminal_manager.send_command(terminal_id, command)
                    logger.debug(f"Command sent to terminal {terminal_id}: {command[:50]}")
                except Exception as e:
                    logger.error(f"Error sending command: {e}")
                    await websocket.send_json({
                        'type': 'error',
                        'message': str(e)
                    })

    except WebSocketDisconnect:
        logger.info(f"Terminal WebSocket disconnected for project {project_pid}")
        terminal_websockets[terminal_id].remove(websocket)
        if not terminal_websockets[terminal_id]:
            del terminal_websockets[terminal_id]


# Callback for terminal output broadcasting
async def broadcast_terminal_output(output: TerminalOutput):
    """Broadcast terminal output to connected WebSocket clients"""
    terminal_id = output.terminal_id

    if terminal_id not in terminal_websockets or not terminal_websockets[terminal_id]:
        return

    message = {
        'type': 'output',
        'stream': output.stream,
        'data': output.data,
        'timestamp': output.timestamp.isoformat()
    }

    # Broadcast to all connected clients for this terminal
    for ws in terminal_websockets[terminal_id][:]:  # Copy to avoid modification during iteration
        try:
            await ws.send_json(message)
        except Exception as e:
            logger.error(f"Error broadcasting to terminal WebSocket: {e}")
            try:
                terminal_websockets[terminal_id].remove(ws)
            except ValueError:
                pass


# Global event loop reference for thread-safe async calls
_event_loop = None

# Startup: iniciar scanner en background
@app.on_event("startup")
async def startup():
    global _event_loop
    _event_loop = asyncio.get_event_loop()
    logger.info("Starting Sendell Brain API server...")

    # Initialize TerminalManager and register output callback
    terminal_manager = get_terminal_manager()

    def schedule_broadcast(output):
        """Schedule async broadcast from sync thread context"""
        try:
            asyncio.run_coroutine_threadsafe(
                broadcast_terminal_output(output),
                _event_loop
            )
        except Exception as e:
            logger.error(f"Failed to schedule broadcast: {e}")

    terminal_manager.register_output_callback(schedule_broadcast)
    logger.info("TerminalManager initialized")

    # Iniciar VS Code scanner
    asyncio.create_task(start_vscode_scanner(ws_manager))

    # Iniciar idle terminal checker
    asyncio.create_task(start_idle_checker())

    logger.info("API server ready on http://localhost:8765")


# Shutdown: cleanup
@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down Sendell Brain API server...")

    # Terminate all terminals
    terminal_manager = get_terminal_manager()
    terminal_manager.terminate_all()

    logger.info("Server shutdown complete")


# Servir archivos estaticos de Angular (despues del build)
static_dir = Path(__file__).parent / "static" / "browser"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
    logger.info(f"Serving Angular app from {static_dir}")
else:
    logger.warning(f"Static directory not found: {static_dir}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
