"""
Dart Game Pro v2.2 — Comprehensive Systems Module
Covers: Voice recognition, SmartBot AI, Career Mode, Pro Simulation,
ELO/Skill systems, Pattern detection, Social features, DARTSLIVE features
"""

import random
import hashlib
import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict


# ===== VOICE RECOGNITION SYSTEM =====
class VoiceRecognition:
    """Simulated voice recognition for dart scoring.
    In production, would use Google Speech-to-Text or Whisper.
    """
    
    SCORE_PHRASES = {
        "sixty": 60, "t20": 60, "triple 20": 60, "triple twenty": 60,
        "fifty seven": 57, "t19": 57, "triple 19": 57,
        "fifty four": 54, "t18": 54, "triple 18": 54,
        "fifty one": 51, "t17": 51, "triple 17": 51,
        "forty eight": 48, "t16": 48, "triple 16": 48,
        "forty five": 45, "t15": 45, "triple 15": 45,
        "forty two": 42, "t14": 42, "triple 14": 42,
        "thirty nine": 39, "t13": 39, "triple 13": 39,
        "thirty six": 36, "t12": 36, "triple 12": 36,
        "thirty three": 33, "t11": 33, "triple 11": 33,
        "thirty": 30, "t10": 30, "triple 10": 30,
        "twenty seven": 27, "t9": 27, "triple 9": 27,
        "twenty four": 24, "t8": 24, "triple 8": 24,
        "twenty one": 21, "t7": 21, "triple 7": 21,
        "forty": 40, "d20": 40, "double 20": 40, "double twenty": 40,
        "thirty eight": 38, "d19": 38, "double 19": 38,
        "thirty six double": 36, "d18": 36, "double 18": 36,
        "thirty four": 34, "d17": 34, "double 17": 34,
        "thirty two": 32, "d16": 32, "double 16": 32,
        "thirty double": 30, "d15": 30, "double 15": 30,
        "twenty eight": 28, "d14": 28, "double 14": 28,
        "twenty six": 26, "d13": 26, "double 13": 26,
        "twenty four double": 24, "d12": 24, "double 12": 24,
        "twenty two": 22, "d11": 22, "double 11": 22,
        "twenty double": 20, "d10": 20, "double 10": 20,
        "eighteen double": 18, "d9": 18, "double 9": 18,
        "sixteen": 16, "d8": 16, "double 8": 16,
        "fourteen": 14, "d7": 14, "double 7": 14,
        "twelve": 12, "d6": 12, "double 6": 12,
        "ten": 10, "d5": 10, "double 5": 10,
        "eight": 8, "d4": 8, "double 4": 8,
        "six": 6, "d3": 6, "double 3": 6,
        "four": 4, "d2": 4, "double 2": 4,
        "two": 2, "d1": 2, "double 1": 2,
        "twenty": 20, "single 20": 20, "s20": 20,
        "nineteen": 19, "single 19": 19, "s19": 19,
        "eighteen": 18, "single 18": 18, "s18": 18,
        "seventeen": 17, "single 17": 17, "s17": 17,
        "sixteen single": 16, "single 16": 16, "s16": 16,
        "fifteen": 15, "single 15": 15, "s15": 15,
        "bull": 50, "bullseye": 50, "inner bull": 50,
        "outer bull": 25, "25": 25,
        "one": 1, "single 1": 1, "s1": 1,
        "zero": 0, "miss": 0, "nothing": 0, "no score": 0,
        "one hundred and eighty": 180, "one eighty": 180, "180": 180,
        "one hundred": 100, "hundred": 100, "ton": 100,
        "one forty": 140, "hundred and forty": 140,
        "one twenty": 120, "hundred and twenty": 120,
        "eighty": 80,
        "seventy": 70,
        "fifty": 50,
    }
    
    @classmethod
    def parse_score(cls, text: str) -> Optional[int]:
        """Parse a spoken score into a numeric value."""
        text = text.lower().strip().replace("-", " ").replace("  ", " ")
        
        # Direct match
        if text in cls.SCORE_PHRASES:
            return cls.SCORE_PHRASES[text]
        
        # Try to parse "X + Y + Z" or "X Y Z" format
        parts = text.split()
        if len(parts) >= 2:
            # Check for three-dart notation like "T20 T20 D20"
            total = 0
            for part in parts:
                if part in cls.SCORE_PHRASES:
                    total += cls.SCORE_PHRASES[part]
            if total > 0:
                return total
        
        # Try numeric parse
        try:
            return int(text)
        except ValueError:
            pass
        
        return None
    
    @classmethod
    def get_available_commands(cls) -> List[str]:
        return [
            "Say scores naturally: 'T20 T19 D20'",
            "Or totals: 'one hundred and eighty', '100', '180'",
            "Say 'miss' or 'zero' for a miss",
            "Say 'bull' for bullseye (50)",
            "Say 'outer bull' or '25' for outer bull",
        ]


# ===== SMARTBOT ADAPTIVE AI =====
class SmartBot:
    """Adaptive AI that analyzes your recent performance and adjusts difficulty."""
    
    def __init__(self, base_level: int = 5):
        self.base_level = base_level
        self.player_history: List[int] = []  # Recent throw totals
        self.adaptive_factor = 1.0
        self.consistency_bonus = 0
    
    def analyze_player(self, recent_throws: List[List[int]]):
        """Analyze player's recent throws and adapt."""
        if not recent_throws:
            return
        
        totals = [sum(t) for t in recent_throws[-10:]]  # Last 10 throws
        avg = sum(totals) / len(totals)
        
        # Adjust to match player's average
        # Target bot average = player average * 0.85 to 1.15
        target_avg = avg * random.uniform(0.90, 1.05)
        
        # Map to level 1-12
        if target_avg < 25: self.base_level = 2
        elif target_avg < 35: self.base_level = 3
        elif target_avg < 45: self.base_level = 4
        elif target_avg < 55: self.base_level = 5
        elif target_avg < 65: self.base_level = 6
        elif target_avg < 75: self.base_level = 7
        elif target_avg < 85: self.base_level = 8
        elif target_avg < 95: self.base_level = 9
        else: self.base_level = 10
        
        self.player_history = totals
    
    def get_adjusted_level(self) -> int:
        """Get the dynamically adjusted difficulty level."""
        level = self.base_level + self.consistency_bonus
        return max(1, min(12, level))
    
    def get_description(self) -> str:
        level = self.get_adjusted_level()
        descriptions = {
            1: "Struggling to keep up", 2: "Finding their feet", 3: "Getting competitive",
            4: "Close match", 5: "Evenly matched", 6: "Pushing you hard",
            7: "Making you work", 8: "Testing your limits", 9: "A real challenge",
            10: "World class opponent", 11: "Almost unbeatable", 12: "Machine precision"
        }
        return descriptions.get(level, "Adapting...")


