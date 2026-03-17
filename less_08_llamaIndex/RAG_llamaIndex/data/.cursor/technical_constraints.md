## Technical Constraints and Coding Standards

### 1. Platform and Runtime Constraints

- **Python version**
  - Target: **Python 3.10+** (as documented in `README.md`).
  - Assumption: Modern type‑hint support (`list[str]`, `|` unions, etc.) is available.

- **Execution model**
  - Single‑process, single‑threaded Gradio app.
  - Analysis is performed synchronously per request:
    - No async IO.
    - No background job queue.
  - Suitable for local desktop use or low‑traffic deployments; not tuned for high concurrency.

- **Environment and dependencies**
  - Expected to run inside a virtual environment created via `python -m venv venv`.
  - Dependencies installed from `requirements.txt` (primarily Gradio and pytest).
  - **Core analysis must remain standard‑library only**:
    - No heavy NLP or ML libraries (`nltk`, `spacy`, `transformers`, etc.) in `core/`.
    - Rationale: keep footprint small, installation simple, and respect “fully local, lightweight” goals.

### 2. Functional Constraints

- **Scope of analysis**
  - Language focus: English‑like text; heuristics are tuned for Latin alphabet.
  - Sentence detection:
    - Implemented via regex splits on `.`, `!`, `?`.
    - Does not model advanced punctuation (e.g., ellipses nuances, abbreviations, quoted text edge cases).
  - Paragraph detection:
    - Split on blank lines (`\n\s*\n`).
    - Single‑paragraph texts are normalized to `paragraph_count >= 1`.

- **Tokenization and counts**
  - Word tokens are extracted via regex `"[a-z']+"` on a lowercased version of the text.
  - Non‑alphabetic tokens (numbers, symbols, non‑ASCII letters) are ignored for the purposes of:
    - Word counts.
    - Top‑word analysis.
    - Sentiment analysis.
  - Character counts:
    - `char_count`: raw string length.
    - `char_count_no_spaces`: spaces removed; other whitespace (e.g., newlines) remains.

- **Readability metrics**
  - Only **Flesch Reading Ease** is supported:
    - Formula: \(206.835 - 1.015 \cdot (words/sentences) - 84.6 \cdot (syllables/words)\).
    - Score clamped to \[0, 100\].
  - Reading level labels are derived from Flesch ranges (e.g., “Very Easy (5th grade)”, “Difficult (College level)”).
  - Syllable counting is approximate:
    - Based on vowel‑group heuristics and a silent‑“e” adjustment.
    - Not phonetically perfect; “good enough” for relative readability, not for linguistic research.

- **Sentiment analysis**
  - Implemented via small fixed keyword sets:
    - `_POSITIVE_WORDS` and `_NEGATIVE_WORDS` are hard‑coded frozensets.
  - Sentiment label is based on the difference between counts of positive and negative keywords (set intersections).
  - No machine learning, no context modeling, no negation handling (e.g., “not good” is still counted as positive).
  - Intended as a coarse indicator only.

- **Top-word frequency**
  - Uses a manually curated `_STOP_WORDS` list to filter high‑frequency function words.
  - Ignores short tokens (`len(w) <= 2`).
  - Returns at most `top_n` words via `Counter(...).most_common(top_n)`.
  - Not intended to be a full keyword extraction or topic modeling system.

### 3. Non-Functional Constraints

- **Performance**
  - Designed for short‑to‑medium texts (e.g., < ~10k words).
  - Complexity is linear in text length:
    - Single pass tokenization, syllable counting, and counting operations.
  - No incremental or streaming processing; each analysis is independent and recomputes metrics from scratch.

- **Memory usage**
  - All data is kept in memory per request; no persistence or caching.
  - Keyword sets and stopwords are small and static.

- **Security and privacy**
  - The app itself does not call external services or APIs.
  - Gradio is configured with `share=False`; public links are not created by default.
  - No authentication or authorization layer:
    - Assumes local or trusted network usage.
  - No data is stored; once the process exits, all user input is forgotten.

### 4. Coding Standards and Design Guidelines

- **Separation of concerns**
  - `app.py`:
    - May contain UI construction and callback wiring only.
    - Must not contain text‑analysis business logic.
  - `core/analyzer/` package:
    - Contains all text processing and statistics, split by responsibility:
      - `models` (dataclasses), `tokenization`, `readability`, `sentiment`, `analysis`, `comparison`.
    - Public API exposed via `core.analyzer` is limited to simple, well‑typed functions (`analyze`, `compare_texts`) and dataclasses (`TextStats`), plus a small set of tested helpers (`_count_syllables`, `_flesch_reading_ease`).
  - `core/formatters.py`:
    - Responsible only for presentation logic (Markdown rendering, formatting helpers).
  - `tests/`:
    - Contains pytest test modules; no application code.

- **Type hints and dataclasses**
  - Use standard library `dataclasses` for structured results (`TextStats`).
  - Use Python 3.10+ type hints (e.g., `list[str]`, `Optional[T]`, `dict[str, tuple[...]]`).

- **Error handling and edge cases**
  - Functions that may receive empty/whitespace text return `None` (for `analyze`) or `{}` (for `compare_texts`) rather than raising exceptions.
  - UI callbacks convert these sentinel values into user‑friendly markdown messages.
  - Guard against division by zero in readability by:
    - Returning 0.0 score when `word_count` or `sentence_count` is zero.
    - Ensuring counts like `sentence_count` and `paragraph_count` are at least 1 where appropriate.

- **Testing and quality**
  - Unit tests must:
    - Cover edge cases (e.g., extreme Flesch inputs, empty strings).
    - Verify invariants (e.g., Flesch score is always within \[0, 100\], lexical diversity in \[0, 1\]).
    - Assert correctness of “directional” behaviors (e.g., comparison deltas).
  - New features in `core/` or `formatters` should be accompanied by corresponding tests in `tests/`.

### 5. Extension Guidelines (Constraints on Future Changes)

- **Adding new metrics**
  - Should re‑use existing tokenization pipeline whenever possible.
  - Must maintain backward compatibility of `TextStats` where feasible (add fields rather than change semantics of existing ones).
  - Any new fields added to `TextStats` should:
    - Be documented in `system_spec.md`.
    - Be surfaced via formatters (or explicitly documented as internal‑only).

- **Introducing new dependencies**
  - UI‑only improvements can add lightweight libraries if they:
    - Do not introduce heavy native dependencies.
    - Do not require external services.
  - Core analysis must remain free of external NLP/ML dependencies to preserve the educational and portable nature of the project.

- **Persistence and integration**
  - If persistence or logging is added later:
    - It should be optional and clearly documented.
    - It should not be required for basic text analysis workflows.

