#!/usr/bin/env python3
"""Set d_TM in tm_porous zones only (not vitreous). Usage: set_d_tm.py 3.55e14"""

import re
import sys
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("Usage: set_d_tm.py <d_TM>", file=sys.stderr)
        sys.exit(1)
    d_tm = sys.argv[1]
    path = Path(__file__).resolve().parent.parent / "fluid" / "system" / "fvOptions"
    text = path.read_text()
    blocks = text.split("vitreous_porous")
    if len(blocks) != 2:
        print("ERROR: expected tm + vitreous blocks", file=sys.stderr)
        sys.exit(1)
    tm_part = blocks[0]
    vit_part = "vitreous_porous" + blocks[1]
    tm_new, n = re.subn(
        r"d\s+d\s+\[0 -2 0 0 0 0 0\]\s+\([^)]+\)",
        f"d   d [0 -2 0 0 0 0 0] ({d_tm} {d_tm} {d_tm})",
        tm_part,
    )
    path.write_text(tm_new + vit_part)
    print(f"Set d_TM = {d_tm} in TM zones ({n} replacements)")

if __name__ == "__main__":
    main()
