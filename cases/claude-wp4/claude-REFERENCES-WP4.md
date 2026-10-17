# WP4 — referências verificadas e o que corrigir

Resultado da checagem das fontes citadas no WP4. Cada item traz: a citação completa,
o que foi **verificado na fonte**, e o que **não foi**. Nada aqui é estimativa minha.

**Convenção de confiança** (a que o plano exige na Seção 2.3):
`[V]` verificado na fonte primária · `[V2]` verificado em fonte secundária, confirmar no
primário · `[NF]` não encontrado / sem fonte.

---

## 1. Parâmetros de vazão — coelho (o conflito 0,26 vs 0,57 está resolvido)

### Conclusão: **0,26 é o valor medido. 0,57 não tem fonte.**

**`[V]` Fourman S, Fourman MB.** "Correlation of tonography and constant pressure
perfusion measurements of outflow facility in the rabbit." *Curr Eye Res.*
1989;8(9):963–969. DOI 10.3109/02713688909082658. PMID 2791636.

- Coelhos New Zealand White.
- Tonografia: **0,26 ± 0,07** µL/min/mmHg.
- Perfusão a pressão constante: **0,26** µL/min/mmHg. *(O resumo imprime "± 0,6", quase
  certamente erro tipográfico de ±0,06 — não propagar esse desvio.)*
- Correlação entre os métodos: r = 0,914, p < 0,001.

**Três consequências para a tese:**

1. **Corrigir o nome dos autores.** O código cita "Fourman & Garner 1989" — **não existe
   Garner**. São Fourman S e Fourman MB.
2. **Os dois métodos concordam** (0,26 em ambos), então a divergência de 2,2× contra o
   0,57 do plano **não pode** ser atribuída a tonografia-vs-perfusão.
3. **O rótulo "coelho anestesiado" em 0,26 não está verificado.** Fourman estudou NZW sem
   que eu tenha confirmado o estado anestésico no resumo. E o comparador consciente é
   **mais baixo**, não mais alto (ver abaixo) — então anestesia também não explica 0,57.

**`[V]` Zhao M, Hejkal JJ, Camras CB, Toris CB.** "Aqueous humor dynamics during the day
and night in juvenile and adult rabbits." *Invest Ophthalmol Vis Sci.*
2010;51(6):3145–3151. DOI 10.1167/iovs.09-4415.

- Coelhos **conscientes** (contidos manualmente).
- Facilidade: **0,14 ± 0,02** (adulto, dia); **0,10 ± 0,02** (noite); **0,20 ± 0,03**
  (juvenil, dia).
- Fluxo de aquoso: **1,46–2,53** µL/min. IOP: 14,5–20,9 mmHg.
- EVP não medida (assumiram valores publicados de 10 e 12 mmHg).

**`[NF]` $C_{out}$ coelho = 0,57 µL/min/mmHg** — **nenhuma fonte publicada encontrada.**
Observação relevante: 0,57 é reproduzível aritmeticamente do balanço de Goldmann com
Q = 3,06 e (IOP − P_ev) ≈ 5,4 mmHg, ou seja, **parece ser número derivado, não medido**.
Até aparecer referência, tratar como sem fonte — e isso significa corrigir a lista de
hedges do plano (linha 839), não o código.

### Pressão venosa episcleral — confirmada

**`[V]` Kiel JW, Kopczynski CC.** "Effect of AR-13324 on episcleral venous pressure in
Dutch Belted rabbits." *J Ocul Pharmacol Ther.* 2015;31(3):146–151.
DOI 10.1089/jop.2014.0146.

- Coelhos **anestesiados**: **EVP 16 ± 1 mmHg**; IOP 33 ± 3; MAP 101 ± 3.
- **Sustenta o $P_{ev} \approx 15{,}5$–16 mmHg** usado no código ✓.
- Não reporta facilidade nem taxa de formação — **não serve para citar 0,26 nem 0,57**.

**`[V]` Kiel JW, Hollingsworth M, Rao R, Chen M, Reitsamer HA.** "Ciliary blood flow and
aqueous humor production." *Prog Retin Eye Res.* 2011;30(1):1–17.
DOI 10.1016/j.preteyeres.2010.08.001. *(Citação confirmada; texto completo não acessado —
**não citar como fonte de 0,26 ou 0,57** sem ler.)*

