# Dossiê on-caso-2 V14b — Modelo SANS validado

**Data:** 2026-05-29
**Status:** Convergiu até λ=1.0 (Δz=-1.5 mm), 49 incrementos, 6m25s (Riks)
**Arquivo principal:** `cases/on-caso-2/ccx/on-caso-2.inp`
**Mesh:** `cases/on-caso-2/solid/system/blockMeshDict` (8 zonas)

---

## 1. Filosofia do modelo SANS

A síndrome neuro-ocular do voo espacial (SANS) **não é flambagem de Euler clássica da dura-máter**.
A dura é mantida **reta e tensa** por:
- Pressurização interna (PIC + SAS solidificado)
- Anisotropia circunferencial (fibras de colágeno)
- Fundação elástica externa (gordura orbital — Winkler)

O que **realmente flamba** é o complexo **nervo+pia**, em modo S (modo 2 antissimétrico),
*dentro* do tubo dural rígido. O SAS sólido fluido-like absorve a deformação
radial sem reagir hidrostaticamente.

**Mecanismo da lesão neural:** o cocoon dural rígido obriga o esmagamento longitudinal
do tecido neural macio — confirmação numérica do quadro clínico SANS (isquemia +
edema da papila).

---

## 2. Geometria e mesh (8 zonas, blockMesh)

| Zona | r interno (mm) | r externo (mm) | z (mm) | Material | E |
|---|---|---|---|---|---|
| **on**          | 0.00 | 1.50 | 0–30        | NEO HOOKE | 30 kPa |
| **pia**         | 1.50 | 1.55 | 0–30        | NEO HOOKE | 3 MPa |
| **sas**         | 1.55 | 2.35 | 0–30        | NEO HOOKE | **3 kPa** |
| **dura**        | 2.35 | 2.50 | 0–30        | ORTOTRÓPICO | 3 / 9 / 3 MPa |
| **lc**          | 0.00 | 1.50 | 30–30.30    | NEO HOOKE | 300 kPa |
| **sclera_peri** | 1.50 | 2.00 | 30–30.30    | NEO HOOKE | 3 MPa |
| **sclera_ring** | 2.00 | 2.50 | 30–30.30    | NEO HOOKE | 3 MPa |
| **globo**       | 0.00 | 2.50 | 30.30–30.80 | NEO HOOKE | 3 MPa |

**Resolução:** 6 tangencial × 10 axial nervo / 1–3 radiais por camada → 2736 hex.
Discretização ortogonal "O-grid" via 4 quadrantes + bloco central (núcleo cartesiano,
arcos no contorno via `arc` no `edges`).

**Patches gerados pelo blockMesh:**
`posterior_{on,pia,sas,dura}` (z=0), `dura_outer` (Winkler), `sclera_ring_outer`,
`globo_outer`, `anterior_globo` (z=30.80).

---

## 3. Materiais (lei NEO HOOKE compressível CCX)

Fórmula CCX: `W = C10·(I1_bar – 3) + (1/D1)·(J – 1)²`
Conversão a partir de E, ν:
```
C10 = E / [4·(1 + ν)]
D1  = 6·(1 – 2ν) / E
K   = E / [3·(1 – 2ν)]   (módulo de bulk)
```

### Tabela de materiais

| Material  | E         | ν     | C10 (Pa)      | D1 (1/Pa)   | Densidade |
|-----------|-----------|-------|---------------|-------------|-----------|
| ON_MAT (nervo)         | 30 kPa  | 0.49 | 5.0335e+03 | 4.0000e-06 | 1000 |
| PIA_MAT                | 3 MPa   | 0.49 | 5.0335e+05 | 4.0000e-08 | 1100 |
| **SAS_MAT (fluid-like)** | **3 kPa** | **0.05** | **7.1430e+02** | **1.8000e-03** | 1000 |
| LC_MAT (lâmina cribrosa) | 300 kPa | 0.49 | 5.0335e+04 | 4.0000e-07 | 1100 |
| SCLERA_PERI_MAT        | 3 MPa   | 0.49 | 5.0335e+05 | 4.0000e-08 | 1400 |
| SCLERA_RING_MAT        | 3 MPa   | 0.49 | 5.0335e+05 | 4.0000e-08 | 1400 |
| GLOBO_MAT              | 3 MPa   | 0.49 | 5.0335e+05 | 4.0000e-08 | 1400 |

