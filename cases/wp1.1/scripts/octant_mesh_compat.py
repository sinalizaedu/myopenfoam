"""Octant mesh matching external WP1 compat convention (i-outer node numbering)."""
from __future__ import annotations

import numpy as np


def build_octant_mesh(n_theta: int, n_phi: int, R: float, theta_min_deg: float = 3.0):
    """Spherical octant S8R grid; node ids 1..N in theta-major order."""
    theta_min = np.radians(theta_min_deg)
    theta = np.linspace(theta_min, np.pi / 2, 2 * n_theta + 1)
    phi = np.linspace(0.0, np.pi / 2, 2 * n_phi + 1)

    nodes: dict[int, tuple[float, float, float]] = {}
    id_grid = np.zeros((len(theta), len(phi)), dtype=int)
    nid = 1
    for i, th in enumerate(theta):
        for j, ph in enumerate(phi):
            x = R * np.sin(th) * np.cos(ph)
            y = R * np.sin(th) * np.sin(ph)
            z = R * np.cos(th)
            nodes[nid] = (float(x), float(y), float(z))
            id_grid[i, j] = nid
            nid += 1

    elements: list[tuple[int, ...]] = []
    for ei in range(n_theta):
        for ej in range(n_phi):
            i0, i1, i2 = 2 * ei, 2 * ei + 1, 2 * ei + 2
            j0, j1, j2 = 2 * ej, 2 * ej + 1, 2 * ej + 2
            conn = (
                int(id_grid[i0, j0]),
                int(id_grid[i2, j0]),
                int(id_grid[i2, j2]),
                int(id_grid[i0, j2]),
                int(id_grid[i1, j0]),
                int(id_grid[i2, j1]),
                int(id_grid[i1, j2]),
                int(id_grid[i0, j1]),
            )
            elements.append(conn)

    sym_y = [int(id_grid[i, 0]) for i in range(len(theta))]
    sym_x = [int(id_grid[i, -1]) for i in range(len(theta))]
    sym_z = [int(id_grid[-1, j]) for j in range(len(phi))]
    inner_ring = [int(id_grid[0, j]) for j in range(len(phi))]

    return nodes, elements, sym_x, sym_y, sym_z, inner_ring
