#!/usr/bin/env python3
"""Extract P(V) from compat octant FRD (OUTPUT=2D, Gauss 3x3, dV*8)."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

WP1_SCRIPTS = Path(__file__).resolve().parents[2] / "wp1.1" / "scripts"
sys.path.insert(0, str(WP1_SCRIPTS))

from octant_mesh_compat import build_octant_mesh  # noqa: E402

GAUSS_3 = [(-math.sqrt(3 / 5), 5 / 9), (0.0, 8 / 9), (math.sqrt(3 / 5), 5 / 9)]


def s8_shape_and_deriv(xi: float, eta: float):
    n = np.zeros(8)
    d_ndxi = np.zeros(8)
    d_ndeta = np.zeros(8)
    n[0] = 0.25 * (1 - xi) * (1 - eta) * (-xi - eta - 1)
    n[1] = 0.25 * (1 + xi) * (1 - eta) * (xi - eta - 1)
    n[2] = 0.25 * (1 + xi) * (1 + eta) * (xi + eta - 1)
    n[3] = 0.25 * (1 - xi) * (1 + eta) * (-xi + eta - 1)
    n[4] = 0.5 * (1 - xi * xi) * (1 - eta)
    n[5] = 0.5 * (1 + xi) * (1 - eta * eta)
    n[6] = 0.5 * (1 - xi * xi) * (1 + eta)
    n[7] = 0.5 * (1 - xi) * (1 - eta * eta)
    d_ndxi[0] = 0.25 * (1 - eta) * (2 * xi + eta)
    d_ndxi[1] = 0.25 * (1 - eta) * (2 * xi - eta)
    d_ndxi[2] = 0.25 * (1 + eta) * (2 * xi + eta)
    d_ndxi[3] = 0.25 * (1 + eta) * (2 * xi - eta)
    d_ndxi[4] = -xi * (1 - eta)
    d_ndxi[5] = 0.5 * (1 - eta * eta)
    d_ndxi[6] = -xi * (1 + eta)
    d_ndxi[7] = -0.5 * (1 - eta * eta)
    d_ndeta[0] = 0.25 * (1 - xi) * (2 * eta + xi)
    d_ndeta[1] = 0.25 * (1 + xi) * (2 * eta - xi)
    d_ndeta[2] = 0.25 * (1 + xi) * (2 * eta + xi)
    d_ndeta[3] = 0.25 * (1 - xi) * (2 * eta - xi)
    d_ndeta[4] = -0.5 * (1 - xi * xi)
    d_ndeta[5] = -eta * (1 + xi)
    d_ndeta[6] = 0.5 * (1 - xi * xi)
    d_ndeta[7] = -eta * (1 - xi)
    return n, d_ndxi, d_ndeta


def element_volume_contribution(coords: np.ndarray, disp: np.ndarray, center: np.ndarray) -> float:
    total = 0.0
    for xi, wx in GAUSS_3:
        for eta, we in GAUSS_3:
            n, d_ndxi, d_ndeta = s8_shape_and_deriv(xi, eta)
            dxdxi = d_ndxi @ coords
            dxdeta = d_ndeta @ coords
            normal_vec = np.cross(dxdxi, dxdeta)
            d_a = np.linalg.norm(normal_vec)
            n_hat = normal_vec / d_a
            pos = n @ coords
            r_hat = pos - center
            r_hat = r_hat / np.linalg.norm(r_hat)
            if np.dot(n_hat, r_hat) < 0:
                n_hat = -n_hat
            u = n @ disp
            total += np.dot(u, n_hat) * d_a * wx * we
    return float(total)


def parse_all_disp_blocks_2d(frd_path: Path) -> list[tuple[float, dict[int, tuple[float, float, float]]]]:
    lines = frd_path.read_text().splitlines()
    blocks: list[tuple[float, dict]] = []
    current_time = 0.0
    current_disp: dict[int, tuple[float, float, float]] = {}
    in_disp = False
    for line in lines:
        if line.startswith("  100CL"):
            parts = line.split()
            current_time = float(parts[2])
            continue
        if "DISP" in line and line.strip().startswith("-4"):
            in_disp = True
            current_disp = {}
            continue
        if in_disp:
            if line.startswith(" -1"):
                nid = int(line[3:13])
                rest = line[13:]
                vals = tuple(float(rest[k * 12 : (k + 1) * 12]) for k in range(3))
                current_disp[nid] = vals
            elif line.startswith(" -3"):
                in_disp = False
                blocks.append((current_time, current_disp))
    return blocks


def compute_dV_octant(nodes: dict, elements: list, disp: dict[int, tuple[float, float, float]]) -> float:
    center = np.array([0.0, 0.0, 0.0])
    d_v = 0.0
    for conn in elements:
        coords = np.array([nodes[nid] for nid in conn])
        u = np.array([disp.get(nid, (0.0, 0.0, 0.0)) for nid in conn])
        d_v += element_volume_contribution(coords, u, center)
    return d_v * 8.0


def extract_octant_pv_curve(
    frd_path: Path,
    n_theta: int,
    n_phi: int,
    R: float,
    p_mmhg_final: float,
) -> list[tuple[float, float]]:
    nodes, elements, *_ = build_octant_mesh(n_theta, n_phi, R)
    curve: list[tuple[float, float]] = []
    for frac, disp in parse_all_disp_blocks_2d(frd_path):
        p_mmhg = frac * p_mmhg_final
        d_v = compute_dV_octant(nodes, elements, disp)
        curve.append((d_v, p_mmhg))
    return sorted(curve, key=lambda x: x[0])


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--frd", type=Path, required=True)
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--R", type=float, default=12.0)
    ap.add_argument("--p-mmhg", type=float, default=80.0)
    args = ap.parse_args()
    curve = extract_octant_pv_curve(args.frd, args.n, args.n, args.R, args.p_mmhg)
    for d_v, p in curve:
        print(f"{d_v:12.4f} {p:12.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
