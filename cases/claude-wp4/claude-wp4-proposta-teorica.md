# WP4 — Acoplamento à Perfusão e Dose Isquêmica (proposta revisada, parte teórica)

**Status:** proposta de reestruturação do WP4, escopo teórico apenas. A parte experimental (sub-estudo OCT-A do WP3) fica para uma fase futura e não é detalhada aqui.

**Autoria:** revisão de literatura e análise conduzidas em sessão com Claude (Opus), a partir do plano de tese original (`plano_tese_IOP_IVI__2_.md`).

---

## 1. Por que o WP4 original precisava mudar

O WP4 do plano original tinha três subitens:

- 4.1 Cadeia IOP(t) → OPP(t) → métrica de isquemia
- 4.2 Métrica nova 𝓘 (integral de isquemia para injeção única)
- 4.3 Resultado teórico H6 (derivação de K_crit)

Isso é elegante como teoria, mas curto demais para sustentar um capítulo de doutorado, por três razões:

1. **O resultado principal, para uma injeção típica, é um zero.** A literatura de 2026 (OCT-angiografia, n = 54 olhos) mostra que durante um pico típico de IOP pós-IVI (14 → 31 mmHg) não há déficit de perfusão mensurável. O modelo prevê exatamente isso quando K do paciente está abaixo de K_crit — mas um capítulo cujo resultado central é "não encontramos nada" não sustenta uma tese sozinho, precisa ser reenquadrado como validação, não como conclusão.
2. **Falta uma segunda pergunta que produza um resultado positivo e original.** A evidência que reunimos (ver Seção 2) aponta consistentemente para **dose acumulada ao longo de um regime terapêutico**, não para o evento único, como o lugar onde há sinal real.
3. **Não havia elo de validação.** A métrica 𝓘 era proposta e derivada, mas nunca confrontada com nenhum dado publicado.

## 2. Literatura que fundamenta a mudança (resumo)

| Achado | Fonte | Uso no WP4 |
|---|---|---|
| Sem déficit de perfusão mensurável durante pico típico de IOP (14→31 mmHg, n=54) | OCT-A 2026 | Valida que 𝓘≈0 para injeção única na maioria dos pacientes |
| CRAO transitória em 0,44% das IVIs (18/4069); 66,6% desses casos com obstrução carotídea ≥70% | Damasceno et al. 2022 | Motiva fator de reserva vascular φ_vasc modulando OPP_crit |
| Paracentese: RCT (injeção única) sem efeito no RNFL; observacional (injeções repetidas) sem perda de RNFL | Meta-análise + RCT + Karger | Assinatura indireta de dano cumulativo, não agudo isolado |
| SF = 1 − b(1 − e^{−at}), a=3,2%/dia, b=44%, R²=0,94 | Modelo de IOP crônica em rato | Fornece forma funcional para acumulação/recuperação entre eventos |
| Apoptose retiniana detectável aos 5–10 min a PIO=97 mmHg, sem dano estrutural | Öz et al. 2005 (coelho) | Sustenta a hipótese de dano sub-clínico acumulável |
| Afinamento retiniano de 25% aos 15 min pós-IVI, resolvido em 48h — atribuído a compressão mecânica, não isquemia | OCT ultra-precoce (PMC13307848) | Controle negativo: o modelo não deve confundir compressão com isquemia |
| "Hypotension burden" (AUC de MAP abaixo de limiar) prediz lesão renal aguda em cirurgia | Literatura de anestesiologia | Precedente metodológico direto para a métrica 𝓘 |
| Tolerância retiniana à oclusão completa: 12–15 min (humano, revisão contestando Hayreh) vs 97–105 min (macaco, Hayreh, contestado) vs 20–30 min (coelho, in vitro) vs 5–10 min (coelho, in vivo, apoptose) | Múltiplas fontes | Define a incerteza de ordens de grandeza em OPP_crit/ΔP_th |

## 3. Estrutura teórica proposta para o WP4

### 4.1 — Cadeia de acoplamento IOP → OPP → isquemia

