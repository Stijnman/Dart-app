# 🔍 Import Audit: Missing Imports Analysis

**Date**: 2026-06-05  
**Status**: ❌ CRITICAL - 5 Missing Module Dependencies  
**Test Status**: FAILING (ImportError in test collection)

---

## Executive Summary

The pytest import error is caused by **multiple missing module files** that are imported but don't exist in the codebase. These aren't `__init__.py` issues — they're completely **missing Python modules**.

### Modules Referenced But Not Found:
1. ❌ `core/player_analytics.py` - Referenced by `core/ghost_bot.py`
2. ❌ `core/party_games.py` - Referenced by `core/engine.py`
3. ❌ `core/practice_drills.py` - Referenced by `core/engine.py`
4. ❌ `core/tournament.py` - Referenced by `core/engine.py`
5. ❌ `core/tactics_joker.py` - Referenced by `core/engine.py` (partial stubs exist but incomplete)

---

## Detailed Analysis

### 1. **core/player_analytics.py** ❌ MISSING
**Status**: File doesn't exist  
**Imported By**: `core/ghost_bot.py` (line 8)
```python
from core.player_analytics import AdvancedPlayerStats
```
**Impact**: GhostBot class cannot be imported, blocks test collection

**Usage**:
- `GhostBot.__init__()` requires `AdvancedPlayerStats` object
- Methods: `get_favorite_segments()`, `get_weak_segments()`, `get_opening_throw_pattern()`, `get_closing_throw_pattern()`, `get_heatmap_data()`

**Solution**: Create stub or remove GhostBot from imports

---

### 2. **core/party_games.py** ❌ MISSING
**Status**: File doesn't exist  
**Imported By**: `core/engine.py` (line 27)
```python
from .party_games import KillerGame, DartsGolf, TicTacToeDarts, ShanghaiChampionship
```
**Impact**: DartGameEngine initialization fails when importing

**Required Classes**:
- `KillerGame`
- `DartsGolf`
- `TicTacToeDarts`
- `ShanghaiChampionship`

---

### 3. **core/practice_drills.py** ❌ MISSING
**Status**: File doesn't exist  
**Imported By**: `core/engine.py` (line 28)
```python
from .practice_drills import Bob27, Game121, HalveIt
```
**Impact**: DartGameEngine initialization fails when importing

**Required Classes**:
- `Bob27`
- `Game121`
- `HalveIt`

---

### 4. **core/tournament.py** ❌ MISSING
**Status**: File doesn't exist  
**Imported By**: `core/engine.py` (line 29)
```python
from .tournament import TournamentManager
```
**Impact**: DartGameEngine initialization fails when importing

**Required Classes**:
- `TournamentManager`

---

### 5. **core/tactics_joker.py** ⚠️ PARTIAL/INCOMPLETE
**Status**: File exists but incomplete  
**Imported By**: `core/engine.py` (line 26)
```python
from .tactics_joker import TacticsJokerGame, TacticsJokerBuilder, PRESET_CLASSIC
```
**Issues**:
- `TacticsJokerGame` class is referenced but incomplete
- `PRESET_CLASSIC` constant may be missing
- File may have syntax errors

---

## Import Chain Analysis

### Failing Import Chain:
```
test_chase_dragon.py
  └─> from core.engine import DartGameEngine
      └─> core/__init__.py (line 28)
          └─> from .systems import (VoiceRecognition, ...)
              └─> [VoiceRecognition exists ✓]
          
          BUT ALSO:
          core/engine.py (lines 26-29)
              └─> from .tactics_joker import TacticsJokerGame, TacticsJokerBuilder, PRESET_CLASSIC
              └─> from .party_games import KillerGame, DartsGolf, TicTacToeDarts, ShanghaiChampionship
              └─> from .practice_drills import Bob27, Game121, HalveIt
              └─> from .tournament import TournamentManager
              
              ALL FAIL → ImportError cascades up to __init__.py
```

---

## Files That Exist ✓

These classes ARE defined and properly exported:

### ✓ `core/gamemodes.py` - Contains:
- `CountUpGame`
- `BermudaGame`
- `JDCChallenge`
- `Practice4160`
- `TacticCricket`
- `RandomCricket`
- `HammerCricket`
- `EliminatorGame`
- `RoadrunnerGame`
- `Escalator20Game`
- `CricketCountUp`
- `ChaseTheDragonGame` ✓

### ✓ `core/systems.py` - Contains:
- `VoiceRecognition` ✓
- `SmartBot` ✓
- `ProSimulation` ✓
- All other systems ✓

### ✓ `core/extensions.py` - Contains:
- `TeamRoundTheClock` ✓
- `BaseballDarts` ✓
- `GotchaGame` ✓
- `TournamentEngine` (but different from `TournamentManager`)
- `BounceOutTracker` ✓

---

## Recommendations

### Option A: **Create Missing Modules** (Recommended)
Create stub implementations for:
1. `core/party_games.py` - Killer, Darts Golf, Tic-Tac-Toe, Shanghai
2. `core/practice_drills.py` - Bob27, Game121, HalveIt practice modes
3. `core/tournament.py` - TournamentManager class
4. `core/player_analytics.py` - AdvancedPlayerStats class

### Option B: **Remove Broken Imports** (Quick Fix)
Update `core/engine.py` to comment out or conditionally import these modules:
```python
# Temporarily disabled - modules not yet implemented
# from .party_games import KillerGame, DartsGolf, TicTacToeDarts, ShanghaiChampionship
# from .practice_drills import Bob27, Game121, HalveIt
# from .tournament import TournamentManager
```

### Option C: **Hybrid Approach** (Best)
- Create minimal stub classes for immediate test passing
- Implement full functionality in future PRs
- Mark stubs with `# TODO` comments

---

## Test Failure Root Cause

```
ERROR collecting tests/test_chase_dragon.py
ImportError: cannot import name 'VoiceRecognition' from 'core.systems'

✓ VoiceRecognition EXISTS in core/systems.py
✓ But core/engine.py imports fail BEFORE __init__.py completes
✓ This causes the entire core module import to fail
✓ Making VoiceRecognition inaccessible in __init__.py
```

---

## Next Steps

1. ✅ **Immediate**: Create the 4 missing module files with stubs
2. ✅ **Verify**: Run `pytest tests/test_chase_dragon.py -v`
3. ✅ **Monitor**: Check for additional missing imports in other test files
4. ✅ **Document**: Add this audit to CONTRIBUTING.md

---

## Files to Create

```
core/
├── party_games.py          (NEW)
├── practice_drills.py       (NEW)
├── tournament.py            (NEW)
└── player_analytics.py      (NEW)
```

---

**Generated by**: GitHub Copilot Assistant  
**Severity**: 🔴 CRITICAL - Tests cannot run