# ===== PRO SIMULATION DATABASE =====
PRO_PLAYERS = {
    "mvg": {
        "name": "Michael van Gerwen",
        "avg": 102.5, "first9": 107.0, "checkout_pct": 48.0,
        "180_rate": 0.15, "style": "aggressive",
        "description": "3x World Champion. Relentless scoring power.",
    },
    "fallon": {
        "name": "Fallon Sherrock",
        "avg": 92.0, "first9": 96.0, "checkout_pct": 40.0,
        "180_rate": 0.10, "style": "calm",
        "description": "Queen of the Palace. Nerves of steel.",
    },
    "whitlock": {
        "name": "Simon Whitlock",
        "avg": 94.0, "first9": 98.0, "checkout_pct": 42.0,
        "180_rate": 0.11, "style": "consistent",
        "description": "The Wizard. Methodical and precise.",
    },
    "webster": {
        "name": "Mark Webster",
        "avg": 90.0, "first9": 93.0, "checkout_pct": 38.0,
        "180_rate": 0.08, "style": "tactical",
        "description": "Former Lakeside Champion. Tactical genius.",
    },
    "nicholson": {
        "name": "Paul Nicholson",
        "avg": 88.0, "first9": 91.0, "checkout_pct": 36.0,
        "180_rate": 0.07, "style": "gritty",
        "description": "The Asset. Tough competitor.",
    },
    "humphries": {
        "name": "Luke Humphries",
        "avg": 98.0, "first9": 103.0, "checkout_pct": 45.0,
        "180_rate": 0.13, "style": "aggressive",
        "description": "World Champion. Cool Hand Luke.",
    },
    "littler": {
        "name": "Luke Littler",
        "avg": 105.0, "first9": 110.0, "checkout_pct": 50.0,
        "180_rate": 0.18, "style": "aggressive",
        "description": "The Nuke. Young phenom with explosive power.",
    },
    "wright": {
        "name": "Peter Wright",
        "avg": 97.0, "first9": 101.0, "checkout_pct": 44.0,
        "180_rate": 0.12, "style": "flamboyant",
        "description": "Snakebite. Multiple world champion.",
    },
}


class ProSimulation:
    """Simulate playing against real professional dart players."""
    
    def __init__(self, pro_id: str, handicap: int = 0):
        self.pro = PRO_PLAYERS.get(pro_id, PRO_PLAYERS["mvg"])
        self.handicap = handicap  # Player advantage in points
        self.match_history = []
    
    def get_pro_throw(self) -> List[int]:
        """Generate a realistic throw for this pro."""
        avg = self.pro["avg"]
        # Convert 3-dart average to individual dart distribution
        # Pros hit T20 ~40% of time, T19 ~15%, other targets ~45%
        darts = []
        for _ in range(3):
            roll = random.random()
            if roll < 0.40:  # T20 attempt
                hit = random.random() < 0.65  # 65% hit rate on T20
                darts.append(60 if hit else random.choice([20, 1, 5]))
            elif roll < 0.55:  # T19 attempt
                hit = random.random() < 0.60
                darts.append(57 if hit else random.choice([19, 3, 7]))
            elif roll < 0.70:  # Other triple
                target = random.choice([18, 17, 14, 16])
                hit = random.random() < 0.55
                darts.append(target * 3 if hit else target)
            elif roll < 0.85:  # Double or single
                darts.append(random.choice([20, 20, 19, 18, 25, 50, 1, 5]))
            else:  # Miss or low score
                darts.append(random.choice([1, 5, 0, 12, 3]))
        
        # Normalize to match pro's average roughly
        current_avg = sum(darts) / 3
        target = avg / 3  # per-dart target
        if current_avg > 0:
            factor = target / current_avg
            darts = [min(60, max(0, int(d * factor))) for d in darts]
        
        return darts
    
    def get_match_intro(self) -> str:
        return f"🎯 Now entering the oche... {self.pro['name']}! {self.pro['description']}"
    
    def get_180_call(self) -> str:
        calls = [
            f"🎤 ONE HUNDRED AND EIGHTY! {self.pro['name']} is on fire!",
            f"🎤 180! Pure class from {self.pro['name']}!",
            f"🎤 Maximum! {self.pro['name']} showing why they're among the best!",
        ]
        return random.choice(calls)
    
    def get_checkout_call(self, remaining: int) -> str:
        return f"🎤 {self.pro['name']} requires {remaining}..."


# ===== CAREER MODE =====
@dataclass
class CareerEvent:
    name: str
    type: str  # "major", "premier", "euro_tour", "pro_tour", "challenge"
    prize_pool: int
    date: str
    completed: bool = False
    result: str = ""  # "W", "F", "SF", "QF", "L16", etc.
    prize_money: int = 0
    avg_thrown: float = 0.0


