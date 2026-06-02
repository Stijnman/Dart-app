"""
Dart Game Pro v2 — Streamlit Frontend
Addresses all competitor UX pain points:
- Quick score buttons (fast input)
- Per-dart AND total entry modes
- Visual interactive dartboard
- Full checkout paths displayed
- Prominent undo/redo
- Dark mode support
- Better stats dashboard
- Offline voice announcements
"""

import streamlit as st
import os
import sys
import random
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

# ── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dart Game Pro v2",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── DARK MODE CSS ───────────────────────────────────────────────────────────
def apply_theme():
    if st.session_state.get("dark_mode", True):
        st.markdown("""
        <style>
        .stApp { background-color: #0e1117; color: #fafafa; }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] { 
            background-color: #1e2329; 
            border-radius: 8px 8px 0 0; 
            padding: 10px 20px;
            color: #fafafa;
        }
        .stTabs [aria-selected="true"] { background-color: #2e3540 !important; }
        div[data-testid="stMetricValue"] { color: #00cc88 !important; font-size: 2rem !important; }
        div[data-testid="stMetricLabel"] { color: #888 !important; }
        .stButton>button { border-radius: 8px; }
        .checkout-box {
            background: linear-gradient(135deg, #1a472a 0%, #0e2a1a 100%);
            border: 2px solid #00cc66;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        }
        .checkout-box h3 { color: #00ff88; margin: 0; }
        .checkout-path { color: #ccffcc; font-size: 1.4rem; font-weight: bold; }
        .score-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
        .history-row { 
            background: #1a1f26; 
            padding: 8px 12px; 
            border-radius: 6px; 
            margin: 4px 0;
            border-left: 3px solid #2e7d32;
        }
        .bust-row {
            border-left-color: #c62828 !important;
            background: #2a1515 !important;
        }
        .checkout-row {
            border-left-color: #00cc66 !important;
            background: #0f2a1a !important;
        }
        .hero-180 {
            border-left-color: #ff6d00 !important;
            background: #2a1800 !important;
        }
        </style>
        """, unsafe_allow_html=True)

# ── AUDIO (Offline TTS) ────────────────────────────────────────────────────
def announce(text: str):
    """Announce via text-to-speech if enabled."""
    if not st.session_state.get("voice_enabled", True):
        return
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass  # Silently fail if TTS not available

# ── INIT ────────────────────────────────────────────────────────────────────
init_db()
apply_theme()

