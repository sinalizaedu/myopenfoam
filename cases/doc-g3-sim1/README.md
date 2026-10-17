# doc-g3-sim1 — G3 Simulação 1 (FSI, geometria G2 completa)

Missel 2012 / Lamminsalo 2018 **3D quarter-eye** with **fluid + solid**.

| Name | Content |
|------|---------|
| **G3** | G2 anatomy for FSI: **G2-fluid** + **G2-solid** (90° calotte) |
| **G2-fluid** | AC ∪ vitreous ∪ TM (same as `doc-g2-sim1`) |
| **G2-solid** | sclera, choroid, retina, cornea, ciliary, lens, iris |

Coupling: `simpleFoam` / `pimpleFoam` (fluid) + `solids4Foam` (solid) via **preCICE**
(one-way Force → solid for Sim1; two-way Displacement later).

## Generate (host)

```bash
# figures + both meshes (M1), structured solid coat + TM-refined fluid
.venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py \
  --case doc-g3-sim1 --mesh --mesh-solid --mesh-level M1 --structured

# legacy unstructured solid + fluid (no --structured)
.venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py \
  --case doc-g3-sim1 --mesh --mesh-solid --mesh-level M1
```

Structured (`--structured` with `--mesh` + `--mesh-solid`):

- **Conformal FSI:** coat hex + structured fluid in one Gmsh session; **312 shared faces**
  (`fsi_wall` fluid ↔ `fsi_active` solid) on cornea + retina with identical 3D nodes.
- **Solid:** coat only (cornea/sclera/choroid/retina) when conformal; lens/iris/ciliary omitted
  from solid mesh (use legacy merge without conformal if needed).
- **Fluid:** hex revolve + TM clustering; patch `fsi_wall` for preCICE Force.

```bash
.venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py \
  --case doc-g3-sim1 --mesh --mesh-solid --mesh-level M1 --structured
```

Artefacts:

- `geometry/eye_g2_fluid_lamminsalo*.msh` — fluid
- `geometry/eye_g2_solid_lamminsalo*.msh` — solid tissues
- `figures/g2_anatomy_*` / `g2_fluid_*`

## Run (Docker)

```bash
cd cases/doc-g3-sim1
SKIP_SOLVE=1 ./Allrun          # import meshes + checkMesh only
MODE=fluid ./Allrun            # steady IOP₀ baseline (rigid wall)
MODE=fsi ./Allrun              # coupled FSI (one-way Force; prewarm + 1 s smoke)
FLUID_PREWARM=0 MODE=fsi ./Allrun   # skip simpleFoam if fluid already converged
```

## Material properties

**Placeholders confirmed for debug** (not literature values):

- **ρ** from Lamminsalo Table I (`solid/constant/mechanicalProperties`)
- **E, ν** — PLACEHOLDER
- **k_winkler_lens = 1e4 Pa/m** on `lens_rim` — PLACEHOLDER (pipe-lens-spring)

See `coefficients.yaml` (`solid_materials_status: PLACEHOLDER`).

## Patches

### Fluid (G2-fluid)

| Patch | Role |
|-------|------|
| `symmetry_0` / `symmetry_90` | 90° sector |
| `ac_inlet` / `outlet_tm` | production / SE |
| `wall` | fsi_active — preCICE Force (cornea + vitreous envelope) |
| `lens_wall` / `iris_wall` | no-slip, no Force |

### Solid (G2-solid)

| Patch | Role |
|-------|------|
| `symmetry_0` / `symmetry_90` | 90° sector |
| `fsi_active` | preCICE `solidForce` (cornea + retina envelope) |
| `fsi_iris` | `fixedDisplacement` — no Force |
| `fsi_lens` | traction-free (fluid-facing caps) |
| `lens_rim` | Winkler `robin` (k=1e4 Pa/m placeholder) |
| `outer` | free traction |

Cell zones: `sclera`, `choroid`, `retina`, `cornea`, `ciliary`, `lens`, `iris`.

**Note:** solid mesh is multi-region (7 disconnected cellZones). Load transfer
between shells is approximate until conformal fuse geometry is added.

## Relation to other cases

| Case | Role |
|------|------|
| [`doc-g2-sim1`](../doc-g2-sim1/) | Fluid-only steady baseline (rigid wall) |
| [`doc-g2-sim2`](../doc-g2-sim2/) | Transient IVI (fluid-only) |
| [`eye-fsi-tc0`](../old/eye-fsi-tc0/) | Legacy 2D FSI sandbox (blockMesh) |
| [`pipe-lens-spring`](../old/pipe-lens-spring/) | Toy lens + Winkler rim reference |
| **`doc-g3-sim1`** | Anatomical G2 solid + fluid FSI |

## Mesh independence (M1 / M2 / M3)

Fluid IOP₀ baseline + one-step FSI snapshot (`FSI_MAX_TIME=0.01` s).
Same `n_θ` levels as [`doc-g2-sim1`](../doc-g2-sim1/mesh_independence/).

```bash
# generate all levels (host)
for L in M1 M2 M3; do
  .venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py \
    --case doc-g3-sim1 --mesh --mesh-solid --mesh-level $L
done

python3 cases/doc-g3-sim1/scripts/run_mesh_independence.py
```

Results: [`mesh_independence/REPORT.md`](mesh_independence/REPORT.md), `results.csv`.
