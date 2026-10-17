# Revisão de engenharia de simulação — WP1.4

Revisado: `cases/wp1.4/sweep_full/` (pipeline oficial, Composer) e `cases/claude-wp1.4-sweep/`
(pipeline anterior, meu). Nenhum arquivo do Composer foi alterado.

---

## 1. O que está correto — verificação independente

Antes das críticas: **a cadeia FE em si está sã.** Fiz uma verificação que não existia no
pipeline — regressão log-log dos 300 resultados contra a lei de casca fina
$dP/dV = tE/[2\pi R^4(1-\nu)]$:

| expoente | teoria | obtido |
|---|---:|---:|
| $R$ | $-4$ | $-4{,}030$ |
| $t$ | $+1$ | $+1{,}087$ |
| $\mu_1$ | $+1$ | $+1{,}055$ |
| $\alpha_1$ | — | $-0{,}013$ |

$R^2 = 0{,}975$ (o resto é o conteúdo não linear, esperado). Malha, material, condições de
contorno e extração P–V reproduzem a escala analítica. Isso é a melhor evidência de que o
núcleo do WP1.4 funciona — **sugiro colocar essa tabela na tese**, é verificação no espírito
do WP1.1 e hoje não existe para o WP1.4.

Também conferido e correto: 300/300 convergidos; `S8R` igual ao WP1.1/WP1.2; `ne=8` → 512
elementos equivalentes, exatamente a malha aprovada no WP1.2; `D1` amarrado a $\mu_1$ mantém
$\nu_{ef}\approx0{,}38$ constante em toda a varredura (coerente com a ressalva já declarada no
seu texto); só `*HYPERELASTIC` é emitido para Ogden, sem `*ELASTIC` perdido; balanço
categórico perfeito (100/100/100 cristalino, 150/150 vitrectomia); calota polar de 3° = 0,07%
da área, igual ao WP1.1; `K_eff` é a secante do primeiro incremento acima de $P_0$, que é a
definição de $K=dP/dV|_{\text{basal}}$ do plano.

---

## 2. BLOQUEANTE — três números inventados, e eles são de primeira ordem

