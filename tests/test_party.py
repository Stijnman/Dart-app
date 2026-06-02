"""
Party game tests: Killer, Half It.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.engine import DartGameEngine
from core.player import Player


class TestKiller:
    """Test Killer party game."""
    
    def test_killer_initialization(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="killer", players=[p1, p2])
        assert engine.state.killer_lives["Alice"] == 3
        assert engine.state.killer_claimed["Alice"] is None
    
    def test_killer_claim(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="killer", players=[p1, p2])
        result = engine.record_throw([5, 0, 0])  # Claim 5
        assert engine.state.killer_claimed["Alice"] == 5
        assert "claims" in result.lower()
    
    def test_killer_kill(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="killer", players=[p1, p2])
        # Both claim different numbers
        engine.state.killer_claimed["Alice"] = 5
        engine.state.killer_claimed["Bob"] = 10
        engine.state.killer_available = [n for n in range(1, 21) if n not in [5, 10]]
        
        # Now Alice hits her number (5), should not affect Bob (different number)
        # To kill Bob, they'd need the same number... let me adjust
        engine.state.killer_claimed["Alice"] = 5
        engine.state.killer_claimed["Bob"] = 5  # Same number scenario
        engine.state.current_player_idx = 0  # Alice's turn
        result = engine.record_throw([5, 0, 0])
        # Bob should lose a life
        assert engine.state.killer_lives["Bob"] == 2


class TestHalfIt:
    """Test Half It game."""
    
    def test_half_it_initialization(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="half_it", players=[p1, p2])
        assert engine.state.half_it_scores["Alice"] == 0
        assert engine.state.half_it_current_target_idx == 0
    
    def test_half_it_hit_scores(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="half_it", players=[p1, p2])
        result = engine.record_throw([15, 15, 15])  # Hit 15 three times
        assert engine.state.half_it_scores["Alice"] > 0
    
    def test_half_it_miss_halves(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="half_it", players=[p1, p2])
        # First hit to get some score
        engine.record_throw([15, 15, 15])
        score = engine.state.half_it_scores["Alice"]
        # Now miss
        engine.state.half_it_current_target_idx += 1  # Move to next target
        engine.record_throw([0, 0, 0])  # Miss next target
        assert engine.state.half_it_scores["Alice"] <= score // 2 or "halved" in engine.state.history[-1].message.lower()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
