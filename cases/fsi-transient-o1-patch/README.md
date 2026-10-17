# fsi-transient-o1-patch

O1 quarter-eye with Model-B patch needle-tip cavities and a **six-zone** Lamminsalo solid
(cornea, retina, choroid, sclera, ciliary, iris). The crystalline lens is a **fluid void**
only (`lens_wall` → `noSlip`); it is **not** meshed in the solid and there is **no** Robin
spring coupling on the solid side.

`MODE=baseline` is the passive **transient pimpleFoam TM calibration**, same protocol as
[`doc-transient-o1-patch-fluid`](../doc-transient-o1-patch-fluid/) (IVI/ACP off).
Default timing: `endTime = 2 s`, starting `deltaT = 0.05 s`, `adjustTimeStep yes`,
`maxCo = 2`, `purgeWrite = 1` (only the latest time folder kept). Target IOP is
**15 mmHg**. `MODE=fsi` then adds
**two-way** preCICE coupling: Force (fluid → solid) and Displacement (solid → fluid
ALE motion on `wall`).

`DELTA_T` is the **time step** (`controlDict` `deltaT` in seconds), not temperature.

## TM / IOP (copied from doc-transient-o1-patch-fluid)

Same O1 patch mesh, ciliary `ac_inlet = 1.25e-11 m³/s`, `outlet_tm` at 10 Torr.
Steady `simpleFoam` `d_TM = 1.645058e+15` gives **13.30 mmHg** on pimpleFoam, not 15.20.
Calibrated pimpleFoam: **`d_TM = 2.489000e+15` → IOP_AC = 14.999 mmHg**.
Do not reuse the simpleFoam `d_TM`. Pressure plateaus by ~0.5 s; equilibrated restart
lives in `fluid/2/` (rename to `0/` for IVI / FSI).

`DELTA_T`, `END_TIME`, `MAX_CO`, `ADJUST_TIME_STEP`, and `MAX_DELTA_T` are read by
`Allrun.sim4` in **both** `MODE=baseline` and `MODE=experiment`.

```bash
# Transient rigid baseline — calibrates / verifies TM (IOP ≈ 15 mmHg)
MODE=baseline ./Allrun

# Reuse mesh; override time step or end time
MODE=baseline REUSE_MESH=1 DELTA_T=0.01 END_TIME=2 ./Allrun

# Re-search d_TM if the mesh or solver settings change
python3 scripts/calibrate_d_tm.py --mesh O1
```

FSI mode runs **two separate time axes**:

1. **Prewarm** (rigid): `PREWARM_END_TIME` (default 2 s) — calibrates TM, seeds `fluid/0`.
2. **Coupled FSI**: clock **reset to t = 0**; `FSI_END_TIME` (default 2 s) — preCICE
   `max-time` matches this phase only. Fluid `wall` → `movingWallVelocity`.

```bash
# Baseline only (phase 1)
MODE=baseline ./Allrun

# Full FSI: 2 s prewarm + 2 s coupled (4 s wall-clock work, 2 s coupled physics)
MODE=fsi ./Allrun

# Short coupled smoke (still prewarms 2 s unless FLUID_PREWARM=0)
MODE=fsi FSI_END_TIME=0.05 DELTA_T=0.05 ./Allrun

# Decouple durations
MODE=fsi PREWARM_END_TIME=2 FSI_END_TIME=1 ./Allrun

# Mesh-only check (no solve)
MODE=fsi SKIP_SOLVE=1 ./Allrun
```

Both meshes are rotated with `transformPoints -rotate-y 90`. Fluid coupling uses
the existing `wall` patch mapped conformally to solid `fsi_active`. Cornea and
posterior coat reuse the same O1 stations and divisions; separate block interpolation
leaves a measured maximum face-centroid mapping distance of 0.51 µm.
The Table-SII iris has incompatible front/rear O1 divisions (40 versus 48), so
preCICE uses **RBF thin-plate-splines** (not nearest-neighbor) for smooth
Displacement/Force mapping under serial-implicit IQN-ILS.

## Solid mesh and materials

| cellZone | cells | material ( `mechanicalProperties` ) |
|----------|------:|-------------------------------------|
| cornea   | 9 360 | cornea — E = 1.5 MPa |
| retina   | 3 204 | retina — E = 20 kPa |
| choroid  | 4 272 | choroid — E = 600 kPa |
| sclera   | 7 788 | sclera — E = 2.54 MPa |
| ciliary  | 5 328 | ciliary — choroid proxy (600 kPa) |
| iris     | 3 456 | iris — E = 4 kPa |

**Total: 33 408** solid cells, **one** connected region (`checkMesh` topology OK).
Literature moduli: Karimi 2018/2024, Tahavvor 2020, Wollensak & Spoerl 2004.
Retina is conformally bonded to choroid/sclera — not a free-floating membrane.

Solid boundary patches (`solid/initial/D`):

| patch | BC |
|-------|-----|
| `fsi_active` | `solidForce` (preCICE Force) |
| `fsi_iris` | `fixedDisplacement` |
| `outer` | `fixedDisplacement` (removes rigid-body mode) |
| `defaultFaces` | `solidTraction` |
| `symmetry_0`, `symmetry_90` | `symmetry` |

There is **no** `fsi_lens` patch and **no** Robin coefficient on the solid.

Fluid mesh after patch-tip carving: **53 532** cells (`fluid/log.subsetMesh.acpTip`).

**Mesh quality (solid):** `checkMesh` currently reports **12** zero/negative-volume cells
and extreme aspect ratios in the limbal/ciliary transition strips. Fix `blockMeshDict.O1solid`
before trusting coupled FSI runs.

FSI mode prewarms with the same transient rigid baseline (`pimpleFoam`), then
switches to serial-implicit two-way coupling with IQN-ILS acceleration.
