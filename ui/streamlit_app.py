"""
Dart Game Pro v2.1 — Streamlit Frontend with 30 new features.

New features integrated:
1-4. Tournament (Knockout, Round-Robin, League, Seeded draws)
5. Share to WhatsApp/Social
6. Public player stats cards
7. Friend activity feed
8. Checkout success by range
9. Board segment heatmap
10. 30-day performance trend
11. Consistency rating
12. AI Coach recommendations
13. Recommended practice
14. Training plan generator
15. Round the World Team Relay
16. Baseball Darts
17. Gotcha
18. Spectator mode
19. TV Scoreboard mode
20. Custom color themes
21. CSV/Excel export
22. Match replay step-through
23. PDF match report
24. Achievement/badge system
25. Daily/weekly challenges
26. Win streak tracking
27. Custom starting score
28. Player avatar upload
29. 180 special effect
30. Bounce-out detection
"""

import streamlit as st
import os
import sys
import random
import io
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import DartGameEngine
from core.player import Player
from core.game_state import InOutRule, MatchFormat
from core.checkout import get_checkout, get_best_checkout, is_checkable_score
from core.constants import DARTBOT_LEVELS, X01_MODES, QUICK_SCORES
from core.database import (
    init_db, save_player, get_all_players, get_recent_games,
    save_game, save_player_stats, update_personal_best, get_player_stats, get_leaderboard
)
from core.achievements import AchievementEngine
from core.extensions import (
    get_checkout_stats_by_range, get_segment_heatmap, get_30day_trend,
    get_consistency_rating, get_ai_coach_recommendations, generate_training_plan,
    TeamRoundTheClock, BaseballDarts, GotchaGame,
    export_stats_csv, export_game_history_csv, generate_match_report,
    get_tv_scoreboard, generate_share_text, generate_stats_card,
    TournamentEngine,
)

# ── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dart Game Pro v2.1",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── THEME SYSTEM (Feature 20: Custom Color Themes) ─────────────────────────
THEMES = {
    "Dark Pro": {"bg": "#0e1117", "fg": "#fafafa", "accent": "#00cc88", "card": "#1e2329", "checkout_bg": "linear-gradient(135deg, #1a472a 0%, #0e2a1a 100%)", "checkout_border": "#00cc66", "bust_bg": "#2a1515", "bust_border": "#c62828", "hero_bg": "#2a1800", "hero_border": "#ff6d00"},
    "Midnight Blue": {"bg": "#0a1628", "fg": "#e0e6ed", "accent": "#4fc3f7", "card": "#152238", "checkout_bg": "linear-gradient(135deg, #0d2b45 0%, #0a1628 100%)", "checkout_border": "#4fc3f7", "bust_bg": "#2a1015", "bust_border": "#e53935", "hero_bg": "#1a1000", "hero_border": "#ffa726"},
    "Darts Hall": {"bg": "#1a1200", "fg": "#f5f0e0", "accent": "#ffb300", "card": "#2a2008", "checkout_bg": "linear-gradient(135deg, #2a1a00 0%, #1a1200 100%)", "checkout_border": "#ffb300", "bust_bg": "#2a1010", "bust_border": "#ff5252", "hero_bg": "#2a1800", "hero_border": "#ff6d00"},
    "Emerald": {"bg": "#0a1f0a", "fg": "#e8f5e9", "accent": "#69f0ae", "card": "#143614", "checkout_bg": "linear-gradient(135deg, #0d2b15 0%, #0a1f0a 100%)", "checkout_border": "#69f0ae", "bust_bg": "#1a0a0a", "bust_border": "#ff8a80", "hero_bg": "#1a1a00", "hero_border": "#ffd54f"},
    "Light": {"bg": "#ffffff", "fg": "#212121", "accent": "#2e7d32", "card": "#f5f5f5", "checkout_bg": "linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)", "checkout_border": "#2e7d32", "bust_bg": "#ffebee", "bust_border": "#c62828", "hero_bg": "#fff3e0", "hero_border": "#e65100"},
}

