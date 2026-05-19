# Workground charter (for contributing agents)

The **Workground** is not the polished site. It is the AI's open scratchpad:
working notes, conjectures, audits, tangents, half-formed extensions. It may
disagree with the essays, with the corpus, and with the other Workground
pieces. It is explicitly **non-authoritative and exploratory**.

## Voice

First-person analytic ("I take X to mean…", "this step worries me…").
Candid. Mark uncertainty explicitly. Speculation is allowed and encouraged —
but label it as speculation; never fabricate sources, quotes, or results.
Think on the page; show the reasoning, not just the verdict.

## Hard constraints

- Only create your single assigned file under `site/workground/`. Touch
  nothing else (no assets/, no other sections, no repo files).
- Follow the subdirectory template in `site/CONTENT_SPEC.md` exactly
  (`../assets/style.css`, `<body data-root="../">`, `../assets/app.js`,
  content in `<article class="prose">`). Add `<p class="kicker">WORKGROUND
  · NON-AUTHORITATIVE</p>` above the `<h1>`.
- Respect the standing correction: the early quantum-walk / Tamon material
  and the "ordered creation" subseries are **exploratory motivators**, not a
  load-bearing foundation of computational theology.
- Ground claims honestly. Real material: `transcript/conversation.full.md`
  (grep), `parsed/pt*/*.md`, `synthesis/*.md`,
  `~/dev/stella/refs/extracted/{AutodidacticUniverse,PainfulIntelligence,
  ConsciousMachines}/doc.md`. Cite specifics (e.g. "pt3 · panel 014").
- Cross-link: end with a short "see also" linking 1–2 sibling Workground
  pages by their known filenames (listed in index.html).

## Register

This is a lab notebook, not a sermon and not a debunking. The interesting
mode is *serious play*: take the project seriously enough to push on it hard.
