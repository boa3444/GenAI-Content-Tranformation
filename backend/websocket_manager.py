import json
import asyncio
import logging
from typing import Dict, Any, Optional
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Maps client_id -> WebSocket connection
        self.active_connections: Dict[str, WebSocket] = {}
        self._locks: Dict[str, asyncio.Lock] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self._locks[client_id] = asyncio.Lock()
        logger.info(f"WebSocket client connected: {client_id}")
        # Send initial confirmation
        await self.send_json(client_id, {
            "type": "connection_ack",
            "client_id": client_id,
            "message": "Connected to Transformation Engine WebSocket"
        })

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self._locks:
            del self._locks[client_id]
        logger.info(f"WebSocket client disconnected: {client_id}")

    async def send_json(self, client_id: str, data: Dict[str, Any]):
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            lock = self._locks.get(client_id)
            try:
                if lock:
                    async with lock:
                        await websocket.send_text(json.dumps(data))
                else:
                    await websocket.send_text(json.dumps(data))
            except Exception as e:
                logger.error(f"Error sending WebSocket message to {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast_status(self, client_id: str, step: str, progress: int, message: str, data: Any = None):
        """Helper to push real-time execution step updates."""
        payload = {
            "type": "status_update",
            "step": step,
            "progress": progress, # 0 to 100
            "message": message,
            "data": data
        }
        await self.send_json(client_id, payload)

    async def broadcast_spoke_result(self, client_id: str, spoke: str, result: Dict[str, Any]):
        """Helper to push completed spoke artifact result."""
        payload = {
            "type": "spoke_completed",
            "spoke": spoke,
            "result": result
        }
        await self.send_json(client_id, payload)

    async def broadcast_stream_chunk(self, client_id: str, spoke: str, chunk: str, job_id: Optional[str] = None):
        """Helper to push real-time streaming text chunks from Gemini API."""
        payload = {
            "type": "stream_chunk",
            "event": "stream_chunk",
            "job_id": job_id,
            "spoke": spoke,
            "chunk": chunk
        }
        await self.send_json(client_id, payload)

    async def broadcast_error(self, client_id: str, error_msg: str):
        payload = {
            "type": "error",
            "message": error_msg
        }
        await self.send_json(client_id, payload)

manager = ConnectionManager()
