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


def _brace_end(text: str, open_idx: int) -> int:
    depth = 0
    for j in range(open_idx, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return j + 1
    raise SystemExit("ERROR: unbalanced boundaryField brace")


def strip_field(text: str, keep: set[str]) -> str:
    # Brace-balanced so codedFixedValue `#{` / `#}` is not truncated at the first `}`.
    out = text
    for name in field_patches(text):
        if name in keep:
            continue
        m = re.search(rf"\n    {re.escape(name)}\s*\{{", out)
        if not m:
            continue
        end = _brace_end(out, m.end() - 1)
        out = out[: m.start()] + out[end:]
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
