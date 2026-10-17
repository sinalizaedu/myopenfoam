# WP4.1 — Cadeia IOP(t) → OPP(t) → métrica de isquemia (implementação)

Este diretório (`cases/claude-wp4/`) contém a implementação do item 4.1 do
WP4, na versão revisada descrita em `claude-wp4-proposta-teorica.md`.

## O que já existia (não duplicado)

`cases/wp0/goldmann_iop_solver.py` já implementa:
- `Protocol`, `simulate()`: gera IOP(t) real do pipeline da tese.
- `perfusion_metrics()`: MOPP(t), dose isquêmica `I_mmHg_min`, T_>30/40/50, MOPP mínima.
- `ischemic_dose_curve()`: 𝓘 como função de OPP_crit (não como número fixo).

Este módulo **não reimplementa nada disso** — importa e reusa.

## O que este módulo adiciona

`claude_opp_perfusion.py`:

1. **`opp_diastolica(IOP, PAD_oftalmica)`** — a segunda definição padrão de
   pressão de perfusão ocular, OPP_diast = PAD_oftálmica − IOP, que o WP0
   ainda não tinha (só MOPP estava implementada).

2. **`opp_crit_efetivo(OPP_crit_ref, phi_vasc)`** — fator de reserva
   vascular paciente-específico, motivado por Damasceno et al. (2022):
   66,6% dos casos de CRAO transitória pós-IVI (18/4069 injeções) tinham
   obstrução carotídea ≥70%. `phi_vasc ≥ 1`; `phi_vasc = 1` é o paciente
   sem comorbidade vascular conhecida.

   **Isto é um parâmetro de sensibilidade/estratificação, não um valor
   calibrado.** Não há, até onde a revisão de literatura desta sessão
   verificou, uma curva phi_vasc(grau de estenose) publicada — é uma
   hipótese de modelagem para separar pacientes de risco, a testar contra
   dado clínico no WP6 (calibração bayesiana).

3. **`cadeia_completa()`** — wrapper que chama `perfusion_metrics()` do
   WP0 com o OPP_crit já ajustado por phi_vasc, e acrescenta OPP_diast(t)
   ao resultado.

4. **`sensibilidade_fator_braquial()`** — varre o fator 2/3 de MOPP na
   faixa 0,5–0,8 exigida pelo plano de tese (nunca reportar como valor
   fixo).

## Testes

`test_claude_opp_perfusion.py` — 8 testes, incluindo um teste de
**reconciliação**: com `phi_vasc=1.0`, a cadeia revisada precisa
reproduzir exatamente os números que `perfusion_metrics()` do WP0 já
produz (garante que a extensão não introduziu nenhuma divergência
silenciosa na fórmula original).

Rodar:
```bash
cd cases/claude-wp4
../wp0/.venv/bin/python -m pytest -v test_claude_opp_perfusion.py
```

Rodar a demonstração:
```bash
cd cases/claude-wp4
../wp0/.venv/bin/python claude_opp_perfusion.py
```

## Pendente para 4.2 (próxima etapa)

- Este item **não** calcula a dose isquêmica acumulada 𝓘_cum (WP4.5) nem
  faz a análise de sensibilidade global (WP4.6) — ambos ficam para depois
  que 4.1 estiver validado.
- `PAD_oftalmica_mmHg` está, por padrão, aproximado pela PAD braquial
  (`proto.DBP_mmHg`) quando não há medida direta — mesma lógica de
  aproximação já usada para o fator 2/3 de MOPP. Declarar isso na tese.
