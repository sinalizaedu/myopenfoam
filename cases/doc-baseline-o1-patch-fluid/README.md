# doc-baseline-o1-patch-fluid

Baseline-only G2 fluid case locked to **MESH_LEVEL=O1** (blockMesh).
**Model B** — IVI+ACP as **patch** tips.
New vitreous porous (`ymin=-3.60 mm`, `d_vit=1.724e13`).
`d_TM = 1.645058e+15` (≈15.2 mmHg, porous redo).

Steady `simpleFoam` (`endTime` 1000 cap); stops early when `residualControl` hits `p < 1e-4, U < 1e-5`.

## Run

```bash
docker compose run --rm --user ubuntu fsi bash -lc \
  'cd /simulation/doc-baseline-o1-patch-fluid && ./Allrun'
```

## ParaView

`fluid/O1.foam`
