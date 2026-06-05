"""
Dart Game Pro v2.4 — Additional Game Modes (11+ modes)
Refactored: Added snapshot support, dart validation, extracted shared utilities, fixed bugs.
"""

import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from .utils import parse_dart_value, validate_dart_throw, is_valid_dart_score


# ===== COUNT UP =====
class CountUpGame:
    """Simple high-score game — score as many points as possible in fixed rounds."""

    def __init__(self, players: List[str], rounds: int = 8):
        self.players = players
        self.total_rounds = rounds
        self.scores = {p: 0 for p in players}
        self.current_round = 1
        self.current_player_idx = 0
        self.round_history: List[Dict] = []
        self.winner = None

    def record_throw(self, darts: List[int]) -> str:
        valid, error = validate_dart_throw(darts)
        if not valid:
            return f"Invalid throw: {error}"

        player = self.players[self.current_player_idx]
        total = sum(darts)
        self.scores[player] += total

        self.round_history.append({
            "round": self.current_round, "player": player,
            "darts": darts, "total": total
        })

        msg = f"{player} Round {self.current_round}: {darts} = {total} (Total: {self.scores[player]})"

        # Advance
        self.current_player_idx += 1
        if self.current_player_idx >= len(self.players):
            self.current_player_idx = 0
            self.current_round += 1

        if self.current_round > self.total_rounds:
            self.winner = max(self.scores, key=self.scores.get)
            msg += f" | GAME OVER! 🏆 {self.winner} wins with {self.scores[self.winner]}!"

        return msg

    def to_snapshot(self) -> dict:
        return {
            "scores": self.scores.copy(),
            "current_round": self.current_round,
            "current_player_idx": self.current_player_idx,
            "round_history": list(self.round_history),
            "winner": self.winner,
        }

    def from_snapshot(self, snap: dict):
        self.scores = snap["scores"].copy()
        self.current_round = snap["current_round"]
        self.current_player_idx = snap["current_player_idx"]
        self.round_history = list(snap.get("round_history", []))
        self.winner = snap.get("winner")

    def get_leaderboard(self) -> List[Tuple[str, int]]:
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=True)


# ===== BERMUDA =====
class BermudaGame:
    """Bermuda Triangle: Each round has a different target. Miss = 0 for the round."""

    BERMUDA_TARGETS = [12, 13, 14, "doubles", 15, 16, "triples", 17, 18, 19, 20, "bull"]

    def __init__(self, players: List[str]):
        self.players = players
        self.scores = {p: 0 for p in players}
        self.current_round = 0
        self.current_player_idx = 0
        self.winner = None

    def get_current_target(self):
        return self.BERMUDA_TARGETS[self.current_round]

    def record_throw(self, darts: List[int]) -> str:
        valid, error = validate_dart_throw(darts)
        if not valid:
            return f"Invalid throw: {error}"

        player = self.players[self.current_player_idx]
        target = self.get_current_target()
        score = 0

        for dart in darts:
            if target == "doubles":
                if dart <= 40 and dart % 2 == 0 and dart > 0:
                    score += dart
            elif target == "triples":
                if dart <= 60 and dart % 3 == 0 and dart > 0:
                    score += dart
            elif target == "bull":
                if dart == 25 or dart == 50:
                    score += dart
            else:
                t = int(target)
                if dart == t:
                    score += t
                elif dart == t * 2:
                    score += t * 2
                elif dart == t * 3:
                    score += t * 3

        self.scores[player] += score

        msg = f"{player} — Target: {target} | {darts} = +{score}pts (Total: {self.scores[player]})"

        # Advance
        self.current_player_idx += 1
        if self.current_player_idx >= len(self.players):
            self.current_player_idx = 0
            self.current_round += 1

        if self.current_round >= len(self.BERMUDA_TARGETS):
            self.winner = max(self.scores, key=self.scores.get)
            msg += f" | 🏆 {self.winner} wins with {self.scores[self.winner]}!"

        return msg

    def to_snapshot(self) -> dict:
        return {
            "scores": self.scores.copy(),
            "current_round": self.current_round,
            "current_player_idx": self.current_player_idx,
            "winner": self.winner,
        }

    def from_snapshot(self, snap: dict):
        self.scores = snap["scores"].copy()
        self.current_round = snap["current_round"]
        self.current_player_idx = snap["current_player_idx"]
        self.winner = snap.get("winner")

    def get_leaderboard(self) -> List[Tuple[str, int]]:
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=True)


