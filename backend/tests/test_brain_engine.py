import pytest
import asyncio
from core.brain import BrainEngine
from core.config import BrainConfig
from core.providers.mock import MockProvider
from core.schemas import BrainEventType

@pytest.mark.asyncio
async def test_brain_engine_successful_stream():
    provider = MockProvider(canned_chunks=["This ", "is ", "Sahistra."], chunk_delay=0.001)
    config = BrainConfig(max_context_turns=5, request_timeout_seconds=5.0)
    engine = BrainEngine(provider=provider, config=config)
    
    events = []
    async for event in engine.process_stream("session-1", "Who are you?"):
        events.append(event)
        
    assert len(events) == 5 # 1 START + 3 CHUNKS + 1 END
    assert events[0].event_type == BrainEventType.RESPONSE_START
    assert events[0].turn_id.startswith("turn-")
    
    turn_id = events[0].turn_id
    assert events[1].event_type == BrainEventType.RESPONSE_CHUNK
    assert events[1].delta == "This "
    assert events[1].turn_id == turn_id
    
    assert events[2].event_type == BrainEventType.RESPONSE_CHUNK
    assert events[2].delta == "is "
    
    assert events[3].event_type == BrainEventType.RESPONSE_CHUNK
    assert events[3].delta == "Sahistra."
    
    assert events[4].event_type == BrainEventType.RESPONSE_END
    assert events[4].full_text == "This is Sahistra."
    assert events[4].turn_id == turn_id
    
    # Verify in-memory context was updated
    session_ctx = engine.context_manager.get_or_create("session-1")
    assert session_ctx.turn_count() == 1
    assert session_ctx.turns[0].user_message.content == "Who are you?"
    assert session_ctx.turns[0].assistant_response.content == "This is Sahistra."

@pytest.mark.asyncio
async def test_brain_engine_cancellation_does_not_update_context():
    # Provider with slow delay
    provider = MockProvider(canned_chunks=["Chunk1", "Chunk2", "Chunk3"], chunk_delay=0.1)
    config = BrainConfig(max_context_turns=5)
    engine = BrainEngine(provider=provider, config=config)
    
    cancel_event = asyncio.Event()
    
    events = []
    
    async def cancel_later():
        await asyncio.sleep(0.05)
        cancel_event.set()
        
    asyncio.create_task(cancel_later())
    
    async for event in engine.process_stream("session-cancel", "Cancel me", cancel_event=cancel_event):
        events.append(event)
        
    # Check that error event is yielded
    last_event = events[-1]
    assert last_event.event_type == BrainEventType.ERROR
    assert last_event.code == "CANCELLED"
    
    # Verify context was NOT updated
    session_ctx = engine.context_manager.get_or_create("session-cancel")
    assert session_ctx.turn_count() == 0

@pytest.mark.asyncio
async def test_brain_engine_provider_error_does_not_update_context():
    provider = MockProvider(should_fail=True, error_message="Provider died")
    config = BrainConfig(max_context_turns=5)
    engine = BrainEngine(provider=provider, config=config)
    
    events = []
    async for event in engine.process_stream("session-err", "Hello"):
        events.append(event)
        
    assert len(events) == 2 # START + ERROR
    assert events[0].event_type == BrainEventType.RESPONSE_START
    assert events[1].event_type == BrainEventType.ERROR
    assert events[1].code == "MOCK_PROVIDER_FAILURE"
    
    # Verify context was NOT updated
    session_ctx = engine.context_manager.get_or_create("session-err")
    assert session_ctx.turn_count() == 0

@pytest.mark.asyncio
async def test_unique_turn_id_per_generation():
    provider = MockProvider(canned_chunks=["A"])
    engine = BrainEngine(provider=provider)
    
    events1 = [e async for e in engine.process_stream("sess", "msg1")]
    events2 = [e async for e in engine.process_stream("sess", "msg2")]
    
    turn1_id = events1[0].turn_id
    turn2_id = events2[0].turn_id
    
    assert turn1_id != turn2_id
