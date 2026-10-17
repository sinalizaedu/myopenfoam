#!/usr/bin/env python3
"""Extract K_FEA = dP/dV from a wp1.1 CalculiX run.

Volume change from cavity boundary:  dV = integral(u . n dA)  on INNER_SURF.

FRD mapping: KDTree nearest nodes at R±t/2, arithmetic mean → midsurface u
(linear through-thickness shell theory). Replaces superseded angular-bucket method.

Also reports radial displacement uniformity on midsurface nodes.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
for _cand in (
    Path("/opt/brunaStuff/artigo_mestrado"),
    HERE.parents[2] / "brunaStuff" / "artigo_mestrado",
):
    if (_cand / "frd_stress.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from frd_stress import parse_frd  # noqa: E402

MMHG_TO_PA = 133.322
MMHG_TO_MPA = MMHG_TO_PA * 1e-6  # N/mm² when length in mm


def parse_nodes(inp: Path) -> dict[int, np.ndarray]:
    nodes: dict[int, np.ndarray] = {}
    lines = inp.read_text().splitlines()
    i = 0
    while i < len(lines):
        if re.match(r"^\*NODE\b", lines[i], re.I) and "FILE" not in lines[i].upper():
            i += 1
            while i < len(lines) and not lines[i].startswith("*"):
                s = lines[i].strip()
                i += 1
                if not s or s.startswith("**"):
                    continue
                parts = [p.strip() for p in s.split(",")]
                nid = int(parts[0])
                nodes[nid] = np.array([float(parts[1]), float(parts[2]), float(parts[3])])
            continue
        if lines[i].upper().startswith("*INCLUDE"):
            m = re.search(r"INPUT\s*=\s*(\S+)", lines[i], re.I)
            if m:
                inc = (inp.parent / m.group(1).strip()).resolve()
                nodes.update(parse_nodes(inc))
        i += 1
    return nodes


def parse_elements(inp: Path) -> dict[int, list[int]]:
    elems: dict[int, list[int]] = {}
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
        if re.match(r"^\*ELEMENT\b", lines[i], re.I):
            i += 1
            while i < len(lines) and not lines[i].startswith("*"):
                s = lines[i].strip()
                i += 1
                if not s or s.startswith("**"):
                    continue
                parts = [p.strip() for p in s.split(",") if p.strip()]
                elems[int(parts[0])] = [int(x) for x in parts[1:]]
            continue
        i += 1
    return elems


def parse_nsets(inp: Path) -> dict[str, list[int]]:
    nsets: dict[str, list[int]] = {}
    lines = inp.read_text().splitlines()
    i = 0
    while i < len(lines):
        u = lines[i].upper()
        if u.startswith("*INCLUDE"):
            m = re.search(r"INPUT\s*=\s*(\S+)", lines[i], re.I)
            if m:
                inc = (inp.parent / m.group(1).strip()).resolve()
                for k, v in parse_nsets(inc).items():
                    nsets.setdefault(k, []).extend(v)
            i += 1
            continue
        if u.startswith("*NSET"):
            m = re.search(r"NSET\s*=\s*([^,\s]+)", lines[i], re.I)
            name = m.group(1).upper() if m else "UNNAMED"
            ids: list[int] = []
            i += 1
            while i < len(lines) and not lines[i].startswith("*"):
                s = lines[i].strip()
                i += 1
                if not s or s.startswith("**"):
                    continue
                ids.extend(int(p.strip()) for p in s.split(",") if p.strip())
            nsets.setdefault(name, []).extend(ids)
            continue
        i += 1
    return nsets


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
                pairs.append((int(parts[0]), int(parts[1].lstrip("Ss"))))
            surfs.setdefault(name, []).extend(pairs)
            continue
        i += 1
    return surfs


def parse_pressure_mpa(inp: Path) -> float:
    """Return |P| in MPa (N/mm²) from first *DSLOAD block."""
    text = inp.read_text()
    m = re.search(r"\*DSLOAD[^\n]*\n[^\n]*,\s*P\s*,\s*([^\n]+)", text, re.I)
    if not m:
        raise ValueError(f"No *DSLOAD pressure in {inp}")
    return abs(float(m.group(1).split(",")[0]))


# S4 / S8 face S1 node indices (0-based in connectivity)
S4_FACE = (0, 1, 2, 3)
S8_FACE = (0, 1, 2, 3, 4, 5, 6, 7)


def _shape_s4(xi: float, eta: float) -> np.ndarray:
    return np.array(
        [
            0.25 * (1 - xi) * (1 - eta),
            0.25 * (1 + xi) * (1 - eta),
            0.25 * (1 + xi) * (1 + eta),
            0.25 * (1 - xi) * (1 + eta),
        ]
    )


def _shape_s8(xi: float, eta: float) -> np.ndarray:
    # serendipity 8-node quad
    s = np.array([-1, 1, 1, -1, 0, 1, 0, -1], dtype=float)
    t = np.array([-1, -1, 1, 1, -1, 0, 1, 0], dtype=float)
    n = np.zeros(8)
    for i in range(8):
        si, ti = s[i], t[i]
        n[i] = 0.25 * (1 + si * xi) * (1 + ti * eta) * (si * xi + ti * eta - 1)
    # mids
    n[4] = 0.5 * (1 - xi * xi) * (1 - eta)
    n[5] = 0.5 * (1 + xi) * (1 - eta * eta)
    n[6] = 0.5 * (1 - xi * xi) * (1 + eta)
    n[7] = 0.5 * (1 - xi) * (1 - eta * eta)
    return n


def _gauss_points(order: int, gauss_order: int = 2) -> list[tuple[float, float, float]]:
    """Return (xi, eta, weight) for face integration."""
    if gauss_order == 3:
        g = math.sqrt(3.0 / 5.0)
        pts = (-g, 0.0, g)
        w1d = (5.0 / 9.0, 8.0 / 9.0, 5.0 / 9.0)
        out: list[tuple[float, float, float]] = []
        for i, xi in enumerate(pts):
            for j, eta in enumerate(pts):
                out.append((xi, eta, w1d[i] * w1d[j]))
        return out
    gp = (-1 / math.sqrt(3), 1 / math.sqrt(3))
    return [(xi, eta, 1.0) for xi in gp for eta in gp]


def _integrate_face(
    nids: list[int],
    nodes: dict[int, np.ndarray],
    disp: dict[int, tuple[float, float, float]],
    order: int,
    gauss_order: int = 2,
) -> float:
    """Integrate u·n dA on one element face (midsurface)."""
    dv = 0.0
    shape_fn = _shape_s8 if order == 2 else _shape_s4
    for xi, eta, weight in _gauss_points(order, gauss_order=gauss_order):
        N = shape_fn(xi, eta)
        u = np.zeros(3)
        for k, nid in enumerate(nids):
            du = disp.get(nid, (0.0, 0.0, 0.0))
            u += N[k] * np.asarray(du)
        dN_dxi = np.zeros(len(nids))
        dN_deta = np.zeros(len(nids))
        eps = 1e-6
        Np = shape_fn(xi + eps, eta)
        Nm = shape_fn(xi - eps, eta)
        for k in range(len(nids)):
            dN_dxi[k] = (Np[k] - Nm[k]) / (2 * eps)
        Np = shape_fn(xi, eta + eps)
        Nm = shape_fn(xi, eta - eps)
        for k in range(len(nids)):
            dN_deta[k] = (Np[k] - Nm[k]) / (2 * eps)
        dx_dxi = sum(dN_dxi[k] * nodes[nids[k]] for k in range(len(nids)))
        dx_deta = sum(dN_deta[k] * nodes[nids[k]] for k in range(len(nids)))
        nvec = np.cross(dx_dxi, dx_deta)
        dv += np.dot(u, nvec) * weight
    return float(dv)


def cavity_dV_mm3(
    pairs: list[tuple[int, int]],
    elems: dict[int, list[int]],
    nodes: dict[int, np.ndarray],
    disp: dict[int, tuple[float, float, float]],
    gauss_order: int = 2,
) -> float:
    total = 0.0
    for eid, loc in pairs:
        if loc != 1:
            continue
        conn = elems[eid]
        order = 2 if len(conn) >= 8 else 1
        nface = conn[:8] if order == 2 else conn[:4]
        face = [nface[i] for i in (S8_FACE if order == 2 else S4_FACE)]
        total += _integrate_face(face, nodes, disp, order, gauss_order=gauss_order)
    return total


def _mesh_meta(mesh_inp: Path) -> dict:
    meta = mesh_inp.with_suffix(".meta.json")
    if meta.is_file():
        return json.loads(meta.read_text())
    out: dict = {}
    for line in mesh_inp.read_text().splitlines():
        if "volume_scale=" in line:
            out["volume_scale"] = float(line.split("volume_scale=")[1].split()[0])
        if "mesh_kind=" in line:
            out["mesh_kind"] = line.split("mesh_kind=")[1].split()[0]
    return out


def radial_stats(
    nodes: dict[int, np.ndarray],
    disp: dict[int, tuple[float, float, float]],
    exclude: set[int] | None = None,
    dedupe_tol: float | None = None,
) -> dict:
    """Radial displacement stats; optional dedupe by position (expanded S8 nodes).

    WARNING (wp1.1 diagnostic): std/mean of nodal u·r̂ is NOT a reliable QA
    metric for S8 cubic-sphere shells — can read ~100% even when ∫u·n dA (K)
    matches analytic to <0.1%.  See DIAGNOSTIC_ur_extraction.md.  Prefer
    cavity_dV_mm3() for volume/K; use this only as exploratory output.
    """
    exclude = exclude or set()
    urs = []
    if dedupe_tol is not None:
        buckets: dict[tuple[int, int, int], list[float]] = {}
        for nid, x0 in nodes.items():
            if nid not in disp:
                continue
            key = tuple(int(round(c / dedupe_tol)) for c in x0)
            rhat = x0 / np.linalg.norm(x0)
            ur = float(np.dot(np.asarray(disp[nid]), rhat))
            buckets.setdefault(key, []).append(ur)
        urs = [float(np.mean(v)) for v in buckets.values()]
    else:
        for nid, x0 in nodes.items():
            if nid not in disp or nid in exclude:
                continue
            rhat = x0 / np.linalg.norm(x0)
            urs.append(float(np.dot(np.asarray(disp[nid]), rhat)))
    arr = np.asarray(urs)
    mean = float(arr.mean())
    std = float(arr.std())
    return {
        "u_r_mean_mm": mean,
        "u_r_std_mm": std,
        "u_r_std_over_mean_pct": 100.0 * std / abs(mean) if abs(mean) > 1e-15 else float("nan"),
        "u_r_n": len(arr),
    }


def K_analytic_mmHg_per_uL(R_mm: float, t_mm: float, E_MPa: float, nu: float) -> float:
    R_m = R_mm * 1e-3
    t_m = t_mm * 1e-3
    E_Pa = E_MPa * 1e6
    K_Pa_m3 = t_m * E_Pa / (2 * math.pi * R_m**4 * (1 - nu))
    return K_Pa_m3 * 1e-9 / MMHG_TO_PA


def _map_frd_disp_to_mesh(
    mesh_nodes: dict[int, np.ndarray],
    frd_nodes: dict[int, tuple],
    disp: dict[int, tuple[float, float, float]],
    t_mm: float,
) -> dict[int, tuple[float, float, float]]:
    """Map expanded S8 FRD displacements onto midsurface nodes (KDTree R±t/2 + mean).

    CalculiX writes top/bottom shell nodes at R±t/2. Under linear through-thickness
    variation, the arithmetic mean is the midsurface displacement.
    """
    frd_ids = np.array([fn for fn in frd_nodes if fn in disp], dtype=int)
    if len(frd_ids) == 0:
        return {}
    frd_xyz = np.array([frd_nodes[int(fn)] for fn in frd_ids], dtype=np.float64)
    frd_u = np.array([disp[int(fn)] for fn in frd_ids], dtype=np.float64)

    mnids = list(mesh_nodes.keys())
    mids = np.array([mesh_nodes[n] for n in mnids], dtype=np.float64)
    r = np.linalg.norm(mids, axis=1)
    rhat = mids / r[:, None]
    half_t = t_mm / 2.0
    targets = np.vstack([rhat * (r + half_t)[:, None], rhat * (r - half_t)[:, None]])

    try:
        from scipy.spatial import cKDTree

        _, idx = cKDTree(frd_xyz).query(targets)
    except ImportError:
        idx = np.array(
            [int(np.argmin(np.linalg.norm(frd_xyz - p, axis=1))) for p in targets],
            dtype=int,
        )

    idx = np.asarray(idx, dtype=int).reshape(2, len(mnids))
    u_mean = 0.5 * (frd_u[idx[0]] + frd_u[idx[1]])
    return {mnid: tuple(u_mean[i]) for i, mnid in enumerate(mnids)}


def _load_mesh_and_disp(
    mesh_inp: Path,
    frd: Path,
    t_mm: float,
) -> tuple[dict[int, np.ndarray], dict[int, list[int]], dict[int, tuple[float, float, float]]]:
    mesh_nodes = parse_nodes(mesh_inp)
    elems = parse_elements(mesh_inp)
    frd_nodes, _, steps = parse_frd(frd)
    if not steps:
        raise ValueError(f"No steps in {frd}")
    disp_raw = steps[-1]["disp"]
    disp = _map_frd_disp_to_mesh(mesh_nodes, frd_nodes, disp_raw, t_mm)
    if len(disp) < len(mesh_nodes):
        raise ValueError(
            f"Mapped only {len(disp)}/{len(mesh_nodes)} mesh nodes from FRD"
        )
    return mesh_nodes, elems, disp


def extract(
    inp: Path,
    frd: Path,
    R_mm: float,
    t_mm: float,
    E_MPa: float = 3.0,
    nu: float = 0.47,
) -> dict:
    mesh_inp = inp
    if inp.read_text().upper().find("*INCLUDE") >= 0:
        m = re.search(r"INPUT\s*=\s*(\S+)", inp.read_text(), re.I)
        if m:
            mesh_inp = (inp.parent / m.group(1).strip()).resolve()

    surfs = parse_surfaces(mesh_inp)
    pairs = surfs.get("INNER_SURF", [])
    if not pairs:
        raise ValueError("INNER_SURF not found")

    nodes, elems, disp = _load_mesh_and_disp(mesh_inp, frd, t_mm)

    meta = _mesh_meta(mesh_inp)
    gauss_order = 3 if meta.get("mesh_kind") == "spherical" else 2
    volume_scale = float(meta.get("volume_scale", 1.0))

    dV_mm3 = cavity_dV_mm3(pairs, elems, nodes, disp, gauss_order=gauss_order)
    dV_uL = dV_mm3 * volume_scale  # 1 mm³ = 1 µL; scale octant → full sphere

    dP_MPa = parse_pressure_mpa(inp)
    dP_mmHg = dP_MPa / MMHG_TO_MPA

    K_FEA = dP_mmHg / dV_uL if abs(dV_uL) > 1e-20 else float("inf")
    K_an = K_analytic_mmHg_per_uL(R_mm, t_mm, E_MPa, nu)
    err_pct = 100.0 * (K_FEA - K_an) / K_an

    nsets = parse_nsets(mesh_inp)
    pin = set(nsets.get("PIN1", []) + nsets.get("PIN2", []) + nsets.get("PIN3", []))
    rstats = radial_stats(nodes, disp, exclude=pin)
    A_mm2 = 4.0 * math.pi * R_mm**2
    dV_uniform_uL = A_mm2 * rstats["u_r_mean_mm"]
    u_r_from_dV = dV_uL / A_mm2
    rstats["u_r_from_dV_mm"] = u_r_from_dV
    rstats["u_r_nodal_vs_dV_pct"] = (
        100.0 * abs(rstats["u_r_mean_mm"] - u_r_from_dV) / abs(u_r_from_dV)
        if abs(u_r_from_dV) > 1e-15
        else float("nan")
    )

    return {
        "dP_mmHg": dP_mmHg,
        "dV_uL": dV_uL,
        "dV_uniform_uL": dV_uniform_uL,
        "K_FEA_mmHg_per_uL": K_FEA,
        "K_analytic_mmHg_per_uL": K_an,
        "error_pct": err_pct,
        "n_elements": len(elems),
        "n_nodes": len(nodes),
        "radial": rstats,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inp", required=True, type=Path)
    ap.add_argument("--frd", required=True, type=Path)
    ap.add_argument("--R", type=float, required=True)
    ap.add_argument("--t", type=float, required=True)
    ap.add_argument("--E", type=float, default=3.0)
    ap.add_argument("--nu", type=float, default=0.47)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    res = extract(args.inp, args.frd, args.R, args.t, args.E, args.nu)
    txt = json.dumps(res, indent=2)
    print(txt)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(txt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