# ===== JDC CHALLENGE =====
class JDCChallenge:
    """Junior Darts Corporation challenge: Hit specific targets in sequence."""

    JDC_TARGETS = [
        ("D1", 2), ("D2", 4), ("D3", 6), ("D4", 8), ("D5", 10),
        ("D6", 12), ("D7", 14), ("D8", 16), ("D9", 18), ("D10", 20),
        ("S20", 20), ("S19", 19), ("S18", 18), ("S17", 17), ("S16", 16),
        ("S15", 15), ("S14", 14), ("S13", 13), ("S12", 12), ("S11", 11),
        ("S10", 10), ("S9", 9), ("S8", 8), ("S7", 7), ("S6", 6),
        ("S5", 5), ("S4", 4), ("S3", 3), ("S2", 2), ("S1", 1),
    ]

    def __init__(self, players: List[str]):
        self.players = players
        self.scores = {p: 0 for p in players}
        self.current_target_idx = 0
        self.current_player_idx = 0
        self.winner = None

    def get_current_target(self):
        return self.JDC_TARGETS[self.current_target_idx]

    def record_throw(self, darts: List[int]) -> str:
        valid, error = validate_dart_throw(darts)
        if not valid:
            return f"Invalid throw: {error}"

        player = self.players[self.current_player_idx]
        target_name, target_value = self.get_current_target()
        score = 0

        for dart in darts:
            # FIXED: Must hit the exact target value (segment), not just score match
            # D1 = 2 points, but S2 also = 2 points. We need to distinguish.
            # For now, we check exact score match which is the best we can do
            # without segment metadata. The UI should pass segment info.
            if dart == target_value:
                score += target_value

        self.scores[player] += score

        msg = f"{player} — {target_name} | {darts} = +{score} (Total: {self.scores[player]})"

        self.current_player_idx += 1
        if self.current_player_idx >= len(self.players):
            self.current_player_idx = 0
            self.current_target_idx += 1

        if self.current_target_idx >= len(self.JDC_TARGETS):
            self.winner = max(self.scores, key=self.scores.get)
            msg += f" | 🏆 {self.winner} wins!"

        return msg

    def to_snapshot(self) -> dict:
        return {
            "scores": self.scores.copy(),
            "current_target_idx": self.current_target_idx,
            "current_player_idx": self.current_player_idx,
            "winner": self.winner,
        }

    def from_snapshot(self, snap: dict):
        self.scores = snap["scores"].copy()
        self.current_target_idx = snap["current_target_idx"]
        self.current_player_idx = snap["current_player_idx"]
        self.winner = snap.get("winner")

    def get_leaderboard(self) -> List[Tuple[str, int]]:
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=True)


