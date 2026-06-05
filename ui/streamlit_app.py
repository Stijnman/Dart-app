"""
Dart Game Pro v2.4 — Streamlit UI
Refactored: Optimized performance, proper session state, fixed lobby system,
            comprehensive mode support, checkout suggestions, scoreboard.
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.engine import DartGameEngine
from core.player import Player
from core.game_state import InOutRule, MatchFormat
from core.checkout import get_checkout, get_best_checkout, is_checkable_score
from core.constants import (
    DARTBOT_LEVELS, QUICK_SCORES, QUICK_CHECKOUTS,
    ALL_MODES, MODE_CATEGORIES, DARTS_PER_TURN,
)
from core.utils import is_valid_dart_score, is_valid_finish
from core.database import (
    init_db, save_player, get_all_players, save_game,
    update_personal_best, get_leaderboard,
)
from core.database_v2 import init_db_v2, save_player_v2, record_login
from core.systems import (
    VoiceRecognition, CommentaryEngine, LobbySystem,
    ThemeSystem, SaveResumeManager,
)
from core.achievements import AchievementEngine

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="Dart Game Pro v2.4",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "engine": None,
        "players": [],
        "current_tab": "Play",
        "game_history": [],
        "achievements": {},
        "theme": "classic",
        "lobby": None,
        "current_lobby_code": None,
        "chat_messages": [],
        "save_manager": None,
        "voice_input": "",
        "last_checkout_suggestion": [],
        "show_checkout": True,
        "auto_bot": False,
        "bot_delay": 1.0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# =============================================================================
# THEME
# =============================================================================

theme = ThemeSystem(st.session_state.theme)
colors = theme.get_colors()

# =============================================================================
# DATABASE INIT
# =============================================================================

@st.cache_resource
def get_db():
    init_db()
    init_db_v2()
    return True

get_db()

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.title("🎯 Dart Game Pro")
    st.caption("v2.4 — Refactored & Fixed")

    st.divider()

    # Navigation
    tabs = ["Play", "Stats", "Achievements", "Leaderboard", "Settings", "Online"]
    st.session_state.current_tab = st.radio("Navigation", tabs, index=tabs.index(st.session_state.current_tab))

    st.divider()

    # Quick Info
    if st.session_state.engine:
        engine = st.session_state.engine
        st.subheader("Current Game")
        st.write(f"Mode: {engine.state.mode.upper()}")
        st.write(f"Turn: {engine.state.turn_number}")
        if engine.state.winner:
            st.success(f"Winner: {engine.state.winner}")
        elif engine.get_current_player():
            st.info(f"Current: {engine.get_current_player().name}")

    st.divider()

    # Checkout Suggestions
    if st.session_state.get("show_checkout", True) and st.session_state.engine:
        engine = st.session_state.engine
        if engine.state.mode in engine.NATIVE_X01:
            player = engine.get_current_player()
            if player and player.score > 0 and player.score <= 170:
                suggestions = engine.get_checkout_suggestion(player.name)
                if suggestions:
                    st.subheader("💡 Checkout")
                    for sug in suggestions[:3]:
                        st.code(sug, language="text")

# =============================================================================
# MAIN CONTENT
# =============================================================================

if st.session_state.current_tab == "Play":
    st.header("🎮 Play Game")

    # Game Setup
    if not st.session_state.engine or st.session_state.engine.is_game_over():
        with st.expander("Start New Game", expanded=True):
            col1, col2, col3 = st.columns(3)

            with col1:
                # Mode Selection
                mode_categories = DartGameEngine.get_all_modes()
                selected_category = st.selectbox("Category", list(mode_categories.keys()))
                selected_mode = st.selectbox("Mode", mode_categories[selected_category])

                # X01 specific
                if selected_mode in DartGameEngine.NATIVE_X01:
                    out_rule = st.selectbox("Out Rule", ["double", "straight", "master"])
                    in_rule = st.selectbox("In Rule", ["straight", "double", "master"])
                else:
                    out_rule = "double"
                    in_rule = "straight"

                # Variant
                variant_options = {
                    "bobs_27": ["standard", "easy", "hard"],
                    "around_the_clock": ["single", "doubles", "triples"],
                    "shanghai": ["standard", "quick"],
                    "killer": ["standard", "quick"],
                    "half_it": ["standard", "quick"],
                }
                if selected_mode in variant_options:
                    variant = st.selectbox("Variant", variant_options[selected_mode])
                else:
                    variant = "standard"

            with col2:
                # Players
                st.subheader("Players")
                existing_players = get_all_players()
                player_names = [p["name"] for p in existing_players]

                num_players = st.number_input("Number of Players", 1, 8, 2)
                players = []
                for i in range(num_players):
                    if i < len(player_names):
                        default = player_names[i]
                    else:
                        default = f"Player {i+1}"
                    name = st.text_input(f"Player {i+1}", value=default, key=f"player_{i}")
                    if name:
                        players.append(Player(name=name))

                # Bot
                add_bot = st.checkbox("Add DartBot")
                if add_bot:
                    bot_level = st.slider("Bot Level", 1, 12, 5)
                    bot_name = DARTBOT_LEVELS.get(bot_level, DARTBOT_LEVELS[5])["name"]
                    players.append(Player(name=f"Bot ({bot_name})", anonymous=True))

            with col3:
                # Match Format
                st.subheader("Match Format")
                match_format = st.selectbox(
                    "Format",
                    ["single_game", "best_of_3", "best_of_5", "best_of_7", "first_to_3", "first_to_5", "first_to_7"]
                )

                # Handicaps
                st.subheader("Handicaps")
                handicaps = {}
                for p in players:
                    if not p.anonymous:
                        h = st.number_input(f"{p.name} handicap", 0, 200, 0, key=f"handicap_{p.name}")
                        if h > 0:
                            handicaps[p.name] = h

            if st.button("🚀 Start Game", type="primary"):
                if len(players) < 1:
                    st.error("Need at least 1 player!")
                else:
                    try:
                        engine = DartGameEngine(
                            mode=selected_mode,
                            players=players,
                            match_format=match_format,
                            in_rule=in_rule,
                            out_rule=out_rule,
                            handicaps=handicaps if handicaps else None,
                            bot_enabled=add_bot,
                            bot_difficulty=bot_level if add_bot else 5,
                            variant=variant,
                        )
                        st.session_state.engine = engine
                        st.session_state.players = players
                        st.success("Game started!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error starting game: {e}")

    # Active Game
    if st.session_state.engine and not st.session_state.engine.is_game_over():
        engine = st.session_state.engine

        # Scoreboard
        st.subheader("📊 Scoreboard")
        scoreboard = engine.get_mode_scoreboard()

        if scoreboard and "players" in scoreboard:
            cols = st.columns(len(scoreboard["players"]))
            for i, player_data in enumerate(scoreboard["players"]):
                with cols[i]:
                    card_bg = colors["primary"] if player_data.get("is_current") else colors["background"]
                    st.markdown(f"""
                        <div style="padding: 10px; border-radius: 10px; background: {card_bg}; border: 2px solid {'#FFD700' if player_data.get('is_current') else '#ddd'};">
                            <h3 style="margin: 0;">{player_data['name']}</h3>
                            <h2 style="margin: 5px 0;">{player_data.get('display', 'Playing')}</h2>
                            <small>Avg: {player_data.get('average', 0)} | Match Avg: {player_data.get('match_average', 0)}</small>
                        </div>
                    """, unsafe_allow_html=True)

        # Extra info
        if scoreboard and "extra" in scoreboard:
            extra = scoreboard["extra"]
            if extra:
                st.info(" | ".join([f"{k}: {v}" for k, v in extra.items()]))

        st.divider()

        # Current Player
        current = engine.get_current_player()
        if current:
            st.subheader(f"🎯 {current.name}'s Turn")

            # Checkout suggestion
            if engine.state.mode in engine.NATIVE_X01 and current.score > 0 and current.score <= 170:
                suggestions = engine.get_checkout_suggestion(current.name)
                if suggestions:
                    st.success(f"💡 Checkout: {suggestions[0]}")

            # Input methods
            input_method = st.radio("Input Method", ["Manual", "Quick Buttons", "Voice"], horizontal=True)

            if input_method == "Manual":
                col1, col2, col3 = st.columns(3)
                with col1:
                    dart1 = st.number_input("Dart 1", 0, 60, 0, key="dart1")
                with col2:
                    dart2 = st.number_input("Dart 2", 0, 60, 0, key="dart2")
                with col3:
                    dart3 = st.number_input("Dart 3", 0, 60, 0, key="dart3")

                darts = [dart1, dart2, dart3]

            elif input_method == "Quick Buttons":
                st.write("Quick Scores:")
                quick_cols = st.columns(len(QUICK_SCORES))
                quick_total = 0
                for i, score in enumerate(QUICK_SCORES):
                    with quick_cols[i]:
                        if st.button(str(score), key=f"quick_{score}"):
                            quick_total = score

                if quick_total > 0:
                    darts = [quick_total, 0, 0]
                else:
                    darts = [0, 0, 0]

                # Quick checkouts
                if current.score in QUICK_CHECKOUTS:
                    st.write("Quick Checkouts:")
                    checkout_cols = st.columns(3)
                    for i, checkout in enumerate(QUICK_CHECKOUTS):
                        with checkout_cols[i % 3]:
                            if st.button(f"D{checkout//2}", key=f"checkout_{checkout}"):
                                darts = [checkout, 0, 0]

            else:  # Voice
                voice_text = st.text_input("Say your score (e.g., 'twenty forty sixty' or '180')", key="voice_input")
                if voice_text:
                    parsed = VoiceRecognition.parse_multiple(voice_text)
                    if parsed:
                        darts = parsed[:3] + [0] * (3 - len(parsed[:3]))
                        st.success(f"Parsed: {darts}")
                    else:
                        darts = [0, 0, 0]
                        st.warning("Could not parse voice input")
                else:
                    darts = [0, 0, 0]

            # Validate
            invalid = [d for d in darts if not is_valid_dart_score(d)]
            if invalid:
                st.error(f"Invalid dart scores: {invalid}")
            else:
                col_submit, col_undo, col_bot = st.columns([2, 1, 1])

                with col_submit:
                    if st.button("🎯 Submit Throw", type="primary", use_container_width=True):
                        msg = engine.record_throw(darts)
                        st.session_state.game_history.append(msg)

                        # Commentary
                        commentary = CommentaryEngine.for_throw(
                            sum(darts),
                            is_checkout="CHECKOUT" in msg,
                            is_bust="BUST" in msg,
                            remaining=current.score - sum(darts) if current.score > sum(darts) else None
                        )
                        if commentary:
                            st.toast(commentary)

                        st.rerun()

                with col_undo:
                    if st.button("↩️ Undo", use_container_width=True):
                        if engine.undo_last_throw():
                            st.success("Undo successful!")
                            st.rerun()
                        else:
                            st.warning("Nothing to undo")

                with col_bot:
                    if engine.dartbot and current.anonymous:
                        if st.button("🤖 Bot Throw", use_container_width=True):
                            bot_darts = engine.get_bot_throw()
                            msg = engine.record_throw(bot_darts)
                            st.session_state.game_history.append(msg)
                            st.rerun()

        # Game History
        if st.session_state.game_history:
            st.divider()
            st.subheader("📜 Game History")
            for msg in reversed(st.session_state.game_history[-10:]):
                st.text(msg)

    # Game Over
    elif st.session_state.engine and st.session_state.engine.is_game_over():
        engine = st.session_state.engine
        st.balloons()
        st.header("🏆 Game Over!")
        st.subheader(f"Winner: {engine.state.winner}")

        # Match summary
        summary = engine.get_match_summary()
        st.json(summary)

        # Save to database
        if st.button("💾 Save Game"):
            try:
                game_id = save_game(
                    mode=engine.state.mode,
                    players=[p.to_dict() for p in engine.state.players],
                    history=[{"turn": r.turn_number, "player": r.player_name, "darts": r.darts, "total": r.total}
                            for r in engine.state.history],
                    winner=engine.state.winner,
                )

                # Update personal bests
                for p in engine.state.players:
                    stats = p.get_stats_summary()
                    update_personal_best(p.name, {
                        "highest_avg": stats.get("average", 0),
                        "best_checkout": stats.get("highest_checkout", 0),
                        "most_180s": stats.get("ton_eighties", 0),
                        "highest_throw": stats.get("best_throw", 0),
                        "total_games": 1,
                        "total_wins": 1 if p.name == engine.state.winner else 0,
                    })

                st.success(f"Game saved! ID: {game_id}")
            except Exception as e:
                st.error(f"Error saving: {e}")

        if st.button("🔄 New Game"):
            st.session_state.engine = None
            st.session_state.game_history = []
            st.rerun()

elif st.session_state.current_tab == "Stats":
    st.header("📊 Player Statistics")

    players = get_all_players()
    if players:
        selected = st.selectbox("Select Player", [p["name"] for p in players])
        if selected:
            from core.database import get_player_stats
            stats = get_player_stats(selected)
            if stats:
                st.json(stats)
            else:
                st.info("No stats yet. Play some games!")
    else:
        st.info("No players yet. Start a game to create players!")

elif st.session_state.current_tab == "Achievements":
    st.header("🏆 Achievements")

    if st.session_state.players:
        player = st.selectbox("Player", [p.name for p in st.session_state.players])
        if player:
            engine = AchievementEngine(player)
            summary = engine.get_summary()
            st.metric("Unlocked", f"{summary['unlocked']}/{summary['total']}")
            st.progress(summary['percentage'] / 100)

            st.subheader("Unlocked")
            for ach in engine.get_unlocked():
                st.success(f"{ach.icon} {ach.name} — {ach.description}")

            st.subheader("Locked")
            for ach in engine.get_locked():
                st.info(f"{ach.icon} {ach.name} — {ach.description} ({ach.progress}/{ach.target})")
    else:
        st.info("Play games to unlock achievements!")

elif st.session_state.current_tab == "Leaderboard":
    st.header("🏅 Leaderboard")

    metric = st.selectbox("Metric", ["highest_avg", "best_checkout", "most_180s", "total_wins", "total_games"])
    leaders = get_leaderboard(metric, limit=20)

    if leaders:
        for i, row in enumerate(leaders):
            st.markdown(f"**{i+1}. {row['player_name']}** — {row[metric]}")
    else:
        st.info("No leaderboard data yet!")

elif st.session_state.current_tab == "Settings":
    st.header("⚙️ Settings")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Theme")
        theme_name = st.selectbox("Theme", ["classic", "dark", "neon", "nature", "fire"])
        if theme_name != st.session_state.theme:
            st.session_state.theme = theme_name
            st.rerun()

    with col2:
        st.subheader("Game Options")
        st.checkbox("Show Checkout Suggestions", value=st.session_state.show_checkout, key="show_checkout_setting")
        st.checkbox("Auto Bot Turn", value=st.session_state.auto_bot, key="auto_bot_setting")
        st.slider("Bot Delay (seconds)", 0.5, 5.0, st.session_state.bot_delay, key="bot_delay_setting")

    st.divider()

    st.subheader("Database")
    if st.button("🗑️ Reset All Data"):
        st.warning("This will delete all data! Are you sure?")
        if st.button("Yes, Delete Everything", type="primary"):
            try:
                os.remove(str(PROJECT_ROOT / "data" / "darts_v2.db"))
                st.success("Database reset! Refresh the page.")
            except Exception as e:
                st.error(f"Error: {e}")

elif st.session_state.current_tab == "Online":
    st.header("🌐 Online Multiplayer")

    # Initialize lobby system with persistent storage
    if not st.session_state.lobby:
        st.session_state.lobby = LobbySystem(st.session_state)

    lobby = st.session_state.lobby

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Create Lobby")
        host_name = st.text_input("Your Name", value="Host", key="host_name")
        if st.button("🏠 Create Lobby"):
            match = lobby.create_lobby(host_name)
            st.session_state.current_lobby_code = match.join_code
            st.success(f"Lobby created! Code: **{match.join_code}**")
            st.rerun()

    with col2:
        st.subheader("Join Lobby")
        join_code = st.text_input("Lobby Code", key="join_code_input")
        player_name = st.text_input("Your Name", value="Player", key="join_player_name")
        if st.button("🔗 Join"):
            match = lobby.join_lobby(join_code, player_name)
            if match:
                st.session_state.current_lobby_code = match.join_code
                st.success(f"Joined! Code: {match.join_code}")
                st.rerun()
            else:
                st.error("Invalid lobby code or lobby full")

    # Display current lobby
    if st.session_state.current_lobby_code:
        st.divider()
        st.subheader(f"💬 Lobby: {st.session_state.current_lobby_code}")

        match = None
        for m in lobby.lobbies.values():
            if m.join_code == st.session_state.current_lobby_code:
                match = m
                break

        if match:
            st.write(f"Host: {match.host}")
            st.write(f"Players: {', '.join(match.players)}")
            st.write(f"Status: {match.status}")

            if st.button("Leave Lobby"):
                st.session_state.current_lobby_code = None
                st.rerun()
        else:
            st.warning("Lobby not found or expired.")
            st.session_state.current_lobby_code = None

    # Open lobbies
    st.divider()
    st.subheader("Open Lobbies")
    open_lobbies = lobby.get_open_lobbies()
    if open_lobbies:
        for lob in open_lobbies:
            st.markdown(f"**{lob['join_code']}** — {lob['host']} ({len(lob['players'])}/4 players)")
    else:
        st.info("No open lobbies. Create one!")

# =============================================================================
# FOOTER
# =============================================================================

st.divider()
st.caption("Dart Game Pro v2.4 — Built with ❤️ for dart players everywhere")
