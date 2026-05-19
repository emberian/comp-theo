## Transcription
ORDERED CREATION / JUSTICE & LEAST-ACTION SERIES · 3 / 9

HOW DO WE COMPOSE GOOD AND ACTION?

Multi-objective architectures for goodness G, action S[p], and justice J.

1) SPACE OF POSSIBLE HISTORIES
- Low action
- Low path
- High good
- Just path
- Other paths
- start
Histories p run paths from x_0 to x_T. They differ in goodness G(p), action cost S[p], and justice J[p].

2) GOODNESS-ACTION TRADEOFF
G(p) Goodness
Infeasible (cannot be realized by physics-law constraints)
Pareto frontier (efficient balance)
Feasible region (admissible histories)
Lower is better for S (cost)
S[p] Action cost
Lower action = lower cost

COMPOSITION SCHEMES
# — SCHEME — FORMAL RULE (OR LOGIC) — INTUITIVE MEANING — PROVIDER — FAILURE MODE
1 — maximize G directly — p* = arg max G[p] — Choose the history with the greatest goodness. — Direct moral aim; no dilution. — May require extreme or wasteful action; ignores justice.
2 — minimize S[p] directly — p* = arg min S[p] — Choose the most efficient (least-action) history. — Parsimony; conserves resources. — Can yield little good; may tolerate injustice.
3 — maximize G[p] then minimize S — Let P_eff = arg max G[p]; p* = arg min_{p∈P_eff} S[p] — Among the most efficient option, choose the most good. — Efficiency first, enriched by good. — Good is constrained by an over-tight efficiency filter.
4 — maximize G[p] then minimize S[p] — Let P_eff = arg max G[p]; p* = arg min_{p∈P_eff} S[p] — Among the best goods, choose the least costly way. — Protects high good; adds efficiency as tie-breaker. — If many meet high good rank, may still be costly overall.
5 — maximize (G − λS)[p] — p* = arg max (G[p] − λS[p]); λ > 0 is a weight — Trade goodness against action by a chosen weight. — Simple, tunable; traces points on the Pareto frontier. — Requires choosing λ; one weight fits not all cases.
6 — maximize G[p] subject to S ≤ B_s — p* = arg max G[p] subject to S[p] ≤ B_s — Achieve at least a target goodness with minimal cost. — Guarantees a goodness floor; efficient among acceptable goals. — If goods too high or B_s infeasible or very expensive.
7 — minimize S[p] subject to J(x) ≥ ... — p* = arg min S[p] subject to J[p] ≥ J_0 — Within a cost budget, get the most good. — Respects hard limits (resources, time, capacity). — Budget may be too small to achieve meaningful good.
8 — joint optimization — p* = arg max U(G[p], −S[p], J[p]) (with Pareto or utility U) — Evaluate and balance all three objectives at once. — Handles tradeoffs explicitly; flexible and principled. — Composite needs transparent U and data on J.

KEY DISTINCTION
G ≠ J
Efficient is not identical to good, and good is not identical to just.

WHERE JUSTICE ENTERS
- As a WEIGHT: Add J[p] with a weight μ. Maximize G − λS + μJ. Justice influences the balance.
- As a HARD CONSTRAINT: Require J[p] ≥ J_0; set unjust constraint G_s(p); only fair histories are admissible.
- As a PENALTY FOR EXTERNALIZED HARM: Subtract a penalty when harm is uncompensated; histories that defer or hide injustice cost more.
- As a FINAL SELECTION OF HISTORIES: One picks G & S; then picks the history with highest J; justice ranks the final goods.
Justice can shape the arc, the score, or the final choice.

MAP OF THE COMPOSITION SPACE
Goodness G
Action S[p]
Justice J
Interpretation: each answer puts weight G and S, or scale, and constrain just paths.

ALGORITHMIC VIEW (ABSTRACTION)
Score histories by admissible histories P
Score function: U[G[p], S[p], J[p]] Measure & model
Select p* by chosen composition rule
Act along p*
Reuse & learn: Update measures & rule if needed

Composition is the real problem—not whether action or goodness exist, but how they are ordered.

Theological plausibility lives in the composition rule.
Measure carefully. Choose transparently. Remain answerable.

## Visual
A tall dark ornate poster with gold linework, scale and constellation motifs on a near-black background, alchemical-treatise style. The top pairs a star-map "space of histories" with a goodness-vs-action Pareto-frontier plot. The dominant central element is a large eight-row composition-schemes table with formal rules and failure modes. Lower panels show a balance-scale "key distinction" (G ≠ J), a "where justice enters" list, a triangular composition-space map, and an algorithmic flow, closing with two italic thesis lines.
