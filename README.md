<div align="center">

# 🧠 Sahistra AI
### *Privacy-Focused, Always-On Personal AI Assistant Architecture*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![WebSocket](https://img.shields.io/badge/Protocol-WebSocket-FF6F00?style=for-the-badge&logo=websocket&logoColor=white)](#)
[![Google Cloud](https://img.shields.io/badge/GCP-STT%20%26%20TTS-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)](https://cloud.google.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](#)

</div>

---

## 📌 Overview

**Sahistra AI** is an intelligent, deeply integrated, private personal assistant built on a **Hub & Spoke** model. It enables continuous awareness, real-time voice interactions, desktop automation, and context-aware reasoning while keeping resource consumption optimized.

```text
               +----------------------------------+
               |        Sahistra AI Hub           |
               |      (Central Brain Server)      |
               |     FastAPI | WebSockets | DB    |
               +-----------------+----------------+
                                 |
                 +---------------+---------------+
                 |                               |
  +--------------v--------------+ +--------------v--------------+
  |    Windows Desktop Agent    | |      Main Mobile Agent      |
  | (Voice, OCR, Screen Index)  | |  (Voice UI, GPS, Sensors)  |
  +-----------------------------+ +-----------------------------+
```

---

## 🚀 Key Features

| Component | Capabilities |
| :--- | :--- |
| **🧠 Central Brain (Hub)** | FastAPI server with low-latency WebSocket streaming & REST endpoints. |
| **🎙️ Voice Pipeline** | Google Cloud Speech-to-Text (STT) + Text-to-Speech (TTS) with barge-in support. |
| **💻 Desktop Agent** | Audio streaming, local Voice Activity Detection (VAD), screen context observer. |
| **🔐 Zero-Trust Security** | Token-authenticated WebSocket connections & Tailscale mesh networking support. |

---

## 📂 Project Structure

```text
Sahistra AI/
├── 📁 backend/                # Hub: Central Brain (FastAPI Server)
│   ├── 📄 main.py             # ASGI entry point & WebSocket handler
│   └── 📄 requirements.txt    # Backend Python dependencies
│
├── 📁 desktop_agent/          # Spoke: Windows Desktop Client
│   ├── 📄 voice_test_client.py# Voice stream client with VAD & GCP integration
│   ├── 📄 .env.example        # Environment variables template
│   └── 📄 requirements.txt    # Client Python dependencies
│
├── 📁 mobile_agent/           # Spoke: Android Native Client (In Development)
├── 📁 shared/                 # Common schemas & configurations
├── 📄 ARCHITECTURE.md         # Full system architectural specification
└── 📄 README.md               # Project documentation
```

---

## ⚙️ Prerequisites & Setup

### 1. Requirements
* **Python 3.11+** installed
* **Google Cloud SDK** configured for Speech & TTS APIs
* **Audio Drivers & Libraries**:
  * **Windows**: `PyAudio` (if `pip install pyaudio` fails, use pre-compiled `.whl` or `pipwin`)
  * **Linux**: `portaudio19-dev` (`sudo apt install portaudio19-dev python3-pyaudio`)

### 2. Google Cloud Authentication

> [!IMPORTANT]
> Google Cloud Application Default Credentials (ADC) must be authorized on your machine for voice synthesis and recognition to function properly.

```bash
# Authenticate Google Cloud ADC
gcloud auth application-default login

# Set your active quota project ID
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

---

## 🏁 Quick Start Guide

### Step 1: Launch the Backend Hub (Brain)

Open Terminal 1 and start the FastAPI ASGI server:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
> [!NOTE]
> The backend server runs at `http://127.0.0.1:8000` with the WebSocket endpoint live at `ws://127.0.0.1:8000/ws/voice`.

---

### Step 2: Configure & Launch Desktop Agent (Spoke)

Open Terminal 2 and initialize the client:

1. **Environment Setup:**
   ```bash
   cd desktop_agent
   copy .env.example .env     # On Windows
   # cp .env.example .env     # On Linux / macOS
   ```

2. **Environment Variables (`desktop_agent/.env`):**
   ```ini
   SAHISTRA_WS_URL=ws://localhost:8000/ws/voice
   SAHISTRA_WS_TOKEN=sahistra_secret_123
   AUDIO_RATE=16000
   VAD_THRESHOLD=500
   STT_PRIMARY_LANG=hi-IN
   STT_ALT_LANGS=en-IN,en-US
   ```

3. **Install & Run:**
   ```bash
   pip install -r requirements.txt
   python voice_test_client.py
   ```

---

## 🛠️ Configuration Reference

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `SAHISTRA_WS_URL` | `ws://localhost:8000/ws/voice` | Backend WebSocket endpoint URI |
| `SAHISTRA_WS_TOKEN` | `sahistra_secret_123` | Auth key matching `SAHISTRA_AUTH_TOKEN` in Hub |
| `AUDIO_RATE` | `16000` | Audio sampling frequency in Hz |
| `VAD_THRESHOLD` | `500` | Voice Activity Detection RMS sensitivity threshold |
| `STT_PRIMARY_LANG` | `hi-IN` | Primary language code for speech recognition |

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">
  <sub>Built with ❤️ for Privacy and Personal Intelligence.</sub>
</div>
