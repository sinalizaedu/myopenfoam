# Revisão de engenharia de simulação — WP4

Revisado: `cases/wp4/` (5 módulos, 1675 linhas com testes) contra o plano de tese
(`plano_tese_IOP_IVI__2_.md`, Seção WP4) e contra o WP0/WP1. Nada foi alterado.

**Veredito curto.** A matemática está correta — verifiquei a fórmula de H6 derivando-a
do zero e confere exatamente, inclusive a derivada e todos os valores numéricos das
tabelas. O código é defensivo e epistemicamente honesto nos itens 4.1–4.3: cada
parâmetro livre é derivado, citado, ou rotulado explicitamente como parâmetro de
sensibilidade. É muito superior ao WP1.4 nesse aspecto.

O problema do WP4 é de outra natureza: **rastreabilidade de referências**. Há uma
citação atribuída ao plano que não existe no plano, dois itens inteiros (4.4 e 4.5)
apresentados como se fossem do plano quando o plano não os tem, uma inconsistência
numérica de 2,2× com o próprio plano, e cerca de oito fontes citadas sem identificador
verificável. Nada disso é fatal, mas **o 4.4 e o 4.5 não estão prontos para a banca
na forma atual.**

---

## 1. O que está correto — verificação independente

### 1.1 A fórmula de H6 (item 4.3) está certa

Derivei do zero, sem olhar o código. Com $\Delta P(t) = \Delta P_0 e^{-t/\tau}$ e
cruzamento do limiar em $t^\ast = \tau \ln(\Delta P_0/\Delta P_{th})$:

$$\mathcal{I} = \int_0^{t^\ast}\!\big(\Delta P_0 e^{-t/\tau} - \Delta P_{th}\big)dt
= \tau\Big[\Delta P_0 - \Delta P_{th} - \Delta P_{th}\ln\tfrac{\Delta P_0}{\Delta P_{th}}\Big]$$

Substituindo $\Delta P_0 = K\Delta V$ e $\tau = 1/(C K)$:

$$\mathcal{I} = \frac{\Delta V}{C} - \frac{\Delta P_{th}}{CK}\Big[1 + \ln\tfrac{K\Delta V}{\Delta P_{th}}\Big]
\qquad\Longrightarrow\qquad
\frac{\partial\mathcal{I}}{\partial K} = \frac{\Delta P_{th}}{CK^2}\ln\frac{K\Delta V}{\Delta P_{th}}$$

Idêntico ao implementado em `h6_teorico.dose_fechada_H6` e ao plano. $K_{crit} = \Delta P_{th}/\Delta V$ ✓.

Recalculei à mão toda a tabela do README (dPth=15, ΔV=50, C=0,28): ΔV/C = 178,571;
K_crit = 0,30; I(0,31) = 0,0945; I(0,40) = 6,11; I(0,60) = 27,43; I(1,00) = 60,50;
I(3,00) = 119,60. **Todos conferem.** A Consequência 3 (I ∝ 1/C, razão exatamente 2)
é correta por inspeção: $C$ aparece só uma vez, multiplicando a expressão inteira.

Recalculei também as tabelas do 4.5: mensal 480,0/250,0; T&E 240,0/58,89;
brolucizumabe 160,0/37,5; faricimabe 120,0/26,25; e a sensibilidade de meia-vida
135,0 / 250,0 / 345,27 / 385,10. **Todos conferem.**

### 1.2 `dPth = f·MAP − P0 − OPP_crit` está derivado corretamente

Como $\text{MOPP} = f\,\text{MAP} - \text{IOP}$ e $\text{IOP} = P_0 + \Delta P$, a condição
$\text{MOPP} < \text{OPP}_{crit}$ equivale a $\Delta P > f\,\text{MAP} - P_0 - \text{OPP}_{crit}$ ✓.
E $\Delta P_{th}(\phi) = \Delta P_{th,basal} - \text{OPP}_{crit,ref}(\phi-1)$ segue algebricamente ✓.

### 1.3 A derivação de $P_0$ (item 4.2) é um acerto real — e amarra o WP1

