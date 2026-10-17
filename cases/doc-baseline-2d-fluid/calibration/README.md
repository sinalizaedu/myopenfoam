# Sim 1 Step 0 — IOP calibration (M2)

Recalibrated for **velocity inlet** (`surfaceNormalFixedValue`, \(U=Q_{3D}/A_{3D}\)).

| Quantity | Value |
|----------|-------|
| Mesh | M2 (164,968 cells) |
| Inlet | \(U = 2{,}22\times10^{-6}\) m/s (Lamminsalo 0,1332 mm/min) |
| Implied \(Q_{2D}\) | 2.292×10⁻¹² m³/s |
| `d_TM` | **1.1064×10¹⁵ m⁻²** |
| IOP_AC mean | **14.999 mmHg** |
| IOP vitreous | 15.000 mmHg |
| Q_TM total | 2.2921×10⁻¹² m³/s (0.00% error vs \(Q_{in}\)) |
| Iterations | 678 (SIMPLE converged) |

Outlet fixed at 10 Torr. Literature \(Q_{3D}=3\) µL/min defines \(U\) only; G1 planar does not impose that absolute \(Q\) on the 1 mm slab.

Previous calibration under `flowRateInletVelocity` (\(Q=3\) µL/min on slab): `d_TM = 5.072×10¹³` — **invalid** with velocity inlet.
