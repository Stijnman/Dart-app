"""
Tournament & Ladder League Systems: Brackets, Round Robin, and ELO-based Ladder.
"""

from typing import List, Dict, Optional, Tuple
import math
import json
import random


class TournamentBracket:
    """
    Manages a Knockout (Single Elimination) Tournament.
    """
    def __init__(self, players: List[str]):
        self.players = players
        self.size = self._get_bracket_size(len(players))
        self.bracket = self._initialize_bracket()
        self.results = {}  # match_id -> winner

    def _get_bracket_size(self, n: int) -> int:
        """Get the smallest power of 2 >= n."""
        return 2 ** math.ceil(math.log2(n))

    def _initialize_bracket(self) -> List[List[Optional[str]]]:
        """Initialize the bracket structure."""
        # Randomize seeding
        players = self.players[:]
        random.shuffle(players)
        
        # Add byes
        while len(players) < self.size:
            players.append(None)  # BYE
            
        rounds = []
        # Round 1
        round1 = []
        for i in range(0, self.size, 2):
            round1.append((players[i], players[i+1]))
        rounds.append(round1)
        
        # Subsequent rounds
        current_size = self.size // 2
        while current_size > 1:
            current_size //= 2
            rounds.append([(None, None)] * current_size)
            
        return rounds

    def record_match_result(self, round_idx: int, match_idx: int, winner: str):
        """Record the winner of a match and advance them to the next round."""
        self.results[f"{round_idx}_{match_idx}"] = winner
        
        # Advance to next round
        if round_idx + 1 < len(self.bracket):
            next_match_idx = match_idx // 2
            current_match = list(self.bracket[round_idx + 1][next_match_idx])
            current_match[match_idx % 2] = winner
            self.bracket[round_idx + 1][next_match_idx] = tuple(current_match)

    def get_status(self) -> Dict:
        """Get current tournament status."""
        return {
            "type": "Knockout",
            "size": self.size,
            "bracket": self.bracket,
            "results": self.results,
            "winner": self.results.get(f"{len(self.bracket)-1}_0")
        }


class LadderLeague:
    """
    ELO-based Ladder League with Tiers (Bronze, Silver, Gold, Pro).
    """
    TIERS = {
        "Pro": 2000,
        "Gold": 1500,
        "Silver": 1000,
        "Bronze": 0
    }

    def __init__(self):
        self.players = {}  # name -> {elo, tier, games_played, wins}

    def add_player(self, name: str, start_elo: int = 1000):
        if name not in self.players:
            self.players[name] = {
                "elo": start_elo,
                "tier": self._get_tier(start_elo),
                "games_played": 0,
                "wins": 0
            }

    def _get_tier(self, elo: int) -> str:
        for tier, min_elo in self.TIERS.items():
            if elo >= min_elo:
                return tier
        return "Bronze"

    def record_match(self, winner: str, loser: str):
        """Update ELO after a match using the ELO formula."""
        if winner not in self.players: self.add_player(winner)
        if loser not in self.players: self.add_player(loser)
        
        K = 32  # K-factor
        elo_w = self.players[winner]["elo"]
        elo_l = self.players[loser]["elo"]
        
        # Expected scores
        exp_w = 1 / (1 + 10 ** ((elo_l - elo_w) / 400))
        exp_l = 1 / (1 + 10 ** ((elo_w - elo_l) / 400))
        
        # Update ELO
        self.players[winner]["elo"] = round(elo_w + K * (1 - exp_w))
        self.players[loser]["elo"] = round(elo_l + K * (0 - exp_l))
        
        # Update tiers and stats
        for p in [winner, loser]:
            self.players[p]["tier"] = self._get_tier(self.players[p]["elo"])
            self.players[p]["games_played"] += 1
            
        self.players[winner]["wins"] += 1

    def get_standings(self) -> List[Dict]:
        """Get league standings sorted by ELO."""
        standings = []
        for name, stats in self.players.items():
            standings.append({
                "name": name,
                **stats
            })
        return sorted(standings, key=lambda x: x["elo"], reverse=True)


class TournamentManager:
    """Main coordinator for all tournament activities."""
    def __init__(self):
        self.active_tournaments = {}
        self.league = LadderLeague()

    def create_knockout(self, tournament_id: str, players: List[str]):
        self.active_tournaments[tournament_id] = TournamentBracket(players)
        return self.active_tournaments[tournament_id]

    def get_tournament(self, tournament_id: str) -> Optional[TournamentBracket]:
        return self.active_tournaments.get(tournament_id)