$$\text{IOP}(t) \;\longrightarrow\; \text{OPP}(t) \;\longrightarrow\; \text{métrica de isquemia}$$

$$\text{MOPP} = \tfrac{2}{3}\,\text{MAP} - \text{IOP}, \qquad \text{OPP}_{\text{diast}} = \text{PAD}_{\text{oft}} - \text{IOP}, \qquad \text{MAP} = \text{PAD} + \tfrac{1}{3}(\text{PAS}-\text{PAD})$$

O fator 2/3 é convenção da literatura de glaucoma, não medida direta — análise de sensibilidade obrigatória em 0,5–0,8.

**Adição em relação ao plano original:** incorporar reserva vascular individual como modulador do limiar,

$$\text{OPP}_{\text{crit}} = \text{OPP}_{\text{crit,ref}} \times \phi_{\text{vasc}}$$

com φ_vasc ≥ 1 (φ_vasc = 1 sem comorbidade vascular; φ_vasc > 1 para obstrução carotídea, diabetes avançada etc.), motivado por Damasceno et al. (2022).

### 4.2 — Métrica de dose isquêmica por evento (𝓘)

$$\mathcal{I} = \int_0^{T} \max\!\big(0,\; \text{OPP}_{\text{crit}} - \text{OPP}(t)\big)\,dt \qquad [\text{mmHg·min}]$$

Complementos: T_{>30}, T_{>40}, T_{>50}; OPP mínima.

**Precedente metodológico:** mesma construção do "hypotension burden" da anestesiologia (AUC de MAP < 65 mmHg durante cirurgia, preditor independente de lesão renal aguda). A transposição para o olho é a contribuição — o conceito matemático já existe alhures.

**Tratamento de OPP_crit:** apresentar sempre como superfície de resposta 𝓘(K, OPP_crit), nunca como valor fixo. Âncoras da literatura (nenhuma diretamente aplicável ao pico transitório pós-IVI, mas balizando a faixa):
- Baltimore Eye Survey: DOPP < 30 mmHg → risco 6× (crônico)
- Barbados Eye Study: MOPP < 42 mmHg → risco 3,1× (crônico)
- CRAO completa humana: dano irreversível em 12–15 min (agudo extremo)

### 4.3 — Resultado teórico H6 (mantido do plano original)

$$\mathcal{I} = \frac{\Delta V}{C} - \frac{\Delta P_{\text{th}}}{CK}\Big[1 + \ln\tfrac{K\Delta V}{\Delta P_{\text{th}}}\Big], \qquad K_{\text{crit}} = \frac{\Delta P_{\text{th}}}{\Delta V}$$

Três consequências (integralmente preservadas do plano original):
1. Sem limiar, K cancela — 𝓘 = ΔV/C é o limite superior assintótico.
2. Com limiar, existe K_crit abaixo do qual a dose é exatamente zero — separação quase binária da população.
3. C_out escala tudo linearmente — o glaucomatoso tem 𝓘 proporcionalmente maior em qualquer K.

**Interpretação clínica adicional:** K_crit é a fronteira de intervenção. Pacientes com K < K_crit não precisam de proteção numa injeção isolada; pacientes com K > K_crit entram na zona onde o volume de proteção (paracentese, injeção lenta, redução de ΔV) é quantificável pelo mesmo modelo.

### 4.4 — Validação teórica contra o zero observado

**Objetivo:** mostrar que o modelo reproduz corretamente a ausência de déficit perfusional relatada na literatura para injeção única, e delimitar a região paramétrica onde essa previsão deixaria de valer.

