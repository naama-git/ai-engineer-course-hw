## Task Backlog – Text Analyser

This backlog is organized into **Completed**, **In Progress**, and **Planned** items. It is intended to be updated over time as the application evolves and as this documenting agent performs new changes.

### 1. Completed Work

- **Core text analysis engine**
  - Implemented `TextStats` dataclass as the single source of truth for metrics.
  - Implemented `analyze(text, top_n)` to compute:
    - Character counts (with and without spaces).
    - Word, sentence, and paragraph counts.
    - Unique word count and lexical diversity.
    - Average word length and sentence length.
    - Flesch Reading Ease score and mapped reading-level labels.
    - Estimated reading time based on ~238 wpm.
    - Rudimentary sentiment indicators via keyword lists.
    - Top‑N content word frequencies with stopword filtering.
  - Implemented `compare_texts(text_a, text_b)` to provide metric deltas between two analyses.

- **Presentation and formatting layer**
  - Implemented Markdown formatters for:
    - Summary metrics panel (`stats_to_summary_markdown`).
    - Top‑word frequency table with ASCII bars (`top_words_to_markdown`).
    - Side‑by‑side comparison table (`compare_to_markdown`).
  - Implemented human‑friendly reading time formatting.

- **Gradio UI and interaction design**
  - Built a multi‑tab Gradio Blocks interface:
    - **Analyse Text** tab with two‑column layout (input/controls vs. results).
    - **Compare Texts** tab with dual textboxes and comparison output.
    - **About** tab with feature list and architecture overview.
  - Added example texts for quick onboarding.
  - Configured `Soft` theme with custom hues, font (Inter), and small CSS tweaks.
  - Implemented Enter‑to‑submit behavior in the analysis textbox.

- **Testing and quality**
  - Added `pytest`-based unit tests for:
    - Syllable counting edge cases.
    - Flesch Reading Ease clamping behavior (0–100).
    - `analyze` behavior on empty and simple sample inputs.
    - Sentiment labels for neutral, positive, and negative texts.
    - `compare_texts` behavior (empty inputs, presence of key metrics, delta sign).
  - Ensured that core logic is test‑covered and deterministic.

- **Project documentation**
  - Authored `README.md` with:
    - Feature overview.
    - Project structure.
    - Installation, usage, and test commands.
    - Technical notes about heuristics and dependencies.
  - **Authored `.cursor` documentation set (this change)**:
    - `system_spec.md` – architecture, flow, and responsibilities.
    - `design_decisions.md` – UI/UX choices, palette, typography, and layout logic.
    - `task_backlog.md` – backlog and history of changes.
    - `technical_constraints.md` – constraints, standards, and trade‑offs.
  - **Refactored core analysis into a package**:
    - Replaced monolithic `core/analyzer.py` with a responsibility‑oriented `core/analyzer/` package:
      - `models.py` (dataclasses, especially `TextStats`).
      - `tokenization.py` (word tokenization helpers).
      - `readability.py` (syllable counting, Flesch score, reading‑level mapping).
      - `sentiment.py` (keyword lists, stopwords, and sentiment computation).
      - `analysis.py` (high‑level `analyze` orchestration).
      - `comparison.py` (comparison logic for two texts).
      - `__init__.py` (public API re‑exports: `TextStats`, `analyze`, `compare_texts`, `_count_syllables`, `_flesch_reading_ease`).
    - Ensured backwards compatibility:
      - Existing imports (`from core.analyzer import ...`) continue to work.
      - All tests in `tests/test_analyzer.py` still pass unchanged (20/20).
    - Updated `.cursor/system_spec.md` and `.cursor/technical_constraints.md` to describe the new package layout and separation of responsibilities.
  - **Reimagined UX/UI design (documentation level)**:
    - Rewrote `.cursor/design_decisions.md` to describe a more engaging, card‑based “analysis workspace”:
      - Dark‑leaning, expressive palette (indigo + amber accents) with emphasis on metric chips and analysis cards.
      - Clear separation between input workspace (left) and insights canvas (right), with cards for overview, readability, sentiment, and top words.
      - Side‑by‑side “comparison board” concept for the Compare tab and a more structured About layout.
    - Added an explicit “Design Rationale & Thought Process” section capturing:
      - Why we moved from a flat form‑style UI to a card‑based layout.
      - Why headline metrics are surfaced as chips before tables.
      - How palette and typography choices support readability and visual interest.
  - **Implemented key UX/UI changes in code**:
    - Updated `app.py` to match the documented “analysis workspace”:
      - Added a **metric chips** row (words, read time, level, sentiment) above the summary using a new helper `_chips_from_stats` and `format_reading_time`.
      - Styled summary, top words, and comparison outputs as **insight cards** via `elem_classes` and extended CSS (rounded cards, shadows, dark background, chip styling).
      - Refined microcopy for empty states and comparison instructions to align with the new workflow language.
    - Verified that all existing unit tests (`tests/test_analyzer.py`) still pass unchanged, confirming that core analysis behavior was not affected by the UI refactor.
  - **Switched results surfaces to light theming**:
    - Updated `app.py` CSS so analysis results render on **light card surfaces**:
      - Page background moved to a soft light radial gradient.
      - `.insight-card` now uses a near‑white background and a lighter shadow for a clean, readable results area.
      - Metric chips keep the indigo accent but with lighter borders and fills for consistency with the new light theme.

### 2. In Progress (Inferred)

- **Documentation & tooling integration**
  - Iteratively enrich `.cursor/*.md` files as new features or refactors are introduced, so tooling and future agents can query up‑to‑date design intent.
  - Keep backlog entries synchronized with actual changes (e.g., new metrics, UI elements, or tests).

- **UX refinement**
  - Monitor how well the current tab/column layout scales with additional metrics.
  - Adjust copy, default values, and empty‑state messages if user feedback indicates confusion.

### 3. Planned / Future Milestones

These are inferred or reasonable next steps based on the current design and typical course‑project evolution.

- **Feature Enhancements**
  - **Additional metrics**:
    - Add more readability scores (e.g., Flesch–Kincaid grade level) while staying within standard library constraints.
    - Add sentence‑level stats (e.g., distribution of sentence lengths).
  - **Export capabilities**:
    - Export summary and comparison results to Markdown or CSV files.
    - Optional “copy to clipboard” friendly versions of tables.
  - **Configurable stopwords and sentiment lexicons**:
    - Allow users to extend or override stopword lists and sentiment keyword sets via simple text inputs or configuration files.

- **Scalability and robustness**
  - Optimize analysis for longer texts (e.g., chapter‑length documents), verifying performance and memory behavior.
  - Harden sentence and paragraph detection for more varied punctuation and line‑break patterns.

- **UX & Accessibility**
  - Add inline help tooltips or collapsible “Help” sections explaining each metric in plain language.
  - Improve keyboard accessibility and screen‑reader friendliness (e.g., ensuring tables have clear headers and descriptive captions).

- **Integration & Automation**
  - Wrap the analysis engine in a simple Python API for programmatic use (e.g., other scripts or services importing `core.analyzer`).
  - Potentially integrate with LlamaIndex examples in the broader course context, while keeping this app itself dependency‑minimal.

- **Quality and Observability**
  - Extend test coverage for:
    - Edge‑case inputs (very short, very long, non‑ASCII-heavy texts).
    - Regression around formatting functions (ensuring tables stay well‑formed).
  - Add lightweight logging or debug toggles in the UI for development builds (e.g., show raw `TextStats` for inspection).

