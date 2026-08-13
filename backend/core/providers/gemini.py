import os
from typing import List, AsyncIterator, Optional
from core.schemas import ChatMessage
from core.providers.base import BaseLLMProvider
from core.exceptions import ProviderError, ProviderNotAvailableError

class GeminiProvider(BaseLLMProvider):
    """
    Concrete provider for Google Gemini models using the official `google-genai` SDK.
    Initialized lazily; validates API key at request time to ensure server startup is never blocked.
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-3.5-flash"
    ):
        self._api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
        self.model_name = model_name
        self._client = None

    def _get_client(self):
        if self._client is None:
            # Re-check environment variable if not provided during init
            key = self._api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
            if not key:
                raise ProviderNotAvailableError(
                    "Gemini API key not found. Please set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.",
                    code="API_KEY_MISSING"
                )
            try:
                from google import genai
                self._client = genai.Client(api_key=key)
            except Exception as e:
                raise ProviderError(
                    f"Failed to initialize Gemini client: {e.__class__.__name__}",
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
            from google.genai import types

            contents = []
            for msg in messages:
                role = "user" if msg.role == "user" else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg.content)]
                    )
                )

            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

            response_stream = await client.aio.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config=config,
            )

            async for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        except (ProviderError, ProviderNotAvailableError):
            raise
        except Exception as e:
            # Avoid logging raw errors that might contain sensitive key information
            error_class = e.__class__.__name__
            clean_msg = str(e)
            # Scrub any raw keys if present in error message
            if self._api_key and self._api_key in clean_msg:
                clean_msg = clean_msg.replace(self._api_key, "[REDACTED_API_KEY]")
            raise ProviderError(f"Gemini API error ({error_class}): {clean_msg}", code="GEMINI_API_ERROR")
