"""
dart_app/api/server.py
FastAPI WebSocket companion sync / broadcast server.
Main dart app (or any client) POSTs game state; connected remote displays / companion apps receive live updates via WS.

Run:
    uvicorn dart_app.api.server:app --port 8765

Clients connect: ws://localhost:8765/ws/companion/my-screen-42
Push from main game: POST /broadcast { "match_id": "...", "scores": {...}, ... }
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import json

app = FastAPI(title="Dart Companion Sync Server", version="0.1.0")

class GameStateUpdate(BaseModel):
    match_id: str
    mode: str = "501"
    players: List[Dict[str, Any]] = []   # [{"name": "Alice", "score": 301}, ...]
    current_player: Optional[str] = None
    winner: Optional[str] = None
    message: Optional[str] = None
    extra: Dict[str, Any] = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        data = json.dumps(message)
        dead = []
        for conn in self.active_connections:
            try:
                await conn.send_text(data)
            except Exception:
                dead.append(conn)
        for d in dead:
            self.disconnect(d)

manager = ConnectionManager()

@app.websocket("/ws/companion/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        await websocket.send_text(json.dumps({"type": "welcome", "client_id": client_id, "msg": "connected to dart companion sync"}))
        while True:
            # Companions can send pings or commands if desired; we mostly broadcast from server
            try:
                _ = await asyncio.wait_for(websocket.receive_text(), timeout=30)
            except asyncio.TimeoutError:
                await websocket.send_text(json.dumps({"type": "ping"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/broadcast")
async def broadcast_state(update: GameStateUpdate):
    """Called by the primary dart game instance (Streamlit, CLI, etc.) to push live state."""
    payload = update.model_dump()
    payload["type"] = "state_update"
    payload["ts"] = __import__("datetime").datetime.utcnow().isoformat() + "Z"
    await manager.broadcast(payload)
    return {"status": "broadcasted", "clients": len(manager.active_connections)}

@app.get("/health")
async def health():
    return {"status": "ok", "clients": len(manager.active_connections)}

# Example usage from a game client (requests or httpx):
# requests.post("http://localhost:8765/broadcast", json={
#     "match_id": "m123", "mode": "501", "players": [{"name":"You","score":250}, {"name":"Opp","score":180}],
#     "current_player": "You"
# })
