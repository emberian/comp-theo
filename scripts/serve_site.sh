#!/usr/bin/env bash
# Local preview: regenerate data, expose images under site/, serve.
set -eu
cd "$(dirname "$0")/.."
python3 scripts/build_site_data.py
[ -e site/images ] || ln -s ../images site/images
echo "http://localhost:8765  (Ctrl-C to stop)"
cd site && exec python3 -m http.server 8765