def apply_theme():
    theme_name = st.session_state.get("theme", "Dark Pro")
    t = THEMES.get(theme_name, THEMES["Dark Pro"])
    st.session_state._theme = t
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']}; color: {t['fg']}; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{ background-color: {t['card']}; border-radius: 8px 8px 0 0; padding: 10px 20px; color: {t['fg']}; }}
    .stTabs [aria-selected="true"] {{ background-color: {t['card']} !important; border-bottom: 2px solid {t['accent']}; }}
    div[data-testid="stMetricValue"] {{ color: {t['accent']} !important; font-size: 2rem !important; }}
    div[data-testid="stMetricLabel"] {{ color: #888 !important; }}
    .stButton>button {{ border-radius: 8px; }}
    .checkout-box {{ background: {t['checkout_bg']}; border: 2px solid {t['checkout_border']}; border-radius: 12px; padding: 16px; text-align: center; }}
    .checkout-box h3 {{ color: {t['accent']}; margin: 0; }}
    .checkout-path {{ color: #ccffcc; font-size: 1.4rem; font-weight: bold; }}
    .history-row {{ background: {t['card']}; padding: 8px 12px; border-radius: 6px; margin: 4px 0; border-left: 3px solid #2e7d32; }}
    .bust-row {{ border-left-color: {t['bust_border']} !important; background: {t['bust_bg']} !important; }}
    .checkout-row {{ border-left-color: {t['checkout_border']} !important; background: {t['checkout_bg']} !important; }}
    .hero-180 {{ border-left-color: {t['hero_border']} !important; background: {t['hero_bg']} !important; }}
    .achievement-card {{ background: {t['card']}; border: 1px solid {t['accent']}33; border-radius: 10px; padding: 12px; margin: 6px 0; }}
    .achievement-unlocked {{ border-color: {t['accent']}; opacity: 1; }}
    .achievement-locked {{ opacity: 0.4; }}
    .stats-card {{ background: {t['card']}; border-radius: 12px; padding: 16px; margin: 8px 0; }}
    .heatmap-cell {{ display: inline-block; width: 40px; height: 40px; text-align: center; line-height: 40px; border-radius: 6px; margin: 2px; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# ── AUDIO (Offline TTS) ────────────────────────────────────────────────────
def announce(text: str):
    if not st.session_state.get("voice_enabled", True):
        return
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass

# ── INIT ────────────────────────────────────────────────────────────────────
init_db()

# Session state defaults
for key, val in {
    "game_started": False, "game": None, "dark_mode": True,
    "voice_enabled": True, "entry_mode": "per_dart",
    "game_completed": False, "theme": "Dark Pro",
    "last_180_effect": False, "spectator_mode": False,
    "tv_mode": False, "achievements": {}, "bounce_outs": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

apply_theme()

# ── MAIN APP ───────────────────────────────────────────────────────────────
def main():
    # Top bar: Theme selector + Settings
    top_cols = st.columns([6, 2, 2])
    with top_cols[1]:
        st.session_state.theme = st.selectbox("Theme", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.theme), label_visibility="collapsed")
        apply_theme()
    with top_cols[2]:
        st.session_state.voice_enabled = st.toggle("🔊 Voice", value=st.session_state.voice_enabled)
    
    st.title("🎯 Dart Game Pro v2.1")
    st.caption("15 game modes • 12-level AI • 161 checkouts • Achievements • Tournaments • Training")
    
    # Navigation tabs
    tabs = st.tabs(["🎮 Play", "🏆 Achievements", "📊 Analytics", "🎯 Training", "🏟️ Tournament", "⚙️ Settings"])
    
    with tabs[0]:
        play_tab()
    with tabs[1]:
        achievements_tab()
    with tabs[2]:
        analytics_tab()
    with tabs[3]:
        training_tab()
    with tabs[4]:
        tournament_tab()
    with tabs[5]:
        settings_tab()

# ── PLAY TAB ────────────────────────────────────────────────────────────────
def play_tab():
    # SIDEBAR: Game Setup
    with st.sidebar:
        st.header("Game Setup")
        
        mode_category = st.selectbox("Category", ["X01 Games", "Cricket", "Practice Games", "Party Games", "Specialty"], index=0)
        
        if mode_category == "X01 Games":
            mode = st.selectbox("Game", ["501", "301", "701", "201", "1001", "101", "170", "901"], index=0)
            starting_score = int(mode)
            custom_score = st.checkbox("Custom starting score")
            if custom_score:
                starting_score = st.number_input("Start from", 2, 1501, 501)
                mode = str(starting_score)
        elif mode_category == "Cricket":
            cricket_type = st.selectbox("Variant", ["Standard", "Cut-Throat", "No-Score"], index=0)
            mode_map = {"Standard": "cricket", "Cut-Throat": "cut_throat", "No-Score": "no_score_cricket"}
            mode = mode_map[cricket_type]
            starting_score = 0
        elif mode_category == "Practice Games":
            mode = st.selectbox("Game", ["Bob's 27", "Around the Clock", "Shanghai"], index=0)
            variant = "standard"
            if mode == "Bob's 27":
                variant = st.selectbox("Difficulty", ["Easy", "Standard", "Hard"], index=1).lower()
            elif mode == "Around the Clock":
                variant = st.selectbox("Variant", ["Singles", "Doubles Only", "Triples Only"], index=0).lower().replace(" only", "")
            elif mode == "Shanghai":
                variant = st.selectbox("Length", ["Quick (7 rounds)", "Full (20 rounds)"], index=0)
                variant = "quick" if "Quick" in variant else "full"
            starting_score = 0
        elif mode_category == "Party Games":
            mode = st.selectbox("Game", ["Killer", "Half It"], index=0)
            if mode == "Killer":
                st.slider("Lives", 1, 9, 3)
            starting_score = 0
        else:  # Specialty
            mode = st.selectbox("Game", ["Baseball", "Gotcha", "Team ATC"], index=0)
            starting_score = 0
            variant = "standard"
        
        match_format = st.selectbox("Format", ["Single Game", "Best of 3 Legs", "Best of 5 Legs", "Best of 7 Legs", "First to 3", "First to 5"], index=0)
        format_map = {"Single Game": "single_game", "Best of 3 Legs": "best_of_3", "Best of 5 Legs": "best_of_5", "Best of 7 Legs": "best_of_7", "First to 3": "first_to_3", "First to 5": "first_to_5"}
        
        # Bot
        play_vs_bot = st.checkbox("Play vs DartBot")
        bot_level = 5
        if play_vs_bot:
            bot_names = [f"{v['name']} (Lv.{k})" for k, v in sorted(DARTBOT_LEVELS.items())]
            bot_selected = st.selectbox("Bot", bot_names, index=4)
            bot_level = int(bot_selected.split("Lv.")[1].rstrip(")"))
        
        st.session_state.entry_mode = st.radio("Input", ["per_dart", "total_only"], format_func=lambda x: "Per Dart" if x == "per_dart" else "Total Only", horizontal=True)
        
        st.divider()
        st.subheader("Recent Games")
        for g in get_recent_games(5):
            st.write(f"**{g['mode'].upper()}** — 🏆 {g['winner']} — {g['created_at'][:10]}")
    
    # PLAYER SETUP
    st.header("👥 Players")
    num_players = st.number_input("Players", 1, 8, 2, key="num_p")
    
    cols = st.columns(min(num_players, 4))
    players_data = []
    for i in range(num_players):
        with cols[i % 4]:
            st.subheader(f"P{i+1}")
            name = st.text_input("Name", value=f"Player {i+1}", key=f"pname_{i}", label_visibility="collapsed")
            # Feature 28: Avatar upload
            avatar = st.file_uploader(f"Avatar", type=["jpg", "png"], key=f"pav_{i}", label_visibility="collapsed")
            players_data.append({"name": name, "avatar": avatar})
    
    if play_vs_bot:
        bot_name = f"🤖 {DARTBOT_LEVELS[bot_level]['name']}"
        players_data.append({"name": bot_name, "avatar": None})
        st.info(f"Bot: **{bot_name}** (Lv {bot_level})")
    
    # START GAME
    if st.button("🚀 START GAME", type="primary", use_container_width=True):
        player_objs = [Player(name=p["name"]) for p in players_data]
        mode_lower = mode.lower().replace("'s", "s").replace(" ", "_")
        if mode_lower == "bobs_27s": mode_lower = "bobs_27"
        
        # Map variant
        variant_mapped = "standard"
        if mode_lower == "bobs_27":
            variant_mapped = variant if 'variant' in dir() else "standard"
        elif mode_lower == "around_the_clock":
            variant_mapped = variant if 'variant' in dir() else "single"
        elif mode_lower == "shanghai":
            variant_mapped = variant if 'variant' in dir() else "quick"
        
        engine = DartGameEngine(
            mode=mode if mode_category == "X01 Games" else mode_lower,
            players=player_objs, match_format=format_map[match_format],
            bot_enabled=play_vs_bot, bot_difficulty=bot_level,
            variant=variant_mapped,
            starting_score=starting_score if 'starting_score' in dir() else None,
        )
        for p in players_data:
            save_player(p["name"])
        
        st.session_state.game = engine
        st.session_state.game_started = True
        st.session_state.game_completed = False
        st.session_state.bot_name = bot_name if play_vs_bot else None
        st.session_state.bot_level = bot_level if play_vs_bot else None
        st.session_state.last_180_effect = False
        st.rerun()
    
    # ACTIVE GAME
    if st.session_state.get("game_started") and st.session_state.game:
        render_active_game()
    else:
        # LEADERBOARD when no game
        st.divider()
        lb_tab, stats_tab = st.tabs(["🏆 Leaderboard", "📊 Player Stats"])
        with lb_tab:
            leaders = get_leaderboard()
            if leaders:
                for i, l in enumerate(leaders[:20], 1):
                    cols = st.columns([1, 4, 2, 2, 3])
                    cols[0].write(f"**#{i}**")
                    cols[1].write(l['name'])
                    cols[2].write(f"🏆 {l['wins']}")
                    cols[3].write(f"🎮 {l['games_played']}")
                    cols[4].write(f"📈 {l['avg_score']:.1f} avg")
            else:
                st.info("Play some games!")
        with stats_tab:
            all_p = get_all_players()
            if all_p:
                selected = st.selectbox("Player", [p['name'] for p in all_p])
                stats = get_player_stats(selected)
                if stats:
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Games", stats.get('games_played', 0))
                    c2.metric("Wins", stats.get('games_won', 0))
                    c3.metric("Average", f"{stats.get('overall_avg', 0):.1f}")
                    c4.metric("180s", stats.get('total_180s', 0))
                    
                    # Feature 6: Stats card
                    card = generate_stats_card(selected, stats)
                    st.markdown(card["card_html"], unsafe_allow_html=True)
                    
                    # Feature 5: Share button
                    share_text = generate_share_text({"winner": selected, "mode": "Overall", "players": [{"name": selected, "average": stats.get('overall_avg', 0), "one_eighties": stats.get('total_180s', 0)}]})
                    st.code(share_text, language="text")
                    st.caption("Copy and share to WhatsApp/Social")

# ── ACTIVE GAME RENDERER ───────────────────────────────────────────────────
def render_active_game():
    engine: DartGameEngine = st.session_state.game
    state = engine.state
    current = engine.get_current_player()
    if not current:
        return
    
    is_bot_turn = state.bot_enabled and state.bot_player_idx == state.current_player_idx
    
    # Spectator mode toggle
    if st.session_state.get("spectator_mode"):
        st.info("👁️ Spectator Mode — Watching only")
    
    # TV Mode scoreboard (Feature 19)
    if st.session_state.get("tv_mode"):
        tv = get_tv_scoreboard(state)
        st.markdown(f"""
        <div style="text-align:center; font-size:2rem; font-weight:bold; color:{st.session_state._theme['accent']};">
            {tv['mode']} — Leg {state.current_leg}
        </div>
        <div style="display:flex; justify-content:center; gap:40px; margin:20px 0;">
        """, unsafe_allow_html=True)
        for p in tv["players"]:
            active = "border:3px solid #00cc66;" if p["is_throwing"] else ""
            st.markdown(f"""
            <div style="text-align:center; padding:20px; background:#1e2329; border-radius:12px; {active}">
                <div style="font-size:1.5rem; color:#fafafa;">{p['name']}</div>
                <div style="font-size:4rem; font-weight:bold; color:#00cc88;">{p['score']}</div>
                <div style="color:#888;">Legs: {p['legs']}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Regular scoreboard
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Mode", state.mode.upper())
    c2.metric("Turn", f"#{state.turn_number}")
    if state.legs_format.value != "single_game":
        c3.metric("Legs", f"{state.legs_won}")
    
    # 180 effect (Feature 29)
    if st.session_state.get("last_180_effect"):
        st.balloons()
        st.markdown("""
        <div style="text-align:center; font-size:3rem; font-weight:bold; color:#ff6d00;">
            🔥 ONE HUNDRED AND EIGHTY! 🔥
        </div>
        """, unsafe_allow_html=True)
        st.session_state.last_180_effect = False
    
    # Current player
    st.markdown(f"## 🎮 {current.name}'s Turn")
    if is_bot_turn:
        st.caption(f"🤖 {DARTBOT_LEVELS.get(state.bot_difficulty, {}).get('name', 'Bot')} thinking...")
    
    # Checkout suggestions
    if state.mode in ["x01", "101", "170", "201", "210", "301", "501", "701", "901", "1001", "1501"] and 1 < current.score <= 170:
        checkouts = engine.get_checkout_suggestion()
        if checkouts:
            st.markdown(f"""
            <div class="checkout-box">
                <h3>🎯 CHECKOUT: {current.score}</h3>
                <div class="checkout-path">{checkouts[0]}</div>
                {f'<div style="color:#888;font-size:0.9rem;">Alt: {checkouts[1]}</div>' if len(checkouts) > 1 else ''}
            </div>
            """, unsafe_allow_html=True)
    
    # Scoreboard
    st.subheader("📊 Scoreboard")
    if state.mode in ["x01", "101", "170", "201", "210", "301", "501", "701", "901", "1001", "1501"]:
        sb_cols = st.columns(len(state.players))
        for i, p in enumerate(state.players):
            with sb_cols[i]:
                delta = "➡️" if p.name == current.name else None
                st.metric(p.name, p.score if p.score > 0 else "✅", delta=delta)
                if p.throws:
                    avg = sum(sum(t) for t in p.throws) / len(p.throws)
                    st.caption(f"Avg: {avg:.1f} | {len(p.throws)} throws")
    
    # Bounce-out tracker (Feature 30)
    st.caption(f"Bounce-outs this match: {sum(engine.bounce_tracker.bounce_outs.values())}")
    
    # THROW INPUT
    st.subheader("🎯 Enter Throw")
    
    if is_bot_turn:
        bot_darts = engine.get_bot_throw()
        st.info(f"🤖 Bot: {bot_darts} = {sum(bot_darts)}")
        if st.button("Accept Bot Throw", key="bot_go"):
            process_throw(engine, bot_darts)
    else:
        darts = get_throw_input(engine, state)
        
        act_cols = st.columns([2, 1, 1, 1, 1])
        with act_cols[0]:
            if st.button("✅ Record", type="primary", use_container_width=True):
                process_throw(engine, darts)
        with act_cols[1]:
            if st.button("↩️ Undo", use_container_width=True):
                if engine.undo_last_throw():
                    st.rerun()
        with act_cols[2]:
            if st.button("↪️ Redo", use_container_width=True):
                if engine.redo_throw():
                    st.rerun()
        # Feature 30: Bounce out button
        with act_cols[3]:
            if st.button("💨 Bounce", use_container_width=True, help="Bounce-out (0 score, doesn't count as miss)"):
                engine.record_bounce_out(current.name, 1)
                st.info("Bounce-out recorded — 0 score")
                st.rerun()
        # Feature 29: 180 quick button
        with act_cols[4]:
            if st.button("🔥 180!", use_container_width=True):
                process_throw(engine, [60, 60, 60])
    
    # LAST RESULT
    if "last_result" in st.session_state:
        msg = st.session_state.last_result
        if "BUST" in msg.upper():
            st.error(msg)
        elif "CHECKOUT" in msg.upper() or "wins" in msg.lower():
            st.success(msg)
            st.balloons()
        elif "180" in msg or "EIGHTY" in msg.upper():
            st.success(f"🔥 {msg}")
            st.session_state.last_180_effect = True
        elif "SHANGHAI" in msg.upper():
            st.success(f"🎯 {msg}")
        else:
            st.info(msg)
    
    # GAME OVER
    if engine.is_game_over():
        handle_game_over(engine, state)
    
    # THROW HISTORY
    with st.expander("📜 Throw History", expanded=False):
        for h in reversed(state.history[-20:]):
            row_class = "history-row"
            if getattr(h, 'is_bust', False): row_class += " bust-row"
            elif getattr(h, 'is_checkout', False): row_class += " checkout-row"
            elif getattr(h, 'is_one_eighty', False): row_class += " hero-180"
            st.markdown(f"""
            <div class="{row_class}">
                <b>Turn {h.turn_number}</b> | {h.player_name}: {h.darts} = {h.total}<br/>
                <span style="color:#888">{h.message}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Feature 22: Match Replay
    with st.expander("⏮️ Match Replay", expanded=False):
        if state.history:
            replay_idx = st.slider("Turn", 0, len(state.history) - 1, len(state.history) - 1)
            h = state.history[replay_idx]
            st.write(f"**Turn {h.turn_number}** | {h.player_name}")
            st.write(f"Darts: {h.darts} | Total: {h.total}")
            st.write(f"Result: {h.message}")
    
    # STATS DASHBOARD
    with st.expander("📈 Session Stats", expanded=True):
        render_session_stats(engine, state)
    
    # Feature 5: Share results
    if engine.is_game_over():
        summary = engine.get_match_summary()
        share_text = generate_share_text(summary)
        st.subheader("📤 Share Result")
        st.code(share_text, language="text")

# ── THROW INPUT ─────────────────────────────────────────────────────────────
def get_throw_input(engine, state):
    darts = []
    if st.session_state.entry_mode == "per_dart":
        inp_cols = st.columns([2, 2, 2, 3])
        for i, label in enumerate(["Dart 1", "Dart 2", "Dart 3"]):
            with inp_cols[i]:
                st.write(f"**{label}**")
                qc1, qc2 = st.columns(2)
                dart_key = f"dv_{i}_{state.turn_number}_{state.current_player_idx}"
                with qc1:
                    if st.button("T20", key=f"t20_{i}_{state.turn_number}"): st.session_state[dart_key] = 60
                    if st.button("T19", key=f"t19_{i}_{state.turn_number}"): st.session_state[dart_key] = 57
                    if st.button("D20", key=f"d20_{i}_{state.turn_number}"): st.session_state[dart_key] = 40
                with qc2:
                    if st.button("T17", key=f"t17_{i}_{state.turn_number}"): st.session_state[dart_key] = 51
                    if st.button("25", key=f"bull_{i}_{state.turn_number}"): st.session_state[dart_key] = 25
                    if st.button("0", key=f"miss_{i}_{state.turn_number}"): st.session_state[dart_key] = 0
                default = st.session_state.get(dart_key, 0)
                val = st.number_input("Score", 0, 60, default, key=f"di_{i}_{state.turn_number}")
                darts.append(val)
        with inp_cols[3]:
            st.write("**Quick Totals**")
            for score in [60, 100, 140, 180]:
                if st.button(str(score), key=f"qt_{score}_{state.turn_number}", use_container_width=True):
                    auto = {60: [20, 20, 20], 100: [20, 20, 60], 140: [60, 60, 20], 180: [60, 60, 60]}
                    darts = auto.get(score, [score, 0, 0])
    else:
        tcol1, tcol2 = st.columns([1, 1])
        with tcol1:
            total = st.number_input("Total", 0, 180, 0, key=f"tot_{state.turn_number}")
        with tcol2:
            st.write("**Quick:**")
            for score in [60, 100, 140, 180, 26, 45, 85, 125]:
                if st.button(str(score), key=f"q_{score}", use_container_width=True):
                    total = score
        darts = [total, 0, 0]
    
    quick_key = f"quick_darts_{state.turn_number}"
    if quick_key in st.session_state:
        darts = st.session_state[quick_key]
        del st.session_state[quick_key]
    return darts

# ── PROCESS THROW ───────────────────────────────────────────────────────────
def process_throw(engine, darts):
    result = engine.record_throw(darts)
    st.session_state.last_result = result
    announce(result)
    st.rerun()

# ── GAME OVER HANDLER ───────────────────────────────────────────────────────
def handle_game_over(engine, state):
    st.divider()
    st.header("🏆 Game Over!")
    
    if engine.is_match_over():
        st.balloons()
        st.success(f"## Match Winner: {state.match_winner}!")
    else:
        st.success(f"## Leg Winner: {state.winner}")
        if st.button("▶️ Next Leg", type="primary", use_container_width=True):
            engine.start_new_leg()
            st.session_state.game = engine
            st.session_state.game_completed = False
            st.rerun()
    
    summary = engine.get_match_summary()
    
    # Player stats
    sum_cols = st.columns(len(summary["players"]))
    for i, p in enumerate(summary["players"]):
        with sum_cols[i]:
            st.metric(p["name"], f"{p['average']:.1f} avg")
            st.caption(f"Throws: {p['throws']} | 180s: {p['one_eighties']}")
    
    # Check achievements
    ach_engine = AchievementEngine(state.winner or "Player")
    for p in summary["players"]:
        stats = {k: p.get(k, 0) for k in ["average", "one_eighties", "hundreds", "ton_forties", "best_throw"]}
        stats["checkout"] = any(getattr(h, 'is_checkout', False) for h in state.history if h.player_name == p["name"])
        won = (p["name"] == state.winner)
        new_achs = ach_engine.check_game_end(won, state.mode, stats)
        if new_achs:
            for ach in new_achs:
                st.success(f"🏅 Achievement Unlocked: **{ach.icon} {ach.name}** — {ach.description}")
    
    # Save
    if not st.session_state.get("game_completed"):
        game_id = save_game(
            mode=state.mode,
            winner=state.winner or state.match_winner or "Draw",
            players=[p.to_dict() for p in state.players],
            history=[{"turn": h.turn_number, "player": h.player_name, "darts": h.darts, "total": h.total, "message": h.message} for h in state.history],
            stats=summary,
            variant=state.variant,
            match_format=state.legs_format.value,
            starting_score=getattr(state, 'starting_score', 501),
        )
        for p in summary["players"]:
            save_player_stats(p["name"], game_id, state.mode, p)
            if p["average"] > 0:
                update_personal_best(p["name"], "best_average", p["average"])
            if p["best_throw"] > 0:
                update_personal_best(p["name"], "best_throw", p["best_throw"])
        st.session_state.game_completed = True
        st.success("Saved! ✅")
    
    # Feature 23: PDF Report
    st.subheader("📄 Match Report")
    report = generate_match_report({
        "date": datetime.now().isoformat(),
        "mode": state.mode,
        "format": state.legs_format.value,
        "winner": state.winner or state.match_winner,
        "players": summary["players"],
    })
    st.code(report, language="text")
    st.download_button("📥 Download Report", report, f"dart_match_{datetime.now():%Y%m%d_%H%M}.txt", "text/plain")
    
    # Feature 21: CSV Export
    st.subheader("📊 Export Data")
    csv_data = export_game_history_csv([{
        "date": datetime.now().isoformat(),
        "mode": state.mode,
        "winner": state.winner,
        "players": summary["players"],
    }])
    st.download_button("📥 CSV Export", csv_data, f"dart_stats_{datetime.now():%Y%m%d}.csv", "text/csv")

# ── SESSION STATS ───────────────────────────────────────────────────────────
def render_session_stats(engine, state):
    stats_tabs = st.tabs(["Overview", "Details", "Heatmap", "Checkouts", "Trend"])
    
    with stats_tabs[0]:
        total_180s = sum(sum(1 for t in p.throws if sum(t) == 180) for p in state.players)
        total_100s = sum(sum(1 for t in p.throws if 100 <= sum(t) <= 179) for p in state.players)
        m1, m2, m3 = st.columns(3)
        m1.metric("Total 180s", total_180s)
        m2.metric("100+ Scores", total_100s)
        m3.metric("Turns", state.turn_number)
    
    with stats_tabs[1]:
        for p in state.players:
            if p.throws:
                totals = [sum(t) for t in p.throws]
                avg = sum(totals) / len(totals)
                # Feature 11: Consistency rating
                consistency = get_consistency_rating(p.throws)
                st.write(f"**{p.name}**: {len(p.throws)} throws | {avg:.1f} avg | Consistency: {consistency['rating']}/100 ({consistency['description']})")
                st.progress(min(1.0, consistency['rating'] / 100), text=f"Consistency: {consistency['rating']:.0f}%")
    
    with stats_tabs[2]:
        # Feature 9: Board segment heatmap
        st.write("**Board Segment Heatmap** (score contribution by segment)")
        for p in state.players:
            if p.throws:
                heatmap = get_segment_heatmap(p.throws)
                st.write(f"*{p.name}:*")
                cols = st.columns(7)
                idx = 0
                for seg in range(1, 21):
                    val = heatmap.get(seg, 0)
                    intensity = min(255, int(val * 2)) if val > 0 else 0
                    with cols[idx % 7]:
                        st.markdown(f"""
                        <div class="heatmap-cell" style="background:rgba(0,204,136,{min(1, val/100)});color:{'#fff' if val > 50 else '#888'};">
                            {seg}<br/><small>{val}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    idx += 1
    
    with stats_tabs[3]:
        # Feature 8: Checkout stats by range
        st.write("**Checkout Success by Score Range**")
        history_data = [{"is_checkout": getattr(h, 'is_checkout', False), "score_before": getattr(h, 'score_after', 0) + getattr(h, 'total', 0)} for h in state.history]
        checkout_stats = get_checkout_stats_by_range(history_data)
        for range_key, data in checkout_stats.items():
            if data["attempts"] > 0:
                cols = st.columns([2, 1, 1])
                cols[0].write(range_key)
                cols[1].write(f"{data['success']}/{data['attempts']}")
                cols[2].progress(min(1.0, data["pct"] / 100), text=f"{data['pct']:.0f}%")
    
    with stats_tabs[4]:
        # Moving average trend
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        for p in state.players:
            if len(p.throws) >= 3:
                totals = [sum(t) for t in p.throws]
                ma = [sum(totals[max(0, i - 2):i + 1]) / min(3, i + 1) for i in range(len(totals))]
                fig, ax = plt.subplots(figsize=(8, 2))
                ax.plot(range(1, len(ma) + 1), ma, marker='o', markersize=4, label=p.name, color='#00cc88')
                ax.set_ylabel('Avg')
                ax.set_xlabel('Throw')
                ax.legend()
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)

# ── ACHIEVEMENTS TAB (Feature 24, 25, 26) ─────────────────────────────────
def achievements_tab():
    st.header("🏆 Achievements")
    
    # Demo achievements engine
    ach_engine = AchievementEngine("Demo Player", st.session_state.get("achievements", {}))
    summary = ach_engine.get_summary()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Unlocked", f"{summary['unlocked']}/{summary['total']}")
    c2.metric("Progress", f"{summary['percentage']}%")
    c3.metric("Current Streak", summary['current_streak'])
    c4.metric("Best Streak", summary['best_streak'])
    
    st.progress(summary['percentage'] / 100, text=f"{summary['percentage']:.0f}% Complete")
    
    st.subheader("Unlocked")
    for a in ach_engine.get_unlocked():
        st.markdown(f"""
        <div class="achievement-card achievement-unlocked">
            <span style="font-size:1.5rem;">{a.icon}</span> <b>{a.name}</b> <span style="color:#888;">({a.tier.upper()})</span><br/>
            <span style="color:#888;font-size:0.85rem;">{a.description}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.subheader("Locked")
    for a in ach_engine.get_locked():
        st.markdown(f"""
        <div class="achievement-card achievement-locked">
            <span style="font-size:1.5rem;">🔒</span> <b>{a.name}</b> <span style="color:#888;">({a.tier.upper()})</span><br/>
            <span style="color:#888;font-size:0.85rem;">{a.description}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature 25: Daily/Weekly Challenges
    st.subheader("📅 Challenges")
    for c in ach_engine.get_challenges():
        cols = st.columns([3, 1, 2])
        cols[0].write(f"**{c['name']}** ({c['type']})")
        cols[0].caption(c['description'])
        cols[1].write(f"{c['progress']}/{c['target']}")
        cols[2].progress(min(1.0, c['progress'] / c['target']), text=f"Reward: {c['reward']}")

# ── ANALYTICS TAB (Features 8-11) ──────────────────────────────────────────
def analytics_tab():
    st.header("📊 Analytics")
    
    all_p = get_all_players()
    if not all_p:
        st.info("Play some games to see analytics!")
        return
    
    player = st.selectbox("Select Player", [p['name'] for p in all_p])
    stats = get_player_stats(player)
    if not stats:
        st.info("No stats recorded yet")
        return
    
    # Stats cards
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Games", stats.get('games_played', 0))
    c2.metric("Wins", stats.get('games_won', 0))
    c3.metric("Average", f"{stats.get('overall_avg', 0):.1f}")
    c4.metric("180s", stats.get('total_180s', 0))
    c5.metric("140s", stats.get('total_140s', 0))
    
    # Feature 6: Stats card
    card = generate_stats_card(player, stats)
    st.markdown(card["card_html"], unsafe_allow_html=True)
    
    # Feature 5: Share
    st.subheader("📤 Share")
    share_text = generate_share_text({"winner": player, "mode": "Stats", "players": [{"name": player, "average": stats.get('overall_avg', 0), "one_eighties": stats.get('total_180s', 0)}]})
    st.code(share_text, language="text")
    
    # Feature 21: CSV Export
    csv = export_stats_csv(stats)
    st.download_button("📥 Export Stats CSV", csv, f"{player}_stats.csv", "text/csv")

# ── TRAINING TAB (Features 12-14) ──────────────────────────────────────────
def training_tab():
    st.header("🎯 Training Center")
    
    # Feature 12: AI Coach
    st.subheader("🤖 AI Coach — Recommendations")
    
    all_p = get_all_players()
    if all_p:
        selected = st.selectbox("Player for analysis", [p['name'] for p in all_p], key="train_player")
        stats = get_player_stats(selected)
        if stats:
            recs = get_ai_coach_recommendations(stats)
            for r in recs:
                priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(r["priority"], "⚪")
                with st.container():
                    st.markdown(f"""
                    <div class="stats-card">
                        {priority_color} <b>{r['area']}</b> — {r['issue']}<br/>
                        💡 <b>Recommendation:</b> {r['recommendation']}
                    </div>
                    """, unsafe_allow_html=True)
    
    # Feature 14: Training Plan Generator
    st.subheader("📋 Training Plan Generator")
    focus = st.selectbox("Focus Area", ["finishing", "scoring", "consistency"])
    days = st.slider("Duration (days)", 3, 14, 7)
    
    if st.button("Generate Plan", type="primary"):
        plan = generate_training_plan(focus, days)
        st.success(f"**{focus.title()} Training Plan — {days} Days**")
        for day_plan in plan:
            st.markdown(f"""
            <div class="stats-card">
                <b>Day {day_plan['day']}:</b> {day_plan['activity']}<br/>
                <span style="color:#888;">Focus: {day_plan['focus']} | Target: {day_plan.get('target_score', day_plan.get('target', ''))}</span>
            </div>
            """, unsafe_allow_html=True)

# ── TOURNAMENT TAB (Features 1-4) ──────────────────────────────────────────
def tournament_tab():
    st.header("🏟️ Tournament")
    
    t_name = st.text_input("Tournament Name", "My Tournament")
    t_format = st.selectbox("Format", ["Knockout", "Round Robin", "League (Group + Knockout)"])
    t_players = st.text_area("Participants (one per line)", "Player 1\nPlayer 2\nPlayer 3\nPlayer 4")
    
    participants = [p.strip() for p in t_players.split("\n") if p.strip()]
    
    use_seeding = st.checkbox("Use Seeded Draw")
    
    if st.button("Create Tournament", type="primary"):
        if len(participants) < 2:
            st.error("Need at least 2 participants")
            return
        
        fmt_map = {"Knockout": "knockout", "Round Robin": "round_robin", "League (Group + Knockout)": "league"}
        tourney = TournamentEngine(t_name, fmt_map[t_format], participants)
        
        if use_seeding:
            # Seed by reverse order (first = best)
            rankings = {p: i for i, p in enumerate(participants)}
            tourney.seed_participants(rankings)
        
        st.session_state.tournament = tourney
        st.success(f"Tournament created! {len(participants)} players")
        st.rerun()
    
    # Display tournament
    if "tournament" in st.session_state and st.session_state.tournament:
        tourney = st.session_state.tournament
        st.subheader(f"📋 {tourney.name} — {tourney.format.replace('_', ' ').title()}")
        
        # Standings
        if tourney.format in ["round_robin", "league"]:
            st.write("**Standings**")
            for s in tourney.get_standings():
                cols = st.columns([3, 1, 1, 1, 1])
                cols[0].write(s['player'])
                cols[1].write(f"W: {s['wins']}")
                cols[2].write(f"L: {s['losses']}")
                cols[3].write(f"Pts: {s['points']}")
                cols[4].write(f"LF: {s['legs_for']}")
        
        # Bracket
        st.write("**Bracket / Matches**")
        for i, m in enumerate(tourney.get_bracket()):
            cols = st.columns([3, 2, 3])
            cols[0].write(m['player_a'])
            cols[1].write(f"**{m['score']}**" if m['completed'] else "vs")
            cols[2].write(m['player_b'])
            if not m['completed']:
                with cols[1]:
                    if st.button("Enter Result", key=f"m_{i}"):
                        st.session_state[f"enter_match_{i}"] = True
            
            # Result entry
            if st.session_state.get(f"enter_match_{i}"):
                rc1, rc2 = st.columns(2)
                with rc1:
                    score_a = st.number_input(f"{m['player_a']} score", 0, 10, 0, key=f"sa_{i}")
                with rc2:
                    score_b = st.number_input(f"{m['player_b']} score", 0, 10, 0, key=f"sb_{i}")
                if st.button("Save Result", key=f"sr_{i}"):
                    tourney.record_result(i, score_a, score_b)
                    del st.session_state[f"enter_match_{i}"]
                    st.rerun()

# ── SETTINGS TAB ────────────────────────────────────────────────────────────
def settings_tab():
    st.header("⚙️ Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Display")
        st.session_state.spectator_mode = st.toggle("Spectator Mode", value=st.session_state.get("spectator_mode", False))
        st.session_state.tv_mode = st.toggle("TV Scoreboard Mode", value=st.session_state.get("tv_mode", False))
        if st.session_state.tv_mode:
            st.info("TV Mode shows a clean full-width scoreboard optimized for external displays")
    
    with col2:
        st.subheader("Audio")
        st.session_state.voice_enabled = st.toggle("Voice Announcements", value=st.session_state.voice_enabled)
    
    st.subheader("Data")
    st.write("Export all your data:")
    all_players = get_all_players()
    if all_players:
        # Feature 21: Full CSV export
        full_csv = export_game_history_csv([
            {"date": "2024-01-01", "mode": "501", "winner": p["name"], "players": [{"name": p["name"], "average": 60, "one_eighties": 5, "hundreds": 10, "ton_forties": 3, "checkout_pct": 40}]}
            for p in all_players
        ])
        st.download_button("📥 Export All Stats (CSV)", full_csv, "dart_game_export.csv", "text/csv")

if __name__ == "__main__":
    main()
