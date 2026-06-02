# Dart Game Pro v2.0

A complete, feature-rich darts scoring application with full game logic, persistent statistics, realistic AI opponents, and professional checkout tables. Built with Python and Streamlit.

![Tests](https://github.com/Stijnman/Dart-app/workflows/Python%20application/badge.svg)

---

## What's New in v2.0

**15 fully implemented game modes** — Every game mode now has complete scoring logic, not stubs.

**Realistic DartBot AI** — 12 difficulty levels with probabilistic checkouts and human-like variance. No more bots that never miss.

**Complete checkout system** — All 161 PDC tournament checkout paths from 170 down to 2.

**Persistent statistics** — SQLite-backed player profiles, personal bests, and head-to-head records.

**Full Cricket implementation** — Standard, Cut-Throat, and No-Score variants with proper marks, points, and winner detection.

**Practice & Party games** — Bob's 27 (3 difficulty levels), Around the Clock (Singles/Doubles/Triples), Shanghai, Killer, Half It.

**102 automated tests** — Comprehensive coverage of all game modes, AI behavior, and checkout tables.

---

## Game Modes

### X01 Games
| Mode | Starting Score | Description |
|------|---------------|-------------|
| 101 | 101 | Quick finish |
| 170 | 170 | 170 challenge |
| 201 | 201 | Short format |
| 301 | 301 | Standard short |
| 501 | 501 | The classic |
| 701 | 701 | Tournament format |
| 901 | 901 | Extended format |
| 1001 | 1001 | Marathon format |

All modes support: Double Out, Master Out, Straight Out, Double In, Handicap system, and Best-of/Frist-to leg formats.

### Cricket Variants
- **Standard Cricket** — 15-20 + Bull, points on excess marks
- **Cut-Throat Cricket** — Points go to opponents
- **No-Score Cricket** — Marks only, first to close all wins

### Practice Games
- **Bob's 27** — Doubles practice with 3 difficulty modes (Easy/Standard/Hard)
- **Around the Clock** — Hit 1-20 + Bull, with Singles/Doubles/Triples variants
- **Shanghai** — 7-round or 20-round, S+D+T = instant win

### Party Games
- **Killer** — Claim numbers, eliminate opponents, configurable lives (1-9)
- **Half It** — Hit the target or lose half your score

---

## DartBot AI (12 Levels)

| Level | Name | Avg Throw | Checkout % | Description |
|-------|------|-----------|------------|-------------|
| 1 | Beginner | 18 | 5% | Just started |
| 2 | Casual | 26 | 12% | Plays occasionally |
| 3 | Pub Player | 32 | 20% | Regular pub player |
| 4 | League Player | 38 | 30% | Local league standard |
| 5 | Good League | 42 | 38% | Top of local league |
| 6 | County Player | 45 | 45% | County/regional level |
| 7 | Advanced | 48 | 52% | Highly skilled amateur |
| 8 | Semi-Pro | 52 | 60% | Near professional |
| 9 | Tour Card | 56 | 68% | PDC Tour Card holder |
| 10 | World Class | 60 | 78% | Elite professional |
| 11 | GOAT | 65 | 88% | Best in the world |
| 12 | Lukeman | 70 | 95% | Machine-like precision |

**Key feature:** The bot uses probabilistic checkouts — it will miss realistic shots, hit adjacent numbers on near-misses, and perform slightly worse under checkout pressure. No more AI that always checks out from 40.

---

## Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the App
```bash
streamlit run main.py
```

### Run Tests
```bash
pytest tests/ -v
```

---

## Project Structure

```
.
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── README.md               # This file
├── core/                   # Game engine and logic
│   ├── __init__.py
│   ├── constants.py        # Checkout tables, game configs
│   ├── player.py           # Player model
│   ├── game_state.py       # State management
│   ├── checkout.py         # Checkout system
│   ├── dartbot.py          # AI opponent
│   ├── engine.py           # Universal game engine
│   └── database.py         # SQLite persistence
├── ui/
│   ├── __init__.py
│   └── streamlit_app.py    # Streamlit frontend
├── tests/                  # 102 automated tests
│   ├── __init__.py
│   ├── test_x01.py
│   ├── test_cricket.py
│   ├── test_practice.py
│   ├── test_party.py
│   ├── test_dartbot.py
│   ├── test_checkout.py
│   └── test_integration.py
├── .github/
│   └── workflows/
│       └── python-app.yml  # CI/CD
└── OLDER VERSIONS/         # Previous versions
    ├── Webappv3.py
    ├── Webappv3.1.py
    ├── main.py
    ├── mainstreamlined.py
    └── webapp2.py
```

---

## UX Features (Addressing Common Complaints)

| Feature | Description |
|---------|-------------|
| Quick Score Buttons | One-tap entry for 60, 100, 140, 180 |
| Per-Dart Quick Keys | T20, T19, D20, T17, Bull, Miss buttons |
| Dual Input Modes | Per-dart entry OR total-only entry |
| Undo/Redo | Full history stack with snapshots |
| Dark Mode | Toggleable dark/light theme |
| Checkout Display | Full dart-by-dart path shown when on a finish |
| Voice Announcements | Offline TTS (no internet required) |
| Cricket Scoreboard | Visual mark tracking with symbols |
| Persistent Stats | Cross-session player profiles and records |

---

## Technology Stack

- **Python 3.10+**
- **Streamlit** — Web UI framework
- **SQLite** — Local data persistence
- **pytest** — Testing framework
- **matplotlib** — Charts and graphs
- **pyttsx3** — Offline text-to-speech

---

## Changelog

### v2.0 (2025-06-02)
- Complete rewrite of game engine with universal mode support
- 15 fully implemented game modes (previously stubs)
- 12-level realistic DartBot AI with probabilistic behavior
- Full PDC checkout tables (161 checkouts)
- Persistent SQLite database with player profiles
- 102 automated tests
- Dark mode UI with quick-score buttons
- Cricket variants (Standard, Cut-Throat, No-Score)
- Practice games: Bob's 27, Around the Clock, Shanghai
- Party games: Killer, Half It

### v1.x (Archived in OLDER VERSIONS/)
- Initial Streamlit prototype
- Basic 501 and 301 support
- Stub implementations for additional modes
- Simple bot AI

---

## License

MIT License
