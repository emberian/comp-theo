import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

d = json.load(open("atlas/detector.json"))
worlds = ["single", "two_basin", "community"]
Ns = [300, 600, 1000]
by = {(r["world"], r["N"]): r for r in d["jaccard"]}

fig, (axL, axR) = plt.subplots(1, 2, figsize=(13.2, 5.4))

# ---- LEFT: jaccard vs N per world ----
colors = {"single": "#3b7dd8", "two_basin": "#d8633b",
          "community": "#3bbf6a"}
for w in worlds:
    m = [by[(w, n)]["mean"] for n in Ns]
    s = [by[(w, n)]["std"] for n in Ns]
    axL.errorbar(Ns, m, yerr=s, marker="o", capsize=4, lw=2,
                 color=colors[w], label=w.replace("_", "-"))
    for n, mv in zip(Ns, m):
        axL.annotate(f"{mv:.2f}", (n, mv), textcoords="offset points",
                     xytext=(0, 8), ha="center", fontsize=8.5,
                     color=colors[w])
axL.axhline(1.0, ls=":", color="#888", lw=1)
axL.text(300, 1.01, "perfect detector (Jaccard=1)", fontsize=8.5,
         color="#888")
axL.axhspan(0, 0.2, color="#e0a33a", alpha=0.10)
axL.text(620, 0.025, "essentially no overlap with true basin",
         fontsize=8.5, color="#b07a1e")
axL.set_xticks(Ns)
axL.set_xlabel("world size N", fontsize=11)
axL.set_ylabel("Jaccard(detected, true basin)", fontsize=11)
axL.set_ylim(-0.03, 1.08)
axL.set_title("(a) Detector quality vs scale\n"
              "K.detect_basin (unsupervised MFPT trap-score), 6 seeds",
              fontsize=11)
axL.legend(title="world", fontsize=10)
axL.grid(alpha=0.25)

# ---- RIGHT: detected-vs-true main effects, fa / community ----
s = d["sensitivity"]
factors = ["vow", "forgive", "variety", "grace"]
det = s["detected"]
tru = s["true"]
x = np.arange(len(factors))
bw = 0.36

ed = [det[f][0] for f in factors]
edl = [det[f][0] - det[f][1] for f in factors]
edh = [det[f][2] - det[f][0] for f in factors]
et = [tru[f][0] for f in factors]
etl = [tru[f][0] - tru[f][1] for f in factors]
eth = [tru[f][2] - tru[f][0] for f in factors]

axR.bar(x - bw / 2, ed, bw, yerr=[edl, edh], capsize=3,
        color="#7d5bd8", label=f"detected basin "
        f"(jac={s['jac_detected']:.2f})")
axR.bar(x + bw / 2, et, bw, yerr=[etl, eth], capsize=3,
        color="#999999", label=f"true basin (jac={s['jac_true']:.2f})")
axR.axhline(0, color="#444", lw=1)
axR.axhline(0.02, ls=":", color="#b07a1e", lw=1)
axR.axhline(-0.02, ls=":", color="#b07a1e", lw=1)
axR.text(-0.45, 0.0205, "|eff|=0.02 robust gate", fontsize=7.5,
         color="#b07a1e", ha="left", va="bottom")

for i, f in enumerate(factors):
    vd = s["verdict_detected"][f]
    vt = s["verdict_true"][f]
    tag = "same" if vd == vt else "FLIP"
    axR.annotate(f"{vd}/{vt}\n{tag}", (i, max(ed[i], et[i]) + 0.004),
                 ha="center", fontsize=8,
                 color="#222" if tag == "same" else "#c0392b")

axR.set_xticks(x)
axR.set_xticklabels(factors, fontsize=11)
axR.set_ylabel("main effect (success on - off)", fontsize=11)
axR.set_title("(b) Verdict sensitivity: DETECTED vs TRUE basin\n"
              "agent=fa, world=community, N=700, 6 seeds; "
              "labels = verdict det/true", fontsize=11)
axR.legend(fontsize=9.5, loc="lower right")
axR.grid(alpha=0.25, axis="y")

flip = s["any_factor_flipped"]
fig.suptitle("Atlas — is the basin detector honest?  "
             f"(no verdict flips: {'NO' if flip else 'YES, claim holds'})",
             fontsize=12.5, y=1.02)
fig.tight_layout()
fig.savefig("figs/atlas_detector.png", dpi=130, bbox_inches="tight")
print("WROTE figs/atlas_detector.png")
