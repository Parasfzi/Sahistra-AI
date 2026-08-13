import os
from typing import List, AsyncIterator, Optional
from core.schemas import ChatMessage
from core.providers.base import BaseLLMProvider
from core.exceptions import ProviderError, ProviderNotAvailableError

class GroqProvider(BaseLLMProvider):
    """
    Concrete LLM provider for Groq Cloud models using the official `groq` SDK.
    Initialized lazily; validates API key at request time to ensure server startup is never blocked.
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "llama-3.3-70b-versatile"
    ):
        self._api_key = api_key or os.environ.get("GROQ_API_KEY") or ""
        self.model_name = model_name
        self._client = None

    def _get_client(self):
        if self._client is None:
            key = self._api_key or os.environ.get("GROQ_API_KEY") or ""
            if not key:
                raise ProviderNotAvailableError(
                    "Groq API key not found. Please set GROQ_API_KEY environment variable.",
                    code="API_KEY_MISSING"
                )
            try:
                from groq import AsyncGroq
                self._client = AsyncGroq(api_key=key)
            except Exception as e:
                raise ProviderError(
                    f"Failed to initialize Groq client: {e.__class__.__name__}",
                    code="CLIENT_INIT_FAILED"
                )
        return self._client

    async def generate_stream(
        self,
        messages: List[ChatMessage],
        system_instruction: str,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> AsyncIterator[str]:
        client = self._get_client()

        try:
            groq_messages = []
            if system_instruction:
                groq_messages.append({"role": "system", "content": system_instruction})

            for msg in messages:
                role = "user" if msg.role == "user" else "assistant"
                groq_messages.append({"role": role, "content": msg.content})

            completion_stream = await client.chat.completions.create(
                model=self.model_name,
                messages=groq_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            async for chunk in completion_stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except (ProviderError, ProviderNotAvailableError):
            raise
        except Exception as e:
            error_class = e.__class__.__name__
            clean_msg = str(e)
            if self._api_key and self._api_key in clean_msg:
                clean_msg = clean_msg.replace(self._api_key, "[REDACTED_API_KEY]")
            raise ProviderError(f"Groq API error ({error_class}): {clean_msg}", code="GROQ_API_ERROR")
