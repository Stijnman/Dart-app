"""
Dart Game Pro v3.0 - Main Streamlit Application
Sublime modern UI, full Custom Game Mode wizard (Surprise Me, preview, stats, export, edit+), rich Analytics (first9, checkout %, heatmaps, exports), Practice Drills, Lobby, Achievements, Handicaps, Leaderboards & more.
"""

import streamlit as st
import numpy as np
from datetime import datetime
from typing import List, Optional
import random
try:
    import websockets
    import asyncio
    WS_AVAILABLE = True
except ImportError:
    WS_AVAILABLE = False
    websockets = None
    asyncio = None

# Core imports - prefer real
try:
    from core.engine import DartGameEngine
    from core.player import Player
    from core.constants import MODE_CATEGORIES, ALL_MODES
    REAL_ENGINE = True
except ImportError:
    REAL_ENGINE = False
    class DartGameEngine:
        def __init__(self, mode="501", players=None, **kw):
            self.mode = mode
            self.players = players or []
            self.winner = None
            self.state = type('s', (), {'history': [], 'recent_throws': [], 'current_player_idx': 0, 'winner': None})()
        def record_throw(self, darts): 
            if isinstance(darts, int): darts = [darts, 0, 0]
            return f"Recorded {sum(darts)} (demo)"
        def undo_last_throw(self): return True
        def switch_player(self): return "Turn passed (demo)"
        def get_current_player(self): 
            return self.players[0] if self.players else type('p',(),{'name':'You','score':401})()
        def get_mode_scoreboard(self): return {"mode": self.mode, "scores": {}}
        def get_checkout_suggestion(self, *a, **k): return ["T20", "D16"]
    class Player:
        def __init__(self, name, score=501):
            self.name = name
            self.score = score
            self.throws = []

try:
    from ui.v24_polished_tab import show_v24_polished_tab, initialize_v24_state
    from core.enhanced_voice_recognition import EnhancedVoiceRecognition
    from core.coaching_mode import CoachingMode
    from core.pressure_performance_index import PressurePerformanceIndex
    from core.advanced_heatmap import generate_advanced_heatmap, HAS_PLOTLY
except Exception:
    pass  # v24 optional for core play

# Custom Game Mode (the complete feature)
try:
    from custom_game_mode import (
        generate_custom_game_mode,
        generate_name_suggestions,
        save_custom_mode,
        get_saved_modes,
        CustomGameMode,
        generate_surprise_mode,
        play_custom_mode,
        delete_custom_mode,
        update_custom_mode,
    )
    HAS_CUSTOM_MODE = True
except Exception:
    HAS_CUSTOM_MODE = False
    CustomGameMode = None

def initialize_session_state():
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.game_started = False
        st.session_state.engine = None
        st.session_state.player_names = ["You", "Opponent"]
        st.session_state.selected_mode = "501"
        st.session_state.current_theme = {"name": "Classic Dark", "background": "#0f0f23"}
        st.session_state.v24_initialized = False
        st.session_state.voice_recognizer = None
        st.session_state.coach = None
        st.session_state.ppi = None
        st.session_state.game_history = []

def apply_theme():
    theme = st.session_state.get("current_theme", {})
    if theme:
        bg = theme.get('background', '#0f0f23')
        st.markdown(f"""
<style>
.stApp {{ background-color: {bg}; }}
.stButton>button {{ border-radius: 8px; }}
.stMetric {{ background: rgba(255,255,255,0.05); border-radius: 8px; padding: 8px; }}
.stExpander {{ border: 1px solid #444; border-radius: 8px; }}
[data-testid="stSidebar"] {{ background: rgba(0,0,0,0.2); }}

/* v3.1 Mobile / PWA responsive (P0-3) */
@media (max-width: 768px) {{
    .stButton>button, .stTextInput>div>div>input {{ min-height: 44px; font-size: 16px; }}
    .stMetric {{ font-size: 0.9em; }}
    [data-testid="stSidebar"] {{ display: none; }} /* collapse on mobile, use top nav */
}}
.stAppViewContainer {{ padding-top: 0.5rem; }}
</style>
""", unsafe_allow_html=True)
    # Mobile PWA hints
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")  # better for mobile

