"""
Dart Game Pro v2 Extensions — 30 new features.
Analytics, export, training, tournament, social, and more.
"""

import json
import csv
import io
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict


# ===== FEATURE 8: CHECKOUT SUCCESS BY RANGE =====
def get_checkout_stats_by_range(history: List[Dict]) -> Dict[str, Dict]:
    """Analyze checkout success rate by score range."""
    ranges = {
        "2-20": {"attempts": 0, "success": 0},
        "21-40": {"attempts": 0, "success": 0},
        "41-60": {"attempts": 0, "success": 0},
        "61-80": {"attempts": 0, "success": 0},
        "81-100": {"attempts": 0, "success": 0},
        "101-120": {"attempts": 0, "success": 0},
        "121-140": {"attempts": 0, "success": 0},
        "141-170": {"attempts": 0, "success": 0},
    }
    
    for h in history:
        if not h.get("is_checkout"):
            continue
        remaining = h.get("score_before", 0)
        if remaining <= 20:
            r = "2-20"
        elif remaining <= 40:
            r = "21-40"
        elif remaining <= 60:
            r = "41-60"
        elif remaining <= 80:
            r = "61-80"
        elif remaining <= 100:
            r = "81-100"
        elif remaining <= 120:
            r = "101-120"
        elif remaining <= 140:
            r = "121-140"
        else:
            r = "141-170"
        ranges[r]["success"] += 1
    
    # Count attempts (any throw from that range)
    for h in history:
        score = h.get("score_before", 0)
        if score <= 0:
            continue
        for r_key, (low, high) in [("2-20", (2,20)), ("21-40", (21,40)), ("41-60", (41,60)),
                                      ("61-80", (61,80)), ("81-100", (81,100)), ("101-120", (101,120)),
                                      ("121-140", (121,140)), ("141-170", (141,170))]:
            if low <= score <= high:
                ranges[r_key]["attempts"] += 1
                break
    
    # Calculate percentages
    for r in ranges:
        a = ranges[r]["attempts"]
        ranges[r]["pct"] = round(ranges[r]["success"] / a * 100, 1) if a > 0 else 0
    
    return ranges


