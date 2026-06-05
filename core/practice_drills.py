"""
Advanced Training & Practice Drills: Bob 27, Game 121, and Halve-It.
"""

from typing import List, Dict, Optional, Tuple


class Bob27:
    """
    Bob 27: Double practice game.
    Start with 27 points. Aim for doubles in order (D1 to D20, then DB).
    Hit = add double value. Miss = subtract double value.
    If score <= 0, game over.
    """
    def __init__(self, player: str):
        self.player = player
        self.score = 27
        self.targets = [i for i in range(1, 21)] + [25]
        self.current_target_idx = 0
        self.winner = None
        self.is_over = False

    def record_throw(self, darts: List[int]) -> str:
        if self.is_over: return "Game already over."
        
        target = self.targets[self.current_target_idx]
        hits = 0
        for dart in darts:
            seg, mult = self._parse_dart(dart)
            if seg == target and mult == 2:
                hits += 1
        
        target_val = target * 2 if target != 25 else 50
        if hits > 0:
            self.score += (hits * target_val)
            msg = f"Hit {hits}x D{target if target != 25 else 'Bull'}. Score: {self.score}"
        else:
            self.score -= target_val
            msg = f"Missed D{target if target != 25 else 'Bull'}. Score: {self.score}"
        
        if self.score <= 0:
            self.score = 0
            self.is_over = True
            msg += " | Game Over! You ran out of points."
        else:
            self.current_target_idx += 1
            if self.current_target_idx >= len(self.targets):
                self.is_over = True
                self.winner = self.player
                msg += f" | Success! Final Score: {self.score}"
        
        return msg

    @staticmethod
    def _parse_dart(dart_value: int) -> Tuple[int, int]:
        if dart_value == 25: return 25, 1
        if dart_value == 50: return 25, 2
        if dart_value <= 20: return dart_value, 1
        elif dart_value <= 40 and dart_value % 2 == 0: return dart_value // 2, 2
        else: return dart_value // 3, 3


class Game121:
    """
    Game 121: Checkout practice.
    Start at 121. Must check out in 9 darts (3 turns).
    If success, move to 122. If fail, restart at 121.
    """
    def __init__(self, player: str, start_score: int = 121):
        self.player = player
        self.current_goal = start_score
        self.remaining = start_score
        self.darts_thrown = 0
        self.turns_taken = 0
        self.msg_log = []

    def record_throw(self, darts: List[int]) -> str:
        self.turns_taken += 1
        turn_score = sum(darts)
        
        # Simple check for double finish (X01 style)
        # In practice mode, we assume the last dart hit was a double if it reaches 0
        if self.remaining - turn_score == 0:
            msg = f"Checked out {self.current_goal}! Moving to {self.current_goal + 1}."
            self.current_goal += 1
            self.remaining = self.current_goal
            self.turns_taken = 0
        elif self.remaining - turn_score < 2 or self.turns_taken >= 3:
            msg = f"Failed {self.current_goal}. Restarting."
            self.remaining = self.current_goal
            self.turns_taken = 0
        else:
            self.remaining -= turn_score
            msg = f"Remaining: {self.remaining} ({3 - self.turns_taken} turns left)"
            
        return msg


class HalveIt:
    """
    Halve-It: Aim for specific targets each round.
    If no hits in a round, score is halved.
    Targets: 20, 16, Double 7, 14, Triple 10, 17, Bull.
    """
    def __init__(self, players: List[str]):
        self.players = players
        self.targets = [
            (20, 1), (16, 1), (7, 2), (14, 1), (10, 3), (17, 1), (25, 1)
        ]
        self.current_round = 0
        self.scores = {p: 40 for p in players}  # Start with 40
        self.current_player_idx = 0
        self.winner = None

    def record_throw(self, darts: List[int]) -> str:
        player = self.players[self.current_player_idx]
        target_seg, target_mult = self.targets[self.current_round]
        
        round_score = 0
        for dart in darts:
            seg, mult = self._parse_dart(dart)
            if seg == target_seg and (target_mult == 1 or mult == target_mult):
                round_score += dart
        
        if round_score > 0:
            self.scores[player] += round_score
            msg = f"{player} hit target! Score: {self.scores[player]}"
        else:
            self.scores[player] //= 2
            msg = f"{player} missed! Score halved to {self.scores[player]}"
        
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        if self.current_player_idx == 0:
            self.current_round += 1
            if self.current_round >= len(self.targets):
                self.winner = max(self.scores, key=self.scores.get)
                msg += f" | Game Over! {self.winner} wins."
        
        return msg

    @staticmethod
    def _parse_dart(dart_value: int) -> Tuple[int, int]:
        if dart_value == 25: return 25, 1
        if dart_value == 50: return 25, 2
        if dart_value <= 20: return dart_value, 1
        elif dart_value <= 40 and dart_value % 2 == 0: return dart_value // 2, 2
        else: return dart_value // 3, 3
