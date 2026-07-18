#!/usr/bin/env python3
"""Set defaultFaces to empty after refineMesh (patch type becomes empty)."""

from pathlib import Path
import re
import sys

CASE = Path(__file__).resolve().parent.parent / "fluid" / "0"

PATCH = "defaultFaces"
REPL = {
    "p": "empty",
    "U": "empty",
}


def fix_field(path: Path, bc_type: str) -> None:
    text = path.read_text()
    pattern = (
        rf"({PATCH}\s*\{{\s*type\s+)[^;]+(;)"
    )
    new, n = re.subn(pattern, rf"\g<1>{bc_type}\2", text, count=1)
    if n != 1:
        print(f"WARN: {path.name}: defaultFaces block not updated ({n})", file=sys.stderr)
        return
    path.write_text(new)
    print(f"Fixed {path.name}: {PATCH} -> {bc_type}")


def main():
    for name, bc in REPL.items():
        p = CASE / name
        if p.exists():
            fix_field(p, bc)


if __name__ == "__main__":
    main()
