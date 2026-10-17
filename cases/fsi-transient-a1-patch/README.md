# fsi-transient-a1-patch

O1 quarter-eye **fluid** (same Model-B patch needle-tip cavities as
[`fsi-transient-o1-patch`](../fsi-transient-o1-patch/)) with the **A1** solid:
a 4-layer hex extrusion of fluid `wall` into the coat only.

A1 is **not** the six-zone Lamminsalo solid. Iris is a fluid `iris_wall`
(`noSlip`); there is no solid iris, no lens, and no Robin spring. `fsi_active`
has **2160** quad faces; fluid `wall` has **2184** (24 wedge-tip triangles
omitted — blockMesh cannot collapse those prisms). preCICE maps Force and
Displacement with **RBF thin-plate-splines**.

| cellZone | cells | material |
|----------|------:|----------|
| cornea   | 3 072 | cornea — E = 1.5 MPa |
| ciliary  | 1 248 | choroid proxy (600 kPa) |
| sclera   | 4 320 | sclera — E = 2.54 MPa |

**Total: 8 640** solid cells. `checkMesh` reports **Mesh OK** (max non-ortho 30.3°).

Solid boundary patches (`solid/initial/D`):

| patch | BC |
|-------|-----|
| `fsi_active` | `solidForce` (preCICE Force) |
| `outer` | `fixedDisplacement` (removes rigid-body mode) |
| `defaultFaces` | `solidTraction` |

Fluid mesh after patch-tip carving: **53 532** cells (same O1 as the o1-patch case).
TM calibration is unchanged: **`d_TM = 2.489000e+15` → IOP_AC = 14.999 mmHg**.

```bash
# Transient rigid baseline
MODE=baseline ./Allrun

# Full FSI: 2 s prewarm + 2 s coupled
MODE=fsi ./Allrun

# Mesh-only check
MODE=fsi SKIP_SOLVE=1 ./Allrun
```

Overnight chain (validation then IVI/ACP experiment):
[`../run_overnight_fsi_transient_a1.sh`](../run_overnight_fsi_transient_a1.sh)
