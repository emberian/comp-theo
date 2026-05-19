import sys, time, json, itertools
sys.path.insert(0, '.')
import lab5kit as K
import numpy as np

t0 = time.time()

# ---- (a) detector quality: Jaccard(Dhat, Dtrue) by world x N x seed ----
worlds = ["single", "two_basin", "community"]
Ns = [300, 600, 1000]
jaccard_rows = []
raw = {}
for world in worlds:
    for N in Ns:
        js = []
        for seed in range(6):
            rng = np.random.default_rng(seed)
            adj, cost, Dtrue, GOOD, esc = K.WORLDS[world](N, rng)
            Dhat, _ = K.detect_basin(adj, cost, GOOD, N)
            j = K.jaccard(Dhat, Dtrue)
            js.append(j)
        js = np.array(js)
        raw[(world, N)] = js.tolist()
        jaccard_rows.append(dict(world=world, N=N,
                                 mean=float(js.mean()),
                                 std=float(js.std())))
        print(f"{world:10s} N={N:4d}  jac mean={js.mean():.3f} "
              f"std={js.std():.3f}  {np.round(js,3).tolist()}",
              flush=True)

all_means = [r["mean"] for r in jaccard_rows]
print(f"\nMEAN JACCARD RANGE: {min(all_means):.3f} .. {max(all_means):.3f}\n",
      flush=True)

# ---- (b) verdict sensitivity: fa / community / N=700 ----
combos = [dict(zip(K.FACTORS, c))
          for c in itertools.product([0, 1], repeat=4)]

tab_det, jac_det = K.grid(K.WORLDS["community"], "fa", 700, range(6),
                          combos, world_seed=0, use_detected=True)
tab_tru, jac_tru = K.grid(K.WORLDS["community"], "fa", 700, range(6),
                          combos, world_seed=0, use_detected=False)
me_det = K.main_effects(tab_det)
me_tru = K.main_effects(tab_tru)


def robust(triple):
    e, lo, hi = triple
    return (lo > 0 or hi < 0) and abs(e) > 0.02


def verdict(triple):
    e, lo, hi = triple
    if robust(triple):
        return "+" if e > 0 else "-"
    return "0"


sens_det = {f: [float(x) for x in me_det[f]] for f in K.FACTORS}
sens_tru = {f: [float(x) for x in me_tru[f]] for f in K.FACTORS}

print(f"detected jac(Duse,Dtrue)={jac_det:.3f}  "
      f"true jac={jac_tru:.3f}\n")
flips = []
for f in K.FACTORS:
    vd, vt = verdict(me_det[f]), verdict(me_tru[f])
    flipped = vd != vt
    if f in ("variety", "grace") and flipped:
        flips.append(f)
    print(f"  {f:8s} DET e={me_det[f][0]:+.4f} "
          f"CI[{me_det[f][1]:+.4f},{me_det[f][2]:+.4f}] -> {vd}   |   "
          f"TRUE e={me_tru[f][0]:+.4f} "
          f"CI[{me_tru[f][1]:+.4f},{me_tru[f][2]:+.4f}] -> {vt}   "
          f"{'FLIP' if flipped else 'same'}", flush=True)

any_flip = any(verdict(me_det[f]) != verdict(me_tru[f])
               for f in K.FACTORS)
focus_flip = any(verdict(me_det[f]) != verdict(me_tru[f])
                 for f in ("variety", "grace"))

out = {
    "slice": "detector",
    "backbone": "lab5kit / labcore (Rust engine)",
    "jaccard": jaccard_rows,
    "jaccard_raw": {f"{w}|{n}": v for (w, n), v in raw.items()},
    "sensitivity": {
        "agent": "fa", "world": "community", "N": 700, "seeds": 6,
        "jac_detected": float(jac_det), "jac_true": float(jac_tru),
        "criterion": "95%CI excludes 0 AND |effect|>0.02",
        "detected": sens_det,
        "true": sens_tru,
        "verdict_detected": {f: verdict(me_det[f]) for f in K.FACTORS},
        "verdict_true": {f: verdict(me_tru[f]) for f in K.FACTORS},
        "any_factor_flipped": bool(any_flip),
        "variety_or_grace_flipped": bool(focus_flip),
    },
    "wall_s": round(time.time() - t0, 1),
}
with open("atlas/detector.json", "w") as f:
    json.dump(out, f, indent=2)

print(f"\nANY VERDICT FLIP (any factor)={any_flip}  "
      f"(variety/grace)={focus_flip}")
print(f"WALL {time.time()-t0:.1f}s")
