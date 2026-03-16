"""
chat_ui.py
──────────
ממשק Gradio Chat עבור ה-RAG pipeline.

מייצא:
    build_gradio_app(run_query_fn, rebuild_engine_fn) -> gr.Blocks

פרמטרים:
    run_query_fn      – callable(question: str) -> (answer: str, sources_md: str)
    rebuild_engine_fn – callable(top_k: int, cutoff: float) -> None
"""

import gradio as gr

# ─────────────────────────────────────────────────────────────────────────────
# עיצוב
# ─────────────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Heebo:wght@300;400;500&display=swap');

/* ── משתני עיצוב ── */
:root {
    --navy:      #0d1b2a;
    --navy-mid:  #132336;
    --navy-soft: #1c3350;
    --amber:     #e8a020;
    --amber-dim: #c4861a;
    --cream:     #f5f0e8;
    --muted:     #8fa3b8;
    --border:    rgba(232,160,32,0.18);
    --radius:    10px;
}

/* ── בסיס ── */
body, .gradio-container {
    background: var(--navy) !important;
    font-family: 'Heebo', 'Noto Sans Hebrew', sans-serif;
    direction: rtl;
    color: var(--cream);
}

/* ── כותרת ── */
#rag-header {
    padding: 28px 32px 12px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 4px;
}
#rag-header h1 {
    font-family: 'Playfair Display', 'Heebo', serif;
    font-size: 2rem;
    font-weight: 900;
    color: var(--amber);
    letter-spacing: -0.5px;
    margin: 0 0 4px;
}
#rag-header p {
    font-size: 0.85rem;
    color: var(--muted);
    font-weight: 300;
    margin: 0;
}

/* ── חלון הצ'אט ── */
#chatbot-wrap .wrap {
    background: var(--navy-mid) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--cream) !important;
}
/* בועות משתמש */
#chatbot-wrap .message.user {
    # background: var(--navy-soft) !important;
    border: 1px solid var(--border) !important;
    color: var(--cream) !important;
    border-radius: 12px 4px 12px 12px !important;
}
/* בועות מודל */
#chatbot-wrap .message.bot {
    # background: linear-gradient(135deg, #1a3a5c 0%, var(--navy-mid) 100%) !important;
    border: 1px solid var(--border) !important;
    color: var(--cream) !important;
    border-radius: 4px 12px 12px 12px !important;
}

/* ── תיבת קלט ── */
#msg-input textarea {
    background: var(--navy-mid) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--cream) !important;
    font-family: 'Heebo', sans-serif;
    font-size: 0.95rem;
    padding: 10px 14px;
    resize: none;
    transition: border-color 0.2s;
}
#msg-input textarea:focus {
    border-color: var(--amber) !important;
    outline: none;
    box-shadow: 0 0 0 2px rgba(232,160,32,0.15);
}
#msg-input textarea::placeholder { color: var(--muted); }

/* ── כפתורים ── */
#send-btn {
    background: var(--amber) !important;
    color: var(--navy) !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: var(--radius) !important;
    transition: background 0.2s, transform 0.1s !important;
    font-family: 'Heebo', sans-serif !important;
}
#send-btn:hover  { background: var(--amber-dim) !important; transform: translateY(-1px); }
#send-btn:active { transform: translateY(0); }

#clear-btn {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--muted) !important;
    border-radius: var(--radius) !important;
    font-family: 'Heebo', sans-serif !important;
    transition: border-color 0.2s, color 0.2s !important;
}
#clear-btn:hover { border-color: var(--amber) !important; color: var(--amber) !important; }

/* ── עמודת מקורות ── */
#sources-panel {
    background: var(--navy-mid);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px;
    height: 100%;
    min-height: 540px;
}
#sources-panel h3 {
    font-family: 'Playfair Display', serif;
    color: var(--amber);
    font-size: 1rem;
    margin: 0 0 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
}
#sources-panel p, #sources-panel li, #sources-panel blockquote {
    color: var(--muted);
    font-size: 0.82rem;
    line-height: 1.55;
}
#sources-panel strong { color: var(--cream); }
#sources-panel blockquote {
    border-right: 3px solid var(--amber);
    border-left: none;
    padding: 4px 10px;
    margin: 4px 0 10px;
    background: rgba(232,160,32,0.05);
    border-radius: 0 4px 4px 0;
}

