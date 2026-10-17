#!/usr/bin/env python3
"""RMS of radial displacement vs u_r = P R^2 (1-nu) / (2 t E) on octant meshes (wp1.tex)."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WP1 = HERE.parent
sys.path.insert(0, str(HERE))
for _c in (
    Path("/opt/brunaStuff/artigo_mestrado"),
    WP1.parents[1] / "brunaStuff" / "artigo_mestrado",
):
    if (_c / "frd_stress.py").is_file():
        sys.path.insert(0, str(_c))
        break

from extract_K import _load_mesh_and_disp, parse_nodes, radial_stats  # noqa: E402

MMHG_TO_MPA = 133.322e-6
CASES = {
    "human": {"R_mm": 12.0, "t_mm": 0.5, "E_MPa": 3.0, "nu": 0.47, "dP_mmHg": 1.0},
    "rabbit": {"R_mm": 7.6, "t_mm": 0.33, "E_MPa": 3.0, "nu": 0.47, "dP_mmHg": 1.0},
}
NE_LEVELS = (3, 6, 12)
THETA_MIN_RAD = math.radians(3.0)


def ur_analytic_mm(case: dict) -> float:
    r = case["R_mm"]
    t = case["t_mm"]
    e = case["E_MPa"]
    nu = case["nu"]
    p_mpa = case["dP_mmHg"] * MMHG_TO_MPA
    return p_mpa * r**2 * (1.0 - nu) / (2.0 * t * e)


def calota_ring_node_ids(mesh_inp: Path) -> set[int]:
    nodes = parse_nodes(mesh_inp)
    ring: set[int] = set()
    for nid, xyz in nodes.items():
        r = float(np.linalg.norm(xyz))
        if r < 1e-9:
            continue
        cos_theta = xyz[2] / r
        if abs(cos_theta - math.cos(THETA_MIN_RAD)) < 2e-3:
            ring.add(nid)
    return ring


def rms_pct(case: str, ne: int, *, exclude_calota: bool) -> dict:
    spec = CASES[case]
    deck = WP1 / "ccx" / f"{case}_oct_ne{ne}.inp"
    frd = deck.with_suffix(".frd")
    mesh = WP1 / "ccx" / f"{case}_oct_ne{ne}_mesh.inp"
    if not frd.is_file():
        return {"ok": False, "reason": f"missing {frd}"}
    mesh_inp = WP1 / "ccx" / f"{case}_oct_ne{ne}_mesh.inp"
    nodes, _elems, disp = _load_mesh_and_disp(mesh_inp, frd, spec["t_mm"])
    exclude = calota_ring_node_ids(mesh) if exclude_calota else set()
    stats = radial_stats(nodes, disp, exclude=exclude or None)
    ur_ref = ur_analytic_mm(spec)
    urs = []
    for nid, xyz in nodes.items():
        if exclude and nid in exclude:
            continue
        du = np.asarray(disp.get(nid, (0.0, 0.0, 0.0)))
        rhat = xyz / np.linalg.norm(xyz)
        urs.append(float(np.dot(du, rhat)))
    arr = np.array(urs)
    rms = float(np.sqrt(np.mean((arr - ur_ref) ** 2)))
    rms_pct = 100.0 * rms / ur_ref if ur_ref > 0 else float("nan")
    return {
        "case": case,
        "ne": ne,
        "full_sphere_equiv_elements": ne * ne * 8,
        "exclude_calota_ring": exclude_calota,
        "u_r_analytic_mm": ur_ref,
        "u_r_mean_mm": stats.get("u_r_mean_mm"),
        "rms_mm": rms,
        "rms_pct": rms_pct,
        "n_nodes": len(arr),
    }


def main() -> int:
    rows: list[dict] = []
    for case in CASES:
        for ne in NE_LEVELS:
            for ex in (False, True):
                rows.append(rms_pct(case, ne, exclude_calota=ex))
    out = WP1 / "output_octant" / "ur_rms_vs_analytic.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2))
    print(json.dumps(rows, indent=2))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
