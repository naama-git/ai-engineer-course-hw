# Component Deep Dive

Detailed breakdown of the internal modules and their specific responsibilities.

## 1. Analysis Engine (`core/analyzer/`)
- **`tokenization.py`**: Uses regex `[a-z']+` to extract clean word tokens. It converts everything to lowercase to ensure "The" and "the" are treated as the same word.
- **`readability.py`**: Implements the Flesch Reading Ease formula. 
    - *Formula*: `206.835 - 1.015 * (ASL) - 84.6 * (ASW)` where ASL is Average Sentence Length and ASW is Average Syllables per Word.
- **`sentiment.py`**: Uses a `frozenset` of positive and negative keywords. It calculates the "net" sentiment by comparing word overlaps. It's fast and requires zero training data.
- **`comparison.py`**: Orchestrates the analysis of two separate strings and computes the mathematical difference (Delta) for each metric.

## 2. Presentation Layer (`core/formatters.py`)
This module is responsible for the "visual" logic:
- **`stats_to_summary_markdown`**: Generates the primary statistics table.
- **`top_words_to_markdown`**: Creates a custom ASCII bar chart using block characters (`█` and `░`) to represent word frequency visually within a Markdown table.
- **`format_reading_time`**: Converts raw seconds into a human-readable `Xm Ys` format.

## 3. User Interface (`app.py`)
The UI is built using **Gradio Blocks** for maximum control over layout:
- **Tabbed Interface**: Separates "Analyse" from "Compare" to reduce cognitive load.
- **Metric Chips**: Custom CSS classes were added to create "chips" for high-level metrics (Words, Read Time, Level) at the top of the results.
- **Interactive Examples**: Pre-loaded "Simple" and "Complex" samples are provided to help users understand the tool's capabilities immediately.

## 4. Quality Assurance (`tests/test_analyzer.py`)
The testing strategy focuses on:
- **Edge Cases**: Empty strings, strings with no vowels, and extremely long sentences.
- **Clamping**: Ensuring Flesch scores stay within the 0-100 range.
- **Sentiment Accuracy**: Verifying that known positive/negative phrases trigger the correct labels.