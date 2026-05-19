#!/usr/bin/env python3
"""
toy_model.py -- "Does It Cash Out?"

A minimal, dependency-free (standard library only) simulation of the
graph-world the Computational Theology corpus repeatedly gestures at but
never actually built. The gesture is explicit in the origin dialogue
(transcript/conversation.full.md, lines ~13894-13902):

    A small graph-world where:
    - agents follow low-cost paths;
    - "demon"       = low-cost capture basin;
    - "vow"         = repeated edge reinforcement toward return;
    - "mercy"       = lowering return-path cost without deleting harm;
    - "grace"       = exogenous addition of a new reachable edge;
    - "variety"     = penalty against collapse of structural views;
    - "forgiveness" = demotion of a wound-node from global routing authority.

And the corpus even names its own falsification test (line ~13909):

    Claim: "A vow changes reachability."
    Failure test: if repeated vow-inscriptions do not measurably alter future
    transition probabilities or path choices, the vow is merely decorative.

So: build it, run the agent, print numbers, and check each metaphor against
the behaviour it is *claimed* to produce. No numpy, no networkx. Just dicts,
the heap, and random with a fixed seed so the printed numbers are reproducible.

Run: python3 site/workground/toy_model.py
"""

import heapq
import math
import random
from collections import Counter

SEED = 1729
SOFTMAX_BETA = 2.5      # inverse temperature for the agent's stochastic walk
N_WALKS = 20000         # sample size per experiment


# ---------------------------------------------------------------------------
# Graph world
# ---------------------------------------------------------------------------
#
#   START --- a --- b --- GOOD
#     |        \         /
#     |         \-- D --/        D = the demon node (cheap to enter)
#     |             |
#     w ------------/            w = the wound node
#
# Directed graph with edge costs. The GOOD is the marked target ("God running
# a search for the Good", per the glossary). D is a basin: entering it is cheap
# and leaving it is expensive -- a "bad goal is a tiny god".

def base_world():
    # edges[u] = list of (v, cost)
    # w is a genuine hub: the cheapest way from START toward b/GOOD runs
    # THROUGH the wound (START->w->b is 1.0+1.0 vs START->a->b at 1.0+1.0,
    # tie-broken toward w by Dijkstra insertion order is not relied on;
    # rather a->b is made slightly more expensive so w carries real
    # betweenness). The wound is load-bearing infrastructure, which is
    # exactly the corpus's point: you cannot just delete it.
    return {
        "START": [("a", 1.5), ("w", 1.0)],
        "a":     [("b", 1.5), ("D", 0.2)],     # D is suspiciously cheap
        "w":     [("b", 1.0), ("D", 0.5)],     # cheap route to b goes via w
        "b":     [("GOOD", 1.0), ("D", 0.2)],
        "D":     [("D", 0.1), ("b", 6.0)],     # self-loop cheap; exit costly
        "GOOD":  [],
    }


def edge_cost(world, u, v):
    for (w, c) in world[u]:
        if w == v:
            return c
    return math.inf


# ---------------------------------------------------------------------------
# Least-cost (tropical / min-plus) shortest path -- Dijkstra
# ---------------------------------------------------------------------------