# ===== 41-60 PRACTICE =====
class Practice4160:
    """Hit 41 through 60 in sequence. Score = numbers hit."""

    def __init__(self, players: List[str]):
        self.players = players
        self.scores = {p: 0 for p in players}
        self.targets = list(range(41, 61))
        self.current_target_idx = {p: 0 for p in players}
        self.current_player_idx = 0
        self.winner = None

    def record_throw(self, darts: List[int]) -> str:
        valid, error = validate_dart_throw(darts)
        if not valid:
            return f"Invalid throw: {error}"

        player = self.players[self.current_player_idx]
        idx = self.current_target_idx[player]

        if idx >= len(self.targets):
            return f"{player}: Already finished!"

        target = self.targets[idx]
        hit = False

        for dart in darts:
            if dart == target:
                self.scores[player] += target
                self.current_target_idx[player] += 1
                hit = True
                break

        if hit:
            next_t = self.targets[self.current_target_idx[player]] if self.current_target_idx[player] < len(self.targets) else "DONE"
            msg = f"{player}: HIT {target}! Next: {next_t}"
        else:
            msg = f"{player}: Missed {target}"

        # Check completion
        if self.current_target_idx[player] >= len(self.targets):
            if not self.winner:
                self.winner = player
            msg += f" | COMPLETE! Score: {self.scores[player]}"

        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        return msg

    def to_snapshot(self) -> dict:
        return {
            "scores": self.scores.copy(),
            "current_target_idx": dict(self.current_target_idx),
            "current_player_idx": self.current_player_idx,
            "winner": self.winner,
        }

    def from_snapshot(self, snap: dict):
        self.scores = snap["scores"].copy()
        self.current_target_idx = snap["current_target_idx"].copy()
        self.current_player_idx = snap["current_player_idx"]
        self.winner = snap.get("winner")

    def get_leaderboard(self) -> List[Tuple[str, int]]:
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=True)


# ===== TACTIC CRICKET =====
class TacticCricket:
    """Tactic Cricket: Cricket with strategic power-play rounds."""

    def __init__(self, players: List[str]):
        self.players = players
        self.targets = [15, 16, 17, 18, 19, 20, 25]
        self.marks = {p: {t: 0 for t in self.targets} for p in players}
        self.points = {p: 0 for p in players}
        self.closed = {t: None for t in self.targets}
        self.current_player_idx = 0
        self.power_play = {p: 1 for p in players}
        self.power_plays_remaining = {p: 2 for p in players}
        self.winner = None
        self.round_num = 1

    def activate_power_play(self, player: str) -> str:
        if self.power_plays_remaining[player] > 0:
            self.power_play[player] = 2
            self.power_plays_remaining[player] -= 1
            return f"⚡ {player} activates POWER PLAY! (2x points this turn, {self.power_plays_remaining[player]} left)"
        return f"{player}: No power plays remaining!"

    def record_throw(self, darts: List[int]) -> str:
        valid, error = validate_dart_throw(darts)
        if not valid:
            return f"Invalid throw: {error}"

        player = self.players[self.current_player_idx]
        multiplier = self.power_play[player]
        msgs = []

        for dart in darts:
            base, mult = parse_dart_value(dart)
            if base not in self.targets:
                continue

            new_marks = self.marks[player][base] + mult
            self.marks[player][base] = min(new_marks, 3)

            if new_marks >= 3 and self.closed[base] is None:
                self.closed[base] = player
                msgs.append(f"{base} CLOSED by {player}")

            excess = new_marks - 3
            if excess > 0:
                for opp in self.players:
                    if opp == player:
                        continue
                    if self.marks[opp][base] < 3:
                        pts = base * excess * multiplier
                        self.points[player] += pts
                        if multiplier > 1:
                            msgs.append(f"⚡ {base}x{excess} = +{pts}pts (POWER PLAY!)")
                        else:
                            msgs.append(f"{base}x{excess} = +{pts}pts")

        # Reset power play
        self.power_play[player] = 1

        # Check winner
        if all(self.marks[player][t] >= 3 for t in self.targets):
            if self.points[player] >= max(self.points.values()):
                self.winner = player
                msgs.append(f"🏆 {player} wins Tactic Cricket!")

        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        if self.current_player_idx == 0:
            self.round_num += 1

        return " | ".join(msgs) if msgs else f"{player}: No scoring marks"

    def to_snapshot(self) -> dict:
        return {
            "marks": {p: m.copy() for p, m in self.marks.items()},
            "points": self.points.copy(),
            "closed": self.closed.copy(),
            "current_player_idx": self.current_player_idx,
            "power_play": self.power_play.copy(),
            "power_plays_remaining": self.power_plays_remaining.copy(),
            "winner": self.winner,
            "round_num": self.round_num,
        }

    def from_snapshot(self, snap: dict):
        self.marks = {p: m.copy() for p, m in snap["marks"].items()}
        self.points = snap["points"].copy()
        self.closed = snap["closed"].copy()
        self.current_player_idx = snap["current_player_idx"]
        self.power_play = snap["power_play"].copy()
        self.power_plays_remaining = snap["power_plays_remaining"].copy()
        self.winner = snap.get("winner")
        self.round_num = snap.get("round_num", 1)

    def get_leaderboard(self) -> List[Tuple[str, int]]:
        return sorted(self.points.items(), key=lambda x: x[1], reverse=True)


