"""G2-fluid structured hex grid → OpenFOAM blockMeshDict (90° calotte, fluid-only).

Builds the same meridional structured grid as g2_structured_mesh (conformal fluid
path) and writes a multi-block blockMeshDict: one (1×1×n_theta) hex column per
(i, j) meridional quad.  Run with OpenFOAM ``blockMesh`` — no Gmsh / gmshToFoam.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from g2_structured_mesh import (
    REVOLVE_RAD,
    STRUCTURED_LEVELS,
    _fluid_inner_on_ray,
    _tm_indices,
    build_fluid_outer_stations,
    classify_fluid_patch,
    point_in_poly,
    resample_curve,
)

# (legacy) meridional columns that needed θ-flip before tangent cleanup
FLIP_K_COLUMNS = frozenset()

N_MID = {"M1": 12, "M2": 16, "M3": 22}
N_LENS = {"M1": 8, "M2": 10, "M3": 12}


def _revolve(x: float, y: float, theta: float) -> tuple[float, float, float]:
    c, s = math.cos(theta), math.sin(theta)
    return x * c, y, -x * s


def _vid(j: int, i: int, k: int, n_m: int, n_r: int) -> int:
    """0-based vertex index in blockMesh vertices list."""
    return k * (n_r + 1) * n_m + j * n_m + i


def _remove_tangent_reversals(outer: np.ndarray, *, min_dx: float = 0.0) -> np.ndarray:
    """Drop sparse meridional stations that reverse +x (breaks blockMesh orientation)."""
    outer = np.asarray(outer, dtype=float)
    if len(outer) < 3:
        return outer
    keep = [0]
    for i in range(1, len(outer) - 1):
        t0 = outer[i] - outer[keep[-1]]
        t1 = outer[i + 1] - outer[i]
        if t0[0] >= -min_dx and t1[0] >= -min_dx:
            keep.append(i)
    keep.append(len(outer) - 1)
    return outer[keep]


def build_fluid_structured_grid(
    bi: dict[str, np.ndarray],
    fluid: dict[str, np.ndarray],
    mesh_level: str,
) -> tuple[dict[tuple[int, int, int], tuple[float, float, float]], dict]:
    """Return 3D node coords keyed by (j, i, k) and a summary dict."""
    if mesh_level not in STRUCTURED_LEVELS:
        raise ValueError(f"unknown mesh_level {mesh_level}")
    cfg = STRUCTURED_LEVELS[mesh_level]
    n_theta = cfg["n_theta"]
    n_r = max(cfg["n_r_fluid"], cfg["fluid_tm_layers"] + 2)
    n_c = max(cfg["n_merid"] // 4, 8)
    n_mid = N_MID.get(mesh_level, 12)
    n_v = max(cfg["n_merid"] // 3, 8)
    n_lens = N_LENS.get(mesh_level, 8)

    outer, _, _ = build_fluid_outer_stations(
        bi, n_c=n_c, n_mid=n_mid, n_v=n_v, n_lens=n_lens,
    )
    outer = _remove_tangent_reversals(outer)
    n_m = len(outer)
    lens = resample_curve(fluid["lens_half"], max(16, n_m // 3) + 1)
    iris = resample_curve(fluid["iris_half"], max(12, n_m // 4) + 1)
    tm_idx = _tm_indices(outer, bi["tm_markers_right"])

    inner_pts = np.array([_fluid_inner_on_ray(p, lens, iris) for p in outer])
    grid = np.zeros((n_r + 1, n_m, 2))
    for i, p_out in enumerate(outer):
        p_in = inner_pts[i]
        cluster = i in tm_idx or any(abs(i - j) <= 1 for j in tm_idx)
        for j in range(n_r + 1):
            s = j / n_r
            if cluster:
                s = 1.0 - (1.0 - s) ** 1.65
            grid[j, i] = (1.0 - s) * p_out + s * p_in

    thetas = [k * REVOLVE_RAD / n_theta for k in range(n_theta + 1)]
    coords: dict[tuple[int, int, int], tuple[float, float, float]] = {}
    for k, th in enumerate(thetas):
        for j in range(n_r + 1):
            for i in range(n_m):
                x, y = grid[j, i]
                x = max(float(x), 1.0e-6) if abs(x) < 1.0e-6 else float(x)
                x3, y3, z3 = _revolve(x, y, th)
                if k == 0:
                    z3 = 0.0
                if k == n_theta:
                    x3 = 0.0
                coords[(j, i, k)] = (x3, y3, z3)

    meta = {
        "mesh_level": mesh_level,
        "n_r": n_r,
        "n_m": n_m,
        "n_theta": n_theta,
        "n_cells": n_r * (n_m - 1) * n_theta,
        "n_vertices": len(coords),
        "tm_stations": sorted(tm_idx),
    }
    return coords, meta


def _hole_at(cx: float, cy: float, cz: float, lens: np.ndarray, iris: np.ndarray) -> str | None:
    p2 = np.array([math.hypot(cx, cz), cy])
    if point_in_poly(p2, lens):
        return "lens"
    if point_in_poly(p2, iris):
        return "iris"
    return None


def _face_centroid(
    coords: dict[tuple[int, int, int], tuple[float, float, float]],
    nodes: tuple[int, ...],
    n_m: int,
    n_r: int,
) -> tuple[float, float, float]:
    pts = []
    for vid in nodes:
        k = vid // ((n_r + 1) * n_m)
        rem = vid % ((n_r + 1) * n_m)
        j = rem // n_m
        i = rem % n_m
        pts.append(coords[(j, i, k)])
    return (
        sum(p[0] for p in pts) / len(pts),
        sum(p[1] for p in pts) / len(pts),
        sum(p[2] for p in pts) / len(pts),
    )


def _block_verts(
    j: int,
    i: int,
    n_m: int,
    n_r: int,
    n_theta: int,
    *,
    flip_k: bool = False,
) -> tuple[int, ...]:
    """OpenFOAM blockMesh hex corners (meridional i × radial j × theta k)."""
    v = (
        _vid(j, i + 1, 0, n_m, n_r),
        _vid(j, i, 0, n_m, n_r),
        _vid(j + 1, i, 0, n_m, n_r),
        _vid(j + 1, i + 1, 0, n_m, n_r),
        _vid(j, i + 1, n_theta, n_m, n_r),
        _vid(j, i, n_theta, n_m, n_r),
        _vid(j + 1, i, n_theta, n_m, n_r),
        _vid(j + 1, i + 1, n_theta, n_m, n_r),
    )
    if flip_k:
        return (v[4], v[5], v[6], v[7], v[0], v[1], v[2], v[3])
    return v


def _hex_volume(
    coords: dict[tuple[int, int, int], tuple[float, float, float]],
    v: tuple[int, ...],
    n_m: int,
    n_r: int,
) -> float:
    def p(vid: int) -> np.ndarray:
        k = vid // ((n_r + 1) * n_m)
        rem = vid % ((n_r + 1) * n_m)
        jj = rem // n_m
        ii = rem % n_m
        return np.array(coords[(jj, ii, k)])

    def sv(a: int, b: int, c: int, d: int) -> float:
        pa, pb, pc, pd = p(a), p(b), p(c), p(d)
        return float(np.dot(pb - pa, np.cross(pc - pa, pd - pa)) / 6.0)

    v0, v1, v2, v3, v4, v5, v6, v7 = v
    return (
        sv(v0, v1, v3, v4)
        + sv(v1, v2, v3, v6)
        + sv(v1, v4, v5, v6)
        + sv(v3, v4, v6, v7)
        + sv(v1, v3, v4, v6)
    )


def _oriented_block_verts(
    coords: dict[tuple[int, int, int], tuple[float, float, float]],
    j: int,
    i: int,
    n_m: int,
    n_r: int,
    n_theta: int,
) -> tuple[int, ...]:
    flip_k = i in FLIP_K_COLUMNS
    v = _block_verts(j, i, n_m, n_r, n_theta, flip_k=flip_k)
    if _hex_volume(coords, v, n_m, n_r) < 0:
        v = _block_verts(j, i, n_m, n_r, n_theta, flip_k=not flip_k)
    return v


def _radial_thickness(
    coords: dict[tuple[int, int, int], tuple[float, float, float]],
    j: int,
    i: int,
) -> float:
    a = np.array(coords[(j, i, 0)])
    b = np.array(coords[(j + 1, i, 0)])
    return float(np.linalg.norm(b - a))


def _valid_block(
    coords: dict[tuple[int, int, int], tuple[float, float, float]],
    j: int,
    i: int,
    *,
    min_dr: float = 5.0e-8,
) -> bool:
    return min(
        _radial_thickness(coords, j, i),
        _radial_thickness(coords, j, i + 1),
    ) >= min_dr


def _classify_boundary_face(
    cx: float,
    cy: float,
    cz: float,
    *,
    face_kind: str,
    lens: np.ndarray,
    iris: np.ndarray,
) -> str:
    hole = _hole_at(cx, cy, cz, lens, iris) if face_kind == "inner" else None
    return classify_fluid_patch(cx, cy, cz, hole=hole)


def _physical_theta_faces(
    coords: dict[tuple[int, int, int], tuple[float, float, float]],
    v: tuple[int, ...],
    n_m: int,
    n_r: int,
) -> tuple[tuple[int, int, int, int], tuple[int, int, int, int]]:
    """(symmetry_0 face, symmetry_90 face) with correct winding."""

    def cz(vid: int) -> float:
        k = vid // ((n_r + 1) * n_m)
        rem = vid % ((n_r + 1) * n_m)
        j = rem // n_m
        i = rem % n_m
        return coords[(j, i, k)][2]

    v0, v1, v2, v3, v4, v5, v6, v7 = v
    bottom = (v1, v0, v3, v2)
    top = (v4, v5, v6, v7)
    if abs(cz(v0)) <= abs(cz(v4)):
        return bottom, top
    return top, bottom


def write_blockmesh_dict(
    out_path: Path,
    coords: dict[tuple[int, int, int], tuple[float, float, float]],
    meta: dict,
    *,
    lens: np.ndarray,
    iris: np.ndarray,
) -> dict:
    n_r = meta["n_r"]
    n_m = meta["n_m"]
    n_theta = meta["n_theta"]

    lines: list[str] = [
        "FoamFile",
        "{",
        "    version     2.0;",
        "    format      ascii;",
        "    class       dictionary;",
        "    object      blockMeshDict;",
        "}",
        "",
        "// G2-fluid 90° calotte — structured hex from g2_blockmesh_fluid.py",
        f"// level={meta['mesh_level']}  cells≈{meta.get('n_cells', '?')}  blocks={meta.get('n_blocks', '?')}",
        "",
        "scale   1;",
        "",
        "vertices",
        "(",
    ]

    n_k = n_theta + 1
    for k in range(n_k):
        for j in range(n_r + 1):
            for i in range(n_m):
                x, y, z = coords[(j, i, k)]
                lines.append(f"    ({x:.16e} {y:.16e} {z:.16e})")

    lines.extend([");", "", "blocks", "("])
    n_blocks = 0
    active_blocks: list[tuple[int, int]] = []
    for j in range(n_r):
        for i in range(n_m - 1):
            if not _valid_block(coords, j, i):
                continue
            v = _oriented_block_verts(coords, j, i, n_m, n_r, n_theta)
            lines.append(
                f"    hex ({v[0]} {v[1]} {v[2]} {v[3]} {v[4]} {v[5]} {v[6]} {v[7]}) "
                f"({1} {1} {n_theta}) simpleGrading (1 1 1)"
            )
            n_blocks += 1
            active_blocks.append((j, i))
    lines.append(");")
    lines.append("")
    meta["n_cells"] = n_blocks * n_theta
    meta["n_blocks"] = n_blocks

    patch_faces: dict[str, list[tuple[int, int, int, int]]] = {
        "symmetry_0": [],
        "symmetry_90": [],
        "wall": [],
        "lens_wall": [],
        "iris_wall": [],
    }

    seen_faces: set[tuple[int, ...]] = set()

    def add_face(pname: str, a: int, b: int, c: int, d: int) -> None:
        key = tuple(sorted((a, b, c, d)))
        if key in seen_faces:
            return
        seen_faces.add(key)
        if pname not in patch_faces:
            patch_faces["wall"].append((a, b, c, d))
        else:
            patch_faces[pname].append((a, b, c, d))

    active_set = set(active_blocks)

    def has_block(jj: int, ii: int) -> bool:
        return (jj, ii) in active_set

    for j, i in active_blocks:
        v0, v1, v2, v3, v4, v5, v6, v7 = _oriented_block_verts(coords, j, i, n_m, n_r, n_theta)

        sym0, sym90 = _physical_theta_faces(coords, (v0, v1, v2, v3, v4, v5, v6, v7), n_m, n_r)
        add_face("symmetry_0", *sym0)
        add_face("symmetry_90", *sym90)

        if j == 0 or not has_block(j - 1, i):
            cx, cy, cz = _face_centroid(coords, (v1, v0, v5, v4), n_m, n_r)
            pname = _classify_boundary_face(cx, cy, cz, face_kind="inner", lens=lens, iris=iris)
            add_face(pname, v1, v0, v5, v4)

        if j == n_r - 1 or not has_block(j + 1, i):
            cx, cy, cz = _face_centroid(coords, (v2, v6, v7, v3), n_m, n_r)
            pname = _classify_boundary_face(cx, cy, cz, face_kind="outer", lens=lens, iris=iris)
            add_face(pname, v2, v6, v7, v3)

        if i == 0 or not has_block(j, i - 1):
            cx, cy, cz = _face_centroid(coords, (v1, v5, v6, v2), n_m, n_r)
            pname = _classify_boundary_face(cx, cy, cz, face_kind="outer", lens=lens, iris=iris)
            add_face(pname, v1, v5, v6, v2)

        if i == n_m - 2 or not has_block(j, i + 1):
            cx, cy, cz = _face_centroid(coords, (v0, v3, v7, v4), n_m, n_r)
            pname = _classify_boundary_face(cx, cy, cz, face_kind="outer", lens=lens, iris=iris)
            add_face(pname, v0, v3, v7, v4)

    lines.append("boundary")
    lines.append("(")
    patch_type = {
        "symmetry_0": "symmetry",
        "symmetry_90": "symmetry",
        "wall": "wall",
        "lens_wall": "wall",
        "iris_wall": "wall",
    }
    patch_report: dict[str, int] = {}
    for pname in ("symmetry_0", "symmetry_90", "wall", "lens_wall", "iris_wall"):
        faces = patch_faces[pname]
        patch_report[pname] = len(faces)
        lines.append(f"    {pname}")
        lines.append("    {")
        lines.append(f"        type {patch_type[pname]};")
        lines.append("        faces")
        lines.append("        (")
        for a, b, c, d in faces:
            lines.append(f"            ({a} {b} {c} {d})")
        lines.append("        );")
        lines.append("    }")
    lines.append(");")
    lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))
    report = {**meta, "patches": patch_report, "method": "blockMesh"}
    print(f"Wrote {out_path}  ({meta['n_cells']} hexes, patches={patch_report})")
    return report


def mesh_g2_fluid_blockmesh(
    bi: dict[str, np.ndarray],
    fluid: dict[str, np.ndarray],
    dict_path: Path,
    *,
    mesh_level: str = "M1",
) -> dict:
    coords, meta = build_fluid_structured_grid(bi, fluid, mesh_level)
    lens = np.asarray(fluid["lens_half"], dtype=float)
    iris = np.asarray(fluid["iris_half"], dtype=float)
    report = write_blockmesh_dict(
        dict_path, coords, meta, lens=lens, iris=iris,
    )
    report_path = dict_path.parent / f"patch_groups_g2_fluid_blockmesh_{mesh_level}.json"
    report_path.write_text(json.dumps(report, indent=2))
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description="G2-fluid blockMeshDict generator")
    ap.add_argument("--case", default="doc-g4-sim4", help="Case under cases/")
    ap.add_argument("--mesh-level", default="M1", choices=sorted(STRUCTURED_LEVELS))
    args = ap.parse_args()

    repo = Path(__file__).resolve().parent.parent
    case = repo / "cases" / args.case
    sys_path = repo / "brunaStuff"
    import sys

    sys.path.insert(0, str(sys_path))

    from gen_lamminsalo_g2 import build_bilateral_m, build_g2_fluid_half, build_outlines_cm

    outlines = build_outlines_cm()
    bi = build_bilateral_m(outlines)
    fluid = build_g2_fluid_half(bi)

    geom = case / "geometry"
    geom.mkdir(parents=True, exist_ok=True)
    dict_path = case / "fluid" / "system" / f"blockMeshDict.{args.mesh_level}"
    mesh_g2_fluid_blockmesh(bi, fluid, dict_path, mesh_level=args.mesh_level)
    # Active dict symlink/copy for Allrun
    active = case / "fluid" / "system" / "blockMeshDict"
    active.write_text(dict_path.read_text())
    print(f"Active blockMeshDict → {active}")


if __name__ == "__main__":
    main()
