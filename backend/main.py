import json
import uuid
import asyncio
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from core.brain import BrainEngine
from core.config import get_config

app = FastAPI(title="Sahistra AI Hub (Module 2: AI Brain)")

# Global Configuration
config = get_config()
AUTH_TOKEN = config.auth_token

# Initialize Brain Engine (lazy initialization, never fails on startup)
brain_engine = BrainEngine(config=config)

@app.get("/")
def read_root():
    return {
        "status": "Sahistra Hub is running",
        "module": "Brain Active",
        "provider": config.llm_provider,
        "model": config.llm_model_name
    }

@app.websocket("/ws/voice")
async def websocket_text_endpoint(websocket: WebSocket, token: str = Query(None)):
    if token != AUTH_TOKEN:
        await websocket.close(code=1008, reason="Unauthorized")
        return
        
    await websocket.accept()
    session_id = f"session-{uuid.uuid4().hex[:8]}"
    
    active_stream_task: Optional[asyncio.Task] = None
    cancel_event: Optional[asyncio.Event] = None
    
    try:
        while True:
            data_str = await websocket.receive_text()
            
            try:
                data = json.loads(data_str)
            except (json.JSONDecodeError, TypeError):
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "turn_id": "none",
                    "code": "INVALID_JSON",
                    "message": "Malformed JSON payload received."
                }))
                continue
            
            if not isinstance(data, dict):
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "turn_id": "none",
                    "code": "INVALID_PAYLOAD",
                    "message": "Payload must be a JSON object."
                }))
                continue

            msg_type = data.get("type")
            
            if msg_type == "transcript":
                transcript = data.get("text", "").strip()
                if not transcript:
                    continue
                
                client_session_id = data.get("session_id") or session_id
                
                # If there's an ongoing generation, cancel it (barge-in)
                if active_stream_task and not active_stream_task.done():
                    if cancel_event:
                        cancel_event.set()
                    active_stream_task.cancel()
                
                cancel_event = asyncio.Event()
                
                async def stream_worker(sess_id: str, text: str, cevent: asyncio.Event):
                    try:
                        async for event in brain_engine.process_stream(
                            session_id=sess_id,
                            user_input=text,
                            cancel_event=cevent
                        ):
                            await websocket.send_text(json.dumps(event.to_dict()))
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        try:
                            await websocket.send_text(json.dumps({
                                "type": "error",
                                "turn_id": "none",
                                "code": "STREAM_ERROR",
                                "message": str(e)
                            }))
                        except Exception:
                            pass

                active_stream_task = asyncio.create_task(
                    stream_worker(client_session_id, transcript, cancel_event)
                )

            elif msg_type == "cancel":
                if active_stream_task and not active_stream_task.done():
                    if cancel_event:
                        cancel_event.set()
                    active_stream_task.cancel()

            elif msg_type == "partial_transcript":
                # Reserved for speculative streaming execution
                pass

    except WebSocketDisconnect:
        if active_stream_task and not active_stream_task.done():
            if cancel_event:
                cancel_event.set()
            active_stream_task.cancel()
        brain_engine.context_manager.remove_session(session_id)
