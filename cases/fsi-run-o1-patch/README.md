# fsi-run-o1-patch

Two-way **preCICE FSI** IVI+ACP experiment on O1 patch mesh (Model B).
No Robin wall — sclera compliance comes from the coupled solid (`fsi_active` ↔ `wall`).

Seeded from [`fsi-transient-o1-patch`](../fsi-transient-o1-patch/) after transient TM
prewarm (`d_TM = 2.489e15`, IOP ≈ 15 mmHg). Equilibrated snapshot: `fluid/1000`.

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
# After fsi-transient-o1-patch MODE=fsi (or baseline prewarm) succeeded:
cd cases/fsi-run-o1-patch
./scripts/bootstrap_from_transient.sh   # first time only
./scripts/seed_from_baseline.sh
# solid mesh (once):
(cd solid && blockMesh -dict system/blockMeshDict.O1solid && transformPoints -rotate-y 90)
```

## Run

```bash
docker compose run --rm --user ubuntu fsi bash -lc \
  'cd /simulation/fsi-run-o1-patch && ./Allrun'
```

Overnight chain (validation + experiment): [`../run_overnight_fsi_transient_o1.sh`](../run_overnight_fsi_transient_o1.sh)

## ParaView

`fluid/O1.foam`, `solid/solid.foam`
