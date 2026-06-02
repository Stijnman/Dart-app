"""
Player model with comprehensive stats tracking.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Player:
    name: str
    picture: Optional[str] = None
    anonymous: bool = False
    
    # Game state (reset per leg)
    score: int = 501
    throws: List[List[int]] = field(default_factory=list)
    current_round_throws: List[int] = field(default_factory=list)
    wins: int = 0
    legs_won: int = 0
    sets_won: int = 0
    
    # Cricket-specific
    cricket_marks: Dict[int, int] = field(default_factory=dict)
    cricket_points: int = 0
    
    # Practice game state
    practice_score: int = 0
    practice_state: Dict = field(default_factory=dict)
    
    # Per-leg stats
    leg_throws: int = 0
    leg_total_scored: int = 0
    
    def reset_for_leg(self, starting_score: int = 501):
        self.score = starting_score
        self.throws = []
        self.current_round_throws = []
        self.leg_throws = 0
        self.leg_total_scored = 0
        self.cricket_marks = {}
        self.cricket_points = 0
        self.practice_score = 0
        self.practice_state = {}
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "picture": self.picture,
            "anonymous": self.anonymous,
            "score": self.score,
            "wins": self.wins,
            "legs_won": self.legs_won,
            "sets_won": self.sets_won,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        p = cls(
            name=data.get("name", "Player"),
            picture=data.get("picture"),
            anonymous=data.get("anonymous", False),
        )
        p.score = data.get("score", 501)
        p.wins = data.get("wins", 0)
        p.legs_won = data.get("legs_won", 0)
        p.sets_won = data.get("sets_won", 0)
        return p

    def get_stats_summary(self) -> dict:
        """Calculate session stats for this player."""
        throws_list = self.throws
        total_throws = len(throws_list)
        if total_throws == 0:
            return {
                "name": self.name,
                "throws": 0,
                "average": 0.0,
                "first_nine_avg": 0.0,
                "hundreds": 0,
                "ton_forties": 0,
                "ton_eighties": 0,
                "best_throw": 0,
                "worst_throw": 0,
                "checkout_rate": 0.0,
            }
        
        totals = [sum(t) for t in throws_list]
        total_score = sum(totals)
        avg = total_score / total_throws
        
        # First 9 darts average (first 3 throws)
        first_nine = throws_list[:3]
        first_nine_avg = sum(sum(t) for t in first_nine) / len(first_nine) if first_nine else 0
        
        hundreds = sum(1 for t in totals if 100 <= t <= 139)
        ton_forties = sum(1 for t in totals if 140 <= t <= 179)
        ton_eighties = sum(1 for t in totals if t == 180)
        
        return {
            "name": self.name,
            "throws": total_throws,
            "average": round(avg, 2),
            "first_nine_avg": round(first_nine_avg, 2),
            "hundreds": hundreds,
            "ton_forties": ton_forties,
            "ton_eighties": ton_eighties,
            "best_throw": max(totals),
            "worst_throw": min(totals),
            "total_scored": total_score,
            "darts_thrown": total_throws * 3,
        }
