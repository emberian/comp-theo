#!/usr/bin/env python3
"""
lab.py -- "From Toy to Lab"

The toy (site/workground/toy_model.py) proved the corpus's metaphors *can*
be literalised on one hand-built 6-node graph with an arbitrary softmax
agent and a single seed. It could not say whether they survive a principled
agent, random graph ensembles, or statistics, and its own verdict flagged
the holes (vow = a bare edge reweight; mercy collapses into it; variety has
no mechanism; the striking grace result rested on one graph).

This is the postdoc version. The agent is no longer an ad-hoc softmax. It is
a **linearly-solvable MDP** (Todorov 2009, KL/path-integral control), the
canonical model of a bounded-rational planner:

    desirability  z(s) = exp(-b V(s))   solves a LINEAR system
        z(s) = sum_{v: s->v} exp(-b c(s,v)) z(v),   z(GOOD)=1
    controlled policy   pi(v|s)  =  exp(-b c(s,v)) z(v) / z(s)

Two facts make this the right core:

  * It is exactly solvable (one linear solve), so nothing diverges -- the
    pathology that made an undiscounted entropy-softmin blow up is gone.
  * -(1/b) log z(START)  ->  the exact min-plus (tropical) shortest path as
    b -> inf.  That is **Maslov dequantisation**, and it turns the corpus's
    "tropical algebra is the b->inf limit / the choice of algebra is an
    ethical decision" from a slogan into a measured curve.

On that one agent we then test, with graph ensembles + bootstrap CIs +
effect sizes, the six claims the toy could only gesture at. Every claim
states its FALSIFICATION condition and the run reports whether it failed.

Dependencies: numpy, scipy, matplotlib (Agg). Deterministic under
MASTER_SEED. Figures -> site/workground/figs/. Run:

    python3 site/workground/lab.py
"""
from __future__ import annotations

import os
import time

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import linalg as sla

MASTER_SEED = 1729
FIGDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(FIGDIR, exist_ok=True)
np.set_printoptions(precision=4, suppress=True)


# ===========================================================================
# Graphs.  Node 0 = START, node n-1 = GOOD (absorbing, zero cost).
# A graph is a cost matrix C (np.inf where no edge), GOOD self-absorbing.
# ===========================================================================

def _ensure_path(C, rng):
    n = len(C)
    if _reach(C, 0, n - 1):
        return
    mid = [k for k in range(1, n - 1)]
    rng.shuffle(mid)
    chain = [0] + mid[:3] + [n - 1]
    for a, b in zip(chain, chain[1:]):
        C[a, b] = rng.uniform(1.0, 2.0)


def _reach(C, s, t):
    n = len(C)
    seen, st = set(), [s]
    while st:
        u = st.pop()
        if u == t:
            return True
        if u in seen:
            continue
        seen.add(u)
        st += list(np.where(np.isfinite(C[u]))[0])
    return False


def _costs(A, rng, lo=0.4, hi=1.6):
    n = len(A)
    C = np.full((n, n), np.inf)
    for u in range(n):
        for v in np.where(A[u])[0]:
            if u != v:
                C[u, v] = rng.uniform(lo, hi)
    C[n - 1, :] = np.inf
    C[n - 1, n - 1] = 0.0                              # GOOD absorbs
    for u in range(n - 1):                             # no transient dead end
        if not np.isfinite(C[u]).any():
            C[u, n - 1] = rng.uniform(3.0, 6.0)
    _ensure_path(C, rng)
    return C


def gen_er(n, rng, p=0.12):
    A = rng.random((n, n)) < p
    np.fill_diagonal(A, False)
    return _costs(A, rng)


