# doc-baseline-o3-patch-fluid

Baseline-only G2 fluid case locked to **MESH_LEVEL=O3** (blockMesh, **1.3×** O1 divisions — finer bracket).
**Model B** — IVI+ACP as **patch** tips.
Same porous settings as O1 baseline redo.

Steady `simpleFoam` (`endTime` 1000 cap); stops early when `residualControl` hits `p < 1e-4, U < 1e-5`.

## Run

```bash
docker compose run --rm --user ubuntu fsi bash -lc \
  'cd /simulation/doc-baseline-o3-patch-fluid && ./Allrun'
```

## Mesh only (no solve)

```bash
docker compose run --rm --user ubuntu fsi bash -lc \
  'cd /simulation/doc-baseline-o3-patch-fluid && SKIP_SOLVE=1 ./Allrun'
```

## ParaView

`fluid/O3.foam`
