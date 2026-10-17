#!/usr/bin/env python3
"""Cavity volume vs pressure from a CalculiX .inp mesh + .frd displacements.

V = (1/3) Σ r·n A on FSI_ACTIVE_SURF plus polar-cap surfaces (holes that do
not pass through the origin). Symmetry planes are skipped (r·n = 0).
Times four for the full eye.

    python3 brunaStuff/extract_inflation.py \\
        --inp cases/fea-simplf/ccx/fea-simplf.inp \\
        --frd cases/fea-simplf/ccx/fea-simplf.frd \\
        --out cases/fea-simplf/results/inflation.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "artigo_mestrado"))
from frd_stress import parse_frd  # noqa: E402

MMHG = 133.322
P0_MMHG = 15.0
P0_PA = P0_MMHG * MMHG
PMAX_PA = 50.0 * MMHG
DV_UL = 50.0  # full-eye extra volume of the protocol


def parse_nodes(inp: Path) -> dict[int, np.ndarray]:
    nodes = {}
    lines = inp.read_text().splitlines()
    i = 0
    while i < len(lines):
        if lines[i].upper().startswith("*NODE"):
            i += 1
            while i < len(lines) and not lines[i].startswith("*"):
                s = lines[i].strip()
                i += 1
                if not s or s.startswith("**"):
                    continue
                parts = [p.strip() for p in s.split(",")]
                if len(parts) < 4:
                    continue
                nid = int(parts[0])
                nodes[nid] = np.array(
                    [float(parts[1]), float(parts[2]), float(parts[3])], dtype=np.float64
                )
            continue
        if lines[i].upper().startswith("*INCLUDE"):
            m = re.search(r"INPUT\s*=\s*(\S+)", lines[i], re.I)
            if m:
                inc = (inp.parent / m.group(1).strip()).resolve()
                nodes.update(parse_nodes(inc))
        i += 1
    return nodes


def parse_elements(inp: Path) -> dict[int, list[int]]:
    elems = {}
    lines = inp.read_text().splitlines()
    i = 0
    while i < len(lines):
        u = lines[i].upper()
        if u.startswith("*INCLUDE"):
            m = re.search(r"INPUT\s*=\s*(\S+)", lines[i], re.I)
            if m:
                inc = (inp.parent / m.group(1).strip()).resolve()
                elems.update(parse_elements(inc))
            i += 1
            continue
        if u.startswith("*ELEMENT"):
            i += 1
            while i < len(lines) and not lines[i].startswith("*"):
                s = lines[i].strip()
                i += 1
                if not s or s.startswith("**"):
                    continue
                parts = [p.strip() for p in s.split(",") if p.strip()]
                eid = int(parts[0])
                elems[eid] = [int(x) for x in parts[1:]]
            continue
        i += 1
    return elems


def parse_surfaces(inp: Path) -> dict[str, list[tuple[int, int]]]:
    surfs: dict[str, list[tuple[int, int]]] = {}
    lines = inp.read_text().splitlines()
    i = 0
    while i < len(lines):
        u = lines[i].upper()
        if u.startswith("*INCLUDE"):
            m = re.search(r"INPUT\s*=\s*(\S+)", lines[i], re.I)
            if m:
                inc = (inp.parent / m.group(1).strip()).resolve()
                for k, v in parse_surfaces(inc).items():
                    surfs.setdefault(k, []).extend(v)
            i += 1
            continue
        if u.startswith("*SURFACE"):
            m = re.search(r"NAME\s*=\s*([^,\s]+)", lines[i], re.I)
            name = m.group(1).upper() if m else "UNNAMED"
            pairs = []
            i += 1
            while i < len(lines) and not lines[i].startswith("*"):
                s = lines[i].strip()
                i += 1
                if not s or s.startswith("**"):
                    continue
                parts = [p.strip() for p in s.split(",") if p.strip()]
                if len(parts) >= 2:
                    loc = int(parts[1].lstrip("Ss"))
                    pairs.append((int(parts[0]), loc))
            surfs.setdefault(name, []).extend(pairs)
            continue
        i += 1
    return surfs


# C3D8 / C3D8I face node indices (0-based into the 8-node list), CCX winding
HEX_FACES = {
    1: (0, 1, 2, 3),
    2: (4, 7, 6, 5),
    3: (0, 1, 5, 4),
    4: (1, 2, 6, 5),
    5: (2, 3, 7, 6),
    6: (3, 0, 4, 7),
}
# C3D6
WEDGE_FACES = {
    1: (0, 1, 2),
    2: (3, 5, 4),
    3: (0, 1, 4, 3),
    4: (1, 2, 5, 4),
    5: (2, 0, 3, 5),
}


def face_nodes(conn: list[int], loc: int) -> list[int]:
    if len(conn) >= 8:
        idx = HEX_FACES[loc]
        return [conn[i] for i in idx]
    idx = WEDGE_FACES[loc]
    return [conn[i] for i in idx]


def tri_vol(a, b, c) -> float:
    return float(np.dot(a, np.cross(b, c))) / 6.0


def face_vol(pts: list[np.ndarray]) -> float:
    if len(pts) == 3:
        return tri_vol(pts[0], pts[1], pts[2])
    # quad → two tris (0-1-2, 0-2-3)
    return tri_vol(pts[0], pts[1], pts[2]) + tri_vol(pts[0], pts[2], pts[3])


def surface_volume(pairs, elems, nodes, disp) -> float:
    v = 0.0
    for eid, loc in pairs:
        conn = elems[eid]
        nids = face_nodes(conn, loc)
        pts = []
        for nid in nids:
            x0 = nodes[nid]
            u = disp.get(nid, (0.0, 0.0, 0.0))
            pts.append(x0 + np.asarray(u, dtype=np.float64))
        v += face_vol(pts)
    return v


def pressure_from_time(t: float, t_prev: float | None) -> float:
    """Map CalculiX step time to IOP [Pa].

    Two *STATIC periods of 1.0: cumulative t in (0,1] → 0..15 mmHg,
    (1,2] → 15..50 mmHg. If the second step restarts at 0, caller should
    pass already-cumulative time.
    """
    if t <= 1.0 + 1e-9:
        return P0_PA * t
    return P0_PA + (PMAX_PA - P0_PA) * (t - 1.0)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inp", required=True, type=Path)
    ap.add_argument("--frd", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--label", default="")
    args = ap.parse_args()

    nodes = parse_nodes(args.inp)
    elems = parse_elements(args.inp)
    surfs = parse_surfaces(args.inp)
    print(f"nodes={len(nodes)} elems={len(elems)} surfaces={list(surfs)}")

    inner_names = [n for n in surfs if n in ("FSI_ACTIVE_SURF", "FSI_IRIS_SURF")]
    cap_names = [n for n in surfs if n in ("POLAR_POST_SURF", "POLAR_ANT_SURF")]
    inner_pairs = []
    for n in inner_names:
        inner_pairs.extend(surfs[n])
    cap_pairs = []
    for n in cap_names:
        cap_pairs.extend(surfs[n])
    print(f"  inner faces={len(inner_pairs)}  polar caps={len(cap_pairs)}")

    frd_nodes, _, steps = parse_frd(args.frd)
    if not nodes and frd_nodes:
        nodes = {nid: np.asarray(xyz, dtype=np.float64) for nid, xyz in frd_nodes.items()}

    # undeformed volume
    v0_wedge = surface_volume(inner_pairs, elems, nodes, {}) + surface_volume(
        cap_pairs, elems, nodes, {}
    )
    v0_full_ul = 4.0 * v0_wedge * 1e9  # m3 → µL  (1 m3 = 1e9 µL?  1e-9 m3 = 1 µL so m3*1e9 = µL)
    # 1 µL = 1e-9 m³ → µL = m³ * 1e9. Yes.

    # first stored increment: cornea apex (min y) must move further anterior (Uy < 0).
    # Posterior Uy may be exactly 0 if the posterior ring is pinned (fea-simplf).
    steps_sorted = sorted(steps, key=lambda d: (d["lam"] if d["lam"] is not None else 0.0))
    apex_id = min(nodes, key=lambda n: nodes[n][1])
    post_id = max(nodes, key=lambda n: nodes[n][1])

    rows = []
    t_offset = 0.0
    last_t = 0.0
    v_at_15 = None
    for i, stp in enumerate(steps_sorted):
        t_raw = float(stp["lam"] if stp["lam"] is not None else 0.0)
        if i > 0 and t_raw + 1e-9 < last_t:
            t_offset += last_t
        t = t_raw + t_offset
        last_t = t_raw
        p_pa = pressure_from_time(t, None)
        p_mmhg = p_pa / MMHG
        disp = stp["disp"]
        vw = surface_volume(inner_pairs, elems, nodes, disp) + surface_volume(
            cap_pairs, elems, nodes, disp
        )
        v_full_ul = 4.0 * vw * 1e9
        uy_apex = disp.get(apex_id, (0.0, 0.0, 0.0))[1]
        uy_post = disp.get(post_id, (0.0, 0.0, 0.0))[1]
        rows.append(
            dict(
                i=i,
                t=t,
                p_pa=p_pa,
                p_mmhg=p_mmhg,
                v_wedge_m3=vw,
                v_full_uL=v_full_ul,
                uy_apex=uy_apex,
                uy_post=uy_post,
            )
        )
        if v_at_15 is None and p_mmhg >= P0_MMHG - 0.05:
            v_at_15 = v_full_ul

    if v_at_15 is None and rows:
        v_at_15 = rows[-1]["v_full_uL"]

    for r in rows:
        r["dV_full_uL"] = r["v_full_uL"] - v_at_15

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            w.writeheader()
            w.writerows(rows)

    # diagnostics
    first = next((r for r in rows if r["p_mmhg"] > 0.3), None)
    last = rows[-1] if rows else None
    vol_up = bool(last and last["v_full_uL"] > v0_full_ul)
    if first is None:
        outward = False
        msg_out = "NO positive-P increment"
    else:
        ok_apex = first["uy_apex"] < 0.0
        outward = ok_apex and vol_up
        msg_out = (
            f"first P={first['p_mmhg']:.2f} mmHg  "
            f"Uy_apex={first['uy_apex']:.3e} (want <0)  "
            f"Uy_post={first['uy_post']:.3e} (0 ok if ring pinned)  "
            f"dV={last['v_full_uL'] - v0_full_ul:.2f} µL"
        )

    dV_max = max((r["dV_full_uL"] for r in rows), default=0.0)
    covers = dV_max >= DV_UL

    # interpolate P at +50 µL on the living branch
    living = [r for r in rows if r["p_mmhg"] >= P0_MMHG - 0.2]
    p_at_50 = None
    if len(living) >= 2:
        xs = np.array([r["dV_full_uL"] for r in living])
        ys = np.array([r["p_mmhg"] for r in living])
        order = np.argsort(xs)
        xs, ys = xs[order], ys[order]
        if xs[0] <= DV_UL <= xs[-1]:
            p_at_50 = float(np.interp(DV_UL, xs, ys))
        elif covers is False:
            # do not silently extrapolate here; goldmann script may
            p_at_50 = float(np.interp(DV_UL, xs, ys))

    summary = {
        "label": args.label or args.frd.stem,
        "v0_wedge_m3": v0_wedge,
        "v0_full_uL": v0_full_ul,
        "v_at_15_uL": v_at_15,
        "outward_ok": bool(outward),
        "outward_msg": msg_out,
        "dV_max_uL": dV_max,
        "covers_50uL": bool(covers),
        "P_at_50uL_mmHg": p_at_50,
        "dIOP_50uL_mmHg": (None if p_at_50 is None else p_at_50 - P0_MMHG),
        "n_steps": len(rows),
        "csv": str(args.out),
    }
    sum_path = args.out.with_suffix(".json")
    sum_path.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    if not outward:
        print("ERROR: inner surface moved INWARD — flip *DSLOAD P sign", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
