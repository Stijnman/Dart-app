"""
Enhanced SQLite database layer with player profiles, game history, and stats aggregation.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = "data/darts_v2.db"


def init_db():
    """Initialize the database with all tables and views."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Players table
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            picture TEXT,
            wins INTEGER DEFAULT 0,
            legs_won INTEGER DEFAULT 0,
            sets_won INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Games table (match-level)
    c.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mode TEXT NOT NULL,
            variant TEXT DEFAULT 'standard',
            winner TEXT,
            match_format TEXT DEFAULT 'single_game',
            in_rule TEXT DEFAULT 'straight',
            out_rule TEXT DEFAULT 'double',
            starting_score INTEGER DEFAULT 501,
            legs_played INTEGER DEFAULT 1,
            players_json TEXT,
            history_json TEXT,
            stats_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Player stats table (per-game stats for aggregation)
    c.execute('''
        CREATE TABLE IF NOT EXISTS player_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            game_id INTEGER,
            mode TEXT,
            won INTEGER DEFAULT 0,
            three_dart_avg REAL DEFAULT 0,
            first_nine_avg REAL DEFAULT 0,
            checkout_pct REAL DEFAULT 0,
            highest_checkout INTEGER DEFAULT 0,
            ton_eighties INTEGER DEFAULT 0,
            ton_forties INTEGER DEFAULT 0,
            hundreds INTEGER DEFAULT 0,
            total_throws INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0,
            darts_thrown INTEGER DEFAULT 0,
            best_throw INTEGER DEFAULT 0,
            legs_played INTEGER DEFAULT 0,
            legs_won INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(id)
        )
    ''')
    
    # Personal bests table
    c.execute('''
        CREATE TABLE IF NOT EXISTS personal_bests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            category TEXT NOT NULL,
            value REAL NOT NULL,
            details TEXT,
            achieved_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_name, category)
        )
    ''')
    
    # Head-to-head records
    c.execute('''
        CREATE TABLE IF NOT EXISTS h2h_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_a TEXT NOT NULL,
            player_b TEXT NOT NULL,
            player_a_wins INTEGER DEFAULT 0,
            player_b_wins INTEGER DEFAULT 0,
            last_played TEXT,
            UNIQUE(player_a, player_b)
        )
    ''')
    
    # Create indexes
    c.execute("CREATE INDEX IF NOT EXISTS idx_stats_player ON player_stats(player_name)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_stats_game ON player_stats(game_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_games_winner ON games(winner)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_games_mode ON games(mode)")
    
    conn.commit()
    conn.close()


def save_player(name: str, picture: Optional[str] = None) -> bool:
    """Save or update a player. Returns True if new player."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM players WHERE name = ?", (name,))
    existing = c.fetchone()
    
    if existing:
        if picture:
            c.execute("UPDATE players SET picture = ? WHERE name = ?", (picture, name))
        conn.commit()
        conn.close()
        return False
    
    c.execute(
        "INSERT INTO players (name, picture, created_at) VALUES (?, ?, ?)",
        (name, picture, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return True


def get_all_players() -> List[Dict]:
    """Get all registered players."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT name, picture, wins, legs_won, created_at FROM players ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_player(name: str) -> Optional[Dict]:
    """Get a specific player."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE name = ?", (name,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def save_game(
    mode: str,
    winner: str,
    players: List[Dict],
    history: List[Dict],
    stats: Optional[Dict] = None,
    variant: str = "standard",
    match_format: str = "single_game",
    in_rule: str = "straight",
    out_rule: str = "double",
    starting_score: int = 501,
    legs_played: int = 1,
) -> int:
    """Save a completed game. Returns game ID."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO games (mode, variant, winner, match_format, in_rule, out_rule,
                          starting_score, legs_played, players_json, history_json, stats_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        mode, variant, winner, match_format, in_rule, out_rule,
        starting_score, legs_played,
        json.dumps(players), json.dumps(history),
        json.dumps(stats) if stats else None,
        datetime.now().isoformat()
    ))
    game_id = c.lastrowid
    conn.commit()
    conn.close()
    return game_id


