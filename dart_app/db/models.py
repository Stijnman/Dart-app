"""
dart_app/db/models.py
SQLAlchemy schema for local sqlite stats telemetry.
Designed for tracking historical averages, checkout success, per-player/per-mode stats.
Can be used alongside (or to augment) the raw sqlite in core/database*.py.

Example:
    from dart_app.db.models import init_db, log_match, get_player_average, get_checkout_stats
    init_db()
    log_match(player_name="Alice", mode="501", score=301, checkout_success=True, avg=72.4)
    print(get_player_average("Alice"))
"""

from __future__ import annotations
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, func, Index
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from sqlalchemy.sql import text
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

BASE_DIR = Path(__file__).parent.parent.parent  # dart_app/db -> project root
DB_PATH = str(BASE_DIR / "data" / "dart_telemetry.db")
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    matches = relationship("Match", back_populates="player")

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    mode = Column(String(50), nullable=False, index=True)
    opponent = Column(String(80), default="")
    result = Column(String(20))  # win/loss/draw
    player_score = Column(Integer)
    opponent_score = Column(Integer)
    three_dart_avg = Column(Float)
    checkout_success = Column(Boolean, default=False)
    checkout_remaining = Column(Integer)
    played_at = Column(DateTime, default=datetime.utcnow, index=True)

    player = relationship("Player", back_populates="matches")

    __table_args__ = (Index("ix_match_player_mode", "player_id", "mode"),)

class Throw(Base):
    __tablename__ = "throws"
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    dart1 = Column(Integer)
    dart2 = Column(Integer)
    dart3 = Column(Integer)
    total = Column(Integer)
    is_checkout_attempt = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Create tables (idempotent for sqlite). Call once at startup."""
    Base.metadata.create_all(bind=engine)

def get_session() -> Session:
    return SessionLocal()

def get_or_create_player(session: Session, name: str) -> Player:
    p = session.query(Player).filter(Player.name == name).first()
    if not p:
        p = Player(name=name)
        session.add(p)
        session.commit()
        session.refresh(p)
    return p

def log_match(
    player_name: str,
    mode: str,
    opponent: str = "",
    result: str = "win",
    player_score: int = 0,
    opponent_score: int = 0,
    three_dart_avg: float = 0.0,
    checkout_success: bool = False,
    checkout_remaining: Optional[int] = None,
) -> int:
    """Log a completed match + stats. Returns match id."""
    with get_session() as session:
        player = get_or_create_player(session, player_name)
        m = Match(
            player_id=player.id,
            mode=mode,
            opponent=opponent,
            result=result,
            player_score=player_score,
            opponent_score=opponent_score,
            three_dart_avg=three_dart_avg,
            checkout_success=checkout_success,
            checkout_remaining=checkout_remaining,
        )
        session.add(m)
        session.commit()
        return m.id

def get_player_average(player_name: str, mode: Optional[str] = None) -> Optional[float]:
    with get_session() as session:
        q = session.query(func.avg(Match.three_dart_avg)).join(Player).filter(Player.name == player_name)
        if mode:
            q = q.filter(Match.mode == mode)
        return q.scalar()

def get_checkout_stats(player_name: str) -> Dict[str, Any]:
    with get_session() as session:
        player = session.query(Player).filter(Player.name == player_name).first()
        if not player:
            return {"attempts": 0, "successes": 0, "rate": 0.0}
        attempts = session.query(Match).filter(
            Match.player_id == player.id, Match.checkout_remaining.isnot(None)
        ).count()
        successes = session.query(Match).filter(
            Match.player_id == player.id, Match.checkout_success == True
        ).count()
        rate = (successes / attempts * 100.0) if attempts > 0 else 0.0
        return {"attempts": attempts, "successes": successes, "rate": round(rate, 1)}

def get_historical_averages(player_name: str, limit: int = 20) -> List[Dict[str, Any]]:
    with get_session() as session:
        player = session.query(Player).filter(Player.name == player_name).first()
        if not player:
            return []
        rows = (
            session.query(Match.mode, func.avg(Match.three_dart_avg).label("avg"), func.count().label("n"))
            .filter(Match.player_id == player.id)
            .group_by(Match.mode)
            .order_by(func.avg(Match.three_dart_avg).desc())
            .limit(limit)
            .all()
        )
        return [{"mode": r.mode, "avg": round(r.avg, 2) if r.avg else 0, "games": r.n} for r in rows]

# One-time init helper
if __name__ == "__main__":
    init_db()
    print("Telemetry DB initialized at", DB_PATH)
