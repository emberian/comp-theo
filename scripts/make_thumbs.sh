#!/usr/bin/env bash
# Downscaled gallery thumbnails (longest side 480px, JPEG ~q60) via sips.
# Mirrors images/<part>/<f>.png -> site/thumbs/<part>/<f>.jpg. Resumable.
set -eu
cd "$(dirname "$0")/.."
n=0; made=0
while IFS= read -r src; do
  rel="${src#images/}"
  dst="site/thumbs/${rel%.png}.jpg"
  n=$((n+1))
  [ -f "$dst" ] && continue
  mkdir -p "$(dirname "$dst")"
  sips -s format jpeg -s formatOptions 60 -Z 480 "$src" \
       --out "$dst" >/dev/null 2>&1 && made=$((made+1))
done < <(find images -name '*.png' | sort)
echo "thumbs: $made new / $n total -> site/thumbs"
du -sh site/thumbs 2>/dev/null || true
