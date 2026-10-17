# Auditoria item por item — WP4, WP5, WP6

Passagem sistemática: cada número que entra no cálculo, de onde vem, e se a fonte
sustenta o que se afirma. Fiz verificação de literatura dirigida para os parâmetros que
estavam sem referência verificável.

**Convenção de confiança:** `[P]` verificado no texto primário · `[S]` verificado em
revisão/livro-texto (primário não acessado) · `[X]` atribuição ERRADA — a fonte citada não
contém o número · `[NF]` sem fonte localizada.

**Resultado em uma linha:** a matemática do WP4 está certa (reverifiquei H6 do zero). O
problema é de procedência: **quatro atribuições erradas**, e uma delas — o limiar de
OPP — é internamente impossível com os próprios valores basais da tese.

---

# PARTE 1 — O achado mais importante

## OPP_crit ≈ 50 mmHg não pode ser usado: torna todo paciente isquêmico em repouso

O plano sugere que "a autorregulação retiniana falha abaixo de MOPP ~50 mmHg em várias
séries", e o WP4 usa `opp_crit_ref=50.0` nos exemplos.

Com os próprios valores padrão da tese (PAS 120 / PAD 70, $P_0 = 16{,}9$ mmHg):

$$\text{MOPP}_{basal} = \tfrac{2}{3}\!\left(70 + \tfrac{120-70}{3}\right) - 16{,}9
= 57{,}78 - 16{,}9 = \mathbf{40{,}9\ \text{mmHg}}$$

**A MOPP basal de um olho saudável em repouso já é 40,9 mmHg — abaixo dos 50.** Com
$\text{OPP}_{crit} = 50$, $\Delta P_{th} = -9{,}12 < 0$: o limiar é cruzado sem injeção
nenhuma. A fórmula de H6 nem se aplica (e o código corretamente levanta `ValueError`
nesse regime — o guard existe, mas ninguém notou que o valor sugerido cai nele).

**De onde vem o 50 e por que está no regime errado:**

`[S]` **Leske MC.** "Ocular perfusion pressure and glaucoma: clinical trial and
epidemiologic findings." *Curr Opin Ophthalmol.* 2009;20(2):73–78. Texto lido: "A low
diastolic perfusion pressure, under 50−55 mmHg, was associated with OAG **prevalence**";
Barbados RR 2,0–2,6 em incidência de 9 anos; Rotterdam OR 4,68; EMGT HR 1,42.

São estudos **transversais e longitudinais de glaucoma crônico**, ao longo de anos. Nenhum
mede evento pressórico agudo de minutos.

**O que a literatura aguda diz** `[P]` (*Sci Rep.* 2018;8:17524,
DOI 10.1038/s41598-018-35683-y, texto lido): o fluxo na cabeça do nervo óptico **mantém**
capacidade autorregulatória com a OPP reduzida em 50,9% (IOP +20) e 74,2% (IOP +30); cita
dados em macaco de que a autorregulação da ONH é "active at OPPs >30 mmHg" e "not present
at <30 mmHg", e dados humanos de que o fluxo "did not decrease significantly until the OPP
values were 30% below the baseline". E admite que "the level of the IOP above which the
autoregulation breaks down has been different in these different experimental studies".

### Três caminhos independentes convergem em ~30 mmHg

| origem | $\text{OPP}_{crit}$ | regime |
|---|---:|---|
| Leske 2009 (glaucoma crônico) | 50–55 | **crônico — inaplicável** |
| Barbados (MOPP<40, RR 2,6) | 40 | crônico |
| Item 4.4, teto do zero do OCT-A | **≤ 31** | agudo pós-IVI |
| Autorregulação aguda da ONH (macaco) | **~30** | agudo experimental |

