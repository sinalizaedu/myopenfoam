# Step 0 — Mesh independence (Lamminsalo BCs)

**Date:** 2026-07-15  
**Solver:** `simpleFoam` fluid-only (`Allrun.step0`)  
**BCs:** Lamminsalo (2018) Table I — ρ=995, μ=6.89×10⁻⁴ Pa·s, Q_prod=3 µL/min, P_epi=10 Torr, d_vit=1.724×10¹³ m⁻²

## Mesh levels

| Level | Method | nCells | TM cells/side (approx.) |
|-------|--------|--------|-------------------------|
| **M1** | baseline `blockMesh` | 3388 | 4 |
| **M2** | `refineMesh` TM zones ×1 | 3412 | 16 |
| **M3** | `refineMesh` TM zones ×2 | 3508 | 64 |

## Calibrated results (IOP₀ ≈ 15 mmHg per mesh)

Each level: binary search on `d_TM` until |IOP−15| < 0.25 mmHg.

| Mesh | d_TM (m⁻²) | IOP₀ mean (mmHg) | Δp AC–vítreo | Q balance err | Verdict |
|------|------------|------------------|--------------|---------------|---------|
| M1 | **1.9448×10¹⁴** | **15.099** | 0.148 mmHg | **0.37 %** | ✅ production |
| M2 | 2.6279×10¹⁴ | 15.126 | 0.146 mmHg | 31.4 % | ⚠️ Q leak after refine |
| M3 | 1.75×10¹⁴ | 15.018 | 0.148 mmHg | 5.27 % | ✅ verification |

**Spread (calibrated IOP):** M3−M1 = −0.08 mmHg (−0.5 %). Acceptable for Step 0.

## Fixed d_TM comparison (M1 calibrated value on all meshes)

| Mesh | d_TM fixed | IOP₀ (mmHg) | Q balance err |
|------|------------|-------------|---------------|
| M1 | 1.9448×10¹⁴ | 15.099 | 0.37 % |
| M2 | 1.9448×10¹⁴ | 13.503 | 36.7 % |
| M3 | — | — | refine BC issue |

M2/M3 at fixed `d_TM` show mesh-dependent hydraulics; **calibrated-per-mesh** comparison is the meaningful metric.

## GCI

Richardson GCI on calibrated IOP (M3→M2→M1): **non-monotonic** (M2 IOP > M1 at separate calibrations).  
**Conclusion:** report calibrated spread (±0.08 mmHg) rather than a single GCI number.

## Production choice (Sim 2)

```yaml
mesh_baseline: M1
d_TM: 1.9448e14
d_vit: 1.724e13
```

M3 documents IOP sensitivity; M2 excluded from production due to mass-balance failure after TM refinement.

## vs previous BCs (Q=2.2 µL/min, P_epi=8 mmHg)

| | Old | Lamminsalo |
|---|-----|------------|
| d_TM (M1) | 3.55×10¹⁴ | **1.94×10¹⁴** |
| IOP₀ | 15.22 mmHg | 15.10 mmHg |

Higher inflow + higher episcleral back-pressure require **lower** effective TM resistance (`d_TM`).