class CareerMode:
    """Full career mode: Season schedule, money list, world rankings."""
    
    SEASON_2024 = [
        CareerEvent("World Championship", "major", 2500000, "2024-01"),
        CareerEvent("UK Open", "major", 600000, "2024-03"),
        CareerEvent("Premier League Darts", "premier", 1000000, "2024-02"),
        CareerEvent("World Matchplay", "major", 800000, "2024-07"),
        CareerEvent("World Grand Prix", "major", 600000, "2024-10"),
        CareerEvent("European Championship", "major", 600000, "2024-10"),
        CareerEvent("Grand Slam of Darts", "major", 650000, "2024-11"),
        CareerEvent("Players Championship Finals", "major", 600000, "2024-11"),
        CareerEvent("World Series Finals", "major", 350000, "2024-09"),
        CareerEvent("Masters", "major", 300000, "2024-01"),
        CareerEvent("UK Open Qualifiers", "pro_tour", 100000, "2024-02"),
        CareerEvent("European Tour 1", "euro_tour", 175000, "2024-03"),
        CareerEvent("European Tour 2", "euro_tour", 175000, "2024-04"),
        CareerEvent("Players Championship 1-30", "pro_tour", 100000, "2024-02"),
        CareerEvent("World Series Events", "challenge", 200000, "2024-06"),
    ]
    
    def __init__(self, player_name: str):
        self.player_name = player_name
        self.season = 1
        self.world_ranking = 64
        self.total_prize_money = 0
        self.season_prize_money = 0
        self.events_completed = 0
        self.events_won = 0
        self.career_high_avg = 0.0
        self.season_avgs = []
        self.event_history = []
        self.current_event_idx = 0
        self.order_of_merit = []
    
    def get_current_event(self) -> Optional[CareerEvent]:
        if self.current_event_idx < len(self.SEASON_2024):
            return self.SEASON_2024[self.current_event_idx]
        return None
    
    def complete_event(self, result: str, avg_thrown: float) -> str:
        """Complete current event with result."""
        event = self.get_current_event()
        if not event:
            return "Season complete!"
        
        event.completed = True
        event.result = result
        event.avg_thrown = avg_thrown
        
        # Calculate prize money based on result
        prize_multipliers = {"W": 0.20, "F": 0.12, "SF": 0.07, "QF": 0.04, "L16": 0.02, "L32": 0.01}
        multiplier = prize_multipliers.get(result, 0.005)
        event.prize_money = int(event.prize_pool * multiplier)
        
        self.total_prize_money += event.prize_money
        self.season_prize_money += event.prize_money
        self.events_completed += 1
        
        if result == "W":
            self.events_won += 1
            self.world_ranking = max(1, self.world_ranking - random.randint(2, 5))
        elif result in ["F", "SF"]:
            self.world_ranking = max(1, self.world_ranking - random.randint(1, 3))
        
        if avg_thrown > self.career_high_avg:
            self.career_high_avg = avg_thrown
        
        self.season_avgs.append(avg_thrown)
        self.event_history.append(event)
        self.current_event_idx += 1
        
        msgs = [
            f"🏆 {event.name}: {result}",
            f"💰 Prize: £{event.prize_money:,}",
            f"📊 Average: {avg_thrown:.2f}",
            f"🌍 Ranking: #{self.world_ranking}",
        ]
        
        # Order of Merit update
        self._update_order_of_merit()
        
        return "\n".join(msgs)
    
    def _update_order_of_merit(self):
        """Update Order of Merit standings."""
        # Generate realistic OOM
        names = ["Littler", "Humphries", "Wright", "van Gerwen", self.player_name.split()[0]]
        oom = []
        for i, name in enumerate(names):
            money = random.randint(200000, 1500000) if name != self.player_name.split()[0] else self.total_prize_money
            oom.append({"rank": i+1, "name": name, "money": money})
        oom.sort(key=lambda x: -x["money"])
        for i, entry in enumerate(oom):
            entry["rank"] = i + 1
        self.order_of_merit = oom
    
    def get_status(self) -> Dict:
        return {
            "player": self.player_name,
            "season": self.season,
            "world_ranking": self.world_ranking,
            "total_prize_money": self.total_prize_money,
            "season_prize_money": self.season_prize_money,
            "events_won": self.events_won,
            "events_completed": f"{self.events_completed}/{len(self.SEASON_2024)}",
            "career_high_avg": round(self.career_high_avg, 2),
            "season_avg": round(sum(self.season_avgs)/len(self.season_avgs), 2) if self.season_avgs else 0,
            "next_event": self.get_current_event().name if self.get_current_event() else "Season Complete!",
            "order_of_merit": self.order_of_merit[:10],
        }


# ===== ELO RATING SYSTEM =====
class EloSystem:
    """ELO rating system for competitive play."""
    
    def __init__(self, base_rating: int = 1000):
        self.base_rating = base_rating
        self.k_factor = 32  # Standard K-factor
    
    @staticmethod
    def expected_score(rating_a: int, rating_b: int) -> float:
        """Calculate expected score for player A vs player B."""
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    
    def update_ratings(self, rating_a: int, rating_b: int, result_a: float) -> Tuple[int, int]:
        """Update ratings after a match. result_a: 1=win, 0.5=draw, 0=loss."""
        expected_a = self.expected_score(rating_a, rating_b)
        expected_b = 1 - expected_a
        
        new_a = int(rating_a + self.k_factor * (result_a - expected_a))
        new_b = int(rating_b + self.k_factor * ((1 - result_a) - expected_b))
        
        return new_a, new_b
    
    def get_grade(self, rating: int) -> str:
        """Get grade name for rating."""
        if rating >= 2400: return "Diamond"
        elif rating >= 2200: return "Platinum"
        elif rating >= 2000: return "Gold"
        elif rating >= 1800: return "Silver"
        elif rating >= 1600: return "Tungsten"
        elif rating >= 1400: return "Bronze"
        elif rating >= 1200: return "Copper"
        else: return "Beginner"
    
    def get_flight(self, rating: int) -> str:
        """DARTSLIVE-style flight rating."""
        if rating >= 2800: return "SA"
        elif rating >= 2600: return "AA"
        elif rating >= 2400: return "A"
        elif rating >= 2200: return "BB"
        elif rating >= 2000: return "B"
        elif rating >= 1800: return "CC"
        else: return "C"


