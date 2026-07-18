# doc-g1-sim1 — G1 Simulação 1 (AC / vitreous / TM only)

Missel 2012 / Lamminsalo 2018 **2D planar bilateral** rabbit eye.

For the 3D 90° calottes see [`../doc-g2-sim1`](../doc-g2-sim1):
**G2** (from G1 anatomy) and **G2-fluid** (from G1-fluid).

## Fluid domain

Only:

| Zone | Role |
|------|------|
| **AC** | free aqueous (anterior chamber + PC path) |
| **Vitreous** | porous (`vitreous_zone`, κ = 5.8×10⁻¹⁴ m²) |
| **TM** | porous outlets L/R (`tm_zone`, `tm_zone_left`) |

**Not meshed as fluid:** sclera, choroid, retina, cornea stroma, ciliary body  
(outer wall = cornea_inside + vitreous–retina; lens / iris / ciliary are holes).

## Generate geometry + mesh (host)

```bash
.venv-geom/bin/python brunaStuff/gen_lamminsalo_2d.py --case doc-g1-sim1 --mesh
# optional: --mesh-level M2|M3
```

Artefacts: `geometry/eye_g1_lamminsalo*.{geo,msh}`, `figures/g1_fluid_2d.png`, `geometry_tables.md`.

## Run (Docker / OpenFOAM)

```bash
cd cases/doc-g1-sim1
./Allclean
SKIP_SOLVE=1 ./Allrun          # mesh + checkMesh only
./Allrun                       # + simpleFoam
```

Optional: `D_TM=5.072e13 ./Allrun`, `REBUILD_MSH=1 ./Allrun`, `MESH_LEVEL=M2 ./Allrun`.

## Calibrated baseline (Step 0)

| Item | Value |
|------|-------|
| Mesh | **M2** (164,968 cells; mesh-independent to ~1%) |
| `d_TM` | **5.072×10¹³ m⁻²** → IOP₀ ≈ **15.00 mmHg** |
| Q | 3 µL/min total, mass balance error 0.00% |

See `calibration/README.md` and `mesh_independence/REPORT.md`.

## BCs (Lamminsalo 2018)

- Q_prod = 3 µL/min (1.5 per side) on `ac_inlet` / `ac_inlet_left` (full AC–CB iris→vitreous face)
- P_TM = 10 Torr on `outlet_tm` / `outlet_tm_left` (full SE face of TM)
- empty `front` / `back` (1 mm slab)
