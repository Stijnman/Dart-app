
"""
Ladder League System for Dart Game Pro v2.4
Implements Feature #7: Ladder League System — Persistent seasonal rankings with promotion/demotion between tiers (Bronze → Silver → Gold → Pro)

This is a full implementation that builds on the existing ELO and CareerMode.

Features:
- Multiple tiers with promotion/relegation thresholds
- Seasonal tracking
- Match results affect ELO + league points
- Automatic promotion/demotion at season end
- Player stats per tier
- Easy integration with existing player/ELO system

Tiers (configurable):
- Bronze (entry)
- Silver
- Gold
- Pro (top)

Usage:
    league = LadderLeagueSystem()
    league.record_match(player_id, opponent_id, player_won=True, player_elo_change=...)
    league.end_season()  # triggers promotions/relegations
    standings = league.get_standings(tier="Gold")
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

class Tier(Enum):
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"
    PRO = "Pro"

@dataclass
class PlayerLeagueStats:
    player_id: str
    name: str
    tier: Tier = Tier.BRONZE
    season_points: int = 0
    matches_played: int = 0
    wins: int = 0
    losses: int = 0
    current_elo: int = 1000
    promotion_points: int = 0
    relegation_points: int = 0

    @property
    def win_rate(self) -> float:
        if self.matches_played == 0:
            return 0.0
        return round(self.wins / self.matches_played * 100, 1)

    @property
    def tier_name(self) -> str:
        return self.tier.value

@dataclass
class Season:
    season_id: str
    start_date: str
    end_date: Optional[str] = None
    active: bool = True

class LadderLeagueSystem:
    """
    Full Ladder League System with promotion/relegation.
    """

    # Tier configuration (easy to tweak)
    TIER_CONFIG = {
        Tier.BRONZE: {"min_elo": 800, "promotion_threshold": 1200, "relegation_threshold": 0},
        Tier.SILVER: {"min_elo": 1200, "promotion_threshold": 1500, "relegation_threshold": 1100},
        Tier.GOLD: {"min_elo": 1500, "promotion_threshold": 1800, "relegation_threshold": 1400},
        Tier.PRO: {"min_elo": 1800, "promotion_threshold": 9999, "relegation_threshold": 1700},
    }

    POINTS_FOR_WIN = 3
    POINTS_FOR_LOSS = 1

    def __init__(self, season_id: Optional[str] = None):
        self.players: Dict[str, PlayerLeagueStats] = {}
        self.current_season = Season(
            season_id=season_id or f"season_{datetime.now().strftime('%Y%m')}",
            start_date=datetime.now().isoformat()
        )
        self.match_history: List[Dict] = []
        self.promotions_relegations: List[Dict] = []

    def register_player(self, player_id: str, name: str, initial_elo: int = 1000, initial_tier: Tier = Tier.BRONZE):
        """Register a new player in the league."""
        if player_id in self.players:
            return self.players[player_id]

        stats = PlayerLeagueStats(
            player_id=player_id,
            name=name,
            tier=initial_tier,
            current_elo=initial_elo
        )
        self.players[player_id] = stats
        return stats

    def record_match(self, 
                     player_id: str, 
                     opponent_id: str, 
                     player_won: bool,
                     player_elo_change: int = 0,
                     opponent_elo_change: int = 0):
        """
        Record the result of a league match.
        Call this after every competitive match.
        """
        if player_id not in self.players:
            self.register_player(player_id, f"Player_{player_id}")
        if opponent_id not in self.players:
            self.register_player(opponent_id, f"Player_{opponent_id}")

        player = self.players[player_id]
        opponent = self.players[opponent_id]

        # Update stats
        player.matches_played += 1
        opponent.matches_played += 1

        if player_won:
            player.wins += 1
            opponent.losses += 1
            player.season_points += self.POINTS_FOR_WIN
            opponent.season_points += self.POINTS_FOR_LOSS
        else:
            player.losses += 1
            opponent.wins += 1
            player.season_points += self.POINTS_FOR_LOSS
            opponent.season_points += self.POINTS_FOR_WIN

        # Update ELO
        player.current_elo += player_elo_change
        opponent.current_elo += opponent_elo_change

        # Record history
        self.match_history.append({
            "timestamp": datetime.now().isoformat(),
            "player_id": player_id,
            "opponent_id": opponent_id,
            "player_won": player_won,
            "player_elo_change": player_elo_change,
            "opponent_elo_change": opponent_elo_change
        })

        # Check for immediate tier changes (optional live promotion)
        self._check_tier_change(player)
        self._check_tier_change(opponent)

    def _check_tier_change(self, player: PlayerLeagueStats):
        """Check if player should be promoted or relegated based on ELO."""
        current_tier = player.tier
        elo = player.current_elo

        for tier, config in self.TIER_CONFIG.items():
            if elo >= config["min_elo"]:
                if tier != current_tier:
                    # Promote or relegate
                    old_tier = current_tier
                    player.tier = tier
                    self.promotions_relegations.append({
                        "player_id": player.player_id,
                        "from_tier": old_tier.value,
                        "to_tier": tier.value,
                        "reason": "ELO threshold crossed",
                        "timestamp": datetime.now().isoformat()
                    })
                    return

    def end_season(self) -> Dict[str, Any]:
        """
        End the current season and process promotions/relegations.
        Returns a summary of changes.
        """
        self.current_season.active = False
        self.current_season.end_date = datetime.now().isoformat()

        changes = []

        for player in self.players.values():
            old_tier = player.tier

            # Apply final ELO-based promotion/relegation
            for tier, config in self.TIER_CONFIG.items():
                if player.current_elo >= config["min_elo"]:
                    if tier != old_tier:
                        player.tier = tier
                        changes.append({
                            "player": player.name,
                            "from": old_tier.value,
                            "to": tier.value,
                            "elo": player.current_elo
                        })
                    break

        # Start new season
        new_season_id = f"season_{(int(self.current_season.season_id.split('_')[1]) + 1)}"
        self.current_season = Season(
            season_id=new_season_id,
            start_date=datetime.now().isoformat()
        )

        # Reset season points for new season
        for player in self.players.values():
            player.season_points = 0
            player.matches_played = 0
            player.wins = 0
            player.losses = 0

        summary = {
            "season_ended": self.current_season.season_id,
            "new_season": new_season_id,
            "tier_changes": changes,
            "total_players": len(self.players)
        }

        return summary

    def get_standings(self, tier: Optional[Tier] = None, limit: int = 20) -> List[Dict]:
        """Get current league standings, optionally filtered by tier."""
        filtered = list(self.players.values())
        if tier:
            filtered = [p for p in filtered if p.tier == tier]

        # Sort by season points, then win rate, then ELO
        filtered.sort(key=lambda p: (-p.season_points, -p.win_rate, -p.current_elo))

        standings = []
        for rank, p in enumerate(filtered[:limit], 1):
            standings.append({
                "rank": rank,
                "player_id": p.player_id,
                "name": p.name,
                "tier": p.tier_name,
                "season_points": p.season_points,
                "matches": p.matches_played,
                "wins": p.wins,
                "losses": p.losses,
                "win_rate": p.win_rate,
                "elo": p.current_elo
            })
        return standings

    def get_player_stats(self, player_id: str) -> Optional[Dict]:
        if player_id not in self.players:
            return None
        p = self.players[player_id]
        return {
            "name": p.name,
            "tier": p.tier_name,
            "season_points": p.season_points,
            "matches_played": p.matches_played,
            "win_rate": p.win_rate,
            "current_elo": p.current_elo,
            "promotion_progress": self._get_promotion_progress(p)
        }

    def _get_promotion_progress(self, player: PlayerLeagueStats) -> Dict:
        config = self.TIER_CONFIG[player.tier]
        if player.tier == Tier.PRO:
            return {"status": "Top tier", "progress": 100}

        next_tier = list(Tier)[list(Tier).index(player.tier) + 1]
        needed = config["promotion_threshold"] - player.current_elo
        progress = min(100, max(0, int((player.current_elo - config["min_elo"]) / (config["promotion_threshold"] - config["min_elo"]) * 100)))

        return {
            "next_tier": next_tier.value,
            "elo_needed": max(0, needed),
            "progress_percent": progress
        }

    def export_season_data(self) -> Dict:
        """Export current season for backup or analysis."""
        return {
            "season": self.current_season.season_id,
            "players": {pid: {
                "name": p.name,
                "tier": p.tier_name,
                "points": p.season_points,
                "elo": p.current_elo,
                "win_rate": p.win_rate
            } for pid, p in self.players.items()},
            "match_count": len(self.match_history)
        }


# Example integration
"""
# In your CareerMode or match result handler:
league = st.session_state.get('ladder_league') or LadderLeagueSystem()
st.session_state.ladder_league = league

# After a ranked match:
league.record_match(
    player_id=current_player.id,
    opponent_id=opponent.id,
    player_won=player_won,
    player_elo_change=elo_change,
    opponent_elo_change=-elo_change
)

# Show standings
standings = league.get_standings(tier=Tier.GOLD)
st.dataframe(standings)

# End of season button (admin or scheduled)
if st.button("End Season"):
    summary = league.end_season()
    st.success(f"Season ended! {len(summary['tier_changes'])} players promoted/relegated.")
"""
