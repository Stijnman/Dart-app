import json
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="Dart App Sync Server")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        payload = json.dumps(message)
        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception:
                pass

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
