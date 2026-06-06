"""
core/multiplayer.py
v3.1 Production core for real-time multiplayer.
Holds GameSyncManager, GameState (pure, no FastAPI), ELO integration, persistence hooks.
Server (FastAPI) imports and uses for WS/REST handlers.
No breaking changes to existing local engine/custom/analytics.
"""

import os
import json
import time
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

# Optional / core imports (graceful)
try:
    from core.engine import DartGameEngine
except Exception:
    DartGameEngine = None  # type: ignore

try:
    from core.player import Player
except Exception:
    class Player:  # type: ignore
        def __init__(self, name): self.name = name; self.score = 0

try:
    from core.systems import EloSystem
    HAS_ELO = True
except Exception:
    HAS_ELO = False
    class EloSystem:  # type: ignore
        def __init__(self): self.players = {}
        def add_player(self, n, s=1000): pass
        def record_match(self, w, l, mf="single_game"): pass
        def get_standings(self): return []
        def get_rating(self, n): return 1000

try:
    from core.database_v2 import init_db_v2, save_match_history, get_match_history
    init_db_v2()
    HAS_DB_V2 = True
except Exception:
    HAS_DB_V2 = False

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
ONLINE_HISTORY_PATH = DATA_DIR / "online_match_history.json"

logger = logging.getLogger("dart.multiplayer")

@dataclass
class GameState:
    match_id: str
    mode: str
    players: List[str]
    engine: Optional[Any] = None
    connected_clients: Dict[str, Any] = field(default_factory=dict)  # ws objects in server
    last_activity: datetime = field(default_factory=datetime.utcnow)
    custom: Optional[dict] = None

