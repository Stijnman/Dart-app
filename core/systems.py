"""
Dart Game Pro - Systems Module
Contains AI, Career, Analytics, Online, and supporting systems.
"""

import random
import hashlib
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict


# ===== VOICE RECOGNITION =====
class VoiceRecognition:
    SCORE_PHRASES = {
        "sixty": 60, "t20": 60, "triple 20": 60,
        "fifty seven": 57, "t19": 57,
        "bull": 50, "bullseye": 50,
        "twenty": 20, "single 20": 20,
        "zero": 0, "miss": 0,
        "one hundred and eighty": 180, "180": 180,
    }

    @classmethod
    def parse_score(cls, text: str) -> Optional[int]:
        text = text.lower().strip()
        if text in cls.SCORE_PHRASES:
            return cls.SCORE_PHRASES[text]
        try:
            return int(text)
        except ValueError:
            return None


# ===== SMARTBOT =====
class SmartBot:
    def __init__(self, base_level: int = 5):
        self.base_level = base_level
        self.player_history = []

    def analyze_player(self, recent_throws: List[List[int]]):
        if not recent_throws:
            return
        totals = [sum(t) for t in recent_throws[-10:]]
        avg = sum(totals) / len(totals)
        if avg < 30: self.base_level = 3
        elif avg < 45: self.base_level = 4
        elif avg < 60: self.base_level = 5
        elif avg < 75: self.base_level = 7
        else: self.base_level = 9

    def get_adjusted_level(self) -> int:
        return max(1, min(12, self.base_level))

    def get_description(self) -> str:
        level = self.get_adjusted_level()
        return {1: "Beginner", 3: "Social Player", 5: "Club Player", 7: "County Player", 9: "Pro Tour", 12: "World Class"}.get(level, "Adaptive Bot")


# ===== PRO SIMULATION =====
PRO_PLAYERS = {
    "mvg": {"name": "Michael van Gerwen", "avg": 102.5, "description": "3x World Champion"},
    "littler": {"name": "Luke Littler", "avg": 105.0, "description": "Young phenom"},
    "humphries": {"name": "Luke Humphries", "avg": 98.0, "description": "World Champion"},
}

class ProSimulation:
    def __init__(self, pro_id: str, handicap: int = 0):
        self.pro = PRO_PLAYERS.get(pro_id, PRO_PLAYERS["mvg"])
        self.handicap = handicap

    def get_pro_throw(self) -> List[int]:
        avg = self.pro["avg"]
        darts = []
        for _ in range(3):
            base = int(avg / 3)
            variation = random.randint(-8, 8)
            darts.append(max(0, min(60, base + variation)))
        return darts

    def get_match_intro(self) -> str:
        return f"🎯 Facing {self.pro['name']}! {self.pro.get('description', '')}"


# ===== CAREER MODE =====
class CareerMode:
    def __init__(self, player_name: str):
        self.player_name = player_name
        self.world_ranking = 64
        self.total_prize_money = 0
        self.events_won = 0

    def get_status(self):
        return {
            "player": self.player_name,
            "world_ranking": self.world_ranking,
            "total_prize_money": self.total_prize_money,
            "events_won": self.events_won,
        }


# ===== ELO SYSTEM =====
class EloSystem:
    def __init__(self):
        self.k_factor = 32

    def update_ratings(self, rating_a: int, rating_b: int, result_a: float):
        expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
        new_a = int(rating_a + self.k_factor * (result_a - expected_a))
        new_b = int(rating_b + self.k_factor * ((1 - result_a) - expected_a))
        return new_a, new_b

    def get_flight(self, rating: int) -> str:
        if rating >= 2400: return "SA"
        elif rating >= 2000: return "A"
        elif rating >= 1600: return "B"
        else: return "C"


# ===== SKILL LEVEL SYSTEM =====
class SkillLevelSystem:
    def calculate_level(self, throws):
        if not throws or len(throws) < 3:
            return {"level": "Beginner", "accuracy": 0, "tier": 1}
        totals = [sum(t) for t in throws]
        avg = sum(totals) / len(totals)
        accuracy = min(100, max(0, (avg - 20) * 2))
        if accuracy < 30: level, tier = "Beginner", 1
        elif accuracy < 50: level, tier = "Intermediate", 3
        elif accuracy < 70: level, tier = "Advanced", 5
        else: level, tier = "Expert", 7
        return {"level": level, "accuracy": round(accuracy, 1), "tier": tier}


