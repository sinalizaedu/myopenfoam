# G1 anatomical — Missel/Lamminsalo 2D planar bilateral

## What this is

- **G1** = anatomical silhouette (Tables SI–SII), 2D planar, bilateral mirror, `empty` front/back.
- **G1 legacy** = rectangular `blockMesh` (`*.legacy`).
- **G2** = future 2D-axisymmetric / 3D.

## Generate geometry + mesh

```bash
# host
.venv-geom/bin/python brunaStuff/gen_lamminsalo_2d.py --mesh
```

Artefacts: `geometry/eye_g1_lamminsalo.{geo,msh}`, `figures/g1_anatomy_2d.png`, `geometry_tables.md`.

## Run (Docker)

```bash
cd cases/eye-fsi-tc0
./Allclean.anatomical
SKIP_SOLVE=1 ./Allrun.anatomical   # mesh + checkMesh only
./Allrun.anatomical                # + simpleFoam
```

Optional: `D_TM=2e14 ./Allrun.anatomical`, `REBUILD_MSH=1 ./Allrun.anatomical`.

## Notes

- Mesh is a **1-layer prism** extrusion (valid OpenFOAM 2D empty).
- ICs live in `fluid/initial/anatomical/` (applied after `createPatch`).
- Schemes: `fvSchemes.anatomical` / `fvSolution.anatomical` (non-ortho correctors for prism mesh).

## Simulação 1 (Step 0) — calibrated 2026-07-15

| Metric | Value |
|--------|-------|
| Malha produção | **M1** (8870 prismas, 1 layer) |
| Q_prod | 3 µL/min |
| P_TM | 10 Torr |
| d_vit | 1.724×10¹³ m⁻² |
| **d_TM** | **1.258×10¹⁴ m⁻²** |
| IOP₀ (M1) | **15.00 mmHg** |
| Q balance | 0.00 % |
| Mesh independence | M1/M2/M3 spread **0.60 mmHg (4.0%)** — PASS |

Artefacts: `coefficients_anatomical.yaml`, `mesh_study_anatomical.md`, `figures/iop_anatomical_sim1.png`.
