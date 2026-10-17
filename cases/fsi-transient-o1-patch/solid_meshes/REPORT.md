# O1 solid mesh study (A1–E1, A2–E2)

Production reference `solid/`: **33408** cells.

## v1 (baseline)

| mesh | cells | neg. vol | open | max non-ortho | fsi_active | conformal vs wall |
|------|------:|---------:|-----:|--------------:|-----------:|-------------------|
| A1 | 8640 | 0 | 0 | 30.3 | 2160 | ERR i_lens patch) [FAIL] wall <-> fsi_active: 2184 != 2160 faces [PASS] Lamminsalo coupled surfaces: max point error 7.57 um [PASS] posterior band offsets: 0.100/0.200/0.330 mm O1 FSI verification FAILED  |
| B1 | 33408 | 0 | 288 | 156.0 | 2184 | PASS 5.001e-07 |
| C1 | 166886 | 0 | 0 | 73.7 | 24793 | ERR lens patch) [FAIL] wall <-> fsi_active: 2184 != 24793 faces [FAIL] Lamminsalo coupled surfaces: max point error 41.89 um [PASS] posterior band offsets: 0.100/0.200/0.330 mm O1 FSI verification FAILED  |
| D1 | 33408 | 0 | 288 | 156.0 | 2264 | ERR 2264 faces [FAIL] lens_wall <-> fsi_lens: 1824 != 64 faces [FAIL] Lamminsalo coupled surfaces: max point error 589.72 um [PASS] posterior band offsets: 0.100/0.200/0.330 mm O1 FSI verification FAILED  |
| E1 | 33408 | 0 | 288 | 156.0 | 2184 | PASS 5.001e-07 |

## v2 (dense + mixed elements, geometry ≥ production)

| mesh | cells | neg. vol | open | max non-ortho | fsi_active | cell mix | conformal |
|------|------:|---------:|-----:|--------------:|-----------:|----------|-----------|
| A2 | 83592 | 0 | 720 | 90.0 | 2324 | 3600 prism | ERR 324 faces [FAIL] lens_wall <-> fsi_lens: 1824 != 130 faces [FAIL] Lamminsalo coupled surfaces: max point error 589.72 um [PASS] posterior band offsets: 0.100/0.200/0.330 mm O1 FSI verification FAILED  |
| B2 | 40896 | 0 | 360 | 151.4 | 2184 | 360 prism | PASS 5.001e-07 |
| C2 | 422635 | 0 | 0 | 74.8 | 60576 | 17785 prism | ERR lens patch) [FAIL] wall <-> fsi_active: 2184 != 60576 faces [FAIL] Lamminsalo coupled surfaces: max point error 25.14 um [PASS] posterior band offsets: 0.100/0.200/0.330 mm O1 FSI verification FAILED  |
| D2 | 83592 | 0 | 720 | 90.0 | 2324 | 3600 prism | ERR 324 faces [FAIL] lens_wall <-> fsi_lens: 1824 != 130 faces [FAIL] Lamminsalo coupled surfaces: max point error 589.72 um [PASS] posterior band offsets: 0.100/0.200/0.330 mm O1 FSI verification FAILED  |
| E2 | 40896 | 0 | 360 | 151.4 | 2184 | 360 prism | PASS 5.001e-07 |

### v2 pipelines

- **A2** Full Lamminsalo Gmsh 3D (H1 limbus): 2× radial, θ=12, limbus quads→prisms. **Not** coat extrusion.
- **B2** H1 structured `blockMesh`, layers 5/5/5/5 (hex wedge).
- **C2** Aggressive `snappyHexMesh` level (3 4), 6 prism-like wedge layers.
- **D2** Fine Gmsh revolve (H1, 2× radial, limbus prisms).
- **E2** `mergeMeshes` + `splitMeshRegions` of fluid + B2.

Build: `MESH=B2 ./Allmesh` or `MESH=v2 ./Allmesh` for all v2 meshes.
FSI hook: `MESH=B2 MODE=fsi ./Allrun` copies `solid_meshes/$MESH`.
