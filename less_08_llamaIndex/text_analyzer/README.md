# Text Analyser

A lightweight, fully local text-analysis application built with Python 3 and [Gradio](https://gradio.app). Analyse single texts or compare two texts on readability, word frequency, sentiment, and other linguistic metrics — no external NLP APIs or ML models required.

## Features

- **Basic counts** — characters (with/without spaces), words, sentences, paragraphs
- **Readability** — Flesch Reading Ease score and plain-English grade label (e.g. "Very Easy (5th grade)")
- **Estimated reading time** — based on average adult reading pace (~238 wpm)
- **Lexical diversity** — ratio of unique words to total words
- **Top-word frequency** — most frequent content words (stop words excluded) with ASCII bar chart
- **Sentiment indicators** — positive/negative signal-word counts and overall label (keyword-based, not ML)
- **Side-by-side comparison** — compare any two texts on key metrics with deltas

## Project Structure

```
text_analyzer/
├── app.py                 # Gradio UI and entry point
├── core/
│   ├── analyzer.py        # All NLP & statistical logic (counts, Flesch, sentiment, etc.)
│   └── formatters.py      # Markdown rendering for the UI
├── tests/
│   └── test_analyzer.py   # Unit tests for analyzer
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10+
- See `requirements.txt` for dependencies (Gradio, pytest)

## Installation

```bash
cd text_analyzer
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Run the app

```bash
python app.py
```

The Gradio UI will start at `http://0.0.0.0:7860`. Open it in a browser to:

1. **Analyse Text** — paste or type text, set “Top N words”, click **Analyse**. View summary (counts, readability, sentiment) and top-word frequency.
2. **Compare Texts** — enter two texts and click **Compare** to see a side-by-side table of metrics and deltas.
3. **About** — short description and architecture overview.

### Run tests

```bash
python -m pytest tests/ -v
```

## Technical Notes

- **Sentiment** — Uses a fixed list of positive/negative keywords (e.g. “good”, “great”, “bad”, “terrible”). No machine learning or external APIs.
- **Syllables** — Estimated with vowel-group heuristics and a simple silent-*e* rule for Flesch scoring. Fast and good enough for readability; not phonetically precise.
- **Dependencies** — Aside from Gradio (UI) and pytest (tests), the core uses only Python standard library (`re`, `math`, `collections`, `dataclasses`).

## License

Part of the AI Engineer course homework (Lesson 08 — LlamaIndex). Use and modify as needed for learning.
