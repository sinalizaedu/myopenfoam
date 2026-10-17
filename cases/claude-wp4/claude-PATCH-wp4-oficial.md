# Patch para o pipeline oficial `cases/wp4/`

Não editei nada em `cases/wp4/` (é do Composer). As correções estão aplicadas nas
minhas versões em `cases/claude-wp4/` e nos módulos novos
`claude_wp4_fixes.py` / `claude-REFERENCES-WP4.md`. Abaixo, o que mudar lá.

---

## 1. `validacao_zero_observado.py` — remover citação inexistente

**Linha ~4 da docstring do módulo.** Apagar:

> Objetivo (citação do plano): "mostrar que o modelo reproduz corretamente a ausência de
> déficit perfusional relatada na literatura para injeção única, e delimitar a região
> paramétrica onde essa previsão deixaria de valer."

Essa frase **não existe no plano** (procurei seis fragmentos distintos: zero ocorrências
de cada). Substituir por formulação própria, sem aspas e sem atribuição, e acrescentar que
o item 4.4 é extensão proposta — **o plano tem só 4.1, 4.2 e 4.3**.

## 2. `validacao_zero_observado.py` — âncora do OCT-A

O estudo "OCT-A 2026 (n=54)" existe (**PMID 42565012, PMCID PMC13444746**) mas **não foi
possível lê-lo** (CAPTCHA no PubMed/PMC, 429 no Europe PMC/OpenAlex/Semantic Scholar).
Logo `n=54`, `14→31 mmHg`, "sem déficit" e — crítico — **se 31 é IOP ou MOPP** seguem não
verificados.

Duas opções, nessa ordem de preferência:

1. Ler o PDF e confirmar se `MOPP_MIN_OBSERVADO_OCT_A_MMHG = 31.0` é MOPP mesmo (hoje é
   **idêntico ao pico de IOP**, o que é exatamente o sinal de conflação).
2. Trocar a âncora por **Colizzi et al. 2025** (verificado, n=119), que dá as duas séries:

   | | basal | imediato | 5 min | 30 min |
   |---|---:|---:|---:|---:|
   | IOP | 15,76 | 49,79 | 29,96 | 21,80 |
   | MOPP | 54,02 | 35,70 | 40,68 | 51,08 |

   > Colizzi B, Romano D, Lunardon S, Sabbatini L, Rossetti LM. *Eur J Ophthalmol.*
   > 2025;35(4):1272–1279. DOI 10.1177/11206721251318773. PMID 40539393.

   Note que **IOP sobe enquanto MOPP desce**, e que ~30 aparece tanto como IOP de 5 min
   quanto perto do vale da MOPP — origem plausível do "~31" conflacionado. Com esses
   dados o MOPP mínimo é **35,7 mmHg**, não 31, o que **move o teto de OPP_crit** da
   conclusão da Peça 1.

Completar também a citação `"fonte": "PMC13307848"` da Peça 3 (um PMCID não é citação).

## 3. `dose_isquemica.py` — autoria, provenância e o $Q_{prod}$ sem fonte

Trocar o comentário de `_PARAMS_LITERATURA` por provenância **por parâmetro** (copiar de
`claude-wp4/claude_dose_isquemica.py`, já feito):

- `C_out = 0,26` **[verificado]** Fourman S, Fourman MB. *Curr Eye Res.* 1989;8(9):963–969.
  DOI 10.3109/02713688909082658. **Não existe "Garner"** — corrigir a autoria.
  Tonografia 0,26 ± 0,07 **e** perfusão a pressão constante 0,26 (r = 0,914): os dois
  métodos concordam, então a divergência de 2,2× contra o 0,57 **não** é de método.
  Remover o rótulo "anestesiado", que não está verificado para a facilidade.
- `Pev = 15,5` **[verificado]** Kiel JW, Kopczynski CC. *J Ocul Pharmacol Ther.*
  2015;31(3):146–151. EVP 16 ± 1 mmHg, coelho anestesiado.
