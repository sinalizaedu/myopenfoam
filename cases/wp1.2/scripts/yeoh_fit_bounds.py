"""Canonical Yeoh-2 search box for WP1.2 inverse FEA (log10 C20, C20 > 0)."""
from __future__ import annotations

import numpy as np

# Aligned with brunaStuff/latex/report/wp1.tex (Park-scale C20, positive only).
YEOH_C10_LO_MPA = 1e-4
YEOH_C10_HI_MPA = 5.0
YEOH_C20_LO_MPA = 0.1
YEOH_C20_HI_MPA = 1000.0


def decode_yeoh(x: np.ndarray) -> tuple[float, float]:
    c10 = float(x[0])
    c20 = float(10.0 ** x[1])
    return c10, c20


def yeoh_bounds() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (x0, lo, hi) for optimizer vector [C10, log10(C20)]."""
    lo = np.array([YEOH_C10_LO_MPA, np.log10(YEOH_C20_LO_MPA)])
    hi = np.array([YEOH_C10_HI_MPA, np.log10(YEOH_C20_HI_MPA)])
    # 0.058 MPa is below C20_LO; use 0.1 MPa for a feasible default start.
    x0 = np.array([0.612, np.log10(YEOH_C20_LO_MPA)])
    return x0, lo, hi
