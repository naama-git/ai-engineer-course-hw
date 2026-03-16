# Internal Architecture Documentation

As the lead developer, I designed this system to be modular, ensuring a strict separation between the User Interface (UI) and the core analytical logic.

## 🏗 System Overview
The project follows a "Functional Core, Imperative Shell" philosophy. All complex calculations are contained within pure functions in the `core/` package, while the Gradio `app.py` acts as the delivery mechanism.

### Project Structure
- `app.py`: The entry point. It manages the Gradio Blocks layout, state, and event listeners.
- `core/analyzer/`: The "Engine". It is sub-divided into modules for tokenization, readability, and sentiment to keep the codebase maintainable.
- `core/formatters.py`: A translation layer. It takes raw data objects (`TextStats`) and converts them into formatted Markdown for the UI.
- `tests/`: A comprehensive test suite using `pytest` to validate the NLP heuristics.

## 🧠 Thought Processes & Design Patterns
1. **Data Transfer Objects (DTO)**: I utilized Python's `@dataclass` in `models.py` to create the `TextStats` object. This ensures that the data passed between the analyzer and the UI is structured and type-hinted.
2. **Heuristic-Based NLP**: To keep the app "lightweight" and "fully local," I intentionally avoided heavy libraries like NLTK or SpaCy. Instead, I implemented regex-based tokenization and vowel-group syllable counting.
3. **Decoupled Formatting**: By separating Markdown generation from the analysis logic, we can easily change the UI (e.g., to a CLI or a Web API) without touching the mathematical core.

## ⚖️ Key Decisions
- **Port Management**: In `app.py`, I implemented a `find_free_port` helper. During development, I found that Gradio sometimes hangs if the default port 7860 is occupied, so this ensures a smooth launch experience.
- **Syllable Counting**: Since perfect syllable counting is phonetically complex, I used a vowel-group heuristic with a "silent-e" correction. It provides ~90% accuracy, which is sufficient for Flesch Reading Ease scores.
- **Stop Word Filtering**: In the word frequency analysis, I implemented a custom `_STOP_WORDS` list to ensure the "Top Words" section provides meaningful content rather than just "the," "and," and "is."