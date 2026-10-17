# Prompt para o Composer: WP1.5, modelo anatômico 3D em `cases/claude-wp1.5-anat/`

## 1. O caso

Tese de doutorado sobre picos de IOP após injeção intravítrea (IVI). O WP1.5 do plano de tese pede um **modelo FEA 3D anatômico** que responda a três perguntas que a casca esférica (WP1.4) não consegue:

1. **Colapso da câmara anterior durante paracentese** (alimenta WP5) — córnea + íris + cristalino, irredutivelmente 3D.
2. **Deformação da lâmina cribrosa / cabeça do nervo óptico** durante o pico de IOP — mecanismo mecânico de risco ao nervo óptico.
3. **Tensão local no sítio de injeção** — risco de vazamento/refluxo pelo trajeto da agulha, conecta com R_ref.

O plano permite construir e testar a malha e o pipeline com **material provisório** (Ogden do WP1.2) antes do WP2.

## 2. O que já existe no repositório

### 2a. Geometria anatômica (Lamminsalo / Missel — COELHO)

**`brunaStuff/gen_lamminsalo_2d.py`** e **`brunaStuff/gen_lamminsalo_g2.py`**: gerador de malha anatômica G2 (90° calotte = um quarto de revolução com simetria), baseado em Missel 2012 / Lamminsalo et al. 2018 (Pharm Res, Tables SI–SII do ESM).

Tecidos presentes na malha:
- **Esclera** (band_sclera): parede externa, elipsoide R1=9.00 mm, R2=7.53 mm
- **Coroide** (band_choroid): camada vascular entre esclera e retina
- **Retina** (band_retina): camada interna
- **Córnea** (band_cornea): cúpula anterior, R=8.29 mm (ext), R=8.01 mm (int)
- **Corpo ciliar** (band_ciliary): produção de aquoso
- **Íris** (iris): diafragma entre CA e câmara posterior
- **Cristalino** (lens): R posterior=4.79 mm, R anterior=5.76 mm
- **Câmara anterior** (ac): domínio fluido entre córnea e íris/cristalino
- **Vítreo** (vitreous): domínio fluido posterior
- **Malha trabecular** (TM): via de drenagem

Malhas já geradas em `cases/doc-g3-sim1/geometry/`:
- `eye_g2_solid_lamminsalo_M1.msh` (465 KB) — nível M1 (mais grosso)
- `eye_g2_solid_lamminsalo_M2.msh` (8.1 MB) — nível M2
- `eye_g2_solid_lamminsalo_M3.msh` (13.3 MB) — nível M3

**IMPORTANTE: esta geometria é de OLHO DE COELHO** (Missel 2012). Para a versão final da tese precisamos de geometria humana. O pipeline pode ser construído e testado com esta geometria.

### 2b. Estrutura detalhada da malha `eye_g2_solid_lamminsalo_M1.msh`

Formato Gmsh 2.2. **Coat only** — contém apenas a parede externa do olho (sem íris, corpo ciliar, cristalino ou TM como volumes sólidos).

| Dado | Valor |
|---|---|
| Nós | 3 780 |
| Elementos de volume (hex8 → **C3D8** no CalculiX) | 2 406 |
| Elementos de superfície (quad4 → faces para BCs) | 1 884 |
| Coordenadas | metros (ordem 0,007–0,009 m) |

**Zonas de volume (Physical Groups 3D):**
| Physical Group ID | Nome | Nº hex8 |
|---|---|---|
| 1 | cornea | 306 |
| 2 | sclera | 840 |
| 3 | choroid | 630 |
| 4 | retina | 630 |

**Patches de superfície (Physical Groups 2D):**
| Physical Group ID | Nome | Nº quad4 | Uso |
|---|---|---|---|
| 5 | fsi_active | 312 | superfície interna (vítreo) — **aplicar pressão** |
| 6 | fsi_iris | 90 | fronteira com íris — **aplicar pressão** |
| 7 | fsi_lens | 94 | fronteira com cristalino — **aplicar pressão** |
| 8 | outer | 444 | superfície externa — livre |
| 9 | symmetry_0 | 511 | plano de simetria θ=0° — **BC de simetria** |
| 10 | symmetry_90 | 433 | plano de simetria θ=90° — **BC de simetria** |

