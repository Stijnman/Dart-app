"""
Dart Game Pro v2.3 — Universal Game Engine
All 30 game modes fully integrated via hybrid architecture:
- Native modes: x01 variants, Cricket variants, Bob's 27, Around the Clock, Shanghai, Killer, Half It
- Sub-engine modes: Count Up, Bermuda, JDC, 41-60, Tactic Cricket, Random Cricket, Hammer Cricket,
  Cricket Count Up, Baseball, Gotcha, Team ATC, Eliminator, Roadrunner, Escalator 20
"""

import random
from typing import List, Optional, Dict, Any
from .game_state import GameState, InOutRule, MatchFormat, TurnRecord
from .player import Player
from .checkout import get_checkout, is_checkable_score
from .constants import (
    BOBS_27_CONFIG, SHANGHAI_CONFIG, HALF_IT_CONFIG,
    KILLER_CONFIG, AROUND_THE_CLOCK_CONFIG
)
from .dartbot import DartBot
from .extensions import BounceOutTracker
from .gamemodes import (
    CountUpGame, BermudaGame, JDCChallenge, Practice4160,
    TacticCricket, RandomCricket, HammerCricket,
    EliminatorGame, RoadrunnerGame, Escalator20Game, CricketCountUp,
    ChaseTheDragonGame,
)
from .tactics_joker import TacticsJokerGame, TacticsJokerBuilder, PRESET_CLASSIC
from .party_games import KillerGame, DartsGolf, TicTacToeDarts, ShanghaiChampionship
from .practice_drills import Bob27, Game121, HalveIt
from .extensions import (
    BaseballDarts, GotchaGame, TeamRoundTheClock,
)


