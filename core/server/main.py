"""
Dart Game Pro v3.1 - FastAPI WebSocket Multiplayer Server
Production-ready real-time backend for online dart matches.
Uses GameSyncManager for state, Redis for pub/sub (optional), JWT auth, rate limiting.
Integrates with existing core.engine for game logic.
"""

import os
import json
import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn

# Optional Redis
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Core integration
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.engine import DartGameEngine
from core.player import Player
from core.constants import ALL_MODES

# v3.1 shared models + auth (prevents cycles)
from core.server.models import (
    Token, User, MatchCreate, ThrowEvent, CommandEvent,
    create_access_token, get_current_user, DEMO_USERS,
    SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, RATE_LIMIT_PER_MIN,
)

# v3.1 Use pure core multiplayer manager (ELO + engine + persist inside)
from core.multiplayer import (
    manager as mp_manager,
    GameState as MPGameState,
    HAS_ELO,
    HAS_DB_V2,
)
# Also import handlers for message dispatch
try:
    from core.server.handlers import handle_ws_message, ws_auth_and_accept, create_match_handler
    HAS_HANDLERS = True
except Exception as _imp_e:
    HAS_HANDLERS = False
    handle_ws_message = None
    ws_auth_and_accept = None
    create_match_handler = None

import json as _json  # fallback
from pathlib import Path
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
ONLINE_HISTORY_PATH = DATA_DIR / "online_match_history.json"

# Config for redis etc (models has the common)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = FastAPI(title="Dart Game Pro Multiplayer API", version="3.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In prod: restrict to your Streamlit domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Auth endpoint (uses models helpers) ---
@app.post("/token", response_model=Token)
async def login(form_data: dict):  # In real: use OAuth2PasswordRequestForm
    username = form_data.get("username")
    password = form_data.get("password")
    if username in DEMO_USERS and DEMO_USERS[username] == password:
        access_token = create_access_token(data={"sub": username})
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Incorrect username or password (demo: demo/demo123)")

# --- Rate Limiter (simple in-memory) ---
rate_limits: Dict[str, List[datetime]] = {}

async def check_rate_limit(user: User):
    now = datetime.utcnow()
    user_limits = rate_limits.setdefault(user.username, [])
    user_limits = [t for t in user_limits if (now - t).total_seconds() < 60]
    if len(user_limits) >= RATE_LIMIT_PER_MIN:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    user_limits.append(now)
    rate_limits[user.username] = user_limits

# --- Delegation to pure core.multiplayer ---
# Keep 'manager' and 'GameState' names for backward compat in this module / tests
GameState = MPGameState
manager = mp_manager  # the singleton from core.multiplayer (has .games, .elo, create_game etc)

# Optional Redis setup on the manager (pub/sub)
if REDIS_AVAILABLE and not getattr(manager, 'redis', None):
    try:
        manager.redis = redis.from_url(REDIS_URL, decode_responses=True)
    except Exception as e:
        logging.warning(f"Redis unavailable for multiplayer: {e}")

async def _broadcast_state(match_id: str, message: dict):
    """Local WS broadcast + optional Redis publish. Called from WS handlers."""
    if match_id not in manager.games:
        return
    state = manager.games[match_id]
    data = json.dumps(message)
    for ws in list(getattr(state, 'connected_clients', {}).values()):
        try:
            await ws.send_text(data)
        except Exception:
            pass
    if getattr(manager, 'redis', None):
        try:
            await manager.redis.publish(f"game:{match_id}", data)
        except Exception:
            pass

# --- WebSocket Endpoint (production: delegates to mp + handlers) ---
@app.websocket("/ws/{match_id}/{player_name}")
async def websocket_endpoint(websocket: WebSocket, match_id: str, player_name: str, token: Optional[str] = Query(None)):
    """Production WS with token auth, rate limit, real engine via core.multiplayer."""
    if token:
        try:
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except Exception:
            await websocket.close(code=1008, reason="Invalid or expired token")
            return
    await websocket.accept()
    try:
        # join via mp_manager (sync under the hood)
        state = manager.join(match_id, player_name, websocket)
        # initial
        initial = manager.get_state(match_id)
        if initial:
            await websocket.send_text(json.dumps({"type": "initial_state", **initial}))
        while True:
            raw = await websocket.receive_text()
            try:
                await check_rate_limit(User(username=player_name))
            except HTTPException as rate_err:
                await websocket.send_text(json.dumps({"type": "error", "message": str(rate_err.detail)}))
                continue
            if HAS_HANDLERS and handle_ws_message:
                await handle_ws_message(websocket, match_id, player_name, raw)
            else:
                # Fallback inline dispatch (uses mp_manager) — strict Pydantic parsing
                try:
                    event = json.loads(raw)
                    et = event.get("type")
                    if et == "throw":
                        parsed = ThrowEvent(**event)
                        res = manager.record_throw(match_id, player_name, parsed.darts)
                        await _broadcast_state(match_id, res)
                    elif et == "command":
                        parsed = CommandEvent(**event)
                        res = manager.process_command(match_id, player_name, parsed.command)
                        await _broadcast_state(match_id, res)
                    elif et == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                    else:
                        await websocket.send_text(json.dumps({"type": "error", "message": "unknown event type"}))
                except Exception as parse_err:
                    await websocket.send_text(json.dumps({"type": "error", "message": f"bad event: {parse_err}"}))
    except WebSocketDisconnect:
        manager.leave(match_id, player_name)
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
        except:
            pass
        manager.leave(match_id, player_name)

