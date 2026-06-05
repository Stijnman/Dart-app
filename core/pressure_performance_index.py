
"""
Pressure Performance Index for Dart Game Pro v2.4
Implements Feature #16: Pressure Performance Index (clutch factor — how players perform when ahead vs behind)

This module tracks and analyzes performance in "pressure situations":
- Ahead in score (leading)
- Behind in score (chasing)
- Close games (within X points)
- High-stakes moments (checkout range, late legs, etc.)

It can be integrated into PatternDetector, CareerMode, or Analytics tab.
Pairs beautifully with the new Advanced Heatmap (shows where pressure affects accuracy).

Usage example in engine or analytics:
    ppi = PressurePerformanceIndex()
    ppi.record_throw(score, was_pressure=True, was_ahead=True)
    stats = ppi.get_clutch_stats()
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import numpy as np
from collections import defaultdict

@dataclass
class PressureThrow:
    score: int
    was_ahead: bool          # Player was leading before this throw
    was_behind: bool         # Player was trailing
    was_close: bool          # Game was within threshold (e.g. 20-30 points)
    in_checkout_range: bool  # Remaining score <= 170 or in finish zone
    leg_number: int
    visit_number: int

class PressurePerformanceIndex:
    """
    Calculates and tracks the Pressure Performance Index (PPI).
    Higher PPI = better performance under pressure (clutch player).
    """

    def __init__(self, close_threshold: int = 25):
        self.close_threshold = close_threshold
        self.throws: List[PressureThrow] = []
        self.history: Dict[str, List[float]] = defaultdict(list)  # e.g. 'ahead', 'behind', 'close'

    def record_throw(self, 
                     score: int, 
                     was_ahead: bool = False, 
                     was_behind: bool = False,
                     was_close: bool = False,
                     in_checkout_range: bool = False,
                     leg_number: int = 1,
                     visit_number: int = 1):
        """
        Call this after every throw (or at end of visit) with context.
        """
        throw = PressureThrow(
            score=score,
            was_ahead=was_ahead,
            was_behind=was_behind,
            was_close=was_close,
            in_checkout_range=in_checkout_range,
            leg_number=leg_number,
            visit_number=visit_number
        )
        self.throws.append(throw)

        # Categorize for quick stats
        if was_ahead:
            self.history['ahead'].append(score)
        if was_behind:
            self.history['behind'].append(score)
        if was_close:
            self.history['close'].append(score)
        if in_checkout_range:
            self.history['checkout'].append(score)

    def get_clutch_stats(self) -> Dict[str, Any]:
        """
        Returns comprehensive pressure/clutch statistics.
        """
        if not self.throws:
            return {"message": "No throws recorded yet"}

        total_throws = len(self.throws)
        ahead_scores = self.history.get('ahead', [])
        behind_scores = self.history.get('behind', [])
        close_scores = self.history.get('close', [])
        checkout_scores = self.history.get('checkout', [])

        def safe_avg(lst):
            return round(np.mean(lst), 2) if lst else 0.0

        def safe_std(lst):
            return round(np.std(lst), 2) if len(lst) > 1 else 0.0

        ahead_avg = safe_avg(ahead_scores)
        behind_avg = safe_avg(behind_scores)
        close_avg = safe_avg(close_scores)
        checkout_avg = safe_avg(checkout_scores)

        overall_avg = safe_avg([t.score for t in self.throws])

        # Clutch Index: How much better (or worse) you perform under pressure
        # Positive = clutch (better when behind or in close games)
        clutch_delta = behind_avg - overall_avg
        close_delta = close_avg - overall_avg

        # Simple PPI score (0-100 scale, higher = more clutch)
        ppi_score = 50  # baseline
        if behind_avg > 0:
            ppi_score += min(25, max(-25, (behind_avg - overall_avg) * 2))
        if close_avg > 0:
            ppi_score += min(15, max(-15, (close_avg - overall_avg) * 1.5))
        ppi_score = max(0, min(100, round(ppi_score)))

        return {
            "total_throws_analyzed": total_throws,
            "overall_average": overall_avg,
            "when_ahead": {
                "average": ahead_avg,
                "std_dev": safe_std(ahead_scores),
                "count": len(ahead_scores)
            },
            "when_behind": {
                "average": behind_avg,
                "std_dev": safe_std(behind_scores),
                "count": len(behind_scores),
                "clutch_delta": round(clutch_delta, 2)
            },
            "when_close": {
                "average": close_avg,
                "std_dev": safe_std(close_scores),
                "count": len(close_scores),
                "close_delta": round(close_delta, 2)
            },
            "in_checkout_range": {
                "average": checkout_avg,
                "count": len(checkout_scores)
            },
            "pressure_performance_index": ppi_score,
            "interpretation": self._interpret_ppi(ppi_score, clutch_delta)
        }

    def _interpret_ppi(self, ppi: float, clutch_delta: float) -> str:
        if ppi >= 75:
            return "Elite clutch performer — thrives under pressure"
        elif ppi >= 60:
            return "Strong under pressure — reliable closer"
        elif ppi >= 45:
            return "Average clutch factor — consistent across situations"
        elif ppi >= 30:
            return "Slightly pressure-sensitive — room to improve in close games"
        else:
            return "Pressure-sensitive — consider mental game training"

    def get_pressure_heatmap_data(self) -> List[Dict]:
        """
        Returns data formatted for the Advanced Heatmap module
        (adds pressure context to throws).
        """
        return [
            {
                "score": t.score,
                "was_pressure": t.was_behind or t.was_close or t.in_checkout_range,
                "context": "behind" if t.was_behind else ("close" if t.was_close else ("checkout" if t.in_checkout_range else "normal"))
            }
            for t in self.throws
        ]

    def reset(self):
        """Clear all recorded data (e.g. new match or season)."""
        self.throws.clear()
        self.history.clear()

# Example integration in your game engine or analytics tab:
"""
# After recording a throw in engine.py or game loop:
if hasattr(st.session_state, 'ppi'):
    ppi = st.session_state.ppi
else:
    ppi = PressurePerformanceIndex()
    st.session_state.ppi = ppi

# Determine context (you already track score, remaining, leg info)
was_ahead = current_player_score > opponent_score
was_behind = current_player_score < opponent_score
was_close = abs(current_player_score - opponent_score) <= 25
in_checkout = remaining_score <= 170

ppi.record_throw(
    score=last_dart_score,
    was_ahead=was_ahead,
    was_behind=was_behind,
    was_close=was_close,
    in_checkout_range=in_checkout,
    leg_number=current_leg,
    visit_number=current_visit
)

# In Analytics tab:
stats = st.session_state.ppi.get_clutch_stats()
st.json(stats)  # or nice cards + charts
"""