**Isso corrobora o item 4.4 em vez de contradizê-lo.** Na revisão anterior eu tinha
anotado que a conclusão do 4.4 ("o zero só é consistente se $\text{OPP}_{crit} \le 31$")
implicaria que o limiar crônico de ~50 não vale no agudo — e a literatura aguda diz
exatamente isso, por um caminho independente. Vale escrever na tese como resultado.

E o efeito na métrica central é enorme:

| $\text{OPP}_{crit}$ | $\Delta P_{th}$ | $\mathcal{I}$ ($K=0{,}325$, $\Delta V=50$) |
|---:|---:|---:|
| 50 | **−9,12** | fora do domínio |
| 40 | 0,88 | 140,8 mmHg·min |
| 31 | 9,88 | 16,0 mmHg·min |
| 30 | 10,88 | 11,1 mmHg·min |

**Fator 13 em $\mathcal{I}$** entre 30 e 40. O alerta metodológico do plano ("apresente
$\mathcal{I}$ como função de $\Delta P_{th}$, nunca com valor fixo") está certo — mas o
valor-âncora sugerido é do regime errado e precisa trocar.

---

# PARTE 2 — WP4, item por item

## 4.1 — Cadeia IOP → OPP (`opp_perfusion.py`)

**Matemática:** correta. $\text{MAP} = \text{PAD} + (\text{PAS}-\text{PAD})/3$ ✓;
$\text{MOPP} = f\cdot\text{MAP} - \text{IOP}$ ✓, igual ao plano §4.1.

**Parâmetros:**

| valor | atribuição no código | verdito |
|---|---|---|
| fator 2/3 braquial→oftálmica | "convenção clínica/literária, não medida direta" | `[S]` honesto — é convenção mesmo; o plano manda varrer 0,5–0,8 |
| $\text{PAD}_{oft} = (2/3)\cdot\text{PAD}$ | "estimativa" | `[NF]` o 2/3 é convenção para a **média**, não para a diastólica — suposição adicional sem fonte |
| $\phi_{vasc}$ multiplicativo em $\text{OPP}_{crit}$ | "motivação clínica: Damasceno 2022" | `[NF]` a fonte sustenta que carótida importa, **não** que o efeito seja multiplicativo no limiar |

**Defeito numérico:** `_tempo_iop_acima` integra indicador binário por trapézio →
devolve $\Delta t \times$ (nº de amostras acima). Irrelevante no grid do solver
($dt = 0{,}01$ min), **erra por minutos no grid clínico de 6 pontos do WP3**. Corrigido em
`claude_wp4_fixes.tempo_acima_interpolado`.

**Sensibilidade do fator 2/3:** ausente no pipeline oficial (`cases/wp4/`); **presente no
meu fork** (`sensibilidade_fator_braquial`). Medida: $\mathcal{I}$ vai de 811,9 (f=0,50) a
77,0 (f=0,80) — **fator 10** na faixa que o plano manda varrer, e com f=0,50 a MOPP fica
negativa. Nenhum resultado de dose pode sair sem essa curva ao lado.

**Decisão aplicada hoje:** `cadeia_completa` passou a ter `estimar_PAD_oftalmica=False`
por padrão. Sem PAD oftálmica medida, `OPP_diast` fica `None` em vez de carregar a
suposição silenciosamente; a convenção do Composer fica disponível com
`estimar_PAD_oftalmica=True`. Isso também recoloca
`test_opp_diast_none_sem_pad_oftalmica` em verde (era a única falha, 59/60).

## 4.2 — Dose isquêmica (`dose_isquemica.py`)

**Matemática:** $\mathcal{I} = \int \max(0, \text{OPP}_{crit} - \text{OPP}(t))\,dt$ ✓
igual ao plano §4.2. `derivar_P0_equilibrio` ✓ é o equilíbrio de Goldmann correto com a
via uveoescleral tratada como insensível à pressão.

### Os quatro parâmetros humanos — dois com atribuição errada

| parâmetro | valor | verdito |
|---|---:|---|
| $Q_{prod}$ | 2,4 µL/min | `[S]` **ok**. Goel et al. 2010 (texto lido): "2.4 ± 0.6 μl/min (daytime, adults 20–83)", traçado a Brubaker 1989 (cap. de livro, não acessado). Atenção: o próprio Goel dá 3,0 de manhã, 2,4 à tarde, **1,5 à noite** — há variação diurna de 2× |
| $C_{out}$ | 0,28 µL/min/mmHg | `[X]` **não está em Goel** — a revisão não dá valor nenhum de facilidade. O suporte é **Adler's Physiology of the Eye** (Kaufman & Alm): $OF = 0{,}54 - 0{,}0042 \times \text{idade}$, com "<40 anos 0,33; >60 anos 0,23; 0,28". Ou seja, 0,28 corresponde a **~62 anos** |
| $P_{ev}$ | 10 mmHg | `[S]` no **topo** da faixa citada. Goel: "approximately 8–10 mmHg" (citando Phelps & Armaly 1978; Brubaker 1967). Smith & Gardiner, *PLoS ONE* 2017;12(12):e0188769 (lido): "7 to 10 mm Hg when IOP is 15 mm Hg" |
| $f_{uv}$ | 0,20 | `[X]` **NÃO está em Goel et al. 2010.** Goel diz 40–50% em primatas não humanos e "a similar fraction" em humanos jovens (citando Alm & Nilsson, *Exp Eye Res* 2009;88(4):760–8). Adler's: "approximately 35–55 percent… in younger humans". O único primário que abarca 20% é **Bill A, Phillips CI.** *Exp Eye Res.* 1971;12(3):275–81 — **4 a 27%, em olhos sob atropina** |

**Consequência do $f_{uv}$, que é a mais séria:** $P_0$ é derivado dele, e
$P_0 = 16{,}9$ é a basal que ancora WP1.2, WP1.3 e WP1.4.

| $f_{uv}$ | origem | $P_0$ derivado |
|---:|---|---:|
| 0,20 | atribuição errada a Goel | **16,86** (valor em uso) |
| 0,27 | topo de Bill & Phillips (atropina) | 16,26 |
| 0,35 | base de Alm & Nilsson / Adler's | 15,57 |
| 0,45 | meio de 35–55% | 14,71 |
| 0,55 | topo | 13,86 |

**3 mmHg de amplitude na basal**, e isso realimenta o $K_f$ recalibrado contra Knecht:

| $P_0$ | $K_f$ recalibrado | $K$(basal) |
|---:|---:|---:|
| 16,86 | 0,005833 | 0,2265 |
| 15,57 | 0,006525 | 0,2339 |
| 13,86 | 0,007535 | 0,2405 |

O $K$ é relativamente robusto (0,227–0,241, variação de 6%) — boa notícia. Mas $P_0$ em si
entra em todo lugar e precisa de fonte própria para $f_{uv}$.

### Âncoras de $\text{OPP}_{crit}$

| citação no código | verdito |
|---|---|
| "Baltimore Eye Survey (DOPP<30, crônico)" | `[S]` Tielsch JM et al. *Arch Ophthalmol.* 1995;113(2):216–221, PMID 7864755. DOPP<30 → risco ~6× (confirmado em revisão, não no primário) |
| "Barbados Eye Study (MOPP<42)" | `[X]` **42 não se confirma** → Leske MC et al. *Ophthalmology* 2008;115(1):85–93, PMID 17629563: **MOPP<40 → RR 2,6**; DOPP<53 → RR 2,2. **Já corrigido** no meu fork |
| "CRAO completa (12–15 min)" | `[P]` **Tobalem S, Schutz JS, Chronopoulos A.** *BMC Ophthalmol.* 2018;18:101, DOI 10.1186/s12886-018-0768-4 (texto lido): "Retinal infarction is most likely to occur after only 12–15 min of complete CRAO" |

Sobre o CRAO, duas notas: o lado contrário (Hayreh) é renderizado pela própria refutação
como **90–240 min**, não 97 — se a tese citar "97 min", puxar do Hayreh original
(*Exp Eye Res.* 2004;78(3):723–736), que não foi acessado. E o código já diz
corretamente que isso é limiar de **tempo**, não de OPP.

**Reforçar no texto:** Baltimore e Barbados são crônicos. O código diz "documentação, NÃO
calibração" ✓, mas a tese precisa dizer no corpo, não só no comentário.

## 4.3 — H6 teórico (`h6_teorico.py`)

**Reverifiquei derivando do zero.** Com $\Delta P(t) = \Delta P_0 e^{-t/\tau}$ e cruzamento
em $t^\ast = \tau\ln(\Delta P_0/\Delta P_{th})$:

$$\mathcal{I} = \tau\Big[\Delta P_0 - \Delta P_{th} - \Delta P_{th}\ln\tfrac{\Delta P_0}{\Delta P_{th}}\Big]
= \frac{\Delta V}{C} - \frac{\Delta P_{th}}{CK}\Big[1+\ln\tfrac{K\Delta V}{\Delta P_{th}}\Big]$$

$$\frac{\partial\mathcal{I}}{\partial K} = \frac{\Delta P_{th}}{CK^2}\ln\frac{K\Delta V}{\Delta P_{th}}, \qquad K_{crit} = \frac{\Delta P_{th}}{\Delta V}$$

Idêntico ao implementado e ao plano. Recalculei à mão toda a tabela (dPth=15, ΔV=50,
C=0,28): ΔV/C = 178,571; K_crit = 0,30; I(0,31)=0,0945; I(0,40)=6,11; I(0,60)=27,43;
I(1,00)=60,50; I(3,00)=119,60. **Todos conferem.** Consequência 3 ($\mathcal{I}\propto 1/C$,
razão exatamente 2) é correta por inspeção.

**Este é o item mais sólido do WP4.** Nenhum `dPth` fixo em função pública ✓, `ValueError`
informativo fora de domínio ✓. Uma imprecisão só de redação: a docstring junta "sem limiar,
K cancela" com "$K\to\infty$" — são dois limites diferentes (o primeiro vale para qualquer
$K$ quando $\Delta P_{th}\to 0$; o segundo é assíntota a $\Delta P_{th}$ fixo). Ambos dão
$\Delta V/C$, então não há erro de conta.

