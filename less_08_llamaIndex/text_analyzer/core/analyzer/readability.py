"""
readability.py
--------------
Syllable counting and Flesch Reading Ease computation.
"""


def _count_syllables(word: str) -> int:
    """
    Estimate syllable count using vowel-group heuristics.
    Not perfectly accurate but sufficient for readability scoring.
    """
    word = word.lower().strip("'")
    if not word:
        return 0
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    # Silent 'e' at end
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def _flesch_reading_ease(
    word_count: int,
    sentence_count: int,
    syllable_count: int,
) -> float:
    """
    Compute the Flesch Reading Ease score.
    Score range: 0 (very hard) – 100 (very easy).
    Formula: 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
    """
    if word_count == 0 or sentence_count == 0:
        return 0.0
    score = (
        206.835
        - 1.015 * (word_count / sentence_count)
        - 84.6 * (syllable_count / word_count)
    )
    return round(max(0.0, min(100.0, score)), 1)


def _reading_level(score: float) -> str:
    """Map a Flesch score to a human-readable grade label."""
    if score >= 90:
        return "Very Easy (5th grade)"
    elif score >= 80:
        return "Easy (6th grade)"
    elif score >= 70:
        return "Fairly Easy (7th grade)"
    elif score >= 60:
        return "Standard (8th–9th grade)"
    elif score >= 50:
        return "Fairly Difficult (10th–12th grade)"
    elif score >= 30:
        return "Difficult (College level)"
    else:
        return "Very Difficult (Professional)"


__all__ = ["_count_syllables", "_flesch_reading_ease", "_reading_level"]

