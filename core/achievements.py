"""
Achievement & Badge System — 30+ unlockable achievements.
Daily/weekly challenges and streak tracking.
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json


@dataclass
class Achievement:
    id: str
    name: str
    description: str
    category: str  # "scoring", "finishing", "games", "streak", "special"
    tier: str  # "bronze", "silver", "gold", "platinum"
    condition_fn: Callable = field(default=None, repr=False)
    icon: str = "🏅"
    unlocked_at: Optional[str] = None
    progress: int = 0
    target: int = 1
    secret: bool = False  # Hidden until unlocked


class AchievementEngine:
    """Tracks achievements, challenges, and streaks."""
    
    ACHIEVEMENT_DEFS = [
        # Scoring achievements
        Achievement("first_180", "First 180!", "Score your first 180", "scoring", "bronze", icon="🎯", target=1),
        Achievement("ton_eighty_10", "T80 Machine", "Score 10x 180", "scoring", "silver", icon="🔥", target=10),
        Achievement("ton_eighty_100", "180 Factory", "Score 100x 180", "scoring", "gold", icon="☄️", target=100),
        Achievement("highest_throw_140", "Big Scorer", "Score 140+ in a throw", "scoring", "bronze", icon="💯", target=1),
        Achievement("highest_throw_170", "Maximum!", "Score 170 in a throw", "scoring", "gold", icon="👑", target=1),
        Achievement("back_to_back_180", "Back to Back!", "Two 180s in a row", "scoring", "platinum", icon="⚡", target=1, secret=True),
        
        # Finishing achievements
        Achievement("first_checkout", "First Checkout", "Win a leg with a checkout", "finishing", "bronze", icon="🎯", target=1),
        Achievement("checkout_100", "Ton Check", "Checkout from 100+", "finishing", "silver", icon="💰", target=1),
        Achievement("checkout_150", "Big Check", "Checkout from 150+", "finishing", "gold", icon="💎", target=1),
        Achievement("checkout_170", "Maximum Checkout!", "Checkout 170", "finishing", "platinum", icon="👑", target=1, secret=True),
        Achievement("checkout_9_darter", "9-Dart Legend", "Win a leg in 9 darts or less", "finishing", "platinum", icon="🌟", target=1, secret=True),
        
        # Game achievements
        Achievement("first_game", "First Steps", "Complete your first game", "games", "bronze", icon="🎮", target=1),
        Achievement("games_10", "Getting Started", "Complete 10 games", "games", "bronze", icon="📊", target=10),
        Achievement("games_50", "Regular Player", "Complete 50 games", "games", "silver", icon="🎲", target=50),
        Achievement("games_100", "Century Club", "Complete 100 games", "games", "gold", icon="🏆", target=100),
        Achievement("games_500", "Dart Addict", "Complete 500 games", "games", "platinum", icon="🎯", target=500),
        Achievement("win_first", "First Victory", "Win your first game", "games", "bronze", icon="🏅", target=1),
        Achievement("wins_10", "Winner", "Win 10 games", "games", "silver", icon="🥇", target=10),
        Achievement("wins_50", "Champion", "Win 50 games", "games", "gold", icon="👑", target=50),
        Achievement("all_modes", "Mode Master", "Play every game mode", "games", "gold", icon="🎪", target=15),
        Achievement("cricket_perfect", "Cricket God", "Close all numbers in one turn (9 darts)", "games", "platinum", icon="🦗", target=1, secret=True),
        
        # Streak achievements
        Achievement("streak_3", "Hot Streak", "Win 3 games in a row", "streak", "bronze", icon="🔥", target=1),
        Achievement("streak_5", "On Fire!", "Win 5 games in a row", "streak", "silver", icon="🔥", target=1),
        Achievement("streak_10", "Unstoppable!", "Win 10 games in a row", "streak", "gold", icon="🔥", target=1),
        Achievement("streak_20", "Legendary!", "Win 20 games in a row", "streak", "platinum", icon="🔥", target=1, secret=True),
        
        # Special achievements
        Achievement("bobs27_perfect", "Bob's Master", "Complete Bob's 27 without losing a life", "special", "gold", icon="🎯", target=1),
        Achievement("shanghai_instant", "Shanghai King", "Win Shanghai on round 1", "special", "gold", icon="🎯", target=1, secret=True),
        Achievement("atc_speedrun", "Speedrunner", "Complete ATC in under 20 darts", "special", "silver", icon="⚡", target=1),
        Achievement("killer_survivor", "Last One Standing", "Win Killer with 1 life remaining", "special", "silver", icon="☠️", target=1),
        Achievement("half_it_comeback", "Comeback King", "Win Half It after being halved to <10", "special", "gold", icon="📈", target=1, secret=True),
        Achievement("beat_bot_hard", "Bot Slayer", "Defeat DartBot on Hard (level 8+)", "games", "silver", icon="🤖", target=1),
        Achievement("beat_bot_max", "AI Destroyer", "Defeat DartBot on Lukeman (level 12)", "games", "gold", icon="💀", target=1),
    ]
    
    def __init__(self, player_name: str, storage: Dict = None):
        self.player_name = player_name
        self.achievements: Dict[str, Achievement] = {}
        self._init_achievements(storage or {})
        
        # Streak tracking
        self.current_streak = 0
        self.best_streak = 0
        
        # Daily/Weekly challenges
        self.challenges: List[Dict] = []
        self._generate_challenges()
        
        # Modes played tracking
        self.modes_played: set = set()
    
    def _init_achievements(self, storage: Dict):
        """Initialize from saved state."""
        saved = storage.get("achievements", {})
        for def_ach in self.ACHIEVEMENT_DEFS:
            ach = Achievement(
                id=def_ach.id,
                name=def_ach.name,
                description=def_ach.description,
                category=def_ach.category,
                tier=def_ach.tier,
                icon=def_ach.icon,
                target=def_ach.target,
                secret=def_ach.secret,
            )
            if def_ach.id in saved:
                ach.unlocked_at = saved[def_ach.id].get("unlocked_at")
                ach.progress = saved[def_ach.id].get("progress", 0)
            self.achievements[def_ach.id] = ach
        
        self.current_streak = storage.get("current_streak", 0)
        self.best_streak = storage.get("best_streak", 0)
        self.modes_played = set(storage.get("modes_played", []))
    
    def to_dict(self) -> Dict:
        return {
            "achievements": {
                aid: {"unlocked_at": a.unlocked_at, "progress": a.progress}
                for aid, a in self.achievements.items()
            },
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
            "modes_played": list(self.modes_played),
        }
    
    def check_game_end(self, won: bool, mode: str, stats: Dict) -> List[Achievement]:
        """Check all achievements after a game ends. Returns newly unlocked."""
        newly_unlocked = []
        
        # Update streaks
        if won:
            self.current_streak += 1
            if self.current_streak > self.best_streak:
                self.best_streak = self.current_streak
        else:
            self.current_streak = 0
        
        self.modes_played.add(mode)
        
        # Check each achievement
        checks = [
            ("first_game", True),  # Any completed game
            ("games_10", True), ("games_50", True), ("games_100", True), ("games_500", True),
            ("win_first", won), ("wins_10", won), ("wins_50", won),
            ("first_180", stats.get("one_eighties", 0) > 0),
            ("ton_eighty_10", stats.get("one_eighties", 0) >= 10),
            ("ton_eighty_100", stats.get("one_eighties", 0) >= 100),
            ("highest_throw_140", stats.get("best_throw", 0) >= 140),
            ("highest_throw_170", stats.get("best_throw", 0) >= 170),
            ("first_checkout", won and stats.get("checkout", False)),
            ("checkout_100", stats.get("highest_checkout", 0) >= 100),
            ("checkout_150", stats.get("highest_checkout", 0) >= 150),
            ("checkout_170", stats.get("highest_checkout", 0) >= 170),
            ("streak_3", self.current_streak >= 3),
            ("streak_5", self.current_streak >= 5),
            ("streak_10", self.current_streak >= 10),
            ("streak_20", self.current_streak >= 20),
            ("all_modes", len(self.modes_played) >= 15),
            ("beat_bot_hard", stats.get("beat_bot_level", 0) >= 8),
            ("beat_bot_max", stats.get("beat_bot_level", 0) >= 12),
        ]
        
        for ach_id, condition in checks:
            if condition:
                unlocked = self._unlock(ach_id)
                if unlocked:
                    newly_unlocked.append(unlocked)
        
        return newly_unlocked
    
    def _unlock(self, ach_id: str) -> Optional[Achievement]:
        """Unlock an achievement if not already unlocked."""
        ach = self.achievements.get(ach_id)
        if ach and not ach.unlocked_at:
            ach.unlocked_at = datetime.now().isoformat()
            ach.progress = ach.target
            return ach
        return None
    
    def get_unlocked(self) -> List[Achievement]:
        """Get all unlocked achievements."""
        return [a for a in self.achievements.values() if a.unlocked_at]
    
    def get_locked(self) -> List[Achievement]:
        """Get locked (visible) achievements."""
        return [a for a in self.achievements.values() if not a.unlocked_at and not a.secret]
    
    def get_secret_locked(self) -> List[Achievement]:
        """Get secret achievements that are still locked."""
        return [a for a in self.achievements.values() if not a.unlocked_at and a.secret]
    
    def get_summary(self) -> Dict:
        """Get achievement summary."""
        unlocked = self.get_unlocked()
        total = len(self.achievements)
        by_tier = {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0}
        for a in unlocked:
            by_tier[a.tier] = by_tier.get(a.tier, 0) + 1
        
        return {
            "unlocked": len(unlocked),
            "total": total,
            "percentage": round(len(unlocked) / total * 100, 1),
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
            "by_tier": by_tier,
        }
    
    # ===== DAILY/WEEKLY CHALLENGES =====
    
    def _generate_challenges(self):
        """Generate daily and weekly challenges."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        self.challenges = [
            {
                "id": f"daily_180_{today}",
                "name": "Daily: 180 Hunter",
                "description": "Score at least one 180 today",
                "type": "daily",
                "target": 1,
                "progress": 0,
                "reward": "+10 XP",
                "expires": (datetime.now() + timedelta(days=1)).isoformat(),
            },
            {
                "id": f"daily_checkout_{today}",
                "name": "Daily: Finisher",
                "description": "Complete 3 checkouts today",
                "type": "daily",
                "target": 3,
                "progress": 0,
                "reward": "+15 XP",
                "expires": (datetime.now() + timedelta(days=1)).isoformat(),
            },
            {
                "id": f"daily_games_{today}",
                "name": "Daily: Practice Makes Perfect",
                "description": "Play 5 games today",
                "type": "daily",
                "target": 5,
                "progress": 0,
                "reward": "+20 XP",
                "expires": (datetime.now() + timedelta(days=1)).isoformat(),
            },
            {
                "id": f"weekly_avg_{today}",
                "name": "Weekly: Consistency",
                "description": "Maintain 60+ average across 10 games this week",
                "type": "weekly",
                "target": 10,
                "progress": 0,
                "reward": "+50 XP",
                "expires": (datetime.now() + timedelta(days=7)).isoformat(),
            },
            {
                "id": f"weekly_wins_{today}",
                "name": "Weekly: Winning Streak",
                "description": "Win 10 games this week",
                "type": "weekly",
                "target": 10,
                "progress": 0,
                "reward": "+75 XP",
                "expires": (datetime.now() + timedelta(days=7)).isoformat(),
            },
            {
                "id": f"weekly_checkouts_{today}",
                "name": "Weekly: Checkout Master",
                "description": "Hit 20 checkouts this week",
                "type": "weekly",
                "target": 20,
                "progress": 0,
                "reward": "+100 XP",
                "expires": (datetime.now() + timedelta(days=7)).isoformat(),
            },
        ]
    
    def get_challenges(self) -> List[Dict]:
        """Get active challenges."""
        return self.challenges
    
    def update_challenge_progress(self, challenge_id: str, progress: int):
        """Update progress on a challenge."""
        for c in self.challenges:
            if c["id"] == challenge_id:
                c["progress"] = min(c["target"], c["progress"] + progress)
                return c["progress"] >= c["target"]
        return False
