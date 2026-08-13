class BrainException(Exception):
    """Base exception for all Brain-related errors."""
    def __init__(self, message: str, code: str = "BRAIN_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code

class ProviderError(BrainException):
    """Raised when an LLM provider fails during request execution."""
    def __init__(self, message: str, code: str = "PROVIDER_ERROR"):
        super().__init__(message, code=code)

class ProviderNotAvailableError(BrainException):
    """Raised when an LLM provider is not configured or unavailable."""
    def __init__(self, message: str, code: str = "PROVIDER_UNAVAILABLE"):
        super().__init__(message, code=code)

class BrainTimeoutError(BrainException):
    """Raised when LLM generation exceeds timeout limit."""
    def __init__(self, message: str = "Request timed out", code: str = "TIMEOUT"):
        super().__init__(message, code=code)

class BrainCancelledError(BrainException):
    """Raised when generation is explicitly cancelled by the caller."""
    def __init__(self, message: str = "Generation cancelled", code: str = "CANCELLED"):
        super().__init__(message, code=code)
