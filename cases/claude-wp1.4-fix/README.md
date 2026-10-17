# WP1.4 — correção (sem números inventados)

Corrige os defeitos listados em `cases/claude-wp1.4/claude-REVISAO-WP1.4.md`.
Não altera nada em `cases/wp1.4/sweep_full/` — reaproveita por importação o que
está correto lá (`write_deck_vt.py`) e o pipeline do WP1.2 (`ccx_utils`,
`extract_pv_curve`).

## O que mudou

| # | Defeito no pipeline original | Correção aqui |
|---|---|---|
| 1 | `vit_dv_scale = 1.085` sem fonte, contradizendo a H4 corrigida do plano | removido; vitrectomia sem via mecânica, vai para $R_{ref}$ no WP0 |
| 2 | `dr_acd = −0,11·(ACD−3,25)` sem fonte | removido; $R = AL/2$ |
| 3 | `LENS_DR_MM = {0, −0,22, +0,35}` sem fonte | removido |
| 4 | pickle gravava 6 nomes de coluna para modelo de 10 colunas | `input_cols` descreve exatamente a matriz; domínio de treino gravado |
| 5 | critério <5% avaliado na média (máx. real 5,96%) | critério no **máximo**; média, p95 e máximo reportados |
| 6 | `n_bands` amarrado a `ne` (confunde malha com espessura) | `n_bands` é argumento próprio |
| 7 | curvas P–V descartadas ao salvar | persistidas; + ΔIOP a 50 µL (grandeza da H1) |
| 8 | sem independência de malha na caixa de projeto | `run_mesh_independence_fixed.py`, estudos A e B separados |
| 9 | `cv=5` sem shuffle (dependia da ordem do CSV) | `KFold(shuffle=True, random_state=42)` |

Mantido do Composer porque está correto: $t(\theta)$ com transição cosseno em
faixas, $P_0 = 16{,}9$ mmHg, teto de 50 mmHg, `S8R`, $D_1$ amarrado a $\mu_1$,
ausência de MULF (justificada pelo WP1.3: efeito <1% no Ogden).

Usa o **mesmo** `sweep_samples.csv` do `sweep_full`, para a comparação ser direta.

## Como rodar

```bash
# 1. Varredura corrigida (300 casos; use --resume se interromper)
docker compose run --rm fsi bash -lc \
  'pip install numpy --break-system-packages && \
   cd /simulation/claude-wp1.4-fix/scripts && python3 run_sweep_fixed.py --resume'

# 2. Emulador
docker compose run --rm fsi bash -lc \
  'pip install numpy scikit-learn --break-system-packages && \
   cd /simulation/claude-wp1.4-fix/scripts && python3 train_emulator_fixed.py'

# 3. Independência de malha (estudos A e B)
docker compose run --rm fsi bash -lc \
  'pip install numpy --break-system-packages && \
   cd /simulation/claude-wp1.4-fix/scripts && python3 run_mesh_independence_fixed.py'
```

Para rodar em pedaços (o passo 1 leva algumas horas):

```bash
docker compose run --rm fsi bash -lc \
  'pip install numpy --break-system-packages && \
   cd /simulation/claude-wp1.4-fix/scripts && \
   python3 run_sweep_fixed.py --start 0 --end 100 --resume'
```

## Saídas

- `output_sweep_fixed/sweep_results_fixed.json` — 300 casos com curva P–V completa,
  `K_basal_first`, `K_basal_fit3`, `dIOP_at_50uL_mmHg`
- `output_emulator_fixed/emulator_*.pkl` + `emulator_report_fixed.json`
- `output_mesh_independence/mesh_independence.json`

## O que verificar depois de rodar

1. **Vitrectomia e cristalino devem sumir como efeito.** Com os fatores removidos,
   casos que diferem só nesses inputs têm geometria e material idênticos.
2. **Expoentes da lei de potência.** Regredir $\log K$ contra $\log R$, $\log t$,
   $\log\mu_1$ deve continuar dando ≈ $-4$, $+1$, $+1$ (antes da correção:
   $-4{,}030$, $+1{,}087$, $+1{,}055$). Se mudar muito, a correção quebrou algo.
3. **ΔIOP a 50 µL** agora existe por caso — é a grandeza da H1 ("o olho de 22 mm
   dispara 2–3× o de 26 mm para o mesmo volume injetado"). Testar H1 diretamente
   com isso, em vez de inferir de $V_{max}$.
4. **Critério do emulador no máximo**, não na média.
5. **Casos fora da faixa de validação clínica** (pico de 30–36 mmHg, Knecht 2009
   via plano) ficam marcados no relatório — reportar as métricas nos dois conjuntos.

---

## Correção da espessura por faixa (03/10)

**Defeito encontrado pelo estudo de malha.** O octante com `ne=8` tem apenas 8 anéis
de elementos. Pedir 16 faixas de espessura (o padrão que a varredura de 300 casos usou)
não cria faixas novas — faz o anel *k* receber o índice de faixa `2k+1`, cuja espessura
é avaliada em `u = (2k+1,5)/16` em vez do centro correto do anel, `u = (2k+1)/16`. Ou
seja, **toda a distribuição de espessura ficou deslocada em 1/8 da largura de um anel**.

Medido no estudo anterior (canto AL=20, t fino), em K:

| n_bands pedido | efetivo | amostragem | K |
|---:|---:|---|---:|
| 8 | 8 | centro correto do anel | 0,47959 |
| **16** | 8 | deslocada (**usado na varredura**) | **0,49188** |
| 32 | 8 | deslocada (metade) | 0,48563 |

**Correção em `gen_mesh_bands.py`:**

1. **Uma faixa por anel** (`n_bands=None`, agora o padrão) — elimina o
   desalinhamento, que era a causa principal.
2. **Espessura = média de t(θ) ponderada pela área do anel**,
   $\bar t = \int t(\theta)\sin\theta\,d\theta / \int \sin\theta\,d\theta$,
   com o span de θ lido das coordenadas da malha. O peso $\sin\theta$ é o elemento de
   área da esfera. Escolhi média por área porque o problema é dominado por membrana
   (a varredura confirma expoente $+1{,}08$ em t), então preservar a média de t por área
   preserva a rigidez de membrana do anel. Média em $t^3$ seria o certo se fosse flexão.
3. `thickness_mode="point"` preserva o comportamento antigo, só para o estudo comparativo.

Com uma faixa por anel, os dois modos ficam a ~0,3% um do outro — confirmando que o
desalinhamento era o problema e a média por área é o acabamento.

**Consequência:** a varredura de 300 casos foi rodada com a amostragem deslocada.
Re-rodar deve mudar K em ~1–3%. O `run_mesh_independence_v2.py` mede exatamente isso.
