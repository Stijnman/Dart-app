"""
Game extensions: Bounce-out tracking, baseball, gotcha, team ATC.
Refactored: Clean implementation with proper state management.
"""

from typing import List, Dict, Optional, Tuple
from collections import defaultdict


# =============================================================================
# BOUNCE-OUT TRACKER
# =============================================================================

class BounceOutTracker:
    """Track bounce-outs (darts that hit the board but fall out)."""

    def __init__(self):
        self.bounce_outs: Dict[str, List[int]] = defaultdict(list)
        self.total_bounce_outs = 0

    def record_bounce_out(self, player_name: str, dart_num: int = 1):
        """Record a bounce-out."""
        self.bounce_outs[player_name].append(dart_num)
        self.total_bounce_outs += 1

    def get_bounce_outs(self, player_name: str) -> List[int]:
        """Get bounce-out history for a player."""
        return list(self.bounce_outs[player_name])

    def get_total(self, player_name: str = None) -> int:
        """Get total bounce-outs."""
        if player_name:
            return len(self.bounce_outs[player_name])
        return self.total_bounce_outs

    def get_summary(self) -> Dict:
        """Get bounce-out summary."""
        return {
            "total": self.total_bounce_outs,
            "by_player": {name: len(darts) for name, darts in self.bounce_outs.items()},
        }


# =============================================================================
# BASEBALL DARTS
# =============================================================================

class BaseballDarts:
    """
    Baseball Darts: 9 innings (segments 1-9).
    Triple = 3 runs, Double = 2 runs, Single = 1 run, Miss = 0.
    """

    def __init__(self, players: List[str]):
        self.players = players
        self.innings = list(range(1, 10))
        self.scores = {p: 0 for p in players}
        self.current_inning = 0
        self.current_player_idx = 0
        self.winner = None
        self.inning_history = []

    def record_throw(self, darts: List[int]) -> str:
        if self.current_inning >= len(self.innings):
            return "Game over!"

        player = self.players[self.current_player_idx]
        target = self.innings[self.current_inning]
        runs = 0

        for dart in darts:
            if dart == target * 3:
                runs += 3
            elif dart == target * 2:
                runs += 2
            elif dart == target:
                runs += 1

        self.scores[player] += runs
        self.inning_history.append({
            "inning": target, "player": player, "runs": runs, "darts": darts
        })

        msg = f"{player} Inning {target}: {runs} runs (Total: {self.scores[player]})"

        self.current_player_idx += 1
        if self.current_player_idx >= len(self.players):
            self.current_player_idx = 0
            self.current_inning += 1

        if self.current_inning >= len(self.innings):
            self.winner = max(self.scores, key=self.scores.get)
            msg += f" | 🏆 {self.winner} wins with {self.scores[self.winner]} runs!"

        return msg

    def to_snapshot(self) -> dict:
        return {
            "scores": self.scores.copy(),
            "current_inning": self.current_inning,
            "current_player_idx": self.current_player_idx,
            "winner": self.winner,
        }

    def from_snapshot(self, snap: dict):
        self.scores = snap["scores"].copy()
        self.current_inning = snap["current_inning"]
        self.current_player_idx = snap["current_player_idx"]
        self.winner = snap.get("winner")

    def get_leaderboard(self) -> List[Tuple[str, int]]:
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=True)


# =============================================================================
# GOTCHA GAME
# =============================================================================

class GotchaGame:
    """
    Gotcha: Players try to hit a target score. If you exceed it, you bust.
    Last player standing wins.
    """

    def __init__(self, players: List[str], lives: int = 3, target_score: int = 301):
        self.players = players
        self.lives = {p: lives for p in players}
        self.scores = {p: 0 for p in players}
        self.target_score = target_score
        self.current_player_idx = 0
        self.winner = None

    def record_throw(self, darts: List[int]) -> str:
        player = self.players[self.current_player_idx]
        if self.lives[player] <= 0:
            return f"{player} is already out!"

        total = sum(darts)
        new_score = self.scores[player] + total

        if new_score > self.target_score:
            self.lives[player] -= 1
            msg = f"{player}: BUST! {total}pts -> Lives: {self.lives[player]}"
            if self.lives[player] <= 0:
                msg += f" | {player} is OUT!"
        else:
            self.scores[player] = new_score
            msg = f"{player}: +{total}pts (Total: {self.scores[player]}/{self.target_score})"

        # Check winner
        alive = [p for p in self.players if self.lives[p] > 0]
        if len(alive) == 1:
            self.winner = alive[0]
            msg += f" | 🏆 {self.winner} wins!"
        elif self.scores[player] == self.target_score:
            self.winner = player
            msg += f" | 🏆 {player} hits exactly {self.target_score}! Wins!"

        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        # Skip eliminated players
        while self.lives[self.players[self.current_player_idx]] <= 0 and self.winner is None:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)

        return msg

    def to_snapshot(self) -> dict:
        return {
            "scores": self.scores.copy(),
            "lives": self.lives.copy(),
            "current_player_idx": self.current_player_idx,
            "winner": self.winner,
        }

    def from_snapshot(self, snap: dict):
        self.scores = snap["scores"].copy()
        self.lives = snap["lives"].copy()
        self.current_player_idx = snap["current_player_idx"]
        self.winner = snap.get("winner")

    def get_leaderboard(self) -> List[Tuple[str, int]]:
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=True)


# =============================================================================
# TEAM ROUND THE CLOCK
# =============================================================================

class TeamRoundTheClock:
    """
    Team Around the Clock: Teams alternate, combined score matters.
    """

    def __init__(self, teams: List[Dict]):
        self.teams = teams  # [{"name": "Team A", "players": ["P1", "P2"]}, ...]
        self.scores = {t["name"]: 0 for t in teams}
        self.current_target = 1
        self.current_team_idx = 0
        self.winner = None
        self.targets = list(range(1, 21)) + [25]

    def record_hit(self, hit: bool) -> str:
        team = self.teams[self.current_team_idx]["name"]

        if hit:
            self.scores[team] += self.current_target
            msg = f"{team}: HIT {self.current_target}! (Total: {self.scores[team]})"
        else:
            msg = f"{team}: Missed {self.current_target}"

        self.current_team_idx = (self.current_team_idx + 1) % len(self.teams)
        if self.current_team_idx == 0:
            self.current_target += 1

        if self.current_target > len(self.targets):
            self.winner = max(self.scores, key=self.scores.get)
            msg += f" | 🏆 {self.winner} wins with {self.scores[self.winner]}!"

        return msg

    def to_snapshot(self) -> dict:
        return {
            "scores": self.scores.copy(),
            "current_target": self.current_target,
            "current_team_idx": self.current_team_idx,
            "winner": self.winner,
        }

    def from_snapshot(self, snap: dict):
        self.scores = snap["scores"].copy()
        self.current_target = snap["current_target"]
        self.current_team_idx = snap["current_team_idx"]
        self.winner = snap.get("winner")

    def get_leaderboard(self) -> List[Tuple[str, int]]:
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
