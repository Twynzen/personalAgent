"""
FastAPI server for Sendell Brain Dashboard
Provides REST API + WebSocket for real-time updates
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import logging
from pathlib import Path

from sendell.web.routes import router
from sendell.web.websocket import WebSocketManager
from sendell.web.background import start_vscode_scanner
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

# WebSocket manager
ws_manager = WebSocketManager()

# Include REST routes
app.include_router(router, prefix="/api")


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


# Startup: iniciar scanner en background
@app.on_event("startup")
async def startup():
    logger.info("Starting Sendell Brain API server...")

    # Iniciar VS Code scanner
    asyncio.create_task(start_vscode_scanner(ws_manager))

    logger.info("API server ready on http://localhost:8765")


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
