import re
from typing import List
from tts_normalizer import TTSNormalizer

class SentenceChunker:
    """
    Incremental sentence and phrase boundary detector for streaming LLM text responses.
    Splits text streams into natural, speakable sentences/phrases without word fragmentation.
    """
    
    # Primary end-of-sentence punctuation
    SENTENCE_END_PATTERN = re.compile(r'([.?!]+(?:\s+|\Z)|\n+)')
    # Secondary phrase boundaries for long streams
    PHRASE_END_PATTERN = re.compile(r'([,;:—-]+(?:\s+|\Z))')

    def __init__(
        self,
        min_chunk_chars: int = 15,
        max_chunk_chars: int = 120,
        soft_clause_chars: int = 40
    ):
        self.min_chunk_chars = min_chunk_chars
        self.max_chunk_chars = max_chunk_chars
        self.soft_clause_chars = soft_clause_chars
        self.buffer = ""

    def add_delta(self, delta: str) -> List[str]:
        """
        Appends a streaming delta token and returns ready speakable sentences/phrases.
        """
        if not delta:
            return []

        self.buffer += delta
        return self._extract_chunks(is_flush=False)

    def flush(self) -> List[str]:
        """
        Flushes all remaining buffered text at stream end.
        """
        return self._extract_chunks(is_flush=True)

    def reset(self):
        """
        Clears internal buffer (used on cancellation / barge-in).
        """
        self.buffer = ""

    def _extract_chunks(self, is_flush: bool) -> List[str]:
        chunks: List[str] = []

        while True:
            normalized_buf = TTSNormalizer.normalize(self.buffer)
            if not normalized_buf:
                if is_flush:
                    self.buffer = ""
                break

            # 1. Try matching primary sentence boundary (. ? ! \n)
            match = self.SENTENCE_END_PATTERN.search(self.buffer)
            if match:
                end_idx = match.end()
                candidate_raw = self.buffer[:end_idx]
                candidate_clean = TTSNormalizer.normalize(candidate_raw)

                if candidate_clean:
                    chunks.append(candidate_clean)
                    self.buffer = self.buffer[end_idx:]
                    continue
                else:
                    self.buffer = self.buffer[end_idx:]
                    continue

            # 2. If buffer is getting long, try soft clause boundaries (, ; :)
            if len(normalized_buf) >= self.soft_clause_chars:
                match = self.PHRASE_END_PATTERN.search(self.buffer)
                if match:
                    end_idx = match.end()
                    candidate_clean = TTSNormalizer.normalize(self.buffer[:end_idx])
                    if candidate_clean and len(candidate_clean) >= self.min_chunk_chars:
                        chunks.append(candidate_clean)
                        self.buffer = self.buffer[end_idx:]
                        continue

            # 3. Hard fallback for very long sentences without punctuation (> max_chunk_chars)
            if len(self.buffer) >= self.max_chunk_chars:
                # Split at last whitespace before max_chunk_chars
                split_idx = self.buffer.rfind(' ', 0, self.max_chunk_chars)
                if split_idx == -1:
                    split_idx = self.max_chunk_chars

                candidate_clean = TTSNormalizer.normalize(self.buffer[:split_idx])
                if candidate_clean:
                    chunks.append(candidate_clean)
                self.buffer = self.buffer[split_idx:].lstrip()
                continue

            # 4. If flushing, emit whatever remains in the buffer
            if is_flush:
                candidate_clean = TTSNormalizer.normalize(self.buffer)
                if candidate_clean:
                    chunks.append(candidate_clean)
                self.buffer = ""
                break

            # No ready chunk found yet; wait for more deltas
            break

        return chunks
