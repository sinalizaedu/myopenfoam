# Mesh independence — doc-g2-sim4 (IVI + ACP)

## Níveis (M5 grossa → M3 fina)

| Level | Papel | lc bulk | lc_fine | lc_tm | n_θ | ~elems Gmsh |
|-------|-------|--------:|--------:|------:|----:|------------:|
| **M5** | mais grossa | 2.0 µm | 550 nm | 220 nm | 4 | 152k |
| **M4** | grossa | 1.4 µm | 400 nm | 150 nm | 5 | 190k |
| **M1** | referência (legado) | 1.0 µm | 300 nm | 120 nm | 6 | 238k |
| **N1** | M7 adaptativa, scout (~20 min, dt=0.02 NP=4) | 1.70 µm | 400 nm | 180 nm | 3 | ~48k |
| **N2** | entre N1 e M8 (template M8: local TM/íris/pontas) | 1.25 µm | 300 nm | 120 nm | 3 | ~68k |
| **M8** | M7 adaptativa + bulk mais grosso (mesmo refinamento local) | 1.38 µm | 300 nm | 120 nm | 3 | ~68k |
| **M7** | adaptativa (M1 local + bulk grosso y±z−) | 1.25 µm | 300 nm | 120 nm | 3 | ~80k |
| **M2** | fina | 700 nm | 220 nm | 85 nm | 8 | 474k |
| **M3** | mais fina | 500 nm | 160 nm | 60 nm | 10 | 731k |

Malhas bulk em `cases/doc-g2-sim1/geometry/` (symlinks em `doc-g2-sim4/geometry/`).

## Gerar malhas

```bash
cases/doc-g2-sim4/scripts/gen_meshes_m1_m5.sh
```

## Rodar estudo completo (Docker)

```bash
cd cases/doc-g2-sim4
./scripts/run_mesh_independence.sh
# ou um subconjunto:
LEVELS=M1,M2,M3 ./scripts/run_mesh_independence.sh
```

Cada nível: `MODE=baseline` (simpleFoam) → `MODE=experiment REUSE_MESH=1` (pimpleFoam, IVI 5–11 s + ACP 15–21 s, t=30 s).

**Estabilidade:** se o experimento divergir (NaN / continuidade), o script retenta com:
`dt=0.05` → `dt=0.05 + Co≤1` → `dt=0.02/0.01 adaptativo` → `dt=0.005/0.001` fixo.

Saídas:
- `mesh_independence/results.csv`
- `mesh_independence/REPORT.md`
- `mesh_independence/{M5..M3}_baseline.log` / `_experiment.log`

## Métricas

- IOP₀ AC / vitreous (baseline)
- Pico IVI AC / vitreous (5–11 s)
- Mínimo ACP AC / vitreous (15–21 s)
- nCells, ivi_tip_cells, acp_tip_cells
- GCI nos pares M5→M4→M1 (grosso) e M1→M2→M3 (fino)

**Malha recomendada:** **N1** scout (~48k); **N2** ≈ M8 (~68k, acoplamento CA/vítreo); **M7** se precisar do bulk um pouco mais fino.
Use M1/M2/M3 para GCI formal; M5/M4 como limite grosso.
