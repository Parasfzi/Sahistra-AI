import os
import pytest
from core.providers.groq import GroqProvider
from core.schemas import ChatMessage
from core.exceptions import ProviderNotAvailableError

def test_groq_missing_api_key_raises_clean_error(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    
    provider = GroqProvider(api_key="")
    messages = [ChatMessage(role="user", content="Hello")]
    
    with pytest.raises(ProviderNotAvailableError) as exc_info:
        gen = provider.generate_stream(messages, system_instruction="Be helpful")
        import asyncio
        asyncio.run(gen.__anext__())
        
    assert exc_info.value.code == "API_KEY_MISSING"

@pytest.mark.asyncio
async def test_groq_live_stream_if_credentials_available():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        pytest.skip("GROQ_API_KEY not set in environment. Skipping live Groq test.")
        
    provider = GroqProvider(api_key=api_key, model_name="llama-3.3-70b-versatile")
    messages = [ChatMessage(role="user", content="Reply with the single word 'PONG'.")]
    
    chunks = []
    async for chunk in provider.generate_stream(messages, system_instruction=""):
        chunks.append(chunk)
        
    full_text = "".join(chunks)
    assert len(full_text) > 0
    assert "PONG" in full_text.upper()
