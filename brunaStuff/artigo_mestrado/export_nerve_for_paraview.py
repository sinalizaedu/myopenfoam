"""Export the optic nerve STL as a VTP file so it can be opened in the
same ParaView session as the artery mesh, in the same coordinate system
(meters). The two were already aligned in the original master STL.

Output:
    cases/artoph-curva-mestrado/nerve_for_paraview.vtp
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import trimesh

REPO = Path(__file__).resolve().parents[1]
NERVE_STL = REPO / (
    "cases/artoph-curva-mestrado/solid/constant/triSurface/nerve.stl"
)
OUT_VTP = REPO / "cases/artoph-curva-mestrado/nerve_for_paraview.vtp"


def write_polydata_vtp(mesh: trimesh.Trimesh, out: Path) -> None:
    """Write a minimal ASCII PolyData VTP file (no scalar fields)."""
    V = mesh.vertices.astype(float)
    F = mesh.faces.astype(int)
    n_pts = len(V)
    n_polys = len(F)

    points_text = "\n".join(
        f"{v[0]:.6e} {v[1]:.6e} {v[2]:.6e}" for v in V
    )
    connectivity_text = "\n".join(" ".join(str(i) for i in face) for face in F)
    offsets_text = "\n".join(str((i + 1) * 3) for i in range(n_polys))

    vtp = f"""<?xml version="1.0"?>
<VTKFile type="PolyData" version="0.1" byte_order="LittleEndian">
  <PolyData>
    <Piece NumberOfPoints="{n_pts}" NumberOfVerts="0" NumberOfLines="0"
           NumberOfStrips="0" NumberOfPolys="{n_polys}">
      <Points>
        <DataArray type="Float32" NumberOfComponents="3" format="ascii">
{points_text}
        </DataArray>
      </Points>
      <Polys>
        <DataArray type="Int32" Name="connectivity" format="ascii">
{connectivity_text}
        </DataArray>
        <DataArray type="Int32" Name="offsets" format="ascii">
{offsets_text}
        </DataArray>
      </Polys>
    </Piece>
  </PolyData>
</VTKFile>
"""
    out.write_text(vtp)


nerve = trimesh.load_mesh(str(NERVE_STL))
print(f"[load] {NERVE_STL}")
print(f"  vertices: {len(nerve.vertices)},  faces: {len(nerve.faces)}")
print(f"  bbox m: {nerve.bounds}")
print(f"  bbox mm: x=[{nerve.bounds[0,0]*1e3:.2f},{nerve.bounds[1,0]*1e3:.2f}]")
print(f"            y=[{nerve.bounds[0,1]*1e3:.2f},{nerve.bounds[1,1]*1e3:.2f}]")
print(f"            z=[{nerve.bounds[0,2]*1e3:.2f},{nerve.bounds[1,2]*1e3:.2f}]")

write_polydata_vtp(nerve, OUT_VTP)
print(f"\n[write] {OUT_VTP}")
print("\nAbra no ParaView com File > Open  (ou arraste para a janela).")
print("Pra ver junto com a artéria, abra também:")
print(f"  {REPO / 'cases/artoph-curva-mestrado/solid/case.foam'}")
