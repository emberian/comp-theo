## Transcription
COMPUTATIONAL THEOLOGY SERIES - 8 / 9

TROPICAL PROVIDENCE
Min-plus action, goodness thresholds, and the algebra of moral selection.

1. WHY TROPICAL?
Least-action search naturally uses min-plus composition: add along paths, minimize over alternatives.
Find path p* that minimizes total action:
p* = argmin_{p∈P(x,y)} S[p]

2. THREE QUANTITIES
- G = goodness: higher is better
- S[p] = action cost: lower is better
- J[p] = justice: higher is better
We measure each path. But composition across time and choice is the real problem.

3. WHAT ADDS, WHAT COMPETES, WHAT WINS
- What ADDS along a path: cost, penalties, damages.
- What COMPETES at a choice: alternative histories.
- What is allowed to WIN: constraints, threshold, lexicographic priorities.

4. WHAT ADDS, WHAT COMPETES, WHAT WINS
WHAT ADDS ALONG A PATH: COST, PENALTIES, DAMAGES
x = t_0 ... t_1 ... t_2 ... t_n
Path cost (action): S[p] = Σ t_t
Include penalties or damages: S[p] = Σ (t_t + p_t + d_t)
Min-plus composition over time: S[p · q] = S[p] + S[q]

WHAT COMPETES AT A CHOICE: ALTERNATIVE HISTORIES
Set of histories from x to y: P(x,y)
Tropical (min-plus) selection: S*[x,t] = min_{p∈P} S[p]
Composition wins by total cost. The minimum wins.

WHAT IS ALLOWED TO WIN: CONSTRAINTS, THRESHOLDS, LEXICOGRAPHIC PRIORITIES
- Constraints forbid paths that violate justice or other hard limits.
- Thresholds require enough goodness, or justice to qualify.
- Lexicographic rules rank goals in priority order: justice first, then cost, then path.

5. MIN-PLUS
The tropical (min-plus) algebra for path composition and choice.
Addition (choice): a ⊕ b = min(a,b)
Multiplication (composition): a ⊗ b = a + b
Paths add. Alternatives compete by minimum.

6. GOODNESS FLOORS
Minimize action subject to a floor on goodness.
Choose path p that minimizes S[p] subject to G[p] ≥ g_0.
p* = argmin_{S[p] | G[p] ≥ g_0}

7. JUSTICE CONSTRAINTS
Justice sets hard or soft limits.
Hard constraint (admissible set): P_J = {p ∈ P(x,y) | J[p] ≥ j_0}
S*[x,t] = min_{p∈P_J} S[p]
Soft constraint (penalize injustice): S[p] = S[p] + λ · max(0, j_0 - J[p])
Higher injustice, higher penalty.

8. LEXICOGRAPHIC RULES
Order goals by priority. Optimize in sequence.
1. Protect justice (hard constraint).
2. Minimize action among admissible.
3. Maximize goodness among minimizers.
Formally: traverse by lexigraphic order (J[p], -G[p], S[p])

9. MORAL POINT
The algebra we choose shapes reality.
- What we treat as additive becomes cumulative burden.
- What we let compete determines what can win.
- What we allow to rule defines the moral horizon.
Choosing the algebra is already an ethical decision.
Different agendas. Different worlds. Different justice.

PROVIDENCE MAY CONSIST IN CHOOSING THE ALGEBRA OF SELECTION: WHICH COSTS ACCUMULATE, WHICH PATHS COMPETE, AND WHICH CONSTRAINTS RULE.

## Visual
A tall dark mathematical infographic with cyan and gold linework on near-black, eighth in a numbered series. Numbered panels mix terse text with LaTeX-style tropical (min-plus) algebra equations and small lattice/path diagrams showing branching trajectories from x to y. A wide central panel 4 holds three sub-diagrams (adds/competes/wins) with node-graph illustrations. Lower panels include a small triangular lexicographic-priority motif and a closing bold serif banner.
