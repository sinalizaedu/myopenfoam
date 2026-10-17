# WP4.3 — Resultado teórico H6 (versão corrigida)

## O que já existia (não duplicado)

`cases/claude-wp4/claude_dose_isquemica.py::validacao_fechada_H6()` (4.2)
já implementa e valida numericamente a fórmula fechada de H6 contra o
solver 0D (erro ~0,17% no cenário humano, `OPP_crit_ref=38`). Esse módulo
usa `Protocol`/`PV` concretos e serve para **checar consistência interna**
do solver.

## O que este módulo adiciona (`claude_h6_teorico.py`)

O item 4.3 do plano pede as **três consequências** da fórmula fechada,
apresentadas como funções dos parâmetros — nunca com um valor fixo. Isso
é conceitualmente diferente de "validar contra o solver": aqui a fórmula
é reescrita em termos dos parâmetros primitivos (K, ΔV, C_out, ΔP_th),
para poder variar cada um livremente sem rodar o solver 0D a cada ponto.

1. `dose_fechada_H6(K, dV, C, dPth)` — a fórmula fechada em si, em termos
   primitivos. **Confirmado idêntico** (`rel=1e-9`) ao `I_fechado` que
   `validacao_fechada_H6()` (4.2) calcula internamente, no mesmo cenário
   — duas implementações da mesma fórmula, caminhos de código diferentes
   (teste `test_dose_fechada_H6_bate_com_validacao_fechada_H6_do_4_2`).
2. `K_crit(dPth, dV)` — Consequência 2. **Reproduz exatamente o exemplo
   citado no plano**: dPth=15 mmHg, ΔV=50 µL → K_crit=0,30 mmHg/µL.
3. `limite_superior_dV_sobre_C(dV, C)` — Consequência 1. Confirmado que
   `dose_fechada_H6` satura nesse valor quando K→∞, e fica estritamente
   abaixo dele para qualquer K finito.
4. `curva_I_vs_K()`, `curva_I_vs_dPth()`, `K_crit_vs_dPth()` — varreduras
   exigidas pelo **alerta metodológico** do plano ("apresente 𝓘 e K_crit
   como função de ΔP_th, nunca com um valor fixo"). `curva_I_vs_dPth` e
   `K_crit_vs_dPth` marcam `None` para ΔP_th≤0 (fora do domínio: perfusão
   basal já abaixo do limiar mesmo sem injeção), em vez de quebrar a
   varredura inteira ou devolver NaN silencioso.
5. `verificar_escala_linear_C_out()` / `escala_C_out()` — Consequência 3.
   Confirmado analiticamente (não é aproximação numérica: τ=1/(C·K) é o
   único lugar em que C aparece na fórmula, e multiplica tudo) que
   `I(C/2) = 2·I(C)` **exatamente** — testado com `rel=1e-9`.

## Verificação numérica dos três achados (rodada nesta sessão)

Cenário do próprio plano (dPth=15 mmHg, ΔV=50 µL, C_out=0,28 µL/min/mmHg):

```
dV/C (limite superior, Consequência 1) = 178,57 mmHg·min

K_crit = 0,30 mmHg/µL  (bate com o plano)
  K=0,050 → I=0        K=0,300 → I=0       (abaixo de K_crit: zero exato)
  K=0,310 → I=0,09      K=1,000 → I=60,50
  K=3,000 → I=119,60   (crescendo em direção a 178,57, nunca ultrapassa)

Escala em C_out (Consequência 3), K=0,5, dPth=15:
  I(C=0,28)  = 16,70 mmHg·min
  I(C=0,14)  = 33,39 mmHg·min   (razão = 2,0000, exatamente 1/fator)
```

## Ressalva sobre `dPth<=0`

A fórmula fechada de H6 pressupõe que a perfusão basal (sem injeção) já
está **acima** do limiar (dPth>0). Se dPth≤0, o regime é outro (o
paciente já estaria cronicamente abaixo do limiar mesmo sem evento
agudo) — fora do escopo de H6, que modela o efeito **transitório** de
uma injeção. Todas as funções deste módulo levantam `ValueError` (não
NaN) nesse caso, ou marcam `None` nas varreduras (`curva_I_vs_dPth`,
`K_crit_vs_dPth`) para não quebrar a varredura inteira por um ponto fora
de domínio — mesma convenção já usada em `validacao_fechada_H6` (4.2).

## Testes

`test_claude_h6_teorico.py` — 13 testes, incluindo:
- `K_crit` reproduz o exemplo do plano (0,30 mmHg/µL)
- dose exatamente zero abaixo de K_crit, positiva acima, contínua na
  fronteira (sem salto artificial)
- saturação em dV/C para K grande, e I estritamente abaixo do limite
  para qualquer K finito
- monotonicidade de I(K)
- escala linear exata em C_out (razão bate com 1/fator a 1e-9)
- consistência com `validacao_fechada_H6` do 4.2 (mesma fórmula, dois
  caminhos de código)
- rejeição correta (ValueError / None) fora do domínio (dPth≤0)

Rodar:
```bash
cd cases/claude-wp4
../wp0/.venv/bin/python -m pytest -v test_claude_h6_teorico.py
```

## Revisão feita antes de começar o 4.3 (a pedido da Bruna)

Antes de escrever este módulo, reconferi:
- **WP1.5 (correção de P0 por espécie, sessão atual)**: revisei o código
  de `run_pilot_species_corrected_claude.py` e dos módulos `_v2_claude`
  linha a linha — `p_targets`, inserção do ponto P0 em `write_deck`,
  filtro de `dV_uL>0` no cálculo de K_eff, e a amplitude ΔP idêntica
  entre espécies. Nenhum bug encontrado; confirmei também que os
  `fit_results.json` que o script vai usar existem no repo.
- **4.1 (`claude_opp_perfusion.py`)**: releitura completa — 9/9 testes
  passando.
- **4.2 (`claude_dose_isquemica.py`)**: releitura completa — encontrei e
  corrigi **um bug pequeno (cosmético, não numérico)**: a mensagem de
  erro de `validacao_fechada_H6()` ainda citava `protocolo_goldmann_consistente()`,
  nome antigo da função que foi substituída por
  `protocolo_com_P0_literatura()` na reconciliação com o relatório WP0.
  Não afetava nenhum resultado (só o texto de uma exceção), mas corrigido
  para não confundir quem ler o erro no futuro. 11/11 testes passando
  depois da correção.