def dijkstra(world, src):
    dist = {n: math.inf for n in world}
    dist[src] = 0.0
    prev = {}
    pq = [(0.0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for (v, c) in world[u]:
            nd = d + c
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    return dist, prev


def path_to(prev, target):
    if target not in prev and target != "START":
        return None
    path = [target]
    while path[-1] != "START":
        if path[-1] not in prev:
            return None
        path.append(prev[path[-1]])
    return list(reversed(path))


# ---------------------------------------------------------------------------
# Softmax random walk (a bounded-rational agent, not a perfect optimiser)
# ---------------------------------------------------------------------------

def softmax_walk(world, rng, beta=SOFTMAX_BETA, max_steps=40):
    """One agent walk from START. Returns (terminal_node, steps, visited)."""
    node = "START"
    visited = Counter()
    for step in range(max_steps):
        visited[node] += 1
        edges = world[node]
        if not edges:                       # absorbing (GOOD)
            return node, step, visited
        # cheap edges are attractive: weight = exp(-beta * cost)
        weights = [math.exp(-beta * c) for (_, c) in edges]
        tot = sum(weights)
        r = rng.random() * tot
        acc = 0.0
        for (v, _), wt in zip(edges, weights):
            acc += wt
            if r <= acc:
                node = v
                break
    return node, max_steps, visited


def reach_stats(world, n=N_WALKS):
    rng = random.Random(SEED)
    good = capture = 0
    steps_to_good = []
    for _ in range(n):
        term, steps, _ = softmax_walk(world, rng)
        if term == "GOOD":
            good += 1
            steps_to_good.append(steps)
        elif term == "D":
            capture += 1
    p_good = good / n
    p_cap = capture / n
    mean_steps = (sum(steps_to_good) / len(steps_to_good)) if steps_to_good else float("nan")
    return p_good, p_cap, mean_steps


# ---------------------------------------------------------------------------
# Interventions
# ---------------------------------------------------------------------------

def apply_vow(world, edge, rounds=8, factor=0.7):
    """VOW = repeated edge reinforcement toward return. Each 'inscription'
    multiplies the target edge's cost by `factor` (makes the return road
    progressively cheaper). Mutates a copy."""
    w = {u: list(es) for u, es in world.items()}
    u, v = edge
    for _ in range(rounds):
        w[u] = [(t, (c * factor if t == v else c)) for (t, c) in w[u]]
    return w


def apply_mercy(world, edge, new_cost):
    """MERCY = lower a return-path cost WITHOUT deleting the harm. The demon
    node and its cheap self-loop stay; we only cheapen one escape edge."""
    w = {u: list(es) for u, es in world.items()}
    u, v = edge
    w[u] = [(t, (new_cost if t == v else c)) for (t, c) in w[u]]
    return w


def apply_grace(world, edge, cost):
    """GRACE = exogenous addition of a NEW reachable edge that did not exist
    in the world's own transition table."""
    w = {u: list(es) for u, es in world.items()}
    u, v = edge
    if any(t == v for (t, _) in w[u]):
        raise ValueError("grace must add an edge that does not exist")
    w[u] = w[u] + [(v, cost)]
    return w


def betweenness(world, wound):
    """Routing centrality of `wound`: fraction of all-pairs shortest paths
    (over non-wound endpoints) whose interior passes through `wound`."""
    nodes = [n for n in world]
    through = 0
    total = 0
    for s in nodes:
        if s == wound:
            continue
        _, prev = dijkstra(world, s)
        for t in nodes:
            if t == s or t == wound:
                continue
            p = []
            cur = t
            ok = True
            while cur != s:
                p.append(cur)
                if cur not in prev:
                    ok = False
                    break
                cur = prev[cur]
            if not ok:
                continue
            total += 1
            if wound in p[1:]:      # interior, not endpoint
                through += 1
    return through / total if total else 0.0


def apply_forgiveness(world, wound, penalty=5.0):
    """FORGIVENESS = demote the wound-node from global routing authority
    WITHOUT deleting it. We add a routing penalty to every edge that *enters*
    the wound, so paths stop preferring to transit it -- but the node, and
    every path that genuinely needs it, still exist."""
    w = {u: list(es) for u, es in world.items()}
    for u in w:
        w[u] = [(t, (c + penalty if t == wound else c)) for (t, c) in w[u]]
    return w


def variety_index(world, rng, n=4000):
    """VARIETY = anti-collapse of structural views. Measure: Shannon entropy
    (in bits) of the distribution over *terminal* states the agent population
    settles into -- i.e. which destinies the world actually realises. A
    monoculture world routes (almost) everyone to one terminal: H -> 0."""
    seen = Counter()
    for _ in range(n):
        term, _, _ = softmax_walk(world, rng)
        seen[term] += 1
    tot = sum(seen.values())
    h = -sum((c / tot) * math.log2(c / tot) for c in seen.values())
    return h, dict(seen)


# ---------------------------------------------------------------------------
# Experiments
# ---------------------------------------------------------------------------

def line(title):
    print("\n" + "=" * 68)
    print(title)
    print("=" * 68)


def main():
    W = base_world()

    line("EXPERIMENT 0 -- the bare world (demon present, no intervention)")
    d, prev = dijkstra(W, "START")
    print(f"  least-cost dist START->GOOD : {d['GOOD']:.3f}")
    print(f"  least-cost path             : {' -> '.join(path_to(prev, 'GOOD'))}")
    print(f"  least-cost dist START->D    : {d['D']:.3f}  (the demon is closer)")
    pg, pc, ms = reach_stats(W)
    print(f"  softmax agent  P(reach GOOD): {pg:.4f}")
    print(f"  softmax agent  P(captured D): {pc:.4f}")
    print(f"  mean steps to GOOD          : {ms:.2f}")
    print("  CLAIM TESTED: 'demon = low-cost capture basin.'")
    print("  -> a cheap-to-enter, costly-to-exit node with a cheap self-loop")
    print("     should swallow most bounded-rational agents. Does it?")

    line("EXPERIMENT 1 -- VOW: reinforce the return edge D->b, 8 rounds x0.7")
    base_cost = edge_cost(W, "D", "b")
    Wv = apply_vow(W, ("D", "b"), rounds=8, factor=0.7)
    print(f"  edge cost D->b  before : {base_cost:.3f}")
    print(f"  edge cost D->b  after  : {edge_cost(Wv, 'D', 'b'):.3f}")
    pg0, pc0, _ = reach_stats(W)
    pg1, pc1, ms1 = reach_stats(Wv)
    print(f"  P(reach GOOD)  before  : {pg0:.4f}")
    print(f"  P(reach GOOD)  after   : {pg1:.4f}   (delta {pg1 - pg0:+.4f})")
    print(f"  P(captured)    before  : {pc0:.4f}")
    print(f"  P(captured)    after   : {pc1:.4f}   (delta {pc1 - pc0:+.4f})")
    print("  CLAIM TESTED: 'a vow changes reachability.' Corpus-named")
    print("  failure test: if repeated inscriptions do NOT measurably alter")
    print("  future path choices, the vow is merely decorative.")

    line("EXPERIMENT 2 -- MERCY: cheapen ONE escape edge, keep the harm")
    Wm = apply_mercy(W, ("D", "b"), new_cost=0.4)
    print("  demon node D still present; self-loop D->D still cost 0.10;")
    print("  wound node w untouched. Only D->b lowered 6.00 -> 0.40.")
    pg2, pc2, ms2 = reach_stats(Wm)
    print(f"  P(reach GOOD)  before  : {pg0:.4f}")
    print(f"  P(reach GOOD)  after   : {pg2:.4f}   (delta {pg2 - pg0:+.4f})")
    print(f"  P(captured)    after   : {pc2:.4f}")
    print(f"  D still in graph?      : {'D' in Wm}  (harm not deleted)")
    print("  CLAIM TESTED: 'mercy lowers return-path cost without deleting")
    print("  harm.' Should rescue agents while leaving the wound in place.")

    line("EXPERIMENT 3 -- GRACE: add a NEW edge D->GOOD (cost 1.5)")
    Wg = apply_grace(W, ("D", "GOOD"), cost=1.5)
    existed = any(t == "GOOD" for (t, _) in W["D"])
    print(f"  edge D->GOOD existed in base world? : {existed}")
    print(f"  edge D->GOOD exists after grace?    : {any(t=='GOOD' for (t,_) in Wg['D'])}")
    dg, pvg = dijkstra(Wg, "START")
    print(f"  least-cost dist START->GOOD before : {d['GOOD']:.3f}")
    print(f"  least-cost dist START->GOOD after  : {dg['GOOD']:.3f}")
    print(f"  new least-cost path : {' -> '.join(path_to(pvg, 'GOOD'))}")
    pg3, pc3, ms3 = reach_stats(Wg)
    print(f"  P(reach GOOD)  before : {pg0:.4f}")
    print(f"  P(reach GOOD)  after  : {pg3:.4f}   (delta {pg3 - pg0:+.4f})")
    print("  CLAIM TESTED: 'grace = exogenous new reachable edge; grace")
    print("  enters from outside the loop.' A path that did not exist in the")
    print("  world's own transition table now does.")

    line("EXPERIMENT 4 -- FORGIVENESS: demote wound-node w, do not delete it")
    bw0 = betweenness(W, "w")
    Wf = apply_forgiveness(W, "w", penalty=5.0)
    bw1 = betweenness(Wf, "w")
    print(f"  routing centrality of w  before : {bw0:.4f}")
    print(f"  routing centrality of w  after  : {bw1:.4f}")
    print(f"  w still a node after forgiveness?: {'w' in Wf}")
    df, _ = dijkstra(Wf, "START")
    print(f"  w still reachable at all?       : {df['w'] < math.inf}  "
          f"(dist {df['w']:.2f})")
    print("  CLAIM TESTED: 'the wound is irreversible; its sovereignty is")
    print("  not -- forgiveness demotes a wound-node from global routing")
    print("  authority, not deleting it.'")

    line("EXPERIMENT 5 -- VARIETY: entropy of exercised structure")
    rng_a = random.Random(SEED)
    hv0, dist0 = variety_index(W, rng_a)
    # collapse the world: make the demon basin overwhelmingly dominant
    Wcol = {u: [(t, (0.01 if t == "D" else c + 3.0)) for (t, c) in es]
            for u, es in W.items()}
    rng_b = random.Random(SEED)
    hv1, dist1 = variety_index(Wcol, rng_b)
    print(f"  structural entropy  base world      : {hv0:.4f} bits")
    print(f"  structural entropy  collapsed world : {hv1:.4f} bits")
    print(f"  base   node-visit spread : {dist0}")
    print(f"  collapsed node-visit spread : {dist1}")
    print("  CLAIM TESTED: 'variety = penalty against collapse of structural")
    print("  views.' A monoculture world should score measurably lower.")

    line("DONE -- numbers above are produced by this script (seed=1729)")


if __name__ == "__main__":
    main()
