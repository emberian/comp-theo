# Poster encoding and originals

All 210 posters remain in Git at their original dimensions. The working images
are lossy WebP quality 97 copies, selected after comparison in Preview on
2026-11-13. Transcriptions, source URLs and source metadata are retained.

The corpus changed from 562,584,362 bytes (536.5 MiB) of PNGs to
155,539,796 bytes (148.3 MiB) of WebPs: 72.4% smaller.
Alpha channels are unchanged. This is a lossy color conversion, not a claim of
pixel identity. Existing gallery thumbnails were retained.

## Encoding

libwebp cwebp 1.6.0, without resizing:

```sh
cwebp -q 97 -m 6 -sharp_yuv -alpha_q 100 -metadata all original.png -o poster.webp
```

`scripts/image_encoding.py` contains the shared encoder arguments. Install
libwebp (for example `brew install webp`) before using `scripts/fetch_albums.py`.
The fetcher skips hash-verified existing images and encodes new downloads
once from original source bytes. Do not recompress the WebP copies.

`manifest.json` keeps `url` and `metadata` for the original source, `file` and
`mime` for the local WebP, and `sha256` for the local file. Each `source` object
records the original file path, MIME type, byte size and SHA256; the archived
capture also includes its original Git blob ID. Source hashes identify the
saved bytes, not a promise that Imgur will serve the same bytes forever.

## Original recovery

The exact original PNGs and complete earlier history are preserved in verified
Git bundles, independently backed up locally and on hbox:

- `~/repo-archives/2026-11-13/pdf-offload/comp-theo.bundle` (before PDF cleanup)
- `~/repo-archives/2026-11-13/comp-theo-q97/before-webp.bundle` (before image conversion)

The second bundle SHA256 is `fd85a4866f68fe9d3df2cdf520766eb9cfe23c7eee0a2185f3158e3473c97d5b`.
To recover an original without changing this checkout, clone either bundle
as a separate mirror and extract the `source.git_blob` from its manifest entry:

```sh
git clone --mirror ~/repo-archives/2026-11-13/comp-theo-q97/before-webp.bundle /tmp/comp-theo-originals.git
git --git-dir=/tmp/comp-theo-originals.git cat-file blob SOURCE_GIT_BLOB > /path/to/original.png
```

Verify the resulting file against `source.sha256`. Original Imgur URLs are
also retained for convenience; the bundles protect against link rot.

## History

Both main and dev were rewritten to replace historical poster PNG blobs with
these same WebP copies; unrelated binary figures, thumbnails and authored
content were retained. `.images/history-map.tsv.xz` maps the pre-WebP commits
to the rewritten commits. `.papers/history-map.tsv.xz` has been composed with
this conversion so it still maps pre-PDF-cleanup commits to current history.
New integration commits sit above the mapped historical tips.

Existing local worktrees were not modified. Use a fresh clone and transfer
local work as reviewed patches; merging old history would restore the bulk.
