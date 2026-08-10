import asyncio
import websockets
import pyaudio
import struct
import math
import sys
import json
import os
import queue
from dotenv import load_dotenv
from google.cloud import speech, texttospeech
from google.api_core.exceptions import GoogleAPIError

# Load environment variables
load_dotenv()

# --- Configuration ---
AUTH_TOKEN = os.environ.get("SAHISTRA_WS_TOKEN", "sahistra_secret_123")
WS_URI = os.environ.get("SAHISTRA_WS_URL", "ws://localhost:8000/ws/voice") + f"?token={AUTH_TOKEN}"
RATE = int(os.environ.get("AUDIO_RATE", 16000))
CHUNK = int(os.environ.get("AUDIO_CHUNK", 1024))
THRESHOLD = int(os.environ.get("VAD_THRESHOLD", 500))
SILENCE_CHUNKS = int(RATE / CHUNK * float(os.environ.get("VAD_SILENCE_DURATION", 1.5)))

STT_PRIMARY_LANG = os.environ.get("STT_PRIMARY_LANG", "hi-IN")
STT_ALT_LANGS = os.environ.get("STT_ALT_LANGS", "en-IN,en-US").split(",")

FORMAT = pyaudio.paInt16
CHANNELS = 1

# Initialize Google Cloud Clients lazily
stt_client = None
tts_client = None

# Global state for barge-in
playback_active_event = asyncio.Event()
cancel_playback_event = asyncio.Event()

def init_clients():
    global stt_client, tts_client
    try:
        stt_client = speech.SpeechClient()
        tts_client = texttospeech.TextToSpeechClient()
        return True
    except Exception as e:
        print("\n" + "="*60)
        print("🚨 GOOGLE CLOUD CREDENTIALS NOT FOUND 🚨")
        print("="*60)
        print("You must authenticate with Google Cloud before running this client.")
        print("Run: gcloud auth application-default login")
        print("Run: gcloud auth application-default set-quota-project YOUR_PROJECT_ID")
        print("="*60 + "\n")
        return False

def get_rms(block):
    count = len(block) / 2
    format = "%dh" % (count)
    try:
        shorts = struct.unpack(format, block)
    except struct.error:
        return 0
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0/32768.0)
        sum_squares += n * n
    return math.sqrt(sum_squares / count) * 32768 if count > 0 else 0

async def play_audio_chunked(audio_data: bytes):
    """Play audio in chunks to allow cancellation (Barge-in)."""
    p = pyaudio.PyAudio()
    try:
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)
        print("🔊 Playing response... (Speak to interrupt)")
        playback_active_event.set()
        cancel_playback_event.clear()

        # Write in chunks so we can yield control to the event loop and check cancellation
        chunk_size = CHUNK * 4 # Slightly larger chunks for playback
        for i in range(0, len(audio_data), chunk_size):
            if cancel_playback_event.is_set():
                print("\n🛑 Playback cancelled (Barge-in detected)!")
                break
            
            chunk = audio_data[i:i+chunk_size]
            
            # Run the blocking write in a thread to keep the event loop responsive
            await asyncio.to_thread(stream.write, chunk)
            await asyncio.sleep(0) # Yield control
            
    except Exception as e:
        print(f"Error playing audio: {e}")
    finally:
        if 'stream' in locals() and stream.is_active():
            stream.stop_stream()
            stream.close()
        p.terminate()
        playback_active_event.clear()
        cancel_playback_event.clear()

def _synthesize_text_sync(text: str) -> bytes:
    """Blocking function to synthesize text."""
    try:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(language_code="en-US", name="en-US-Journey-F")
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE
        )
        response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        return response.audio_content
    except GoogleAPIError as e:
        print(f"TTS API Error: {e}")
        return b''
    except Exception as e:
        print(f"Unknown TTS Error: {e}")
        return b''

async def synthesize_text_async(text: str) -> bytes:
    return await asyncio.to_thread(_synthesize_text_sync, text)

