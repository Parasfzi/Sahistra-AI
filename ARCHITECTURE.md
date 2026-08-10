# Sahistra - Personal AI Assistant Architecture

This document outlines the complete architectural design for "Sahistra", a deeply integrated, privacy-focused, personal AI assistant.

## System Architecture
**Hub and Spoke Model**
- **Hub (The Brain)**: The old Android phone runs a local web server environment (using Termux). It acts as the central source of truth, storing databases, managing queues, and orchestrating API calls.
- **Spokes (The Senses & Actuators)**: 
  - Main Android Phone (Voice UI, GPS, Notifications)
  - Windows Laptop (Desktop automation, Screen indexing)

**Why?** Centralizing state on a 24/7 low-power device ensures the AI is always awake and maintains a continuous stream of consciousness, while offloading heavy UI or observation tasks to the devices being actively used.

## Folder Structure
A Monorepo approach for easier maintainability across a single-developer system.
```text
sahistra/
├── backend/            # Runs on Old Android (Termux)
│   ├── api/            # FastAPI routes (REST & WebSockets)
│   ├── core/           # Brain logic, agent router, tool registry
│   ├── memory/         # RAG, Vector DB management, summarization
│   └── database/       # SQLite schemas and migrations
├── desktop_agent/      # Runs on Windows Laptop
│   ├── observer/       # Screenshot & file indexing
│   └── executor/       # PyAutoGUI & script execution
├── mobile_agent/       # Runs on Main Android Phone
│   ├── voice_ui/       # Speech interface and Wake Word
│   └── background/     # Notification listener, location tracking
└── shared/             # API schemas (Pydantic), common configs
```
**Why?** A single repository ensures API contracts between the Hub and Spokes stay in sync. Modular folders keep concerns independent.

## Technology Stack
- **Backend (Old Android)**: Python 3.11+ via Termux, FastAPI.
- **Database**: SQLite (Relational), `sqlite-vec` or ChromaDB (Vector/Memory).
- **Desktop Agent**: Python, PySide6 (SysTray), PyAutoGUI, `mss` (screenshots), Tesseract (OCR).
- **Mobile Agent (Main)**: Kotlin Native Android App.
- **Networking**: Tailscale (Mesh VPN).
- **AI Models**: Gemini API (Reasoning), Piper (Local TTS), Whisper.cpp (Local STT).

**Why?** Python is the undisputed king of AI integrations. FastAPI is asynchronous and lightweight enough for 4GB RAM. SQLite requires no background daemon. Native Kotlin for the main phone allows deep OS hooks (like Accessibility Services).

## Communication between modules
- **Synchronous Actions**: REST API (HTTP/JSON). Used for querying memory, updating state.
- **Asynchronous/Streams**: WebSockets. Used for voice streaming and real-time screen events.
- **Authentication**: Static API Keys.

**Why?** WebSockets provide low latency for voice. Static API keys are perfectly secure for a single-user system running inside a private Tailscale network.

## Database design
**Relational (SQLite)**:
- `users`: preferences, API keys.
- `tasks`: id, description, status, due_date, context.
- `logs`: timestamp, level, module, message.

**Vector (sqlite-vec / ChromaDB)**:
- `episodic_memory`: Chunks of past conversations with embeddings.
- `semantic_memory`: Extracted facts.

**Why?** Splitting relational and vector data ensures fast exact-match queries for concrete data, while enabling fuzzy semantic search for abstract memories.

## AI Brain architecture
**The Cognitive Loop**:
1. **Input Parser**: Normalizes input.
2. **Context Injector**: Fetches relevant facts and current screen context.
3. **Router (LLM)**: Analyzes user intent and selects a Tool.
4. **Tool Execution**: Triggers Desktop Agent, searches Web, updates Memory.
5. **Response Generator (LLM)**: Crafts the final user-facing response.

**Why?** A modular cognitive loop allows swapping out the underlying LLM (e.g., swapping Gemini for Claude) without rewriting tool execution logic.

## Memory architecture
- **Working Memory**: The last 10 conversational turns (RAM/KV).
- **Short-term Memory**: Daily interactions (SQLite).
- **Long-term Memory**: Nightly job summarizes the day and stores in Vector DB.
- **Decay System**: Raw logs purged after 30 days.

**Why?** Snapdragon 450 will choke if asked to search raw logs dynamically. Summarizing and vectorizing at night shifts compute burden off-peak.

## Voice pipeline
- **Wake Word**: Local Porcupine on the Main Phone.
- **VAD**: Silero VAD to detect end of speech.
- **STT**: Audio streamed to Hub. Hub uses Whisper (tiny) locally or Cloud STT.
- **TTS**: Hub streams audio back using Piper TTS.

**Why?** Running wake-word locally saves battery on main phone. Streaming audio keeps heavy lifting centralized.

## Desktop Agent architecture
- **Screen Observer**: Takes screenshot every 10-30 seconds.
- **Local OCR**: Extracts text from screenshots.
- **Delta Sync**: Only sends text to Hub if screen changed significantly.
- **Actuator**: WebSocket endpoint for remote script execution.

**Why?** Pre-processing on the desktop saves Android network and CPU bandwidth.

## Android Agent architecture
- **Foreground Service**: Keeps agent alive to listen for wake word.
- **Notification Listener**: Forwards important messages to Hub.
- **Quick Settings Tile**: Fast access to voice.

**Why?** Deep integration requires native services to bypass aggressive battery management.

## Security model
- **Zero-Trust Network**: Connect via Tailscale. Hub binds ONLY to `100.x.x.x`.
- **Encryption**: Tailscale handles end-to-end encryption.
- **Permissions**: Explicit confirmation prompt for destructive actions.

**Why?** Exposing personal AI to public internet is a massive risk. Tailscale creates a private mesh network.

## Local storage strategy
- **Image Purge**: Desktop screenshots deleted after OCR.
- **Audio Purge**: Voice recordings deleted after STT.
- **Database Limits**: SQLite capped size, auto-archiving.

**Why?** 64GB is very limited; permanent memory must be strictly text-based.

## Future expansion strategy
- **Smart Home**: Connect to Home Assistant.
- **Local LLM**: Swap Cloud API for Ollama when hardware upgrades.
- **Vision Integration**: Pass images to Gemini Vision.

**Why?** Modular APIs allow hardware upgrades without client rewrites.

## Development roadmap
- **Phase 1 (Foundation)**: Termux on Old Android, FastAPI, Tailscale.
- **Phase 2 (The Senses)**: Desktop Agent (screenshots/OCR).
- **Phase 3 (The Brain)**: LLM API, Tool Router, SQLite Memory.
- **Phase 4 (The Voice)**: Main Android App with Wake Word.
- **Phase 5 (Autonomy)**: Nightly memory consolidation, automation.

**Why?** Building core brain and text tools first ensures fundamentally sound logic.
