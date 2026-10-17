# claude-wp1.4 — piloto de biometria (14 casos), atualizado

Terceiro braço independente (Sonnet). Atualiza `cases/wp1.4/` (rodado em
22/set, ANTES do fechamento do WP1.2): lá o Yeoh usa parâmetros antigos
(C10=4.364 em vez de ~1.02) e P_final=80 (abandonado em favor de 50).

## O que este piloto testa

Até o WP1.3, tudo foi calibrado/testado num olho "padrão" (R=12mm,
t=0.5mm). Olhos de verdade variam: este piloto roda os mesmos 14 casos
de biometria do WP1.4 original (R de 11.0 a 13.5mm, t de 0.40 a 0.60mm
-- faixa anatômica normal) e mede **V_max** (volume máximo antes de
bater no teto de pressão de 50mmHg) para saber se o comportamento do
modelo é sensível ao tamanho/espessura individual do olho.

## O que muda em relação ao original

- **Material**: Ogden E Yeoh (o original só tinha Yeoh), ambos com os
  fits oficiais do fechamento do WP1.2
  (`cases/wp1.2/output_literature_p50_v2/friedenwald_{ogden,yeoh}/fit_results.json`).
- **P_final**: 50 mmHg (era 80).
- Reusa sem editar: `cases/wp1.4/data/biometry_14.csv` (mesma tabela de
  14 casos) e `cases/wp1.2/scripts/yeoh_forward_run.py`. Criei
  `ogden_forward_run.py` porque não existia equivalente para Ogden.

## Rodar (dentro do container)

```bash
docker compose run --rm fsi bash -lc \
  'cd /simulation/claude-wp1.4 && python3 scripts/run_pilot_biometry_claude.py'
```

Ou só um material: `--materials yeoh` / `--materials ogden`.

## Saída

- `output_pilot_biometry_claude/RESULTS_CLAUDE.md` — tabela dos 14
  casos, V_max Ogden vs. Yeoh lado a lado.
- `output_pilot_biometry_claude/pilot_biometry_results.json` — dados
  completos.

Custo estimado: 28 forward runs (14 casos x 2 materiais), mais rápido
que o WP1.3 (sem MULF) -- deve rodar em minutos, não horas.
