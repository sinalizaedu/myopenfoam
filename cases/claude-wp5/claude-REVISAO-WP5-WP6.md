# Revisão de engenharia de simulação — WP5 e WP6

**Estado:** WP5 e WP6 **não existem como código**. Não há `cases/wp5/` nem `cases/wp6/`,
nem nada de paracentese/bayesiano/nomograma fora do termo `Q_paracentese` que já está no
solver do WP0. Então esta é uma revisão da **especificação** (Seções 5 e 6 do plano) e das
peças que o WP5/WP6 vão consumir — que é o momento certo de revisar, antes de construir.

Tudo que é aritmética eu recalculei. O script `claude_wp5_verificacao.py` roda essas
verificações (linhas de execução no fim deste documento).

---

## PARTE A — WP5 (protocolo de paracentese)

### A.1 A Seção 5.3 lineariza uma curva que a própria tese diz ser exponencial

Este é o achado principal, e muda a conclusão do capítulo.

O plano calcula o volume de paracentese por
$\Delta V_{\text{a retirar}} = (\text{IOP}_{atual} - \text{IOP}_{alvo})/K_{paciente}$ —
uma **linearização** com $K$ constante. Recalculei a tabela do plano e ela está
aritmeticamente correta:

| $K$ | origem | $\Delta V$ (50→15 mmHg) |
|---:|---|---:|
| 0,196 | casca fina linear (WP1.1) | 178,6 µL |
| 0,34 | intermediário | 102,9 µL |
| 0,44 | Friedenwald in vivo | 79,5 µL |