**Notas sobre a malha:**
- A malha é **coat only**: esclera+coroide+retina+córnea. Íris, corpo ciliar e cristalino NÃO são volumes sólidos — aparecem apenas como fronteiras (fsi_iris, fsi_lens).
- Para as três perguntas do WP1.5 (Fase 2), será necessário incluir esses tecidos como sólidos. Mas para a **Fase 1 (teste de pipeline)**, a coat-only é suficiente.
- Os elementos são **hexaedros lineares de 8 nós** → tipo **C3D8** no CalculiX (NÃO C3D10 nem C3D4).

### 2c. Pipeline FEA existente (casca esférica)

Os pilotos em `cases/wp1.4/` e `cases/wp1.5/` usam casca esférica (elementos S8R) gerada por `brunaStuff/gen_fea_simplf_sphere.py`. O runner (`forward_run_v2.py`) escreve .inp do CalculiX e executa `ccx`.

Material provisório (Friedenwald, WP1.2):
- **Ogden N=1**: mu1 = 2,2708 MPa, alpha1 = 1,0562, D1 = 0,2247
- **Yeoh**: C10 = 1,0198 MPa, C20 = 4,9905 MPa

### 2d. O que NÃO existe (precisa ser criado)

1. Conversor de malha Gmsh (.msh) → CalculiX (.inp) para malha sólida 3D
2. Atribuição de materiais por região (cellZone → ELSET no CalculiX)
3. Runner 3D anatômico com carregamento de pressão interna
4. Pós-processamento específico para as três perguntas (ACD, lâmina cribrosa, sítio de injeção)
5. Geometria humana (para depois — rodar primeiro com coelho)

## 2e. Regra de ouro: nenhum número inventado

Todo número que entra no cálculo precisa ter uma destas origens: (a) o plano de tese, (b) uma referência publicada, citada no código ou em `MODELING_NOTES.md`, ou (c) um resultado do próprio projeto (WP1.2, WP1.3). **Proibido**: pesos de mistura, multiplicadores "fenomenológicos", faixas arredondadas "de bom senso", correções pós-FE. Se não houver fonte, o parâmetro não entra. Perguntar à usuária em vez de preencher.

### Números já disponíveis com fonte

| Número | Fonte | Status |
|---|---|---|
| mu1 = 2,2708 MPa, alpha1 = 1,0562, D1 = 0,2247 | ajuste Friedenwald WP1.2 (Ogden) | ✓ ok |
| C10 = 1,0198 MPa, C20 = 4,9905 MPa | ajuste Friedenwald WP1.2 (Yeoh) | ✓ ok |
| P0 = 15 mmHg (IOP basal fisiológica) | plano de tese: "Equilibrar a 15 mmHg" (Ensaio A, WP2) | ✓ ok |
| P_final = 50 mmHg | plano de tese: "injetar 50 µL em 6 s" (Ensaio B, WP2) — é o pico atingido, não prescrito | ⚠ verificar se o plano fixa 50 ou se é resultado |
| Geometria coelho (SURFACES, PTS) | Lamminsalo et al. 2018, Pharm Res, ESM Tables SI–SII, de Missel 2012 | ✓ ok |
| MULF β=0,7 | Gee, Förster & Wall 2010 | ✓ ok (WP1.3, não usado nesta etapa) |

### Números que PRECISAM de referência (buscar antes de usar)

| Número | O que é | Onde buscar |
|---|---|---|
| Propriedades da córnea | E ou parâmetros hiperelásticos | Woo et al. 1972; Elsheikh et al. 2007; Kling & Marcos 2013 |
| Propriedades da íris | E ≈ 4 kPa (plano de tese, linha 592) | Plano cita E = 4 kPa → buscar fonte primária |
| Propriedades do cristalino | E ou hiperelástico | Fisher 1971; Weeber & van der Heijde 2007 |
| Propriedades da lâmina cribrosa | E ou hiperelástico | Sigal et al. 2004, 2005; Eilaghi et al. 2010 |
| Espessura da lâmina cribrosa | ~0,2–0,5 mm | Sigal et al. 2004; Jonas et al. 2004 |
| Geometria humana (se for trocar) | SURFACES e PTS para olho humano | Atchison 2006; Riordan-Eva & Augsburger (Vaughan & Asbury) |

