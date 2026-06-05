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
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Optional Redis
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# JWT
from jose import JWTError, jwt
from passlib.context import CryptContext

# Core integration
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.engine import DartGameEngine
from core.player import Player
from core.constants import ALL_MODES

# Config
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
RATE_LIMIT_PER_MIN = 60  # per user

app = FastAPI(title="Dart Game Pro Multiplayer API", version="3.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In prod: restrict to your Streamlit domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Models ---
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str

class MatchCreate(BaseModel):
    mode: str = "501"
    players: List[str]
    out_rule: str = "double"

class ThrowEvent(BaseModel):
    match_id: str
    player: str
    darts: List[int]

class CommandEvent(BaseModel):
    match_id: str
    player: str
    command: str  # "undo", "next", etc.

# --- Auth ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return User(username=username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Simple in-memory users for demo (replace with DB)
fake_users_db = {"demo": {"username": "demo", "hashed_password": pwd_context.hash("demo123")}}

@app.post("/token", response_model=Token)
async def login(form_data: dict):  # In real: use OAuth2PasswordRequestForm
    username = form_data.get("username")
    password = form_data.get("password")
    user = fake_users_db.get(username)
    if not user or not pwd_context.verify(password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}

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

# --- Game Sync Manager ---
@dataclass
class GameState:
    match_id: str
    mode: str
    players: List[str]
    engine: Optional[DartGameEngine] = None
    connected_clients: Dict[str, WebSocket] = field(default_factory=dict)
    last_activity: datetime = field(default_factory=datetime.utcnow)

class GameSyncManager:
    def __init__(self):
        self.games: Dict[str, GameState] = {}
        self.redis: Optional[redis.Redis] = None
        if REDIS_AVAILABLE:
            try:
                self.redis = redis.from_url(REDIS_URL, decode_responses=True)
            except Exception as e:
                logging.warning(f"Redis unavailable: {e}")

    async def create_game(self, match_id: str, mode: str, players: List[str], user: User) -> GameState:
        if match_id in self.games:
            return self.games[match_id]
        p_objs = [Player(name) for name in players]
        engine = DartGameEngine(mode=mode, players=p_objs)
        state = GameState(match_id=match_id, mode=mode, players=players, engine=engine)
        self.games[match_id] = state
        await self._broadcast_state(match_id, {"type": "game_created", "match_id": match_id, "players": players})
        return state

    async def join_game(self, match_id: str, player_name: str, websocket: WebSocket):
        if match_id not in self.games:
            raise ValueError("Match not found")
        state = self.games[match_id]
        state.connected_clients[player_name] = websocket
        await self._broadcast_state(match_id, {"type": "player_joined", "player": player_name})
        return state

    async def leave_game(self, match_id: str, player_name: str):
        if match_id in self.games:
            state = self.games[match_id]
            if player_name in state.connected_clients:
                del state.connected_clients[player_name]
            await self._broadcast_state(match_id, {"type": "player_left", "player": player_name})
            if not state.connected_clients:
                # Cleanup after timeout in prod
                del self.games[match_id]

    async def process_throw(self, match_id: str, player: str, darts: List[int]):
        if match_id not in self.games:
            return
        state = self.games[match_id]
        if state.engine is None:
            return
        try:
            msg = state.engine.record_throw(darts)
            state.last_activity = datetime.utcnow()
            await self._broadcast_state(match_id, {
                "type": "throw",
                "player": player,
                "darts": darts,
                "message": msg,
                "scores": {p.name: p.score for p in state.engine.players},
                "winner": state.engine.state.winner,
            })
            # TODO: Update ELO if winner
        except Exception as e:
            await self._broadcast_state(match_id, {"type": "error", "message": str(e)})

    async def process_command(self, match_id: str, player: str, command: str):
        if match_id not in self.games:
            return
        state = self.games[match_id]
        if state.engine is None:
            return
        if command == "undo":
            ok = state.engine.undo_last_throw()
            await self._broadcast_state(match_id, {"type": "undo", "success": ok})
        elif command == "next":
            msg = state.engine.switch_player() if hasattr(state.engine, 'switch_player') else "Turn passed"
            await self._broadcast_state(match_id, {"type": "next_player", "message": msg})

    async def _broadcast_state(self, match_id: str, message: dict):
        if match_id not in self.games:
            return
        state = self.games[match_id]
        data = json.dumps(message)
        # Local broadcast
        for ws in list(state.connected_clients.values()):
            try:
                await ws.send_text(data)
            except:
                pass
        # Redis pub/sub for multi-process
        if self.redis:
            await self.redis.publish(f"game:{match_id}", data)

    async def get_state(self, match_id: str) -> Optional[dict]:
        if match_id not in self.games:
            return None
        state = self.games[match_id]
        if state.engine:
            return {
                "match_id": match_id,
                "mode": state.mode,
                "players": state.players,
                "scores": {p.name: p.score for p in state.engine.players},
                "winner": state.engine.state.winner,
                "history": [asdict(h) for h in state.engine.state.history[-10:]],
            }
        return None

manager = GameSyncManager()

# --- WebSocket Endpoint ---
@app.websocket("/ws/{match_id}/{player_name}")
async def websocket_endpoint(websocket: WebSocket, match_id: str, player_name: str, token: str = None):
    # Simple token check (in prod use Depends in HTTP, pass via query for WS)
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            # validate user
        except:
            await websocket.close(code=1008)
            return
    await websocket.accept()
    try:
        state = await manager.join_game(match_id, player_name, websocket)
        # Send initial state
        initial = await manager.get_state(match_id)
        if initial:
            await websocket.send_text(json.dumps({"type": "initial_state", **initial}))
        while True:
            data = await websocket.receive_text()
            event = json.loads(data)
            await check_rate_limit(User(username=player_name))  # simplistic
            if event.get("type") == "throw":
                await manager.process_throw(match_id, player_name, event.get("darts", []))
            elif event.get("type") == "command":
                await manager.process_command(match_id, player_name, event.get("command", ""))
    except WebSocketDisconnect:
        await manager.leave_game(match_id, player_name)
    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
        await manager.leave_game(match_id, player_name)

# --- REST Endpoints for match creation etc. ---
@app.post("/matches")
async def create_match(match: MatchCreate, user: User = Depends(get_current_user)):
    match_id = f"match_{int(datetime.utcnow().timestamp())}"
    await manager.create_game(match_id, match.mode, match.players, user)
    return {"match_id": match_id, "join_code": match_id[-6:].upper()}

@app.get("/matches/{match_id}")
async def get_match(match_id: str):
    state = await manager.get_state(match_id)
    if not state:
        raise HTTPException(404, "Match not found")
    return state

@app.get("/matches")
async def list_open_matches():
    return [m for m in manager.games.values() if len(m.connected_clients) < 4]  # simplistic

# For local dev
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)