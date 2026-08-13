import pytest
import json
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from main import app, AUTH_TOKEN, brain_engine
from core.providers.mock import MockProvider

def test_root_endpoint():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Sahistra Hub is running"
    assert data["module"] == "Brain Active"

def test_websocket_unauthorized_token():
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/voice?token=wrong_token"):
            pass
    assert exc_info.value.code == 1008

def test_websocket_authorized_flow():
    # Use MockProvider on brain_engine for deterministic testing
    orig_provider = brain_engine.provider
    brain_engine.provider = MockProvider(canned_chunks=["Hello ", "there!"], chunk_delay=0.001)
    
    try:
        client = TestClient(app)
        with client.websocket_connect(f"/ws/voice?token={AUTH_TOKEN}") as ws:
            # Send valid transcript
            ws.send_text(json.dumps({"type": "transcript", "text": "Hi"}))
            
            # 1. response_start
            msg1 = json.loads(ws.receive_text())
            assert msg1["type"] == "response_start"
            turn_id = msg1["turn_id"]
            
            # 2. response_chunk 1
            msg2 = json.loads(ws.receive_text())
            assert msg2["type"] == "response_chunk"
            assert msg2["turn_id"] == turn_id
            assert msg2["delta"] == "Hello "
            
            # 3. response_chunk 2
            msg3 = json.loads(ws.receive_text())
            assert msg3["type"] == "response_chunk"
            assert msg3["delta"] == "there!"
            
            # 4. response_end
            msg4 = json.loads(ws.receive_text())
            assert msg4["type"] == "response_end"
            assert msg4["full_text"] == "Hello there!"
            assert msg4["turn_id"] == turn_id
    finally:
        brain_engine.provider = orig_provider

def test_websocket_malformed_json():
    client = TestClient(app)
    with client.websocket_connect(f"/ws/voice?token={AUTH_TOKEN}") as ws:
        ws.send_text("THIS IS NOT JSON")
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "error"
        assert msg["code"] == "INVALID_JSON"

def test_websocket_invalid_payload_type():
    client = TestClient(app)
    with client.websocket_connect(f"/ws/voice?token={AUTH_TOKEN}") as ws:
        ws.send_text(json.dumps(["not", "a", "dict"]))
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "error"
        assert msg["code"] == "INVALID_PAYLOAD"
