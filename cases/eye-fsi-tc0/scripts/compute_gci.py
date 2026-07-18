#!/usr/bin/env python3
"""Compute GCI from three mesh IOP values (fine→coarse: M3, M2, M1)."""

import math

# Fixed d_TM=3.62e14 across meshes (mesh sensitivity without recalibration)
data = [
    ("M1", 3388, 15.054),
    ("M2", 3412, 16.302),
    ("M3", 3508, 15.848),
]

# Calibrated to IOP≈15 mmHg per level
calibrated = [
    ("M1", 3388, 3.62e14, 15.054),
    ("M2", 3412, 3.30e14, 15.685),
    ("M3", 3508, 3.25e14, 15.129),
]

def gci(phi_coarse, phi_medium, phi_fine, r=1.03):
    eps21 = phi_medium - phi_fine
    eps32 = phi_coarse - phi_medium
    if abs(eps21) < 1e-9:
        return float("nan"), float("nan")
    p = abs(math.log(abs(eps32 / eps21)) / math.log(r)) if abs(eps32) > 1e-9 else 1.0
    fs = abs((r**p - 1.0) / (2.0 * p * eps21))
    gci_fine = 1.25 * fs * abs(eps21) / abs(phi_fine) * 100.0
    return gci_fine, p

print("=== Fixed d_TM=3.62e14 (mesh sensitivity) ===")
for row in data:
    print(f"  {row[0]}: n={row[1]}, IOP={row[2]:.3f} mmHg")
gci, p = gci(15.054, 16.302, 15.848, r=3412/3508)
print(f"  GCI(fine,M3)={gci:.1f}%  p={p:.2f}  [non-monotonic → indicative only]")

print("\n=== Calibrated d_TM per level (IOP target 15 mmHg) ===")
for row in calibrated:
    print(f"  {row[0]}: n={row[1]}, d_TM={row[2]:.2e}, IOP={row[3]:.3f} mmHg")
spread = max(r[3] for r in calibrated) - min(r[3] for r in calibrated)
print(f"  IOP spread = {spread:.3f} mmHg ({spread/15*100:.1f}%)")
