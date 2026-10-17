# doc-transient-o1-patch-fluid

Passive **pimpleFoam** baseline locked to **MESH_LEVEL=O1** (blockMesh).
**Model B** — IVI+ACP as **patch** tips (`subsetMesh`), both **off**.

Ciliary `ac_inlet` stays at `1.25e-11 m³/s`. `ivi_tip` / `acp_tip` are `noSlip`.
`dt = 0.05 s`, `endTime = 1 s` (pressure plateaus by ~0.5 s). Equilibrated fields live in `fluid/1`.

Seeded mesh from [`doc-baseline-o1-patch-fluid`](../doc-baseline-o1-patch-fluid/).
Steady `simpleFoam` `d_TM = 1.645058e+15` gives **13.30 mmHg** on this pimpleFoam baseline, not 15.20.
Calibrated pimpleFoam: **`d_TM = 2.489000e+15` → IOP_AC = 14.999 mmHg** (Q_TM matches 1.25e-11 m³/s, IVI=ACP=0).

## Run

```bash
docker compose run --rm --user ubuntu fsi bash -lc \
  'cd /simulation/doc-transient-o1-patch-fluid && ./Allrun'
```

Calibrate:

```bash
docker compose run --rm --user ubuntu fsi bash -lc \
  'cd /simulation/doc-transient-o1-patch-fluid && python3 scripts/calibrate_d_tm.py --mesh O1'
```

## Sister cases

- [`doc-transient-o1-volume-fluid`](../doc-transient-o1-volume-fluid/) — Model C, volumetric IVI/ACP sources off
- [`doc-transient-f1-volume-fluid`](../doc-transient-f1-volume-fluid/) — F1 Fluent mesh, volumetric sources off
