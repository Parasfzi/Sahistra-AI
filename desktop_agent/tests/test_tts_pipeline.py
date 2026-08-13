import pytest
import asyncio
from tts_normalizer import TTSNormalizer
from sentence_chunker import SentenceChunker

# 1. Bold Markdown
def test_bold_markdown_normalization():
    raw = "This is **bold** text and __also bold__."
    expected = "This is bold text and also bold."
    assert TTSNormalizer.normalize(raw) == expected

# 2. Italic Markdown
def test_italic_markdown_normalization():
    raw = "This is *italic* and _also italic_."
    expected = "This is italic and also italic."
    assert TTSNormalizer.normalize(raw) == expected

# 3. Bullet lists
def test_bullet_list_normalization():
    raw = "- First item\n* Second item\n+ Third item"
    expected = "First item Second item Third item"
    assert TTSNormalizer.normalize(raw) == expected

# 4. Numbered lists
def test_numbered_list_normalization():
    raw = "1. First item\n2) Second item"
    expected = "First item Second item"
    assert TTSNormalizer.normalize(raw) == expected

# 5. Code blocks
def test_code_block_normalization():
    raw = "Here is the code:\n```python\ndef hello():\n    print('hi')\n```\nHope that helps!"
    expected = "Here is the code: Hope that helps!"
    assert TTSNormalizer.normalize(raw) == expected

# 6. Inline code
def test_inline_code_normalization():
    raw = "Use the `pip install` command to proceed."
    expected = "Use the pip install command to proceed."
    assert TTSNormalizer.normalize(raw) == expected

# 7. Markdown links
def test_markdown_link_normalization():
    raw = "Visit [Google AI Studio](https://aistudio.google.com/) for API keys."
    expected = "Visit Google AI Studio for API keys."
    assert TTSNormalizer.normalize(raw) == expected

# 8. Mixed Hindi + English
def test_mixed_hindi_english_normalization():
    raw = "**Namaste!** Main aapki *help* kar sakta hoon."
    expected = "Namaste! Main aapki help kar sakta hoon."
    assert TTSNormalizer.normalize(raw) == expected

# 9. Long responses chunking
def test_long_response_sentence_chunking():
    chunker = SentenceChunker(soft_clause_chars=30)
    tokens = ["This ", "is ", "the ", "first ", "sentence. ", "Here ", "is ", "the ", "second ", "sentence! "]
    emitted = []
    for t in tokens:
        emitted.extend(chunker.add_delta(t))
    emitted.extend(chunker.flush())
    
    assert len(emitted) == 2
    assert emitted[0] == "This is the first sentence."
    assert emitted[1] == "Here is the second sentence!"

# 10. Very short responses
def test_short_response_flush():
    chunker = SentenceChunker()
    emitted = chunker.add_delta("Hi")
    assert len(emitted) == 0 # Buffer holds short text
    flushed = chunker.flush()
    assert len(flushed) == 1
    assert flushed[0] == "Hi"

# 11. Response ending without punctuation
def test_unpunctuated_response_flush():
    chunker = SentenceChunker()
    chunker.add_delta("I am Sahistra")
    flushed = chunker.flush()
    assert flushed == ["I am Sahistra"]

# 12. Streaming cancellation / barge-in reset
def test_chunker_reset_on_cancellation():
    chunker = SentenceChunker()
    chunker.add_delta("Partial text before cancel")
    chunker.reset()
    assert chunker.buffer == ""
    assert len(chunker.flush()) == 0

# 13. TTS Queue cancellation simulation
@pytest.mark.asyncio
async def test_tts_queue_cancellation():
    queue = asyncio.Queue()
    cancel_flag = asyncio.Event()
    
    processed = []
    
    async def worker():
        while True:
            item = await queue.get()
            if item is None:
                queue.task_done()
                break
            if not cancel_flag.is_set():
                processed.append(item)
            queue.task_done()
            
    worker_task = asyncio.create_task(worker())
    
    await queue.put("Sentence 1")
    await asyncio.sleep(0.01) # Yield to worker so Sentence 1 is processed
    cancel_flag.set() # Set cancellation
    await queue.put("Sentence 2")
    await queue.put(None)
    await worker_task
    
    assert processed == ["Sentence 1"]

# 14. No text duplication & 15. No sentence loss
def test_no_sentence_loss_or_duplication():
    chunker = SentenceChunker()
    text = "First sentence here. Second sentence follows. Third sentence ends."
    
    # Feed one character at a time to simulate token streaming
    emitted = []
    for char in text:
        emitted.extend(chunker.add_delta(char))
    emitted.extend(chunker.flush())
    
    reconstructed = " ".join(emitted)
    assert "First sentence here." in reconstructed
    assert "Second sentence follows." in reconstructed
    assert "Third sentence ends." in reconstructed
    assert len(emitted) == 3
