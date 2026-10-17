# WP4.5 — Dose isquêmica acumulada ao longo de um regime terapêutico

## O que este módulo faz (`claude_dose_cumulativa.py`)

Contribuição original (não estava em nenhum item anterior). Implementa

    I_cum(N) = Σ_j I_j · w(Δt_j)

com os DOIS limites de `w(Δt)` exigidos pelo plano — nunca reportar só
um:

- **Acumulação perfeita**: `w=1` sempre → `I_cum = N·I` (K constante).
- **Recuperação parcial**: `w(Δt) = (1−b) + b·e^(−a·Δt)`, inspirado no
  modelo SF do rato (`SF = 1 − b(1 − e^{−at})`), reinterpretado aqui como
  a fração de dano que **persiste** após um intervalo Δt. Para b=1 (uso
  padrão aqui) isso é o decaimento exponencial puro — uma simplificação
  do modelo original do rato (que tem assíntota b<1, dano residual
  permanente); `b<1` já é suportado se a tese precisar dessa
  generalização.

`a` e `b` **não têm calibração direta** na literatura para recuperação
perfusional ocular — são parâmetros de sensibilidade, como φ_vasc (4.1)
e OPP_crit (4.2/4.3).

## Resultado (I por evento = 20 mmHg·min, meia-vida ilustrativa = 4 semanas)

| regime | N (2 anos) | intervalo | I_cum perfeita | I_cum parcial |
|---|---:|---:|---:|---:|
| mensal fixo | 24 | 4 sem | 480,0 | 250,0 |
| treat-and-extend | 12 | 10 sem | 240,0 | 58,9 |
| brolucizumabe | 8 | 12 sem | 160,0 | 37,5 |
| faricimabe | 6 | 16 sem | 120,0 | 26,3 |

Ordem preservada nos dois limites: menos injeções + intervalo maior →
sempre menos acúmulo, no limite perfeito (trivial, é só N) e também no
limite com recuperação parcial (onde o efeito é ainda mais pronunciado,
porque menos injeções TAMBÉM significa mais tempo de recuperação entre
elas).

### Sensibilidade à meia-vida de recuperação (regime mensal, N=24)

| meia-vida | I_cum parcial |
|---:|---:|
| 2 semanas | 135,0 |
| 4 semanas | 250,0 |
| 8 semanas | 345,3 |
| 12 semanas | 385,1 |

Quanto mais lenta a recuperação (meia-vida maior), mais o resultado se
aproxima do limite de acumulação perfeita (480,0) — como esperado.

## Suporte indireto da literatura (citado no plano)

O contraste entre paracentese sem efeito detectável (RCT, evento único)
e paracentese com RNFL preservado (observacional, uso repetido) é a
assinatura esperada de um processo cumulativo: cada evento isolado é
indetectável, mas a soma sem proteção não é. Este módulo formaliza esse
raciocínio qualitativo em um número.

## Testes

`test_claude_dose_cumulativa.py` — 18 testes, incluindo:
- limite de acumulação perfeita = N·I exatamente
- w(0)=1, w(∞)=1−b, monotonicidade em Δt
- Δt→∞ tende a contar só o primeiro evento; Δt→0 tende à acumulação
  perfeita
- consistência entre `regime_terapeutico()` (wrapper) e `dose_cumulativa()`
  (função de baixo nível) montada manualmente
- ordenação dos 4 regimes do plano preservada em AMBOS os limites
- meia-vida ilustrativa reproduz w=0,5 exatamente no próprio período
  (checagem de definição)

Rodar:
```bash
cd cases/claude-wp4
../wp0/.venv/bin/python -m pytest -v test_claude_dose_cumulativa.py
```
