"""lab5kit -- the Robustness Atlas backbone.

Everything a swarm slice needs to re-test a corpus claim across instruments,
all on the Rust engine (labcore):

  * three WORLD generators  : single-basin, two-basin, community(found)
  * a basin DETECTOR        : unsupervised MFPT trap-score (lab4)
  * spectral FEATURES       : graph-Laplacian embedding (lab4)
  * an AGENT registry       : myopic(2) / tabular(0) / linear-FA(1)
  * claim RUNNERS           : factorial(main effects + seed-bootstrap CI),
                              scaling-law (bare success vs reference exit τ)

A slice script imports this, runs ONE region of the atlas, writes a JSON +
a figure + a short HTML fragment. No engine edits; lab5kit is read-only
backbone (same discipline as the essay swarm).
"""
import os
import sys

import numpy as np
from scipy import linalg as sla

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab3
import labkit

ATLAS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "atlas")
os.makedirs(ATLAS_DIR, exist_ok=True)

# agent name -> engine mode + default budget
AGENTS = {
    "myopic": dict(mode=2, ep=90, cap=160, beta=3.0, feats=False),
    "tabular": dict(mode=0, ep=250, cap=150, beta=3.0, feats=False),
    "fa": dict(mode=1, ep=260, cap=150, beta=3.0, feats=True, k=16),
}
FACTORS = ["vow", "forgive", "variety", "grace"]


# ---------------------------------------------------------------------------
# World generators -> (adj[list[np.int]], cost[list[np.float]], D set,
#                      GOOD int, escape (gate, exit_to))   [lab3 format]
# ---------------------------------------------------------------------------

def world_single(N, rng):
    return lab3.make_world(N, rng)


