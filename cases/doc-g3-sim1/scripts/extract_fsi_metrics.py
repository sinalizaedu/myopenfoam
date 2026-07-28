#!/usr/bin/env python3
"""Extract fluid + FSI metrics for doc-g3-sim1 mesh / coupling studies."""

from __future__ import annotations

import math
import os
import pathlib
import re
import sys

RHO = 995.0
PA_TO_MMHG = 0.0075006
N_THETA = {"M1": 6, "M2": 10, "M3": 16}


def pkin_to_mmhg(p: float) -> float:
    return p * RHO * PA_TO_MMHG


def read_ncells(log_check: pathlib.Path) -> int | None:
    if not log_check.exists():
        return None
    for line in log_check.read_text().splitlines():
        if "nCells:" in line:
            return int(line.split()[-1])
        m = re.search(r"^\s*cells:\s+(\d+)", line)
        if m:
            return int(m.group(1))
    return None


def read_patch_nfaces(boundary: pathlib.Path, name: str) -> int | None:
    if not boundary.exists():
        return None
    text = boundary.read_text()
    m = re.search(rf"\b{name}\b[\s\S]*?nFaces\s+(\d+)", text)
    return int(m.group(1)) if m else None


def read_iop_probes(fluid: pathlib.Path) -> tuple[float, float] | None:
    path = fluid / "postProcessing" / "iop_probe" / "0" / "p"
    if not path.exists():
        return None
    vals: list[float] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        parts = line.split()
        if len(parts) >= 5:
            vals = [float(x) for x in parts[1:5]]
    if len(vals) < 4:
        return None
    ac = 0.5 * (pkin_to_mmhg(vals[0]) + pkin_to_mmhg(vals[1]))
    vit = 0.5 * (pkin_to_mmhg(vals[2]) + pkin_to_mmhg(vals[3]))
    return ac, vit


def read_q_tm(fluid: pathlib.Path) -> float | None:
    for log_name in ("log.simpleFoam", "log.simpleFoam.prewarm", "log.pimpleFoam"):
        log = fluid / log_name
        if not log.exists():
            continue
        for line in reversed(log.read_text().splitlines()):
            if "sum(outlet_tm) of phi" in line:
                return float(line.split("=")[-1].strip())
    return None


def read_mapping_max(case: pathlib.Path) -> float | None:
    for log in (case / "solid" / "log.solids4Foam", case / "fluid" / "log.pimpleFoam"):
        if not log.exists():
            continue
        for line in log.read_text().splitlines():
            if "Mapping distance" in line and "max:" in line:
                m = re.search(r"max:([0-9.eE+-]+)", line)
                if m:
                    return float(m.group(1))
    return None


def read_vector_field_max(path: pathlib.Path) -> float | None:
    if not path.exists():
        return None
    text = path.read_text()
    if "internalField" in text and "nonuniform List" in text:
        block = text.split("internalField", 1)[1]
        nums = re.findall(r"\(([-0-9.eE+]+)\s+([-0-9.eE+]+)\s+([-0-9.eE+]+)\)", block)
        if not nums:
            return None
        return max(math.hypot(float(a), math.hypot(float(b), float(c))) for a, b, c in nums)
    m = re.search(r"internalField\s+uniform\s+\(([-0-9.eE+]+)\s+([-0-9.eE+]+)\s+([-0-9.eE+]+)\)", text)
    if m:
        x, y, z = (float(m.group(i)) for i in (1, 2, 3))
        return math.hypot(x, math.hypot(y, z))
    return None


def latest_time_dir(domain: pathlib.Path) -> pathlib.Path | None:
    best: float | None = None
    best_path: pathlib.Path | None = None
    for p in domain.iterdir():
        if not p.is_dir():
            continue
        try:
            t = float(p.name)
        except ValueError:
            continue
        if best is None or t > best:
            best, best_path = t, p
    return best_path


def main() -> None:
    case = pathlib.Path(__file__).resolve().parent.parent
    fluid = case / "fluid"
    solid = case / "solid"
    level = case.name  # unused; caller may set MESH_LEVEL in env

    mesh_level = os.environ.get("MESH_LEVEL", "M1")
    n_fluid = read_ncells(fluid / "log.checkMesh")
    n_solid = read_ncells(solid / "log.checkMesh")
    iop = read_iop_probes(fluid)
    q_tm = read_q_tm(fluid)
    map_max = read_mapping_max(case)

    tdir = latest_time_dir(solid)
    d_max = read_vector_field_max(tdir / "D") if tdir else None
    d_max_um = d_max * 1e6 if d_max is not None else None

    wall_n = read_patch_nfaces(fluid / "constant" / "polyMesh" / "boundary", "wall")
    fsi_solid_n = read_patch_nfaces(solid / "constant" / "polyMesh" / "boundary", "fsi_active")

    fsi_ok = not (solid / "log.solids4Foam").exists() or "FOAM FATAL" not in (
        solid / "log.solids4Foam"
    ).read_text()
    if (solid / "log.solids4Foam").exists():
        fsi_ok = "FOAM FATAL" not in (solid / "log.solids4Foam").read_text() and (
            "The coupling completed" in (fluid / "log.pimpleFoam").read_text()
            if (fluid / "log.pimpleFoam").exists()
            else True
        )

    print(f"mesh_level={mesh_level}")
    print(f"n_theta={N_THETA.get(mesh_level, '?')}")
    print(f"nCells_fluid={n_fluid}")
    print(f"nCells_solid={n_solid}")
    print(f"wall_faces={wall_n}")
    print(f"fsi_active_faces_solid={fsi_solid_n}")
    if iop:
        print(f"IOP_AC={iop[0]:.3f} mmHg")
        print(f"IOP_vitreous={iop[1]:.3f} mmHg")
    else:
        print("IOP_AC=N/A")
    print(f"Q_TM={q_tm:.4e}" if q_tm else "Q_TM=N/A")
    print(f"mapping_max_m={map_max:.6e}" if map_max is not None else "mapping_max_m=N/A")
    print(f"D_max_um={d_max_um:.4f}" if d_max_um is not None else "D_max_um=N/A")
    print(f"fsi_coupling_ok={fsi_ok}")


if __name__ == "__main__":
    main()
