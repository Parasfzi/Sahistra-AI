import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

@dataclass(frozen=True)
class BrainConfig:
    auth_token: str = os.environ.get("SAHISTRA_AUTH_TOKEN", "sahistra_secret_123")
    llm_provider: str = os.environ.get("LLM_PROVIDER", "groq")
    llm_model_name: str = os.environ.get(
        "LLM_MODEL_NAME",
        "llama-3.3-70b-versatile" if os.environ.get("LLM_PROVIDER", "groq").lower() == "groq" else "gemini-3.5-flash"
    )
    gemini_api_key: str = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
    groq_api_key: str = os.environ.get("GROQ_API_KEY") or ""
    llm_temperature: float = float(os.environ.get("LLM_TEMPERATURE", "0.7"))
    llm_max_output_tokens: int = int(os.environ.get("LLM_MAX_OUTPUT_TOKENS", "1024"))
    max_context_turns: int = int(os.environ.get("MAX_CONTEXT_TURNS", "10"))
    request_timeout_seconds: float = float(os.environ.get("LLM_REQUEST_TIMEOUT_SECONDS", "30.0"))
    system_instruction: str = os.environ.get(
        "SYSTEM_INSTRUCTION",
        "You are Sahistra, a fast, intelligent, and concise personal AI assistant. "
        "For voice conversations, keep responses natural, direct, and brief (1-3 sentences). "
        "Avoid long bullet lists, code blocks, or heavy formatting unless the user explicitly requests details or code."
    )

def get_config() -> BrainConfig:
    load_dotenv(override=True)
    return BrainConfig()
