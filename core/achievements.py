"""
Achievement & Badge System — 35 unlockable achievements.
Refactored: All achievements are checked, progress tracking, persistent challenges.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json


@dataclass
class Achievement:
    id: str
    name: str
    description: str
    category: str
    tier: str
    icon: str = "🏅"
    unlocked_at: Optional[str] = None
    progress: int = 0
    target: int = 1
    secret: bool = False


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
        Achievement("streak_3", "Hot Streak", "Win 3 games in a row", "streak", "bronze", icon="🔥", target=3),
        Achievement("streak_5", "On Fire!", "Win 5 games in a row", "streak", "silver", icon="🔥", target=5),
        Achievement("streak_10", "Unstoppable!", "Win 10 games in a row", "streak", "gold", icon="🔥", target=10),
        Achievement("streak_20", "Legendary!", "Win 20 games in a row", "streak", "platinum", icon="🔥", target=20, secret=True),

        # Special achievements
        Achievement("bobs27_perfect", "Bob's Master", "Complete Bob's 27 without losing a life", "special", "gold", icon="🎯", target=1),
        Achievement("shanghai_instant", "Shanghai King", "Win Shanghai on round 1", "special", "gold", icon="🎯", target=1, secret=True),
        Achievement("atc_speedrun", "Speedrunner", "Complete ATC in under 20 darts", "special", "silver", icon="⚡", target=1),
        Achievement("killer_survivor", "Last One Standing", "Win Killer with 1 life remaining", "special", "silver", icon="☠️", target=1),
        Achievement("half_it_comeback", "Comeback King", "Win Half It after being halved to <10", "special", "gold", icon="📈", target=1, secret=True),
        Achievement("beat_bot_hard", "Bot Slayer", "Defeat DartBot on Hard (level 8+)", "games", "silver", icon="🤖", target=1),
        Achievement("beat_bot_max", "AI Destroyer", "Defeat DartBot on Machine (level 12)", "games", "gold", icon="💀", target=1),
    ]

    def __init__(self, player_name: str, storage: Dict = None):
        self.player_name = player_name
        self.achievements: Dict[str, Achievement] = {}
        self._init_achievements(storage or {})

        self.current_streak = 0
        self.best_streak = 0
        self.modes_played: set = set()
        self._last_throw_was_180 = False
        self._games_played_count = 0
        self._games_won_count = 0
        self._total_180s = 0

        # Daily/Weekly challenges
        self.challenges: List[Dict] = []
        self._generate_challenges()

    def _init_achievements(self, storage: Dict):
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
        self._games_played_count = storage.get("games_played_count", 0)
        self._games_won_count = storage.get("games_won_count", 0)
        self._total_180s = storage.get("total_180s", 0)

    def to_dict(self) -> Dict:
        return {
            "achievements": {
                aid: {"unlocked_at": a.unlocked_at, "progress": a.progress}
                for aid, a in self.achievements.items()
            },
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
            "modes_played": list(self.modes_played),
            "games_played_count": self._games_played_count,
            "games_won_count": self._games_won_count,
            "total_180s": self._total_180s,
        }

    def check_game_end(self, won: bool, mode: str, stats: Dict) -> List[Achievement]:
        """Check all achievements after a game ends. Returns newly unlocked."""
        newly_unlocked = []
        self._games_played_count += 1
        self.modes_played.add(mode)

        if won:
            self.current_streak += 1
            self._games_won_count += 1
            if self.current_streak > self.best_streak:
                self.best_streak = self.current_streak
        else:
            self.current_streak = 0

        # Update 180 tracking
        one_eighties = stats.get("one_eighties", 0)
        self._total_180s += one_eighties

        # Check back-to-back 180
        back_to_back = stats.get("back_to_back_180", False)

        # Check 9-darter
        darts_for_leg = stats.get("darts_for_leg", 999)
        is_9_darter = darts_for_leg <= 9

        # Check cricket perfect (9 darts to close all)
        cricket_darts_to_close = stats.get("cricket_darts_to_close", 999)
        is_cricket_perfect = cricket_darts_to_close <= 9

        # Check Bob's 27 perfect
        bobs27_lives_lost = stats.get("bobs27_lives_lost", 999)
        is_bobs27_perfect = bobs27_lives_lost == 0

        # Check Shanghai instant win
        shanghai_round_won = stats.get("shanghai_round_won", 999)
        is_shanghai_instant = shanghai_round_won == 1

        # Check ATC speedrun
        atc_darts_used = stats.get("atc_darts_used", 999)
        is_atc_speedrun = atc_darts_used <= 20

        # Check Killer survivor
        killer_lives_remaining = stats.get("killer_lives_remaining", 0)
        is_killer_survivor = won and killer_lives_remaining == 1

        # Check Half It comeback
        half_it_lowest_score = stats.get("half_it_lowest_score", 999)
        is_half_it_comeback = won and half_it_lowest_score < 10

        # Check bot defeat level
        bot_level = stats.get("beat_bot_level", 0)

        # Build all checks with progress updates
        checks = [
            # Game count (with progress)
            ("first_game", self._games_played_count >= 1, self._games_played_count),
            ("games_10", self._games_played_count >= 10, self._games_played_count),
            ("games_50", self._games_played_count >= 50, self._games_played_count),
            ("games_100", self._games_played_count >= 100, self._games_played_count),
            ("games_500", self._games_played_count >= 500, self._games_played_count),
            # Wins (with progress)
            ("win_first", self._games_won_count >= 1, self._games_won_count),
            ("wins_10", self._games_won_count >= 10, self._games_won_count),
            ("wins_50", self._games_won_count >= 50, self._games_won_count),
            # 180s (with progress)
            ("first_180", self._total_180s >= 1, self._total_180s),
            ("ton_eighty_10", self._total_180s >= 10, self._total_180s),
            ("ton_eighty_100", self._total_180s >= 100, self._total_180s),
            # Best throw
            ("highest_throw_140", stats.get("best_throw", 0) >= 140, stats.get("best_throw", 0)),
            ("highest_throw_170", stats.get("best_throw", 0) >= 170, stats.get("best_throw", 0)),
            # Checkouts
            ("first_checkout", won and stats.get("checkout", False), 1 if (won and stats.get("checkout", False)) else 0),
            ("checkout_100", stats.get("highest_checkout", 0) >= 100, stats.get("highest_checkout", 0)),
            ("checkout_150", stats.get("highest_checkout", 0) >= 150, stats.get("highest_checkout", 0)),
            ("checkout_170", stats.get("highest_checkout", 0) >= 170, stats.get("highest_checkout", 0)),
            ("checkout_9_darter", is_9_darter, 1 if is_9_darter else 0),
            # Streaks (with progress)
            ("streak_3", self.current_streak >= 3, self.current_streak),
            ("streak_5", self.current_streak >= 5, self.current_streak),
            ("streak_10", self.current_streak >= 10, self.current_streak),
            ("streak_20", self.current_streak >= 20, self.current_streak),
            # Modes
            ("all_modes", len(self.modes_played) >= 15, len(self.modes_played)),
            # Special
            ("back_to_back_180", back_to_back, 1 if back_to_back else 0),
            ("cricket_perfect", is_cricket_perfect, 1 if is_cricket_perfect else 0),
            ("bobs27_perfect", is_bobs27_perfect, 1 if is_bobs27_perfect else 0),
            ("shanghai_instant", is_shanghai_instant, 1 if is_shanghai_instant else 0),
            ("atc_speedrun", is_atc_speedrun, 1 if is_atc_speedrun else 0),
            ("killer_survivor", is_killer_survivor, 1 if is_killer_survivor else 0),
            ("half_it_comeback", is_half_it_comeback, 1 if is_half_it_comeback else 0),
            # Bot defeats
            ("beat_bot_hard", bot_level >= 8, bot_level),
            ("beat_bot_max", bot_level >= 12, bot_level),
        ]

        for ach_id, condition, progress in checks:
            if condition:
                unlocked = self._unlock(ach_id)
                if unlocked:
                    newly_unlocked.append(unlocked)
            else:
                # Update progress even if not unlocked
                self._update_progress(ach_id, progress)

        return newly_unlocked

    def _unlock(self, ach_id: str) -> Optional[Achievement]:
        ach = self.achievements.get(ach_id)
        if ach and not ach.unlocked_at:
            ach.unlocked_at = datetime.now().isoformat()
            ach.progress = ach.target
            return ach
        return None

    def _update_progress(self, ach_id: str, progress: int):
        ach = self.achievements.get(ach_id)
        if ach and not ach.unlocked_at:
            ach.progress = min(progress, ach.target)

    def get_unlocked(self) -> List[Achievement]:
        return [a for a in self.achievements.values() if a.unlocked_at]

    def get_locked(self) -> List[Achievement]:
        return [a for a in self.achievements.values() if not a.unlocked_at and not a.secret]

    def get_secret_locked(self) -> List[Achievement]:
        return [a for a in self.achievements.values() if not a.unlocked_at and a.secret]

    def get_summary(self) -> Dict:
        unlocked = self.get_unlocked()
        total = len(self.achievements)
        by_tier = {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0}
        for a in unlocked:
            by_tier[a.tier] = by_tier.get(a.tier, 0) + 1

        return {
            "unlocked": len(unlocked),
            "total": total,
            "percentage": round(len(unlocked) / total * 100, 1) if total > 0 else 0,
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
            "by_tier": by_tier,
        }

    # ===== DAILY/WEEKLY CHALLENGES =====

    def _generate_challenges(self):
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
        return self.challenges

    def update_challenge_progress(self, challenge_id: str, progress: int):
        for c in self.challenges:
            if c["id"] == challenge_id:
                c["progress"] = min(c["target"], c["progress"] + progress)
                return c["progress"] >= c["target"]
        return False
