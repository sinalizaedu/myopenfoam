# WP1.5 — Modelo FEA 3D anatômico do olho

## Contexto

Tese de doutorado sobre picos de IOP após injeção intravítrea (IVI). O WP1.5 constrói um **modelo FEA 3D com geometria anatômica** que responde a três perguntas que a casca esférica (WP1.4) não consegue:

1. **Colapso da câmara anterior durante paracentese** — córnea + íris + cristalino, irredutivelmente 3D.
2. **Deformação da lâmina cribrosa** durante o pico de IOP — mecanismo de risco ao nervo óptico.
3. **Tensão no sítio de injeção** — risco de vazamento na pars plana.

## O que já está pronto

Os três scripts abaixo já estão escritos e testados. Estão na pasta `scripts/`:

### 1. `convert_gmsh_to_ccx.py`
Converte a malha Gmsh `eye_g2_solid_lamminsalo_M1.msh` (formato 2.2, hexaedros de 8 nós) para CalculiX `.inp`.

A malha é **coat-only** (parede do olho sem estruturas internas):
- **3 780 nós**, **2 406 elementos C3D8**
- Zonas de volume: CORNEA (306), SCLERA (840), CHOROID (630), RETINA (630)
- Patches de superfície: FSI_ACTIVE (312), FSI_IRIS (90), FSI_LENS (94), OUTER (444), SYMMETRY_0 (511), SYMMETRY_90 (433)
- Coordenadas em **metros** (valores ~0,007–0,009 m)

O script gera:
- `mesh/eye_anatomical.inp` — nós, elementos, ELSETs, NSETs, SURFACEs
- `mesh/mesh_conversion_summary.json` — resumo da conversão

### 2. `run_anatomical_test.py`
Gera o `.inp` completo e executa `ccx`. Fase 1 = material único para teste de pipeline.

**Material** (Ogden N=1, ajuste Friedenwald WP1.2):
- mu1 = 2,2708 MPa, alpha1 = 1,0562, D1 = 0,2247 1/MPa
- Em unidades SI: mu1 = 2.2708e6 Pa, D1 = 0.2247e-6 1/Pa
- Mesmo material para todas as regiões (simplificação Fase 1)

**Condições de contorno:**
- Simetria: SYMMETRY_0 (plano z=0, DOF 3 = 0), SYMMETRY_90 (plano x=0, DOF 1 = 0)
- Pressão interna na SURFACE SINNER (= FSI_ACTIVE + FSI_IRIS + FSI_LENS)
- Step 1: P = 15 mmHg = 1999,83 Pa (basal, fonte: plano de tese, Ensaio A WP2)
- Step 2: P = 50 mmHg = 6666,1 Pa (pico, fonte: plano de tese, Ensaio B WP2)
- `*STEP, NLGEOM` — geometria não-linear para hiperelástico

### 3. `postprocess_frd.py`
Lê o `.frd` do CalculiX e extrai:
- Deslocamentos por nó e por zona (em µm)
- Tensão de Von Mises (em kPa)
- Verificação de ordem de grandeza (sanity check)
- Resultados em `output_test/test_results.json`

## Como rodar

Todos os comandos usam Docker. Os caminhos dentro do container são `/simulation/<nome-da-pasta>/`:

```bash
# 1. Converter malha
docker compose run --rm fsi bash -lc \
  'pip install numpy --break-system-packages && \
   cd /simulation/<PASTA>/scripts && python3 convert_gmsh_to_ccx.py'

# 2. Rodar CalculiX
docker compose run --rm fsi bash -lc \
  'cd /simulation/<PASTA>/scripts && python3 run_anatomical_test.py'

# 3. Pós-processar
docker compose run --rm fsi bash -lc \
  'pip install numpy --break-system-packages && \
   cd /simulation/<PASTA>/scripts && python3 postprocess_frd.py'
```

Substituir `<PASTA>` pelo nome da pasta que você criou.

## Verificação (critérios de aceitação)

Depois de rodar os três passos:

1. **ccx convergiu?** — `run_anatomical_test.py` imprime o return code. O `.log` tem os detalhes.
2. **Deslocamentos razoáveis?** — Espera-se µm a centenas de µm. Se for km ou zero, há erro.
3. **Tensão razoável?** — Von Mises deve estar na faixa de kPa a MPa.
4. **`.frd` gerado?** — O pós-processamento precisa dele.

## O que NÃO fazer agora (Fase 2, futura)

Documentar no MODELING_NOTES.md, mas **não implementar**:

- Materiais diferenciados por tecido (córnea, íris, cristalino, lâmina cribrosa — precisam de referências)
- Malha com iris/ciliary/TM como volumes sólidos (a coat-only não os tem)
- Pré-tensionamento MULF (Gee, Förster & Wall 2010, β=0,7)
- As três perguntas do WP1.5 (CA collapse, lâmina cribrosa, sítio de injeção)

## Regra de ouro: nenhum número inventado

Todo número que entra no cálculo precisa ter uma destas origens:
- (a) o plano de tese
- (b) uma referência publicada, citada no código
- (c) um resultado do próprio projeto (WP1.2, WP1.3)

**Proibido**: pesos de mistura, multiplicadores "fenomenológicos", faixas arredondadas "de bom senso", correções pós-FE. Se não houver fonte, o parâmetro não entra. Perguntar à usuária.

### Números disponíveis com fonte

| Número | Fonte |
|---|---|
| mu1 = 2,2708 MPa, alpha1 = 1,0562, D1 = 0,2247 | ajuste Friedenwald WP1.2 (Ogden) |
| P0 = 15 mmHg | plano de tese, "Equilibrar a 15 mmHg" (Ensaio A, WP2) |
| P_final = 50 mmHg | plano de tese, Ensaio B, WP2 |
| Geometria coelho (SURFACES, PTS) | Lamminsalo et al. 2018, Pharm Res, ESM Tables SI–SII (Missel 2012) |

### Números que precisam de referência (buscar antes de usar na Fase 2)

| Parâmetro | Referências sugeridas |
|---|---|
| Propriedades da córnea | Woo et al. 1972; Elsheikh et al. 2007; Kling & Marcos 2013 |
| Propriedades da íris (E ≈ 4 kPa, plano l.592) | buscar fonte primária |
| Propriedades do cristalino | Fisher 1971; Weeber & van der Heijde 2007 |
| Propriedades da lâmina cribrosa | Sigal et al. 2004, 2005; Eilaghi et al. 2010 |

## Notas técnicas

- A malha é de **olho de coelho** (Missel 2012). Troca para humano é tarefa futura.
- O conversor já foi testado e todas as 1 884 faces de superfície foram matched corretamente aos elementos de volume.
- Geometria é 90° calotte (1/4 do olho), com simetria em dois planos perpendiculares.
- Unidades consistentes: metros (malha) + Pa (pressão, material).
- `*DLOAD` no CalculiX usa pressão positiva para compressão (pressão interna aponta para dentro da superfície).
