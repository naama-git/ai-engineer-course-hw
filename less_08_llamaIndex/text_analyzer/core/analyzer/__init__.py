"""
core.analyzer package
---------------------
Public API surface for text analysis logic.
"""

from .models import TextStats
from .analysis import analyze
from .comparison import compare_texts
from .readability import _count_syllables, _flesch_reading_ease

__all__ = [
    "TextStats",
    "analyze",
    "compare_texts",
    "_count_syllables",
    "_flesch_reading_ease",
]

