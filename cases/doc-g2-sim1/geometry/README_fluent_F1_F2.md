# Fluent fluid meshes (F1 / F2)

| Level | Source | File | Status |
|-------|--------|------|--------|
| **F1** | ANSYS `meshfile2.msh` | `eye_g2_fluid_fluent_F1.msh` | in repo (855k tets, 3D 90° sector) |
| **F2** | finer 3D fluid-only export | `eye_g2_fluid_fluent_F2.msh` | **add before running F2 baselines** |

`meshfile.msh` (2D axisymmetric full eye with solids) is **not** F2 — different dimension and zones.

Import pipeline (same as F1):

```bash
# copy export from ~/Documents/Doutorado/Profile/Mesh/ → eye_g2_fluid_fluent_F2.msh
docker compose run --rm --user ubuntu fsi bash -lc \
  'cd /simulation/doc-baseline-f2-patch-fluid && SKIP_SOLVE=1 ./Allrun'
```

ParaView VTK convention (optional, regenerate after import):

- `eye_g2_fluid_fluent_F1_surface.vtp` / `_volume.vtu` — done for F1
- `eye_g2_fluid_fluent_F2_surface.vtp` / `_volume.vtu` — create after F2 polyMesh exists

System dicts: `T1: Volume vs Patch/doc-g2-sim5/fluid/system/topoSetDict.F{1,2}`, `createPatchDict.F{1,2}`, `topoSetDict.F{1,2}zones`.
