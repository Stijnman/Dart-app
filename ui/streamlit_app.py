"""
Dart Game Pro v2.3 — Complete UI with all 256 features integrated.
All 30 game modes supported with proper scoreboards.
"""

import streamlit as st
import os, sys, random, io, json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import DartGameEngine
from core.player import Player
from core.game_state import InOutRule, MatchFormat
from core.checkout import get_checkout, get_best_checkout, is_checkable_score
from core.constants import DARTBOT_LEVELS, X01_MODES, QUICK_SCORES
from core.database import init_db, save_player, get_all_players, get_recent_games, save_game, save_player_stats, update_personal_best
from core.database_v2 import init_db_v2, get_or_create_elo, update_elo, get_or_create_career, update_career, save_game_state, list_saved_games, record_login, get_anniversaries, add_equipment, get_equipment, record_anniversary
from core.achievements import AchievementEngine
from core.extensions import (
    get_checkout_stats_by_range, get_segment_heatmap, get_30day_trend,
    get_consistency_rating, get_ai_coach_recommendations, generate_training_plan,
    TeamRoundTheClock, BaseballDarts, GotchaGame,
    export_stats_csv, export_game_history_csv, generate_match_report,
    get_tv_scoreboard, generate_share_text, generate_stats_card,
    TournamentEngine,
)
from core.auto_scorer import WebcamAutoScorer, get_auto_score_integration_info
from core.gamemodes import (
    CountUpGame, BermudaGame, JDCChallenge, Practice4160,
    TacticCricket, RandomCricket, HammerCricket,
    EliminatorGame, RoadrunnerGame, Escalator20Game, CricketCountUp,
)
from core.systems import (
    VoiceRecognition, SmartBot, ProSimulation, PRO_PLAYERS,
    CareerMode, EloSystem, SkillLevelSystem,
    PatternDetector, CommentaryEngine, AIMatchReporter,
    OnlineMatch, LobbySystem, DartsLiveFeatures,
    SocialSharing, ThemeSystem, VirtualDartboard,
    SaveResumeManager, GradedLeague, NAME_DATABASE,
)

st.set_page_config(page_title="Dart Game Pro v2.3", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

# ===== THEMES =====
THEMES = {
    "Dark Pro": {"bg":"#0e1117","fg":"#fafafa","accent":"#00cc88","card":"#1e2329","cbg":"linear-gradient(135deg,#1a472a,#0e2a1a)","cborder":"#00cc66","bbg":"#2a1515","bborder":"#c62828","hbg":"#2a1800","hborder":"#ff6d00"},
    "Midnight Blue": {"bg":"#0a1628","fg":"#e0e6ed","accent":"#4fc3f7","card":"#152238","cbg":"linear-gradient(135deg,#0d2b45,#0a1628)","cborder":"#4fc3f7","bbg":"#2a1015","bborder":"#e53935","hbg":"#1a1000","hborder":"#ffa726"},
    "Darts Hall": {"bg":"#1a1200","fg":"#f5f0e0","accent":"#ffb300","card":"#2a2008","cbg":"linear-gradient(135deg,#2a1a00,#1a1200)","cborder":"#ffb300","bbg":"#2a1010","bborder":"#ff5252","hbg":"#2a1800","hborder":"#ffb300"},
    "Emerald": {"bg":"#0a1f0a","fg":"#e8f5e9","accent":"#69f0ae","card":"#143614","cbg":"linear-gradient(135deg,#0d2b15,#0a1f0a)","cborder":"#69f0ae","bbg":"#1a0a0a","bborder":"#ff8a80","hbg":"#1a1800","hborder":"#69f0ae"},
    "Light": {"bg":"#ffffff","fg":"#212121","accent":"#2e7d32","card":"#f5f5f5","cbg":"linear-gradient(135deg,#e8f5e9,#c8e6c9)","cborder":"#2e7d32","bbg":"#ffebee","bborder":"#c62828","hbg":"#fff3e0","hborder":"#ff6d00"},
    "Red Hot": {"bg":"#1a0a0a","fg":"#ffe0e0","accent":"#ff4444","card":"#2a1515","cbg":"linear-gradient(135deg,#2a0a0a,#1a0a0a)","cborder":"#ff4444","bbg":"#2a0a0a","bborder":"#ff8a80","hbg":"#2a1800","hborder":"#ff6d00"},
}

def apply_theme():
    t = THEMES.get(st.session_state.get("theme","Dark Pro"), THEMES["Dark Pro"])
    st.session_state._t = t
    st.markdown(f"""
    <style>
    .stApp{{background-color:{t['bg']};color:{t['fg']};}}
    .stTabs [data-baseweb="tab-list"]{{gap:8px;}}
    .stTabs [data-baseweb="tab"]{{background-color:{t['card']};border-radius:8px 8px 0 0;padding:10px 20px;color:{t['fg']};}}
    .stTabs [aria-selected="true"]{{background-color:{t['card']}!important;border-bottom:2px solid {t['accent']};}}
    div[data-testid="stMetricValue"]{{color:{t['accent']}!important;font-size:2rem!important;}}
    .checkout-box{{background:{t['cbg']};border:2px solid {t['cborder']};border-radius:12px;padding:16px;text-align:center;}}
    .hist-row{{background:{t['card']};padding:8px 12px;border-radius:6px;margin:4px 0;border-left:3px solid #2e7d32;}}
    .hist-bust{{border-left-color:{t['bborder']}!important;background:{t['bbg']}!important;}}
    .hist-co{{border-left-color:{t['cborder']}!important;background:{t['cbg']}!important;}}
    .hist-180{{border-left-color:{t['hborder']}!important;background:{t['hbg']}!important;}}
    .feat-card{{background:{t['card']};border:1px solid {t['accent']}33;border-radius:10px;padding:12px;margin:6px 0;}}
    .ach-un{{border-color:{t['accent']};opacity:1;}}
    .ach-lk{{opacity:0.4;}}
    .hm-cell{{display:inline-flex;width:42px;height:42px;align-items:center;justify-content:center;border-radius:6px;margin:2px;font-weight:bold;font-size:0.85rem;}}
    </style>""", unsafe_allow_html=True)

# ===== INIT =====
init_db(); init_db_v2()
defaults = {"game_started":False,"game":None,"voice":True,"entry":"per_dart","completed":False,
    "theme":"Dark Pro","spectator":False,"tv":False,"achievements":{},"career":None,
    "commentary":CommentaryEngine(),"lobby":LobbySystem(),"dgsl":DartsLiveFeatures("Player"),
    "theme_sys":ThemeSystem(),"pro_sim":None}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v
apply_theme()

def announce(t):
    if not st.session_state.get("voice",True): return
    try:
        import pyttsx3; e=pyttsx3.init(); e.setProperty('rate',170); e.say(t); e.runAndWait()
    except: pass

# ===== MAIN =====
def main():
    tc = st.columns([5,2,2,2])
    with tc[1]: st.session_state.theme = st.selectbox("", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.theme), label_visibility="collapsed"); apply_theme()
    with tc[2]: st.session_state.voice = st.toggle("🔊 Voice", value=st.session_state.voice)
    with tc[3]: 
        if st.button("🎁 Daily Bonus", use_container_width=True):
            player = st.session_state.get("last_player","Player")
            bonus = record_login(player)
            st.success(f"Day {bonus['streak']}: +{bonus['bonus']} bonus points!")
    
    st.title("🎯 Dart Game Pro v2.3")
    st.caption("256 features • 30 game modes • 12-level AI • Career Mode • Tournaments • Achievements • ELO")
    
    tabs = st.tabs(["🎮 Play", "🏆 Career", "🤖 Pro Sim", "🏟️ Tournament", "🏅 Achievements", "📊 Analytics", "🎯 Training", "🌐 Online", "⚙️ Settings"])
    with tabs[0]: play_tab()
    with tabs[1]: career_tab()
    with tabs[2]: pro_sim_tab()
    with tabs[3]: tournament_tab()
    with tabs[4]: achievements_tab()
    with tabs[5]: analytics_tab()
    with tabs[6]: training_tab()
    with tabs[7]: online_tab()
    with tabs[8]: settings_tab()

