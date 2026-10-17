"""Load the FSI fluid and solid meshes into the ParaView GUI, ready to inspect.

    /Applications/ParaView-6.1.0.app/Contents/MacOS/paraview \
        --script=brunaStuff/pv_load_fsi_meshes.py

Each tissue zone gets an explicit solid colour instead of a mapped array, so no
scalar bar is created. On macOS the scalar bar goes through
vtkOpenGLContextDevice2D, which is the component that throws
"Hardware does not support the number of textures defined" in ParaView 6.1.
"""

from paraview.simple import *  # noqa: F403

CASE = "/Users/brunaenne/Documents/repos/myopenfoam/cases/fsi-baseline-o1-volume-fluid"

ZONES = [
    ("sclera", (0.847, 0.796, 0.706)),
    ("choroid", (0.663, 0.196, 0.149)),
    ("retina", (0.945, 0.580, 0.541)),
    ("cornea", (0.682, 0.839, 0.945)),
    ("ciliary", (0.490, 0.808, 0.627)),
    ("lens", (0.969, 0.863, 0.435)),
    ("iris", (0.733, 0.561, 0.808)),
]


def main() -> None:
    view = GetActiveViewOrCreate("RenderView")
    view.Background = [1.0, 1.0, 1.0]
    view.UseColorPaletteForBackground = 0

    solid = OpenFOAMReader(
        registrationName="solid", FileName=f"{CASE}/solid/solid.foam"
    )
    solid.MeshRegions = ["internalMesh"]
    solid.Readzones = 1
    solid.SkipZeroTime = 0
    solid.UpdatePipeline()

    for name, color in ZONES:
        blk = ExtractBlock(
            registrationName=name,
            Input=solid,
            Selectors=[f"/Root/zones/cellZones/{name}"],
        )
        rep = Show(blk, view)
        rep.Representation = "Surface With Edges"
        rep.ColorArrayName = [None, ""]
        rep.DiffuseColor = list(color)
        rep.AmbientColor = list(color)
        rep.EdgeColor = [0.18, 0.22, 0.26]
        rep.LineWidth = 0.5

    fluid = OpenFOAMReader(
        registrationName="fluid", FileName=f"{CASE}/fluid/O1.foam"
    )
    fluid.MeshRegions = ["internalMesh"]
    fluid.SkipZeroTime = 0
    fluid.UpdatePipeline()
    frep = Show(fluid, view)
    frep.Representation = "Surface With Edges"
    frep.ColorArrayName = [None, ""]
    frep.DiffuseColor = [0.13, 0.47, 0.71]
    frep.AmbientColor = [0.13, 0.47, 0.71]
    frep.EdgeColor = [0.05, 0.16, 0.28]
    frep.LineWidth = 0.4
    frep.Visibility = 0  # start with the solid alone; toggle the eye to compare

    ResetCamera(view)
    # Anterior is -y in this frame.
    view.CameraViewUp = [0.0, -1.0, 0.0]
    Render(view)
    print("FSI meshes loaded: 7 solid tissue zones plus a hidden fluid mesh.")


main()
