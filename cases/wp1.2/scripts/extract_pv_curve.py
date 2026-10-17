#!/usr/bin/env python3
"""Extract P(V) from a multi-step wp1.2 hyperelastic CalculiX run.

V is relative to the state at P0 = 15 mmHg (Ensaio A reference).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WP1_SCRIPTS = HERE.parents[1] / "wp1.1" / "scripts"
sys.path.insert(0, str(WP1_SCRIPTS))
sys.path.insert(0, str(HERE))

from extract_K import cavity_dV_mm3, parse_elements, parse_nodes, parse_surfaces  # noqa: E402
from extract_K import _map_frd_disp_to_mesh, _mesh_meta  # noqa: E402

from ccx_utils import MMHG_TO_MPA  # noqa: E402

P0_MMHG = 15.0


def _mesh_volume_scale(mesh_inp: Path) -> float:
    meta = mesh_inp.with_suffix(".meta.json")
    if meta.is_file():
        return float(json.loads(meta.read_text()).get("volume_scale", 1.0))
    for line in mesh_inp.read_text().splitlines():
        if "volume_scale=" in line:
            return float(line.split("volume_scale=")[1].split()[0])
    return 1.0


def _parse_step_pressures(deck: Path) -> list[float]:
    meta = deck.with_suffix(".meta.json")
    if meta.is_file():
        data = json.loads(meta.read_text())
        return [float(s["p_mmhg"]) for s in data["steps"]]
    # fallback: read DSLOAD pressures in order
    ps = []
    for line in deck.read_text().splitlines():
        if ", P," in line.upper() and not line.strip().startswith("**"):
            ps.append(float(line.split(",")[-1].strip()) / MMHG_TO_MPA)
    return ps


def _end_of_step_indices(lams: list[float]) -> list[int]:
    """Return FRD step indices at the end of each CalculiX *STEP (lambda reset)."""
    if not lams:
        return []
    ends = [0]
    for i in range(1, len(lams)):
        if lams[i] + 1e-6 < lams[i - 1]:
            ends.append(i - 1)
            ends.append(i)
    ends.append(len(lams) - 1)
    # unique, sorted, keep last index per contiguous block
    uniq: list[int] = []
    for idx in ends:
        if not uniq or idx != uniq[-1]:
            uniq.append(idx)
    # collapse: for each reset segment keep only the final index
    blocks: list[list[int]] = []
    start = 0
    for i in range(1, len(lams)):
        if lams[i] + 1e-6 < lams[i - 1]:
            blocks.append(list(range(start, i)))
            start = i
    blocks.append(list(range(start, len(lams))))
    return [b[-1] for b in blocks if b]


def _indices_for_pseudo_times(lams: list[float], pseudo_times: list[float]) -> list[int]:
    """Map target pseudo-times (0..1) to closest FRD block in a single NLGEOM step."""
    if not lams:
        return []
    indices: list[int] = []
    for t in pseudo_times:
        idx = min(range(len(lams)), key=lambda j: abs(lams[j] - t))
        indices.append(idx)
    # enforce monotonic sampling for interpolation downstream
    for i in range(1, len(indices)):
        indices[i] = max(indices[i], indices[i - 1])
    return indices


def _mulf_step_blocks(lams: list[float]) -> tuple[int, list[list[int]]]:
    """Return (prestress_block_idx, list of index ranges per CalculiX *STEP)."""
    if not lams:
        return 0, []
    blocks: list[list[int]] = []
    start = 0
    for i in range(1, len(lams)):
        if lams[i] + 1e-6 < lams[i - 1]:
            blocks.append(list(range(start, i)))
            start = i
    blocks.append(list(range(start, len(lams))))
    return 0, blocks


def _sta_step_frames(sta_path: Path) -> tuple[int, list[int]]:
    """Map .sta increments to FRD frame indices; return (prestress_end_idx, step2_indices)."""
    if not sta_path.is_file():
        raise ValueError(f"Missing .sta file: {sta_path}")
    step1_times: list[float] = []
    step2_times: list[float] = []
    for line in sta_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("SUMMARY") or line.startswith("STEP"):
            continue
        parts = line.split()
        if len(parts) < 6:
            continue
        step_no = int(parts[0])
        step_time = float(parts[5])
        if step_no == 1:
            step1_times.append(step_time)
        elif step_no == 2:
            step2_times.append(step_time)
    if not step1_times or not step2_times:
        raise ValueError(f"Could not parse step 1/2 increments from {sta_path}")
    prestress_end = len(step1_times) - 1
    step2_start = len(step1_times)
    step2_indices = list(range(step2_start, step2_start + len(step2_times)))
    return prestress_end, step2_indices, step2_times


def extract_pv_mulf(
    inp: Path,
    frd: Path,
    R_mm: float,
    p0_mmhg: float | None = None,
) -> list[dict]:
    """Extract P(V) from step 2 only, with V=0 at end of prestress step (MULF)."""
    meta_path = inp.with_suffix(".meta.json")
    if not meta_path.is_file():
        raise ValueError(f"Missing MULF meta: {meta_path}")
    meta = json.loads(meta_path.read_text())
    if not meta.get("mulf"):
        raise ValueError("Deck meta is not MULF; use extract_pv() instead")

    mesh_inp = inp
    text = inp.read_text()
    if "*INCLUDE" in text.upper():
        import re

        m = re.search(r"INPUT\s*=\s*(\S+)", text, re.I)
        if m:
            mesh_inp = (inp.parent / m.group(1).strip()).resolve()

    nodes = parse_nodes(mesh_inp)
    elems = parse_elements(mesh_inp)
    pairs = parse_surfaces(mesh_inp).get("INNER_SURF", [])
    if not pairs:
        raise ValueError("INNER_SURF not found")

    for _cand in (
        Path("/opt/brunaStuff/artigo_mestrado"),
        WP1_SCRIPTS.parents[2] / "brunaStuff" / "artigo_mestrado",
    ):
        if (_cand / "frd_stress.py").is_file():
            sys.path.insert(0, str(_cand))
            break
    from frd_stress import parse_frd  # noqa: E402

    frd_nodes, _, steps = parse_frd(frd)
    lams = [float(stp["lam"] if stp["lam"] is not None else 0.0) for stp in steps]
    _, blocks = _mulf_step_blocks(lams)

    step2_pressures = [float(p) for p in meta["step2_pressures_mmhg"]]
    pseudo = [i / max(1, len(step2_pressures) - 1) for i in range(len(step2_pressures))]

    sta_path = frd.with_suffix(".sta")
    if len(blocks) >= 2:
        load_block = blocks[1]
        load_lams = [lams[i] for i in load_block]
        end_rel = _indices_for_pseudo_times(load_lams, pseudo)
        end_idx = [load_block[i] for i in end_rel]
        prestress_idx = blocks[0][-1]
    else:
        prestress_idx, step2_block, step2_times = _sta_step_frames(sta_path)
        if len(steps) < prestress_idx + len(step2_block):
            raise ValueError(
                f"FRD has {len(steps)} frames but .sta expects "
                f"{prestress_idx + 1 + len(step2_block)}"
            )
        end_rel = _indices_for_pseudo_times(step2_times, pseudo)
        end_idx = [step2_block[i] for i in end_rel]

    mesh_meta = _mesh_meta(mesh_inp)
    t_mm = float(mesh_meta.get("t_mm", 0.5))
    gauss_order = 3 if mesh_meta.get("mesh_kind") == "spherical" else 2
    volume_scale = _mesh_volume_scale(mesh_inp)
    p0 = float(p0_mmhg if p0_mmhg is not None else meta.get("P0_mmHg", P0_MMHG))

    stp0 = steps[prestress_idx]
    disp0 = _map_frd_disp_to_mesh(nodes, frd_nodes, stp0["disp"], t_mm)
    dV0 = cavity_dV_mm3(pairs, elems, nodes, disp0, gauss_order=gauss_order) * volume_scale
    v_ref_uL = float(dV0)

    rows: list[dict] = []
    for j, i in enumerate(end_idx):
        stp = steps[i]
        disp = _map_frd_disp_to_mesh(nodes, frd_nodes, stp["disp"], t_mm)
        dV_mm3 = cavity_dV_mm3(pairs, elems, nodes, disp, gauss_order=gauss_order) * volume_scale
        v_uL = float(dV_mm3)
        p_mmhg = float(step2_pressures[min(j, len(step2_pressures) - 1)])
        rows.append(
            {
                "i": i,
                "p_mmhg": p_mmhg,
                "v_abs_uL": v_uL,
                "dV_uL": v_uL - v_ref_uL,
                "mulf_step": 2,
            }
        )

    return rows


def extract_pv(
    inp: Path,
    frd: Path,
    R_mm: float,
    p0_mmhg: float | None = None,
) -> list[dict]:
    mesh_inp = inp
    text = inp.read_text()
    if "*INCLUDE" in text.upper():
        import re

        m = re.search(r"INPUT\s*=\s*(\S+)", text, re.I)
        if m:
            mesh_inp = (inp.parent / m.group(1).strip()).resolve()

    nodes = parse_nodes(mesh_inp)
    elems = parse_elements(mesh_inp)
    pairs = parse_surfaces(mesh_inp).get("INNER_SURF", [])
    if not pairs:
        raise ValueError("INNER_SURF not found")

    for _cand in (
        Path("/opt/brunaStuff/artigo_mestrado"),
        WP1_SCRIPTS.parents[2] / "brunaStuff" / "artigo_mestrado",
    ):
        if (_cand / "frd_stress.py").is_file():
            sys.path.insert(0, str(_cand))
            break
    from frd_stress import parse_frd  # noqa: E402

    frd_nodes, _, steps = parse_frd(frd)
    step_pressures = _parse_step_pressures(inp)
    lams = [float(stp["lam"] if stp["lam"] is not None else 0.0) for stp in steps]
    meta = json.loads(inp.with_suffix(".meta.json").read_text()) if inp.with_suffix(".meta.json").is_file() else {}
    if meta.get("mulf"):
        return extract_pv_mulf(inp, frd, R_mm, p0_mmhg=p0_mmhg)
    if meta.get("single_step"):
        pseudo = [float(s.get("pseudo_time", 0.0)) for s in meta.get("steps", [])]
        if len(pseudo) == len(step_pressures):
            end_idx = _indices_for_pseudo_times(lams, pseudo)
        else:
            end_idx = _indices_for_pseudo_times(
                lams,
                [i / (len(step_pressures) - 1) for i in range(len(step_pressures))],
            )
    else:
        end_idx = _end_of_step_indices(lams)
    if len(end_idx) != len(step_pressures):
        # fallback: evenly subsample if reset detection fails
        if len(step_pressures) > 0 and len(steps) >= len(step_pressures):
            end_idx = [
                int(round((k + 1) * len(steps) / len(step_pressures)) - 1)
                for k in range(len(step_pressures))
            ]
            end_idx[-1] = len(steps) - 1
        else:
            end_idx = list(range(len(steps)))

    mesh_meta = _mesh_meta(mesh_inp)
    t_mm = float(mesh_meta.get("t_mm", 0.5))
    gauss_order = 3 if mesh_meta.get("mesh_kind") == "spherical" else 2
    volume_scale = _mesh_volume_scale(mesh_inp)
    p0 = float(p0_mmhg if p0_mmhg is not None else meta.get("P0_mmHg", P0_MMHG))
    rows: list[dict] = []
    v_ref_uL: float | None = None

    for j, i in enumerate(end_idx):
        stp = steps[i]
        disp_raw = stp["disp"]
        disp = _map_frd_disp_to_mesh(nodes, frd_nodes, disp_raw, t_mm)
        dV_mm3 = cavity_dV_mm3(pairs, elems, nodes, disp, gauss_order=gauss_order)
        dV_mm3 *= volume_scale
        v_uL = float(dV_mm3)  # 1 mm³ = 1 µL
        p_mmhg = float(step_pressures[min(j, len(step_pressures) - 1)])
        if v_ref_uL is None and abs(p_mmhg - p0) < 0.5:
            v_ref_uL = v_uL
        rows.append({"i": i, "p_mmhg": p_mmhg, "v_abs_uL": v_uL})

    if v_ref_uL is None:
        v_ref_uL = rows[0]["v_abs_uL"]

    for r in rows:
        r["dV_uL"] = r["v_abs_uL"] - v_ref_uL

    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inp", required=True, type=Path)
    ap.add_argument("--frd", required=True, type=Path)
    ap.add_argument("--R", type=float, required=True)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    rows = extract_pv(args.inp, args.frd, args.R)
    txt = json.dumps(rows, indent=2)
    print(txt)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(txt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
