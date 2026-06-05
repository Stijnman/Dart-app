"""
Advanced Player Analytics & Heatmap Generation
Tracks detailed statistics for every player to enable Ghost Bot cloning and visual analytics.
"""

from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass
import math
import json

@dataclass
class DartThrowAnalysis:
    """Detailed analysis of a single throw."""
    segment: int  # 1-20 or 25 (bull)
    multiplier: int  # 1 (single), 2 (double), 3 (triple)
    score: int
    accuracy: float  # 0-1, how close to intended target
    consistency_group: str  # "T20_cluster", "miss_low", etc.


class PlayerHeatmap:
    """Generate visual heatmap data for a player's throw patterns."""
    
    SEGMENTS = list(range(1, 21)) + [25]  # 1-20 + Bull
    
    def __init__(self, player_name: str):
        self.player_name = player_name
        self.segment_hits = defaultdict(lambda: {"single": 0, "double": 0, "triple": 0, "total_score": 0})
        self.miss_zones = defaultdict(int)  # Track misses near each segment
        
    def record_throw(self, segment: int, multiplier: int, score: int):
        """Record a throw and update heatmap."""
        mult_name = {1: "single", 2: "double", 3: "triple"}.get(multiplier, "single")
        self.segment_hits[segment][mult_name] += 1
        self.segment_hits[segment]["total_score"] += score
    
    def record_miss(self, near_segment: int):
        """Record a miss near a segment."""
        self.miss_zones[near_segment] += 1
    
    def get_heatmap_data(self) -> Dict:
        """Return heatmap data for visualization."""
        heatmap = {}
        for seg in self.SEGMENTS:
            hits = self.segment_hits.get(seg, {"single": 0, "double": 0, "triple": 0, "total_score": 0})
            total_hits = hits.get("single", 0) + hits.get("double", 0) + hits.get("triple", 0)
            avg_score = hits.get("total_score", 0) / total_hits if total_hits > 0 else 0
            
            heatmap[seg] = {
                "total_hits": total_hits,
                "singles": hits.get("single", 0),
                "doubles": hits.get("double", 0),
                "triples": hits.get("triple", 0),
                "avg_score": round(avg_score, 1),
                "intensity": min(total_hits / 10, 1.0),  # 0-1 for color intensity
                "misses_nearby": self.miss_zones.get(seg, 0),
            }
        
        return heatmap
    
    def get_favorite_segments(self, top_n: int = 5) -> List[Tuple[int, int]]:
        """Get player's top N favorite/most-hit segments."""
        sorted_segs = sorted(
            [(seg, self.segment_hits.get(seg, {}).get("single", 0) + self.segment_hits.get(seg, {}).get("double", 0) + self.segment_hits.get(seg, {}).get("triple", 0)) for seg in self.SEGMENTS],
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_segs[:top_n]
    
    def get_weak_segments(self, top_n: int = 5) -> List[Tuple[int, int]]:
        """Get player's weakest segments (lowest hit count)."""
        sorted_segs = sorted(
            [(seg, self.segment_hits.get(seg, {}).get("single", 0) + self.segment_hits.get(seg, {}).get("double", 0) + self.segment_hits.get(seg, {}).get("triple", 0)) for seg in self.SEGMENTS],
            key=lambda x: x[1]
        )
        return sorted_segs[:top_n]


class AdvancedPlayerStats:
    """Comprehensive player statistics for cloning and analysis."""
    
    def __init__(self, player_name: str):
        self.player_name = player_name
        self.throws_history = []  # List of [dart1, dart2, dart3] per turn
        self.game_records = []  # List of game results
        self.heatmap = PlayerHeatmap(player_name)
        
        # Behavioral patterns
        self.pressure_performance = {}  # Score when ahead vs. behind
        self.checkout_patterns = {}  # Common checkout sequences
        self.opening_throws = []  # First throw of each leg
        self.closing_throws = []  # Last throw of each leg
        
    def add_throw(self, darts: List[int]):
        """Record a throw (3 darts)."""
        self.throws_history.append(darts)
        
        # Update heatmap
        for dart in darts:
            if dart == 0:
                continue
            segment, multiplier = self._parse_dart(dart)
            self.heatmap.record_throw(segment, multiplier, dart)
    
    def add_game_record(self, mode: str, result: str, avg: float, one_eighties: int, checkouts: int):
        """Record a completed game."""
        self.game_records.append({
            "mode": mode,
            "result": result,  # "win" or "loss"
            "average": avg,
            "one_eighties": one_eighties,
            "checkouts": checkouts,
        })
    
    def record_opening_throw(self, dart_score: int):
        """Record the opening throw of a leg."""
        self.opening_throws.append(dart_score)
    
    def record_closing_throw(self, dart_score: int):
        """Record the closing throw of a leg."""
        self.closing_throws.append(dart_score)
    
    def get_opening_throw_pattern(self) -> Dict:
        """Analyze opening throw patterns."""
        if not self.opening_throws:
            return {"most_common": 0, "average": 0, "consistency": 0}
        
        avg = sum(self.opening_throws) / len(self.opening_throws)
        from statistics import stdev
        std = stdev(self.opening_throws) if len(self.opening_throws) > 1 else 0
        
        return {
            "most_common": max(set(self.opening_throws), key=self.opening_throws.count),
            "average": round(avg, 1),
            "consistency": round(100 - (std / avg * 100) if avg > 0 else 0, 1),
        }
    
    def get_closing_throw_pattern(self) -> Dict:
        """Analyze closing throw patterns."""
        if not self.closing_throws:
            return {"most_common": 0, "average": 0, "success_rate": 0}
        
        avg = sum(self.closing_throws) / len(self.closing_throws)
        success = sum(1 for t in self.closing_throws if t > 0) / len(self.closing_throws)
        
        return {
            "most_common": max(set(self.closing_throws), key=self.closing_throws.count),
            "average": round(avg, 1),
            "success_rate": round(success * 100, 1),
        }
    
    def get_comprehensive_profile(self) -> Dict:
        """Generate a complete player profile for cloning."""
        if not self.game_records:
            return {"error": "Insufficient data"}
        
        wins = sum(1 for g in self.game_records if g["result"] == "win")
        total_games = len(self.game_records)
        avg_avg = sum(g["average"] for g in self.game_records) / total_games
        total_180s = sum(g["one_eighties"] for g in self.game_records)
        
        return {
            "player_name": self.player_name,
            "total_games": total_games,
            "win_rate": round(wins / total_games * 100, 1),
            "average_average": round(avg_avg, 1),
            "total_180s": total_180s,
            "favorite_segments": self.heatmap.get_favorite_segments(5),
            "weak_segments": self.heatmap.get_weak_segments(5),
            "opening_pattern": self.get_opening_throw_pattern(),
            "closing_pattern": self.get_closing_throw_pattern(),
            "heatmap": self.heatmap.get_heatmap_data(),
        }
    
    @staticmethod
    def _parse_dart(dart_value: int) -> Tuple[int, int]:
        """Parse a dart value into (segment, multiplier)."""
        if dart_value == 0:
            return 0, 0
        if dart_value == 25:
            return 25, 1  # Outer bull
        if dart_value == 50:
            return 25, 2  # Bullseye
        
        # Single (1-20)
        if dart_value <= 20:
            return dart_value, 1
        # Double (40-60, even)
        elif dart_value <= 40:
            return dart_value // 2, 2
        # Triple (51-60, odd)
        else:
            return dart_value // 3, 3


class PlayerCloneManager:
    """Manages player clones for Ghost Bot functionality."""
    
    def __init__(self):
        self.player_profiles = {}  # player_name -> AdvancedPlayerStats
    
    def create_profile(self, player_name: str) -> AdvancedPlayerStats:
        """Create a new player profile."""
        profile = AdvancedPlayerStats(player_name)
        self.player_profiles[player_name] = profile
        return profile
    
    def get_profile(self, player_name: str) -> Optional[AdvancedPlayerStats]:
        """Retrieve a player profile."""
        return self.player_profiles.get(player_name)
    
    def export_profile_json(self, player_name: str) -> str:
        """Export a player profile as JSON for storage."""
        profile = self.get_profile(player_name)
        if not profile:
            return "{}"
        
        return json.dumps({
            "player_name": profile.player_name,
            "profile": profile.get_comprehensive_profile(),
            "throws_count": len(profile.throws_history),
        }, indent=2)
    
    def load_profile_json(self, json_data: str) -> Optional[AdvancedPlayerStats]:
        """Load a player profile from JSON."""
        try:
            data = json.loads(json_data)
            profile = AdvancedPlayerStats(data["player_name"])
            self.player_profiles[data["player_name"]] = profile
            return profile
        except:
            return None
