"""
app.py
------
Gradio UI for the Text Analysis Tool.
Strictly handles user interaction and delegates all computation to core/.
"""

import gradio as gr
import sys
import os

# Ensure the project root is on the path so `core` is importable
sys.path.insert(0, os.path.dirname(__file__))

from core import (
    analyze,
    compare_texts,
    stats_to_summary_markdown,
    top_words_to_markdown,
    compare_to_markdown,
)
from core.formatters import format_reading_time

def _chips_from_stats(stats) -> str:
    """Build a compact 'metric chips' row from TextStats."""
    rt = format_reading_time(stats.estimated_reading_time_sec)
    return f"""
<div class="metric-chips-row">
  <span class="metric-chip">📝 <strong>Words</strong>: {stats.word_count:,}</span>
  <span class="metric-chip">⏱ <strong>Read Time</strong>: {rt}</span>
  <span class="metric-chip">📚 <strong>Level</strong>: {stats.reading_level}</span>
  <span class="metric-chip">🎭 {stats.sentiment_label}</span>
</div>
"""


# ---------------------------------------------------------------------------
# UI callback functions
# ---------------------------------------------------------------------------

def run_analysis(text: str, top_n: int) -> tuple[str, str, str]:
    """
    Gradio callback: analyse a single text.

    Returns
    -------
    (chips_markdown, summary_markdown, top_words_markdown)
    """
    if not text or not text.strip():
        empty = "_Paste or type some text on the left, then click **Analyse** to see insights here._"
        return "", empty, ""

    stats = analyze(text, top_n=int(top_n))
    if stats is None:
        return "", "_Could not analyse the text._", ""

    chips = _chips_from_stats(stats)
    return chips, stats_to_summary_markdown(stats), top_words_to_markdown(stats)


def run_comparison(text_a: str, text_b: str) -> str:
    """
    Gradio callback: compare two texts.

    Returns
    -------
    comparison_markdown
    """
    if not text_a.strip() or not text_b.strip():
        return "_Fill both texts above, then click **Compare** to see how they differ._"

    comparison = compare_texts(text_a, text_b)
    return compare_to_markdown(comparison)


# ---------------------------------------------------------------------------
# Sample texts
# ---------------------------------------------------------------------------

_SAMPLE_SIMPLE = (
    "The cat sat on the mat. It was a big, fat cat. "
    "The mat was red and soft. The cat liked the mat a lot. "
    "Every day the cat came back to sit on the mat. It was happy there."
)

_SAMPLE_COMPLEX = (
    "The epistemological implications of post-structuralist discourse present "
    "considerable challenges to conventional hermeneutic frameworks. "
    "Deconstructionist methodologies, while intellectually stimulating, "
    "often obfuscate rather than illuminate the underlying phenomenological "
    "substrate of linguistic praxis. Consequently, practitioners must "
    "exercise judicious discernment when navigating these multifaceted "
    "conceptual landscapes."
)

# ---------------------------------------------------------------------------
# Build and launch the Gradio interface
# ---------------------------------------------------------------------------

