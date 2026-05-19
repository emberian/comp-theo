"""Robustness-atlas slice (lab4-A): universality of the SCALING LAW.

Does "bare-agent collapse is predicted by the reference exit time tau"
(lab4's headline A) hold across EVERY instrument (3 agents x 3 worlds)?
Read-only on lab5kit backbone.

lawful iff rho > 0.6 (Spearman B/tau vs bare success).
"""
import json
import sys
import time

sys.path.insert(0, ".")
import numpy as np

import lab5kit as K

AGENTS = ["myopic", "tabular", "fa"]
WORLDS = ["single", "two_basin", "community"]
Ns = [200, 350, 500, 750, 1000, 1400]

t0 = time.time()
grid = []
for agent in AGENTS:
    for world in WORLDS:
        rows, rho = K.scaling_law(K.WORLDS[world], agent, Ns,
                                  seeds=range(5))
        lawful = bool(rho > 0.6)
        rrows = [[int(N), float(tau), float(bt), float(s)]
                 for (N, tau, bt, s) in rows]
        grid.append(dict(agent=agent, world=world,
                         rho=round(float(rho), 6), lawful=lawful,
                         rows=rrows))
        print(f"{agent:8s} {world:10s} rho={rho:+.4f} "
              f"lawful={lawful}", flush=True)

out = dict(slice="scaling", grid=grid,
           backbone="lab5kit / labcore (Rust engine)",
           Ns=Ns, seeds=5,
           criterion="lawful iff Spearman(B/tau, success) rho > 0.6",
           wall_s=round(time.time() - t0, 1))
with open("atlas/scaling.json", "w") as f:
    json.dump(out, f, indent=1)
print("WROTE atlas/scaling.json  wall_s=", out["wall_s"])
