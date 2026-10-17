# claude-wp1_octant

Versão independente da matriz Ogden × Yeoh do Composer
(`cases/wp1_octant/`), construída em paralelo — **nenhum arquivo existente
foi editado**, só importados (read-only) os módulos de `wp1.1/scripts`,
`wp1.2/scripts`, `wp1.3/scripts`. Ainda **não rodada** — para você executar
no Docker e comparar com o Composer.

## O que muda em relação ao Composer

| | Composer (`wp1_octant`) | claude-wp1_octant |
|---|---|---|
| WP1.1 | linear only (`run_verification_octant.py`) | linear only (mesmo) |
| WP1.2 Ogden | 1 start, x0=(2.14,1.77), D1 amarrado, bounds α₁∈[0.5,6.0] | **7 starts**, D1 livre, bounds α₁∈[0.15,3.5] (inclui região baixa) |
| WP1.2 Yeoh | 1 start, x0=(0.612,0.058) | **6 starts**, bounds alargados (C10,C20 até 8, vs 5 no Composer) |
| WP1.3 pretensão | só curva-do-ajuste (poucos pontos) | curva-do-ajuste **e** curva densa forward (30 pts, malha nova) lado a lado |

## Avaliação do estudo do Composer

**Pontos fortes** (mantenho, e reaproveito o código deles):
- Pipeline reprodutível, output bem estruturado, fácil de auditar.
- WP1.1 permanece linear-only (V&V de malha e extração de ΔV); material
  hiperelástico começa no WP1.2.
- WP1.3 agora usa a curva do próprio ajuste (`pretension_from_fit.py`) em vez
  da curva densa antiga (`pretension_study.py`, usada no E5) — isso já é uma
  melhoria de consistência metodológica (compara o material realmente
  ajustado, não uma curva solta), mas troca um problema por outro (ver abaixo).

**Limitação real, não cosmética — a trilha Ogden não é um ajuste novo**:
o `wp1.2-ogden` do material matrix roda `fit_pallikaris.py` sem nenhuma
mudança: mesmo x0=(2.14,1.77), mesmo D1 amarrado, mesmo bound inferior
α₁≥0.5. O resultado (μ₁=7.1586, **α₁=0.50000007**) está *colado* no limite
inferior da caixa até a sétima casa decimal — isso não é um mínimo local
genuíno, é o otimizador batendo na parede e parando. Já vimos isso antes
(era exatamente o resultado do Cursor que motivou o multi-start em
`claude-wp1.2`). Ou seja: **o número "Ogden" do material matrix não é uma
peça de evidência nova** — é o mesmo resultado antigo, reembalado dentro do
pipeline novo. Isso não invalida o WP1.3-ogden calculado a partir dele, mas
significa que ele herda a mesma incerteza: não sabemos
se esse (μ₁,α₁,D1) é representativo do "modelo Ogden" ou só de uma esquina
arbitrária do espaço de parâmetros.

A trilha Yeoh é mais sólida: converge de forma robusta (nfev=22, sem bater em
bound), e já foi reproduzida 2× de forma independente (5/5 no E3, 3/3 aqui).
Ainda é single-start, mas Yeoh (polinomial, sem expoente livre) tem muito
menos motivo estrutural para múltiplos mínimos do que Ogden N=1 — meu
multi-start serve para confirmar isso, não porque eu desconfie do resultado.

**Gap não testado**: nenhuma das duas trilhas cruzou o método de derivada
do WP1.3 com uma curva densa nova — o `claude-wp1_octant` cobre isso.

## Veredito: com qual prosseguir

**Yeoh.** Três motivos, nessa ordem de peso:

1. **Reprodutibilidade já demonstrada**: 100% de convergência em todo o
   E1/E2 (35 runs), 5/5 e 3/3 de repro isolada, e agora (depois de rodado)
   um multi-start que deve confirmar se é o único mínimo relevante. Ogden
   não tem isso — o próprio Composer, sem querer, mostrou de novo que o
   ajuste padrão fica preso na borda do bound.
2. **Sem a patologia numérica do expoente**: seja ou não a explicação
   correta para as falhas antigas (o E1 do Composer não confirmou a
   hipótese do outro Claude, e meu multi-start anterior não achou
   divergência ao empurrar α₁ para baixo — mas ainda não testamos α₁<0.3
   *neste* ambiente, o que este pacote faz), Yeoh estruturalmente não tem
   esse problema: não há termo `1/α²` explodindo.
3. **Ajuste ligeiramente melhor** no mesmo alvo Pallikaris: R²=0.938 vs
   0.931, resíduo máx. 7.90 vs 8.48 mmHg — pequeno, mas consistente.

**Contra-argumento honesto**: Ogden captura softening/stiffening
assimétrico com um parâmetro a mais de forma (α₁) que Yeoh não tem — se o
objetivo científico for testar hipóteses sobre a forma da curva de rigidez
(não só ajustar um P(V) observado), abandonar Ogden descarta essa
flexibilidade. Mas para o propósito do WP1 (achar *um* material que
reproduza a curva de Pallikaris com robustez numérica adequada para as
simulações de injeção subsequentes), Yeoh é a escolha mais defensável agora.

**O que eu NÃO declararia resolvido ainda**: o WP1.3 (pretensão) — nem a
versão do Composer nem esta aqui devem entrar no relatório como número
final. As duas ainda dependem de diferenciação numérica de uma curva P(V)
sem MULF (pré-tensão real da membrana). O próximo passo de verdade, depois
de fechar Ogden-vs-Yeoh, é implementar MULF — não mais uma terceira forma de
derivar a mesma curva.

## Como rodar

```bash
cd /simulation/claude-wp1_octant   # dentro do container Docker
./Allrun                # tudo (ogden + yeoh), ~2-3h
./Allrun --only yeoh     # só Yeoh (WP1.2-1.3, octante), mais rápido e mais barato
```

Saídas em `output/wp1.{2,3}-{ogden,yeoh}/RESULTS.md` — mesmo layout do
Composer, para comparar lado a lado. WP1.1 linear: `wp1.1/output_octant/`.

## Pedido de 22/09/2026 — só Yeoh, WP1.2-1.3, octante

Rode `./Allrun --only yeoh`. Ao final ele chama automaticamente
`scripts/compare_to_composer_claude.py`, que lê os JSONs deste caso e escreve
`output/COMPARE_TO_COMPOSER.md` com uma tabela `BATE`/`DIVERGE` ponto a ponto
contra os números do Composer (C10, C20, R², resíduo máx. do WP1.2;
dP/dV @V0, @V_ref e variação % do WP1.3) — tolerância 2% para o ajuste
em si (C10/C20/R²) e 8% para grandezas derivadas (K, dP/dV), que amplificam
qualquer diferença de malha ou escolha de cluster no multi-start.

Isso responde "está igual ao Composer?" sem precisar voltar pro chat — mas
me manda o `output/COMPARE_TO_COMPOSER.md` (ou só cola o conteúdo) que eu
reviso com atenção: um `DIVERGE` pode ser malha diferente (Composer usou
ne=8 fixo; aqui os 6 starts multi-start também usam ne=8 por padrão, então
não deveria divergir por isso) ou um cluster genuinamente diferente do
espaço (C10,C20) — o que seria, em si, um achado interessante sobre
identificabilidade do Yeoh (até agora eu esperava que fosse bem-condicionado
e convergisse pro mesmo ponto de qualquer start).
