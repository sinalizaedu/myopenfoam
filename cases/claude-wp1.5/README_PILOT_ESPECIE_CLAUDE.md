# claude-wp1.5 — piloto de espécie (humano + coelho), atualizado

Terceiro braço independente (Sonnet). Atualiza `cases/wp1.5/` (rodado em
22/set, ANTES do fechamento do WP1.2): lá o Yeoh usa parâmetros antigos
e P_final=80.

## O que este piloto testa

A maior parte dos dados de literatura usados pra calibrar (WP1.2) vem
de estudos em **coelho**, extrapolados pra humano. Este piloto aplica o
MESMO material calibrado (humano) na geometria de um olho de coelho
(bem menor: R=7,6mm, t=0,33mm vs. R=12mm, t=0,5mm do humano) e mede
V_max e a rigidez inicial (K_eff), pra ver se a diferença de escala
entre as espécies é grande e em que direção.

## O que muda em relação ao original

- **Material**: Ogden E Yeoh (original só tinha Yeoh), fits oficiais do
  fechamento do WP1.2 (`friedenwald_{ogden,yeoh}/fit_results.json`).
- **P_final**: 50 mmHg (era 80).
- Mesmas geometrias de espécie do original (`SPECIES` em
  `cases/wp1.5/scripts/run_pilot_yeoh.py`, leitura apenas).

## Rodar (dentro do container)

```bash
docker compose run --rm fsi bash -lc \
  'cd /simulation/claude-wp1.5 && python3 scripts/run_pilot_species_claude.py'
```

## Saída

- `output_pilot_species_claude/RESULTS_CLAUDE.md` — V_max e K_eff,
  Ogden vs. Yeoh, humano vs. coelho.
- `output_pilot_species_claude/pilot_species_results.json` — dados
  completos.

Custo: só 4 simulações forward (2 espécies x 2 materiais) — rápido.