`derivar_P0_equilibrio`: $P_0 = P_{ev} + Q_{prod}(1-f_{uv})/C_{out}$. É o equilíbrio de
Goldmann com a via uveoescleral tratada como insensível à pressão ✓.

- Humano: $10 + 2{,}4(0{,}80)/0{,}28 = 16{,}857$ mmHg.
- **Isso explica e legitima o $P_0 = 16{,}9$ mmHg usado no WP1.2, WP1.3 e WP1.4.**
  Vale escrever essa cadeia na tese: a basal não foi escolhida, foi derivada.

O módulo também corrige um defeito real do WP0 (`Protocol()` default com $P_0=15$ e
$Q_{prod}=3{,}0$, cujo equilíbrio verdadeiro é ~18,57 mmHg — a IOP derivava sem injeção).
Bom achado, bem documentado.

### 1.4 Boas práticas que valem registro

- `validacao_fechada_H6` recusa rodar fora do domínio (exige $K$ constante, recusa
  refluxo/paracentese ligados, levanta `ValueError` informativo se $\Delta P_{th}\le 0$
  em vez de devolver `NaN` silencioso). Erro de 0,17% contra o solver 0D, com a causa
  declarada (rampa de 6 s vs bólus instantâneo). Isso é verificação no nível certo.
- `curva_sensibilidade_opp_crit` e `curva_I_vs_dPth` tornam o alerta metodológico do
  plano executável: nenhuma função pública tem `dPth` ou `OPP_crit` fixo.
- Fração uveoescleral de coelho = 0,05, coerente com a correção do próprio plano
  (3–8% em coelho, não os 20% humanos) ✓.
- Compat `np.trapezoid`/`np.trapz`, validação de formas, mensagens de erro úteis.

---

## 2. Rastreabilidade — aqui está o problema sério

### 2.1 Há uma citação atribuída ao plano que não existe no plano

`validacao_zero_observado.py`, docstring do módulo:

> Objetivo (citação do plano): "mostrar que o modelo reproduz corretamente a ausência
> de déficit perfusional relatada na literatura para injeção única, e delimitar a
> região paramétrica onde essa previsão deixaria de valer."

Procurei no plano por seis fragmentos distintos dessa frase ("ausência de déficit",
"delimitar a região", "reproduz corretamente", "zero observado", "deixaria de valer").
**Zero ocorrências de cada um.** A frase não está no plano.

Numa tese isso é o tipo de erro mais grave de rastreabilidade: uma citação entre aspas
atribuída a uma fonte que não a contém. Tem que sair, ou virar texto próprio sem aspas
e sem atribuição.

### 2.2 O plano não tem item 4.4 nem 4.5

A Seção WP4 do plano tem exatamente três subitens: 4.1 (cadeia), 4.2 (métrica nova),
4.3 (resultado teórico H6). Não existe 4.4 nem 4.5.

Consequências concretas:

- `dose_cumulativa.py` afirma: *"Regimes terapêuticos do plano (Seção 4.5), N em 2 anos:
  mensal_fixo (24, 4 sem), treat_and_extend (~12, média 10 sem), brolucizumabe (~8,
  12 sem), faricimabe (~6, 16 sem)"*. **Nada disso está no plano** — verifiquei:
  "brolucizumab", "faricimab", "treat-and-extend", "dose acumulada", "injeções
  repetidas" têm zero ocorrências. Esses quatro regimes precisam de fonte primária
  (ensaios pivotais / bula: q12s para brolucizumabe, q16s para faricimabe), não do plano.
- O README apresenta o 4.5 como "contribuição original" ✓ (correto), mas apresenta o
  **4.4 como se fosse item planejado**. Ou os dois são declarados extensões ao plano,
  ou o plano é atualizado para incluí-los. As duas saídas servem; a mistura atual não.

### 2.3 Fontes citadas sem identificador verificável

