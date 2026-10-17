# Handoff: WP1.1, WP1.2 e WP1.3 refeitos em geometria de octante

Resumo do que foi feito deste lado, para vocês reproduzirem, conferirem e aprimorarem.

## Contexto da mudança

O WP1.2 (Ogden + `NLGEOM=YES`) nunca convergiu na esfera completa com 3 pinos discretos, em nenhuma combinação de malha, tipo de elemento (S8/S8R), magnitude de carga, ou método de solução (incluindo Riks). Diagnóstico: um pino discreto trava a posição de um nó mas não trava a rotação da casca ao redor dele, permitindo uma concentração de curvatura tipo dobradiça sob grande deformação. Com material linear isso não importa (rigidez tangente constante, resolve em um passo). Com Ogden, a rigidez tangente depende da deformação local, e essa curvatura concentrada deixa a matriz tangente mal condicionada bem no pino, levando o Newton-Raphson a divergir.

**Decisão**: trocar a restrição pontual por condição de simetria nos três planos coordenados ($x=0$, $y=0$, $z=0$), modelando só 1/8 da esfera (octante). Isso não é um artifício, é a condição que já existiria naquele lugar por simetria se a esfera inteira fosse modelada — se distribui por uma linha inteira de nós, não concentra num ponto. Aplicado retroativamente também no WP1.1 (que já funcionava com pinos), por consistência entre todas as etapas.

## O que foi rodado, com números

### WP1.1 — verificação + independência de malha, octante

Malha: parametrização esférica $(\theta,\phi)$, ambos de $0$ a $90°$, elementos S8R. Polo evitado por uma calota não malhada de $\theta<3°$ (área $\approx0{,}07\%$ da esfera), com borda interna livre (sem tratamento especial — ver pergunta 1 abaixo).

Independência de malha, 4 níveis (contagem equivalente na esfera completa $=$ elementos do octante $\times8$):

| Elementos | $K_{FEA}$ humano | $\varepsilon_i$ humano | $K_{FEA}$ coelho | $\varepsilon_i$ coelho |
|---|---|---|---|---|
| 72 | 0,163259 | — | 0,669901 | — |
| 288 | 0,163295 | 0,0221% | 0,669989 | 0,0131% |
| 1152 | 0,163290 | 0,0027% | 0,669971 | 0,0027% |
| 4608 | 0,163290 | 0,0001% | 0,669971 | 0,0001% |

$K_{analítico}$: humano $0{,}162933$, coelho $0{,}668380$. Erro final: $+0{,}22\%$ humano, $+0{,}24\%$ coelho (melhor que os $+0{,}48\%$/$+0{,}50\%$ obtidos antes com pinos). Malha recomendada: $288$ elementos equivalentes.

Extração de $\Delta V$: integral de Gauss $3\times3$ por elemento de $u\cdot n\,dA$, com deslocamento de superfície média obtido pela média entre os nós expandidos de topo ($R+t/2$) e base ($R-t/2$) que o CalculiX gera por padrão para elementos de casca — mapeados de volta aos nós originais por correspondência de posição 3D (KDTree), não por proximidade angular.

### WP1.2 — hiperelástico vs. curva do Pallikaris, octante

**Status (Sep 2026): resultados numéricos Ogden retirados — não reprodutíveis isoladamente.**

Material alvo: Ogden $N=1$ ou Yeoh-2 (Metodologia prevê ambos). Alvo: curva sintética
$\Delta P(V) = P_0(10^{K_fV}-1)$ com $K_f=0{,}0126$, $P_0=16{,}9$ mmHg, $V$ de $0$ a $50$ µL.

Hipótese de instabilidade: Ogden com $\alpha_1$ baixo → cancelamento catastrófico na energia
e na matriz tangente. Plano: E1 (mapa $\alpha_1$ × convergência) + E2 (Yeoh controle) → E3
(ajuste Yeoh completo se E2 passar). Ver `cases/wp1.2/output_exploration/RESULTS.md`.

### WP1.3 — quantificação preliminar do pré-tensionamento

