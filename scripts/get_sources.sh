#!/usr/bin/env bash
# Assemble primary sources into refs/. arXiv PDFs are freely redistributable;
# copyrighted books are cited-only (not hosted). Resumable.
set -u
cd "$(dirname "$0")/.."
mkdir -p refs/papers refs/texts
STELLA="$HOME/dev/stella/refs/originals"

# Local arXiv PDFs that underpin computational theology (copy if present).
for f in AutodidacticUniverse PainfulIntelligence ConsciousMachines Cap_Matching; do
  if [ -f "$STELLA/$f.pdf" ] && [ ! -f "refs/papers/$f.pdf" ]; then
    cp "$STELLA/$f.pdf" "refs/papers/$f.pdf" && echo "[copy] $f.pdf"
  fi
done

# Tamon / quantum-walk arXiv papers referenced in the transcript.
for id in 2204.04355 2211.14704 2301.07251 2508.06611 2605.04414 \
          2104.03902 2205.15409; do
  out="refs/papers/arxiv-$id.pdf"
  [ -f "$out" ] && { echo "[skip] $id"; continue; }
  if curl -fsSL --retry 2 -A "Mozilla/5.0" \
       "https://arxiv.org/pdf/$id" -o "$out" && [ -s "$out" ] \
     && head -c4 "$out" | grep -q '%PDF'; then
    echo "[ok]   arxiv $id ($(du -h "$out" | cut -f1))"
  else
    rm -f "$out"; echo "[FAIL] arxiv $id"
  fi
  sleep 1
done

# NOTE: The Cloud of Unknowing is intentionally NOT mirrored. A reliable
# public-domain plaintext (Underhill ed.) could not be sourced — Gutenberg
# #57254 is a different work entirely — so it is cited by title/tradition
# only (see site/compare/apophatic.html, references.html). Re-add here if a
# verified source is found.

echo "--- refs/ ---"; find refs -type f | sort
