"""
core/server/models.py
Shared Pydantic models, auth helpers, config for the v3.1 multiplayer server.
Imported by main.py (FastAPI app) and handlers.py (no cycles).
"""

import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

# Config (override via env in prod)
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-prod-please")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
RATE_LIMIT_PER_MIN = 60

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Demo users (plain for robustness across envs; prod: real DB + hashed)
DEMO_USERS: Dict[str, str] = {"demo": "demo123", "player1": "pass", "player2": "pass"}

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str

class MatchCreate(BaseModel):
    mode: str = "501"
    players: List[str]
    out_rule: str = "double"
    custom: Optional[dict] = None

class ThrowEvent(BaseModel):
    match_id: str
    player: str
    darts: List[int]

class CommandEvent(BaseModel):
    match_id: str
    player: str
    command: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return User(username=username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_demo_login(username: str, password: str) -> bool:
    return username in DEMO_USERS and DEMO_USERS[username] == password

__all__ = [
    "SECRET_KEY", "ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES", "RATE_LIMIT_PER_MIN",
    "Token", "User", "MatchCreate", "ThrowEvent", "CommandEvent",
    "create_access_token", "get_current_user", "verify_demo_login", "DEMO_USERS",
]
