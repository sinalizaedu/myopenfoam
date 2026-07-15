#!/usr/bin/env python3
"""
After artoph_closest_point_to_nerve.py, sync preCICE watch-point and probe
coordinates in controlDict files from constant/closest_to_ON_ref.json.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

def _cases_root() -> Path:
    p = Path(__file__).resolve()
    if p.parent.name == "scripts":
        return p.parents[2]
    return p.parents[1] / "cases"


CASES = _cases_root()
_CASE_CANDIDATES = ["ao-mestrado", "artoph-fsi-curva-mestrado"]
_CASE_NAME = next((n for n in _CASE_CANDIDATES if (CASES / n).is_dir()),
                  _CASE_CANDIDATES[0])
CASE = CASES / _CASE_NAME
JSON_PATH = CASE / "constant" / "closest_to_ON_ref.json"
PRECICE = CASE / "precice-config.xml"
FLUID_CTRL = CASE / "fluid" / "system" / "controlDict"
SOLID_CTRL = CASE / "solid" / "system" / "controlDict"


def main() -> None:
    if not JSON_PATH.is_file():
        print(f"[skip] no {JSON_PATH}")
        return
    data = json.loads(JSON_PATH.read_text())
    coord = data["precice_watchpoint_coordinate"]
    p = data["closest_point_m"]
    px, py, pz = p[0], p[1], p[2]

    if PRECICE.is_file():
        txt = PRECICE.read_text()
        txt2 = re.sub(
            r'(<watch-point[^>]*coordinate=")[^"]+(")',
            rf"\g<1>{coord}\2",
            txt,
            count=1,
        )
        if txt2 != txt:
            PRECICE.write_text(txt2)
            print(f"[ok] updated watch-point in {PRECICE.relative_to(CASES)}")

    probe_block = f"""        probeLocations
        (
            ({px} {py} {pz})
        );"""

    if FLUID_CTRL.is_file():
        t = FLUID_CTRL.read_text()
        t2 = re.sub(
            r"probeLocations\s*\([^;]*\);",
            probe_block,
            t,
            count=1,
            flags=re.DOTALL,
        )
        if t2 != t:
            FLUID_CTRL.write_text(t2)
            print(f"[ok] probes in {FLUID_CTRL.relative_to(CASES)}")

    if SOLID_CTRL.is_file():
        t = SOLID_CTRL.read_text()
        t2 = re.sub(
            r"(point\s+)(\([^)]+\))(;)",
            rf"\g<1>({px} {py} {pz})\3",
            t,
            count=1,
        )
        # solidPointDisplacement point line - may need second replace for dispNearestON
        t2 = re.sub(
            r"(dispNearestON[\s\S]*?point\s+)(\([^)]+\))(;)",
            rf"\g<1>({px} {py} {pz})\3",
            t2,
            count=1,
        )
        if t2 != t:
            SOLID_CTRL.write_text(t2)
            print(f"[ok] solidPointDisplacement in {SOLID_CTRL.relative_to(CASES)}")


if __name__ == "__main__":
    main()
