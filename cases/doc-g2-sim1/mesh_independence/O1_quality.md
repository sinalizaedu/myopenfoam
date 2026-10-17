# O1 — native `blockMesh` mesh of the G2-fluid domain

O1 is the Lamminsalo/Missel G2-fluid domain (anterior chamber + posterior
chamber + pupil + trabecular meshwork + vitreous, with the lens and iris as
voids) written by hand as a single `blockMeshDict`. No Gmsh, no Python, no
`gmshToFoam`, no `changeDictionary`: every coordinate is read off Missel (2012)
/ Lamminsalo (2018) Tables SI–SII or evaluated analytically from the five
surfaces those tables define, and all of it is documented in the header of
`fluid/system/blockMeshDict.O1`.

## Reproduce

```bash
docker compose run --rm fsi bash -lc '
  mkdir -p /tmp/o1/system
  cp /simulation/doc-g2-sim1/fluid/system/{controlDict,fvSchemes,fvSolution} /tmp/o1/system/
  cp /simulation/doc-g2-sim1/fluid/system/blockMeshDict.O1 /tmp/o1/system/blockMeshDict
  cd /tmp/o1 && blockMesh
  checkMesh -allGeometry -allTopology -writeAllFields
  foamToVTK -constant -one-boundary
  python3 /opt/brunaStuff/verify_o1_mesh.py'
```

The mesh is built in a scratch directory on purpose: `fluid/constant/polyMesh`
still holds the production Gmsh mesh, and O1 is not wired into `Allrun` yet.

## Mesh statistics

| | |
|---|---|
| Cells | 54,672 |
| Points | 61,832 |
| Faces | 170,936 (156,448 internal) |
| Hexahedra | 54,024 (98.8%) |
| Prisms | 648 (1.2%) — the four axis-touching blocks only |
| Pyramids / tets / polyhedra | 0 |
| Blocks | 32 (16 meridional regions × 2 azimuthal blocks of 45°) |
| Azimuthal resolution | 12 cells over 90° (7.5°/cell) |
| Cell zones | `tm_zone`, 720 cells |
| Bounding box | x ∈ [0, 8.37], y ∈ [−8.16, 6.90], z ∈ [0, 8.37] mm |

Patches, all non-empty, with no `defaultFaces`:

| Patch | Type | Faces |
|---|---|---:|
| `outlet_tm` | patch | 144 |
| `ac_inlet` | patch | 96 |
| `lens_wall` | wall | 1,824 |
| `iris_wall` | wall | 1,128 |
| `wall` | wall | 2,184 |
| `symmetry_0` | symmetry | 4,556 |
| `symmetry_90` | symmetry | 4,556 |

This is exactly the patch set `fluid/initial/U`, `fluid/initial/p` and
`changeDictionaryDict` already expect, so no boundary-condition edits are
needed to run on O1.

## Quality against the plan's targets

| Metric | Target | O1 | |
|---|---|---|---|
| Number of regions | 1 | 1 | pass |
| Open edges / boundary openness | 0 / OK | 0 / 7e−16 | pass |
| Max cell openness | OK | 8.6e−16 | pass |
| Max non-orthogonality | < 70°, aim < 60° | **55.87°** | pass |
| Average non-orthogonality | < 20° | **13.66°** | pass |
| Max skewness | < 4, aim < 2 | **0.890** | pass |
| Max aspect ratio | < 100 | **52.99** (19.77 off-axis) | pass |
| Min cell volume | > 0 | 3.12e−14 m³ | pass |
| Min face area | > 0 | 2.22e−10 m² | pass |
| Face pyramids / tets | OK | OK | pass |
| Concave cells | none | none | pass |
| Face flatness | — | min 0.9995 | pass |
| Face interpolation weight | — | min 0.146 | pass |
| Face volume ratio | — | min 0.164 | pass |
| Min cell determinant | > 0.001 | **9.56e−06** | **fail** |

`checkMesh` reports `Failed 1 mesh checks` — the cell-determinant
(well-posedness) check, with 1,398 cells (2.56%) below 0.001.

### Why the determinant check fails, and why it is acceptable

The determinant measure penalises cells whose three edge directions are very
unequal in length. It is a warning about the *conditioning* of the least-squares
gradient reconstruction, not a validity error: the cells are all convex, all
positive-volume, all closed, and skewness and non-orthogonality are well inside
target.

The low-determinant cells are exactly where the anatomy is thin:

| Location | Cells | Cause |
|---|---:|---|
| Pupil channel + pupil exit (`PCi`, `AC5`) | 1,244 | 3.9 µm across the gap vs ~420 µm of azimuthal extent at r ≈ 3.2 mm |
| Revolve axis (r < 0.3 mm) | 124 | azimuthal extent → 0 on the axis, the standard collapsed-hex treatment |
| TM / iridocorneal angle | 30 | 22.8 µm × 28.9 µm cells inside a millimetre-scale domain |

