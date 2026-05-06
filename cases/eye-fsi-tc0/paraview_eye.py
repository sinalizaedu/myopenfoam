"""
eye-fsi-tc0 — ParaView visualisation script
============================================
Two domains:
  fluid/ — coloured by velocity magnitude U
  solid/ — all structures (lens + iris + sclera + cornea), coloured by |D|
           Warp By Vector applied to solid to amplify deformation ×500

IOP = 10 mmHg initial condition → expected deformations:
  sclera  ~0.5 µm  (E=2.5 MPa)
  cornea  ~2.3 µm  (E=0.57 MPa)
  iris    larger   (E=2 kPa, spring-restrained at base)

With WARP_SCALE=500 those displacements become 0.25–1.15 mm → clearly visible.

Run:
  pvpython paraview_eye.py
  OR: ParaView GUI → Tools → Python Shell → paste → Run Script
"""

from paraview.simple import *
import os

CASE       = os.path.dirname(os.path.abspath(__file__))
WARP_SCALE = 500      # amplify solid displacement for visualisation

view = GetActiveViewOrCreate('RenderView')
view.Background = [0.15, 0.15, 0.15]

# ── 1. Fluid — coloured by velocity magnitude ─────────────────────────────
fluidSrc = OpenFOAMReader(
    registrationName='Fluid',
    FileName=os.path.join(CASE, 'fluid', 'eye-fsi-tc0-fluid.foam')
)
fluidSrc.MeshRegions = ['internalMesh']
fluidSrc.CellArrays  = ['U', 'p']
fluidSrc.UpdatePipeline()
fluidDisp = Show(fluidSrc, view)
ColorBy(fluidDisp, ('CELLS', 'U'))
fluidDisp.SetScalarBarVisibility(view, True)

# ── 2. Solid — all structures, warped by displacement ─────────────────────
solidSrc = OpenFOAMReader(
    registrationName='Solid',
    FileName=os.path.join(CASE, 'solid', 'eye-fsi-tc0-solid.foam')
)
solidSrc.MeshRegions = ['internalMesh']
solidSrc.CellArrays  = ['D']
solidSrc.UpdatePipeline()

# Convert cell-centred D to point-centred for Warp By Vector
cellToPoint = CellDatatoPointData(Input=solidSrc)
cellToPoint.CellDataArraytoprocess = ['D']

warp = WarpByVector(Input=cellToPoint)
warp.Vectors = ['POINTS', 'D']
warp.ScaleFactor = WARP_SCALE

warpDisp = Show(warp, view)
ColorBy(warpDisp, ('POINTS', 'D'))
warpDisp.Opacity = 0.95

# ── Camera: 2-D orthographic view ─────────────────────────────────────────
view.CameraPosition   = [0.011,  0.012, 0.5]
view.CameraFocalPoint = [0.011,  0.012, 0.0005]
view.CameraViewUp     = [0.0,    1.0,   0.0]
ResetCamera()
Render()

print("\n=== eye-fsi-tc0 loaded ===")
print(f"  fluid/  : velocity U (coloured) + pressure p")
print(f"  solid/  : lens + iris + sclera + cornea — displacement D")
print(f"            Warped ×{WARP_SCALE} so µm deformations appear as mm")
print( "  Scrub the time slider to animate 0 → 25 s")
print( "  IOP=10 mmHg initial load → sclera ~0.5 µm, cornea ~2 µm, iris larger\n")

# ══════════════════════════════════════════════════════════════════════════
# MANUAL STEPS (GUI):
#   1. File > Open → fluid/eye-fsi-tc0-fluid.foam   → Apply
#   2. File > Open → solid/eye-fsi-tc0-solid.foam   → Apply
#        Cell Arrays: check "D"
#   3. Filters > Alphabetical > Cell Data to Point Data  → Apply
#   4. Filters > Common > Warp By Vector
#        Vectors: D,  Scale Factor: 500              → Apply
#        Colour by "D" → lens/iris/sclera/cornea deformation visible
# ══════════════════════════════════════════════════════════════════════════
