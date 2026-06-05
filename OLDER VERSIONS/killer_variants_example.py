
"""
Killer Variants Extension for Dart Game Pro v2.4
Starter implementation for Feature #1: Killer Variants (Soft Killer 3 lives, Hard Killer 1 life, Sudden Death Killer)

Current repo has basic Killer / killer_party in engine.py (native).
This adds configurable lives system + sudden death rule.

How to integrate:
1. Add to core/extensions.py or as new sub-engine mode.
2. Register in engine.py ModeRegistry under PARTY or new KILLER_VARIANTS category.
3. Add UI selector for variant type in game setup screen.
4. Extend game_state with per-player 'lives' tracking.

This is a clean, self-contained starting point you can expand.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class KillerPlayerState:
    name: str
    lives: int = 3
    numbers_hit: List[int] = field(default_factory=list)  # or use bitmask for closed numbers
    is_eliminated: bool = False

class KillerVariantsGame:
    """
    Enhanced Killer with multiple difficulty variants.
    Rules (customizable):
    - Each player starts with N lives.
    - Hit your own number (or specific targets) to reduce a life? (Classic Killer often: hit numbers to "kill" others or survive).
    - Standard variant logic can be: last player with lives remaining wins, or first to hit all own numbers while reducing others.
    
    For simplicity here we implement a common "Killer" style:
    - Players have lives.
    - On your turn you try to hit targets; successful hits can deduct lives from opponents or protect your own.
    - Soft: 3 lives, miss = lose 1 life sometimes.
    - Hard: 1 life.
    - Sudden Death: any miss after certain point = lose all remaining lives.
    """

    VARIANT_CONFIGS = {
        "soft": {"lives": 3, "name": "Soft Killer", "description": "Forgiving — 3 lives, standard deductions"},
        "hard": {"lives": 1, "name": "Hard Killer", "description": "Brutal — only 1 life"},
        "sudden_death": {"lives": 3, "name": "Sudden Death Killer", "description": "Lose ALL lives on a single miss after the first round"}
    }

    def __init__(self, players: List[str], variant: str = "soft", starting_lives: Optional[int] = None):
        self.variant = variant
        config = self.VARIANT_CONFIGS.get(variant, self.VARIANT_CONFIGS["soft"])
        self.starting_lives = starting_lives or config["lives"]
        self.players: Dict[str, KillerPlayerState] = {
            p: KillerPlayerState(name=p, lives=self.starting_lives) for p in players
        }
        self.current_player_idx = 0
        self.round = 1
        self.game_over = False
        self.winner: Optional[str] = None
        self.log: List[str] = []

    @property
    def current_player(self) -> str:
        return list(self.players.keys())[self.current_player_idx]

    def record_hit(self, player: str, target_hit: bool = True, is_own_number: bool = False):
        """Call this from engine when a dart hits (you decide the rule for what 'hit' means in your Killer)."""
        state = self.players[player]
        if state.is_eliminated:
            return

        if not target_hit:
            # Miss handling
            if self.variant == "sudden_death" and self.round > 1:
                state.lives = 0
                self.log.append(f"{player} missed in Sudden Death mode — all lives lost!")
            else:
                state.lives = max(0, state.lives - 1)
                self.log.append(f"{player} missed — lost 1 life. Lives left: {state.lives}")

            if state.lives <= 0:
                state.is_eliminated = True
                self.log.append(f"💀 {player} has been eliminated!")
        else:
            # Successful hit logic (example: can be "kill" an opponent or gain life, etc.)
            # For demo: successful hit on own number or target protects or deducts from random opponent
            if is_own_number:
                # Classic protection or progress
                self.log.append(f"{player} hit their number — staying strong!")
            else:
                # Example: deduct life from a random other active player (aggressive Killer variant)
                active_others = [p for p, s in self.players.items() if not s.is_eliminated and p != player]
                if active_others:
                    victim = active_others[0]  # or random.choice
                    self.players[victim].lives = max(0, self.players[victim].lives - 1)
                    self.log.append(f"{player} hit — {victim} loses a life! ({self.players[victim].lives} left)")

        self._check_game_over()

    def next_turn(self):
        if self.game_over:
            return
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        # Skip eliminated
        while self.players[list(self.players.keys())[self.current_player_idx]].is_eliminated:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        self.round += 1  # simplistic; better to track full rounds

    def _check_game_over(self):
        active = [p for p, s in self.players.items() if not s.is_eliminated]
        if len(active) <= 1:
            self.game_over = True
            self.winner = active[0] if active else None
            if self.winner:
                self.log.append(f"🏆 {self.winner} wins {self.VARIANT_CONFIGS[self.variant]['name']}!")

    def get_status(self) -> Dict:
        return {
            "variant": self.VARIANT_CONFIGS[self.variant]["name"],
            "players": {p: {"lives": s.lives, "eliminated": s.is_eliminated} for p, s in self.players.items()},
            "current_player": self.current_player,
            "round": self.round,
            "game_over": self.game_over,
            "winner": self.winner,
            "recent_log": self.log[-5:] if self.log else []
        }

# Quick test
if __name__ == "__main__":
    game = KillerVariantsGame(["Alice", "Bob", "Charlie"], variant="sudden_death")
    print(game.get_status())
    game.record_hit("Alice", target_hit=False)
    print(game.get_status())