class MicrophoneStream:
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True
        self._p = pyaudio.PyAudio()

    def __enter__(self):
        self._audio_stream = self._p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._p.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        print("\n🎙️ [Listening... Speak now]")
        silent_chunks = 0
        recording = False

        while not self.closed:
            try:
                # Use a timeout to allow checking flags periodically
                chunk = self._buff.get(timeout=0.1)
            except queue.Empty:
                continue
                
            if chunk is None:
                return

            data = [chunk]
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            raw_data = b"".join(data)
            rms = get_rms(raw_data)

            # Barge-in logic: If user starts speaking while TTS is playing
            if rms > THRESHOLD:
                if playback_active_event.is_set():
                    cancel_playback_event.set() # Stop the audio

                recording = True
                silent_chunks = 0
            elif recording:
                silent_chunks += 1
                if silent_chunks > SILENCE_CHUNKS:
                    print("\n[Silence detected. Finishing transcription...]")
                    self.closed = True
                    return

            if recording:
                yield raw_data

def _streaming_recognize_sync():
    """Blocking function to handle the Google STT stream."""
    try:
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=STT_PRIMARY_LANG,
            alternative_language_codes=STT_ALT_LANGS,
            enable_automatic_punctuation=True
        )
        streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True
        )

        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)
            
            responses = stt_client.streaming_recognize(streaming_config, requests)

            final_transcript = ""
            for response in responses:
                if not response.results:
                    continue
                result = response.results[0]
                if not result.alternatives:
                    continue

                transcript = result.alternatives[0].transcript
                
                if not result.is_final:
                    sys.stdout.write(f"\rPartial: {transcript[:80].ljust(80)}")
                    sys.stdout.flush()
                else:
                    final_transcript = transcript
                    sys.stdout.write(f"\rFinal: {final_transcript.ljust(80)}\n")
                    sys.stdout.flush()

            return final_transcript.strip()
            
    except GoogleAPIError as e:
        print(f"\nSTT API Error: {e}")
        return ""
    except Exception as e:
        print(f"\nUnknown STT Error: {e}")
        return ""

async def record_and_transcribe_async() -> str:
    return await asyncio.to_thread(_streaming_recognize_sync)

async def voice_client():
    if not init_clients():
        return
        
    attempt = 0
    max_backoff = 30
    
    while True: # Auto-reconnect loop with exponential backoff
        try:
            print(f"Connecting to Hub...")
            async with websockets.connect(WS_URI) as websocket:
                print("✅ Connected to Sahistra Voice Hub (Text Mode).")
                attempt = 0 # Reset attempts on success
                
                while True:
                    # 1. Record and transcribe via streaming STT
                    transcript = await record_and_transcribe_async()
                    
                    if not transcript:
                        continue
                        
                    # 3. Send final text to Hub
                    payload = {"type": "transcript", "text": transcript}
                    await websocket.send(json.dumps(payload))
                    
                    # 4. Wait for text response from Hub
                    try:
                        response_str = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        response_data = json.loads(response_str)
                        
                        if response_data.get("type") == "response":
                            hub_text = response_data.get("text", "")
                            print(f"🤖 Hub says: {hub_text}")
                            
                            # 5. Synthesize text to speech
                            audio_response = await synthesize_text_async(hub_text)
                            if audio_response:
                                # Play chunked audio (allows barge-in cancellation)
                                await play_audio_chunked(audio_response)
                                
                    except asyncio.TimeoutError:
                        print("⏳ Timeout waiting for Hub response.")
                    except json.JSONDecodeError:
                        print("❌ Received invalid JSON from Hub")
                            
        except websockets.exceptions.ConnectionClosed as e:
            wait_time = min(max_backoff, 2 ** attempt)
            print(f"⚠️ Disconnected from Hub (Code: {e.code}). Reconnecting in {wait_time}s...")
            await asyncio.sleep(wait_time)
            attempt += 1
        except ConnectionRefusedError:
            wait_time = min(max_backoff, 2 ** attempt)
            print(f"❌ Cannot connect to Hub. Reconnecting in {wait_time}s...")
            await asyncio.sleep(wait_time)
            attempt += 1
        except Exception as e:
            wait_time = min(max_backoff, 2 ** attempt)
            print(f"❌ Unexpected Error: {e}. Reconnecting in {wait_time}s...")
            await asyncio.sleep(wait_time)
            attempt += 1

if __name__ == "__main__":
    try:
        print("Starting Sahistra Voice Client...")
        asyncio.run(voice_client())
    except KeyboardInterrupt:
        print("\n🛑 Exiting Sahistra Client cleanly...")
        sys.exit(0)
