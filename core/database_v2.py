"""
Advanced Database v2: Player profiles, equipment, match history, analytics, login streaks.
Refactored: Context managers, foreign keys, schema migrations, clean imports, persistent challenges.
"""

import sqlite3
import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path


# Shared database path
BASE_DIR = Path(__file__).parent.parent
DB_PATH = str(BASE_DIR / "data" / "darts_v2.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def _sanitize_name(name: str) -> str:
    """Sanitize player name."""
    return name.strip()[:50]


def init_db_v2():
    """Initialize v2 database tables with foreign keys and schema versioning."""
    with sqlite3.connect(DB_PATH) as conn:
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")

        # Players table (base table)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS players_v2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                email TEXT,
                picture TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)

        # Equipment table (FK to players_v2)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT,
                weight REAL,
                purchase_date TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players_v2(id) ON DELETE CASCADE
            )
        """)

        # Match history
        conn.execute("""
            CREATE TABLE IF NOT EXISTS match_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                mode TEXT NOT NULL,
                opponent TEXT,
                result TEXT,
                player_score INTEGER,
                opponent_score INTEGER,
                avg REAL,
                checkout INTEGER,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players_v2(id) ON DELETE CASCADE
            )
        """)

        # Login streaks
        conn.execute("""
            CREATE TABLE IF NOT EXISTS login_streaks (
                player_id INTEGER PRIMARY KEY,
                current_streak INTEGER DEFAULT 0,
                best_streak INTEGER DEFAULT 0,
                last_login_date DATE,
                total_logins INTEGER DEFAULT 0,
                FOREIGN KEY (player_id) REFERENCES players_v2(id) ON DELETE CASCADE
            )
        """)

        # Challenges (persistent)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                challenge_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                challenge_type TEXT,
                target INTEGER DEFAULT 1,
                progress INTEGER DEFAULT 0,
                reward TEXT,
                expires_at TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players_v2(id) ON DELETE CASCADE
            )
        """)

        # Analytics
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players_v2(id) ON DELETE CASCADE
            )
        """)

        # Schema version
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version_v2 (
                version INTEGER PRIMARY KEY
            )
        """)
        conn.execute("INSERT OR IGNORE INTO schema_version_v2 (version) VALUES (1)")
        conn.commit()


def get_db_version_v2() -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT version FROM schema_version_v2 LIMIT 1")
        row = cursor.fetchone()
        return row[0] if row else 0


def migrate_db_v2():
    """Run v2 database migrations."""
    current_version = get_db_version_v2()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        if current_version < 1:
            conn.execute("INSERT OR REPLACE INTO schema_version_v2 (version) VALUES (1)")

        # Future migrations
        # if current_version < 2:
        #     conn.execute("ALTER TABLE ...")
        #     conn.execute("UPDATE schema_version_v2 SET version = 2")

        conn.commit()


def save_player_v2(name: str, email: str = None, picture: str = None) -> int:
    """Save or update a player v2 profile. Returns player ID."""
    name = _sanitize_name(name)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.execute("""
            INSERT INTO players_v2 (name, email, picture)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                email = COALESCE(excluded.email, email),
                picture = COALESCE(excluded.picture, picture)
        """, (name, email, picture))
        conn.commit()

        # Get the player ID
        cursor = conn.execute("SELECT id FROM players_v2 WHERE name = ?", (name,))
        row = cursor.fetchone()
        return row[0] if row else 0


def get_player_v2(name: str) -> Optional[Dict]:
    name = _sanitize_name(name)
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM players_v2 WHERE name = ?", (name,))
        row = cursor.fetchone()
        return dict(row) if row else None


def save_equipment(player_id: int, name: str, equipment_type: str = None, weight: float = None) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("""
            INSERT INTO equipment (player_id, name, type, weight, purchase_date)
            VALUES (?, ?, ?, ?, ?)
        """, (player_id, name, equipment_type, weight, datetime.now().isoformat()))
        conn.commit()
    return True


