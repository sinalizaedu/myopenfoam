# doc-g2-sim1 — G2 Simulação 1 (90° calotte)

Missel 2012 / Lamminsalo 2018 **3D quarter-eye** from the G1 right-half profile.

## What this is

- **G1** = 2D planar bilateral, empty slab.
- **G2** = G1 cut to the **right half**, revolved **90°** about the
  optical axis → calotte with two **symmetry** faces (4× recovers 360°).

## Fluid domain

Same as G1 Sim 1: **AC + vitreous + TM** only (lens / iris holes).

## Generate geometry + mesh (host)

```bash
.venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py --case doc-g2-sim1 --mesh
# optional: --mesh-level M2|M3
```

Artefacts: `geometry/eye_g2_lamminsalo*.{geo,msh,vtk}`,
`figures/g2_half_meridional.png`, `figures/g2_calotte_3d.png`, `geometry_tables.md`.

## Patches

| Patch | Role |
|-------|------|
| `symmetry_0` | cut plane θ = 0° (`z = 0`) — `symmetryPlane` |
| `symmetry_90` | cut plane θ = 90° (`x = 0`) — `symmetryPlane` |
| `ac_inlet` | AC–CB production (single sector) |
| `outlet_tm` | TM SE outlet (single sector) |
| `lens_wall` / `iris_wall` / `wall` | no-slip walls |
