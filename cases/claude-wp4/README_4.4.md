# WP4.4 — Validação teórica contra o zero observado

## O que este módulo faz (`claude_validacao_zero_observado.py`)

Construído sobre o 4.3 (`claude_h6_teorico.py::dose_fechada_H6`) e o 4.1
(`claude_opp_perfusion.py::opp_crit_efetivo`). Etapa inteiramente
computacional (literatura publicada vs. simulação 0D) — sem dado
próprio, conforme o plano.

### Peça 1 — consistência com o zero do OCT-A 2026 (n=54)

O estudo relata ausência de déficit perfusional mensurável durante um
pico típico de IOP pós-IVI (14→31 mmHg), com MOPP≈31 mmHg relatado
diretamente pelo estudo durante o evento (usamos esse valor **relatado**,
não recalculado a partir de MAP populacional genérica — o estudo tem seu
próprio MAP de coorte que não reproduzimos aqui).

- `K_implicito_do_pico_observado()` = (31−14)/50 = **0,34 mmHg/µL** — não
  é um K medido independentemente, é uma leitura do próprio pico
  relatado, útil como âncora de ordem de grandeza.
- `tabela_consistencia_zero_oct_a()`: o modelo prediz 𝓘=0 (consistente
  com o zero observado) para **qualquer OPP_crit ≤ 31 mmHg**, e 𝓘>0
  (inconsistente) acima disso. Isso responde diretamente à pergunta do
  plano: o limiar crônico usualmente citado (~50 mmHg) **não pode
  explicar o zero observado se também for aplicado a eventos
  transitórios** — o limiar efetivo para eventos agudos, se existir,
  tem que estar ≤31 mmHg, bem abaixo do limiar crônico.

### Peça 2 — subgrupo de risco de Damasceno et al. 2022

CRAO transitória ocorreu em 0,44% das injeções (18/4069); destes, 66,6%
tinham obstrução carotídea ≥70%.

`subgrupo_risco_damasceno()` compara, no MESMO cenário basal (mesmo
`dPth_basal`, mesmo `OPP_crit_ref`): paciente típico (K=0,34, φ_vasc=1)
vs. subgrupo de risco (K alto=1,0 "olho curto", φ_vasc=1,3 "obstrução
carotídea"). Resultado (cenário ilustrativo dPth_basal=20, OPP_crit_ref=25):

```
Típico:  dPth=20,0 mmHg  →  I = 0,0 mmHg·min   (consistente com OCT-A)
Risco:   dPth=12,5 mmHg  →  I = 72,0 mmHg·min  (consistente com a associação
                                                  observada obstrução↔CRAO)
```

Mesmo cenário basal, dois desfechos opostos — só por causa de K e
φ_vasc. Isso é a assinatura que o plano pede: o modelo prevê risco
diferencial exatamente no subgrupo que a literatura já identificou como
de risco, sem precisar recalibrar nada.

### Peça 3 — controle negativo (OCT ultra-precoce)

Afinamento retiniano de 25% aos 15 min pós-IVI, resolvido em 48h,
atribuído a compressão mecânica (PMC13307848) — **não** isquemia.
`controle_negativo_afinamento_mecanico()` não calcula nada: documenta
explicitamente por que o modelo **não pode** confundir esse achado com
dose isquêmica — o modelo vive inteiramente no espaço de pressão de
perfusão ao longo do tempo (MOPP/OPP_diast), não tem nenhuma variável de
espessura estrutural, e a escala de tempo (resolução em 48h) é
incompatível com um processo hemodinâmico agudo.

## Testes

`test_claude_validacao_zero_observado.py` — 10 testes, incluindo:
- K implícito bate com o pico relatado (0,34 mmHg/µL)
- tabela de consistência com veredito correto (incluindo a fronteira
  OPP_crit=31 exatamente)
- subgrupo de risco: típico dá zero, risco dá positivo, no mesmo
  cenário basal
- rejeição correta (marcado como "regime crônico", não NaN) quando
  φ_vasc é alto o bastante para já cruzar o limiar mesmo sem injeção
- estrutura e valores do controle negativo conferem com o plano

Rodar:
```bash
cd cases/claude-wp4
../wp0/.venv/bin/python -m pytest -v test_claude_validacao_zero_observado.py
```
