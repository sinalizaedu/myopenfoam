#!/usr/bin/env python3
"""Replace the wall patch in a U field with scleraRobinBC from the template."""
from __future__ import annotations

import re
import sys
from pathlib import Path


def brace_block(text: str, start: int) -> tuple[str, int]:
    i = text.find("{", start)
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[start : j + 1], j + 1
    raise SystemExit("ERROR: unbalanced braces")


def wall_entry(text: str) -> tuple[int, int, str]:
    m = re.search(r"\n    wall\s*\{", text)
    if not m:
        raise SystemExit("ERROR: no wall patch")
    block, end = brace_block(text, m.start() + 1)
    return m.start() + 1, end, block


def main() -> None:
    case = Path(__file__).resolve().parents[1]
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else case / "fluid" / "5" / "U"
    tmpl = case / "fluid" / "initial" / "U.experiment.1h"
    src = tmpl.read_text()
    dst = target.read_text()
    _, _, robin = wall_entry(src)
    a, b, old = wall_entry(dst)
    if "codedFixedValue" in old:
        print(f"apply_robin_wall: {target} already Robin")
        return
    target.write_text(dst[:a] + robin + dst[b:])
    print(f"apply_robin_wall: wrote scleraRobinBC into {target}")


if __name__ == "__main__":
    main()
