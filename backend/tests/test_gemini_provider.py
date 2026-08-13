import os
import pytest
from core.providers.gemini import GeminiProvider
from core.schemas import ChatMessage
from core.exceptions import ProviderNotAvailableError

def test_gemini_missing_api_key_raises_clean_error(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    
    provider = GeminiProvider(api_key="")
    messages = [ChatMessage(role="user", content="Hello")]
    
    with pytest.raises(ProviderNotAvailableError) as exc_info:
        # Accessing generator triggers _get_client
        gen = provider.generate_stream(messages, system_instruction="Be helpful")
        import asyncio
        asyncio.run(gen.__anext__())
        
    assert exc_info.value.code == "API_KEY_MISSING"

@pytest.mark.asyncio
async def test_gemini_live_stream_if_credentials_available():
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY / GOOGLE_API_KEY not set in environment. Skipping live Gemini test.")
        
    provider = GeminiProvider(api_key=api_key, model_name="gemini-3.5-flash")
    messages = [ChatMessage(role="user", content="Reply with the single word 'PONG'.")]
    
    chunks = []
    async for chunk in provider.generate_stream(messages, system_instruction=""):
        chunks.append(chunk)
        
    full_text = "".join(chunks)
    assert len(full_text) > 0
    assert "PONG" in full_text.upper()
