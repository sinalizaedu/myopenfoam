# WP1.5 — Fechamento: piloto de espécie (humano + coelho)

**Status: ✅ Concluído.** Atualiza `cases/wp1.5/` (rodado em 22/set, ANTES
do fechamento do WP1.2, só Yeoh e P_final=80) com os parâmetros oficiais
recalibrados (Friedenwald, P_final=50) e adiciona Ogden. Cross-validado
byte-a-byte com o Composer/Cursor.

---

## O que o WP1.5 testa

A maior parte dos dados de literatura usados pra calibrar (WP1.2) vem de
estudos em **coelho**, extrapolados pra humano. Este piloto aplica o
MESMO material calibrado num humano na geometria de um olho de coelho
(bem menor: R=7,6mm, t=0,33mm vs. R=12mm, t=0,5mm) e mede V_max e a
rigidez inicial (K_eff), pra checar a diferença de escala entre espécies.

---

## Resultado final (2 espécies × 2 materiais = 4 simulações)

| espécie | R [mm] | t [mm] | V_max Ogden [µL] | K_eff Ogden | V_max Yeoh [µL] | K_eff Yeoh |
|---|---:|---:|---:|---:|---:|---:|
| humano | 12,0 | 0,5 | 115,3 | 0,300 | 111,5 | 0,392 |
| coelho | 7,6 | 0,33 | 28,0 | 1,232 | 27,1 | 1,612 |

**Convergência: 4/4 OK** dos dois lados. **Cross-validado**: Composer
rodou de forma independente com o mesmo fit oficial — valores idênticos
até a casa decimal (incluindo ΔV e ΔK entre materiais).

### Resposta

O olho de coelho é **~4,1x menos complacente** que o humano na mesma
faixa de pressão (V_max ~4,1x menor, K_eff inicial ~4,1x maior) — em
ambos os materiais. Isso é relevante pra quem for usar os dados de
literatura (majoritariamente em coelho) pra validar contra dados
clínicos humanos: a diferença de escala geométrica sozinha já explica
boa parte da diferença de rigidez aparente entre as espécies, sem
precisar invocar diferença de material biológico entre elas.

---

## Validação física

Mesma checagem de casca fina do WP1.4 (`V ∝ R⁴/t`), agora usada pra
prever a razão humano/coelho a partir só da geometria:

```
previsto: V_humano/V_coelho = (R_h/R_c)⁴ · (t_c/t_h) = (12/7,6)⁴ · (0,33/0,5) = 4,102
real Ogden: 115,3/28,0 = 4,118  (erro 0,4%)
real Yeoh:  111,5/27,1 = 4,114  (erro 0,3%)
```

A mesma proporção aparece invertida em K_eff (coelho/humano ≈ 4,11 em
ambos os materiais) — consistente, porque K_eff é aproximadamente
proporcional a 1/V nessa faixa. Bate com <0,4% de erro nos quatro casos
— forte evidência de que a simulação está capturando a física certa, e
não é coincidência do cross-check entre os dois branches.

---

## Ressalva de escopo

Mesma do WP1.4: é forward puro com material fixo (o calibrado pro olho
humano), aplicado à geometria de coelho — não recalibra o material para
o tecido escleral de coelho, que biologicamente é diferente do humano
(colágeno, espessura de camadas, etc.), só testa o efeito puramente
geométrico da escala. Além disso, é uma "casca esférica simplificada"
— não modela a anatomia completa do globo (córnea, câmara anterior),
que é bem diferente entre as espécies.

---

## Rastreabilidade

- Fits: `cases/wp1.2/output_literature_p50_v2/friedenwald_{ogden,yeoh}/fit_results.json`.
- Geometrias de espécie (reuso, não editado): `cases/wp1.5/scripts/run_pilot_yeoh.py` (dict SPECIES).
- Scripts (não editam nada do Composer):
  `cases/claude-wp1.5/scripts/run_pilot_species_claude.py` +
  `ogden_forward_run.py` (mesmo do claude-wp1.4); reusa
  `cases/wp1.2/scripts/yeoh_forward_run.py` via import.
- Resultado: `cases/claude-wp1.5/output_pilot_species_claude/RESULTS_CLAUDE.md`.
- Cross-validação: `cases/wp1.5/output_pilot_species_p50/RESULTS.md`
  (Composer, valores idênticos, 4/4 OK).