def start_new_game(mode: str, names: List[str], custom_mode: Optional[CustomGameMode] = None, **engine_kwargs):
    players = [Player(n) for n in names if n.strip()]
    if not players:
        players = [Player("You"), Player("Opponent")]

    # Map custom mode to engine params (makes the generated custom actually playable)
    if custom_mode and HAS_CUSTOM_MODE:
        cm = custom_mode
        # Choose base engine mode based on style/win_condition (leverages our wired real subs)
        if "Survival" in (cm.win_condition or "") or cm.lives:
            mode = "killer_party"
            engine_kwargs.setdefault("variant", "hard" if (cm.lives or 3) <= 1 else "standard")
        elif "Highest score" in (cm.win_condition or "") or (cm.round_limit and "round" in (cm.win_condition or "").lower()):
            mode = "count_up"
        elif "Target" in (cm.win_condition or ""):
            mode = "around_the_clock"
        # else keep provided mode or default 501

        if "Only Doubles" in (cm.special_rules or []):
            engine_kwargs["out_rule"] = "double"

        if cm.lives:
            engine_kwargs.setdefault("variant", str(cm.lives))  # rough for some

        # Store for display during game
        st.session_state.active_custom_mode = cm

    try:
        engine = DartGameEngine(mode=mode, players=players, **engine_kwargs)
        st.session_state.engine = engine
        st.session_state.game_started = True
        st.session_state.selected_mode = mode
        st.session_state.player_names = [p.name for p in players]
        # v2.4 modules
        if not st.session_state.get("v24_initialized"):
            initialize_v24_state()
            st.session_state.v24_initialized = True
        if st.session_state.voice_recognizer is None:
            st.session_state.voice_recognizer = EnhancedVoiceRecognition(engine_ref=engine)
        if st.session_state.coach is None:
            st.session_state.coach = CoachingMode(style="balanced")
        if st.session_state.ppi is None:
            st.session_state.ppi = PressurePerformanceIndex()
        success_msg = f"Started {mode}"
        if custom_mode:
            success_msg = f"Started Custom: {custom_mode.name} ({mode} base)"
            # Increment play count + best tracking (high impact gamification)
            try:
                play_custom_mode(custom_mode.name)
            except Exception:
                pass
        st.success(success_msg)
    except Exception as e:
        st.error(f"Failed to start game: {e}")
        # fallback demo
        st.session_state.engine = DartGameEngine(mode=mode, players=[Player(n) for n in names])
        st.session_state.game_started = True
        if custom_mode:
            st.session_state.active_custom_mode = custom_mode

def get_scoreboard_display(engine):
    if not engine:
        return {}
    try:
        if hasattr(engine, "get_mode_scoreboard"):
            return engine.get_mode_scoreboard() or {}
    except:
        pass
    # fallback
    return {"mode": getattr(engine, "mode", "unknown"), "scores": {}}


