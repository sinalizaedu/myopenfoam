# Achado: bug na relaxação do MULF (`cases/wp1.2/scripts/mulf_gee.py`)

**Não editado no arquivo original** (regra do projeto) — esta nota só
aponta o problema; quem decide corrigir o arquivo oficial é o
Composer/Cursor. Uma versão corrigida, separada, está em
`cases/claude-wp1.3/scripts/mulf_gee_fixed_relax_claude.py` para teste.

## O problema

`mulf_iterate()` em `mulf_gee.py` atualiza a estimativa da configuração
de referência assim:

```python
x_next[nid] = xo - b * du[nid]   # = X_obs - beta * u(X_ref_atual)
```

Isso é o ponto fixo de um mapa `h(X) = X_obs - beta*u(X)`. Mas o método
de Gee et al. (2010) pede o ponto fixo de `g(X) = X_obs - u(X)` (sem o
beta multiplicando `u`). A relaxação de Picard padrão para `g` deveria
misturar com o `X_ref` da **iteração anterior**, não com `X_obs` fixo:

```
X_ref^(k+1) = (1-beta)*X_ref^(k) + beta*(X_obs - u(X_ref^(k)))
```

Como `h ≠ g` (a menos que beta=1), o algoritmo converge — mas para o
ponto fixo de `h`, que **não** é a configuração de referência que o
MULF pede.

## Confirmação numérica (nos 8 casos já rodados)

Se a causa é essa, o `verify_error_mm` reportado deveria ser exatamente
`(1-beta)*u_max` (não um erro numérico genuíno). Conferido nos 8 casos:

| caso | u_max (mm) | verify_err reportado | (1-beta)·u_max previsto | razão |
|---|---:|---:|---:|---:|
| agra_ogden | 0.013980 | 0.004194 | 0.004194 | 1.000 |
| agra_yeoh | 0.014319 | 0.004296 | 0.004296 | 1.000 |
| friedenwald_ogden | 0.032085 | 0.009630 | 0.009626 | 1.000 |
| friedenwald_yeoh | 0.031305 | 0.009396 | 0.009391 | 1.001 |
| pallikaris_ogden | 0.017133 | 0.005141 | 0.005140 | 1.000 |
| pallikaris_yeoh | 0.017614 | 0.005285 | 0.005284 | 1.000 |
| silver_ogden | 0.013205 | 0.003962 | 0.003962 | 1.000 |
| silver_yeoh | 0.013457 | 0.004037 | 0.004037 | 1.000 |

Bate em todos os 8 (razão 1.000). O `verify_error_mm < 0.05mm` que
estava sendo usado como "prova de convergência do MULF" é, na verdade,
**tautológico** — mede o próprio viés da fórmula, não uma checagem
física independente.

## Impacto esperado

- A comparação **relativa** entre os 8 casos provavelmente se mantém
  (mesmo beta=0.7, mesmo bug em todos) — a conclusão qualitativa (Yeoh
  amolece em geral, Ogden diverge no Agra) não deveria se inverter.
- Os valores **absolutos** de Δ% de rigidez podem mudar, porque a
  configuração de referência encontrada está sistematicamente
  sub-corrigida (falta ~30% do deslocamento de retração, já que
  beta=0.7).

## Ação recomendada

1. Rodar `cases/claude-wp1.3/scripts/run_pretension_matrix_fixed_claude.py`
   (relaxação corrigida) e comparar com
   `output_pretension_8cases/PRETENSION_MATRIX_SUMMARY_CLAUDE.md`.
2. Se a diferença for pequena (poucos pp), promover a correção pra
   `mulf_gee.py` oficial é de baixo risco. Se for grande, vale re-rodar
   os 8 casos oficiais do WP1.3 com a fórmula corrigida antes de reportar
   os números como finais.
3. Alternativa mais simples pra testar rápido: rodar com `--beta 1.0`
   nos scripts originais (sem relaxação) — nesse caso h=g e o bug não
   tem efeito, mas a convergência pode ficar instável/oscilar.
