# Computational Theology — Archive & Archeology

**Live site:** https://emberian.github.io/comp-theo/ — poster browser
(all 210 panels, both transcription passes side-by-side), critical essays,
guided lessons, philosophy comparisons, glossary, and poster map.

A mirror and reconstruction of the *Computational Theology* visual-essay
series (5 imgur albums, 210 posters), plus the dialogue transcript that
produced it.

## Why

The source albums are private imgur galleries and prone to link rot. This
repo preserves the images, machine-transcribes every panel, and reconstructs
the underlying intellectual framework from the primary material.

## Layout

```
images/ptN/NNN_<id>.png   mirrored posters, album order preserved
manifest.json             ordered index: part, index, imgur id, url, dims
parsed/ptN/NNN_<id>.md    per-image transcription + visual description
scripts/fetch_albums.py   re-runnable mirror (parses embedded imgur JSON)
scripts/parse_images.sh   re-runnable codex/ChatGPT vision pass (resumable)
synthesis/MAP.md          one line per poster (210), album order
synthesis/GLOSSARY.md     core vocabulary, grouped, with provenance
synthesis/provenance.json which engine parsed each image (codex vs claude)
transcript/conversation.full.md  complete originating ChatGPT dialogue
                                 (prompts, replies, hidden reasoning,
                                  tool calls — full fidelity)
logs/                     run + error logs
```

## Source albums

| Part | Slug | Count |
|------|------|-------|
| pt1 | computational-theology-xCd6wA0 | 50 |
| pt2 | computational-theology-pt2-eST1EhE | 50 |
| pt3 | computational-theology-pt3-5FEtmF0 | 50 |
| pt4 | computational-theology-pt4-joslo98 | 50 |
| pt5 | computational-theology-pt5-le7NmNz | 10 |

Author account: `UrPissMissedThePot` (imgur id 155100497). Albums created
2026-05-15, platform iOS, privacy: private. Captured 2026-05-18.

## Parse provenance

Transcriptions were produced by two engines: **73** via `codex exec`
(ChatGPT GPT-5.x vision) before the ChatGPT plan usage limit was hit, and
the remaining **137** via Claude (Opus 4.7) vision when the quota blocked
codex for hours. Per-file mapping in `synthesis/provenance.json`. Format and
prompt were identical across both.

## Site

Plain HTML/JS (no build framework) under `site/`, deployed to GitHub Pages
by `.github/workflows/pages.yml` (assembles `site/` + mirrored `images/`,
regenerating `site/data/` via `scripts/build_site_data.py`). Local preview:
`scripts/serve_site.sh` → http://localhost:8765. Interpretive essays/lessons/
comparisons are a skeptical outside reading, not the original author's voice.

## Reproduce

```sh
python3 scripts/fetch_albums.py        # mirror images + manifest
scripts/parse_images.sh 5              # parse via `codex exec` vision
                                       # (needs `codex` logged in; resumable)
CODEX_MODEL=gpt-5.5 scripts/parse_images.sh 5   # to pin a model
```
