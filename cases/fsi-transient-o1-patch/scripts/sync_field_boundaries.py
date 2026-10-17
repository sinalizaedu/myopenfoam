#!/usr/bin/env python3
"""Sync fluid/0/{U,p} boundaryField with constant/polyMesh/boundary.

Only strips entries for patches removed from the mesh. Never writes to fluid/initial/.
If a mesh patch is missing from the field, exit with an error (do not inject defaults).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def mesh_patches(fluid: Path) -> set[str]:
    text = (fluid / "constant/polyMesh/boundary").read_text()
    return set(re.findall(r"^\s{4}(\w+)\s*$", text, re.M))


def field_patches(text: str) -> set[str]:
    return set(re.findall(r"^\s{4}(\w+)\s*\{", text, re.M))


def strip_field(text: str, keep: set[str]) -> str:
    out = text
    for name in field_patches(text):
        if name in keep:
            continue
        out = re.sub(
            rf"\n    {re.escape(name)} \{{[^}}]*\}}",
            "",
            out,
            count=1,
            flags=re.S,
        )
    return out


def sync_one(path: Path, keep: set[str]) -> bool:
    if path.name not in ("U", "p"):
        return False
    text = path.read_text()
    out = strip_field(text, keep)
    missing = sorted(keep - field_patches(out))
    if missing:
        print(
            f"ERROR: {path} missing boundaryField for mesh patches: {missing}",
            file=sys.stderr,
        )
        sys.exit(1)
    if out != text:
        path.write_text(out)
        return True
    return False


def main() -> int:
    fluid = Path(sys.argv[1] if len(sys.argv) > 1 else "fluid")
    keep = mesh_patches(fluid)
    changed = []
    for name in ("U", "p"):
        path = fluid / "0" / name
        if path.is_file() and sync_one(path, keep):
            changed.append(path)
            print(f"sync_field_boundaries: updated {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