- `Q_prod = 3,06` **[SEM FONTE]** — nenhuma fonte localizada. O fluxo publicado
  verificável é **1,46–2,53 µL/min** (coelho consciente; Zhao M, Hejkal JJ, Camras CB,
  Toris CB. *IOVS* 2010;51(6):3145–3151. DOI 10.1167/iovs.09-4415). **3,06 está acima da
  faixa medida**, e $P_0$ do coelho depende dele:

  | $Q_{prod}$ | $P_0$ derivado |
  |---|---:|
  | 1,46 | 20,83 mmHg |
  | 2,00 | 22,81 mmHg |
  | 2,53 | 24,74 mmHg |
  | **3,06 (sem fonte)** | **26,68 mmHg** |

- Declarar o **alerta de mistura de condições**: $P_{ev}$ anestesiado + faixa de fluxo
  consciente + Fourman não confirmado, somados num único $P_0$.

## 4. `dose_isquemica.py` — Barbados: 42 → 40

A docstring diz "Barbados Eye Study (MOPP<42)". O primário dá **MOPP < 40 → RR 2,6** e
DOPP < 53 → RR 2,2 (Leske MC, Wu SY, Hennis A, Honkanen R, Nemesure B. *Ophthalmology.*
2008;115(1):85–93. PMID 17629563). Baltimore: DOPP < 30, risco ~6× (Tielsch JM, Katz J,
Sommer A, Quigley HA, Javitt JC. *Arch Ophthalmol.* 1995;113(2):216–221. PMID 7864755).
**Os dois são estudos crônicos** — dizer isso no texto da tese, não só no comentário.

## 5. `dose_cumulativa.py` — atribuição ao plano e o T&E

Apagar "Regimes terapêuticos do plano (Seção 4.5)". O plano não tem Seção 4.5 e não
menciona brolucizumabe, faricimabe nem treat-and-extend. Citar:

- Dugel PU et al. HAWK/HARRIER. *Ophthalmology* 2020;127(1):72–84. DOI 10.1016/j.ophtha.2019.04.017
  (96 sem: 2021;128(1):89–99, PMID 32574761)
- Heier JS et al. TENAYA/LUCERNE. *Lancet* 2022;399(10326):729–740. DOI 10.1016/S0140-6736(22)00010-1
- Gemenetzi M, Patel PJ. *Ophthalmol Ther* 2017;6(1):79–92. DOI 10.1007/s40123-017-0087-5

**Corrigir o treat-and-extend:** está `N=12, intervalo 10 semanas`. As fontes dão
**13,0–14,3 injeções em 2 anos** e intervalo médio de **~6,3 semanas**. Com o valor certo,
o T&E fica bem mais perto do mensal — e isso **muda a magnitude da separação entre
regimes**, que é a conclusão do item 4.5.

**Declarar a ressalva estrutural:** q12s e q16s nos ensaios são a **proporção de pacientes
que conseguiu manter o intervalo** (51–56% brolucizumabe; ~45% faricimabe na semana 48),
não o intervalo de toda a coorte. Tratar como 100% subestima a dose média da população.

## 6. `dose_cumulativa.py` — trocar o desconto por evento por modelo de estado

Substituir `dose_cumulativa()` por `claude_wp4_fixes.dano_acumulado_com_estado()`.
O original ($\sum_j I_j w(\Delta t_j)$) não tem variável de estado, cresce linearmente em
$N$ e **nunca satura**. Com estado, $D_j = D_{j-1}e^{-a\Delta t} + I_j$ satura em
$D_\infty = I/(1-e^{-a\Delta t})$. Rodei os dois ($I = 20$ mmHg·min, meia-vida 4 semanas):

| regime | $N$ | Δt | original | com estado | $D_\infty$ |
|---|---:|---:|---:|---:|---:|
| mensal fixo | 24 | 4 sem | 250,00 | **40,00** | 40,00 |
| treat-and-extend (corrigido) | 13 | 6,3 sem | 100,55 | **30,10** | 30,10 |
| brolucizumabe q12s | 8 | 12 sem | 37,50 | **22,86** | 22,86 |
| faricimabe q16s | 6 | 16 sem | 26,25 | **21,33** | 21,33 |