# ===== RANDOM CRICKET =====
class RandomCricket:
    """Cricket but targets are randomized each game."""

    def __init__(self, players: List[str], num_targets: int = 7):
        self.players = players
        all_numbers = list(range(1, 21)) + [25]
        self.targets = sorted(random.sample(all_numbers, min(num_targets, len(all_numbers))))
        self.marks = {p: {t: 0 for t in self.targets} for p in players}
        self.points = {p: 0 for p in players}
        self.closed = {t: None for t in self.targets}
        self.current_player_idx = 0
        self.winner = None

    def record_throw(self, darts: List[int]) -> str:
        valid, error = validate_dart_throw(darts)
        if not valid:
            return f"Invalid throw: {error}"

        player = self.players[self.current_player_idx]
        msgs = []

        for dart in darts:
            base, mult = parse_dart_value(dart)
            if base not in self.targets:
                continue
            new_marks = self.marks[player][base] + mult
            self.marks[player][base] = min(new_marks, 3)

            if new_marks >= 3 and self.closed[base] is None:
                self.closed[base] = player
                msgs.append(f"{base} CLOSED")

            excess = new_marks - 3
            if excess > 0:
                for opp in self.players:
                    if opp != player and self.marks[opp][base] < 3:
                        self.points[player] += base * excess
                        msgs.append(f"+{base * excess}pts")

            if all(self.marks[player][t] >= 3 for t in self.targets):
                if self.points[player] >= max(self.points.values()):
                    self.winner = player
                    msgs.append(f"🏆 {player} wins!")

        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        return " | ".join(msgs) if msgs else f"{player}: No marks"

    def to_snapshot(self) -> dict:
        return {
            "targets": list(self.targets),
            "marks": {p: m.copy() for p, m in self.marks.items()},
            "points": self.points.copy(),
            "closed": self.closed.copy(),
            "current_player_idx": self.current_player_idx,
            "winner": self.winner,
        }

    def from_snapshot(self, snap: dict):
        self.targets = list(snap["targets"])
        self.marks = {p: m.copy() for p, m in snap["marks"].items()}
        self.points = snap["points"].copy()
        self.closed = snap["closed"].copy()
        self.current_player_idx = snap["current_player_idx"]
        self.winner = snap.get("winner")

    def get_leaderboard(self) -> List[Tuple[str, int]]:
        return sorted(self.points.items(), key=lambda x: x[1], reverse=True)


