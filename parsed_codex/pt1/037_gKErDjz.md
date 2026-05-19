## Transcription

ORDERED CREATION / JUSTICE & LEAST-ACTION SERIES · 3 / 9

HOW DO WE COMPOSE  
GOOD AND ACTION?

Multi-objective architectures for goodness G, action S[p], and justice J.

α  
Ω  
η  
α

1) SPACE OF POSSIBLE HISTORIES

Low-action path (eff.)  
High-good path  
Just path (different)  
Other paths

x_0 start  
x_T end

x_0  
x_T

Histories p are paths from x_0 to x_T.  
They differ in goodness G[p], action cost S[p], and justice J[p].

2) GOODNESS–ACTION TRADEOFF

Goodness  
G

Infeasible  
(ruled out by  
physics, logic,  
or constraints)

Pareto  
frontier  
(efficient  
histories)

Feasible region  
(achievable  
histories)

Lower is better  
for S (cost)

Lower is better for S (cost) →

Action cost  
S[p]

COMPOSITION SCHEMES

#  
SCHEME  
FORMAL RULE (for a history p)  
INTUITIVE MEANING  
PROMISE  
FAILURE MODE

1  
maximize  
G directly  
p* = arg max_p G[p]  
Choose the history  
with the greatest  
goodness.  
Direct moral aim;  
no dilution.  
May require extreme or  
wasteful action;  
ignores justice.

2  
minimize  
S[p] directly  
p* = arg min_p S[p]  
Choose the most  
efficient (least-action)  
history.  
Parsimony;  
conserves resources.  
Can yield little good;  
may tolerate injustice.

3  
minimize S[p]  
then maximize G  
Let P_min = arg min_p S[p]  
p* = arg max_{p ∈ P_min} G[p]  
Among the most efficient  
options, choose the most  
good.  
Efficiency first;  
tie-break by good.  
Good is constrained  
by an overly tight  
efficiency filter.

4  
maximize G  
then minimize S[p]  
Let P_max = arg max_p G[p]  
p* = arg min_{p ∈ P_max} S[p]  
Among the best goods,  
choose the least costly  
way.  
Protects high good;  
adds efficiency  
as tie-breaker.  
If many near-tied goods  
exist, may still be  
costly overall.

5  
maximize  
G − λS[p]  
p* = arg max_p {G[p] − λS[p]}  
λ > 0 is a weight.  
Trade goodness  
against action by  
a chosen weight.  
Simple, tunable;  
traces points on the  
Pareto frontier.  
Requires choosing λ;  
one weight fits none  
across all cases.

6  
minimize S[p]  
subject to G ≥ g_0  
p* = arg min_p S[p]  
subject to G[p] ≥ g_0.  
Achieve at least a  
target goodness with  
minimal cost.  
Guarantees a goodness  
floor; efficient among  
acceptable goods.  
If g_0 too high, may be  
infeasible or very  
expensive.

7  
maximize G  
subject to S[p] ≤ s_0  
p* = arg max_p G[p]  
subject to S[p] ≤ s_0.  
Within a cost budget,  
get the most good.  
Respects hard limits  
(resources, time,  
capacity).  
Budget may be too  
small to achieve  
meaningful good.

8  
joint optimization  
over (G, S, J)  
p* = arg max_p U(G[p], −S[p], J[p])  
(with Pareto or utility U)  
Evaluate and balance  
all three objectives  
at once.  
Handles tradeoffs  
explicitly; flexible  
and principled.  
Complex; needs  
transparent U and  
data on J.

KEY DISTINCTION

G  
J  
S[p]

Efficient is not identical to good,  
and good is not identical to just.

WHERE JUSTICE ENTERS

AS A WEIGHT  
Add J[p] with a weight μ.  
Maximize G − λS + μJ.  
Justice influences the balance.

AS A HARD CONSTRAINT  
Require J[p] ≥ J_0 (or satisfy  
constraints C_J[p]). Only just  
histories are admissible.

AS A PENALTY FOR  
EXTERNALIZED HARM  
Subtract μH_ext[p] where H_ext  
measures harm shifted to others  
or future persons.

AS A FINAL EVALUATOR  
OF HISTORIES  
First pick by G,S; then prefer the  
history with higher J[p] among  
equally good & efficient options.

Justice can shape the set, the score, or the final choice.

MAP OF THE COMPOSITION SPACE

Goodness  
G

Action cost  
S (low is better)

Justice  
J

Interpretation  
Each interior point  
weights G, S, and J  
in some way.  
Different rules pick  
different regions  
or points.  
There is no single  
correct corner.

ALGORITHMIC VIEW (ABSTRACTION)

Define world  
& admissible  
histories P

Score histories  
(G[p], S[p], J[p])  
Measure & model

Choose rule  
(1–8 above)  
Set parameters

Select p* by chosen composition rule

Act along p*

Reassess & learn  
Update measures  
& rule if needed

Composition is the real problem—not whether action or goodness exists, but how they are ordered.

Theological plausibility lives in the composition rule.

Measure carefully. Choose transparently. Remain answerable.

## Visual

A dark, gold-on-black illuminated-manuscript poster combines scientific diagrams, theological ornament, and tabular formalism. The layout moves from two top explanatory panels into a large central comparison table, then into smaller bottom panels showing scales, justice mechanisms, a triangular composition map, and an algorithmic flowchart. Visual motifs include star charts, network paths, Pareto curves, balance scales, a lock, an hourglass, and glowing celestial geometry, using serif small caps, teal/yellow/red accents, and aged parchment-like linework.
