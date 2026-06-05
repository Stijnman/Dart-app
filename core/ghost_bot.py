"""
Ghost Bot: AI that clones a player's throwing patterns and behavior.
Uses historical player data to replicate their style, accuracy, and decision-making.
"""

import random
from typing import List, Dict, Optional, Tuple
from core.player_analytics import AdvancedPlayerStats


class GhostBot:
    """
    A bot that mimics a real player's behavior based on their historical data.
    """
    
    def __init__(self, player_profile: AdvancedPlayerStats, difficulty_modifier: float = 1.0):
        """
        Initialize a Ghost Bot from a player profile.
        
        Args:
            player_profile: AdvancedPlayerStats object containing player's history
            difficulty_modifier: 0.5-1.5 to make the ghost easier/harder
        """
        self.player_profile = player_profile
        self.difficulty_modifier = difficulty_modifier
        self.name = f"Ghost of {player_profile.player_name}"
        
        # Extract behavioral patterns
        self.favorite_segments = dict(player_profile.heatmap.get_favorite_segments(3))
        self.weak_segments = dict(player_profile.heatmap.get_weak_segments(3))
        self.opening_pattern = player_profile.get_opening_throw_pattern()
        self.closing_pattern = player_profile.get_closing_throw_pattern()
        self.heatmap = player_profile.heatmap.get_heatmap_data()
    
    def get_throw_x01(self, remaining_score: int) -> List[int]:
        """
        Generate a throw for X01 games based on player's profile.
        """
        darts = [0, 0, 0]
        
        # Phase 1: Opening (first leg, high score)
        if remaining_score > 300:
            darts[0] = self._get_opening_throw()
            darts[1] = self._get_opening_throw()
            darts[2] = self._get_opening_throw()
        
        # Phase 2: Mid-game (scoring phase)
        elif remaining_score > 50:
            # Aim for high-value segments
            for i in range(3):
                darts[i] = self._get_scoring_throw()
        
        # Phase 3: Checkout (low score, need exact finish)
        else:
            darts = self._get_checkout_throw(remaining_score)
        
        return darts
    
    def get_throw_cricket(self) -> List[int]:
        """Generate a throw for Cricket games."""
        # Cricket: aim for 15-20 and bull
        cricket_targets = [15, 16, 17, 18, 19, 20, 25]
        darts = []
        
        for _ in range(3):
            if random.random() < 0.7:  # 70% hit rate
                target = random.choice(cricket_targets)
                multiplier = random.choice([1, 2, 3])
                darts.append(target * multiplier)
            else:
                darts.append(0)  # Miss
        
        return darts
    
    def _get_opening_throw(self) -> int:
        """Get a throw based on player's opening pattern."""
        opening_avg = self.opening_pattern.get("average", 60)
        variance = opening_avg * 0.15  # 15% variance
        
        # Add some randomness but bias towards their average
        base_throw = int(opening_avg + random.gauss(0, variance))
        return max(0, min(base_throw, 180))
    
    def _get_scoring_throw(self) -> int:
        """Get a high-value scoring throw."""
        # Bias towards favorite segments
        if random.random() < 0.6:  # 60% of the time, hit favorite segment
            fav_seg = random.choice(list(self.favorite_segments.keys()))
            multiplier = random.choices([1, 2, 3], weights=[0.2, 0.3, 0.5])[0]
            return fav_seg * multiplier if fav_seg != 25 else (25 if multiplier == 1 else 50)
        else:
            # Otherwise, random high-value throw
            segments = list(range(1, 21)) + [25]
            seg = random.choice(segments)
            multiplier = random.choices([1, 2, 3], weights=[0.1, 0.3, 0.6])[0]
            return seg * multiplier if seg != 25 else (25 if multiplier == 1 else 50)
    
    def _get_checkout_throw(self, remaining: int) -> List[int]:
        """Get a checkout throw sequence."""
        darts = [0, 0, 0]
        
        # Try to hit a valid checkout
        closing_avg = self.closing_pattern.get("average", 40)
        
        # First dart: aim high to reduce score
        if remaining > 100:
            darts[0] = int(closing_avg * 0.8)
        elif remaining > 50:
            darts[0] = int(closing_avg * 0.6)
        else:
            darts[0] = int(closing_avg * 0.4)
        
        # Remaining after first dart
        remaining -= darts[0]
        
        # Second dart
        if remaining > 50:
            darts[1] = int(remaining * 0.7)
        else:
            darts[1] = int(remaining * 0.5)
        
        remaining -= darts[1]
        
        # Third dart: try to finish with double
        if 2 <= remaining <= 40 and remaining % 2 == 0:
            darts[2] = remaining  # Exact double
        else:
            darts[2] = max(0, remaining - 5)
        
        return darts
    
    def get_pressure_adjustment(self, is_ahead: bool, score_diff: int) -> float:
        """
        Adjust throw accuracy based on match pressure.
        Returns a multiplier to apply to accuracy.
        """
        if is_ahead:
            # Playing safe when ahead
            return 0.95 + (score_diff / 100) * 0.05
        else:
            # Playing aggressive when behind
            return 1.0 + (score_diff / 100) * 0.1
    
    def get_fatigue_factor(self, darts_thrown: int) -> float:
        """
        Simulate fatigue over a long match.
        Returns a multiplier to apply to accuracy.
        """
        # Every 100 darts, accuracy drops by 2%
        fatigue = max(0, (darts_thrown / 100) * 0.02)
        return max(0.7, 1.0 - fatigue)


class GhostBotManager:
    """Manages multiple Ghost Bots for tournament play."""
    
    def __init__(self):
        self.ghosts = {}  # player_name -> GhostBot
    
    def create_ghost(self, player_profile: AdvancedPlayerStats, difficulty: float = 1.0) -> GhostBot:
        """Create a new Ghost Bot from a player profile."""
        ghost = GhostBot(player_profile, difficulty)
        self.ghosts[player_profile.player_name] = ghost
        return ghost
    
    def get_ghost(self, player_name: str) -> Optional[GhostBot]:
        """Retrieve a Ghost Bot."""
        return self.ghosts.get(player_name)
    
    def list_available_ghosts(self) -> List[str]:
        """List all available Ghost Bots."""
        return list(self.ghosts.keys())
