"""
Dart Game Pro v2.2 — Enhanced Database Layer
New tables: ELO ratings, career data, online matches, pattern data,
save/resume, anniversaries, login bonuses, social shares
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = "data/darts_v2.db"


def init_db_v2():
    """Initialize v2 database with all new tables."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # ELO Ratings table
    c.execute('''
        CREATE TABLE IF NOT EXISTS elo_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT UNIQUE NOT NULL,
            rating REAL DEFAULT 1000,
            games_played INTEGER DEFAULT 0,
            games_won INTEGER DEFAULT 0,
            flight TEXT DEFAULT 'C',
            division TEXT DEFAULT 'Beginner',
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Career mode table
    c.execute('''
        CREATE TABLE IF NOT EXISTS career_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT UNIQUE NOT NULL,
            season INTEGER DEFAULT 1,
            world_ranking INTEGER DEFAULT 64,
            total_prize_money INTEGER DEFAULT 0,
            events_won INTEGER DEFAULT 0,
            career_high_avg REAL DEFAULT 0,
            current_division TEXT DEFAULT 'Bronze',
            career_json TEXT,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Saved games (save/resume)
    c.execute('''
        CREATE TABLE IF NOT EXISTS saved_games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            save_name TEXT NOT NULL,
            player_name TEXT NOT NULL,
            game_mode TEXT,
            game_state_json TEXT,
            saved_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Pattern/weakness data
    c.execute('''
        CREATE TABLE IF NOT EXISTS player_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            pattern_type TEXT,
            pattern_data TEXT,
            detected_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Anniversaries
    c.execute('''
        CREATE TABLE IF NOT EXISTS anniversaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            event_type TEXT NOT NULL,
            event_date TEXT NOT NULL,
            years INTEGER DEFAULT 0,
            UNIQUE(player_name, event_type)
        )
    ''')
    
    # Login bonuses
    c.execute('''
        CREATE TABLE IF NOT EXISTS login_bonuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            login_date TEXT NOT NULL,
            streak INTEGER DEFAULT 1,
            bonus_points INTEGER DEFAULT 10,
            UNIQUE(player_name, login_date)
        )
    ''')
    
    # Social shares
    c.execute('''
        CREATE TABLE IF NOT EXISTS social_shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            platform TEXT,
            content TEXT,
            shared_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Equipment tracking
    c.execute('''
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            equipment_name TEXT,
            equipment_type TEXT,
            weight TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Indexes
    c.execute("CREATE INDEX IF NOT EXISTS idx_elo_player ON elo_ratings(player_name)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_career_player ON career_data(player_name)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_saved_player ON saved_games(player_name)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_anniversary_player ON anniversaries(player_name)")
    
    conn.commit()
    conn.close()


# ELO functions
def get_or_create_elo(player_name: str) -> Dict:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM elo_ratings WHERE player_name = ?", (player_name,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO elo_ratings (player_name) VALUES (?)", (player_name,))
        conn.commit()
        c.execute("SELECT * FROM elo_ratings WHERE player_name = ?", (player_name,))
        row = c.fetchone()
    conn.close()
    return dict(row) if row else {}


def update_elo(player_name: str, new_rating: float, won: bool):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE elo_ratings 
        SET rating = ?, games_played = games_played + 1, 
            games_won = games_won + ?,
            last_updated = ?
        WHERE player_name = ?
    """, (new_rating, 1 if won else 0, datetime.now().isoformat(), player_name))
    conn.commit()
    conn.close()


# Career functions
def get_or_create_career(player_name: str) -> Dict:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM career_data WHERE player_name = ?", (player_name,))
    row = c.fetchone()
    if not row:
        c.execute("""
            INSERT INTO career_data (player_name, career_json) 
            VALUES (?, ?)
        """, (player_name, json.dumps({"season": 1, "world_ranking": 64})))
        conn.commit()
        c.execute("SELECT * FROM career_data WHERE player_name = ?", (player_name,))
        row = c.fetchone()
    conn.close()
    return dict(row) if row else {}


def update_career(player_name: str, data: Dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE career_data 
        SET season = ?, world_ranking = ?, total_prize_money = ?,
            events_won = ?, career_high_avg = ?, current_division = ?,
            career_json = ?, last_updated = ?
        WHERE player_name = ?
    """, (
        data.get("season", 1), data.get("world_ranking", 64),
        data.get("total_prize_money", 0), data.get("events_won", 0),
        data.get("career_high_avg", 0), data.get("current_division", "Bronze"),
        json.dumps(data), datetime.now().isoformat(), player_name
    ))
    conn.commit()
    conn.close()


# Save/Resume
def save_game_state(player_name: str, save_name: str, game_mode: str, state_json: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO saved_games (player_name, save_name, game_mode, game_state_json, saved_at)
        VALUES (?, ?, ?, ?, ?)
    """, (player_name, save_name, game_mode, state_json, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def list_saved_games(player_name: str) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM saved_games WHERE player_name = ? ORDER BY saved_at DESC", (player_name,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# Equipment
def add_equipment(player_name: str, name: str, eq_type: str, weight: str, notes: str = ""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO equipment (player_name, equipment_name, equipment_type, weight, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (player_name, name, eq_type, weight, notes))
    conn.commit()
    conn.close()


def get_equipment(player_name: str) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM equipment WHERE player_name = ?", (player_name,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# Login bonuses
def record_login(player_name: str) -> Dict:
    """Record login and calculate streak + bonus."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Check yesterday's login
    yesterday = (datetime.now() - __import__('datetime').timedelta(days=1)).strftime("%Y-%m-%d")
    c.execute("SELECT streak FROM login_bonuses WHERE player_name = ? AND login_date = ?", 
              (player_name, yesterday))
    row = c.fetchone()
    
    if row:
        streak = row[0] + 1
    else:
        streak = 1
    
    bonus = min(50, 10 * streak)
    
    try:
        c.execute("""
            INSERT INTO login_bonuses (player_name, login_date, streak, bonus_points)
            VALUES (?, ?, ?, ?)
        """, (player_name, today, streak, bonus))
        conn.commit()
    except sqlite3.IntegrityError:
        # Already logged in today
        c.execute("SELECT streak, bonus_points FROM login_bonuses WHERE player_name = ? AND login_date = ?",
                  (player_name, today))
        row = c.fetchone()
        if row:
            streak, bonus = row
    
    conn.close()
    return {"streak": streak, "bonus": bonus}


# Anniversaries
def record_anniversary(player_name: str, event_type: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO anniversaries (player_name, event_type, event_date)
            VALUES (?, ?, ?)
        """, (player_name, event_type, datetime.now().isoformat()))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()


def get_anniversaries(player_name: str) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM anniversaries WHERE player_name = ?", (player_name,))
    rows = c.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        event_date = datetime.fromisoformat(d["event_date"])
        years = (datetime.now() - event_date).days / 365.25
        d["years"] = round(years, 1)
        result.append(d)
    return result
