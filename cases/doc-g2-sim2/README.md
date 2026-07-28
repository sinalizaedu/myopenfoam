# doc-g2-sim2 — G2 Simulação 2 (IVI + Robin)

Missel 2012 / Lamminsalo 2018 **3D quarter-eye** (90° calotte).
Same fluid domain as Sim 1 (**AC ∪ vitreous ∪ TM**).

| Case | Role |
|------|------|
| [`doc-g2-sim1`](../doc-g2-sim1/) | Sim 1 — steady baseline, mesh independence, IOP₀ ≈ 15 mmHg |
| **`doc-g2-sim2`** | Sim 2 — transient IVI (tip source) + volume-matched Robin wall |

## Physics (Model B + Robin)

| Piece | Implementation |
|-------|----------------|
| **IVI** | Internal tip cavity (`subsetMesh` → patch `ivi_tip`) mid-vitreous **on optical axis** |
| **Bolus** | `flowRateInletVelocity` table, **Q = Q_clinical/4** (sector) |
| **Wall** | Volume-matched Robin: `Q_wall(t) = −Q_ivi(t)` |
| **Porous** | Same Darcy `fvOptions` as Sim 1 (`d_TM`, `d_vit`) |

## 30G needle (nominal lumen)

- ID **0.14 mm** → r = **0.07 mm** (`coefficients.yaml`, `g2_needle.py`)
- `topoSetDict.iviTip`: `nearestToCell` + `sphereToCell` at lumen radius
- Dose via **`Q(t)`**, not cavity volume
- Tip centre: **`(0, 3.0, −0.40) mm`** on optical axis

## Mesh (sim2-specific, IVI-only refinement)

Generate **local IVI tip** meshes (not sim1 symlinks):

```bash
./scripts/gen_meshes_ivi.sh
# or per level:
.venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py \
  --case doc-g2-sim2 --mesh --mesh-level M1 --tip-refine ivi
```

## Mesh (sim2 — M1 operacional)

Malha **bulk** sem embed no tip (estável para transient):

```bash
.venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py \
  --case doc-g2-sim2 --mesh --mesh-level M1 --tip-refine none
```

| Item | Valor |
|------|-------|
| Células | ~51 700 |
| `ivi_tip_cells` | 15 (topoSet r = 0.55 mm) |
| Aspect ratio máx. | ~74 |
| Lúmen físico 30G | r = 0.07 mm documentado; patch numérico maior, dose via **Q(t)** |

Refinamento Gmsh com embed (13 células em r = 0.07 mm) gera aspect ratio >300 e crash transient — reservado para estudo de malha posterior.

## Temporal (experiment)

`controlDict.experiment`: `adjustTimeStep no`, `deltaT 0.01`, `maxCo 50` — passo fixo estável com patch de 15 células.

Mesh independence (baseline `simpleFoam` + IVI `pimpleFoam` per level):

```bash
./scripts/run_mesh_independence.sh
# → mesh_independence/REPORT.md, results.csv
```

## How to run (single level)

```bash
cd cases/doc-g2-sim2

# 1) Steady baseline (builds mesh + tip cavity)
MODE=baseline MESH_LEVEL=M1 ./Allrun

# 2) Transient IVI + Robin wall
MODE=experiment MESH_LEVEL=M1 REUSE_MESH=1 ./Allrun
```

Docker:

```bash
docker compose run --rm fsi bash -lc \
  'cd /simulation/doc-g2-sim2 && MODE=baseline MESH_LEVEL=M1 ./Allrun'
```

## Experiment protocol

| Phase | Time [s] | Active |
|-------|----------|--------|
| Baseline | 0–5 | `ac_inlet` only |
| **IVI** | 5–11 | tip in `+Q_ivi`; wall out `−Q_ivi` |
| Recovery | 11–20 | tip/wall off |

`Q_ivi_quarter = 2.08325×10⁻⁹ m³/s` (¼ of 50 µL / 6 s).

See `coefficients.yaml` for frozen porous coefficients.