| Onde | Como está citado | Falta |
|---|---|---|
| 4.2, faixa de OPP_crit | "Baltimore Eye Survey (DOPP<30)" | autor, ano, revista, DOI |
| 4.2, idem | "Barbados Eye Study (MOPP<42)" | idem |
| 4.2, idem | "CRAO completa (12–15 min)" | fonte inteira |
| 4.2, coelho | "Kiel et al. 2011/2015" | revista, DOI; e qual dos dois dá qual parâmetro |
| 4.2, coelho | "Fourman & Garner 1989" | revista, DOI |
| 4.4, Peça 1 | "OCT-A 2026 (n=54)" | **autor, título, revista, DOI — não há citação nenhuma** |
| 4.4, Peça 2 | "Damasceno et al. 2022" | revista, DOI |
| 4.4, Peça 3 | `"fonte": "PMC13307848"` | citação completa; um PMCID não é citação |
| 4.5 | "modelo SF do rato" | **fonte inteira — é a forma funcional de todo o item** |

"Goel et al. 2010" para a fração uveoescleral humana de 20% **é** rastreável ao plano ✓
(é o único desta lista que é).

Duas observações sobre o 4.4 Peça 1 em particular. Primeiro: um estudo de 2026 está além
do que eu consigo verificar — não tenho como confirmar que existe nem que os números
estão certos; isso precisa ser conferido na fonte. Segundo, e mais importante:
`MOPP_MIN_OBSERVADO_OCT_A_MMHG = 31.0` é **numericamente igual ao pico de IOP** (31,0
mmHg). O código afirma em comentário que foi "relatada diretamente pelo estudo", mas a
coincidência é exatamente o que um revisor vai sondar — se for transcrição errada do pico
de IOP no lugar da MOPP, **a conclusão inteira da Peça 1 cai**, porque o teto
"OPP_crit ≤ 31 mmHg" é literalmente esse número. Conferir na fonte, e registrar o MAP da
coorte junto (MOPP de 31 com IOP de 31 exige $f\cdot\text{MAP} = 62$, ou MAP ≈ 93 mmHg —
plausível, mas é o que precisa aparecer).

### 2.4 Falta a etiqueta de confiança que o próprio plano exige

O plano manda: *"Etiquete a confiança de cada fração usada em toda tabela de parâmetros
da tese: medida no seu próprio suíno / extrapolada da literatura de coelho / extrapolada
da literatura humana."* O `_PARAMS_LITERATURA` tem as fontes em comentário, mas nenhuma
etiqueta de confiança. É fácil de corrigir e o plano pede explicitamente.

---

## 3. Inconsistência numérica com o plano — $C_{out}$ de coelho difere 2,2×

| Fonte | $C_{out}$ coelho |
|---|---|
| Plano de tese (lista de hedges obrigatórios, linha 839) | **≈ 0,57** µL/min/mmHg |
| `dose_isquemica._PARAMS_LITERATURA["coelho_anestesiado"]` | **0,26** µL/min/mmHg |

Fator 2,2. E como a Consequência 3 de H6 é exata ($\mathcal{I} \propto 1/C_{out}$),
**isso propaga linearmente**: toda dose isquêmica de coelho muda por 2,2× dependendo de
qual valor se usa. A anestesia realmente reduz produção e pode alterar a facilidade, então
0,26 pode estar certo *para coelho anestesiado* — mas aí o plano está desatualizado, e os
dois valores não podem coexistir na tese sem uma frase explicando qual vale onde. Este é
exatamente o tipo de erro sistemático entre espécies que o registro de auditoria do plano
diz que "passou uma vez sem ser notado".

---

## 4. Defeitos técnicos

### 4.1 `_tempo_iop_acima` usa o estimador errado — inofensivo hoje, quebra no WP3

```python
mask = iop > limiar
return float(_trapz(mask.astype(float), t))
```

Integrar trapezoidalmente um indicador binário devolve, em grid uniforme,
$\Delta t \times (\text{nº de amostras acima})$ — não o tempo real acima, que depende de
onde os cruzamentos caem dentro dos intervalos. O viés é de até um intervalo de
amostragem.