### **Problema novo que eu não havia detectado: $Q_{prod}$ do coelho não tem fonte**

**`[NF]` $Q_{prod} = 3{,}06$ µL/min (coelho)** — nenhuma fonte localizada. O fluxo
publicado que consegui verificar é **1,46–2,53 µL/min** (Zhao 2010, consciente), ou seja
**3,06 está acima da faixa medida**.

Isso importa porque $P_0$ do coelho é derivado desse número:

| $Q_{prod}$ | fonte | $P_0$ derivado (com $P_{ev}$=15,5, $C_{out}$=0,26, $f_{uv}$=0,05) |
|---|---|---|
| 3,06 | **`[NF]`** | **26,68 mmHg** (valor hoje no código) |
| 2,53 (topo da faixa medida) | `[V]` Zhao 2010 | 24,74 mmHg |
| 2,00 (meio da faixa) | `[V]` Zhao 2010 | 22,81 mmHg |
| 1,46 (base da faixa) | `[V]` Zhao 2010 | 20,84 mmHg |

**Quase 6 mmHg de amplitude na basal do coelho**, dependendo de um número sem fonte.

**Alerta de mistura de condições:** $C_{out}$ e $Q_{prod}$ de Zhao são de coelho
**consciente**; o $P_{ev}$ de Kiel é de coelho **anestesiado**; Fourman não teve a
condição confirmada. Combinar os três num só $P_0$ mistura condições experimentais — é
exatamente o tipo de erro entre espécies/condições que o registro de auditoria do plano
diz ter passado uma vez sem ser notado. **Declarar a condição de cada parâmetro.**

### Humano — único parâmetro já rastreável ao plano

**`[V2]` Goel et al. 2010** — fração uveoescleral humana ≈ 20%. É citado no próprio plano
(nota de auditoria sobre o erro de usar fração humana em coelho) ✓. $C_{out}$ = 0,28 e
$P_{ev}$ = 10 constam da lista de hedges do plano.

---

## 2. Regimes de anti-VEGF (item 4.5) — todos verificados, e um número a corrigir

O código atribui esses regimes "ao plano (Seção 4.5)". **O plano não os contém** (nem tem
Seção 4.5). As fontes primárias reais:

**`[V]` Dugel PU, Koh A, Ogura Y, Jaffe GJ, Schmidt-Erfurth U, Brown DM, Gomes AV,
Warburton J, Weichselberger A, Holz FG.** "HAWK and HARRIER: Phase 3, Multicenter,
Randomized, Double-Masked Trials of Brolucizumab for Neovascular Age-Related Macular
Degeneration." *Ophthalmology.* 2020;127(1):72–84. DOI 10.1016/j.ophtha.2019.04.017.

**`[V]` Dugel PU, Singh RP, Koh A, Ogura Y, Weissgerber G, Gedif K, Jaffe GJ, Tadayoni R,
Schmidt-Erfurth U, Holz FG.** (96 semanas) *Ophthalmology.* 2021;128(1):89–99.
DOI 10.1016/j.ophtha.2020.06.028. PMID 32574761.

- `[V2]` **56% (HAWK) / 51% (HARRIER)** mantidos em q12s até a semana 48; desses,
  82%/75% seguiram em q12s até a semana 96. *(De revisão secundária — confirmar no PDF
  primário antes de citar.)*

**`[V]` Heier JS, Khanani AM, Quezada Ruiz C, Basu K, et al.** "Efficacy, durability, and
safety of intravitreal faricimab up to every 16 weeks for neovascular age-related macular
degeneration (TENAYA and LUCERNE)." *Lancet.* 2022;399(10326):729–740.
DOI 10.1016/S0140-6736(22)00010-1.

- `[V2]` Semana 48: **q16s em 45,7% (TENAYA) / 44,9% (LUCERNE)**; q12s em 34,0%/32,9%;
  ~80% em ≥q12s.

**`[V]` Gemenetzi M, Patel PJ.** "A Systematic Review of the Treat and Extend Treatment
Regimen with Anti-VEGF Agents for Neovascular Age-Related Macular Degeneration."
*Ophthalmol Ther.* 2017;6(1):79–92. DOI 10.1007/s40123-017-0087-5.

