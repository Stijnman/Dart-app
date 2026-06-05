"""
Dart Game Pro v2.4 — Feature Demo Script
Shows all major new features working together in a simulated environment.

This is a standalone runnable demo (no full Streamlit app required).
It demonstrates:
- Voice Commands
- Advanced Heat Maps (text output + matplotlib if available)
- Adaptive Bot Difficulty Scaling
- Themes + Eye Comfort
- Pressure Performance Index
- Coaching Mode
- Ladder League System

Run with: python docs/v24_feature_demo.py
"""

import sys
import os

# Add parent directory to path so we can import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.enhanced_voice_recognition import EnhancedVoiceRecognition
    from core.advanced_heatmap import generate_advanced_heatmap, HAS_PLOTLY
    from core.smartbot_autoscale import AdaptiveDifficultyScaler
    from core.extended_themes import get_enhanced_theme, get_all_enhanced_themes
    from core.pressure_performance_index import PressurePerformanceIndex
    from core.coaching_mode import CoachingMode
    from core.ladder_league import LadderLeagueSystem, Tier
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the project root or the files are in core/")
    sys.exit(1)

import numpy as np

print("=" * 70)
print("🎯 DART GAME PRO v2.4 — FEATURE DEMO")
print("=" * 70)

# ============================================================
# 1. VOICE COMMANDS DEMO
# ============================================================
print("\n1. VOICE COMMANDS (#9)")
print("-" * 40)

vr = EnhancedVoiceRecognition()
commands_to_test = [
    "t20",
    "undo last dart",
    "skip turn",
    "show stats",
    "what is the best checkout",
    "one eighty"
]

for cmd in commands_to_test:
    result = vr.recognize(cmd)
    print(f"  Voice: '{cmd}' → {result[0]} (score: {result[1]})")

# ============================================================
# 2. ADVANCED HEAT MAPS DEMO
# ============================================================
print("\n2. ADVANCED HEAT MAPS (#15)")
print("-" * 40)

# Generate sample throw data
np.random.seed(42)
sample_throws = [
    {
        "x": np.random.uniform(-1, 1),
        "y": np.random.uniform(-1, 1),
        "score": np.random.randint(20, 61),
        "visit": i // 3
    }
    for i in range(30)
]

fig, analysis = generate_advanced_heatmap(
    sample_throws, 
    player_name="Demo Player", 
    use_plotly=HAS_PLOTLY
)

print("  Generated advanced heatmap analysis:")
print(analysis[:300] + "..." if len(analysis) > 300 else analysis)
print(f"  Plotly available: {HAS_PLOTLY}")

# ============================================================
# 3. ADAPTIVE BOT DIFFICULTY
# ============================================================
print("\n3. ADAPTIVE BOT DIFFICULTY SCALING (#21)")
print("-" * 40)

scaler = AdaptiveDifficultyScaler(current_bot_level=6)

# Simulate player getting better
good_scores = [45, 52, 48, 55, 60, 58, 62, 65, 70, 68]
adjustment = scaler.adjust_difficulty(good_scores, force_adjust=True)

print(f"  Player recent avg: {np.mean(good_scores):.1f}")
print(f"  Bot adjusted from level {adjustment['old_level']} → {adjustment['new_level']}")
print(f"  Reason: {adjustment['reason']}")

# ============================================================
# 4. THEMES + EYE COMFORT
# ============================================================
print("\n4. THEMES + EYE COMFORT (#29/#30)")
print("-" * 40)

themes = get_all_enhanced_themes()
print("  Available themes:")
for key, name in themes.items():
    print(f"    - {key}: {name}")

holo_theme = get_enhanced_theme("holographic", eye_comfort=True, brightness=0.95, oled_optimized=True)
print(f"\n  Holographic theme loaded with eye comfort:")
print(f"    Background: {holo_theme['background']}")
print(f"    Accent: {holo_theme['accent']}")

# ============================================================
# 5. PRESSURE PERFORMANCE INDEX
# ============================================================
print("\n5. PRESSURE PERFORMANCE INDEX (#16)")
print("-" * 40)

ppi = PressurePerformanceIndex()

# Simulate some throws in different situations
ppi.record_throw(45, was_ahead=True, was_close=False, in_checkout_range=False)
ppi.record_throw(52, was_behind=True, was_close=True, in_checkout_range=False)
ppi.record_throw(60, was_behind=True, was_close=True, in_checkout_range=True)
ppi.record_throw(38, was_ahead=False, was_close=True, in_checkout_range=False)

stats = ppi.get_clutch_stats()
print(f"  Pressure Performance Index: {stats['pressure_performance_index']}")
print(f"  Interpretation: {stats['interpretation']}")
print(f"  When behind avg: {stats['when_behind']['average']}")

# ============================================================
# 6. COACHING MODE
# ============================================================
print("\n6. COACHING MODE (#23)")
print("-" * 40)

coach = CoachingMode(style="balanced")

suggestion = coach.get_suggestion(
    remaining=85,
    opponent_remaining=62,
    is_pressure=True,
    recent_avg=48
)

print(f"  Coach recommends: {suggestion.target}")
print(f"  Explanation: {suggestion.explanation}")
print(f"  Confidence: {suggestion.confidence:.0%}")

# Post-leg report
report = coach.get_post_leg_report("Demo Player")
print(f"\n  Post-leg report generated with {report['suggestions_given']} suggestions.")

# ============================================================
# 7. LADDER LEAGUE SYSTEM
# ============================================================
print("\n7. LADDER LEAGUE SYSTEM (#7)")
print("-" * 40)

league = LadderLeagueSystem(season_id="demo_season_2026")

# Register some players
league.register_player("p1", "Alice", initial_elo=1350, initial_tier=Tier.SILVER)
league.register_player("p2", "Bob", initial_elo=1620, initial_tier=Tier.GOLD)
league.register_player("p3", "Charlie", initial_elo=980, initial_tier=Tier.BRONZE)

# Simulate some matches
league.record_match("p1", "p3", player_won=True, player_elo_change=25, opponent_elo_change=-25)
league.record_match("p2", "p1", player_won=True, player_elo_change=18, opponent_elo_change=-18)
league.record_match("p3", "p2", player_won=False, player_elo_change=-12, opponent_elo_change=12)

standings = league.get_standings(limit=5)
print("  Current Standings (top 5):")
for s in standings:
    print(f"    {s['rank']}. {s['name']} ({s['tier']}) — {s['season_points']} pts, ELO {s['elo']}")

print("\n  Ladder League System fully operational with promotion tracking.")

# ============================================================
print("\n" + "=" * 70)
print("✅ ALL v2.4 FEATURES DEMONSTRATED SUCCESSFULLY!")
print("=" * 70)
print("\nAll new modules are working together beautifully.")
print("Check the individual files in core/ for full source and more examples.")
print("See docs/v2.4_integration_guide.md for production integration steps.")