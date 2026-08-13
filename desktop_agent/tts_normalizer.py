import re

class TTSNormalizer:
    """
    Normalizes raw LLM markdown text into clean, natural text suitable for TTS engines.
    Preserves text/UI layer markdown while generating sanitized speakable strings.
    """
    
    # Pre-compiled regex patterns
    CODE_BLOCK_PATTERN = re.compile(r'```[\s\S]*?```')
    INLINE_CODE_PATTERN = re.compile(r'`([^`]+)`')
    MARKDOWN_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\([^\)]+\)')
    URL_PATTERN = re.compile(r'https?://\S+')
    
    BOLD_ITALIC_PATTERN = re.compile(r'(\*{1,3}|_{1,3})([^*_]+)\1')
    HEADING_PATTERN = re.compile(r'^\s*#{1,6}\s+', re.MULTILINE)
    BULLET_PATTERN = re.compile(r'^\s*[-*+]\s+', re.MULTILINE)
    NUMBERED_LIST_PATTERN = re.compile(r'^\s*\d+[\.\)]\s+', re.MULTILINE)
    
    SPECIAL_SYMBOLS_PATTERN = re.compile(r'[~>#|\\\[\]{}]')
    REPEATED_PUNCT_PATTERN = re.compile(r'([.?!,;:-])\1+')
    WHITESPACE_PATTERN = re.compile(r'\s+')

    @classmethod
    def normalize(cls, text: str) -> str:
        """
        Converts raw markdown text to speakable text.
        """
        if not text:
            return ""

        # 1. Remove code blocks completely or replace with a pause
        cleaned = cls.CODE_BLOCK_PATTERN.sub('', text)

        # 2. Extract link label from [label](url)
        cleaned = cls.MARKDOWN_LINK_PATTERN.sub(r'\1', cleaned)

        # 3. Remove raw URLs
        cleaned = cls.URL_PATTERN.sub('', cleaned)

        # 4. Convert inline code `code` -> code
        cleaned = cls.INLINE_CODE_PATTERN.sub(r'\1', cleaned)

        # 5. Remove bold / italic formatting (*text*, **text**, _text_)
        # Run twice to handle nested formatting like ***bold italic***
        cleaned = cls.BOLD_ITALIC_PATTERN.sub(r'\2', cleaned)
        cleaned = cls.BOLD_ITALIC_PATTERN.sub(r'\2', cleaned)

        # 6. Remove headings markers (# Heading -> Heading)
        cleaned = cls.HEADING_PATTERN.sub('', cleaned)

        # 7. Convert bullet points & numbered lists into clause pauses
        cleaned = cls.BULLET_PATTERN.sub('', cleaned)
        cleaned = cls.NUMBERED_LIST_PATTERN.sub('', cleaned)

        # 8. Strip standalone markdown structural symbols
        cleaned = cls.SPECIAL_SYMBOLS_PATTERN.sub('', cleaned)

        # 9. Normalize repeated punctuation (e.g. "!!" -> "!")
        cleaned = cls.REPEATED_PUNCT_PATTERN.sub(r'\1', cleaned)

        # 10. Normalize whitespace & linebreaks
        cleaned = cls.WHITESPACE_PATTERN.sub(' ', cleaned).strip()

        return cleaned