def get_equipment(player_id: int) -> List[Dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM equipment WHERE player_id = ?", (player_id,))
        return [dict(row) for row in cursor.fetchall()]


def save_match_history(player_id: int, mode: str, opponent: str, result: str,
                       player_score: int, opponent_score: int, avg: float, checkout: int) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("""
            INSERT INTO match_history (player_id, mode, opponent, result, player_score, opponent_score, avg, checkout)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (player_id, mode, opponent, result, player_score, opponent_score, avg, checkout))
        conn.commit()
    return True


def get_match_history(player_id: int, limit: int = 50) -> List[Dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT * FROM match_history WHERE player_id = ? ORDER BY date DESC LIMIT ?
        """, (player_id, limit))
        return [dict(row) for row in cursor.fetchall()]


def record_login(player_id: int) -> Dict:
    """
    Record a login and update streak.
    FIXED: Uses timedelta from module level, not __import__.
    """
    today = datetime.now().date()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row

        # Get current streak data
        cursor = conn.execute("SELECT * FROM login_streaks WHERE player_id = ?", (player_id,))
        row = cursor.fetchone()

        if row:
            last_login = datetime.strptime(row["last_login_date"], "%Y-%m-%d").date() if row["last_login_date"] else None
            current_streak = row["current_streak"] or 0
            best_streak = row["best_streak"] or 0
            total_logins = row["total_logins"] or 0

            if last_login:
                days_diff = (today - last_login).days
                if days_diff == 1:
                    # Consecutive day
                    current_streak += 1
                    best_streak = max(best_streak, current_streak)
                elif days_diff == 0:
                    # Same day, don't increment
                    pass
                else:
                    # Streak broken
                    current_streak = 1
            else:
                current_streak = 1

            total_logins += 1

            conn.execute("""
                UPDATE login_streaks
                SET current_streak = ?, best_streak = ?, last_login_date = ?, total_logins = ?
                WHERE player_id = ?
            """, (current_streak, best_streak, today.isoformat(), total_logins, player_id))
        else:
            # First login
            conn.execute("""
                INSERT INTO login_streaks (player_id, current_streak, best_streak, last_login_date, total_logins)
                VALUES (?, 1, 1, ?, 1)
            """, (player_id, today.isoformat()))
            current_streak = 1
            best_streak = 1
            total_logins = 1

        conn.commit()

        return {
            "current_streak": current_streak,
            "best_streak": best_streak,
            "total_logins": total_logins,
            "bonus": min(50, 10 * current_streak),
        }


def get_login_streak(player_id: int) -> Optional[Dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM login_streaks WHERE player_id = ?", (player_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def save_challenge(player_id: int, challenge: Dict) -> bool:
    """Save a challenge to the database."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("""
            INSERT INTO challenges (player_id, challenge_id, name, description, challenge_type, target, progress, reward, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT DO NOTHING
        """, (
            player_id,
            challenge["id"],
            challenge["name"],
            challenge.get("description", ""),
            challenge.get("type", "daily"),
            challenge.get("target", 1),
            challenge.get("progress", 0),
            challenge.get("reward", ""),
            challenge.get("expires"),
        ))
        conn.commit()
    return True


def update_challenge_progress(player_id: int, challenge_id: str, progress: int) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("""
            UPDATE challenges
            SET progress = ?, completed_at = CASE WHEN progress >= target THEN CURRENT_TIMESTAMP ELSE completed_at END
            WHERE player_id = ? AND challenge_id = ?
        """, (progress, player_id, challenge_id))
        conn.commit()
    return True


def get_challenges(player_id: int, active_only: bool = True) -> List[Dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        if active_only:
            cursor = conn.execute("""
                SELECT * FROM challenges
                WHERE player_id = ? AND completed_at IS NULL
                ORDER BY expires_at
            """, (player_id,))
        else:
            cursor = conn.execute("""
                SELECT * FROM challenges WHERE player_id = ? ORDER BY created_at DESC
            """, (player_id,))
        return [dict(row) for row in cursor.fetchall()]


def save_analytics(player_id: int, metric_name: str, metric_value: float) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("""
            INSERT INTO analytics (player_id, metric_name, metric_value)
            VALUES (?, ?, ?)
        """, (player_id, metric_name, metric_value))
        conn.commit()
    return True


def get_analytics(player_id: int, metric_name: str = None, limit: int = 100) -> List[Dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        if metric_name:
            cursor = conn.execute("""
                SELECT * FROM analytics
                WHERE player_id = ? AND metric_name = ?
                ORDER BY recorded_at DESC LIMIT ?
            """, (player_id, metric_name, limit))
        else:
            cursor = conn.execute("""
                SELECT * FROM analytics
                WHERE player_id = ?
                ORDER BY recorded_at DESC LIMIT ?
            """, (player_id, limit))
        return [dict(row) for row in cursor.fetchall()]