## 4.4 — Validação contra o zero observado (`validacao_zero_observado.py`)

| item | verdito |
|---|---|
| "citação do plano" entre aspas | `[X]` **a frase não existe no plano** — procurei seis fragmentos, zero ocorrências. **Removida** do meu fork hoje |
| O item 4.4 existir no plano | `[X]` o plano tem só 4.1, 4.2, 4.3. É extensão proposta |
| OCT-A "2026, n=54", 14→31 mmHg | `[NF]` o artigo existe (**PMID 42565012, PMCID PMC13444746**) mas **não foi possível ler** (CAPTCHA/429). n=54, os 14→31 e "sem déficit" seguem não verificados |
| `MOPP_min = 31,0` = pico de IOP | risco de conflação **confirmado como real** — ver abaixo |
| Damasceno et al. 2022 | `[P]` **confere exatamente**: Damasceno NA, Yannuzzi NA, Maia M, Farah ME, Flynn HW Jr, Damasceno EF. *Eur J Ophthalmol.* 2022;32(5):2819–2823, PMID 34962172. 807 pacientes, 4.069 injeções, 18 casos (0,44%), **12/18 (66,6%)** com obstrução ≥70% |
| "PMC13307848" (Peça 3) | `[NF]` um PMCID não é citação — falta autor, título, revista, ano, DOI |
| $\phi = 1{,}3$, $K_{alto} = 1{,}0$, $\Delta P_{th}=20$, $\text{OPP}_{crit}=25$ | declarados "ilustrativos" ✓, mas separar dois grupos com 4 parâmetros livres não é teste |

