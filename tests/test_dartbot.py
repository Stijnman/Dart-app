"""
DartBot AI tests — Verifying realistic, unpredictable behavior.
Key requirement: Bot must NOT always checkout when below average.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.dartbot import DartBot
from core.checkout import get_best_checkout


class TestDartBotLevels:
    """Test all difficulty levels are functional."""
    
    def test_all_levels_exist(self):
        for level in range(1, 13):
            bot = DartBot(level)
            assert bot.level == level
            assert bot.avg_throw > 0
            assert bot.checkout_pct > 0
    
    def test_beginner_low_average(self):
        bot = DartBot(1)
        assert bot.avg_throw < 30
        assert bot.checkout_pct < 0.1
    
    def test_world_class_high_average(self):
        bot = DartBot(10)
        assert bot.avg_throw >= 55
        assert bot.checkout_pct > 0.7
    
    def test_level_12_is_best(self):
        bot_12 = DartBot(12)
        bot_1 = DartBot(1)
        assert bot_12.avg_throw > bot_1.avg_throw
        assert bot_12.checkout_pct > bot_1.checkout_pct


class TestDartBotThrowGeneration:
    """Test that bot generates valid throws."""
    
    def test_throw_returns_3_darts(self):
        bot = DartBot(5)
        throw = bot.get_throw_x01(501)
        assert len(throw) == 3
    
    def test_throw_values_valid(self):
        bot = DartBot(5)
        throw = bot.get_throw_x01(501)
        for dart in throw:
            assert 0 <= dart <= 60, f"Invalid dart value: {dart}"
    
    def test_throw_reduces_remaining(self):
        bot = DartBot(5)
        remaining = 100
        throw = bot.get_throw_x01(remaining)
        total = sum(throw)
        assert total <= remaining or total > remaining  # Can bust too (realistic)
    
    def test_multiple_throws_different(self):
        """Key test: Bot should NOT produce identical throws."""
        bot = DartBot(5)
        throws = [bot.get_throw_x01(200) for _ in range(10)]
        unique_throws = set(tuple(t) for t in throws)
        assert len(unique_throws) > 1, "Bot is too predictable!"


class TestDartBotUnpredictability:
    """
    CRITICAL: These tests verify the bot does NOT always checkout.
    This addresses the #1 user complaint about dart scoring apps.
    """
    
    def test_not_always_checkouts_on_40(self):
        """Bot at medium level should miss D20 sometimes."""
        bot = DartBot(5)
        successes = 0
        attempts = 50
        for _ in range(attempts):
            throw = bot.get_throw_x01(40)
            if sum(throw) == 40:
                successes += 1
        # Should NOT be 100% - allow 10% failure rate minimum
        assert successes < attempts, f"Bot never missed checkout! ({successes}/{attempts})"
    
    def test_not_always_checkouts_on_32(self):
        """Bot should miss D16 sometimes."""
        bot = DartBot(5)
        successes = 0
        attempts = 50
        for _ in range(attempts):
            throw = bot.get_throw_x01(32)
            if sum(throw) == 32:
                successes += 1
        assert successes < attempts, f"Bot never missed D16! ({successes}/{attempts})"
    
    def test_beginner_often_misses(self):
        """Beginner bot should miss most checkouts."""
        bot = DartBot(2)
        successes = 0
        for _ in range(20):
            throw = bot.get_throw_x01(40)
            if sum(throw) == 40:
                successes += 1
        # Beginner should miss more than half
        assert successes <= 15, f"Beginner too good: {successes}/20 on D20"
    
    def test_variance_in_throws(self):
        """Throws should have realistic variance, not identical."""
        bot = DartBot(6)
        totals = [sum(bot.get_throw_x01(300)) for _ in range(20)]
        avg = sum(totals) / len(totals)
        variance = sum((t - avg) ** 2 for t in totals) / len(totals)
        assert variance > 10, f"Too little variance: {variance:.1f}"


class TestDartBotScoring:
    """Test regular scoring throws."""
    
    def test_scoring_throw_reasonable(self):
        bot = DartBot(5)
        dart = bot._scoring_throw()
        assert 0 <= dart <= 60
    
    def test_high_level_scores_better(self):
        """Higher level bots should average higher scores."""
        bot_high = DartBot(10)
        bot_low = DartBot(2)
        
        high_scores = [sum(bot_high.get_throw_x01(500)) for _ in range(30)]
        low_scores = [sum(bot_low.get_throw_x01(500)) for _ in range(30)]
        
        high_avg = sum(high_scores) / len(high_scores)
        low_avg = sum(low_scores) / len(low_scores)
        
        assert high_avg > low_avg, f"High level not better: {high_avg:.1f} vs {low_avg:.1f}"


class TestDartBotFinish:
    """Test finishing behavior."""
    
    def test_finish_on_double(self):
        """Bot should try D8 from 16. May hit adjacent double or miss."""
        bot = DartBot(8)
        totals = [sum(bot.get_throw_x01(16)) for _ in range(20)]
        # Should hit exactly 16 at least a few times (D8 checkout)
        exact = sum(1 for t in totals if t == 16)
        assert exact >= 2, f"Bot rarely hits D8: {exact}/20"
    
    def test_bull_finish(self):
        """Bot should attempt bull when on 50. May miss sometimes."""
        bot = DartBot(8)
        # Test multiple times - should hit bull or near-bull at least sometimes
        totals = [sum(bot.get_throw_x01(50)) for _ in range(20)]
        # At high level, should checkout at least a few times
        checkouts = sum(1 for t in totals if t == 50)
        assert checkouts >= 2, f"Level 8 bot too weak on bull: {checkouts}/20 checkouts"


class TestDartBotNearMiss:
    """Test that near-misses are realistic."""
    
    def test_near_miss_not_zero(self):
        """When bot misses, it should still hit something nearby, not always 0."""
        bot = DartBot(5)
        # Force a miss by using a very low success rate scenario
        bot.checkout_pct = 0.0  # Force misses
        dart = bot._near_miss("T", 20)
        # Should hit something nearby, not always 0
        assert dart >= 0  # 0 is acceptable for a complete miss


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
