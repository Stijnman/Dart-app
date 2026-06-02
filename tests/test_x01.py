"""
Comprehensive X01 game mode tests.
Covers: 501, 301, 701, scoring, bust detection, double-out, checkouts, legs/sets.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.engine import DartGameEngine
from core.player import Player
from core.game_state import InOutRule


class TestX01Basics:
    """Test basic X01 scoring mechanics."""
    
    def test_501_game_creation(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2])
        assert engine.state.mode == "501"
        assert p1.score == 501
        assert p2.score == 501
    
    def test_301_game_creation(self):
        p1 = Player("Alice")
        engine = DartGameEngine(mode="301", players=[p1])
        assert p1.score == 301
    
    def test_701_game_creation(self):
        p1 = Player("Alice")
        engine = DartGameEngine(mode="701", players=[p1])
        assert p1.score == 701
    
    def test_single_throw_scoring(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2])
        result = engine.record_throw([20, 20, 20])  # 60
        assert p1.score == 441
        assert "60" in result
    
    def test_treble_scoring(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2])
        engine.record_throw([60, 60, 60])  # 180
        assert p1.score == 321
    
    def test_turn_rotation(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2])
        engine.record_throw([20, 20, 20])  # Alice
        assert engine.state.current_player().name == "Bob"
        engine.record_throw([20, 20, 20])  # Bob
        assert engine.state.current_player().name == "Alice"
    
    def test_throw_history_recorded(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2])
        engine.record_throw([20, 5, 1])
        assert len(engine.state.history) == 1
        assert engine.state.history[0].player_name == "Alice"
        assert engine.state.history[0].total == 26


class TestBustDetection:
    """Test bust detection scenarios."""
    
    def test_bust_going_below_zero(self):
        p1 = Player("Alice")
        p1.score = 20
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2])
        result = engine.record_throw([20, 20, 20])  # 60 from 20 = bust
        assert "BUST" in result.upper()
        assert p1.score == 20  # Score should not change
    
    def test_bust_score_of_one(self):
        p1 = Player("Alice")
        p1.score = 20
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2])
        result = engine.record_throw([19, 0, 0])  # 19 from 20 = 1 (impossible)
        assert "BUST" in result.upper()
    
    def test_exact_finish_double(self):
        p1 = Player("Alice")
        p1.score = 40
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2])
        result = engine.record_throw([0, 0, 40])  # D20 = 40, exact finish
        assert "CHECKOUT" in result.upper() or "wins" in result.lower()
        assert p1.score == 0
    
    def test_bust_not_double(self):
        p1 = Player("Alice")
        p1.score = 40
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2])
        result = engine.record_throw([20, 20, 0])  # 20 is not a double finish
        assert "BUST" in result.upper()
        assert p1.score == 40  # Back to 40


class TestCheckoutScenarios:
    """Test various checkout scenarios."""
    
    def test_bull_finish(self):
        p1 = Player("Alice")
        p1.score = 50
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2])
        result = engine.record_throw([0, 0, 50])  # Bull = 50
        assert p1.score == 0
        assert "CHECKOUT" in result.upper()
    
    def test_double_16_finish(self):
        p1 = Player("Alice")
        p1.score = 32
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2])
        result = engine.record_throw([0, 0, 32])  # D16 = 32
        assert p1.score == 0
    
    def test_score_of_two(self):
        p1 = Player("Alice")
        p1.score = 2
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2])
        result = engine.record_throw([0, 0, 2])  # D1 = 2
        assert p1.score == 0


class TestMatchFormats:
    """Test match format functionality."""
    
    def test_best_of_3_format(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2], match_format="best_of_3")
        assert engine.state.legs_to_win == 2
    
    def test_leg_win_tracking(self):
        p1 = Player("Alice")
        p1.score = 40
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2], match_format="best_of_3")
        engine.record_throw([0, 0, 40])
        assert engine.state.legs_won.get("Alice", 0) >= 1
    
    def test_multiple_legs_possible(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2], match_format="best_of_3")
        assert engine.state.legs_to_win == 2
        # Play first leg
        p1.score = 40
        engine.record_throw([0, 0, 40])
        assert engine.state.legs_won["Alice"] == 1


class TestHandicap:
    """Test handicap system."""
    
    def test_handicap_reduces_starting_score(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2], handicaps={"Alice": 100})
        assert p1.score == 401  # 501 - 100 handicap
        assert p2.score == 501


class TestCheckoutSuggestions:
    """Test checkout suggestion system."""
    
    def test_suggestion_for_170(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2])
        p1.score = 170
        suggestions = engine.get_checkout_suggestion("Alice")
        assert len(suggestions) > 0
        assert "T20" in suggestions[0]
    
    def test_suggestion_for_40(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2])
        p1.score = 40
        suggestions = engine.get_checkout_suggestion("Alice")
        assert len(suggestions) > 0
    
    def test_no_suggestion_above_170(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2])
        p1.score = 171
        suggestions = engine.get_checkout_suggestion("Alice")
        assert len(suggestions) == 0


class TestUndoRedo:
    """Test undo/redo functionality."""
    
    def test_undo_restores_score(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2])
        original_score = p1.score
        engine.record_throw([20, 20, 20])
        assert p1.score == original_score - 60
        success = engine.undo_last_throw()
        assert success
        assert p1.score == original_score
    
    def test_undo_empty_stack_fails(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2])
        success = engine.undo_last_throw()
        assert not success


class TestOneEighty:
    """Test 180 detection."""
    
    def test_180_scoring(self):
        p1 = Player("Alice")
        p2 = Player("Bob")
        engine = DartGameEngine(mode="501", players=[p1, p2])
        result = engine.record_throw([60, 60, 60])
        assert p1.score == 321
        assert "180" in result or "EIGHTY" in result


class TestAllX01Variants:
    """Test all X01 starting scores work."""
    
    def test_all_starting_scores(self):
        scores = [101, 170, 201, 210, 301, 501, 701, 901, 1001]
        for score in scores:
            p = Player("Test")
            engine = DartGameEngine(mode=str(score), players=[p])
            assert p.score == score, f"Failed for {score}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
