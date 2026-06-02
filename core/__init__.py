"""
Dart Game Pro v2.1 — Core package
"""

from .engine import DartGameEngine
from .player import Player
from .game_state import GameState, InOutRule, MatchFormat
from .checkout import get_checkout, get_best_checkout, is_checkable_score
from .dartbot import DartBot
from .database import init_db, save_player, get_all_players, get_recent_games
from .achievements import AchievementEngine
from .extensions import (
    get_checkout_stats_by_range, get_segment_heatmap, get_30day_trend,
    get_consistency_rating, get_ai_coach_recommendations, generate_training_plan,
    TeamRoundTheClock, BaseballDarts, GotchaGame,
    export_stats_csv, export_game_history_csv, generate_match_report,
    get_tv_scoreboard, generate_share_text, generate_stats_card,
    TournamentEngine, BounceOutTracker,
)
from .constants import DARTBOT_LEVELS, X01_MODES, QUICK_SCORES

__version__ = "2.1.0"

__all__ = [
    "DartGameEngine", "Player", "GameState", "InOutRule", "MatchFormat",
    "get_checkout", "get_best_checkout", "is_checkable_score",
    "DartBot", "init_db", "save_player", "get_all_players", "get_recent_games",
    "DARTBOT_LEVELS", "X01_MODES", "QUICK_SCORES", "__version__",
    "AchievementEngine",
    "get_checkout_stats_by_range", "get_segment_heatmap", "get_30day_trend",
    "get_consistency_rating", "get_ai_coach_recommendations", "generate_training_plan",
    "TeamRoundTheClock", "BaseballDarts", "GotchaGame",
    "export_stats_csv", "export_game_history_csv", "generate_match_report",
    "get_tv_scoreboard", "generate_share_text", "generate_stats_card",
    "TournamentEngine", "BounceOutTracker",
]