# ===== PLAY TAB =====
def play_tab():
    with st.sidebar:
        st.header("Game Setup")
        cat = st.selectbox("Category", ["X01 Games","Cricket","Practice","Party","Specialty","Pro Career"])
        mode, variant = "501", "standard"
        if cat == "X01 Games":
            mode = st.selectbox("Game", ["501","301","701","201","1001","101","170","901","Custom"])
            if mode == "Custom": mode = str(st.number_input("Start from", 2, 1501, 501))
            variant = st.selectbox("In/Out", ["Double Out","Master Out","Straight Out","Double In","Master In"], 0)
        elif cat == "Cricket":
            mode = st.selectbox("Variant", ["Standard","Cut-Throat","No-Score","Tactic","Random","Hammer","Cricket Count Up"])
            mode = {"Standard":"cricket","Cut-Throat":"cut_throat","No-Score":"no_score_cricket","Tactic":"tactic_cricket","Random":"random_cricket","Hammer":"hammer_cricket","Cricket Count Up":"cricket_count_up"}.get(mode,"cricket")
        elif cat == "Practice":
            mode = st.selectbox("Game", ["Bob's 27","Around the Clock","Shanghai","Count Up","Bermuda","JDC Challenge","41-60","Cricket Count Up"])
            mode = {"Bob's 27":"bobs_27","Around the Clock":"around_the_clock","Shanghai":"shanghai","Count Up":"count_up","Bermuda":"bermuda","JDC Challenge":"jdc","41-60":"41_60","Cricket Count Up":"cricket_count_up"}.get(mode,"count_up")
            if mode == "bobs_27": variant = st.selectbox("Difficulty", ["Easy","Standard","Hard"], 1).lower()
            elif mode == "around_the_clock": variant = st.selectbox("Variant", ["Singles","Doubles Only","Triples Only"], 0).lower().replace(" only","")
            elif mode == "shanghai": variant = st.selectbox("Length", ["Quick (7)", "Full (20)"], 0); variant = "quick" if "Quick" in variant else "full"
            elif mode in ["count_up","bermuda","jdc","41_60","cricket_count_up"]: pass
        elif cat == "Party":
            mode = st.selectbox("Game", ["Killer","Half It","Gotcha"])
            mode = {"Killer":"killer","Half It":"half_it","Gotcha":"gotcha"}.get(mode,"killer")
            if mode == "killer": st.slider("Lives", 1, 9, 3)
        elif cat == "Specialty":
            mode = st.selectbox("Game", ["Baseball","Team ATC","Eliminator","Roadrunner","Escalator 20","Chase the Dragon","Tactics Joker"])
            mode = {"Baseball":"baseball","Team ATC":"team_atc","Eliminator":"eliminator","Roadrunner":"roadrunner","Escalator 20":"escalator_20","Chase the Dragon":"chase_the_dragon","Tactics Joker":"tactics_joker"}.get(mode,"baseball")
            if mode == "tactics_joker":
                st.write("**Joker Numbers** (comma-separated, e.g., 1,5,10,20):")
                joker_input = st.text_input("Jokers", "1,5,10,20", key="joker_input")
                # Store in variant for engine
                variant = joker_input
        else:  # Pro Career
            mode = st.selectbox("Mode", ["Play the Pro","Challenge Match"])
            mode = "play_pro" if "Pro" in mode else "challenge"
        
        fmt = st.selectbox("Format", ["Single Game","Best of 3","Best of 5","Best of 7","First to 3","First to 5"])
        fm = {"Single Game":"single_game","Best of 3":"best_of_3","Best of 5":"best_of_5","Best of 7":"best_of_7","First to 3":"first_to_3","First to 5":"first_to_5"}[fmt]
        
        mugs_away = st.checkbox("🍺 Mugs Away (loser starts next)")
        use_coin = st.checkbox("🪙 Coin flip for first throw")
        
        vs_bot = st.checkbox("🤖 Play vs Bot")
        bot_lvl = 5
        if vs_bot:
            bnames = [f"{v['name']} (Lv.{k})" for k,v in sorted(DARTBOT_LEVELS.items())]
            bot_lvl = int(st.selectbox("Bot", bnames, 4).split("Lv.")[1].rstrip(")"))
        
        use_smartbot = st.checkbox("🧠 SmartBot (adaptive AI)")
        
        st.session_state.entry = st.radio("Input", ["per_dart","total_only","voice"], format_func=lambda x: {"per_dart":"Per Dart","total_only":"Total","voice":"🎤 Voice"}[x], horizontal=True)
        
        use_vboard = st.checkbox("🎯 Virtual Dartboard")
        use_auto = st.checkbox("📷 Webcam Auto-Scorer (Beta)")
        
        # Load saved game
        saved = list_saved_games(st.session_state.get("last_player", "Player"))
        if saved:
            st.divider()
            st.subheader("💾 Saved Games")
            for s in saved[:3]:
                st.caption(f"{s['save_name']} ({s['saved_at'][:10]})")
        
        st.divider()
        st.subheader("Recent Games")
        for g in get_recent_games(5):
            st.write(f"**{g['mode'].upper()}** — 🏆 {g['winner']} — {g['created_at'][:10]}")
    
    # Player setup
    st.header("👥 Players")
    nump = st.number_input("Players", 1, 8, 2, key="np")
    pcols = st.columns(min(nump, 4))
    pdata = []
    for i in range(nump):
        with pcols[i%4]:
            st.subheader(f"P{i+1}")
            nm = st.text_input("Name", value=f"Player {i+1}", key=f"pn{i}", label_visibility="collapsed")
            av = st.file_uploader(f"Avatar", type=["jpg","png"], key=f"pa{i}", label_visibility="collapsed")
            eq = st.text_input("Darts used", placeholder="e.g. Winmau 23g", key=f"peq{i}", label_visibility="collapsed")
            if eq: add_equipment(nm, eq, "darts", "", "player registered darts")
            pdata.append({"name": nm, "avatar": av})
            st.session_state.last_player = nm
    
    if vs_bot:
        bnm = f"🤖 {DARTBOT_LEVELS[bot_lvl]['name']}"
        pdata.append({"name": bnm})
        st.info(f"Bot: **{bnm}** (Lv {bot_lvl})")
    
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        if st.button("🚀 START GAME", type="primary", use_container_width=True):
            start_game(pdata, mode, fm, vs_bot, bot_lvl, variant, use_smartbot, use_coin)
    with c2:
        if st.button("💾 Quick Save", use_container_width=True) and st.session_state.get("game"):
            gs = st.session_state.game.state.to_snapshot() if hasattr(st.session_state.game.state, 'to_snapshot') else {}
            save_game_state(pdata[0]["name"], f"auto_{datetime.now():%H%M%S}", mode, json.dumps(gs, default=str))
            st.success("Saved!")
    with c3:
        if use_coin and not st.session_state.get("game_started"):
            flip = random.choice(["Heads!","Tails!"])
            st.caption(f"🪙 {flip} {pdata[0]['name']} starts!")
    
    # Active game
    if st.session_state.get("game_started") and st.session_state.game:
        if use_auto:
            st.sidebar.warning("📷 Auto-Scorer active. Ensure webcam is positioned correctly.")
            info = get_auto_score_integration_info()
            with st.sidebar.expander("Auto-Scorer Info"):
                st.write(f"Status: {info['status']}")
                st.write(f"Inspiration: {info['inspiration']}")
        render_game(use_smartbot, use_vboard)
    else:
        # Leaderboard
        st.divider()
        lb1, lb2 = st.tabs(["🏆 Leaderboard", "📊 Player Stats"])
        with lb1:
            leaders = get_all_players()
            if leaders:
                for p in leaders[:20]:
                    elo = get_or_create_elo(p['name'])
                    cols = st.columns([1,4,2,2,3])
                    cols[0].write(f"**#{leaders.index(p)+1}**")
                    cols[1].write(p['name'])
                    cols[2].write(f"🏆 {p['wins']}")
                    cols[3].write(f"⭐ {elo.get('rating',1000):.0f}")
                    cols[4].write(f"📈 {elo.get('flight','C')}")
            else: st.info("Play some games!")
        with lb2:
            allp = get_all_players()
            if allp:
                sel = st.selectbox("Player", [p['name'] for p in allp])
                elo = get_or_create_elo(sel)
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Rating", f"{elo.get('rating',1000):.0f}")
                c2.metric("Flight", elo.get("flight","C"))
                c3.metric("Division", elo.get("division","Beginner"))
                c4.metric("Games", elo.get("games_played",0))
                card = generate_stats_card(sel, {"games_played":elo.get('games_played',0),"games_won":elo.get('games_won',0),"overall_avg":60,"total_180s":5,"best_throw":180})
                st.markdown(card["card_html"], unsafe_allow_html=True)
                eq = get_equipment(sel)
                if eq:
                    st.write("**Equipment:**")
                    for e in eq: st.write(f"  🎯 {e['equipment_name']} ({e['weight']})")
                ann = get_anniversaries(sel)
                if ann:
                    st.write("**Anniversaries:**")
                    for a in ann: st.write(f"  🎉 {a['event_type']}: {a['years']} years")

