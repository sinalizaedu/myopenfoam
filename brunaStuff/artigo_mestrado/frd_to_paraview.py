#!/usr/bin/env python3
"""
frd_to_paraview.py
==================
Converte um resultado CalculiX (.frd) + a malha (.inp) em uma SERIE TEMPORAL
ParaView (.pvd + um .vtu por passo de carga do Riks), carregando o campo de
DESLOCAMENTO nodal U (vetor) e a tensao de von Mises. Pensado para VISUALIZAR
A FLAMBAGEM: abrir o .pvd no ParaView, aplicar "Warp By Vector" em U e dar play
para ver o nervo dobrar conforme o fator de carga lambda cresce de 0 a 1.

Nao depende de ccx2paraview (que nao esta instalado no host nem no container).
Reaproveita o parser de malha do inp_to_vtk.py e o parser multi-passo do
frd_stress.py.

Uso:
    python3 brunaStuff/frd_to_paraview.py \
        --inp cases/on-caso-3F2/ccx/on-caso-3F2_mesh.inp \
        --frd cases/on-caso-3F2/ccx/on-caso-3F2.frd \
        --out cases/on-caso-3F2/ccx/pv/on-caso-3F2

Gera:
    <out>.pvd            (abrir este no ParaView)
    <out>_t000.vtu ...   (um por passo)
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from inp_to_vtk import parse_inp          # nodes{nid:(x,y,z)}, elems[(eid,conn,zone)]
from frd_stress import parse_frd          # nodes, n2zone, steps[{lam,disp,vm}]

VTK_HEXAHEDRON = 12


def write_vtu(out: Path, node_ids, idx, nodes, elems, zone_id,
              disp, vm):
    npts = len(node_ids)
    ncells = len(elems)
    with open(out, "w") as fh:
        fh.write('<?xml version="1.0"?>\n')
        fh.write('<VTKFile type="UnstructuredGrid" version="0.1" byte_order="LittleEndian">\n')
        fh.write("  <UnstructuredGrid>\n")
        fh.write(f'    <Piece NumberOfPoints="{npts}" NumberOfCells="{ncells}">\n')

        # ---- points (coords originais; o warp aplica U) ----
        fh.write("      <Points>\n")
        fh.write('        <DataArray type="Float64" NumberOfComponents="3" format="ascii">\n')
        for nid in node_ids:
            x, y, z = nodes[nid]
            fh.write(f"          {x:.8e} {y:.8e} {z:.8e}\n")
        fh.write("        </DataArray>\n      </Points>\n")

        # ---- cells ----
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

        # ---- point data: U (vetor), |U|, |U_lat|, vonMises ----
        fh.write('      <PointData Vectors="U">\n')
        fh.write('        <DataArray type="Float64" Name="U" NumberOfComponents="3" format="ascii">\n')
        for nid in node_ids:
            ux, uy, uz = disp.get(nid, (0.0, 0.0, 0.0))
            fh.write(f"          {ux:.8e} {uy:.8e} {uz:.8e}\n")
        fh.write("        </DataArray>\n")
        fh.write('        <DataArray type="Float64" Name="U_mag" format="ascii">\n')
        for nid in node_ids:
            ux, uy, uz = disp.get(nid, (0.0, 0.0, 0.0))
            fh.write(f"          {math.sqrt(ux*ux+uy*uy+uz*uz):.8e}\n")
        fh.write("        </DataArray>\n")
        fh.write('        <DataArray type="Float64" Name="U_lat" format="ascii">\n')
        for nid in node_ids:
            ux, uy, _ = disp.get(nid, (0.0, 0.0, 0.0))
            fh.write(f"          {math.hypot(ux, uy):.8e}\n")
        fh.write("        </DataArray>\n")
        fh.write('        <DataArray type="Float64" Name="vonMises" format="ascii">\n')
        for nid in node_ids:
            fh.write(f"          {vm.get(nid, 0.0):.8e}\n")
        fh.write("        </DataArray>\n")
        fh.write("      </PointData>\n")

        # ---- cell data: zone_id ----
        fh.write('      <CellData Scalars="zone_id">\n')
        fh.write('        <DataArray type="Int32" Name="zone_id" format="ascii">\n')
        for _, _, z in elems:
            fh.write(f"          {zone_id[z]}\n")
        fh.write("        </DataArray>\n      </CellData>\n")

        fh.write("    </Piece>\n  </UnstructuredGrid>\n</VTKFile>\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inp", required=True, type=Path, help="*_mesh.inp (NODE+ELEMENT hex)")
    ap.add_argument("--frd", required=True, type=Path, help=".frd do CalculiX")
    ap.add_argument("--out", required=True, type=Path,
                    help="prefixo de saida (ex.: .../pv/on-caso-3F2)")
    args = ap.parse_args()

    nodes, elems = parse_inp(args.inp)
    if not elems:
        raise SystemExit("Nenhum hex no .inp.")
    node_ids = sorted(nodes.keys())
    idx = {nid: i for i, nid in enumerate(node_ids)}
    zones = sorted({z for (_, _, z) in elems})
    zone_id = {z: i for i, z in enumerate(zones)}

    _, _, steps = parse_frd(args.frd)
    steps = sorted(steps, key=lambda d: (d["lam"] if d["lam"] is not None else 0.0))
    if not steps:
        raise SystemExit("Nenhum passo de DISP no .frd.")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    pvd_entries = []
    for k, stp in enumerate(steps):
        lam = stp["lam"] if stp["lam"] is not None else float(k)
        vtu = args.out.parent / f"{args.out.name}_t{k:03d}.vtu"
        write_vtu(vtu, node_ids, idx, nodes, elems, zone_id,
                  stp.get("disp", {}), stp.get("vm", {}))
        pvd_entries.append((lam, vtu.name))

    pvd = args.out.with_suffix(".pvd")
    with open(pvd, "w") as fh:
        fh.write('<?xml version="1.0"?>\n')
        fh.write('<VTKFile type="Collection" version="0.1" byte_order="LittleEndian">\n')
        fh.write("  <Collection>\n")
        for lam, name in pvd_entries:
            fh.write(f'    <DataSet timestep="{lam:.6f}" group="" part="0" file="{name}"/>\n')
        fh.write("  </Collection>\n</VTKFile>\n")

    print(f"[frd_to_paraview] {len(node_ids)} nos, {len(elems)} hexs, {len(steps)} passos")
    print(f"[frd_to_paraview] zonas (zone_id): " +
          ", ".join(f"{z}={zone_id[z]}" for z in zones))
    print(f"[frd_to_paraview] lambdas: " +
          ", ".join(f"{lam:.3f}" for lam, _ in pvd_entries))
    print(f"[frd_to_paraview] abrir no ParaView: {pvd}")


if __name__ == "__main__":
    main()
