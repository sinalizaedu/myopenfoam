# doc-run-o1-patch-fluid

Production G2 fluid run locked to **MESH_LEVEL=O1** (blockMesh).
**Model B** — IVI+ACP as **patch** tips (`subsetMesh`).

Seeded from [`doc-transient-o1-patch-fluid`](../doc-transient-o1-patch-fluid/)
(`d_TM = 2.489000e+15`, pimpleFoam IOP_AC ≈ 14.999 mmHg). The equilibrated
snapshot is stored as `fluid/1000` so it does not collide with experiment times 1–30.

## Protocol (experiment clock 5–30 s)

The passive 0–5 s plateau is **not** recomputed here. It lives in
[`doc-transient-o1-patch-fluid`](../doc-transient-o1-patch-fluid/). This case
copies that snapshot to `fluid/1000`, then to `fluid/5/`, and starts at
`startTime = 5`. Needle tables stay on the published clock (IVI 5–12, ACP 15–22)
so metrics stay comparable to the rigid Dirichlet archive.

| Phase | Time [s] | Plateau [s] | IVI | ACP | Wall |
|-------|----------|-------------|-----|-----|------|
| Transient baseline | other case | — | off | off | `noSlip` |
| IVI | 5–12 | 6–11 | +Q | off | Robin |
| Gap | 12–15 | — | off | off | Robin |
| ACP | 15–22 | 16–21 | off | −Q | Robin |
| Recovery | 22–30 | — | off | off | Robin |

Robin (`codedFixedValue` / `scleraRobinBC`) is **experiment-only**.
`U.baseline` keeps `wall noSlip`. Do not run `MODE=baseline` in this directory.

Every IVI/ACP edge has a **1.0 s linear ramp** in `fluid/initial/U.experiment`.
Plateau 5 s + two half-ramps = **6 s effective** delivery.

`Q = 2.08325×10⁻⁹ m³/s` ≈ (50 µL / 6 s) / 4 — already the quarter-symmetry rate,
so IVI/ACP use `±Q`, not `±Q/4`. Delivered volume `Q × 6 s = 12.5 µL` per quarter
= 50 µL for the full eye.

The `wall` patch is a global Robin **conductance** (`codedFixedValue` /
`scleraRobinBC` in `fluid/initial/U.experiment.robin`):  
`U_n = K_comp (⟨p⟩_wall − p_base)` with `p_base = 2.01` (≈15 mmHg kinematic)
and `K_comp = 1.0e-7 s/m`. Pressure is area-averaged over the whole `wall`
patch (not local faces). This is a 0-D Windkessel relief valve, not elastic
FSI and not the old volume-matched Dirichlet table.

## Setup (once)

```bash
cd cases/doc-run-o1-patch-fluid
./scripts/seed_from_baseline.sh
```

Copies `polyMesh`, latest baseline time dir, and `calibration/baseline_iop.yaml` from the O1 patch baseline.

## Run

Stable two-stage experiment (~1 h target):

```bash
docker compose run --rm --user ubuntu fsi bash -lc \
  'cd /simulation/doc-run-o1-patch-fluid && ./scripts/run_experiment_1h.sh O1 4'
```

`run_experiment_1h.sh` defaults to `START_TIME=5` (copy `1000`→`0`→`5`, then IVI).
Do not use `MODE=baseline` here.

Or via Allrun (requires seed + `REUSE_MESH=1`):

```bash
docker compose run --rm --user ubuntu fsi bash -lc \
  'cd /simulation/doc-run-o1-patch-fluid && MODE=experiment REUSE_MESH=1 ./Allrun'
```

## Clean

```bash
./Allclean          # keep seeded polyMesh + baseline time dir
FULL=1 ./Allclean   # also remove polyMesh (re-seed required)
```

## ParaView

`fluid/O1.foam`