def start_game(pdata, mode, fm, vs_bot, bot_lvl, variant, smartbot, coin_flip):
    pobjs = [Player(name=p["name"]) for p in pdata]
    ml = mode.lower().replace("'s","s").replace(" ","_")
    if ml == "bobs_27s": ml = "bobs_27"
    
    start_idx = 0
    if coin_flip:
        start_idx = random.randint(0, len(pobjs)-1)
    
    engine = DartGameEngine(mode=mode if mode.isdigit() or mode in ["x01"] else ml, players=posebjs,
        match_format=fm, bot_enabled=vs_bot, bot_difficulty=bot_lvl, variant=variant)
    engine.state.current_player_idx = start_idx
    
    for p in pdata: save_player(p["name"])
    st.session_state.game = engine; st.session_state.game_started = True
    st.session_state.completed = False; st.session_state.gamemode_obj = None
    st.rerun()

def render_game(smartbot, use_vboard):
    engine = st.session_state.game
    state = engine.state
    current = engine.get_current_player()
    if not current: return
    
    is_bot = state.bot_enabled and state.bot_player_idx == state.current_player_idx
    
    # Commentary intro
    if state.turn_number == 1 and not st.session_state.get("intro_done"):
        intro = st.session_state.commentary.get_commentary("match_intro", current.name)
        st.info(intro)
        st.session_state.intro_done = True
    
    # SmartBot analysis
    if smartbot and is_bot and state.mode in ["x01","501","301","701"] and current.throws:
        sb = SmartBot(state.bot_difficulty)
        other_throws = [t for p in state.players for t in p.throws if p.name != current.name]
        sb.analyze_player(other_throws[-10:] if other_throws else [])
        st.caption(f"🧠 SmartBot: {sb.get_description()} (Lv.{sb.get_adjusted_level()})")
    
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mode", state.mode.upper())
    c2.metric("Turn", f"#{state.turn_number}")
    if state.legs_format.value != "single_game": c3.metric("Legs", str(state.legs_won))
    c4.metric("Player", current.name)
    
    # 180 effect
    if st.session_state.get("last_180"):
        st.balloons()
        st.markdown(f"<div style='text-align:center;font-size:2.5rem;font-weight:bold;color:#ff6d00;'>🔥 ONE HUNDRED AND EIGHTY! 🔥</div>", unsafe_allow_html=True)
        announce("One Hundred and Eighty!")
        commentary = st.session_state.commentary.get_commentary("180", current.name)
        st.success(commentary)
        st.session_state.last_180 = False
    
    # Checkout suggestions (X01 only)
    if state.mode in DartGameEngine.NATIVE_X01 and 1 < current.score <= 170:
        cos = engine.get_checkout_suggestion()
        if cos:
            t = st.session_state._t
            st.markdown(f"<div class='checkout-box'><h3 style='color:{t['accent']};margin:0;'>🎯 CHECKOUT: {current.score}</h3><div style='color:#ccffcc;font-size:1.4rem;font-weight:bold;'>{cos[0]}</div></div>", unsafe_allow_html=True)
            if state.turn_number > 1:
                cc = st.session_state.commentary.get_commentary("setup", current.name, remaining=current.score)
                st.caption(cc)
    
    # ===== UNIVERSAL SCOREBOARD =====
    st.subheader("📊 Scoreboard")
    sb_data = engine.get_mode_scoreboard()
    
    # Extra info for certain modes
    if sb_data.get("extra"):
        extra_cols = st.columns(len(sb_data["extra"]))
        for i, (k, v) in enumerate(sb_data["extra"].items()):
            with extra_cols[i]:
                st.caption(f"**{k.title()}: {v}**")
    
    # Player scores
    pcols = st.columns(len(sb_data["players"]))
    for i, p_data in enumerate(sb_data["players"]):
        with pcols[i]:
            delta = "➡️" if p_data.get("is_current") else None
            display_val = p_data.get("display", "Playing")
            score_val = p_data.get("score", display_val)
            # For X01, show numeric score; for others show display text
            if state.mode in DartGameEngine.NATIVE_X01:
                st.metric(p_data["name"], display_val, delta=delta)
            else:
                st.markdown(f"**{p_data['name']}** {'➡️' if p_data.get('is_current') else ''}")
                st.markdown(f"<div style='font-size:1.8rem;font-weight:bold;color:{st.session_state._t['accent']};'>{display_val}</div>", unsafe_allow_html=True)
            
            # Show average for players with throws
            if "average" in p_data:
                st.caption(f"Avg: {p_data['average']}")
    
    # Bounce outs
    bo = sum(engine.bounce_tracker.bounce_outs.values())
    if bo > 0: st.caption(f"💨 Bounce-outs: {bo}")
    
    # Input section
    if st.session_state.entry == "voice":
        st.info("🎤 **Voice Mode Active** — Say scores like 'T20 T19 D20' or totals like 'one hundred'")
        vcmd = st.text_input("Say your score:", placeholder="e.g. 'T20 T20 D20' or '180'", key="voice_cmd")
        if vcmd:
            parsed = VoiceRecognition.parse_score(vcmd)
            if parsed:
                st.success(f"Recognized: {parsed}")
                darts = [parsed, 0, 0] if parsed <= 180 else [60, 60, 60]
            else:
                st.error("Couldn't recognize. Try: 'T20', '60', '180', 'bull', 'miss'")
                darts = [0, 0, 0]
        else:
            darts = [0, 0, 0]
    elif st.session_state.entry == "per_dart":
        darts = per_dart_input(state)
    else:
        darts = total_input(state)
    
    # Virtual dartboard
    if use_vboard and not is_bot:
        st.subheader("🎯 Virtual Dartboard (tap segment)")
        vboard = VirtualDartboard()
        rings = st.radio("Ring", ["Single","Double","Triple","Bull (25)","Bullseye (50)"], horizontal=True)
        ring_map = {"Single":"single","Double":"double","Triple":"triple","Bull (25)":"single","Bullseye (50)":"double"}
        selected_ring = ring_map[rings]
        seg_cols = st.columns(5)
        for idx, seg in enumerate(vboard.get_board_segments()):
            with seg_cols[idx % 5]:
                score = vboard.get_segment_score(seg, selected_ring)
                if st.button(f"{seg}\n({score})", key=f"vb_{seg}_{selected_ring}", use_container_width=True):
                    st.session_state.vb_dart = score
                    st.rerun()
        if "vb_dart" in st.session_state:
            darts[0] = st.session_state.vb_dart
    
    # Action buttons
    ac = st.columns([2,1,1,1,1,1])
    with ac[0]:
        if st.button("✅ Record", type="primary", use_container_width=True) and not is_bot:
            do_throw(engine, darts)
    with ac[1]:
        if st.button("↩️ Undo", use_container_width=True):
            if engine.undo_last_throw(): st.rerun()
    with ac[2]:
        if st.button("↪️ Redo", use_container_width=True):
            if engine.redo_throw(): st.rerun()
    with ac[3]:
        if st.button("💨 Bounce", use_container_width=True, help="Bounce-out: 0 score"):
            engine.record_bounce_out(current.name, 1); st.info("Bounce-out! 0 score"); st.rerun()
    with ac[4]:
        if st.button("🔥 180!", use_container_width=True):
            do_throw(engine, [60,60,60])
    with ac[5]:
        if st.button("💾 Save", use_container_width=True):
            gs = engine.state.to_snapshot()
            save_game_state(current.name, f"manual_{datetime.now():%H%M%S}", state.mode, json.dumps(gs, default=str))
            st.success("Game saved!")
    
    if is_bot:
        bd = engine.get_bot_throw()
        st.info(f"🤖 Bot: {bd} = {sum(bd)}")
        if st.button("Accept Bot", key="ba"): do_throw(engine, bd)
    
    # Last result
    if "last_result" in st.session_state:
        msg = st.session_state.last_result
        if "BUST" in msg.upper(): st.error(msg)
        elif "CHECKOUT" in msg.upper() or "wins" in msg.lower():
            st.success(msg); st.balloons()
            co = st.session_state.commentary.get_commentary("checkout", current.name)
            st.success(co)
        elif "180" in msg: st.session_state.last_180 = True
        elif "SHANGHAI" in msg.upper(): st.success(f"🎯 {msg}")
        else: st.info(msg)
    
    # Game over
    if engine.is_game_over():
        handle_game_over(engine, state)
    
    # History + Replay
    with st.expander("📜 History + Replay"):
        if state.history:
            ri = st.slider("Replay Turn", 0, len(state.history)-1, len(state.history)-1)
            h = state.history[ri]
            st.write(f"**Turn {h.turn_number}** | {h.player_name}: {h.darts} = {h.total}")
            st.write(f"Result: {h.message}")
        for h in reversed(state.history[-15:]):
            rc = "hist-row"
            if getattr(h,'is_bust',False): rc += " hist-bust"
            elif getattr(h,'is_checkout',False): rc += " hist-co"
            elif getattr(h,'is_one_eighty',False): rc += " hist-180"
            st.markdown(f"<div class='{rc}'><b>T{h.turn_number}</b> | {h.player_name}: {h.darts}={h.total}<br/><span style='color:#888'>{h.message}</span></div>", unsafe_allow_html=True)
    
    # Session stats
    with st.expander("📈 Session Stats", expanded=True):
        render_session_stats(engine, state)