# ===== HAMMER CRICKET (Party) =====
class HammerCricket:
    """Party variant: Last person to close a number gets 'hammered' (loses points)."""

    def __init__(self, players: List[str]):
        self.players = players
        self.targets = [15, 16, 17, 18, 19, 20, 25]
        self.marks = {p: {t: 0 for t in self.targets} for p in players}
        self.points = {p: 0 for p in players}
        self.closed_by = {t: [] for t in self.targets}
        self.current_player_idx = 0
        self.winner = None

    def record_throw(self, darts: List[int]) -> str:
        valid, error = validate_dart_throw(darts)
        if not valid:
            return f"Invalid throw: {error}"

        player = self.players[self.current_player_idx]
        msgs = []

        for dart in darts:
            base, mult = parse_dart_value(dart)
            if base not in self.targets:
                continue

            new_marks = self.marks[player][base] + mult
            self.marks[player][base] = min(new_marks, 3)

            # Check if just closed
            if new_marks >= 3 and player not in self.closed_by[base]:
                self.closed_by[base].append(player)
                msgs.append(f"{player} closed {base}")

                # If this player is LAST to close, they get 'hammered'
                if len(self.closed_by[base]) == len(self.players):
                    penalty = base * 3
                    self.points[player] -= penalty
                    msgs.append(f"🔨 HAMMERED! Last to close {base}: -{penalty}pts!")
                # If first to close, bonus
                elif len(self.closed_by[base]) == 1:
                    bonus = base
                    self.points[player] += bonus
                    msgs.append(f"🥇 First to close {base}: +{bonus}pts!")

        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        return " | ".join(msgs) if msgs else f"{player}: No marks"

    def to_snapshot(self) -> dict:
        return {
            "marks": {p: m.copy() for p, m in self.marks.items()},
            "points": self.points.copy(),
            "closed_by": {t: list(v) for t, v in self.closed_by.items()},
            "current_player_idx": self.current_player_idx,
            "winner": self.winner,
        }

    def from_snapshot(self, snap: dict):
        self.marks = {p: m.copy() for p, m in snap["marks"].items()}
        self.points = snap["points"].copy()
        self.closed_by = {t: list(v) for t, v in snap["closed_by"].items()}
        self.current_player_idx = snap["current_player_idx"]
        self.winner = snap.get("winner")

    def get_leaderboard(self) -> List[Tuple[str, int]]:
        return sorted(self.points.items(), key=lambda x: x[1], reverse=True)


# ===== ELIMINATOR =====
class EliminatorGame:
    """Eliminator: If you finish a leg last, you're out. Last player standing wins."""

    def __init__(self, players: List[str], starting_score: int = 501):
        self.all_players = players.copy()
        self.active_players = players.copy()
        self.starting_score = starting_score
        self.scores = {p: starting_score for p in players}
        self.eliminated = []
        self.current_player_idx = 0
        self.winner = None
        self.leg_in_progress = True

    def record_throw(self, player: str, darts: List[int]) -> str:
        valid, error = validate_dart_throw(darts)
        if not valid:
            return f"Invalid throw: {error}"

        if player not in self.active_players:
            return f"{player} is already eliminated!"

        total = sum(darts)
        new_score = self.scores[player] - total

        msg = f"{player}: {total} → {max(0, new_score)}"

        # Check for bust
        if new_score < 0 or new_score == 1:
            msg += " | BUST!"
            return msg

        # Check for checkout - must be double
        if new_score == 0:
            last_dart = darts[-1] if darts else 0
            is_double = (last_dart == 50) or (last_dart % 2 == 0 and 2 <= last_dart <= 40)
            if is_double:
                self.scores[player] = 0
                msg += " | CHECKOUT!"
            else:
                msg += " | BUST! Must finish on a double."
            return msg

        self.scores[player] = new_score
        return msg

    def end_round(self) -> str:
        """End the round — eliminate player(s) with highest remaining score."""
        if len(self.active_players) <= 1:
            self.winner = self.active_players[0] if self.active_players else None
            return f"🏆 {self.winner} wins Eliminator!"

        # Find player(s) with highest remaining score (who haven't checked out)
        active_scores = {p: self.scores[p] for p in self.active_players if self.scores[p] > 0}
        if not active_scores:
            # Everyone checked out, no elimination
            for p in self.active_players:
                self.scores[p] = self.starting_score
            return "Everyone checked out! Next round..."

        max_score = max(active_scores.values())
        to_eliminate = [p for p, s in active_scores.items() if s == max_score]

        for p in to_eliminate:
            if len(self.active_players) > 1:
                self.active_players.remove(p)
                self.eliminated.append(p)

        # Reset scores for next round
        for p in self.active_players:
            self.scores[p] = self.starting_score

        if len(self.active_players) == 1:
            self.winner = self.active_players[0]
            return f"🔨 {', '.join(to_eliminate)} eliminated! | 🏆 {self.winner} wins!"

        return f"🔨 {', '.join(to_eliminate)} eliminated! | Remaining: {', '.join(self.active_players)}"

    def to_snapshot(self) -> dict:
        return {
            "active_players": list(self.active_players),
            "eliminated": list(self.eliminated),
            "scores": self.scores.copy(),
            "current_player_idx": self.current_player_idx,
            "winner": self.winner,
        }

    def from_snapshot(self, snap: dict):
        self.active_players = list(snap["active_players"])
        self.eliminated = list(snap["eliminated"])
        self.scores = snap["scores"].copy()
        self.current_player_idx = snap["current_player_idx"]
        self.winner = snap.get("winner")

    def get_leaderboard(self) -> List[Tuple[str, int]]:
        # In eliminator, fewer remaining score is better (checked out = 0)
        return sorted(
            [(p, self.scores[p]) for p in self.active_players],
            key=lambda x: x[1]
        )


