# Sahistra AI - Setup & Running Guide

This guide explains how to set up and run the entire Sahistra AI project, including the **Backend Hub (Brain)** and the **Desktop Agent (Voice Client)**.

---

## Architecture Overview
Sahistra runs on a **Hub and Spoke** model:
- **Backend (Hub)**: The central brain running a FastAPI server (WebSocket and REST API).
- **Desktop Agent (Spoke)**: Runs locally on your machine, handles audio capture (Microphone), Google Cloud STT/TTS, and communicates with the Backend.

---

## Prerequisites
1. **Python 3.11+** installed on your system.
2. **Google Cloud SDK** installed (needed for STT and TTS APIs).
3. **PyAudio Dependencies**:
   - **Windows**: You might need to install PyAudio. If direct `pip install pyaudio` fails, you can download the appropriate pre-compiled `.whl` file or install via `pipwin`.
   - **Linux**: Requires portaudio development headers (`sudo apt-get install portaudio19-dev python3-pyaudio`).

---

## Step-by-Step Startup Guide

### Step 1: Authenticate Google Cloud (Important)
Since the voice client uses Google Cloud Speech-to-Text and Text-to-Speech, you must authenticate your local terminal:
```bash
# 1. Login to Google Cloud Application Default Credentials (ADC)
gcloud auth application-default login

# 2. Set your Google Cloud billing/quota project
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```
*(Replace `YOUR_PROJECT_ID` with your actual GCP Project ID)*

---

### Step 2: Start the Backend Hub (Brain)
The backend acts as the central server.
1. Open a new terminal.
2. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the backend server using Uvicorn:
   ```bash
   uvicorn main:app --reload
   ```
   *The backend will run on `http://127.0.0.1:8000`*

---

### Step 3: Start the Desktop Agent (Voice Spoke)
The desktop agent captures your voice, converts it to text, sends it to the Hub, and plays back the response.
1. Open a **second** terminal.
2. Navigate to the `desktop_agent` folder:
   ```bash
   cd desktop_agent
   ```
3. Set up the environment variables:
   - Copy the `.env.example` file and rename it to `.env`:
     - **Windows**: `copy .env.example .env`
     - **macOS/Linux**: `cp .env.example .env`
   - Open `.env` and verify the settings:
     ```env
     SAHISTRA_WS_URL=ws://localhost:8000/ws/voice
     SAHISTRA_WS_TOKEN=sahistra_secret_123
     ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the voice client:
   ```bash
   python voice_test_client.py
   ```

---

## Running in the Background (Optional)
If you want to run these commands in the background without keeping multiple terminal windows open, you can run them using tools like `screen`, `tmux` (on Linux), or background jobs on Windows PowerShell.
