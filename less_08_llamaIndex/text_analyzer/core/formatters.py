"""
formatters.py
-------------
Presentation helpers: convert raw TextStats into strings and
structured data suitable for the Gradio UI layer.
"""

from core.analyzer import TextStats


def format_reading_time(seconds: int) -> str:
    """Return a human-friendly reading time string."""
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    remaining = seconds % 60
    return f"{minutes}m {remaining}s" if remaining else f"{minutes}m"


def stats_to_summary_markdown(stats: TextStats) -> str:
    """
    Build a Markdown summary card for the main metrics panel.

    Parameters
    ----------
    stats : TextStats
        Computed analysis results.

    Returns
    -------
    str — Markdown-formatted summary.
    """
    rt = format_reading_time(stats.estimated_reading_time_sec)
    return f"""
### 📊 Text Overview

| Metric | Value |
|--------|-------|
| Characters | {stats.char_count:,} ({stats.char_count_no_spaces:,} without spaces) |
| Words | {stats.word_count:,} |
| Unique Words | {stats.unique_words:,} |
| Sentences | {stats.sentence_count:,} |
| Paragraphs | {stats.paragraph_count:,} |
| Avg Word Length | {stats.avg_word_length} chars |
| Avg Sentence Length | {stats.avg_sentence_length} words |

### 📚 Readability

| Metric | Value |
|--------|-------|
| Flesch Score | **{stats.flesch_reading_ease}** / 100 |
| Reading Level | {stats.reading_level} |
| Estimated Read Time | {rt} |
| Lexical Diversity | {stats.lexical_diversity:.1%} |

### 🎭 Sentiment Indicators

| Metric | Value |
|--------|-------|
| Overall Sentiment | {stats.sentiment_label} |
| Positive Word Signals | {stats.positive_word_count} |
| Negative Word Signals | {stats.negative_word_count} |
"""


def top_words_to_markdown(stats: TextStats) -> str:
    """Format top-word frequency list as a Markdown table."""
    if not stats.top_words:
        return "_No significant words found._"

    max_freq = stats.top_words[0][1] if stats.top_words else 1
    rows = []
    for rank, (word, freq) in enumerate(stats.top_words, 1):
        bar_len = round((freq / max_freq) * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        rows.append(f"| {rank} | `{word}` | {freq} | `{bar}` |")

    table = "\n".join(rows)
    return f"""### 🔤 Top Words

| # | Word | Count | Frequency |
|---|------|-------|-----------|
{table}
"""


def compare_to_markdown(comparison: dict) -> str:
    """Format a comparison dict (from compare_texts) as a Markdown table."""
    if not comparison:
        return "_Please provide two non-empty texts to compare._"

    rows = []
    for metric, (va, vb, delta) in comparison.items():
        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "—")
        rows.append(f"| {metric} | {va} | {vb} | {arrow} {abs(delta)} |")

    table = "\n".join(rows)
    return f"""### ⚖️ Side-by-Side Comparison

| Metric | Text A | Text B | Δ Change |
|--------|--------|--------|----------|
{table}
"""
