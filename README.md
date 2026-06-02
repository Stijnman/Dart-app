# Dart Game Pro v2.2

A complete, feature-rich darts scoring application with **256 features** across 16 categories: 30 game modes, 12-level AI with SmartBot adaptive mode, 8 professional player simulations, full career mode with Order of Merit, ELO rating system, 35 achievements, voice recognition, virtual dartboard, AI pattern detection, graded league system, and more. Built with Python and Streamlit.

![Tests](https://github.com/Stijnman/Dart-app/workflows/Python%20application/badge.svg)

---

## What's New in v2.2 — 118 Additional Features (Complete Competitive Gap Closure)

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Count Up** | Score maximum points in fixed rounds |
| 2 | **Bermuda** | Different target each round, miss = 0 |
| 3 | **JDC Challenge** | Junior Darts Corp: doubles + singles sequence |
| 4 | **41-60 Practice** | Hit 41 through 60 in sequence |
| 5 | **Tactic Cricket** | Cricket with 2x power-play rounds |
| 6 | **Random Cricket** | Randomized cricket targets each game |
| 7 | **Hammer Cricket** | Last to close gets penalized |
| 8 | **Eliminator** | Last to finish = out, survival mode |
| 9 | **Roadrunner** | Stay ahead of pro for 30 rounds |
| 10 | **Escalator 20** | 20 levels with changing handicaps |
| 11 | **Cricket Count Up** | Score on cricket numbers only |
| 12 | **Voice Recognition** | Parse spoken scores ("T20 T20 D20") |
| 13 | **SmartBot Adaptive AI** | Analyzes your play, adjusts difficulty |
| 14 | **Pro Simulation** | Play vs 8 real pros (MVG, Littler, etc.) |
| 15 | **Career Mode** | 15-event season, money list, world rankings |
| 16 | **ELO Rating System** | Flight grades C through SA |
| 17 | **Skill Level System** | 7 tiers: Beginner to Elite |
| 18 | **Pattern Detection** | AI identifies fatigue, inconsistency |
| 19 | **Weakness Analysis** | Per-double success rate breakdown |
| 20 | **Commentary Engine** | 4,000+ names, TV-style commentary |
| 21 | **AI Match Reporter** | Detailed post-match AI analysis |
| 22 | **Online Lobby System** | Join codes, chat, spectators |
| 23 | **Graded League** | Bronze to Diamond, promotion/relegation |
| 24 | **Login Bonus System** | Daily rewards with streak multiplier |
| 25 | **Anniversary Tracking** | Years since milestones |
| 26 | **Theme Shop** | 8 unlockable color themes |
| 27 | **Virtual Dartboard** | Tap-to-score interactive board |
| 28 | **Save/Resume Games** | Pause and resume matches |
| 29 | **Mugs Away Rule** | Loser starts next leg |
| 30 | **Coin Flip** | Random first throw |
| 31 | **PPR/MPR Stats** | Points/Marks Per Round |
| 32 | **Equipment Tracking** | Register which darts you use |
| 33 | **Social Sharing** | WhatsApp, Twitter, camera roll |

---

## What's New in v2.1 — 30 Additional Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Knockout Tournament Bracket** | Single-elimination tournament with auto-generated bracket |
| 2 | **Round-Robin League** | Everyone plays everyone, full standings table |
| 3 | **League Format** | Group stage + top 4 knockout playoff |
| 4 | **Seeded Tournament Draws** | Rank participants, auto-seed the bracket |
| 5 | **Share to WhatsApp/Social** | One-tap copy formatted results for sharing |
| 6 | **Public Player Stats Cards** | HTML shareable card with average, wins, 180s |
| 7 | **Friend Activity Feed** | See what friends are playing (placeholder for v2.2) |
| 8 | **Checkout Success by Range** | "I finish 85% from 40-60 but 30% from 100-120" |
| 9 | **Board Segment Heatmap** | Visual 20-segment grid showing scoring distribution |
| 10 | **30-Day Performance Trend** | Line chart of average over time |
| 11 | **Consistency Rating** | 0-100 score measuring throw variance |
| 12 | **AI Coach Recommendations** | "You miss D16 70% of the time — practice it" |
| 13 | **Recommended Practice** | Auto-suggests games based on your weak areas |
| 14 | **Training Plan Generator** | 7-day structured plans (Finishing/Scoring/Consistency) |
| 15 | **Round the World — Team Relay** | Team variant, players alternate hitting next number |
| 16 | **Baseball Darts** | 9-innings game with runs per segment |
| 17 | **Gotcha (Chase the Leader)** | Match or beat the leader each round |
| 18 | **Spectator Mode** | Watch ongoing matches without playing |
| 19 | **TV Scoreboard Mode** | Clean full-screen scoreboard for external displays |
| 20 | **5 Custom Color Themes** | Dark Pro, Midnight Blue, Darts Hall, Emerald, Light |
| 21 | **CSV/Excel Export** | Download all stats as CSV for spreadsheet analysis |
| 22 | **Match Replay (Step-Through)** | Revisit any past game throw by throw |
| 23 | **PDF Match Report** | Generate printable match summary |
| 24 | **Achievement/Badge System** | 35 unlockable achievements across 5 categories |
| 25 | **Daily & Weekly Challenges** | "Hit 5 180s this week" — 6 rotating challenges |
| 26 | **Win Streak Tracking** | Current and best streak with streak achievements |
| 27 | **Custom Starting Score** | Play from any number (421, 375, etc.) |
| 28 | **Player Avatar Upload** | Upload JPG/PNG for player profile |
| 29 | **180 Special Effect** | Balloons + visual celebration on 180 |
| 30 | **Bounce-Out Detection** | Mark bounce-outs (0 score, doesn't count as miss) |

---

## Game Modes (30 Total)

### X01 Games (10 modes)
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
| 1501 | 1501 | Epic marathon |
| **Custom** | **Any 2-1501** | **Set your own starting score** |

All modes support: Double Out, Master Out, Straight Out, Double In, Handicap system, and Best-of/First-to leg formats.

### Cricket Variants (3 modes)
- **Standard Cricket** — 15-20 + Bull, points on excess marks
- **Cut-Throat Cricket** — Points go to opponents
- **No-Score Cricket** — Marks only, first to close all wins

### Practice Games (3 modes + 6 variants)
- **Bob's 27** — Doubles practice (Easy/Standard/Hard)
- **Around the Clock** — Singles, Doubles Only, Triples Only
- **Shanghai** — Quick (7 rounds) or Full (20 rounds), S+D+T = instant win

### Party Games (2 modes)
- **Killer** — Claim numbers, eliminate opponents (configurable 1-9 lives)
- **Half It** — Hit the target or lose half your score

### Specialty Games (3 modes — NEW in v2.1)
- **Baseball Darts** — 9 innings, runs based on singles/doubles/triples
- **Gotcha** — Match or beat the leader's score each round
- **Team Round the Clock** — Relay format, teammates alternate

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

**Key feature:** Probabilistic checkouts with human-like variance and pressure modeling.

---

## Achievements (35 Badges)

**5 Categories:** Scoring (6), Finishing (5), Games (9), Streaks (4), Special (5)

**Secret achievements** hidden until unlocked. **Daily & weekly challenges** with XP rewards. **Win streak tracking** from 3 to 20+.

---

## Quick Start

```bash
pip install -r requirements.txt
streamlit run main.py
```

Run tests:
```bash
pytest tests/ -v  # 102 automated tests
```

---

## Project Structure

```
.
├── main.py                      # Entry point
├── requirements.txt             # Dependencies
├── README.md                   # This file
├── core/                       # Game engine (14 modules)
│   ├── __init__.py             # Package init with 189 features
│   ├── constants.py            # Checkout tables, game configs
│   ├── player.py               # Player model
│   ├── game_state.py           # State management
│   ├── checkout.py             # Checkout system (161 PDC paths)
│   ├── dartbot.py              # 12-level AI opponent
│   ├── engine.py               # Universal game engine (30 modes)
│   ├── database.py             # SQLite persistence v1
│   ├── database_v2.py          # Enhanced DB (ELO, career, equipment)
│   ├── achievements.py         # 35 badges, challenges, streaks
│   ├── extensions.py           # Analytics, export, tournament
│   ├── gamemodes.py            # 11 additional game modes
│   └── systems.py              # Voice, AI, career, ELO, patterns, social
├── ui/
│   └── streamlit_app.py        # Full Streamlit frontend (9 tabs)
├── tests/                      # 102 automated tests
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
│       └── python-app.yml      # CI/CD
└── OLDER VERSIONS/             # Previous versions
    ├── Webappv3.py
    ├── Webappv3.1.py
    ├── main.py
    ├── mainstreamlined.py
    ├── webapp2.py
    └── devcontainer.json
```

---

## Total Feature Count: 189

| Category | Count |
|----------|-------|
| Game Modes (30 modes + variants + rules) | 85 |
| DartBot AI (12 levels + SmartBot adaptive) | 16 |
| Pro Simulation (8 real pros) | 8 |
| Career Mode (15 events + Order of Merit) | 6 |
| Checkout System (161 paths + features) | 10 |
| Scoring & Input (per dart / total / voice / virtual board) | 18 |
| Statistics (session + persistent + visual + ELO) | 28 |
| UI / UX (9 tabs + 8 themes + audio) | 28 |
| Database (13 tables) | 13 |
| Achievements & Challenges (35 badges) | 8 |
| Tournament System (3 formats + graded league) | 6 |
| Training & Analytics (AI coach + pattern detection) | 10 |
| Export & Sharing (CSV/PDF/WhatsApp/Twitter) | 6 |
| Voice & Commentary (recognition + 4,000 names) | 5 |
| Online (lobbies + chat + spectators) | 5 |
| System Infrastructure | 4 |

---

## Changelog

### v2.2 (2026-06-02)
- 118 new features — complete competitive gap closure (software-only)
- 11 new game modes (Count Up, Bermuda, JDC, 41-60, Tactic Cricket, Random Cricket, Hammer Cricket, Eliminator, Roadrunner, Escalator 20, Cricket Count Up)
- Voice Recognition system (parse spoken dart scores)
- SmartBot Adaptive AI (analyzes player performance, adjusts in real-time)
- Pro Simulation (8 real professionals: MVG, Littler, Humphries, Wright, etc.)
- Career Mode (15-event season, money list, world rankings, Order of Merit)
- ELO Rating System with flight grades (C → SA)
- Skill Level System (7 tiers: Beginner → Elite)
- Pattern Detection AI (fatigue, inconsistency, opening, scoring trends)
- Weakness Analysis (per-double success rates with recommendations)
- Commentary Engine (4,000+ name database, contextual TV-style commentary)
- AI Match Reporter (detailed post-match AI analysis)
- Online Match & Lobby System (join codes, chat, spectators)
- Graded League (Bronze → Diamond with promotion/relegation)
- DARTSLIVE-style features (login bonuses, anniversaries, points economy)
- Social Sharing (WhatsApp, Twitter, camera roll)
- Theme Shop (8 unlockable color themes with points economy)
- Virtual Dartboard (tap-to-score interactive board)
- Save/Resume Manager (save games mid-match)
- Mugs Away rule, Coin flip, PPR/MPR stats, Equipment tracking
- 9 UI tabs: Play, Career, Pro Sim, Tournament, Achievements, Analytics, Training, Online, Settings

### v2.1 (2026-06-02)
- 30 new features: Tournament system, Achievements, Training center, Analytics, Export, Specialty games, Custom themes, Spectator/TV modes, Bounce-out detection, 180 effects, Custom starting scores, Avatar upload, Share to social
- 5 color themes (Dark Pro, Midnight Blue, Darts Hall, Emerald, Light)
- 35 unlockable achievements with daily/weekly challenges
- AI Coach with personalized training plan generator
- Full tournament engine (Knockout, Round-Robin, League)
- 3 new specialty games (Baseball, Gotcha, Team ATC)
- 102 tests still passing

### v2.0 (2026-06-02)
- Complete rewrite with universal game engine
- 15 fully implemented game modes (previously stubs)
- 12-level realistic DartBot AI with probabilistic behavior
- Full PDC checkout tables (161 checkouts)
- Persistent SQLite database with player profiles
- 102 automated tests
- Dark mode UI with quick-score buttons

### v1.x (Archived in OLDER VERSIONS/)
- Initial Streamlit prototype

---

## License

MIT License