## 3. O que fazer

Trabalhar em **`cases/claude-wp1.5-anat/`** (criar a pasta), com subpastas `scripts/`, `output_test/`. Não tocar em nada fora desta pasta exceto leitura.

### Fase 1 — Pipeline de validação (esta rodada)

**Objetivo:** rodar a malha Lamminsalo M1 (coelho) no CalculiX com material de esclera provisório (Ogden) e pressão interna, confirmando que o pipeline 3D funciona.

1. **Conversor de malha Gmsh → CalculiX .inp**
   - Ler `cases/doc-g3-sim1/geometry/eye_g2_solid_lamminsalo_M1.msh` (formato **Gmsh 2.2**)
   - Physical Groups já definidos (ver Seção 2b): 4 zonas de volume (cornea, sclera, choroid, retina) e 6 patches de superfície
   - Exportar como .inp com:
     - `*NODE` (3 780 nós, coordenadas em metros)
     - `*ELEMENT, TYPE=C3D8` (hexaedros de 8 nós, 2 406 elementos)
     - `*ELSET` por zona de volume: CORNEA, SCLERA, CHOROID, RETINA
     - `*NSET` por patch de superfície: FSI_ACTIVE, FSI_IRIS, FSI_LENS, OUTER, SYMMETRY_0, SYMMETRY_90
     - `*SURFACE` para pressão interna: combinar FSI_ACTIVE + FSI_IRIS + FSI_LENS
     - `*SURFACE` para simetria: SYMMETRY_0 e SYMMETRY_90 separados
   - Script: `scripts/convert_gmsh_to_ccx.py`
   - **Usar meshio** (`pip install meshio --break-system-packages`) ou parser nativo de .msh 2.2
   - **ATENÇÃO**: no formato Gmsh 2.2 as faces (quad4) estão no bloco `$Elements` com type=3, e os volumes (hex8) com type=5. O tag numérico é o Physical Group ID (ver tabela na Seção 2b).

2. **Material único (esclera) para todas as regiões — teste de pipeline**
   - Ogden N=1: mu1 = 2,2708 MPa, alpha1 = 1,0562, D1 = 0,2247
   - Nesta fase, todas as regiões recebem o mesmo material. A diferenciação vem na Fase 2.
   - Documentar isto explicitamente em MODELING_NOTES.md como simplificação provisória.

3. **Condições de contorno**
   - **Simetria:** nós do NSET SYMMETRY_0 (plano θ=0°) e SYMMETRY_90 (plano θ=90°). Determinar quais DOFs restringir pela orientação dos planos na malha (verificar as coordenadas dos nós para identificar o plano normal).
   - **Pressão interna:** na SURFACE combinada de FSI_ACTIVE + FSI_IRIS + FSI_LENS (toda a face interna da coat).
   - P = 15 mmHg = 1999,83 Pa (basal) → P = 50 mmHg = 6666,1 Pa (pico), em 16 incrementos.
   - `*STEP, NLGEOM` — geometria não-linear obrigatória para hiperelástico.
   - **Nota sobre simetria:** a calotte cobre 90° de revolução (um quarto do olho). As faces de simetria são perpendiculares entre si. Verificar se a malha está no plano XY (θ=0°) e XZ (θ=90°), ou outra orientação, antes de definir os DOFs.

4. **Runner `scripts/run_anatomical_test.py`**
   - Gerar o .inp completo: malha + material + BCs + step de pressão
   - Chamar `ccx` e capturar o log
   - Pós-processar o .frd: extrair deslocamentos, tensões, volume da cavidade
   - Salvar resultados em `output_test/test_results.json`

5. **Verificação**
   - A malha converge? (ccx não aborta)
   - O deslocamento é fisicamente razoável? (µm a centenas de µm, não km)
   - O volume injetado corresponde aproximadamente à integral de deslocamento na superfície?