Com o grid atual do solver (`n_points=4000` em 40 min → $\Delta t = 0{,}01$ min) o erro é
~0,6 s: irrelevante. **Mas a função não sabe que grid vai receber.** E o uso óbvio dela é
justamente a série temporal clínica do WP3, que é de **6 pontos** (imediato, 2, 5, 10, 15,
30 min). Nesse grid, $T_{>30}$ e $T_{>40}$ erram por minutos, e são métricas reportadas da
tese (plano, §4.2). O certo é interpolar $\text{IOP}(t) = \text{limiar}$ e devolver a
diferença entre os cruzamentos.

O mesmo vale para `dose_isquemica`: trapézio sobre o déficit recortado, num grid de 6
pontos com pico em $t<1$ min e $\tau\approx3$ min, **subestima $\mathcal{I}$
substancialmente**. Precisa de interpolação nos cruzamentos ou de um aviso de resolução
mínima.

### 4.2 A forma funcional de `phi_vasc` não tem fonte

$\text{OPP}_{crit,efetivo} = \text{OPP}_{crit,ref}\cdot\phi_{vasc}$. O README cita
Damasceno et al. 2022 como "motivação clínica" — e motivação não é fonte para uma forma
multiplicativa. O código está honesto em tratá-lo como parâmetro de sensibilidade ✓, mas
falta dizer no texto que *a forma* (multiplicativa sobre o limiar, e só para cima, pois
$\phi\ge1$ é imposto) é suposição, não medida. Tratar como o plano trata OPP_crit:
apresentar resultados como função de $\phi$.

### 4.3 `pad_oftalmica = (2/3)·PAD` é uma suposição mais forte do que parece

O fator 2/3 é convenção para a queda da pressão **média** da braquial à oftálmica.
Aplicá-lo à **diastólica** assume que a queda proporcional é a mesma para média e
diastólica — o que a convenção não afirma e não tem fonte. E a OPP diastólica é uma das
duas vias que alimentam $\mathcal{I}$ no 4.2. Está divulgado no README, mas precisa
aparecer como suposição rotulada na tese, ou ser substituído por PAD oftálmica informada.

### 4.4 Falta a análise de sensibilidade do fator 2/3, que o plano exige

O plano é explícito: *"O fator 2/3 aproxima a queda de pressão da braquial até a artéria
oftálmica. Declare como suposição e faça análise de sensibilidade em 0,5–0,8."*

Existe `curva_sensibilidade_opp_crit` para OPP_crit, mas **não existe nada equivalente
para o fator braquial-oftálmica**. O parâmetro é aceito em todas as funções ✓, mas a
varredura mandatada não está implementada. É o item mais fácil de fechar da lista toda.

---

## 5. Crítica de modelagem do item 4.5 — o mais frágil

### 5.1 O que está implementado não é um modelo de recuperação

$$\mathcal{I}_{cum}(N) = \sum_{j=1}^{N}\mathcal{I}_j\, w(t_j - t_{j-1})$$

Cada evento é descontado por um peso que depende **só do intervalo imediatamente
anterior**. Não há variável de estado. Um modelo de dano que acumula e recupera seria

$$D_j = D_{j-1}e^{-a\Delta t} + \mathcal{I}_j,$$

que **satura** em $D_\infty = \mathcal{I}/(1-e^{-a\Delta t})$ — para o regime mensal
($w=0{,}5$), $D_\infty = 2\mathcal{I} = 40$ mmHg·min. O que está implementado **cresce
linearmente em $N$ sem limite** (250 mmHg·min em $N=24$, e seguiria subindo). São
predições qualitativamente diferentes, e a que satura é o que "recuperação parcial"
significa fisicamente. Como está, o "limite de recuperação parcial" não é um limite — é o
limite de acumulação perfeita com uma constante multiplicativa.

### 5.2 A conclusão sobre a ordem dos regimes é aritmética, não resultado

Com $\mathcal{I}$ e $\Delta t$ constantes, $\mathcal{I}_{cum} = \mathcal{I}[1 + (N-1)w(\Delta t)]$,
monótona em $N$ e em $w$. Como os quatro regimes têm simultaneamente $N$ maior e
$\Delta t$ menor (24/4sem, 12/10sem, 8/12sem, 6/16sem), a ordem
mensal > T&E > brolucizumabe > faricimabe **não pode sair diferente**. Afirmar que "a
ordem é preservada nos dois limites" é descrever a monotonicidade da própria fórmula, não
um achado. Pior: a pergunta clinicamente interessante — se um intervalo maior com o
*mesmo* $N$ seria mais seguro — não pode ser respondida, porque $N$ e $\Delta t$ estão
amarrados na tabela de regimes.

