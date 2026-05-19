"""labkit -- thin bridge from the Python experiment harness to the
zero-dependency Rust engine `labcore`.

Python still does everything it is good at: world generation (lab3),
spectral features / detection (numpy+scipy), statistics and figures. Rust
does the one thing Python is bad at: millions of RL training steps, across
all (seed x cell) in parallel. The split keeps the readable-lab-notebook
ethic; Rust is only the engine.
"""
import os
import subprocess
import tempfile

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_BIN = os.path.join(_HERE, "..", "..", "labcore", "target", "release",
                    "labcore")
LABCORE = os.path.abspath(_BIN)


def ensure_built():
    if os.path.exists(LABCORE):
        return LABCORE
    root = os.path.join(_HERE, "..", "..", "labcore")
    subprocess.run(["cargo", "build", "--release", "--offline"],
                    cwd=os.path.abspath(root), check=True)
    return LABCORE


def serialize_world(path, adj, cost, D, GOOD, escape, feats=None):
    """Write a world (lab3.make_world output) + optional feature matrix to
    the text format labcore parses."""
    n = len(adj)
    dim = 0 if feats is None else feats.shape[1]
    parts = [f"{n} {GOOD} {dim}"]
    for s in range(n):
        nb, cs = adj[s], cost[s]
        row = [str(len(nb))]
        for v, c in zip(nb, cs):
            row.append(str(int(v)))
            row.append(repr(float(c)))
        parts.append(" ".join(row))
    Ds = sorted(int(x) for x in D)
    parts.append("DEMON " + str(len(Ds)) + " " + " ".join(map(str, Ds)))
    parts.append(f"ESCAPE {int(escape[0])} {int(escape[1])}")
    if dim:
        flat = feats.astype(np.float64).ravel(order="C")
        parts.append(" ".join(repr(float(x)) for x in flat))
    with open(path, "w") as f:
        f.write("\n".join(parts) + "\n")


def batch_run(world_path, specs):
    """specs: list of dicts {seed, fa, vow, forgive, variety, grace,
    episodes, cap}. Returns list of (success, capture) in order. One Rust
    process; it parallelises the batch across all cores internally."""
    lines = [world_path]
    for s in specs:
        lines.append("{seed} {fa} {vow} {forgive} {variety} {grace} "
                      "{episodes} {cap}".format(
                          seed=int(s["seed"]),
                          fa=1 if s.get("fa") else 0,
                          vow=1 if s.get("vow") else 0,
                          forgive=1 if s.get("forgive") else 0,
                          variety=1 if s.get("variety") else 0,
                          grace=1 if s.get("grace") else 0,
                          episodes=int(s["episodes"]),
                          cap=int(s["cap"])))
    p = subprocess.run([ensure_built()], input="\n".join(lines),
                        capture_output=True, text=True, check=True)
    out = []
    for ln in p.stdout.strip().splitlines():
        a, b = ln.split()
        out.append((float(a), float(b)))
    return out


def run_world_grid(adj, cost, D, GOOD, escape, specs, feats=None):
    """Convenience: serialize a world to a temp file and batch-run specs."""
    with tempfile.NamedTemporaryFile("w", suffix=".world",
                                     delete=False) as tf:
        wp = tf.name
    try:
        serialize_world(wp, adj, cost, D, GOOD, escape, feats)
        return batch_run(wp, specs)
    finally:
        os.unlink(wp)