**Achado substantivo:** a ordem entre regimes se mantém, mas a separação colapsa de ~4×
(480 vs 120 na tabela atual) para **1,9×** (40 vs 21). Ou seja, com um modelo de
recuperação que satura, a diferença clínica entre regimes é **muito menor** do que o item
4.5 afirma hoje. Isso precisa ser corrigido antes de virar texto.

E obter fonte para o "modelo SF do rato" ou remover o item: é a forma funcional de todo o
4.5 e não tem referência nenhuma.

## 7. `opp_perfusion.py` — estimador de `T_acima_*`

Substituir `_tempo_iop_acima` por `claude_wp4_fixes.tempo_acima_interpolado`, e
`dose_isquemica` por `dose_isquemica_exata`. Medido num decaimento exponencial sintético
($\tau = 3{,}18$ min, Ruffini 2024):

| | analítico | grid do solver (dt=0,01) | **grid clínico do WP3 (6 pontos)** |
|---|---:|---:|---:|
| $T_{>30}$, indicador/trapézio | 2,938 | 2,935 | **3,500** |
| $T_{>30}$, interpolado | 2,938 | 2,938 | **3,255** |
| $\mathcal{I}$ (OPP_crit=25), trapézio | — | 17,510 | **21,414** |
| $\mathcal{I}$ (OPP_crit=25), exata | — | 17,510 | **19,250** (−11,2%) |

Duas leituras honestas: (a) no grid do solver o defeito é irrelevante; (b) no grid clínico
de 6 pontos a interpolação **melhora mas não salva** — ela corrige o viés do *estimador*,
não a limitação da *amostragem* ($\Delta t_{max}/\tau = 4{,}7$). Se as métricas temporais
forem aplicadas a dado clínico, isso tem que estar declarado como limitação.

## 8. `opp_perfusion.py` — sensibilidade do fator 2/3 (o plano exige e não existe)

Acrescentar `claude_wp4_fixes.curva_sensibilidade_fator_braquial`. O plano manda varrer
0,5–0,8. É enorme:

| fator | MOPP mín | $\mathcal{I}$ (OPP_crit=50) |
|---:|---:|---:|
| 0,50 | −6,57 | 811,93 |
| 2/3 | 7,88 | 378,60 |
| 0,80 | 19,43 | 77,03 |

**Fator 10 em $\mathcal{I}$** dentro da faixa que o plano manda varrer — e com 0,50 a MOPP
fica negativa, regime de cessação de perfusão. Nenhum resultado de dose isquêmica pode ser
reportado sem essa curva ao lado.

## 9. Rotular as formas funcionais supostas

- `opp_crit_efetivo = opp_crit_ref · phi_vasc`: a **forma** (multiplicativa, e só para
  cima, pois $\phi\ge1$ é imposto) é suposição, não medida. Damasceno 2022 motiva que
  carótida importa, não que o efeito seja multiplicativo no limiar.
- `pad_oftalmica = (2/3)·PAD`: aplicar à **diastólica** o fator que é convenção para a
  **média** é suposição adicional, sem fonte. E a OPP diastólica alimenta $\mathcal{I}$.

## 10. `validacao_zero_observado.py` — detalhe de forma

`FRACAO_COM_OBSTRUCAO_CAROTIDEA = 0.666` → escrever `12/18` (é contagem, não medida).
Damasceno et al. 2022 confere exatamente: 807 pacientes, 4.069 injeções, 18 casos (0,44%),
12/18 com obstrução ≥70%.

> Damasceno NA, Yannuzzi NA, Maia M, Farah ME, Flynn HW Jr, Damasceno EF. *Eur J
> Ophthalmol.* 2022;32(5):2819–2823. DOI 10.1177/11206721211066196. PMID 34962172.
