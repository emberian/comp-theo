import sys, time, json
sys.path.insert(0, '.')
import lab5kit as K
import numpy as np

t0 = time.time()
agents = ["myopic", "tabular", "fa"]
worlds = ["single", "two_basin", "community"]
grid = []

for agent in agents:
    for world in worlds:
        tab, jac = K.full_factorial(
            K.WORLDS[world], agent, N=600, seeds=range(6),
            world_seed=hash((agent, world)) % 1000)
        me = K.main_effects(tab)
        eff, lo, hi = me["forgive"]
        robust = (lo > 0 or hi < 0) and abs(eff) > 0.02
        if eff > 0:
            sign = "+"
        elif eff < 0:
            sign = "-"
        else:
            sign = "0"
        grid.append(dict(agent=agent, world=world, effect=float(eff),
                         lo=float(lo), hi=float(hi), jaccard=float(jac),
                         robust=bool(robust), sign=sign))
        print(f"{agent:8s} {world:10s} forgive={eff:+.4f} "
              f"CI[{lo:+.4f},{hi:+.4f}] jac={jac:.3f} "
              f"robust={robust} {sign}")

wall = time.time() - t0
out = {
    "slice": "forgive",
    "mechanism": "forgive",
    "backbone": "lab5kit / labcore (Rust engine)",
    "N": 600,
    "seeds": 6,
    "criterion": "95%CI excludes 0 AND |effect|>0.02",
    "grid": grid,
    "wall_s": round(wall, 1),
}
with open("atlas/forgive.json", "w") as f:
    json.dump(out, f, indent=2)
print(f"WALL {wall:.1f}s -> atlas/forgive.json")
