import sys, time, json
sys.path.insert(0, '.')
import lab5kit as K
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

t0 = time.time()
agents = ["myopic", "tabular", "fa"]
worlds = ["single", "two_basin", "community"]
grid = []
M = {}  # (agent,world) -> effect for heatmap

for agent in agents:
    for world in worlds:
        tab, jac = K.full_factorial(
            K.WORLDS[world], agent, N=600, seeds=range(6),
            world_seed=hash((agent, world)) % 1000)
        me = K.main_effects(tab)
        eff, lo, hi = me["vow"]
        robust = (lo > 0 or hi < 0) and abs(eff) > 0.02
        sign = "+" if eff > 0 else ("-" if eff < 0 else "0")
        if eff == 0:
            sign = "0"
        grid.append(dict(agent=agent, world=world, effect=eff,
                         lo=lo, hi=hi, jaccard=float(jac),
                         robust=bool(robust), sign=sign))
        M[(agent, world)] = eff
        print(f"{agent:8s} {world:10s} vow={eff:+.4f} "
              f"CI[{lo:+.4f},{hi:+.4f}] jac={jac:.3f} "
              f"robust={robust} {sign}")

with open("atlas/vow.json", "w") as f:
    json.dump({"slice": "vow", "grid": grid}, f, indent=2)

# 3x3 heatmap
Z = np.array([[M[(a, w)] for w in worlds] for a in agents])
vmax = max(0.05, np.abs(Z).max())
fig, ax = plt.subplots(figsize=(6.2, 5.4))
im = ax.imshow(Z, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
ax.set_xticks(range(3)); ax.set_xticklabels(worlds)
ax.set_yticks(range(3)); ax.set_yticklabels(agents)
ax.set_xlabel("world"); ax.set_ylabel("agent")
ax.set_title("Vow main effect across every instrument\n"
             "(N=600, 6 seeds, detected basin)")
for i, a in enumerate(agents):
    for j, w in enumerate(worlds):
        g = next(x for x in grid if x["agent"] == a and x["world"] == w)
        star = " *" if g["robust"] else ""
        ax.text(j, i, f"{Z[i, j]:+.3f}{star}", ha="center",
                va="center", fontsize=10,
                color=("white" if abs(Z[i, j]) > 0.6 * vmax else "black"))
cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cb.set_label("vow effect (Δ success)")
fig.tight_layout()
fig.savefig("figs/atlas_vow.png", dpi=110)
print(f"WALL {time.time()-t0:.1f}s")
