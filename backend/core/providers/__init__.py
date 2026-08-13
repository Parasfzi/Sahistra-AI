from typing import Optional
from core.providers.base import BaseLLMProvider
from core.providers.mock import MockProvider
from core.providers.gemini import GeminiProvider
from core.providers.groq import GroqProvider

def get_provider(
    name: Optional[str] = None,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    **kwargs
) -> BaseLLMProvider:
    """Factory to retrieve the configured LLM provider."""
    provider_name = (name or "groq").lower().strip()
    
    if provider_name == "mock":
        return MockProvider(**kwargs)
    elif provider_name == "gemini":
        default_model = model_name or "gemini-3.5-flash"
        return GeminiProvider(api_key=api_key, model_name=default_model)
    elif provider_name == "groq":
        default_model = model_name or "llama-3.3-70b-versatile"
        return GroqProvider(api_key=api_key, model_name=default_model)
    else:
        raise ValueError(f"Unsupported LLM provider: {name}. Choose 'groq', 'gemini', or 'mock'.")

__all__ = ["BaseLLMProvider", "GeminiProvider", "MockProvider", "GroqProvider", "get_provider"]