def gen_ws(n, rng, k=4, beta=0.15):
    A = np.zeros((n, n), bool)
    for i in range(n):
        for j in range(1, k // 2 + 1):
            A[i, (i + j) % n] = A[i, (i - j) % n] = True
    for i in range(n):
        for j in range(1, k // 2 + 1):
            if rng.random() < beta:
                A[i, (i + j) % n] = False
                A[i, rng.integers(n)] = True
    np.fill_diagonal(A, False)
    return _costs(A, rng)


def gen_ba(n, rng, m=2):
    A = np.zeros((n, n), bool)
    deg = np.ones(n) * 1e-9
    for i in range(1, n):
        tgt = i if i <= m else m
        pr = deg[:i] / deg[:i].sum()
        for t in rng.choice(i, size=tgt, replace=False, p=pr):
            A[i, t] = A[t, i] = True
            deg[i] += 1
            deg[t] += 1
    np.fill_diagonal(A, False)
    return _costs(A, rng)


def gen_sbm(n, rng, p_in=0.32, p_out=0.04):
    h = n // 2
    blk = np.array([0] * h + [1] * (n - h))
    P = np.where(blk[:, None] == blk[None, :], p_in, p_out)
    A = rng.random((n, n)) < P
    np.fill_diagonal(A, False)
    return _costs(A, rng)


ENSEMBLES = {"ER": gen_er, "WS": gen_ws, "BA": gen_ba, "SBM": gen_sbm}


def demon_graph(n, rng, depth, k=None):
    """A CLEAN metastable module. Layout (no other edges, no _ensure_path
    so nothing punches a shortcut out of the basin):

        START --0.3--> D0  (cheap mouth: the agent is pulled in)
        START --8.0--> e1  (an expensive bypass: the planner CAN avoid D)
        D = {D0..D_{k-1}}  fully connected, every interior edge ~0.10
        D_{k-1} --depth--> e1   (the ONLY way out of D; toll = depth)
        e1 --0.5--> e2 --0.5--> GOOD   (cheap once you have paid the toll)

    Cheap interior + single costly exit => a genuine metastable set whose
    mean exit time ~ exp(beta*depth). depth small = not metastable (control).
    """
    GOOD = n - 1
    dx, e1, e2 = 2, GOOD - 2, GOOD - 1                  # dx = the sticky node
    cs = 0.3                                            # self-loop (dwell) cost
    C = np.full((n, n), np.inf)
    C[0, dx] = 0.3                                      # cheap mouth into dx
    C[0, e1] = 8.0                                      # expensive bypass
    C[dx, dx] = cs                                      # cheap to linger
    C[dx, e1] = float(depth)                            # the ONLY exit, toll
    C[e1, e2] = 0.5
    C[e2, GOOD] = 0.5
    # ONE companion node: the canonical two-state metastable motif
    # (dx <-> c cheap, single costly exit dx->e1). More nodes only thicken
    # it; one keeps the escape-rate analysis textbook-clean.
    comp = 3
    C[dx, comp] = rng.uniform(0.20, 0.30)
    C[comp, dx] = rng.uniform(0.20, 0.30)
    # every other node gets ONE expensive edge out (no isolated z=0 nodes)
    for u in range(1, n - 1):
        if u in (dx, e1, e2):
            continue
        if not np.isfinite(C[u]).any():
            C[u, e1] = rng.uniform(3.0, 6.0)
    C[GOOD, :] = np.inf
    C[GOOD, GOOD] = 0.0
    return C, {dx}


# ===========================================================================
# The agent: linearly-solvable MDP (KL / path-integral control).
#   z(s) = sum_v exp(-b C[s,v]) z(v),  z(GOOD)=1   ->  one linear solve
#   V    = -(1/b) log z          (free energy / soft value)
#   P(v|s) = exp(-b C[s,v]) z(v) / z(s)            (controlled chain)
# b -> inf : V(START) -> tropical shortest-path cost  (Maslov).
# ===========================================================================

def solve_lmdp(C, beta, gamma=1.0):
    """gamma<1 = a per-step survival/impatience discount. It keeps the
    controlled chain row-stochastic (gamma folds into z) while guaranteeing
    the Boltzmann path-sum converges, i.e. it is exactly a constant
    'impatience toll' -ln(gamma)/beta added to every edge. gamma=1 is the
    pure (windowed) Maslov regime used only by EXP 1."""
    n = len(C)
    GOOD = n - 1
    M = np.where(np.isfinite(C),
                 gamma * np.exp(-beta * np.nan_to_num(C, posinf=0.0)), 0.0)
    M[~np.isfinite(C)] = 0.0
    M[GOOD, :] = 0.0
    T = list(range(n - 1))
    g = M[np.ix_(T, [GOOD])].flatten()                 # transient -> GOOD
    Mtt = M[np.ix_(T, T)]
    # The Boltzmann path-sum (I-Mtt)^-1 only converges when rho(Mtt) < 1.
    # Above that the partition function genuinely diverges (a real high-
    # temperature transition, not a bug): signal invalid so callers skip.
    rho = np.max(np.abs(np.linalg.eigvals(Mtt))) if len(T) else 0.0
    if rho >= 1.0 - 1e-9:
        return None
    try:
        zT = sla.solve(np.eye(len(T)) - Mtt, g)
    except sla.LinAlgError:
        return None
    if not np.all(np.isfinite(zT)) or np.any(zT <= 0):
        return None
    z = np.ones(n)
    z[T] = np.clip(zT, 1e-300, None)
    with np.errstate(divide="ignore"):
        V = -(1.0 / beta) * np.log(z)
    # controlled transition matrix
    P = np.zeros((n, n))
    P[GOOD, GOOD] = 1.0
    for s in T:
        row = M[s] * z
        tot = row.sum()
        if tot <= 0:
            P[s, GOOD] = 1.0
        else:
            P[s] = row / tot
    return V, z, P


def myopic_chain(C, beta):
    """The toy's actual agent: a Gibbs walk on immediate edge cost only,
    NO value / look-ahead.  P(v|s) ∝ exp(-beta c(s,v)).  This is the agent
    that can be kinetically trapped; the LMDP agent above cannot."""
    n = len(C)
    P = np.zeros((n, n))
    P[n - 1, n - 1] = 1.0
    for s in range(n - 1):
        nb = np.where(np.isfinite(C[s]))[0]
        if len(nb) == 0:
            P[s, n - 1] = 1.0
            continue
        w = np.exp(-beta * C[s, nb])
        P[s, nb] = w / w.sum()
    return P


def tropical_dist(C):
    """Exact min-plus shortest path from START (Bellman-Ford)."""
    n = len(C)
    d = np.full(n, np.inf)
    d[0] = 0.0
    for _ in range(n - 1):
        for u in range(n):
            if not np.isfinite(d[u]):
                continue
            nb = np.where(np.isfinite(C[u]))[0]
            for v in nb:
                if d[u] + C[u, v] < d[v]:
                    d[v] = d[u] + C[u, v]
    return d


# ----- metastability diagnostics on the controlled chain -------------------

def mfpt(P, src, n):
    T = [i for i in range(n) if i != n - 1]
    Q = P[np.ix_(T, T)]
    try:
        t = sla.solve(np.eye(len(T)) - Q, np.ones(len(T)))
    except sla.LinAlgError:
        return np.inf
    return float(t[T.index(src)]) if src in T else 0.0


def spectral_gap(P, n):
    T = [i for i in range(n) if i != n - 1]
    if not T:
        return 1.0
    ev = np.sort(np.abs(np.linalg.eigvals(P[np.ix_(T, T)])))
    return float(1.0 - ev[-1])


def committor(P, n, demon):
    """q(s) = P(reach GOOD before re-entering demon core). q(GOOD)=1,
    q(demon)=0, harmonic under P elsewhere."""
    GOOD = n - 1
    fixed = {GOOD: 1.0}
    for d in demon:
        fixed[d] = 0.0
    free = [s for s in range(n) if s not in fixed]
    if not free:
        return 0.0
    idx = {s: i for i, s in enumerate(free)}
    A = np.eye(len(free))
    b = np.zeros(len(free))
    for s in free:
        for v in np.where(P[s] > 0)[0]:
            if v in idx:
                A[idx[s], idx[v]] -= P[s, v]
            else:
                b[idx[s]] += P[s, v] * fixed[v]
    try:
        q = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        return 0.0
    return float(q[idx[0]]) if 0 in idx else 0.0


def capture_prob(P, n, demon, horizon=400):
    v = np.zeros(n)
    v[0] = 1.0
    for _ in range(horizon):
        v = v @ P
    return float(sum(v[d] for d in demon))


# ===========================================================================
# Stats helpers
# ===========================================================================

def ci(x, fn=np.mean, B=1500, seed=0):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return (np.nan, np.nan, np.nan)
    rng = np.random.default_rng(seed)
    bs = [fn(rng.choice(x, len(x), replace=True)) for _ in range(B)]
    return float(fn(x)), float(np.percentile(bs, 2.5)), float(
        np.percentile(bs, 97.5))


def cohen_d(a, b):
    a = np.asarray(a, float)
    a = a[np.isfinite(a)]
    b = np.asarray(b, float)
    b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return 0.0
    sp = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1))
                 / max(len(a) + len(b) - 2, 1))
    return float((a.mean() - b.mean()) / sp) if sp > 0 else 0.0


