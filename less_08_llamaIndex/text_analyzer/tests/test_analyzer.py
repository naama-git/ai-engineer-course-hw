"""
test_analyzer.py
----------------
Unit tests for core/analyzer.py.
Run with: python -m pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from core.analyzer import (
    analyze,
    compare_texts,
    _count_syllables,
    _flesch_reading_ease,
)


# ---------------------------------------------------------------------------
# Syllable Counter
# ---------------------------------------------------------------------------

class TestCountSyllables:
    def test_single_syllable(self):
        assert _count_syllables("cat") == 1

    def test_two_syllables(self):
        assert _count_syllables("happy") == 2

    def test_silent_e(self):
        # "love" → lo-ve, silent e removed → 1
        assert _count_syllables("love") == 1

    def test_empty_string(self):
        assert _count_syllables("") == 0


# ---------------------------------------------------------------------------
# Flesch Score
# ---------------------------------------------------------------------------

class TestFleschScore:
    def test_zero_words(self):
        assert _flesch_reading_ease(0, 0, 0) == 0.0

    def test_clamp_to_100(self):
        # Very short words / very short sentences → score might exceed 100 raw
        score = _flesch_reading_ease(100, 1, 100)
        assert score <= 100.0

    def test_clamp_to_0(self):
        # Very long sentences, many syllables
        score = _flesch_reading_ease(5, 1, 100)
        assert score >= 0.0


# ---------------------------------------------------------------------------
# Analyze Function
# ---------------------------------------------------------------------------

class TestAnalyze:
    _simple = "The cat sat on the mat. It was a red mat. The cat liked it."

    def test_returns_none_for_empty(self):
        assert analyze("") is None
        assert analyze("   ") is None

    def test_word_count(self):
        stats = analyze(self._simple)
        assert stats is not None
        assert stats.word_count == 15  # tokenised alpha words (the, cat, sat, on, the, mat, it, was, a, red, mat, the, cat, liked, it)

    def test_sentence_count(self):
        stats = analyze(self._simple)
        assert stats.sentence_count == 3

    def test_unique_words_lte_total(self):
        stats = analyze(self._simple)
        assert stats.unique_words <= stats.word_count

    def test_lexical_diversity_range(self):
        stats = analyze(self._simple)
        assert 0.0 <= stats.lexical_diversity <= 1.0

    def test_flesch_score_range(self):
        stats = analyze(self._simple)
        assert 0.0 <= stats.flesch_reading_ease <= 100.0

    def test_top_words_length(self):
        stats = analyze(self._simple, top_n=5)
        assert len(stats.top_words) <= 5

    def test_sentiment_label_neutral(self):
        stats = analyze("The box is on the table in the room.")
        assert stats.sentiment_label == "😐 Neutral"

    def test_sentiment_positive(self):
        stats = analyze("This is a great, wonderful, amazing, fantastic day!")
        assert "Positive" in stats.sentiment_label

    def test_sentiment_negative(self):
        stats = analyze("This is terrible, awful, horrible, and very bad.")
        assert "Negative" in stats.sentiment_label


# ---------------------------------------------------------------------------
# Compare Texts
# ---------------------------------------------------------------------------

class TestCompareTexts:
    def test_empty_returns_empty_dict(self):
        assert compare_texts("", "hello world") == {}

    def test_keys_present(self):
        result = compare_texts("Hello world.", "Hello brave new world.")
        assert "Word Count" in result
        assert "Flesch Score" in result

    def test_delta_direction(self):
        result = compare_texts("Hi.", "Hello world, this is a longer sentence today.")
        # Text B has more words → positive delta
        _, _, delta = result["Word Count"]
        assert delta > 0
