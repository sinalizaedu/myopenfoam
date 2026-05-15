#!/usr/bin/env python3
"""
Verify eye-fsi-tc0: every preCICE patch exists on its mesh; every solid preCICE patch uses solidForce.

Usage:
  python3 brunaStuff/audit_eye_fsi_tc0.py [path/to/cases/eye-fsi-tc0]
Default case dir: repo_root/cases/eye-fsi-tc0 (script lives in brunaStuff/).
Exit 0 if OK, 1 if mismatches.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def boundary_patch_names(poly_mesh_boundary: Path) -> set[str]:
    text = poly_mesh_boundary.read_text()
    # Lines like "    patchName" immediately before "{"
    names: set[str] = set()
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^    ([a-zA-Z][a-zA-Z0-9_]*)$", line)
        if m and i + 1 < len(lines) and lines[i + 1].strip() == "{":
            names.add(m.group(1))
    return names


def patch_type_in_boundary(boundary_text: str, patch_name: str) -> str | None:
    anchor = f"    {patch_name}\n"
    idx = boundary_text.find(anchor)
    if idx < 0:
        return None
    start = boundary_text.find("{", idx)
    if start < 0:
        return None
    depth = 0
    for j in range(start, len(boundary_text)):
        c = boundary_text[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                block = boundary_text[start : j + 1]
                m = re.search(r"type\s+(\w+)\s*;", block)
                return m.group(1) if m else None
    return None


def precice_interface_patches(precice_dict: Path) -> list[str]:
    text = precice_dict.read_text()
    m = re.search(r"patches\s*\(\s*(.*?)\s*\)\s*;", text, re.DOTALL)
    if not m:
        raise ValueError(f"No patches block in {precice_dict}")
    return [p for p in m.group(1).split() if p]


def patch_bc_type_in_d(d_path: Path, patch: str) -> str | None:
    text = d_path.read_text()
    anchor = f"    {patch}\n"
    idx = text.find(anchor)
    if idx < 0:
        return None
    chunk = text[idx : idx + 1200]
    for line in chunk.split("\n"):
        s = line.strip()
        if s.startswith("type"):
            parts = s.split()
            if len(parts) >= 2:
                return parts[1].rstrip(";")
    return None


def main() -> int:
    root = repo_root()
    case = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else root / "cases/eye-fsi-tc0"
    fluid_b = case / "fluid" / "constant" / "polyMesh" / "boundary"
    solid_b = case / "solid" / "constant" / "polyMesh" / "boundary"
    fluid_pd = case / "fluid" / "system" / "preciceDict"
    solid_pd = case / "solid" / "system" / "preciceDict"
    solid_d = case / "solid" / "0" / "D"

    missing = []
    for label, p in (
        ("fluid boundary", fluid_b),
        ("solid boundary", solid_b),
        ("fluid preciceDict", fluid_pd),
        ("solid preciceDict", solid_pd),
        ("solid 0/D", solid_d),
    ):
        if not p.is_file():
            missing.append(f"{label}: {p}")

    if missing:
        print("FAIL — missing files (run blockMesh / from repo root?):")
        for m in missing:
            print(" ", m)
        return 1

    fluid_names = boundary_patch_names(fluid_b)
    solid_names = boundary_patch_names(solid_b)
    fluid_iface = precice_interface_patches(fluid_pd)
    solid_iface = precice_interface_patches(solid_pd)

    errors: list[str] = []

    for p in fluid_iface:
        if p not in fluid_names:
            errors.append(f'Fluid preCICE patch "{p}" not in fluid polyMesh/boundary')

    for p in solid_iface:
        if p not in solid_names:
            errors.append(f'Solid preCICE patch "{p}" not in solid polyMesh/boundary')

    for p in solid_iface:
        bt = patch_bc_type_in_d(solid_d, p)
        if bt != "solidForce":
            errors.append(
                f'Solid preCICE patch "{p}" must use type solidForce in solid/0/D (found {bt!r})'
            )

    text_fb = fluid_b.read_text()
    fluid_wall_patches: set[str] = set()
    for name in fluid_names:
        if patch_type_in_boundary(text_fb, name) == "wall":
            fluid_wall_patches.add(name)

    allowed_wall_skip_precice = {"lens_right", "lens_left"}
    for w in sorted(fluid_wall_patches):
        if w in fluid_iface:
            continue
        if w in allowed_wall_skip_precice:
            continue
        errors.append(
            f'Fluid wall patch "{w}" is not in fluid preCICE interfaces '
            f"(and not in allowed skip {allowed_wall_skip_precice})"
        )

    if errors:
        print("FAIL — eye-fsi-tc0 interface audit:")
        for e in errors:
            print(" ", e)
        return 1

    print("OK — eye-fsi-tc0 interface audit:")
    print(f"  fluid boundary patches : {len(fluid_names)}")
    print(f"  solid boundary patches : {len(solid_names)}")
    print(f"  fluid preCICE patches  : {len(fluid_iface)}")
    print(f"  solid preCICE patches  : {len(solid_iface)} (all solidForce)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
