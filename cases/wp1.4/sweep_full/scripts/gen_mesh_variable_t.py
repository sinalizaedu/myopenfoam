#!/usr/bin/env python3
"""Spherical octant shell mesh with colatitude-dependent thickness (banded ELSETs)."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WP11 = HERE.parents[2] / "wp1.1" / "scripts"
sys.path.insert(0, str(WP11))

from gen_sphere_shell_mesh import _nset, _surf, build_spherical_octant  # noqa: E402

from case_model import thickness_at_colatitude  # noqa: E402


def _element_colatitude(coords: dict[int, np.ndarray], nodes: list[int]) -> float:
    pts = np.array([coords[n] for n in nodes[:4]])
    c = pts.mean(axis=0)
    r = np.linalg.norm(c)
    if r < 1e-12:
        return math.pi / 2.0
    return float(math.acos(min(1.0, max(-1.0, c[2] / r))))


def write_mesh_variable_thickness(
    out: Path,
    R: float,
    t_equatorial_mm: float,
    t_posterior_mm: float,
    ne: int,
    order: int,
    label: str,
    *,
    theta_min_deg: float = 3.0,
    reduced: bool = True,
) -> dict:
    coords, elems, nsets, inner_pairs = build_spherical_octant(
        R, ne, order, theta_min_deg=theta_min_deg
    )
    theta_min = math.radians(theta_min_deg)
    theta_max = math.pi / 2.0

    bands: list[list[tuple[int, list[int]]]] = [[] for _ in range(ne)]
    band_t: list[float] = []
    for b in range(ne):
        u = (b + 0.5) / ne
        theta_c = theta_min + (theta_max - theta_min) * u
        band_t.append(
            thickness_at_colatitude(
                theta_c, t_equatorial_mm, t_posterior_mm, theta_min_rad=theta_min
            )
        )

    for eid, nodes in elems:
        th = _element_colatitude(coords, nodes)
        u = (th - theta_min) / max(theta_max - theta_min, 1e-9)
        bi = min(ne - 1, max(0, int(u * ne)))
        bands[bi].append((eid, nodes))

    etype = "S8R" if (order == 2 and reduced) else ("S8" if order == 2 else "S4")
    volume_scale = 8
    out.parent.mkdir(parents=True, exist_ok=True)

    with open(out, "w") as fh:
        fh.write(f"** wp1.4 sweep_full — variable t(θ) shell — {label}\n")
        fh.write(
            f"** R={R} mm  t_eq={t_equatorial_mm}  t_post={t_posterior_mm}  "
            f"ne={ne}  type={etype}\n"
        )
        fh.write("** mesh_kind=spherical  bc_mode=symmetry_octant  volume_scale=8\n")
        fh.write(f"** theta_min_deg={theta_min_deg}  thickness_bands={ne}\n")
        fh.write(f"** nodes={len(nsets['NALL'])}  elements={len(elems)}\n")
        fh.write("*NODE, NSET=NALL\n")
        for nid in nsets["NALL"]:
            x, y, z = coords[nid]
            fh.write(f"{nid:8d}, {x: .8f}, {y: .8f}, {z: .8f}\n")

        for b in range(ne):
            elset = f"T_BAND_{b:02d}"
            fh.write(f"*ELEMENT, TYPE={etype}, ELSET={elset}\n")
            for eid, nodes in bands[b]:
                fh.write(", ".join(f"{v:8d}" for v in [eid, *nodes]) + "\n")

        fh.write("*ELSET, ELSET=SHELL\n")
        all_eids = sorted(eid for band in bands for eid, _ in band)
        for i in range(0, len(all_eids), 8):
            fh.write(", ".join(f"{e:8d}" for e in all_eids[i : i + 8]) + "\n")

        for name, ids in nsets.items():
            if name != "NALL":
                _nset(fh, name, ids)
        _surf(fh, "INNER_SURF", inner_pairs)

    t_mean = float(np.mean(band_t))
    meta = {
        "R_mm": R,
        "t_mm": t_mean,
        "t_mean_mm": t_mean,
        "t_equatorial_mm": t_equatorial_mm,
        "t_posterior_mm": t_posterior_mm,
        "band_thickness_mm": band_t,
        "ne": ne,
        "order": order,
        "etype": etype,
        "mesh_kind": "spherical",
        "bc_mode": "symmetry_octant",
        "volume_scale": volume_scale,
        "theta_min_deg": theta_min_deg,
        "variable_thickness": True,
        "n_nodes": len(nsets["NALL"]),
        "n_elements": len(elems),
        "reduced": reduced,
    }
    meta_path = out.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2))
    return meta
