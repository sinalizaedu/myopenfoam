# doc-g2-sim3 — G2 Simulação 3 (paracentese / ACP)

Missel 2012 / Lamminsalo 2018 **3D quarter-eye** (90° calotte).

| Case | Role |
|------|------|
| [`doc-g2-sim2`](../doc-g2-sim2/) | Sim 2 — IVI (tip source) + Robin |
| **`doc-g2-sim3`** | Sim 3 — ACP only (paracentesis tip) + Robin |
| [`doc-g2-sim4`](../doc-g2-sim4/) | Sim 4 — IVI + ACP combined |

## Physics (Model B + Robin)

| Piece | Implementation |
|-------|----------------|
| **ACP** | Internal tip cavity (`subsetMesh` → patch `acp_tip`) in AC on optical axis |
| **Drainage** | `flowRateInletVelocity` table, **Q = Q_clinical/4** (sector), negative on `acp_tip` |
| **Wall** | Volume-matched Robin: `Q_wall(t) = +Q_acp(t)` during paracentesis |
| **Porous** | Same as Sim 1/2 (`d_TM=7.779e14`, IOP₀≈15 mmHg) |

## Protocol

| Phase | Time [s] | Active |
|-------|----------|--------|
| Baseline | 0–5 | `ac_inlet` only |
| Wait | 5–15 | production only |
| **ACP** | 15–21 | `acp_tip` out `−Q`; wall in `+Q` |
| Recovery | 21–30 | all tips off |

`Q_acp_quarter = 2.08325×10⁻⁹ m³/s` (50 µL/6 s ÷ 4).

## Tip location

Sphere centre **`(0, −7.0, 0.40) mm`** on optical axis in the AC (posterior to previous −6.5 mm site).
Figure: [`figures/g2_fluid_acp.png`](figures/g2_fluid_acp.png).

## How to run

```bash
cd cases/doc-g2-sim3
MODE=baseline MESH_LEVEL=M1 ./Allrun
MODE=experiment MESH_LEVEL=M1 REUSE_MESH=1 ./Allrun

# Smoke (ACP starts at t=15)
MODE=experiment MESH_LEVEL=M1 REUSE_MESH=1 END_TIME=16 ./Allrun
```

Docker:

```bash
docker compose run --rm --user ubuntu fsi bash -lc \
  'cd /simulation/doc-g2-sim3 && MODE=baseline MESH_LEVEL=M1 ./Allrun'
```

## IOP calibration

IOP₀ ≈ **15 mmHg** is set by **`d_TM`** in `fluid/system/fvOptions`, with **`outlet_tm` fixed at P_TM = 10 Torr** — not by shifting the pressure field.

After baseline, `save_baseline_calibration.py` writes `calibration/baseline_iop.yaml`. Experiment init copies baseline `p`/`U` unchanged (`init_experiment_from_baseline.py`).

## Production results (2026-07-22)

Archived under `results/` (`Allrun` experiment branch archives automatically):

| Metric | Value | Figure |
|--------|-------|--------|
| Min IOP during ACP (AC / vit) | **4.67 / 10.47** mmHg @ 15.5 s | `figures/iop_acp_onaxis.png` |
| Recovery @ t=30 s | **14.675** mmHg | |

Steady baseline (simpleFoam): **15.004 mmHg**. Transient repouso @ t=0.1 s: **14.681 mmHg**.
