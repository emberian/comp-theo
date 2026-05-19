## Transcription
ORDERED CREATION / JUSTICE & LEAST-ACTION SERIES · 4 / 9

α  
Ω

TROPICAL ALGEBRA  
OF PROVIDENCE

η  
α

Using min-plus and max-plus composition to think  
about action, value, and path selection.

TROPICAL SEMIRING  
(MIN-PLUS)

a ⊕ b = min(a, b)

a ⊗ b = a + b

SEMIRING TABLES (MIN-PLUS)

a ⊕ b = min(a, b)

| ⊕ | 0 | 1 | 2 | ∞ |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 |
| 1 | 0 | 1 | 1 | 1 |
| 2 | 0 | 1 | 2 | 2 |
| ∞ | 0 | 1 | 2 | ∞ |

∞ is additive identity: a ⊕ ∞ = a  
0 is additive absorbing: a ⊕ 0 = 0

a ⊗ b = a + b

| ⊗ | 0 | 1 | 2 | ∞ |
|---|---|---|---|---|
| 0 | 0 | 1 | 2 | ∞ |
| 1 | 1 | 2 | 3 | ∞ |
| 2 | 2 | 3 | 4 | ∞ |
| ∞ | ∞ | ∞ | ∞ | ∞ |

0 is multiplicative identity: a ⊗ 0 = a  
∞ is multiplicative absorbing: a ⊗ ∞ = ∞

DUAL MAX-PLUS VIEW  
(MAX-PLUS)

a ⊕ b = max(a, b)

a ⊗ b = a + b

PATH COMPOSITION: ADD ALONG, MIN OVER ALTERNATIVES

Local action terms add  
along a path (⊗ = +).

Path selection happens  
by min (⊕ = min).

Start  
Goal  
Edge (x → y)  
with local cost L(x, y)

x₀  
a  
b  
c  
xT

L(x₀, a) = 2  
L(x₀, b) = 1  
L(x₀, c) = 3  
L(a, xT) = 3  
L(b, xT) = 4  
L(c, xT) = 2

Path costs (additive):  
x₀ → a → xT : 2 + 3 = 5  
x₀ → b → xT : 1 + 4 = 5  
x₀ → c → xT : 3 + 2 = 5

Path selection (min):  
V(x₀, xT) = min{5, 5, 5} = 5

General path value:  
V(x₀, xT) = min_{π ∈ P(x₀,xT)} Σ_{k=0}^{T−1} L(x_k, x_{k+1})

BELLMAN RECURSION  
(TROPICAL DYNAMIC PROGRAMMING)

V(x) = min_y [ L(x, y) + V(y) ]

V(x) is the least action-to-go from x.  
Terminal condition: V(x_terminal) = 0.  
Compute V by iterating until convergence.

WHY THIS MATTERS HERE

LEAST-ACTION SEARCH  
is naturally min-plus.  
We ADD costs along  
paths and take the  
MIN over alternatives.

GOODNESS AGGREGATION  
may look max-like  
or threshold-like.

threshold

MIN-PLUS vs. MAX-PLUS INTUITION

Min-plus (least action)  
• Lower is better  
• Costs accumulate  
• Selection is min

Max-plus (goodness)  
• Higher is better  
• Values accumulate  
• Selection is max

In providential reasoning, both may appear. Frame clearly which semiring governs which layer.

COMPOSING MORAL AND DYNAMICAL QUANTITIES WITH TROPICAL IDEAS

COST PENALTIES  
(additive in path)  
Add penalties to local cost.  
They accumulate.

L′(x, y) = L(x, y) + P(x, y)

JUSTICE PENALTIES  
(weighted costs)  
Encode injustice as cost.  
Heavier = steer away.

L′(x, y) = L(x, y) + J(x, y)

GOODNESS FLOORS  
(threshold constraints)  
Require goodness ≥ τ  
or pay a large penalty.

L′(x, y) = L(x, y) +  
{ 0 if G(x, y) ≥ τ  
  M if G(x, y) < τ }

LEXICOGRAPHIC MINIMA  
(ordered priorities)  
Minimize in layers:  
primary before secondary.

Primary (e.g., justice)  
⊕  
Secondary (e.g., cost)  
⊕  
Tertiary (e.g., ease)

SOFT CONSTRAINTS  
(soft weights)  
Soften constraints via  
finite penalties.

L′(x, y) = L(x, y) + w · c(x, y)  
w ≥ 0

All are min-plus compositions. Only the design of L′ and the constraint scheme changes what the search prefers.

THREE ARCHITECTURES FOR ACTION SELECTION

① PURE LEAST-ACTION  
Minimize total cost.

V(x) = min_y [ L(x, y) + V(y) ]

Seeks the easiest path.  
Blind to value unless  
encoded as cost.

② GOODNESS-WEIGHTED  
LEAST-ACTION

Minimize cost, but encode  
goodness as negative cost  
or floor/bonus.

L′(x, y) = L(x, y) − λ · G(x, y)  
V(x) = min_y [ L′(x, y) + V(y) ]

Rewards good outcomes  
while still counting cost.

③ JUSTICE-CONSTRAINED  
LEAST-ACTION

Minimize cost subject to  
justice constraints.

J(x, y) ≤ κ (hard)  
or  
L′(x, y) = L(x, y) + J(x, y)  
(soft)

V(x) = min_y [ L′(x, y) + V(y) ]

Protects justice first,  
then seeks least action  
within allowable space.

WARNING

Tropical elegance does  
not solve the ethical  
problem by itself.

It only clarifies  
composition.

PROVIDENTIAL READING

God may set the algebra of selection:

WHAT ADDS  
Which quantities  
accumulate along  
the way.

WHAT COMPETES  
Which alternatives  
confront each other  
at choices.

WHAT IS ALLOWED  
TO WIN  
Which constraints  
can veto, cap,  
or permit.

Not all values are of the  
same kind. The algebra  
we choose is already  
a moral decision.

THESIS

Tropical algebra gives a language for composing  
ease, value, and constraint.

## Visual
A tall, ornate dark infographic uses gold/copper borders, teal accents, and classical serif/small-cap typography. The layout stacks panels from definitions and semiring tables at the top, through a central path graph and Bellman recursion, into moral constraint variants, action-selection architectures, warnings, and a thesis footer. Node-link networks, arrows, threshold curves, justice scales, compass-like ornaments, and theological iconography visually connect algebraic path selection with ethical and providential framing.
