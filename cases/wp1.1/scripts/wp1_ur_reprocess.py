#!/usr/bin/env python3
"""wp1 ur — reprocess u_r from existing .frd (no re-simulation).

Compares three projections on human/rabbit ne12:
  A) u·r̂_geom   — geometric radial from mesh midsurface (undeformed)
  B) u·n_elem   — element connectivity normal (corner 1-2 × 1-4), per element
  C) pipeline   — current extract_K radial_stats path

Also reports inverted-element count (n·r̂_centroid < 0).
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
    parse_surfaces,
    radial_stats,
)
from frd_stress import parse_frd  # noqa: E402


def mesh_normal_check(mesh_inp: Path) -> dict:
    nodes = parse_nodes(mesh_inp)
    elems = parse_elements(mesh_inp)
    inward = []
    for eid, conn in elems.items():
        pts = np.array([nodes[conn[i]] for i in range(4)])
        c = pts.mean(0)
        n = np.cross(pts[1] - pts[0], pts[3] - pts[0])
        n = n / np.linalg.norm(n)
        rhat = c / np.linalg.norm(c)
        if float(np.dot(n, rhat)) < 0:
            inward.append(eid)
    return {
        "n_elements": len(elems),
        "n_inward": len(inward),
        "inward_eids": inward[:20],
    }


def ur_geometric_clean(mesh_inp: Path, frd_path: Path, match_tol_mm: float = 0.01):
    """u_r = u·r̂ with r̂ from undeformed mesh node; u from nearest FRD node by XYZ."""
    mesh = parse_nodes(mesh_inp)
    frd_nodes, _, steps = parse_frd(frd_path)
    disp_frd = steps[-1]["disp"]
    frd_ids = np.array([fn for fn in frd_nodes if fn in disp_frd])
    frd_xyz = np.array([frd_nodes[int(fn)] for fn in frd_ids], dtype=np.float64)

    urs = []
    miss = 0
    for mnid, x0 in sorted(mesh.items()):
        d = np.linalg.norm(frd_xyz - x0, axis=1)
        j = int(np.argmin(d))
        if d[j] > match_tol_mm:
            miss += 1
            continue
        fn = int(frd_ids[j])
        rhat = x0 / np.linalg.norm(x0)
        u = np.asarray(disp_frd[fn], dtype=np.float64)
        urs.append(float(np.dot(u, rhat)))

    arr = np.array(urs)
    return {
        "method": "u·r̂_geom (mesh XYZ match, tol={} mm)".format(match_tol_mm),
        "n": len(arr),
        "missed_nodes": miss,
        "mean_mm": float(arr.mean()),
        "std_mm": float(arr.std()),
        "std_over_mean_pct": 100 * float(arr.std() / abs(arr.mean())),
        "frac_negative_pct": 100 * float((arr < 0).mean()),
    }


def ur_geometric_angular_mean(mesh_inp: Path, frd_path: Path):
    """u_r = (mean u at angle)·r̂ — average all expanded FRD nodes per direction."""
    mesh = parse_nodes(mesh_inp)
    frd_nodes, _, steps = parse_frd(frd_path)
    disp_frd = steps[-1]["disp"]
    tol = 1e-3
    buckets: dict[tuple, list[np.ndarray]] = {}
    for fn, xyz in frd_nodes.items():
        if fn not in disp_frd:
            continue
        xyz = np.asarray(xyz)
        key = tuple(int(round(c / tol)) for c in xyz / np.linalg.norm(xyz))
        buckets.setdefault(key, []).append(np.asarray(disp_frd[fn]))

    urs = []
    for x0 in mesh.values():
        key = tuple(int(round(c / tol)) for c in x0 / np.linalg.norm(x0))
        vals = buckets.get(key)
        if not vals:
            continue
        u = np.mean(vals, axis=0)
        rhat = x0 / np.linalg.norm(x0)
        urs.append(float(np.dot(u, rhat)))

    arr = np.array(urs)
    return {
        "method": "u·r̂_geom (angular mean of expanded FRD u)",
        "n": len(arr),
        "mean_mm": float(arr.mean()),
        "std_mm": float(arr.std()),
        "std_over_mean_pct": 100 * float(arr.std() / abs(arr.mean())),
        "frac_negative_pct": 100 * float((arr < 0).mean()),
    }


def ur_element_normal(mesh_inp: Path, frd_path: Path, t: float):
    """u·n_elem at element centroid (uses connectivity normal, NOT geometric r̂)."""
    mesh = parse_nodes(mesh_inp)
    elems = parse_elements(mesh_inp)
    _, _, disp = _load_mesh_and_disp(mesh_inp, frd_path, t)
    uns = []
    for conn in elems.values():
        pts = np.array([mesh[conn[i]] for i in range(4)])
        n = np.cross(pts[1] - pts[0], pts[3] - pts[0])
        n = n / np.linalg.norm(n)
        u = sum(np.asarray(disp.get(conn[i], (0, 0, 0))) for i in range(4)) / 4.0
        uns.append(float(np.dot(u, n)))
    arr = np.array(uns)
    return {
        "method": "u·n_elem at centroid (connectivity normal)",
        "n": len(arr),
        "mean_mm": float(arr.mean()),
        "std_mm": float(arr.std()),
        "std_over_mean_pct": 100 * float(arr.std() / abs(arr.mean())),
        "frac_negative_pct": 100 * float((arr < 0).mean()),
    }


def pipeline_radial(mesh_inp: Path, frd_path: Path, t: float):
    nodes, _, disp = _load_mesh_and_disp(mesh_inp, frd_path, t)
    rs = radial_stats(nodes, disp)
    return {
        "method": "pipeline radial_stats() [u·r̂_geom on mapped disp]",
        "n": rs["u_r_n"],
        "mean_mm": rs["u_r_mean_mm"],
        "std_mm": rs["u_r_std_mm"],
        "std_over_mean_pct": rs["u_r_std_over_mean_pct"],
        "frac_negative_pct": float("nan"),  # not tracked
    }


def main() -> None:
    ccx = HERE.parent / "ccx"
    cases = (("human", 12.0, 0.5), ("rabbit", 7.6, 0.33))
    print("=" * 70)
    print("wp1 ur — u_r reprocessing (existing ne12 .frd, no re-simulation)")
    print("=" * 70)

    for name, R, t in cases:
        mesh_inp = ccx / f"{name}_ne12_mesh.inp"
        frd = ccx / f"{name}_ne12.frd"
        print(f"\n### {name.upper()}  R={R} mm  t={t} mm ###\n")

        nc = mesh_normal_check(mesh_inp)
        print("Mesh orientation check (connectivity normal · r̂_centroid > 0):")
        print(f"  elements: {nc['n_elements']}  inward/flipped: {nc['n_inward']}")
        if nc["n_inward"]:
            print(f"  inward eids (sample): {nc['inward_eids']}")

        pairs = parse_surfaces(mesh_inp)["INNER_SURF"]
        elems = parse_elements(mesh_inp)
        nodes, _, disp = _load_mesh_and_disp(mesh_inp, frd, t)
        dV = cavity_dV_mm3(pairs, elems, nodes, disp)
        A = 4 * np.pi * R**2
        print(f"\nVolume check: ΔV={dV:.6f} µL  u_r_from_ΔV={dV/A:.6f} mm\n")

        methods = [
            ur_geometric_clean(mesh_inp, frd),
            ur_geometric_angular_mean(mesh_inp, frd),
            ur_element_normal(mesh_inp, frd, t),
            pipeline_radial(mesh_inp, frd, t),
        ]
        print(f"{'method':<55} {'std/mean%':>10} {'neg%':>8}")
        print("-" * 75)
        for m in methods:
            neg = m.get("frac_negative_pct", float("nan"))
            neg_s = f"{neg:7.2f}" if neg == neg else "    n/a"
            print(
                f"{m['method']:<55} {m['std_over_mean_pct']:10.2f} {neg_s:>8}"
            )

    print("\n" + "=" * 70)
    print("CODE REFERENCE (extract_K.py radial_stats, lines ~270-274):")
    print("  rhat = x0 / np.linalg.norm(x0)   # geometric, from mesh node")
    print("  ur   = np.dot(u, rhat)           # NOT element normal")
    print("Volume integral (cavity_dV_mm3) uses u·n on Gauss points (face normal).")
    print("=" * 70)


if __name__ == "__main__":
    main()
