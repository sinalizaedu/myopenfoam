# Mesh-independence study — G1 Sim 1

## Setup

Uniform in-plane refinement was applied while retaining one cell through the
1 mm slab. The effective 2D refinement ratio is `2.000`.
Geometry, boundary areas, flow rate, porous coefficients, schemes and
convergence tolerances were held fixed.

- M1: 41,242 cells; IOP = 22.930 mmHg; formally converged in 252 iterations.
- M2: 164,968 cells; IOP = 22.398 mmHg; formally converged in 685 iterations.
- M3: 659,872 cells; IOP = 22.209 mmHg; reached 1000 iterations. Its pressure and outlet flow were stationary, but its initial pressure residual remained about 2e-4 rather than crossing the formal 1e-4 criterion.

The inlet area was 5.162364e-7 m² per side and the outlet area was
3.471311e-7 m² per side on every level. Total outlet flow was 5.0000e-11 m³/s
on every level.

## Grid-convergence result

- M2 → M3 IOP change: 0.851%.
- Observed order: p = 1.493.
- Richardson-extrapolated IOP: 22.105 mmHg.
- Fine-grid GCI: 0.586%.
- Medium-grid GCI: 1.636%.
- Asymptotic-range check: 0.992 (ideal = 1).

## Decision

The sequence is monotonic and in the asymptotic range. M2 differs from M3 by
less than 1% in the primary outcome, so M2 is mesh-independent for a 1%
engineering criterion and is recommended for production. Use M3 when reporting
sub-percent discretization uncertainty; its estimated GCI is about
0.59%.

M3's formal residual caveat does not materially affect the reported IOP: probe
values were unchanged to the shown precision from iteration 820 through 1000.
