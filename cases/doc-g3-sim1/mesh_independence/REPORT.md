# Mesh-independence — G3 Sim 1 (G2-fluid + G2-solid FSI)

## Setup

Structured OCC revolve (`n_θ` = 6 / 10 / 16), same porous coeffs as G2 Sim 1
(`d_TM = 7.779×10¹⁴`, IOP₀ target ≈ 15 mmHg).

Per level:
1. `MODE=fluid` — rigid-wall steady IOP₀
2. `MODE=fsi` — one-way Force, `FSI_MAX_TIME=0.01` s (after fluid warm state)

| Level | n_θ | nCells fluid | nCells solid | IOP [mmHg] | Q_TM [m³/s] | |D|_max fsi [µm] | map max [m] | FSI ok |
|-------|----:|-------------:|-------------:|-----------:|------------:|----------------:|------------:|:------:|
| M1 | 6 | 33906 | 33108 | 15.004 | 1.2500e-11 | 0.0000 | 6.535130e-03 | True |
| M2 | 10 | 69780 | 75140 | 15.261 | 1.2500e-11 | 0.0000 | 6.504260e-03 | True |
| M3 | 16 | 111648 | 127552 | 15.181 | 1.2500e-11 | 0.0000 | 6.506600e-03 | True |

## Grid convergence (fluid IOP)

- M1 → M2: **1.71%**
- M2 → M3: **0.52%**
- M1 → M3: **1.18%**

## FSI snapshot (|D|_max on solid after coupled step)

- All levels: |D|_max ≈ 0 µm (one 0.01 s step; solid still at rest).

## Decision

**M2** for production (fluid IOP within 1% of M3; matches G2-fluid study).

Solid mesh remains **7 disconnected regions** — |D|_max is a patch-local smoke metric,
not a converged structural solution.

## Reproduce

```bash
.venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py \
  --case doc-g3-sim1 --mesh --mesh-solid --mesh-level M1  # repeat M2,M3
python3 cases/doc-g3-sim1/scripts/run_mesh_independence.py
```
