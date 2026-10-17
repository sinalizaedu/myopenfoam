# claude-wp1.2 — 8 casos: 4 alvos P(V) x 2 materiais (P_final=50 mmHg)

Terceiro braco independente (Sonnet/Claude), em paralelo a `cases/wp1.2/`
(Composer/Cursor). Nao edita nada la — so importa (leitura) `Geometry`,
`fit_ogden1`, `PallikarisForward` de `fit_pallikaris.py` e `fit_yeoh2`,
`PallikarisYeohForward` de `run_e3_e1b.py`, ja validados pelo Composer.

## O que muda em relacao ao pedido

- **P_final: 80 -> 50 mmHg.** O teto da rampa de pressao na FEA agora e
  50 mmHg (o Composer ja havia migrado `DP_FEA_FINAL` para 50 em
  `fit_pallikaris.py`, entao isso confirma que os dois bracos convergiram
  independentemente na mesma conclusao — ver justificativa abaixo).
- **4 alvos P(V):**
  1. `pallikaris` — P0=16,9, Kf=0,0126 (forma exponencial ja usada no repo)
  2. `silver` — Silver & Geyer (2000), coeficientes exatos do artigo
  3. `agra` — Agra et al. (2023), bancada hidraulica (nao e olho)
  4. `friedenwald` — **recalibrado do seu WP0** (Kf=0,00581, contra o pico
     clinico de Knecht et al. 2009), **nao** o classico historico (0,0215)
- **2 materiais:** Ogden N=1 e Yeoh-2 (mesmos ajustes ja validados do
  Composer, so aplicados a alvo x material diferentes)
- **Total: 8 casos** = 4 alvos x 2 materiais

## Por que os `v_max` de cada alvo nao sao todos 50 µL

Isso e importante e nao estava no seu pedido original, entao quero deixar
explicito: **50 mmHg e um teto de pressao, nao de volume.** Quando eu inverto
cada curva P(V) para achar em que volume ela pediria mais que 50 mmHg:

| alvo | V onde a curva atinge 50 mmHg | v_max usado no caso |
|---|---:|---:|
| pallikaris (Kf=0,0126) | 37,4 µL | **35,0 µL** (margem de seguranca) |
| silver & geyer | 40,8 µL | **38,0 µL** (margem de seguranca) |
| agra (tabela) | ponto V=50→P=50,7 fica acima do teto | **40,0 µL** (so pontos com P≤50 mmHg) |
| friedenwald (WP0, adotado) | 81,1 µL | **50,0 µL** (folga ampla, cobre o padrao clinico de IVI inteiro) |

Se eu tivesse forcado todos os 4 alvos ate V=50 µL com o teto de 50 mmHg,
os casos `pallikaris` e `silver` pediriam a FEA para alcancar uma pressao
que ela nunca aplica — o ajuste falharia silenciosamente (residuo saturado
em 50 mmHg, sem sentido fisico). Truncar o volume-alvo por material e a
forma correta de manter os 8 casos consistentes com o novo teto de 50 mmHg.

Isso tambem reforca o que ja tinha aparecido na sua leitura do WP0: o alvo
`friedenwald` (recalibrado, que voce ja validou) e o unico que cobre o
volume clinico padrao de 50 µL folgadamente dentro de um teto de pressao
plausivel — os outros tres (pallikaris bruto, silver, e o ultimo ponto da
agra) already exigem pressoes acima do fisiologicamente esperado para
chegar a 50 µL.

## Arquivos criados (novos, nada editado em `cases/wp1.2/`)

- `scripts/literature_targets_claude.py` — gera as 4 curvas-alvo (CSV +
  `ExpPoint`), com o Friedenwald recalibrado do WP0 e os `v_max` seguros
  documentados acima.
- `scripts/run_literature_matrix_claude.py` — orquestrador: roda os 8
  casos (target x material), grava `fit_results.json` + `RESULTS.md` por
  caso e um `LITERATURE_MATRIX_SUMMARY_CLAUDE.md` geral.
- `Allrun_8casos_claude` — atalho de execucao.

## Rodar (dentro do container)

Todos os 8 casos:

```bash
docker compose run --rm fsi bash -lc 'cd /simulation/claude-wp1.2 && python3 scripts/run_literature_matrix_claude.py'
```

Ou, de dentro do container ja aberto:

```bash
cd cases/claude-wp1.2 && ./Allrun_8casos_claude
```

**Custo estimado:** 8 casos x ~30 nfev x ~10-15 s/CCX ≈ **1h-1h20 no total.**
Se quiser rodar por partes (ex.: so Ogden primeiro, ou so 2 alvos por vez):

```bash
# so os 4 casos Ogden (mais rapido, sem Yeoh)
python3 scripts/run_literature_matrix_claude.py --materials ogden

# so pallikaris e friedenwald, os dois materiais
python3 scripts/run_literature_matrix_claude.py --targets pallikaris,friedenwald

# ajuste mais grosseiro/rapido pra conferir que roda (menos avaliacoes)
python3 scripts/run_literature_matrix_claude.py --max-nfev 15
```

## Saida

- `output_literature_p50_claude/<target>_<material>/`
  - `<target>_target.csv` — curva-alvo usada (DeltaP acima de P0=16,9)
  - `fit_results.json` — parametros ajustados, qualidade (R2, residuo max),
    curva FEA final
  - `RESULTS.md` — resumo legivel
- `output_literature_p50_claude/LITERATURE_MATRIX_SUMMARY_CLAUDE.md` —
  tabela com os 8 casos lado a lado (R2, residuo, nfev)

## Depois de rodar

Me manda o `LITERATURE_MATRIX_SUMMARY_CLAUDE.md` (ou os 8 `fit_results.json`)
que eu comparo com o que o Composer ja tem em
`cases/wp1.2/output_literature_p50/` (se existir) e com o alvo do seu WP0.
