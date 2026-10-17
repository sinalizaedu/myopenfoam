# WP4 — Perfusão ocular pós-IVI (plano de tese)

## Item 4.1 — Cadeia IOP(t) → OPP(t)

Módulo: **`opp_perfusion.py`**

Entrada típica: vetores `t` (min) e `IOP(t)` (mmHg) produzidos por
`cases/wp0/goldmann_iop_solver.py` (`simulate()`). Este WP **não** altera o solver 0D.

### Fórmulas

**Pressão arterial média (MAP, braquial)**

\[
\mathrm{MAP} = \mathrm{PAD} + \frac{1}{3}(\mathrm{PAS} - \mathrm{PAD})
\]

**MOPP (mean ocular perfusion pressure)**

\[
\mathrm{MOPP}(t) = f_{\mathrm{braq\text{-}oft}} \cdot \mathrm{MAP} - \mathrm{IOP}(t)
\]

- `fator_braquial_oftalmica` (padrão **2/3**) escala a MAP braquial para a
  pressão efetiva na circulação ocular posterior.
- Esse fator é **convenção clínica/literária**, não uma medida direta por paciente.
  Para sensibilidade, varrer **0,5–0,8** (função `mopp(..., fator_braquial_oftalmica=...)`).

**OPP diastólica**

\[
\mathrm{OPP}_{\mathrm{diast}}(t) = \mathrm{PAD}_{\mathrm{oftálmica}} - \mathrm{IOP}(t)
\]

Na função `aplicar_cadeia`, quando não se informa PAD oftálmica separada, usa-se
\(\mathrm{PAD}_{\mathrm{oftálmica}} = f_{\mathrm{braq\text{-}oft}} \cdot \mathrm{PAD}\).

**Limiar efetivo (reserva vascular)**

\[
\mathrm{OPP}_{\mathrm{crit,efetivo}} = \mathrm{OPP}_{\mathrm{crit,ref}} \cdot \phi_{\mathrm{vasc}}
\]

- \(\phi_{\mathrm{vasc}} \ge 1\): **1,0** = sem comorbidade vascular extra;
  **> 1** = menor reserva (obstrução carotídea, diabetes avançada, etc.).
- Motivação clínica: Damasceno et al. (2022) — alta fração de CRAO transitória
  pós-IVI com estenose carotídea relevante.

**Limiares temporais de IOP (item 4.1)**

`aplicar_cadeia` reporta minutos com \(\mathrm{IOP}(t) > 30\), \(> 40\), \(> 50\) mmHg
(`T_acima_30`, `T_acima_40`, `T_acima_50`), por integração trapezoidal do indicador.

Também: `opp_minima_atingida` = \(\min_t \mathrm{MOPP}(t)\) (pior perfusão média no episódio).

### Pipeline oficial WP4.1 / WP4.2 numérico

- **`run_wp41.py`** — `protocolo_referencia()` = `protocol_humano_relatorio(..., par_enabled=False)`:
  refluxo **instantâneo** ($\Delta V\approx1{,}19$ µL), IVI $50$ µL / $6$ s, **sem paracentese** (igual ao humano de referência do WP0).
- **`sensibilidade_wp42.py`** e **`verifica_wp4.py`** usam o mesmo `protocolo_referencia()`.

### Item 4.6 — Paracentese (três estratégias WP0)

Módulo: **`run_wp46_paracentese.py`**

Repete MOPP mínima, tempos abaixo de 30/40 mmHg e $\mathcal{I}_{\mathrm{evt}}$ (Friedenwald, 120/80) para sem par, profilática ($-30$ s), reativa ($+30$ s) e tardia ($+2$ min), via `simulate_wp0_timeline` (mesmos instantes do WP0).

```bash
cases/wp0/.venv/bin/python cases/wp4/run_wp46_paracentese.py
```

Saída: `output_wp46/wp46_paracentese.json`.

### Uso rápido

```python
from pathlib import Path
import sys
sys.path.insert(0, "cases/wp0")
sys.path.insert(0, "cases/wp4")

from goldmann_iop_solver import FriedenwaldPV, simulate
from opp_perfusion import aplicar_cadeia
from run_wp41 import protocolo_referencia

pv = FriedenwaldPV(Kf_per_uL=0.0126, P0_mmHg=15.0)
proto = protocolo_referencia()
t, V, iop = simulate(proto, pv)

out = aplicar_cadeia(t, iop, pas=120, pad=70, opp_crit_ref=50.0)
print(out["T_acima_40"], out["opp_minima_atingida"])
```

