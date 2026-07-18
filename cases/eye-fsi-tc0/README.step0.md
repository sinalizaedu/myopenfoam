> **G1 geometry update (2026-07):** the default anatomical mesh is documented in
> [`README.anatomical.md`](README.anatomical.md) (`./Allrun.anatomical`).
> Rectangular `blockMesh` remains available as **G1 legacy** (`blockMeshDict.legacy`).
> **G2** = future axisymmetric/3D.

# Step 0 — Steady hydraulic calibration (Simulação 1)

## Quick start (Docker)

```bash
cd cases/eye-fsi-tc0
./Allclean.step0
MESH_LEVEL=M1 ./Allrun.step0          # baseline mesh
MESH_LEVEL=M3 ./Allrun.step0          # TM-refined verification mesh
```

Optional: `D_TM=3.62e14` overrides TM permeability before run.

## Deliverables

| File | Content |
|------|---------|
| `coefficients_step0.yaml` | Frozen d_TM, d_vit for Sim 2 |
| `mesh_study.md` | M1/M2/M3 independence study |
| `sim1_report.md` | V&V checklist + go/no-go opinion |
| `calibration_step0.log` | Calibration history |
| `figures/iop_step0_steady.png` | IOP vs iteration |

## Scripts

- `scripts/extract_step0_metrics.py` — post-run metrics
- `scripts/plot_step0_iop.py` — convergence figure
- `scripts/set_d_tm.py` — update fvOptions d_TM
- `scripts/compute_gci.py` — GCI summary

## Frozen coefficients (M1 → Sim 2)

- **κ_vit:** 5.8×10⁻¹⁴ m² (Tabela I)
- **d_vit:** 1.724×10¹³ m⁻² (= 1/κ)
- **d_TM:** a recalibrar (κ_TM ajustada)
- **P_epi:** 10 Torr (Lamminsalo 2018)
- **Q_prod:** 3.0 µL/min total (Lamminsalo 2018)
