# fea-sim — O1/B2 corneoscleral coat (CalculiX)

Anatomical six-zone Lamminsalo solid (B2 mesh), Neo-Hooke from
`mechanicalProperties`. Living IOP = **15 mmHg**. `outer` is traction-free.

If Step 2 diverges, `Allrun` reruns `fea-sim_frozen.inp` (iris clamped).
If that also dies, stop: the study is the sphere + thin-shell analytic
(~17 mmHg sphere, ~19 mmHg B2 equatorial). Do not invent a number from a
crashed `.sta`.

**This run:** free iris diverged in Step 1 (iris \(E=4\,\mathrm{kPa}\)).
Frozen iris then died (`increment size smaller than minimum`). See
`results/status.txt` = `frozen_failed`. QoI is the sphere curve in
`../fea-simplf` plus the 17/19 mmHg analytic bounds.

```bash
docker compose run --rm fsi bash -lc 'cd /simulation/fea-sim && ./Allrun'
```

Mesh is converted from
`cases/fsi-transient-o1-patch/solid_meshes/B2` (no remesh).
