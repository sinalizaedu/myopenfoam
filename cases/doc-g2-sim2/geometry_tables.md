# G2 / G2-fluid geometry (Missel / Lamminsalo ESM)

Same SI–SII tables as G1. Units in tables: **cm**. OpenFOAM uses **metres**.

## Nomenclature

| Name | Source | Domain |
|------|--------|--------|
| **G1** | Missel/Lamminsalo | full anatomy, 2D planar bilateral |
| **G1-fluid** | subset of G1 | AC + vitreous + TM only |
| **G2** | G1 right-half × revolve 90° | full anatomy calotte |
| **G2-fluid** | G1-fluid right-half × revolve 90° | CFD fluid calotte |

Two planar cut faces = **symmetry** patches; **4 × 90° = 360°** of the eye.

## Construction

1. Take the **right half** (`x ≥ 0`) of the corresponding G1 silhouette.
2. `OCC revolve` about optical axis `(0,1,0)` by `90°`.
3. Patches: `symmetry_0` (θ=0°, `z=0`), `symmetry_90` (θ=90°, `x=0`), plus walls/inlets.

## Coordinate map

| Missel | OpenFOAM G2 |
|--------|-------------|
| X (radial) | `x = X·10⁻²` (half-plane, then revolved) |
| Z (optical) | `y = Z·10⁻²` (**revolve axis**) |
| — | `z` from revolution |

## Generated artefacts

### G2 (anatomy)
- `figures/g2_anatomy_half.png`
- `figures/g2_anatomy_3d.png`
- `geometry/eye_g2_lamminsalo.geo`

### G2-fluid (CFD)
- `figures/g2_fluid_half.png`
- `figures/g2_fluid_3d.png`
- `geometry/eye_g2_fluid_lamminsalo.{geo,msh,vtk}` (with `--mesh`)