### Dura ortotrópica (sistema cilíndrico)

```
*MATERIAL, NAME=DURA_MAT
*ELASTIC, TYPE=ENGINEERING CONSTANTS
** E_r,    E_theta, E_z,     nu_rt, nu_rz, nu_tz, G_rt,    G_rz
3.000e+6, 9.000e+6, 3.000e+6, 0.30,  0.30,  0.30,  1.150e+6, 1.150e+6
** G_tz, T
1.150e+6, 0.0
*DENSITY
1100

*ORIENTATION, NAME=ORI_CYL, SYSTEM=CYLINDRICAL
0.0, 0.0, 0.0,  0.0, 0.0, 1.0
*SOLID SECTION, ELSET=DURA, MATERIAL=DURA_MAT, ORIENTATION=ORI_CYL
```

**Razão E_θ / E_axial = 3** (Holzapfel 10× é severo demais para convergir junto
com perturbação). O eixo do CYLINDRICAL é a normal `(0,0,1)` (z = eixo do nervo).

### SAS "fluid-like" — chave do modelo

- **E = 3 kPa** (10× mais macio que o nervo neural)
- **ν = 0.05** (quase-nulo) → **K = 1.1 kPa** (45× menor que com ν=0.30)
- Permite "esmagamento" axial sem desenvolver contrapressão lateral irrealista
- Continuidade de mesh impede pia atravessar dura
- **Substitui as molas SPRINGA** (trabéculas) e o **DSLOAD de PIC** (a tensão
  hidrostática emerge naturalmente da compressão)

---

## 4. Elemento e seções

```
*SOLID SECTION, ELSET=ON,          MATERIAL=ON_MAT
*SOLID SECTION, ELSET=PIA,         MATERIAL=PIA_MAT
*SOLID SECTION, ELSET=SAS,         MATERIAL=SAS_MAT
*SOLID SECTION, ELSET=DURA,        MATERIAL=DURA_MAT, ORIENTATION=ORI_CYL
*SOLID SECTION, ELSET=LC,          MATERIAL=LC_MAT
*SOLID SECTION, ELSET=SCLERA_PERI, MATERIAL=SCLERA_PERI_MAT
*SOLID SECTION, ELSET=SCLERA_RING, MATERIAL=SCLERA_RING_MAT
*SOLID SECTION, ELSET=GLOBO,       MATERIAL=GLOBO_MAT
```

**Tipo de elemento:** **C3D8I** (hex linear com modos incompatíveis).
Mitiga *volumetric locking* em ν≥0.49 sem precisar montar C3D20R.
Definido no `foam_polymesh_to_ccx_inp.py` (`--element-type C3D8I`).

---

## 5. Boundary conditions

### Engaste posterior (canal óptico, z=0)
Fixa rígida, todos os DOFs (ósseo apertando o nervo radialmente E axialmente):
```
*BOUNDARY
POSTERIOR_ON,   1, 3, 0.0
POSTERIOR_PIA,  1, 3, 0.0
POSTERIOR_SAS,  1, 3, 0.0
POSTERIOR_DURA, 1, 3, 0.0
```

### Anterior globo (z=30.80)
Confinado lateralmente (órbita) + rampa Dz prescrita:
```
*BOUNDARY
ANTERIOR_GLOBO, 1, 2, 0.0          ! XY fixo, simula a órbita

*BOUNDARY, AMPLITUDE=DZRAMP
ANTERIOR_GLOBO, 3, 3, -1.50e-3     ! rampa axial -1.5 mm em z
```

### Winkler (gordura orbital, k=200 kPa/m)
Gerada automaticamente no `on-caso-2_winkler.inp` pelo conversor. SPRINGA radiais
em todos os nós de `dura_outer` ligando-os a um nó "ground" fixo.

---

## 6. Cargas

### Amplitude (rampa linear 0→1)
```
*AMPLITUDE, NAME=DZRAMP
0.0, 0.0,   1.0, 1.0
```

### EOM (tração residual dos músculos extraoculares)
Carga complementar pequena que se soma ao deslocamento do globo:
```
*CLOAD, AMPLITUDE=DZRAMP
ANTERIOR_GLOBO, 3, -1.0e-4         ! ~16 mN total em z negativo
```

