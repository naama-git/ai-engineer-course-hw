"""
core package — text analysis logic and formatters.
"""

from core.analyzer import analyze, compare_texts, TextStats
from core.formatters import (
    stats_to_summary_markdown,
    top_words_to_markdown,
    compare_to_markdown,
)

__all__ = [
    "analyze",
    "compare_texts",
    "TextStats",
    "stats_to_summary_markdown",
    "top_words_to_markdown",
    "compare_to_markdown",
]
