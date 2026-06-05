import sys, os, random
sys.path.insert(0, ".")
from core.engine import DartGameEngine
from core.player import Player
from custom_game_mode import generate_custom_game_mode, play_custom_mode
from core.utils import validate_dart_throw, parse_dart_value

def valid_dart():
    # realistic: 0-20, or doubles 2-40 even, triples 3-60, 25/50 bull
    r = random.random()
    if r < 0.1: return 0
    if r < 0.2: return 25
    if r < 0.25: return 50
    base = random.randint(1,20)
    mult = random.choice([1,1,1,2,3])
    if mult==1: return base
    if mult==2: return base*2
    return base*3

def simulate_game(mode="501", players=None, num_turns=20, custom=None, out_rule="double", variant=None):
    if players is None: players = [Player("P1"), Player("P2")]
    kwargs = {"out_rule": out_rule}
    if variant: kwargs["variant"] = variant
    engine = DartGameEngine(mode=mode, players=players, **kwargs)
    logs = []
    for t in range(num_turns):
        darts = [valid_dart() for _ in range(3)]
        valid, err = validate_dart_throw(darts)
        if not valid:
            darts = [0,0,0]  # safe
        try:
            msg = engine.record_throw(darts)
            logs.append(f"T{t}: {darts} -> {msg[:80]} | scores {[getattr(p,'score',0) for p in players]} winner={engine.state.winner}")
            if engine.state.winner:
                if custom:
                    try: play_custom_mode(custom.name, max(getattr(pp,'score',0) for pp in players))
                    except: pass
                break
        except Exception as e:
            logs.append(f"ERR T{t} {darts}: {e}")
            break
    return logs, engine

def run_all_edges():
    print("=== COMPREHENSIVE EDGE SIMS ===")
    # 1. X01 critical bust=1, double out
    print("\n1. X01 bust=1 + double finish")
    p1=Player("A"); p1.score=1; p2=Player("B")
    e = DartGameEngine("501", [p1,p2], out_rule="double")
    print("record 1 on 1:", e.record_throw([1,0,0]))
    p1.score = 2; print("record 2 on 2 (straight? but double):", e.record_throw([2,0,0]))
    p1.score = 32; print("finish D16:", e.record_throw([32,0,0]))  # 32= D16? wait 16*2=32 yes

    # 2. Custom with special rules
    print("\n2. Custom Survival + Only Doubles")
    cm = generate_custom_game_mode({"style":"Survival","starting_score":301,"difficulty":"Hard","special_rules":["Only Doubles","Bust = Lose Life"]})
    cm.name = "EdgeCustom"
    logs, _ = simulate_game("killer_party", num_turns=15, custom=cm, variant="hard")
    print("Custom logs last 3:", logs[-3:])
    print("Custom lives etc:", cm.lives, cm.special_rules)

    # 3. Cricket variants close
    print("\n3. Cutthroat Cricket close")
    logs, e = simulate_game("cut_throat", num_turns=10)
    print("Cricket close sample:", logs[-2:])

    # 4. Undo/redo edge after bust/win
    print("\n4. Undo after bust")
    p=[Player("U1"),Player("U2")]
    e= DartGameEngine("301",p)
    e.record_throw([60,60,60]); e.record_throw([10,10,10])  # bust likely
    print("Undo1:", e.undo_last_throw())
    print("Undo2:", e.undo_last_throw())

    # 5. Sub modes tictactoe golf tactics with valid
    for m, v in [("tictactoe",None), ("golf","9"), ("tactics_joker","balanced")]:
        print(f"\n5. {m} sub")
        logs, e = simulate_game(m, num_turns=8, variant=v)
        print(f"{m} winner={e.state.winner} last log:", logs[-1] if logs else "none")

    # 6. Voice on real engine with state
    print("\n6. Voice full")
    from core.enhanced_voice_recognition import EnhancedVoiceRecognition
    e = DartGameEngine("501", [Player("V1"), Player("V2")])
    e.record_throw([20,20,20])
    vr=EnhancedVoiceRecognition(engine_ref=e)
    for c in ["undo last", "next player", "show stats", "what checkout", "t20"]:
        cmd,s,_ = vr.recognize(c)
        res = vr.execute_command(cmd) if cmd and cmd != "score" else {"success": cmd=="score"}
        print(f"  {c} -> {cmd} success={res.get('success')}")

    # 7. Handicap + multi leg
    print("\n7. Handicap multi")
    p1,p2=Player("H1"),Player("H2")
    e=DartGameEngine("501",[p1,p2], handicaps={"H1":100})
    for _ in range(3): e.record_throw([20,20,20])
    print("After 3x60 with H1 -100 start:", p1.score, p2.score)

    print("\n=== ALL EDGES RAN ===")
    return "OK"

if __name__=="__main__":
    run_all_edges()
