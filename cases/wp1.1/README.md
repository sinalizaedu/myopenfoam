# wp1.1 — verificação FEA casca esférica fina (CalculiX)

Verificação de código: compara `K_FEA = ΔP/ΔV` contra a fórmula de membrana

`K = t·E / (2·π·R⁴·(1−ν))`

para globo ocular pressurizado (humano e coelho). **Alinhado ao relatório (`wp1.tex`): octante esférico.**

```bash
cd cases/wp1.1 && ./Allrun

# só repost-processar .frd já existentes (sem CCX):
python3 scripts/reprocess_octant.py

# estudo esfera completa (legado / malha ne=12, não é o do PDF):
python3 scripts/run_verification.py

# container FSI:
docker compose run --rm fsi bash -lc 'cd /simulation/wp1.1 && ./Allrun'
```

## Casos

| espécie | R (mm) | t (mm) | E (MPa) | ν |
|---|---:|---:|---:|---:|
| humano | 12.0 | 0.5 | 3.0 | 0.47 |
| coelho | 7.6 | 0.33 | 3.0 | 0.47 |

## Modelo (relatório)

- **Octante** esférico (θ, φ) com simetria em x=0, y=0, z=0 (`SYM_X/Y/Z`)
- Malha de referência: **ne = 6** divisões por face → **288 elementos equivalentes** na esfera completa (8×ne²)
- Elementos **S8R**, θ_min = 3°, `NLGEOM=NO`
- Carga: ΔP = 1 mmHg na superfície interna; ΔV no octante × **8**
- Pós-processamento: KDTree R±t/2 + média (superfície média)

Valores de referência do PDF @ 288 elem.: humano **K = 0,163338**, erro **+0,25%**; coelho **K = 0,670183**, erro **+0,27%**.

## Entregáveis

| arquivo | conteúdo |
|---|---|
| `ccx/human_wp1.1.inp` | deck humano (octante ne=6, copiado do run) |
| `ccx/rabbit_wp1.1.inp` | deck coelho (octante ne=6) |
| `output_octant/summary.json` | convergência + linearidade |
| `output_octant/RESULTS_human.md` | tabelas por espécie |
| `output_wp1.1/RESULTS.md` | resumo estilo relatório |
| `output_wp1.1/verify_wp1_octant_report.json` | checagem vs wp1.tex |

## Critério de sucesso

`|K_FEA − K_analítico| / K_analítico < 2%` @ malha de referência (288 elem. equiv.).

## Diagnóstico u_r

Ver `DIAGNOSTIC_ur_extraction.md` — scatter nodal de u·r̂ não invalida K obtido por ∫ u·n dA.
