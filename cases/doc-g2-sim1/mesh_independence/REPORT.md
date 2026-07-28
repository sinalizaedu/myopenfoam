# Mesh-independence study — G2-fluid Sim 1 (90° calotte)

## Setup

Structured OCC revolve (`n_θ` = 6 / 10 / 16) with recombine → prisms.
Geometry, BCs (Q = 1.25×10⁻¹¹ m³/s = ¼ of 3 µL/min), porous coefficients
(`d_TM = 7.779×10¹⁴`, `d_vit = 1.724×10¹³`), schemes held fixed.
Target IOP₀ ≈ **15 mmHg** (G2-calibrated 2026-07-19).

| Level | n_θ | Cells | IOP [mmHg] | Q_TM [m³/s] | Notes |
|-------|----:|------:|-----------:|------------:|-------|
| M1 | 6 | 33,906 | 15.004 | 1.2500e-11 | formal residualControl |
| M2 | 10 | 69,780 | 15.261 | 1.2500e-11 | engineering (endTime) |
| M3 | 16 | 111,648 | 15.181 | 1.2500e-11 | engineering (endTime) |

Q balance error = 0.00% on all levels (outlet = inlet = quarter-eye target).

## Grid-convergence

- M1 → M2 IOP change: **1.71%**
- M2 → M3 IOP change: **0.52%**
- M1 → M3 IOP change: **1.18%**
- Fine-grid (M3) sits between M1 and M2; M2/M3 did not trigger formal residual stop
  (same behaviour as the prior softer-`d_TM` study for M2).

## Decision

**Recommended mesh: M1** (33.9k cells, n_θ=6) — converges cleanly to the
calibrated IOP₀ = **15.004 mmHg**, matches production `doc-g2-sim2` baseline.

Use **M2/M3** only if reporting sub-percent discretization uncertainty; expect
~1% IOP scatter vs M1 at this `d_TM` unless residuals are tightened further.

## How to reproduce

```bash
# host meshes
.venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py --case doc-g2-sim1 --mesh --mesh-level M1
.venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py --case doc-g2-sim1 --mesh --mesh-level M2
.venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py --case doc-g2-sim1 --mesh --mesh-level M3

# docker
cd cases/doc-g2-sim1
MESH_LEVEL=M1 ./Allrun
MESH_LEVEL=M2 ./Allrun
MESH_LEVEL=M3 ./Allrun
```