# ===== FEATURE 9: BOARD SEGMENT HEATMAP =====
def get_segment_heatmap(throws: List[List[int]]) -> Dict[int, int]:
    """Generate scoring heatmap by board segment (1-20, 25)."""
    heatmap = defaultdict(int)
    
    for throw in throws:
        for dart in throw:
            if dart <= 20 and dart > 0:
                heatmap[dart] += dart  # Score contributed
            elif dart == 25:
                heatmap[25] += 25
            elif dart == 50:
                heatmap[25] += 50
            elif dart <= 40 and dart % 2 == 0:
                heatmap[dart // 2] += dart  # Double
            elif dart <= 60 and dart % 3 == 0:
                heatmap[dart // 3] += dart  # Triple
    
    return dict(heatmap)


# ===== FEATURE 10: 30-DAY PERFORMANCE TREND =====
def get_30day_trend(game_history: List[Dict]) -> List[Dict]:
    """Get daily average over last 30 days."""
    cutoff = (datetime.now() - timedelta(days=30)).isoformat()
    daily = defaultdict(list)
    
    for g in game_history:
        if g.get("date", "") < cutoff:
            continue
        day = g["date"][:10]
        daily[day].append(g.get("average", 0))
    
    trend = []
    for day in sorted(daily.keys()):
        avg = sum(daily[day]) / len(daily[day])
        trend.append({"date": day, "average": round(avg, 1), "games": len(daily[day])})
    
    return trend


# ===== FEATURE 11: CONSISTENCY RATING =====
def get_consistency_rating(throws: List[List[int]]) -> Dict:
    """Calculate consistency metrics."""
    if len(throws) < 3:
        return {"rating": 0, "variance": 0, "std_dev": 0, "description": "Not enough data"}
    
    totals = [sum(t) for t in throws]
    n = len(totals)
    mean = sum(totals) / n
    variance = sum((x - mean) ** 2 for x in totals) / n
    std_dev = variance ** 0.5
    
    # Consistency rating 0-100 (lower variance = higher score)
    # A pro has std_dev around 20-30 from a mean of 85
    # A beginner has std_dev around 40-60
    if mean > 0:
        cv = (std_dev / mean) * 100  # Coefficient of variation
        rating = max(0, min(100, 100 - cv))
    else:
        rating = 0
    
    if rating >= 80:
        desc = "Elite consistency"
    elif rating >= 60:
        desc = "Good consistency"
    elif rating >= 40:
        desc = "Average consistency"
    elif rating >= 20:
        desc = "Inconsistent"
    else:
        desc = "Highly variable"
    
    return {
        "rating": round(rating, 1),
        "variance": round(variance, 2),
        "std_dev": round(std_dev, 2),
        "mean": round(mean, 1),
        "description": desc,
    }


# ===== FEATURE 12 & 13: AI COACH + RECOMMENDED PRACTICE =====
def get_ai_coach_recommendations(stats: Dict) -> List[Dict]:
    """Analyze stats and recommend practice areas."""
    recommendations = []
    
    # Check checkout weakness
    checkout_pct = stats.get("checkout_pct", 0)
    if checkout_pct < 30:
        recommendations.append({
            "area": "Finishing",
            "issue": f"Low checkout rate ({checkout_pct:.0f}%)",
            "recommendation": "Practice Bob's 27 (Hard mode) and D16/D20 drills",
            "priority": "high",
            "game": "bobs_27",
        })
    
    # Check scoring power
    avg = stats.get("average", 0)
    if avg < 45:
        recommendations.append({
            "area": "Scoring",
            "issue": f"Average below 45 ({avg:.1f})",
            "recommendation": "Practice Around the Clock (Triples) for T20 accuracy",
            "priority": "high",
            "game": "around_the_clock",
            "variant": "triples",
        })
    elif avg < 60:
        recommendations.append({
            "area": "Scoring",
            "issue": f"Room for improvement ({avg:.1f})",
            "recommendation": "Focus on Shanghai 20-round for sustained accuracy",
            "priority": "medium",
            "game": "shanghai",
            "variant": "full",
        })
    
    # Check 180s
    ton80s = stats.get("ton_eighties", 0)
    games = stats.get("games_played", 1)
    if ton80s / games < 0.1:
        recommendations.append({
            "area": "Power Scoring",
            "issue": "Few 180s relative to games played",
            "recommendation": "Play 100 Darts at T20 practice sessions",
            "priority": "medium",
            "drill": "t20_accuracy",
        })
    
    # Check consistency
    if stats.get("consistency_rating", 100) < 40:
        recommendations.append({
            "area": "Consistency",
            "issue": "Throw scores vary widely",
            "recommendation": "Focus on form with Around the Clock (Singles) — aim for steady rhythm",
            "priority": "medium",
            "game": "around_the_clock",
            "variant": "single",
        })
    
    if not recommendations:
        recommendations.append({
            "area": "Overall",
            "issue": "Solid all-around play!",
            "recommendation": "Challenge yourself: Play vs Bot level 8+, try Shanghai full",
            "priority": "low",
            "game": "shanghai",
            "variant": "full",
        })
    
    return recommendations


# ===== FEATURE 14: TRAINING PLAN GENERATOR =====
def generate_training_plan(focus_area: str, days: int = 7) -> List[Dict]:
    """Generate a structured multi-day training plan."""
    plans = {
        "finishing": [
            {"day": 1, "activity": "Bob's 27 (Standard) — 3 rounds", "focus": "D1-D7", "target_score": 80},
            {"day": 2, "activity": "Bob's 27 (Hard) — 2 rounds", "focus": "D8-D14", "target_score": 60},
            {"day": 3, "activity": "Around the Clock (Doubles)", "focus": "All doubles", "target": "Complete in <30 darts"},
            {"day": 4, "activity": "Rest or light play", "focus": "Recovery", "target": "Fun games only"},
            {"day": 5, "activity": "Bob's 27 (Standard) — Full 21 targets", "focus": "All doubles", "target_score": 100},
            {"day": 6, "activity": "Play 501 vs Bot (Lv.5)", "focus": "Apply finishing under pressure", "target": "Win 2/3 legs"},
            {"day": 7, "activity": "Test: 170 finish attempts x10", "focus": "Big checkouts", "target": "Complete 3+"},
        ],
        "scoring": [
            {"day": 1, "activity": "Around the Clock (Triples) — Speed run", "focus": "T1-T10", "target": "<40 darts"},
            {"day": 2, "activity": "Shanghai (Quick) x5 games", "focus": "Round numbers 1-7", "target": "Win 3+"},
            {"day": 3, "activity": "501 vs Bot (Lv.4) — Aim for 100+ avg", "focus": "T20 consistency", "target_avg": 85},
            {"day": 4, "activity": "Rest or light play", "focus": "Recovery", "target": "Fun games only"},
            {"day": 5, "activity": "Around the Clock (Triples) — Full run", "focus": "T11-T20 + Bull", "target": "<50 darts"},
            {"day": 6, "activity": "Shanghai (Full) x3 games", "focus": "All 20 rounds", "target": "200+ points"},
            {"day": 7, "activity": "Test: 100 darts at T20", "focus": "Measure accuracy", "target": "40+ hits"},
        ],
        "consistency": [
            {"day": 1, "activity": "Around the Clock (Singles) — 3 attempts", "focus": "Smooth rhythm", "target": "Best score <45 darts"},
            {"day": 2, "activity": "501 vs Bot (Lv.3) — Track every throw", "focus": "No wild misses", "target": "Std dev <25"},
            {"day": 3, "activity": "Killer (3 lives) — Stay focused", "focus": "Steady concentration", "target": "Win 1 game"},
            {"day": 4, "activity": "Rest", "focus": "Recovery", "target": "Light play only"},
            {"day": 5, "activity": "Bob's 27 (Easy) — Complete all targets", "focus": "Controlled doubles", "target": "Score >200"},
            {"day": 6, "activity": "501 x5 legs — Record all scores", "focus": "Identify patterns", "target": "Avg 60+ every leg"},
            {"day": 7, "activity": "Test: Consistency check — 50 throws", "focus": "Measure improvement", "target": "Consistency rating >50"},
        ],
    }
    
    return plans.get(focus_area, plans["scoring"])[:days]


# ===== FEATURE 15: ROUND THE WORLD (TEAM RELAY) =====
class TeamRoundTheClock:
    """Team relay variant of Around the Clock."""
    
    def __init__(self, teams: List[Dict]):
        """teams = [{"name": "Team A", "players": ["Alice", "Bob"]}, ...]"""
        self.teams = teams
        self.team_progress = {t["name"]: 0 for t in teams}  # Index 0-20
        self.current_team_idx = 0
        self.current_player_idx = 0  # Within team
        self.targets = list(range(1, 21)) + [25]
        self.winner = None
        self.history = []
    
    def record_hit(self, hit: bool):
        """Record a hit for current team's current player."""
        team = self.teams[self.current_team_idx]
        tname = team["name"]
        player = team["players"][self.current_player_idx]
        
        current_target_idx = self.team_progress[tname]
        if current_target_idx >= len(self.targets):
            return f"{tname} already finished!"
        
        target = self.targets[current_target_idx]
        
        if hit:
            self.team_progress[tname] += 1
            msg = f"{tname}/{player}: HIT {target}!"
            if self.team_progress[tname] >= len(self.targets):
                self.winner = tname
                msg += f" {tname} WINS!"
        else:
            msg = f"{tname}/{player}: Missed {target}"
        
        self.history.append({"team": tname, "player": player, "target": target, "hit": hit})
        
        # Rotate: next player in team, then next team
        self.current_player_idx = (self.current_player_idx + 1) % len(team["players"])
        if self.current_player_idx == 0:
            self.current_team_idx = (self.current_team_idx + 1) % len(self.teams)
        
        return msg
    
    def get_current_target(self, team_name: str) -> int:
        idx = self.team_progress.get(team_name, 0)
        if idx < len(self.targets):
            return self.targets[idx]
        return -1


# ===== FEATURE 16: BASEBALL DARTS =====
class BaseballDarts:
    """9-innings baseball on the dartboard."""
    
    def __init__(self, players: List[str]):
        self.players = players
        self.scores = {p: [] for p in players}  # Runs per inning
        self.current_inning = 1
        self.current_player_idx = 0
        self.winner = None
    
    def get_inning_target(self) -> str:
        """Get the target segment for current inning."""
        inning_targets = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9}
        # Extra innings if tied
        inn = self.current_inning
        if inn > 9:
            # Use 10->10, 11->11... 20->20, 21->Bull
            target = inn if inn <= 20 else 25
        else:
            target = inning_targets.get(inn, inn)
        return target
    
    def record_throw(self, darts: List[int]) -> str:
        """Record 3 darts for current player in current inning."""
        player = self.players[self.current_player_idx]
        target = self.get_inning_target()
        
        runs = 0
        for dart in darts:
            # Single = 1 run, Double = 2 runs, Triple = 3 runs
            if dart == target:  # Single
                runs += 1
            elif dart == target * 2:  # Double
                runs += 2
            elif dart == target * 3:  # Triple
                runs += 3
        
        # Ensure scores list is long enough
        while len(self.scores[player]) < self.current_inning:
            self.scores[player].append(0)
        self.scores[player][self.current_inning - 1] = runs
        
        msg = f"{player} Inning {self.current_inning} (target {target}): {runs} run{'s' if runs != 1 else ''}"
        
        # Advance
        self.current_player_idx += 1
        if self.current_player_idx >= len(self.players):
            self.current_player_idx = 0
            self.current_inning += 1
        
        # Check for winner after 9 innings
        if self.current_inning > 9:
            self._determine_winner()
        
        return msg
    
    def _determine_winner(self):
        """Determine winner (highest total runs)."""
        totals = {p: sum(scores) for p, scores in self.scores.items()}
        max_runs = max(totals.values())
        winners = [p for p, r in totals.items() if r == max_runs]
        if len(winners) == 1:
            self.winner = winners[0]
    
    def get_scoreboard(self) -> Dict:
        """Get full scoreboard."""
        return {
            p: {
                "innings": scores + ["-"] * (max(9, self.current_inning - 1) - len(scores)),
                "total": sum(scores),
            }
            for p, scores in self.scores.items()
        }


# ===== FEATURE 17: GOTCHA (CHASE THE LEADER) =====
class GotchaGame:
    """Gotcha: Match or beat the leader's score each round."""
    
    def __init__(self, players: List[str], lives: int = 3):
        self.players = players
        self.lives = {p: lives for p in players}
        self.round_leader_score = 0
        self.current_round_scores = {}
        self.current_player_idx = 0
        self.round_num = 1
        self.winner = None
        self.history = []
    
    def record_throw(self, darts: List[int]) -> str:
        """Record throw for current player."""
        player = self.players[self.current_player_idx]
        total = sum(darts)
        self.current_round_scores[player] = total
        
        msgs = [f"{player}: {total}"]
        
        # Update leader score
        if total > self.round_leader_score:
            self.round_leader_score = total
            msgs.append(f"New leader: {total}!")
        
        # Advance
        self.current_player_idx += 1
        if self.current_player_idx >= len(self.players):
            # End of round — check who didn't match leader
            msgs.append(f"--- Round {self.round_num} over. Target: {self.round_leader_score} ---")
            for p in self.players:
                if self.lives.get(p, 0) > 0:
                    score = self.current_round_scores.get(p, 0)
                    if score < self.round_leader_score:
                        self.lives[p] -= 1
                        msgs.append(f"{p} failed to match! Lives: {self.lives[p]}")
                        if self.lives[p] <= 0:
                            msgs.append(f"{p} is OUT!")
            
            # Check winner
            alive = [p for p in self.players if self.lives.get(p, 0) > 0]
            if len(alive) == 1:
                self.winner = alive[0]
                msgs.append(f"{alive[0]} WINS!")
            
            # Reset for next round
            self.current_player_idx = 0
            self.current_round_scores = {}
            self.round_leader_score = 0
            self.round_num += 1
        
        return " | ".join(msgs)


# ===== FEATURE 21: CSV/EXCEL EXPORT =====
def export_stats_csv(player_stats: Dict) -> str:
    """Export player stats as CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Metric", "Value"])
    for key, val in player_stats.items():
        writer.writerow([key.replace("_", " ").title(), val])
    return output.getvalue()


def export_game_history_csv(games: List[Dict]) -> str:
    """Export game history as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Mode", "Winner", "Player", "Average", "180s", "100+", "Checkout%"])
    for g in games:
        for p in g.get("players", []):
            writer.writerow([
                g.get("date", ""),
                g.get("mode", ""),
                g.get("winner", ""),
                p.get("name", ""),
                p.get("average", 0),
                p.get("one_eighties", 0),
                p.get("hundreds", 0) + p.get("ton_forties", 0),
                p.get("checkout_pct", 0),
            ])
    return output.getvalue()


# ===== FEATURE 23: PDF MATCH REPORT =====
def generate_match_report(match_data: Dict) -> str:
    """Generate a formatted text report (PDF-ready)."""
    lines = []
    lines.append("=" * 50)
    lines.append("DART GAME PRO — MATCH REPORT")
    lines.append("=" * 50)
    lines.append(f"Date: {match_data.get('date', datetime.now().isoformat()[:10])}")
    lines.append(f"Mode: {match_data.get('mode', 'Unknown').upper()}")
    lines.append(f"Format: {match_data.get('format', 'Single Game')}")
    lines.append(f"Winner: {match_data.get('winner', 'N/A')}")
    lines.append("")
    lines.append("-" * 50)
    lines.append("PLAYER STATISTICS")
    lines.append("-" * 50)
    
    for p in match_data.get("players", []):
        lines.append(f"\n{p.get('name', 'Unknown')}:")
        lines.append(f"  Throws: {p.get('throws', 0)}")
        lines.append(f"  Average: {p.get('average', 0):.1f}")
        lines.append(f"  180s: {p.get('one_eighties', 0)}")
        lines.append(f"  140+: {p.get('ton_forties', 0)}")
        lines.append(f"  100+: {p.get('hundreds', 0)}")
        lines.append(f"  Best Throw: {p.get('best_throw', 0)}")
    
    lines.append("")
    lines.append("=" * 50)
    lines.append("Generated by Dart Game Pro v2.0")
    lines.append("=" * 50)
    
    return "\n".join(lines)


# ===== FEATURE 19: TV SCOREBOARD =====
def get_tv_scoreboard(game_state) -> Dict:
    """Generate clean scoreboard data for external display."""
    current_p = game_state.players[game_state.current_player_idx] if game_state.players else None
    
    # Extract current target for practice modes
    target = ""
    if game_state.sub_engine and hasattr(game_state.sub_engine, 'get_current_target'):
        try:
            res = game_state.sub_engine.get_current_target()
            if isinstance(res, tuple): target = res[0]
            else: target = str(res)
        except:
            try:
                res = game_state.sub_engine.get_current_target(current_p.name)
                if isinstance(res, tuple): target = res[0]
                else: target = str(res)
            except: pass

    return {
        "mode": game_state.mode.upper(),
        "turn": game_state.turn_number,
        "current_player": current_p.name if current_p else "",
        "target": target,
        "players": [
            {
                "name": p.name,
                "score": p.score,
                "display": str(p.score), # Base score display
                "legs": game_state.legs_won.get(p.name, 0),
                "sets": game_state.sets_won.get(p.name, 0),
                "is_throwing": i == game_state.current_player_idx,
            }
            for i, p in enumerate(game_state.players)
        ],
        "format": game_state.legs_format.value,
    }


# ===== FEATURE 5: SHARE RESULTS =====
def generate_share_text(match_data: Dict) -> str:
    """Generate shareable text for WhatsApp/Social."""
    winner = match_data.get("winner", "Unknown")
    mode = match_data.get("mode", "501").upper()
    lines = [
        f"🎯 Dart Game Pro — {mode} Results",
        f"🏆 Winner: {winner}",
        "",
        "📊 Stats:",
    ]
    for p in match_data.get("players", []):
        avg = p.get("average", 0)
        t80 = p.get("one_eighties", 0)
        lines.append(f"  {p['name']}: {avg:.1f} avg | {t80}x 180s")
    
    lines.append("")
    lines.append("Play at: github.com/Stijnman/Dart-app")
    return "\n".join(lines)


# ===== FEATURE 6: PUBLIC STATS CARD =====
def generate_stats_card(player_name: str, stats: Dict) -> Dict:
    """Generate a shareable stats card."""
    return {
        "player": player_name,
        "title": f"{player_name}'s Dart Stats",
        "games": stats.get("games_played", 0),
        "wins": stats.get("games_won", 0),
        "average": stats.get("overall_avg", 0),
        "best_throw": stats.get("best_throw", 0),
        "one_eighties": stats.get("total_180s", 0),
        "checkout_pct": stats.get("checkout_pct", 0),
        "streak": stats.get("current_streak", 0),
        "card_html": f"""
        <div style="background:linear-gradient(135deg,#1a472a,#0e2a1a);border:2px solid #00cc66;
             border-radius:12px;padding:20px;text-align:center;max-width:300px;">
            <h2 style="color:#00ff88;margin:0;">🎯 {player_name}</h2>
            <div style="color:#ccffcc;font-size:2rem;font-weight:bold;">{stats.get('overall_avg', 0):.1f}</div>
            <div style="color:#888;">3-Dart Average</div>
            <hr style="border-color:#2e7d32;">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;color:#ccc;">
                <div>🎮 {stats.get('games_played', 0)} Games</div>
                <div>🏆 {stats.get('games_won', 0)} Wins</div>
                <div>🔥 {stats.get('total_180s', 0)} 180s</div>
                <div>💎 {stats.get('best_throw', 0)} Best</div>
            </div>
        </div>
        """
    }


# ===== FEATURE 30: BOUNCE-OUT DETECTION =====
class BounceOutTracker:
    """Track bounce-outs (darts that hit board but fall out)."""
    
    def __init__(self):
        self.bounce_outs: Dict[str, int] = defaultdict(int)
        self.bounce_out_history: List[Dict] = []
    
    def record_bounce_out(self, player: str, dart_num: int, intended_target: str = ""):
        """Record a bounce-out."""
        self.bounce_outs[player] += 1
        self.bounce_out_history.append({
            "player": player,
            "dart": dart_num,
            "target": intended_target,
            "time": datetime.now().isoformat(),
        })
    
    def get_count(self, player: str) -> int:
        return self.bounce_outs.get(player, 0)
    
    def get_summary(self) -> Dict:
        return {
            "total": sum(self.bounce_outs.values()),
            "by_player": dict(self.bounce_outs),
            "bounce_out_rate": round(len(self.bounce_out_history) / max(sum(self.bounce_outs.values()), 1) * 100, 1),
        }


# ===== FEATURE 1-4: TOURNAMENT ENGINE =====
class TournamentEngine:
    """Knockout and Round-Robin tournament management."""
    
    FORMAT_KNOCKOUT = "knockout"
    FORMAT_ROUND_ROBIN = "round_robin"
    FORMAT_LEAGUE = "league"
    
    def __init__(self, name: str, format_type: str, participants: List[str]):
        self.name = name
        self.format = format_type
        self.participants = participants
        self.matches = []
        self.standings = {p: {"wins": 0, "losses": 0, "points": 0, "legs_for": 0, "legs_against": 0} for p in participants}
        self.current_round = 0
        self.winner = None
        self._generate_bracket()
    
    def _generate_bracket(self):
        """Auto-generate tournament bracket."""
        if self.format == self.FORMAT_ROUND_ROBIN:
            # Everyone plays everyone
            for i, a in enumerate(self.participants):
                for b in self.participants[i+1:]:
                    self.matches.append({
                        "round": 0, "player_a": a, "player_b": b,
                        "score_a": 0, "score_b": 0, "completed": False,
                    })
        elif self.format == self.FORMAT_KNOCKOUT:
            import random
            randomized = self.participants.copy()
            random.shuffle(randomized)
            # Pair up
            for i in range(0, len(randomized), 2):
                if i + 1 < len(randomized):
                    self.matches.append({
                        "round": 1, "player_a": randomized[i], "player_b": randomized[i+1],
                        "score_a": 0, "score_b": 0, "completed": False,
                    })
        elif self.format == self.FORMAT_LEAGUE:
            # Round robin + top 4 knockout
            for i, a in enumerate(self.participants):
                for b in self.participants[i+1:]:
                    self.matches.append({
                        "phase": "league", "round": 0,
                        "player_a": a, "player_b": b,
                        "score_a": 0, "score_b": 0, "completed": False,
                    })
    
    def record_result(self, match_idx: int, score_a: int, score_b: int):
        """Record match result."""
        m = self.matches[match_idx]
        m["score_a"] = score_a
        m["score_b"] = score_b
        m["completed"] = True
        
        # Update standings
        pa, pb = m["player_a"], m["player_b"]
        if score_a > score_b:
            self.standings[pa]["wins"] += 1
            self.standings[pa]["points"] += 2
            self.standings[pb]["losses"] += 1
        elif score_b > score_a:
            self.standings[pb]["wins"] += 1
            self.standings[pb]["points"] += 2
            self.standings[pa]["losses"] += 1
        else:
            self.standings[pa]["points"] += 1
            self.standings[pb]["points"] += 1
        
        self.standings[pa]["legs_for"] += score_a
        self.standings[pa]["legs_against"] += score_b
        self.standings[pb]["legs_for"] += score_b
        self.standings[pb]["legs_against"] += score_a
    
    def get_standings(self) -> List[Dict]:
        """Get sorted standings."""
        sorted_s = sorted(
            [(p, s) for p, s in self.standings.items()],
            key=lambda x: (-x[1]["points"], -(x[1]["legs_for"] - x[1]["legs_against"]))
        )
        return [{"player": p, **s} for p, s in sorted_s]
    
    def get_bracket(self) -> List[Dict]:
        """Get bracket visualization data."""
        return [{
            "round": m["round"],
            "player_a": m["player_a"], "player_b": m["player_b"],
            "score": f"{m['score_a']}-{m['score_b']}" if m["completed"] else "vs",
            "completed": m["completed"],
        } for m in self.matches]
    
    def seed_participants(self, rankings: Dict[str, int]):
        """Seed participants by ranking (lower = better)."""
        sorted_p = sorted(self.participants, key=lambda p: rankings.get(p, 999))
        self.participants = sorted_p
        self.matches = []
        self._generate_bracket()
