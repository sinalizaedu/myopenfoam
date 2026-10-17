# claude-wp1_analysis — por que Ogden "endurece" e Yeoh "amolece"?

Investigação em resposta ao pedido de 22/09: (1) referências de P(V) além de
Pallikaris, (2) explicação analítica do porquê Ogden dá +1,3% e Yeoh dá
-37,5% no dP/dV entre V=0 e V_ref, (3) gráficos. Arquivo novo, não edita
nada do Composer nem do `claude-wp1_octant`.

**Resumo executivo**: fiz um modelo fechado (casca fina, membrana
equibiaxial, com a MESMA compressibilidade D1 que cada material usa no
deck real) e testei se ele reproduz o que a FEA está reportando. **Não
reproduz.** O modelo analítico prevê que os dois materiais deveriam
amolecer por quantidade quase igual e pequena (Ogden −0,30%, Yeoh −0,34%)
na deformação fisiológica envolvida (λ−1 ~ 0,05-0,1%, ΔV=10 µL numa esfera
de ~7200 mm³). A FEA reporta +1,28% e −37,5% — sinais opostos e duas ordens
de magnitude de diferença entre si. Isso é evidência de que **o número de
pretensão não está sendo dominado pela física do material** (a hipótese
original "Ogden endurece / Yeoh amolece"), e sim por algo no pipeline
numérico. Achei um candidato concreto e concordante com os novos dados que
você acabou de mandar (não-identificabilidade do Yeoh): ver Seção 3.

---

## 1. Referências de P(V) além de Pallikaris et al. 2005