### Perturbação antissimétrica (gatilho de modo 2)
Dois nset's na pia outer (r=1.55 mm) em pontos opostos longitudinalmente,
forçando o modo S em vez do modo C:
```
*NSET, NSET=PERT_NODES_A
2148, 2147, 2149, 2146, 2150
*NSET, NSET=PERT_NODES_B
2311, 2310, 2312, 2309, 2313

*CLOAD                              ! NÃO usa AMPLITUDE: pert constante
PERT_NODES_A, 1, +3.0e-3            ! +X em z≈10 mm
PERT_NODES_B, 1, -3.0e-3            ! -X em z≈20 mm
```

### PIC (REMOVIDO)
Não há mais `*DSLOAD` em `fsi_pia_surf` ou `fsi_dura_surf`. O SAS sólido
quase-incompressível (K=1.1 kPa) desenvolve tensão hidrostática intrínseca
sob compressão axial — substitui o load explícito de PIC.

---

## 7. Solver (Riks arc-length)

```
*STEP, NLGEOM=YES, INC=500
*STATIC, RIKS
0.025, 1.0, 1e-5, 0.05, 2.5
**       dl_init=0.025
**       l_total=1.0
**       dl_min =1e-5
**       dl_max =0.05
**       lambda_max (ARCMAX) = 2.5
```

**Por que Riks e não Newton-Raphson:**
- Estrutura amolece após P_cr (snap-through ou bifurcação Euler)
- Newton diverge no ponto crítico
- Riks ajusta dinamicamente o incremento via λ (load proportionality factor)
- ARCMAX=2.5 permite ir além de Δz=-1.5 mm se quiser explorar pós-buckling

**Single-step:** todas as cargas ramped juntas (PIC+Dz+pert) com mesmo λ.
2-step (PIC preload depois Dz) divergiu na transição por cargas residuais
mal condicionadas no `.sta`.

---

## 8. Outputs

```
*NODE PRINT, FREQUENCY=1, NSET=POSTERIOR_DURA, TOTALS=ONLY
RF, U
*NODE PRINT, FREQUENCY=1, NSET=POSTERIOR_PIA,  TOTALS=ONLY
RF, U
*NODE PRINT, FREQUENCY=1, NSET=POSTERIOR_ON,   TOTALS=ONLY
RF, U
*NODE PRINT, FREQUENCY=1, NSET=ANTERIOR_GLOBO, TOTALS=ONLY
RF, U

*NODE FILE, FREQUENCY=5
U, RF
*EL FILE, FREQUENCY=5
S, E
*END STEP
```

**Outputs gerados:**
- `.dat` — totais RF/U por NSET por incremento (curva F-d)
- `.frd` — campos U, RF, S, E para visualização (cgx/ParaView)
- `.cvg` — resíduos por iteração (debug de convergência)
- `.sta` — status de cada incremento Riks (λ atual, dl, número de iter)

---

## 9. Pipeline de execução (Allrun)

```bash
cd cases/on-caso-2/ccx && ./Allrun
```

**Etapas internas:**
1. **blockMesh** + topoSet + createPatch (gera polyMesh em `../solid`)
2. **foam_polymesh_to_ccx_inp.py** converte polyMesh → 2 .inp:
   - `on-caso-2_mesh.inp` (nodes, elementos, NSETs, ELSETs)
   - `on-caso-2_winkler.inp` (SPRINGA radiais em dura_outer, k=200000 N/m³)
3. **ccx_preCICE -i on-caso-2** (CalculiX standalone, sem precice-config)
4. **ccx2paraview** (host, fora do container) → `.vtu` + `.pvd` para ParaView

**Comando completo manual:**
```bash
cd /Users/brunaenne/Documents/repos/myopenfoam
docker compose run --rm fsi bash -lc "cd /simulation/on-caso-2/ccx && ./Allrun"
# converter para ParaView (host):
cd cases/on-caso-2/ccx && /tmp/ccx2pv/bin/ccx2paraview on-caso-2.frd vtu
```

---

## 10. Pós-processamento

`brunaStuff/analyze_on-caso-2_ccx.py` — extrai do `.dat`:
- RF total nos engastes posteriores (z=0)
- Dz real do anterior_globo (Riks varia o load factor)
- Decomposição por camada (dura, pia, on)
- Comparação com Euler analítico (P_cr K=0.5/0.7/1.0)
- Lateral kink máximo (envelope de Ux,Uy)

**Outputs:**
- `on-caso-2_ccx_F_vs_dz.png` (curva F-d + comparação Euler)
- `on-caso-2_ccx_summary.txt` (resumo numérico)

