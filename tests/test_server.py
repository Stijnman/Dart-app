"""
tests/test_server.py
v3.1 server tests: REST create, WS basic (via testclient), ELO, custom support, history.
Run: pytest tests/test_server.py -q --tb=line
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

# Import after path
from core.server.main import app, manager, HAS_ELO
from core.server.models import DEMO_USERS

def _get_client():
    return TestClient(app)

def test_health_and_version():
    client = _get_client()
    r = client.get("/docs")
    assert r.status_code in (200, 404)  # docs may be openapi
    # openapi
    r = client.get("/openapi.json")
    assert r.status_code == 200
    data = r.json()
    assert "Dart Game Pro" in data.get("info", {}).get("title", "")

def test_demo_create_match():
    client = _get_client()
    payload = {"mode": "501", "players": ["Alice", "Bob"]}
    r = client.post("/demo/matches", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "match_id" in data
    assert data["mode"] == "501"
    mid = data["match_id"]
    # get it
    r2 = client.get(f"/matches/{mid}")
    assert r2.status_code == 200
    assert r2.json()["players"] == ["Alice", "Bob"]

def test_custom_mode_create():
    client = _get_client()
    payload = {
        "mode": "501",
        "players": ["P1", "P2"],
        "custom": {"win_condition": "Survival (last life wins)", "lives": 3, "special_rules": ["Only Doubles"]}
    }
    r = client.post("/demo/matches", json=payload)
    assert r.status_code == 200
    assert r.json()["mode"] == "killer_party"  # mapped

def test_elo_standings():
    client = _get_client()
    r = client.get("/elo/standings")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_history_endpoint():
    client = _get_client()
    r = client.get("/history/demo")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_token_and_protected():
    client = _get_client()
    # login
    r = client.post("/token", json={"username": "demo", "password": "demo123"})
    assert r.status_code == 200
    tok = r.json()["access_token"]
    # protected create
    headers = {"Authorization": f"Bearer {tok}"}
    r2 = client.post("/matches", json={"mode": "301", "players": ["A", "B"]}, headers=headers)
    assert r2.status_code == 200

def test_list_matches():
    client = _get_client()
    r = client.get("/matches")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

if __name__ == "__main__":
    pytest.main([__file__, "-q"]) 


def test_overlay_escapes_match_identifier():
    from urllib.parse import quote

    malicious_id = "<img src=x onerror=alert(1)>"
    response = _get_client().get("/overlays/obs/" + quote(malicious_id, safe=""))
    assert response.status_code == 200
    assert malicious_id not in response.text
    assert "&lt;img src=x onerror=alert(1)&gt;" in response.text
    assert 'fetch("/stream/%3Cimg%20src%3Dx%20onerror%3Dalert%281%29%3E")' in response.text
    assert ".textContent =" in response.text
    assert ".innerHTML" not in response.text


def test_overlay_keeps_quotes_out_of_script_url():
    from urllib.parse import quote

    malicious_id = "');alert(1);//"
    # Slashes are route delimiters; test the endpoint directly for this case.
    import asyncio
    from core.server.main import obs_overlay

    response = asyncio.run(obs_overlay(malicious_id))
    html = response.body.decode()
    assert 'fetch("/stream/' + quote(malicious_id, safe="") + '")' in html
    assert "fetch('/stream/" not in html


def test_websocket_accepts_valid_token_and_rejects_invalid_token():
    from starlette.websockets import WebSocketDisconnect
    from core.server.models import create_access_token

    client = _get_client()
    mid = client.post("/demo/matches", json={"mode": "501", "players": ["demo", "other"]}).json()["match_id"]
    token = create_access_token({"sub": "demo"})
    with client.websocket_connect(f"/ws/{mid}/demo?token={token}") as ws:
        assert ws.receive_json()["type"] == "initial_state"
        ws.send_json({"type": "ping"})
        assert ws.receive_json()["type"] == "pong"
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect(f"/ws/{mid}/demo?token=invalid"):
            pass
    assert exc.value.code == 1008
