"""Small-multiples 3x3 grid: bare success vs B/tau (log x), one panel per
(agent x world), annotated with Spearman rho and lawful verdict."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

d = json.load(open("atlas/scaling.json"))
agents = ["myopic", "tabular", "fa"]
worlds = ["single", "two_basin", "community"]
by = {(r["agent"], r["world"]): r for r in d["grid"]}

fig, axes = plt.subplots(3, 3, figsize=(11.4, 9.2), sharey=True)
for i, a in enumerate(agents):
    for j, w in enumerate(worlds):
        ax = axes[i][j]
        r = by[(a, w)]
        rows = np.array(r["rows"])           # N, tau, B/tau, success
        Ns, bt, sc = rows[:, 0], rows[:, 2], rows[:, 3]
        sccol = ax.scatter(bt, sc, c=Ns, cmap="viridis", s=46,
                           edgecolor="k", linewidth=0.4, zorder=3)
        ax.set_xscale("log")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(alpha=0.25, zorder=0)
        lawful = r["lawful"]
        col = "#1a7f1a" if lawful else "#c0392b"
        ax.text(0.04, 0.93,
                f"rho={r['rho']:+.2f}  {'LAWFUL' if lawful else 'FAILS'}",
                transform=ax.transAxes, fontsize=10.5, fontweight="bold",
                color=col, va="top",
                bbox=dict(boxstyle="round", fc="white", ec=col, alpha=0.9))
        for s in ax.spines.values():
            s.set_edgecolor(col)
            s.set_linewidth(2.0 if lawful else 1.6)
        if i == 0:
            ax.set_title(w.replace("_", "-"), fontsize=12,
                         fontweight="bold")
        if j == 0:
            ax.set_ylabel(f"{a}\nbare success", fontsize=11)
        if i == 2:
            ax.set_xlabel("B / tau  (log)", fontsize=10)

fig.suptitle("Is the tau-scaling law universal?  bare-agent success vs "
             "budget/exit-time (B/tau), coloured by N\n"
             "lab4-A across every instrument  -  green = lawful "
             "(rho>0.6),  red = law fails",
             fontsize=12.5, y=0.99)
cb = fig.colorbar(sccol, ax=axes, fraction=0.022, pad=0.015)
cb.set_label("graph size N", fontsize=10)
fig.savefig("figs/atlas_scaling.png", dpi=130, bbox_inches="tight")
print("WROTE figs/atlas_scaling.png")
