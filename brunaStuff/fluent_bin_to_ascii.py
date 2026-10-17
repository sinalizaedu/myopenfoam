#!/usr/bin/env python3
"""Convert a binary ANSYS Fluent .msh export to the ASCII dialect fluent3DMeshToFoam reads.

OpenFOAM's fluent3DMeshToFoam lexer only accepts ASCII sections, so binary exports
from ANSYS Meshing (sections 2010/3010 nodes, 2012/3012 cells, 2013/3013 faces) have
to be rewritten as their ASCII counterparts (10/12/13) first.

Binary section layout, as written by ANSYS Meshing:

    (3010 (zone first last type nd)\n(<nd doubles per node>)\nEnd of Binary Section 3010)
    (2010 ...)                       same, single precision floats
    (2012 (zone first last type et))  empty body when et != 0 (uniform element type)
    (2013 (zone first last bc ft)\n(<int32 records>)\nEnd of Binary Section 2013)

Face records hold `ft` node indices followed by the two adjacent cell indices when the
face type is uniform (ft in 1..4), or a leading vertex count per face when ft is 0 or 5
(mixed/polygonal). Indices are 1-based, 0 meaning "no cell".

Usage:
    python3 brunaStuff/fluent_bin_to_ascii.py input.msh output.msh
"""

from __future__ import annotations

import argparse
import re
import struct
import sys
from pathlib import Path

# Binary tags: 2xxx are single precision / int32, 3xxx are double precision / int32.
NODE_TAGS = {"2010": "f", "3010": "d"}
CELL_TAGS = ("2012", "3012")
FACE_TAGS = ("2013", "3013")

SECTION_RE = re.compile(rb"\((\d{1,4}) \(([0-9a-fA-F ]+)\)")
ZONE_RE = re.compile(rb"\((?:39|45) \(\d+ [\w\-.]+ [^)]*\)\(\)\)")
DIM_RE = re.compile(rb"\(2 (\d)\)")


class ConversionError(RuntimeError):
    pass


def _hex_args(raw: bytes) -> list[int]:
    return [int(tok, 16) for tok in raw.decode("ascii").split()]


def _body_start(data: bytes, after_header: int) -> int:
    """Index of the first byte of a binary payload, i.e. just past the opening '('."""
    i = after_header
    while i < len(data) and data[i] in b" \t\r\n":
        i += 1
    if i >= len(data) or data[i] != ord("("):
        raise ConversionError(f"expected '(' opening a binary body at offset {after_header}")
    return i + 1


def _read_nodes(data: bytes, args: list[int], start: int, fmt: str) -> tuple[str, int]:
    zone, first, last, ntype = args[0], args[1], args[2], args[3]
    ndim = args[4] if len(args) > 4 else 3
    count = (last - first + 1) * ndim
    width = struct.calcsize(fmt)
    values = struct.unpack(f"<{count}{fmt}", data[start : start + count * width])

    lines = [f"(10 ({zone:x} {first:x} {last:x} {ntype} {ndim})("]
    lines += [
        " ".join(repr(v) for v in values[i : i + ndim]) for i in range(0, count, ndim)
    ]
    lines.append("))")
    return "\n".join(lines), start + count * width


def _read_faces(data: bytes, args: list[int], start: int) -> tuple[str, int]:
    zone, first, last, bctype, ftype = args[0], args[1], args[2], args[3], args[4]
    nfaces = last - first + 1

    lines = [f"(13 ({zone:x} {first:x} {last:x} {bctype:x} {ftype:x})("]
    if 1 <= ftype <= 4:
        stride = ftype + 2
        count = nfaces * stride
        rec = struct.unpack(f"<{count}i", data[start : start + count * 4])
        lines += [
            " ".join(f"{v:x}" for v in rec[i : i + stride])
            for i in range(0, count, stride)
        ]
        consumed = count * 4
    else:
        # Mixed/polygonal: each record is prefixed by its vertex count.
        offset = start
        for _ in range(nfaces):
            (nv,) = struct.unpack("<i", data[offset : offset + 4])
            stride = nv + 3
            rec = struct.unpack(f"<{stride}i", data[offset : offset + stride * 4])
            lines.append(" ".join(f"{v:x}" for v in rec))
            offset += stride * 4
        consumed = offset - start
    lines.append("))")
    return "\n".join(lines), start + consumed


def convert(src: Path, dst: Path) -> None:
    data = src.read_bytes()

    dim = DIM_RE.search(data)
    if dim is None:
        raise ConversionError("no (2 <dim>) dimension record found")
    dimension = int(dim.group(1))

    declarations: dict[str, str] = {}
    blocks: list[str] = []
    payloads: list[tuple[int, int]] = []

    # Sequential scan: binary payloads can contain byte sequences that look like a
    # section header, so the cursor has to step over each payload it decodes.
    pos = 0
    while (match := SECTION_RE.search(data, pos)) is not None:
        tag = match.group(1).decode("ascii")
        args = _hex_args(match.group(2))
        pos = match.end()

        if tag in ("10", "12", "13") and args[0] == 0:
            declarations[tag] = f"({tag} (0 {args[1]:x} {args[2]:x} {args[3]}))"
        elif tag in NODE_TAGS:
            body = _body_start(data, pos)
            block, pos = _read_nodes(data, args, body, NODE_TAGS[tag])
            payloads.append((body, pos))
            blocks.append(block)
        elif tag in CELL_TAGS:
            if len(args) < 5 or args[4] == 0:
                raise ConversionError(
                    f"cell zone {args[0]:x} has a mixed element type; "
                    "its binary body is not handled"
                )
            blocks.append(
                f"(12 ({args[0]:x} {args[1]:x} {args[2]:x} {args[3]:x} {args[4]:x}))"
            )
        elif tag in FACE_TAGS:
            body = _body_start(data, pos)
            block, pos = _read_faces(data, args, body)
            payloads.append((body, pos))
            blocks.append(block)

    missing = {"10", "12", "13"} - declarations.keys()
    if missing:
        raise ConversionError(f"missing declaration section(s): {sorted(missing)}")

    zones = [
        m.group(0).decode("ascii")
        for m in ZONE_RE.finditer(data)
        if not any(lo <= m.start() < hi for lo, hi in payloads)
    ]

    # The lexer skips (0 ...) comments by matching a quoted string that may not
    # contain parentheses, so keep the banner paren-free.
    out = [
        f'(0 "converted from binary Fluent export {src.name} by fluent_bin_to_ascii.py")',
        f"(2 {dimension})",
        declarations["10"],
        declarations["13"],
        declarations["12"],
        *blocks,
        *zones,
    ]
    dst.write_text("\n".join(out) + "\n")

    print(f"{src} -> {dst}")
    print(f"  dimension : {dimension}")
    for tag, label in (("10", "nodes"), ("12", "cells"), ("13", "faces")):
        print(f"  {label:<9}: {int(declarations[tag].split()[3], 16)}")
    print(f"  zones     : {len(zones)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("src", type=Path, help="binary Fluent .msh")
    parser.add_argument("dst", type=Path, help="ASCII Fluent .msh to write")
    args = parser.parse_args(argv)

    try:
        convert(args.src, args.dst)
    except ConversionError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
