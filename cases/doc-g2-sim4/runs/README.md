# Per-mesh run archives

Each mesh level gets its own OpenFOAM case snapshot so ParaView
does not lose results when the next mesh overwrites `fluid/`.

```
runs/
  O1/
    O1.foam      ← open this in ParaView
    constant/
    0/ 2/ … 30/
  F1/
    F1.foam
    …
```

Archive with:

```bash
./scripts/archive_mesh_run.sh O1
./scripts/archive_mesh_run.sh F1
```

The overnight batch calls this after each experiment.
