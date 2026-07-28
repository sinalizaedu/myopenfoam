#!/usr/bin/env python3
"""Seed fluid/0 from steady simpleFoam baseline with experiment BCs.

Preserves baseline face `value` data when swapping BC types.
IOP is set by d_TM in fvOptions (TM porous resistance), not by shifting p.
outlet_tm fixedValue stays at P_TM = 10 Torr.
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path


def latest_time(fluid: Path) -> Path:
    ints: list[tuple[float, Path]] = []
    fracs: list[tuple[float, Path]] = []
    for p in fluid.iterdir():
        if not p.is_dir():
            continue
        try:
            t = float(p.name)
        except ValueError:
            continue
        if t <= 0:
            continue
        if p.name.isdigit():
            ints.append((t, p))
        else:
            fracs.append((t, p))
    if ints:
        return max(ints, key=lambda x: x[0])[1]
    if fracs:
        return max(fracs, key=lambda x: x[0])[1]
    raise SystemExit("ERROR: no positive time directories under fluid/")


def extract_brace_block(text: str, start: int) -> tuple[str, int]:
    i = text.find("{", start)
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[start : j + 1], j + 1
    raise SystemExit("ERROR: unbalanced brace block")


def parse_patches(boundary_field_block: str) -> dict[str, str]:
    m = re.match(r"boundaryField\s*\{(.*)\}\s*$", boundary_field_block, re.S)
    body = m.group(1) if m else boundary_field_block
    patches: dict[str, str] = {}
    pos = 0
    while True:
        mm = re.search(r"([A-Za-z_][\w]*)\s*\{", body[pos:])
        if not mm:
            break
        abs_start = pos + mm.start()
        entry, end = extract_brace_block(body, abs_start)
        patches[mm.group(1)] = entry
        pos = end
    return patches


def patch_value_entry(patch_block: str) -> str | None:
    m = re.search(
        r"(value\s+nonuniform\s+List<[^>]+>\s*\n\d+\s*\n\(.*?\)\s*;)",
        patch_block,
        re.S,
    )
    if m:
        return m.group(1)
    m = re.search(r"(value\s+uniform\s+[^;]+;)", patch_block)
    return m.group(1) if m else None


def merge_boundary(field_text: str, bc_template: str) -> str:
    m_src = re.search(r"boundaryField\s*\{", bc_template)
    m_dst = re.search(r"boundaryField\s*\{", field_text)
    if not m_src or not m_dst:
        raise SystemExit("ERROR: missing boundaryField")

    src_block, _ = extract_brace_block(bc_template, m_src.start())
    dst_block, dst_end = extract_brace_block(field_text, m_dst.start())
    tmpl_patches = parse_patches(src_block)
    base_patches = parse_patches(dst_block)

    merged_entries: list[str] = []
    for name, tmpl_entry in tmpl_patches.items():
        entry = tmpl_entry
        if name in base_patches:
            base_val = patch_value_entry(base_patches[name])
            if base_val:
                if re.search(r"value\s+", entry):
                    entry = re.sub(
                        r"value\s+nonuniform\s+List<[^>]+>\s*\n\d+\s*\n\(.*?\)\s*;"
                        r"|value\s+uniform\s+[^;]+;",
                        base_val,
                        entry,
                        count=1,
                        flags=re.S,
                    )
                else:
                    entry = entry.rstrip()
                    if entry.endswith("}"):
                        entry = entry[:-1] + f"        {base_val}\n    }}"
        merged_entries.append(entry)

    new_bf = "boundaryField\n{\n" + "\n".join(merged_entries) + "\n}"
    return field_text[: m_dst.start()] + new_bf + field_text[dst_end:]


def main() -> None:
    case = Path(__file__).resolve().parents[1]
    fluid = case / "fluid"
    src_dir = latest_time(fluid)
    print(f"=== seeding experiment 0/ from {src_dir.name} (baseline p/U, no p shift) ===")

    zero = fluid / "0"
    zero.mkdir(exist_ok=True)

    p_out = zero / "p"
    p_out.write_text(merge_boundary((src_dir / "p").read_text(), (fluid / "initial" / "p.experiment").read_text()))
    u_out = zero / "U"
    u_out.write_text(merge_boundary((src_dir / "U").read_text(), (fluid / "initial" / "U.experiment").read_text()))

    for out in (p_out, u_out):
        txt = out.read_text()
        txt = re.sub(r'(location\s+")[^"]+(")', r"\g<1>0\2", txt, count=1)
        out.write_text(txt)

    for name in ("phi", "uniform"):
        p = zero / name
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)

    print("  wrote fluid/0/U and fluid/0/p (experiment BCs, baseline pressure from d_TM)")


if __name__ == "__main__":
    sys.exit(main() or 0)