/* ── Accordion הגדרות ── */
.gr-accordion {
    background: var(--navy-soft) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    margin-top: 12px;
}
.gr-accordion summary {
    color: var(--muted) !important;
    font-size: 0.82rem !important;
    font-family: 'Heebo', sans-serif !important;
}
.gr-accordion summary:hover { color: var(--amber) !important; }

/* ── Sliders ── */
.gr-slider input[type=range]::-webkit-slider-thumb { background: var(--amber) !important; }
.gr-slider input[type=range]::-moz-range-thumb     { background: var(--amber) !important; }

/* ── כפתור החל ── */
#apply-btn {
    background: var(--navy-soft) !important;
    border: 1px solid var(--border) !important;
    color: var(--muted) !important;
    font-family: 'Heebo', sans-serif !important;
    border-radius: var(--radius) !important;
    font-size: 0.82rem !important;
    transition: all 0.2s !important;
}
#apply-btn:hover { border-color: var(--amber) !important; color: var(--amber) !important; }

/* ── misc ── */
footer { display: none !important; }
.gap { gap: 10px !important; }
"""

# ─────────────────────────────────────────────────────────────────────────────
# בנאי הממשק
# ─────────────────────────────────────────────────────────────────────────────
def build_gradio_app(run_query_fn, rebuild_engine_fn) -> gr.Blocks:

    # ── callbacks ──────────────────────────────────────────────────────────
    def chat_fn(message: str, history: list):
        if not message.strip():
            return history, "", ""

        answer, sources_md = run_query_fn(message)

        history = history or []
        history.append({"role": "user",      "content": message})
        history.append({"role": "assistant", "content": answer})
        return history, "", sources_md

    def apply_settings(top_k, cutoff):
        rebuild_engine_fn(int(top_k), float(cutoff))
        return gr.update(value="✅ הגדרות עודכנו.")

    def clear_chat():
        return [], "","_The resources will appear here after a query._"

    # ── layout ────────────────────────────────────────────────────────────
    with gr.Blocks(css=CSS, title="RAG Chat · LlamaIndex") as demo:

        # כותרת
        gr.HTML("""
            <div id="rag-header">
                <h1>⬡ RAG Chat</h1>
                <p>LlamaIndex · Pinecone · Gradio 6 — Ask questions about your documents</p>
            </div>
        """)

        with gr.Row(equal_height=True):

            # ── עמודת צ'אט ──────────────────────────────────────────────
            with gr.Column(scale=3, elem_id="chat-col"):
                chatbot = gr.Chatbot(
                    height=480,
                    show_label=False,
                    elem_id="chatbot-wrap",
                    placeholder="<b>RAG Chat</b><br> Ask something to start the conversation!",
                )

                with gr.Row():
                    msg_box = gr.Textbox(
                        placeholder="Type a question and press Enter or send...",
                        show_label=False,
                        lines=1,
                        scale=5,
                        rtl=True,
                        elem_id="msg-input",
                    )
                    send_btn = gr.Button("שלח ➤", scale=1, variant="primary",
                                         elem_id="send-btn")

                clear_btn = gr.Button("🗑️ clear session", size="sm", elem_id="clear-btn")

            # ── עמודת מקורות ────────────────────────────────────────────
            with gr.Column(scale=1):
                with gr.Group(elem_id="sources-panel"):
                    gr.HTML("<h3>📄 Resources</h3>")
                    sources_box = gr.Markdown(
                        value="_Here will appear the sources after a query._",
                    )

                with gr.Accordion("⚙️ Query Settings ", open=False):
                    top_k_slider = gr.Slider(
                        minimum=1, maximum=15, value=5, step=1,
                        label=" Results number (top_k)",
                    )
                    cutoff_slider = gr.Slider(
                        minimum=0.0, maximum=1.0, value=0.7, step=0.05,
                        label="Minimum similarity threshold",
                    )
                    apply_btn = gr.Button("Apply Settings", size="sm",
                                          elem_id="apply-btn")

        # ── wiring ────────────────────────────────────────────────────────
        send_btn.click(
            chat_fn,
            inputs=[msg_box, chatbot],
            outputs=[chatbot, msg_box, sources_box],
        )
        msg_box.submit(
            chat_fn,
            inputs=[msg_box, chatbot],
            outputs=[chatbot, msg_box, sources_box],
        )
        clear_btn.click(clear_chat, outputs=[chatbot, msg_box, sources_box])
        apply_btn.click(
            apply_settings,
            inputs=[top_k_slider, cutoff_slider],
            outputs=[sources_box],
        )

    return demo