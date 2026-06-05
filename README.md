# 🎯 Dart Game Pro v3.0

[![Version](https://img.shields.io/badge/version-3.0-blue)](https://github.com/Stijnman/Dart-app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?logo=streamlit)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.15+-brightgreen)](https://plotly.com)

**The most comprehensive, sublime dart scoring & practice app.**

**v3.0** delivers a major leap: a fully-featured **Custom Game Mode system**, **sublime modern UI**, **deep Analytics**, **Practice Drills suite**, enhanced multiplayer/social features, and more — built with the latest popular tools (Streamlit, Plotly, pandas, pyttsx3). Focus on **added value** for players and creators.

---

## ✨ What's New in v3.0 — Major Additions

**Sublime UI + Powerful New Systems** built with the latest & most popular tools: Streamlit (modern components, theming), Plotly (stunning interactive viz), pandas (exports), pyttsx3 (voice), rich custom mode engine, and deep integration with existing core (engine, DB, analytics modules).

### 🎲 Custom Game Mode 2.0 (Standout Feature)
- Full **Custom Game Mode Wizard** in Play tab: Choose style (Scoring Race, Target Hunting, Survival, Chaos), difficulty, special rules.
- **Surprise Me** random generator with wacky/funny names.
- **Beautiful Preview Cards** with emoji, description, estimated time, tags, rules, multiplier *before* saving.
- **15+ High-Impact Polish** (from community feedback): Edit/Duplicate/Delete saved modes, local play counts + best scores, "Play Again", Recent modes, Export full JSON for sharing/import, funny generation messages, expanded special rules (8+ incl. "Must hit bull", "Reverse scoring", "Sudden death"), better name gen with puns/themes.
- **Actually Playable**: Maps intelligently to real engine modes (e.g. Survival → killer_party with lives, Only Doubles → proper out_rule). Rules displayed live during play.
- **Stats & History**: Per-custom leaderboards, best scores tracked in DB/JSON.
- Persisted in `data/custom_modes.json`. Use in analytics/exports.

### 📊 Sublime Analytics Dashboard
- **Deep per-player & session stats**: 3-dart avg, **First 9 avg**, **Checkout % by remaining score** (bucketed), overall checkout rate, 180s, best/worst, etc. (powered by Player.get_stats_summary).
- Interactive **Advanced Heatmaps** (3D trajectory + clusters + 2D density via Plotly, with analysis text).
- **Pressure Performance Index (PPI)** live clutch stats.
- **Per-leg/turn history** with full messages.
- **One-click Exports**: CSV/JSON of full stats for sharing or analysis.
- Long-term trends via DB.

### 🏋️ Practice & Training Suite
- **Checkout Trainer**: Real PDC-style suggestions from `checkout.py`, filtered by out rule. Practice any remaining score.
- **Target Practice**: Custom segment drills (e.g. only 20s or doubles) with hit-rate sim for consistency training.
- Full integration with existing practice modes (Bob's 27 variants, ATC single/double/triple, Shanghai) + Custom Game Mode for personalized routines.
- Weakness insights via heatmaps + PPI + coach.

### 🎨 Sublime Modern UI & UX (Layout Overhaul)
- **Beautiful, responsive layout**: Modern CSS (rounded cards, subtle themes, metrics with backgrounds), heavy use of `st.container(border=True)`, columns, expanders, emojis, st.tabs-style navigation feel.
- **Handicaps & Multi-Profiles**: Built into game setup for fair play + stats tracking.
- **Achievements & Milestones**: Live display, progress, unlocks (35 total, integrated with game end).
- **Local Leaderboards & Per-Mode Stats**: Engine + custom mode leaderboards, play counts, bests.
- **Multiplayer Lobby**: Create/Join persistent lobbies (via core LobbySystem), join codes, spectator hints.
- **Voice Commands**: Enhanced text/voice input (t20, undo, skip, stats, checkout) with full engine integration.
- **Exports Everywhere**: JSON for customs/modes, CSV for stats.
- **Onboarding + TV Mode**: Dedicated hints for big-screen casting, new user guide.
- **Theme System**: Eye comfort, OLED, brightness, holographic — applied globally.
- **Other Polish**: Undo/redo robust, session summaries, recent history, "Surprise Me" discovery, better error handling.

### Other Major Additions
- More game types fully wired and exposed (Cricket variants, Killer/Half It/Gotcha, subs like Golf/Tic-Tac-Toe/Tactics Joker with real classes not fallbacks).
- Enhanced DB persistence for games, PBs, challenges, custom stats.
- Custom mode + practice integration for endless variety.
- Focus on **player creation & fun**: Custom modes feel alive with names, emojis, previews, stats.

See full details in [CHANGELOG.md](CHANGELOG.md), [ALL_FEATURES.md](ALL_FEATURES.md) (complete list of all features), and docs/.

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py

# Or directly with Streamlit
streamlit run ui/streamlit_app.py
```

---

## 🎮 Supported Modes (30+)

### X01 Games
- 101, 170, 201, 210, 301, 501, 701, 901, 1001, 1501

### Cricket
- Standard, Cut-Throat, No-Score, Tactic, Random, Hammer

### Practice
- Bob's 27 (Easy/Standard/Hard)
- Around the Clock (Single/Double/Triple)
- Shanghai (Standard/Quick)
- Count Up, Bermuda, JDC Challenge, 41-60

### Party
- Killer, Half It, Gotcha

### Specialty
- Baseball, Team ATC, Eliminator, Roadrunner, Escalator 20, Chase the Dragon

### Tactics
- Tactics Joker

### Classic
- Golf, Tic-Tac-Toe, Shanghai Championship, Bob27, Game 121, Halve It

---

## 🏗️ Architecture

After `git clone .../Dart-app.git && cd Dart-app` (or pip install), the layout is flat at repo root:

```
Dart-app/
├── core/                    # All game logic, bots, voice, analytics, DB, themes...
│   ├── engine.py            # Universal (native + 20+ real sub-engines; recently wired golf/tictactoe/killer_party/tactics_joker etc.)
│   ├── gamemodes.py party_games.py practice_drills.py tactics_joker.py extensions.py
│   ├── ... (player, checkout, database*, achievements, coaching, ppi, heatmap, etc.)
├── ui/
│   └── streamlit_app.py     # Improved Play: real multi-mode engine, 3-dart visits, dynamic scoreboard, voice/coach integration
├── main.py                  # DB init + stable streamlit entry (headless friendly)
├── tests/
├── docs/ (feature status, integration guide, roadmap)
├── requirements.txt
└── README.md
```

Key: Many "custom" / specialty modes (Tactics Joker with builder, Darts Golf, Tic-Tac-Toe, Killer variants, Bob27 etc.) now use their dedicated classes instead of CountUp fallbacks. Checkout rules, win conditions, and JSON export for custom modes are first-class or easily extended (see plan + competitive analysis feedback).

---

## 🧪 Testing

```bash
# Run the test suite
python -m pytest tests/

# Or test specific components
python -c "from core.engine import DartGameEngine; print('Engine OK')"
python -c "from core.checkout import get_checkout; print('Checkout OK')"
python -c "from core.dartbot import DartBot; print('DartBot OK')"
```

---

## 📊 Stats & Features (v3.0 Highlights)

- **30+ Game Modes** (full native + wired real subs: Cricket variants, Killer, Golf, Tactics Joker, etc. + **Custom Game Modes**)
- **Sublime Custom Game Mode System**: Wizard, Surprise Me, preview cards, edit/dup/del, JSON export/share, live stats (play count, best), emoji/flavor/tags/time estimates, 8+ special rules.
- **Deep Analytics Dashboard**: First-9 avg, checkout % by remaining, advanced Plotly heatmaps (3D+clusters), PPI, per-leg history, CSV/JSON exports.
- **Practice Suite**: Checkout Trainer (real suggestions), Target Practice drills, integrated with customs + classic modes.
- **12 DartBot Levels** + SmartBot + Adaptive Scaling
- **35 Achievements** with live progress/unlocks in UI
- **Voice Commands** (full integration: score + controls)
- **Checkout Suggestions** (170+ , rule-filtered)
- **Personal Bests, Leaderboards** (global + per-custom/mode)
- **Handicaps, Multi-Profiles, Multiplayer Lobby** (create/join persistent)
- **Sublime UI**: Modern CSS/themes (eye comfort, OLED), cards, metrics, responsive, TV mode ready, onboarding.
- **DB Persistence**: Games, challenges, custom stats, PBs.
- **Save/Resume + Exports** everywhere.

---

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete history.

**v3.0** (2026-06-05) — Major focus on **added features** (Custom Game Modes, Sublime Analytics, Practice Suite, UI/UX overhaul, etc.). Previous v2.4 emphasized architecture fixes and bug resolution.

---

## 🤝 Contributing

Pull requests welcome! Focus areas:
- Additional game modes
- Mobile responsiveness
- Real-time online play (WebSocket backend)
- AI opponent improvements
- Tournament bracket generation

---

## 📜 License

MIT License — free for personal and commercial use.

---

**Built with ❤️ for dart players everywhere.**
