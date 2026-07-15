#!/usr/bin/env python3
"""
frd_to_vtu.py
=============
Exporta um .frd do CalculiX para uma SERIE temporal .vtu + um indice .pvd que
o ParaView abre direto -- SEM depender de vtk/ccx2paraview (usa o parser puro
frd_stress.parse_frd e a malha do .inp).

Gera, por passo de carga (lambda do Riks):
  <prefix>.<k>.vtu  com:
    - pontos = coords de REFERENCIA (malha do .inp; ja' varrida em J se for o caso)
    - PointData: U (vetor 3-comp, deslocamento)   -> use "Warp By Vector" no ParaView
                 vmises (escalar, tensao de von Mises) quando houver STRESS
    - CellData:  zone_id (inteiro por ELSET: ON, PIA, DURA, ...)
  <prefix>.pvd     indexando os .vtu por timestep = lambda.

Uso:
    brunaStuff/.venv/bin/python brunaStuff/frd_to_vtu.py \\
        --inp cases/on-caso-3J/ccx/on-caso-3J_mesh.inp \\
        --frd cases/on-caso-3J/ccx/on-caso-3J.frd
    (default --out = mesmo dir/prefixo do .frd)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from frd_stress import parse_frd
from inp_to_vtk import parse_inp

VTK_HEXAHEDRON = 12


def write_vtu(out: Path, node_ids, idx, nodes, elems, zone_id, U, vm):
    npts = len(node_ids)
    ncells = len(elems)
    with open(out, "w") as fh:
        fh.write('<?xml version="1.0"?>\n')
        fh.write('<VTKFile type="UnstructuredGrid" version="0.1" byte_order="LittleEndian">\n')
        fh.write("  <UnstructuredGrid>\n")
        fh.write(f'    <Piece NumberOfPoints="{npts}" NumberOfCells="{ncells}">\n')

        fh.write("      <Points>\n")
        fh.write('        <DataArray type="Float64" NumberOfComponents="3" format="ascii">\n')
        for nid in node_ids:
            x, y, z = nodes[nid]
            fh.write(f"          {x:.8e} {y:.8e} {z:.8e}\n")
        fh.write("        </DataArray>\n      </Points>\n")

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
        fh.write("        </DataArray>\n      </Cells>\n")

        has_vm = bool(vm)
        scalars = ' Scalars="vmises"' if has_vm else ""
        fh.write(f'      <PointData Vectors="U"{scalars}>\n')
        fh.write('        <DataArray type="Float64" Name="U" NumberOfComponents="3" format="ascii">\n')
        for nid in node_ids:
            ux, uy, uz = U.get(nid, (0.0, 0.0, 0.0))
            fh.write(f"          {ux:.8e} {uy:.8e} {uz:.8e}\n")
        fh.write("        </DataArray>\n")
        if has_vm:
            fh.write('        <DataArray type="Float64" Name="vmises" format="ascii">\n')
            for nid in node_ids:
                fh.write(f"          {vm.get(nid, 0.0):.8e}\n")
            fh.write("        </DataArray>\n")
        fh.write("      </PointData>\n")

        fh.write('      <CellData Scalars="zone_id">\n')
        fh.write('        <DataArray type="Int32" Name="zone_id" format="ascii">\n')
        for _, _, z in elems:
            fh.write(f"          {zone_id[z]}\n")
        fh.write("        </DataArray>\n      </CellData>\n")

        fh.write("    </Piece>\n  </UnstructuredGrid>\n</VTKFile>\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inp", required=True, type=Path, help="malha .inp (geometria de referencia)")
    ap.add_argument("--frd", required=True, type=Path, help=".frd do CalculiX")
    ap.add_argument("--out", type=Path, default=None,
                    help="prefixo de saida (default = .frd sem extensao)")
    a = ap.parse_args()

    prefix = a.out or a.frd.with_suffix("")
    prefix = Path(prefix)

    nodes, elems = parse_inp(a.inp)
    node_ids = sorted(nodes.keys())
    idx = {nid: i for i, nid in enumerate(node_ids)}
    zones = sorted({z for (_, _, z) in elems})
    zone_id = {z: i for i, z in enumerate(zones)}

    _, _n2zone, steps = parse_frd(a.frd)
    steps = [s for s in steps if s.get("disp")]
    steps.sort(key=lambda d: (d["lam"] if d["lam"] is not None else 0.0))
    if not steps:
        raise SystemExit("Nenhum passo com deslocamento no .frd.")

    pvd = ['<?xml version="1.0"?>',
           '<VTKFile type="Collection" version="0.1" byte_order="LittleEndian">',
           "  <Collection>"]
    for k, stp in enumerate(steps):
        lam = stp["lam"] if stp["lam"] is not None else float(k)
        vtu = prefix.with_name(f"{prefix.name}.{k}.vtu")
        write_vtu(vtu, node_ids, idx, nodes, elems, zone_id, stp["disp"], stp.get("vm", {}))
        pvd.append(f'    <DataSet timestep="{lam:.6f}" part="0" file="{vtu.name}"/>')
    pvd += ["  </Collection>", "</VTKFile>"]
    pvd_path = prefix.with_suffix(".pvd")
    pvd_path.write_text("\n".join(pvd) + "\n")

    print(f"[frd_to_vtu] {len(steps)} passos -> {prefix.name}.0..{len(steps)-1}.vtu")
    print(f"[frd_to_vtu] indice ParaView: {pvd_path}")
    print(f"[frd_to_vtu] PointData: U (vetor; Warp By Vector), "
          f"vmises ({'sim' if steps[-1].get('vm') else 'ausente'}); CellData: zone_id")
    print(f"[frd_to_vtu] zonas: " + ", ".join(f"{z}={zone_id[z]}" for z in zones))


if __name__ == "__main__":
    main()
