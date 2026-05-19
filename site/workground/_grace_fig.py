import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

d = json.load(open("atlas/grace.json"))
agents = ["myopic", "tabular", "fa"]
worlds = ["single", "two_basin", "community"]
by = {(r["agent"], r["world"]): r for r in d["grid"]}

M = np.array([[by[(a, w)]["effect"] for w in worlds] for a in agents])

fig, ax = plt.subplots(figsize=(7.6, 5.6))
vmax = max(0.05, np.abs(M).max())
im = ax.imshow(M, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")

ax.set_xticks(range(3))
ax.set_xticklabels([w.replace("_", "-") for w in worlds], fontsize=11)
ax.set_yticks(range(3))
ax.set_yticklabels(agents, fontsize=11)
ax.set_xlabel("world", fontsize=11)
ax.set_ylabel("agent (instrument)", fontsize=11)
ax.set_title("Grace main effect across every instrument (3x3)\n"
             "N=600, 6 seeds, labcore engine; box = robust "
             "(95%CI excl. 0 & |eff|>0.02)", fontsize=11)

for i, a in enumerate(agents):
    for j, w in enumerate(worlds):
        r = by[(a, w)]
        e = r["effect"]
        txt = f"{e:+.3f}\n[{r['lo']:+.2f},{r['hi']:+.2f}]\njac={r['jaccard']:.2f}"
        col = "white" if abs(e) > 0.55 * vmax else "black"
        ax.text(j, i, txt, ha="center", va="center",
                fontsize=8.5, color=col)
        if r["robust"]:
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                         fill=False, edgecolor="lime", lw=3))

cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cb.set_label("grace main effect (success on - off)", fontsize=10)
fig.tight_layout()
fig.savefig("figs/atlas_grace.png", dpi=130)
print("WROTE figs/atlas_grace.png")
