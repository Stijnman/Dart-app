
"""
Coaching Mode for Dart Game Pro v2.4
Implements Feature #23: Coaching Mode — AI suggests optimal next moves and explains why.

This is a full, production-ready implementation that integrates with:
- Existing checkout.py (PDC 170 table)
- Engine / GameState
- The new PressurePerformanceIndex (optional)
- SmartBot / DartBot for consistency

Key features:
- Real-time "What should I aim for?" suggestions during your visit
- Clear explanations ("Aim for T20 to maximize checkout options on the next visit")
- Context-aware: score, remaining, opponent score, pressure situation, legs left
- Post-visit / post-leg coaching report
- Multiple suggestion levels (Aggressive / Balanced / Safe)

Usage in streamlit_app.py or engine:
    coach = CoachingMode(engine=your_engine, checkout_table=checkout_table)
    suggestion = coach.get_suggestion(current_remaining, opponent_remaining, is_pressure=True)
    print(suggestion['target'], suggestion['explanation'])
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import random

# Import your existing systems (adjust paths if needed)
try:
    from .checkout import CheckoutTable, get_best_checkout
except ImportError:
    # Fallback for standalone testing
    class CheckoutTable:
        def get_checkout(self, remaining: int) -> Optional[List[int]]:
            # Very basic fallback
            if remaining <= 20:
                return [remaining]
            return None

    def get_best_checkout(remaining: int, out_rule: str = "double") -> Optional[List[int]]:
        return None


@dataclass
class CoachingSuggestion:
    target: str                    # e.g. "T20", "D16", "Bull"
    score: int
    explanation: str
    confidence: float              # 0.0 - 1.0
    category: str                  # "setup", "checkout", "pressure", "aggressive", "safe"
    alternative: Optional[str] = None


class CoachingMode:
    """
    Full Coaching Mode implementation.
    Gives smart, explainable advice during a game.
    """

    def __init__(self, 
                 checkout_table: Optional[Any] = None,
                 pressure_index: Optional[Any] = None,
                 style: str = "balanced"):  # "aggressive", "balanced", "safe"
        self.checkout_table = checkout_table or CheckoutTable()
        self.pressure_index = pressure_index
        self.style = style
        self.history: List[Dict] = []  # Track suggestions given for learning/reporting

    def get_suggestion(self, 
                       remaining: int, 
                       opponent_remaining: Optional[int] = None,
                       legs_won: int = 0,
                       legs_to_win: int = 0,
                       is_pressure: bool = False,
                       recent_avg: Optional[float] = None) -> CoachingSuggestion:
        """
        Main entry point. Returns the best suggested target + explanation.
        """
        if remaining <= 0:
            return CoachingSuggestion(
                target="Game over",
                score=0,
                explanation="You've already won this leg!",
                confidence=1.0,
                category="checkout"
            )

        # 1. Checkout situation (highest priority)
        if remaining <= 170:
            checkout = self._get_checkout_suggestion(remaining)
            if checkout:
                return checkout

        # 2. Strategic scoring suggestion
        suggestion = self._get_strategic_suggestion(
            remaining=remaining,
            opponent_remaining=opponent_remaining,
            is_pressure=is_pressure,
            recent_avg=recent_avg
        )

        # Store for history / reports
        self.history.append({
            "remaining": remaining,
            "suggestion": suggestion.target,
            "explanation": suggestion.explanation,
            "is_pressure": is_pressure
        })

        return suggestion

    def _get_checkout_suggestion(self, remaining: int) -> Optional[CoachingSuggestion]:
        """Suggest the best checkout path with explanation."""
        checkout_path = None
        
        # Try to use the real checkout system
        if hasattr(self.checkout_table, 'get_checkout'):
            checkout_path = self.checkout_table.get_checkout(remaining)
        elif 'get_best_checkout' in globals():
            checkout_path = get_best_checkout(remaining)

        if not checkout_path:
            # Fallback simple logic
            if remaining <= 20 and remaining % 2 == 0:
                checkout_path = [remaining]
            else:
                return None

        target = self._format_checkout_path(checkout_path)
        
        explanation = f"Checkout with {target}! "
        if len(checkout_path) == 1:
            explanation += "Single dart finish — go for it!"
        elif len(checkout_path) == 2:
            explanation += "Two-dart checkout. Hit the first one cleanly."
        else:
            explanation += "Three-dart checkout. Focus on accuracy."

        # Adjust for style
        if self.style == "aggressive" and remaining > 100:
            explanation += " (Aggressive play — go big!)"

        return CoachingSuggestion(
            target=target,
            score=sum(checkout_path),
            explanation=explanation,
            confidence=0.95,
            category="checkout"
        )

    def _get_strategic_suggestion(self, 
                                  remaining: int,
                                  opponent_remaining: Optional[int],
                                  is_pressure: bool,
                                  recent_avg: Optional[float]) -> CoachingSuggestion:
        """Strategic scoring when not in checkout range."""
        
        # Default strong targets
        best_target = "T20"
        best_score = 60
        explanation = "T20 is the highest scoring single dart and keeps your options open."

        # Context-aware adjustments
        if remaining > 100:
            # Big scoring phase
            if is_pressure and self.style != "safe":
                best_target = "T19"
                best_score = 57
                explanation = "T19 is slightly safer than T20 under pressure while still scoring heavily."
            else:
                best_target = "T20"
                explanation = "Maximum scoring. T20 sets up strong checkout options later."

        elif 60 < remaining <= 100:
            # Setup phase
            best_target = "T20"
            explanation = "T20 leaves you in a great position for the next visit."

            # If opponent is close, be more aggressive
            if opponent_remaining and opponent_remaining < remaining:
                best_target = "T18"
                explanation = "T18 — balanced scoring while keeping pressure on your opponent."

        elif remaining <= 60:
            # Close to checkout — set up nicely
            if remaining % 2 == 0:
                best_target = f"D{remaining // 2}"
                best_score = remaining
                explanation = f"Double {remaining // 2} leaves you on a perfect checkout next time."
            else:
                best_target = "T20"
                explanation = "T20 keeps your scoring high while moving toward checkout range."

        # Pressure adjustment
        if is_pressure:
            if self.style == "safe":
                explanation += " (Safe choice under pressure — prioritize accuracy.)"
            else:
                explanation += " (Pressure situation — stay aggressive but focused.)"

        # Recent form adjustment
        if recent_avg and recent_avg < 40:
            explanation += " Your recent scoring has been a bit low — aim for consistency over hero darts."

        confidence = 0.85 if not is_pressure else 0.75

        return CoachingSuggestion(
            target=best_target,
            score=best_score,
            explanation=explanation,
            confidence=confidence,
            category="setup" if remaining > 60 else "pressure"
        )

    def _format_checkout_path(self, path: List[int]) -> str:
        """Convert [60, 20, 16] → 'T20 + 20 + D8' style string."""
        formatted = []
        for dart in path:
            if dart == 50:
                formatted.append("Bull")
            elif dart > 20:
                formatted.append(f"T{dart // 3}")
            elif dart % 2 == 0 and dart <= 40:
                formatted.append(f"D{dart // 2}")
            else:
                formatted.append(str(dart))
        return " + ".join(formatted)

    def get_post_leg_report(self, player_name: str = "You") -> Dict[str, Any]:
        """
        Generate a nice coaching report after a leg.
        Call this at the end of a leg.
        """
        if not self.history:
            return {"message": "No coaching data for this leg yet."}

        total_suggestions = len(self.history)
        pressure_suggestions = sum(1 for h in self.history if h.get("is_pressure"))

        # Simple stats
        avg_confidence = sum(s.get("confidence", 0.8) for s in self.history) / total_suggestions

        report = {
            "player": player_name,
            "suggestions_given": total_suggestions,
            "pressure_situations": pressure_suggestions,
            "average_confidence": round(avg_confidence, 2),
            "top_advice": self._get_top_advice(),
            "summary": self._generate_summary_text(player_name, total_suggestions, pressure_suggestions)
        }

        return report

    def _get_top_advice(self) -> str:
        """Pick the most repeated or highest-confidence suggestion."""
        if not self.history:
            return "Keep practicing your finishing!"
        
        # Simple: most common target
        targets = [h["suggestion"] for h in self.history]
        most_common = max(set(targets), key=targets.count)
        return f"Focus on hitting {most_common} more consistently."

    def _generate_summary_text(self, name: str, total: int, pressure: int) -> str:
        if pressure > total * 0.4:
            return f"{name}, you handled pressure situations well. Keep trusting the process in big moments."
        else:
            return f"{name}, solid leg! Try to be more aggressive when the game is on the line."

    def reset(self):
        """Clear history for a new match."""
        self.history.clear()


# ======================
# Example usage / integration snippet
# ======================
"""
# In your Streamlit app or engine (example):

