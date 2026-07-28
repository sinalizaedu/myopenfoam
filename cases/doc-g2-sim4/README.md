# doc-g2-sim4 — G2 Simulação 4 (IVI + ACP combinado)

| Case | Role |
|------|------|
| [`doc-g2-sim3`](../doc-g2-sim3/) | Sim 3 — ACP only |
| **`doc-g2-sim4`** | Sim 4 — IVI then ACP + Robin |

## Protocol

| Phase | Time [s] | ivi_tip | acp_tip | wall (Robin) |
|-------|----------|---------|---------|--------------|
| Baseline | 0–5 | off | off | 0 |
| IVI | 5–11 | +Q/4 | off | −Q |
| Gap | 11–15 | off | off | 0 |
| ACP | 15–21 | off | −Q/4 | +Q |
| Recovery | 21–30 | off | off | 0 |

`Q = 2.08325×10⁻⁹ m³/s` (50 µL/6 s ÷ 4).

## Tips

- **IVI:** `(0, 3.0, −0.40) mm` mid-vitreous — [`figures/g2_fluid_ivi_acp.png`](figures/g2_fluid_ivi_acp.png)
- **ACP:** `(0, −7.0, 0.40) mm` in AC on optical axis

## How to run

```bash
cd cases/doc-g2-sim4
MODE=baseline MESH_LEVEL=M1 ./Allrun
MODE=experiment MESH_LEVEL=M1 REUSE_MESH=1 ./Allrun
```

Docker:

```bash
docker compose run --rm --user ubuntu fsi bash -lc \
  'cd /simulation/doc-g2-sim4 && MODE=baseline MESH_LEVEL=M1 ./Allrun'
```

## IOP calibration

Same as Sim 2/3: **`d_TM`** in `fvOptions`, **`outlet_tm` = P_TM = 10 Torr**. Experiment init from baseline `p`/`U` without pressure shift.

## Production results (2026-07-22)

Archived under `results/`:

| Phase | Peak / min IOP (AC / vit) | Time | Recovery @ t=30 |
|-------|---------------------------|------|-----------------|
| IVI (5–11 s) | **25.00 / 56.22** mmHg | ~5.5 s | — |
| ACP (15–21 s) | **4.67 / 10.46** mmHg (min) | 15.6 s | **14.675** mmHg |

Figure: `figures/iop_ivi_acp_onaxis.png`

Steady baseline (simpleFoam): **15.004 mmHg**. Transient repouso @ t=0.1 s: **14.681 mmHg**.
