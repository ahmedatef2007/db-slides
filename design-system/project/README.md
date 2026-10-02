# Database Course

The visual language of the *Database Fundamentals* course decks (Lessons 1–5: Introduction, ERD, ERD-to-tables mapping, SQL, Normalization). It is a calm, technical look for teaching: warm paper backgrounds, a deep navy ink, one orange accent that means "pay attention", one blue that means "SQL / correct practice", and dark code blocks.

## Content fundamentals

- **One idea per slide.** A slide title names the topic in a few words ("Weak entity types", "TRUNCATE vs DELETE"). An eyebrow above it names the section ("ERD · Attributes").
- **Show, then tell.** Prefer a small worked example (an ERD fragment, a table before/after, a SQL query plus its result) over a list of definitions.
- **Every section ends the same way:** *Key takeaways* → *Practice* (exercises tagged **Core**, **Stretch** or **Challenge**; all optional) → *Study more* (books, courses and free practice sites with links).
- **Corrections are silent on the slide and explicit in the notes.** When a slide fixes something from the original course material, its speaker notes start with `Fixed:`.
- SQL in prose is written in UPPERCASE keywords (`SELECT`, `GROUP BY`) and colored `blue`. Table and column names stay as written in the schema.
- Tone: direct, second person, short sentences. No emoji.

## Visual foundations

- **Canvas** 1920×1080, margins `space-xl` (128px), footer row pinned at `space-l` (64px) from the bottom: lesson name left, slide number right, `caption` in `muted`.
- **Backgrounds:** `paper` for content, `paper-2` for recap/practice/resources, `ink` for covers and section dividers. The single statement slide per lesson uses `accent-fill` with `ink` text.
- **Type:** `display` (Space Grotesk) for headings, `sans` (IBM Plex Sans) for text, `mono` (JetBrains Mono) for code. Scale: hero 96 · title 64 · card-title 36 · body 30 · small 26 · caption/eyebrow 24. No text under 24px.
- **Cards:** `card` surface, 1px `line` border, `radius-m`, padding `space-m`. No shadows, no left-border accent cards.
- **Code blocks:** `code-bg`, `radius-m`, `code` style; keywords `code-keyword`, literals `code-string`, comments `code-comment`.
- **Tables:** header row in `ink` on `paper-2`, body rows on `card`, 26px text.
- **ERD diagrams (Chen notation):** entities = `ink` stroke on `card` rectangles; relationships = diamonds in `accent-tint` with `accent` stroke; attributes = ellipses in `blue-tint` with `blue` stroke. Weak entity / identifying relationship = double stroke; key attribute = underlined; multivalued = double ellipse; derived = dashed ellipse; total participation = double line.
- **Color never carries meaning alone:** a "good" vs "bad" example also says so in words (*Correct*, *Avoid*).

## Iconography

No icon set of its own: decks use the slide runtime's built-in line icons (Database, Key, Lock, Users, Search, Code, Lightbulb, Warning, Check) in `ink` or `accent`, at 48px or larger, always next to a word.

## Tokens

See `tokens.json`: 20 colors (one light theme), 9 text styles in 3 families, 5 spacing steps, 3 radii. Fonts are Google Fonts (Space Grotesk, IBM Plex Sans, JetBrains Mono); no font files are bundled.
