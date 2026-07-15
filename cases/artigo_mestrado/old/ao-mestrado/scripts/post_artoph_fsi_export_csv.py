#!/usr/bin/env python3
"""
After a run, copy probe and solid point-displacement outputs into one CSV under
brunaStuff/ for quick plotting (run from repo root).

Reads:
  cases/artoph-fsi-curva-mestrado/fluid/postProcessing/probesNearON/*/p
  cases/artoph-fsi-curva-mestrado/solid/postProcessing/dispNearestON/*/pointDD.dat (if present)
"""
from __future__ import annotations

import csv
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
OUT = (
    CASE / "postProcessing" / "artoph_fsi_nearestON_summary.csv"
    if (Path(__file__).resolve().parent.name == "scripts")
    else Path(__file__).resolve().parents[1] / "brunaStuff" / "artoph_fsi_nearestON_summary.csv"
)


def latest_time_dir(base: Path) -> Path | None:
    if not base.is_dir():
        return None
    times = []
    for c in base.iterdir():
        if c.is_dir() and re.match(r"^[0-9.]+$", c.name):
            times.append(float(c.name))
    if not times:
        return None
    return base / str(max(times))


def main() -> None:
    rows: list[dict[str, str]] = []
    probe_p = latest_time_dir(CASE / "fluid" / "postProcessing" / "probesNearON")
    if probe_p:
        pfile = probe_p / "p"
        if pfile.is_file():
            with pfile.open() as f:
                for line in f:
                    if line.startswith("#") or not line.strip():
                        continue
                    parts = line.split()
                    if len(parts) >= 2:
                        rows.append({"source": "fluid_p_probe", "time": parts[0], "value": parts[1]})

    disp = latest_time_dir(CASE / "solid" / "postProcessing" / "dispNearestON")
    if disp:
        dfile = disp / "pointDD.dat"
        if dfile.is_file():
            with dfile.open() as f:
                for line in f:
                    if line.startswith("#") or not line.strip():
                        continue
                    parts = line.split()
                    if len(parts) >= 4:
                        rows.append(
                            {
                                "source": "solid_pointDD",
                                "time": parts[0],
                                "value": f"({parts[1]} {parts[2]} {parts[3]})",
                            }
                        )

    if not rows:
        print("No postProcessing data found; run the coupled case first.")
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=["source", "time", "value"])
        w.writeheader()
        w.writerows(rows)
    print(f"[ok] wrote {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
