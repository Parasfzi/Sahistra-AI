import asyncio
from typing import List, AsyncIterator, Optional
from core.schemas import ChatMessage
from core.providers.base import BaseLLMProvider

class MockProvider(BaseLLMProvider):
    """
    Mock LLM provider for unit tests and local development without API keys.
    Yields chunks with realistic asynchronous delays.
    """
    def __init__(
        self,
        canned_chunks: Optional[List[str]] = None,
        chunk_delay: float = 0.01,
        should_fail: bool = False,
        error_message: str = "Mock error occurred"
    ):
        self.canned_chunks = canned_chunks
        self.chunk_delay = chunk_delay
        self.should_fail = should_fail
        self.error_message = error_message

    async def generate_stream(
        self,
        messages: List[ChatMessage],
        system_instruction: str,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> AsyncIterator[str]:
        if self.should_fail:
            from core.exceptions import ProviderError
            raise ProviderError(self.error_message, code="MOCK_PROVIDER_FAILURE")

        last_user_message = messages[-1].content if messages else "empty"
        
        if self.canned_chunks is not None:
            chunks = self.canned_chunks
        else:
            # Generate deterministic words echoing context awareness
            chunks = [
                "I ", "heard ", "you: ", f'"{last_user_message}". ',
                "How ", "can ", "I ", "assist ", "you ", "next?"
            ]

        for chunk in chunks:
            if self.chunk_delay > 0:
                await asyncio.sleep(self.chunk_delay)
            yield chunk
