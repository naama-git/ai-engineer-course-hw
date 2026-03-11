"""
sentiment.py
------------
Word lists and helpers for rudimentary sentiment and stopword handling.
"""

from collections.abc import Iterable


_POSITIVE_WORDS: frozenset[str] = frozenset(
    [
        "good",
        "great",
        "excellent",
        "amazing",
        "wonderful",
        "fantastic",
        "brilliant",
        "outstanding",
        "superb",
        "love",
        "happy",
        "joy",
        "positive",
        "best",
        "awesome",
        "beautiful",
        "perfect",
        "success",
        "win",
        "winning",
        "nice",
        "fun",
        "helpful",
        "impressive",
        "strong",
    ]
)

_NEGATIVE_WORDS: frozenset[str] = frozenset(
    [
        "bad",
        "terrible",
        "awful",
        "horrible",
        "dreadful",
        "poor",
        "wrong",
        "failure",
        "fail",
        "sad",
        "hate",
        "ugly",
        "worst",
        "negative",
        "weak",
        "boring",
        "disappointing",
        "disaster",
        "problem",
        "issue",
        "difficult",
        "hard",
        "frustrating",
        "annoying",
        "useless",
        "broken",
    ]
)

_STOP_WORDS: frozenset[str] = frozenset(
    [
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "shall",
        "that",
        "this",
        "these",
        "those",
        "it",
        "its",
        "i",
        "you",
        "he",
        "she",
        "we",
        "they",
        "my",
        "your",
        "his",
        "her",
        "our",
        "their",
        "not",
        "no",
        "so",
        "if",
        "as",
        "up",
        "out",
        "from",
        "into",
        "about",
        "than",
        "more",
        "also",
        "just",
        "can",
        "all",
    ]
)


def compute_sentiment(words: Iterable[str]) -> tuple[int, int, str]:
    """
    Given an iterable of words, compute positive/negative counts and label.

    Returns
    -------
    (positive_count, negative_count, label)
    """
    word_set = set(words)
    positive_count = len(word_set & _POSITIVE_WORDS)
    negative_count = len(word_set & _NEGATIVE_WORDS)

    diff = positive_count - negative_count
    if diff > 0:
        label = "😊 Positive"
    elif diff < 0:
        label = "😟 Negative"
    else:
        label = "😐 Neutral"

    return positive_count, negative_count, label


__all__ = [
    "_POSITIVE_WORDS",
    "_NEGATIVE_WORDS",
    "_STOP_WORDS",
    "compute_sentiment",
]

