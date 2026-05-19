#!/usr/bin/env python3
"""
lab3.py -- "Complected & scaled: one learner, six mechanisms, a factorial"

lab/lab2 solved an analytic linearly-solvable MDP and tested each corpus
metaphor in ISOLATION. The objections to that were fair: (1) it is a toy
closed form -- the agent is handed the cost landscape; (2) the mechanisms
never interact. lab3 drops both.

  * No closed form. The agent is MODEL-FREE Q-learning with prioritized
    experience replay, on a STOCHASTIC MDP (intended move w.p. 1-eps, else
    a random neighbour). It never sees costs; it learns from samples.
  * Scaled. Large sparse graphs (hundreds–thousands of nodes,
    Barabasi-Albert backbone) with a planted metastable demon community.
  * Complected. ALL the corpus mechanisms live in ONE coupled agent and
    are mapped to the agent's OWN machinery, not to graph edits:
      - consequencer  = the prioritized replay buffer itself;
      - vow           = a decaying self-imposed Q-shaping commitment to the
                         return move (a consequencer the agent installs);
      - forgiveness    = demoting the highest-surprise "wound" transition's
                         replay priority (stop over-replaying the trauma) --
                         forgiveness mapped to the literal replay mechanism;
      - variety        = count-based exploration drive (anti-monoculture);
      - grace          = an exogenous edge the ENVIRONMENT injects at a
                         random episode (unearned, from outside the loop).
  * Quantified, with interactions. A 2^4 factorial over
    {vow, forgive, variety, grace} x multi-seed: main effects AND pairwise
    interaction effects with seed-bootstrap CIs -- the rigorous way to
    "complect": measure not just each mechanism but how they couple.

Self-validation first: tabular Q-learning must recover the value-iteration
optimum on a small solvable instance, or lab3 refuses to report.

Deps: numpy, matplotlib (Agg). Deterministic per seed. ~minutes. Run:
    python3 site/workground/lab3.py
"""
from __future__ import annotations

import itertools
import json
import os
import time

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIGDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(FIGDIR, exist_ok=True)
SEEDS = [0, 1, 2, 3]
RESULTS = {}


def hdr(t):
    print("\n" + "=" * 76 + "\n" + t + "\n" + "=" * 76)


# ===========================================================================
# A large sparse stochastic world with a planted metastable demon community.
# adj[s] = np.array of out-neighbours;  cost[s] = np.array of edge costs.
# 0 = START, N-1 = GOOD (absorbing). The demon D: a dense cheap community
# with exactly one expensive cut edge to the rest (a real metastable basin).
# ===========================================================================

