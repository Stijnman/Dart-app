
"""
SmartBot Auto Difficulty Scaling for Dart Game Pro v2.4
Completes Feature #21: Difficulty Scaling — Bots automatically adjust based on player performance.

Extends the existing SmartBot in core/systems.py and integrates with DartBot (core/dartbot.py) + engine.

Logic:
- After each leg/visit or at checkout, analyze recent player performance (avg, consistency, 180 rate, checkout success).
- Dynamically suggest or auto-set bot level (1-12).
- Can be "adaptive during match" or "post-leg adjustment".
- Includes pressure-aware modifiers (existing in DartBot) + new performance-based scaling.

This makes the bot a true adaptive opponent/coach.
"""

from typing import Dict, List, Optional, Any
import numpy as np

# Assume these are imported from your existing modules
# from core.dartbot import DARTBOT_LEVELS, DartBot
# from core.systems import SmartBot  (the analyzer)

DARTBOT_LEVELS = {
    1: {"name": "Beginner", "avg_throw": 25, "checkout_pct": 0.15, "triple_pct": 0.05, "double_pct": 0.20},
    2: {"name": "Novice", "avg_throw": 35, "checkout_pct": 0.25, "triple_pct": 0.10, "double_pct": 0.25},
    # ... up to level 12 "Elite Pro / World Champion" ~105 avg, high consistency
    12: {"name": "Elite Pro", "avg_throw": 105, "checkout_pct": 0.85, "triple_pct": 0.55, "double_pct": 0.70, "consistency": 0.95},
}

class AdaptiveDifficultyScaler:
    """
    Standalone scaler you can instantiate in engine.py or attach to SmartBot.
    Call after significant events (end of leg, after 9 darts, or on bust/checkout).
    """

    def __init__(self, current_bot_level: int = 6, adaptation_rate: float = 0.15):
        self.current_level = max(1, min(12, current_bot_level))
        self.adaptation_rate = adaptation_rate  # How aggressively to change (0.1-0.3 recommended)
        self.performance_history: List[Dict] = []  # Store recent player metrics
        self.last_adjustment_reason = ""

    def analyze_player_performance(self, recent_throws: List[int], checkouts_attempted: int = 0, checkouts_made: int = 0) -> Dict[str, float]:
        """Compute key metrics from recent throws (last 9-30 darts recommended)."""
        if not recent_throws:
            return {"avg": 40.0, "consistency": 0.5, "t80_rate": 0.0, "checkout_rate": 0.3}

        arr = np.array(recent_throws)
        avg = float(np.mean(arr))
        std = float(np.std(arr))
        consistency = max(0.1, 1.0 - (std / max(avg, 1)))  # lower std relative to mean = higher consistency

        t80_count = sum(1 for s in recent_throws if s >= 80)
        t80_rate = t80_count / len(recent_throws)

        checkout_rate = (checkouts_made / max(checkouts_attempted, 1)) if checkouts_attempted > 0 else 0.4

        return {
            "avg": round(avg, 1),
            "consistency": round(consistency, 2),
            "t80_rate": round(t80_rate, 2),
            "checkout_rate": round(checkout_rate, 2),
            "sample_size": len(recent_throws)
        }

    def calculate_target_level(self, metrics: Dict[str, float]) -> int:
        """Map metrics to ideal bot level 1-12."""
        avg = metrics["avg"]
        t80 = metrics["t80_rate"]
        checkout = metrics["checkout_rate"]
        cons = metrics["consistency"]

        # Simple weighted scoring (tune these weights)
        score = 0
        score += min(12, max(1, (avg - 20) / 7 )) * 0.45          # avg dominant
        score += min(5, t80 * 20) * 0.25                           # 180s / high scores
        score += min(4, checkout * 8) * 0.20                       # finishing ability
        score += cons * 1.5 * 0.10                                 # consistency

        target = int(round(np.clip(score, 1, 12)))
        return target

    def adjust_difficulty(self, recent_throws: List[int], checkouts_made: int = 0, checkouts_attempted: int = 0, 
                          force_adjust: bool = False) -> Dict[str, Any]:
        """
        Main method to call from engine after a leg or visit.
        Returns adjustment info + new recommended level.
        Set force_adjust=True for immediate post-leg change.
        """
        metrics = self.analyze_player_performance(recent_throws, checkouts_attempted, checkouts_made)
        target_level = self.calculate_target_level(metrics)

        old_level = self.current_level
        delta = target_level - old_level

        # Apply adaptation rate (smooth change, not jump)
        if abs(delta) >= 1 or force_adjust:
            adjustment = int(round(delta * self.adaptation_rate))
            if adjustment == 0 and delta != 0:
                adjustment = 1 if delta > 0 else -1
            new_level = max(1, min(12, old_level + adjustment))
        else:
            new_level = old_level
            adjustment = 0

        self.current_level = new_level
        self.performance_history.append(metrics)
        if len(self.performance_history) > 10:
            self.performance_history.pop(0)

        reason = self._generate_reason(metrics, old_level, new_level, adjustment)

        return {
            "old_level": old_level,
            "new_level": new_level,
            "adjustment": adjustment,
            "metrics": metrics,
            "reason": reason,
            "bot_name": DARTBOT_LEVELS.get(new_level, {}).get("name", f"Level {new_level}"),
            "message_for_player": f"Bot adjusted to Level {new_level} ({DARTBOT_LEVELS.get(new_level,{}).get('name')}). {reason}"
        }

    def _generate_reason(self, metrics: Dict, old: int, new: int, adj: int) -> str:
        if adj == 0:
            return "Performance stable — keeping current challenge level."
        direction = "increased" if adj > 0 else "decreased"
        parts = []
        if metrics["avg"] > 70:
            parts.append("strong scoring")
        if metrics["t80_rate"] > 0.15:
            parts.append("frequent high scores / 180s")
        if metrics["checkout_rate"] > 0.6:
            parts.append("excellent finishing")
        if metrics["consistency"] > 0.75:
            parts.append("high consistency")

        perf_desc = ", ".join(parts) if parts else "solid overall play"
        return f"Bot {direction} because of your {perf_desc} (avg {metrics['avg']}, consistency {metrics['consistency']})."

    def get_current_bot_config(self) -> Dict:
        """Get the full config dict for current level to pass to DartBot constructor."""
        return DARTBOT_LEVELS.get(self.current_level, DARTBOT_LEVELS[6])


# Integration example in engine.py or game loop (pseudo):
"""
# After a player finishes a leg or after 9 darts:
if st.session_state.get('bot_enabled') and st.session_state.get('adaptive_bot'):
    scaler = st.session_state.get('difficulty_scaler') or AdaptiveDifficultyScaler(current_bot_level=6)
    
    recent_scores = [t['score'] for t in game_state['recent_throws'][-12:]]  # last 4 visits
    checkouts_made = game_state.get('player_checkouts_made', 0)
    checkouts_attempted = game_state.get('player_checkouts_attempted', 1)
    
    adjustment = scaler.adjust_difficulty(recent_scores, checkouts_made, checkouts_attempted, force_adjust=True)
    
    if adjustment['adjustment'] != 0:
        st.toast(adjustment['message_for_player'], icon="🤖")
        # Update the actual DartBot instance difficulty
        current_bot = st.session_state.engine.bot
        current_bot.update_level(adjustment['new_level'])  # Add this method to DartBot if missing
        st.session_state.difficulty_scaler = scaler
"""

# Bonus: You can also expose this in Coaching Mode or as a "Bot Strength" slider with "Adaptive" toggle.
