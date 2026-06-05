"""
Party & Specialty Games: Killer Variants, Darts Golf, Tic-Tac-Toe, and Shanghai Championship.
"""

from typing import List, Dict, Optional, Set, Tuple
import random


class KillerGame:
    """
    Killer Game with difficulty variants.
    """
    def __init__(self, players: List[str], lives: int = 3, difficulty: str = "normal"):
        self.players = players
        self.lives = {p: lives for p in players}
        self.player_numbers = {p: None for p in players}  # Assigned segment
        self.killers = set()
        self.current_player_idx = 0
        self.difficulty = difficulty  # "soft", "normal", "hard", "sudden_death"
        self.winner = None
        self.turn_history = []
        
    def assign_number(self, player: str, number: int):
        """Assign a unique segment number to a player."""
        if number in self.player_numbers.values():
            return False, "Number already taken"
        self.player_numbers[player] = number
        return True, "Success"

    def record_throw(self, darts: List[int]) -> str:
        """Record a throw (3 darts)."""
        player = self.players[self.current_player_idx]
        if self.lives[player] <= 0:
            self._advance_player()
            return f"{player} is out!"
            
        msgs = []
        for dart in darts:
            if dart == 0: continue
            
            # Simplified parsing: value is segment * multiplier
            segment, multiplier = self._parse_dart(dart)
            
            # If not yet a killer, try to hit own number to become one
            if player not in self.killers:
                if segment == self.player_numbers[player]:
                    self.killers.add(player)
                    msgs.append(f"🔥 {player} is now a KILLER!")
            else:
                # If killer, try to hit others' numbers to take lives
                for other, num in self.player_numbers.items():
                    if other != player and segment == num:
                        self.lives[other] -= multiplier
                        msgs.append(f"⚔️ {player} hit {other}! {other} has {self.lives[other]} lives left.")
                        if self.lives[other] <= 0:
                            msgs.append(f"💀 {other} ELIMINATED!")
        
        # Check for winner
        active = [p for p in self.players if self.lives[p] > 0]
        if len(active) == 1:
            self.winner = active[0]
            msgs.append(f"🏆 {self.winner} WINS!")
            
        self._advance_player()
        return " | ".join(msgs) if msgs else "No hits."

    def _advance_player(self):
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        # Skip eliminated players
        while self.lives[self.players[self.current_player_idx]] <= 0 and self.winner is None:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)

    @staticmethod
    def _parse_dart(dart_value: int) -> Tuple[int, int]:
        if dart_value == 25: return 25, 1
        if dart_value == 50: return 25, 2
        if dart_value <= 20: return dart_value, 1
        elif dart_value <= 40 and dart_value % 2 == 0: return dart_value // 2, 2
        else: return dart_value // 3, 3


class DartsGolf:
    """
    Darts Golf: 9 or 18 holes. Each hole is a segment (1-18).
    Score is based on how many darts it takes to hit the target.
    """
    def __init__(self, players: List[str], holes: int = 9):
        self.players = players
        self.holes = holes
        self.current_hole = 1
        self.scores = {p: 0 for p in players}
        self.current_player_idx = 0
        self.winner = None

    def record_throw(self, darts: List[int]) -> str:
        player = self.players[self.current_player_idx]
        target = self.current_hole
        
        # Golf scoring:
        # Triple = 1 stroke
        # Double = 2 strokes
        # Single = 3 strokes
        # Miss = 5 strokes (if all 3 darts miss)
        
        hole_score = 5
        for dart in darts:
            seg, mult = self._parse_dart(dart)
            if seg == target:
                if mult == 3: hole_score = 1; break
                if mult == 2: hole_score = 2; break
                if mult == 1: hole_score = 3; break
        
        self.scores[player] += hole_score
        msg = f"{player} scored {hole_score} on Hole {target}."
        
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        if self.current_player_idx == 0:
            self.current_hole += 1
            if self.current_hole > self.holes:
                self.winner = min(self.scores, key=self.scores.get)
                msg += f" | Game Over! {self.winner} wins with {self.scores[self.winner]} strokes."
        
        return msg

    @staticmethod
    def _parse_dart(dart_value: int) -> Tuple[int, int]:
        if dart_value == 25: return 25, 1
        if dart_value == 50: return 25, 2
        if dart_value <= 20: return dart_value, 1
        elif dart_value <= 40 and dart_value % 2 == 0: return dart_value // 2, 2
        else: return dart_value // 3, 3