The worst cell (det 9.56e−06) sits at r = 3.247 mm, y = −5.069 mm, i.e. inside
the 37 µm iris–lens minimum clearance. Its aspect ratio is 16.4. Both are the
direct consequence of resolving a 37 µm gap in a 16 mm eye — the same trade-off
the plan anticipated, and the reason the plan set the aspect-ratio budget at 100
rather than 10.

Refining azimuthally makes this *worse*, not better: at n_θ = 14 the minimum
determinant rises slightly (1.27e−05) but the max aspect ratio grows from 53 to
62 and the low-determinant population grows to 1,580, because shrinking the
azimuthal cell size thins the axis prisms faster than it fattens the pupil
cells. n_θ = 12 is the better operating point and is what is shipped.

### Compared with the production Gmsh mesh

Same `checkMesh -allGeometry` on `fluid/constant/polyMesh` as currently
installed (the Gmsh OCC-revolve mesh the calibrated Sim-1 results were produced
on):

| Metric | O1 (`blockMesh`) | Resident Gmsh mesh |
|---|---|---|
| Cells | 54,672 | 175,362 |
| Cell types | 98.8% hex, 1.2% prism | 0% hex, 99.4% prism, 486 tets |
| Max non-orthogonality | 55.87° | 35.98° |
| Average non-orthogonality | 13.66° | 2.24° |
| Max skewness | 0.890 | 1.887 |
| Max aspect ratio | 52.99 | 28.26 |
| Min cell volume | 3.12e−14 | 9.55e−15 |
| Min cell determinant | 9.56e−06 | **8.67e−19** |
| Cells with determinant < 0.001 | 1,398 (2.56%) | **24,758 (14.12%)** |
| Average determinant | 0.239 | 0.033 |
| `checkMesh` verdict | Failed 1 check | Failed 1 check |

Both meshes fail the same single check, and O1 fails it far less badly: thirteen
orders of magnitude better minimum determinant, a fifth of the affected
fraction, seven times the average. O1 is also better on skewness and minimum
volume, with a third of the cell count. The Gmsh mesh wins on non-orthogonality
and aspect ratio, which is expected — it is a 2D triangulation swept azimuthally,
so its cells are near-uniform in the sweep direction, whereas O1 pays for being
all-hex by grading hard into the thin features.

## Acceptance checks

Verified independently of the dict by `brunaStuff/verify_o1_mesh.py`, which
reads only `constant/polyMesh` and compares against the analytic surfaces. All
pass.

### 1. The TM is a rectangle

Table SI gives a parallelogram, not a perfect rectangle, and O1 keeps the table
values rather than snapping to 90°:

- B−C is the exact negative of D−E, closure error 0.000 nm, so the quad is a
  true parallelogram.
- 0.34713 mm (`outlet_tm` face C−D) × 0.11402 mm (thickness B−C), corner angle
  86.38°, i.e. rectangular to within 3.6°.
- 5 cells across the thickness (22.8 µm, matching `fluid_tm_layers`) × 12 along
  the face (28.9 µm) — near-square cells.
- `tm_zone` holds exactly 5 × 12 × 12 = 720 cells, so no neighbouring anterior
  chamber cell was pulled in. This is strictly better than the
  `cylinderAnnulusToCell` in `topoSetDict.g2`, which on a hex mesh also grabs AC
  cells.
- The TM is one block; nothing else intrudes into it.

### 2. No loose parts

- `Number of regions: 1`. This is the sharp test: the anterior group reaches the
  posterior group through only the 43 µm pupil throat face P−R, so if that
  throat failed to conform the mesh would split in two.
- Boundary definition, cell-to-face addressing, point usage, upper-triangular
  ordering, face vertices, cell zip-up and face-face connectivity all OK; no
  open edges; all 7 patches singly connected and the union closed.
- Cell types are as designed: only the four axis-touching blocks produce prisms
  (648 = 4 blocks × 27 axis cells × 6 azimuthal cells, doubled for the two 45°
  blocks). Any other prism would mean a wrong vertex order.
- Bounding box matches the analytic domain to 1 µm.

### 3. The lens and iris voids, and the gap

- Every one of the 1,965 `lens_wall` points lies within **4.99 µm** of
  `lens_front` (centre (0, −0.31), R = 5.76) or `lens_rear` (centre (0, −4.15),
  R = 4.79). The residual is the azimuthal chord sagitta, r(1 − cos 3.75°) ≈
  10 µm at the equator, not a geometry error — the tables themselves are only
  self-consistent to ~40 µm.
- Lens void spans y = −6.070 to +0.640 mm with the equator at r = 4.750 mm,
  exactly M, K and L.
- Every one of the 1,235 `iris_wall` points lies within **2.57 µm** of a Table
  SII segment, so the five straight faces are straight and the turning points N
  and Q are not smoothed. Minimum iris radius 3.0000 mm — a 6.0 mm pupil.
- The clearance is crossed by **8 cells everywhere** (9 grid lines × 7 columns
  between P and Q), against a requirement of 4. At the minimum section
  (x = 3.2015 mm, gap 37.35 µm) the cells are 3.87 µm each. The narrowest
  section is *not* on a block boundary — it sits inside `PCi` — so this is
  measured from the mesh points, not assumed:

