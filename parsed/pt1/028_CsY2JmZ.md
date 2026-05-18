## Transcription

ORDERED CREATION / LEAST-ACTION SERIES • 2 / 8

ACTION ON AN  
ORDERED WORLD

Defining a cost functional on a poset and its cover graph.

“Action prices  
lawful change.”  
— least-action  
principle

ORDERED STATE SPACE (POSET) AND COVER GRAPH

higher  
(order)

FINITE POSET (PARTIAL ORDER)

COVER GRAPH (HASSE DIAGRAM)

x_T  
top

Rank 4  
Rank 3  
Rank 2  
Rank 1  
Rank 0

x_0  
bottom

How to read this  
• Every upward edge respects the order (x ≤ y).  
• Ranks increase by 1 along each cover.  
• Moves are only allowed along cover edges.

state  
state (in cover graph)  
≤ (order relation)  
cover (immediate relation)

WHAT CONTRIBUTES  
TO ACTION?

GEOMETRY (DISTANCE)  
Spatial separation between  
adjacent states.

ASCENT THROUGH ORDER  
Climbing to higher rank  
carries a price.

SWITCHING COST  
Changing direction or choice  
incurs a penalty.

BOUNDARY CROSSINGS  
Leaving the interior or  
entering forbidden/rare  
regions costs more.

WEAK LINKS  
Edges with low capacity  
or reliability add cost.

DISSIPATION / DRAG  
Irreversible effort, friction,  
or information loss.

COST CONTRIBUTIONS  
geometry  
other penalties  
order ascent  
sum (total action)

LOCAL ACTION  
DENSITY

DISCRETE LAGRANGIAN (LOCAL COST)

L(x_t, x_{t+1}) = α · d(x_t, x_{t+1})  
+ β · Δ rank(x_t, x_{t+1})  
+ χ · 1_∂(x_t, x_{t+1})  
+ η · w(x_t, x_{t+1})  
+ ζ · diss(x_t, x_{t+1})

d        distance (geometry)  
Δ rank   rank change (0 or +1)  
1_∂      boundary crossing (0 or 1)  
w        weak-link penalty (≥ 0)  
diss     dissipation / drag (≥ 0)

PATH ACTION

S[p] = Σ_t L(x_t, x_{t+1})

Total action is the sum of  
local costs along the path.

EXAMPLE PATHS  
FROM x_0 TO x_T

LOW-ACTION PATH (Preferred)

x_T  
x_0

Step costs    Value  
geometry      6.0  
order ascent  3.0  
switching     1.0  
boundary      0.0  
weak links    0.5  
dissipation   0.5

TOTAL ACTION 11.0

MEDIUM-ACTION PATH

x_T  
x_0

Step costs    Value  
geometry      9.0  
order ascent  4.0  
switching     2.5  
boundary      1.0  
weak links    1.0  
dissipation   1.5

TOTAL ACTION 19.0

HIGH-ACTION PATH

x_T  
x_0

Value  
14.0  
5.0  
4.5  
2.0  
3.0  
3.5

TOTAL ACTION 32.0

All paths start at x_0 (bottom) and end at x_T (top). Only cover edges are used.

DESIGN CHOICE

We do not merely declare a goal  
and hope to reach it.

We engineer the worldsystem  
by engineering:

ADJACENCY  
who can connect to whom

LOCAL COSTS  
what each move costs

CONSTRAINTS  
which moves are legal

FEEDBACK  
how costs are perceived  
and learned

Right structure, right prices,  
right flows.

THESIS

..

Once the state space is ordered, action is a rule that assigns price  
to every lawful move. Trajectories differ not only by destination,  
but by what they cost to realize.

THE PROCESS

DISTINCTION  
Differentiate the  
state space.

ORDER  
Impose a partial  
order (poset).

LOCAL COST  
Assign prices to  
lawful moves.

ACCUMULATED ACTION  
S[p]  
Sum local costs  
along a path.

LOW-ACTION ROUTE  
Select the path  
of least action.

SERIES ROADMAP (8 PARTS)  
1 Order & Intention • 2 Order & Prices • 3 Action & Path Selection • 4 Path Ensembles • 5 Open Systems • 6 Emergent Goods • 7 Scaling & Recursion • 8 Realization

## Visual

A dense infographic poster with a large typographic title, a central poset/Hasse diagram, side explanatory panels, formula blocks, and bottom process panels connected by arrows. The visual language uses cream paper texture, heavy black condensed type, red and teal emphasis, blue/red/black/teal diagram paths, and small geometric icons for cost components. The main meaning-bearing figures are the ordered graph, three example paths with different action totals, and the process chain showing how distinction becomes order, local cost, accumulated action, and route selection.