# ===== PATTERN DETECTOR =====
class PatternDetector:
    @staticmethod
    def detect_patterns(throws):
        if len(throws) < 5:
            return [{"type": "info", "message": "Not enough data yet."}]
        return [{"type": "good", "message": "Looking solid!"}]

    @staticmethod
    def weakness_analysis(throws):
        return []


# ===== COMMENTARY ENGINE =====
class CommentaryEngine:
    def get_commentary(self, event: str, player_name: str = "Player", **kwargs):
        if event == "180":
            return f"🎯 ONE HUNDRED AND EIGHTY! {player_name} with a maximum!"
        elif event == "checkout":
            return f"🎯 Game shot! {player_name} takes the leg!"
        return f"{player_name} plays well."


# ===== AI MATCH REPORTER =====
class AIMatchReporter:
    @staticmethod
    def generate_report(match_data):
        return "AI Match Report: Good performance overall."


# ===== ONLINE MATCH + LOBBY =====
class OnlineMatch:
    def __init__(self, match_id: str, host: str, mode: str = "501", max_players: int = 2):
        self.match_id = match_id
        self.host = host
        self.mode = mode
        self.max_players = max_players
        self.players = [host]
        self.status = "waiting"
        self.chat_history = []
        self.spectators = []
        self.created_at = datetime.now().isoformat()

    def join(self, player_name: str) -> bool:
        if len(self.players) < self.max_players and self.status == "waiting":
            self.players.append(player_name)
            return True
        return False

    def send_chat(self, from_player: str, message: str):
        self.chat_history.append({"from": from_player, "msg": message, "time": datetime.now().isoformat()})

    def get_chat_history(self):
        return self.chat_history[-30:]

    def clear_chat(self):
        self.chat_history = []


class LobbySystem:
    def __init__(self):
        self.lobbies: Dict[str, OnlineMatch] = {}
        self.join_codes: Dict[str, str] = {}

    def create_lobby(self, host: str, mode: str = "501") -> str:
        match_id = hashlib.md5(f"{host}{datetime.now()}".encode()).hexdigest()[:8]
        code = match_id.upper()
        self.lobbies[match_id] = OnlineMatch(match_id, host, mode)
        self.join_codes[code] = match_id
        return code

    def join_by_code(self, code: str, player: str) -> bool:
        match_id = self.join_codes.get(code.upper())
        if match_id and match_id in self.lobbies:
            return self.lobbies[match_id].join(player)
        return False

    def quick_match(self, player_name: str, mode: str = "501", player_avg: float = 50.0):
        for code, match_id in list(self.join_codes.items()):
            lobby = self.lobbies.get(match_id)
            if lobby and lobby.status == "waiting" and len(lobby.players) < lobby.max_players:
                if self.join_by_code(code, player_name):
                    return code
        return self.create_lobby(player_name, mode)

    def get_open_lobbies(self):
        return [
            {"code": code, "host": l.host, "mode": l.mode, "players": f"{len(l.players)}/{l.max_players}"}
            for code, mid in self.join_codes.items()
            if (l := self.lobbies.get(mid)) and l.status == "waiting"
        ]

    def get_lobby_info(self, code: str):
        mid = self.join_codes.get(code.upper())
        if not mid or mid not in self.lobbies:
            return None
        l = self.lobbies[mid]
        return {
            "code": code, "host": l.host, "mode": l.mode,
            "players": l.players, "max_players": l.max_players, "status": l.status
        }


# ===== OTHER SYSTEMS (light implementations) =====
class DartsLiveFeatures:
    def __init__(self, player_name="Player"):
        self.player_name = player_name
        self.points = 0

class SocialSharing:
    @staticmethod
    def whatsapp_share(data): return "Share on WhatsApp"

class ThemeSystem:
    pass

class VirtualDartboard:
    pass

class SaveResumeManager:
    pass

class GradedLeague:
    pass

NAME_DATABASE = ["James", "John", "Robert", "Michael", "William"]
