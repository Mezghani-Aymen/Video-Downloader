import asyncio
import threading
from typing import Set, Any, Optional
from starlette.websockets import WebSocket, WebSocketState
from interfaces.broadcaster import ITaskBroadcaster
from logger import logger

class WebSocketBroadcaster(ITaskBroadcaster):
    """
    Observer pattern implementation managing live WebSocket clients.
    Broadcasts real-time download progress and status updates simultaneously.
    """

    def __init__(self):
        self._active_connections: Set[WebSocket] = set()
        self._lock = threading.Lock()
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Explicitly record the main asyncio event loop."""
        self._loop = loop

    async def connect(self, websocket: WebSocket) -> None:
        """Register client connection and auto-detect event loop."""
        if self._loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                pass

        await websocket.accept()
        with self._lock:
            self._active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Active clients: {len(self._active_connections)}")

    async def disconnect(self, websocket: WebSocket) -> None:
        """Unregister client connection safely."""
        with self._lock:
            self._active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Active clients: {len(self._active_connections)}")

    async def broadcast(self, task_data: dict[str, Any]) -> None:
        """Asynchronously send task status update to all connected clients."""
        with self._lock:
            connections = list(self._active_connections)

        if not connections:
            return

        dead_connections = []
        for ws in connections:
            try:
                if ws.client_state == WebSocketState.CONNECTED:
                    await ws.send_json(task_data)
                else:
                    dead_connections.append(ws)
            except Exception as exc:
                logger.debug(f"Error broadcasting to client: {exc}")
                dead_connections.append(ws)

        if dead_connections:
            with self._lock:
                for ws in dead_connections:
                    self._active_connections.discard(ws)

    def broadcast_sync(self, task_data: dict[str, Any]) -> None:
        """Thread-safe synchronous broadcast dispatch for background workers."""
        if not self._active_connections:
            return

        loop = self._loop
        if loop is None:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = None

        if loop and loop.is_running():
            asyncio.run_coroutine_threadsafe(self.broadcast(task_data), loop)
        else:
            try:
                asyncio.run(self.broadcast(task_data))
            except Exception:
                pass