- Totais em 2 anos: **14,3 injeções** (Abedi: 8,6 + 5,7) e **13,0** (Arnold / Fight
  Retinal Blindness: 7,5 + 5,5). Mrejen: 8,3/ano ≈ intervalo médio de 6,3 semanas.

> **Corrigir no código:** o T&E está como `N_2anos = 12, intervalo 10 semanas`. As fontes
> dão **13,0–14,3 injeções em 2 anos** e intervalo médio de **~6,3 semanas**, não 10.
> Com 13 injeções a 6,3 semanas o T&E fica muito mais perto do mensal do que a tabela
> atual sugere — **isso muda a ordenação dos regimes**, que é a conclusão do item 4.5.

**Nota importante sobre a estrutura dos regimes.** q12s e q16s nos ensaios são
**proporções de pacientes que conseguiram manter o intervalo**, não o intervalo de todo
mundo. Modelar "brolucizumabe = 8 injeções a cada 12 semanas" trata ~51–56% da coorte
como se fosse 100%. Se o item 4.5 for para a tese, isso precisa estar declarado, ou
modelado como mistura de intervalos.

---

## 3. Limiares de pressão de perfusão (item 4.2)

**`[V]` Tielsch JM, Katz J, Sommer A, Quigley HA, Javitt JC.** "Hypertension, perfusion
pressure, and primary open-angle glaucoma: a population-based assessment." *Arch
Ophthalmol.* 1995;113(2):216–221. DOI 10.1001/archopht.1995.01100020100038. PMID 7864755.
*(Baltimore Eye Survey.)*

- `[V2]` Limiar **DOPP < 30 mmHg**, associado a risco ~**6×** maior de POAG. Confirmado
  em revisão, **não** no texto primário — conferir OR e IC no artigo.

**`[V]` Leske MC, Wu SY, Hennis A, Honkanen R, Nemesure B.** "Risk factors for incident
open-angle glaucoma: the Barbados Eye Studies." *Ophthalmology.* 2008;115(1):85–93.
PMID 17629563.

- `[V2]` RR de 2,0–2,6 para OPP sistólica/diastólica/média baixas.
- **O limiar de 42 mmHg não se confirma.** A fonte dá **MOPP < 40 mmHg → RR 2,6** e
  **DOPP < 53 mmHg → RR 2,2**. **Corrigir 42 → 40**, ou achar o primário do 42.
- Existe um seguimento dedicado: Leske et al., "Incident open-angle glaucoma and ocular
  perfusion pressure", PMID 21984728 (não acessado).

**Os dois são estudos crônicos**, populacionais, de prevalência/incidência de glaucoma ao
longo de anos (Baltimore transversal; Barbados incidência em 4 e 9 anos). **Nenhum estuda
evento pressórico agudo transitório.** Usá-los para um pico de minutos pós-IVI é erro de
categoria — o código já diz "documentação, NÃO calibração" ✓, mas a **tese** tem que
dizer isso explicitamente no texto, não só no comentário do código.

---

## 4. Item 4.4 — a peça que sustenta a conclusão não está verificada

**`[NF-parcial]` O estudo OCT-A "2026, n=54".** Existe um artigo com exatamente esse
assunto — *"Intraocular pressure spikes after intravitreal injection and their impact on
OCT angiography"*, **PMID 42565012, PMCID PMC13444746** — mas **não foi possível lê-lo**
(PubMed e PMC serviram CAPTCHA; Europe PMC, OpenAlex e Semantic Scholar devolveram 429).

Portanto, **permanecem não verificados**: n = 54, IOP 14 → 31 mmHg, "sem déficit
mensurável", e — o mais crítico — **se 31 mmHg é o pico de IOP ou a MOPP**.
**Não citar antes de ler o PDF.**

### Substituto verificado, e ele mostra exatamente por que a distinção importa

**`[V]` Colizzi B, Romano D, Lunardon S, Sabbatini L, Rossetti LM.** "Evaluation of
intraocular pressure and mean ocular perfusion pressure changes following intravitreal
anti-VEGF injections." *Eur J Ophthalmol.* 2025;35(4):1272–1279.
DOI 10.1177/11206721251318773. PMID 40539393. **n = 119 olhos.**