# ===== SKILL LEVEL SYSTEM (like Easy Darts) =====
class SkillLevelSystem:
    """7-tier skill level system based on accuracy."""
    
    LEVELS = [
        {"name": "Beginner", "min": 0, "max": 15, "color": "#9E9E9E"},
        {"name": "Novice", "min": 15, "max": 30, "color": "#8BC34A"},
        {"name": "Intermediate", "min": 30, "max": 45, "color": "#4CAF50"},
        {"name": "Advanced", "min": 45, "max": 60, "color": "#2196F3"},
        {"name": "Expert", "min": 60, "max": 75, "color": "#9C27B0"},
        {"name": "Master", "min": 75, "max": 96, "color": "#FF9800"},
        {"name": "Elite", "min": 96, "max": 100, "color": "#F44336"},
    ]
    
    @classmethod
    def calculate_level(cls, throws: List[List[int]]) -> Dict:
        """Calculate skill level from throw history."""
        if not throws or len(throws) < 5:
            return {"level": "Beginner", "accuracy": 0, "tier": 1}
        
        # Calculate accuracy across different targets
        singles_hit = 0
        singles_total = 0
        doubles_hit = 0
        doubles_total = 0
        triples_hit = 0
        triples_total = 0
        bull_hit = 0
        bull_total = 0
        
        for throw in throws:
            for dart in throw:
                if dart == 0:
                    continue
                if dart == 50:  # Bull
                    bull_hit += 1
                    bull_total += 1
                elif dart == 25:  # Outer bull
                    bull_total += 1
                elif dart <= 20:  # Single
                    singles_hit += 1
                    singles_total += 1
                elif dart <= 40 and dart % 2 == 0:  # Double
                    doubles_hit += 1
                    doubles_total += 1
                elif dart <= 60 and dart % 3 == 0:  # Triple
                    triples_hit += 1
                    triples_total += 1
        
        # Weighted accuracy
        total_attempts = singles_total + doubles_total*2 + triples_total*3 + bull_total*4
        total_hits = singles_hit + doubles_hit*2 + triples_hit*3 + bull_hit*4
        
        if total_attempts == 0:
            accuracy = 0
        else:
            accuracy = (total_hits / total_attempts) * 100
        
        # Find level
        for level in cls.LEVELS:
            if level["min"] <= accuracy < level["max"]:
                return {
                    "level": level["name"],
                    "accuracy": round(accuracy, 1),
                    "tier": cls.LEVELS.index(level) + 1,
                    "color": level["color"],
                    "singles_pct": round(singles_hit/max(singles_total,1)*100, 1),
                    "doubles_pct": round(doubles_hit/max(doubles_total,1)*100, 1),
                    "triples_pct": round(triples_hit/max(triples_total,1)*100, 1),
                    "bull_pct": round(bull_hit/max(bull_total,1)*100, 1),
                }
        
        return {"level": "Elite", "accuracy": round(accuracy, 1), "tier": 7, "color": "#F44336"}


