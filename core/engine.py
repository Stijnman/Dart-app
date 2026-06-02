"""
Comprehensive Dart Game Engine — All game modes with full rules.
Handles X01 (with all in/out variants), Cricket, Cut-Throat, practice games, and party games.
"""

import random
from typing import List, Optional, Dict, Tuple
from .game_state import GameState, InOutRule, MatchFormat, TurnRecord
from .player import Player
from .checkout import get_checkout, is_checkable_score
from .constants import (
    BOBS_27_CONFIG, SHANGHAI_CONFIG, HALF_IT_CONFIG, 
    KILLER_CONFIG, AROUND_THE_CLOCK_CONFIG
)
from .dartbot import DartBot
from .extensions import BounceOutTracker


class DartGameEngine:
    """Universal dart game engine supporting all major game modes."""
    
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
        
        # Configure match format
        self._configure_match()
        
        # Initialize players
        self._init_players()
        
        # Initialize bot
        if bot_enabled:
            self.dartbot = DartBot(bot_difficulty)
            # Mark last player as bot
            if self.state.players:
                self.state.bot_player_idx = len(self.state.players) - 1
        else:
            self.dartbot = None
        self.bounce_tracker = BounceOutTracker()
        
        # Override starting score if provided (custom starting score feature)
        if starting_score is not None and self.state.mode in ["x01", "101", "170", "201", "210", "301", "501", "701", "901", "1001", "1501"]:
            self.state.starting_score = starting_score
            for p in self.state.players:
                p.score = starting_score - self.state.handicaps.get(p.name, 0)
        
        # Initialize game-specific state
        if self.state.mode in ["cricket", "cut_throat", "no_score_cricket"]:
            self._init_cricket()
        elif self.state.mode == "bobs_27":
            self._init_bobs27()
        elif self.state.mode == "around_the_clock":
            self._init_atc()
        elif self.state.mode == "shanghai":
            self._init_shanghai()
        elif self.state.mode == "killer":
            self._init_killer()
        elif self.state.mode == "half_it":
            self._init_half_it()
        elif self.state.mode in ["x01", "101", "170", "201", "210", "301", "501", "701", "901", "1001", "1501"]:
            self._init_x01()
    
    def _configure_match(self):
        """Set legs/sets to win based on format."""
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
        
        # Initialize legs/sets tracking
        for p in self.state.players:
            self.state.legs_won[p.name] = 0
            self.state.sets_won[p.name] = 0
    
    def _init_players(self):
        """Set starting scores for all players."""
        if self.state.mode in ["x01", "101", "170", "201", "210", "301", "501", "701", "901", "1001", "1501"]:
            # Parse starting score from mode name
            try:
                start = int(self.state.mode)
            except ValueError:
                start = 501
            self.state.starting_score = start
            for p in self.state.players:
                # Only reset if player hasn't been manually configured
                # (score is still default 501 and no throws recorded)
                if p.score == 501 and not p.throws:
                    p.score = start - self.state.handicaps.get(p.name, 0)
                    p.throws = []
    
    def _init_x01(self):
        """Initialize X01 game state."""
        pass  # Handled in _init_players
    
    def _init_cricket(self):
        """Initialize Cricket/Cut-Throat/No-Score state."""
        targets = [15, 16, 17, 18, 19, 20, 25]
        for p in self.state.players:
            self.state.cricket_marks[p.name] = {t: 0 for t in targets}
            self.state.cricket_points[p.name] = 0
    
    def _init_bobs27(self):
        """Initialize Bob's 27."""
        for p in self.state.players:
            self.state.bobs27_score[p.name] = 27
            self.state.bobs27_current_target_idx[p.name] = 0
            if self.state.variant == "easy":
                self.state.bobs27_lives[p.name] = 999  # No elimination
            elif self.state.variant == "hard":
                self.state.bobs27_lives[p.name] = 1  # One miss = out
            else:
                self.state.bobs27_lives[p.name] = 3  # Standard
    
    def _init_atc(self):
        """Initialize Around the Clock."""
        targets = list(range(1, 21)) + [25]
        for p in self.state.players:
            self.state.atc_targets[p.name] = 0  # Index into targets list
    
    def _init_shanghai(self):
        """Initialize Shanghai."""
        # 7 rounds for quick, 20 for full
        rounds = 7 if self.state.variant == "quick" else 20
        self.state.shanghai_targets = list(range(1, rounds + 1))
        self.state.shanghai_round = 1
    
    def _init_killer(self):
        """Initialize Killer."""
        lives = 3  # Default
        for p in self.state.players:
            self.state.killer_lives[p.name] = lives
            self.state.killer_claimed[p.name] = None
        self.state.killer_available = list(range(1, 21))
    
    def _init_half_it(self):
        """Initialize Half It."""
        targets = ["15", "16", "17", "18", "19", "20", "Bull", "D", "T"]
        self.state.half_it_targets = targets
        self.state.half_it_current_target_idx = 0
        for p in self.state.players:
            self.state.half_it_scores[p.name] = 0
    
    # =========================================================================
    # CORE: Record a throw
    # =========================================================================
    
    def record_throw(self, dart_scores: List[int]) -> str:
        """Record a throw and return a message describing the result."""
        if self.state.winner:
            return "Game already has a winner."
        
        player = self.state.current_player()
        if not player:
            return "No current player."
        
        # Save snapshot for undo
        snapshot = self.state.to_snapshot()
        self.state.undo_stack.append(snapshot)
        self.state.redo_stack.clear()  # Clear redo on new action
        
        # Clamp to 3 darts
        darts = dart_scores[:3] if dart_scores else [0, 0, 0]
        total = sum(darts)
        
        record = TurnRecord(
            turn_number=self.state.turn_number,
            player_name=player.name,
            darts=darts,
            total=total,
            message="",
            score_after=player.score,
            is_one_eighty=(total == 180),
            is_hundred_plus=(total >= 100),
        )
        
        # Route to game mode handler
        if self.state.mode in ["x01", "101", "170", "201", "210", "301", "501", "701", "901", "1001", "1501"]:
            msg = self._process_x01_throw(player, darts, total, record)
        elif self.state.mode in ["cricket", "cut_throat", "no_score_cricket"]:
            msg = self._process_cricket_throw(player, darts, total, record)
        elif self.state.mode == "bobs_27":
            msg = self._process_bobs27_throw(player, darts, total, record)
        elif self.state.mode == "around_the_clock":
            msg = self._process_atc_throw(player, darts, total, record)
        elif self.state.mode == "shanghai":
            msg = self._process_shanghai_throw(player, darts, total, record)
        elif self.state.mode == "killer":
            msg = self._process_killer_throw(player, darts, total, record)
        elif self.state.mode == "half_it":
            msg = self._process_half_it_throw(player, darts, total, record)
        else:
            msg = f"{player.name} scored {total}"
        
        record.message = msg
        self.state.history.append(record)
        
        # Advance turn unless game is over
        if not self.state.winner:
            self._advance_turn()
        
        return msg
    
    def _process_x01_throw(self, player: Player, darts: List[int], total: int, record: TurnRecord) -> str:
        """Process X01 throw with full double-out and bust detection."""
        starting = player.score
        new_score = starting - total
        
        # Check bust
        if new_score < 0:
            record.is_bust = True
            record.score_after = starting
            return f"BUST! {player.name} stays at {starting}"
        
        # Check if we need double-out
        if new_score == 0:
            last_dart = darts[-1] if darts else 0
            is_double = self._is_valid_finish(last_dart)
            
            if is_double:
                player.score = 0
                record.score_after = 0
                record.is_checkout = True
                darts_used = len([d for d in darts if d > 0]) or 3
                
                # Check for match win
                self.state.legs_won[player.name] = self.state.legs_won.get(player.name, 0) + 1
                
                if self.state.legs_won[player.name] >= self.state.legs_to_win:
                    self.state.match_winner = player.name
                    self.state.winner = player.name
                    return f"CHECKOUT! {player.name} wins the match in {darts_used} darts! ({self.state.legs_to_win} legs)"
                
                self.state.winner = player.name  # Leg winner
                return f"CHECKOUT! {player.name} wins the leg in {darts_used} darts! ({self.state.legs_won[player.name]}/{self.state.legs_to_win})"
            else:
                record.is_bust = True
                record.score_after = starting
                return f"BUST! Must finish on a double. Back to {starting}"
        
        # Check for no-checkable score (1, or scores that can't be finished)
        if new_score == 1:
            record.is_bust = True
            record.score_after = starting
            return f"BUST! Score of 1 is impossible. Back to {starting}"
        
        # Check if score is uncheckable (>170 or impossible)
        # Allow any score down to 2 (will check later on checkout attempt)
        if new_score > 170:
            pass  # Still playing, fine
        
        player.score = new_score
        player.throws.append(darts)
        record.score_after = new_score
        
        # Build message
        msg_parts = [f"{player.name}: {total} → {new_score}"]
        if total == 180:
            msg_parts.append("ONE HUNDRED AND EIGHTY!")
        elif total >= 140:
            msg_parts.append("TON PLUS!")
        elif total >= 100:
            msg_parts.append("TON!")
        
        return " | ".join(msg_parts)
    
    def _is_valid_finish(self, dart_score: int) -> bool:
        """Check if a raw dart score represents a valid double finish.
        
        Valid finishes:
        - 50 = Bull (inner bull, counts as double)
        - Any even number from 2-40 = D1 through D20
        """
        if dart_score == 50:  # Inner Bull
            return True
        if dart_score == 25:  # Outer Bull - NOT a valid double finish
            return False
        if dart_score % 2 == 0 and 2 <= dart_score <= 40:
            return True
        return False
    
    def _process_cricket_throw(self, player: Player, darts: List[int], total: int, record: TurnRecord) -> str:
        """Process Cricket throw with full scoring logic."""
        targets = [15, 16, 17, 18, 19, 20, 25]
        marks = self.state.cricket_marks[player.name]
        points = self.state.cricket_points[player.name]
        
        is_cutthroat = self.state.mode == "cut_throat"
        is_noscore = self.state.mode == "no_score_cricket"
        
        msgs = []
        points_scored = 0
        
        for dart in darts:
            # Parse dart score into (base, multiplier)
            base, mult = self._parse_dart_value(dart)
            if base not in targets:
                continue
            
            # Determine marks
            new_marks = marks.get(base, 0) + mult
            marks[base] = min(new_marks, 3)  # Cap at 3 (closed)
            
            # Check if this player just closed this number
            if new_marks >= 3 and base not in self.state.cricket_closed:
                self.state.cricket_closed[base] = player.name
                msgs.append(f"{base} CLOSED by {player.name}")
            
            # Check for points (only if we have more marks than needed)
            excess = new_marks - 3
            if excess > 0 and not is_noscore:
                # Points: only score if opponents haven't closed this number
                for opp in self.state.players:
                    if opp.name == player.name:
                        continue
                    opp_marks = self.state.cricket_marks.get(opp.name, {}).get(base, 0)
                    if opp_marks < 3:  # Opponent hasn't closed
                        if is_cutthroat:
                            # In cut-throat, points go TO opponents
                            self.state.cricket_points[opp.name] = self.state.cricket_points.get(opp.name, 0) + (base * excess)
                            msgs.append(f"{base}x{excess} → {opp.name} ({is_cutthroat})")
                        else:
                            points_scored += base * excess
        
        if points_scored > 0 and not is_cutthroat:
            self.state.cricket_points[player.name] = points + points_scored
            msgs.append(f"+{points_scored} pts")
        
        # Check for winner (all targets closed by one player)
        self._check_cricket_winner()
        
        if not msgs:
            return f"{player.name}: No scoring marks"
        return f"{player.name}: {' | '.join(msgs)}"
    
    def _parse_dart_value(self, dart: int) -> tuple:
        """Parse a raw dart score into (base, multiplier)."""
        # For now, expect pre-multiplied values
        # Single 1-20 = 1-20, S25=25, Bull=50
        # Double = value * 2, Triple = value * 3
        if dart <= 20 and dart > 0:
            return (dart, 1)  # Single
        elif dart == 25:
            return (25, 1)  # Outer bull single
        elif dart == 50:
            return (25, 2)  # Bull (counts as double on 25)
        elif dart > 20 and dart <= 40 and dart % 2 == 0:
            return (dart // 2, 2)  # Double
        elif dart > 20 and dart <= 60 and dart % 3 == 0:
            return (dart // 3, 3)  # Triple
        return (0, 0)  # Miss
    
    def _check_cricket_winner(self):
        """Check if any player has closed all numbers."""
        targets = [15, 16, 17, 18, 19, 20, 25]
        for p in self.state.players:
            marks = self.state.cricket_marks.get(p.name, {})
            if all(marks.get(t, 0) >= 3 for t in targets):
                # For standard cricket, also need highest or tied points
                if self.state.mode == "no_score_cricket":
                    self.state.winner = p.name
                    return
                # For standard cricket: closed all + most points
                my_points = self.state.cricket_points.get(p.name, 0)
                all_points = [self.state.cricket_points.get(op.name, 0) for op in self.state.players]
                if my_points >= max(all_points):
                    self.state.winner = p.name
                    return
    
    def _process_bobs27_throw(self, player: Player, darts: List[int], total: int, record: TurnRecord) -> str:
        """Process Bob's 27 throw."""
        targets = list(range(1, 21)) + [25]
        idx = self.state.bobs27_current_target_idx.get(player.name, 0)
        if idx >= len(targets):
            return f"{player.name}: All targets completed!"
        
        target = targets[idx]
        score = self.state.bobs27_score.get(player.name, 27)
        
        # Check if any dart hit a double of the target number
        # D1=2, D2=4, D3=6... D20=40, D25=50
        hits = 0
        for dart in darts:
            # Direct check: did we hit the double value?
            if dart == target * 2:  # Double hit
                hits += 1
            elif target == 25 and dart == 50:  # Double bull
                hits += 1
        
        if hits > 0:
            score += target * hits
            msgs = [f"{player.name}: D{target} HIT! +{target * hits}pts"]
        else:
            score -= target
            msgs = [f"{player.name}: D{target} MISSED! -{target}pts"]
        
        # Check elimination
        lives = self.state.bobs27_lives.get(player.name, 3)
        if score <= 0:
            if self.state.variant == "hard":
                msgs.append("ELIMINATED!")
                self.state.bobs27_lives[player.name] = 0
            elif self.state.variant == "easy":
                score = 0  # Floor at 0 in easy mode
                msgs.append("(Easy mode - score floored at 0)")
            else:
                lives -= 1
                self.state.bobs27_lives[player.name] = lives
                score = 27  # Reset
                msgs.append(f"Life lost! {lives} remaining. Score reset to 27")
                if lives <= 0:
                    msgs.append("ELIMINATED!")
        
        self.state.bobs27_score[player.name] = score
        self.state.bobs27_current_target_idx[player.name] = idx + 1
        
        # Check if all targets done
        if self.state.bobs27_current_target_idx[player.name] >= len(targets):
            msgs.append(f"FINISHED! Final score: {score}")
            if not self.state.winner:
                self.state.winner = player.name
        
        return " | ".join(msgs)
    
    def _process_atc_throw(self, player: Player, darts: List[int], total: int, record: TurnRecord) -> str:
        """Process Around the Clock throw."""
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
                # Check if dart value equals target*2 (D1=2, D2=4, etc.)
                if dart == current_target * 2:
                    hits += 1
                elif current_target == 25 and dart == 50:  # Double bull
                    hits += 1
            elif hit_type == "triples" and base == current_target and mult == 3:
                hits += 1
            elif hit_type == "single" and base == current_target:
                hits += 1
        
        if hits > 0:
            new_idx = min(idx + hits, len(targets))
            self.state.atc_targets[player.name] = new_idx
            next_target = targets[new_idx] if new_idx < len(targets) else "DONE"
            
            if new_idx >= len(targets):
                if not self.state.winner:
                    self.state.winner = player.name
                return f"{player.name}: HIT {current_target}! Around the Clock COMPLETE!"
            return f"{player.name}: HIT {current_target}! Now aiming for {next_target}"
        
        return f"{player.name}: Missed {current_target}, still aiming for {current_target}"
    
    def _process_shanghai_throw(self, player: Player, darts: List[int], total: int, record: TurnRecord) -> str:
        """Process Shanghai throw."""
        if self.state.shanghai_round > len(self.state.shanghai_targets):
            return f"{player.name}: Game over!"
        
        target = self.state.shanghai_targets[self.state.shanghai_round - 1]
        score = 0
        got_shanghai = False
        msgs = []
        
        hit_single = False
        hit_double = False
        hit_triple = False
        
        for dart in darts:
            # For Shanghai, check raw dart values against target multiples
            # S1=1, D1=2, T1=3, S2=2, D2=4, T2=6, etc.
            if dart == target:  # Single
                score += target
                hit_single = True
            elif dart == target * 2:  # Double
                score += target * 2
                hit_double = True
            elif dart == target * 3:  # Triple
                score += target * 3
                hit_triple = True
        
        player.practice_score = player.practice_score + score if hasattr(player, 'practice_score') else score
        
        # Check Shanghai (S+D+T on round number)
        if hit_single and hit_double and hit_triple:
            got_shanghai = True
            msgs.append(f"SHANGHAI! {player.name} wins!")
            self.state.winner = player.name
        
        msgs.append(f"{player.name} Round {self.state.shanghai_round} (aiming {target}): +{score}pts")
        
        if not got_shanghai:
            self.state.shanghai_round += 1
            if self.state.shanghai_round > len(self.state.shanghai_targets):
                # Game over - highest score wins
                winner = max(self.state.players, key=lambda p: getattr(p, 'practice_score', 0))
                self.state.winner = winner.name
                msgs.append(f"Game over! {winner.name} wins with {getattr(winner, 'practice_score', 0)}pts!")
        
        return " | ".join(msgs)
    
    def _process_killer_throw(self, player: Player, darts: List[int], total: int, record: TurnRecord) -> str:
        """Process Killer throw."""
        msgs = []
        
        # Claim phase (first throw for each player)
        if self.state.killer_claimed.get(player.name) is None:
            # Claim based on where they hit
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
        
        # Kill phase
        claimed = self.state.killer_claimed.get(player.name)
        lives_taken = 0
        
        for dart in darts:
            if dart == claimed or dart == claimed * 2 or dart == claimed * 3:
                # Hit own number - kill other players who claimed that number
                for opp in self.state.players:
                    if opp.name != player.name:
                        opp_claimed = self.state.killer_claimed.get(opp.name)
                        if opp_claimed == claimed:
                            self.state.killer_lives[opp.name] = max(0, self.state.killer_lives[opp.name] - 1)
                            lives_taken += 1
                            msgs.append(f"{opp.name} loses a life! ({self.state.killer_lives[opp.name]} left)")
                            if self.state.killer_lives[opp.name] <= 0:
                                msgs.append(f"{opp.name} is OUT!")
        
        # Check for winner (only one player left with lives)
        alive = [p for p in self.state.players if self.state.killer_lives.get(p.name, 0) > 0]
        if len(alive) == 1:
            self.state.winner = alive[0].name
            msgs.append(f"{alive[0].name} wins Killer!")
        
        if not msgs:
            msgs.append(f"{player.name}: No kills")
        
        return " | ".join(msgs)
    
    def _process_half_it_throw(self, player: Player, darts: List[int], total: int, record: TurnRecord) -> str:
        """Process Half It throw."""
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
        
        # Advance target after all players have thrown
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
        """Move to next player, increment turn counter."""
        self.state.current_player_idx = (self.state.current_player_idx + 1) % len(self.state.players)
        if self.state.current_player_idx == 0:
            self.state.turn_number += 1
    
    def undo_last_throw(self) -> bool:
        """Undo the last throw. Returns True if successful."""
        if not self.state.undo_stack:
            return False
        
        # Save current for redo
        current_snap = self.state.to_snapshot()
        self.state.redo_stack.append(current_snap)
        
        # Restore previous state (snapshot already has correct history without last throw)
        snap = self.state.undo_stack.pop()
        self.state.from_snapshot(snap)
        
        self.state.winner = None  # Clear winner so play can continue
        return True
    
    def redo_throw(self) -> bool:
        """Redo a previously undone throw. Returns True if successful."""
        if not self.state.redo_stack:
            return False
        
        snap = self.state.redo_stack.pop()
        self.state.from_snapshot(snap)
        return True
    
    def get_bot_throw(self) -> List[int]:
        """Get the bot's throw if it's the bot's turn."""
        if not self.dartbot:
            return [0, 0, 0]
        
        player = self.state.current_player()
        if not player:
            return [0, 0, 0]
        
        if self.state.mode in ["x01", "101", "170", "201", "210", "301", "501", "701", "901", "1001", "1501"]:
            return self.dartbot.get_throw_x01(player.score)
        elif self.state.mode in ["cricket", "cut_throat"]:
            return self.dartbot.get_throw_cricket()
        else:
            return self.dartbot.get_throw_x01(501)
    
    def start_new_leg(self):
        """Start a new leg after someone wins."""
        self.state.winner = None
        self.state.current_leg += 1
        self.state.turn_number = 1
        self.state.current_player_idx = 0
        self.state.history = []
        self.state.undo_stack = []
        self.state.redo_stack = []
        
        # Reset player scores
        for p in self.state.players:
            p.reset_for_leg(self.state.starting_score - self.state.handicaps.get(p.name, 0))
    
    def get_current_player(self) -> Optional[Player]:
        return self.state.current_player()
    
    def is_game_over(self) -> bool:
        return self.state.winner is not None
    
    def is_match_over(self) -> bool:
        return self.state.match_winner is not None
    
    def get_leaderboard(self) -> List[Player]:
        """Return players sorted by current game state."""
        if self.state.mode in ["x01", "101", "170", "201", "210", "301", "501", "701", "901", "1001", "1501"]:
            return sorted(self.state.players, key=lambda p: p.score if p.score > 0 else -1)
        elif self.state.mode in ["cricket", "cut_throat", "no_score_cricket"]:
            # Sort by points (ascending for cut-throat, descending for standard)
            reverse = self.state.mode != "cut_throat"
            return sorted(self.state.players, 
                         key=lambda p: self.state.cricket_points.get(p.name, 0), 
                         reverse=reverse)
        elif self.state.mode == "bobs_27":
            return sorted(self.state.players, 
                         key=lambda p: self.state.bobs27_score.get(p.name, 0), 
                         reverse=True)
        elif self.state.mode == "half_it":
            return sorted(self.state.players,
                         key=lambda p: self.state.half_it_scores.get(p.name, 0),
                         reverse=True)
        return self.state.players
    
    def get_checkout_suggestion(self, player_name: str = None) -> List[str]:
        """Get checkout suggestions for current or specified player."""
        if player_name:
            player = self.state.get_player_by_name(player_name)
        else:
            player = self.state.current_player()
        
        if not player:
            return []
        
        if self.state.mode not in ["x01", "101", "170", "201", "210", "301", "501", "701", "901", "1001", "1501"]:
            return []
        
        score = player.score
        if score <= 0 or score > 170:
            return []
        
        return get_checkout(score)
    
    def record_bounce_out(self, player_name: str, dart_num: int = 1):
        """Record a bounce-out (dart hit board but fell out). Score = 0 but doesn't count as a miss."""
        self.bounce_tracker.record_bounce_out(player_name, dart_num)
    
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
                "average": round(sum(sum(t) for t in p.throws) / len(p.throws), 2) if p.throws else 0,
                "one_eighties": sum(1 for t in p.throws if sum(t) == 180),
                "hundreds": sum(1 for t in p.throws if 100 <= sum(t) <= 139),
                "ton_forties": sum(1 for t in p.throws if 140 <= sum(t) <= 179),
            } for p in self.state.players],
        }
