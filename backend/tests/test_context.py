import pytest
from core.context import SessionContext, ContextManager, ConversationTurn
from core.schemas import ChatMessage

def test_session_context_initialization():
    ctx = SessionContext(session_id="test-1", max_turns=3)
    assert ctx.session_id == "test-1"
    assert ctx.turn_count() == 0
    assert len(ctx.get_messages()) == 0

def test_single_turn_is_user_plus_assistant_pair():
    ctx = SessionContext(session_id="test-1", max_turns=3)
    ctx.add_completed_turn(user_text="Hi", assistant_text="Hello!")
    
    assert ctx.turn_count() == 1
    messages = ctx.get_messages()
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[0].content == "Hi"
    assert messages[1].role == "assistant"
    assert messages[1].content == "Hello!"

def test_sliding_window_max_turns():
    max_turns = 3
    ctx = SessionContext(session_id="test-1", max_turns=max_turns)
    
    for i in range(1, 6): # Add 5 turns
        ctx.add_completed_turn(user_text=f"User {i}", assistant_text=f"Bot {i}")
        
    assert ctx.turn_count() == max_turns
    messages = ctx.get_messages()
    # 3 turns = 6 messages (Turns 3, 4, 5)
    assert len(messages) == 6
    assert messages[0].content == "User 3"
    assert messages[1].content == "Bot 3"
    assert messages[4].content == "User 5"
    assert messages[5].content == "Bot 5"

def test_context_manager():
    mgr = ContextManager(max_turns=5)
    ctx1 = mgr.get_or_create("sess-A")
    ctx2 = mgr.get_or_create("sess-B")
    
    ctx1.add_completed_turn("A1", "A1_ans")
    assert ctx1.turn_count() == 1
    assert ctx2.turn_count() == 0
    
    mgr.remove_session("sess-A")
    # Fresh session recreated if asked
    ctx1_new = mgr.get_or_create("sess-A")
    assert ctx1_new.turn_count() == 0