### Convenções MOPP vs OPP diastólica

| Métrica | Papel |
|--------|--------|
| **MOPP** | Proxy usual de perfusão **média** na retina posterior; alinha com WP0 e literatura de CRAO pós-IVI. |
| **OPP diastólica** | Enfatiza o **vale** hemodinâmico (sistole longa / hipotensão); útil como eixo complementar. |

### Parâmetro de sensibilidade (importante)

> **OPP_crit deve sempre ser tratado como parâmetro de sensibilidade, nunca como
> valor fixo — ver Seção 4.2 do plano de tese.**

O item **4.1** entrega somente a cadeia IOP → OPP e os tempos acima de
30/40/50 mmHg de IOP. Os itens seguintes constroem sobre ele.

---

## Item 4.2 — Dose isquêmica por evento (𝓘)

Módulo: **`dose_isquemica.py`**

\[
\mathcal{I} = \int \max\big(0,\ \mathrm{OPP}_{crit} - \mathrm{OPP}(t)\big)\,dt \quad [\mathrm{mmHg\cdot min}]
\]

- `dose_isquemica(t, OPP_t, OPP_crit)` — generalizada (MOPP ou OPP_diast).
- `dose_isquemica_da_cadeia(t, chain)` — 𝓘 nas duas vias a partir de `aplicar_cadeia` (4.1).
- `curva_sensibilidade_opp_crit` — 𝓘(OPP_crit) em faixa, nunca um número só.
- `derivar_P0_equilibrio` / `protocolo_com_P0_literatura(especie)` — P0 **derivado**
  dos 4 parâmetros de vazão (humano 16,86; coelho anestesiado 26,68 mmHg), corrigindo
  o drift dos defaults do WP0 (P0=15 com Q_prod=3,0 → equilíbrio real ~18,57 mmHg).
- `delta_V_bolus_fechada(proto)` — ΔV líquido (V_inj − refluxo instantâneo WP0).
- `validacao_fechada_H6(proto, pv, OPP_crit_ref)` — 𝓘 numérico vs fórmula fechada
  (K constante, sem paracentese; mesmo ΔV líquido). Erro medido: **≈0,3%** no protocolo
  WP4.1 com refluxo (residual da rampa de 6 s vs bólus).

## Item 4.3 — H6 teórico em primitivos

Módulo: **`h6_teorico.py`**

\[
\mathcal{I} = \frac{\Delta V}{C} - \frac{dP_{th}}{C\,K}\left[1 + \ln\frac{K\,\Delta V}{dP_{th}}\right]
\ \ (K\Delta V > dP_{th});\qquad
\mathcal{I} = 0\ \ (K\Delta V \le dP_{th});\qquad
K_{crit} = \frac{dP_{th}}{\Delta V}
\]

Verificação numérica no cenário do plano (dPth=15 mmHg, ΔV_eff≈48,81 µL pós-refluxo WP0, C=0,28):

- **ΔV_eff/C ≈ 174,3 mmHg·min** (limite superior assintótico, K→∞ — Consequência 1)
- **K_crit ≈ 0,307 mmHg/µL** (Consequência 2 — abaixo, 𝓘 = 0 exatamente)

| K [mmHg/µL] | 0,05 | 0,10 | 0,20 | 0,30 | 0,31 | 0,40 | 0,60 | 1,00 | 3,00 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **𝓘 [mmHg·min]** | 0 | 0 | 0 | 0 | 0,007 | 5,09 | 25,30 | 57,54 | ~115 |

Consequência 3 verificada: I(C=0,14) / I(C=0,28) = **2,000000** (exato, qualquer K).
Consistência com `validacao_fechada_H6` (4.2): idêntico a < 10⁻⁹ (duas escritas da
mesma fórmula). `curva_I_vs_dPth` / `K_crit_vs_dPth` marcam `None` para dPth ≤ 0.

> **Alerta metodológico (plano, literal):** "todo o resultado depende do valor de
> dPth, que é justamente o parâmetro mais mal conhecido do modelo... Apresente 𝓘 e
> K_crit como função de dPth, nunca com um valor fixo." Nenhuma função pública do
> módulo tem dPth hardcoded.

