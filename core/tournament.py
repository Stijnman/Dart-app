"""
core/tournament.py
v3.1 stub for tournament brackets (P0-2 / v3.2).
Dataclasses for Bracket + Match, auto-advance hooks, Plotly tree viz stub.
Integrate with WS for live updates in future (listen to match end -> advance).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import random

@dataclass
class BracketMatch:
    id: str
    p1: str
    p2: str
    winner: Optional[str] = None
    score: Optional[Dict[str, int]] = None
    round: int = 0

@dataclass
class TournamentBracket:
    id: str
    players: List[str]
    matches: List[BracketMatch] = field(default_factory=list)
    current_round: int = 0
    completed: bool = False

    def build_seeded(self):
        """Simple single elim bracket."""
        self.matches = []
        ps = self.players[:]
        random.shuffle(ps)
        r = 1
        while len(ps) > 1:
            nxt = []
            for i in range(0, len(ps), 2):
                if i+1 < len(ps):
                    m = BracketMatch(id=f"r{r}m{i//2}", p1=ps[i], p2=ps[i+1], round=r)
                    self.matches.append(m)
                    nxt.append(f"winner_{m.id}")
                else:
                    nxt.append(ps[i])
            ps = nxt
            r += 1
        self.current_round = 1

    def advance(self, match_id: str, winner: str):
        """Call from WS/game end to progress bracket."""
        for m in self.matches:
            if m.id == match_id:
                m.winner = winner
                break
        # TODO: auto create next round matches when all current done
        # integrate with engine + WS broadcast

    def to_plotly_tree(self):
        """Return fig or data for st.plotly_chart (tree / bracket viz)."""
        try:
            import plotly.graph_objects as go
            # very simple text viz for now; real: use igraph or manual shapes
            labels = [f"{m.p1} vs {m.p2}\n→{m.winner or '?'}" for m in self.matches]
            fig = go.Figure(go.Scatter(x=list(range(len(labels))), y=[m.round for m in self.matches],
                                       text=labels, mode="markers+text", textposition="top center"))
            fig.update_layout(title=f"Bracket {self.id}", height=300)
            return fig
        except Exception:
            return None

# Example usage in UI (v3.0 Advanced or new Tournaments tab):
# tb = TournamentBracket(id="t1", players=["A","B","C","D"]); tb.build_seeded()
# st.plotly_chart(tb.to_plotly_tree())
# On match end from online: tb.advance(mid, winner); st.rerun()