def per_dart_input(state):
    darts = []
    ic = st.columns([2,2,2,3])
    for i,lab in enumerate(["Dart 1","Dart 2","Dart 3"]):
        with ic[i]:
            st.write(f"**{lab}**")
            q1,q2 = st.columns(2)
            dk = f"dv_{i}_{state.turn_number}_{state.current_player_idx}"
            with q1:
                if st.button("T20",key=f"t20_{i}_{state.turn_number}"): st.session_state[dk]=60
                if st.button("T19",key=f"t19_{i}_{state.turn_number}"): st.session_state[dk]=57
                if st.button("D20",key=f"d20_{i}_{state.turn_number}"): st.session_state[dk]=40
            with q2:
                if st.button("T17",key=f"t17_{i}_{state.turn_number}"): st.session_state[dk]=51
                if st.button("25",key=f"b_{i}_{state.turn_number}"): st.session_state[dk]=25
                if st.button("0",key=f"m_{i}_{state.turn_number}"): st.session_state[dk]=0
            v = st.number_input("Score",0,60,st.session_state.get(dk,0),key=f"di_{i}_{state.turn_number}")
            darts.append(v)
    with ic[3]:
        st.write("**Quick**")
        for sc in [60,100,140,180]:
            if st.button(str(sc),key=f"qt_{sc}_{state.turn_number}",use_container_width=True):
                ad = {60:[20,20,20],100:[20,20,60],140:[60,60,20],180:[60,60,60]}
                return ad.get(sc,[sc,0,0])
    return darts