**Substituto verificado que mostra a conflação:** `[P]` **Colizzi B, Romano D, Lunardon S,
Sabbatini L, Rossetti LM.** *Eur J Ophthalmol.* 2025;35(4):1272–1279,
DOI 10.1177/11206721251318773, PMID 40539393, **n = 119**:

| | basal | imediato | 5 min | 30 min |
|---|---:|---:|---:|---:|
| IOP | 15,76 | 49,79 | **29,96** | 21,80 |
| MOPP | 54,02 | **35,70** | 40,68 | 51,08 |

IOP sobe enquanto MOPP desce, e **~30 aparece como IOP de 5 min e perto do vale da MOPP** —
origem plausível de um "31" conflacionado. Nestes dados o mínimo de MOPP é **35,7**, não
31, o que **move o teto de $\text{OPP}_{crit}$** da conclusão da Peça 1.

Achado adicional útil para o eixo (d): só 25% dos olhos glaucomatosos voltaram à IOP basal
em 30 min, contra 48,9% dos não glaucomatosos (p = 0,02).

## 4.5 — Dose acumulada (`dose_cumulativa.py`)

| item | verdito |
|---|---|
| "Regimes terapêuticos do plano (Seção 4.5)" | `[X]` o plano não tem 4.5 nem menciona brolucizumabe/faricimabe/T&E. **Corrigido** no meu fork |
| brolucizumabe q12s | `[P]` Dugel PU et al. HAWK/HARRIER. *Ophthalmology* 2020;127(1):72–84, DOI 10.1016/j.ophtha.2019.04.017 (96 sem: 2021;128(1):89–99, PMID 32574761) |
| faricimabe q16s | `[P]` Heier JS et al. TENAYA/LUCERNE. *Lancet* 2022;399(10326):729–740, DOI 10.1016/S0140-6736(22)00010-1 |
| T&E "12 injeções a cada 10 semanas" | `[X]` **errado** → Gemenetzi M, Patel PJ. *Ophthalmol Ther* 2017;6(1):79–92: **13,0–14,3 injeções em 2 anos**, intervalo médio ~**6,3 semanas** |
| "modelo SF do rato" | `[NF]` **nenhuma fonte** — e é a forma funcional de todo o item |
| $w(\Delta t)$ como desconto por evento | erro de modelagem: não tem variável de estado, cresce linear em $N$, **nunca satura** |

