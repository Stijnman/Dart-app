# 🎯 Dart Game Pro v2.3

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-102%20passing-brightgreen.svg)](tests/)
[![Modes](https://img.shields.io/badge/Game%20Modes-30-orange.svg)](#game-modes)
[![Features](https://img.shields.io/badge/Features-256-blueviolet.svg)](#feature-overview)

> The most comprehensive dart scoring application available — 30 game modes, AI opponents, career simulation, tournaments, deep analytics, and more. Built for casual players and serious competitors alike.

![Dart Game Pro](https://img.shields.io/badge/Dart%20Game%20Pro-v2.3-00cc88?style=for-the-badge)

---

## ✨ Feature Overview

| Category | Features | Count |
|----------|----------|-------|
| **Game Modes** | X01 variants, Cricket variants, Practice, Party, Specialty | 30 |
| **AI & Bots** | 12-level DartBot, SmartBot adaptive AI, 8 Pro simulations | 20 |
| **Career & Progression** | Career mode, ELO system, graded leagues, achievements | 35 |
| **Analytics** | Heatmaps, trends, consistency rating, pattern detection, AI coach | 30 |
| **Tournaments** | Knockout, Round-Robin, League formats with brackets | 15 |
| **Social & Sharing** | WhatsApp share, stats cards, match reports, live links | 20 |
| **Customization** | 6 themes, theme shop, virtual dartboard, equipment tracking | 25 |
| **Quality of Life** | Undo/redo, save/resume, voice input, bounce-out detection | 25 |
| **Online Framework** | Lobby system, matchmaking, chat, spectator links | 15 |
| **Training** | AI coach, training plans, skill assessment, weakness analysis | 25 |
| **TOTAL** | | **~256** |

---

## 🎮 Game Modes

### X01 Games (11 variants)
| Mode | Description |
|------|-------------|
| 101, 170, 201, 210, 301, 501, 701, 901, 1001, 1501 | Standard X01 with configurable in/out rules |
| Custom X01 | Any starting score from 2 to 1501 |

### Cricket Variants (7 modes)
| Mode | Description |
|------|-------------|
| Standard Cricket | Classic 15-20 + Bull, close to score |
| Cut-Throat | Points go to opponents |
| No-Score Cricket | Close-only, no points |
| Tactic Cricket | Power-play rounds for double points |
| Random Cricket | Random target numbers each game |
| Hammer Cricket | Last to close gets penalized |
| Cricket Count Up | Score on cricket numbers only |

### Practice Games (8 modes)
| Mode | Description |
|------|-------------|
| Bob's 27 | Hit doubles 1-20 + Bull, 3 lives |
| Around the Clock | Hit 1-20 + Bull (Singles/Doubles/Triples variants) |
| Shanghai | Hit S+D+T of round number |
| Count Up | Score max points in fixed rounds |
| Bermuda | Round-specific targets, miss = 0 |
| JDC Challenge | Junior Darts Corp target sequence |
| 41-60 Practice | Hit 41 through 60 in order |

### Party Games (3 modes)
| Mode | Description |
|------|-------------|
| Killer | Claim a number, eliminate others |
| Half It | Miss = score halved |
| Gotcha | Match or beat the leader each round |

### Specialty Games (5 modes)
| Mode | Description |
|------|-------------|
| Baseball | 9 innings on the dartboard |
| Team ATC | Team relay Around the Clock |
| Eliminator | Last to checkout is eliminated |
| Roadrunner | Stay ahead of the pro for 30 rounds |
| Escalator 20 | Level up through 15 difficulty tiers |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/Stijnman/Dart-app.git
cd Dart-app

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install streamlit pyttsx3 matplotlib

# Launch the application
streamlit run main.py
```

### Docker (Optional)

```bash
# Build and run with Docker
docker build -t dart-game-pro .
docker run -p 8501:8501 dart-game-pro
```

Then open your browser to: **http://localhost:8501**

---

## 📸 Screenshots

| Play Tab | Analytics | Tournament |
|----------|-----------|------------|
| Dark theme scoreboard with checkout suggestions | Board heatmap, ELO rating, pattern detection | Bracket visualization, standings table |

---

## 🏗️ Architecture

```
Dart-app/
├── main.py                 # Entry point
├── core/                   # Game engine & logic
│   ├── engine.py           # Universal game engine (30 modes)
│   ├── game_state.py       # State management with undo/redo
│   ├── player.py           # Player model with stats
│   ├── checkout.py         # PDC checkout tables (2-170)
│   ├── dartbot.py          # 12-level probabilistic AI
│   ├── constants.py        # Game configs, bot levels
│   ├── database.py         # v1 SQLite (players, games, stats)
│   ├── database_v2.py      # v2 tables (ELO, career, saves)
│   ├── achievements.py     # 35 achievements + challenges
│   ├── extensions.py       # Analytics, export, tournaments
│   ├── gamemodes.py        # 11 additional game modes
│   ├── systems.py          # Career, ELO, patterns, social
│   └── __init__.py         # Package exports
├── ui/
│   └── streamlit_app.py    # Complete UI (9 tabs)
├── tests/                  # 102 automated tests
├── .github/
│   ├── workflows/          # CI/CD
│   └── ISSUE_TEMPLATE/     # Issue templates
├── requirements.txt
├── LICENSE
├── CONTRIBUTING.md
└── README.md
```

---

## 🤖 AI & Bot System

### DartBot (12 Difficulty Levels)
| Level | Name | 3-Dart Avg | Description |
|-------|------|-----------|-------------|
| 1 | Beginner | ~25 | Random scatter |
| 3 | Social Player | ~40 | Hits board consistently |
| 5 | Club Player | ~55 | Targets T20 regularly |
| 7 | County Player | ~72 | Strong scoring |
| 9 | Pro Tour | ~88 | Professional standard |
| 12 | World Champion | ~105 | Elite accuracy |

### SmartBot (Adaptive AI)
- Analyzes your recent performance
- Dynamically adjusts difficulty to match your level
- Provides real-time challenge description

### Pro Simulation
Play against 8 professionally modeled players including Michael van Gerwen, Luke Littler, Luke Humphries, and more — each with realistic averages, checkout rates, and playing styles.

---

## 📊 Analytics Engine

- **Board Segment Heatmap** — See where you score most
- **30-Day Trend** — Track improvement over time
- **Consistency Rating** — Measure throw-to-throw stability
- **Checkout Success by Range** — Identify finishing weaknesses
- **AI Pattern Detection** — Fatigue, inconsistency, scoring power analysis
- **Weakness Analysis** — Pinpoint your worst doubles

---

## 🏆 Career Mode

Complete a full season of 15 PDC events:
- World Championship, Premier League, World Matchplay, and more
- Prize money tracking with realistic distributions
- World Ranking system with Order of Merit
- Career statistics and personal bests

---

## 🛠️ Development

### Running Tests
```bash
pytest tests/ -v
```

### Project Structure
The codebase follows clean architecture principles:
- **Separation of concerns**: Engine, UI, and data layers are independent
- **Extensible mode system**: Adding new game modes requires minimal changes
- **Comprehensive state management**: Full undo/redo with snapshot pattern

### Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📝 Changelog

### v2.3 (Current)
- Full integration of all 30 game modes into unified engine
- Universal scoreboard supporting all modes
- Complete UI overhaul with 9 functional tabs
- GitHub best practices: templates, code of conduct, contributing guide

### v2.2
- 11 additional game modes (standalone)
- Systems module: Career, ELO, patterns, social
- Voice recognition scoring

### v2.1
- 30 new features: achievements, tournaments, training, themes
- Analytics extensions

### v2.0
- 15 core game modes with full scoring logic
- 12-level DartBot AI with probabilistic checkouts
- 161 PDC checkout tables
- SQLite database with player profiles

---

## 📜 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Checkout tables based on PDC official data
- Inspired by popular dart apps: DARTSLIVE, Lidarts, Score Darts, n01
- Built with [Streamlit](https://streamlit.io)

---

<p align="center">
  <b>🎯 Dart Game Pro — Play Like a Pro</b><br/>
  <a href="https://github.com/Stijnman/Dart-app">GitHub</a> •
  <a href="https://github.com/Stijnman/Dart-app/issues">Issues</a> •
  <a href="https://github.com/Stijnman/Dart-app/blob/main/CONTRIBUTING.md">Contribute</a>
</p>
