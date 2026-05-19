## Transcription
WORLDSYSTEMS AS ORDERED CREATION · 6 / 8

CHIRAL ORDER

Orientation changes what can be reached

CORE IDEA

Order is not only
hierarchical;
transitions can be
oriented and
phase-weighted.

Orientation + phase
break symmetry,
reshape interference,
and alter what is
reachable.

ADJACENCY COMPARISON

Ordinary adjacency
(unoriented)

Layer 2
(top)

Layer 1
(mid)

Layer 0
(base)

• Undirected links  
• Symmetric transitions  
• Reachability ignores direction

Chiral / oriented adjacency
(phase-weighted)

e^{i\theta_1}

e^{i\theta_2}

e^{i\phi_1}

e^{i\phi_2}

e^{i\phi_3}

• Directed links with unit-modulus
complex weights e^{i\theta} ∈ T  
• Antisymmetric (chiral) orientation  
• Reachability becomes phase-dependent

ENGINEERING
USE

break
symmetric
reachability

bias upward
vs downward
flow

encode
direction
without
removing law

shape
interference
to favor
desired
outcomes

CHIRAL WEIGHTING RULE

Oriented adjacency matrix A^σ
(rows = sources, cols = targets)

A^σ =
[ 0    σ_{12}  σ_{13}  ...
  σ_{21} 0     σ_{23}  ...
  σ_{31} σ_{32} 0      ...
  ⋮      ⋮      ⋮      ⋱ ]

Chirality (antisymmetry)

σ_{uv} = \overline{σ_{vu}}

reverse orientation
conjugates the weight

Edge weights are unit-modulus phases:  σ_{uv} = e^{iθ_{uv}},  θ_{uv} ∈ R

Path amplitude along a walk  p = (v_0 → v_1 → ··· → v_k):

A^σ(p) = ∏_{j=0}^{k-1} σ_{v_j v_{j+1}} = e^{i(θ_{v_0v_1}+···+θ_{v_{k-1}v_k})}

ORIENTATION → OUTCOME PROCESS

1.
choose directions
on ordered links

2. PHASE
assign phases
(e^{iθ})

3. INTERFERENCE
phases compose:
constructive or
destructive

4. REACHABILITY
accessible states
expand, shrink,
or redirect

PHASE CHANGES WHAT CAN BE REACHED

Same ordered graph,
different orientations / phases

Layer 2
(top)

Layer 1
(mid)

Layer 0
(base)

T_1

T_2

T_3

e^{iα}

e^{iβ}

e^{iγ}

M_1

M_2

M_1^‡

M_2

e^{iν}

B_1

B_2

B_3

B_2

B_3

B_2

e^{iρ_1}

e^{iρ_2}

e^{iρ_3}

e^{iρ_4}

Orientation / phases set A
(constructive to T_1, T_2; destructive to T_3)

Net amplitude to tops

|A(T_1)|    |A(T_2)|    |A(T_3)|

large       large       ≈ 0

Accessible (bright):

T_1        T_2        T_3

Orientation / phases set B
(constructive to T_3; destructive to T_1, T_2)

Net amplitude to tops

|A(T_1)|    |A(T_2)|    |A(T_3)|

≈ 0         ≈ 0         large

Accessible (bright):

T_1        T_2        T_3

THESIS

Once order becomes oriented,
reachability is no longer merely combinatorial;
it becomes phase-structured.

mark → order → adjacency → evolution → search → manifestation

## Visual
A tall, ornate dark-blue poster uses gold serif headings, cyan italic accents, thin geometric borders, and glowing node-link diagrams. The layout is symmetrical and instructional: side columns frame a central comparison, formula panel, process sequence, and bottom worked example showing how phase choices alter accessible targets. Spiral galaxies, compass-like mandalas, arrows, phase labels, and illuminated nodes visually connect chirality, orientation, interference, and reachability.