**Ressalva estrutural que ninguém declarou:** q12s e q16s nos ensaios são a **proporção de
pacientes que conseguiu manter o intervalo** (51–56% brolucizumabe; ~45% faricimabe na
semana 48), não o intervalo de toda a coorte. Modelar como se 100% mantivesse subestima a
dose média da população.

**Efeito do modelo de estado** ($D_j = D_{j-1}e^{-a\Delta t} + I_j$, satura em
$I/(1-e^{-a\Delta t})$), com $I=20$ e meia-vida de 4 semanas:

| regime | original | com estado | $D_\infty$ |
|---|---:|---:|---:|
| mensal | 250,0 | **40,0** | 40,0 |
| T&E (corrigido) | 100,6 | **30,1** | 30,1 |
| brolucizumabe | 37,5 | **22,9** | 22,9 |
| faricimabe | 26,3 | **21,3** | 21,3 |

A separação entre regimes colapsa de ~4× para **1,9×**. A conclusão do item 4.5 muda.

---

# PARTE 3 — WP5 (especificação; não existe código)

| item | verdito |
|---|---|
| Tabela §5.3 (179/103/80 µL) | aritmética ✓, mas **lineariza** uma curva que a tese adota como exponencial → superestima **1,9×** |
| $K_f$ adotado (0,00581) vs faixa do plano (0,0126–0,0280) | `[X]` inconsistência de **2,2×** entre capítulos. É consequência deliberada da recalibração contra Knecht, mas os dois não podem coexistir sem declaração |
| volume da CA ~250 µL | `[X]` **sem fonte, e o medido é bem menor** (ver abaixo) |
| $R_{par} = 6{,}2\times10^{11}$ Pa·s/m³ | `[P]` **derivável**: Poiseuille com 30G ½ pol ($d$=0,159 mm, $L$=12,7 mm) e $\mu_{aquoso}$=0,75 mPa·s dá $6{,}07\times10^{11}$ — 2% de diferença ✓ |
| duração da paracentese (0,2 min, "sem fonte" no plano) | agora **derivável**: integrando a drenagem, 7,5–13,6 s = 4–7% de $\tau$. A pendência pode ser fechada |
| IOP ≥ 6 mmHg (hipotonia) | `[X]` **nenhuma fonte dá exatamente 6** |

