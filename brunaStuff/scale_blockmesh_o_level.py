#!/usr/bin/env python3
"""Scale blockMeshDict.O1 hex divisions to O2/O3 bracket meshes.

O2 = 0.7× O1 divisions (coarser), O3 = 1.3× O1 divisions (finer).
Geometry vertices and grading are unchanged; only (Nx, Ny, Nz) per hex block.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
O1_SRC = REPO / "cases/doc-baseline-o1-volume-fluid/fluid/system/blockMeshDict.O1"

LEVEL_FACTORS = {
    "O2": 0.7,
    "O3": 1.3,
}

OUT_PATHS = {
    "O2": [
        REPO / "cases/doc-baseline-o2-patch-fluid/fluid/system/blockMeshDict.O2",
        REPO / "cases/doc-baseline-o2-volume-fluid/fluid/system/blockMeshDict.O2",
        REPO / "cases/doc-g2-sim1/fluid/system/blockMeshDict.O2",
    ],
    "O3": [
        REPO / "cases/doc-baseline-o3-patch-fluid/fluid/system/blockMeshDict.O3",
        REPO / "cases/doc-baseline-o3-volume-fluid/fluid/system/blockMeshDict.O3",
        REPO / "cases/doc-g2-sim1/fluid/system/blockMeshDict.O3",
    ],
}

HEX_COUNTS = re.compile(
    r"(hex\s+\([^)]+\)\s+(?:\w+\s+)?)\((\d+)\s+(\d+)\s+(\d+)\)"
)


def scale_int(n: int, factor: float) -> int:
    return max(1, int(round(n * factor)))


def scale_text(text: str, factor: float, level: str) -> str:
    def repl(m: re.Match[str]) -> str:
        prefix, nx, ny, nz = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
        sx, sy, sz = scale_int(nx, factor), scale_int(ny, factor), scale_int(nz, factor)
        return f"{prefix}({sx} {sy} {sz})"

    out = HEX_COUNTS.sub(repl, text)
    out = re.sub(
        r"^// Mesh level O[123].*$",
        f"// Mesh level {level} -- G2-fluid domain built natively with blockMesh.",
        out,
        count=1,
        flags=re.M,
    )
    out = re.sub(
        r"^// Scaled from O1 by factor .*$",
        f"// Scaled from O1 by factor {factor:g} (all hex Nx Ny Nz; grading unchanged).",
        out,
        count=1,
        flags=re.M,
    )
    if "// Scaled from O1 by factor" not in out:
        out = out.replace(
            f"// Mesh level {level} -- G2-fluid domain built natively with blockMesh.\n",
            f"// Mesh level {level} -- G2-fluid domain built natively with blockMesh.\n"
            f"// Scaled from O1 by factor {factor:g} (all hex Nx Ny Nz; grading unchanged).\n",
            1,
        )
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--level",
        choices=sorted(LEVEL_FACTORS),
        nargs="+",
        default=sorted(LEVEL_FACTORS),
    )
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src = O1_SRC.read_text()
    for level in args.level:
        factor = LEVEL_FACTORS[level]
        scaled = scale_text(src, factor, level)
        for path in OUT_PATHS[level]:
            if args.dry_run:
                print(f"would write {path} (factor {factor})")
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(scaled)
                print(f"wrote {path} (factor {factor})")


if __name__ == "__main__":
    main()
