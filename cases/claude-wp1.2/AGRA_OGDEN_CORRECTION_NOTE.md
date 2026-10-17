# Correção pendente: Agra-Ogden (matriz oficial `cases/wp1.2/`)

**Não editado no arquivo original** (`cases/wp1.2/output_literature_p50_v2/`)
por regra do projeto — esta nota só aponta a correção, quem decide promover
pro arquivo oficial é o Composer/Cursor.

## O problema

`cases/wp1.2/output_literature_p50_v2/agra_ogden/fit_results.json` e
`LITERATURE_MATRIX_SUMMARY.md` ainda reportam o ajuste **preso no limite
da caixa de busca** (α₁ no bound superior = 6,0):

```json
{"mu1_MPa": 5.185, "alpha1": 5.999, "D1": 0.0984, "R2": 0.9385}
```

## O valor correto

Confirmado pelo estudo `output_caveats_p50/ogden_alpha_wide/agra/`
(multi-start com α₁∈[0,15, 10], fora da caixa original [0,5, 6]):

```json
{"mu1_MPa": 5.198, "alpha1": 0.186, "D1": 0.098, "R2": 0.9538}
```

R² sobe de 0,9385 para 0,9538 — o ajuste antigo não era o ótimo, estava
artificialmente limitado pelo bound superior de α₁=6,0 da matriz original.

## Ação recomendada

Atualizar `cases/wp1.2/output_literature_p50_v2/agra_ogden/fit_results.json`
e a linha do Agra-Ogden em `LITERATURE_MATRIX_SUMMARY.md` com os valores
acima, citando `output_caveats_p50/ogden_alpha_wide/agra/multistart_results.json`
como fonte (campo `global_best`).

Não afeta o alvo principal adotado (Friedenwald), que já estava correto.
