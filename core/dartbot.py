"""
Realistic DartBot AI — Unpredictable, human-like throwing with variance.
Refactored: Fixed mid-visit checkout recalculation, added dart validation, improved realism.
"""

import random
from typing import List, Tuple
from .constants import DARTBOT_LEVELS, ADJACENT_MAP
from .checkout import get_best_checkout, parse_checkout_path
from .utils import is_valid_dart_score


class DartBot:
    """
    Adaptive DartBot with realistic variance.

    Key improvements:
    1. Recalculates checkout path after each dart in a visit
    2. Validates all generated dart scores
    3. Improved pressure simulation for checkouts
    4. Realistic triple/double hit rates with variance
    """

    def __init__(self, level: int = 5):
        self.level = max(1, min(12, level))
        config = DARTBOT_LEVELS.get(self.level, DARTBOT_LEVELS[5])
        self.name = config["name"]
        self.avg_throw = config["avg_throw"]
        self.checkout_pct = config["checkout_pct"]
        self.triple_pct = config["triple_pct"]
        self.double_pct = config["double_pct"]
        self._consistency = 0.7 + (self.level * 0.025)

    def get_throw_x01(self, remaining: int) -> List[int]:
        """Generate a 3-dart throw for X01. Recalculates checkout path after each dart."""
        darts = []
        current_remaining = remaining

        for dart_num in range(3):
            if current_remaining <= 0:
                darts.append(0)
                continue

            dart = self._throw_dart_x01(current_remaining, dart_num, darts)

            # Validate generated dart score
            if not is_valid_dart_score(dart):
                dart = self._safe_fallback_throw()

            darts.append(dart)
            current_remaining -= dart

            # Check if we won
            if current_remaining == 0:
                break

        # Fill remaining darts with 0
        while len(darts) < 3:
            darts.append(0)

        return darts[:3]

    def _throw_dart_x01(self, remaining: int, dart_num: int, previous_darts: List[int]) -> int:
        """Throw a single dart in X01 context with updated remaining score."""

        # CHECKOUT ATTEMPTS
        if remaining <= 170:
            checkout = get_best_checkout(remaining)
            if checkout:
                return self._attempt_checkout(remaining, checkout, dart_num)

        # SETUP SHOTS (if we can't checkout this visit)
        if remaining > 50:
            return self._scoring_throw()

        # We're in finish range but not on a checkout
        if remaining <= 50:
            return self._finish_throw(remaining)

        return self._scoring_throw()

    def _attempt_checkout(self, remaining: int, checkout_path: str, dart_num: int) -> int:
        """Attempt a checkout with realistic success probability."""
        segments = parse_checkout_path(checkout_path)
        if dart_num >= len(segments):
            return 0

        mult, val = segments[dart_num]

        # Apply pressure modifier for checkouts
        pressure = 1.0
        if remaining <= 40:
            pressure = 1.3
        elif remaining <= 100:
            pressure = 1.15
        elif remaining >= 150:
            pressure = 0.9

        success_chance = self.checkout_pct * pressure
        success_chance += random.uniform(-0.1, 0.05)
        success_chance = max(0.02, min(0.98, success_chance))

        if random.random() < success_chance:
            # Hit the intended target
            if mult == "T":
                return val * 3
            elif mult == "D":
                return val * 2
            elif mult == "B":
                return 50  # Inner bull
            else:
                return val
        else:
            return self._near_miss(mult, val)

    def _near_miss(self, intended_mult: str, intended_val: int) -> int:
        """Generate a realistic near-miss score."""
        miss_type = random.random()
        adjacent = self._adjacent_number(intended_val)

        if intended_mult == "T":
            if miss_type < 0.4:
                return intended_val  # Single instead of triple
            elif miss_type < 0.65:
                return adjacent * 3  # Adjacent triple
            elif miss_type < 0.85:
                return adjacent  # Adjacent single
            else:
                return random.choice([1, 5, 12, 3])  # Wild miss

        elif intended_mult == "D":
            if miss_type < 0.35:
                return intended_val  # Single instead of double
            elif miss_type < 0.6:
                return adjacent * 2  # Adjacent double
            elif miss_type < 0.8:
                return 0  # Complete miss
            else:
                return adjacent

        elif intended_mult == "B":
            if miss_type < 0.5:
                return 25  # Outer bull instead of inner
            else:
                return random.choice([1, 3, 5, 8, 10])  # Wild miss near bull

        return intended_val

    def _scoring_throw(self) -> int:
        """Regular scoring throw (aiming for T20, T19, T18)."""
        target_roll = random.random()

        if target_roll < 0.7:
            target = 20
        elif target_roll < 0.85:
            target = 19
        elif target_roll < 0.93:
            target = 18
        else:
            target = random.choice([17, 16, 14, 12])

        if random.random() < self.triple_pct:
            return target * 3
        elif random.random() < self.double_pct:
            return target * 2
        else:
            if random.random() < 0.3:
                return self._adjacent_number(target)
            return target

    def _finish_throw(self, remaining: int) -> int:
        """Throw when trying to finish."""
        # Try to hit the exact double
        if remaining <= 40 and remaining % 2 == 0:
            double_val = remaining // 2
            if random.random() < self.double_pct * 0.8:
                return remaining
            elif random.random() < 0.5:
                return double_val
            else:
                return 0

        # Try for bull
        if remaining == 50:
            if random.random() < self.double_pct * 0.75:
                return 50
            elif random.random() < 0.5:
                return 25
            return random.choice([0, 1, 5, 3, 10])

        # Setup for next turn
        return self._scoring_throw()

    def _adjacent_number(self, num: int) -> int:
        """Get an adjacent number on the dartboard."""
        adj = ADJACENT_MAP.get(num, [num])
        return random.choice(adj)

    def _safe_fallback_throw(self) -> int:
        """Return a safe valid dart score if something goes wrong."""
        return random.choice([1, 5, 10, 15, 20])

    def get_throw_cricket(self, closed_numbers: set = None) -> List[int]:
        """
        Generate throws for Cricket mode.

        Args:
            closed_numbers: Set of numbers already closed by this bot (to avoid)
        """
        darts = []
        targets = [20, 19, 18, 17, 16, 15, 25]
        weights = [25, 20, 18, 15, 12, 7, 3]

        # If some numbers are closed, shift focus to open ones
        if closed_numbers:
            adjusted_targets = []
            adjusted_weights = []
            for t, w in zip(targets, weights):
                if t not in closed_numbers:
                    adjusted_targets.append(t)
                    adjusted_weights.append(w)
            if adjusted_targets:
                targets = adjusted_targets
                weights = adjusted_weights

        for _ in range(3):
            target = random.choices(targets, weights=weights, k=1)[0]

            if random.random() < self.triple_pct:
                darts.append(target * 3)
            elif random.random() < self.double_pct:
                darts.append(target * 2)
            else:
                darts.append(target)

        return darts

    def get_avg_throw_score(self) -> int:
        """Get expected average throw score for display."""
        return self.avg_throw
