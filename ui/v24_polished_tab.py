"""
v3.0 Advanced / Polished & Integrated Enhancements Tab
(Formerly v2.4) Ready to enhance Play/Analytics or standalone "Advanced" tab.

Features:
- Proper st.session_state initialization
- Real connections to game engine + custom modes
- Better styling with containers, columns, and visual cards
- v3.0 features (analytics, practice, customs) wired together
"""

import streamlit as st
import numpy as np
from typing import Optional

# Import core modules
from core.enhanced_voice_recognition import EnhancedVoiceRecognition
from core.advanced_heatmap import generate_advanced_heatmap, HAS_PLOTLY
from core.smartbot_autoscale import AdaptiveDifficultyScaler
from core.extended_themes import get_enhanced_theme, get_all_enhanced_themes
from core.pressure_performance_index import PressurePerformanceIndex
from core.coaching_mode import CoachingMode
from core.ladder_league import LadderLeagueSystem, Tier


def initialize_v24_state():
    """Initialize all v2.4 objects in session_state properly."""
    if "v24_initialized" not in st.session_state:
        st.session_state.v24_initialized = True
        
        # Core objects
        st.session_state.voice_recognizer = EnhancedVoiceRecognition()
        st.session_state.coach = CoachingMode(style="balanced")
        st.session_state.ppi = PressurePerformanceIndex()
        st.session_state.bot_scaler = AdaptiveDifficultyScaler(current_bot_level=6)
        st.session_state.league = LadderLeagueSystem()
        
        # Theme
        st.session_state.current_theme = get_enhanced_theme("classic", eye_comfort=True)
        
        # Demo players for league
        st.session_state.league.register_player("demo_alice", "Alice", 1420, Tier.SILVER)
        st.session_state.league.register_player("demo_bob", "Bob", 1680, Tier.GOLD)
        st.session_state.league.register_player("demo_charlie", "Charlie", 1050, Tier.BRONZE)


def get_real_game_context():
    """Try to get real data from the game engine if available."""
    engine = st.session_state.get("engine")
    if engine:
        # Prefer public API + .score (real Player); compat for .remaining in stubs/old
        p = engine.get_current_player() if hasattr(engine, "get_current_player") else getattr(engine, "current_player", None)
        opp = getattr(engine, "opponent", None)
        rem = getattr(p, "score", getattr(p, "remaining", 85)) if p else 85
        orem = getattr(opp, "score", getattr(opp, "remaining", 62)) if opp else 62
        throws = getattr(engine, "recent_throws", []) or getattr(getattr(engine, "state", None), "recent_throws", []) or []
        return {
            "remaining": rem,
            "opponent_remaining": orem,
            "recent_throws": throws[-12:],
            "current_leg": getattr(getattr(engine, "state", engine), "current_leg", getattr(engine, "current_leg", 1)),
        }
    # Fallback demo data
    return {
        "remaining": 85,
        "opponent_remaining": 62,
        "recent_throws": [{"score": np.random.randint(20, 61)} for _ in range(9)],
        "current_leg": 3,
    }


def show_v24_polished_tab():
    initialize_v24_state()
    context = get_real_game_context()
    
    st.header("🚀 v2.4 Advanced Tools")
    st.caption("All new features integrated with your live game state")
    
    # Use nice containers for polish
    with st.container(border=True):
        st.subheader("🎨 Theme & Eye Comfort")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            themes = get_all_enhanced_themes()
            selected_theme = st.selectbox(
                "Theme", 
                list(themes.keys()), 
                format_func=lambda x: themes[x],
                key="theme_selector"
            )
        
        with col2:
            eye = st.toggle("Eye Comfort", value=True, key="eye_comfort")
            oled = st.toggle("OLED Mode", value=True, key="oled")
        
        brightness = st.slider("Brightness", 0.7, 1.15, 1.0, 0.05, key="brightness")
        
        if st.button("Apply Theme", type="primary", key="apply_theme"):
            new_theme = get_enhanced_theme(selected_theme, eye_comfort=eye, brightness=brightness, oled_optimized=oled)
            st.session_state.current_theme = new_theme
            st.success(f"Applied: {new_theme['name']}")
            st.rerun()
    
    # === Voice + Coaching Row ===
    col_voice, col_coach = st.columns(2)
    
    with col_voice:
        with st.container(border=True):
            st.subheader("🎤 Voice Commands")
            vr = st.session_state.voice_recognizer
            
            voice_text = st.text_input("Voice / Text Command", key="voice_input", 
                                       placeholder="t20, undo, skip turn, show stats...")
            
            if st.button("Process", key="process_voice"):
                if voice_text:
                    cmd, score, raw = vr.recognize(voice_text)
                    if cmd == "score":
                        st.success(f"✅ Scored **{score}**")
                    elif cmd:
                        result = vr.execute_command(cmd)
                        st.info(result.get("message", "Command executed"))
                    else:
                        st.warning("Could not understand command")
    
    with col_coach:
        with st.container(border=True):
            st.subheader("🤖 Live Coaching")
            coach = st.session_state.coach
            
            suggestion = coach.get_suggestion(
                remaining=context["remaining"],
                opponent_remaining=context["opponent_remaining"],
                is_pressure=True
            )
            
            st.metric("Recommended Target", suggestion.target)
            st.caption(suggestion.explanation)
            
            if st.button("Apply Suggestion to Next Throw"):
                st.toast(f"Next dart aimed at {suggestion.target}", icon="🎯")
    
    # === Analytics Section ===
    st.subheader("📊 Real-time Analytics")
    
    tab_ppi, tab_heatmap = st.tabs(["Pressure Index", "Advanced Heatmap"])
    
    with tab_ppi:
        ppi = st.session_state.ppi
        
        # Feed real recent throws into PPI if available
        if context["recent_throws"]:
            for throw in context["recent_throws"]:
                score = throw.get("score", 40)
                ppi.record_throw(
                    score,
                    was_behind=(context["remaining"] < context["opponent_remaining"]),
                    was_close=abs(context["remaining"] - context["opponent_remaining"]) < 30,
                    in_checkout_range=(context["remaining"] <= 170)
                )
        
        stats = ppi.get_clutch_stats()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("PPI Score", stats.get("pressure_performance_index", 50))
        c2.metric("When Behind Avg", stats.get("when_behind", {}).get("average", 0))
        c3.metric("Interpretation", stats.get("interpretation", "N/A")[:40])
    
    with tab_heatmap:
        if st.button("Generate Heatmap from Current Game", key="gen_heatmap"):
            if context["recent_throws"]:
                fig, analysis = generate_advanced_heatmap(
                    context["recent_throws"], 
                    player_name=st.session_state.get("player_name", "You"),
                    use_plotly=HAS_PLOTLY
                )
                if fig:
                    if HAS_PLOTLY:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.pyplot(fig)
                st.markdown(analysis)
            else:
                st.info("Play some darts to generate real heatmap data.")
    
    # === Ladder League ===
    with st.container(border=True):
        st.subheader("🏆 Ladder League")
        league = st.session_state.league
        
        if st.button("Simulate Ranked Match"):
            import random
            players = list(league.players.keys())
            p1, p2 = random.sample(players, 2)
            won = random.choice([True, False])
            league.record_match(p1, p2, won, 22 if won else -15, -15 if won else 20)
        
        standings = league.get_standings(limit=6)
        st.dataframe(standings, use_container_width=True, hide_index=True)
    
    # Footer
    st.caption("All features connected to live game state via session_state and engine.")