class TicTacToeDarts:
    """
    Tic-Tac-Toe Darts: Players claim segments on a 3x3 grid.
    Grid segments: [20, 1, 18, 4, 13, 6, 10, 15, 2]
    """
    def __init__(self, player1: str, player2: str):
        self.players = [player1, player2]
        self.grid = [None] * 9  # 0-8
        self.segments = [20, 1, 18, 4, 13, 6, 10, 15, 2]
        self.current_player_idx = 0
        self.winner = None

    def record_throw(self, darts: List[int]) -> str:
        player = self.players[self.current_player_idx]
        msgs = []
        
        for dart in darts:
            seg, _ = self._parse_dart(dart)
            if seg in self.segments:
                idx = self.segments.index(seg)
                if self.grid[idx] is None:
                    self.grid[idx] = player
                    msgs.append(f"✅ {player} claimed segment {seg}!")
                    if self._check_win(player):
                        self.winner = player
                        msgs.append(f"🏆 {player} WINS TIC-TAC-TOE!")
                        break
        
        self.current_player_idx = (self.current_player_idx + 1) % 2
        return " | ".join(msgs) if msgs else "No segments claimed."

    def _check_win(self, player: str) -> bool:
        wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        return any(all(self.grid[i] == player for i in combo) for combo in wins)

    @staticmethod
    def _parse_dart(dart_value: int) -> Tuple[int, int]:
        if dart_value == 25: return 25, 1
        if dart_value == 50: return 25, 2
        if dart_value <= 20: return dart_value, 1
        elif dart_value <= 40 and dart_value % 2 == 0: return dart_value // 2, 2
        else: return dart_value // 3, 3


class ShanghaiChampionship:
    """
    Shanghai Championship: Players must hit single, double, and triple of a segment.
    Each round is a different segment (1-20).
    "Shanghai" = hit S, D, and T of the current round segment in one turn (Instant Win).
    """
    def __init__(self, players: List[str], rounds: int = 7):
        self.players = players
        self.rounds = rounds
        self.current_round = 1
        self.scores = {p: 0 for p in players}
        self.current_player_idx = 0
        self.winner = None

    def record_throw(self, darts: List[int]) -> str:
        player = self.players[self.current_player_idx]
        target = self.current_round
        
        # Check for Shanghai (S, D, T in one turn)
        hits = {"S": False, "D": False, "T": False}
        turn_score = 0
        
        for dart in darts:
            seg, mult = self._parse_dart(dart)
            if seg == target:
                turn_score += dart
                if mult == 1: hits["S"] = True
                if mult == 2: hits["D"] = True
                if mult == 3: hits["T"] = True
        
        if all(hits.values()):
            self.winner = player
            return f"🌟 SHANGHAI! {player} wins instantly on segment {target}!"
        
        self.scores[player] += turn_score
        msg = f"{player} scored {turn_score} on segment {target}."
        
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        if self.current_player_idx == 0:
            self.current_round += 1
            if self.current_round > self.rounds:
                self.winner = max(self.scores, key=self.scores.get)
                msg += f" | Tournament Over! {self.winner} wins with {self.scores[self.winner]} points."
        
        return msg

    @staticmethod
    def _parse_dart(dart_value: int) -> Tuple[int, int]:
        if dart_value == 25: return 25, 1
        if dart_value == 50: return 25, 2
        if dart_value <= 20: return dart_value, 1
        elif dart_value <= 40 and dart_value % 2 == 0: return dart_value // 2, 2
        else: return dart_value // 3, 3
