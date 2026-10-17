# WP1.3 — Fechamento: sensibilidade à pré-tensão (MULF Gee 2010)

**Status: ✅ Concluído**, incluindo a correção de um bug real na relaxação
do MULF, encontrado nesta revisão e **cross-validado de forma
independente** entre este braço (Sonnet) e o Composer/Cursor.

---

## Pergunta que o WP1.3 respondeu

A divergência observada no caso original (Friedenwald, P_final=50):
**Ogden endurece levemente sob pré-tensão, Yeoh amolece muito** — é uma
característica **geral** dos dois modelos constitutivos, ou é específica
de como o Friedenwald foi calibrado?

Testado nas 8 combinações da matriz oficial do WP1.2 (4 alvos × 2
materiais): Pallikaris, Silver, Agra, Friedenwald recalibrado.

---

## Resultado final (8 casos, relaxação MULF corrigida)

| Alvo | Material | Δ% rigidez (corrigido) | Δ% original (bug) | diferença | MULF | verify_err [mm] |
|---|---|---:|---:|---:|---|---:|
| Pallikaris | Ogden | **+1.29%** | +1.29% | 0.00 | OK | 1.37e-04 |
| Pallikaris | Yeoh | **−37.66%** | −37.66% | 0.00 | OK | 1.41e-04 |
| Silver | Ogden | **+1.29%** | +1.30% | −0.01 | OK | 3.54e-04 |
| Silver | Yeoh | **−37.63%** | −37.63% | 0.00 | OK | 3.60e-04 |
| Agra | Ogden | **−28.33%** ⚠️ | −28.34% | +0.01 | OK | 3.74e-04 |
| Agra | Yeoh | **−37.65%** | −37.65% | 0.00 | OK | 3.83e-04 |
| Friedenwald | Ogden | **+1.32%** | +1.32% | 0.00 | OK | 2.55e-04 |
| Friedenwald | Yeoh | **−42.23%** | −42.36% | +0.12 | OK | 2.49e-04 |

**Cross-validado duplamente**: (1) Composer e Claude bateram nos 8 casos
originais (com o bug); (2) Composer e Claude, de forma independente,
diagnosticaram o mesmo bug de relaxação, implementaram a mesma correção,
e bateram de novo nos 8 casos corrigidos (diferença ≤0,12pp).

### Resposta

- **Yeoh amolece sob pré-tensão em TODOS os alvos** (−37,6% a −42,2%,
  spread de só ~5pp). **Característica geral do modelo**, não artefato
  da calibração Friedenwald.
- **Ogden endurece em 3 dos 4 alvos** (+1,29% a +1,32%) — **também
  geral**, com uma exceção real: **Agra-Ogden amolece (−28,33%)**. Ver
  ressalva abaixo.
- A correção do bug de relaxação (ver seção seguinte) **não muda a
  conclusão** — os Δ% mudam no máximo 0,12pp.

---

## Achado técnico: bug na relaxação do MULF (encontrado e corrigido nesta revisão)

Ao revisar a implementação como um "especialista em simulação" (pedido
explícito da Bruna), encontrei que `mulf_iterate()` em
`cases/wp1.2/scripts/mulf_gee.py` tinha a fórmula de relaxação errada:

```python
x_next = x_obs - beta * u(x_ref_atual)      # ponto fixo de h(x) = x_obs - beta*u(x)
```

O MULF de Gee et al. (2010) pede o ponto fixo de `g(x) = x_obs - u(x)`
(sem o beta multiplicando `u`). A relaxação de Picard correta mistura
com o `x_ref` da iteração anterior, não com `x_obs` fixo:

```python
x_next = (1-beta)*x_ref_atual + beta*(x_obs - u(x_ref_atual))   # ponto fixo de g
```

**Prova de que era um bug real, não estilo de código**: o
`verify_error_mm` que os 8 casos originais reportavam batia
*exatamente* com `(1-beta)*u_max` em todos eles (razão 1.0000–1.0005) —
ou seja, o "erro de verificação" usado como prova de convergência era
tautológico, gerado pelo próprio bug, não uma checagem física
independente.

**Impacto real, medido**: rodei os 8 casos com a fórmula corrigida
(`cases/claude-wp1.3/scripts/mulf_gee_fixed_relax_claude.py`, sem
editar o arquivo original do Composer) e o Composer fez o mesmo
diagnóstico e teste, de forma independente. Resultado:
- Os Δ% de rigidez praticamente não mudam (≤0,12pp) — a conclusão do
  WP1.3 permanece válida.
