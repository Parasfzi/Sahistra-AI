from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
import json
import os

app = FastAPI(title="Sahistra AI Hub (Production Text-Only)")

# Configuration
AUTH_TOKEN = os.environ.get("SAHISTRA_AUTH_TOKEN", "sahistra_secret_123")

@app.get("/")
def read_root():
    return {"status": "Sahistra Hub is running", "module": "Text Brain Active"}

@app.websocket("/ws/voice")
async def websocket_text_endpoint(websocket: WebSocket, token: str = Query(None)):
    if token != AUTH_TOKEN:
        await websocket.close(code=1008, reason="Unauthorized")
        print("Unauthorized connection attempt rejected.")
        return
        
    await websocket.accept()
    print("Client connected to Voice WebSocket (Text Mode)")
    
    try:
        while True:
            # Receive text chunk from client (Expecting JSON)
            data_str = await websocket.receive_text()
            
            try:
                data = json.loads(data_str)
            except json.JSONDecodeError:
                print(f"Invalid JSON received: {data_str}")
                continue
            
            if data.get("type") == "transcript":
                transcript = data.get("text", "")
                print(f"User said: {transcript}")
                
                # TODO: Route to LLM for reasoning
                # For now, mock the response
                response_text = f"Acknowledged. You said: {transcript}"
                
                # Send text response back to client for local TTS
                response_payload = {
                    "type": "response",
                    "text": response_text
                }
                await websocket.send_text(json.dumps(response_payload))
                print(f"Brain responded: {response_text}")

            elif data.get("type") == "partial_transcript":
                transcript = data.get("text", "")
                print(f"[Partial] User is saying: {transcript}")
                # Handle streaming speculative execution here later
                pass

    except WebSocketDisconnect:
        print("Client disconnected from Voice WebSocket")