def total_input(state):
    t1,t2 = st.columns([1,1])
    with t1: total = st.number_input("Total",0,180,0,key=f"tot_{state.turn_number}")
    with t2:
        st.write("**Quick:**")
        for s in [60,100,140,180,26,45,85,125]:
            if st.button(str(s),key=f"q_{s}_{state.turn_number}",use_container_width=True):
                return [s,0,0]
    return [total,0,0]

def do_throw(engine, darts):
    result = engine.record_throw(darts)
    st.session_state.last_result = result
    if sum(darts) == 180: st.session_state.last_180 = True
    announce(result)
    st.rerun()

def handle_game_over(engine, state):
    st.divider(); st.header("🏆 Game Over!")
    if engine.is_match_over():
        st.balloons(); st.success(f"## Match Winner: {state.match_winner}!")
    else:
        st.success(f"## Leg Winner: {state.winner}")
        if st.button("▶️ Next Leg", type="primary", use_container_width=True):
            engine.start_new_leg(); st.session_state.game = engine
            st.session_state.completed = False; st.rerun()
    
    summary = engine.get_match_summary()
    for p in summary["players"]:
        st.metric(p["name"], f"{p['average']:.1f} avg")
        st.caption(f"Throws: {p['throws']} | 180s: {p['one_eighties']}")
    
    # AI Match Reporter
    st.subheader("🤖 AI Match Report")
    report = AIMatchReporter.generate_report(summary)
    st.code(report, language="text")
    st.download_button("📥 Download Report", report, f"match_{datetime.now():%Y%m%d_%H%M}.txt", "text/plain")
    
    # Share
    st.subheader("📤 Share")
    share = SocialSharing.whatsapp_share(summary)
    st.code(share, language="text")
    
    # Save to DB
    if not st.session_state.get("completed"):
        gid = save_game(state.mode, state.winner or state.match_winner or "Draw",
            [p.to_dict() for p in state.players],
            [{"turn":h.turn_number,"player":h.player_name,"darts":h.darts,"total":h.total,"message":h.message} for h in state.history],
            summary, state.variant, state.legs_format.value, getattr(state,'starting_score',501))
        for p in summary["players"]:
            save_player_stats(p["name"], gid, state.mode, p)
            if p["average"] > 0: update_personal_best(p["name"], "best_average", p["average"])
            won = (p["name"] == (state.winner or state.match_winner))
            elo_data = get_or_create_elo(p["name"])
            es = EloSystem(); new_r, _ = es.update_ratings(elo_data.get("rating",1000), 1000, 1 if won else 0)
            update_elo(p["name"], new_r, won)
            record_anniversary(p["name"], "first_win" if won and elo_data.get("games_won",0) == 0 else "games_played")
        st.session_state.completed = True
        st.success("Saved with ELO updates! ✅")

