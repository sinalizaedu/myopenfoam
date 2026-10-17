#!/usr/bin/env python3
"""Diagnose wp1.1 u_r scatter vs good K integral.

Checks (in order):
  1. Mesh element normal consistency (outward n·r > 0)
  2. CCX expanded-node FRD coords vs midsurface mesh (offset ~t/2)
  3. u_r from mapped FRD disp vs u·n (correct surface measure)
  4. u_r from direct FRD nodes (no mapping)
  5. Tangential |u| vs radial |u·r̂| on midsurface
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
for _c in (
    Path("/opt/brunaStuff/artigo_mestrado"),
    HERE.parents[2] / "brunaStuff" / "artigo_mestrado",
):
    if (_c / "frd_stress.py").is_file():
        sys.path.insert(0, str(_c))
        break

from extract_K import (  # noqa: E402
    _load_mesh_and_disp,
    cavity_dV_mm3,
    parse_elements,
    parse_nodes,
    parse_nsets,
    parse_surfaces,
    radial_stats,
)
from frd_stress import parse_frd  # noqa: E402


def element_normal_outward(
    conn: list[int], nodes: dict[int, np.ndarray]
) -> tuple[np.ndarray, float]:
    """Normal from corner 1-2 × 1-4; return (unit_n, n·r at centroid)."""
    pts = np.array([nodes[conn[i]] for i in range(4)])
    c = pts.mean(axis=0)
    n = np.cross(pts[1] - pts[0], pts[3] - pts[0])
    ln = np.linalg.norm(n)
    if ln < 1e-15:
        return n, 0.0
    n = n / ln
    rhat = c / np.linalg.norm(c)
    return n, float(np.dot(n, rhat))


def check_mesh_normals(mesh_inp: Path) -> dict:
    nodes = parse_nodes(mesh_inp)
    elems = parse_elements(mesh_inp)
    dots = []
    flipped = []
    for eid, conn in elems.items():
        _, nd = element_normal_outward(conn[:8] if len(conn) >= 8 else conn, nodes)
        dots.append(nd)
        if nd < 0:
            flipped.append(eid)
    arr = np.array(dots)
    return {
        "n_elements": len(elems),
        "n_outward": int((arr > 0).sum()),
        "n_inward": int((arr < 0).sum()),
        "n_degenerate": int((np.abs(arr) < 1e-6).sum()),
        "min_dot": float(arr.min()),
        "max_dot": float(arr.max()),
        "flipped_eids": flipped[:10],
    }


def ur_from_un_dot(nodes, disp):
    """Effective normal displacement u·r̂ (r̂ from origin)."""
    vals = []
    for nid, x0 in nodes.items():
        if nid not in disp:
            continue
        rhat = x0 / np.linalg.norm(x0)
        u = np.asarray(disp[nid])
        vals.append(float(np.dot(u, rhat)))
    return np.asarray(vals)


def ur_from_un_surface(conn, nodes, disp):
    """u·n with element outward normal at centroid (4 corner avg u)."""
    pts = np.array([nodes[conn[i]] for i in range(4)])
    c = pts.mean(axis=0)
    n = np.cross(pts[1] - pts[0], pts[3] - pts[0])
    n = n / np.linalg.norm(n)
    u = np.zeros(3)
    for i in range(4):
        u += np.asarray(disp.get(conn[i], (0, 0, 0)))
    u /= 4.0
    return float(np.dot(u, n))


def frd_coord_offset(mesh_inp: Path, frd: Path) -> dict:
    nodes = parse_nodes(mesh_inp)
    frd_nodes, _, steps = parse_frd(frd)
    disp = steps[-1]["disp"]
    frd_ids = [fn for fn in frd_nodes if fn in disp]
    # nearest midsurface mesh node for each FRD node
    mesh_ids = list(nodes.keys())
    mesh_xyz = np.array([nodes[i] for i in mesh_ids])
    offsets = []
    for fn in frd_ids:
        xyz = np.array(frd_nodes[fn])
        d = np.linalg.norm(mesh_xyz - xyz, axis=1)
        j = int(np.argmin(d))
        offsets.append(float(d[j]))
    arr = np.array(offsets)
    return {
        "n_frd": len(frd_ids),
        "offset_mm_min": float(arr.min()),
        "offset_mm_median": float(np.median(arr)),
        "offset_mm_max": float(arr.max()),
        "offset_mm_mean": float(arr.mean()),
    }


def diagnose(case: str, R: float, t: float) -> dict:
    ccx = HERE.parent / "ccx"
    mesh_inp = ccx / f"{case}_ne12_mesh.inp"
    frd = ccx / f"{case}_ne12.frd"
    deck = ccx / f"{case}_ne12.inp"

    rep = {"case": case, "R_mm": R, "t_mm": t}
    rep["mesh_normals"] = check_mesh_normals(mesh_inp)
    rep["frd_offset"] = frd_coord_offset(mesh_inp, frd)

    nodes, elems, disp_mapped = _load_mesh_and_disp(mesh_inp, frd, t)
    nsets = parse_nsets(mesh_inp)
    pin = set(
        nsets.get("PIN1", []) + nsets.get("PIN2", []) + nsets.get("PIN3", [])
    )

    ur_map = ur_from_un_dot(nodes, disp_mapped)
    rep["mapped"] = {
        "n": len(ur_map),
        "mean": float(ur_map.mean()),
        "std": float(ur_map.std()),
        "std_over_mean_pct": 100 * ur_map.std() / abs(ur_map.mean()),
        "frac_negative": float((ur_map < 0).mean()),
    }
    if pin:
        mask = np.array([nid not in pin for nid in sorted(nodes) if nid in disp_mapped])
        ur_nopin = ur_from_un_dot(
            {k: v for k, v in nodes.items() if k not in pin},
            disp_mapped,
        )
        rep["mapped_no_pin"] = {
            "mean": float(ur_nopin.mean()),
            "std": float(ur_nopin.std()),
            "std_over_mean_pct": 100 * ur_nopin.std() / abs(ur_nopin.mean()),
            "frac_negative": float((ur_nopin < 0).mean()),
        }

    # Direct FRD: group by angular direction, average u·r̂
    frd_nodes, _, steps = parse_frd(frd)
    disp_raw = steps[-1]["disp"]
    frd_xyz = {fn: np.array(x) for fn, x in frd_nodes.items() if fn in disp_raw}
    ur_frd = []
    for fn, xyz in frd_xyz.items():
        rhat = xyz / np.linalg.norm(xyz)
        ur_frd.append(float(np.dot(np.asarray(disp_raw[fn]), rhat)))
    ur_frd = np.array(ur_frd)
    rep["frd_direct_ur_dot"] = {
        "n": len(ur_frd),
        "mean": float(ur_frd.mean()),
        "std": float(ur_frd.std()),
        "std_over_mean_pct": 100 * ur_frd.std() / abs(ur_frd.mean()),
        "frac_negative": float((ur_frd < 0).mean()),
    }

    # u·n at element centroids (mesh connectivity + mapped disp)
    un_elem = [
        ur_from_un_surface(c[:8] if len(c) >= 8 else c, nodes, disp_mapped)
        for c in elems.values()
    ]
    un_elem = np.array(un_elem)
    rep["element_u_dot_n"] = {
        "mean": float(un_elem.mean()),
        "std": float(un_elem.std()),
        "std_over_mean_pct": 100 * un_elem.std() / abs(un_elem.mean()),
        "frac_negative": float((un_elem < 0).mean()),
    }

    # Volume integral (authoritative for K)
    pairs = parse_surfaces(mesh_inp)["INNER_SURF"]
    dV = cavity_dV_mm3(pairs, elems, nodes, disp_mapped)
    A = 4 * np.pi * R**2
    rep["volume"] = {
        "dV_uL": dV,
        "u_r_from_dV_mm": dV / A,
        "K_FEA": 1.0 / dV,
    }

    # Tangential contamination: |u_t| / |u_r| on mapped midsurface nodes
    ratios = []
    for nid, x0 in nodes.items():
        if nid not in disp_mapped:
            continue
        rhat = x0 / np.linalg.norm(x0)
        u = np.asarray(disp_mapped[nid])
        ur = float(np.dot(u, rhat))
        ut = u - ur * rhat
        if abs(ur) > 1e-9:
            ratios.append(float(np.linalg.norm(ut) / abs(ur)))
    ratios = np.array(ratios)
    rep["tangential_ratio"] = {
        "median": float(np.median(ratios)),
        "p95": float(np.percentile(ratios, 95)),
    }

    return rep


def main() -> None:
    for case, R, t in (("human", 12.0, 0.5), ("rabbit", 7.6, 0.33)):
        r = diagnose(case, R, t)
        print(f"\n{'='*60}\nCASE: {case}\n{'='*60}")
        for k, v in r.items():
            if k == "case":
                continue
            print(f"\n[{k}]")
            if isinstance(v, dict):
                for kk, vv in v.items():
                    print(f"  {kk}: {vv}")
            else:
                print(f"  {v}")


if __name__ == "__main__":
    main()