---

## 11. Resultados V14b (validação SANS)

**Parâmetros finais que funcionaram:**
- Mesh: 8 zonas, 2736 C3D8I, ν=0.49 quase-incompressível
- SAS: E=3 kPa, ν=0.05 (fluid-like)
- Dura: ortotrópica E_circ=3·E_axial
- Winkler: k=200 kPa/m em dura_outer
- Perturbação: ±3 mN antissimétrica em pia outer
- Dz prescrito: -1.5 mm em rampa
- EOM CLOAD: -1e-4 N/nó complementar
- Riks: dl_init=0.025, dl_max=0.05, ARCMAX=2.5

**Resultado:**

| Camada (radial) | Kink lateral max (mm) | Comportamento |
|---|---|---|
| ON (r=0.5)   | 0.20  | segue pia, esmagado axialmente |
| **PIA (r=1.55)** | **0.275** | **modo S claro com inflexão em z≈14 mm** |
| SAS (r=2.0)  | 0.16  | esmagado, deforma radialmente sem reagir |
| DURA (r=2.5) | 0.08  | quase reta — tubo rígido |

**Curva F-d:**
- F_total no engaste = 537 mN @ Dz=-1.5 mm
- Dura sozinha = 33 mN (longe dos 221 mN de Euler com K=1.0) → **dura nunca flamba**
- Nervo absorve 437 mN → **esmagamento neural = mecanismo SANS confirmado**

---

## 12. Lições para outros casos

1. **Solver:** sempre Riks com NLGEOM=YES para problemas de instabilidade
2. **Elemento:** C3D8I obrigatório para ν≥0.49 (sem locking)
3. **SAS solidificado** com ν muito baixo (0.05) é **superior** a:
   - DSLOAD de PIC (PIC explícito gera oscilações no Riks)
   - SPRINGA radiais (não impedem interpenetração da pia na dura)
4. **Dura ortotrópica** (E_circ > E_axial) é essencial para obter dura reta
   sob PIC interna — caso isotrópica, dura "balona"
5. **Perturbação antissimétrica** (modo 2) é necessária para obter S em vez de C
6. **Engaste total dos 4 patches z=0** (incluindo SAS) é coerente com canal óptico
   ósseo, e estabiliza o solver
7. **Single-step Riks** > 2-step (PIC preload + Dz separados divergem)
8. **Anisotropia 3× é o limite numérico** — 10× (Holzapfel pleno) diverge

## 13. Variáveis sem implementar (fica para variantes futuras)

- **Gravidade** = 0 (consistente com microgravidade SANS — não foi adicionada)
- **EOM force-driven puro** (sem Dz prescrito) — divergiu, fica para `on-caso-2.2`
- **PIC como `*INITIAL CONDITIONS, TYPE=STRESS`** (preload pré-existente) — omitido
- **Contato pia-dura explícito** (`*CONTACT PAIR`) — substituído por SAS sólido
- **Anisotropia da pia/sclera** — todas isotrópicas Neo-Hooke
- **Variação fásica/temporal** — caso é estático Riks, sem dinâmica

---

## 14. Plots gerados

- `brunaStuff/on-caso-2_v14b_SAS_nu005.png` — vista XZ + envelope kink por camada
- `brunaStuff/on-caso-2_ccx_F_vs_dz.png` — curva F-d com decomposição
- `brunaStuff/on-caso-2_v14_SAS_solid.png` — comparativo (SAS ν=0.30)
- `brunaStuff/on-caso-2_v13_3items.png` — versão com SPRINGA + ortotrópica
- `brunaStuff/on-caso-2_v12_SANS_S_kink.png` — versão com PIC explícito

## 15. Histórico das iterações principais

| Versão | Mudança | Resultado |
|---|---|---|
| V2-V8 | Mesh 7 zonas, sem SAS, com PIC DSLOAD | Modo C, dura flamba (errado) |
| V9-V11 | Tentativas de modo S por BC | C ou S parcial |
| V12 | PIC=1500 Pa + Winkler+Pert | Dura ainda flamba |
| V13 | Trabéculas SPRINGA + Dura ortotrópica + EOM | S parcial, springs estouram |
| V14 | SAS sólido E=3kPa ν=0.30 | S claro, mas SAS gera contrapressão |
| **V14b** | **SAS sólido E=3kPa ν=0.05** | **S nítido + SAS esmagável** |
