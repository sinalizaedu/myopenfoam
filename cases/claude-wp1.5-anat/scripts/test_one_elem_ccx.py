#!/usr/bin/env python3
"""Debug: run CCX on single hex element 1 from converted mesh."""
from pathlib import Path

mesh = Path("../mesh/eye_anatomical.inp").read_text().splitlines()
nodes = {}
mode = None
elem1 = None
for line in mesh:
    s = line.strip()
    if s.startswith("*NODE"):
        mode = "node"
        continue
    if s.startswith("*ELEMENT"):
        mode = "elem"
        continue
    if s.startswith("*") and not s.startswith("**"):
        mode = None
        continue
    if mode == "node" and s:
        p = [x.strip() for x in s.split(",")]
        nodes[int(p[0])] = (float(p[1]), float(p[2]), float(p[3]))
    if mode == "elem" and s:
        p = [int(x.strip()) for x in s.split(",")]
        if p[0] == 1:
            elem1 = p[1:]

out = Path("../output_test/one_elem.inp")
nids = elem1
lines = ["*NODE"]
for i in nids:
    x, y, z = nodes[i]
    lines.append(f"{i:8d}, {x:16.9f}, {y:16.9f}, {z:16.9f}")
lines.append("*ELEMENT, TYPE=C3D8I, ELSET=E1")
lines.append("1, " + ", ".join(str(n) for n in nids))
lines += [
    "*MATERIAL, NAME=M",
    "*ELASTIC",
    "1e6, 0.3",
    "*SOLID SECTION, ELSET=E1, MATERIAL=M",
    "*STEP",
    "*STATIC",
    "1",
    "*END STEP",
]
out.write_text("\n".join(lines) + "\n")
print("Wrote", out, "nodes", nids)
