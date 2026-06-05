# Dart Game Pro Changelog

## [3.0.0] - 2026-06-05

### 🚀 Major Release: Sublime UI + Custom Game Modes + Deep Analytics + Practice Suite

**v3.0** is a feature-packed major release focused on **added value**, player creation, and a sublime modern experience. Built on the solid v2.4 foundation with the latest popular tools (Streamlit components + theming, Plotly interactive viz, pandas exports, pyttsx3 voice, rich custom engine).

Completely revamped emphasis on **Custom Game Modes**, **Analytics depth**, **Practice tools**, **UI polish**, and social features — making it the most fun and feature-rich dart app for casual, serious, and creative players.

#### ✨ Standout New Additions

**🎲 Custom Game Mode System (v3.0 Flagship)**
- Complete **Wizard in Play tab**: Style selection, difficulty, 8+ special rules.
- **Surprise Me** instant random wacky mode generator.
- **Sublime Preview Cards**: Emoji, flavor description, est. playtime, tags, rules, multiplier — see before save.
- **15+ High-Impact Features** (community-driven): Edit/Duplicate/Delete, local play counts + best scores, "Play Again", Recents, full JSON export/share/import, funny generation messages, vastly improved name generator (puns, themes, "Insane Point Pandemonium"), tags, more.
- **Real Gameplay**: Smart mapping to wired engine modes (Survival → killer_party with lives/variants, Only Doubles → out_rule, etc.). Rules shown live + stats tracked.
- Persisted + integrated with Analytics, Leaderboards, Exports, Achievements.

**📊 Sublime Analytics & Stats**
- Full per-player/session dashboard: 3-dart avg, **First 9 avg**, **Checkout success % by remaining score**, overall checkout rate, 180s, best/worst throws, etc.
- **Advanced Plotly Heatmaps** (3D trajectory, clusters, drift, density) with textual analysis.
- Live **PPI (Pressure Performance Index)** clutch stats.
- **Per-leg/turn history**, session reports.
- **Exports**: CSV (pandas) + enhanced JSON for customs/modes.
- Powered by core player stats + DB.

**🏋️ Practice & Training Suite**
- **Checkout Trainer**: Real suggestions from `checkout.py` (filtered by out rule) — practice any finish.
- **Target Practice Drills**: Custom segment (20s, doubles, etc.) with hit-rate simulator for consistency.
- Seamless with Custom Game Modes for personalized practice + classic modes (Bob's 27 variants, ATC, Shanghai, etc.).
- Weakness insights via heatmaps/PPI/coach.

**🎨 Sublime Modern UI/UX Overhaul**
- **Beautiful layout**: Custom CSS (rounded cards, themed metrics, subtle backgrounds), heavy `st.container(border=True)`, columns, expanders, emojis everywhere.
- **Handicaps + Multi-Profiles** in setup for fair/fun play + stats.
- **Achievements** fully integrated in UI (live checks, progress, unlocks on game end).
- **Local Leaderboards** (engine + per-custom/mode with play/best).
- **Multiplayer Lobby**: Create/Join persistent lobbies (join codes, open list) via core system; spectator hints.
- **Voice** polished + prominent (full commands wired to real engine).
- **Other Polish**: TV Mode + Onboarding hints, eye-comfort themes global, robust undo, session summaries, "Surprise Me" discovery, better errors/responsiveness.

**Other Major Added Features**
- More game types fully exposed/wired (Cricket full variants, Party classics like Killer/Half It, subs now real not CountUp fallbacks).
- Enhanced DB for customs, stats, PBs, challenges.
- Exports & sharing everywhere (custom JSON, stats CSV).
- Focus on **creativity & retention**: Custom modes feel premium and alive.

#### 📦 Key Files Added/Changed
- `custom_game_mode.py` (full system + wizard logic)
- Major updates to `ui/streamlit_app.py` (Play overhaul, Analytics, Practice, Lobby, Achievements, CSS, etc.)
- `core/engine.py` (more wiring for customs/subs)
- Docs updated (this CHANGELOG, README sublime rewrite, ROADMAP, feature status)

See README for sublime new layout + feature focus (no bugfix walls).

### How to Upgrade
1. `git pull origin main`
2. `pip install -r requirements.txt` (plotly, pandas already recommended)
3. `python main.py` or `streamlit run ui/streamlit_app.py`
4. Dive into **Play → Custom Game Mode** wizard and **Analytics** tab first!

---

## [2.4.0] - 2026-06-05 (Previous)

(Previous release focused on 30 Cool Features wishlist implementation, voice, heatmaps, scaling, themes, etc. See full history or git tags for details. v3.0 shifts emphasis to major new player-facing systems and sublime experience.)

---

## Previous Versions
- **v2.3** — Unified engine, 30+ game modes, DartBot 12 levels, Career mode, basic analytics, voice input foundation.
- **v2.0 – v2.2** — Core game modes, AI opponents, achievements, tournaments, ELO system.

**Full credit to the original wishlist and roadmap for guiding this major release.** 

Let's keep building the ultimate darts platform! 🎯