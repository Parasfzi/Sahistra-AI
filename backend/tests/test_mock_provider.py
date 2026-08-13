import pytest
from core.providers.mock import MockProvider
from core.schemas import ChatMessage
from core.exceptions import ProviderError

@pytest.mark.asyncio
async def test_mock_provider_streaming():
    canned = ["Hello", " ", "World", "!"]
    provider = MockProvider(canned_chunks=canned, chunk_delay=0.001)
    
    messages = [ChatMessage(role="user", content="Hi")]
    chunks = []
    async for chunk in provider.generate_stream(messages, system_instruction=""):
        chunks.append(chunk)
        
    assert chunks == canned
    assert "".join(chunks) == "Hello World!"

@pytest.mark.asyncio
async def test_mock_provider_failure():
    provider = MockProvider(should_fail=True, error_message="Simulated Quota Error")
    messages = [ChatMessage(role="user", content="Hi")]
    
    with pytest.raises(ProviderError) as exc_info:
        async for _ in provider.generate_stream(messages, system_instruction=""):
            pass
            
    assert "Simulated Quota Error" in str(exc_info.value)
