# doc-g2-sim1 — G2 / G2-fluid (90° calotte)

Missel 2012 / Lamminsalo 2018 **3D quarter-eye**.

## Naming (same split as G1)

| Name | Based on | Content |
|------|----------|---------|
| **G2** | **G1** | full anatomy (sclera, choroid, retina, cornea, lens, iris, ciliary, AC, vitreous, TM) |
| **G2-fluid** | **G1-fluid** | AC + vitreous + TM only (Sim 1 CFD domain) |

Both: right-half meridional profile revolved **90°** about the optical
axis → calotte with two **symmetry** faces (4× recovers 360°).

## Generate (host)

```bash
# figures + geo for G2 and G2-fluid
.venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py --case doc-g2-sim1

# + G2-fluid volume mesh (CFD)
.venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py --case doc-g2-sim1 --mesh
```

## Artefacts

- `figures/g2_anatomy_{half,3d}.png` — **G2** from G1
- `figures/g2_fluid_{half,3d}.png` — **G2-fluid** from G1-fluid
- `geometry/eye_g2_lamminsalo.geo` — anatomy stub
- `geometry/eye_g2_fluid_lamminsalo.msh` — fluid mesh (`--mesh`)

## Patches (G2-fluid)

| Patch | Role |
|-------|------|
| `symmetry_0` | θ = 0° (`z = 0`) — `symmetryPlane` |
| `symmetry_90` | θ = 90° (`x = 0`) — `symmetryPlane` |
| `ac_inlet` | AC–CB production (1/4 eye) |
| `outlet_tm` | TM SE outlet (1/4 eye) |
| `lens_wall` / `iris_wall` / `wall` | no-slip |
