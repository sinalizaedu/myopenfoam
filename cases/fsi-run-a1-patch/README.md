# fsi-run-a1-patch

Two-way **preCICE FSI** IVI+ACP experiment on O1 patch **fluid** + **A1** extruded
coat solid. No Robin wall — sclera compliance comes from the coupled solid
(`fsi_active` ↔ `wall`, RBF mapping).

Seeded from [`fsi-transient-a1-patch`](../fsi-transient-a1-patch/) after transient TM
prewarm (`d_TM = 2.489e15`, IOP ≈ 15 mmHg).

## Protocol (experiment clock 5–30 s)

Same needle schedule as [`doc-run-o1-patch-fluid`](../doc-run-o1-patch-fluid/):

| Phase | Time [s] | IVI | ACP | Wall |
|-------|----------|-----|-----|------|
| Transient prewarm | other case | off | off | rigid `noSlip` |
| Settle | 4.8–5 | off | off | rigid `noSlip` |
| IVI | 5–12 | +Q | off | `movingWallVelocity` + solid |
| Gap | 12–15 | off | off | FSI |
| ACP | 15–22 | off | −Q | FSI |
| Recovery | 22–30 | off | off | FSI |

`Q = 2.08325×10⁻⁹ m³/s` (quarter-eye). Lens is a **fluid void** (`lens_wall` only).

## Setup

```bash
# After fsi-transient-a1-patch MODE=fsi (or baseline prewarm) succeeded:
cd cases/fsi-run-a1-patch
./scripts/bootstrap_from_transient.sh   # first time only
./scripts/seed_from_baseline.sh
./scripts/build_solid_a1.sh
```

## Run

```bash
docker compose run --rm --user ubuntu fsi bash -lc \
  'cd /simulation/fsi-run-a1-patch && ./Allrun'
```

Overnight chain: [`../run_overnight_fsi_transient_a1.sh`](../run_overnight_fsi_transient_a1.sh)