# --- REST Endpoints for match creation etc. (thin, delegate to mp_manager + handlers) ---
@app.post("/matches")
async def create_match(match: MatchCreate, user: User = Depends(get_current_user)):
    mid = "match_" + uuid.uuid4().hex[:10]
    st = manager.create_game(mid, match.mode, match.players, custom=match.custom)
    await _broadcast_state(mid, {"type": "game_created", "match_id": mid, "players": match.players})
    return {"match_id": mid, "join_code": mid[-6:].upper(), "mode": st.mode}

@app.post("/demo/matches")
async def create_demo_match(match: MatchCreate):
    """Public demo (no auth) for UI/curl tests. Supports custom modes."""
    mid = "match_" + uuid.uuid4().hex[:10]
    st = manager.create_game(mid, match.mode, match.players, custom=match.custom)
    await _broadcast_state(mid, {"type": "game_created", "match_id": mid, "players": match.players})
    return {"match_id": mid, "join_code": mid[-6:].upper(), "mode": getattr(st, 'mode', match.mode)}

@app.get("/matches/{match_id}")
async def get_match(match_id: str):
    st = manager.get_state(match_id)
    if not st:
        raise HTTPException(404, "Match not found")
    return st

@app.get("/matches")
async def list_open_matches():
    res = []
    for mid, gs in manager.games.items():
        if len(getattr(gs, 'connected_clients', {})) < 4:
            res.append({"match_id": mid, "players": gs.players, "mode": gs.mode})
    return res

@app.get("/elo/standings")
async def get_elo_standings():
    if getattr(manager, 'elo', None):
        return manager.elo.get_standings()
    return []

@app.get("/history/{player_name}")
async def get_player_history(player_name: str, limit: int = 20):
    if HAS_DB_V2:
        try:
            from core.database_v2 import get_match_history as _gmh
            h = _gmh(1, limit=limit)
            return [r for r in h if player_name.lower() in str(r).lower()]
        except Exception:
            pass
    if ONLINE_HISTORY_PATH and ONLINE_HISTORY_PATH.exists():
        try:
            allh = _json.loads(ONLINE_HISTORY_PATH.read_text(encoding="utf-8") or "[]")
            return [r for r in allh if player_name.lower() in str(r.get("players", [])).lower()][:limit]
        except Exception:
            pass
    return []

@app.post("/admin/cleanup")
async def cleanup_stale():
    """Demo/admin endpoint to force stale game cleanup (call from cron or healthcheck in prod)."""
    removed = manager.cleanup_stale_games(max_idle_seconds=3600)
    return {"removed": removed, "active_games": len(manager.games)}

# --- Streaming / OBS overlay endpoints (P1-2) ---
@app.get("/stream/{match_id}")
async def stream_match(match_id: str):
    """JSON feed for OBS browser source, web overlays, or external dashboards. Poll or use WS for live."""
    st = manager.get_state(match_id)
    if not st:
        raise HTTPException(404, "Match not found")
    # enrich for overlays
    st["ts"] = datetime.utcnow().isoformat()
    st["live"] = match_id in manager.games and len(getattr(manager.games[match_id], 'connected_clients', {})) > 0
    return st

@app.get("/overlays/obs/{match_id}", response_class=HTMLResponse)
async def obs_overlay(match_id: str):
    """Minimal HTML overlay for OBS. In real: use /stream json + JS poll or WS."""
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Dart Overlay {match_id}</title>
<style>body{{font-family:system-ui;margin:0;padding:12px;background:rgba(0,0,0,0.6);color:#fff}} .score{{font-size:28px}}</style>
</head><body>
<h3>🎯 Live — {match_id}</h3>
<div id="s"></div>
<script>
async function poll(){{ try{{ const r=await fetch('/stream/{match_id}'); const j=await r.json(); document.getElementById('s').innerHTML = '<pre>'+JSON.stringify(j.scores||j,null,2)+'</pre>'; }}catch(e){{}} setTimeout(poll,800); }}
poll();
</script>
</body></html>"""
    return HTMLResponse(html)

# For local dev
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)