def build_ui() -> gr.Blocks:
    """Construct the full Gradio Blocks application."""

    with gr.Blocks(title="Text Analyser") as app:

        # ── Header ──────────────────────────────────────────────────────────
        gr.Markdown(
            """
            # 🔍 Text Analyser
            > A focused workspace for readability, word frequency, sentiment, and side‑by‑side comparison — all processed locally.
            """,
        )

        # ── Tabs ─────────────────────────────────────────────────────────────
        with gr.Tabs():

            # ── Tab 1: Single Text Analysis ──────────────────────────────────
            with gr.TabItem("📄 Analyse Text"):
                with gr.Row():
                    with gr.Column(scale=2):
                        input_text = gr.Textbox(
                            label="Input Text",
                            placeholder="Paste or type your text here…",
                            lines=12,
                            max_lines=30,
                        )
                        with gr.Row():
                            top_n_slider = gr.Slider(
                                minimum=5,
                                maximum=25,
                                value=10,
                                step=1,
                                label="Top N words to show",
                            )
                        with gr.Row():
                            analyse_btn = gr.Button(
                                "🔍 Analyse", variant="primary", size="lg"
                            )
                            clear_btn = gr.ClearButton(
                                [input_text], value="🗑 Clear"
                            )

                        gr.Examples(
                            examples=[
                                [_SAMPLE_SIMPLE, 10],
                                [_SAMPLE_COMPLEX, 10],
                            ],
                            inputs=[input_text, top_n_slider],
                            label="📝 Quick Start Samples",
                        )

                    with gr.Column(scale=3):
                        chips_out = gr.Markdown(
                            value="",
                            elem_classes=["metric-chips-container"],
                        )
                        summary_out = gr.Markdown(
                            value="_Paste some text on the left and hit **Analyse** to see metrics here._",
                            label="Summary",
                            elem_classes=["insight-card"],
                        )
                        top_words_out = gr.Markdown(
                            value="",
                            label="Top Words",
                            elem_classes=["insight-card"],
                        )

                analyse_btn.click(
                    fn=run_analysis,
                    inputs=[input_text, top_n_slider],
                    outputs=[chips_out, summary_out, top_words_out],
                )
                # Also trigger on pressing Enter inside the textbox
                input_text.submit(
                    fn=run_analysis,
                    inputs=[input_text, top_n_slider],
                    outputs=[chips_out, summary_out, top_words_out],
                )

            # ── Tab 2: Text Comparison ────────────────────────────────────────
            with gr.TabItem("⚖️ Compare Texts"):
                gr.Markdown(
                    "Enter two texts below, then click **Compare** to see how their key metrics differ."
                )
                with gr.Row():
                    text_a = gr.Textbox(
                        label="Text A",
                        placeholder="Paste first text…",
                        lines=10,
                    )
                    text_b = gr.Textbox(
                        label="Text B",
                        placeholder="Paste second text…",
                        lines=10,
                    )

                compare_btn = gr.Button(
                    "⚖️ Compare", variant="primary", size="lg"
                )
                comparison_out = gr.Markdown(
                    value="_Fill both texts above and click **Compare** to see side‑by‑side metrics here._",
                    elem_classes=["insight-card"],
                )

                gr.Examples(
                    examples=[[_SAMPLE_SIMPLE, _SAMPLE_COMPLEX]],
                    inputs=[text_a, text_b],
                    label="📝 Load Sample Comparison",
                )

                compare_btn.click(
                    fn=run_comparison,
                    inputs=[text_a, text_b],
                    outputs=[comparison_out],
                )

            # ── Tab 3: About ──────────────────────────────────────────────────
            with gr.TabItem("ℹ️ About"):
                gr.Markdown(
                    """
                    ## About This Tool

                    **Text Analyser** is a lightweight, fully local text-analysis application
                    built with Python 3 and [Gradio](https://gradio.app).

                    ### Features
                    - **Basic counts** — characters, words, sentences, paragraphs
                    - **Readability** — Flesch Reading Ease score + plain-English grade label
                    - **Estimated reading time** — based on an average adult reading pace (238 wpm)
                    - **Lexical diversity** — ratio of unique to total words
                    - **Top-word frequency** — content words with ASCII bar chart
                    - **Sentiment indicators** — positive / negative signal words
                    - **Side-by-side comparison** — compare any two texts on key metrics

                    ### Architecture
                    ```
                    text_analyzer/
                    ├── app.py              ← Gradio UI (this file)
                    ├── core/
                    │   ├── analyzer/       ← All NLP & statistical logic (package)
                    │   └── formatters.py   ← Markdown rendering helpers
                    └── tests/
                        └── test_analyzer.py
                    ```

                    ### Notes
                    - Sentiment detection uses a simple keyword word-list (not ML).
                    - Syllable counting uses vowel-group heuristics for speed.
                    - No external NLP libraries required — pure Python stdlib only.
                    """
                )

    return app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import socket

    def find_free_port(start: int = 7860, max_tries: int = 10) -> int:
        for i in range(max_tries):
            port = start + i
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("0.0.0.0", port))
                    return port
            except OSError:
                continue
        return start

    ui = build_ui()
    port = find_free_port(7860)
    if port != 7860:
        print(f"Port 7860 in use, using {port} instead.")
    ui.launch(
        server_name="0.0.0.0",
        server_port=port,
        show_error=True,
        share=False,
        theme=gr.themes.Soft(
            primary_hue="indigo",
            secondary_hue="slate",
            font=[gr.themes.GoogleFont("Inter"), "sans-serif"],
        ),
        css="""
            body { background: radial-gradient(circle at top, #eef2ff 0, #f8fafc 45%, #ffffff 100%); }
            .tab-nav button { font-weight: 600; }

            .metric-chips-container { margin-bottom: 0.75rem; }
            .metric-chips-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
                margin-bottom: 0.5rem;
            }
            .metric-chip {
                display: inline-flex;
                align-items: center;
                padding: 0.35rem 0.75rem;
                border-radius: 9999px;
                background: rgba(99, 102, 241, 0.10);
                border: 1px solid rgba(99, 102, 241, 0.25);
                font-size: 0.9rem;
            }

            .insight-card {
                border-radius: 16px !important;
                border: 1px solid rgba(148, 163, 184, 0.55);
                box-shadow: 0 14px 30px rgba(2, 6, 23, 0.10);
                padding: 0.75rem 1rem;
                background: rgba(255, 255, 255, 0.98);
            }

            footer { display: none !important; }
        """,
    )
