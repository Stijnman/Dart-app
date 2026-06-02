"""
Checkout system tests — verify all 161 checkouts from 170 down to 2.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.checkout import (
    get_checkout, get_best_checkout, parse_checkout_path,
    is_checkable_score, get_checkout_score_for_dart, get_first_dart_suggestion,
    CHECKOUT_TABLE
)


class TestCheckoutTableCompleteness:
    """Verify the checkout table has entries for all checkable scores."""
    
    def test_all_scores_2_to_40_present(self):
        """Every even number 2-40 must have a checkout."""
        for score in range(2, 41, 2):
            assert score in CHECKOUT_TABLE, f"Missing checkout for {score}"
    
    def test_all_scores_41_to_60_present(self):
        for score in range(41, 61):
            assert score in CHECKOUT_TABLE, f"Missing checkout for {score}"
    
    def test_all_scores_61_to_99_present(self):
        for score in range(61, 100):
            assert score in CHECKOUT_TABLE, f"Missing checkout for {score}"
    
    def test_all_scores_100_to_139_present(self):
        for score in range(100, 140):
            assert score in CHECKOUT_TABLE, f"Missing checkout for {score}"
    
    def test_all_scores_140_to_170_present(self):
        # Some scores between 140-170 are genuinely uncheckable (no 3-dart checkout exists)
        uncheckable = {159, 162, 163, 165, 166, 168, 169}  # Mathematically impossible
        for score in range(140, 171):
            if score not in uncheckable:
                assert score in CHECKOUT_TABLE, f"Missing checkout for {score}"
    
    def test_no_score_1(self):
        """Score of 1 is impossible."""
        assert 1 not in CHECKOUT_TABLE
    
    def test_no_score_above_170(self):
        """Scores above 170 can't be checked out in 3 darts."""
        assert 171 not in CHECKOUT_TABLE


class TestCheckoutPaths:
    """Verify checkout paths are valid."""
    
    def test_170_is_t20_t20_bull(self):
        path = get_best_checkout(170)
        assert "T20" in path
        assert "Bull" in path
    
    def test_40_is_d20(self):
        path = get_best_checkout(40)
        assert "D20" in path
    
    def test_50_is_bull(self):
        path = get_best_checkout(50)
        assert "Bull" in path or "bull" in path.lower()
    
    def test_32_is_d16(self):
        path = get_best_checkout(32)
        assert "D16" in path
    
    def test_2_is_d1(self):
        path = get_best_checkout(2)
        assert "D1" in path


class TestCheckoutParsing:
    """Test parsing checkout strings."""
    
    def test_parse_simple_path(self):
        segments = parse_checkout_path("T20 T20 D20")
        assert len(segments) == 3
        assert segments[0] == ("T", 20)
        assert segments[1] == ("T", 20)
        assert segments[2] == ("D", 20)
    
    def test_parse_bull(self):
        segments = parse_checkout_path("T20 T19 Bull")
        assert len(segments) == 3
        assert segments[2] == ("B", 25)
    
    def test_parse_single(self):
        segments = parse_checkout_path("20 D20")
        assert segments[0] == ("S", 20)


class TestIsCheckable:
    """Test checkable score detection."""
    
    def test_170_is_checkable(self):
        assert is_checkable_score(170)
    
    def test_40_is_checkable(self):
        assert is_checkable_score(40)
    
    def test_1_is_not_checkable(self):
        assert not is_checkable_score(1)
    
    def test_171_is_not_checkable(self):
        assert not is_checkable_score(171)


class TestFirstDartSuggestion:
    """Test first dart suggestions."""
    
    def test_170_first_dart_is_t20(self):
        suggestion = get_first_dart_suggestion(170)
        assert "T20" == suggestion
    
    def test_50_first_dart_is_bull(self):
        suggestion = get_first_dart_suggestion(50)
        assert "Bull" == suggestion
    
    def test_impossible_score_returns_none(self):
        suggestion = get_first_dart_suggestion(171)
        assert suggestion is None


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
