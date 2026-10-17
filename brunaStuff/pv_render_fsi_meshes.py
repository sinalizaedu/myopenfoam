#!/usr/bin/env python3
"""Render the FSI fluid and solid meshes offscreen with ParaView.

Run with pvpython, not the system python:

    /Applications/ParaView-6.1.0.app/Contents/bin/pvpython \
        --force-offscreen-rendering brunaStuff/pv_render_fsi_meshes.py

Offscreen rendering avoids the macOS Qt/OpenGL context bug that floods the GUI
with "Hardware does not support the number of textures defined".
"""

from __future__ import annotations

import argparse
import os

from paraview.simple import *  # noqa: F403

REPO = "/Users/brunaenne/Documents/repos/myopenfoam"

# Same palette as brunaStuff/plot_o1_solid_mesh.py, as 0-1 RGB.
ZONES = [
    ("sclera", (0.847, 0.796, 0.706)),
    ("choroid", (0.663, 0.196, 0.149)),
    ("retina", (0.945, 0.580, 0.541)),
    ("cornea", (0.682, 0.839, 0.945)),
    ("ciliary", (0.490, 0.808, 0.627)),
    ("lens", (0.969, 0.863, 0.435)),
    ("iris", (0.733, 0.561, 0.808)),
]


def _norm(v):
    n = sum(c * c for c in v) ** 0.5
    return tuple(c / n for c in v)


def place_camera(view, bounds, direction, *, zoom: float = 1.0) -> None:
    cx = 0.5 * (bounds[0] + bounds[1])
    cy = 0.5 * (bounds[2] + bounds[3])
    cz = 0.5 * (bounds[4] + bounds[5])
    diag = (
        (bounds[1] - bounds[0]) ** 2
        + (bounds[3] - bounds[2]) ** 2
        + (bounds[5] - bounds[4]) ** 2
    ) ** 0.5
    d = _norm(direction)
    dist = 2.1 * diag / zoom
    view.CameraFocalPoint = [cx, cy, cz]
    view.CameraPosition = [cx + d[0] * dist, cy + d[1] * dist, cz + d[2] * dist]
    # Anterior is -y in this frame, so -y points up.
    view.CameraViewUp = [0.0, -1.0, 0.0]
    view.CameraParallelProjection = 1
    view.CameraParallelScale = 0.62 * diag / zoom


def load_solid(path: str):
    r = OpenFOAMReader(registrationName="solid", FileName=path)
    r.MeshRegions = ["internalMesh"]
    r.Readzones = 1
    r.SkipZeroTime = 0
    r.UpdatePipeline()
    return r


def load_fluid(path: str):
    r = OpenFOAMReader(registrationName="fluid", FileName=path)
    r.MeshRegions = ["internalMesh"]
    r.SkipZeroTime = 0
    r.UpdatePipeline()
    return r


def show_solid_zones(solid, view, *, opacity: float = 1.0, edges: bool = True):
    reps = []
    for name, color in ZONES:
        blk = ExtractBlock(
            registrationName=f"zone_{name}",
            Input=solid,
            Selectors=[f"/Root/zones/cellZones/{name}"],
        )
        rep = Show(blk, view)
        rep.Representation = "Surface With Edges" if edges else "Surface"
        rep.DiffuseColor = list(color)
        rep.AmbientColor = list(color)
        rep.ColorArrayName = [None, ""]
        rep.EdgeColor = [0.18, 0.22, 0.26]
        rep.LineWidth = 0.5
        rep.Opacity = opacity
        reps.append(rep)
    return reps


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--case", default=f"{REPO}/cases/fsi-baseline-o1-volume-fluid")
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--width", type=int, default=1700)
    ap.add_argument("--height", type=int, default=1400)
    args = ap.parse_args()

    outdir = args.outdir or os.path.join(args.case, "figures")
    os.makedirs(outdir, exist_ok=True)
    res = [args.width, args.height]

    solid_foam = os.path.join(args.case, "solid", "solid.foam")
    fluid_foam = os.path.join(args.case, "fluid", "O1.foam")

    # --- 1. Solid only, oblique cutaway showing both symmetry faces. -----
    view = CreateRenderView()
    view.Background = [1.0, 1.0, 1.0]
    view.UseColorPaletteForBackground = 0
    view.OrientationAxesVisibility = 0

    solid = load_solid(solid_foam)
    show_solid_zones(solid, view)
    bounds = solid.GetDataInformation().GetBounds()
    place_camera(view, bounds, (-1.0, 0.35, 1.0))
    Render(view)
    out1 = os.path.join(outdir, "pv_solid_zones_oblique.png")
    SaveScreenshot(out1, view, ImageResolution=res, TransparentBackground=0)
    print(f"Wrote {out1}")

    # --- 2. Same solid seen straight onto the symmetry_0 plane. ----------
    place_camera(view, bounds, (-1.0, 0.0, 0.0), zoom=1.05)
    Render(view)
    out2 = os.path.join(outdir, "pv_solid_zones_meridional.png")
    SaveScreenshot(out2, view, ImageResolution=res, TransparentBackground=0)
    print(f"Wrote {out2}")

    # --- 3. Fluid plus translucent solid, to check they nest correctly. --
    view2 = CreateRenderView()
    view2.Background = [1.0, 1.0, 1.0]
    view2.UseColorPaletteForBackground = 0
    view2.OrientationAxesVisibility = 0

    fluid = load_fluid(fluid_foam)
    frep = Show(fluid, view2)
    frep.Representation = "Surface With Edges"
    frep.DiffuseColor = [0.13, 0.47, 0.71]
    frep.AmbientColor = [0.13, 0.47, 0.71]
    frep.ColorArrayName = [None, ""]
    frep.EdgeColor = [0.05, 0.16, 0.28]
    frep.LineWidth = 0.4

    solid2 = load_solid(solid_foam)
    show_solid_zones(solid2, view2, opacity=0.30, edges=False)

    b2 = solid2.GetDataInformation().GetBounds()
    place_camera(view2, b2, (-1.0, 0.35, 1.0))
    Render(view2)
    out3 = os.path.join(outdir, "pv_fluid_plus_solid.png")
    SaveScreenshot(out3, view2, ImageResolution=res, TransparentBackground=0)
    print(f"Wrote {out3}")

    fb = fluid.GetDataInformation().GetBounds()
    print(f"fluid bounds  {tuple(round(x, 6) for x in fb)}")
    print(f"solid bounds  {tuple(round(x, 6) for x in b2)}")


if __name__ == "__main__":
    main()
