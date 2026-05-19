"""Robustness-atlas slice: the VARIETY mechanism's main effect across
every instrument (3 agents x 3 worlds). Read-only on lab5kit backbone.

robust iff 95%CI excludes 0 AND |effect| > 0.02.
"""
import json
import sys
import time

sys.path.insert(0, ".")
import numpy as np

import lab5kit as K

AGENTS = ["myopic", "tabular", "fa"]
WORLDS = ["single", "two_basin", "community"]

t0 = time.time()
grid = []
for agent in AGENTS:
    for world in WORLDS:
        ws = hash((agent, world)) % 1000
        tab, jac = K.full_factorial(
            K.WORLDS[world], agent, N=600, seeds=range(6), world_seed=ws)
        me = K.main_effects(tab)
        eff, lo, hi = me["variety"]
        robust = bool((lo > 0 or hi < 0) and abs(eff) > 0.02)
        sign = "+" if eff > 0 else ("-" if eff < 0 else "0")
        row = dict(agent=agent, world=world,
                   effect=round(eff, 6), lo=round(lo, 6), hi=round(hi, 6),
                   jaccard=round(float(jac), 6), robust=robust, sign=sign)
        grid.append(row)
        print(f"{agent:8s} {world:10s} variety={eff:+.4f} "
              f"CI[{lo:+.4f},{hi:+.4f}] jac={jac:.3f} "
              f"robust={robust}", flush=True)

out = dict(
    slice="variety",
    mechanism="variety",
    backbone="lab5kit / labcore (Rust engine)",
    N=600, seeds=6,
    criterion="95%CI excludes 0 AND |effect|>0.02",
    grid=grid,
    wall_s=round(time.time() - t0, 1),
)
with open("atlas/variety.json", "w") as f:
    json.dump(out, f, indent=1)
print("WROTE atlas/variety.json  wall_s=", out["wall_s"])