- O `verify_error_mm` cai de ~4–10×10⁻³ mm (tautológico) para
  ~1–4×10⁻⁴ mm (uma ordem de grandeza menor, e agora sim uma checagem
  física genuína de que a configuração de referência recupera a forma
  observada).

**Não editei `mulf_gee.py`** (regra do projeto) — documentei em
`MULF_RELAXATION_BUG_NOTE_CLAUDE.md` e testei em arquivos separados. O
Composer confirmou o achado de forma independente e decide se promove a
correção para o arquivo oficial.

---

## Ressalva: o caso Agra-Ogden (−28,33%)

**Decisão de escopo:** a conclusão principal ("Ogden endurece ~1,3%") é
sustentada pelos 3 alvos de origem **clínica/in vivo** (Pallikaris,
Silver, Friedenwald). O Agra é dado de **bancada (ex-vivo)** — o
mecanismo de pré-tensão que o MULF modela (tecido esticado pela pressão
intraocular basal em olho vivo, com tônus ativo) não necessariamente
existe da mesma forma em um globo ex-vivo. O Agra-Ogden entra como nota
à parte, não como contraexemplo da conclusão principal.

**Confirmado que NÃO é artefato numérico** (nem do bug de relaxação,
nem de escolha de V_ref): MULF converge limpo com a fórmula corrigida
(verify_err 3,7×10⁻⁴mm) e o amolecimento se mantém negativo em toda a
faixa de V_ref testada (−14,5% a −50,5%).

**Hipótese não testada (trabalho futuro):** o Agra é o único alvo
calibrado com apenas 4 pontos de tabela (faixa estreita, 20-50µL) —
pode ser efeito de calibração pouco restringida, não propriedade
intrínseca do Ogden.

---

## Trabalho futuro (não bloqueia o fechamento)

1. **Por que o Yeoh amolece tanto?** Hipótese: rigidez tangente do Yeoh
   perto de deformação zero ≈ 2×C₁₀; C₁₀ caiu muito mais que C₂₀ na
   recalibração, deixando o material desproporcionalmente mole perto de
   zero-strain. Não escala linearmente com C₂₀/C₁₀ — precisaria de
   sweep dedicado de C₁₀ para confirmar.
2. **Por que o Agra-Ogden quebra o padrão?** Hipótese: poucos pontos de
   calibração (4, faixa estreita) deixam o ajuste pouco restringido.
   Precisaria de um alvo sintético de controle (mesma faixa/nº de
   pontos, origem clínica) para isolar "poucos pontos" de "bancada".

Nenhuma das duas é necessária para responder à pergunta original do
WP1.3 — ambas ficam como próximo passo.

---

## Figuras sugeridas (descritas, não geradas)

1. **Barras Δ% por alvo × material** (valores corrigidos) — 4 grupos,
   2 barras cada, linha em 0%.
2. **Curva P(V) antes/depois do MULF**, um painel por material,
   sobrepondo os 4 alvos.
3. **Sweep de V_ref para Agra-Ogden** (Δ% vs. V_ref, 1 a 20µL).

---

## Rastreabilidade

- Fits: `cases/wp1.2/output_literature_p50_v2/<alvo>_<material>/fit_results.json`.
- Scripts (não editam nada do Composer):
  - `cases/claude-wp1.3/scripts/run_pretension_matrix_claude.py` (relaxação original, reuso do script do Composer via subprocess).
  - `cases/claude-wp1.3/scripts/mulf_gee_fixed_relax_claude.py` + `run_wp13_mulf_gee_fixed_claude.py` + `run_pretension_matrix_fixed_claude.py` (relaxação corrigida).
- Resultados: `output_pretension_8cases/` (original) e
  `output_pretension_8cases_fixed_relax/` (corrigido).
- Bug documentado: `MULF_RELAXATION_BUG_NOTE_CLAUDE.md`.
- Cross-validação original: `cases/wp1.3/output_pretension_8cases/PRETENSION_MATRIX_SUMMARY.md` (Composer, valores idênticos).
- Cross-validação da correção: Composer reproduziu o mesmo bug (razão 1.0000–1.0005) e os mesmos Δ% corrigidos (diferença ≤0,12pp), de forma independente.