def world_two_basin(N, rng):
    """Two planted basins of different depth, two cheap mouths from START,
    one expensive bypass. Single agent, two traps (a light 'contested'
    world). D = union; escape = the shallower basin's gate (the learnable
    way out)."""
    GOOD = N - 1
    adj = [[] for _ in range(N)]
    cost = [[] for _ in range(N)]

    def link(u, v, c):
        adj[u].append(int(v))
        cost[u].append(float(c))

    pool = list(range(2, GOOD - 3))
    rng.shuffle(pool)
    k = max(4, N // 24)
    D1 = pool[:k]
    D2 = pool[k:2 * k]
    e1, e2 = GOOD - 3, GOOD - 2
    for Dx in (D1, D2):
        for u in Dx:
            for v in rng.choice(Dx, size=min(4, len(Dx)), replace=False):
                if u != int(v):
                    link(u, int(v), rng.uniform(0.04, 0.10))
    link(0, D1[0], 0.15)            # cheap mouth -> shallow basin
    link(0, D2[0], 0.18)            # cheap mouth -> deep basin
    link(0, e1, 3.0)               # expensive bypass first hop
    link(D1[-1], e1, 9.0)          # shallow toll
    link(D2[-1], e1, 26.0)         # deep toll
    link(e1, e2, 0.5)
    link(e2, GOOD, 0.5)
    for u in range(1, N - 1):
        if not adj[u]:
            link(u, e1, rng.uniform(3.0, 6.0))
    adj = [np.array(a, np.int32) for a in adj]
    cost = [np.array(c, np.float64) for c in cost]
    adj[GOOD] = np.array([GOOD], np.int32)
    cost[GOOD] = np.array([0.0])
    D = set(int(x) for x in D1 + D2)
    return adj, cost, D, GOOD, (int(D1[-1]), e1)


def world_community(N, rng, blocks=4):
    """Stochastic-block world; one block is a cheap-internal community with
    only costly edges leaving it -- an EMERGENT basin (no planted label
    used by mechanisms; see detect_basin). START / GOOD in other blocks."""
    GOOD = N - 1
    blk = rng.integers(0, blocks, size=N)
    blk[0] = 0
    blk[GOOD] = blocks - 1
    basin_blk = 1
    adj = [[] for _ in range(N)]
    cost = [[] for _ in range(N)]

    def link(u, v, c):
        adj[u].append(int(v))
        cost[u].append(float(c))

    for u in range(N):
        if u == GOOD:
            continue
        for v in range(N):
            if u == v or v == 0:
                continue
            same = blk[u] == blk[v]
            p = 0.06 if same else 0.012
            if rng.random() < p:
                if blk[u] == basin_blk and blk[v] == basin_blk:
                    c = rng.uniform(0.05, 0.12)        # cheap inside basin
                elif blk[u] == basin_blk:
                    c = rng.uniform(8.0, 16.0)         # costly to leave
                else:
                    c = rng.uniform(0.8, 2.0)
                link(u, v, c)
    # a cheap lure START -> basin, an expensive bypass START -> elsewhere
    binds = [i for i in range(1, N - 1) if blk[i] == basin_blk]
    others = [i for i in range(1, N - 1) if blk[i] not in (basin_blk,)]
    if not binds or not others:
        return world_single(N, rng)
    link(0, int(rng.choice(binds)), 0.2)
    link(0, int(rng.choice(others)), 3.0)
    # ensure GOOD reachable: chain through 'others'
    ch = [0] + list(rng.choice(others, size=min(6, len(others)),
                               replace=False)) + [GOOD]
    for a, b in zip(ch, ch[1:]):
        link(int(a), int(b), rng.uniform(1.0, 2.0))
    for u in range(1, N - 1):
        if not adj[u]:
            link(u, GOOD, rng.uniform(3.0, 6.0))
    adj = [np.array(a, np.int32) for a in adj]
    cost = [np.array(c, np.float64) for c in cost]
    adj[GOOD] = np.array([GOOD], np.int32)
    cost[GOOD] = np.array([0.0])
    Dtrue = set(int(i) for i in binds)
    gate = max(binds, key=lambda u: len(adj[u]))
    exit_to = int(rng.choice(others))
    return adj, cost, Dtrue, GOOD, (gate, exit_to)


WORLDS = {"single": world_single, "two_basin": world_two_basin,
          "community": world_community}


# ---------------------------------------------------------------------------
# Detector / features / reference exit time  (ports of lab4)
# ---------------------------------------------------------------------------

def detect_basin(adj, cost, GOOD, N, beta=3.0):
    P = np.zeros((N, N))
    P[GOOD, GOOD] = 1.0
    for s in range(N):
        if s == GOOD or len(adj[s]) == 0:
            P[s, GOOD] = 1.0
            continue
        w = np.exp(-beta * cost[s])
        for v, ww in zip(adj[s], w):
            P[s, int(v)] += ww
        P[s] /= P[s].sum()
    T = [i for i in range(N) if i != GOOD]
    try:
        h = sla.solve(np.eye(len(T)) - P[np.ix_(T, T)], np.ones(len(T)))
    except sla.LinAlgError:
        return set(), np.zeros(N)
    sc = np.zeros(N)
    sc[T] = h
    thr = np.quantile(sc[T], 0.90)
    return set(int(i) for i in T if sc[i] >= thr), sc


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / max(len(a | b), 1)


def spectral_features(adj, N, k):
    A = np.zeros((N, N))
    for u in range(N):
        for v in adj[u]:
            A[u, int(v)] = A[int(v), u] = 1.0
    d = A.sum(1)
    d[d == 0] = 1.0
    L = np.eye(N) - (A / np.sqrt(d)[:, None] / np.sqrt(d)[None, :])
    _, V = np.linalg.eigh(L)
    F = V[:, 1:k + 1]
    F = (F - F.mean(0)) / (F.std(0) + 1e-9)
    return np.hstack([F, np.ones((N, 1))])


def reference_exit_time(adj, cost, GOOD, N, beta=3.0):
    P = np.zeros((N, N))
    P[GOOD, GOOD] = 1.0
    for s in range(N):
        if s == GOOD or len(adj[s]) == 0:
            P[s, GOOD] = 1.0
            continue
        w = np.exp(-beta * cost[s])
        for v, ww in zip(adj[s], w):
            P[s, int(v)] += ww
        P[s] /= P[s].sum()
    T = [i for i in range(N) if i != GOOD]
    try:
        t = sla.solve(np.eye(len(T)) - P[np.ix_(T, T)], np.ones(len(T)))
    except sla.LinAlgError:
        return np.inf
    return float(t[0]) if 0 in T else np.inf


# ---------------------------------------------------------------------------
# Engine grid + claim runners
# ---------------------------------------------------------------------------

def _agent_world(world_fn, agent, N, rng, use_detected=True):
    adj, cost, Dtrue, GOOD, esc = world_fn(N, rng)
    spec = AGENTS[agent]
    feats = (spectral_features(adj, N, spec["k"])
             if spec["feats"] else None)
    Dhat, _ = detect_basin(adj, cost, GOOD, N)
    Duse = Dhat if (use_detected and Dhat) else Dtrue
    return adj, cost, Duse, Dtrue, GOOD, esc, feats


def grid(world_fn, agent, N, seeds, flag_combos, world_seed=0,
         use_detected=True):
    """flag_combos: list of dict(vow,forgive,variety,grace). Returns
    {combo_tuple: [success per seed]} and detector Jaccard."""
    spec = AGENTS[agent]
    rng = np.random.default_rng(1000 + world_seed)
    adj, cost, Duse, Dtrue, GOOD, esc, feats = _agent_world(
        world_fn, agent, N, rng, use_detected)
    jac = jaccard(Duse, Dtrue)
    specs, key = [], []
    for sd in seeds:
        for fc in flag_combos:
            specs.append(dict(seed=4000 + sd, mode=spec["mode"],
                              episodes=spec["ep"], cap=spec["cap"],
                              beta=spec["beta"], **fc))
            key.append((tuple(fc.get(f, 0) for f in FACTORS), sd))
    res = labkit.run_world_grid(adj, cost, Duse, GOOD, esc, specs,
                                feats=feats)
    out = {}
    for (combo, sd), (s, c) in zip(key, res):
        out.setdefault(combo, []).append(s)
    return out, jac


def full_factorial(world_fn, agent, N, seeds, world_seed=0):
    import itertools
    combos = [dict(zip(FACTORS, c))
              for c in itertools.product([0, 1], repeat=4)]
    return grid(world_fn, agent, N, seeds, combos, world_seed)


def main_effects(table):
    """table {combo->[succ]} -> {factor: (effect, lo, hi)} seed-bootstrap."""
    import itertools
    cells = list(itertools.product([0, 1], repeat=4))
    nseed = len(next(iter(table.values())))
    eff = {}
    for i, f in enumerate(FACTORS):
        per = []
        for sdi in range(nseed):
            on = np.mean([table[c][sdi] for c in cells if c[i] == 1])
            off = np.mean([table[c][sdi] for c in cells if c[i] == 0])
            per.append(on - off)
        per = np.array(per)
        rng = np.random.default_rng(7 + i)
        bs = [rng.choice(per, len(per), replace=True).mean()
              for _ in range(3000)]
        eff[f] = (float(per.mean()), float(np.percentile(bs, 2.5)),
                  float(np.percentile(bs, 97.5)))
    return eff


def scaling_law(world_fn, agent, Ns, seeds):
    """bare-agent success vs reference exit time tau; returns rows and
    Spearman(B/tau, success)."""
    spec = AGENTS[agent]
    B = spec["ep"] * spec["cap"]
    rows = []
    for sd in seeds:
        for N in Ns:
            rng = np.random.default_rng(400 + sd)
            adj, cost, Dtrue, GOOD, esc = world_fn(N, rng)
            tau = reference_exit_time(adj, cost, GOOD, N)
            feats = (spectral_features(adj, N, spec["k"])
                     if spec["feats"] else None)
            r = labkit.run_world_grid(
                adj, cost, Dtrue, GOOD, esc,
                [dict(seed=9000 + sd, mode=spec["mode"],
                      episodes=spec["ep"], cap=spec["cap"],
                      beta=spec["beta"])], feats=feats)[0]
            rows.append((N, tau, B / max(tau, 1e-9), r[0]))
    ratio = np.array([x[2] for x in rows])
    sc = np.array([x[3] for x in rows])
    rk = lambda z: np.argsort(np.argsort(z))
    rho = (float(np.corrcoef(rk(ratio), rk(sc))[0, 1])
           if len(rows) > 2 else 0.0)
    return rows, rho