# ===== ROADRUNNER =====
class RoadrunnerGame:
    """Roadrunner: Stay ahead of the pro for 30 rounds. If caught, game over."""

    def __init__(self, player: str, pro_level: int = 8):
        self.player = player
        self.pro_score = 0
        self.player_score = 0
        self.round_num = 1
        self.max_rounds = 30
        self.pro_level = pro_level
        self.winner = None
        self.caught = False
        self._pro_won = False

    def get_pro_throw(self) -> int:
        """Generate pro throw based on level."""
        avg_map = {1: 20, 2: 30, 3: 35, 4: 40, 5: 45, 6: 50, 7: 55, 8: 60, 9: 65, 10: 70}
        base = avg_map.get(self.pro_level, 50)
        # Use truncated normal to avoid negative or unrealistic values
        import random
        val = random.gauss(base, base * 0.15)
        return max(5, min(60, int(val)))

    def play_round(self, player_darts: List[int]) -> str:
        valid, error = validate_dart_throw(player_darts)
        if not valid:
            return f"Invalid throw: {error}"

        if self.round_num > self.max_rounds or self.caught:
            return "Game already over!"

        player_total = sum(player_darts)
        pro_total = self.get_pro_throw()

        self.player_score += player_total
        self.pro_score += pro_total

        gap = self.player_score - self.pro_score

        msg = f"Round {self.round_num}/{self.max_rounds}: You {player_total} vs Pro {pro_total} | Gap: {gap:+d}"

        if gap <= 0:
            self.caught = True
            self._pro_won = True
            self.winner = None  # No player winner
            msg += "
🔴 CAUGHT! The Pro caught you! Game Over!"
        elif self.round_num >= self.max_rounds:
            self.winner = self.player
            msg += f"
🏆 You survived all {self.max_rounds} rounds! You win!"
        else:
            rounds_left = self.max_rounds - self.round_num
            msg += f" | {rounds_left} rounds to go..."

        self.round_num += 1
        return msg

    def to_snapshot(self) -> dict:
        return {
            "player_score": self.player_score,
            "pro_score": self.pro_score,
            "round_num": self.round_num,
            "winner": self.winner,
            "caught": self.caught,
            "pro_won": self._pro_won,
        }

    def from_snapshot(self, snap: dict):
        self.player_score = snap["player_score"]
        self.pro_score = snap["pro_score"]
        self.round_num = snap["round_num"]
        self.winner = snap.get("winner")
        self.caught = snap.get("caught", False)
        self._pro_won = snap.get("pro_won", False)

    def get_leaderboard(self) -> List[Tuple[str, int]]:
        if self._pro_won:
            return [("Pro", self.pro_score), (self.player, self.player_score)]
        return [(self.player, self.player_score), ("Pro", self.pro_score)]


