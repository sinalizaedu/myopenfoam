# Prompt para Composer/Cursor — WP1.4 Varredura Paramétrica Completa

## Contexto

O piloto do WP1.4 está feito (14 biometrias × 2 materiais = 28 simulações, em `cases/wp1.4/` e `cases/claude-wp1.4/`). Ele varia apenas R (raio) e t (espessura uniforme) em cascas esféricas, com material fixo (Friedenwald Ogden e Yeoh). Agora é preciso fazer a **varredura completa** conforme o plano de tese.

## O que precisa ser feito

### 1. Geração de amostras LHS (Latin Hypercube Sampling)

Já existe um script pronto em `cases/claude-wp1.4-sweep/scripts/generate_lhs_samples.py`. Ele gera N amostras (padrão 300) no espaço de 8 parâmetros:

| Parâmetro | Faixa | Tipo |
|---|---|---|
| comprimento_axial_mm | 20–30 mm | contínuo |
| t_equatorial_mm | 0.3–0.8 mm | contínuo |
| t_posterior_mm | 0.6–1.2 mm | contínuo |
| mu1_factor | 0.5–1.5 (×nominal) | contínuo |
| alpha1_factor | 0.5–1.5 (×nominal) | contínuo |
| ACD_mm | 2.0–4.5 mm | contínuo |
| lens_status | phakic/pseudophakic/aphakic | categórico |
| vitrectomy | sim/não | categórico |

Os valores nominais de material são os do fit Ogden/Friedenwald do WP1.2:
- mu1 = 2.2708 MPa
- alpha1 = 1.0562

Os fatores multiplicativos (0.5–1.5) representam ±~2 desvios-padrão.

Para rodar:
```bash
cd /simulation/claude-wp1.4-sweep/scripts
python3 generate_lhs_samples.py --n 300 --seed 42 --out sweep_samples.csv
```

### 2. Runner da varredura

O script `run_sweep_claude.py` lê o CSV de amostras e roda cada caso no CalculiX. Na versão atual (casca esférica), ele:
- Mapeia comprimento_axial → R = AL/2
- Usa t_equatorial como espessura uniforme
- Varia mu1 e alpha1 conforme os fatores
- Ignora ACD, lens_status e vitrectomy (a serem implementados)

Para rodar:
```bash
cd /simulation/claude-wp1.4-sweep/scripts
python3 run_sweep_claude.py --samples sweep_samples.csv --resume
```

O `--resume` permite reiniciar de onde parou. O `--start/--end` permite dividir em lotes.

### 3. O que FALTA implementar no runner (para você, Composer)

#### 3a. Geometria não esférica (PRIORIDADE ALTA)

O gerador de malha atual (`wp1.1/scripts/gen_sphere_shell_mesh.py`) só faz esferas com espessura uniforme. Para a varredura completa, é necessário:

**Opção A (mínima, recomendada para começar):**
- Continuar com esfera, mas com **espessura variável**: t_equatorial na região equatorial, t_posterior no polo posterior, com transição suave (interpolação linear ou cosseno) entre elas.
- Isso requer modificar `gen_sphere_shell_mesh.py` (ou criar uma versão nova) para aceitar t como função da latitude (colatitude θ).

**Opção B (mais realista, pode ser feita depois):**
- Substituir a esfera por um **elipsoide prolato** com semi-eixo posterior > semi-eixo equatorial.
- O comprimento_axial_mm define o semi-eixo axial; o raio equatorial é derivado (tipicamente ~11.5 mm para um olho de 24 mm de AL).

#### 3b. Efeito do cristalino e vitrectomia (PRIORIDADE MÉDIA)

Para a simulação simplificada (casca pressurizada), esses fatores afetam:
- **lens_status**: muda o volume interno efetivo. Pseudophakic tem lente artificial (menor volume), aphakic não tem lente (maior volume). Pode ser modelado como ajuste no volume de referência.
- **vitrectomy**: olho vitrectomizado tem gel vítreo substituído por BSS, que é menos viscoso. No modelo quase-estático, o efeito principal é na complacência efetiva. Pode ser modelado como fator de correção em K.

Uma abordagem pragmática: tratar como fatores multiplicativos no volume ou na pressão.

#### 3c. Profundidade da câmara anterior — ACD (PRIORIDADE BAIXA para a varredura)

A ACD afeta o volume interno disponível. No modelo esférico, pode ser incorporada como ajuste no volume efetivo. No modelo anatômico (WP1.5), é uma dimensão geométrica real.

### 4. Treinamento do emulador

O script `train_emulator_claude.py` treina um GP (processo gaussiano) com kernel Matérn 5/2 sobre os resultados da varredura. Requer scikit-learn:

```bash
pip install scikit-learn --break-system-packages
python3 train_emulator_claude.py --results ../output_sweep_claude/sweep_results.json
```

Critério de aceitação do plano: erro de validação cruzada < 5%.

O emulador produz:
- `emulator_V_max_uL.pkl` — prediz V_max dado os parâmetros
- `emulator_K_eff_mmHg_per_uL.pkl` — prediz K_eff
- `emulator_report.json` — métricas de CV

### 5. Resumo das etapas de execução

```bash
# 1. Gerar amostras
docker compose run --rm fsi bash -lc \
  'cd /simulation/claude-wp1.4-sweep/scripts && \
   python3 generate_lhs_samples.py --n 300 --seed 42'

# 2. Rodar varredura (leva horas — dividir em lotes se necessário)
docker compose run --rm fsi bash -lc \
  'cd /simulation/claude-wp1.4-sweep/scripts && \
   python3 run_sweep_claude.py --resume'

# 3. Treinar emulador
docker compose run --rm fsi bash -lc \
  'pip install scikit-learn --break-system-packages && \
   cd /simulation/claude-wp1.4-sweep/scripts && \
   python3 train_emulator_claude.py'
```

### 6. Estrutura de pastas esperada

```
cases/claude-wp1.4-sweep/
├── scripts/
│   ├── generate_lhs_samples.py      ← gera amostras LHS
│   ├── run_sweep_claude.py          ← roda cada caso no CalculiX
│   └── train_emulator_claude.py     ← treina GP
├── sweep_samples.csv                ← amostras geradas (300 linhas)
├── sweep_samples.meta.json          ← metadados do sampling
├── output_sweep_claude/
│   ├── ccx_runs/                    ← arquivos CalculiX de cada caso
│   └── sweep_results.json           ← resultados consolidados
└── output_emulator_claude/
    ├── emulator_V_max_uL.pkl
    ├── emulator_K_eff_mmHg_per_uL.pkl
    └── emulator_report.json
```

### 7. Notas importantes

- **Material provisório:** O plano de tese diz que a varredura pode ser "depurada de ponta a ponta" com material provisório (Friedenwald). O emulador FINAL com material calibrado é gerado durante o WP2 ("Calibração final").
- **Pré-tensionamento:** O piloto foi rodado SEM pré-tensionamento (MULF do WP1.3). A varredura completa deveria idealmente incluir MULF, mas pode ser feita primeiro sem (como no piloto) e depois re-rodada com MULF.
- **Número de amostras:** O plano pede 200–500. Começar com 300 é um bom meio-termo. Se o emulador não passar no critério de 5%, aumentar para 500.
- **scikit-learn:** Não está instalado no container por padrão. Instalar com pip no início do passo 3.
