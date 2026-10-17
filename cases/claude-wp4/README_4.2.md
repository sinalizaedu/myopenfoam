# WP4.2 — Dose isquêmica por evento único (𝓘)

## O que já existia (não duplicado)

`cases/wp0/goldmann_iop_solver.py` já calcula 𝓘 via MOPP dentro de
`perfusion_metrics()`, e `ischemic_dose_curve()` varre OPP_crit. Este
módulo generaliza, sem duplicar.

## O que este módulo adiciona (`claude_dose_isquemica.py`)

1. `dose_isquemica(t, OPP_t, OPP_crit)` — genérica: aceita MOPP(t) OU
   OPP_diast(t), não amarrada a MOPP como o WP0.
2. `dose_isquemica_da_cadeia()` — calcula 𝓘 para as duas definições a
   partir do dict do 4.1, e confere contra `I_mmHg_min` que o WP0 já
   produz (checagem de consistência).
3. `curva_sensibilidade_opp_crit()` — 𝓘(OPP_crit), generaliza
   `ischemic_dose_curve()` para qualquer série de OPP.
4. `validacao_fechada_H6()` — compara 𝓘 numérico (via MOPP, saída real do
   solver) contra a fórmula fechada de H6 (Seção 1/4.3 do plano de
   tese). **Bateu em <0,5% de erro** — ver achado abaixo.

## ACHADO IMPORTANTE — inconsistência nos parâmetros default do WP0

Ao tentar validar 𝓘 contra a fórmula fechada de H6, a primeira tentativa
divergiu **60–100%**. Investigando: **o `Protocol()` padrão do WP0 não
satisfaz o próprio equilíbrio de Goldmann no `P0_mmHg` declarado.**

Com os valores default —
`Q_prod=3,0 µL/min`, `C_out=0,28 µL/min/mmHg`, `Pev=10 mmHg`,
`frac_uveoscleral=0,20` — o balanço de vazões no basal é:

```
Q_prod (3,0) ≠ Q_TM(P0=15) + Q_uv = 0,28×(15−10) + 0,20×3,0 = 1,4 + 0,6 = 2,0
```

Sobra **+1,0 µL/min** não contabilizado. Isso não é cosmético: rodando o
solver **sem nenhuma injeção**, por 100 min, o IOP diverge de 15 mmHg
para **~18,57 mmHg** — com a MESMA constante de tempo (~18 min) da
própria dinâmica pós-injeção que o WP4 está tentando medir. Ou seja,
**qualquer simulação de 30–40 min com os parâmetros default já carrega
um viés de deriva basal da mesma ordem de grandeza do fenômeno em
estudo.**

Verificado por simulação direta:

```python
proto = Protocol(V_inj_uL=0.0, t_end_min=100.0)  # sem injeção nenhuma
# IOP(t=0)=15.0, IOP(t=40)=18.17, IOP(t=100)=18.56 mmHg
```

**Isso não foi corrigido em `goldmann_iop_solver.py`** (restrição do
projeto: não editar arquivos existentes).

### Reconciliação com o relatório WP0 em LaTeX

A Bruna apontou que o relatório WP0 (LaTeX, seção "Produção trabecular e
uveoescleral") já resolve exatamente isso — e resolve melhor do que a
primeira correção feita aqui. O relatório **não** fixa P0 e recalcula
Q_prod (o que eu tinha feito de saída, sem base própria); ele mantém os
QUATRO parâmetros de vazão ancorados na literatura (Goel et al. 2010
para humano) e **deriva** P0 do equilíbrio:

```
P0 = Pev + Q_prod×(1−frac_uveoscleral)/C_out
   = 10 + 2,4×0,8/0,28 = 16,86 mmHg  ≈ 16,9 mmHg (relatório)
```

Com `Q_prod=2,4 µL/min` (Goel et al. 2010: 2,4±0,6), não os `3,0` do
`Protocol()` default. Para coelho anestesiado, o mesmo cálculo dá
`P0=26,7 mmHg` (Q_prod=3,06, C_out=0,26, Pev=15,5, frac=0,05 — Kiel et
al. 2011/2015, Fourman & Garner 1989), também batendo com o relatório.

**Isto é estritamente melhor que a correção original desta sessão**:
em vez de inventar um `Q_prod=1,75` sem nenhuma citação só para forçar
P0=15, agora os quatro parâmetros de vazão do `Protocol` têm cada um sua
própria fonte na literatura, e P0 é uma CONSEQUÊNCIA deles, não um valor
arbitrário imposto por fora. Implementado como
`derivar_P0_equilibrio()` + `protocolo_com_P0_literatura(especie=...)`
(substitui a função `protocolo_goldmann_consistente()` de uma versão
anterior deste módulo).

Com esse `Protocol` (humano, P0=16,86), a validação fechada contra H6
bateu em **0,17 %** de erro (OPP_crit=38 mmHg, janela não-trivial:
dose numérica e fechada ambas ≈60,7 mmHg·min, não um 0-contra-0 vazio).

### Recomendação

**O `Protocol()` padrão em `goldmann_iop_solver.py` não bate com os
valores de literatura já usados no próprio relatório WP0**: usa
`Q_prod=3,0` (relatório cita Goel et al. 2010: 2,4) e `P0=15,0`
(relatório deriva 16,9). Recomendo reconciliar o `Protocol()` oficial
com os valores do relatório — decisão de quem mantém esse arquivo
(você/Composer), não deste módulo.

Enquanto isso não for corrigido, **todo resultado do WP0 e do WP4 que
usa `Protocol()` sem modificação carrega esse viés** — inclusive os
números que reportei nas etapas anteriores desta sessão (item 4.1). Não
invalida a lógica das fórmulas (MOPP, T_>X, 𝓘 continuam corretas
matematicamente), mas os **valores absolutos** de MOPP mínima e 𝓘
relatados até aqui, com o `Protocol()` default e janelas de 30–40 min,
estão inflados por essa deriva. Recomendo revalidar os números-chave do
capítulo com `protocolo_com_P0_literatura()` (ou o equivalente já
corrigido em `goldmann_iop_solver.py`) antes de reportar qualquer valor
absoluto na tese.

## Testes

`test_claude_dose_isquemica.py` — 11 testes, incluindo:
- reconciliação com o `I_mmHg_min` do WP0 (deve ser idêntico)
- `derivar_P0_equilibrio()` reproduz exatamente os P0=16,9 (humano) e
  P0=26,7 (coelho anestesiado) do relatório WP0 em LaTeX
- validação fechada contra H6 (erro 0,17%, numa janela não-trivial de
  OPP_crit)
- detecção do próprio achado acima (teste que confirma a deriva basal
  existe nos parâmetros default, e que `protocolo_com_P0_literatura()`
  a remove)
- rejeição correta (ValueError, não NaN) quando a validação fechada é
  usada fora do seu domínio de validade (K não-constante, paracentese
  ligada, ou limiar já abaixo do basal)

Rodar:
```bash
cd cases/claude-wp4
../wp0/.venv/bin/python -m pytest -v test_claude_dose_isquemica.py
```
