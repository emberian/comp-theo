#!/usr/bin/env python3
"""Mirror the Computational Theology imgur albums into images/.

Parses the `postDataJSON` blob embedded in each gallery page (no API key
needed), preserves album order, and downloads full-resolution media.
"""
import html
import json
import os
import re
import sys
import time
import urllib.request

ALBUMS = [
    ("pt1", "computational-theology-xCd6wA0"),
    ("pt2", "computational-theology-pt2-eST1EhE"),
    ("pt3", "computational-theology-pt3-5FEtmF0"),
    ("pt4", "computational-theology-pt4-joslo98"),
    ("pt5", "computational-theology-pt5-le7NmNz"),
]

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "images")


def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read() if binary else r.read().decode("utf-8", "replace")


def parse_album(page_html):
    key = 'postDataJSON="'
    start = page_html.find(key)
    if start == -1:
        raise RuntimeError("postDataJSON not found")
    i = start + len(key)
    buf = []
    while i < len(page_html):
        c = page_html[i]
        if c == "\\":
            buf.append(page_html[i:i + 2])
            i += 2
            continue
        if c == '"':  # first unescaped quote ends the JS string
            break
        buf.append(c)
        i += 1
    js = "".join(buf)
    # JS-string -> real text -> JSON
    decoded = js.encode().decode("unicode_escape")
    decoded = html.unescape(decoded)
    data = json.loads(decoded)
    return data


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    manifest = []
    for part, slug in ALBUMS:
        print(f"== {part}: {slug} ==")
        page = get(f"https://imgur.com/gallery/{slug}")
        data = parse_album(page)
        media = data.get("media") or []
        print(f"   title={data.get('title')!r} image_count={data.get('image_count')} media={len(media)}")
        part_dir = os.path.join(IMG_DIR, part)
        os.makedirs(part_dir, exist_ok=True)
        for i, item in enumerate(media, 1):
            mid = item.get("id")
            ext = item.get("ext") or "png"
            url = item.get("url") or f"https://i.imgur.com/{mid}.{ext}"
            fn = f"{i:03d}_{mid}.{ext}"
            dest = os.path.join(part_dir, fn)
            rec = {
                "part": part, "index": i, "id": mid, "url": url,
                "file": os.path.relpath(dest, ROOT),
                "width": item.get("width"), "height": item.get("height"),
                "mime": item.get("mime_type"),
                "metadata": item.get("metadata", {}),
            }
            manifest.append(rec)
            if os.path.exists(dest) and os.path.getsize(dest) > 0:
                print(f"   [skip] {fn}")
                continue
            try:
                blob = get(url, binary=True)
                with open(dest, "wb") as f:
                    f.write(blob)
                print(f"   [ok]   {fn} ({len(blob)} bytes)")
            except Exception as e:
                print(f"   [FAIL] {fn}: {e}")
            time.sleep(0.3)
    with open(os.path.join(ROOT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nWrote manifest.json with {len(manifest)} entries")


if __name__ == "__main__":
    main()
