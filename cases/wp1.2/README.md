# wp1.2 — ajuste hiperelástico inverso (CalculiX)

Ajusta parâmetros **Yeoh** (2–3) ou **Ogden** (N=1 ou N=2) a uma curva **P(V)** experimental
(Ensaio A, ramo de infusão) de olho suíno ex vivo, usando FEA inversa com casca esférica
(reaproveita malha e CB de `cases/wp1.1`).

**Não é validação anatômica 3D** — isso fica para wp1.4/1.5.

## Entrada

CSV com colunas `V_uL`, `P_mmHg` (e opcionalmente `eye_id`):

- `V_uL`: volume infundido **acima do basal** (referência **V=0 @ P=15 mmHg**).
- Apenas ramo de **carregamento** (infusão); não misturar deflação.
- Um ajuste por olho (`--eye-id`).

Geometria **R** (raio equivalente) e **t** (espessura escleral): preferir valores pós-dissecção
do mesmo olho. Se ausentes, declarar fonte (ver `--geom-source`).

### Referência suíno (somente se não houver dissecção)

| parâmetro | valor | fonte | confiança |
|---|---:|---|---|
| R | 9.0 mm | volume ocular ~3 mL → esfera equivalente | estimativa |
| t | 0.45 mm | faixa literature porcine sclera | estimativa |

Substitua assim que tiver medidas do Ensaio A.

## Modelos (ordem automática)

1. **Yeoh 2 parâmetros** (C10, C20) — D1 fixo por ν=0.47
2. **Yeoh 3** — só se R² < 0,98
3. **Ogden N=1** (µ, α)
4. **Ogden N=2** — só se N=1 insuficiente

## Execução

```bash
cd cases/wp1.2 && ./Allrun

# ou no container FSI (CalculiX ccx_preCICE):
docker compose run --rm fsi bash -lc 'cd /simulation/wp1.2 && ./Allrun'
```

Matriz principal (relatório WP1.2, 3 alvos × Ogden/Yeoh):

```bash
cd cases/wp1.2 && ./Allrun_literature_p50
# Yeoh: C10∈[1e-4,5] MPa, C20∈[0.1,10³] MPa via log10(C20) — yeoh_fit_bounds.py / fit_yeoh2
# Env: TARGETS, MATERIALS, OUT (honrados por run_literature_matrix.py)
```

Com seus dados:

```bash
python3 scripts/fit_hyperelastic.py \
  --data data/meu_ensaio_A.csv \
  --eye-id pig01 \
  --R 9.2 --t 0.43 \
  --geom-source "dissecção pós-teste olho pig01" \
  --out output_wp1.2
```

## Saídas (`output_wp1.2/`)

| arquivo | conteúdo |
|---|---|
| `fit_results.json` | parâmetros, R², resíduos, dP/dV basal e pico |
| `pv_overlay.csv` | dados para plot experimental vs FEA |
| `pv_fit.png` | gráfico sobreposto |
| `RESULTS.md` | resumo legível |

## Critério

- R² e resíduo máximo reportados em todos os casos.
- dP/dV @ V=0 e no pico da curva [mmHg/µL] — comparável ao K linear (wp0/wp1.1) e Kf de Friedenwald.
- Sem pré-tensionamento extra (wp1.3).