### Fase 2 — Multi-material e três perguntas (rodada seguinte)

**NÃO implementar agora. Apenas documentar o plano em MODELING_NOTES.md.**

Quando as propriedades de cada tecido estiverem referenciadas:
- Atribuir material diferente por ELSET (córnea, esclera, lâmina cribrosa, etc.)
- **Pergunta 1 (colapso CA):** retirar volume progressivamente da CA, monitorar ACD. Saída: curva ACD(ΔV).
- **Pergunta 2 (lâmina cribrosa):** com pressão no pico, extrair tensão e deformação na LC. Saída: campo de deformação na LC.
- **Pergunta 3 (sítio de injeção):** com pressão no pico, extrair tensão na região da pars plana (3,5 mm posterior ao limbo). Saída: tensão local máxima.

Para a Pergunta 2, a malha Lamminsalo **não tem lâmina cribrosa explícita** — o polo posterior é esclera contínua. Opções:
- (a) Criar uma região de LC no polo posterior com espessura e propriedades diferentes (Sigal et al. 2004)
- (b) Usar mesh refinement local no polo posterior e material diferenciado

**Documentar** cada decisão e referência em `MODELING_NOTES.md`.

## 4. Estrutura de arquivos esperada

```
cases/claude-wp1.5-anat/
├── scripts/
│   ├── convert_gmsh_to_ccx.py      # Gmsh .msh → CalculiX .inp
│   ├── run_anatomical_test.py       # runner principal
│   └── postprocess_frd.py           # pós-processamento do .frd
├── output_test/
│   └── test_results.json            # resultados do teste de pipeline
├── MODELING_NOTES.md                # hipóteses, fontes, decisões
└── README.md                        # instruções de uso
```

## 5. Critérios de aceitação (Fase 1)

- [ ] Malha Lamminsalo M1 convertida para .inp com ELSETs por região
- [ ] CalculiX roda sem abortar (convergência em todos os passos)
- [ ] Deslocamentos fisicamente razoáveis (verificação de ordem de grandeza)
- [ ] MODELING_NOTES.md documenta todas as hipóteses com fontes
- [ ] Plano da Fase 2 documentado (sem implementação)

## 6. Notas

- **Não editar arquivos fora de `cases/claude-wp1.5-anat/`.** Leitura é permitida em qualquer lugar.
- A geometria é de coelho (Lamminsalo). A troca para geometria humana é tarefa futura.
- Sem pré-tensionamento (MULF) nesta rodada. Pode ser acrescentado na Fase 2.
- A malha sólida usa elementos volumétricos (tetraedros ou hexaedros), **não elementos de casca** como no WP1.4.
- Coordenadas na malha Gmsh estão em **metros** (valores da ordem de 0,007–0,009).
- As unidades do CalculiX são consistentes: se a malha está em metros, pressão em Pa (1 mmHg = 133,322 Pa), material em Pa.
- Não é possível rodar CalculiX fora do Docker. Comando:

```bash
docker compose run --rm fsi bash -lc \
  'pip install meshio --break-system-packages && \
   cd /simulation/claude-wp1.5-anat/scripts && python3 convert_gmsh_to_ccx.py'

docker compose run --rm fsi bash -lc \
  'cd /simulation/claude-wp1.5-anat/scripts && python3 run_anatomical_test.py'
```

- O caminho da malha Gmsh dentro do Docker é: `/simulation/doc-g3-sim1/geometry/eye_g2_solid_lamminsalo_M1.msh`
- O JSON com metadados da malha coat-only: `/simulation/doc-g3-sim1/geometry/patch_groups_g2_solid.json`
- O JSON com metadados da malha revolvida completa (117K hex, inclui iris/ciliary/tm): `/simulation/doc-g3-sim1/geometry/patch_groups_g2_solid_revolve_M1.json`
- **Para a Fase 1 usar a malha coat-only** (`eye_g2_solid_lamminsalo_M1.msh`). A malha completa com iris/ciliary será para a Fase 2.