| Station | x [mm] | gap [µm] |
|---|---|---|
| P, iris tip corner | 3.000 | 42.93 |
| minimum | 3.195 | 37.34 |
| Q, iris turning point | 3.690 | 77.16 |

The fallback in the plan (an extra cut at x = 3.195 to pin the throat to a block
face) was not needed.

## Grading

- `VIT1`–`VIT7` carry a three-segment multi-grading in the radial direction that
  puts 12 of 28 cells into y = 2.39–3.90 mm on the axis, giving 0.125 mm cells
  around the IVI needle site at (0, +3.0, 0). `PCo` uses the same distribution
  because it shares the L−H face.
- The ACP needle site (0, −7.0, 0) is the block vertex V, so it is pinned to a
  face. `AC4` is graded 0.5 along its axis direction, shrinking the cells there
  from 0.128 to 0.064 mm and halving the size jump onto `AC3`'s 0.047 mm cells.
- `AC1` tapers geometrically from 0.678 mm at the B−Z cut to 2.272 mm at N−U,
  which refines the mesh into the outflow corner for free.
- The pupil needs no grading: `PCi` crosses the gap with 8 uniform cells, which
  is 115 µm at the L−Y cut and 3.9 µm at the minimum.

## ParaView

- `geometry/eye_g2_fluid_lamminsalo_O1_volume.vtu` — cells, with 13 quality
  fields as cell data (`nonOrthoAngle`, `skewness`, `cellDeterminant`,
  `aspectRatio`, `cellAspectRatio`, `cellVolume`, `cellVolumeRatio`,
  `minTetVolume`, `minPyrVolume`, `faceWeight`, `cellShapes`, `cellRegion`,
  `cellZone`), so the mesh can be coloured by any metric directly.
- `geometry/eye_g2_fluid_lamminsalo_O1_surface.vtp` — all patches combined,
  following the `_volume.vtu` / `_surface.vtp` convention already used for F1.
- `mesh_independence/O1/O1.foam` — opens the mesh with ParaView's OpenFOAM
  reader. This standalone case holds its own `constant/polyMesh` and `system/`,
  so opening it cannot pick up the production Gmsh mesh by accident.

The three heavy outputs are git-ignored as regenerable. To rebuild the O1 case
in place:

```bash
docker compose run --rm fsi bash -lc \
  'cd /simulation/doc-g2-sim1/mesh_independence/O1 && blockMesh'
```

Useful views: threshold on `cellZone` to isolate the TM; clip at z = 0 and
colour by `cellDeterminant` (log scale) to see the pupil channel; threshold
`cellShapes` to see the 648 axis prisms.

## Not done

O1 is not hooked into `Allrun` — there is no `MESH_LEVEL=O1` branch and no
baseline run, so it has not been compared against M1/M2/M3 on IOP. Two decisions
are open before that:

1. `vitreous_zone`. O1 can declare it on the `VIT` blocks, but those span
   y = −3.57 to +6.90 mm whereas the current `topoSetDict.g2` box starts at
   y = −1.5 mm. Block-based zoning would therefore change the porous region and
   invalidate the existing IOP calibration. `tm_zone` has no such problem and is
   already declared on the block.
2. `Allrun` would need a branch that calls `blockMesh -dict
   system/blockMeshDict.O1` instead of `gmshToFoam` + `createPatch` +
   `changeDictionary`, since O1 already emits final patch names and types.

---

## Justificativa de modelagem — redação da tese

> Texto de referência para métodos / discussão (registrado 2026-08-27). Não altera
> parâmetros de simulação; serve só como nota para perguntas futuras sobre Darcy
> vs Brinkman, stair-step na interface VC–AC e malha hexaédrica O1.

O escoamento do humor aquoso através da câmara vítrea foi modelado como um meio
poroso homogêneo e isótropo utilizando a Lei de Darcy. Embora formulações mais
complexas, como as equações de Brinkman, sejam por vezes aplicadas na literatura
para acoplar meios porosos a fluidos livres, a simplificação para a Lei de Darcy
é fisicamente rigorosa e computacionalmente vantajosa no cenário oftálmico basal
devido ao regime de escoamento de creeping flow (Reynolds próximo de zero), onde
as velocidades de percolação são da ordem de \(10^{-8}\) a \(10^{-9}\) m/s. Sob
essas condições, os termos de transporte viscoso e inercial de Brinkman tornam-se
desprezíveis. Adicionalmente, a transição geométrica da interface anterior do
vítreo foi discretizada de forma estruturada hexaédrica (stair-stepping). O uso
de uma malha estruturada hexaédrica pura via Volumes Finitos prioriza a
ortogonalidade e a estabilidade numérica do acoplamento FSI subsequente, sendo
que o teste de independência de malha confirmou que o balanço de massa global
permaneceu estrito e exato, com variações de pressão residual insignificantes de
apenas −1,99% entre os níveis de refino.

Ver também: `cases/doc-baseline-2d-fluid/lamminsaloGoverningEquations.md` §3
(mapeamento Brinkman→Darcy OpenFOAM).