- Confrontar 𝓘 previsto (usando K típico de população, MAP populacional, ΔV = 50 µL) com o resultado nulo do OCT-A 2026 (pico 14→31 mmHg, MOPP ≈ 31 mmHg durante o evento). Determinar se o zero é consistente com OPP_crit < 31 mmHg, ou se a discordância exige revisar a hipótese de que o limiar crônico (~50 mmHg) se aplica a eventos transitórios.
- Simular o subgrupo de risco de Damasceno et al. (K alto, olho curto + φ_vasc elevado por obstrução carotídea) e verificar se o modelo prevê 𝓘 > 0 nesse subgrupo — consistente com a observação de que a reserva vascular modula o risco de CRAO transitória.
- Usar o achado do OCT ultra-precoce (afinamento de 25% aos 15 min, resolução em 48h, atribuído a compressão mecânica) como controle negativo: o modelo não deve atribuir a isquemia o que é efeito mecânico transitório.

Esta etapa é inteiramente computacional (literatura publicada vs. simulação 0D), sem necessidade de dado próprio.

### 4.5 — Dose isquêmica acumulada ao longo de um regime terapêutico (contribuição original)

$$\mathcal{I}_{\text{cum}}(N) = \sum_{j=1}^{N} \mathcal{I}_j \cdot w(t_j - t_{j-1})$$

onde N é o número de injeções e w(Δt) pondera acumulação vs. recuperação entre eventos.

Dois limites de w(Δt):
- **Acumulação perfeita:** w = 1 sempre → 𝓘_cum = N·𝓘 (K constante).
- **Acumulação com recuperação parcial:** inspirado no modelo SF do rato (SF = 1 − b(1 − e^{−at})) — se Δt ≫ 1/a, recuperação quase completa entre eventos; se Δt é curto, dano acumula.

**Regimes terapêuticos a simular** (varrendo K, OPP_crit, φ_vasc):

| Regime | N (2 anos) | Intervalo típico |
|---|---|---|
| Mensal fixo | 24 | 4 semanas |
| Treat-and-extend | ~12 | 8–12 semanas |
| Brolucizumabe | ~8 | 12 semanas |
| Faricimabe | ~6 | 16 semanas |

**Suporte indireto da literatura:** o contraste entre paracentese sem efeito detectável (RCT, evento único) e paracentese com RNFL preservado (observacional, uso repetido) é a assinatura esperada de um processo cumulativo — cada evento isolado é indetectável, mas a soma sem proteção não é.

### 4.6 — Análise de sensibilidade global

Varrer simultaneamente (Sobol' ou Morris): K (0,15–1,0 mmHg/µL), C_out (0,15–0,40 µL/min/mmHg), OPP_crit (20–55 mmHg), fator braquial→oftálmica (0,5–0,8), MAP (70–110 mmHg), ΔV (50–100 µL), φ_vasc (1,0–2,0), w (0–1).

**Saída:** índices de Sobol' para 𝓘 (evento único) e 𝓘_cum (20 injeções). Se OPP_crit dominar a incerteza (esperado), a conclusão do capítulo é que **a contribuição mais urgente do campo não é mais modelagem, é medir o limiar isquêmico agudo humano** — o que aponta diretamente para o valor do sub-estudo OCT-A futuro.

**Hedge obrigatório:** o modelo é exploratório/relativo (estratificação de risco entre pacientes), não preditivo em valor absoluto de 𝓘, enquanto a incerteza em OPP_crit permanecer maior que um fator 2.

### 4.7 — Conexão com dado empírico (futuro, fora do escopo teórico atual)

A validação direta de 𝓘 contra medida real de perfusão (sub-estudo OCT-A do WP3) fica para uma fase experimental futura, fora do escopo desta etapa teórica.

---

## 4. Impacto

| Subitem | Situação |
|---|---|
| 4.1 | Mantido + φ_vasc |
| 4.2 | Mantido + precedente anestesiológico + âncoras |
| 4.3 | Mantido integralmente |
| 4.4 | Novo — validação teórica contra dado publicado |
| 4.5 | Novo — dose acumulada (contribuição original) |
| 4.6 | Novo — sensibilidade global |
| 4.7 | Novo, mas reduzido a placeholder — execução futura |

Todo o trabalho de 4.1–4.6 é computável com o solver 0D já existente (`cases/wp0/goldmann_iop_solver.py`) mais um módulo novo de perfusão/dose isquêmica — nenhuma dependência de CalculiX ou experimento novo.
