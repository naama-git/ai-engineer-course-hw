"""
tokenization.py
---------------
Helpers for tokenizing raw text into word tokens.
"""

import re


def _tokenize_words(text: str) -> list[str]:
    """Extract lowercase alphabetic tokens from text."""
    return re.findall(r"[a-z']+", text.lower())


__all__ = ["_tokenize_words"]