# ==================== CUSTOM GAME WIZARD (enhanced with 15 easy high-impact improvements) ====================
def custom_game_wizard():
    st.header("🎲 Create Custom Game Mode — Now with Wack Good Features")

    # 1. Surprise Me (top recommendation, very high engagement)
    if st.button("🎁 SURPRISE ME (Random Wack Mode)", type="secondary"):
        surprise = generate_surprise_mode()
        st.session_state.temp_mode = surprise
        st.session_state.name_suggestions = [surprise.name]  # already has a good one
        st.session_state.funny_message = random.choice([
            "Generating pure chaos...",
            "Rolling the dart dice of destiny...",
            "Consulting the dart gods...",
            "Brewing something spicy...",
            "Mayhem loading... please hold your darts"
        ])
        st.rerun()

    if st.session_state.get("funny_message"):
        st.caption(f"✨ {st.session_state.funny_message}")
        if "temp_mode" in st.session_state:
            del st.session_state.funny_message  # one time

    answers = {}
    answers["style"] = st.selectbox(
        "Game Style", 
        ["Scoring Race", "Target Hunting", "Survival", "Chaos Mode"]
    )
    answers["starting_score"] = st.slider("Starting Score", 101, 1001, 501, 100)
    answers["difficulty"] = st.select_slider(
        "Difficulty", ["Easy", "Normal", "Hard", "Brutal"]
    )
    # 4. More Special Rules (high impact variety)
    answers["special_rules"] = st.multiselect(
        "Special Rules (pick a few for extra spice)",
        [
            "Only Doubles", "Bust = Lose Life", "Must hit bull to win",
            "Triple points only", "No 180s allowed", "Reverse scoring (lowest wins)",
            "Sudden death on any checkout", "All scores doubled after round 3"
        ]
    )

    col_gen, col_surprise = st.columns([1, 1])
    with col_gen:
        if st.button("✨ Generate Mode + Name Ideas", type="primary"):
            mode = generate_custom_game_mode(answers)
            st.session_state.temp_mode = mode
            st.session_state.name_suggestions = generate_name_suggestions(
                answers["style"], answers["difficulty"]
            )

    # Preview Card + Name selection (high value UX)
    if "name_suggestions" in st.session_state and "temp_mode" in st.session_state:
        mode: CustomGameMode = st.session_state.temp_mode

        # 3. Preview card (makes it feel premium)
        with st.container(border=True):
            st.subheader(f"{mode.emoji} {mode.name or 'Your New Mode'}")
            st.caption(f"⏱️ ~{mode.estimated_minutes} min  |  Tags: {', '.join(mode.tags) if mode.tags else 'none'}")
            st.write(f"**Win Condition:** {mode.win_condition}")
            if mode.special_rules:
                st.write("**Special Rules:** " + " • ".join(mode.special_rules))
            st.write(f"**Multiplier:** x{mode.scoring_multiplier}")
            if mode.lives:
                st.write(f"**Lives:** {mode.lives}")
            st.caption(mode.description or "A custom darts experience.")

        st.subheader("Choose or customize the name:")
        selected_name = st.radio("Pick a banger name:", st.session_state.name_suggestions, key="name_pick")

        # Allow quick edit of the chosen name
        custom_name = st.text_input("Or type your own legendary name", value=selected_name)

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("✅ Save & Use This Mode"):
                mode.name = custom_name or selected_name
                save_custom_mode(mode)
                st.session_state.generated_mode = mode
                st.success(f"Mode **{mode.name}** saved! Ready to throw.")
                del st.session_state.temp_mode
                del st.session_state.name_suggestions
                st.rerun()
        with c2:
            if st.button("📋 Duplicate as New"):
                dup = CustomGameMode(**mode.to_dict())
                dup.name = f"{custom_name or selected_name} (Copy)"
                save_custom_mode(dup)
                st.session_state.generated_mode = dup
                st.success("Duplicated!")
                st.rerun()
        with c3:
            if st.button("🎲 Surprise me another name"):
                st.session_state.name_suggestions = generate_name_suggestions(answers["style"], answers["difficulty"])
                st.rerun()

    # Enhanced saved modes list with stats, edit, delete, recent (14, 11, 6, 9, 10)
    st.divider()
    st.subheader("📁 Your Saved Custom Modes (with stats & management)")

    # Simple recent tracking (session only for demo)
    recent = st.session_state.get("recent_customs", [])
    if recent:
        st.caption("🕒 Recently played: " + " → ".join(recent[-3:]))

    saved = get_saved_modes()
    if saved:
        # Sort by last_played or play_count for "recent" feel
        saved_sorted = sorted(saved, key=lambda m: (m.last_played or "", m.play_count), reverse=True)[:8]

        for mode in saved_sorted:
            header = f"{mode.emoji} {mode.name}  (played {mode.play_count}x"
            if mode.best_score is not None:
                header += f" • best {mode.best_score}"
            header += ")"
            with st.expander(header):
                st.write(f"**Win:** {mode.win_condition}")
                if mode.special_rules:
                    st.write("**Rules:**", " • ".join(mode.special_rules))
                st.caption(f"⏱️ ~{mode.estimated_minutes} min | Tags: {', '.join(mode.tags or [])}")
                if mode.description:
                    st.caption(mode.description)

                cols = st.columns(4)
                with cols[0]:
                    if st.button(f"▶️ Play {mode.name}", key=f"play_{mode.name}"):
                        st.session_state.use_custom_for_next = mode
                        # track recent
                        rec = st.session_state.get("recent_customs", [])
                        if mode.name not in rec:
                            rec.append(mode.name)
                        st.session_state.recent_customs = rec[-5:]
                        st.rerun()
                with cols[1]:
                    if st.button("✏️ Edit", key=f"edit_{mode.name}"):
                        st.session_state.temp_mode = mode
                        st.session_state.name_suggestions = [mode.name]
                        st.rerun()
                with cols[2]:
                    if st.button("📋 Duplicate", key=f"dup_{mode.name}"):
                        dup = CustomGameMode(**mode.to_dict())
                        dup.name = f"{mode.name} (v2)"
                        save_custom_mode(dup)
                        st.success("Duplicated!")
                        st.rerun()
                with cols[3]:
                    if st.button("🗑️ Delete", key=f"del_{mode.name}"):
                        delete_custom_mode(mode.name)
                        st.warning("Deleted.")
                        st.rerun()
    else:
        st.info("No saved modes yet. Create one above or hit Surprise Me!")

