"""
Dart Game Pro v2.2 — Core package with 189 features
"""

__version__ = "2.3.0"

from .engine import DartGameEngine
from .player import Player
from .game_state import GameState, InOutRule, MatchFormat
from .checkout import get_checkout, get_best_checkout, is_checkable_score
from .dartbot import DartBot
from .database import init_db, save_player, get_all_players, get_recent_games
from .database_v2 import init_db_v2, get_or_create_elo, update_elo, get_or_create_career, update_career, record_login, get_anniversaries, add_equipment, get_equipment
from .achievements import AchievementEngine
from .extensions import (
    get_checkout_stats_by_range, get_segment_heatmap, get_30day_trend,
    get_consistency_rating, get_ai_coach_recommendations, generate_training_plan,
    TeamRoundTheClock, BaseballDarts, GotchaGame,
    export_stats_csv, export_game_history_csv, generate_match_report,
    get_tv_scoreboard, generate_share_text, generate_stats_card,
    TournamentEngine, BounceOutTracker,
)
from .gamemodes import (
    CountUpGame, BermudaGame, JDCChallenge, Practice4160,
    TacticCricket, RandomCricket, HammerCricket,
    EliminatorGame, RoadrunnerGame, Escalator20Game, CricketCountUp,
)
from .systems import (
    VoiceRecognition, SmartBot, ProSimulation, PRO_PLAYERS, CareerMode,
    EloSystem, SkillLevelSystem, PatternDetector, CommentaryEngine,
    AIMatchReporter, OnlineMatch, LobbySystem, DartsLiveFeatures,
    SocialSharing, ThemeSystem, VirtualDartboard, SaveResumeManager,
    GradedLeague, NAME_DATABASE,
)
from .constants import DARTBOT_LEVELS, X01_MODES, QUICK_SCORES

__all__ = [
    "DartGameEngine", "Player", "GameState", "InOutRule", "MatchFormat",
    "get_checkout", "get_best_checkout", "is_checkable_score",
    "DartBot", "init_db", "save_player", "get_all_players", "get_recent_games",
    "init_db_v2", "get_or_create_elo", "update_elo", "get_or_create_career", "update_career",
    "record_login", "get_anniversaries", "add_equipment", "get_equipment",
    "AchievementEngine",
    "get_checkout_stats_by_range", "get_segment_heatmap", "get_30day_trend",
    "get_consistency_rating", "get_ai_coach_recommendations", "generate_training_plan",
    "TeamRoundTheClock", "BaseballDarts", "GotchaGame",
    "export_stats_csv", "export_game_history_csv", "generate_match_report",
    "get_tv_scoreboard", "generate_share_text", "generate_stats_card",
    "TournamentEngine", "BounceOutTracker",
    "CountUpGame", "BermudaGame", "JDCChallenge", "Practice4160",
    "TacticCricket", "RandomCricket", "HammerCricket",
    "EliminatorGame", "RoadrunnerGame", "Escalator20Game", "CricketCountUp",
    "VoiceRecognition", "SmartBot", "ProSimulation", "PRO_PLAYERS", "CareerMode",
    "EloSystem", "SkillLevelSystem", "PatternDetector", "CommentaryEngine",
    "AIMatchReporter", "OnlineMatch", "LobbySystem", "DartsLiveFeatures",
    "SocialSharing", "ThemeSystem", "VirtualDartboard", "SaveResumeManager",
    "GradedLeague", "NAME_DATABASE",
    "DARTBOT_LEVELS", "X01_MODES", "QUICK_SCORES", "__version__",
]
