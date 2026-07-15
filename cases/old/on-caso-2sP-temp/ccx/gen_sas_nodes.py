#!/usr/bin/env python3
"""
gen_sas_nodes.py
================
Gera um include com os node-sets necessarios para o caso de inchaco
(swelling) higroscopico do SAS (analogia de expansao volumetrica):

  *NSET, NSET=NALL       -> todos os nos (para *INITIAL CONDITIONS,TEMPERATURE)
  *NSET, NSET=SAS_NODES  -> nos pertencentes aos elementos do ELSET=SAS
                            (recebem a "temperatura" = campo de inchaco)

Le tudo do mesh .inp gerado pelo conversor (numeracao deterministica).

Uso:
  python3 gen_sas_nodes.py <mesh.inp> <out_nsets.inp>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> None:
    mesh_inp = Path(sys.argv[1])
    out = Path(sys.argv[2])
    txt = mesh_inp.read_text()

    # todos os ids de no do bloco *NODE
    nblocks = re.findall(r"\*NODE\b[^\n]*\n(.*?)(?=\n\*)", txt,
                         re.IGNORECASE | re.DOTALL)
    node_ids = []
    for blk in nblocks:
        for line in blk.strip().splitlines():
            head = line.split(",")[0].strip()
            if head.isdigit():
                node_ids.append(int(head))
    max_node = max(node_ids)

    # nos dos elementos SAS
    eblocks = re.findall(r"\*ELEMENT[^\n]*ELSET=SAS\b(.*?)(?=\n\*)",
                        txt, re.IGNORECASE | re.DOTALL)
    sas_nodes: set[int] = set()
    for blk in eblocks:
        for line in blk.strip().splitlines():
            parts = [p.strip() for p in line.split(",") if p.strip()]
            if parts and parts[0].isdigit():
                for p in parts[1:]:
                    if p.isdigit():
                        sas_nodes.add(int(p))

    sas_sorted = sorted(sas_nodes)
    lines = ["*NSET, NSET=NALL, GENERATE", f"1, {max_node}, 1", "*NSET, NSET=SAS_NODES"]
    row = []
    for i, n in enumerate(sas_sorted, 1):
        row.append(str(n))
        if i % 16 == 0:
            lines.append(", ".join(row))
            row = []
    if row:
        lines.append(", ".join(row))
    out.write_text("\n".join(lines) + "\n")
    print(f"OK: {out}  (NALL=1..{max_node}; SAS_NODES={len(sas_sorted)} nos)")


if __name__ == "__main__":
    main()
