"""The full-resolution poster encoding approved after visual review."""
import subprocess
import tempfile
from pathlib import Path

CWEBP_ARGS = ["-q", "97", "-m", "6", "-sharp_yuv", "-alpha_q", "100", "-metadata", "all"]


def encode_webp(original):
    """Encode original source bytes once; never recompress an existing WebP."""
    with tempfile.TemporaryDirectory(prefix="comp-theo-image-") as directory:
        source, target = Path(directory) / "source", Path(directory) / "encoded.webp"
        source.write_bytes(original)
        subprocess.run(["cwebp", "-quiet", *CWEBP_ARGS, str(source), "-o", str(target)],
                       check=True, capture_output=True)
        return target.read_bytes()