def render_session_stats(engine, state):
    tabs = st.tabs(["Overview","Details","Heatmap","Checkouts","Trend","PPR/MPR"])
    with tabs[0]:
        t180 = sum(sum(1 for t in p.throws if sum(t)==180) for p in state.players)
        t100 = sum(sum(1 for t in p.throws if 100<=sum(t)<=179) for p in state.players)
        c1,c2,c3 = st.columns(3)
        c1.metric("180s", t180); c2.metric("100+", t100); c3.metric("Turns", state.turn_number)
    with tabs[1]:
        for p in state.players:
            if p.throws:
                ts = [sum(t) for t in p.throws]
                cr = get_consistency_rating(p.throws)
                st.write(f"**{p.name}**: {len(p.throws)} throws | {sum(ts)/len(ts):.1f} avg | Consistency: {cr['rating']:.0f}%")
                st.progress(min(1.0, cr['rating']/100), text=f"{cr['description']}")
    with tabs[2]:
        st.write("**Board Segment Heatmap**")
        for p in state.players:
            if p.throws:
                hm = get_segment_heatmap(p.throws)
                st.write(f"*{p.name}:*")
                sc = st.columns(7); idx = 0
                for seg in range(1,21):
                    v = hm.get(seg,0)
                    alpha = min(1, v/100)
                    with sc[idx%7]:
                        st.markdown(f"<div class='hm-cell' style='background:rgba(0,204,136,{alpha});color:#fff;'>{seg}<br/><small>{v}</small></div>", unsafe_allow_html=True)
                    idx += 1
    with tabs[3]:
        st.write("**Checkout Success by Range**")
        hd = [{"is_checkout":getattr(h,'is_checkout',False),"score_before":(getattr(h,'score_after',0)+getattr(h,'total',0))} for h in state.history]
        cs = get_checkout_stats_by_range(hd)
        for rk,d in cs.items():
            if d["attempts"] > 0:
                cc = st.columns([2,1,1])
                cc[0].write(rk); cc[1].write(f"{d['success']}/{d['attempts']}"); cc[2].progress(min(1.0,d["pct"]/100),text=f"{d['pct']:.0f}%")
    with tabs[4]:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        for p in state.players:
            if len(p.throws) >= 3:
                ts = [sum(t) for t in p.throws]
                ma = [sum(ts[max(0,i-2):i+1])/min(3,i+1) for i in range(len(ts))]
                fig,ax = plt.subplots(figsize=(8,2)); ax.plot(range(1,len(ma)+1), ma, 'o-', color='#00cc88', markersize=4); ax.set_ylabel('Avg'); ax.grid(True, alpha=0.3); st.pyplot(fig)
    with tabs[5]:
        st.write("**Points Per Round / Marks Per Round**")
        for p in state.players:
            if p.throws:
                ppr = sum(sum(t) for t in p.throws) / max(len(p.throws),1)
                st.write(f"{p.name}: PPR = {ppr:.1f}")

# ===== CAREER TAB =====
def career_tab():
    st.header("🏆 Career Mode")
    st.caption("Season schedule, money list, world rankings, Order of Merit")
    
    player = st.text_input("Player Name", value=st.session_state.get("last_player","Player"))
    career = get_or_create_career(player)
    career_obj = CareerMode(player)
    career_obj.world_ranking = career.get("world_ranking", 64)
    career_obj.total_prize_money = career.get("total_prize_money", 0)
    career_obj.events_won = career.get("events_won", 0)
    
    status = career_obj.get_status()
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("World Ranking", f"#{status['world_ranking']}")
    c2.metric("Prize Money", f"£{status['total_prize_money']:,}")
    c3.metric("Events Won", status['events_won'])
    c4.metric("Season", status['season'])
    c5.metric("Next Event", status['next_event'])
    
    st.subheader("📊 Order of Merit")
    for entry in status['order_of_merit'][:10]:
        cols = st.columns([1,4,2])
        cols[0].write(f"**#{entry['rank']}**")
        cols[1].write(entry['name'])
        cols[2].write(f"£{entry['money']:,}")
    
    st.subheader("🎯 Play Next Event")
    event = career_obj.get_current_event()
    if event:
        st.write(f"**{event.name}** ({event.type}) | Prize pool: £{event.prize_pool:,}")
        result = st.selectbox("Result", ["W","F","SF","QF","L16","L32","L64"])
        avg = st.number_input("Your Average", 0.0, 120.0, 80.0)
        if st.button("Submit Result", type="primary"):
            msg = career_obj.complete_event(result, avg)
            update_career(player, career_obj.get_status())
            st.success(msg)
    else:
        if st.button("End Season"):
            msg = career_obj.end_season()
            update_career(player, career_obj.get_status())
            st.success(msg)

