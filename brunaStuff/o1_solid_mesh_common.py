"""Shared meridional geometry for O1 Lamminsalo solid mesh variants.

Re-exports ``o1_solid_anatomy`` so older imports keep working.
"""
from __future__ import annotations

from o1_solid_anatomy import (  # noqa: F401
    N_THETA,
    THETAS,
    Z_SLAB_MM,
    Curve,
    Point,
    along_segment,
    circle_points,
    cornea_outer,
    ellipse_curve,
    ellipse_point,
    lerp_point,
    parametric_t,
    projected_ellipse,
    quad_convex,
    require_convex,
)
