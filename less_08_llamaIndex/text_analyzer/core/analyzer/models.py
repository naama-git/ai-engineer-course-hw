"""
models.py
---------
Dataclasses and core data structures for text analysis.
"""

from dataclasses import dataclass, field


@dataclass
class TextStats:
    """Container for all computed statistics of a given text."""

    # Counts
    char_count: int = 0
    char_count_no_spaces: int = 0
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    unique_words: int = 0

    # Averages
    avg_word_length: float = 0.0
    avg_sentence_length: float = 0.0  # in words

    # Readability
    flesch_reading_ease: float = 0.0
    reading_level: str = ""
    estimated_reading_time_sec: int = 0

    # Richness
    lexical_diversity: float = 0.0  # unique / total words

    # Top words
    top_words: list[tuple[str, int]] = field(default_factory=list)

    # Sentiment indicators
    positive_word_count: int = 0
    negative_word_count: int = 0
    sentiment_label: str = ""