def save_player_stats(player_name: str, game_id: int, mode: str, stats: Dict):
    """Save detailed player stats for a game."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO player_stats
        (player_name, game_id, mode, won, three_dart_avg, first_nine_avg,
         checkout_pct, highest_checkout, ton_eighties, ton_forties, hundreds,
         total_throws, total_score, darts_thrown, best_throw, legs_played, legs_won, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        player_name, game_id, mode,
        stats.get('won', 0),
        stats.get('three_dart_avg', 0),
        stats.get('first_nine_avg', 0),
        stats.get('checkout_pct', 0),
        stats.get('highest_checkout', 0),
        stats.get('ton_eighties', 0),
        stats.get('ton_forties', 0),
        stats.get('hundreds', 0),
        stats.get('total_throws', 0),
        stats.get('total_score', 0),
        stats.get('darts_thrown', 0),
        stats.get('best_throw', 0),
        stats.get('legs_played', 1),
        stats.get('legs_won', 0),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()


def update_personal_best(player_name: str, category: str, value: float, details: str = ""):
    """Update a personal best if the new value exceeds the old."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT value FROM personal_bests WHERE player_name = ? AND category = ?",
              (player_name, category))
    row = c.fetchone()
    
    is_higher_better = category not in ['best_leg_darts', 'worst_leg_darts']
    
    if row is None:
        c.execute('''
            INSERT INTO personal_bests (player_name, category, value, details, achieved_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (player_name, category, value, details, datetime.now().isoformat()))
    elif (is_higher_better and value > row[0]) or (not is_higher_better and value < row[0]):
        c.execute('''
            UPDATE personal_bests SET value = ?, details = ?, achieved_at = ?
            WHERE player_name = ? AND category = ?
        ''', (value, details, datetime.now().isoformat(), player_name, category))
    
    conn.commit()
    conn.close()


def get_personal_bests(player_name: str) -> Dict[str, dict]:
    """Get all personal bests for a player."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT category, value, details, achieved_at 
        FROM personal_bests WHERE player_name = ?
    ''', (player_name,))
    rows = c.fetchall()
    conn.close()
    return {r['category']: dict(r) for r in rows}


def get_recent_games(limit: int = 10) -> List[Dict]:
    """Get recent games."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT id, mode, variant, winner, match_format, starting_score, created_at
        FROM games ORDER BY id DESC LIMIT ?
    ''', (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_player_stats(player_name: str) -> Dict:
    """Get aggregated stats for a player."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT 
            COUNT(*) as games_played,
            SUM(won) as games_won,
            AVG(three_dart_avg) as avg_three_dart,
            AVG(first_nine_avg) as avg_first_nine,
            MAX(best_throw) as best_throw,
            SUM(ton_eighties) as total_180s,
            SUM(ton_forties) as total_140s,
            SUM(hundreds) as total_100s,
            SUM(total_throws) as total_throws,
            SUM(total_score) as total_score,
            SUM(darts_thrown) as total_darts
        FROM player_stats WHERE player_name = ?
    ''', (player_name,))
    row = c.fetchone()
    conn.close()
    
    if row:
        stats = dict(row)
        if stats['total_throws']:
            stats['overall_avg'] = round(stats['total_score'] / stats['total_throws'], 2)
        else:
            stats['overall_avg'] = 0
        return stats
    return {}


def get_leaderboard() -> List[Dict]:
    """Get global leaderboard by wins."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT 
            p.name,
            p.wins,
            COUNT(ps.id) as games_played,
            COALESCE(AVG(ps.three_dart_avg), 0) as avg_score
        FROM players p
        LEFT JOIN player_stats ps ON p.name = ps.player_name
        GROUP BY p.name
        ORDER BY p.wins DESC, avg_score DESC
        LIMIT 50
    ''')
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_h2h_record(player_a: str, player_b: str) -> Dict:
    """Get head-to-head record between two players."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT * FROM h2h_records 
        WHERE (player_a = ? AND player_b = ?) OR (player_a = ? AND player_b = ?)
    ''', (player_a, player_b, player_b, player_a))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else {"player_a": player_a, "player_b": player_b, "player_a_wins": 0, "player_b_wins": 0}