# Session state defaults
for key, val in {
    "game_started": False,
    "game": None,
    "dark_mode": True,
    "voice_enabled": True,
    "entry_mode": "per_dart",
    "game_completed": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── SIDEBAR: SETUP ─────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🎯 Dart Game Pro v2")
    
    # Settings
    with st.expander("⚙️ Settings", expanded=False):
        st.session_state.dark_mode = st.toggle("Dark Mode", value=st.session_state.dark_mode)
        st.session_state.voice_enabled = st.toggle("Voice Announcements", value=st.session_state.voice_enabled)
        st.session_state.entry_mode = st.radio(
            "Input Mode", 
            ["per_dart", "total_only"],
            format_func=lambda x: "Per Dart (T20+T20+D20)" if x == "per_dart" else "Total Only (180)",
            index=0,
        )
    
    st.divider()
    
    # Game Mode Selection
    st.header("Game Setup")
    
    mode_category = st.selectbox(
        "Category",
        ["X01 Games", "Cricket", "Practice Games", "Party Games"],
        index=0,
    )
    
    if mode_category == "X01 Games":
        mode = st.selectbox("Game", ["501", "301", "701", "201", "1001", "101", "170", "901"], index=0)
        starting_score = int(mode)
    elif mode_category == "Cricket":
        cricket_type = st.selectbox("Variant", ["Standard", "Cut-Throat", "No-Score"], index=0)
        mode_map = {"Standard": "cricket", "Cut-Throat": "cut_throat", "No-Score": "no_score_cricket"}
        mode = mode_map[cricket_type]
        starting_score = 0
    elif mode_category == "Practice Games":
        mode = st.selectbox("Game", ["Bob's 27", "Around the Clock", "Shanghai"], index=0)
        if mode == "Bob's 27":
            bobs_mode = st.selectbox("Difficulty", ["Easy (no elimination)", "Standard (3 lives)", "Hard (1 life)"], index=1)
        if mode == "Around the Clock":
            atc_mode = st.selectbox("Variant", ["Singles", "Doubles Only", "Triples Only"], index=0)
        if mode == "Shanghai":
            shanghai_variant = st.selectbox("Length", ["Quick (7 rounds)", "Full (20 rounds)"], index=0)
        starting_score = 0
    else:  # Party Games
        mode = st.selectbox("Game", ["Killer", "Half It"], index=0)
        if mode == "Killer":
            killer_lives = st.slider("Lives", 1, 9, 3)
        starting_score = 0
    
    # Match Format
    match_format = st.selectbox(
        "Match Format",
        ["Single Game", "Best of 3 Legs", "Best of 5 Legs", "Best of 7 Legs", "First to 3", "First to 5"],
        index=0,
    )
    format_map = {
        "Single Game": "single_game",
        "Best of 3 Legs": "best_of_3",
        "Best of 5 Legs": "best_of_5",
        "Best of 7 Legs": "best_of_7",
        "First to 3": "first_to_3",
        "First to 5": "first_to_5",
    }
    
    # In/Out Rules (for X01)
    if mode_category == "X01 Games":
        with st.expander("Advanced Rules"):
            out_rule = st.selectbox("Finish Rule", ["Double Out", "Master Out", "Straight Out"], index=0)
            in_rule = st.selectbox("Start Rule", ["Straight In", "Double In", "Master In"], index=0)
            
            # Handicap
            use_handicap = st.checkbox("Enable Handicap", value=False)
            handicaps = {}
            if use_handicap:
                st.caption("Players with positive handicap start with reduced score")
                registered = get_all_players()
                for p in registered[:4]:
                    h = st.number_input(f"{p['name']} handicap", 0, 200, 0, key=f"handicap_{p['name']}")
                    if h > 0:
                        handicaps[p['name']] = h
    else:
        out_rule = "double"
        in_rule = "straight"
        handicaps = {}
    
    # Bot
    play_vs_bot = st.checkbox("Play vs DartBot", value=False)
    bot_level = 5
    if play_vs_bot:
        bot_names = [f"{v['name']} (Lv.{k})" for k, v in sorted(DARTBOT_LEVELS.items())]
        bot_selected = st.selectbox("Bot Level", bot_names, index=4)
        bot_level = int(bot_selected.split("Lv.")[1].rstrip(")"))
        st.caption(f"Avg throw: ~{DARTBOT_LEVELS[bot_level]['avg_throw']}pts | {DARTBOT_LEVELS[bot_level]['description']}")
    
    st.divider()
    
    # Recent Games
    st.subheader("Recent Games")
    recent = get_recent_games(5)
    if recent:
        for g in recent:
            st.write(f"**{g['mode'].upper()}** — 🏆 {g['winner']} — {g['created_at'][:10]}")
    else:
        st.caption("No games played yet")

# ── MAIN: PLAYER REGISTRATION ──────────────────────────────────────────────
st.header("👥 Players")

num_players = st.number_input("Number of Players", 1, 8, 2, key="num_players")

cols = st.columns(min(num_players, 4))
players_data = []
for i in range(num_players):
    with cols[i % 4]:
        st.subheader(f"Player {i+1}")
        name = st.text_input("Name", value=f"Player {i+1}", key=f"pname_{i}")
        use_existing = st.checkbox("Use saved player", key=f"pexisting_{i}")
        if use_existing:
            saved = get_all_players()
            if saved:
                selected = st.selectbox("Select", [s['name'] for s in saved], key=f"psaved_{i}")
                name = selected
        players_data.append({"name": name})

# Bot player
if play_vs_bot:
    bot_name = f"🤖 {DARTBOT_LEVELS[bot_level]['name']}"
    players_data.append({"name": bot_name})
    st.info(f"Bot: **{bot_name}** (Level {bot_level})")

# Start Game Button
if st.button("🚀 START GAME", type="primary", use_container_width=True):
    player_objs = [Player(name=p["name"]) for p in players_data]
    
    # Map mode names
    mode_lower = mode.lower().replace("'s", "s").replace(" ", "_")
    if mode_lower == "bobs_27s":
        mode_lower = "bobs_27"
    if mode_lower == "around_the_clock":
        mode_lower = "around_the_clock"
    
    # Variant mapping
    variant = "standard"
    if mode_lower == "bobs_27":
        variant_map = {"Easy (no elimination)": "easy", "Standard (3 lives)": "standard", "Hard (1 life)": "hard"}
        variant = variant_map.get(bobs_mode, "standard")
    elif mode_lower == "around_the_clock":
        variant_map = {"Singles": "single", "Doubles Only": "doubles", "Triples Only": "triples"}
        variant = variant_map.get(atc_mode, "single")
    elif mode_lower == "shanghai":
        variant = "quick" if shanghai_variant == "Quick (7 rounds)" else "full"
    
    # Create engine
    engine = DartGameEngine(
        mode=mode if mode_category == "X01 Games" else mode_lower,
        players=player_objs,
        match_format=format_map[match_format],
        in_rule=in_rule.lower().replace(" ", "_"),
        out_rule=out_rule.lower().replace(" ", "_"),
        handicaps=handicaps,
        bot_enabled=play_vs_bot,
        bot_difficulty=bot_level,
        variant=variant,
    )
    
    # Save players
    for p in players_data:
        save_player(p["name"])
    
    st.session_state.game = engine
    st.session_state.game_started = True
    st.session_state.game_completed = False
    st.session_state.bot_name = bot_name if play_vs_bot else None
    st.session_state.bot_level = bot_level if play_vs_bot else None
    st.rerun()

# ── MAIN: ACTIVE GAME ───────────────────────────────────────────────────────
if st.session_state.get("game_started") and st.session_state.game:
    engine: DartGameEngine = st.session_state.game
    state = engine.state
    current = engine.get_current_player()
    
    if not current:
        st.error("Game error: no current player")
        st.stop()
    
    # ── GAME HEADER ─────────────────────────────────────────────────────────
    st.divider()
    
    col_mode, col_turn, col_format = st.columns(3)
    with col_mode:
        st.metric("Mode", state.mode.upper())
    with col_turn:
        st.metric("Turn", f"#{state.turn_number}")
    with col_format:
        if state.legs_format.value != "single_game":
            st.metric("Legs", f"{state.legs_won}")
    
    # ── CURRENT PLAYER + CHECKOUT ──────────────────────────────────────────
    is_bot_turn = state.bot_enabled and state.bot_player_idx == state.current_player_idx
    
    st.markdown(f"## 🎮 {current.name}'s Turn")
    if is_bot_turn:
        st.caption(f"🤖 Thinking... ({DARTBOT_LEVELS.get(state.bot_difficulty, {}).get('name', 'Bot')})")
    
    # Checkout suggestions
    if state.mode in ["x01", "101", "170", "201", "210", "301", "501", "701", "901", "1001", "1501"] and current.score <= 170 and current.score > 1:
        checkouts = engine.get_checkout_suggestion()
        if checkouts:
            best = checkouts[0]
            st.markdown(f"""
            <div class="checkout-box">
                <h3>🎯 CHECKOUT: {current.score}</h3>
                <div class="checkout-path">{best}</div>
                {f'<div style="color:#888;font-size:0.9rem;">Alt: {checkouts[1]}</div>' if len(checkouts) > 1 else ''}
            </div>
            """, unsafe_allow_html=True)
    
    # ── SCOREBOARD GRID ────────────────────────────────────────────────────
    st.subheader("📊 Scoreboard")
    
    if state.mode in ["x01", "101", "170", "201", "210", "301", "501", "701", "901", "1001", "1501"]:
        sb_cols = st.columns(len(state.players))
        for i, p in enumerate(state.players):
            with sb_cols[i]:
                delta = None
                if p.name == current.name:
                    delta = "➡️ THROWING"
                st.metric(
                    label=p.name,
                    value=p.score if p.score > 0 else "✅",
                    delta=delta,
                )
                # Mini stats
                if p.throws:
                    avg = sum(sum(t) for t in p.throws) / len(p.throws)
                    st.caption(f"Avg: {avg:.1f} | {len(p.throws)} throws")
    
    elif state.mode in ["cricket", "cut_throat", "no_score_cricket"]:
        # Cricket scoreboard
        targets = [15, 16, 17, 18, 19, 20, 25]
        header_cols = st.columns([2] + [1] * len(targets) + [2])
        with header_cols[0]:
            st.write("**Player**")
        for j, t in enumerate(targets):
            with header_cols[j+1]:
                st.write(f"**{t}**")
        with header_cols[-1]:
            st.write("**Points**")
        
        for p in state.players:
            row_cols = st.columns([2] + [1] * len(targets) + [2])
            with row_cols[0]:
                st.write(p.name + (" ➡️" if p.name == current.name else ""))
            marks = state.cricket_marks.get(p.name, {})
            for j, t in enumerate(targets):
                with row_cols[j+1]:
                    m = marks.get(t, 0)
                    symbol = "○" if m == 0 else ("/" if m == 1 else "X" if m == 2 else "◉")
                    st.write(symbol)
            with row_cols[-1]:
                st.write(f"{state.cricket_points.get(p.name, 0)}")
    
    # ── THROW INPUT ────────────────────────────────────────────────────────
    st.subheader("🎯 Enter Throw")
    
    if is_bot_turn:
        # Auto-throw for bot
        bot_darts = engine.get_bot_throw()
        bot_total = sum(bot_darts)
        st.info(f"🤖 Bot threw: {bot_darts} = {bot_total}")
        
        if st.button("Accept Bot Throw", key="bot_accept"):
            result = engine.record_throw(bot_darts)
            st.session_state.last_result = result
            st.rerun()
    else:
        # Human input
        if st.session_state.entry_mode == "per_dart":
            # Per-dart entry with quick buttons
            inp_cols = st.columns([2, 2, 2, 3])
            darts = []
            
            for i, label in enumerate(["Dart 1", "Dart 2", "Dart 3"]):
                with inp_cols[i]:
                    st.write(f"**{label}**")
                    # Quick buttons for common scores
                    qcol1, qcol2 = st.columns(2)
                    dart_key = f"dart_val_{i}_{state.turn_number}_{state.current_player_idx}"
                    
                    with qcol1:
                        if st.button("T20", key=f"t20_{i}"):
                            st.session_state[dart_key] = 60
                        if st.button("T19", key=f"t19_{i}"):
                            st.session_state[dart_key] = 57
                        if st.button("D20", key=f"d20_{i}"):
                            st.session_state[dart_key] = 40
                    with qcol2:
                        if st.button("T17", key=f"t17_{i}"):
                            st.session_state[dart_key] = 51
                        if st.button("25", key=f"bull_{i}"):
                            st.session_state[dart_key] = 25
                        if st.button("0", key=f"miss_{i}"):
                            st.session_state[dart_key] = 0
                    
                    default = st.session_state.get(dart_key, 0)
                    val = st.number_input("Score", 0, 60, default, key=f"dart_inp_{i}_{state.turn_number}")
                    darts.append(val)
            
            with inp_cols[3]:
                st.write("**Quick Totals**")
                q_totals = st.columns(2)
                total_quick = 0
                for qi, (label, score) in enumerate([("60", 60), (100, 100), (140, 140), (180, 180)]):
                    with q_totals[qi % 2]:
                        if st.button(f"{score}", key=f"qt_{score}_{state.turn_number}", use_container_width=True):
                            # Auto-fill darts for common totals
                            auto_darts = {60: [20, 20, 20], 100: [20, 20, 60], 140: [60, 60, 20], 180: [60, 60, 60]}
                            darts = auto_darts.get(score, [score, 0, 0])
                            total_quick = score
                            # Store and trigger
                            st.session_state[f"quick_darts_{state.turn_number}"] = darts
                            st.session_state[f"quick_total_{state.turn_number}"] = total_quick
                            st.rerun()
                
                # Manual total override
                st.write("**Or Total:**")
                manual_total = st.number_input("Total", 0, 180, 0, key=f"manual_total_{state.turn_number}")
                if manual_total > 0:
                    darts = [manual_total, 0, 0]  # Total-only mode
        else:
            # Total-only mode
            darts = []
            tcol1, tcol2 = st.columns([1, 1])
            with tcol1:
                total = st.number_input("Total Score (all 3 darts)", 0, 180, 0, key=f"total_{state.turn_number}")
            with tcol2:
                st.write("**Quick:**")
                qc = st.columns(3)
                quick_totals = [60, 100, 140, 45, 85, 125, 26, 81, 180]
                for idx, score in enumerate(quick_totals):
                    with qc[idx % 3]:
                        if st.button(str(score), key=f"qt_{score}", use_container_width=True):
                            total = score
                            st.rerun()
            darts = [total, 0, 0]
        
        # Check for quick darts from session state
        quick_key = f"quick_darts_{state.turn_number}"
        if quick_key in st.session_state:
            darts = st.session_state[quick_key]
            del st.session_state[quick_key]
        
        # Action buttons
        act_cols = st.columns([2, 2, 2, 4])
        with act_cols[0]:
            if st.button("✅ Record Throw", type="primary", use_container_width=True):
                result = engine.record_throw(darts)
                st.session_state.last_result = result
                announce(result)
                st.rerun()
        
        with act_cols[1]:
            if st.button("↩️ Undo", use_container_width=True):
                if engine.undo_last_throw():
                    st.success("Last throw undone")
                    st.rerun()
                else:
                    st.warning("Nothing to undo")
        
        with act_cols[2]:
            if st.button("↪️ Redo", use_container_width=True):
                if engine.redo_throw():
                    st.success("Throw redone")
                    st.rerun()
                else:
                    st.warning("Nothing to redo")
    
    # ── LAST RESULT ────────────────────────────────────────────────────────
    if "last_result" in st.session_state:
        msg = st.session_state.last_result
        if "BUST" in msg.upper():
            st.error(msg)
        elif "CHECKOUT" in msg.upper() or "wins" in msg.lower():
            st.success(msg)
            st.balloons()
        elif "180" in msg or "ONE HUNDRED" in msg.upper():
            st.success(f"🔥 {msg}")
        elif "SHANGHAI" in msg.upper():
            st.success(f"🎯 {msg}")
        else:
            st.info(msg)
    
    # ── GAME OVER HANDLING ────────────────────────────────────────────────
    if engine.is_game_over():
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
        
        # Match summary
        summary = engine.get_match_summary()
        st.subheader("📊 Match Summary")
        
        sum_cols = st.columns(len(summary["players"]))
        for i, p in enumerate(summary["players"]):
            with sum_cols[i]:
                st.metric(p["name"], f"{p['average']:.1f} avg")
                st.caption(f"Throws: {p['throws']} | 180s: {p['one_eighties']} | 100+: {p['hundreds']+p['ton_forties']}")
        
        # Save game
        if not st.session_state.get("game_completed"):
            game_id = save_game(
                mode=state.mode,
                winner=state.winner or state.match_winner or "Draw",
                players=[p.to_dict() for p in state.players],
                history=[h.__dict__ if hasattr(h, '__dict__') else h for h in state.history],
                stats=summary,
                variant=state.variant,
                match_format=state.legs_format.value,
                starting_score=getattr(state, 'starting_score', 501),
            )
            
            # Save individual player stats
            for p in summary["players"]:
                save_player_stats(
                    player_name=p["name"],
                    game_id=game_id,
                    mode=state.mode,
                    stats=p,
                )
                # Update personal bests
                if p["average"] > 0:
                    update_personal_best(p["name"], "best_average", p["average"])
                if p["best_throw"] > 0:
                    update_personal_best(p["name"], "best_throw", p["best_throw"])
                update_personal_best(p["name"], "most_180s_session", p["one_eighties"])
            
            st.session_state.game_completed = True
            st.success("Game saved! ✅")
    
    # ── THROW HISTORY ──────────────────────────────────────────────────────
    with st.expander("📜 Throw History", expanded=False):
        for h in reversed(state.history[-20:]):
            row_class = "history-row"
            if getattr(h, 'is_bust', False):
                row_class += " bust-row"
            elif getattr(h, 'is_checkout', False):
                row_class += " checkout-row"
            elif getattr(h, 'is_one_eighty', False):
                row_class += " hero-180"
            
            st.markdown(f"""
            <div class="{row_class}">
                <b>Turn {h.turn_number}</b> | {h.player_name}: {h.darts} = {h.total}<br/>
                <span style="color:#888">{h.message}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # ── STATS DASHBOARD ────────────────────────────────────────────────────
    with st.expander("📈 Session Stats", expanded=True):
        stats_tabs = st.tabs(["Overview", "Player Details", "Performance"])
        
        with stats_tabs[0]:
            total_180s = sum(
                sum(1 for t in p.throws if sum(t) == 180)
                for p in state.players
            )
            total_hundreds = sum(
                sum(1 for t in p.throws if 100 <= sum(t) <= 179)
                for p in state.players
            )
            
            met1, met2, met3 = st.columns(3)
            met1.metric("Total 180s", total_180s)
            met2.metric("100+ Scores", total_hundreds)
            met3.metric("Total Turns", state.turn_number)
        
        with stats_tabs[1]:
            for p in state.players:
                if p.throws:
                    totals = [sum(t) for t in p.throws]
                    avg = sum(totals) / len(totals)
                    st.write(f"**{p.name}**: {len(p.throws)} throws | {avg:.1f} avg | "
                            f"180s: {sum(1 for t in totals if t == 180)} | "
                            f"Best: {max(totals)}")
        
        with stats_tabs[2]:
            # Simple trend chart
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            for p in state.players:
                if len(p.throws) >= 3:
                    totals = [sum(t) for t in p.throws]
                    # Moving average of 3
                    ma = [sum(totals[max(0,i-2):i+1])/min(3, i+1) for i in range(len(totals))]
                    fig, ax = plt.subplots(figsize=(8, 2))
                    ax.plot(range(1, len(ma)+1), ma, marker='o', markersize=4, label=p.name)
                    ax.set_ylabel('Avg')
                    ax.set_xlabel('Throw')
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    st.pyplot(fig)

# ── LEADERBOARD TAB (when no game active) ──────────────────────────────────
if not st.session_state.get("game_started"):
    st.divider()
    lb_tab, stats_tab = st.tabs(["🏆 Leaderboard", "📊 Player Stats"])
    
    with lb_tab:
        leaders = get_leaderboard()
        if leaders:
            st.write("| Rank | Player | Wins | Games | Avg Score |")
            st.write("|------|--------|------|-------|-----------|")
            for i, l in enumerate(leaders[:20], 1):
                st.write(f"| {i} | {l['name']} | {l['wins']} | {l['games_played']} | {l['avg_score']:.1f} |")
        else:
            st.info("Play some games to see the leaderboard!")
    
    with stats_tab:
        all_players = get_all_players()
        if all_players:
            selected = st.selectbox("Select Player", [p['name'] for p in all_players])
            stats = get_player_stats(selected)
            if stats:
                c1, c2, c3 = st.columns(3)
                c1.metric("Games", stats.get('games_played', 0))
                c2.metric("Wins", stats.get('games_won', 0))
                c3.metric("Average", f"{stats.get('overall_avg', 0):.1f}")
                
                st.write(f"**180s:** {stats.get('total_180s', 0)} | **140s:** {stats.get('total_140s', 0)} | **100s:** {stats.get('total_100s', 0)}")
                
                # Personal bests
                from core.database import get_personal_bests
                bests = get_personal_bests(selected)
                if bests:
                    st.subheader("Personal Bests")
                    for cat, data in bests.items():
                        st.write(f"{cat.replace('_', ' ').title()}: **{data['value']:.1f}** ({data['achieved_at'][:10]})")
            else:
                st.info("No stats recorded yet")
        else:
            st.info("No players registered yet")

if __name__ == "__main__":
    pass