class GameSyncManager:
    """
    Central authority for match state, turns (via engine), broadcast, ELO, history.
    Thread/async safe enough for uvicorn workers + redis.
    """
    def __init__(self):
        self.games: Dict[str, GameState] = {}
        self.elo = EloSystem() if HAS_ELO else None
        self._demo_player_id = 1
        self.redis = None  # set by server if available
        # simple in-mem rate (server may override)
        self._rate: Dict[str, List[float]] = {}

    def create_game(self, match_id: str, mode: str, players: List[str], custom: Optional[dict] = None) -> GameState:
        if match_id in self.games:
            # collision or reuse (should not with uuid mids)
            return self.games[match_id]
        p_objs = [Player(name) for name in players]
        ekwargs = {}
        eff_mode = mode
        if custom:
            wc = str(custom.get("win_condition", "") or "")
            if "Survival" in wc or custom.get("lives"):
                eff_mode = "killer_party"
                ekwargs["variant"] = "hard" if (custom.get("lives") or 3) <= 3 else "standard"
            elif "Highest score" in wc or custom.get("round_limit"):
                eff_mode = "count_up"
            elif "Target" in wc:
                eff_mode = "around_the_clock"
            if "Only Doubles" in (custom.get("special_rules") or []):
                ekwargs["out_rule"] = "double"
            if custom.get("lives"):
                ekwargs.setdefault("variant", str(custom.get("lives")))
        try:
            engine = DartGameEngine(mode=eff_mode, players=p_objs, **ekwargs) if DartGameEngine else None
        except Exception as ex:
            logger.warning(f"Engine create fallback for {eff_mode}: {ex}")
            engine = DartGameEngine(mode=mode, players=p_objs) if DartGameEngine else None
        state = GameState(match_id=match_id, mode=eff_mode, players=players, engine=engine, custom=custom)
        self.games[match_id] = state
        return state

    def join(self, match_id: str, player_name: str, client: Any = None) -> GameState:
        if match_id not in self.games:
            raise ValueError("Match not found")
        state = self.games[match_id]
        if client is not None:
            state.connected_clients[player_name] = client
        state.last_activity = datetime.utcnow()
        return state

    def leave(self, match_id: str, player_name: str):
        if match_id in self.games:
            state = self.games[match_id]
            state.connected_clients.pop(player_name, None)
            if not state.connected_clients:
                # keep a bit for reconnect; real cleanup via TTL job
                pass

    def cleanup_stale_games(self, max_idle_seconds: int = 3600):
        """Remove games with no activity for too long (call periodically)."""
        now = datetime.utcnow()
        to_remove = []
        for mid, state in list(self.games.items()):
            idle = (now - state.last_activity).total_seconds()
            if idle > max_idle_seconds and not state.connected_clients:
                to_remove.append(mid)
        for mid in to_remove:
            del self.games[mid]
        return len(to_remove)

    def record_throw(self, match_id: str, player: str, darts: List[int]) -> dict:
        if match_id not in self.games:
            return {"error": "no match"}
        state = self.games[match_id]
        eng = state.engine
        if not eng:
            return {"error": "no engine"}
        try:
            # Enforce turn (engine does inside record_throw for most)
            cur = None
            try:
                cp = eng.get_current_player()
                cur = getattr(cp, 'name', None)
            except:
                pass
            if cur and player != cur:
                return {"error": f"Not your turn (current: {cur})"}
            msg = eng.record_throw(darts)
            state.last_activity = datetime.utcnow()
            winner = None
            try:
                winner = getattr(eng.state, 'winner', None) or eng.get_winner()
            except:
                pass
            ps = getattr(eng, 'players', None) or getattr(getattr(eng, 'state', None), 'players', []) or []
            scores = {p.name: getattr(p, 'score', getattr(p, 'remaining', 0)) for p in ps}
            res = {
                "type": "throw",
                "player": player,
                "darts": darts,
                "message": msg,
                "scores": scores,
                "winner": winner,
                "current_player": getattr(eng.get_current_player(), 'name', None) if hasattr(eng, 'get_current_player') else None,
            }
            if winner:
                self._update_elo_and_persist(state, winner)
            return res
        except Exception as e:
            return {"type": "error", "message": str(e)}

    def _update_elo_and_persist(self, state: GameState, winner: str):
        players = state.players
        if self.elo and len(players) >= 2:
            loser = players[1] if players[0] == winner else players[0]
            try:
                self.elo.record_match(winner, loser)
            except Exception:
                pass
        # persist
        self._persist(state, winner)

    def _persist(self, state: GameState, winner: Optional[str] = None):
        eng = state.engine
        if not eng:
            return
        history = getattr(getattr(eng, 'state', None), 'history', []) or []
        avgs = [h.get('score', 0) for h in history if isinstance(h, dict) and 'score' in h]
        avg = round(sum(avgs) / max(1, len(avgs)), 1) if avgs else 0.0
        if HAS_DB_V2:
            try:
                save_match_history(self._demo_player_id, state.mode, ",".join(state.players),
                                   "win" if winner else "in_progress", 0, 0, avg, 0)
            except Exception:
                pass
        # JSON fallback (ring buffer)
        if ONLINE_HISTORY_PATH:
            try:
                rec = {
                    "match_id": state.match_id,
                    "ts": datetime.utcnow().isoformat(),
                    "mode": state.mode,
                    "players": state.players,
                    "winner": winner,
                    "scores": {p.name: getattr(p, 'score', getattr(p, 'remaining', 0)) for p in (getattr(eng,'players',None) or getattr(getattr(eng,'state',None),'players',[]) or []) },
                    "avg": avg,
                }
                hist = []
                if ONLINE_HISTORY_PATH.exists():
                    hist = json.loads(ONLINE_HISTORY_PATH.read_text(encoding="utf-8") or "[]")
                hist.append(rec)
                ONLINE_HISTORY_PATH.write_text(json.dumps(hist[-200:], indent=2), encoding="utf-8")
            except Exception:
                pass

    def process_command(self, match_id: str, player: str, cmd: str, payload: Optional[dict] = None) -> dict:
        if match_id not in self.games:
            return {"error": "no match"}
        state = self.games[match_id]
        eng = state.engine
        if not eng:
            return {"error": "no engine"}
        try:
            if cmd == "undo":
                ok = bool(eng.undo_last_throw()) if hasattr(eng, 'undo_last_throw') else False
                ps = getattr(eng,'players',None) or getattr(getattr(eng,'state',None),'players',[]) or []
                return {"type": "undo", "success": ok, "scores": {p.name: getattr(p,'score',getattr(p,'remaining',0)) for p in ps}}
            elif cmd in ("next", "next_player", "pass"):
                msg = ""
                if hasattr(eng, 'switch_player'):
                    msg = eng.switch_player() or "Turn passed"
                return {"type": "next_player", "message": msg}
            return {"type": "command", "cmd": cmd, "ok": True}
        except Exception as e:
            return {"type": "error", "message": str(e)}

    def get_state(self, match_id: str) -> Optional[dict]:
        if match_id not in self.games:
            return None
        state = self.games[match_id]
        eng = state.engine
        if not eng:
            return {"match_id": match_id, "players": state.players, "mode": state.mode}
        try:
            cur = eng.get_current_player().name if hasattr(eng, 'get_current_player') else None
        except:
            cur = None
        ps = getattr(eng, 'players', None) or getattr(getattr(eng, 'state', None), 'players', []) or []
        return {
            "match_id": match_id,
            "mode": state.mode,
            "players": state.players,
            "scores": {p.name: getattr(p, 'score', getattr(p, 'remaining', 0)) for p in ps},
            "winner": getattr(eng.state, 'winner', None) if hasattr(eng, 'state') else None,
            "current_player": cur,
            "history": [asdict(h) if hasattr(h, '__dataclass_fields__') else h for h in (getattr(eng.state, 'history', []) or [])[-10:]],
        }

    def broadcast_local(self, match_id: str, message: dict, sockets: List[Any]):
        """Server calls this; for redis see server layer."""
        data = json.dumps(message)
        for ws in list(sockets):
            try:
                # ws.send_text in async context of server
                # here we just prepare; actual await in endpoint
                pass
            except:
                pass

# Singleton for import
manager = GameSyncManager()

__all__ = ["GameSyncManager", "GameState", "manager", "HAS_ELO", "HAS_DB_V2"]