### 5.3 A forma funcional não tem fonte, e a reinterpretação é um salto

"inspirado no modelo SF do rato, $SF = 1 - b(1-e^{-at})$, reinterpretado como a FRAÇÃO de
dano que persiste" — sem citação nenhuma, e a reinterpretação (de o que quer que SF
signifique na fonte, para "fração de dano que persiste") é semanticamente diferente, sem
justificativa. É a forma funcional sobre a qual todo o item 4.5 repousa.

**O que eu faria:** manter o 4.5 como *envelope de sensibilidade*, nunca como resultado;
trocar a soma descontada pelo modelo com estado (3 linhas de código) para que o limite de
recuperação sature; e rotular $\mathcal{I}_{cum}$ como **índice**, não como dose, já que a
soma ponderada não é uma grandeza conservada.

---

## 6. Crítica epistêmica do item 4.4

- **Peça 1 é a parte forte** e é um resultado real: de um zero observado, extrai uma
  restrição falseável ($\text{OPP}_{crit} \le 31$ mmHg para eventos transitórios,
  implicando que o limiar crônico de ~50 mmHg não valeria no agudo). Isso merece estar na
  tese. Depende inteiramente de uma citação de 2026 não verificada e de um número que
  coincide com o pico de IOP (§2.3).
- **Peça 2 não tem conteúdo de falsificação.** Separar dois grupos usando quatro
  parâmetros escolhidos ($K_{tip}$, $K_{alto}=1{,}0$, $\phi=1{,}3$, $\Delta P_{th,basal}=20$,
  $\text{OPP}_{crit,ref}=25$) é sempre possível. O README diz "cenário ilustrativo" ✓, mas
  conclui "consistente com a associação observada", que lê como validação. Para virar
  teste: fixar $K$ pelo emulador do WP1.4 com a biometria do subgrupo e $\phi$ por algo
  mensurável, e só então ver se a separação aparece.
- **Peça 3 não é controle negativo**, é declaração de escopo. O argumento (o modelo vive
  no espaço de pressão de perfusão, não de espessura, logo não pode confundir compressão
  mecânica com isquemia) está certo e vale escrever — só não é um controle em sentido
  estatístico. Renomear.

---

## 7. Ordem de correção sugerida

1. **Remover a citação inexistente** do plano em `validacao_zero_observado.py` (§2.1).
2. **Resolver $C_{out}$ de coelho**: 0,26 (anestesiado) vs 0,57 (plano) — decidir, citar,
   e escrever qual vale onde (§3).
3. **Fechar as citações** da tabela do §2.3, começando pelo estudo OCT-A de 2026 e pelo
   modelo SF do rato, que são os dois que sustentam conclusões.
4. **Conferir na fonte** se `MOPP_min = 31,0` é mesmo MOPP e não o pico de IOP (§2.3).
5. **Reposicionar 4.4 e 4.5** como extensões ao plano, ou atualizar o plano (§2.2).
6. **Implementar a sensibilidade do fator 2/3** em 0,5–0,8, que o plano manda (§4.4).
7. **Trocar o estimador de `T_acima_*`** por interpolação de cruzamentos, e pôr guarda de
   resolução em `dose_isquemica` antes de aplicar a dado clínico de 6 pontos (§4.1).
8. **Reescrever o 4.5** com modelo de estado (satura) e rotular como índice (§5).
9. Rotular `phi_vasc` e `pad_oftalmica = (2/3)PAD` como formas funcionais supostas (§4.2, §4.3).
10. Acrescentar as etiquetas de confiança de parâmetro que o plano exige (§2.4).

Itens 1–4 são bloqueantes para a banca. 5–7 são de uma tarde. 8–10 são de redação, exceto
o 8 que é código.
