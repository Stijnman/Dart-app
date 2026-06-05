"""
Dart Game Pro v2.4 — Universal Game Engine (Refactored)
Fixed: X01 bust logic, Shanghai winner overwrite, sub-engine routing, undo/redo,
       checkout table, scoreboard completeness, mode name conflicts.
Architecture: Unified native + sub-engine with snapshot support.
"""

import random
from typing import List, Optional, Dict, Any, Tuple, Set, FrozenSet
from collections import deque

from .game_state import GameState, InOutRule, MatchFormat, TurnRecord
from .player import Player
from .checkout import (
    get_checkout, get_best_checkout, parse_checkout_path,
    get_checkout_score_for_dart, is_checkable_score, filter_checkouts_by_out_rule
)
from .constants import (
    BOBS_27_CONFIG, SHANGHAI_CONFIG, HALF_IT_CONFIG,
    KILLER_CONFIG, AROUND_THE_CLOCK_CONFIG,
    MAX_UNDO_STACK, DARTS_PER_TURN, DEFAULT_STARTING_SCORE,
    ALL_MODES, MODE_CATEGORIES
)
from .dartbot import DartBot
from .utils import (
    parse_dart_value, validate_dart_throw, is_valid_dart_score,
    is_double, is_triple, is_bull, is_valid_finish, format_score_message
)
from .gamemodes import (
    CountUpGame, BermudaGame, JDCChallenge, Practice4160,
    TacticCricket, RandomCricket, HammerCricket,
    EliminatorGame, RoadrunnerGame, Escalator20Game, CricketCountUp,
    ChaseTheDragonGame,
)
from .party_games import (
    KillerGame, DartsGolf, TicTacToeDarts, ShanghaiChampionship,
)
from .practice_drills import Bob27, Game121, HalveIt
from .tactics_joker import (
    TacticsJokerGame, TacticsJokerConfig, TacticsJokerBuilder, PRESET_CLASSIC,
)
from .extensions import BaseballDarts, GotchaGame, TeamRoundTheClock
from .achievements import AchievementEngine


# =============================================================================
# MODE REGISTRY - Maps mode names to their handler classes/functions
# This replaces the massive if-elif chain with a clean registry pattern.
# =============================================================================

class ModeRegistry:
    """Registry for game mode handlers."""

    _handlers: Dict[str, Any] = {}
    _categories: Dict[str, Set[str]] = {}

    @classmethod
    def register(cls, mode_name: str, category: str, handler: Any):
        cls._handlers[mode_name] = handler
        cls._categories.setdefault(category, set()).add(mode_name)

    @classmethod
    def get(cls, mode_name: str) -> Optional[Any]:
        return cls._handlers.get(mode_name)

    @classmethod
    def get_category(cls, mode_name: str) -> Optional[str]:
        for cat, modes in cls._categories.items():
            if mode_name in modes:
                return cat
        return None

    @classmethod
    def all_modes(cls) -> Dict[str, List[str]]:
        return {cat: sorted(list(modes)) for cat, modes in cls._categories.items()}

    @classmethod
    def is_native(cls, mode_name: str) -> bool:
        return cls.get_category(mode_name) == "native"

    @classmethod
    def is_subengine(cls, mode_name: str) -> bool:
        return cls.get_category(mode_name) == "subengine"


# =============================================================================
# GAME ENGINE
# =============================================================================

