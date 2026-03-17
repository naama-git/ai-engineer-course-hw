## System Specification – Text Analyser

### 1. Purpose and Scope

- **Primary goal**: Provide a fully local, lightweight text-analysis tool that offers readability metrics, lexical statistics, simple sentiment indicators, and side‑by‑side comparisons without relying on external NLP APIs or machine‑learning services.
- **Target users**: Developers, students, and analysts who need quick feedback on the structure and complexity of English texts (e.g., homework, documentation, blog posts).
- **Out-of-scope**:
  - Deep semantic understanding or ML-based sentiment/emotion analysis.
  - Multi-language support beyond simple behavior on non-English characters.
  - Long‑document indexing, search, or retrieval (separate from LlamaIndex course content).

### 2. High-Level Architecture

The application is structured as a thin UI layer on top of a pure‑Python analysis core.

- **UI Layer (`app.py`)**
  - Technology: **Python 3 + Gradio Blocks**.
  - Responsibilities:
    - Define the Gradio Blocks layout (tabs, textboxes, sliders, buttons, markdown outputs).
    - Expose callback functions (`run_analysis`, `run_comparison`) that adapt user input to the core API.
    - Start the Gradio server, select a free port, and configure theme and CSS overrides.
  - No business logic: all text processing is delegated to `core/`.

- **Core Analysis Layer (`core/analyzer/`)**
  - Technology: **Python standard library only** (`re`, `collections.Counter`, `dataclasses`, `typing`).
  - Package layout (separation of responsibilities):
    - `core/analyzer/models.py`:
      - Defines the `TextStats` dataclass as the canonical container for all metrics.
    - `core/analyzer/tokenization.py`:
      - Implements `_tokenize_words` over lower‑cased alphabetic tokens.
    - `core/analyzer/readability.py`:
      - Implements `_count_syllables` via vowel‑group heuristics.
      - Computes Flesch Reading Ease (`_flesch_reading_ease`) and maps scores to grade labels (`_reading_level`).
    - `core/analyzer/sentiment.py`:
      - Maintains small in‑memory lexicons:
        - Positive keyword set (`_POSITIVE_WORDS`).
        - Negative keyword set (`_NEGATIVE_WORDS`).
        - Stopword set (`_STOP_WORDS`) for top‑word filtering.
      - Provides `compute_sentiment` to derive positive/negative counts and label from tokens.
    - `core/analyzer/analysis.py`:
      - Provides the main analysis function `analyze(text: str, top_n: int) -> TextStats | None`, orchestrating tokenization, readability, sentiment, and aggregation into `TextStats`.
    - `core/analyzer/comparison.py`:
      - Provides comparison logic `compare_texts(text_a: str, text_b: str) -> dict` using the analysis engine.
    - `core/analyzer/__init__.py`:
      - Exposes the public API surface (`TextStats`, `analyze`, `compare_texts`, `_count_syllables`, `_flesch_reading_ease`) while keeping the internal modules logically separated.

- **Presentation / Formatting Layer (`core/formatters.py`)**
  - Technology: Python standard library.
  - Responsibilities:
    - Convert `TextStats` instances into Markdown strings suitable for rendering in Gradio markdown components:
      - `stats_to_summary_markdown` – main metrics table + readability + sentiment section.
      - `top_words_to_markdown` – table with ASCII bar chart for frequency.
      - `compare_to_markdown` – side‑by‑side comparison table for two analyses.
    - Provide small utilities such as `format_reading_time` to display reading time as `"Xs"`, `"Ym"`, or `"Ym Zs"`.

- **Test Layer (`tests/test_analyzer.py`)**
  - Technology: **pytest**.
  - Responsibilities:
    - Unit test core helpers (`_count_syllables`, `_flesch_reading_ease`).
    - Validate `analyze` for:
      - Empty/whitespace behavior.
      - Word, sentence, and uniqueness counts.
      - Lexical diversity and Flesch score ranges.
      - Top‑word list length.
      - Sentiment labeling (neutral / positive / negative).
    - Validate `compare_texts` for:
      - Empty‑input handling.
      - Presence of key metrics.
      - Correct delta sign behavior.

### 3. Data Flow

