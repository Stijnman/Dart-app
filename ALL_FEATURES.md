# 🎯 Dart Game Pro v3.0 - Complete Feature List

[![Version](https://img.shields.io/badge/version-3.0-blue)](https://github.com/Stijnman/Dart-app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?logo=streamlit)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.15+-brightgreen)](https://plotly.com)

**The most comprehensive, sublime dart scoring & practice app.**

<<<<<<< Updated upstream
**v3.0** is a major release focused on **added value**, player creativity, deep insights, training tools, and a modern, beautiful UI experience. Built with the latest popular tools and practices (Streamlit modern components + theming/CSS, Plotly for stunning interactive visualizations, pandas for exports, pyttsx3 for voice, rich dataclasses for custom modes, persistent SQLite, etc.).
=======
**v3.0** is a major release focused on **added value**, player creativity, deep insights, training tools, and a modern, beautiful UI experience. Built with the latest popular tools and practices (Streamlit modern components + theming/CSS, Plotly for stunning interactive visualizations, pandas for exports, pyttsx3 for voice, rich Python dataclasses for custom modes, persistent SQLite, etc.).
>>>>>>> Stashed changes

This document consolidates **ALL FEATURES**:
- Core from previous versions + v2.4 "30 Cool Features" wishlist.
- **New in v3.0** from community/competitor analysis (Statistics, Practice, Custom Modes, UI/UX, Multiplayer, AI, Data/History, Polish, etc.).
- Status: Implemented, Enhanced, Partial, or Future (with notes on location in code).

<<<<<<< Updated upstream
Layout is clean, scannable, and "sublime" with emojis, tables, categorized sections, and highlights for new additions.
=======
Layout is clean, scannable, and "sublime" with emojis, tables, categorized sections, and highlights for new additions. Many competitor gaps from the deep analysis are now closed or significantly improved for a local/Streamlit experience.
>>>>>>> Stashed changes

See [README.md](README.md) for sublime marketing-focused overview (added things, not bugfixes), [CHANGELOG.md](CHANGELOG.md) for release notes, and code for implementation.

---

## 🚀 Quick Start
```bash
pip install -r requirements.txt
python main.py
# or
streamlit run ui/streamlit_app.py
```

**New in v3.0 Highlights to Try First**:
- Play tab → Custom Game Mode expander (wizard, Surprise Me, preview).
- Analytics tab (deep stats + exports).
- Practice drills in Play (checkout trainer, target practice).
- v3.0 Advanced tab for themes, coach, PPI, heatmaps, lobby.

---

## 🎮 Core Gameplay & Game Modes (30+)

Engine supports native + real sub-engines (many wired in v3.0 from CountUp fallbacks to dedicated classes like KillerGame, DartsGolf, TicTacToeDarts, TacticsJokerGame, etc.).

### X01 Games
- 101, 170, 201, 210, 301, 501, 701, 901, 1001, 1501 (with handicaps, best-of legs/sets, in/out rules: double/master/straight).

### Cricket (Full Variants - Enhanced Exposure)
- Standard, Cut-Throat, No-Score, Tactic, Random, Hammer (marks, points, closing, winner logic in engine + UI scoreboard).

### Practice
- Bob's 27 (Easy/Standard/Hard)
- Around the Clock (Single/Double/Triple)
- Shanghai (Standard/Quick)
- Count Up, Bermuda, JDC Challenge, 41-60, Cricket Count Up

### Party
- Killer (native + killer_party sub with lives/difficulty variants)
- Half It
- Gotcha

### Specialty / Wired Subs (v3.0 Real Classes)
- Baseball, Team ATC, Eliminator, Roadrunner, Escalator 20, Chase the Dragon
- Darts Golf (18-hole style), Tic-Tac-Toe Darts (3x3 grid), Shanghai Championship

### Tactics
- Tactics Joker (highly customizable with builder, presets, joker numbers, bull subs, config)

### Classic
- Golf, Tic-Tac-Toe, Shanghai Championship, Bob27, Game 121, Halve It

**v3.0 Additions**: Full wiring for subs (no more simplified CountUp fallbacks for golf/tictactoe/killer_party/tactics_joker etc.), handicaps in setup, variant support, custom mode mapping to these.

**Future**: More conditional rules, team variants, time attack.

---

## 🎲 Custom Game Mode System (v3.0 Flagship - All New/Enhanced)

Complete end-to-end system in `custom_game_mode.py` + deep integration in `ui/streamlit_app.py` Play tab.

<<<<<<< Updated upstream
- **Wizard UI**: Select style (Scoring Race, Target Hunting, Survival, Chaos Mode), starting score, difficulty, special rules.
=======
- **Wizard UI**: Select style (Scoring Race, Target Hunting, Survival, Chaos Mode), starting score, difficulty (Easy/Normal/Hard/Brutal), special rules.
>>>>>>> Stashed changes
- **Surprise Me**: One-click random wacky mode generator.
- **Name Suggestions**: 5+ funny/wacky/punny options (improved generator with themes like "Insane Point Pandemonium", "Chillax Madhouse Mayhem", puns, "The Cursed...", "Darts Gone Wild").
- **Beautiful Preview Cards** (sublime): Emoji + short flavor text/description, estimated playtime (e.g. ~7 min), tags (e.g. "survival", "high-score"), rules, multiplier, win condition — see *before* saving.
- **15+ High-Impact Polish** (directly from analysis/feedback):
  1. Surprise Me button (very high engagement).
  2. Emoji + short description/flavor per mode.
  3. Show expected playtime.
  4. "Play Again" button on saved modes.
  5. Better/funnier name generator (puns, creative, themed).
  6. Show how many times played + best score (local stats).
  7. Expanded Special Rules (8+ : Only Doubles, Bust = Lose Life, Must hit bull to win, Triple points only, No 180s, Reverse scoring (lowest wins), Sudden death on any checkout, All scores doubled after round 3).
  8. Preview card before saving (sublime UX).
  9. Edit saved mode.
  10. Tags/Categories (Short, Chaotic, Competitive, etc.).
  11. Local leaderboard per custom mode (play count, best score).
  12. Export mode as JSON (share with friends; full data incl. stats).
  13. Duplicate Mode button.
  14. Recent modes section (last 5 played).
  15. Funny loading/generation messages ("Generating pure chaos...", "Mayhem loading...").
  + Bonus: Delete, Play from saved list, auto-increment stats on use, integration with engine for real play + rules display.
- **Actually Playable & Integrated**:
<<<<<<< Updated upstream
  - Maps to real engine modes (e.g. Survival → killer_party with lives, Scoring Race → count_up with round_limit, Only Doubles → out_rule=double, Target Hunting → around_the_clock).
=======
  - Maps to real engine modes (e.g. Survival → killer_party with lives/variant, Scoring Race → count_up with round_limit, Only Doubles → out_rule=double, Target Hunting → around_the_clock).
>>>>>>> Stashed changes
  - Rules shown live in Play (banner with name, win condition, specials, multiplier).
  - Stats tracked (play_count, best_score) via `play_custom_mode()`.
  - Handicaps, bot, voice, undo all work.
- **Persistence & Sharing**: Saved to `data/custom_modes.json`. Export full JSON for import/share. Use in leaderboards, analytics, exports.
<<<<<<< Updated upstream
- **Stats & Gamification**: Per-custom leaderboards, best scores, recents. "🏆 Record my score as best" during play.
=======
- **Stats & Gamification**: Per-mode play counts, best scores, recents. "🏆 Record my score as best" during play.
>>>>>>> Stashed changes
- **In UI**: Expander in Play (before/after game setup). "Use this Custom" auto-starts with mapping. Saved list with emoji, details, Play/Edit/Dup/Del buttons.

**Addresses Competitor Gaps**: Advanced rule creation (specials + win conditions like best-of, highest after rounds, last man standing), customization depth (checkout rules via mapping, bull value, #darts implied), win conditions variety, per-mode stats/leaderboards, share/export (JSON), edit/duplicate, preview, tags, surprise/random, funny UX.

**Future**: Full conditional rules engine (e.g. "if score >100 then 2x"), procedural generation, story modes, public library (needs backend), animated GIF exports.

**Files**: `custom_game_mode.py`, integrated in `ui/streamlit_app.py` (Play + wizard function), used in start_new_game, analytics, exports.

---

## 📊 Analytics & Statistics (Major v3.0 Enhancements - Closed Many Gaps)

Overhauled `show_analytics_page()` + integrated in Play/v3.0 Advanced. Pulls from real `Player.get_stats_summary()`, engine history/state, DB, v2.4 modules.

- **Core Stats** (per player/session, from throws/legs):
  - 3-dart average, **First 9 darts average** (exactly as requested in analysis).
  - **Checkout success rate %** (overall + attempts/successes).
  - **Checkout % by remaining score** (detailed per player by score range/bucket e.g. ~80, ~100, ~170 — aggregated from history + checkout.py).
  - 100s, 140-179, 180s counts.
  - Best/worst throw, total scored, darts thrown.
  - Highest checkout.
- **Advanced Visuals**:
  - **Interactive Advanced Heatmaps** (3D trajectory + clusters + 2D density via Plotly; fallback matplotlib; with analysis text on consistency, drift, favorites/weak segments).
  - **Pressure Performance Index (PPI)**: Clutch factor (ahead/behind, close games, checkout range). get_clutch_stats().
- **History & Reports**:
  - **Per-leg/turn breakdown** (full history with messages, scores after, is_bust/is_checkout/180s).
  - Recent visits/legs.
  - Session summaries.
- **Exports** (new/easy win):
  - CSV (pandas DataFrame of stats, mode, etc.) — download button.
  - JSON for customs/modes (full data incl. stats, rules).
- **Other**:
  - Long-term trends via DB (personal bests, challenges, player_stats).
  - Player comparison hints via leaderboards.
  - Checkout success detailed by range (enhanced from partial).
  - Pattern detection (fatigue etc. via existing + PPI/heatmap).

**Addresses Analysis**: Per-leg/turn, checkout % by score range (detailed), heatmaps (advanced 3D+), first9, consistency (PPI + std via analysis), session reports, personal records, trends, exports (CSV/Excel-like via pandas/JSON), player comparison foundation.

**In UI**: Dedicated Analytics tab (rich when game active; demo fallback). Also in Play (PPI/heatmap teasers), v3.0 Advanced, custom integration.

**Files**: `ui/streamlit_app.py` (show_analytics_page + exports), `core/player.py` (get_stats_summary + first_nine), `core/advanced_heatmap.py`, `core/pressure_performance_index.py`, `core/database.py` (save_player_stats etc.), engine history/leaderboard.

**Future**: Full PDF/Excel reports, photo attachments, notes per game, velocity (acoustic), animated GIF leaderboards.

---

## 🏋️ Practice & Training Features (New Suite + Enhancements)

- **Dedicated Practice Drills** (new in Play expander):
  - **Checkout Trainer**: Practice finishing from any remaining (2-170). Real suggestions from `core/checkout.py` (get_best_checkout + filter_checkouts_by_out_rule respecting game out_rule). "Get Checkout Suggestion" button.
  - **Target Practice**: Choose segment (e.g. 20 for 20s, or doubles). Simulate 3-dart throws with realistic hit rate (70% demo). "Hits on X: Y/3" for consistency training. Addresses "Target Practice modes", "Checkout Practice".
- **Integrated with Modes**: Select "Practice" category (Bob's 27 Easy/Standard/Hard with lives, Around the Clock Single/Double/Triple, Shanghai, Count Up, etc.) for full games with real engine scoring/feedback.
- **Custom Practice**: Use Custom Game Mode for personalized drills (e.g. "Target Hunting" style, "Time Attack" via round_limit, "Survival" for lives-based).
- **AI Coaching & Feedback**: Real-time suggestions with explanations (CoachingMode). Pattern/weakness detection (heatmap favorites/weak + PPI + player_analytics). Post-throw/leg insights.
- **Other Training**: 180 streak practice via history, weakness analysis (via analytics tab), daily-style via recents.

**Addresses Analysis**: Target practice, checkout practice/ trainer, Around the Clock/Bob's 27/Shanghai (full), custom practice routines, AI coach for optimal moves + why, practice drills with real-time feedback, 180 streak. (Daily plans, full weakness AI as future extensions on existing modules.)

**In UI**: Play tab drills expander (always when game running). Mode selector for full practice games. Analytics for insights. Custom wizard for routines.

**Files**: `ui/streamlit_app.py` (drills + integration), `core/checkout.py`, `core/engine.py` (practice modes), `core/coaching_mode.py`, `core/player_analytics.py`, `core/advanced_heatmap.py`, `custom_game_mode.py`.

**Future**: Time Attack, more guided drills (T20 accuracy, 180 streak specific), full custom routines builder, daily training plans.

---

## 🤖 AI & Bot Features

- **DartBot**: 12 levels (Beginner to Machine). Realistic variance, pressure modifiers on checkout. get_bot_throw().
- **SmartBot + Adaptive Scaling**: Analyzes performance (recent throws, checkouts attempted/made). Auto-adjusts difficulty in real-time during match. Player-friendly messages.
- **Coaching Mode**: Suggests optimal targets with clear "why" explanations (context: remaining, opponent, pressure, legs). Post-leg reports. Multiple styles (aggressive/balanced/safe).
- **Ghost Bot**: Clones player profiles (favorites/weak from heatmap) for practice against "yourself".
- **Pattern Detection**: Fatigue, inconsistency, power (via player_analytics + heatmap + PPI).
- **Pro Simulation**: Realistic high-level bots.
- **Achievements Tracking**: 35 with progress (not just binary). check_game_end on win/loss, 180s, streaks, modes played. UI display + unlocks.
- **Weakness Analysis**: Heatmaps (favorites/weak segments), PPI, coach suggestions, analytics stats.

**Addresses Analysis**: Difficulty scaling (full), AI coach (suggest optimal + explain), pattern detection, personalized recs (via stats/heatmap/coach), smart AI opponents (different styles via profiles/ghost), bot tournament foundation (career/pro events).

**In UI**: v3.0 Advanced tab (coach, PPI, heatmaps), Play (bot throw button, coach teaser), Analytics (insights), Achievements expander.

**Files**: `core/dartbot.py`, `core/smartbot_autoscale.py`, `core/coaching_mode.py`, `core/ghost_bot.py`, `core/player_analytics.py`, `core/achievements.py`, `core/engine.py` (bot integration), `ui/streamlit_app.py`.

**Future**: Psychological bot (mood state), full personalized daily plans, bot tournaments spectator.

---

## 👥 Multiplayer, Social & Competitive

- **Multiplayer Lobby** (new/enhanced UI): Create lobby (host), join by code, list open lobbies. Persistent via storage (DB-like). Uses `core.systems.LobbySystem` + OnlineMatch.
- **Online Match / LobbySystem**: Host, players list, status (waiting), join_code, created_at. Persisted.
- **Spectator Mode**: Hints/links in lobby (real-time limited by Streamlit; foundation exists).
- **Local Leaderboards**: Per mode/custom (play counts, best scores, rankings). Engine.get_leaderboard() + custom stats.
- **Career / Tournaments / ELO**: CareerMode, ELO with dynamic K, tournaments (brackets, pro events), ladder league (tiers promo/demotion, seasonal).
- **Challenges**: Daily/weekly, persistent in DB v2.
<<<<<<< Updated upstream
- **Achievements**: 35 milestones (100 games, 10 180s, 50 streak, etc.). Progress tracking, unlocks.
=======
- **Achievements Badges**: 35 milestones (100 games, 10 180s, 50 streak, etc.). Progress tracking, unlocks.
>>>>>>> Stashed changes
- **Custom Mode Sharing**: Export JSON (full config + stats) for friends. Import support via wizard.
- **Handicaps**: Per-player in setup for fair multiplayer.
- **Team Modes**: Partial (Team ATC, team relay hints).

**Addresses Analysis**: Online multiplayer (lobby + foundation; real-time hard but stub improved), spectator, friend challenges (via lobby/career), global/local leaderboards (local per mode/custom + sharing), match history (engine history + DB), tournament creator (stub + career), team modes, leaderboard sharing (JSON + stats), achievement badges (full + UI).

**In UI**: Play (lobby expander), v3.0 Advanced / Career tab, custom export, leaderboards in expanders.

**Files**: `core/systems.py` (LobbySystem, OnlineMatch, CareerMode etc.), `core/engine.py` (ELO/tournament), `core/tournament.py`, `core/ladder_league.py`, `ui/streamlit_app.py` (lobby UI + integration), `custom_game_mode.py` (export), DB v2.

**Future**: Full real-time (WebSocket), global leaderboards (backend), animated GIF top moments, push challenges, full bracket creator.

---

## 🎨 UI/UX Enhancements (Sublime Modern Overhaul - v3.0)

- **Modern Sublime Layout**: Custom CSS (rounded buttons/cards/metrics, subtle backgrounds, high-contrast themes). Heavy use of `st.container(border=True)`, columns, expanders, st.metric, emojis. Responsive feel.
- **Theming**: 5+ (classic, neon, retro, minimal, dark_pro, holographic). Eye comfort (OLED, blue light filter, adjustable brightness). Global apply + per-custom.
- **Voice Input**: Enhanced (text input for commands/scores: t20, undo last, skip turn, show stats, checkout, cheer). Full engine integration (recognize + execute + record_throw/switch_player/undo). Placeholder for real STT (browser mic, whisper).
- **Handicaps & Profiles**: In setup (number inputs + selectbox for active profile/stats). Fair play + tracking.
- **Achievements Display**: Live in expander (unlocked icons, progress, "Check Achievements" button that runs check_game_end).
- **Leaderboards & Stats**: Prominent in expanders (per mode/custom, with counts/bests).
<<<<<<< Updated upstream
- **Multiplayer UI**: Lobby create/join/list (codes, status, spectator hints).
=======
- **Multiplayer UI**: Lobby create/join/list (codes, status).
>>>>>>> Stashed changes
- **Exports**: CSV (stats), JSON (customs/modes with full data) — download buttons everywhere.
- **Onboarding + TV Mode**: Dedicated expanders/hints (cast to big screen, large fonts, new user guide in setup).
- **Other Polish**:
  - Robust undo/redo (capped stack, post-bust/win safe).
  - Session summaries, recent history, "Play Again"/recents.
  - "Surprise Me" discovery.
  - Better error handling/toasts.
<<<<<<< Updated upstream
  - Accessibility: High contrast themes, emojis, clear labels, keyboard-friendly Streamlit.
  - Custom mode preview cards (sublime UX).
  - TV-friendly (headless + hints).

**Addresses Analysis**: Dark/light + custom themes (enhanced), voice input (polished), quick undo/redo (robust + UI), TV mode (hints), onboarding (guide), customizable dartboard/themes (full), accessibility (high contrast + more), gesture (web), offline (full local + DB), etc.
=======
  - Accessibility: High contrast themes, emojis, clear labels.
  - Custom mode preview cards (sublime UX).
  - TV-friendly (headless + hints).

**Addresses Analysis**: Dark/light + custom themes (enhanced), voice input (polished), quick undo/redo (robust + UI), TV mode (hints), onboarding (guide), customizable dartboard/themes (full), accessibility (high contrast + more), gesture (web), offline (full local + DB).
>>>>>>> Stashed changes

**In UI**: Play (setup with new options, drills, custom wizard, lobby, voice, leaderboards), Analytics (exports, rich viz), v3.0 Advanced (themes, coach, etc.), Settings.

**Files**: `ui/streamlit_app.py` (main overhaul + CSS in apply_theme + all sections), `core/extended_themes.py`, `core/systems.py` (lobby), `custom_game_mode.py`.

**Future**: Full mobile (custom components for haptics), AR, streaming overlays (Twitch), smart dartboard API, more 3D board viz.

---

## 🏆 Achievements, Data & History

- **35 Achievements**: Tracked with progress (not binary). check_game_end on game end (won, mode, stats like 180s, streaks, modes played). UI display + auto-unlock toasts.
<<<<<<< Updated upstream
- **Session / Match History**: Full per-throw/leg (engine.state.history as TurnRecord: darts, total, message, score_after, is_bust/checkout/180s). Undo stack (snapshots).
=======
- **Session / Match History**: Full per-throw/leg (engine.state.history as TurnRecord: darts, total, message, score_after, is_bust/checkout/180). Undo stack (snapshots).
>>>>>>> Stashed changes
- **Per-Mode / Custom Stats**: Play counts, best scores, leaderboards (local).
- **Personal Bests**: DB tracked (update on high scores/checkouts).
- **Exports & Sharing**:
  - Stats CSV (pandas, full session).
  - Custom/mode JSON (share/import, includes rules + stats).
  - Share text/images (systems generate).
- **DB Persistence** (v1 + v2): Games, player_stats, personal_bests, challenges (daily/weekly), login streaks, equipment, match_history, FKs, migrations. Context managers, UPSERT.
- **Career / Seasons**: CareerMode with tournaments, ELO, seasonal processing.
- **Notes / Replays (Foundation)**: History as basic replay (re-run throws). DB for save/resume. Custom JSON for "notes".

**Addresses Analysis**: Achievements badges (full + UI), per-mode stats/leaderboards/history, session reports/summaries, exports (CSV/JSON + PDF foundation via pandas/matplotlib), replay (state sequence + history), personal bests, career stats, challenges.

**In UI**: Analytics (history + exports), Play (recent + leaderboards + achievements), custom (stats + export), DB auto on wins.

**Files**: `core/achievements.py`, `core/database.py` + `database_v2.py`, `core/engine.py` (history + check), `core/systems.py` (save_game, share), `custom_game_mode.py`, `ui/streamlit_app.py` (displays + exports).

**Future**: Full PDF/Excel with highlights/trends (reportlab), photo attachments to sessions, per-game notes, slow-mo replay viz (matplotlib animation), cloud sync, GIF exports.

---

## Other Notable / Polish / Bonus

- **Offline Mode**: Full (local DB + Streamlit desktop/app).
- **Multiple Profiles**: Stub (select in setup for stats; extendable to full switcher).
- **Seasons / Leagues**: LadderLeagueSystem (tiers, promo/demotion, ELO, seasonal), Career with tournaments.
- **Handicaps**: Full support in engine + UI setup.
- **Accessibility**: High-contrast themes, clear metrics/labels, emojis, keyboard-friendly Streamlit.
- **Bonus from Analysis**: Time Attack (via custom round_limit), gesture (web touch in Streamlit), offline strong. Hardware (Autodarts stub via auto_scorer). Cloud (future).
- **Code Quality**: Type hints, snapshots for undo, validation, clean architecture. 100+ tests.
- **Audio/Voice Foundation**: pyttsx3 TTS (activated in audio_engine), placeholders for full STT/acoustic (auto_scorer sim).

**Addresses Remaining Gaps**: Most "easy wins" and many medium from analysis now done (stats depth, practice, customs, UI polish, exports, achievements, lobby, handicaps, profiles, voice, themes, accessibility, per-mode stats). Harder ones (real-time multi, full replays, AR, psychological AI, hardware) have foundations or noted as future.

---

## Implementation & Files

- **Core**: `core/engine.py` (modes, custom mapping, stats, handicaps, achievements), `custom_game_mode.py` (full system), `core/player.py` (stats), `core/*` (analytics, coach, heatmap, checkout, DB, achievements, systems/lobby, etc.).
- **UI**: `ui/streamlit_app.py` (Play with wizard/drills/lobby/setup, Analytics rich + exports, v3.0 Advanced, CSS/themes).
- **Docs**: README (sublime added-focus), CHANGELOG, ROADMAP, feature_status (updated for v3.0), ALL_FEATURES.md (this file).
- **Other**: `data/` (darts_v2.db, custom_modes.json), requirements.txt (plotly, pandas, pyttsx3).

**Tests**: 105+ (engine, modes, customs via sims). Edge cases simulated (busts incl. score=1, only-doubles customs, undo, voice, subs, handicaps) — clean, no crashes.

**How Features Work Together**: Start game (with custom/ handicap) → Play with 3-dart/voice → Drills for practice → Analytics for insights/exports → Achievements unlock → Custom stats/leaderboards update → Lobby for social.

This makes Dart Game Pro v3.0 a **sublime, feature-rich** app that closes many competitor gaps while staying fun, local-first, and extensible.

For full details, run the app and explore Play + Analytics + v3.0 Advanced tabs!

**Built with ❤️ using latest popular tools for dart players everywhere.** 

(Generated/updated as part of v3.0 improvements. See git history for exact PRs/commits.)