"""
comparison.py
-------------
Logic for comparing two texts using the analysis engine.
"""

from .analysis import analyze


def compare_texts(text_a: str, text_b: str) -> dict:
    """
    Compare two texts and return a dictionary of deltas for key metrics.

    Parameters
    ----------
    text_a, text_b : str
        The two texts to compare.

    Returns
    -------
    dict mapping metric names to (value_a, value_b, delta) tuples.
    """
    a = analyze(text_a)
    b = analyze(text_b)

    if a is None or b is None:
        return {}

    metrics = [
        ("Word Count", a.word_count, b.word_count),
        ("Unique Words", a.unique_words, b.unique_words),
        ("Avg Word Length", a.avg_word_length, b.avg_word_length),
        ("Avg Sentence Length", a.avg_sentence_length, b.avg_sentence_length),
        ("Flesch Score", a.flesch_reading_ease, b.flesch_reading_ease),
        ("Lexical Diversity", a.lexical_diversity, b.lexical_diversity),
    ]

    return {
        name: (va, vb, round(vb - va, 3))
        for name, va, vb in metrics
    }


__all__ = ["compare_texts"]

