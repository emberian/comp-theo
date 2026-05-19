## Transcription
ORDERED CREATION / LEAST-ACTION SERIES · 3 / 8

LOW-ACTION SEARCH

From quantum-walk search to stationary-action path selection.

"We prefer the paths that nature herself is most willing to take."

TWO VIEWS OF DYNAMICS

Ordinary marked search
Find the marked target w by exploring the graph.
x_0 ... w
- diffuse exploration
- no preference among admissible paths
- arrival amplitude spreads across many routes

VS.

Low-action search
Many admissible paths compete; low-action trajectories win.
x_0 ... x_T = w
p*
p_1, p_2, p_3
- low action (high weight)
- medium action
- high action (low weight)

PATH ENSEMBLE
A(x_0 → x_T) = Σ_{p ∈ P(x_0, x_T)} e^{−S[p]/τ}
S[p] = Σ_t L(x_t, x_{t+1})  (action of path p)
τ = action temperature (control sharpness)
Lower action S[p] receives higher effective weight.

QUANTUM IDIOM (COMPARE)
In a more quantum setting, compare phase-weights:
A_q(x_0 → x_T) = Σ_p e^{iS[p]/ℏ}
Stationary bases stationary-action paths.

CANDIDATE PATHS THROUGH AN ORDERED GRAPH
Path action — low / medium / high
x_0 ... x_T = w
low thickness indicates effective weight
higher action (lower weight)

ARRIVAL PROFILE AT TARGET
arrival probability (or amplitude magnitude)
- low-action arrival: high amplitude, early
- medium action
- high-action: low broad amplitude
time steps
Low-action trajectories arrive earlier, sharper arrival.

INTERPRETATION
Search is no longer merely "find the good node"; it becomes "distribute amplitude over lawful trajectories and let low-action paths dominate."

CONSEQUENCES
- CONCENTRATION: Amplitude concentrates on efficient paths, accelerating arrival.
- ROBUSTNESS: Graceful adaptation to perturbations in the landscape.
- AVOIDANCE OF BRITTLE DETOURS: High-action cul-de-sacs naturally carry little weight.
- PATH COMPETITION: Multiple paths can share the load constructively.

THESIS
Action minimization replaces explicit maximization of goodness with a lawful bias toward efficient trajectories.

SERIES ROADMAP (8 PARTS): 1 Shift Objective  2 Order & Price  3 Low-Action Search  4 Path Ensembles  5 Open Systems  6 Emergent Goods  7 Scaling & Recursion

## Visual
A tall Swiss/Bauhaus poster with red, black, blue, and yellow blocks on cream paper with heavy condensed headlines. The "Two Views of Dynamics" band contrasts an ordinary marked-search scatter graph against a low-action search graph with a bold red minimizing path among lighter competing paths. Below sit boxed path-ensemble equations, a candidate-paths graph, and an arrival-profile plot with sharp early peaks. A consequences row of icon panels and a thesis bar with roadmap footer close the page.
