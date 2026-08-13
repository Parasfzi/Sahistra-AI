from dataclasses import dataclass
from typing import List, Dict, Optional
from core.schemas import ChatMessage

@dataclass
class ConversationTurn:
    """Represents a single conversational turn: 1 user query + 1 assistant answer."""
    user_message: ChatMessage
    assistant_response: ChatMessage

class SessionContext:
    """In-memory sliding-window context for a single conversation session."""
    def __init__(self, session_id: str, max_turns: int = 10):
        self.session_id = session_id
        self.max_turns = max_turns
        self.turns: List[ConversationTurn] = []

    def add_completed_turn(self, user_text: str, assistant_text: str):
        """Appends a successfully completed turn and maintains sliding window."""
        turn = ConversationTurn(
            user_message=ChatMessage(role="user", content=user_text),
            assistant_response=ChatMessage(role="assistant", content=assistant_text)
        )
        self.turns.append(turn)
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]

    def get_messages(self, pending_user_text: Optional[str] = None) -> List[ChatMessage]:
        """Returns the flat chronological list of messages in this context."""
        messages: List[ChatMessage] = []
        for turn in self.turns:
            messages.append(turn.user_message)
            messages.append(turn.assistant_response)
        if pending_user_text is not None:
            messages.append(ChatMessage(role="user", content=pending_user_text))
        return messages

    def turn_count(self) -> int:
        return len(self.turns)

    def clear(self):
        self.turns.clear()

class ContextManager:
    """Manages in-memory SessionContext instances across active sessions."""
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self._sessions: Dict[str, SessionContext] = {}

    def get_or_create(self, session_id: str) -> SessionContext:
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionContext(session_id, max_turns=self.max_turns)
        return self._sessions[session_id]

    def remove_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]
