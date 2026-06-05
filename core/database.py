"""
Database layer for player profiles, game history, and personal bests.
Refactored: Context managers, UPSERT, shared DB_PATH, input sanitization.
"""

import sqlite3
import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path


# Shared database path (absolute, based on this file's location)
BASE_DIR = Path(__file__).parent.parent
DB_PATH = str(BASE_DIR / "data" / "darts_v2.db")

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def _sanitize_name(name: str) -> str:
    """Sanitize player name to prevent injection issues."""
    return name.strip()[:50]  # Limit length, strip whitespace


def init_db():
    """Initialize the database with all tables."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                picture TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mode TEXT NOT NULL,
                players_json TEXT NOT NULL,
                history_json TEXT NOT NULL,
                winner TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS personal_bests (
                player_name TEXT PRIMARY KEY,
                highest_avg REAL DEFAULT 0,
                best_checkout INTEGER DEFAULT 0,
                most_180s INTEGER DEFAULT 0,
                highest_throw INTEGER DEFAULT 0,
                total_games INTEGER DEFAULT 0,
                total_wins INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS player_stats (
                player_name TEXT PRIMARY KEY,
                stats_json TEXT NOT NULL DEFAULT '{}',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY
            )
        """)
        # Set schema version
        conn.execute("INSERT OR IGNORE INTO schema_version (version) VALUES (1)")
        conn.commit()


def get_db_version() -> int:
    """Get current database schema version."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT version FROM schema_version LIMIT 1")
        row = cursor.fetchone()
        return row[0] if row else 0


def migrate_db():
    """Run database migrations."""
    current_version = get_db_version()

    with sqlite3.connect(DB_PATH) as conn:
        if current_version < 1:
            # Initial schema already created in init_db
            conn.execute("INSERT OR REPLACE INTO schema_version (version) VALUES (1)")

        # Future migrations go here
        # if current_version < 2:
        #     conn.execute("ALTER TABLE ...")
        #     conn.execute("UPDATE schema_version SET version = 2")

        conn.commit()


def save_player(name: str, picture: str = None) -> bool:
    """Save or update a player profile."""
    name = _sanitize_name(name)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO players (name, picture) VALUES (?, ?)
            ON CONFLICT(name) DO UPDATE SET picture=excluded.picture
        """, (name, picture))
        conn.commit()
    return True


def get_player(name: str) -> Optional[Dict]:
    """Get a player by name."""
    name = _sanitize_name(name)
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM players WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_all_players() -> List[Dict]:
    """Get all players."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM players ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]


def save_game(mode: str, players: List[Dict], history: List[Dict], winner: str = None) -> int:
    """Save a completed game."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            INSERT INTO games (mode, players_json, history_json, winner)
            VALUES (?, ?, ?, ?)
        """, (
            mode,
            json.dumps(players, default=str),
            json.dumps(history, default=str),
            winner,
        ))
        conn.commit()
        return cursor.lastrowid


def get_games(limit: int = 50, offset: int = 0) -> List[Dict]:
    """Get recent games."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT * FROM games ORDER BY created_at DESC LIMIT ? OFFSET ?
        """, (limit, offset))
        return [dict(row) for row in cursor.fetchall()]


def get_player_games(player_name: str, limit: int = 50) -> List[Dict]:
    """Get games for a specific player."""
    player_name = _sanitize_name(player_name)
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT * FROM games 
            WHERE players_json LIKE ? 
            ORDER BY created_at DESC LIMIT ?
        """, (f'%"name": "{player_name}"%', limit))
        return [dict(row) for row in cursor.fetchall()]


def update_personal_best(player_name: str, stats: Dict) -> bool:
    """
    Update personal bests using UPSERT (atomic operation).
    FIXED: No more read-then-write race condition.
    """
    player_name = _sanitize_name(player_name)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO personal_bests (player_name, highest_avg, best_checkout, most_180s, highest_throw, total_games, total_wins)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(player_name) DO UPDATE SET
                highest_avg = MAX(highest_avg, excluded.highest_avg),
                best_checkout = MAX(best_checkout, excluded.best_checkout),
                most_180s = MAX(most_180s, excluded.most_180s),
                highest_throw = MAX(highest_throw, excluded.highest_throw),
                total_games = total_games + excluded.total_games,
                total_wins = total_wins + excluded.total_wins,
                updated_at = CURRENT_TIMESTAMP
        """, (
            player_name,
            stats.get("highest_avg", 0),
            stats.get("best_checkout", 0),
            stats.get("most_180s", 0),
            stats.get("highest_throw", 0),
            stats.get("total_games", 1),
            stats.get("total_wins", 0),
        ))
        conn.commit()
    return True


def get_personal_best(player_name: str) -> Optional[Dict]:
    """Get personal bests for a player."""
    player_name = _sanitize_name(player_name)
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM personal_bests WHERE player_name = ?", (player_name,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def save_player_stats(player_name: str, stats: Dict) -> bool:
    """Save player statistics."""
    player_name = _sanitize_name(player_name)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO player_stats (player_name, stats_json)
            VALUES (?, ?)
            ON CONFLICT(player_name) DO UPDATE SET
                stats_json = excluded.stats_json,
                updated_at = CURRENT_TIMESTAMP
        """, (player_name, json.dumps(stats, default=str)))
        conn.commit()
    return True


def get_player_stats(player_name: str) -> Optional[Dict]:
    """Get player statistics."""
    player_name = _sanitize_name(player_name)
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM player_stats WHERE player_name = ?", (player_name,))
        row = cursor.fetchone()
        if row:
            data = dict(row)
            data["stats"] = json.loads(data["stats_json"])
            return data
        return None


def delete_player(name: str) -> bool:
    """Delete a player and all associated data."""
    name = _sanitize_name(name)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM players WHERE name = ?", (name,))
        conn.execute("DELETE FROM personal_bests WHERE player_name = ?", (name,))
        conn.execute("DELETE FROM player_stats WHERE player_name = ?", (name,))
        conn.commit()
    return True


def get_leaderboard(metric: str = "highest_avg", limit: int = 10) -> List[Dict]:
    """Get leaderboard for a specific metric."""
    valid_metrics = ["highest_avg", "best_checkout", "most_180s", "highest_throw", "total_games", "total_wins"]
    if metric not in valid_metrics:
        metric = "highest_avg"

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(f"""
            SELECT player_name, {metric}, total_games, total_wins
            FROM personal_bests
            ORDER BY {metric} DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
