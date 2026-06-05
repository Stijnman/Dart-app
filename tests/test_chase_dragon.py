
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.engine import DartGameEngine
from core.player import Player

def test_chase_dragon_initialization():
    players = [Player(name="Alice"), Player(name="Bob")]
    engine = DartGameEngine(mode="chase_the_dragon", players=players)
    
    assert engine.state.mode == "chase_the_dragon"
    assert engine.state.sub_engine is not None
    
    sb = engine.get_mode_scoreboard()
    assert sb["players"][0]["display"] == "Target: T10"
    assert sb["extra"]["target"] == "T10"

def test_chase_dragon_scoring():
    players = [Player(name="Alice"), Player(name="Bob")]
    engine = DartGameEngine(mode="chase_the_dragon", players=players)
    
    # Alice hits T10 (30)
    msg = engine.record_throw([30, 0, 0])
    assert "HIT T10" in msg
    
    # Check next target
    sb = engine.get_mode_scoreboard()
    # Note: current player index advances, so we check Alice's specific display
    assert sb["players"][0]["display"] == "Target: T11"

def test_chase_dragon_win():
    players = [Player(name="Alice")]
    engine = DartGameEngine(mode="chase_the_dragon", players=players)
    
    # Simulate hitting all targets
    targets = [
        30, 33, 36, 39, 42,
        45, 48, 51, 54, 57,
        60, 25, 50
    ]
    
    for t in targets[:-1]:
        engine.record_throw([t, 0, 0])
        
    # Last target
    msg = engine.record_throw([50, 0, 0])
    assert "DRAGON SLAYED" in msg
    assert engine.state.winner == "Alice"

if __name__ == "__main__":
    test_chase_dragon_initialization()
    test_chase_dragon_scoring()
    test_chase_dragon_win()
    print("Chase the Dragon tests passed!")
