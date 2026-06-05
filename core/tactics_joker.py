"""
Tactics Joker: A highly customizable game mode where players can designate "joker" numbers.
Hitting a triple of a joker number allows it to be used as a single bull (25 points).
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field


@dataclass
class TacticsJokerConfig:
    """Configuration for a Tactics Joker game."""
    joker_numbers: List[int]  # e.g., [1, 5, 10, 20]
    joker_triple_value: int = 25  # Points awarded for triple joker
    starting_score: int = 501
    bull_substitute_enabled: bool = True  # Can triple joker be used as bull?
    bull_substitute_value: int = 25  # Points if used as bull
    
    def validate(self) -> bool:
        """Validate configuration."""
        return all(1 <= n <= 20 for n in self.joker_numbers) and len(self.joker_numbers) > 0


class TacticsJokerGame:
    """
    Tactics Joker game implementation.
    
    Rules:
    - Players start with 501 (or custom score)
    - Joker numbers are designated at game start
    - Hitting a TRIPLE of a joker number gives 25 points (or custom value)
    - If bull_substitute_enabled, a triple joker can be used as a single bull (25 pts)
    """
    
    def __init__(self, players: List[str], config: TacticsJokerConfig):
        self.players = players
        self.config = config
        self.current_player_idx = 0
        self.scores = {p: config.starting_score for p in players}
        self.joker_hits = {p: {j: 0 for j in config.joker_numbers} for p in players}
        self.bull_substitutes_available = {p: 0 for p in players}  # Count of available bull subs
        self.history = []
        self.winner = None
        self.turn_number = 1
    
    def record_throw(self, darts: List[int]) -> str:
        """Record a throw and return result message."""
        player = self.players[self.current_player_idx]
        msgs = []
        
        for dart in darts:
            if dart == 0:
                continue
            
            segment, multiplier = self._parse_dart(dart)
            
            # Check if it's a joker triple
            if multiplier == 3 and segment in self.config.joker_numbers:
                self.joker_hits[player][segment] += 1
                self.bull_substitutes_available[player] += 1
                msgs.append(f"🃏 JOKER TRIPLE {segment}! (+1 Bull Substitute)")
            
            # Normal scoring
            score_gained = dart
            
            # Check if player wants to use a bull substitute
            # (This would be handled in the UI, but we track availability here)
            
            self.scores[player] -= score_gained
            
            if self.scores[player] < 0:
                self.scores[player] = 0
                msgs.append(f"BUST! Score reset to {self.config.starting_score}")
                self.scores[player] = self.config.starting_score
            elif self.scores[player] == 0:
                self.winner = player
                msgs.append(f"🎯 {player} WINS!")
        
        # Advance player
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        if self.current_player_idx == 0:
            self.turn_number += 1
        
        return " | ".join(msgs) if msgs else f"{player}: {sum(darts)} points"
    
    def use_bull_substitute(self, player: str) -> bool:
        """Use a bull substitute (triple joker as 25 pts)."""
        if self.bull_substitutes_available[player] > 0:
            self.bull_substitutes_available[player] -= 1
            self.scores[player] -= self.config.bull_substitute_value
            return True
        return False
    
    def get_joker_status(self, player: str) -> Dict:
        """Get current joker status for a player."""
        return {
            "player": player,
            "score": self.scores[player],
            "joker_hits": self.joker_hits[player],
            "bull_substitutes": self.bull_substitutes_available[player],
        }
    
    def get_scoreboard(self) -> Dict:
        """Get current game scoreboard."""
        return {
            "mode": "TACTICS_JOKER",
            "turn": self.turn_number,
            "current_player": self.players[self.current_player_idx],
            "joker_numbers": self.config.joker_numbers,
            "players": [
                {
                    "name": p,
                    "score": self.scores[p],
                    "bull_subs": self.bull_substitutes_available[p],
                    "is_current": p == self.players[self.current_player_idx],
                }
                for p in self.players
            ],
        }
    
    @staticmethod
    def _parse_dart(dart_value: int) -> tuple:
        """Parse dart value into (segment, multiplier)."""
        if dart_value == 0:
            return 0, 0
        if dart_value == 25:
            return 25, 1
        if dart_value == 50:
            return 25, 2
        if dart_value <= 20:
            return dart_value, 1
        elif dart_value <= 40:
            return dart_value // 2, 2
        else:
            return dart_value // 3, 3


class TacticsJokerBuilder:
    """Builder for creating custom Tactics Joker configurations."""
    
    def __init__(self):
        self.joker_numbers = []
        self.starting_score = 501
        self.joker_triple_value = 25
        self.bull_substitute_enabled = True
        self.bull_substitute_value = 25
    
    def add_joker(self, number: int) -> "TacticsJokerBuilder":
        """Add a joker number."""
        if 1 <= number <= 20 and number not in self.joker_numbers:
            self.joker_numbers.append(number)
        return self
    
    def add_jokers(self, numbers: List[int]) -> "TacticsJokerBuilder":
        """Add multiple joker numbers."""
        for n in numbers:
            self.add_joker(n)
        return self
    
    def set_starting_score(self, score: int) -> "TacticsJokerBuilder":
        """Set the starting score."""
        self.starting_score = score
        return self
    
    def set_joker_triple_value(self, value: int) -> "TacticsJokerBuilder":
        """Set the value of a triple joker."""
        self.joker_triple_value = value
        return self
    
    def enable_bull_substitute(self, enabled: bool) -> "TacticsJokerBuilder":
        """Enable/disable bull substitutes."""
        self.bull_substitute_enabled = enabled
        return self
    
    def set_bull_substitute_value(self, value: int) -> "TacticsJokerBuilder":
        """Set the value of a bull substitute."""
        self.bull_substitute_value = value
        return self
    
    def build(self) -> TacticsJokerConfig:
        """Build the configuration."""
        config = TacticsJokerConfig(
            joker_numbers=self.joker_numbers,
            joker_triple_value=self.joker_triple_value,
            starting_score=self.starting_score,
            bull_substitute_enabled=self.bull_substitute_enabled,
            bull_substitute_value=self.bull_substitute_value,
        )
        if not config.validate():
            raise ValueError("Invalid Tactics Joker configuration")
        return config


# Example presets
PRESET_CLASSIC = TacticsJokerConfig(
    joker_numbers=[1, 5, 10, 20],
    starting_score=501,
)

PRESET_AGGRESSIVE = TacticsJokerConfig(
    joker_numbers=[20],  # Only T20 is joker
    starting_score=301,
)

PRESET_BALANCED = TacticsJokerConfig(
    joker_numbers=[10, 15, 20],
    starting_score=501,
)