**Mas a tese adota uma lei exponencial** (WP1.2: "a curva de Friedenwald recalibrada é o
alvo adotado daqui em diante"), e com ela $dP/dV = \ln(10)\,K_f P$ — ou seja, **a rigidez
é proporcional à pressão**. O olho a 50 mmHg é muito mais rígido que a 15, então usar
$K$(basal) ao longo de todo o caminho de 50 até 15 **superestima** o volume necessário.

Integrando a curva em vez de linearizar, para a faixa de $K_f$ que o próprio plano lista
como literatura:

| $K_f$ | fonte | exponencial | linearizada | fator |
|---:|---|---:|---:|---:|
| 0,0126 | Pallikaris 2005 (limite inf.) | **41,5 µL** | 80,4 µL | 1,94× |
| 0,0215 | Friedenwald 1937 | **24,3 µL** | 47,1 µL | 1,94× |
| 0,0280 | limite sup. do plano | **18,7 µL** | 36,2 µL | 1,94× |

**A linearização superestima o volume por ~1,9× de forma sistemática.** E isso resolve
exatamente a tensão que o plano registra como "armadilha de consistência interna": a
tabela linearizada faz a paracentese parecer inviável (72% da câmara anterior), quando a
lei que a tese adota diz 7–17% — compatível com o fato clínico de que a paracentese é
usada e funciona, que é o teste de sanidade que o próprio plano exige.

**O que corrigir:** a regra de bolso $\Delta V = \Delta\text{IOP}/K$ não serve como
entregável do WP5. Substituir por $\Delta V = V(P_{atual}) - V(P_{alvo})$ com a $P(V)$
calibrada, ou pelo emulador invertido. A regra linear pode ficar como aproximação de
primeira ordem **declarada**, com o fator de 1,9× explícito.

### A.2 Inconsistência de $K_f$ entre capítulos — fator 2,2

O $K_f$ efetivamente adotado no WP1.2 é derivável do que o texto reporta
($P_0 = 16{,}9$ mmHg, 33,0 mmHg em 50 µL): $K_f = 0{,}005813$ µL⁻¹.

Isso está **abaixo do limite inferior da faixa de literatura que o plano lista**
(0,0126–0,0280) por **fator 2,2**.

Não é erro — é consequência deliberada da recalibração contra o pico de Knecht (o próprio
plano avisa que $K_f = 0{,}0126$ produz pico de 63 mmHg, bem acima dos 30–36 mmHg
observados). **Mas os dois números não podem coexistir na tese sem uma frase explícita**,
porque o volume de paracentese depende diretamente dele:

| $K_f$ | $\Delta V$ exponencial (50 → basal) | fração de uma CA de 250 µL |
|---:|---:|---:|
| 0,005813 (adotado no WP1.2) | 81,0 µL | 32% |
| 0,0126 (Pallikaris) | 41,5 µL | 17% |

**Fator 2 no entregável clínico central do WP5**, decidido por qual $K_f$ se usa. E note
que a recalibração contra Knecht é, ela mesma, um resultado interessante: implica que o
olho humano in vivo é ~2× mais complacente que qualquer coeficiente de Friedenwald
publicado. Isso merece ser afirmado como achado, não ficar escondido numa discrepância.

### A.3 Volume da câmara anterior (~250 µL) não tem fonte

A conversão "X µL = Y% da câmara anterior", que é como o plano comunica a viabilidade,
depende inteiramente desse 250 µL, que aparece sem referência. E a sensibilidade é grande:

| volume da CA | $\Delta V$ exponencial ($K_f$ WP1.2) | linearizado |
|---:|---:|---:|
| 150 µL | 54,0% | 97,6% |
| 200 µL | 40,5% | 73,2% |
| 250 µL | 32,4% | 58,5% |

Com CA de 150 µL e a conta linearizada, a paracentese consumiria **98% da câmara** — a
conclusão de inviabilidade sai inteira de dois números sem fonte combinados. Precisa de
referência para o volume da CA (e ele varia com idade, status do cristalino e ACD, que são
justamente variáveis do modelo).

### A.4 O que está correto e verificado: a resistência da via

$R_{par} = 6{,}2\times10^{11}$ Pa·s/m³ (plano) → $Q = 4{,}30$ µL/s a 20 mmHg; o plano diz
4,29 ✓.

E o valor é **fisicamente derivável**, não assumido. Por Poiseuille,
$R = 8\mu L/(\pi r^4)$, com $\mu_{aquoso} = 0{,}75$ mPa·s (o mesmo que o plano usa na
Seção 7.4):

| agulha | $R$ calculado | $Q$ @ 20 mmHg |
|---|---:|---:|
| 30G, ½ pol (d=0,159 mm, L=12,7 mm) | **6,07×10¹¹** ✓ | 4,39 µL/s |
| 30G, 1 pol | 1,21×10¹² | 2,20 µL/s |
| 25G, ½ pol | 1,15×10¹¹ | 23,2 µL/s |

Confere com a 30G de meia polegada dentro de 2%. **Bom: esse parâmetro tem procedência.**
Note de passagem que a 25G drena 5× mais rápido — o que importa para o $Q_{crit}$ do WP8.

### A.5 A duração da paracentese não precisa ser assumida — ela é saída, não entrada

O registro de auditoria do plano lista como pendência: *"Duração da paracentese
($t_{par\_dur}$): sem fonte encontrada na literatura, permanece como estimativa de ordem de
grandeza no WP0."* E o solver do WP0 usa `t_par_dur_min = 0.2` (12 s).

Integrando a drenagem por Poiseuille com a $P(V)$ exponencial — ou seja, deixando a física
determinar a duração:

| $K_f$ | volume a drenar | tempo | % de $\tau$ (191 s) |
|---|---:|---:|---:|
| 0,005813 (WP1.2) | 81,0 µL | **13,6 s** | 7,1% |
| 0,0126 (Pallikaris) | 41,5 µL | **7,5 s** | 3,9% |

Três conclusões: (a) a estimativa de 12 s estava certa, e agora é **derivada** em vez de
assumida — a pendência do plano pode ser fechada; (b) tratar a paracentese como
instantânea é defensável, porque leva 4–7% de $\tau$ — mas o plano deve **reportar esse
número** em vez de assumir; (c) o 0,2 min do solver deveria ser substituído pelo cálculo,
porque muda com o calibre e com $K_f$.

### A.6 Problemas estruturais da formulação de otimização (5.1)

$$\min_{\Delta V,\,t_{par}} \mathcal{I}(\Delta V, t_{par})
\quad\text{s.a.}\quad \text{IOP} \ge 6,\; \text{ACD} \ge \text{ACD}_{\min},\;
\Delta V \le \Delta V_{\max}$$

1. **Não existe um $\Delta V^\ast$ único.** $\mathcal{I}$ depende de $\Delta P_{th}$, que
   depende de $\text{OPP}_{crit}$ — o parâmetro que o próprio plano manda tratar sempre
   como incerto. Logo o entregável do WP5 **não é um volume ótimo, é uma superfície**
   $\Delta V^\ast(\text{OPP}_{crit}, \Delta P_{th})$. Se o capítulo entregar um número
   único, cai pela mesma razão que o plano diz que o Capítulo 8 cairia.
2. **O limite de hipotonia (IOP ≥ 6 mmHg) não tem fonte** no plano. Precisa de referência.
3. **$\text{ACD}_{\min}$ virou dependente de experimento.** Com o WP1.5 cortado, a curva
   $\text{ACD}(\Delta V)$ vem do Ensaio D do WP2 (o próprio plano já previa isso como
   plano B). Consequência de cronograma: a **estrutura** da otimização pode ser construída
   e testada agora, mas a restrição de ACD fica como placeholder até o experimento. Vale
   declarar isso no plano reorganizado.
4. **$\Delta V_{\max}(\text{anatomia})$ não está definido** — é o mesmo problema do volume
   da CA (A.3).

### A.7 O item 5.4 (timing) é a parte pronta para rodar hoje

"Se for para fazer, faça imediatamente ou não faça" é uma predição testável **agora**: o
solver do WP0 já tem `par_enabled`, `t_par_start_min` e `R_par`. O script
`claude_wp5_verificacao.py` roda $\mathcal{I}(t_{par})$ para $t_{par}$ = 0, 1, 2, 5, 10 min
e sem paracentese, e sai a resposta quantitativa. **Isso não depende de nenhum
experimento** — é WP5 entregável no bloco sem lab.

---

## PARTE B — WP6 (estratificação de risco e calibração bayesiana)

### B.1 O $\phi$ da H3 confunde três coisas, e a interpretação do plano só vale se duas delas forem zero

O plano define (Seção 6.2):

$$\phi = \frac{K_{\text{ex vivo, corrigido para geometria humana}}}{K_{\text{in vivo, ajustado}}}$$

e conclui: *"Se $\phi > 1$, a diferença é o volume de sangue expelido da coroide durante o
pico. Ninguém mediu isso diretamente."*

**Essa inferência não se sustenta como está.** A razão absorve, no mínimo, três
contribuições distintas:

1. **Diferença de material entre espécies** — esclera suína não é esclera humana. A
   correção descrita é de **geometria** ("corrigido para geometria humana"); ela não
   remove nada da diferença constitutiva.
2. **Vivo vs morto** — a complacência coroidal aguda, que é o que se quer medir.
3. **Erro da própria correção geométrica** — que, como a Seção A.1 mostra, depende da
   lei $P(V)$ adotada e do ponto da curva.

Como está, qualquer diferença material suíno-humano entra em $\phi$ e é **lida como
complacência coroidal**. É o mesmo tipo de erro sistemático entre espécies que o registro
de auditoria do plano diz ter passado uma vez sem ser notado (a fração uveoescleral), e é
mais grave aqui porque $\phi$ é apresentado como número novo de fisiologia ocular.

**Saídas possíveis:** (a) medir $K$ suíno **e** humano no mesmo aparato, impossível aqui;
(b) limitar a afirmação a um **limite superior** da complacência coroidal, declarando que
o termo de espécie está dentro; (c) usar o braço de deriva pós-morte do WP2 para estimar
a parte "morto" separadamente. A (b) é honesta e barata e eu iria por ela.

### B.2 A fusão bayesiana assume que $\theta$ é comum às espécies

$$p(\theta)\times p(D_{\text{suíno}}\mid\theta)\times p(D_{\text{clínico}}\mid\theta)
\Rightarrow p(\theta\mid D)$$

O produto de verossimilhanças assume independência condicional dos dois conjuntos dado
$\theta$ — isso está certo. O problema é **$\theta$ ser o mesmo**: os parâmetros de Ogden
ajustados à esclera suína não são os humanos. Sem um modelo de transferência (por exemplo
$\theta_{humano} = g(\theta_{suíno}, \psi)$ com $\psi$ estimado ou declarado), o posterior
mistura as duas espécies num só vetor de parâmetros e o resultado não é interpretável
como "material humano". Precisa de uma camada hierárquica, ou de declarar que o suíno
entra como **prior** e não como verossimilhança conjunta.

### B.3 O WP6 herda tudo do emulador — e a correção do WP1.4 muda o que ele pode estimar

O plano é explícito: *"Use MCMC rodando sobre o emulador, não sobre o CalculiX. Sem
emulador isto é computacionalmente impossível."* Logo o WP6 herda integralmente a qualidade
do WP1.4.

Com a correção do WP1.4 (remoção dos três constantes inventados), **ACD, estado do
cristalino e vitrectomia deixam de ter via mecânica** — o emulador não tem o que aprender
sobre eles. Consequência direta para o WP6: esses três **não podem entrar em $\theta$**.
Eles têm que entrar como **covariáveis clínicas** na regressão sobre o dado do WP3, não
pelo caminho do FEA. Isso é mudança de arquitetura do WP6, não detalhe.

### B.4 O semáforo de risco vai precisar de limiares, e eles não existem

O entregável 6.3 inclui "Semáforo de risco". Qualquer corte verde/amarelo/vermelho é um
número novo. Se vier de "bom senso", é exatamente o que a regra de ouro do plano proíbe.
Tem que sair da distribuição de dose isquêmica da própria coorte (percentis declarados) ou
de um limiar clínico com fonte. **Decidir isso antes de desenhar a saída**, porque o
semáforo é a parte que o médico vai olhar.

### B.5 Validação: a divisão temporal é a mais fraca das opções, e o plano já sabe

"Primeiros 100 treinam, últimos 50 testam" é suscetível a deriva de técnica, de operador e
de seleção ao longo do recrutamento — e a deriva é plausível justamente porque a medida
"imediata" (<60 s) depende de treino, que melhora com o tempo. O plano já diz que validação
externa num segundo centro é melhor; reportar AUC **e** gráfico de calibração está correto.
Eu acrescentaria: reportar a métrica temporal separada por período de recrutamento, para
que a deriva fique visível em vez de diluída.

---

## PARTE C — o que roda agora

```bash
docker compose run --rm fsi bash -lc 'pip install numpy scipy --break-system-packages && cd /simulation/claude-wp5 && python3 claude_wp5_verificacao.py'
```

O script faz, em ordem: (1) reproduz a tabela linearizada do plano; (2) recalcula com a lei
exponencial e mostra o fator de 1,9×; (3) expõe a inconsistência de $K_f$; (4) varre o
volume da CA; (5) verifica $R_{par}$ contra Poiseuille para três calibres; (6) **deriva** a
duração da paracentese em vez de assumir; (7) roda $\mathcal{I}(t_{par})$ no solver do WP0
para o item 5.4.

Os itens 1–6 não dependem de nada além do numpy. O item 7 usa o solver do WP0 e as funções
corrigidas do WP4 (`claude_wp4_fixes.dose_isquemica_exata`).

---

## Ordem de correção sugerida

| # | O que | Bloqueante? |
|---|---|---|
| 1 | Trocar $\Delta V = \Delta\text{IOP}/K$ por integração da $P(V)$ calibrada (A.1) | **sim** — muda a conclusão do WP5 |
| 2 | Declarar a inconsistência de $K_f$ (0,0058 adotado vs 0,0126–0,0280 da literatura) e escolher (A.2) | **sim** |
| 3 | Referência para o volume da câmara anterior (A.3) | **sim** — a viabilidade é comunicada nessa fração |
| 4 | Reformular a H3/$\phi$ como limite superior, declarando o termo de espécie (B.1) | **sim** |
| 5 | Decidir se o suíno entra como prior ou como verossimilhança conjunta (B.2) | **sim** |
| 6 | Tirar ACD/cristalino/vitrectomia de $\theta$ e pôr como covariáveis clínicas (B.3) | sim, mas é consequência do WP1.4 |
| 7 | Referência para o limite de hipotonia de 6 mmHg (A.6) | não |
| 8 | Substituir `t_par_dur_min = 0.2` pelo valor derivado (A.5) | não — melhoria |
| 9 | Definir a origem dos cortes do semáforo (B.4) | não, mas antes de desenhar a saída |
| 10 | Entregar o WP5 como superfície $\Delta V^\ast(\text{OPP}_{crit})$, não número único (A.6) | não — forma do entregável |
