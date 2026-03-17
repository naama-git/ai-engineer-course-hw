## Design Decisions – UI & UX

### 1. Overall UX Philosophy (Revised)

- **Workspace-first, insight-second**:
  - The primary experience is a “text analysis workspace” rather than a traditional form.
  - The input area stays visually anchored on the left, while the right side behaves like a dynamic **insights canvas** composed of cards (overview, readability, sentiment, top words).
- **Progressive disclosure of detail**:
  - High‑level metrics (e.g., word count, reading time, sentiment label) are surfaced as compact “metric chips” above the main tables.
  - Richer tables and explanations sit below, so beginners are not overwhelmed while power users still get depth.
- **Playful but professional**:
  - Emojis and accent colors add personality, while alignment, spacing, and typography stay disciplined.
  - Visual hierarchy is used to guide the eye: primary actions and key metrics are more vivid; secondary text is muted.

### 2. Visual Identity (Theme, Color, Typography) – More Expressive Variant

- **Base Theme**
  - Still uses Gradio `Soft` as the foundation for compatibility and sensible defaults.
  - The theme configuration in `app.py` is treated as a **neutral base**, with additional customization layered via CSS.

- **Color Palette (Approximate Hex Values)**
  - **Core neutrals**
    - Background: `#0F172A` → deep slate/indigo hybrid for a “night‑mode by default” feeling.
    - Surface cards: `#020617` / `#111827` with subtle borders (`#1F2937`) to create contrast between panels.
  - **Primary accent (Electric Indigo)**
    - Main accent: `#6366F1` – used for primary buttons, active tab underline, and metric chip highlights.
    - Hover states: `#818CF8` with slightly brighter shadows.
  - **Secondary accent (Amber)**
    - Emphasis accent: `#F59E0B` – for highlighting reading difficulty levels or drawing attention to key callouts.
  - **Semantic cues**
    - Positive sentiment accents (if used): `#22C55E`.
    - Negative sentiment accents (if used): `#EF4444`.
    - Neutral sentiment relies on text and emoji, not color alone, to remain accessible.

- **Typography**
  - **Primary font**: Inter (via `gr.themes.GoogleFont("Inter")`) remains, but the hierarchy is more structured:
    - Titles (H1/H2): heavier weight, slightly increased letter‑spacing.
    - Metric chips: semi‑bold, uppercase or small caps style for quick scanning (implemented via CSS, not semantic casing in strings).
  - **Font sizing strategy**:
    - Base body size designed for comfortable reading on desktop (≈ 16px).
    - Tab titles and primary buttons slightly larger to act as anchors.

### 3. Layout and Information Architecture – Card-Based Workspace

- **Top-Level Layout**
  - `gr.Blocks` root with:
    - **Hero header** at the top:
      - Title, short descriptor, and a subtle tagline explaining the purpose (readability, frequency, sentiment).
      - Header sits on a slightly darker gradient background to visually separate it from the work area.
    - `gr.Tabs` below the header separate the main flows:
      - **Analyse Text** – default workspace.
      - **Compare Texts** – dual‑panel comparison view.
      - **About** – in‑app documentation.

- **Tab 1 – “📄 Analyse Text” (Workspace)**
  - **Left Pane – Input & Controls**
    - A tall `Textbox` framed as a “document editor”:
      - Comfortable line count and max height, with consistent padding.
      - Clear placeholder copy that invites pasting or typing text.
    - Control row under the textbox:
      - `Top N words` slider with tooltip‑style helper text explaining what it does.
      - Primary “Analyse” button; secondary “Clear” button aligned to the right for a more tool‑like feel.
    - Sample texts:
      - Examples are visually separated in a **“Quick Start” strip** below controls (e.g., a pill‑shaped container) so they look optional and playful rather than part of the main form.
  - **Right Pane – Insights Canvas**
    - Top row: **metric chips**
      - Compact summary of key metrics (word count, estimated reading time, reading level, sentiment).
      - Each chip is styled as a pill with subtle background and border, visually clickable even if they are informational only.
    - Main column: **stacked analysis cards**
      - **Overview card**:
        - Table of counts (characters, words, sentences, paragraphs, unique words).
        - Visual emphasis on word count and unique words (e.g., stronger accent or bolding).
      - **Readability card**:
        - Flesch score and reading level with richer copy, potentially using amber to call out more complex texts.
      - **Sentiment card**:
        - Emoji label plus counts of positive/negative signals.
      - **Top Words card**:
        - Existing ASCII bar chart table, but wrapped in a visually distinct card with its own sub‑heading.
    - Cards maintain consistent padding, rounded corners, and subtle drop‑shadows to feel like modular blocks users can visually parse at a glance.

