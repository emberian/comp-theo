# Content page spec (for content authors)

Plain HTML/JS site, no build step. Shared CSS + nav/footer are injected by
`assets/app.js`. Content authors only add **standalone HTML pages** in their
own directory; never edit `assets/`, `index.html`, `gallery.html`, the
glossary/map pages, or another author's directory.

## Page template (subdirectory pages — essays/, lessons/, compare/)

```html
<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PAGE TITLE — Computational Theology</title>
<link rel="stylesheet" href="../assets/style.css">
</head><body data-root="../">
<main><article class="prose">

  <p class="kicker">SECTION LABEL</p>
  <h1>Page title</h1>
  <p class="lede">One-sentence framing.</p>

  ...content: h2/h3, p, ul/ol, blockquote, <div class="note">caveats</div>...
  Link to a panel: <a href="../gallery.html">poster browser</a>.

</article></main>
<script src="../assets/app.js"></script>
</body></html>
```

The index.html of each section should use `<ul class="cards">` linking its
pages (see root `index.html` for the pattern).

## Voice (non-negotiable)

Scholarly and skeptical. Expound the framework accurately, then interrogate
it: situate moves against named existing thinkers, separate **load-bearing**
claims from **decorative** ones, name where a mathematical analogy is doing
real work vs. supplying atmosphere. Cite the corpus's own "analogy, not
theorem" guardrail and hold it to that standard. No hype, no devotional
register, no inventing sources. Hedge claims about what the math "proves."

## Grounding sources (read before writing)

- `synthesis/GLOSSARY.md`, `synthesis/MAP.md` — the spine and vocabulary.
- `transcript/conversation.full.md` — primary origin dialogue (1 MB; grep
  for terms, do not read whole).
- `parsed/pt*/<n>.md` — individual panel transcriptions (cite as "pt3 · 014").
- For external comparisons, reference real, verifiable works (Spencer-Brown,
  *Laws of Form*; Whitehead, *Process and Reality*; Tegmark / Smolin et al.,
  *The Autodidactic Universe*, arXiv:2104.03902; Hyvärinen, *Painful
  Intelligence*, arXiv:2205.15409; Bennett, *Conscious Machines* thesis;
  apophatic / negative theology; Madhyamaka; etc.). Quote sparingly.
