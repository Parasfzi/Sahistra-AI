from abc import ABC, abstractmethod
from typing import List, AsyncIterator
from core.schemas import ChatMessage

class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers in Sahistra AI."""
    
    @abstractmethod
    async def generate_stream(
        self,
        messages: List[ChatMessage],
        system_instruction: str,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> AsyncIterator[str]:
        """
        Asynchronously streams token deltas from the provider.
        
        Args:
            messages: List of ChatMessage representing conversational context and latest prompt.
            system_instruction: System prompt framing assistant persona and guidelines.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in response.
            
        Yields:
            str: Delta text chunks as they arrive from the model.
        """
        pass