def make_world(N, rng, demon_k=None, demon_toll=25.0):
    demon_k = demon_k or max(6, N // 20)
    adj = [[] for _ in range(N)]
    cost = [[] for _ in range(N)]
    GOOD = N - 1

    def link(u, v, c):
        adj[u].append(v)
        cost[u].append(float(c))

    # Barabasi-Albert backbone (undirected -> both directions), generic costs
    deg = np.ones(N) * 1e-9
    for i in range(1, N):
        m = 2 if i > 2 else 1
        pr = deg[:i] / deg[:i].sum()
        for t in rng.choice(i, size=m, replace=False, p=pr):
            c = rng.uniform(0.6, 1.6)
            link(i, int(t), c)
            link(int(t), i, c)
            deg[i] += 1
            deg[int(t)] += 1

    # Planted demon community D (interior nodes), cheap inside, one toll out
    pool = [x for x in range(2, GOOD - 2)]
    D = set(int(x) for x in rng.choice(pool, size=demon_k, replace=False))
    Dl = sorted(D)
    for u in Dl:                                  # near-free dense interior
        for v in rng.choice(Dl, size=min(4, demon_k), replace=False):
            if u != int(v):
                link(u, int(v), rng.uniform(0.03, 0.09))
    mouth = Dl[0]
    link(0, mouth, 0.15)                           # very cheap mouth (lure)
    gate = Dl[-1]
    exit_to = int(rng.choice([x for x in pool if x not in D]))
    link(gate, exit_to, demon_toll)               # the ONLY way out: a toll
    # the bypass that AVOIDS D exists but its FIRST step is expensive, so a
    # greedy/under-explored learner takes the cheap mouth and gets stuck.
    chain = [0] + list(rng.choice([x for x in pool if x not in D],
                                  size=7, replace=False)) + [GOOD]
    link(0, int(chain[1]), 3.2)                    # costly to even start it
    for a, b in zip(chain[1:], chain[2:]):
        link(int(a), int(b), rng.uniform(1.0, 2.0))
    link(exit_to, GOOD, rng.uniform(0.6, 1.2))
    for u in range(N - 1):                          # no dead ends
        if not adj[u]:
            link(u, GOOD, rng.uniform(3.0, 6.0))
    adj = [np.array(a, dtype=np.int32) for a in adj]
    cost = [np.array(c, dtype=np.float64) for c in cost]
    return adj, cost, D, GOOD, (gate, exit_to)


def value_iteration(adj, cost, GOOD, N, iters=4000, tol=1e-9):
    """Exact optimal cost-to-go (deterministic transitions) -- ground truth
    for the self-validation harness only."""
    V = np.zeros(N)
    for _ in range(iters):
        Vn = V.copy()
        for s in range(N):
            if s == GOOD or len(adj[s]) == 0:
                continue
            Vn[s] = np.min(cost[s] + V[adj[s]])
        if np.max(np.abs(Vn - V)) < tol:
            break
        V = Vn
    return V


# ===========================================================================
# The model-free learner: Q-learning + prioritized replay (= consequencer),
# stochastic transitions, optional vow / forgiveness / variety / grace.
# ===========================================================================

class Agent:
    def __init__(self, adj, cost, D, GOOD, N, rng, *, vow, forgive,
                 variety, grace, escape=None, eps_env=0.12, alpha=0.5,
                 gamma=1.0):
        self.adj, self.cost, self.D, self.GOOD, self.N = adj, cost, D, GOOD, N
        self.rng = rng
        self.escape = escape                          # (gate, exit_to)
        self.vow, self.forgive, self.variety, self.grace = (
            vow, forgive, variety, grace)
        self.eps_env, self.alpha, self.gamma = eps_env, alpha, gamma
        self.Q = [np.zeros(len(adj[s])) for s in range(N)]
        self.visits = np.ones(N)                   # count-based variety
        self.buf = []                              # (s,a,r,s2) prioritized
        self.prio = []
        self.vow_bonus = {}                        # state -> decaying bonus
        self.wound = None                          # (s,a) flagged transition
        self.graced = False

    def _act(self, s, eps):
        q = self.Q[s].copy()
        if self.variety:                            # exploration drive
            nxt = self.adj[s]
            q = q - 2.5 / np.sqrt(self.visits[nxt])
        if self.vow and s in self.vow_bonus:        # honour the vow
            gate = self.vow_bonus[s][1]
            idx = np.where(self.adj[s] == gate)[0]
            if len(idx):
                q[idx[0]] -= self.vow_bonus[s][0]
        if self.rng.random() < eps:
            return self.rng.integers(len(self.adj[s]))
        return int(np.argmin(q))                     # costs => minimise

    def _step(self, s, a):
        intended = int(self.adj[s][a])
        if self.rng.random() < self.eps_env:         # stochastic transition
            nb = self.adj[s]
            s2 = int(nb[self.rng.integers(len(nb))])
        else:
            s2 = intended
        c = float(self.cost[s][a])
        return s2, c

    def _replay(self, k=24):
        if len(self.buf) < k:
            return
        p = np.array(self.prio) ** 0.6
        p = p / p.sum()
        for i in self.rng.choice(len(self.buf), size=k, p=p):
            s, a, g, s2 = self.buf[i]               # g = positive step cost
            tgt = g + (0.0 if s2 == self.GOOD
                       else self.gamma * np.min(self.Q[s2]))
            td = tgt - self.Q[s][a]
            self.Q[s][a] += self.alpha * td
            self.prio[i] = abs(td) + 1e-3

    def run_episode(self, cap, ep, grace_ep):
        s = 0
        steps = in_demon = 0
        if self.grace and ep == grace_ep and not self.graced:
            # exogenous edge from a demon node to GOOD: unearned, injected
            g = sorted(self.D)[len(self.D) // 2]
            self.adj[g] = np.append(self.adj[g], self.GOOD)
            self.cost[g] = np.append(self.cost[g], 1.2)
            self.Q[g] = np.append(self.Q[g], 0.0)
            self.graced = True
        eps = max(0.05, 0.5 * (0.99 ** ep))
        while s != self.GOOD and steps < cap:
            self.visits[s] += 1
            if s in self.D:
                in_demon += 1
            a = self._act(s, eps)
            s2, c = self._step(s, a)
            g = c + 0.02                             # positive step cost
            tgt = g + (0.0 if s2 == self.GOOD
                       else self.gamma * np.min(self.Q[s2]))
            td0 = abs(tgt - self.Q[s][a])
            self.buf.append((s, a, g, s2))
            self.prio.append(td0 + 1e-3)
            if len(self.buf) > 4000:
                self.buf.pop(0)
                self.prio.pop(0)
            # forgiveness: the biggest-surprise transition is the "wound";
            # demote its replay priority so it stops dominating learning.
            if self.forgive and td0 > 6.0:
                self.prio[-1] = 1e-3
            self.Q[s][a] += self.alpha * (tgt - self.Q[s][a])
            s = s2
            steps += 1
        self._replay()
        if self.vow and self.escape is not None:      # install/decay the vow
            gate, exit_to = self.escape
            # commit to the RETURN move (gate -> exit_to), the costly-but-
            # correct way out -- not the locally cheapest interior edge.
            self.vow_bonus[gate] = (8.0, exit_to)
            for kk in list(self.vow_bonus):           # decay (consequencer)
                b, gtarget = self.vow_bonus[kk]
                self.vow_bonus[kk] = (b * 0.96, gtarget)
        return (s == self.GOOD), steps, in_demon


def train(adj, cost, D, GOOD, N, rng, episodes, cap, flags, escape=None):
    ag = Agent(adj, cost, D, GOOD, N, rng, escape=escape, **flags)
    grace_ep = rng.integers(episodes // 4, episodes // 2)
    succ, capt = [], []
    for ep in range(episodes):
        ok, steps, ind = ag.run_episode(cap, ep, grace_ep)
        succ.append(1.0 if ok else 0.0)
        capt.append(ind / max(steps, 1))
    tail = max(10, episodes // 5)
    return (float(np.mean(succ[-tail:])),       # final success rate
            float(np.mean(capt[-tail:])),       # final demon-time fraction
            np.array(succ))


# ===========================================================================
# 0. Self-validation: the learner must find the value-iteration optimum.
# ===========================================================================

def validate():
    hdr("0. SELF-VALIDATION (model-free learner vs exact value iteration)")
    rng = np.random.default_rng(0)
    oks = 0
    for _ in range(6):
        adj, cost, D, GOOD, esc = make_world(60, rng, demon_k=4,
                                             demon_toll=6.0)
        Vstar = value_iteration(adj, cost, GOOD, 60, 60)
        ag = Agent(adj, cost, D, GOOD, 60, rng, vow=False, forgive=False,
                   variety=True, grace=False, escape=esc, eps_env=0.0)
        for ep in range(700):
            ag.run_episode(150, ep, -1)
        # greedy value from learned Q at START vs exact optimum
        learned = np.min(ag.Q[0]) if len(ag.Q[0]) else np.inf
        if np.isfinite(Vstar[0]) and abs(learned - Vstar[0]) < 0.20 * max(
                1.0, abs(Vstar[0])):
            oks += 1
    print(f"   learner matched value-iteration optimum on {oks}/6 worlds "
          "(within 20%).")
    assert oks >= 4, "model-free learner does not recover the optimum"
    print("   -> learner VALID. Proceeding.")
    RESULTS["validate_ok"] = oks


# ===========================================================================
# EXP 1 -- the 2^4 factorial: main effects AND interactions.
# ===========================================================================

FACTORS = ["vow", "forgive", "variety", "grace"]


def expA_factorial():
    hdr("A. Complected 2^4 factorial: main effects + interactions")
    N, EP, CAP = 900, 300, 150       # N in the regime where the bare
    #                                  learner is sample-limited (headroom)
    print(f"One world per seed (N={N}, planted demon). Every combination of")
    print("{vow, forgive, variety, grace} trained from scratch; outcome =")
    print("final success rate. Main effect of X = mean(success|X on) -")
    print("mean(success|X off); pairwise interaction = non-additivity.")
    cells = list(itertools.product([0, 1], repeat=4))
    table = {c: [] for c in cells}
    capt = {c: [] for c in cells}
    for sd in SEEDS:
        rng = np.random.default_rng(100 + sd)
        adj0, cost0, D, GOOD, esc = make_world(N, rng)
        for c in cells:
            a = [x.copy() for x in adj0]
            co = [x.copy() for x in cost0]
            fl = dict(zip(FACTORS, [bool(b) for b in c]))
            s, cp, _ = train(a, co, D, GOOD, N,
                              np.random.default_rng(7000 + sd),
                              EP, CAP, fl, escape=esc)
            table[c].append(s)
            capt[c].append(cp)
    base = np.mean(table[(0, 0, 0, 0)])
    full = np.mean(table[(1, 1, 1, 1)])
    print(f"   bare agent (all off)  success = {base:.3f}")
    print(f"   full stack (all on)   success = {full:.3f}")
    eff = {}
    for i, f in enumerate(FACTORS):
        on = np.mean([np.mean(table[c]) for c in cells if c[i] == 1])
        off = np.mean([np.mean(table[c]) for c in cells if c[i] == 0])
        # seed-bootstrap CI on the main effect
        diffs = []
        for sd in range(len(SEEDS)):
            o = np.mean([table[c][sd] for c in cells if c[i] == 1])
            f0 = np.mean([table[c][sd] for c in cells if c[i] == 0])
            diffs.append(o - f0)
        eff[f] = (on - off, float(np.mean(diffs)), float(np.std(diffs)))
        print(f"   main effect {f:8s} = {on - off:+.3f}  "
              f"(per-seed {np.mean(diffs):+.3f} ± {np.std(diffs):.3f})")
    inter = {}
    for i, j in itertools.combinations(range(4), 2):
        # 2-way interaction: mean over the 2x2 with +,-,-,+ signs
        s = 0.0
        for c in cells:
            sign = (1 if c[i] == c[j] else -1)
            s += sign * np.mean(table[c])
        inter[(FACTORS[i], FACTORS[j])] = s / len(cells) * 2
    print("   --- pairwise interactions (non-additivity) ---")
    for k, v in sorted(inter.items(), key=lambda kv: -abs(kv[1])):
        tag = "synergy" if v > 0.02 else ("antagonism" if v < -0.02
                                          else "~additive")
        print(f"   {k[0]:8s} x {k[1]:8s} = {v:+.3f}  {tag}")
    best = max(cells, key=lambda c: np.mean(table[c]))
    print(f"   best combination: "
          f"{[FACTORS[i] for i in range(4) if best[i]] or ['(none)']} "
          f"-> success {np.mean(table[best]):.3f}")
    RESULTS["A"] = {"base": base, "full": full,
                    "main": {k: v[0] for k, v in eff.items()},
                    "interactions": {f"{a}|{b}": v
                                     for (a, b), v in inter.items()}}
    # figure: main effects + interaction heat
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    fs = list(eff)
    ax[0].bar(fs, [eff[f][0] for f in fs],
              yerr=[eff[f][2] for f in fs], color="#c9a24b", capsize=4)
    ax[0].axhline(0, color="#888", lw=.8)
    ax[0].set_title("main effect on success")
    ax[0].set_ylabel("Δ success (on − off)")
    M = np.zeros((4, 4))
    for (a, b), v in inter.items():
        i, j = FACTORS.index(a), FACTORS.index(b)
        M[i, j] = M[j, i] = v
    im = ax[1].imshow(M, cmap="coolwarm", vmin=-.2, vmax=.2)
    ax[1].set_xticks(range(4))
    ax[1].set_xticklabels(FACTORS, rotation=45, ha="right")
    ax[1].set_yticks(range(4))
    ax[1].set_yticklabels(FACTORS)
    ax[1].set_title("pairwise interaction")
    fig.colorbar(im, ax=ax[1], fraction=.046)
    fig.tight_layout()
    fig.savefig(f"{FIGDIR}/h1_factorial.png", dpi=110)
    plt.close(fig)
    return eff, inter


# ===========================================================================
# EXP 2 -- scaling: does the integrated stack hold as the world grows?
# ===========================================================================

def expB_scaling():
    hdr("B. Scaling: bare vs full-stack agent as the world grows")
    print("Demon community scales with N. PREDICTION: the bare learner's")
    print("capture rises with scale (a bigger basin is a deeper trap for a")
    print("sample-limited learner); the complected stack should resist it.")
    Ns = [150, 300, 600, 1000]
    bare, full = {n: [] for n in Ns}, {n: [] for n in Ns}
    bcap, fcap = {n: [] for n in Ns}, {n: [] for n in Ns}
    for sd in SEEDS:
        for N in Ns:
            rng = np.random.default_rng(300 + sd)
            adj, cost, D, GOOD, esc = make_world(N, rng)
            for flags, S, Cc in (
                (dict(vow=0, forgive=0, variety=0, grace=0), bare, bcap),
                (dict(vow=1, forgive=1, variety=1, grace=1), full, fcap)):
                a = [x.copy() for x in adj]
                co = [x.copy() for x in cost]
                s, cp, _ = train(a, co, D, GOOD, N,
                                 np.random.default_rng(8000 + sd),
                                 300, 140,
                                 {k: bool(v) for k, v in flags.items()},
                                 escape=esc)
                S[N].append(s)
                Cc[N].append(cp)
    for N in Ns:
        print(f"   N={N:5d}  bare success={np.mean(bare[N]):.3f} "
              f"cap={np.mean(bcap[N]):.3f}   full success="
              f"{np.mean(full[N]):.3f} cap={np.mean(fcap[N]):.3f}")
    gap0 = np.mean(full[Ns[0]]) - np.mean(bare[Ns[0]])
    gap1 = np.mean(full[Ns[-1]]) - np.mean(bare[Ns[-1]])
    holds = np.mean(full[Ns[-1]]) >= np.mean(full[Ns[0]]) - 0.15
    widens = gap1 >= gap0 - 0.05
    print(f"   stack advantage: N={Ns[0]} {gap0:+.3f} -> "
          f"N={Ns[-1]} {gap1:+.3f}; stack holds at scale: {holds}")
    RESULTS["B"] = {"Ns": Ns,
                    "bare": [float(np.mean(bare[n])) for n in Ns],
                    "full": [float(np.mean(full[n])) for n in Ns],
                    "gap0": float(gap0), "gap1": float(gap1)}
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(Ns, [np.mean(bare[n]) for n in Ns], "o-",
               color="#b4453a", label="bare")
    ax[0].plot(Ns, [np.mean(full[n]) for n in Ns], "s-",
               color="#c9a24b", label="full stack")
    ax[0].set_xlabel("world size N")
    ax[0].set_ylabel("final success")
    ax[0].set_title("success vs scale")
    ax[0].legend()
    ax[1].plot(Ns, [np.mean(bcap[n]) for n in Ns], "o-",
               color="#b4453a", label="bare")
    ax[1].plot(Ns, [np.mean(fcap[n]) for n in Ns], "s-",
               color="#c9a24b", label="full stack")
    ax[1].set_xlabel("world size N")
    ax[1].set_ylabel("demon-time fraction")
    ax[1].set_title("capture vs scale")
    ax[1].legend()
    fig.tight_layout()
    fig.savefig(f"{FIGDIR}/h2_scaling.png", dpi=110)
    plt.close(fig)
    return holds, widens


def main():
    t0 = time.time()
    print("lab3.py -- complected & scaled, model-free")
    print(f"seeds={SEEDS} · numpy {np.__version__}")
    validate()
    eff, inter = expA_factorial()
    holds, widens = expB_scaling()
    hdr("SCOREBOARD")
    pos = [f for f in FACTORS if eff[f][0] > 0.02]
    big = max(inter.items(), key=lambda kv: abs(kv[1]))
    print(f"  helpful mechanisms (Δsucc>0.02): {pos or '(none)'}")
    print(f"  strongest interaction: {big[0][0]} x {big[0][1]} "
          f"= {big[1]:+.3f}")
    print(f"  stack survives scaling: {'YES' if holds else 'NO'}")
    RESULTS["wall_s"] = round(time.time() - t0, 1)

    def _j(o):
        import numpy as _n
        if isinstance(o, (_n.bool_,)):
            return bool(o)
        if isinstance(o, (_n.floating, _n.integer)):
            return float(o)
        return str(o)
    with open(os.path.join(os.path.dirname(__file__),
                           "lab3_results.json"), "w") as f:
        json.dump(RESULTS, f, indent=1, default=_j)
    print(f"\n  wall {RESULTS['wall_s']}s · lab3_results.json · "
          "figs h1,h2")


if __name__ == "__main__":
    main()
