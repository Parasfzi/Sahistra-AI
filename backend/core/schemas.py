import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any

class BrainEventType(str, Enum):
    RESPONSE_START = "response_start"
    RESPONSE_CHUNK = "response_chunk"
    RESPONSE_END = "response_end"
    ERROR = "error"

@dataclass
class ChatMessage:
    role: str # "user" or "assistant"
    content: str
    timestamp: float = field(default_factory=time.time)

@dataclass
class BrainEvent:
    event_type: BrainEventType
    turn_id: str
    delta: Optional[str] = None
    full_text: Optional[str] = None
    code: Optional[str] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.event_type == BrainEventType.RESPONSE_START:
            return {
                "type": "response_start",
                "turn_id": self.turn_id
            }
        elif self.event_type == BrainEventType.RESPONSE_CHUNK:
            return {
                "type": "response_chunk",
                "turn_id": self.turn_id,
                "delta": self.delta or ""
            }
        elif self.event_type == BrainEventType.RESPONSE_END:
            return {
                "type": "response_end",
                "turn_id": self.turn_id,
                "full_text": self.full_text or ""
            }
        elif self.event_type == BrainEventType.ERROR:
            return {
                "type": "error",
                "turn_id": self.turn_id,
                "code": self.code or "UNKNOWN_ERROR",
                "message": self.message or "An unexpected error occurred."
            }
        return {
            "type": str(self.event_type.value),
            "turn_id": self.turn_id
        }
