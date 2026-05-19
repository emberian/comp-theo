import sys, time, json, itertools
sys.path.insert(0, '.')
import lab5kit as K
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

t0 = time.time()
FACTORS = K.FACTORS
agents = ["tabular", "fa"]
OUT = {}
cells = list(itertools.product([0, 1], repeat=4))

for agent in agents:
    ws = 42 if agent == "tabular" else 43
    tab, jac = K.full_factorial(
        K.world_community, agent, N=800, seeds=range(8), world_seed=ws)
    me = K.main_effects(tab)
    base = float(np.mean(tab[(0, 0, 0, 0)]))
    full = float(np.mean(tab[(1, 1, 1, 1)]))
    # pairwise interactions (lab3 convention)
    inter = {}
    for i, j in itertools.combinations(range(4), 2):
        s = 0.0
        for c in cells:
            sign = (1 if c[i] == c[j] else -1)
            s += sign * np.mean(tab[c])
        inter[f"{FACTORS[i]}|{FACTORS[j]}"] = float(s / len(cells) * 2)
    OUT[agent] = dict(
        base=base, full=full, jaccard=float(jac),
        main={f: [float(me[f][0]), float(me[f][1]), float(me[f][2])]
              for f in FACTORS},
        inter=inter)
    print(f"=== {agent}  base={base:.4f} full={full:.4f} "
          f"jac={jac:.4f} ws={ws}")
    for f in FACTORS:
        e, lo, hi = me[f]
        sig = "ROBUST" if (lo > 0 or hi < 0) else "ns"
        print(f"  main {f:8s} {e:+.4f}  CI[{lo:+.4f},{hi:+.4f}] {sig}")
    for k, v in sorted(inter.items(), key=lambda kv: -abs(kv[1])):
        tag = ("synergy" if v > 0.02 else
               "antagonism" if v < -0.02 else "~additive")
        print(f"  inter {k:18s} {v:+.4f}  {tag}")

with open("atlas/factorial_community.json", "w") as f:
    json.dump({"slice": "factorial_community", "agents": OUT}, f, indent=2)

# ---- figure: 2 columns (tabular | fa); rows: main-effect bars, inter heat
fig, ax = plt.subplots(2, 2, figsize=(11.5, 9.2))
for col, agent in enumerate(agents):
    d = OUT[agent]
    fs = FACTORS
    effs = [d["main"][f][0] for f in fs]
    los = [d["main"][f][0] - d["main"][f][1] for f in fs]
    his = [d["main"][f][2] - d["main"][f][0] for f in fs]
    a0 = ax[0, col]
    bars = a0.bar(fs, effs, yerr=[los, his], capsize=4,
                  color="#c9a24b", edgecolor="#7a6320")
    a0.axhline(0, color="#888", lw=.8)
    a0.set_title(f"{agent} — main effects on found basin\n"
                 f"(N=800, 8 seeds, detected; Jaccard={d['jaccard']:.3f})",
                 fontsize=10)
    a0.set_ylabel("Δ success (on − off)")
    for b, f in zip(bars, fs):
        lo, hi = d["main"][f][1], d["main"][f][2]
        rob = (lo > 0 or hi < 0)
        a0.text(b.get_x() + b.get_width() / 2,
                b.get_height() + (0.004 if b.get_height() >= 0 else -0.012),
                f"{b.get_height():+.3f}" + ("*" if rob else ""),
                ha="center", fontsize=8.5,
                fontweight=("bold" if rob else "normal"))
    a0.text(0.5, -0.16, f"base={d['base']:.3f}   full={d['full']:.3f}",
            transform=a0.transAxes, ha="center", fontsize=8.5,
            color="#555")

    # interaction heatmap (4x4 symmetric, diag blank)
    M = np.full((4, 4), np.nan)
    for i, j in itertools.combinations(range(4), 2):
        v = d["inter"][f"{FACTORS[i]}|{FACTORS[j]}"]
        M[i, j] = M[j, i] = v
    a1 = ax[1, col]
    vmax = max(0.03, np.nanmax(np.abs(M)))
    im = a1.imshow(M, cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    a1.set_xticks(range(4)); a1.set_xticklabels(fs, fontsize=8.5)
    a1.set_yticks(range(4)); a1.set_yticklabels(fs, fontsize=8.5)
    a1.set_title(f"{agent} — pairwise interactions\n"
                 "(blue<0 = antagonism, red>0 = synergy)", fontsize=10)
    for i in range(4):
        for j in range(4):
            if np.isnan(M[i, j]):
                a1.text(j, i, "—", ha="center", va="center",
                        color="#999")
            else:
                a1.text(j, i, f"{M[i, j]:+.3f}", ha="center",
                        va="center", fontsize=8.5,
                        color=("white" if abs(M[i, j]) > 0.6 * vmax
                               else "black"))
    fig.colorbar(im, ax=a1, fraction=0.046, pad=0.04)

fig.suptitle("Atlas — full 2⁴ factorial + interactions on the "
             "found (community/emergent) basin", fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig("figs/atlas_factorial_community.png", dpi=110)
print(f"WALL {time.time()-t0:.1f}s")
