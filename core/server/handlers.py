"""
core/server/handlers.py
v3.1 - Thin handlers for FastAPI routes and WS message dispatch.
Delegates core logic to core.multiplayer.GameSyncManager (ELO, engine, persist).
Keeps server/main.py focused on app, middleware, auth, endpoints wiring.
"""

import json
import logging
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials

# Import the pure core manager
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.multiplayer import manager as mp_manager, GameState
from core.server.models import (
    User, get_current_user, create_access_token, SECRET_KEY, ALGORITHM, DEMO_USERS,
    MatchCreate
)
from jose import jwt

logger = logging.getLogger("dart.handlers")

async def handle_ws_message(websocket: WebSocket, match_id: str, player_name: str, raw: str):
    """Dispatch one WS message. Called from the WS loop in main."""
    try:
        event = json.loads(raw)
    except Exception:
        await websocket.send_text(json.dumps({"type": "error", "message": "bad json"}))
        return

    et = event.get("type")
    if et == "throw":
        darts = event.get("darts", [])
        res = mp_manager.record_throw(match_id, player_name, darts)
        # broadcast is done by caller after; or here we can return and broadcast in endpoint
        await websocket.send_text(json.dumps(res))  # echo to sender; main also broadcasts
        # For full: after record, main will call broadcast_state using mp_manager.get_state
    elif et == "command":
        cmd = event.get("command", event.get("cmd", ""))
        res = mp_manager.process_command(match_id, player_name, cmd)
        await websocket.send_text(json.dumps(res))
    elif et == "ping":
        await websocket.send_text(json.dumps({"type": "pong", "ts": event.get("ts")}))
    else:
        await websocket.send_text(json.dumps({"type": "error", "message": f"unknown event {et}"}))

async def ws_auth_and_accept(websocket: WebSocket, match_id: str, player_name: str, token: Optional[str]):
    if token:
        try:
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except Exception:
            await websocket.close(code=1008, reason="bad token")
            return None
    await websocket.accept()
    try:
        state = mp_manager.join(match_id, player_name, websocket)
        return state
    except ValueError as ve:
        await websocket.send_text(json.dumps({"type": "error", "message": str(ve)}))
        await websocket.close(code=1000)
        return None

def create_match_handler(match: MatchCreate, user: Optional[User] = None, demo: bool = False) -> dict:
    import uuid as _uuid
    mid = "match_" + _uuid.uuid4().hex[:10]
    custom = getattr(match, "custom", None)
    state = mp_manager.create_game(mid, match.mode, match.players, custom=custom)
    return {"match_id": mid, "join_code": mid[-6:].upper(), "mode": state.mode}

def get_match_handler(mid: str):
    st = mp_manager.get_state(mid)
    if not st:
        raise HTTPException(404, "Match not found")
    return st

# For direct use in tests or other
__all__ = ["handle_ws_message", "ws_auth_and_accept", "create_match_handler", "get_match_handler"]
