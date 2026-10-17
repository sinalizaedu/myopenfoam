# doc-baseline-2d-fluid — G1 Simulação 1 (AC / vitreous / TM only)

Missel 2012 / Lamminsalo 2018 **2D planar bilateral** rabbit eye.

**Scope:** Sim 1 only (steady + `d_TM` calibration). No planar Sim 2 — µL/clinical transients continue on [`doc-g2-sim2`](../doc-g2-sim2/). See `plano_doutorado.md` (§ G1 planar scope stop).

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
.venv-geom/bin/python brunaStuff/gen_lamminsalo_2d.py --case doc-baseline-2d-fluid --mesh
# optional: --mesh-level M2|M3
```

Artefacts: `geometry/eye_g1_lamminsalo*.{geo,msh}`, `figures/g1_fluid_2d.png`, `geometry_tables.md`.

## Run (Docker / OpenFOAM)

```bash
cd cases/doc-baseline-2d-fluid
./Allclean
SKIP_SOLVE=1 ./Allrun          # mesh + checkMesh only
./Allrun                       # + simpleFoam
```

Optional: `D_TM=1.1064e15 ./Allrun`, `REBUILD_MSH=1 ./Allrun`, `MESH_LEVEL=M2 ./Allrun`.

## Calibrated baseline (Step 0)

| Item | Value |
|------|-------|
| Mesh | **M2** (164,968 cells; mesh-independent to ~1%) |
| Inlet | \(U = 2{,}22\times10^{-6}\) m/s (velocity-matched to 3D) |
| `d_TM` | **1.1064×10¹⁵ m⁻²** → IOP₀ ≈ **15.00 mmHg** |
| \(Q_{2D}\) | ≈ 2.292×10⁻¹² m³/s, mass balance error 0.00% |

See `calibration/README.md` and `mesh_independence/REPORT.md`.

## BCs (Lamminsalo 2018)

- **Inlet velocity** (not flow-rate): \(U = Q_{3D}/A_{3D} = 0{,}1332\) mm/min = **2.22×10⁻⁶ m/s**
  (`surfaceNormalFixedValue` on `ac_inlet` / `ac_inlet_left`)
- Literature rate \(Q_{3D} = 3\) µL/min defines \(U\) via Missel/Lamminsalo inlet-port area; G1 planar does **not** impose that absolute \(Q\) on the 1 mm slab (wrong Re). See `plano_doutorado.md`.
- P_TM = 10 Torr on `outlet_tm` / `outlet_tm_left` (full SE face of TM)
- empty `front` / `back` (1 mm slab)