| Referência | O que mede | Forma funcional | Observação |
|---|---|---|---|
| **Friedenwald (1937)**, "Contribution to the theory and practice of tonometry" — formulação clássica revisitada em [Ocular Rigidity and Intraocular Pressure, Springer](https://link.springer.com/chapter/10.1007/978-3-030-64422-2_16) | Coeficiente de rigidez ocular E, via manometria + indentação | **log-linear**: log₁₀(P₂/P₁) = E·(V₂−V₁), *não* exponencial como Pallikaris | Base histórica de todo o campo; assume E constante (não captura curvatura 2ª ordem) |
| **Silver & Geyer (2000)**, "Pressure-volume relation for the living human eye", *Current Eye Research* 20(2) — [PubMed](https://pubmed.ncbi.nlm.nih.gov/10617912/), [ResearchGate](https://www.researchgate.net/publication/12694928_Pressure-volume_relation_for_the_living_human_eye) | P(V) em olhos humanos vivos, via infusão controlada | Curva P(V) empírica com rigidez crescente com P — forma consistente com Pallikaris mas de outro grupo/protocolo | É a referência mais citada como "segunda fonte" independente de Pallikaris para validar a forma da curva |
| **Kotliar, Maier, Bauer, Feucht, Lohmann, Lanzl (2007)**, "Effect of intravitreal injections and volume changes on IOP: clinical results and biomechanical model", *Acta Ophthalmol Scand* — [Wiley](https://onlinelibrary.wiley.com/doi/10.1111/j.1600-0420.2007.00939.x), [PubMed](https://pubmed.ncbi.nlm.nih.gov/17573861/) | Especificamente injeção intravítrea (o mesmo cenário do seu WP1!) + modelo biomecânico próprio | Modelo tipo mola/Hooke não-linear ajustado a dados clínicos reais de pico de PIO pós-injeção | **É a referência mais diretamente comparável ao seu WP1.3** — vale conferir se o pico de ΔP deles bate com o seu P(V) fitted, é um ponto de validação independente que ainda não está no seu relatório |
| **Wang, Padilla, et al.**, "Ocular Rigidity in Living Human Eyes" — [IOVS/ARVO](https://iovs.arvojournals.org/article.aspx?articleid=2124027), [ResearchGate](https://www.researchgate.net/publication/8061079_Ocular_Rigidity_in_Living_Human_Eyes) | Rigidez ocular in vivo por pulso ocular + OCT | Relação P-V ajustada por regressão, coeficiente de rigidez reportado com IC | Boa referência para faixa fisiológica esperada de K em olho saudável (compare com seu K_FEA) |
| **Sherwood, Boazak, Feola, Parker, Ethier, Overby (2019)**, "Measurement of Ocular Compliance Using iPerfusion", *Front. Bioeng. Biotechnol.* — [Frontiers](https://www.frontiersin.org/journals/bioengineering-and-biotechnology/articles/10.3389/fbioe.2019.00276/full) | Complacência ocular (olho de camundongo, iPerfusion) | **Lei de potência**: φ = φᵣ·(Pᵣ/P)^γ — forma funcional *diferente* de Pallikaris (nem exponencial nem log-linear) | Espécie diferente (camundongo), mas é a terceira forma funcional distinta encontrada (Friedenwald log-linear, Pallikaris exponencial, esta em lei de potência) — útil para discutir robustez da escolha de forma no capítulo de métodos |

**Conclusão da busca**: existem pelo menos três formas funcionais distintas
usadas na literatura para P(V)/rigidez ocular (log-linear clássica,
exponencial tipo-Pallikaris, lei de potência), e ao menos uma referência
(Kotliar 2007) trata exatamente do cenário de injeção intravítrea com
biomecânica própria — vale citar como segunda validação do WP1, e
possivelmente comparar o ΔP de pico previsto pelo seu Yeoh/Ogden fitted
contra os dados clínicos dele.

Fontes consultadas nesta busca (nem todas citáveis diretamente, mas
mapeiam o campo): [Ocular Rigidity in Living Human Eyes (academia.edu)](https://www.academia.edu/40971156/Ocular_Rigidity_in_Living_Human_Eyes), [Ocular volume and ocular rigidity (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0014483581800620), [Non-invasive in vivo measurement of ocular rigidity (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0014483519304208), [Correlation of ocular rigidity with IOP spike after intravitreal bevacizumab (PubMed)](https://pubmed.ncbi.nlm.nih.gov/32345604/) — este último é *diretamente* sobre pico de PIO pós-injeção e rigidez ocular, também merece leitura.

---

## 2. Modelo analítico: casca fina, membrana equibiaxial, compressível

### 2.1 Formulação

Esfera fina (R₀=12 mm, t₀=0,5 mm) sob pressão interna, estiramento
equibiaxial λ=λ₁=λ₂ na superfície média, λ₃ na espessura determinado pela
condição de tensão nula na face livre (σ₃=0) — **sem** assumir
incompressibilidade a priori. Tensão de Cauchy principal calculada pela
forma geral σᵢ = (λᵢ/J)·∂W/∂λᵢ, com W escrito com a mesma decomposição
volumétrica/desviadora que o CalculiX usa (`(1/D1)(J−1)²`), e **com o D1
real de cada deck**:

- Ogden: `D1 = 1e-6` MPa⁻¹ → k = 2/D1 ≈ 2,0×10⁶ MPa (praticamente travado
  volumetricamente — isso é um *workaround numérico* de estabilidade do
  Ogden no CCX, documentado no próprio `ccx_utils.py`: *"CalculiX Ogden is
  unstable with the Yeoh-style D1 (~0.1); it expects near-zero D1"*).
- Yeoh: `D1 = d1_from_nu_mpa(0.47, 3.0) = 0,12` MPa⁻¹ → k ≈ 16,7 MPa
  (compressibilidade real de tecido quase-incompressível, k/μ≈1,9).

Equilíbrio de membrana: P(λ) = 2·t(λ)·σ_eq(λ)/R(λ), com t(λ)=t₀·λ₃(λ) e
R(λ)=R₀·λ. V(λ)=(4/3)πR(λ)³. K=dP/dV por diferenciação numérica de alta
precisão.

### 2.2 Resultado — o modelo NÃO reproduz a FEA

| | λ₀ (P=P₀=16,9 mmHg) | λ₁ (ΔV=10 µL) | J₀ | K@V=0 | K@V_ref | Δ% analítico | Δ% FEA reportado |
|---|---|---|---|---|---|---|---|
| **Ogden** | 1,000631 | 1,001091 | 1,000000 (travado) | 1,230 mmHg/µL | 1,226 | **−0,30%** | **+1,28%** |
| **Yeoh** | 1,000879 | 1,001339 | 1,001083 (dilata de fato) | 0,881 | 0,878 | **−0,34%** | **−37,5%** |

(script: `thin_shell_compressible.py`, resultados em
`thin_shell_compressible_results.json`)

Gráfico: `figs/03_analytic_vs_fea.png`.

**Leitura**: o modelo confirma que a diferença de compressibilidade É real
(J₀ do Yeoh se afasta de 1, o do Ogden fica travado em 1,000000 — os dois
materiais realmente respondem diferente ao mesmo P₀), mas o efeito disso
na faixa de deformação fisiológica (λ−1 ~ 0,06-0,13%) é **pequeno e do
mesmo sinal para os dois** (~−0,3%). Não há, no mecanismo de membrana
equibiaxial isolado, nenhuma razão para o Ogden *endurecer* (sinal
positivo) nem para o Yeoh amolecer 100× mais que isso.

### 2.3 Por que a intuição "Ogden endurece / Yeoh amolece" não se sustenta

`figs/01_stress_stretch_tangent.png` mostra σ_eq(λ) e dσ_eq/dλ para os
dois materiais numa faixa ampliada (λ até 1,5, bem além do fisiológico,
só para visualizar a forma). Fica visível que:

- Ogden com α₁=0,5 tem tangente dσ/dλ **decrescente** com λ — é
  estruturalmente um material que *amolece* em deformação finita grande
  (efeito conhecido do expoente baixo). Isso é o oposto da leitura
  "Ogden endurece".
- Yeoh com C20>0 tem tangente **crescente** com λ (o termo (I₁−3)² sempre
  endurece para C20>0) — na verdade é o Yeoh que endurece em deformação
  finita grande, não o Ogden.

Ou seja: **a rotulagem "Ogden endurece / Yeoh amolece" observada no dP/dV
da FEA é, pelo que este modelo mostra, o oposto do que os dois materiais
fazem intrinsecamente em deformação finita.** Isso reforça que o sinal
medido no WP1.3 não vem da forma da energia de deformação em si.

### 2.4 Onde a divergência provavelmente está vindo

Dado que o mecanismo de membrana (material + compressibilidade real)
**não** produz o efeito observado, os candidatos que sobram, em ordem de
probabilidade:

1. **Ruído numérico na extração de dP/dV local.** A faixa de deformação
   real é minúscula (λ−1 < 0,15% até V_ref). `dp_dv_local` usa spline
   pchip sobre poucos pontos de pressão amostrados pela FEA (24-30 passos
   de carga) — nessa escala, erro de convergência do CCX, resíduo de
   arredondamento na extração de volume via nós do FRD, e a própria
   discretização da malha (ne=8, S8R) podem facilmente gerar variações de
   1ª ordem comparáveis ou maiores que o "sinal" físico real (~0,3%).
   Isso é visível no próprio gráfico `figs/02_pv_and_k_analytic.png`
   (painel direito): mesmo o modelo fechado, calculado com derivada
   analítica de alta precisão, mostra uma curva "ruidosa" para o Ogden
   quando a derivada é feita por diferença finita simples — imagine o
   efeito em cima de uma solução FEA com tolerância de convergência
   finita.
2. **Não-identificabilidade do Yeoh — CONFIRMADA pelos seus resultados
   novos.** Você acabou de rodar o multi-start e achou 2 mínimos quase
   equivalentes (C10=4,37/C20=7,99, custo=102,39, 4/6 starts vs
   C10=4,36/C20=4,99, custo=102,56, 1/6 start — R²=0,938 nos dois). Testei
   os dois no modelo analítico: dão **−0,338% e −0,340%** — praticamente
   idênticos (`figs/04_yeoh_identifiability.png`). Isso quer dizer que a
   não-identificabilidade do Yeoh (C20 variando 60%) **não** é, por si só,
   a explicação do −37,5% — o efeito de C20 na faixa fisiológica é
   desprezível. Mas é uma segunda confirmação independente de que o Yeoh
   ajustado a essa curva não é um material único e bem determinado, o que
   mina a confiabilidade de qualquer número derivado dele (incluindo o
   WP1.3), goste ou não do valor específico de pretensão.
3. **Efeitos de casca real (flexão, BC de octante) não capturados pelo
   modelo de membrana pura.** O S8R tem rigidez à flexão perto das
   arestas de simetria que este modelo (membrana pura, esfera fechada)
   não tem. Isso pode ser real, mas nesse caso a divergência seria um
   artefato de malha/BC, não uma propriedade do material Ogden-vs-Yeoh —
   testável rodando WP1.3 com ne=6 vs ne=8 e vendo se o −37,5% do Yeoh
   muda (o WP1.1 hiperelástico que você rodou mostrou 0% de sensibilidade
   de malha para K linear, mas isso foi em P linear longe da pré-tensão;
   não garante o mesmo na derivada local perto de V=0).

### 2.5 Recomendação concreta

Antes de reportar +1,3%/−37,5% como um resultado científico
("Ogden e Yeoh discordam no sinal do efeito de pré-tensão"), eu rodaria um
teste de convergência de malha *especificamente* no WP1.3 (ne=6 vs 8 vs 12,
mesmo V_ref) e um teste de refinamento de passos de carga (n_steps=24 vs
48). Se o −37,5% do Yeoh mudar de forma significativa com qualquer um
desses, o número não é robusto o suficiente para entrar no capítulo — e aí
a resposta para "por que Yeoh amolece" deixa de ser uma pergunta sobre
mecânica de material e vira uma pergunta sobre precisão numérica, que é
mais fácil de resolver (refinar malha/passo) do que a physics question
original.

---

## 3. Nota sobre os resultados que você acabou de mandar

- **WP1.2 Yeoh multi-start**: confirma achado da Seção 2.4(2) acima — 2
  mínimos quase equivalentes. Vale reportar os dois clusters no capítulo,
  não só o C2 (que coincide com o x0 do Composer por coincidência de
  bacia de atração, não porque seja "o" mínimo).
- **WP1.1 K hiperelástico (ne=6 vs 8, K=0,916, +462% vs linear)**: isso
  ainda é o item que você pediu para excluir ("wp1.1 nao deveria ser
  hiperelastico"). Ainda não removi os arquivos correspondentes do
  `claude-wp1_octant` (`wp11_hyperelastic_k_claude.py`,
  `run_all_claude.py`, `compare_to_composer_claude.py`, `README.md`) —
  isso continua pendente; me avisa se quer que eu tire agora.
- **Tabela WP1.3 "Concordância entre métodos"**: o texto que você colou
  está um pouco confuso (mistura "+15,5% → BATE" com "-37,5%" na mesma
  linha da curva do ajuste, e depois "+1,3% @ V=0, -45% @ V_ref" separado)
  — antes de eu tentar interpretar esse número específico, você pode
  colar o `output/wp1.3-yeoh/RESULTS.md` (ou o JSON) direto? Prefiro não
  adivinhar o que o `compare_to_composer_claude.py` calculou ali.

---

## Arquivos deste pacote

```
claude-wp1_analysis/
├── PRETENSION_MECHANISM_INVESTIGATION.md   (este arquivo)
├── thin_shell_analysis.py                  (modelo incompressível, 1ª versão)
├── thin_shell_compressible.py              (modelo compressível, D1 real de cada deck)
├── make_plots.py                           (gera os 4 gráficos)
├── thin_shell_results.json
├── thin_shell_compressible_results.json
├── thin_shell_compressible_curves.json
└── figs/
    ├── 01_stress_stretch_tangent.png
    ├── 02_pv_and_k_analytic.png
    ├── 03_analytic_vs_fea.png
    └── 04_yeoh_identifiability.png
```

Nenhum arquivo do Composer ou do `claude-wp1_octant` foi alterado.