## Volume da câmara anterior — correção que piora a conclusão

`[P]` **Dinc UA, Oncel B, Gorgun E, Alimgil L.** "Quantitative assessment of anterior
chamber volume using slit-lamp OCT and Pentacam." *Eur J Ophthalmol.* 2009;19(3):411–415,
DOI 10.1177/112067210901900314, PMID 19396787. n = 80 olhos saudáveis:
**Pentacam 163,34 ± 29,76 mm³**, SL-OCT 164,14 ± 28,44 (p = 0,872).

Zong Y et al. *J Ophthalmol.* 2017;2017:6762047 (n = 313, SS-OCT): **153,83 ± 32,42 mm³**.

Os 250 µL parecem ser número de denominador de turnover de livro-texto, **não volume
medido**. E isso **piora** a viabilidade da paracentese, ao contrário do que eu disse na
revisão anterior:

| $\Delta V$ | fração de 163 µL (medido) | fração de 250 µL (sem fonte) |
|---:|---:|---:|
| 41,5 µL (exponencial, $K_f$=0,0126) | **25,4%** | 16,6% |
| 81,0 µL (exponencial, $K_f$ WP1.2) | **49,6%** | 32,4% |
| 178,6 µL (linearizada, $K$=0,196) | **109,3%** | 71,4% |

Ou seja: a correção da linearização (1,9× a menos) e a correção do volume da CA (1,5× a
menos de câmara) **se cancelam em boa parte**. A conclusão honesta é mais morna do que eu
havia sugerido: com a lei exponencial e o volume medido, a paracentese consome **25–50% da
câmara anterior** — factível, mas não confortável, e no limite superior do $K_f$ adotado
fica perto da metade da câmara.

## Hipotonia

`[S]` **Wang Q, Thau A, Levin AV, Lee D.** "Ocular hypotony: a comprehensive review."
*Surv Ophthalmol.* 2019;64(5):619–638, DOI 10.1016/j.survophthal.2019.04.006: hipotonia
**estatística** = IOP mais de 3 DP abaixo da média, **< 6,5 mmHg**; e a *World Glaucoma
Association* sugere corte de **≤ 5 mmHg** para IOP não fisiológica.

**Nenhuma fonte dá 6 mmHg.** Usar 6,5 (estatística) ou 5 (WGA), e dizer qual.

---

# PARTE 4 — WP6 (especificação; não existe código)

| item | verdito |
|---|---|
| $\phi = K_{\text{ex vivo}}/K_{\text{in vivo}}$ = complacência coroidal | confunde espécie + vivo/morto + erro da correção geométrica. A correção descrita é só de **geometria**; a diferença de material suíno-humano cai dentro de $\phi$ e é lida como sangue coroidal |
| $p(\theta)\,p(D_{suíno}|\theta)\,p(D_{clínico}|\theta)$ | independência condicional ✓, mas **$\theta$ não é comum às espécies** sem modelo de transferência |
| MCMC sobre o emulador | ✓ arquitetura certa; herda o WP1.4. Com a correção, ACD/cristalino/vitrectomia **saem de $\theta$** e viram covariáveis clínicas do WP3 |
| semáforo de risco | os cortes verde/amarelo/vermelho seriam números novos — precisam de percentis da coorte ou limiar com fonte |
| validação 100/50 temporal | a mais fraca das opções; deriva de técnica é plausível justamente porque a medida "imediata" depende de treino |

