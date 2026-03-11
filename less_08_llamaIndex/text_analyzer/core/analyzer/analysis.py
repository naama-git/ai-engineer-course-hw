"""
analysis.py
-----------
High-level text analysis orchestration: glue between tokenization, readability,
sentiment, and aggregation into TextStats.
"""

import re
from collections import Counter
from typing import Optional

from .models import TextStats
from .tokenization import _tokenize_words
from .readability import _count_syllables, _flesch_reading_ease, _reading_level
from .sentiment import _STOP_WORDS, compute_sentiment


def analyze(text: str, top_n: int = 10) -> Optional[TextStats]:
    """
    Perform a full analysis of the provided text.

    Parameters
    ----------
    text : str
        The raw input text to analyze.
    top_n : int
        Number of most-frequent non-stop words to return.

    Returns
    -------
    TextStats or None if the text is empty/whitespace.
    """
    text = text.strip()
    if not text:
        return None

    stats = TextStats()

    # --- Basic Counts ---
    stats.char_count = len(text)
    stats.char_count_no_spaces = len(text.replace(" ", ""))

    words = _tokenize_words(text)
    stats.word_count = len(words)
    stats.unique_words = len(set(words))

    # Sentences: split on .  !  ? followed by whitespace or end-of-string
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    stats.sentence_count = max(1, len(sentences))

    # Paragraphs: split on blank lines
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    stats.paragraph_count = max(1, len(paragraphs))

    # --- Averages ---
    if words:
        stats.avg_word_length = round(
            sum(len(w) for w in words) / len(words),
            2,
        )
    stats.avg_sentence_length = round(
        stats.word_count / stats.sentence_count,
        1,
    )

    # --- Readability ---
    syllable_count = sum(_count_syllables(w) for w in words)
    stats.flesch_reading_ease = _flesch_reading_ease(
        stats.word_count,
        stats.sentence_count,
        syllable_count,
    )
    stats.reading_level = _reading_level(stats.flesch_reading_ease)

    # Average adult reads ~238 words per minute
    stats.estimated_reading_time_sec = max(
        1,
        round((stats.word_count / 238) * 60),
    )

    # --- Lexical Diversity ---
    if stats.word_count:
        stats.lexical_diversity = round(
            stats.unique_words / stats.word_count,
            3,
        )

    # --- Top Words (excluding stop words) ---
    content_words = [w for w in words if w not in _STOP_WORDS and len(w) > 2]
    stats.top_words = Counter(content_words).most_common(top_n)

    # --- Sentiment Indicators ---
    (
        stats.positive_word_count,
        stats.negative_word_count,
        stats.sentiment_label,
    ) = compute_sentiment(words)

    return stats


__all__ = ["analyze"]

