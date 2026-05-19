## Transcription
ORDERED CREATION / LEAST-ACTION SERIES · 2 / 8

ACTION ON AN ORDERED WORLD

Defining a cost functional on a poset and its cover graph.

"Action prices lawful change." — least-action principle

ORDERED STATE SPACE (POSET) AND COVER GRAPH

FINITE POSET (PARTIAL ORDER)
Rank 4
Rank 3
Rank 2
Rank 1
Rank 0
x_0 ... x_T

COVER GRAPH (HASSE DIAGRAM)
x_0 ... x_T
How to read this:
- Every upward edge respects the order (x ≤ y).
- Paths traverse by 1 along each cover.
- Moves are only allowed along cover edges.

- state
- cover relation
- p (order route)
- core (immediate states)

WHAT CONTRIBUTES TO ACTION?
- GEOMETRY (DISTANCE): Spatial separation between adjacent states.
- ASCENT THROUGH ORDER: Climbing to higher rank carries a price.
- BOUNDARY CROSSINGS: Leaving the interior or entering forbidden zones registers costs more.
- WEAK LINKS: Edges with low capacity or reliability add cost.
- DISSIPATION / DRAIN: Irreversible effort, friction, leakage cost.

LOCAL ACTION DENSITY
DISCRETE LAGRANGIAN (LOCAL COST)
L(x_t, x_{t+1}) = α · d(x_t, x_{t+1})
+ β · Δrank(x_t, x_{t+1})
+ γ · 1_∂(x_t, x_{t+1})
+ ε · w(x_t, x_{t+1})
+ ζ · diss(x_t, x_{t+1})
d = distance (geometry)
Δrank = rank change (0 or +1)
1_∂ = boundary crossing (0 or 1)
w = weak-link penalty (≥ 0)
diss = dissipation / drag (≥ 0)

COST CONTRIBUTIONS
α, β, γ, ε, ζ ≥ 0

PATH ACTION
S[p] = Σ_t L(x_t, x_{t+1})
Total action is the sum of local costs along the path.

EXAMPLE PATHS FROM x_0 TO x_T
LOW-ACTION PATH (preferred)
Step,state — Value
TOTAL ACTION: 8.0
MEDIUM-ACTION PATH
Step,state — Value
TOTAL ACTION: 19.0
HIGH-ACTION PATH
Step,state — Value
TOTAL ACTION: 32.0

DESIGN CHOICE
We do not merely declare a goal and hope to reach it.
We engineer the worldsystem by engineering:
- ADJACENCY: who can connect to whom
- LOCAL COSTS: what each move costs
- CONSTRAINTS: which moves are legal
- REALIZATION: low costs are perceived as good outcomes

THESIS
Once the state space is ordered, action is a rule that assigns price to every lawful move. Trajectories differ not only by destination, but by what they cost to realize.

THE PROCESS
- DISTINCTION: Differentiate the state space.
- ORDER: Impose a partial order (poset).
- LOCAL COST: Assign prices to lawful moves.
- ACCUMULATE ACTION: S[p] — Sum local costs along a path.
- LOW-ACTION PATH: Select the path of least action.

SERIES ROADMAP · 2 / 8: 1 Shift Objective  2 Action Design  3 Path Ensembles  4 Open Systems  5 Emergent Goods  6 Stability & Bounds  7 Realization  8 Synthesis

## Visual
A tall Swiss/Bauhaus poster with red, black, blue, and yellow blocks on cream stock and heavy condensed headlines. The upper left shows a ranked finite-poset lattice and an adjacent Hasse cover graph with a highlighted path. The right column lists "what contributes to action" with circular icons. The middle holds a boxed discrete Lagrangian; the lower left compares three example paths (low/medium/high action) in tinted panels. A horizontal five-step process strip and a roadmap footer close the page.
