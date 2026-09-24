from typing import Protocol, runtime_checkable, Any
from starlette.websockets import WebSocket

@runtime_checkable
class ITaskBroadcaster(Protocol):
    """
    Protocol for real-time pub/sub task status broadcasting.
    Adheres to the Observer pattern and Single Responsibility Principle.
    """

    async def connect(self, websocket: WebSocket) -> None:
        """Register an active client connection."""
        ...

    async def disconnect(self, websocket: WebSocket) -> None:
        """Unregister a client connection."""
        ...

    def broadcast_sync(self, task_data: dict[str, Any]) -> None:
        """
        Broadcast a task update dictionary across all active connections.
        Can be safely called from sync background worker threads.
        """
        ...

    async def broadcast(self, task_data: dict[str, Any]) -> None:
        """Asynchronously broadcast a task update across all active connections."""
        ...