- **Tab 2 – “⚖️ Compare Texts” (Side-by-Side Board)**
  - **Inputs**
    - Two textboxes remain side by side but are visually grouped in a **“Text A / Text B” board** with labels and subtle colored borders:
      - Text A: neutral border.
      - Text B: slightly tinted border to differentiate.
  - **Actions**
    - The compare button is centered below the two textboxes, visually associated with both.
  - **Results**
    - The comparison markdown is treated as a **single wide card**:
      - The table remains, but a short explanatory sentence above it clarifies how to read deltas (e.g., “Positive Δ means Text B is higher than Text A”).

- **Tab 3 – “ℹ️ About”**
  - Content remains informational but is formatted into:
    - A top summary card (what the tool is and who it’s for).
    - Two columns on larger screens for “Features” and “Architecture”.

### 4. Micro-Interactions and Feedback (Reimagined)

- **Empty states**
  - Still provide friendly markdown guidance, but copy is written as **short onboarding prompts**:
    - Analyse tab: “Paste some text on the left and hit Analyse to see metrics here.”
    - Compare tab: “Fill both texts above and click Compare to see deltas.”
- **Hover and focus**
  - Buttons, tabs, and chips use subtle scale/shadow changes on hover/focus (via CSS) to give a tactile feel.
- **Responsive behavior (conceptual)**
  - On narrower screens:
    - Insights cards stack under the input instead of sitting side‑by‑side.
    - Metric chips wrap onto multiple lines rather than truncating.

### 5. Iconography and Copy (Sharpened)

- **Icons**
  - Emojis are kept but used more systematically:
    - Header: single 🔍 icon near the product name.
    - Tabs: 📄 / ⚖️ / ℹ️ as before, but considered part of the brand language.
    - Section headings inside cards: matching emojis (📊, 📚, 🎭, 🔤) prefixed to their titles.
  - Avoids introducing additional icon fonts or libraries.
- **Copy**
  - Goal is to be:
    - **Actionable** (“Paste text…”, “Compare two drafts…”).
    - **Reassuring** (“All processing runs locally on your machine.”).
  - Microcopy is tuned to align with the “workspace” mental model: “workspace”, “insights”, “cards”, “metrics”.

### 6. CSS and Theming Tweaks (Target Design)

- The CSS block attached to `ui.launch` is treated as the main lever for expressing the new visual language:
  - `.tab-nav button { font-weight: 600; }` remains as a baseline improvement for tab readability.
  - `.metric-card`, `.insight-card`, `.metric-chip` (conceptual classes):
    - Rounded corners (`border-radius: 16px`).
    - Soft shadow and border for card‑like appearance.
    - Consistent padding and vertical spacing for rhythm.
  - Global background:
    - Dark gradient behind the header and a slightly lighter tone behind the workspace to create depth.
  - Footer remains hidden (`footer { display: none !important; }`) to keep focus on the tool.

### 7. Accessibility and Usability Considerations (Revisited)

- **Keyboard and focus**
  - Continue to leverage Gradio’s built‑in focus handling.
  - The more card‑like layout is designed so the **logical reading and tabbing order** remains top‑to‑bottom, left‑to‑right.
- **Color and contrast**
  - Dark‑themed palette is chosen with sufficient contrast between text and background.
  - Semantic information is always encoded in **text + emoji**; color is supportive, not required.
- **Cognitive load**
  - Breaking metrics into cards and chips reduces the feeling of a big unstructured table.
  - Progressive disclosure ensures beginners can stop at “headline” metrics while advanced users scroll into tables.

### 8. Design Rationale & Thought Process

- **Why move to a card-based workspace?**
  - The original design was clear but visually flat and “form‑like”.
  - A card‑based layout matches how users mentally group metrics (overview vs. readability vs. sentiment vs. frequency) and makes it easier to scan.
- **Why a darker, more expressive palette?**
  - Text‑heavy tools benefit from a dark‑leaning background: it reduces glare and makes colored highlights and metric chips stand out.
  - The indigo/amber pairing conveys a “data + creativity” vibe that fits a text‑analysis tool used by writers and developers.
- **Why metric chips above tables?**
  - Most users care about a few key answers first: “How long?”, “How complex?”, “What’s the tone?”.
  - Chips provide those answers in a compact, memorable way before the user dives into full tables.
- **Why keep emojis and tables?**
  - Emojis provide instant semantic cues with essentially zero performance cost.
  - Markdown tables are robust across themes and renderers and keep the tool lightweight while still feeling data‑rich.

