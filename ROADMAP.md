# 🎯 Dart Game Pro - Roadmap (Updated v3.0)

**Current Version**: v3.0 (Sublime UI + Custom Game Modes + Analytics + Practice)  
**Repository**: https://github.com/Stijnman/Dart-app  
**Last Updated**: 2026-06-05

## Vision
The most complete, intelligent, and engaging darts platform — from casual play to serious competitive training and community.

## Current State (v3.0 – Just Shipped)

### ✅ Major Additions in v3.0 (Focus: Added Features, Sublime Experience)
- **Custom Game Mode System (Flagship)**: Full wizard, Surprise Me, preview cards, 15+ polish features (edit/dup/del, stats, export JSON, better names, more rules, tags, est. time, funny msgs, etc.). Real playable integration + stats.
- **Sublime Analytics Dashboard**: First-9, checkout % by remaining, advanced Plotly heatmaps (3D+), PPI, per-leg history, CSV/JSON exports.
- **Practice & Training Suite**: Checkout Trainer (real core/checkout), Target Practice drills, integrated with customs + classics.
- **UI/UX Overhaul (Sublime Layout)**: Modern CSS (cards, themes), handicaps + multi-profiles in setup, achievements live in UI, local leaderboards (per custom/mode), multiplayer lobby (create/join), voice polish, TV/onboarding hints, responsive/emoji-rich.
- More game types fully wired/exposed (Cricket variants, Party, subs real).
- Enhanced DB for customs/stats, exports everywhere, achievements integration.

### Other Strong Areas
- 30+ game modes with universal engine + real sub-engines (no more CountUp fallbacks for many).
- DartBot 12 levels + SmartBot + adaptive.
- Career, ELO, tournaments, 35 achievements (now UI-visible).
- Voice, coach, heatmaps, PPI, themes (eye comfort).
- Clean architecture, 100+ tests, Streamlit + Plotly/pandas.

## Medium / Future (v3.x+)
- Knockout Tournament enhancements, full live brackets.
- Deeper AI Coach + personalized recs/weakness analysis.
- Real-time online multiplayer (WebSockets beyond lobby stub).
- More custom rule enforcement (conditional logic, full builder in UI).
- Mobile responsiveness, AR hints, streaming overlays.
- Per-custom leaderboards + seasonal play.

See README for sublime v3.0 layout + added-things focus. Previous roadmap items largely completed or integrated into v3.0 customs/analytics.

## Future / Low Priority (Backlog)
- Multilingual AI Commentary (#10)
- Crowd Sounds + Custom Callouts (#11, #12)
- Dart Impact Calibration + Throw Velocity (#13, #18) — Recommend hardware integration (Autodarts) over pure acoustic ML for reliability
- Replay System with slow-mo (#26)
- Full Live Spectator multi-client (#25)
- AR Mode, Streaming overlays, Smart Dartboard API
- Psychological Bot (#22)

## What Was Delivered in This Update (2026-06-05)
All files saved to `/home/workdir/artifacts/`:
1. `dart_app_feature_status.md` — Complete 30-feature audit + status matrix
2. `enhanced_voice_recognition.py` — Production-ready Voice Commands module + Streamlit integration example
3. `advanced_heatmap.py` — Interactive 3D + cluster + drift heatmaps (Plotly recommended)
4. `smartbot_autoscale.py` — Auto difficulty scaling engine hook
5. `extended_themes.py` — Holographic theme + eye comfort controls
6. `killer_variants_example.py` — Starter for Soft/Hard/Sudden Death Killer
7. This updated ROADMAP

## How to Integrate (Quick Start)
1. Copy the .py enhancement files into your `core/` folder.
2. Import and wire:
   - Voice: Replace/enhance `VoiceRecognition` in `systems.py` or use the new class in UI.
   - Heatmaps: Import `generate_advanced_heatmap` in analytics tab of `streamlit_app.py`.
   - Scaling: Instantiate `AdaptiveDifficultyScaler` and call after legs/visits in engine loop.
   - Themes: Use `get_enhanced_theme(...)` in settings + apply to dartboard drawing.
3. (Optional) Add `plotly` to requirements.txt for best heatmap experience.
4. Run `streamlit run main.py` and test the new features in Play / Analytics / Settings tabs.
5. Update tests and open PR or commit.

## Tracking & Contribution
- GitHub Projects board + `roadmap` labeled issues
- Milestones: v2.4 (Voice + Polish + Adaptive) **shipped**, v2.5 (Competitive Edge)
- All new code follows existing clean architecture and includes docstrings + examples.

**Thank you for building the ultimate darts app!**  
The foundation is now even stronger for the features that matter most to serious and casual players alike.

Next up: Which medium priority feature should we tackle first (Ladder League, full Killer Variants, or Pressure Index)? Or shall we implement Darts Golf?

🎯 Let's keep shipping.