1. **User input (UI)**
   - Single Text:
     - User types or pastes text into the `Input Text` textbox and chooses `Top N words` via a slider (5–25, default 10).
     - On clicking **Analyse** or pressing Enter, Gradio calls `run_analysis(text, top_n)`.
   - Comparison:
     - User fills `Text A` and `Text B` textboxes.
     - On clicking **Compare**, Gradio calls `run_comparison(text_a, text_b)`.

2. **Core analysis**
   - `run_analysis`:
     - Validates that text is non‑empty; otherwise returns a pair of placeholder markdown strings.
     - Calls `core.analyzer.analyze(text, top_n)` and receives a `TextStats` instance.
   - `analyze`:
     - Normalizes and trims the text.
     - Computes:
       - Counts: characters (with/without spaces), words, sentences, paragraphs, unique word count.
       - Averages: average word length, average sentence length.
       - Readability metrics: Flesch score + textual grade label, estimated reading time (seconds) assuming ~238 words per minute.
       - Lexical diversity: `unique_words / word_count`.
       - Top words (excluding stopwords and short tokens) via `Counter(...).most_common(top_n)`.
       - Sentiment indicators via set intersection with positive/negative keyword sets, and a coarse label (Positive / Negative / Neutral with emoji).
   - `run_comparison`:
     - Delegates to `compare_texts(text_a, text_b)`.
   - `compare_texts`:
     - Calls `analyze` for both inputs.
     - If either is `None`, returns an empty dict.
     - Otherwise builds a dict mapping metric names to `(value_a, value_b, delta)` tuples.

3. **Formatting**
   - For single analysis:
     - `stats_to_summary_markdown(stats)` → Markdown string for the summary panel.
     - `top_words_to_markdown(stats)` → Markdown string for the “Top Words” panel, including ASCII bars.
   - For comparison:
     - `compare_to_markdown(comparison_dict)` → Markdown string for a comparison table.

4. **Presentation**
   - Gradio markdown components in `app.py` receive the strings and render them in the browser.
   - The UI uses a custom theme (`gr.themes.Soft`) and lightweight CSS tweaks for a clean, card‑like layout.

### 4. Technology Stack

- **Language**: Python 3.10+.
- **Runtime**: Local Python process, no external services.
- **UI Framework**: Gradio Blocks with:
  - `gr.Blocks`, `gr.TabItem`, `gr.Textbox`, `gr.Slider`, `gr.Markdown`, `gr.Button`, `gr.ClearButton`, `gr.Examples`.
  - Theme: `gr.themes.Soft` with `primary_hue="indigo"`, `secondary_hue="slate"`, custom font stack [`Inter`, `sans-serif`].
- **Testing**: pytest.
- **Dependencies**:
  - Gradio (UI).
  - pytest (testing).
  - Standard library modules only inside `core/` for analysis logic.

### 5. Runtime Behavior and Deployment

- **Execution**:
  - Entry point: `python app.py`.
  - `build_ui()` constructs the Blocks app; the `__main__` section:
    - Finds a free port starting at `7860` (up to 10 attempts).
    - Launches the app on `0.0.0.0:<port>`, with error display enabled and `share=False`.
- **Environment**:
  - Expected to run in a virtual environment with dependencies installed from `requirements.txt`.
  - Designed to run entirely offline once dependencies are installed.

### 6. Non-Functional Characteristics

- **Performance**:
  - Optimized for short to medium texts (e.g., articles, essays, documentation).
  - Single‑threaded; analysis runs synchronously on each request.
  - Uses simple regex and counting operations that are \(O(n)\) in text length.
- **Reliability**:
  - Core logic covered by unit tests, particularly edge cases for syllable counting, Flesch score clamping, and sentiment labeling.
  - UI protects against empty inputs and surfaces understandable fallback messages instead of tracebacks.
- **Security**:
  - All computation is local; no text is sent to external services by the app itself.
  - No authentication layer is implemented (assumed local/developer use).
- **Maintainability**:
  - Clear separation of concerns:
    - UI → `app.py`.
    - Business logic → `core/analyzer/` package (models, tokenization, readability, sentiment, orchestration, comparison).
    - Presentation formatting → `core/formatters.py`.
    - Tests → `tests/test_analyzer.py`.
  - Strong typing via `dataclasses` and type hints on public functions to support editor tooling and static checking.