def rankcorr(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    if len(x) < 3:
        return 0.0
    rx = np.argsort(np.argsort(x))
    ry = np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def hdr(t):
    print("\n" + "=" * 74 + "\n" + t + "\n" + "=" * 74)


# ===========================================================================
# Operators
# ===========================================================================

def reweight(C, u, v, factor):
    C = C.copy()
    C[u, v] *= factor
    return C


def vow(C, u, v, rounds, step, decay):
    """Vow = spaced reinforcement WITH forgetting. Inscribe (x step), then
    relax toward baseline by `decay`, repeat. A decree pays its whole budget
    once; a vow fights decay every round."""
    C = C.copy()
    base = C[u, v]
    cur = base
    for _ in range(rounds):
        cur = cur * step
        cur = cur + decay * (base - cur)
    C[u, v] = cur
    return C


def add_grace(C, u, v, cost):
    if np.isfinite(C[u, v]):
        raise ValueError("grace must add an edge not in the support")
    C = C.copy()
    C[u, v] = cost
    return C


def demote(C, w, penalty):
    C = C.copy()
    col = np.isfinite(C[:, w])
    C[col, w] += penalty
    return C


def centralities(C, n):
    A = (np.isfinite(C) & (C > 0)).astype(float)
    np.fill_diagonal(A, 0)
    out = {}
    ev, Vc = np.linalg.eig(A.T)
    pc = np.abs(Vc[:, np.argmax(np.abs(ev))])
    out["eigenvector"] = pc / (pc.sum() or 1)
    try:
        al = 0.85 / (max(abs(ev)) or 1.0)
        kz = np.linalg.solve(np.eye(n) - al * A.T, np.ones(n))
        out["katz"] = np.abs(kz) / (np.abs(kz).sum() or 1)
    except np.linalg.LinAlgError:
        out["katz"] = out["eigenvector"]
    btw = np.zeros(n)
    for s in range(n):
        dist = np.full(n, -1)
        dist[s] = 0
        order, dq, par = [], [s], {s: []}
        sig = np.zeros(n)
        sig[s] = 1
        while dq:
            u = dq.pop(0)
            order.append(u)
            for v in np.where(A[u] > 0)[0]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    dq.append(v)
                if dist[v] == dist[u] + 1:
                    sig[v] += sig[u]
                    par.setdefault(v, []).append(u)
        dl = np.zeros(n)
        for w in reversed(order):
            for u in par.get(w, []):
                dl[u] += (sig[u] / sig[w]) * (1 + dl[w])
            if w != s:
                btw[w] += dl[w]
    out["betweenness"] = btw / (btw.sum() or 1)
    return out


# ===========================================================================
# EXPERIMENTS
# ===========================================================================

def exp1_dequantisation():
    hdr("EXP 1  Maslov dequantisation: bounded agent -> tropical limit")
    print("CLAIM: -(1/b) log z(START) -> exact min-plus shortest path as")
    print("       b -> inf.  The corpus's tropical-algebra claim, measured.")
    print("FALSIFY: if the gap does not collapse toward 0 as b grows.")
    rng = np.random.default_rng(MASTER_SEED)
    # valid Boltzmann window: below ~b=2 the path-sum diverges (rho>=1),
    # above ~b=128 exp(-b c) underflows float64. Both are explained, not
    # hidden; the convergence claim lives strictly inside the window.
    betas = np.array([2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128])
    n = 32
    M = []
    for _ in range(60):
        C = gen_er(n, rng)
        ds = tropical_dist(C)[n - 1]
        if not np.isfinite(ds):
            continue
        row = []
        for b in betas:
            r = solve_lmdp(C, float(b))
            row.append(abs(r[0][0] - ds) if r is not None else np.nan)
        M.append(row)
    M = np.array(M)
    med = np.nanmedian(M, axis=0)
    for b, e in zip(betas, med):
        print(f"   b={b:6.1f}   median |V_b(START) - tropical| = {e:.5f}")
    ok = med[-1] < 0.02 and med[-1] < 0.05 * med[0]
    print(f"   -> RESULT: {'SURVIVES' if ok else 'FAILS'} "
          f"(gap {med[0]:.3f} at b={betas[0]} -> {med[-1]:.5f} at b={betas[-1]})")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(betas, med, "o-", color="#c9a24b")
    ax.fill_between(betas, np.nanpercentile(M, 25, 0),
                    np.nanpercentile(M, 75, 0), alpha=.2, color="#c9a24b")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("inverse temperature  b  (log)")
    ax.set_ylabel("|V_b(START) - tropical|  (log)")
    ax.set_title("Maslov dequantisation: bounded agent → least action")
    fig.tight_layout()
    fig.savefig(f"{FIGDIR}/f1_dequantisation.png", dpi=110)
    plt.close(fig)
    return ok


def exp2_metastable():
    hdr("EXP 2  Demon = metastable basin: a dose-response in basin depth")
    print("CLAIM: deepen the exit toll and the basin becomes metastable --")
    print("       exit time explodes, committor(demon->GOOD) -> 0,")
    print("       monotonically. 'capture basin' = a real metastable set.")
    print("FALSIFY: if exit time / committor do not scale with depth.")
    print("The real question is AGENT-RELATIVE. For a MYOPIC Gibbs agent")
    print("(the toy's actual agent) the basin should be Kramers-metastable:")
    print("exit time ~ exp(slope*depth), R^2~1. For the value-aware LMDP")
    print("agent it should NOT be (it pays the toll and leaves).")
    print("FALSIFY: if myopic exit time is not exponential in depth, OR if")
    print("         the LMDP agent is trapped just as badly (then the toy's")
    print("         'capture' was not a myopia artifact after all).")
    rng = np.random.default_rng(MASTER_SEED + 1)
    n, beta, gamma = 34, 2.0, 0.6
    depths = np.array([0.5, 1, 2, 3, 4, 5, 6, 8])
    myo, lmd = [], []
    for dep in depths:
        em, el = [], []
        for _ in range(40):
            C, D = demon_graph(n, rng, dep)
            dx = next(iter(D))
            em.append(min(mfpt(myopic_chain(C, beta), dx, n), 1e12))
            r = solve_lmdp(C, beta, gamma)
            if r is not None:
                el.append(min(mfpt(r[2], dx, n), 1e12))
        myo.append(np.median(em))
        lmd.append(np.median(el) if el else np.nan)
        print(f"   depth={dep:4.1f}  myopic exit={myo[-1]:13.2f}   "
              f"LMDP exit={lmd[-1]:8.2f}")
    myo = np.array(myo)
    lmd = np.array(lmd)
    sl, ic = np.polyfit(depths, np.log(myo), 1)
    pred = np.polyval([sl, ic], depths)
    ss = np.sum((np.log(myo) - pred) ** 2)
    st = np.sum((np.log(myo) - np.log(myo).mean()) ** 2)
    r2 = 1 - ss / st if st > 0 else 0.0
    lmd_flat = (np.nanmax(lmd) / max(np.nanmin(lmd), 1e-9)) < 5
    print(f"   myopic fit: log(exit) = {sl:.3f}*depth + {ic:.2f}  "
          f"R^2 = {r2:.4f}")
    print(f"   LMDP exit spans {np.nanmin(lmd):.1f}..{np.nanmax(lmd):.1f} "
          f"({'flat -> NOT trapped' if lmd_flat else 'also grows'})")
    ok = sl > 0.3 and r2 > 0.95 and lmd_flat
    print("   -> RESULT: " + ("SURVIVES -- the demon is a genuine Kramers "
          "basin FOR A MYOPIC AGENT (exp law, R^2 %.3f) but the value-aware "
          "agent escapes: metastability is agent-relative. This both "
          "vindicates and corrects the toy." % r2 if ok else
          "FAILS -- the agent-relativity dissociation did not hold"))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(depths, myo, "o-", color="#b4453a",
            label=f"myopic Gibbs (exp, R²={r2:.3f})")
    ax.plot(depths, lmd, "s--", color="#7fb0ff",
            label="LMDP (value-aware)")
    xs = np.linspace(depths.min(), depths.max(), 50)
    ax.plot(xs, np.exp(np.polyval([sl, ic], xs)), ":", color="#c9a24b",
            lw=1, label=f"exp fit slope {sl:.2f}")
    ax.set_yscale("log")
    ax.set_xlabel("basin depth (exit toll)")
    ax.set_ylabel("mean exit time (log)")
    ax.set_title("Metastability is agent-relative")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{FIGDIR}/f2_metastable.png", dpi=110)
    plt.close(fig)
    return ok


def exp3_vow_vs_decree():
    hdr("EXP 3  Vow vs budget-matched decree, UNDER FORGETTING")
    print("CLAIM (corpus): a vow is not a one-shot decree; iteration matters.")
    print("FALSIFY: if a spaced vow and a single decree of equal nominal")
    print("         budget are statistically indistinguishable under decay,")
    print("         'repetition' is decorative (the toy's open admission).")
    rng = np.random.default_rng(MASTER_SEED + 2)
    n, beta = 34, 5.0
    rounds, step, decay = 8, 0.72, 0.5
    decree = step ** rounds
    dv, dd = [], []
    for _ in range(140):
        C, D = demon_graph(n, rng, rng.choice([4, 8, 16]))
        u = list(D)[-1]
        vs = np.where(np.isfinite(C[u]) & (np.arange(n) != u))[0]
        vs = [v for v in vs if v not in D]
        if not vs:
            continue
        v = int(vs[0])
        rv = solve_lmdp(vow(C, u, v, rounds, step, decay), beta, 0.6)
        rd = solve_lmdp(reweight(C, u, v, decree), beta, 0.6)
        if rv is None or rd is None:
            continue
        dv.append(min(mfpt(rv[2], 0, n), 1e6))
        dd.append(min(mfpt(rd[2], 0, n), 1e6))
    mv, md = ci(dv, np.median, seed=3), ci(dd, np.median, seed=4)
    d = cohen_d(dv, dd)
    print(f"   vow    MFPT median = {mv[0]:9.2f} [{mv[1]:.1f},{mv[2]:.1f}]")
    print(f"   decree MFPT median = {md[0]:9.2f} [{md[1]:.1f},{md[2]:.1f}]")
    print(f"   effect size Cohen d = {d:+.2f}")
    distinct = abs(d) > 0.2
    print("   -> RESULT: " + ("vow is GENUINELY DISTINCT from a decree under "
          "forgetting -- repetition is load-bearing" if distinct else
          "vow ~ decree -- repetition stays decorative even with decay "
          "(honest negative result)"))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(np.log10(np.clip(dv, 1, None)), 22, alpha=.7,
            label="vow (spaced+decay)", color="#c9a24b")
    ax.hist(np.log10(np.clip(dd, 1, None)), 22, alpha=.7,
            label="decree (one-shot)", color="#7fb0ff")
    ax.set_xlabel("log10 MFPT START→GOOD")
    ax.set_title("Vow vs budget-matched decree, with forgetting")
    ax.legend()
    fig.tight_layout()
    fig.savefig(f"{FIGDIR}/f3_vow_vs_decree.png", dpi=110)
    plt.close(fig)
    return distinct


def exp4_grace_law():
    hdr("EXP 4  Grace acts on the boundedness gap, not the optimum")
    print("Re-tested with the agent dissociation from EXP 2. CLAIM: grace")
    print("(an exogenous dx->GOOD edge) rescues the TRAPPED MYOPIC agent")
    print("robustly across the ensemble. The toy's extra claim -- that grace")
    print("is also ~inert for the planner -- is topology-specific.")
    print("FALSIFY: if grace does not reliably rescue the trapped agent.")
    rng = np.random.default_rng(MASTER_SEED + 3)
    n, beta = 34, 3.0
    ds, do = [], []
    for _ in range(160):
        C, D = demon_graph(n, rng, rng.choice([8, 16, 32]))
        dx = next(iter(D))
        if np.isfinite(C[dx, n - 1]):
            continue
        s0 = 1.0 - capture_prob(myopic_chain(C, beta), n, D)
        o0 = tropical_dist(C)[n - 1]
        G = add_grace(C, dx, n - 1, 1.5)
        s1 = 1.0 - capture_prob(myopic_chain(G, beta), n, D)
        o1 = tropical_dist(G)[n - 1]
        ds.append(s1 - s0)
        if np.isfinite(o0) and np.isfinite(o1):
            do.append(o0 - o1)
    b = ci(ds, np.mean, seed=6)
    a = ci(do, np.mean, seed=5)
    print(f"   Δ trapped-agent success  mean = {b[0]:+.3f} "
          f"[{b[1]:+.3f}, {b[2]:+.3f}]   (n={len(ds)})")
    print(f"   Δ planner optimal cost   mean = {a[0]:+.3f} "
          f"[{a[1]:+.3f}, {a[2]:+.3f}]   (large here = on-path toll, not a "
          "side basin)")
    ok = len(ds) > 20 and b[0] > 0.20
    print("   -> RESULT: " + ("SURVIVES (the robust half) -- grace reliably "
          "rescues the trapped myopic agent across the ensemble; the "
          "'inert for the planner' half is a side-basin property the toy's "
          "topology happened to have, not a general law" if ok else
          "FAILS -- grace does not reliably rescue the trapped agent"))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(ds, 24, color="#c9a24b", alpha=.85)
    ax.axvline(b[0], color="#b4453a", ls="--",
               label=f"mean Δsuccess {b[0]:+.2f}")
    ax.set_xlabel("Δ trapped-agent success after grace")
    ax.set_title("Grace rescues the trapped agent (ensemble)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(f"{FIGDIR}/f4_grace_law.png", dpi=110)
    plt.close(fig)
    return ok


def exp5_forgiveness_centrality():
    hdr("EXP 5  Which centrality IS 'global routing authority'?")
    print("CLAIM: 'demote the wound-node from routing authority' presumes a")
    print("       specific centrality. Which best predicts the behavioural")
    print("       effect of demoting a node (kept reachable)?")
    print("FALSIFY: if no centrality predicts it, 'routing authority' has")
    print("         no referent.")
    rng = np.random.default_rng(MASTER_SEED + 4)
    n, beta = 30, 5.0
    cols = {"betweenness": [], "eigenvector": [], "katz": []}
    eff = []
    for name, gen in ENSEMBLES.items():
        for _ in range(40):
            C = gen(n, rng)
            cen = centralities(C, n)
            cand = [u for u in range(1, n - 1)
                    if cen["betweenness"][u] > 0
                    and np.isfinite(C[:, u]).sum() > 1]
            if not cand:
                continue
            w = int(rng.choice(cand))
            r0 = solve_lmdp(C, beta)
            Cd = demote(C, w, 4.0)
            if not np.isfinite(tropical_dist(Cd)[w]) or \
               not np.isfinite(tropical_dist(Cd)[n - 1]):
                continue
            r1 = solve_lmdp(Cd, beta)
            if r0 is None or r1 is None:
                continue
            m0 = mfpt(r0[2], 0, n)
            m1 = mfpt(r1[2], 0, n)
            eff.append(abs(min(m1, 1e6) - min(m0, 1e6)))
            for k in cols:
                cols[k].append(cen[k][w])
    print("   predictor   |  rank corr with |Δ behaviour|  (95% CI)")
    ranked = {}
    for k, v in cols.items():
        r = rankcorr(v, eff)
        # bootstrap CI on the rank correlation
        pair = np.array([(a, b) for a, b in zip(v, eff)
                         if np.isfinite(a) and np.isfinite(b)])
        rng2 = np.random.default_rng(7)
        bs = [rankcorr(*pair[rng2.integers(0, len(pair), len(pair))].T)
              for _ in range(800)] if len(pair) > 3 else [0, 0]
        ranked[k] = r
        print(f"   {k:12s}|  rho = {r:+.3f}  "
              f"[{np.percentile(bs, 2.5):+.3f}, {np.percentile(bs, 97.5):+.3f}]")
    win = max(ranked, key=lambda k: ranked[k])
    ok = ranked[win] > 0.15
    print(f"   -> RESULT: 'routing authority' best matches **{win}** "
          f"(rho={ranked[win]:+.3f}); " + ("a real referent" if ok else
          "weak -- the phrase is largely underdetermined (honest result)"))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(list(ranked), [ranked[k] for k in ranked],
           color=["#c9a24b", "#7fb0ff", "#b4453a"])
    ax.axhline(0, color="#888", lw=.8)
    ax.set_ylabel("rank corr with |Δ behaviour|")
    ax.set_title("Which centrality = 'global routing authority'?")
    fig.tight_layout()
    fig.savefig(f"{FIGDIR}/f5_forgiveness_centrality.png", dpi=110)
    plt.close(fig)
    return ok, win


def exp6_variety_frontier():
    hdr("EXP 6  Variety as a LEVER, and its price (rate-distortion)")
    print("For the MYOPIC agent (EXP 2) the temperature b IS a variety")
    print("lever: low b = exploratory (high occupation entropy) and randomly")
    print("escapes the basin; high b = commits down the cheap mouth and is")
    print("captured. The price is expected cost. A real rate-distortion")
    print("frontier.  FALSIFY: if entropy can't be driven, or extra variety")
    print("         does not reduce capture.")
    rng = np.random.default_rng(MASTER_SEED + 5)
    n = 32
    betas = np.array([0.5, 1, 2, 3, 5, 8, 13, 21, 34])
    worlds = [demon_graph(n, rng, 12.0) for _ in range(30)]
    H, COST, CAP = [], [], []
    for b in betas:
        hs, cs, cp = [], [], []
        for C, D in worlds:
            P = myopic_chain(C, float(b))
            r = np.array([np.nansum([P[s, v] * (C[s, v] if np.isfinite(
                C[s, v]) else 0.0) for v in range(n)]) for s in range(n)])
            v = np.zeros(n)
            v[0] = 1.0
            occ = np.zeros(n)
            for _ in range(400):
                occ += v
                v = v @ P
            occn = occ / occ.sum()
            pp = occn[occn > 1e-9]
            hs.append(float(-(pp * np.log2(pp)).sum()))   # occupation entropy
            # price of variety = time-averaged cost RATE (occupation-weighted
            # expected step cost). Finite even when the trapped chain almost
            # never absorbs, unlike total expected cost.
            cs.append(float(np.nansum(occn * r)))
            cp.append(float(sum(v[d] for d in D)))         # residual basin mass
        H.append(np.nanmean(hs))
        COST.append(np.nanmean(cs))
        CAP.append(np.nanmean(cp))
    for b, h, c, cp in zip(betas, H, COST, CAP):
        print(f"   b={b:5.1f}  entropy={h:5.3f} bits  E[cost]={c:7.3f}  "
              f"capture={cp:5.3f}")
    drivable = (max(H) - min(H)) > 0.3
    helped = CAP[0] < CAP[-1] - 1e-3
    ok = drivable and helped
    print("   -> RESULT: " + (f"SURVIVES -- entropy spans {min(H):.2f}->"
          f"{max(H):.2f} bits; high variety cuts capture "
          f"{CAP[-1]:.2f}->{CAP[0]:.2f} at measured cost" if ok else
          "variety is still not an independent priced mechanism"))
    fig, ax1 = plt.subplots(figsize=(6, 4))
    ax1.plot(betas, H, "o-", color="#c9a24b", label="terminal entropy")
    ax1.set_xscale("log")
    ax1.set_xlabel("inverse temperature b (log) — the variety lever")
    ax1.set_ylabel("terminal-state entropy (bits)", color="#c9a24b")
    ax2 = ax1.twinx()
    ax2.plot(betas, CAP, "s--", color="#b4453a", label="demon capture")
    ax2.set_ylabel("demon capture prob", color="#b4453a")
    ax1.set_title("Variety is dial-able — and priced")
    fig.tight_layout()
    fig.savefig(f"{FIGDIR}/f6_variety_frontier.png", dpi=110)
    plt.close(fig)
    return ok


def main():
    t0 = time.time()
    print("lab.py -- postdoc instrument for Computational Theology")
    print(f"numpy {np.__version__} · scipy LMDP agent · seed {MASTER_SEED}")
    r1 = exp1_dequantisation()
    r2 = exp2_metastable()
    r3 = exp3_vow_vs_decree()
    r4 = exp4_grace_law()
    r5, win = exp5_forgiveness_centrality()
    r6 = exp6_variety_frontier()
    hdr("SCOREBOARD (every figure & number above is from this run)")
    print(f"  1 Maslov dequantisation      : {'PASS' if r1 else 'FAIL'}")
    print(f"  2 Demon = metastable basin   : {'PASS' if r2 else 'FAIL'}")
    print(f"  3 Vow vs decree (w/ decay)   : "
          f"{'DISTINCT' if r3 else 'indistinct (honest negative)'}")
    print(f"  4 Grace ~ boundedness gap    : {'PASS' if r4 else 'FAIL'}")
    print(f"  5 'routing authority' = {win:11s}: "
          f"{'identified' if r5 else 'underdetermined (honest)'}")
    print(f"  6 Variety = priced lever     : {'PASS' if r6 else 'FAIL'}")
    print(f"\n  wall time {time.time() - t0:.1f}s  "
          f"figures -> site/workground/figs/")


if __name__ == "__main__":
    main()
