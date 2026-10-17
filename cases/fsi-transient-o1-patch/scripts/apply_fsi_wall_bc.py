#!/usr/bin/env python3
"""Patch fluid/0/U: wall noSlip → movingWallVelocity for two-way ALE FSI."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "fluid/0/U")
    text = path.read_text()
    patched, n = re.subn(
        r"(?m)^(\s*)wall\s*\{\s*type\s+noSlip;\s*\}",
        r"\1wall\n\1{\n\1    type            movingWallVelocity;\n"
        r"\1    value           uniform (0 0 0);\n\1}",
        text,
        count=1,
    )
    if n != 1:
        if "movingWallVelocity" in text and "wall" in text:
            print(f"{path}: wall already movingWallVelocity")
            return 0
        print(f"ERROR: could not patch wall BC in {path}", file=sys.stderr)
        return 1
    path.write_text(patched)
    print(f"{path}: wall → movingWallVelocity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
