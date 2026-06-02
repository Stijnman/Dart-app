"""
Game state management and turn tracking.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class InOutRule(str, Enum):
    STRAIGHT = "straight"      # Any score to start/finish
    DOUBLE = "double"          # Must hit double to start/finish
    MASTER = "master"          # Must hit double or triple to start/finish


class GameMode(str, Enum):
    # X01 family
    X01 = "x01"
    # Cricket family
    CRICKET = "cricket"
    CUT_THROAT = "cut_throat"
    NO_SCORE_CRICKET = "no_score_cricket"
    # Practice games
    BOBS_27 = "bobs_27"
    AROUND_THE_CLOCK = "around_the_clock"
    SHANGHAI = "shanghai"
    # Party games
    KILLER = "killer"
    HALF_IT = "half_it"


class MatchFormat(str, Enum):
    SINGLE_GAME = "single_game"
    BEST_OF_3 = "best_of_3"
    BEST_OF_5 = "best_of_5"
    BEST_OF_7 = "best_of_7"
    FIRST_TO_3 = "first_to_3"
    FIRST_TO_5 = "first_to_5"
    FIRST_TO_7 = "first_to_7"


@dataclass
class TurnRecord:
    turn_number: int
    player_name: str
    darts: List[int]
    total: int
    message: str
    score_after: Optional[int] = None
    is_bust: bool = False
    is_checkout: bool = False
    is_one_eighty: bool = False
    is_hundred_plus: bool = False


@dataclass
class GameState:
    mode: str = "501"
    variant: str = "standard"  # For cricket variants, practice variants
    players: List[Any] = field(default_factory=list)
    current_player_idx: int = 0
    turn_number: int = 1
    history: List[TurnRecord] = field(default_factory=list)
    winner: Optional[str] = None
    match_winner: Optional[str] = None
    
    # Match tracking
    legs_format: MatchFormat = MatchFormat.SINGLE_GAME
    legs_to_win: int = 1
    legs_won: Dict[str, int] = field(default_factory=dict)
    sets_format: Optional[MatchFormat] = None
    sets_to_win: int = 0
    sets_won: Dict[str, int] = field(default_factory=dict)
    current_leg: int = 1
    current_set: int = 1
    
    # X01 rules
    in_rule: InOutRule = InOutRule.STRAIGHT
    out_rule: InOutRule = InOutRule.DOUBLE
    starting_score: int = 501
    
    # Handicap
    handicaps: Dict[str, int] = field(default_factory=dict)  # Score offset per player
    
    # Undo stack
    undo_stack: List[dict] = field(default_factory=list, repr=False)
    redo_stack: List[dict] = field(default_factory=list, repr=False)
    
    # Game-specific state
    cricket_marks: Dict[str, Dict[int, int]] = field(default_factory=dict)
    cricket_points: Dict[str, int] = field(default_factory=dict)
    cricket_closed: Dict[int, str] = field(default_factory=dict)  # who closed each number
    
    # Shanghai state
    shanghai_round: int = 1
    shanghai_targets: List[int] = field(default_factory=list)
    
    # Killer state
    killer_lives: Dict[str, int] = field(default_factory=dict)
    killer_claimed: Dict[str, int] = field(default_factory=dict)  # number each player owns
    killer_available: List[int] = field(default_factory=list)
    
    # Half It state
    half_it_targets: List[str] = field(default_factory=list)
    half_it_current_target_idx: int = 0
    half_it_scores: Dict[str, int] = field(default_factory=dict)
    
    # Around the Clock state
    atc_targets: Dict[str, int] = field(default_factory=dict)  # current target for each player
    atc_hit_type: str = "single"  # single, double, triple
    
    # Bob's 27 state
    bobs27_score: Dict[str, int] = field(default_factory=dict)
    bobs27_current_target_idx: Dict[str, int] = field(default_factory=dict)
    bobs27_lives: Dict[str, int] = field(default_factory=dict)
    bobs27_mode: str = "standard"  # easy, standard, hard
    
    # Bot settings
    bot_enabled: bool = False
    bot_difficulty: int = 5
    bot_player_idx: int = -1
    
    def current_player(self):
        if not self.players:
            return None
        return self.players[self.current_player_idx]
    
    def next_player(self):
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        if self.current_player_idx == 0:
            self.turn_number += 1
    
    def get_player_by_name(self, name: str):
        for p in self.players:
            if p.name == name:
                return p
        return None
    
    def to_snapshot(self) -> dict:
        """Create a snapshot for undo."""
        return {
            "current_player_idx": self.current_player_idx,
            "turn_number": self.turn_number,
            "winner": self.winner,
            "legs_won": self.legs_won.copy(),
            "sets_won": self.sets_won.copy(),
            "current_leg": self.current_leg,
            "current_set": self.current_set,
            "cricket_marks": {k: v.copy() for k, v in self.cricket_marks.items()},
            "cricket_points": self.cricket_points.copy(),
            "cricket_closed": self.cricket_closed.copy(),
            "shanghai_round": self.shanghai_round,
            "killer_lives": self.killer_lives.copy(),
            "killer_claimed": self.killer_claimed.copy(),
            "killer_available": self.killer_available.copy(),
            "half_it_current_target_idx": self.half_it_current_target_idx,
            "half_it_scores": self.half_it_scores.copy(),
            "atc_targets": self.atc_targets.copy(),
            "bobs27_score": self.bobs27_score.copy(),
            "bobs27_current_target_idx": {k: v for k, v in self.bobs27_current_target_idx.items()},
            "bobs27_lives": self.bobs27_lives.copy(),
            "player_scores": [p.score for p in self.players],
            "player_throws": [p.throws.copy() for p in self.players],
            "history": list(self.history),  # Copy history for redo
        }
    
    def from_snapshot(self, snap: dict):
        """Restore from snapshot."""
        self.current_player_idx = snap["current_player_idx"]
        self.turn_number = snap["turn_number"]
        self.winner = snap["winner"]
        self.legs_won = snap["legs_won"].copy()
        self.sets_won = snap["sets_won"].copy()
        self.current_leg = snap["current_leg"]
        self.current_set = snap["current_set"]
        self.cricket_marks = {k: v.copy() for k, v in snap["cricket_marks"].items()}
        self.cricket_points = snap["cricket_points"].copy()
        self.cricket_closed = snap["cricket_closed"].copy()
        self.shanghai_round = snap["shanghai_round"]
        self.killer_lives = snap["killer_lives"].copy()
        self.killer_claimed = snap["killer_claimed"].copy()
        self.killer_available = snap["killer_available"].copy()
        self.half_it_current_target_idx = snap["half_it_current_target_idx"]
        self.half_it_scores = snap["half_it_scores"].copy()
        self.atc_targets = snap["atc_targets"].copy()
        self.bobs27_score = snap["bobs27_score"].copy()
        self.bobs27_current_target_idx = snap["bobs27_current_target_idx"].copy()
        self.bobs27_lives = snap["bobs27_lives"].copy()
        if "history" in snap:
            self.history = list(snap["history"])
        for i, p in enumerate(self.players):
            p.score = snap["player_scores"][i]
            p.throws = [t.copy() for t in snap["player_throws"][i]]
