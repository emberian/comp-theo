import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

d = json.load(open("atlas/forgive.json"))
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
ax.set_title("Forgive main effect across every instrument (3x3)\n"
             "N=600, 6 seeds, labcore engine; box = robust "
             "(95%CI excl. 0 & |eff|>0.02)", fontsize=11)

for i, a in enumerate(agents):
    for j, w in enumerate(worlds):
        r = by[(a, w)]
        e = r["effect"]
        if a == "myopic":
            txt = f"{e:+.3f}\n(no-op)"
        else:
            txt = f"{e:+.3f}\n[{r['lo']:+.2f},{r['hi']:+.2f}]"
        col = "white" if abs(e) > 0.55 * vmax else "black"
        ax.text(j, i, txt, ha="center", va="center",
                fontsize=8.5, color=col)
        if r["robust"]:
            ec = "lime" if e > 0 else "magenta"
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                         fill=False, edgecolor=ec, lw=3))

cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cb.set_label("forgive main effect (success on - off)", fontsize=10)
fig.text(0.5, 0.005,
         "magenta box = robust but HARMFUL (no robustly-helpful cell); "
         "myopic row is a structural no-op (no replay to re-prioritise)",
         ha="center", fontsize=8, color="#444")
fig.tight_layout(rect=[0, 0.04, 1, 1])
fig.savefig("figs/atlas_forgive.png", dpi=130)
print("WROTE figs/atlas_forgive.png")
