import json
import logging
import asyncio
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

logger = logging.getLogger("dart_app.api.server")

app = FastAPI(title="Dart App Sync Server")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            pass

    async def broadcast(self, message: dict):
        payload = json.dumps(message)
        coros = []
        to_remove = []
        for connection in list(self.active_connections):
            async def _send(conn):
                try:
                    await conn.send_text(payload)
                except Exception as exc:
                    logger.debug("Failed sending to websocket: %s", exc)
                    to_remove.append(conn)
            coros.append(_send(connection))
        if coros:
            await asyncio.gather(*coros, return_exceptions=True)
        for c in to_remove:
            self.disconnect(c)

manager = ConnectionManager()

@app.websocket("/ws/match")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                parsed_data = json.loads(data)
                await manager.broadcast({"type": "STATE_UPDATE", "data": parsed_data})
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid format"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as exc:
        logger.exception("Unexpected websocket error: %s", exc)
        manager.disconnect(websocket)