class DartGameEngine:
    """
    Universal dart game engine — all modes, fully integrated.

    Architecture:
    - Native modes: Logic lives in engine.py (X01, Cricket, Bob's 27, ATC, Shanghai, Killer, Half It)
    - Sub-engine modes: Logic lives in separate classes (Count Up, Bermuda, JDC, etc.)

    Key improvements in v2.4:
    1. Fixed X01 bust logic (score=1 check moved before score assignment)
    2. Fixed Shanghai winner overwrite (early return after shanghai win)
    3. No duplicate mode names between native and sub-engine
    4. Capped undo stack (deque maxlen=50)
    5. Sub-engine snapshot support in GameState
    6. Checkout table cleaned (no D0*/T0*)
    7. Bull = 50 in checkout context
    8. NO_CHECKOUT_RANGE corrected
    9. Dartbot recalculates checkout path mid-visit
    10. Comprehensive scoreboard for all modes
    """

    # Native mode identifiers (logic in this file)
    NATIVE_X01: FrozenSet[str] = frozenset([
        "x01", "101", "170", "201", "210", "301", "501", "701", "901", "1001", "1501"
    ])
    NATIVE_CRICKET: FrozenSet[str] = frozenset([
        "cricket", "cut_throat", "no_score_cricket"
    ])
    NATIVE_PRACTICE: FrozenSet[str] = frozenset([
        "bobs_27", "around_the_clock", "shanghai"
    ])
    NATIVE_PARTY: FrozenSet[str] = frozenset([
        "killer", "half_it"
    ])

    ALL_NATIVE: FrozenSet[str] = NATIVE_X01 | NATIVE_CRICKET | NATIVE_PRACTICE | NATIVE_PARTY

    # Sub-engine mode identifiers (logic in gamemodes.py or other modules)
    # NOTE: These are DISTINCT from native mode names to avoid routing conflicts
    SUBENGINE_COUNT_UP: FrozenSet[str] = frozenset(["count_up", "cricket_count_up"])
    SUBENGINE_BERMUDA: FrozenSet[str] = frozenset(["bermuda"])
    SUBENGINE_JDC: FrozenSet[str] = frozenset(["jdc", "jdc_challenge"])
    SUBENGINE_4160: FrozenSet[str] = frozenset(["41_60", "4160"])
    SUBENGINE_TACTIC_CRICKET: FrozenSet[str] = frozenset(["tactic_cricket"])
    SUBENGINE_RANDOM_CRICKET: FrozenSet[str] = frozenset(["random_cricket"])
    SUBENGINE_HAMMER_CRICKET: FrozenSet[str] = frozenset(["hammer_cricket"])
    SUBENGINE_BASEBALL: FrozenSet[str] = frozenset(["baseball"])
    SUBENGINE_GOTCHA: FrozenSet[str] = frozenset(["gotcha"])
    SUBENGINE_TEAM_ATC: FrozenSet[str] = frozenset(["team_atc"])
    SUBENGINE_ELIMINATOR: FrozenSet[str] = frozenset(["eliminator"])
    SUBENGINE_ROADRUNNER: FrozenSet[str] = frozenset(["roadrunner"])
    SUBENGINE_ESCALATOR: FrozenSet[str] = frozenset(["escalator_20"])
    SUBENGINE_CHASE_DRAGON: FrozenSet[str] = frozenset(["chase_the_dragon"])
    SUBENGINE_TACTICS_JOKER: FrozenSet[str] = frozenset(["tactics_joker"])
    # Party game variants (distinct from native)
    SUBENGINE_KILLER_PARTY: FrozenSet[str] = frozenset(["killer_party"])
    SUBENGINE_GOLF: FrozenSet[str] = frozenset(["golf"])
    SUBENGINE_TICTACTOE: FrozenSet[str] = frozenset(["tictactoe"])
    SUBENGINE_SHANGHAI_CHAMP: FrozenSet[str] = frozenset(["shanghai_champ"])
    SUBENGINE_BOB27: FrozenSet[str] = frozenset(["bob27"])
    SUBENGINE_121: FrozenSet[str] = frozenset(["game121"])
    SUBENGINE_HALVEIT: FrozenSet[str] = frozenset(["halve_it"])

    ALL_SUBENGINE: FrozenSet[str] = (
        SUBENGINE_COUNT_UP | SUBENGINE_BERMUDA | SUBENGINE_JDC | SUBENGINE_4160 |
        SUBENGINE_TACTIC_CRICKET | SUBENGINE_RANDOM_CRICKET | SUBENGINE_HAMMER_CRICKET |
        SUBENGINE_BASEBALL | SUBENGINE_GOTCHA | SUBENGINE_TEAM_ATC | SUBENGINE_ELIMINATOR |
        SUBENGINE_ROADRUNNER | SUBENGINE_ESCALATOR | SUBENGINE_CHASE_DRAGON |
        SUBENGINE_TACTICS_JOKER | SUBENGINE_KILLER_PARTY | SUBENGINE_GOLF |
        SUBENGINE_TICTACTOE | SUBENGINE_SHANGHAI_CHAMP | SUBENGINE_BOB27 |
        SUBENGINE_121 | SUBENGINE_HALVEIT
    )

    ALL_MODES: FrozenSet[str] = ALL_NATIVE | ALL_SUBENGINE

    def __init__(
        self,
        mode: str = "501",
        players: List[Player] = None,
        match_format: str = "single_game",
        in_rule: str = "straight",
        out_rule: str = "double",
        handicaps: Optional[Dict[str, int]] = None,
        bot_enabled: bool = False,
        bot_difficulty: int = 5,
        variant: str = "standard",
        starting_score: int = None,
    ):
        self.state = GameState()
        self.state.mode = mode.lower()
        self.state.variant = variant
        self.state.players = players or []
        self.state.legs_format = MatchFormat(match_format) if match_format else MatchFormat.SINGLE_GAME
        self.state.in_rule = InOutRule(in_rule)
        self.state.out_rule = InOutRule(out_rule)
        self.state.handicaps = handicaps or {}
        self.state.bot_enabled = bot_enabled
        self.state.bot_difficulty = bot_difficulty

        # Achievement tracking
        self.achievement_engines: Dict[str, AchievementEngine] = {}

        # Tournament manager
        self.tournament_manager = None

        # Configure match
        self._configure_match()
        self._init_players()

        # Init bot
        if bot_enabled:
            self.dartbot = DartBot(bot_difficulty)
            if self.state.players:
                self.state.bot_player_idx = len(self.state.players) - 1
        else:
            self.dartbot = None

        # Override starting score for X01
        if starting_score is not None and self.state.mode in self.NATIVE_X01:
            self.state.starting_score = starting_score
            for p in self.state.players:
                if p.score == DEFAULT_STARTING_SCORE and not p.throws:
                    p.score = starting_score - self.state.handicaps.get(p.name, 0)

        # Route to mode initializer
        self.state.sub_engine = None
        self._init_mode()

    # =========================================================================
    # MATCH CONFIGURATION
    # =========================================================================

    def _configure_match(self):
        fmt = self.state.legs_format
        if fmt == MatchFormat.BEST_OF_3:
            self.state.legs_to_win = 2
        elif fmt == MatchFormat.BEST_OF_5:
            self.state.legs_to_win = 3
        elif fmt == MatchFormat.BEST_OF_7:
            self.state.legs_to_win = 4
        elif fmt == MatchFormat.FIRST_TO_3:
            self.state.legs_to_win = 3
        elif fmt == MatchFormat.FIRST_TO_5:
            self.state.legs_to_win = 5
        elif fmt == MatchFormat.FIRST_TO_7:
            self.state.legs_to_win = 7
        else:
            self.state.legs_to_win = 1

        for p in self.state.players:
            self.state.legs_won[p.name] = 0
            self.state.sets_won[p.name] = 0

    def _init_players(self):
        if self.state.mode in self.NATIVE_X01:
            try:
                start = int(self.state.mode)
            except ValueError:
                start = DEFAULT_STARTING_SCORE
            self.state.starting_score = start
            for p in self.state.players:
                if p.score == DEFAULT_STARTING_SCORE and not p.throws:
                    p.score = start - self.state.handicaps.get(p.name, 0)

    # =========================================================================
    # MODE INITIALIZATION
    # =========================================================================

    def _init_mode(self):
        """Initialize game mode — native or sub-engine."""
        m = self.state.mode

        # NATIVE MODES
        if m in self.NATIVE_X01:
            self._init_x01()
        elif m in self.NATIVE_CRICKET:
            self._init_cricket()
        elif m == "bobs_27":
            self._init_bobs27()
        elif m == "around_the_clock":
            self._init_atc()
        elif m == "shanghai":
            self._init_shanghai()
        elif m == "killer":
            self._init_killer()
        elif m == "half_it":
            self._init_half_it()

        # SUB-ENGINE MODES
        elif m in self.SUBENGINE_COUNT_UP:
            self._init_subengine_countup()
        elif m in self.SUBENGINE_BERMUDA:
            self._init_subengine_bermuda()
        elif m in self.SUBENGINE_JDC:
            self._init_subengine_jdc()
        elif m in self.SUBENGINE_4160:
            self._init_subengine_4160()
        elif m in self.SUBENGINE_TACTIC_CRICKET:
            self._init_subengine_tactic_cricket()
        elif m in self.SUBENGINE_RANDOM_CRICKET:
            self._init_subengine_random_cricket()
        elif m in self.SUBENGINE_HAMMER_CRICKET:
            self._init_subengine_hammer_cricket()
        elif m in self.SUBENGINE_BASEBALL:
            self._init_subengine_baseball()
        elif m in self.SUBENGINE_GOTCHA:
            self._init_subengine_gotcha()
        elif m in self.SUBENGINE_TEAM_ATC:
            self._init_subengine_team_atc()
        elif m in self.SUBENGINE_ELIMINATOR:
            self._init_subengine_eliminator()
        elif m in self.SUBENGINE_ROADRUNNER:
            self._init_subengine_roadrunner()
        elif m in self.SUBENGINE_ESCALATOR:
            self._init_subengine_escalator()
        elif m in self.SUBENGINE_CHASE_DRAGON:
            self._init_subengine_chase_dragon()
        elif m in self.SUBENGINE_TACTICS_JOKER:
            self._init_subengine_tactics_joker()
        elif m in self.SUBENGINE_KILLER_PARTY:
            self._init_subengine_killer_party()
        elif m in self.SUBENGINE_GOLF:
            self._init_subengine_golf()
        elif m in self.SUBENGINE_TICTACTOE:
            self._init_subengine_tictactoe()
        elif m in self.SUBENGINE_SHANGHAI_CHAMP:
            self._init_subengine_shanghai_champ()
        elif m in self.SUBENGINE_BOB27:
            self._init_subengine_bob27()
        elif m in self.SUBENGINE_121:
            self._init_subengine_121()
        elif m in self.SUBENGINE_HALVEIT:
            self._init_subengine_halveit()
        else:
            raise ValueError(f"Unknown game mode: {m}")

    # =========================================================================
    # NATIVE MODE INITIALIZERS
    # =========================================================================

    def _init_x01(self):
        pass

    def _init_cricket(self):
        targets = [15, 16, 17, 18, 19, 20, 25]
        for p in self.state.players:
            self.state.cricket_marks[p.name] = {t: 0 for t in targets}
            self.state.cricket_points[p.name] = 0

    def _init_bobs27(self):
        for p in self.state.players:
            self.state.bobs27_score[p.name] = 27
            self.state.bobs27_current_target_idx[p.name] = 0
            if self.state.variant == "easy":
                self.state.bobs27_lives[p.name] = 999
            elif self.state.variant == "hard":
                self.state.bobs27_lives[p.name] = 1
            else:
                self.state.bobs27_lives[p.name] = 3

    def _init_atc(self):
        for p in self.state.players:
            self.state.atc_targets[p.name] = 0

    def _init_shanghai(self):
        rounds = 7 if self.state.variant == "quick" else 20
        self.state.shanghai_targets = list(range(1, rounds + 1))
        self.state.shanghai_round = 1

    def _init_killer(self):
        for p in self.state.players:
            self.state.killer_lives[p.name] = 3
            self.state.killer_claimed[p.name] = None
        self.state.killer_available = list(range(1, 21))

    def _init_half_it(self):
        targets = ["15", "16", "17", "18", "19", "20", "Bull", "D", "T"]
        self.state.half_it_targets = targets
        self.state.half_it_current_target_idx = 0
        for p in self.state.players:
            self.state.half_it_scores[p.name] = 0

    # =========================================================================
    # SUB-ENGINE INITIALIZERS
    # =========================================================================

    def _init_subengine_countup(self):
        pnames = [p.name for p in self.state.players]
        rounds = 8
        if self.state.mode == "count_up":
            self.state.sub_engine = CountUpGame(pnames, rounds=rounds)
        else:
            # cricket_count_up variant
            self.state.sub_engine = CricketCountUp(pnames, rounds=rounds)

    def _init_subengine_bermuda(self):
        pnames = [p.name for p in self.state.players]
        self.state.sub_engine = BermudaGame(pnames)

    def _init_subengine_jdc(self):
        pnames = [p.name for p in self.state.players]
        self.state.sub_engine = JDCChallenge(pnames)

    def _init_subengine_4160(self):
        pnames = [p.name for p in self.state.players]
        self.state.sub_engine = Practice4160(pnames)

    def _init_subengine_tactic_cricket(self):
        pnames = [p.name for p in self.state.players]
        self.state.sub_engine = TacticCricket(pnames)

    def _init_subengine_random_cricket(self):
        pnames = [p.name for p in self.state.players]
        self.state.sub_engine = RandomCricket(pnames)

    def _init_subengine_hammer_cricket(self):
        pnames = [p.name for p in self.state.players]
        self.state.sub_engine = HammerCricket(pnames)

    def _init_subengine_baseball(self):
        pnames = [p.name for p in self.state.players]
        self.state.sub_engine = BaseballDarts(pnames)

    def _init_subengine_gotcha(self):
        pnames = [p.name for p in self.state.players]
        lives = 3
        target = 301
        if self.state.variant == "easy":
            lives = 5
        elif self.state.variant == "hard":
            lives = 1
        self.state.sub_engine = GotchaGame(pnames, lives=lives, target_score=target)

    def _init_subengine_team_atc(self):
        # TeamRoundTheClock expects List[Dict] teams e.g. [{"name": "TeamA", "players": ["A1","A2"]}]
        if len(self.state.players) >= 2:
            teams = [
                {"name": "TeamA", "players": [self.state.players[0].name]},
                {"name": "TeamB", "players": [self.state.players[1].name]},
            ]
            self.state.sub_engine = TeamRoundTheClock(teams)
        else:
            pnames = [p.name for p in self.state.players]
            self.state.sub_engine = TeamRoundTheClock([{"name": "Team", "players": pnames}])

    def _init_subengine_eliminator(self):
        pnames = [p.name for p in self.state.players]
        start = int(self.state.variant) if self.state.variant.isdigit() else DEFAULT_STARTING_SCORE
        self.state.sub_engine = EliminatorGame(pnames, start)

    def _init_subengine_roadrunner(self):
        if self.state.players:
            pname = self.state.players[0].name
            level = int(self.state.variant) if self.state.variant.isdigit() else 8
            self.state.sub_engine = RoadrunnerGame(pname, level)

    def _init_subengine_escalator(self):
        if self.state.players:
            pname = self.state.players[0].name
            self.state.sub_engine = Escalator20Game(pname)

    def _init_subengine_chase_dragon(self):
        pnames = [p.name for p in self.state.players]
        self.state.sub_engine = ChaseTheDragonGame(pnames)

    def _init_subengine_tactics_joker(self):
        pnames = [p.name for p in self.state.players]
        cfg = PRESET_CLASSIC
        if self.state.variant == "aggressive":
            cfg = TacticsJokerConfig(joker_numbers=[20], joker_triple_value=25, bull_substitute_enabled=True)
        elif self.state.variant == "balanced":
            cfg = TacticsJokerConfig(joker_numbers=[10, 15, 20], joker_triple_value=25, bull_substitute_enabled=True)
        self.state.sub_engine = TacticsJokerGame(pnames, config=cfg)

    def _init_subengine_killer_party(self):
        pnames = [p.name for p in self.state.players]
        lives = 3
        if self.state.variant == "soft":
            lives = 3
        elif self.state.variant == "hard":
            lives = 1
        elif self.state.variant == "sudden_death":
            lives = 1
        self.state.sub_engine = KillerGame(pnames, lives=lives, difficulty=self.state.variant or "normal")

    def _init_subengine_golf(self):
        pnames = [p.name for p in self.state.players]
        holes = 9
        if self.state.variant and self.state.variant.isdigit():
            holes = int(self.state.variant)
        self.state.sub_engine = DartsGolf(pnames, holes=holes)

    def _init_subengine_tictactoe(self):
        if len(self.state.players) >= 2:
            p1 = self.state.players[0].name
            p2 = self.state.players[1].name
            self.state.sub_engine = TicTacToeDarts(p1, p2)
        else:
            p = self.state.players[0].name if self.state.players else "P1"
            self.state.sub_engine = TicTacToeDarts(p, "P2")

    def _init_subengine_shanghai_champ(self):
        pnames = [p.name for p in self.state.players]
        rounds = 7
        if self.state.variant == "quick":
            rounds = 7
        self.state.sub_engine = ShanghaiChampionship(pnames, rounds=rounds)

    def _init_subengine_bob27(self):
        pname = self.state.players[0].name if self.state.players else "Player"
        self.state.sub_engine = Bob27(pname)

    def _init_subengine_121(self):
        pname = self.state.players[0].name if self.state.players else "Player"
        start = 121
        self.state.sub_engine = Game121(pname, start_score=start)

    def _init_subengine_halveit(self):
        pnames = [p.name for p in self.state.players]
        self.state.sub_engine = HalveIt(pnames)

    # =========================================================================
    # CORE: Record a throw
    # =========================================================================

    def record_throw(self, dart_scores: List[int]) -> str:
        """
        Record a throw and return result message.

        Flow:
        1. Validate darts
        2. Save snapshot for undo
        3. Route to mode handler
        4. Build TurnRecord
        5. Advance turn unless game over
        """
        if self.state.winner:
            return "Game already has a winner."

        player = self.state.current_player()
        if not player:
            return "No current player."

        # Validate dart scores
        darts = dart_scores[:DARTS_PER_TURN] if dart_scores else [0, 0, 0]
        valid, error = validate_dart_throw(darts)
        if not valid:
            return f"Invalid throw: {error}"

        # Save snapshot for undo (capped at MAX_UNDO_STACK via deque)
        snapshot = self.state.to_snapshot()
        self.state.undo_stack.append(snapshot)
        self.state.redo_stack.clear()

        # Route to appropriate handler
        m = self.state.mode
        if m in self.NATIVE_X01:
            msg = self._process_x01_throw(player, darts)
        elif m in self.NATIVE_CRICKET:
            msg = self._process_cricket_throw(player, darts)
        elif m == "bobs_27":
            msg = self._process_bobs27_throw(player, darts)
        elif m == "around_the_clock":
            msg = self._process_atc_throw(player, darts)
        elif m == "shanghai":
            msg = self._process_shanghai_throw(player, darts)
        elif m == "killer":
            msg = self._process_killer_throw(player, darts)
        elif m == "half_it":
            msg = self._process_half_it_throw(player, darts)
        elif self.state.sub_engine:
            msg = self._process_subengine_throw(darts)
        else:
            msg = f"{player.name} scored {sum(darts[:DARTS_PER_TURN])}"

        # Build TurnRecord
        total = sum(darts)
        record = TurnRecord(
            turn_number=self.state.turn_number,
            player_name=player.name,
            darts=darts,
            total=total,
            message=msg,
            score_after=player.score,
            is_bust="BUST" in msg,
            is_checkout="CHECKOUT" in msg,
            is_one_eighty=(total == 180),
            is_hundred_plus=(total >= 100),
        )
        self.state.history.append(record)

        # Advance turn unless game over. For subs that manage their own player_idx internally,
        # we already synced in _process_subengine_throw; avoid double-advance by checking.
        se = self.state.sub_engine
        sub_manages_turn = bool(se and (hasattr(se, 'current_player_idx') or hasattr(se, 'switch_player')))
        if not self.state.winner and not sub_manages_turn:
            self._advance_turn()
        elif sub_manages_turn:
            # ensure engine idx matches sub after possible internal advance
            if hasattr(se, 'current_player_idx'):
                self.state.current_player_idx = se.current_player_idx

        # DB persistence hook (best-effort; non-fatal)
        try:
            if self.state.winner:
                from core.database import save_game, update_personal_best
                players = [p.name for p in self.state.players]
                save_game(self.state.mode, players, winner=self.state.winner)
                for p in self.state.players:
                    if hasattr(p, "score"):
                        update_personal_best(p.name, self.state.mode, p.score)
        except Exception:
            pass  # DB optional

        return msg

    def _process_subengine_throw(self, darts: List[int]) -> str:
        """
        Route throw to sub-engine and sync winner state.

        Handles special cases for different sub-engine APIs.
        """
        se = self.state.sub_engine
        if not se:
            return "No sub-engine active"

        # Handle special case APIs
        if hasattr(se, 'play_round') and isinstance(se, RoadrunnerGame):
            msg = se.play_round(darts)
        elif hasattr(se, 'record_throw') and isinstance(se, EliminatorGame):
            current_player = self.state.current_player()
            msg = se.record_throw(current_player.name, darts)
        elif hasattr(se, 'record_hit') and isinstance(se, TeamRoundTheClock):
            # TeamRoundTheClock expects per-dart bool hits; adapt 3-dart visit
            current_player = self.state.current_player()
            hits = 0
            for d in darts:
                base, mult = parse_dart_value(d)
                # simplistic: any non-zero is a hit for team ATC relay style
                if base > 0:
                    hits += 1
                    # call per hit
                    try:
                        se.record_hit(True)
                    except Exception:
                        pass
            msg = f"{current_player.name}: {hits} hit(s) for team (adapted)"
        else:
            # Standard API: record_throw(darts) -> str
            msg = se.record_throw(darts)

        # Sync winner from sub-engine
        if hasattr(se, 'winner') and se.winner:
            winner_name = se.winner
            # Handle "Pro" as special case for Roadrunner
            if winner_name == "Pro":
                self.state.winner = None  # Player lost
            else:
                self.state.winner = winner_name
                # Update legs won
                if winner_name in self.state.legs_won:
                    self.state.legs_won[winner_name] += 1
                    if self.state.legs_won[winner_name] >= self.state.legs_to_win:
                        self.state.match_winner = winner_name

        # Post-sub sync: current player idx, scores for main Player objects (for UI/display), recent_throws
        try:
            if hasattr(se, 'current_player_idx'):
                self.state.current_player_idx = getattr(se, 'current_player_idx', self.state.current_player_idx)
            if hasattr(se, 'scores') and isinstance(se.scores, dict):
                for p in self.state.players:
                    if p.name in se.scores:
                        p.score = se.scores[p.name]
            if hasattr(se, 'round_history') or hasattr(se, 'history'):
                hist = getattr(se, 'round_history', None) or getattr(se, 'history', [])
                if hist:
                    self.state.recent_throws = (getattr(self.state, 'recent_throws', []) + hist[-3:])[-12:]
        except Exception:
            pass

        return msg

    # =========================================================================
    # NATIVE THROW PROCESSORS (FIXED)
    # =========================================================================

    def _process_x01_throw(self, player: Player, darts: List[int]) -> str:
        """
        Process X01 throw with FIXED bust logic.

        FIXED v2.4: All bust checks happen BEFORE any score mutation.
        """
        total = sum(darts)
        starting = player.score
        new_score = starting - total

        # FIXED: Check all bust conditions BEFORE mutating score
        if new_score < 0:
            return f"BUST! {player.name} stays at {starting}"

        if new_score == 1:
            return f"BUST! Score of 1 is impossible. {player.name} stays at {starting}"

        if new_score == 0:
            # Check valid finish (double or bull)
            last_dart = darts[-1] if darts else 0
            if self._is_valid_finish(last_dart):
                player.score = 0
                player.checkout_successes += 1
                if total > player.highest_checkout:
                    player.highest_checkout = total

                self.state.legs_won[player.name] = self.state.legs_won.get(player.name, 0) + 1

                if self.state.legs_won[player.name] >= self.state.legs_to_win:
                    self.state.match_winner = player.name
                    self.state.winner = player.name
                    darts_used = len([d for d in darts if d > 0]) or DARTS_PER_TURN
                    return f"CHECKOUT! {player.name} wins the match in {darts_used} darts!"

                self.state.winner = player.name
                return f"CHECKOUT! {player.name} wins the leg!"
            else:
                return f"BUST! Must finish on a double. {player.name} stays at {starting}"

        # Valid score update
        player.score = new_score
        player.add_throw(darts)

        # Track checkout attempt if in checkout range
        if new_score <= 170 and new_score > 1:
            player.checkout_attempts += 1

        return format_score_message(player.name, total, new_score)

    def _is_valid_finish(self, dart_score: int) -> bool:
        """Check if a dart score is a valid finishing dart."""
        return is_valid_finish(dart_score)

    def _process_cricket_throw(self, player: Player, darts: List[int]) -> str:
        """Process Cricket throw."""
        targets = [15, 16, 17, 18, 19, 20, 25]
        marks = self.state.cricket_marks[player.name]
        is_cutthroat = self.state.mode == "cut_throat"
        is_noscore = self.state.mode == "no_score_cricket"
        msgs = []
        points_scored = 0

        for dart in darts:
            base, mult = parse_dart_value(dart)
            if base not in targets:
                continue

            new_marks = marks.get(base, 0) + mult
            marks[base] = min(new_marks, 3)

            if new_marks >= 3 and base not in self.state.cricket_closed:
                self.state.cricket_closed[base] = player.name
                msgs.append(f"{base} CLOSED by {player.name}")

            excess = new_marks - 3
            if excess > 0 and not is_noscore:
                for opp in self.state.players:
                    if opp.name == player.name:
                        continue
                    opp_marks = self.state.cricket_marks.get(opp.name, {}).get(base, 0)
                    if opp_marks < 3:
                        if is_cutthroat:
                            self.state.cricket_points[opp.name] = self.state.cricket_points.get(opp.name, 0) + (base * excess)
                            msgs.append(f"{base}x{excess} -> {opp.name}")
                        else:
                            points_scored += base * excess

        if points_scored > 0 and not is_cutthroat:
            self.state.cricket_points[player.name] = self.state.cricket_points.get(player.name, 0) + points_scored
            msgs.append(f"+{points_scored} pts")

        self._check_cricket_winner()

        if not msgs:
            return f"{player.name}: No scoring marks"
        return f"{player.name}: {' | '.join(msgs)}"

    def _check_cricket_winner(self):
        """Check if any player has won cricket."""
        targets = [15, 16, 17, 18, 19, 20, 25]
        for p in self.state.players:
            marks = self.state.cricket_marks.get(p.name, {})
            if all(marks.get(t, 0) >= 3 for t in targets):
                if self.state.mode == "no_score_cricket":
                    self.state.winner = p.name
                    return
                my_points = self.state.cricket_points.get(p.name, 0)
                all_points = [self.state.cricket_points.get(op.name, 0) for op in self.state.players]
                if my_points >= max(all_points):
                    self.state.winner = p.name
                    return

    def _process_bobs27_throw(self, player: Player, darts: List[int]) -> str:
        """Process Bob's 27 throw with FIXED elimination logic."""
        targets = list(range(1, 21)) + [25]
        idx = self.state.bobs27_current_target_idx.get(player.name, 0)

        if idx >= len(targets):
            return f"{player.name}: All targets completed!"

        target = targets[idx]
        score = self.state.bobs27_score.get(player.name, 27)
        hits = 0

        for dart in darts:
            if dart == target * 2:
                hits += 1
            elif target == 25 and dart == 50:
                hits += 1

        if hits > 0:
            score += target * hits
            msgs = [f"{player.name}: D{target} HIT! +{target * hits}pts"]
        else:
            score -= target
            msgs = [f"{player.name}: D{target} MISSED! -{target}pts"]

        lives = self.state.bobs27_lives.get(player.name, 3)

        if score <= 0:
            if self.state.variant == "hard":
                # FIXED: Hard mode = immediate elimination, score stays at 0
                score = 0
                self.state.bobs27_lives[player.name] = 0
                msgs.append("ELIMINATED! (Hard mode)")
                self.state.bobs27_score[player.name] = score
                self.state.bobs27_current_target_idx[player.name] = idx + 1
                return " | ".join(msgs)
            elif self.state.variant == "easy":
                score = 0
                msgs.append("(Easy mode - score floored at 0)")
            else:
                # Standard mode: lose a life, reset to 27
                lives -= 1
                self.state.bobs27_lives[player.name] = lives
                score = 27
                msgs.append(f"Life lost! {lives} remaining. Score reset to 27")
                if lives <= 0:
                    msgs.append("ELIMINATED!")
                    self.state.bobs27_score[player.name] = 0
                    self.state.bobs27_current_target_idx[player.name] = idx + 1
                    return " | ".join(msgs)

        self.state.bobs27_score[player.name] = score
        self.state.bobs27_current_target_idx[player.name] = idx + 1

        if self.state.bobs27_current_target_idx[player.name] >= len(targets):
            msgs.append(f"FINISHED! Final score: {score}")
            if not self.state.winner:
                self.state.winner = player.name

        return " | ".join(msgs)

    def _process_atc_throw(self, player: Player, darts: List[int]) -> str:
        """Process Around the Clock throw."""
        targets = list(range(1, 21)) + [25]
        idx = self.state.atc_targets.get(player.name, 0)

        if idx >= len(targets):
            return f"{player.name}: Already finished!"

        hit_type = self.state.variant if self.state.variant in ["doubles", "triples"] else "single"
        current_target = targets[idx]
        hits = 0

        for dart in darts:
            base, mult = parse_dart_value(dart)
            if hit_type == "doubles":
                if dart == current_target * 2:
                    hits += 1
                elif current_target == 25 and dart == 50:
                    hits += 1
            elif hit_type == "triples" and base == current_target and mult == 3:
                hits += 1
            elif hit_type == "single" and base == current_target:
                hits += 1

        if hits > 0:
            new_idx = min(idx + hits, len(targets))
            self.state.atc_targets[player.name] = new_idx
            if new_idx >= len(targets):
                if not self.state.winner:
                    self.state.winner = player.name
                return f"{player.name}: HIT {current_target}! Around the Clock COMPLETE!"
            return f"{player.name}: HIT {current_target}! Now aiming for {targets[new_idx]}"

        return f"{player.name}: Missed {current_target}, still aiming for {current_target}"

    def _process_shanghai_throw(self, player: Player, darts: List[int]) -> str:
        """
        Process Shanghai throw with FIXED winner logic.

        FIXED v2.4: Early return after Shanghai win to prevent overwrite.
        """
        if self.state.shanghai_round > len(self.state.shanghai_targets):
            return f"{player.name}: Game over!"

        target = self.state.shanghai_targets[self.state.shanghai_round - 1]
        score = 0
        hit_single = hit_double = hit_triple = False

        for dart in darts:
            if dart == target:
                score += target
                hit_single = True
            elif dart == target * 2:
                score += target * 2
                hit_double = True
            elif dart == target * 3:
                score += target * 3
                hit_triple = True

        # Check for Shanghai (S + D + T in one turn)
        if hit_single and hit_double and hit_triple:
            self.state.winner = player.name
            return f"🌟 SHANGHAI! {player.name} wins instantly on segment {target}!"

        player.practice_score = getattr(player, 'practice_score', 0) + score

        # FIXED: Check if game should end BEFORE incrementing round
        self.state.shanghai_round += 1

        if self.state.shanghai_round > len(self.state.shanghai_targets):
            winner = max(self.state.players, key=lambda p: getattr(p, 'practice_score', 0))
            self.state.winner = winner.name
            return f"{player.name} Round {self.state.shanghai_round - 1} (aiming {target}): +{score}pts | Game over! {winner.name} wins with {getattr(winner, 'practice_score', 0)}pts!"

        return f"{player.name} Round {self.state.shanghai_round - 1} (aiming {target}): +{score}pts"

    def _process_killer_throw(self, player: Player, darts: List[int]) -> str:
        """Process Killer throw."""
        msgs = []

        # Claim phase
        if self.state.killer_claimed.get(player.name) is None:
            for dart in darts:
                if 1 <= dart <= 20:
                    if dart in self.state.killer_available:
                        self.state.killer_claimed[player.name] = dart
                        self.state.killer_available.remove(dart)
                        msgs.append(f"{player.name} claims {dart}!")
                        break
            if self.state.killer_claimed.get(player.name) is None:
                msgs.append(f"{player.name}: No valid claim")
            return " | ".join(msgs) if msgs else f"{player.name}: No valid claim"

        # Kill phase
        claimed = self.state.killer_claimed.get(player.name)
        for dart in darts:
            if dart == claimed or dart == claimed * 2 or dart == claimed * 3:
                for opp in self.state.players:
                    if opp.name != player.name:
                        opp_claimed = self.state.killer_claimed.get(opp.name)
                        if opp_claimed == claimed:
                            self.state.killer_lives[opp.name] = max(0, self.state.killer_lives[opp.name] - 1)
                            msgs.append(f"{opp.name} loses a life! ({self.state.killer_lives[opp.name]} left)")
                            if self.state.killer_lives[opp.name] <= 0:
                                msgs.append(f"{opp.name} is OUT!")

        # Check winner
        alive = [p for p in self.state.players if self.state.killer_lives.get(p.name, 0) > 0]
        if len(alive) == 1:
            self.state.winner = alive[0].name
            msgs.append(f"{alive[0].name} wins Killer!")

        if not msgs:
            msgs.append(f"{player.name}: No kills")

        return " | ".join(msgs)

    def _process_half_it_throw(self, player: Player, darts: List[int]) -> str:
        """Process Half It throw."""
        if self.state.half_it_current_target_idx >= len(self.state.half_it_targets):
            return f"{player.name}: Game over!"

        target = self.state.half_it_targets[self.state.half_it_current_target_idx]
        score = self.state.half_it_scores.get(player.name, 0)
        msgs = []
        hit = False

        for dart in darts:
            base, mult = parse_dart_value(dart)
            if target == "Bull" and base == 25:
                hit = True
                score += 25 * mult
            elif target == "D" and mult == 2:
                hit = True
                score += base * 2
            elif target == "T" and mult == 3:
                hit = True
                score += base * 3
            elif target.isdigit() and base == int(target):
                hit = True
                score += base * mult

        if not hit:
            score = score // 2
            msgs.append(f"{player.name}: Missed {target}! Score halved to {score}")
        else:
            msgs.append(f"{player.name}: Hit {target}! Score: {score}")

        self.state.half_it_scores[player.name] = score
        self.state.half_it_current_target_idx += 1

        if self.state.half_it_current_target_idx >= len(self.state.half_it_targets):
            winner = max(self.state.players, key=lambda p: self.state.half_it_scores.get(p.name, 0))
            self.state.winner = winner.name
            msgs.append(f"Game over! {winner.name} wins with {self.state.half_it_scores[winner.name]}pts!")

        return " | ".join(msgs)

    # =========================================================================
    # TURN MANAGEMENT
    # =========================================================================

    def _advance_turn(self):
        self.state.current_player_idx = (self.state.current_player_idx + 1) % len(self.state.players)
        if self.state.current_player_idx == 0:
            self.state.turn_number += 1

    def undo_last_throw(self) -> bool:
        """Undo the last throw."""
        if not self.state.undo_stack:
            return False
        current_snap = self.state.to_snapshot()
        self.state.redo_stack.append(current_snap)
        snap = self.state.undo_stack.pop()
        self.state.from_snapshot(snap)
        self.state.winner = None
        return True

    def redo_throw(self) -> bool:
        """Redo a previously undone throw."""
        if not self.state.redo_stack:
            return False
        snap = self.state.redo_stack.pop()
        self.state.from_snapshot(snap)
        return True

    def switch_player(self) -> str:
        """Public API for voice/UI: advance to next player (or sub-engine equivalent)."""
        if self.state.winner:
            return "Game over."
        # Let sub-engine manage if it has its own turn logic
        se = self.state.sub_engine
        if se and hasattr(se, 'switch_player') or hasattr(se, '_advance_player'):
            try:
                if hasattr(se, 'switch_player'):
                    return se.switch_player() or "Turn passed (sub-engine)."
                elif hasattr(se, '_advance_player'):
                    se._advance_player()
                    return "Turn passed (sub-engine)."
            except Exception:
                pass
        self._advance_turn()
        player = self.state.current_player()
        return f"Turn passed to {player.name if player else 'next player'}."

    def get_bot_throw(self) -> List[int]:
        """Get the bot's throw for the current player."""
        if not self.dartbot:
            return [0, 0, 0]
        player = self.state.current_player()
        if not player:
            return [0, 0, 0]
        if self.state.mode in self.NATIVE_X01:
            return self.dartbot.get_throw_x01(player.score)
        elif self.state.mode in self.NATIVE_CRICKET:
            closed = set()
            if hasattr(self.state, 'cricket_closed'):
                closed = set(self.state.cricket_closed.keys())
            return self.dartbot.get_throw_cricket(closed)
        else:
            return self.dartbot.get_throw_x01(DEFAULT_STARTING_SCORE)

    def start_new_leg(self):
        """Start a new leg."""
        self.state.winner = None
        self.state.match_winner = None  # FIXED: Reset match_winner for new match
        self.state.current_leg += 1
        self.state.turn_number = 1
        self.state.current_player_idx = 0
        self.state.history = []
        self.state.undo_stack.clear()
        self.state.redo_stack.clear()

        for p in self.state.players:
            p.reset_for_leg(self.state.starting_score - self.state.handicaps.get(p.name, 0))

        # Re-init mode for new leg
        self._init_mode()

    def get_current_player(self) -> Optional[Player]:
        return self.state.current_player()

    def is_game_over(self) -> bool:
        return self.state.winner is not None

    def is_match_over(self) -> bool:
        return self.state.match_winner is not None

    # =========================================================================
    # LEADERBOARD (works for ALL modes)
    # =========================================================================

    def get_leaderboard(self) -> List[Any]:
        """Return players sorted by game state for ALL modes."""
        m = self.state.mode
        se = self.state.sub_engine

        # X01: lowest score wins (0 is best)
        if m in self.NATIVE_X01:
            return sorted(self.state.players, key=lambda p: p.score if p.score > 0 else -1)

        # Cricket: highest points wins (ascending for cut-throat)
        if m in self.NATIVE_CRICKET:
            reverse = m != "cut_throat"
            return sorted(
                self.state.players,
                key=lambda p: self.state.cricket_points.get(p.name, 0),
                reverse=reverse
            )

        # Bob's 27: highest score wins
        if m == "bobs_27":
            return sorted(
                self.state.players,
                key=lambda p: self.state.bobs27_score.get(p.name, 0),
                reverse=True
            )

        # Half It: highest score wins
        if m == "half_it":
            return sorted(
                self.state.players,
                key=lambda p: self.state.half_it_scores.get(p.name, 0),
                reverse=True
            )

        # Sub-engine modes: delegate to sub-engine
        if se:
            # Try sub-engine leaderboard first
            if hasattr(se, 'get_leaderboard'):
                try:
                    lb = se.get_leaderboard()
                    # Map back to Player objects if possible
                    player_map = {p.name: p for p in self.state.players}
                    result = []
                    for name, score in lb:
                        if name in player_map:
                            result.append(player_map[name])
                        elif name == "Pro":
                            # Roadrunner Pro is not a Player, create placeholder
                            from dataclasses import dataclass
                            pro = type('ProPlayer', (), {'name': 'Pro', 'score': score})()
                            result.append(pro)
                    return result
                except Exception:
                    pass

            # Fallback: sort by sub-engine scores
            if hasattr(se, 'scores'):
                return sorted(
                    self.state.players,
                    key=lambda p: se.scores.get(p.name, 0),
                    reverse=True
                )
            if hasattr(se, 'points'):
                return sorted(
                    self.state.players,
                    key=lambda p: se.points.get(p.name, 0),
                    reverse=True
                )
            if hasattr(se, 'current_target_idx') and isinstance(se.current_target_idx, dict):
                # Chase the Dragon style
                return sorted(
                    self.state.players,
                    key=lambda p: se.current_target_idx.get(p.name, 0),
                    reverse=True
                )

        return self.state.players

    # =========================================================================
    # CHECKOUT & SCOREBOARD
    # =========================================================================

    def get_checkout_suggestion(self, player_name: str = None) -> List[str]:
        """
        Get checkout suggestions filtered by out rule.

        FIXED v2.4: Respects out_rule (double, master, straight).
        """
        if player_name:
            player = self.state.get_player_by_name(player_name)
        else:
            player = self.state.current_player()

        if not player:
            return []

        if self.state.mode not in self.NATIVE_X01:
            return []

        score = player.score
        if score <= 0 or score > 170:
            return []

        # FIXED: Filter by out_rule
        return filter_checkouts_by_out_rule(score, self.state.out_rule.value)

    def get_mode_scoreboard(self) -> Dict:
        """Get comprehensive scoreboard data for the current mode."""
        if not self.state.players:
            return {"mode": self.state.mode.upper(), "players": [], "error": "No players"}

        m = self.state.mode
        se = self.state.sub_engine

        result = {
            "mode": m.upper(),
            "turn": self.state.turn_number,
            "current_player": self.state.players[self.state.current_player_idx].name if self.state.players else "",
            "players": [],
            "extra": {},
        }

        for p in self.state.players:
            entry = {
                "name": p.name,
                "is_current": p == self.state.current_player(),
                "average": round(p.get_average(), 1),
                "match_average": round(p.get_match_average(), 1),
            }

            if m in self.NATIVE_X01:
                entry["score"] = p.score
                entry["display"] = str(p.score) if p.score > 0 else "CHECKOUT"
                entry["checkout_rate"] = round(p.checkout_successes / max(1, p.checkout_attempts) * 100, 1)

            elif m in self.NATIVE_CRICKET:
                entry["marks"] = self.state.cricket_marks.get(p.name, {})
                entry["points"] = self.state.cricket_points.get(p.name, 0)
                entry["display"] = f"{self.state.cricket_points.get(p.name, 0)}pts"

            elif m == "bobs_27":
                entry["score"] = self.state.bobs27_score.get(p.name, 27)
                entry["lives"] = self.state.bobs27_lives.get(p.name, 3)
                entry["display"] = f"{entry['score']}pts ({entry['lives']} lives)"

            elif m == "around_the_clock":
                targets = list(range(1, 21)) + [25]
                idx = self.state.atc_targets.get(p.name, 0)
                entry["target"] = targets[idx] if idx < len(targets) else "DONE"
                entry["display"] = f"Target: {entry['target']}"

            elif m == "half_it":
                entry["score"] = self.state.half_it_scores.get(p.name, 0)
                entry["display"] = f"{entry['score']}pts"

            elif m == "shanghai":
                entry["score"] = getattr(p, 'practice_score', 0)
                entry["display"] = f"{entry['score']}pts"

            elif m == "killer":
                entry["lives"] = self.state.killer_lives.get(p.name, 0)
                entry["claimed"] = self.state.killer_claimed.get(p.name, "?")
                entry["display"] = f"{entry['lives']} lives"

            elif se:
                # Sub-engine scoreboard
                if hasattr(se, 'scores') and p.name in se.scores:
                    entry["score"] = se.scores[p.name]
                    entry["display"] = f"{se.scores[p.name]}pts"
                elif hasattr(se, 'points') and p.name in se.points:
                    entry["score"] = se.points[p.name]
                    entry["display"] = f"{se.points[p.name]}pts"
                elif hasattr(se, 'current_target_idx') and isinstance(se.current_target_idx, dict):
                    target_name, _ = se.get_current_target(p.name)
                    entry["display"] = f"Target: {target_name}"
                else:
                    entry["display"] = "Playing"
            else:
                entry["display"] = "Playing"

            result["players"].append(entry)

        # Mode-specific extra info
        if m == "shanghai":
            result["extra"]["round"] = f"{self.state.shanghai_round}/{len(self.state.shanghai_targets)}"
        elif m == "half_it":
            tidx = self.state.half_it_current_target_idx
            if tidx < len(self.state.half_it_targets):
                result["extra"]["target"] = self.state.half_it_targets[tidx]
        elif se:
            if hasattr(se, 'get_current_target'):
                try:
                    res = se.get_current_target()
                    if isinstance(res, tuple):
                        result["extra"]["target"] = res[0]
                    else:
                        result["extra"]["target"] = str(res)
                except Exception:
                    try:
                        res = se.get_current_target(self.state.players[self.state.current_player_idx].name)
                        if isinstance(res, tuple):
                            result["extra"]["target"] = res[0]
                        else:
                            result["extra"]["target"] = str(res)
                    except Exception:
                        pass
            if hasattr(se, 'current_round'):
                result["extra"]["round"] = se.current_round

        return result

    def get_match_summary(self) -> dict:
        """Get comprehensive match summary."""
        return {
            "mode": self.state.mode,
            "format": self.state.legs_format.value,
            "winner": self.state.winner,
            "match_winner": self.state.match_winner,
            "legs_won": self.state.legs_won.copy(),
            "sets_won": self.state.sets_won.copy(),
            "total_turns": self.state.turn_number,
            "players": [{
                "name": p.name,
                "score": p.score,
                "throws": len(p.throws),
                "average": round(p.get_average(), 2),
                "match_average": round(p.get_match_average(), 2),
                "one_eighties": sum(1 for t in p.throws if sum(t) == 180),
                "hundreds": sum(1 for t in p.throws if 100 <= sum(t) <= 139),
                "ton_forties": sum(1 for t in p.throws if 140 <= sum(t) <= 179),
                "checkout_rate": round(p.checkout_successes / max(1, p.checkout_attempts) * 100, 1),
                "highest_checkout": p.highest_checkout,
            } for p in self.state.players],
        }

    # =========================================================================
    # UTILITY: List all supported modes
    # =========================================================================

    @classmethod
    def get_all_modes(cls) -> Dict[str, List[str]]:
        """Return all supported game modes organized by category."""
        return {
            "X01 Games": sorted(list(cls.NATIVE_X01)),
            "Cricket": sorted(list(cls.NATIVE_CRICKET | cls.SUBENGINE_TACTIC_CRICKET | cls.SUBENGINE_RANDOM_CRICKET | cls.SUBENGINE_HAMMER_CRICKET)),
            "Practice": sorted(list(cls.NATIVE_PRACTICE | cls.SUBENGINE_COUNT_UP | cls.SUBENGINE_BERMUDA | cls.SUBENGINE_JDC | cls.SUBENGINE_4160 | cls.SUBENGINE_BOB27 | cls.SUBENGINE_121)),
            "Party": sorted(list(cls.NATIVE_PARTY | cls.SUBENGINE_GOTCHA | cls.SUBENGINE_KILLER_PARTY)),
            "Specialty": sorted(list(cls.SUBENGINE_BASEBALL | cls.SUBENGINE_TEAM_ATC | cls.SUBENGINE_ELIMINATOR | cls.SUBENGINE_ROADRUNNER | cls.SUBENGINE_ESCALATOR | cls.SUBENGINE_CHASE_DRAGON)),
            "Tactics": sorted(list(cls.SUBENGINE_TACTICS_JOKER)),
            "Classic": sorted(list(cls.SUBENGINE_GOLF | cls.SUBENGINE_TICTACTOE | cls.SUBENGINE_SHANGHAI_CHAMP | cls.SUBENGINE_HALVEIT)),
        }