| | basal | imediato | 5 min | 30 min |
|---|---:|---:|---:|---:|
| **IOP** (mmHg) | 15,76 ± 4,34 | 49,79 ± 15,73 | 29,96 ± 10,55 | 21,80 ± 7,36 |
| **MOPP** (mmHg) | 54,02 ± 10,7 | 35,7 ± 19,7 | 40,68 ± 15,9 | 51,08 ± 12,2 |

**IOP sobe enquanto MOPP desce** — direções opostas, que é precisamente a confusão que o
`MOPP_min = 31,0 = pico de IOP` do item 4.4 sugere. Note que **~30 aparece aqui tanto
como IOP de 5 min quanto perto do vale da MOPP** — origem plausível de um "~31 mmHg"
conflacionado.

Achado adicional útil para o eixo (d): só **25% dos olhos glaucomatosos** voltaram à IOP
basal em 30 min, contra **48,9% dos não glaucomatosos** (p = 0,02).

**`[V]` Damasceno NA, Yannuzzi NA, Maia M, Farah ME, Flynn HW Jr, Damasceno EF.**
"Transient central retina artery occlusion in patients undergoing intravitreal anti-VEGF
injections." *Eur J Ophthalmol.* 2022;32(5):2819–2823. DOI 10.1177/11206721211066196.
PMID 34962172.

- 807 pacientes, **4.069 injeções**, **18 casos (0,44%)** — 14 leves (77,7%), 4 graves
  (22,3%); **obstrução carotídea ≥70% em 12/18 (66,6%)**, <70% em 6/18 (33,3%).
- **Os três números do código conferem exatamente** ✓. *(E 0,666 no código é 12/18 —
  melhor escrever como a fração para não parecer arredondamento arbitrário.)*

**`[NF]` "PMC13307848"** (afinamento retiniano de 25% aos 15 min, Peça 3) — citação
incompleta; um PMCID não é citação. Precisa de autor, título, revista, ano, DOI.

**`[NF]` "modelo SF do rato"** (forma funcional de todo o item 4.5) — **nenhuma fonte**.
É o elo mais fraco do WP4: a forma $SF = 1 - b(1-e^{-at})$ e a reinterpretação de SF como
"fração de dano que persiste" não têm referência alguma.

---

## 5. Lista de correções, em ordem

| # | O que | Onde |
|---|---|---|
| 1 | Remover a citação inexistente atribuída ao plano | `validacao_zero_observado.py`, docstring |
| 2 | "Fourman & Garner 1989" → **Fourman S, Fourman MB 1989** | `dose_isquemica.py`, comentário de `_PARAMS_LITERATURA` |
| 3 | Manter $C_{out}$ coelho = **0,26** (medido); marcar **0,57 do plano como sem fonte** e corrigir o plano | código + plano linha 839 |
| 4 | Remover o rótulo "anestesiado" não verificado de 0,26; declarar a condição de cada parâmetro | `dose_isquemica.py` |
| 5 | Marcar $Q_{prod}$ coelho = 3,06 como **`[NF]`** e reportar a faixa medida 1,46–2,53 com o $P_0$ resultante | `dose_isquemica.py` |
| 6 | Barbados: **42 → 40 mmHg** | `dose_isquemica.py`, docstring |
| 7 | Declarar Baltimore/Barbados como estudos **crônicos** no texto da tese | tese |
| 8 | Substituir o OCT-A 2026 por **Colizzi 2025** como âncora, ou ler o PMID 42565012 antes de citar | `validacao_zero_observado.py` |
| 9 | T&E: **13,0–14,3 injeções/2 anos, intervalo ~6,3 sem** (não 12 a cada 10 sem) | `dose_cumulativa.py` |
| 10 | Citar HAWK/HARRIER e TENAYA/LUCERNE; declarar que q12s/q16s são **proporções de pacientes** | `dose_cumulativa.py` |
| 11 | Obter fonte do "modelo SF do rato" ou remover o item 4.5 | `dose_cumulativa.py` |
| 12 | Completar a citação de "PMC13307848" | `validacao_zero_observado.py` |