# ===== PATTERN DETECTION =====
class PatternDetector:
    """AI-powered pattern detection in throw data."""
    
    @staticmethod
    def detect_patterns(throws: List[List[int]]) -> List[Dict]:
        """Detect patterns and weaknesses in player's throw data."""
        patterns = []
        
        if not throws or len(throws) < 10:
            return [{"type": "info", "message": "Need more data for pattern detection. Keep playing!"}]
        
        totals = [sum(t) for t in throws]
        
        # Pattern 1: Declining performance (fatigue)
        first_half = sum(totals[:len(totals)//2]) / max(len(totals)//2, 1)
        second_half = sum(totals[len(totals)//2:]) / max(len(totals) - len(totals)//2, 1)
        if second_half < first_half * 0.85:
            patterns.append({
                "type": "fatigue",
                "severity": "high" if second_half < first_half * 0.7 else "medium",
                "message": f"Performance drops {((first_half-second_half)/first_half*100):.0f}% in later throws. Take more breaks!",
                "recommendation": "Practice stamina: Play longer sessions to build endurance."
            })
        
        # Pattern 2: First dart accuracy
        first_darts = [t[0] if len(t) > 0 else 0 for t in throws]
        first_avg = sum(first_darts) / max(len(first_darts), 1)
        if first_avg < 30:
            patterns.append({
                "type": "opening",
                "severity": "medium",
                "message": f"First dart average is only {first_avg:.1f}. You're not starting strong.",
                "recommendation": "Focus on your first dart - it's your most important. Warm up properly."
            })
        
        # Pattern 3: Consistency check
        import statistics
        try:
            std_dev = statistics.stdev(totals)
            mean = statistics.mean(totals)
            cv = (std_dev / mean) * 100 if mean > 0 else 0
            if cv > 35:
                patterns.append({
                    "type": "inconsistency",
                    "severity": "high" if cv > 50 else "medium",
                    "message": f"High variability (CV: {cv:.0f}%). Scores range from {min(totals)} to {max(totals)}.",
                    "recommendation": "Practice Around the Clock (Singles) for rhythm and consistency."
                })
        except statistics.StatisticsError:
            pass
        
        # Pattern 4: Big score frequency
        big_scores = sum(1 for t in totals if t >= 140)
        if big_scores / len(totals) < 0.1:
            patterns.append({
                "type": "scoring_power",
                "severity": "medium",
                "message": f"Only {big_scores/len(totals)*100:.0f}% of throws are 140+. Need more power.",
                "recommendation": "Focus on T20 accuracy. Try '100 Darts at T20' drill."
            })
        
        # Pattern 5: 180 frequency
        one_eighties = sum(1 for t in totals if t == 180)
        if one_eighties == 0 and len(totals) > 20:
            patterns.append({
                "type": "no_180s",
                "severity": "low",
                "message": "No 180s yet in this session. They're coming!",
                "recommendation": "Keep focusing on T20-T20-T20. The 180 will come."
            })
        
        return patterns if patterns else [{"type": "good", "message": "Looking solid! No major patterns detected.", "recommendation": "Keep doing what you're doing!"}]
    
    @staticmethod
    def weakness_analysis(throws: List[List[int]]) -> List[Dict]:
        """Detailed breakdown of weak doubles/segments."""
        double_hits = defaultdict(lambda: {"hit": 0, "miss": 0})
        
        for throw in throws:
            for dart in throw:
                # Check if aiming at a double (even number 2-40)
                if dart <= 40 and dart % 2 == 0 and dart > 0:
                    double_val = dart // 2
                    double_hits[double_val]["hit"] += 1
                elif dart <= 40 and dart > 0 and dart % 2 != 0:
                    # Likely aiming at nearby double
                    nearby_double = dart // 2
                    double_hits[nearby_double]["miss"] += 1
        
        weaknesses = []
        for double_num in range(1, 21):
            data = double_hits[double_num]
            total = data["hit"] + data["miss"]
            if total >= 3:
                pct = data["hit"] / total * 100
                if pct < 30:
                    weaknesses.append({
                        "double": f"D{double_num}",
                        "success_rate": round(pct, 1),
                        "attempts": total,
                        "severity": "high" if pct < 15 else "medium",
                    })
        
        # Sort by success rate ascending
        weaknesses.sort(key=lambda x: x["success_rate"])
        return weaknesses[:5]  # Top 5 weaknesses


# ===== NAME DATABASE FOR COMMENTARY =====
NAME_DATABASE = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
    "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Kenneth", "Joshua",
    "Kevin", "Brian", "George", "Timothy", "Ronald", "Jason", "Edward", "Jeffrey", "Ryan", "Jacob",
    "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon", "Benjamin",
    "Samuel", "Gregory", "Frank", "Alexander", "Raymond", "Patrick", "Jack", "Dennis", "Jerry", "Tyler",
    "Aaron", "Jose", "Adam", "Nathan", "Henry", "Douglas", "Zachary", "Peter", "Kyle", "Ethan",
    "Walter", "Noah", "Jeremy", "Christian", "Keith", "Roger", "Terry", "Gerald", "Harold", "Sean",
    "Austin", "Carl", "Arthur", "Lawrence", "Dylan", "Jesse", "Jordan", "Bryan", "Billy", "Joe",
    "Bruce", "Gabriel", "Logan", "Albert", "Willie", "Alan", "Juan", "Wayne", "Elijah", "Randy",
    "Roy", "Vincent", "Ralph", "Eugene", "Russell", "Bobby", "Mason", "Philip", "Louis", "Mary",
    "Emma", "Olivia", "Ava", "Sophia", "Isabella", "Mia", "Charlotte", "Amelia", "Harper", "Evelyn",
    "Abigail", "Emily", "Elizabeth", "Mila", "Ella", "Avery", "Sofia", "Camila", "Aria", "Scarlett",
    "Victoria", "Madison", "Luna", "Grace", "Chloe", "Penelope", "Layla", "Riley", "Zoey", "Nora",
    "Lily", "Eleanor", "Hannah", "Lillian", "Addison", "Aubrey", "Ellie", "Stella", "Natalie", "Zoe",
    "Leah", "Hazel", "Violet", "Aurora", "Savannah", "Audrey", "Brooklyn", "Bella", "Claire", "Skylar",
    # Darts player names
    "Phil", "Raymond", "Eric", "Adrian", "Michael", "Peter", "Gerwyn", "Rob", "Dimitri", "Daryl",
    "Nathan", "Jonny", "Joe", "Danny", "Krzysztof", "Dave", "Ross", "Gabriel", "Brendan", "Ryan",
    "Luke", "Chris", "Stephen", "Mensur", "Damon", "Ian", "Scott", "Callan", "Madars", "Martin",
    "Kim", "Vincent", "Jose", "Simon", "Rowby", "Jeffrey", "Florian", "Cameron", "Ricky", "Andrew",
    "Mickey", "Toni", "Jermaine", "Keegan", "William", "Steve", "Matt", "Wesley", "Darius", "Richard",
    # Nicknames
    "The Power", "The Hurricane", "Jackpot", "MVG", "Snakebite", "Cool Hand", "The Nuke",
    "Iceman", "Aussie", "Superchin", "The Asp", "Rapid", "Bully Boy", "The Rock",
]


class CommentaryEngine:
    """TV-style commentary system with name database."""
    
    def __init__(self):
        self.name_db = set(NAME_DATABASE)
    
    def get_commentary(self, event: str, player_name: str = "Player", score: int = 0, remaining: int = 501) -> str:
        """Generate contextual commentary for game events."""
        
        commentaries = {
            "180": [
                f"🎤 ONE HUNDRED AND EIGHTY! {player_name} with a maximum!",
                f"🎤 180! {player_name} is absolutely flying!",
                f"🎤 Maximum score! {player_name} showing their class!",
                f"🎤 ONE HUNDRED AND EIGHTY! The crowd goes wild!",
            ],
            "140": [
                f"🎤 One forty! {player_name} with a big score!",
                f"🎤 Ton plus! Excellent scoring from {player_name}!",
            ],
            "100": [
                f"🎤 Ton! {player_name} with a solid score.",
                f"🎤 One hundred! Good scoring from {player_name}.",
            ],
            "checkout": [
                f"🎤 Game shot! {player_name} takes the leg!",
                f"🎤 CHECKOUT! {player_name} finishes it!",
                f"🎤 {player_name} hits the double and the leg is theirs!",
            ],
            "bust": [
                f"🎤 Oh no! {player_name} has bust! Back they go!",
                f"🎤 Bust for {player_name}! That'll hurt!",
            ],
            "setup": [
                f"🎤 {player_name} requires {remaining}...",
                f"🎤 {player_name} needs {remaining} for the leg...",
            ],
            "match_intro": [
                f"🎤 Ladies and gentlemen, please welcome to the oche... {player_name}!",
                f"🎤 First on stage tonight... {player_name}!",
            ],
            "crowd": [
                "👏 *Crowd cheers*",
                "👏 *Applause*",
                "🙌 *Crowd roars*",
            ],
        }
        
        lines = commentaries.get(event, [f"🎤 {event}"])
        result = random.choice(lines)
        
        # Add crowd reaction for big moments
        if event in ["180", "checkout"]:
            result += f"\n{random.choice(commentaries['crowd'])}"
        
        return result
    
    def can_pronounce_name(self, name: str) -> bool:
        """Check if we have this name in our database."""
        return name in self.name_db


# ===== ONLINE SIMULATION (local multiplayer framework) =====
class OnlineMatch:
    """Simulated online match framework with lobby, chat, and spectator support."""
    
    def __init__(self, match_id: str, host: str, mode: str = "501", max_players: int = 2):
        self.match_id = match_id
        self.host = host
        self.mode = mode
        self.max_players = max_players
        self.players = [host]
        self.status = "waiting"  # waiting, active, finished
        self.chat_history = []
        self.spectators = []
        self.created_at = datetime.now().isoformat()
        self.abandonment_tracker = {}  # Track who leaves
    
    def join(self, player_name: str) -> bool:
        if len(self.players) < self.max_players and self.status == "waiting":
            self.players.append(player_name)
            self.chat_history.append({"from": "System", "msg": f"{player_name} joined the match!"})
            if len(self.players) >= self.max_players:
                self.status = "active"
                self.chat_history.append({"from": "System", "msg": "Match starting!"})
            return True
        return False
    
    def add_spectator(self, spectator_name: str):
        self.spectators.append(spectator_name)
        self.chat_history.append({"from": "System", "msg": f"{spectator_name} is watching!"})
    
    def send_chat(self, from_player: str, message: str):
        self.chat_history.append({"from": from_player, "msg": message, "time": datetime.now().isoformat()})
    
    def record_abandonment(self, player: str):
        self.abandonment_tracker[player] = self.abandonment_tracker.get(player, 0) + 1
    
    def get_abandonment_rate(self, player: str) -> float:
        total = len(self.abandonment_tracker)
        if total == 0:
            return 0.0
        return (self.abandonment_tracker.get(player, 0) / total) * 100


class LobbySystem:
    """Open lobby matchmaking system."""
    
    def __init__(self):
        self.lobbies: Dict[str, OnlineMatch] = {}
        self.join_codes: Dict[str, str] = {}  # code -> match_id
    
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
    
    def get_open_lobbies(self) -> List[Dict]:
        return [
            {"code": code, "host": lobby.host, "mode": lobby.mode, "players": f"{len(lobby.players)}/{lobby.max_players}"}
            for code, match_id in self.join_codes.items()
            if match_id in self.lobbies and self.lobbies[match_id].status == "waiting"
        ]


# ===== DARTSLIVE-STYLE FEATURES =====
class DartsLiveFeatures:
    """DARTSLIVE-inspired gamification features."""
    
    def __init__(self, player_name: str):
        self.player_name = player_name
        self.rating = 1000.0  # Starting rating
        self.points = 0  # In-game currency
        self.anniversaries = {}
        self.awards = []
        self.login_streak = 0
        self.last_login = None
        self.groups = []
        self.home_shop = None
    
    def update_rating(self, game_result: str, avg_thrown: float):
        """Update real-time rating based on game performance."""
        base_change = {"W": 15, "F": 10, "SF": 7, "QF": 5, "L16": 3, "L": -5}
        change = base_change.get(game_result, 0)
        avg_bonus = (avg_thrown - 60) * 0.5  # Bonus for high averages
        self.rating = max(0, self.rating + change + avg_bonus)
    
    def get_flight(self) -> str:
        """Get DARTSLIVE-style flight rating."""
        r = self.rating
        if r >= 2800: return "SA"
        elif r >= 2600: return "AA"
        elif r >= 2400: return "A"
        elif r >= 2200: return "BB"
        elif r >= 2000: return "B"
        elif r >= 1800: return "CC"
        else: return "C"
    
    def check_login_bonus(self) -> Dict:
        """Check daily login bonus."""
        today = datetime.now().date()
        
        if self.last_login:
            last = datetime.fromisoformat(self.last_login).date()
            if today == last:
                return {"bonus": 0, "streak": self.login_streak, "message": "Already claimed today!"}
            elif (today - last).days == 1:
                self.login_streak += 1
            else:
                self.login_streak = 1
        else:
            self.login_streak = 1
        
        self.last_login = datetime.now().isoformat()
        bonus = min(50, 10 * self.login_streak)  # Increasing bonus
        self.points += bonus
        
        return {
            "bonus": bonus,
            "streak": self.login_streak,
            "total_points": self.points,
            "message": f"Day {self.login_streak} login bonus: +{bonus} points! 🔥"
        }
    
    def add_anniversary(self, event_type: str):
        """Track playing anniversaries."""
        if event_type not in self.anniversaries:
            self.anniversaries[event_type] = datetime.now().isoformat()
    
    def get_anniversaries(self) -> List[Dict]:
        """Get upcoming/current anniversaries."""
        results = []
        for event, date_str in self.anniversaries.items():
            date = datetime.fromisoformat(date_str)
            years = (datetime.now() - date).days / 365.25
            results.append({"event": event, "years": round(years, 1), "date": date_str[:10]})
        return results


# ===== GRADED LEAGUE SYSTEM (like GDL180) =====
class GradedLeague:
    """Graded league system with promotion/relegation."""
    
    DIVISIONS = [
        {"name": "Diamond", "min_avg": 85, "max_players": 16},
        {"name": "Platinum", "min_avg": 75, "max_players": 16},
        {"name": "Gold", "min_avg": 65, "max_players": 16},
        {"name": "Silver", "min_avg": 55, "max_players": 16},
        {"name": "Tungsten", "min_avg": 45, "max_players": 16},
        {"name": "Bronze", "min_avg": 35, "max_players": 16},
    ]
    
    def __init__(self, player_name: str):
        self.player_name = player_name
        self.division = "Bronze"
        self.season = 1
        self.season_wins = 0
        self.season_losses = 0
        self.season_points = 0
        self.all_time_wins = 0
        self.all_time_losses = 0
    
    def record_match(self, won: bool, avg: float):
        """Record a league match result."""
        if won:
            self.season_wins += 1
            self.season_points += 3
            self.all_time_wins += 1
        else:
            self.season_losses += 1
            self.all_time_losses += 1
        
        # Auto-adjust division based on average
        for div in self.DIVISIONS:
            if avg >= div["min_avg"]:
                if div["name"] != self.division:
                    old = self.division
                    self.division = div["name"]
                    return f"🎉 PROMOTED! {old} → {self.division}!"
                break
    
    def end_season(self) -> str:
        """End season, handle promotion/relegation."""
        win_rate = self.season_wins / max(self.season_wins + self.season_losses, 1)
        
        # Top 2 promote, bottom 2 relegate
        standing = self.season_points
        
        result = f"Season {self.season} Complete! {self.season_wins}W-{self.season_losses}L | Points: {self.season_points}"
        
        if win_rate >= 0.7:
            # Find next division up
            current_idx = next(i for i, d in enumerate(self.DIVISIONS) if d["name"] == self.division)
            if current_idx > 0:
                old = self.division
                self.division = self.DIVISIONS[current_idx - 1]["name"]
                result += f"\n🎉 PROMOTED! {old} → {self.division}!"
        elif win_rate <= 0.3:
            current_idx = next(i for i, d in enumerate(self.DIVISIONS) if d["name"] == self.division)
            if current_idx < len(self.DIVISIONS) - 1:
                old = self.division
                self.division = self.DIVISIONS[current_idx + 1]["name"]
                result += f"\n📉 Relegated to {self.division}"
        
        self.season += 1
        self.season_wins = 0
        self.season_losses = 0
        self.season_points = 0
        
        return result


# ===== AI MATCH REPORTER =====
class AIMatchReporter:
    """Generate detailed AI-powered post-match reports."""
    
    @staticmethod
    def generate_report(match_data: Dict) -> str:
        """Generate comprehensive match report."""
        lines = []
        lines.append("=" * 60)
        lines.append("🤖 AI MATCH REPORT")
        lines.append("=" * 60)
        
        for player in match_data.get("players", []):
            name = player.get("name", "Unknown")
            avg = player.get("average", 0)
            throws = player.get("throws", 0)
            one_eighties = player.get("one_eighties", 0)
            
            lines.append(f"\n📊 {name}:")
            lines.append(f"   3-Dart Average: {avg:.1f}")
            lines.append(f"   Throws: {throws}")
            lines.append(f"   180s: {one_eighties}")
            
            # AI Analysis
            if avg >= 90:
                lines.append(f"   🟢 AI: World-class performance! Consistent 90+ averaging.")
            elif avg >= 75:
                lines.append(f"   🟢 AI: Strong performance. Professional-level scoring.")
            elif avg >= 60:
                lines.append(f"   🟡 AI: Solid performance. Good club player standard.")
            elif avg >= 45:
                lines.append(f"   🟡 AI: Decent showing. Room for improvement on the scoring.")
            else:
                lines.append(f"   🔴 AI: Below average. Focus on T20 accuracy in practice.")
            
            if one_eighties >= 3:
                lines.append(f"   🔥 AI: {one_eighties}x 180s! Power scoring was a highlight.")
            
            # Pattern observations
            if player.get("checkout_pct", 0) < 25:
                lines.append(f"   💡 AI: Checkout percentage below 25%. Practice Bob's 27 daily.")
        
        # Head-to-head
        if len(match_data.get("players", [])) == 2:
            p1, p2 = match_data["players"][:2]
            avg_diff = abs(p1.get("average", 0) - p2.get("average", 0))
            if avg_diff > 15:
                better = p1["name"] if p1["average"] > p2["average"] else p2["name"]
                lines.append(f"\n📈 The difference in scoring power ({avg_diff:.1f} avg) was decisive.")
                lines.append(f"   {better} dominated the scoring department.")
        
        lines.append("\n" + "=" * 60)
        lines.append("Generated by Dart Game Pro AI Reporter")
        lines.append("=" * 60)
        
        return "\n".join(lines)


# ===== SOCIAL SHARING =====
class SocialSharing:
    """Generate shareable content for social media."""
    
    @staticmethod
    def whatsapp_share(match_data: Dict) -> str:
        """Generate WhatsApp-formatted share text."""
        lines = [
            f"🎯 *Dart Game Pro Results*",
            f"",
            f"Mode: *{match_data.get('mode', '501').upper()}*",
            f"Winner: *🏆 {match_data.get('winner', 'N/A')}*",
            f"",
            f"*Stats:*",
        ]
        for p in match_data.get("players", []):
            avg = p.get("average", 0)
            t80 = p.get("one_eighties", 0)
            lines.append(f"  {p['name']}: {avg:.1f} avg | {t80}x 180s")
        
        lines.append("")
        lines.append("Download: github.com/Stijnman/Dart-app")
        return "\n".join(lines)
    
    @staticmethod
    def twitter_share(match_data: Dict) -> str:
        """Twitter-formatted (280 char limit)."""
        winner = match_data.get("winner", "")
        mode = match_data.get("mode", "501")
        return f"Just won a {mode} match on Dart Game Pro! 🎯🏆 Average: {match_data['players'][0]['average']:.1f} | 180s: {match_data['players'][0]['one_eighties']} #Darts #DartGamePro"
    
    @staticmethod
    def camera_roll_summary(match_data: Dict) -> str:
        """Generate a text summary suitable for saving/sharing."""
        lines = [
            f"Dart Game Pro - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Mode: {match_data.get('mode', '501').upper()}",
            f"Winner: {match_data.get('winner', 'N/A')}",
            "",
        ]
        for p in match_data.get("players", []):
            lines.append(f"{p['name']}: {p['average']:.1f} avg, {p['one_eighties']} 180s, best: {p.get('best_throw', 0)}")
        return "\n".join(lines)


# ===== THEME SYSTEM =====
class ThemeSystem:
    """Unlockable color themes with points economy."""
    
    THEMES = {
        "default": {"name": "Default", "colors": {"bg": "#0e1117", "accent": "#00cc88"}, "cost": 0},
        "red_hot": {"name": "Red Hot", "colors": {"bg": "#1a0a0a", "accent": "#ff4444"}, "cost": 100},
        "blue_steel": {"name": "Blue Steel", "colors": {"bg": "#0a0a1a", "accent": "#4488ff"}, "cost": 100},
        "purple_haze": {"name": "Purple Haze", "colors": {"bg": "#140a1a", "accent": "#aa44ff"}, "cost": 150},
        "golden_throw": {"name": "Golden Throw", "colors": {"bg": "#1a1400", "accent": "#ffaa00"}, "cost": 200},
        "pink_power": {"name": "Pink Power", "colors": {"bg": "#1a0a14", "accent": "#ff66aa"}, "cost": 150},
        "cyberpunk": {"name": "Cyberpunk", "colors": {"bg": "#0d0d1a", "accent": "#00ffcc"}, "cost": 300},
        "retro": {"name": "Retro Arcade", "colors": {"bg": "#001a00", "accent": "#33ff33"}, "cost": 250},
    }
    
    def __init__(self, unlocked: List[str] = None):
        self.unlocked = set(unlocked or ["default"])
        self.current = "default"
    
    def unlock(self, theme_id: str, available_points: int) -> Tuple[bool, str]:
        if theme_id in self.unlocked:
            return False, "Already unlocked!"
        
        theme = self.THEMES.get(theme_id)
        if not theme:
            return False, "Theme not found!"
        
        if available_points >= theme["cost"]:
            self.unlocked.add(theme_id)
            return True, f"Unlocked '{theme['name']}' for {theme['cost']} points!"
        return False, f"Need {theme['cost']} points, you have {available_points}"
    
    def get_available_themes(self, player_points: int) -> List[Dict]:
        result = []
        for tid, theme in self.THEMES.items():
            result.append({
                "id": tid,
                "name": theme["name"],
                "cost": theme["cost"],
                "unlocked": tid in self.unlocked,
                "can_afford": player_points >= theme["cost"],
                "colors": theme["colors"],
            })
        return result


# ===== VIRTUAL DARTBOARD INPUT =====
class VirtualDartboard:
    """Interactive virtual dartboard for tap-based scoring."""
    
    # Standard dartboard layout (number, then positions)
    BOARD_LAYOUT = {
        # segment: (single, double, triple)
        20: {"single": 20, "double": 40, "triple": 60},
        1: {"single": 1, "double": 2, "triple": 3},
        18: {"single": 18, "double": 36, "triple": 54},
        4: {"single": 4, "double": 8, "triple": 12},
        13: {"single": 13, "double": 26, "triple": 39},
        6: {"single": 6, "double": 12, "triple": 18},
        10: {"single": 10, "double": 20, "triple": 30},
        15: {"single": 15, "double": 30, "triple": 45},
        2: {"single": 2, "double": 4, "triple": 6},
        17: {"single": 17, "double": 34, "triple": 51},
        3: {"single": 3, "double": 6, "triple": 9},
        19: {"single": 19, "double": 38, "triple": 57},
        7: {"single": 7, "double": 14, "triple": 21},
        16: {"single": 16, "double": 32, "triple": 48},
        8: {"single": 8, "double": 16, "triple": 24},
        11: {"single": 11, "double": 22, "triple": 33},
        14: {"single": 14, "double": 28, "triple": 42},
        9: {"single": 9, "double": 18, "triple": 27},
        12: {"single": 12, "double": 24, "triple": 36},
        5: {"single": 5, "double": 10, "triple": 15},
        25: {"single": 25, "double": 50, "triple": 0},  # Bull/Bullseye
    }
    
    @classmethod
    def get_segment_score(cls, segment: int, ring: str) -> int:
        """Get score for a segment + ring combination."""
        data = cls.BOARD_LAYOUT.get(segment, {})
        return data.get(ring, 0)
    
    @classmethod
    def get_board_segments(cls) -> List[int]:
        """Get all board segment numbers in standard order."""
        return [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]


# ===== SAVE/RESUME SYSTEM =====
class SaveResumeManager:
    """Save and resume games mid-match."""
    
    SAVE_DIR = "data/saves"
    
    @classmethod
    def save_game(cls, game_state, save_name: str = None) -> str:
        """Save current game state to file."""
        os.makedirs(cls.SAVE_DIR, exist_ok=True)
        
        if not save_name:
            save_name = f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        filepath = os.path.join(cls.SAVE_DIR, f"{save_name}.json")
        
        save_data = {
            "save_name": save_name,
            "saved_at": datetime.now().isoformat(),
            "game_state": game_state.to_snapshot() if hasattr(game_state, 'to_snapshot') else str(game_state),
        }
        
        with open(filepath, 'w') as f:
            json.dump(save_data, f, default=str)
        
        return filepath
    
    @classmethod
    def list_saves(cls) -> List[Dict]:
        """List all saved games."""
        if not os.path.exists(cls.SAVE_DIR):
            return []
        
        saves = []
        for fname in sorted(os.listdir(cls.SAVE_DIR)):
            if fname.endswith('.json'):
                filepath = os.path.join(cls.SAVE_DIR, fname)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    saves.append({
                        "name": data.get("save_name", fname),
                        "saved_at": data.get("saved_at", "unknown"),
                        "filepath": filepath,
                    })
                except:
                    pass
        return saves
