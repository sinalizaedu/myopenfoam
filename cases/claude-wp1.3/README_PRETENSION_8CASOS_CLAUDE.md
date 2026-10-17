# claude-wp1.3 — pré-tensão (MULF Gee 2010) para os 8 casos do WP1.2

Terceiro braço independente (Sonnet/Claude), em paralelo a `cases/wp1.3/`
(Composer/Cursor). Não edita nada lá — só **chama** (via `subprocess`) o
script já validado `run_wp13_mulf_gee.py` para cada uma das 8 combinações
(4 alvos × 2 materiais) da matriz oficial do WP1.2.

## O que já existia vs. o que isto adiciona

O WP1.3 já tinha testado a divergência de pré-tensão (Ogden endurece
levemente, Yeoh amolece bastante) **só para o alvo Friedenwald**
(`wp1_octant/output/wp1.3-{ogden,yeoh}-new/`, P_final=50). Isso confirmou
que a divergência **não é** artefato do bug/P_final=80 antigo.

**O que ainda não sabíamos:** se essa divergência é uma característica dos
próprios materiais (Ogden vs. Yeoh, universal, aparece com qualquer
calibração) ou é específica de como o Friedenwald foi calibrado. Este
script responde isso rodando o **mesmo teste MULF** para os outros 3
alvos (Pallikaris, Silver, Agra) que ainda não tinham sido testados.

## Alvos e parâmetros usados

Os 8 fits vêm da matriz oficial do WP1.2
(`cases/wp1.2/output_literature_p50_v2/<alvo>_<material>/fit_results.json`),
já com a correção do Agra-Ogden aplicada (α₁≈0,19, R²=0,954) — a mesma
fonte usada no fechamento do WP1.2.

## Rodar (dentro do container)

Todos os 8 casos:

```bash
docker compose run --rm fsi bash -lc \
  'cd /simulation/claude-wp1.3 && python3 scripts/run_pretension_matrix_claude.py'
```

Ou por partes:

```bash
# só um alvo
python3 scripts/run_pretension_matrix_claude.py --targets pallikaris

# só um material
python3 scripts/run_pretension_matrix_claude.py --materials yeoh
```

**Custo estimado:** cada caso roda um MULF (até 12 iterações de FEA para
achar a configuração de referência relaxada) + 1 curva de carga (24
passos) — mais caro que um fit simples. Com 8 casos, espere algo entre
1h e 2h no total (a mesma ordem de grandeza dos outros estudos MULF já
rodados).

## Saída

- `output_pretension_8cases/<alvo>_<material>/pretension_mulf_gee.json` —
  resultado completo (convergência do MULF, curva P(V), K local em V≈0 e
  V_ref, sweep de V_ref).
- `output_pretension_8cases/<alvo>_<material>/RESULTS.md` — resumo legível
  por caso.
- `output_pretension_8cases/PRETENSION_MATRIX_SUMMARY_CLAUDE.md` — tabela
  com os 8 casos lado a lado (Δ% de rigidez local por alvo × material).

## Depois de rodar

Me manda o `PRETENSION_MATRIX_SUMMARY_CLAUDE.md` que eu comparo com o
resultado equivalente do Composer (prompt espelhado sugerido à parte) e
respondo à pergunta: a divergência Ogden/Yeoh é geral ou específica do
Friedenwald?