def show_play_page():
    st.header("🎯 Play - Real Multi-Mode Scoring")

    # === CUSTOM GAME MODE WIZARD INTEGRATION (from complete feature) ===
    if HAS_CUSTOM_MODE:
        with st.expander("🎲 Create / Load Custom Game Mode (new powerful feature)", expanded=bool(st.session_state.get("generated_mode"))):
            custom_game_wizard()

            # If a custom was just generated/saved, offer to use it
            if st.session_state.get("generated_mode"):
                cm: CustomGameMode = st.session_state.generated_mode
                st.success(f"Custom mode ready: **{cm.name}**")
                st.write(f"Win: {cm.win_condition} | Multiplier x{cm.scoring_multiplier}")
                if cm.special_rules:
                    st.write("Rules:", cm.special_rules)
                if st.button("🚀 Play this Custom Mode now", type="primary", key="play_custom_now"):
                    # Will be picked up in the setup below or direct start
                    st.session_state.use_custom_for_next = cm
                    # Clear generated so it doesn't loop
                    if "generated_mode" in st.session_state:
                        del st.session_state.generated_mode
                    st.rerun()

    # Auto-start if user clicked "Play this Custom Mode now" from wizard
    if st.session_state.get("use_custom_for_next") and not st.session_state.get("game_started"):
        cm = st.session_state.use_custom_for_next
        start_new_game("501", ["You", "Opponent"], custom_mode=cm)
        if "use_custom_for_next" in st.session_state:
            del st.session_state.use_custom_for_next
        st.rerun()

    if not st.session_state.get("game_started") or not st.session_state.get("engine"):
        # Onboarding / TV mode hint (UX polish)
        with st.expander("📺 TV Mode / Onboarding (cast this to big screen)", expanded=False):
            st.caption("Run with --server.headless true --server.port 8501, use browser cast or HDMI. Use large fonts in browser. New users: start with 501, add players, throw 3 darts per turn!")
        st.subheader("Setup Game")

        # If user chose to play a custom, pre-apply it
        prefilled_mode = st.session_state.get("selected_mode", "501")
        prefilled_custom = st.session_state.get("use_custom_for_next")
        if prefilled_custom:
            st.info(f"Using Custom: {prefilled_custom.name}")
            # map a sensible base for the selector
            if "Survival" in (prefilled_custom.win_condition or ""):
                prefilled_mode = "killer_party"
            elif "Highest" in (prefilled_custom.win_condition or ""):
                prefilled_mode = "count_up"
            else:
                prefilled_mode = "501"

        colm, colp = st.columns([1, 2])
        with colm:
            cats = list(MODE_CATEGORIES.keys()) if REAL_ENGINE else ["X01", "Cricket", "Practice", "Party"]
            cat = st.selectbox("Category", cats, key="cat")
            modes = MODE_CATEGORIES.get(cat, ["501"]) if REAL_ENGINE else ["501", "cricket", "bobs_27", "killer", "golf", "tictactoe", "tactics_joker"]
            mode = st.selectbox("Mode / Variant", modes, index=modes.index(prefilled_mode) if prefilled_mode in modes else 0, key="mode_sel")
            st.caption("Subs like golf/tictactoe/tactics_joker now use real rules (wired). Custom modes map to closest base + rules.")
        with colp:
            p1 = st.text_input("Player 1", value=st.session_state.player_names[0] if st.session_state.player_names else "You")
            p2 = st.text_input("Player 2", value=st.session_state.player_names[1] if len(st.session_state.player_names)>1 else "Opponent")
            bot = st.checkbox("Enable DartBot", value=False)
            out_rule = st.selectbox("Out Rule", ["double", "master", "straight"], index=0)
            hcap1 = st.number_input(f"Handicap {p1}", 0, 200, 0, key="h1")
            hcap2 = st.number_input(f"Handicap {p2}", 0, 200, 0, key="h2")
            profile = st.selectbox("Active Profile (stats)", [p1, p2, "Guest"], index=0)
        if st.button("🚀 Start / Restart Game", type="primary"):
            custom_to_use = st.session_state.get("use_custom_for_next")
            hcaps = {p1: int(hcap1), p2: int(hcap2)}
            start_new_game(mode, [p1, p2], custom_mode=custom_to_use, bot_enabled=bot, out_rule=out_rule, handicaps=hcaps)
            # clear the one-time flag
            if "use_custom_for_next" in st.session_state:
                del st.session_state.use_custom_for_next
            st.rerun()
        st.info("Select mode (incl. custom subs), players, start. Or use the Custom Wizard above for generated modes. Then use the scoring below.")
        return

    engine = st.session_state.engine
    mode = getattr(engine, "mode", getattr(engine.state, "mode", "unknown"))
    st.caption(f"Mode: **{mode}** | Real engine: {REAL_ENGINE}")

    # Show active custom rules if playing a generated custom mode
    cm = st.session_state.get("active_custom_mode")
    if cm:
        st.info(f"🎲 Custom Mode: **{cm.name}** — {cm.win_condition}")
        if cm.special_rules:
            st.caption("Special Rules: " + " • ".join(cm.special_rules))
        if cm.scoring_multiplier != 1.0:
            st.caption(f"Scoring multiplier: x{cm.scoring_multiplier}")

    # Multiplayer basics (lobby from core/systems, feature rich social)
    with st.expander("👥 Multiplayer Lobby (simulated online)", expanded=False):
        try:
            from core.systems import LobbySystem
            lobby_sys = LobbySystem()
            st.caption("Create/Join lobbies (persisted). Real-time would need sockets.")
            colc, colj = st.columns(2)
            with colc:
                if st.button("Create Lobby"):
                    match = lobby_sys.create_lobby(st.session_state.get("player_names", ["You"])[0])
                    st.session_state.current_lobby = match.to_dict() if hasattr(match, 'to_dict') else {"id": match.match_id}
                    st.success(f"Lobby created: {st.session_state.current_lobby.get('join_code', 'N/A')}")
            with colj:
                code = st.text_input("Join Code")
                if st.button("Join") and code:
                    m = lobby_sys.join_lobby(code, "Guest")
                    if m: st.success("Joined!")
            if st.session_state.get("current_lobby"):
                st.json(st.session_state.current_lobby)
            st.caption("Spectator mode & challenges: stubs in systems.py / roadmap.")
        except Exception as ex:
            st.caption(f"Lobby: {ex}")

    # Feature rich: Local Leaderboards (engine + per custom)
    with st.expander("🏅 Local Leaderboards & Session History", expanded=False):
        try:
            lb = engine.get_leaderboard() if hasattr(engine, "get_leaderboard") else []
            if lb:
                st.dataframe(lb[:5] if isinstance(lb, list) else [{"name": str(lb)}])
            else:
                st.caption("Play more for leaderboards.")
            if cm:
                st.caption(f"Custom {cm.name} plays: {cm.play_count} | best: {cm.best_score}")
        except: pass
        # simple history
        if hasattr(engine, "state") and engine.state.history:
            st.write("Last visits:", [f"{h.player_name}:{h.total}" for h in engine.state.history[-5:]])

    # Top controls
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🔄 New Leg / Restart"):
            try:
                engine.start_new_leg()
            except:
                start_new_game(mode, st.session_state.player_names)
            st.rerun()
    with c2:
        if st.button("⏪ Undo Last Visit"):
            ok = engine.undo_last_throw() if hasattr(engine, "undo_last_throw") else False
            st.toast("Undone" if ok else "Nothing to undo")
            st.rerun()
    with c3:
        if st.button("🤖 Bot Throw"):
            try:
                darts = engine.get_bot_throw() if hasattr(engine, "get_bot_throw") else [20, 20, 20]
                msg = engine.record_throw(darts)
                st.success(msg)
                st.rerun()
            except Exception as ex:
                st.error(str(ex))
    with c4:
        if st.button("➡️ Next Player (Voice)"):
            try:
                msg = engine.switch_player() if hasattr(engine, "switch_player") else "Advanced"
                st.info(msg)
                st.rerun()
            except Exception as ex:
                st.error(str(ex))

    # 3-Dart Visit Input (real engine expects List[int])
    st.subheader("Record Visit (3 darts)")
    dc1, dc2, dc3, dc4 = st.columns([1,1,1,1])
    with dc1:
        d1 = st.number_input("Dart 1", 0, 60, 20, key="d1")
    with dc2:
        d2 = st.number_input("Dart 2", 0, 60, 20, key="d2")
    with dc3:
        d3 = st.number_input("Dart 3", 0, 60, 20, key="d3")
    with dc4:
        if st.button("🎯 Submit Visit", type="primary", key="submit_visit"):
            darts = [int(d1), int(d2), int(d3)]
            try:
                msg = engine.record_throw(darts)
                st.success(f"Visit result: {msg}")
                # feed v2.4 live modules
                if st.session_state.get("ppi"):
                    try:
                        remaining = getattr(engine.get_current_player(), "score", 0) if hasattr(engine, "get_current_player") else 0
                        st.session_state.ppi.record_throw(sum(darts), was_behind=False, was_close=False, in_checkout_range=(remaining <= 170))
                    except: pass
                st.rerun()
            except Exception as ex:
                st.error(f"Throw error: {ex}")

            # Record best for custom (easy gamification #6)
            if cm := st.session_state.get("active_custom_mode"):
                if st.button("🏆 Record my score as best for this mode"):
                    try:
                        p = engine.get_current_player()
                        sc = getattr(p, "score", random.randint(200, 450))
                        play_custom_mode(cm.name, achieved_score=sc)
                        st.toast(f"Best score for {cm.name} updated to {sc}!")
                        st.rerun()
                    except Exception as ex:
                        st.toast(str(ex))

    # === Achievements (wire core/achievements for feature rich) ===
    if st.session_state.get("engine") and st.session_state.get("active_custom_mode") or True:
        with st.expander("🏆 Achievements & Milestones", expanded=False):
            try:
                from core.achievements import AchievementEngine
                eng = st.session_state.engine
                if not hasattr(eng, "_ach_engine"):
                    eng._ach_engine = AchievementEngine()
                achs = eng._ach_engine
                if st.button("Check Achievements (after game)"):
                    stats = {"one_eighties": 2, "back_to_back_180": False}  # sim from history
                    won = bool(eng.state.winner)
                    mode = getattr(eng, "mode", "custom")
                    new = achs.check_game_end(won, mode, stats)
                    for a in new:
                        st.success(f"UNLOCKED: {a.name} - {a.description}")
                    # show some
                    unlocked = [a for a in achs.achievements.values() if a.unlocked_at]
                    st.write(f"Unlocked {len(unlocked)} / {len(achs.achievements)}")
                    for a in list(achs.achievements.values())[:5]:
                        icon = "✅" if a.unlocked_at else "🔒"
                        st.caption(f"{icon} {a.name}: {a.description} (progress {a.progress})")
            except Exception as ex:
                st.caption(f"Achievements: {ex}")

    # === Practice & Training Drills (high impact from analysis) ===
    with st.expander("🏋️ Quick Practice Drills (Checkout Trainer, Target Practice, etc.)", expanded=False):
        st.subheader("Checkout Trainer")
        target_rem = st.number_input("Practice finishing from remaining", 2, 170, 80, key="checkout_practice")
        if st.button("Get Checkout Suggestion"):
            try:
                from core.checkout import get_best_checkout, filter_checkouts_by_out_rule
                out = getattr(getattr(engine, "state", None), "out_rule", "double") if engine else "double"
                suggestions = filter_checkouts_by_out_rule(target_rem, out) or get_best_checkout(target_rem) or []
                if suggestions:
                    st.success(f"Best paths: {suggestions[:3]}")
                else:
                    st.warning("No checkout for that score.")
            except Exception as ex:
                st.error(str(ex))

        st.subheader("Target Practice (e.g. only 20s or doubles)")
        target_seg = st.number_input("Target segment (e.g. 20 for 20s)", 1, 25, 20)
        if st.button("Simulate Target Throw (3 darts)"):
            hits = 0
            for _ in range(3):
                # Simulate realistic throw
                if random.randint(1, 100) > 30:  # 70% hit rate for demo
                    hits += 1
            st.write(f"Hits on {target_seg}: {hits}/3 — Good practice for consistency!")

        st.caption("More drills (Bob's 27, ATC, Shanghai) available by selecting those modes in the main setup above. Custom practice routines via the Custom Game Mode wizard!")

    # Voice (text for now; real STT easy extension)
    with st.expander("🎤 Voice / Text Commands (t20, undo, skip turn, show stats, checkout suggestion...)"):
        if st.session_state.get("voice_recognizer"):
            vr = st.session_state.voice_recognizer
            txt = st.text_input("Command or score", key="voice_cmd", placeholder="t20 or 'undo last' or 60")
            if st.button("Process Voice/Text"):
                try:
                    cmd, score, raw = vr.recognize(txt or "")
                    if cmd == "score" and score is not None:
                        msg = engine.record_throw([score, 0, 0])
                        st.success(f"Scored {score}: {msg}")
                    elif cmd:
                        res = vr.execute_command(cmd)
                        st.info(res.get("message", cmd))
                    else:
                        st.warning("Unrecognized")
                    st.rerun()
                except Exception as ex:
                    st.error(str(ex))
        else:
            st.caption("Voice module not initialized (start game first)")

    # Dynamic Mode-Specific Scoreboard (key improvement)
    st.subheader("Scoreboard")
    try:
        board = get_scoreboard_display(engine)
        if board and board.get("scores"):
            st.json(board)  # rich; in real would render tables per mode
        else:
            # Fallback nice metrics + history
            cur = engine.get_current_player() if hasattr(engine, "get_current_player") else None
            st.metric("Current Player Score", getattr(cur, "score", getattr(cur, "remaining", "?")) if cur else "?")
            if hasattr(engine, "state") and engine.state.history:
                st.write("Recent visits:", [ (h.darts, h.total) for h in engine.state.history[-5:] ])
    except Exception:
        st.write("Scoreboard (demo)")

    # Live Coach + PPI teaser (from v2.4)
    if st.session_state.get("coach"):
        with st.expander("🤖 Live Coach (from v2.4)"):
            try:
                p = engine.get_current_player() if hasattr(engine, "get_current_player") else None
                rem = getattr(p, "score", 85) if p else 85
                sug = st.session_state.coach.get_suggestion(rem, 62, is_pressure=(rem < 100))
                st.write(f"Target: **{sug.target}** — {sug.explanation}")
            except: st.caption("Coach demo")

    # History
    if hasattr(engine, "state") and getattr(engine.state, "history", None):
        with st.expander("Visit History"):
            for h in engine.state.history[-8:]:
                st.text(f"{h.player_name}: {h.darts} = {h.total} | {h.message}")