## Item 4.4 — Validação contra o zero observado

Módulo: **`validacao_zero_observado.py`** (inteiramente computacional).

**Peça 1 — OCT-A 2026 (n=54):** pico 14→31 mmHg, MOPP≈31 mmHg durante o evento,
sem déficit mensurável. K implícito do pico = **0,34 mmHg/µL**. O modelo prediz
zero sse OPP_crit ≤ MOPP_min observado:

| OPP_crit [mmHg] | 15 | 20 | 25 | 30 | **31** | 35 | 40 | 45 | 50 |
|---:|---|---|---|---|---|---|---|---|---|
| Previsão | zero | zero | zero | zero | **zero (fronteira)** | déficit>0 | déficit>0 | déficit>0 | déficit>0 |

→ O zero do OCT-A é consistente com o modelo **somente se OPP_crit ≤ 31 mmHg** —
o limiar crônico ~50 mmHg da literatura **não** valeria para eventos transitórios.

**Peça 2 — subgrupo Damasceno et al. 2022** (CRAO transitória: 0,44% = 18/4069;
66,6% com obstrução carotídea ≥70%). Cenário ilustrativo (K_tip=0,34, K_alto=1,0,
ΔV=50, C=0,28, dPth_basal=20, OPP_crit_ref=25, φ_risco=1,3):

| Grupo | dPth | 𝓘 |
|---|---:|---:|
| Típico (φ=1) | 20,0 | **0** (K·ΔV=17 ≤ 20) |
| Risco (φ=1,3) | 12,5 | **72,0 mmHg·min** |

O modelo separa os dois grupos no MESMO cenário basal — consistente com a
associação observada. Se dPth_risco ≤ 0, marca "regime cronico" (não ValueError).

**Peça 3 — controle negativo:** afinamento retiniano de 25% aos 15 min (PMC13307848,
resolvido em 48 h, compressão mecânica) é estruturalmente incompatível com 𝓘 — o
modelo não tem variável de espessura; não pode confundir deformação com isquemia.

## Item 4.5 — Dose acumulada em regime terapêutico (contribuição original)

Módulo: **`dose_cumulativa.py`**

\[
\mathcal{I}_{cum}(N) = \sum_{j=1}^{N} \mathcal{I}_j \cdot w(t_j - t_{j-1}),\qquad
w(\Delta t) = (1-b) + b\,e^{-a\,\Delta t}
\]

Dois limites sempre reportados: **acumulação perfeita** (w=1, I_cum = N·I) e
**recuperação parcial** (modelo SF do rato reinterpretado). **a e b NÃO têm
calibração na literatura** — parâmetros de sensibilidade. Meia-vida de referência
ILUSTRATIVA: **4 semanas** (a = ln2/(4 sem) ≈ 1,72×10⁻⁵ /min), escolhida por estar
na ordem do intervalo mais curto (mensal), onde a diferença entre limites mais importa.

**Os 4 regimes do plano (I por evento = 20 mmHg·min, meia-vida 4 sem, b=1):**

| Regime | N (2 anos) | Intervalo | I_cum perfeita | I_cum parcial |
|---|---:|---:|---:|---:|
| Mensal fixo | 24 | 4 sem | 480,0 | 250,0 |
| Treat-and-extend | 10 | 10 sem (ALTAIR ~10,4/96 sem) | 200,0 | 51,8 |
| Brolucizumabe | 8 | 12 sem | 160,0 | 37,5 |
| Faricimabe | 6 | 16 sem | 120,0 | 26,3 |

**Sensibilidade à meia-vida (mensal fixo, N=24, I=20):**

| Meia-vida | 2 sem | 4 sem | 8 sem | 12 sem |
|---|---:|---:|---:|---:|
| I_cum parcial [mmHg·min] | 135,0 | 250,0 | 345,3 | 385,1 |

A ordem entre regimes (mensal > T&E > brolucizumabe > faricimabe) é preservada nos
dois limites; a recuperação parcial comprime sobretudo os regimes de intervalo longo.

---

### Testes

```bash
cd cases/wp4 && ../wp0/.venv/bin/python -m pytest . -v
```

53 testes (4.1: 7 · 4.2: 11 · 4.3: 10 · 4.4: 11 · 4.5: 14).
