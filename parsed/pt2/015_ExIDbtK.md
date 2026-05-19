## Transcription
COMPUTATIONAL THEOLOGY SERIES
12 / 18

TROPICAL SELECTION
In min-plus worlds, what wins is what reaches value at least cost.

1. TROPICAL INTUITION
Min-plus or max-plus algebra replaces ordinary addition / multiplication in optimization landscapes.
CLASSICAL ALGEBRA: a + b -> min(a,b) (tropical add); a x b -> a + b (tropical mult)
TROPICAL ALGEBRA: neutral: + inf (for +), 0 (for x)
We trade smooth sums for sparse choices.

2. CORE RULE: BEST PATH IS SELECTED BY CUMULATIVE COST
A path is a sequence of steps with costs.
FORMAL COST: cost(p) = c_1 + c_2 + ... + c_n
We add cost along the path (min-plus multiplication).
The world selects the path with least total cost.
best = min_p cost(p)
TROPICAL OPERATIONS: a (+) b = min(a,b); a (x) b = a + b

3. REACHABILITY AND REWARD
Desirability is reward discounted by cost-to-reach.
Reward R(p) at goal g / Cost C(p) of path p / Desirability D(p)
DESIRABILITY OF PATH p: D(p) = R(g) - C(p)
BEST CHOICE: choose p* = arg max D(p)
= arg max [R(g) - C(p)]
High reward helps—if it can be reached cheaply.

4. TROPICAL GEOMETRY OF CHOICE
Many paths compete; the cheapest wins.
START -> ... -> GOAL
Other paths (higher cost) / Winning path (least cost)
PATH COSTS: p_1: 1+4+2 = 7 ; p_2: 1+4+2 = 7 ; p_3: 2+1+1 = 4 ; p_4: 3+2+2 = 7
Winner: p_3 (cost = 4)

5. PREDICTION UNDER COST SEMANTICS
Forecasts sort futures by accessibility.
FUTURE / COST TO REACH / REWARD / DESIRABILITY (R - C)
F_1: 3 / 10 / 7
F_2: 5 / 8 / 3
F_3: 2 / 6 / 4
F_4: 7 / 12 / 5
Prediction = ranking by effective desirability (R - C).

6. ETHICAL READING
What becomes optimal may not be what is virtuous.
Tropical selection favors the reachable over the worthy.
Unreachable goods may be of higher intrinsic value.
Awareness must invite the gap.
BEWARE: Very high value but very costly.
TROPICAL CHOICE: Lower value but reachable.
Ask: Which cost structure shaped this desire?

7. DESIGN WARNING
Poor cost geometry can produce pathological attractors.
Locally cheap loops look attractive.
They trap agents in low-value cycles.
The geometry (friction, incentives, telemetry).
Loop cost = 3 ; forward = 5
Better goal here (cost = 4, reward = 9)
Bad geometry hides better futures.

8. PROVISIONAL THESIS
Tropical selection uses min-plus rules to pick least-cost paths.
It converts landscape -> preference (one achieved choice).
It explains how world-form and preference interact before conscious desire.
To change outcomes, change the cost geometry, not the goal.

INTRINSIC VALUE vs. EFFECTIVE VALUE UNDER COST
INTRINSIC VALUE (WITHOUT COST): What is good in itself; Measured by worth, beauty, truth; Life is reward independent of cost.
EFFECTIVE VALUE UNDER COST (TROPICAL): What can be reached; Measured by reward minus cost; Depends on friction, distance, constraints; What gets chosen.

Selection is often tropical: the world chooses through path cost before the agent calls it desire.

## Visual
A tall illuminated-manuscript-style poster on cream parchment with gilded borders, navy serif headings, and numbered gold roundels. It is heavy with mathematical notation (min-plus algebra, cost equations, desirability formulas) alongside a blue spiral galaxy motif, a node-and-edge graph showing competing weighted paths, a small data table, and a haloed scholar/scribe figure with a book. The bottom band is a two-column "intrinsic vs. effective value" comparison, closed by a gold thesis banner in bold serif.
