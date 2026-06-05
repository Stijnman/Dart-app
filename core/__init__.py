"""
Dart Game Pro v2.4 — Core Package
"""

from .engine import DartGameEngine
from .player import Player
from .game_state import GameState, InOutRule, MatchFormat
from .checkout import get_checkout, get_best_checkout, is_checkable_score
from .dartbot import DartBot
from .achievements import AchievementEngine
from .constants import ALL_MODES, MODE_CATEGORIES, DARTBOT_LEVELS
from .systems import (
    VoiceRecognition, SmartBot, ProSimulation, CareerMode,
    EloSystem, PatternDetector, CommentaryEngine, AIMatchReporter,
    OnlineMatch, LobbySystem, DartsLiveFeatures, SocialSharing,
    ThemeSystem, VirtualDartboard, SaveResumeManager, GradedLeague,
)
from .extensions import (
    BounceOutTracker, BaseballDarts, GotchaGame, TeamRoundTheClock,
)
from .utils import parse_dart_value, validate_dart_throw, is_valid_dart_score, is_valid_finish
from .database import (
    init_db, save_player, get_player, get_all_players,
    save_game, get_games, get_player_games,
    update_personal_best, get_personal_best,
    save_player_stats, get_player_stats,
    get_leaderboard, delete_player,
)
from .database_v2 import (
    init_db_v2, save_player_v2, get_player_v2,
    save_equipment, get_equipment,
    save_match_history, get_match_history,
    record_login, get_login_streak,
    save_challenge, get_challenges,
    save_analytics, get_analytics,
)

__version__ = "3.1.0"
__all__ = [
    "DartGameEngine", "Player", "GameState", "InOutRule", "MatchFormat",
    "get_checkout", "get_best_checkout", "is_checkable_score",
    "DartBot", "AchievementEngine",
    "ALL_MODES", "MODE_CATEGORIES", "DARTBOT_LEVELS",
    "VoiceRecognition", "SmartBot", "ProSimulation", "CareerMode",
    "EloSystem", "PatternDetector", "CommentaryEngine", "AIMatchReporter",
    "OnlineMatch", "LobbySystem", "DartsLiveFeatures", "SocialSharing",
    "ThemeSystem", "VirtualDartboard", "SaveResumeManager", "GradedLeague",
    "BounceOutTracker", "BaseballDarts", "GotchaGame", "TeamRoundTheClock",
    "parse_dart_value", "validate_dart_throw", "is_valid_dart_score", "is_valid_finish",
]
