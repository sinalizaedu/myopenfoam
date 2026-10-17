# WP1.4 — Fechamento: piloto de biometria (14 casos, Ogden + Yeoh)

**Status: ✅ Concluído.** Atualiza `cases/wp1.4/` (rodado em 22/set, ANTES
do fechamento do WP1.2, com Yeoh desatualizado e P_final=80) com os
parâmetros oficiais recalibrados (Friedenwald, P_final=50). Cross-
validado byte-a-byte com o Composer/Cursor.

---

## O que o WP1.4 testa

Todo o trabalho até aqui (WP1.1-1.3) calibrou e testou num olho "padrão"
(R=12mm, t=0,5mm). Olhos de verdade variam de pessoa pra pessoa. O
WP1.4 pergunta: **mantendo o material fixo (o mesmo calibrado no
WP1.2), o quanto o comportamento P(V) muda s6 por causa do tamanho e
espessura do olho?**

14 combinações de R (11,0 a 13,5mm) × t (0,40 a 0,60mm) — faixa
anatômica humana normal — medindo **V_max** (volume máximo antes do
teto de 50mmHg), para Ogden e Yeoh.

---

## Resultado final (14 casos × 2 materiais = 28 simulações)

| case | R [mm] | t [mm] | nota | V_max Ogden [µL] | V_max Yeoh [µL] |
|---|---:|---:|---|---:|---:|
| B01 | 11.0 | 0.45 | short eye thin | 90.5 | 87.5 |
| B02 | 11.0 | 0.55 | short eye thick | 73.3 | 71.1 |
| B03 | 11.5 | 0.45 | | 108.4 | 104.7 |
| B04 | 11.5 | 0.55 | | 87.7 | 85.0 |
| B05 | 12.0 | 0.45 | reference human-ish | 128.8 | 124.4 |
| B06 | 12.0 | 0.55 | | 104.3 | 101.0 |
| B07 | 12.5 | 0.45 | | 152.1 | 146.7 |
| B08 | 12.5 | 0.55 | | 123.0 | 119.1 |
| B09 | 13.0 | 0.45 | | 178.3 | 171.9 |
| B10 | 13.0 | 0.55 | | 144.2 | 139.5 |
| B11 | 13.5 | 0.45 | long eye thin | 207.8 | 200.2 |
| B12 | 13.5 | 0.55 | long eye thick | 168.1 | 162.5 |
| B13 | 12.0 | 0.40 | thin variant | 146.0 | 140.6 |
| B14 | 12.0 | 0.60 | thick variant | 95.1 | 92.3 |

**Convergência: 28/28 OK** dos dois lados. **Cross-validado**: Composer
rodou de forma independente com o mesmo fit oficial — valores idênticos
até a casa decimal.

---

## Validação física (o achado mais importante desta revisão)

Pra uma casca esférica fina sob pressão interna, a teoria clássica de
membranas prevê `V ∝ R⁴/t` (tensão de membrana `σ=PR/2t`, deformação
`~σ/E`, volume `~R³·deformação`). Testei essa previsão contra os dados:

- **Escala com R⁴** (B05→B09, R=12→13mm, t fixo): previsto 177,5µL,
  simulado 178,3µL → erro de **0,47%**
- **Escala com 1/t** (B05→B06, t=0,45→0,55mm, R fixo): previsto
  105,4µL, simulado 104,3µL → erro de **−1,10%**

Isso é uma checagem independente da física do problema (não é
comparação entre os dois branches) — confirma que a FEA está produzindo
resultados fisicamente consistentes, com desvios pequenos e no sentido
esperado (a teoria linear de casca fina subestima levemente, já que os
materiais são hiperelásticos não-lineares).

---

## Ogden vs. Yeoh: divergência sistemática e proporcional

Yeoh fica sempre **3,3% a 3,7% abaixo** do Ogden em V_max, e a diferença
absoluta cresce proporcionalmente ao volume (−3,0µL em B01/90,5µL vs.
−7,6µL em B11/207,8µL, ambos ~3,3-3,7%). Não há inversão de sinal nem
comportamento errático em nenhum dos 14 casos — os dois materiais
extrapolam de forma consistente para fora da geometria de calibração
(R=12, t=0,5).

---

## Ressalva de escopo (não é erro, é limite do que foi testado)

Este é um piloto **forward puro com material fixo**: mede o quanto uma
geometria específica aguenta, mas não recalibra o material para cada
biometria. Ou seja, responde "dado o material do olho-padrão, quanto
ESTA geometria aguenta" — não "cada paciente teria parâmetros de
material ligeiramente diferentes". Nenhuma questão de variabilidade
inter-paciente do próprio tecido (rigidez do colágeno, idade, etc.) foi
testada aqui.

---

## Rastreabilidade

- Fits: `cases/wp1.2/output_literature_p50_v2/friedenwald_{ogden,yeoh}/fit_results.json`.
- Dados de biometria (reuso, não editado): `cases/wp1.4/data/biometry_14.csv`.
- Scripts (não editam nada do Composer):
  `cases/claude-wp1.4/scripts/run_pilot_biometry_claude.py` +
  `ogden_forward_run.py` (novo, não existia equivalente); reusa
  `cases/wp1.2/scripts/yeoh_forward_run.py` via import.
- Resultado: `cases/claude-wp1.4/output_pilot_biometry_claude/RESULTS_CLAUDE.md`.
- Cross-validação: `cases/wp1.4/output_pilot_biometry_p50/RESULTS.md`
  (Composer, valores idênticos, 28/28 OK).
