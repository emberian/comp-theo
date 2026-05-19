#!/usr/bin/env python3
"""Generate site/data/*.json from manifest + parsed transcriptions.

No external deps. Includes the codex pass as an alternate transcription
when present (side-by-side comparison in the gallery).
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DATA = os.path.join(ROOT, "site", "data")
PAGE = re.compile(
    r"^\s*(\d+\s*(/|of)\s*\d+|\d{1,2}|[ivxlcdm]+|page \d+)\s*$", re.I)
BOIL = re.compile(
    r"^[•\s]*(computational\s+theology(\s+series)?|series)[•\s]*$", re.I)


def split_md(path):
    if not os.path.exists(path):
        return None, None
    t = open(path, encoding="utf-8", errors="replace").read()
    body = t.split("## Transcription", 1)[-1]
    trans, _, vis = body.partition("## Visual")
    return trans.strip(), vis.strip()


def title_of(trans):
    lines = [l.strip(" \t#·—-") for l in (trans or "").splitlines()]
    lines = [l for l in lines
             if l and not PAGE.match(l) and not BOIL.match(l)
             and not re.match(r"^[\W_]+$", l)]
    buf = ""
    for l in lines[:6]:
        buf = (buf + (" " if buf else "") + l).strip()
        if len(buf) >= 18 or buf.endswith((".", "?", "!")):
            break
    return re.sub(r"\s+", " ", buf)[:95] or "(untitled)"


def main():
    os.makedirs(SITE_DATA, exist_ok=True)
    man = json.load(open(os.path.join(ROOT, "manifest.json")))
    prov = {}
    pj = os.path.join(ROOT, "synthesis", "provenance.json")
    if os.path.exists(pj):
        prov = json.load(open(pj))

    posters, parts = [], {}
    for r in man:
        key = f"{r['part']}/{r['index']:03d}_{r['id']}.md"
        tr, vi = split_md(os.path.join(ROOT, "parsed", key))
        ctr, cvi = split_md(os.path.join(ROOT, "parsed_codex", key))
        rec = {
            "part": r["part"], "index": r["index"], "id": r["id"],
            "img": r["file"],
            "thumb": "thumbs/" + r["file"][len("images/"):].rsplit(".", 1)[0]
            + ".jpg",
            "w": r.get("width"), "h": r.get("height"),
            "title": title_of(tr),
            "transcription": tr or "", "visual": vi or "",
            "engine": prov.get(key, "unknown"),
            "codex": ({"transcription": ctr or "", "visual": cvi or ""}
                      if ctr else None),
        }
        posters.append(rec)
        parts.setdefault(r["part"], 0)
        parts[r["part"]] += 1

    json.dump({"posters": posters,
               "parts": [{"part": k, "count": v}
                         for k, v in sorted(parts.items())],
               "codex_count": sum(1 for p in posters if p["codex"])},
              open(os.path.join(SITE_DATA, "posters.json"), "w"),
              ensure_ascii=False)

    # Ship the synthesis markdown for client-side rendering.
    for name in ("GLOSSARY.md", "MAP.md"):
        src = os.path.join(ROOT, "synthesis", name)
        if os.path.exists(src):
            open(os.path.join(SITE_DATA, name), "w").write(
                open(src, encoding="utf-8").read())

    print(f"posters.json: {len(posters)} posters, "
          f"{sum(1 for p in posters if p['codex'])} with codex variant")


if __name__ == "__main__":
    main()