class DartGameEngine:
    """Universal dart game engine — all 30 modes, fully integrated."""

    # Mode classification
    NATIVE_X01 = ["x01", "101", "170", "201", "210", "301", "501", "701", "901", "1001", "1501"]
    NATIVE_CRICKET = ["cricket", "cut_throat", "no_score_cricket"]
    NATIVE_PRACTICE = ["bobs_27", "around_the_clock", "shanghai"]
    NATIVE_PARTY = ["killer", "half_it"]
    
    SUBENGINE_COUNT_UP = ["count_up", "cricket_count_up"]
    SUBENGINE_BERMUDA = ["bermuda"]
    SUBENGINE_JDC = ["jdc", "jdc_challenge"]
    SUBENGINE_4160 = ["41_60", "4160"]
    SUBENGINE_TACTIC_CRICKET = ["tactic_cricket"]
    SUBENGINE_RANDOM_CRICKET = ["random_cricket"]
    SUBENGINE_HAMMER_CRICKET = ["hammer_cricket"]
    SUBENGINE_BASEBALL = ["baseball"]
    SUBENGINE_GOTCHA = ["gotcha"]
    SUBENGINE_TEAM_ATC = ["team_atc"]
    SUBENGINE_ELIMINATOR = ["eliminator"]
    SUBENGINE_ROADRUNNER = ["roadrunner"]
    SUBENGINE_ESCALATOR = ["escalator_20"]
    SUBENGINE_CHASE_DRAGON = ["chase_the_dragon"]
    SUBENGINE_TACTICS_JOKER = ["tactics_joker"]
    SUBENGINE_KILLER = ["killer"]
    SUBENGINE_GOLF = ["golf"]
    SUBENGINE_TICTACTOE = ["tictactoe"]
    SUBENGINE_SHANGHAI = ["shanghai_champ"]
    SUBENGINE_BOB27 = ["bob27"]
    SUBENGINE_121 = ["game121"]
    SUBENGINE_HALVEIT = ["halve_it"]

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
        self.bounce_tracker = BounceOutTracker()

        # Override starting score for X01
        if starting_score is not None and self.state.mode in self.NATIVE_X01:
            self.state.starting_score = starting_score
            for p in self.state.players:
                p.score = starting_score - self.state.handicaps.get(p.name, 0)

        # Route to mode initializer
        self.state.sub_engine = None
        self._init_mode()

    def _init_mode(self):
        """Initialize game mode — native or sub-engine."""
        m = self.state.mode
        
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
        elif m in self.SUBENGINE_KILLER:
            self._init_subengine_killer()
        elif m in self.SUBENGINE_GOLF:
            self._init_subengine_golf()
        elif m in self.SUBENGINE_TICTACTOE:
            self._init_subengine_tictactoe()
        elif m in self.SUBENGINE_SHANGHAI:
            self._init_subengine_shanghai()
        elif m in self.SUBENGINE_BOB27:
            self._init_subengine_bob27()
        elif m in self.SUBENGINE_121:
            self._init_subengine_121()
        elif m in self.SUBENGINE_HALVEIT:
            self._init_subengine_halveit()

    # =========================================================================
    # NATIVE MODE INITIALIZERS
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
                start = 501
            self.state.starting_score = start
            for p in self.state.players:
                if p.score == 501 and not p.throws:
                    p.score = start - self.state.handicaps.get(p.name, 0)

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
    # SUB-ENGINE INITIALIZERS (wrap standalone game mode classes)
    # =========================================================================

    def _init_subengine_countup(self):
        pnames = [p.name for p in self.state.players]
        rounds = 8 if self.state.mode == "count_up" else 8
        self.state.sub_engine = CountUpGame(pnames, rounds)

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
        lives = 3 if self.state.variant not in ["easy", "hard"] else (5 if self.state.variant == "easy" else 1)
        self.state.sub_engine = GotchaGame(pnames, lives)

    def _init_subengine_team_atc(self):
        # Team ATC: group players into teams of 2
        pnames = [p.name for p in self.state.players]
        if len(pnames) >= 4:
            teams = [
                {"name": f"Team {i+1}", "players": pnames[i:i+2]}
                for i in range(0, len(pnames), 2)
            ]
        else:
            teams = [{"name": f"Team {i+1}", "players": [pnames[i]]}
                     for i in range(len(pnames))]
        self.state.sub_engine = TeamRoundTheClock(teams)

    def _init_subengine_eliminator(self):
        pnames = [p.name for p in self.state.players]
        start = int(self.state.variant) if self.state.variant.isdigit() else 501
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
        # Use variant to pass joker config (e.g., "1,5,10,20" or "classic")
        if self.state.variant == "classic":
            config = PRESET_CLASSIC
        else:
            # Parse joker numbers from variant string
            try:
                joker_nums = [int(x.strip()) for x in self.state.variant.split(",")]
                builder = TacticsJokerBuilder()
                builder.add_jokers(joker_nums)
                config = builder.build()
            except:
                config = PRESET_CLASSIC
        
        self.state.sub_engine = TacticsJokerGame(pnames, config)

    def _init_subengine_killer(self):
        pnames = [p.name for p in self.state.players]
        self.state.sub_engine = KillerGame(pnames)

    def _init_subengine_golf(self):
        pnames = [p.name for p in self.state.players]
        self.state.sub_engine = DartsGolf(pnames)

    def _init_subengine_tictactoe(self):
        pnames = [p.name for p in self.state.players]
        if len(pnames) >= 2:
            self.state.sub_engine = TicTacToeDarts(pnames[0], pnames[1])

    def _init_subengine_shanghai(self):
        pnames = [p.name for p in self.state.players]
        self.state.sub_engine = ShanghaiChampionship(pnames)

    def _init_subengine_bob27(self):
        pname = self.state.players[0].name if self.state.players else "Player"
        self.state.sub_engine = Bob27(pname)

    def _init_subengine_121(self):
        pname = self.state.players[0].name if self.state.players else "Player"
        self.state.sub_engine = Game121(pname)

    def _init_subengine_halveit(self):
        pnames = [p.name for p in self.state.players]
        self.state.sub_engine = HalveIt(pnames)

    # =========================================================================
    # CORE: Record a throw
    # =========================================================================

    def record_throw(self, dart_scores: List[int]) -> str:
        """Record a throw and return result message."""
        if self.state.winner:
            return "Game already has a winner."

        player = self.state.current_player()
        if not player:
            return "No current player."

        # Save snapshot for undo
        snapshot = self.state.to_snapshot()
        self.state.undo_stack.append(snapshot)
        self.state.redo_stack.clear()

        # Route to appropriate handler
        if self.state.mode in self.NATIVE_X01:
            msg = self._process_x01_throw(player, dart_scores)
        elif self.state.mode in self.NATIVE_CRICKET:
            msg = self._process_cricket_throw(player, dart_scores)
        elif self.state.mode == "bobs_27":
            msg = self._process_bobs27_throw(player, dart_scores)
        elif self.state.mode == "around_the_clock":
            msg = self._process_atc_throw(player, dart_scores)
        elif self.state.mode == "shanghai":
            msg = self._process_shanghai_throw(player, dart_scores)
        elif self.state.mode == "killer":
            msg = self._process_killer_throw(player, dart_scores)
        elif self.state.mode == "half_it":
            msg = self._process_half_it_throw(player, dart_scores)
        elif self.state.sub_engine:
            msg = self._process_subengine_throw(dart_scores)
        elif self.state.mode in self.SUBENGINE_CHASE_DRAGON:
            msg = self._process_subengine_throw(dart_scores)
        else:
            msg = f"{player.name} scored {sum(dart_scores[:3])}"

        # Build TurnRecord
        darts = dart_scores[:3] if dart_scores else [0, 0, 0]
        total = sum(darts)
        record = TurnRecord(
            turn_number=self.state.turn_number,
            player_name=player.name,
            darts=darts,
            total=total,
            message=msg,
            score_after=player.score,
            is_one_eighty=(total == 180),
            is_hundred_plus=(total >= 100),
        )
        self.state.history.append(record)

        # Advance turn unless game over
        if not self.state.winner:
            self._advance_turn()

        return msg

    def _process_subengine_throw(self, darts: List[int]) -> str:
        """Route throw to sub-engine and sync winner state."""
        se = self.state.sub_engine
        if not se:
            return "No sub-engine active"
        
        # Handle special case modes with different APIs
        if isinstance(se, TeamRoundTheClock):
            # Team ATC uses hit/miss, not dart scores - use first dart as hit indicator
            hit = sum(darts[:3]) > 0
            msg = se.record_hit(hit)
        elif isinstance(se, RoadrunnerGame):
            msg = se.play_round(darts[:3])
        elif isinstance(se, Escalator20Game):
            # Escalator is turn-based level progression, not per-throw
            msg = f"{se.player}: {sum(darts[:3])}pts (Level {se.current_level_idx + 1})"
        elif isinstance(se, EliminatorGame):
            current_player = self.state.current_player()
            msg = se.record_throw(current_player.name, darts[:3])
        else:
            # Standard API: record_throw(darts) -> str
            msg = se.record_throw(darts[:3])
        
        # Sync winner from sub-engine
        if hasattr(se, 'winner') and se.winner:
            self.state.winner = se.winner
            # Update legs won
            if se.winner in self.state.legs_won:
                self.state.legs_won[se.winner] += 1
                if self.state.legs_won[se.winner] >= self.state.legs_to_win:
                    self.state.match_winner = se.winner
        
        return msg

    # =========================================================================
    # NATIVE THROW PROCESSORS
    # =========================================================================

    def _process_x01_throw(self, player: Player, dart_scores: List[int]) -> str:
        darts = dart_scores[:3] if dart_scores else [0, 0, 0]
        total = sum(darts)
        starting = player.score
        new_score = starting - total

        if new_score < 0:
            return f"BUST! {player.name} stays at {starting}"
        if new_score == 0:
            last_dart = darts[-1] if darts else 0
            if self._is_valid_finish(last_dart):
                player.score = 0
                self.state.legs_won[player.name] = self.state.legs_won.get(player.name, 0) + 1
                if self.state.legs_won[player.name] >= self.state.legs_to_win:
                    self.state.match_winner = player.name
                    self.state.winner = player.name
                    darts_used = len([d for d in darts if d > 0]) or 3
                    return f"CHECKOUT! {player.name} wins the match in {darts_used} darts!"
                self.state.winner = player.name
                return f"CHECKOUT! {player.name} wins the leg!"
            else:
                return f"BUST! Must finish on a double. Back to {starting}"
        if new_score == 1:
            return f"BUST! Score of 1 is impossible. Back to {starting}"

        player.score = new_score
        player.throws.append(darts)
        msg = f"{player.name}: {total} -> {new_score}"
        if total == 180:
            msg += " | ONE HUNDRED AND EIGHTY!"
        elif total >= 140:
            msg += " | TON PLUS!"
        elif total >= 100:
            msg += " | TON!"
        return msg

    def _is_valid_finish(self, dart_score: int) -> bool:
        if dart_score == 50:
            return True
        if dart_score == 25:
            return False
        if dart_score % 2 == 0 and 2 <= dart_score <= 40:
            return True
        return False

    def _process_cricket_throw(self, player: Player, dart_scores: List[int]) -> str:
        darts = dart_scores[:3] if dart_scores else [0, 0, 0]
        targets = [15, 16, 17, 18, 19, 20, 25]
        marks = self.state.cricket_marks[player.name]
        is_cutthroat = self.state.mode == "cut_throat"
        is_noscore = self.state.mode == "no_score_cricket"
        msgs = []
        points_scored = 0

        for dart in darts:
            base, mult = self._parse_dart_value(dart)
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

    def _parse_dart_value(self, dart: int) -> tuple:
        if dart <= 20 and dart > 0:
            return (dart, 1)
        elif dart == 25:
            return (25, 1)
        elif dart == 50:
            return (25, 2)
        elif dart > 20 and dart <= 40 and dart % 2 == 0:
            return (dart // 2, 2)
        elif dart > 20 and dart <= 60 and dart % 3 == 0:
            return (dart // 3, 3)
        return (0, 0)

    def _check_cricket_winner(self):
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

    def _process_bobs27_throw(self, player: Player, dart_scores: List[int]) -> str:
        darts = dart_scores[:3] if dart_scores else [0, 0, 0]
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
                msgs.append("ELIMINATED!")
                self.state.bobs27_lives[player.name] = 0
            elif self.state.variant == "easy":
                score = 0
                msgs.append("(Easy mode - score floored at 0)")
            else:
                lives -= 1
                self.state.bobs27_lives[player.name] = lives
                score = 27
                msgs.append(f"Life lost! {lives} remaining. Score reset to 27")
                if lives <= 0:
                    msgs.append("ELIMINATED!")

        self.state.bobs27_score[player.name] = score
        self.state.bobs27_current_target_idx[player.name] = idx + 1
        if self.state.bobs27_current_target_idx[player.name] >= len(targets):
            msgs.append(f"FINISHED! Final score: {score}")
            if not self.state.winner:
                self.state.winner = player.name
        return " | ".join(msgs)

    def _process_atc_throw(self, player: Player, dart_scores: List[int]) -> str:
        darts = dart_scores[:3] if dart_scores else [0, 0, 0]
        targets = list(range(1, 21)) + [25]
        idx = self.state.atc_targets.get(player.name, 0)
        if idx >= len(targets):
            return f"{player.name}: Already finished!"
        hit_type = self.state.variant if self.state.variant in ["doubles", "triples"] else "single"
        current_target = targets[idx]
        hits = 0
        for dart in darts:
            base, mult = self._parse_dart_value(dart)
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

    def _process_shanghai_throw(self, player: Player, dart_scores: List[int]) -> str:
        darts = dart_scores[:3] if dart_scores else [0, 0, 0]
        if self.state.shanghai_round > len(self.state.shanghai_targets):
            return f"{player.name}: Game over!"
        target = self.state.shanghai_targets[self.state.shanghai_round - 1]
        score = 0
        got_shanghai = False
        msgs = []
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
        player.practice_score = getattr(player, 'practice_score', 0) + score
        if hit_single and hit_double and hit_triple:
            got_shanghai = True
            msgs.append(f"SHANGHAI! {player.name} wins!")
            self.state.winner = player.name
        msgs.append(f"{player.name} Round {self.state.shanghai_round} (aiming {target}): +{score}pts")
        if not got_shanghai:
            self.state.shanghai_round += 1
            if self.state.shanghai_round > len(self.state.shanghai_targets):
                winner = max(self.state.players, key=lambda p: getattr(p, 'practice_score', 0))
                self.state.winner = winner.name
                msgs.append(f"Game over! {winner.name} wins with {getattr(winner, 'practice_score', 0)}pts!")
        return " | ".join(msgs)

    def _process_killer_throw(self, player: Player, dart_scores: List[int]) -> str:
        darts = dart_scores[:3] if dart_scores else [0, 0, 0]
        msgs = []
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
            return " | ".join(msgs)
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
        alive = [p for p in self.state.players if self.state.killer_lives.get(p.name, 0) > 0]
        if len(alive) == 1:
            self.state.winner = alive[0].name
            msgs.append(f"{alive[0].name} wins Killer!")
        if not msgs:
            msgs.append(f"{player.name}: No kills")
        return " | ".join(msgs)

    def _process_half_it_throw(self, player: Player, dart_scores: List[int]) -> str:
        darts = dart_scores[:3] if dart_scores else [0, 0, 0]
        if self.state.half_it_current_target_idx >= len(self.state.half_it_targets):
            return f"{player.name}: Game over!"
        target = self.state.half_it_targets[self.state.half_it_current_target_idx]
        score = self.state.half_it_scores.get(player.name, 0)
        msgs = []
        hit = False
        for dart in darts:
            base, mult = self._parse_dart_value(dart)
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
        if not self.state.undo_stack:
            return False
        current_snap = self.state.to_snapshot()
        self.state.redo_stack.append(current_snap)
        snap = self.state.undo_stack.pop()
        self.state.from_snapshot(snap)
        self.state.winner = None
        return True

    def redo_throw(self) -> bool:
        if not self.state.redo_stack:
            return False
        snap = self.state.redo_stack.pop()
        self.state.from_snapshot(snap)
        return True

    def get_bot_throw(self) -> List[int]:
        if not self.dartbot:
            return [0, 0, 0]
        player = self.state.current_player()
        if not player:
            return [0, 0, 0]
        if self.state.mode in self.NATIVE_X01:
            return self.dartbot.get_throw_x01(player.score)
        elif self.state.mode in self.NATIVE_CRICKET:
            return self.dartbot.get_throw_cricket()
        else:
            return self.dartbot.get_throw_x01(501)

    def start_new_leg(self):
        self.state.winner = None
        self.state.current_leg += 1
        self.state.turn_number = 1
        self.state.current_player_idx = 0
        self.state.history = []
        self.state.undo_stack = []
        self.state.redo_stack = []
        for p in self.state.players:
            p.reset_for_leg(self.state.starting_score - self.state.handicaps.get(p.name, 0))
        # Re-init sub-engine for new leg
        self._init_mode()

    def get_current_player(self) -> Optional[Player]:
        return self.state.current_player()

    def is_game_over(self) -> bool:
        return self.state.winner is not None

    def is_match_over(self) -> bool:
        return self.state.match_winner is not None

    # =========================================================================
    # LEADERBOARD (works for all modes)
    # =========================================================================

    def get_leaderboard(self) -> List[Any]:
        """Return players sorted by game state for ALL modes."""
        m = self.state.mode
        
        # X01: lowest score wins
        if m in self.NATIVE_X01:
            return sorted(self.state.players, key=lambda p: p.score if p.score > 0 else -1)
        
        # Cricket: highest points wins (ascending for cut-throat)
        if m in self.NATIVE_CRICKET:
            reverse = m != "cut_throat"
            return sorted(self.state.players,
                         key=lambda p: self.state.cricket_points.get(p.name, 0),
                         reverse=reverse)
        
        # Bob's 27: highest score wins
        if m == "bobs_27":
            return sorted(self.state.players,
                         key=lambda p: self.state.bobs27_score.get(p.name, 0),
                         reverse=True)
        
        # Half It: highest score wins
        if m == "half_it":
            return sorted(self.state.players,
                         key=lambda p: self.state.half_it_scores.get(p.name, 0),
                         reverse=True)
        
        # Sub-engine modes: delegate to sub-engine
        if self.state.sub_engine:
            se = self.state.sub_engine
            # Sort by sub-engine scores if available
            if hasattr(se, 'scores'):
                return sorted(self.state.players,
                             key=lambda p: se.scores.get(p.name, 0),
                             reverse=True)
            if hasattr(se, 'points'):
                return sorted(self.state.players,
                             key=lambda p: se.points.get(p.name, 0),
                             reverse=True)
            # Default: return as-is
            return self.state.players
        
        return self.state.players

    # =========================================================================
    # CHECKOUT & SCOREBOARD
    # =========================================================================

    def get_checkout_suggestion(self, player_name: str = None) -> List[str]:
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
        return get_checkout(score)

    def get_mode_scoreboard(self) -> Dict:
        """Get scoreboard data for the current mode."""
        m = self.state.mode
        result = {
            "mode": m.upper(),
            "turn": self.state.turn_number,
            "current_player": self.state.players[self.state.current_player_idx].name if self.state.players else "",
            "players": [],
            "extra": {},
        }
        
        for p in self.state.players:
            entry = {"name": p.name, "is_current": p == self.state.current_player()}
            
            if m in self.NATIVE_X01:
                entry["score"] = p.score
                entry["display"] = str(p.score) if p.score > 0 else "CHECKOUT"
                entry["average"] = round(sum(sum(t) for t in p.throws) / len(p.throws), 1) if p.throws else 0
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
            elif self.state.sub_engine:
                se = self.state.sub_engine
                if hasattr(se, 'scores') and p.name in se.scores:
                    entry["score"] = se.scores[p.name]
                    entry["display"] = f"{se.scores[p.name]}pts"
                elif hasattr(se, 'points') and p.name in se.points:
                    entry["score"] = se.points[p.name]
                    entry["display"] = f"{se.points[p.name]}pts"
                elif isinstance(se, ChaseTheDragonGame):
                    target_name, _ = se.get_current_target(p.name)
                    entry["display"] = f"Target: {target_name}"
                else:
                    entry["display"] = "Playing"
            else:
                entry["display"] = "Playing"
            
            result["players"].append(entry)
        
        # Mode-specific extra info
        if m == "bermuda" and self.state.sub_engine:
            result["extra"]["target"] = str(self.state.sub_engine.get_current_target())
        elif m == "jdc" and self.state.sub_engine:
            tname, tval = self.state.sub_engine.get_current_target()
            result["extra"]["target"] = f"{tname} ({tval})"
        elif m == "shanghai":
            result["extra"]["round"] = f"{self.state.shanghai_round}/{len(self.state.shanghai_targets)}"
        elif m == "half_it":
            tidx = self.state.half_it_current_target_idx
            if tidx < len(self.state.half_it_targets):
                result["extra"]["target"] = self.state.half_it_targets[tidx]
        elif self.state.sub_engine:
            se = self.state.sub_engine
            if hasattr(se, 'get_current_target'):
                try:
                    res = se.get_current_target()
                    if isinstance(res, tuple): result["extra"]["target"] = res[0]
                    else: result["extra"]["target"] = str(res)
                except:
                    try:
                        res = se.get_current_target(self.state.players[self.state.current_player_idx].name)
                        if isinstance(res, tuple): result["extra"]["target"] = res[0]
                        else: result["extra"]["target"] = str(res)
                    except: pass
        
        return result

    def record_bounce_out(self, player_name: str, dart_num: int = 1):
        self.bounce_tracker.record_bounce_out(player_name, dart_num)

    def get_match_summary(self) -> dict:
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
                "average": round(sum(sum(t) for t in p.throws) / len(p.throws), 2) if p.throws else 0,
                "one_eighties": sum(1 for t in p.throws if sum(t) == 180),
                "hundreds": sum(1 for t in p.throws if 100 <= sum(t) <= 139),
                "ton_forties": sum(1 for t in p.throws if 140 <= sum(t) <= 179),
            } for p in self.state.players],
        }

    # =========================================================================
    # UTILITY: List all supported modes
    # =========================================================================

    @classmethod
    def get_all_modes(cls) -> Dict[str, List[str]]:
        """Return all supported game modes organized by category."""
        return {
            "X01 Games": cls.NATIVE_X01,
            "Cricket": cls.NATIVE_CRICKET + cls.SUBENGINE_TACTIC_CRICKET + cls.SUBENGINE_RANDOM_CRICKET + cls.SUBENGINE_HAMMER_CRICKET,
            "Practice": cls.NATIVE_PRACTICE + cls.SUBENGINE_COUNT_UP + cls.SUBENGINE_BERMUDA + cls.SUBENGINE_JDC + cls.SUBENGINE_4160,
            "Party": cls.NATIVE_PARTY + cls.SUBENGINE_GOTCHA,
            "Specialty": cls.SUBENGINE_BASEBALL + cls.SUBENGINE_TEAM_ATC + cls.SUBENGINE_ELIMINATOR + cls.SUBENGINE_ROADRUNNER + cls.SUBENGINE_ESCALATOR,
        }