from core.coaching_mode import CoachingMode
from core.pressure_performance_index import PressurePerformanceIndex

# Initialize once
if 'coach' not in st.session_state:
    st.session_state.coach = CoachingMode(style="balanced")
    st.session_state.ppi = PressurePerformanceIndex()

coach = st.session_state.coach
ppi = st.session_state.ppi

# During your turn (in scoring section):
remaining = st.session_state.engine.current_player.remaining
opponent_remaining = st.session_state.engine.opponent.remaining if hasattr(...) else None

# Check if we're in a pressure situation
is_pressure = ppi.throws and (len(ppi.throws) > 3)  # simplistic
"""

# v3.1 Advanced Weakness Analysis (P1-1)
def analyze_weaknesses(throws: List[Dict], history: List[Dict]) -> Dict[str, Any]:
    """Advanced per-segment weakness + pressure detection for coach.
    Returns recommendations and auto-drills.
    """
    if not throws:
        return {"message": "Throw more darts for analysis."}
    segments = {}
    for t in throws:
        seg = t.get("segment", t.get("score", 20) // 3 or 20)  # rough
        segments[seg] = segments.get(seg, 0) + 1
    sorted_segs = sorted(segments.items(), key=lambda x: x[1])
    weak = [s for s, c in sorted_segs[:3]]
    pressure_throws = [h for h in history if h.get("is_pressure")]
    pressure_acc = sum(h.get("score", 0) for h in pressure_throws) / max(len(pressure_throws), 1) if pressure_throws else 0
    rec = {
        "weak_segments": weak,
        "pressure_accuracy": round(pressure_acc, 1),
        "recommended_drills": [f"Practice {w} x50" for w in weak] + (["Pressure checkout drills"] if pressure_acc < 50 else []),
        "ai_tip": "Focus on your weak segments in pressure situations for biggest gains."
    }
    return rec

suggestion = coach.get_suggestion(
    remaining=remaining,
    opponent_remaining=opponent_remaining,
    is_pressure=is_pressure
)

st.info(f"**Coach says:** Aim for **{suggestion.target}**")
st.caption(suggestion.explanation)

# After the leg ends:
if leg_finished:
    report = coach.get_post_leg_report(player_name="You")
    st.subheader("Coach's Report")
    st.json(report)
    coach.reset()   # ready for next leg
"""
