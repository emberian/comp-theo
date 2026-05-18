#!/usr/bin/env bash
# Parse every mirrored image with `codex exec` (ChatGPT vision).
# Resumable: skips images whose .md already exists and is non-empty.
# Usage: scripts/parse_images.sh [PARALLELISM]   (default 5)
set -u
cd "$(dirname "$0")/.."
ROOT="$PWD"
PAR="${1:-5}"
MODEL="${CODEX_MODEL:-}"            # optional: export CODEX_MODEL=gpt-5.5
mkdir -p parsed logs

read -r -d '' PROMPT <<'EOF'
This image is one poster/panel from a multi-part visual essay series titled
"computational theology" (parts 1-5). Do TWO things, in this exact format:

## Transcription
Every piece of text in the image, verbatim, preserving reading order,
headings, numbered panels, formulas (use LaTeX-ish plaintext), captions,
page markers, and footnotes. Do not paraphrase or summarize. If text is
unreadable, write [illegible].

## Visual
2-4 sentences: layout, diagrams, imagery, color/typographic style, and any
figures or symbols that carry meaning beyond the text.

No preamble, no closing commentary. Output only those two sections.
EOF

parse_one() {
  local img="$1" out="$2"
  local margs=()
  [ -n "${MODEL:-}" ] && margs=(-m "$MODEL")
  printf '%s' "$PROMPT" | timeout 180 codex exec --sandbox read-only \
      "${margs[@]}" -i "$img" >"$out.tmp" 2>"$ROOT/logs/$(basename "$out").err"
  if [ -s "$out.tmp" ] && grep -q '## Transcription' "$out.tmp"; then
    mv "$out.tmp" "$out"
    echo "[ok]   $out"
  else
    rm -f "$out.tmp"
    echo "[FAIL] $img (see logs/$(basename "$out").err)"
  fi
}
export -f parse_one
export PROMPT MODEL ROOT

# Build worklist from manifest order, skipping completed outputs.
python3 - "$ROOT" <<'PY' > /tmp/ct_worklist.txt
import json, os, sys
root = sys.argv[1]
for r in json.load(open(os.path.join(root, "manifest.json"))):
    img = os.path.join(root, r["file"])
    out = os.path.join(root, "parsed", r["part"],
                       "%03d_%s.md" % (r["index"], r["id"]))
    if os.path.exists(out) and os.path.getsize(out) > 0:
        continue
    os.makedirs(os.path.dirname(out), exist_ok=True)
    print(f"{img}\t{out}")
PY

n=$(wc -l < /tmp/ct_worklist.txt | tr -d ' ')
echo "Worklist: $n images, parallelism=$PAR, model=${MODEL:-default}"
[ "$n" -eq 0 ] && { echo "Nothing to do."; exit 0; }

while IFS=$'\t' read -r img out; do
  while [ "$(jobs -rp | wc -l)" -ge "$PAR" ]; do wait -n 2>/dev/null || sleep 1; done
  parse_one "$img" "$out" &
done < /tmp/ct_worklist.txt
wait

done_n=$(find parsed -name '*.md' | wc -l | tr -d ' ')
echo "Done. parsed/*.md total: $done_n / 210"
