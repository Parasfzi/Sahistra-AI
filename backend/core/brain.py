import asyncio
import uuid
from typing import AsyncIterator, Optional
from core.schemas import BrainEvent, BrainEventType
from core.context import ContextManager
from core.providers.base import BaseLLMProvider
from core.providers import get_provider
from core.config import BrainConfig, get_config
from core.exceptions import (
    BrainException,
    BrainTimeoutError,
    BrainCancelledError,
)

class BrainEngine:
    """
    Core AI Brain Orchestrator for Sahistra AI.
    Handles streaming responses, session context management, timeout, and cancellation.
    """
    def __init__(
        self,
        provider: Optional[BaseLLMProvider] = None,
        config: Optional[BrainConfig] = None
    ):
        self.config = config or get_config()
        api_key = self.config.groq_api_key if self.config.llm_provider.lower() == "groq" else self.config.gemini_api_key
        self.provider = provider or get_provider(
            name=self.config.llm_provider,
            api_key=api_key,
            model_name=self.config.llm_model_name
        )
        self.context_manager = ContextManager(max_turns=self.config.max_context_turns)

    async def process_stream(
        self,
        session_id: str,
        user_input: str,
        cancel_event: Optional[asyncio.Event] = None
    ) -> AsyncIterator[BrainEvent]:
        """
        Processes a user text input and yields streaming BrainEvents.
        
        Turn lifecycle:
        1. Emits RESPONSE_START
        2. Streams RESPONSE_CHUNK events
        3. On completion, updates in-memory context and emits RESPONSE_END
        4. On error/timeout/cancellation, emits ERROR event (context is NOT updated).
        """
        turn_id = f"turn-{uuid.uuid4().hex[:8]}"
        session_context = self.context_manager.get_or_create(session_id)
        
        # Fetch existing turns + pending prompt
        messages = session_context.get_messages(pending_user_text=user_input)
        
        # 1. Emit START event
        yield BrainEvent(event_type=BrainEventType.RESPONSE_START, turn_id=turn_id)
        
        accumulated_chunks = []
        
        try:
            stream_gen = self.provider.generate_stream(
                messages=messages,
                system_instruction=self.config.system_instruction,
                temperature=self.config.llm_temperature,
                max_tokens=self.config.llm_max_output_tokens
            )
            
            while True:
                if cancel_event and cancel_event.is_set():
                    raise BrainCancelledError("Generation cancelled by user.")
                
                try:
                    chunk = await asyncio.wait_for(
                        stream_gen.__anext__(),
                        timeout=self.config.request_timeout_seconds
                    )
                except StopAsyncIteration:
                    break
                except asyncio.TimeoutError:
                    raise BrainTimeoutError(
                        f"Generation timed out after {self.config.request_timeout_seconds}s."
                    )
                
                if cancel_event and cancel_event.is_set():
                    raise BrainCancelledError("Generation cancelled by user.")
                
                if chunk:
                    accumulated_chunks.append(chunk)
                    yield BrainEvent(
                        event_type=BrainEventType.RESPONSE_CHUNK,
                        turn_id=turn_id,
                        delta=chunk
                    )
            
            full_text = "".join(accumulated_chunks)
            
            # Update context ONLY after complete, successful generation
            session_context.add_completed_turn(user_text=user_input, assistant_text=full_text)
            
            # Emit END event
            yield BrainEvent(
                event_type=BrainEventType.RESPONSE_END,
                turn_id=turn_id,
                full_text=full_text
            )

        except asyncio.CancelledError:
            yield BrainEvent(
                event_type=BrainEventType.ERROR,
                turn_id=turn_id,
                code="CANCELLED",
                message="Generation was cancelled."
            )
        except BrainCancelledError as e:
            yield BrainEvent(
                event_type=BrainEventType.ERROR,
                turn_id=turn_id,
                code=e.code,
                message=e.message
            )
        except BrainTimeoutError as e:
            yield BrainEvent(
                event_type=BrainEventType.ERROR,
                turn_id=turn_id,
                code=e.code,
                message=e.message
            )
        except BrainException as e:
            yield BrainEvent(
                event_type=BrainEventType.ERROR,
                turn_id=turn_id,
                code=e.code,
                message=e.message
            )
        except Exception as e:
            yield BrainEvent(
                event_type=BrainEventType.ERROR,
                turn_id=turn_id,
                code="INTERNAL_ERROR",
                message=f"Brain processing failed: {e.__class__.__name__}"
            )