Violam a regra de ouro do plano ("proibido: multiplicadores fenomenológicos... se não houver
fonte, o parâmetro não entra"). Os três estão em `scripts/case_model.py`.

### 2.1 `vit_dv_scale = 1.085` — o mais grave

```python
vit_dv_scale = 1.085 if vit else 1.0   # case_model.py
...
for r in pv_rows: r["dV_uL"] = r["dV_uL"] * scale   # run_sweep.py
```

Três problemas somados:

1. **Sem fonte.** Os 8,5% não vêm do plano, de referência nenhuma, nem de resultado do projeto.
2. **A justificativa é um não-sequitur físico.** `MODELING_NOTES.md` diz "BSS menos viscoso →
   maior incremento de volume aparente". Viscosidade não altera complacência volumétrica.
3. **Contradiz a própria H4 corrigida da sua tese.** O plano é explícito: "Gel vítreo e BSS são
   ambos praticamente incompressíveis... Não há razão para o pico elástico diferir", e a H4
   falseável diz $K_{\text{vitrectomizado}} \approx K_{\text{controle}}$, com a diferença em
   $R_{\text{ref}}$, não em $K$. O código faz exatamente o que a hipótese diz que não acontece.

**Quantifiquei o dano.** Controlando geometria (regressão de $\log K$ com dummy de vitrectomia):

- coeficiente observado: $-0{,}0797$
- esperado se for *só* o fator 1,085: $\log(1/1{,}085) = -0{,}0816$

Ou seja: **todo o sinal de vitrectomia do emulador é o constante inventado** (a diferença
residual é confundimento da lei de potência imperfeita, não física extra). Mesma coisa em
`V_max`: $+0{,}0794$ vs $+0{,}0816$ esperado.

E o fator entra em `K_eff` também, porque é aplicado a todos os `dV` antes do cálculo da
secante — então $K_{vit} = K/1{,}085$ por construção. Isso vai direto para
$\Delta V = \Delta\text{IOP}/K$ do WP5 e para o posterior do WP6.

**Correção:** `vit_dv_scale = 1.0`, declarar que casca de uma camada não tem via mecânica para
vitrectomia, e levar vitrectomia para onde a H4 manda — $R_{\text{ref}}$ no WP0.

### 2.2 `dr_acd = −0,11 × (ACD − 3,25)`

Coeficiente $-0{,}11$ e nominal $3{,}25$ mm sem fonte. Efeito medido na sensibilidade OAT do
próprio pipeline: $\pm4{,}5\%$ em `V_max`. Como $R$ entra em $K$ com expoente $-4$, o
deslocamento total inventado de $R$ (até $0{,}485$ mm, 4,3% de $R$) implica **até 18% em $K$**.

Além de não ter fonte, não tem mecanismo: ACD não enrijece nem amolece uma casca de uma
camada. E o sinal é contraintuitivo — câmara anterior mais rasa deixa o olho *mais mole*.
Pior: ACD e comprimento axial são amostrados como independentes no LHS, quando anatomicamente
$AL = ACD + \text{espessura do cristalino} + \text{profundidade vítrea}$.

### 2.3 `LENS_DR_MM = {phakic: 0, pseudophakic: −0,22, aphakic: +0,35}`

Mesmo problema. Efeito: $-7{,}0\%$ e $+11{,}9\%$ em `V_max` (tabela de sensibilidade do
pipeline). Afácico fica 12% mais complacente só por um deslocamento de raio sem referência.

### 2.4 Consequência conjunta

**Três dos oito inputs (ACD, cristalino, vitrectomia) não têm via mecânica nenhuma num modelo
de casca esférica.** Eles ganharam uma via por três constantes inventadas, e o emulador aprende
essas constantes com fidelidade. A "análise de sensibilidade" do WP1.4, para esses três inputs,
não mede física — mede os números que foram digitados.

Isso é exatamente o que o WP1.5 existiria para responder, e o WP1.5 foi (corretamente) cortado.
A saída honesta não é inventar um proxy: é declarar que esses três inputs entram na calculadora
clínica mas **não têm efeito em $K$** neste modelo, e que ACD volta no WP5 pela restrição
$ACD_{\min}$ medida no Ensaio D.

---

## 3. Erros técnicos

### 3.1 O pickle do emulador está inconsistente — vai dar predição errada silenciosa

`train_emulator.py` monta `X` com **10 colunas** (6 contínuas + 3 one-hot de cristalino + 1 de
vitrectomia):

```python
X = np.zeros((n, len(INPUT_COLS) + 4))
```

mas grava no pickle só os **6 nomes** de `INPUT_COLS`, e a ordem do one-hot não é registrada em
lugar nenhum:

```python
pickle.dump({"model":..., "scaler":..., "input_cols": INPUT_COLS, "target": name}, fh)
```

Quem carregar o emulador seguindo `input_cols` — o WP5, o WP6, ou você em três meses — passa 6
colunas para um modelo que exige 10. Ou quebra, ou (se alguém preencher o resto) devolve número
errado sem avisar. **Corrigir antes de qualquer uso downstream:** gravar a lista completa das 10
colunas e o codificador.

### 3.2 O critério de <5% é avaliado na média, e o `V_max` reprova no pior ponto

```python
"passes_5pct_criterion": float(np.mean(rel)) < 5.0
```

Relatado em `emulator_report.json`:

| alvo | erro médio | **erro máximo** | marcado como |
|---|---:|---:|---|
| `V_max_uL` | 0,48% | **5,96%** | PASS |
| `K_eff` | 0,38% | 4,94% | PASS |

O emulador de `V_max` **não cumpre <5% no pior ponto**, e o relatório diz PASS. O "erro CV
<0,4%" que circula como resultado é a média. Para um emulador que vai dentro de calibração
bayesiana e de calculadora clínica, o critério tem que ser avaliado na cauda. Reportar
média, p95 e máximo, e dizer a qual deles o critério se aplica.

### 3.3 A espessura posterior está sendo aplicada também no polo anterior

O octante é $\theta\in[\theta_{\min},90°]$, $\varphi\in[0,90°]$ — **um polo só** — e o plano
$z=0$ é plano de simetria (`SYM_Z`, `volume_scale=8`). Então, ao espelhar, `t_posterior` cai
também onde ficaria a **córnea**.

Resultado: a varredura varia "espessura escleral posterior" de 0,6 a 1,2 mm e aplica esse
valor numa região que anatomicamente é córnea (mais fina e muito mais complacente). A
sensibilidade reportada para esse parâmetro ($+16{,}8\%$ / $-10{,}8\%$ em `V_max`) é em parte
artefato. A geometria de octante com simetria equatorial **não consegue** ter polo anterior
diferente do posterior — isso precisa ser declarado como limitação, não contornado.

### 3.4 Não há verificação de independência de malha para a configuração de espessura variável

A convergência do WP1.2 foi estabelecida com $t$ uniforme, $R=12$, $t=0{,}5$. A varredura roda
$R\in[10;15]$ e $t\in[0{,}3;1{,}2]$ — $t/R$ varia ~4×, e o termo de 2ª ordem que o próprio
WP1.1 identificou escala com $(t/R)^2$. Nenhum caso da varredura tem checagem de malha
(os arquivos `*_mesh.*` são a malha incluída, não um refinamento de controle).

Agravante estrutural: **o número de faixas de espessura é igual a `ne`** (8 faixas com `ne=8`).
Refinar a malha refina também a discretização de $t(\theta)$, então os dois efeitos não podem
ser separados como o código está. Mínimo necessário: rodar os cantos da caixa de projeto em
`ne` = 8, 10, 12 e reportar $\varepsilon_i$, com o número de faixas desacoplado de `ne`.

---

## 4. Consistência e escopo

- **O amostrador LHS não está no pipeline oficial.** `generate_lhs_samples.py` só existe em
  `claude-wp1.4-sweep/scripts/`; `wp1.4/sweep_full/scripts/` não regenera o próprio
  planejamento de experimentos. Problema de reprodutibilidade — mover para lá.
- **`mu1_factor`/`alpha1_factor` ∈ [0,5; 1,5] são placeholder.** O plano pede "±2 DP do ajuste
  suíno"; o dado suíno não existe. ±50% não é ±2 DP de nada medido — declarar como provisório,
  a ser substituído após o WP2.
- **$\alpha_1$ é um input morto.** Expoente $-0{,}013$ na minha regressão, OAT <0,1%. É
  consistente com o seu próprio WP1.2 (multi-start: $\alpha_1$ de 0,51 a 6,00 com curvas
  indistinguíveis). Não é erro, mas infla a dimensionalidade aparente e embeleza as métricas do
  GP. Ou tira, ou declara que foi mantido justamente para mostrar a insensibilidade.
- **Yeoh desapareceu.** O WP1.2 conclui "Ogden e Yeoh mantidos em paralelo"; a varredura é só
  Ogden. Isso precisa de justificativa explícita — e existe uma boa: o WP1.3 mostrou efeito de
  pré-tensionamento <1% no Ogden contra ~6%/−4% no Yeoh, então rodar sem MULF só se sustenta no
  Ogden. Escrever isso fecha os dois pontos de uma vez.
- **A caixa de projeto inclui olhos impossíveis.** 13% dos casos têm $K<0{,}15$ mmHg/µL, o que
  implica $\Delta$IOP de 2,9–7,5 mmHg para 50 µL — contra os 30–36 mmHg de pico do Knecht que o
  próprio plano usa como faixa de validação. 18% precisam de >200 µL para chegar a 50 mmHg. A
  faixa de $K$ cobre 27×, e é essa amplitude que faz o $R^2$ parecer 0,9999. Sugiro reportar as
  métricas também restritas à sub-região clinicamente plausível.
- **As curvas P–V não foram salvas no JSON.** `save_results` descarta `pv_curve`, então
  $\Delta$IOP para 50 µL fixos — que é exatamente a grandeza da H1 — não está nos resultados.
  **Recuperável sem re-simular:** os `.frd` sobreviveram em `output_sweep/ccx_runs/`, basta
  re-rodar `extract_pv`.

---

## 5. Sobre o meu pipeline anterior (`claude-wp1.4-sweep`) — para registro

Para ser justa a comparação: o meu tinha os seus próprios defeitos, e um deles o Composer
corrigiu bem.

- **Eu tinha número inventado também:** `t_mm = 0.55*t_equatorial + 0.45*t_posterior`, com
  malha uniforme. Os pesos 0,55/0,45 não têm fonte — é o mesmo tipo de erro que critico acima. O
  $t(\theta)$ com transição cosseno e seções por faixa do Composer é **genuinamente melhor**.
- **Mas eu deixava ACD sem uso:** "ACD_mm armazenada para uso futuro com geometria que inclua
  câmara anterior". Isso era incompleto, porém honesto. O pipeline oficial transformou um input
  sem uso em um mecanismo fabricado — essa é a regressão.
- **Os dois discordam muito e nada arbitra.** O `RESULTS.md` do Composer registra a comparação:
  média $+13{,}3\%$, desvio $11{,}8\%$, **máximo $48\%$** em `V_max`. Duas implementações do
  mesmo WP diferindo até 48%, sem verificação independente para decidir qual está certa. A
  regressão da Seção 1 é o começo dessa arbitragem; a diferença restante vem justamente dos
  itens inventados da Seção 2.

---

## 6. Ordem de correção sugerida

1. Zerar os três constantes inventados (`vit_dv_scale`, `dr_acd`, `dr_lens`) e declarar
   ACD/cristalino/vitrectomia como sem via mecânica nesta geometria. **Requer re-rodar os 300
   casos** — cada caso levou ~1–2 min, é viável.
2. Corrigir o pickle (10 colunas + codificador) e o critério de aceitação (média vs máximo).
3. Declarar a limitação do polo anterior (Seção 3.3) no texto.
4. Checagem de malha nos cantos da caixa, com faixas de espessura desacopladas de `ne`.
5. Mover o amostrador LHS para o pipeline oficial; declarar ±50% como provisório.
6. Recuperar as curvas P–V dos `.frd` para ter $\Delta$IOP a 50 µL (H1).
7. Acrescentar a tabela de expoentes da Seção 1 como verificação do WP1.4.