Nenhum desses depende de referência externa — são decisões de arquitetura. Mas o $\phi$ da
H3 é apresentado como **número novo de fisiologia ocular**, e aí a exigência de rigor é
máxima: como está, não sustenta a interpretação. Saída honesta e barata: declarar como
**limite superior** da complacência coroidal, com o termo de espécie dentro.

---

# PARTE 5 — Lista consolidada de correções

## Bloqueantes para a banca

| # | O que | Onde |
|---|---|---|
| 1 | **$\text{OPP}_{crit}$: trocar a âncora de ~50 (crônico) para ~30 (agudo)**, citando Leske 2009 como crônico e a autorregulação aguda da ONH. Com 50, $\Delta P_{th}<0$ e o modelo não roda | WP4 §4.2/4.3, texto |
| 2 | **$f_{uv} = 0{,}20$ não está em Goel 2010.** Achar fonte ou adotar a faixa de Bill & Phillips 1971 (4–27%) / Alm & Nilsson (35–55%) e declarar o efeito em $P_0$ (16,9 → 13,9) | WP4 §4.2 → propaga a WP1.2/1.3/1.4 |
| 3 | **$C_{out} = 0{,}28$ não está em Goel** — é Adler's ($OF = 0{,}54 - 0{,}0042\times$idade, ≈62 anos). Para coorte de DMRI (70–85 anos) seria ~0,22 | WP4 §4.2 |
| 4 | **Volume da CA: 250 → 163 µL** (Dinc 2009, primário). Refazer a conclusão de viabilidade da paracentese | WP5 §5.3 |
| 5 | **$K_f$: uma história só** (0,0058 recalibrado vs 0,0126–0,0280 da literatura) | WP1.2 ↔ WP5 |
| 6 | Trocar $\Delta V = \Delta\text{IOP}/K$ por integração da $P(V)$ | WP5 §5.3 |
| 7 | **Ler o PMID 42565012** antes de citar, ou trocar por Colizzi 2025 (n=119, verificado) | WP4 §4.4 |
| 8 | Reformular $\phi$ da H3 como limite superior | WP6 §6.2 |

## Já corrigido no meu fork hoje

- Citação inexistente atribuída ao plano — removida
- "Fourman & Garner" → **Fourman S, Fourman MB** (não existe Garner)
- Barbados 42 → **40 mmHg** (RR 2,6)
- Atribuição falsa dos regimes anti-VEGF ao plano; T&E corrigido para 13 injeções / 6,3 sem
- Provenância por parâmetro no coelho, com $Q_{prod}=3{,}06$ marcado **sem fonte**
- `PAD_oftalmica` virou opt-in (padrão não estima) → o teste que falhava volta a passar
- `np.trapezoid` → shim de compatibilidade (numpy 1.26 do container)

## Não bloqueantes

Hipotonia 6 → 6,5 ou 5 mmHg · estimador de `T_acima_*` por interpolação · modelo de estado
no 4.5 · rotular $\phi_{vasc}$ e $\text{PAD}_{oft}$ como formas supostas · citação completa
do PMC13307848 · fonte do "modelo SF do rato" ou remover o 4.5 · autoria
Tobalem/Schutz/**Chronopoulos** · declarar que q12s/q16s são proporções de pacientes

---

# Como rodar os testes

A VM não tem pytest/scipy; precisa do container:

```bash
docker compose run --rm fsi bash -lc 'pip install pytest numpy scipy --break-system-packages && cd /simulation/claude-wp4 && python3 -m pytest . -q'
```