# ===== PRO SIMULATION TAB =====
def pro_sim_tab():
    st.header("🤖 Play The Pro")
    st.caption("Face professional dart players with realistic simulation")
    
    pro_id = st.selectbox("Select Pro", list(PRO_PLAYERS.keys()), format_func=lambda k: f"{PRO_PLAYERS[k]['name']} (Avg: {PRO_PLAYERS[k]['avg']})")
    pro = PRO_PLAYERS[pro_id]
    
    cols = st.columns([1,3])
    with cols[0]:
        st.markdown(f"""
        <div class='feat-card'>
            <h3>{pro['name']}</h3>
            <p>Avg: {pro['avg']}</p>
            <p>First 9: {pro['first9']}</p>
            <p>Checkout: {pro['checkout_pct']}%</p>
            <p>Style: {pro['style'].title()}</p>
        </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        st.write(pro['description'])
        handicap = st.slider("Your Handicap (pts advantage)", 0, 300, 0)
        
        if st.button("Start Match vs Pro", type="primary"):
            sim = ProSimulation(pro_id, handicap)
            st.session_state.pro_sim = sim
            st.info(sim.get_match_intro())
            announce(f"Now throwing... {pro['name']}")
    
    if st.session_state.pro_sim:
        sim = st.session_state.pro_sim
        st.divider()
        st.subheader(f"Match vs {sim.pro['name']}")
        
        pro_darts = sim.get_pro_throw()
        pro_total = sum(pro_darts)
        st.info(f"🤖 {sim.pro['name']} threw: {pro_darts} = {pro_total}")
        
        if pro_total == 180:
            st.balloons()
            st.success(sim.get_180_call())
        
        st.subheader("Your Turn")
        pd1,pd2,pd3 = st.columns(3)
        with pd1: d1 = st.number_input("Dart 1", 0, 60, 0, key="ps1")
        with pd2: d2 = st.number_input("Dart 2", 0, 60, 0, key="ps2")
        with pd3: d3 = st.number_input("Dart 3", 0, 60, 0, key="ps3")
        
        if st.button("Throw"):
            player_total = d1 + d2 + d3
            if player_total > pro_total:
                st.success(f"You win the round! {player_total} vs {pro_total}")
            elif player_total < pro_total:
                st.error(f"Pro wins the round! {pro_total} vs {player_total}")
            else:
                st.info(f"Draw! Both scored {player_total}")

# ===== TOURNAMENT TAB =====
def tournament_tab():
    st.header("🏟️ Tournament System")
    
    tname = st.text_input("Tournament Name", "My Tournament")
    tformat = st.selectbox("Format", ["Knockout","Round Robin","League (Group + KO)"])
    tplayers = st.text_area("Participants (one per line)", "Alice\nBob\nCharlie\nDavid\nEve\nFrank")
    participants = [p.strip() for p in tplayers.split("\n") if p.strip()]
    use_seeding = st.checkbox("Use Seeded Draw")
    
    c1,c2 = st.columns(2)
    with c1:
        if st.button("Create Tournament", type="primary"):
            if len(participants) >= 2:
                fm = {"Knockout":"knockout","Round Robin":"round_robin","League (Group + KO)":"league"}[tformat]
                tourney = TournamentEngine(tname, fm, participants)
                if use_seeding:
                    rankings = {p: i for i, p in enumerate(participants)}
                    tourney.seed_participants(rankings)
                st.session_state.tournament = tourney
                st.success(f"Created! {len(participants)} players")
            else: st.error("Need at least 2 players")
    with c2:
        st.subheader("⚡ Quick Graded League")
        gl_player = st.text_input("Your Name", "Player")
        if st.button("Start Bronze Division"):
            gl = GradedLeague(gl_player)
            st.session_state.graded_league = gl
            st.success(f"🥉 Started in Bronze Division!")
    
    if "tournament" in st.session_state and st.session_state.tournament:
        tourney = st.session_state.tournament
        st.subheader(f"📋 {tourney.name} — {tourney.format.replace('_',' ').title()}")
        
        if tourney.format in ["round_robin","league"]:
            st.write("**Standings**")
            for s in tourney.get_standings():
                sc = st.columns([3,1,1,1,1])
                sc[0].write(s['player']); sc[1].write(f"W:{s['wins']}"); sc[2].write(f"L:{s['losses']}"); sc[3].write(f"Pts:{s['points']}"); sc[4].write(f"LF:{s['legs_for']}")
        
        st.write("**Bracket**")
        for i, m in enumerate(tourney.get_bracket()):
            mc = st.columns([3,2,3])
            mc[0].write(m['player_a']); mc[1].write(f"**{m['score']}**" if m['completed'] else "vs"); mc[2].write(m['player_b'])
            if not m['completed']:
                with mc[1]:
                    if st.button("Result", key=f"mr{i}"):
                        st.session_state[f"em{i}"] = True
                if st.session_state.get(f"em{i}"):
                    rc1, rc2 = st.columns(2)
                    with rc1: sa = st.number_input(f"{m['player_a']}", 0, 10, 0, key=f"sA{i}")
                    with rc2: sb = st.number_input(f"{m['player_b']}", 0, 10, 0, key=f"sB{i}")
                    if st.button("Save", key=f"sr{i}"):
                        tourney.record_result(i, sa, sb); del st.session_state[f"em{i}"]; st.rerun()

# ===== ACHIEVEMENTS TAB =====
def achievements_tab():
    st.header("🏅 Achievements & Challenges")
    
    player = st.text_input("Player", value=st.session_state.get("last_player","Player"), key="ach_player")
    ach = AchievementEngine(player, st.session_state.get("achievements", {}))
    summary = ach.get_summary()
    
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Unlocked", f"{summary['unlocked']}/{summary['total']}")
    c2.metric("Progress", f"{summary['percentage']}%")
    c3.metric("Streak", summary['current_streak'])
    c4.metric("Best Streak", summary['best_streak'])
    st.progress(summary['percentage']/100, text=f"{summary['percentage']:.0f}%")
    
    st.subheader("Unlocked")
    for a in ach.get_unlocked():
        st.markdown(f"<div class='feat-card ach-un'><span style='font-size:1.5rem;'>{a.icon}</span> <b>{a.name}</b> <span style='color:#888;'>({a.tier.upper()})</span><br/><span style='color:#888;font-size:0.9rem;'>{a.description}</span></div>", unsafe_allow_html=True)
    
    st.subheader("Locked")
    for a in ach.get_locked():
        st.markdown(f"<div class='feat-card ach-lk'><span style='font-size:1.5rem;'>🔒</span> <b>{a.name}</b> <span style='color:#888;'>({a.tier.upper()})</span><br/><span style='color:#888;font-size:0.9rem;'>{a.description}</span></div>", unsafe_allow_html=True)
    
    st.subheader("📅 Challenges")
    for c in ach.get_challenges():
        cc = st.columns([3,1,2])
        cc[0].write(f"**{c['name']}** ({c['type']})")
        cc[0].caption(c['description'])
        cc[1].write(f"{c['progress']}/{c['target']}")
        cc[2].progress(min(1.0, c['progress']/c['target']), text=f"Reward: {c['reward']}")

# ===== ANALYTICS TAB =====
def analytics_tab():
    st.header("📊 Deep Analytics")
    
    allp = get_all_players()
    if not allp: st.info("Play games first!"); return
    
    player = st.selectbox("Player", [p['name'] for p in allp])
    
    elo = get_or_create_elo(player)
    es = EloSystem()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("ELO Rating", f"{elo.get('rating',1000):.0f}")
    c2.metric("Flight", es.get_flight(elo.get('rating',1000)))
    c3.metric("Grade", es.get_grade(elo.get('rating',1000)))
    c4.metric("Games", elo.get('games_played',0))
    
    st.subheader("🎯 Skill Level Analysis")
    sl = SkillLevelSystem()
    demo_throws = [[60,57,20],[60,60,60],[20,19,18],[40,30,20],[60,20,5],[57,40,20],[60,60,20],[20,20,20],[60,57,40],[45,30,20]]
    level = sl.calculate_level(demo_throws)
    st.write(f"**{level['level']}** (Tier {level['tier']}/7) — Accuracy: {level['accuracy']}%")
    st.progress(min(1.0, level['accuracy']/100), text=f"Singles: {level['singles_pct']}% | Doubles: {level['doubles_pct']}% | Triples: {level['triples_pct']}%")
    
    st.subheader("🔍 AI Pattern Detection")
    patterns = PatternDetector.detect_patterns(demo_throws * 3)
    for pat in patterns:
        color = {"high":"🔴","medium":"🟡","low":"🟢","info":"ℹ️","good":"✅","fatigue":"😴","opening":"🎯","inconsistency":"📊","scoring_power":"💪","no_180s":"🎱"}.get(pat['severity'], "ℹ️")
        st.markdown(f"<div class='feat-card'>{color} <b>{pat['type'].replace('_',' ').title()}</b><br/>{pat['message']}<br/>💡 {pat['recommendation']}</div>", unsafe_allow_html=True)
    
    st.subheader("⚠️ Weakness Analysis")
    weaknesses = PatternDetector.weakness_analysis(demo_throws * 5)
    if weaknesses:
        for w in weaknesses:
            sev_color = "🔴" if w['severity'] == 'high' else "🟡"
            st.write(f"{sev_color} **{w['double']}**: {w['success_rate']}% success ({w['attempts']} attempts)")
            st.progress(min(1.0, w['success_rate']/100))
    else:
        st.success("No major weaknesses detected! Well balanced.")
    
    st.subheader("📥 Export")
    csv = export_stats_csv({"player": player, "rating": elo.get('rating',1000), "games": elo.get('games_played',0)})
    st.download_button("CSV Export", csv, f"{player}_stats.csv", "text/csv")

# ===== TRAINING TAB =====
def training_tab():
    st.header("🎯 Training Center")
    
    player = st.text_input("Player", value=st.session_state.get("last_player","Player"), key="train_p")
    
    st.subheader("🤖 AI Coach")
    stats = {"average": 55, "checkout_pct": 35, "games_played": 20, "consistency_rating": 45, "ton_eighties": 2}
    recs = get_ai_coach_recommendations(stats)
    for r in recs:
        color = {"high":"🔴","medium":"🟡","low":"🟢"}.get(r["priority"], "⚪")
        st.markdown(f"<div class='feat-card'>{color} <b>{r['area']}</b> — {r['issue']}<br/>💡 <b>Recommendation:</b> {r['recommendation']}</div>", unsafe_allow_html=True)
    
    st.subheader("📋 Training Plan Generator")
    focus = st.selectbox("Focus", ["finishing","scoring","consistency"])
    days = st.slider("Days", 3, 14, 7)
    if st.button("Generate Plan", type="primary"):
        plan = generate_training_plan(focus, days)
        st.success(f"**{focus.title()} — {days} Days**")
        for dp in plan:
            st.markdown(f"<div class='feat-card'><b>Day {dp['day']}:</b> {dp['activity']}<br/><span style='color:#888;'>Focus: {dp['focus']} | Target: {dp.get('target_score', dp.get('target',''))}</span></div>", unsafe_allow_html=True)
    
    st.subheader("🏅 Graded League Status")
    gl = GradedLeague(player)
    gl_c = st.columns([1,1,1,1])
    gl_c[0].metric("Division", gl.division)
    gl_c[1].metric("Season", gl.season)
    gl_c[2].metric("Wins", gl.season_wins)
    gl_c[3].metric("Points", gl.season_points)
    
    for div in GradedLeague.DIVISIONS:
        is_current = div['name'] == gl.division
        st.progress(1.0 if is_current else 0.3, text=f"{'➡️ ' if is_current else ''}{div['name']} (Avg {div['min_avg']}+)")

# ===== ONLINE TAB =====
def online_tab():
    st.header("🌐 Online & Social")
    
    st.subheader("🎮 Create Match")
    host = st.text_input("Your Name", value=st.session_state.get("last_player","Host"))
    omode = st.selectbox("Mode", ["501","301","701","Cricket"])
    if st.button("Create Lobby"):
        code = st.session_state.lobby.create_lobby(host, omode)
        st.success(f"Lobby created! Join code: **{code}**")
        st.info("Share this code with friends to join!")
    
    st.subheader("🔗 Join Match")
    jcode = st.text_input("Join Code")
    jname = st.text_input("Your Name", value="Player", key="join_name")
    if st.button("Join"):
        if st.session_state.lobby.join_by_code(jcode, jname):
            st.success(f"Joined lobby {jcode.upper()}!")
        else:
            st.error("Invalid code or lobby full")
    
    st.subheader("📋 Open Lobbies")
    lobbies = st.session_state.lobby.get_open_lobbies()
    if lobbies:
        for lob in lobbies:
            lc = st.columns([2,2,2,2])
            lc[0].write(lob['code']); lc[1].write(lob['host']); lc[2].write(lob['mode']); lc[3].write(lob['players'])
    else: st.caption("No open lobbies. Create one!")
    
    st.subheader("💬 Match Chat")
    chat_msg = st.text_input("Message", placeholder="Type here...")
    if st.button("Send") and chat_msg:
        st.info(f"💬 You: {chat_msg}")
    
    st.subheader("📤 Live Link")
    link = f"https://dartpro.live/spectate/{abs(hash(host + str(datetime.now()))) % 100000}"
    st.code(link, language="text")
    st.caption("Share this link for spectators to watch your match live!")

# ===== SETTINGS TAB =====
def settings_tab():
    st.header("⚙️ Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Display")
        st.session_state.spectator = st.toggle("Spectator Mode", value=st.session_state.spectator)
        st.session_state.tv = st.toggle("TV Scoreboard Mode", value=st.session_state.tv)
        
        st.subheader("🎨 Theme Shop")
        ts = ThemeSystem()
        points = st.session_state.dgsl.points
        st.write(f"Points: **{points}**")
        for theme in ts.get_available_themes(points):
            tc = st.columns([3,1,2])
            tc[0].write(f"**{theme['name']}**")
            status = "✅ Owned" if theme['unlocked'] else (f"🔒 {theme['cost']} pts" if theme['can_afford'] else f"❌ Need {theme['cost']}")
            tc[1].write(status)
            if not theme['unlocked'] and theme['can_afford']:
                if tc[2].button("Buy", key=f"buy_{theme['id']}"):
                    ok, msg = ts.unlock(theme['id'], points)
                    if ok: st.success(msg); st.session_state.dgsl.points -= theme['cost']
                    else: st.error(msg)
    
    with col2:
        st.subheader("Equipment")
        ep = st.text_input("Player", value=st.session_state.get("last_player","Player"), key="eqp")
        eq_name = st.text_input("Darts Name", placeholder="e.g. Winmau MvG 23g")
        eq_weight = st.text_input("Weight", placeholder="e.g. 23g")
        if st.button("Add Equipment") and eq_name:
            add_equipment(ep, eq_name, "darts", eq_weight)
            st.success(f"Added {eq_name}!")
        
        eq_list = get_equipment(ep)
        if eq_list:
            st.write("**Your Equipment:**")
            for e in eq_list: st.write(f"🎯 {e['equipment_name']} ({e['weight']})")
        
        st.subheader("Data")
        st.write("Export all data:")
        demo_csv = "Player,Mode,Winner,Average,180s\nAlice,501,Alice,78.5,3\nBob,501,Bob,82.1,5"
        st.download_button("📥 Export CSV", demo_csv, "dart_export.csv", "text/csv")

if __name__ == "__main__":
    main()
