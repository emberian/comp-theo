#!/usr/bin/env bash
# Parallel codex pass over ONLY the 137 images Claude transcribed, into
# parsed_codex/ (side-by-side with parsed/). Resumable across quota windows:
# images whose codex .md already exists+non-empty are skipped.
# Usage: scripts/parse_codex_137.sh [PARALLELISM]   (default 5)
set -u
cd "$(dirname "$0")/.."
ROOT="$PWD"
PAR="${1:-5}"
MODEL="${CODEX_MODEL:-}"
mkdir -p parsed_codex logs/codex137

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
  local img="$1" out="$2" margs=()
  [ -n "${MODEL:-}" ] && margs=(-m "$MODEL")
  printf '%s' "$PROMPT" | timeout 180 codex exec --sandbox read-only \
      "${margs[@]}" -i "$img" >"$out.tmp" \
      2>"$ROOT/logs/codex137/$(basename "$out").err"
  if [ -s "$out.tmp" ] && grep -q '## Transcription' "$out.tmp" \
     && ! grep -qi 'usage limit' "$out.tmp"; then
    mv "$out.tmp" "$out"; echo "[ok]   $out"
  else
    rm -f "$out.tmp"
    if grep -qi 'usage limit' "$ROOT/logs/codex137/$(basename "$out").err"; then
      echo "[QUOTA] $img"
    else
      echo "[FAIL] $img"
    fi
  fi
}
export -f parse_one
export PROMPT MODEL ROOT

# Worklist = images whose synthesis/provenance.json value is the Claude pass.
python3 - "$ROOT" > /tmp/codex137.tsv <<'PY'
import json, os, sys
root = sys.argv[1]
prov = json.load(open(os.path.join(root, "synthesis/provenance.json")))
man = {f"{r['part']}/{r['index']:03d}_{r['id']}.md": r
       for r in json.load(open(os.path.join(root, "manifest.json")))}
for key, eng in sorted(prov.items()):
    if "claude" not in eng:
        continue
    r = man[key]
    img = os.path.join(root, r["file"])
    out = os.path.join(root, "parsed_codex", key)
    if os.path.exists(out) and os.path.getsize(out) > 0:
        continue
    os.makedirs(os.path.dirname(out), exist_ok=True)
    print(f"{img}\t{out}")
PY

n=$(grep -c . /tmp/codex137.tsv || true)
echo "Worklist: $n / 137 remaining, parallelism=$PAR, model=${MODEL:-default}"
[ "$n" -eq 0 ] && { echo "All 137 codex transcriptions complete."; exit 0; }

while IFS=$'\t' read -r img out; do
  [ -z "$img" ] && continue
  while [ "$(jobs -rp | wc -l)" -ge "$PAR" ]; do wait -n 2>/dev/null || sleep 1; done
  parse_one "$img" "$out" &
done < /tmp/codex137.tsv
wait

done_n=$(find parsed_codex -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
q=$(grep -c QUOTA /dev/stdin 2>/dev/null || true)
echo "Pass ended. parsed_codex/*.md: $done_n / 137"