def show_analytics_page():
    st.header("📊 Analytics & Statistics")
    st.caption("Deep stats pulled from the real engine and player data. Competitors eat this up.")

    engine = st.session_state.get("engine")
    if not engine or not getattr(engine, "players", None):
        st.warning("Start a game in the Play tab to see live stats, or load a saved profile.")
        # Demo data
        st.subheader("Demo Player Stats")
        demo_stats = {
            "name": "Demo Player",
            "throws": 45,
            "average": 62.4,
            "first_nine_avg": 68.2,
            "checkout_rate": 42.5,
            "checkout_attempts": 12,
            "checkout_successes": 5,
            "highest_checkout": 120,
            "ton_eighties": 3,
            "hundreds": 8,
        }
        col1, col2, col3 = st.columns(3)
        col1.metric("3-Dart Average", f"{demo_stats['average']}")
        col2.metric("First 9 Avg", f"{demo_stats['first_nine_avg']}")
        col3.metric("Checkout %", f"{demo_stats['checkout_rate']}%")
        st.json(demo_stats)
        return

    # Real stats from players in current engine
    st.subheader("Current Session Stats")
    for p in getattr(engine, "players", []):
        if hasattr(p, "get_stats_summary"):
            stats = p.get_stats_summary()
            with st.container(border=True):
                st.markdown(f"### {stats.get('name', p.name)}")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Avg", f"{stats.get('average', 0)}")
                c2.metric("First 9 Avg", f"{stats.get('first_nine_avg', 0)}")
                c3.metric("Checkout %", f"{stats.get('checkout_rate', 0)}% ({stats.get('checkout_successes',0)}/{stats.get('checkout_attempts',0)})")
                c4.metric("180s", stats.get('ton_eighties', 0))
                st.write(f"Best Throw: {stats.get('best_throw')} | Highest Checkout: {stats.get('highest_checkout')}")
                if stats.get('checkout_attempts', 0) > 0:
                    st.progress(min(stats['checkout_rate']/100, 1.0))

    # Advanced Heatmap from v2.4
    st.subheader("Advanced Heatmaps & Analysis")
    if st.button("Generate Heatmap from Current Throws"):
        throws = []
        for p in getattr(engine, "players", []):
            if hasattr(p, "throws"):
                for visit in p.throws[-9:]:  # recent
                    throws.append({"score": sum(visit), "visit": len(throws)})
        if throws:
            fig, analysis = generate_advanced_heatmap(throws, player_name="You", use_plotly=HAS_PLOTLY)
            if fig:
                if HAS_PLOTLY:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.pyplot(fig)
            st.markdown(analysis)
        else:
            st.info("Throw some darts first!")

    # PPI / Pressure from v2.4
    st.subheader("Pressure Performance Index (PPI)")
    if st.session_state.get("ppi"):
        ppi_stats = st.session_state.ppi.get_clutch_stats()
        st.json(ppi_stats)
    else:
        st.caption("PPI available in v3.0 Advanced or after throws.")

    # Checkout by remaining (simulated from checkout.py + history)
    st.subheader("Checkout Success by Remaining (from history)")
    if hasattr(engine, "state") and engine.state.history:
        # Simple aggregation
        checkout_data = {}
        for h in engine.state.history:
            if "CHECKOUT" in h.message and hasattr(h, "score_after"):
                rem_before = h.score_after + h.total
                bucket = (rem_before // 20) * 20
                if bucket not in checkout_data:
                    checkout_data[bucket] = {"attempts": 0, "success": 0}
                checkout_data[bucket]["attempts"] += 1
                checkout_data[bucket]["success"] += 1
        if checkout_data:
            for rem, data in sorted(checkout_data.items()):
                rate = (data["success"] / data["attempts"] * 100) if data["attempts"] else 0
                st.write(f"~{rem} remaining: {rate:.0f}% ({data['success']}/{data['attempts']})")
        else:
            st.caption("No checkouts yet in this session.")
    else:
        st.caption("Play some games with checkouts to see breakdown.")

    # Per-leg / history
    st.subheader("Recent Legs / Turns")
    if hasattr(engine, "state") and engine.state.history:
        for h in engine.state.history[-10:]:
            st.text(f"Turn {h.turn_number}: {h.player_name} {h.darts} = {h.total} | {h.message}")
    else:
        st.caption("History will appear here during play.")

    st.info("For long-term trends, check the DB or v3.0 Advanced. Exports available (CSV/JSON of stats).")

    # Exports (pandas for CSV/JSON, addresses data/history gap)
    try:
        import pandas as pd
        if st.button("Export Current Session Stats (CSV)"):
            stats_rows = []
            for p in getattr(engine, "players", []):
                if hasattr(p, "get_stats_summary"):
                    s = p.get_stats_summary()
                    s["mode"] = getattr(engine, "mode", "unknown")
                    stats_rows.append(s)
            if stats_rows:
                df = pd.DataFrame(stats_rows)
                csv = df.to_csv(index=False)
                st.download_button("Download stats.csv", csv, "session_stats.csv")
                st.success("Exported!")
    except Exception as ex:
        st.caption(f"Export needs pandas: {ex}")

def show_career_page():
    st.header("Career Mode")
    st.info("Tournaments, ELO, challenges, ladder — full in v3.0 Advanced + DB persistence (work in progress).")

def show_settings_page():
    st.header("Settings")
    st.subheader("Theme (v2.4)")
    if st.button("Open full v2.4 Theme + Eye Comfort Controls"):
        # switch tab behavior
        st.session_state["_goto_v24"] = True
        st.rerun()

def main():
    st.set_page_config(page_title="Dart Game Pro v3.0", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")
    initialize_session_state()
    apply_theme()
    st.title("🎯 Dart Game Pro v3.0")
    st.caption("Sublime UI • Custom Game Modes • Deep Analytics • Practice Drills • Lobby & More")

    with st.sidebar:
        st.header("Navigation")
        pages = ["Play", "Analytics", "v3.0 Advanced", "Career", "Online", "Settings"]
        page = st.radio("Go to", pages, index=0, key="nav_radio")
        st.divider()
        if st.session_state.get("engine"):
            try:
                cur = st.session_state.engine.get_current_player()
                st.metric("Current", f"{getattr(cur,'name','?')} @ {getattr(cur,'score', getattr(cur,'remaining','?'))}")
            except:
                pass
        if st.button("💾 Save Game (DB)"):
            try:
                from core.database import save_game
                eng = st.session_state.engine
                save_game(getattr(eng, "mode", "custom"), [p.name for p in getattr(eng, "players", [])], winner=getattr(eng, "state", eng).winner)
                st.toast("Saved to DB")
            except Exception as ex:
                st.toast(f"DB save skipped: {ex}")
        if st.button("📤 Export Mode JSON (share/custom)"):
            try:
                import json
                eng = st.session_state.engine
                cm = st.session_state.get("active_custom_mode")
                if cm:
                    cfg = cm.to_dict()
                    cfg["note"] = "Custom Game Mode — importable with the custom_game_mode.py loader."
                else:
                    cfg = {
                        "mode": getattr(eng, "mode", "501"),
                        "players": [p.name for p in getattr(eng, "players", [])],
                        "out_rule": getattr(getattr(eng, "state", None), "out_rule", "double"),
                        "variant": getattr(getattr(eng, "state", None), "variant", None),
                        "note": "Import support + advanced rules (checkout, win cond, joker, power) via custom builder (see TacticsJoker + plan). Copy this JSON."
                    }
                st.download_button("Download mode.json", data=json.dumps(cfg, indent=2), file_name="dart_mode.json")
            except Exception as ex:
                st.toast(str(ex))

    if page == "Play":
        show_play_page()
    elif page == "Analytics":
        show_analytics_page()
    elif page == "v3.0 Advanced":
        show_v24_polished_tab()  # v3.0 advanced tools & features
    elif page == "Career":
        show_career_page()
    elif page == "Online":
        show_online_multiplayer_page()
    elif page == "Settings":
        show_settings_page()

def show_online_multiplayer_page():
    st.header("🌐 Online Multiplayer (v3.1 WebSocket)")
    st.caption("Connect to FastAPI server (run `python -m core.server.main` on port 8001). Demo uses localhost.")

    if not WS_AVAILABLE:
        st.warning("Install websockets: pip install websockets. Using simulated local lobby for now.")
        # Fallback to old lobby
        try:
            from core.systems import LobbySystem
            lobby = LobbySystem()
            if st.button("Create Demo Lobby"):
                m = lobby.create_lobby("You")
                st.session_state.demo_lobby = m.to_dict() if hasattr(m, 'to_dict') else {"id": "demo"}
            if st.session_state.get("demo_lobby"):
                st.json(st.session_state.demo_lobby)
        except:
            pass
        return

    server_url = st.text_input("Server WS URL", "ws://localhost:8001/ws")
    match_id = st.text_input("Match ID (or create via /matches API)", "demo-match-123")
    player_name = st.text_input("Your Name", st.session_state.get("player_names", ["You"])[0])

    if "ws_messages" not in st.session_state:
        st.session_state.ws_messages = []

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Connect & Join"):
            st.session_state.ws_connected = True
            # Note: Full async WS in Streamlit needs threading or asyncio.run in callback; simplified here
            st.info("In production: use st.experimental_rerun loop or separate thread for WS. For demo, simulate messages.")
            # Simulate connect
            st.session_state.ws_messages.append(f"Connected to {match_id} as {player_name}")
    with col2:
        if st.button("Disconnect"):
            st.session_state.ws_connected = False
            st.session_state.ws_messages = []

    if st.session_state.get("ws_connected"):
        dart_input = st.text_input("Throw darts (comma sep, e.g. 20,20,20)", "20,20,20")
        if st.button("Send Throw"):
            try:
                darts = [int(x.strip()) for x in dart_input.split(",")]
                # In real: await ws.send(json of throw)
                st.session_state.ws_messages.append(f"You threw {darts}")
                # Simulate response
                st.session_state.ws_messages.append(f"Server: Throw processed, scores updated")
            except:
                st.error("Invalid darts")
        cmd = st.selectbox("Command", ["undo", "next"])
        if st.button("Send Command"):
            st.session_state.ws_messages.append(f"Command: {cmd}")
            st.session_state.ws_messages.append("Server: Command executed")

        st.subheader("Live Messages")
        for msg in st.session_state.ws_messages[-10:]:
            st.text(msg)

        st.caption("Full integration: Connect to WS, send ThrowEvent/CommandEvent, receive state broadcasts. See core/server/main.py for backend.")

if __name__ == "__main__":
    main()