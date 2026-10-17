# Prompt para o Composer: WP1.4, varredura completa em `cases/wp1.4/`

## 1. O caso

Tese de doutorado sobre picos de PIO após injeção intravítrea. O WP1.4 do plano de tese pede uma varredura paramétrica por hipercubo latino (LHS, 200–500 simulações FEA) e um emulador (processo gaussiano ou chaos polinomial) com erro de validação cruzada < 5%.

Parâmetros pedidos pelo plano:

| Parâmetro | Faixa |
|---|---|
| Comprimento axial | 20–30 mm |
| Espessura escleral equatorial | 0,3–0,8 mm |
| Espessura escleral posterior | 0,6–1,2 mm |
| Parâmetros Ogden (mu1, alpha1) | ±2 DP (usar fator 0,5–1,5 sobre o nominal) |
| Profundidade da câmara anterior (ACD) | 2,0–4,5 mm |
| Estado do cristalino | fácico / pseudofácico / afácico |
| Vitrectomia | sim / não |

Material nominal provisório (Friedenwald, WP1.2): Ogden N=1, mu1 = 2,2708 MPa, alpha1 = 1,0562, D1 = 0,2247. O plano diz que o WP1.4 pode ser depurado com material provisório. O emulador final com material calibrado vem no WP2.

## 2. O que já existe

**Seu piloto (`cases/wp1.4/`)**: 14 biometrias × 2 materiais (Ogden e Yeoh), casca esférica de espessura uniforme, só R e t variando. Serviu para validar o pipeline e o escalonamento R⁴/t.

**Varredura do Claude (`cases/claude-wp1.4-sweep/`, NÃO editar nada ali)**: 300 amostras LHS, casca esférica, Ogden. Resultado: 300/300 convergiram, emulador GP com erro CV de 0,38% (V_max) e 0,26% (K_eff).

**Problema encontrado**: apesar de a tabela de amostras ter 8 parâmetros, o runner só usa 4 (R = AL/2, t equatorial, mu1, alpha1). Regressão em log nos 300 resultados:

V_max ∝ R^4,07 · t^-1,06 · mu1^-1,04, com alpha1 praticamente sem efeito (coeficiente −0,01).

t posterior, ACD, estado do cristalino e vitrectomia **não têm nenhum efeito** no resultado, porque o gerador de malha esférico não os representa. Logo, esse emulador é um emulador esférico de ~3 variáveis efetivas, e não satisfaz o plano.

Com material nominal, a varredura do Claude reproduz o seu piloto dentro de ~3% nas 14 biometrias (sem erro em nenhum dos dois pipelines).

## 3. O que pedir ao Composer

Rodar a varredura completa na **sua pasta `cases/wp1.4/`**, em subpasta nova `cases/wp1.4/sweep_full/` (scripts, amostras, `output_sweep/`, `output_emulator/`), sem tocar em `claude-*`.

1. **Usar as mesmas amostras** do Claude para permitir comparação caso a caso: copiar (somente leitura na origem) `cases/claude-wp1.4-sweep/scripts/sweep_samples.csv` (300 linhas, seed 42) para `sweep_full/`.
2. **Geometria com espessura variável** (mínimo): esfera com t = t_equatorial no equador e t = t_posterior no polo posterior, transição suave (cosseno) na colatitude. Elipsoide prolato é opcional, para depois.
3. **Cada parâmetro precisa ter efeito físico real, vindo da malha ou da física do modelo**, nunca de multiplicador. Se um parâmetro (ACD, cristalino, vitrectomia) ainda não puder ser representado fisicamente com dados de fonte citável, ele **fica de fora do emulador e do relatório como "não modelado"**. O runner deve avisar claramente quando uma coluna da tabela de amostras não é usada. Documentar cada hipótese de modelagem, com a fonte, em `sweep_full/MODELING_NOTES.md`.
4. **Teste de sensibilidade antes da varredura**: variar cada parâmetro isoladamente a partir do nominal (um parâmetro por vez, extremos da faixa) e mostrar que todos mudam V_max. Parâmetro sem efeito = bug a corrigir, não resultado.
5. **Rodar as 300 simulações** (P0 = 16,9 → 50 mmHg, 16 passos, NLGEOM, como no piloto) com `--resume` e salvamento incremental.
6. **Treinar o emulador GP** (Matérn 5/2, entradas padronizadas, categóricas em one-hot) para V_max e K_eff. Critério: erro relativo médio de CV < 5%. Ampliar os bounds do kernel para eliminar os ConvergenceWarning.
7. **Relatório `sweep_full/RESULTS.md`** com: sensibilidades por parâmetro, faixas de V_max e K_eff, erro de CV, e comparação com o Claude (mesma amostra, mesmo material) com tabela caso a caso.

## 4. Critérios de aceitação

- Todos os 8 parâmetros têm efeito mensurável em V_max (ou estão documentados como não modelados, com justificativa).
- 300/300 casos convergidos (casos que falharem: listar e reexecutar).
- Emulador com erro de CV < 5% para V_max e K_eff.
- Comparação com o Claude mostrada; diferenças atribuídas à geometria/modelagem nova.

## 5. Notas

- Sem pré-tensionamento (MULF) nesta rodada, como no piloto. Pode ser acrescentado depois.
- Não editar arquivos existentes fora de `cases/wp1.4/sweep_full/`.
- Não é possível rodar CalculiX fora do Docker. Comandos no padrão do repositório:

```bash
docker compose run --rm fsi bash -lc \
  'cd /simulation/wp1.4/sweep_full/scripts && python3 run_sweep.py --resume'

docker compose run --rm fsi bash -lc \
  'pip install scikit-learn --break-system-packages && \
   cd /simulation/wp1.4/sweep_full/scripts && python3 train_emulator.py'
```