# ===== ESCALATOR 20 =====
class Escalator20Game:
    """Escalator 20: Level up through 20 levels. Handicap changes each level."""

    LEVEL_CONFIGS = [
        {"level": 1, "name": "Beginner", "player_start": 301, "bot_start": 501, "bot_level": 1},
        {"level": 2, "name": "Easy", "player_start": 301, "bot_start": 501, "bot_level": 2},
        {"level": 3, "name": "Getting There", "player_start": 401, "bot_start": 501, "bot_level": 3},
        {"level": 4, "name": "Intermediate", "player_start": 401, "bot_start": 501, "bot_level": 4},
        {"level": 5, "name": "Standard", "player_start": 501, "bot_start": 501, "bot_level": 5},
        {"level": 6, "name": "Challenge", "player_start": 501, "bot_start": 501, "bot_level": 6},
        {"level": 7, "name": "Hard", "player_start": 501, "bot_start": 401, "bot_level": 7},
        {"level": 8, "name": "Very Hard", "player_start": 501, "bot_start": 301, "bot_level": 8},
        {"level": 9, "name": "Expert", "player_start": 501, "bot_start": 301, "bot_level": 9},
        {"level": 10, "name": "Pro", "player_start": 501, "bot_start": 301, "bot_level": 10},
        {"level": 11, "name": "Elite", "player_start": 501, "bot_start": 201, "bot_level": 10},
        {"level": 12, "name": "Master", "player_start": 501, "bot_start": 201, "bot_level": 11},
        {"level": 13, "name": "Grandmaster", "player_start": 501, "bot_start": 101, "bot_level": 11},
        {"level": 14, "name": "Legend", "player_start": 501, "bot_start": 101, "bot_level": 12},
        {"level": 15, "name": "GOAT", "player_start": 501, "bot_start": 51, "bot_level": 12},
        {"level": 16, "name": "Superhuman", "player_start": 501, "bot_start": 51, "bot_level": 12},
        {"level": 17, "name": "Godlike", "player_start": 501, "bot_start": 41, "bot_level": 12},
        {"level": 18, "name": "Immortal", "player_start": 501, "bot_start": 41, "bot_level": 12},
        {"level": 19, "name": "Transcendent", "player_start": 501, "bot_start": 21, "bot_level": 12},
        {"level": 20, "name": "Perfect", "player_start": 501, "bot_start": 21, "bot_level": 12},
    ]

    def __init__(self, player: str):
        self.player = player
        self.current_level_idx = 0
        self.level_wins = 0
        self.level_losses = 0
        self.overall_wins = 0
        self.winner = None

    def get_current_config(self):
        if self.current_level_idx < len(self.LEVEL_CONFIGS):
            return self.LEVEL_CONFIGS[self.current_level_idx]
        return self.LEVEL_CONFIGS[-1]

    def win_level(self):
        """Player won this level."""
        self.level_wins += 1
        self.overall_wins += 1
        self.current_level_idx += 1

        if self.current_level_idx >= len(self.LEVEL_CONFIGS):
            self.winner = self.player
            return f"🏆 CONGRATULATIONS! You completed ALL 20 levels of Escalator! You are a DARTS LEGEND!"

        next_config = self.get_current_config()
        return f"Level complete! ⬆️ Now at Level {next_config['level']}: {next_config['name']} | You start at {next_config['player_start']}, Bot at {next_config['bot_start']}"

    def lose_level(self):
        """Player lost this level."""
        self.level_losses += 1
        return f"Level failed. Try again! (Wins: {self.level_wins}, Losses: {self.level_losses})"

    def to_snapshot(self) -> dict:
        return {
            "current_level_idx": self.current_level_idx,
            "level_wins": self.level_wins,
            "level_losses": self.level_losses,
            "overall_wins": self.overall_wins,
            "winner": self.winner,
        }

    def from_snapshot(self, snap: dict):
        self.current_level_idx = snap["current_level_idx"]
        self.level_wins = snap["level_wins"]
        self.level_losses = snap["level_losses"]
        self.overall_wins = snap["overall_wins"]
        self.winner = snap.get("winner")

    def get_leaderboard(self) -> List[Tuple[str, int]]:
        return [(self.player, self.current_level_idx)]