**Status: quantificação numérica retirada** — dependia do ajuste Ogden contaminado do WP1.2.
Método descrito; resultado $-2{,}1\%$ não reportado até WP1.2 validado (E3 + saída densa).

## Perguntas para vocês investigarem/aprimorarem

**1. Tratamento do polo.** Deixei a calota ($\theta<3°$) simplesmente com borda livre, sem nenhuma restrição especial. Isso é uma aproximação grosseira — fisicamente, aquela borda deveria continuar suave com o resto da casca, não ficar livre para "abrir". Dado que vocês já lidam com octante, será que a malha de vocês evita esse problema de outro jeito (talvez uma parametrização diferente que não crie um polo geometricamente singular)? Se sim, qual é? Se não, vale testar quanto essa borda livre está distorcendo o resultado perto do polo, mesmo que o efeito agregado em $K$ pareça pequeno.

**2. O otimizador do WP1.2 parou cedo.** Só 4 avaliações de função antes de reportar `success: True`, com `diff_step=0.05` (grande) e tolerâncias `xtol=ftol=1e-4`. Rodem de novo com um `diff_step` menor e mais avaliações permitidas, e vejam se o resíduo máximo de $2{,}23$ mmHg em $V=50$ µL melhora. Minha suspeita é que sim.

**3. $D_1$ amarrado a $\mu_1$, não livre.** Usei $D_1=0{,}5\times(1{,}0204/\mu_1)$ como atalho, não ajustei $D_1$ como parâmetro livre do otimizador. Isso restringe o espaço de busca de um jeito que pode não ser o ideal. Vale testar ajustar $D_1$ livremente (com algum limite inferior tipo $10^{-4}$ para evitar problema de quase-incompressibilidade instável) e ver se o $R^2$ melhora.

**4. O achado do WP1.3 é estranho e merece desconfiança.** Encontrei amolecimento ($-2{,}1\%$), não endurecimento, entre $V=0$ e $P_0$. Isso pode ser: (a) genuíno, dado esse $\alpha_1=1{,}77$ específico e esse modo de carregamento (inflação equibiaxial de membrana, que se comporta diferente de tração uniaxial para Ogden); (b) um artefato de eu ter usado só a curva do ajuste do WP1.2 em vez de implementar o MULF de verdade. Vocês conseguem implementar o MULF (Gee et al. 2010) nessa mesma geometria de octante e comparar contra esse número aproximado?

**5. Confirmem a extração de $\Delta V$ independentemente.** Reproduzam a Tabela de independência de malha do WP1.1 acima com o pipeline de vocês, na mesma malha de octante (ou descrevam a malha de vocês se for diferente), e vejam se os números batem. Se não baterem, é a mesma classe de investigação que já fizemos antes (mapeamento FRD, quadratura, orientação) — só que agora numa geometria nova, que nunca foi cruzada entre os dois lados.

**6. WP1.4 e WP1.5 ainda não foram tocados nesta geometria.** Se a independência de malha de vocês bater com a minha, o próximo passo natural é vocês rodarem a varredura paramétrica (WP1.4) já usando o octante como padrão, evitando qualquer nova tentativa com pinos.

## Estado deste repositório (`myopenfoam`) em relação a este handoff

| Item | Status local (Sep 2026) |
|---|---|
| Octante `symmetry_octant` em `gen_sphere_shell_mesh.py` | Parcial — clip do cubic-sphere, não $(\theta,\phi)$ |
| Malha wp1.1 oficial | Ainda esfera completa + PINs (864 elem.) |
| wp1.2 Ogden 3D octante | Converge com deck corrigido (single-step + D1≈1e-6) |
| S8R, polo θ<3°, Gauss 3×3 | **Não implementado** aqui |
| Pallikaris / D1=0.5×(1.0204/μ₁) | **Não implementado** |
| wp1.3 MULF | **Não implementado** |

Ver também alterações locais em `cases/wp1.2/scripts/` (`write_deck.py`, `ccx_utils.py`, `extract_pv_curve.py`, `fit_hyperelastic.py`).
