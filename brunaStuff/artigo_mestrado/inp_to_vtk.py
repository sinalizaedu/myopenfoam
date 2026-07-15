#!/usr/bin/env python3
"""
inp_to_vtk.py
=============
Converte a malha de um .inp CalculiX (apenas *NODE + *ELEMENT hex C3D8/C3D8I/
C3D8R) em um .vtu (VTK UnstructuredGrid XML) para visualizar a GEOMETRIA no
ParaView -- sem precisar rodar o solver.

Util para inspecionar a tortuosidade inicial embutida em on-caso-2.2 (que vive
no .inp, nao no polyMesh -> abrir case.foam mostraria a malha reta).

- Ignora *ELEMENT SPRINGA (molas Winkler/trabeculas) e quaisquer nos fantasmas.
- Emite um campo de celula "zone_id" (inteiro por ELSET) para colorir por zona
  (ON, PIA, DURA, LC, ...).

Uso:
    python3 inp_to_vtk.py --inp caso_mesh.inp --out caso_mesh.vtu
"""

from __future__ import annotations

import argparse
from pathlib import Path

# C3D8 (CalculiX) e VTK_HEXAHEDRON (type 12) usam a MESMA ordem de nos:
# quad inferior CCW (0-1-2-3) seguido do quad superior CCW (4-5-6-7).
VTK_HEXAHEDRON = 12
HEX_TYPES = {"C3D8", "C3D8I", "C3D8R"}


def parse_inp(path: Path):
    nodes: dict[int, tuple[float, float, float]] = {}
    elems: list[tuple[int, list[int], str]] = []  # (eid, [node_ids], zone)

    mode = None          # 'node' | 'elem' | None
    cur_zone = "UNSET"
    cur_is_hex = False

    for raw in path.read_text().splitlines():
        s = raw.strip()
        if not s or s.startswith("**"):
            continue
        if s.startswith("*"):
            kw = s.upper()
            if kw.startswith("*NODE") and not kw.startswith("*NODE PRINT") \
                    and not kw.startswith("*NODE FILE"):
                mode = "node"
            elif kw.startswith("*ELEMENT"):
                mode = "elem"
                etype = ""
                for tok in s.split(","):
                    t = tok.strip()
                    if t.upper().startswith("TYPE="):
                        etype = t.split("=", 1)[1].strip().upper()
                    if t.upper().startswith("ELSET="):
                        cur_zone = t.split("=", 1)[1].strip()
                cur_is_hex = etype in HEX_TYPES
            else:
                mode = None
            continue

        parts = [p.strip() for p in s.split(",") if p.strip() != ""]
        if mode == "node" and len(parts) >= 4:
            nid = int(parts[0])
            nodes[nid] = (float(parts[1]), float(parts[2]), float(parts[3]))
        elif mode == "elem" and cur_is_hex and len(parts) >= 9:
            eid = int(parts[0])
            conn = [int(x) for x in parts[1:9]]
            elems.append((eid, conn, cur_zone))

    return nodes, elems


def write_vtu(out: Path, nodes, elems):
    node_ids = sorted(nodes.keys())
    idx = {nid: i for i, nid in enumerate(node_ids)}

    zones = sorted({z for (_, _, z) in elems})
    zone_id = {z: i for i, z in enumerate(zones)}

    npts = len(node_ids)
    ncells = len(elems)

    with open(out, "w") as fh:
        fh.write('<?xml version="1.0"?>\n')
        fh.write('<VTKFile type="UnstructuredGrid" version="0.1" '
                 'byte_order="LittleEndian">\n')
        fh.write("  <UnstructuredGrid>\n")
        fh.write(f'    <Piece NumberOfPoints="{npts}" NumberOfCells="{ncells}">\n')

        fh.write("      <Points>\n")
        fh.write('        <DataArray type="Float64" NumberOfComponents="3" format="ascii">\n')
        for nid in node_ids:
            x, y, z = nodes[nid]
            fh.write(f"          {x:.8e} {y:.8e} {z:.8e}\n")
        fh.write("        </DataArray>\n")
        fh.write("      </Points>\n")

        fh.write("      <Cells>\n")
        fh.write('        <DataArray type="Int64" Name="connectivity" format="ascii">\n')
        for _, conn, _ in elems:
            fh.write("          " + " ".join(str(idx[n]) for n in conn) + "\n")
        fh.write("        </DataArray>\n")
        fh.write('        <DataArray type="Int64" Name="offsets" format="ascii">\n')
        off = 0
        for _ in elems:
            off += 8
            fh.write(f"          {off}\n")
        fh.write("        </DataArray>\n")
        fh.write('        <DataArray type="UInt8" Name="types" format="ascii">\n')
        for _ in elems:
            fh.write(f"          {VTK_HEXAHEDRON}\n")
        fh.write("        </DataArray>\n")
        fh.write("      </Cells>\n")

        fh.write("      <CellData Scalars=\"zone_id\">\n")
        fh.write('        <DataArray type="Int32" Name="zone_id" format="ascii">\n')
        for _, _, z in elems:
            fh.write(f"          {zone_id[z]}\n")
        fh.write("        </DataArray>\n")
        fh.write("      </CellData>\n")

        fh.write("    </Piece>\n")
        fh.write("  </UnstructuredGrid>\n")
        fh.write("</VTKFile>\n")

    print(f"[inp_to_vtk] {npts} nos, {ncells} hexs -> {out}")
    print(f"[inp_to_vtk] zonas (zone_id): " +
          ", ".join(f"{z}={zone_id[z]}" for z in zones))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inp", required=True, type=Path, help="Arquivo .inp da malha")
    ap.add_argument("--out", type=Path, default=None,
                    help="Saida .vtu (default: mesmo nome do .inp com extensao .vtu)")
    args = ap.parse_args()

    out = args.out or args.inp.with_suffix(".vtu")
    nodes, elems = parse_inp(args.inp)
    if not elems:
        raise SystemExit("Nenhum elemento hex encontrado no .inp.")
    write_vtu(out, nodes, elems)


if __name__ == "__main__":
    main()