# ===== CRICKET COUNT UP =====
class CricketCountUp:
    """Cricket-style Count Up: Score on cricket numbers only."""

    def __init__(self, players: List[str], rounds: int = 8):
        self.players = players
        self.targets = [15, 16, 17, 18, 19, 20, 25]
        self.scores = {p: 0 for p in players}
        self.total_rounds = rounds
        self.current_round = 1
        self.current_player_idx = 0
        self.winner = None

    def record_throw(self, darts: List[int]) -> str:
        valid, error = validate_dart_throw(darts)
        if not valid:
            return f"Invalid throw: {error}"

        player = self.players[self.current_player_idx]
        score = 0

        for dart in darts:
            base, mult = parse_dart_value(dart)
            if base in self.targets:
                score += base * mult

        self.scores[player] += score

        msg = f"{player} R{self.current_round}: +{score} (Total: {self.scores[player]})"

        self.current_player_idx += 1
        if self.current_player_idx >= len(self.players):
            self.current_player_idx = 0
            self.current_round += 1

        if self.current_round > self.total_rounds:
            self.winner = max(self.scores, key=self.scores.get)
            msg += f" | 🏆 {self.winner} wins with {self.scores[self.winner]}!"

        return msg

    def to_snapshot(self) -> dict:
        return {
            "scores": self.scores.copy(),
            "current_round": self.current_round,
            "current_player_idx": self.current_player_idx,
            "winner": self.winner,
        }

    def from_snapshot(self, snap: dict):
        self.scores = snap["scores"].copy()
        self.current_round = snap["current_round"]
        self.current_player_idx = snap["current_player_idx"]
        self.winner = snap.get("winner")

    def get_leaderboard(self) -> List[Tuple[str, int]]:
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=True)


# ===== CHASE THE DRAGON =====
class ChaseTheDragonGame:
    """
    Chase the Dragon: Hit treble segments from 10-20, then outer bull and bull in order.
    """

    DRAGON_TARGETS = [
        ("T10", 30), ("T11", 33), ("T12", 36), ("T13", 39), ("T14", 42),
        ("T15", 45), ("T16", 48), ("T17", 51), ("T18", 54), ("T19", 57),
        ("T20", 60), ("Outer Bull", 25), ("Bullseye", 50)
    ]

    def __init__(self, players: List[str]):
        self.players = players
        self.current_target_idx = {p: 0 for p in players}
        self.current_player_idx = 0
        self.winner = None
        self.history = []

    def get_current_target(self, player: str):
        idx = self.current_target_idx[player]
        if idx < len(self.DRAGON_TARGETS):
            return self.DRAGON_TARGETS[idx]
        return None, None

    def record_throw(self, darts: List[int]) -> str:
        valid, error = validate_dart_throw(darts)
        if not valid:
            return f"Invalid throw: {error}"

        player = self.players[self.current_player_idx]
        idx = self.current_target_idx[player]

        if idx >= len(self.DRAGON_TARGETS):
            return f"{player}: Already slayed the dragon!"

        msgs = []
        targets_hit_this_visit = 0

        for dart in darts:
            target_name, target_value = self.get_current_target(player)
            if not target_name:
                break

            if dart == target_value:
                self.current_target_idx[player] += 1
                targets_hit_this_visit += 1
                msgs.append(f"🎯 HIT {target_name}!")

                if self.current_target_idx[player] >= len(self.DRAGON_TARGETS):
                    if not self.winner:
                        self.winner = player
                    msgs.append(f"🐉 DRAGON SLAYED! {player} wins!")
                    break
            # If missed, we keep trying the same target with remaining darts

        if not msgs:
            target_name, _ = self.get_current_target(player)
            msgs.append(f"❌ Missed {target_name}")

        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)

        return " | ".join(msgs)

    def to_snapshot(self) -> dict:
        return {
            "current_target_idx": dict(self.current_target_idx),
            "current_player_idx": self.current_player_idx,
            "winner": self.winner,
        }

    def from_snapshot(self, snap: dict):
        self.current_target_idx = snap["current_target_idx"].copy()
        self.current_player_idx = snap["current_player_idx"]
        self.winner = snap.get("winner")

    def get_leaderboard(self) -> List[Tuple[str, int]]:
        return sorted(
            self.current_target_idx.items(),
            key=lambda x: x[1],
            reverse=True
        )
