# Anatomical G1 — mesh independence (Sim 1)

Fixed `d_TM = 1.257839e+14` m⁻² (calibrated on prior M1 baseline).

| Level | nCells | TM R/L cells | IOP₀ [mmHg] | Q err [%] | Q_right [%] |
|-------|--------|--------------|-------------|-----------|-------------|
| M1 | 8870 | 164/162 | 15.000 | 0.00 | 56.1 |
| M2 | 15735 | 409/415 | 14.405 | 0.00 | 47.7 |
| M3 | 22200 | 810/837 | 14.410 | 0.00 | 50.7 |

**IOP spread** (fixed d_TM): **0.595 mmHg** (4.0% of 15).

Acceptance (legacy Sim1): spread ≲ 5%. Recalibrate `d_TM` per level if needed.
