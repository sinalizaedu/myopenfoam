# Caso `sugestao` — FSI artéria-nervo com contato físico real

> **Objetivo primário**: extrair `P_contact(t, x)` da interface artéria-ONS via
> solver de contato físico (não inferido por escalar prescrito).
>
> **Objetivo secundário**: medir tortuosidade do nervo óptico ao longo do
> ciclo cardíaco.
>
> **Preparação fase 2**: setup compatível com adição posterior de pressão CSF
> no espaço subaracnóide, que vai inflar a ONS e expandir naturalmente o
> patch de contato — sem reescrita do caso.

---

## 1. Arquitetura

```
                  ┌────────────────────────────────────────┐
                  │           CASE  sugestao               │
                  └────────────────────────────────────────┘
                  │
   ┌──────────────┴───────────────┐
   ▼                              ▼
┌────────────────┐         ┌──────────────────────────────────────────┐
│  fluid/        │         │  solid/                                   │
│  pimpleFoam    │         │  solids4Foam (unsLinearGeometry)          │
│  Newtonian     │         │                                            │
│  laminar       │         │  6 cellZones:                             │
│                │         │     arteria  E=0.3 MPa, nu=0.49           │
│  Inlet/outlet: │         │     on        E=30  kPa, nu=0.49          │
│  OMVS waveform │         │     ons       E=3.0 MPa, nu=0.49          │
│  120/80, 69bpm │         │     lc        E=0.4 MPa, nu=0.49          │
│  Δt = 1 ms     │         │     sclera    E=5.0 MPa, nu=0.45          │
│                │         │     globo     E=5.0 MPa, nu=0.45          │
└──────┬─────────┘         └──────────────────────────────────────────┘
       │ preCICE one-way                ▲          ▲
       │ Force                          │          │
       │ Fluid-Mesh -> Solid-Mesh       │          │
       └───────► arteria_lumen ─────────┘          │
                                                   │
                       solidContact (penalty)      │
                       arteria_externa  <-->  ons_outer
                       master                slave
                       => P_contact(t, x) emerge dinamicamente
```

### Patches do solid (12 total)

Da artéria (zona `arteria`, ~15k cells):
- `arteria_lumen`     — interface FSI (preCICE Force)
- `arteria_externa`   — **MASTER** do solidContact (par com `ons_outer`)
- `inner_cap_back`    — engaste anatômico (fixedDisplacement)
- `inner_cap_front`   — engaste anatômico (fixedDisplacement)

Do nervo + bainha + lc + sclera + globo (zonas `on`/`ons`/`lc`/`sclera`/`globo`,
~16k cells):
- `posterior_on`      — solidTraction(0) (ON livre, desliza na bainha)
- `posterior_ons`     — solidTraction(0) — **placeholder CSF (FASE 2)**
- `ons_outer`         — **SLAVE** do solidContact
- `sclera_outer`      — solidTraction(0) (livre)
- `globo_outer`       — solidTraction(0) (livre)
- `anterior_globo`    — fixedDisplacement (parede orbital)

Patches CSF criados a posteriori via `createBaffles` (debond ON↔ONS):
- `on_outer`          — solidTraction(0) — **placeholder CSF (FASE 2)**
- `ons_inner`         — solidTraction(0) — **placeholder CSF (FASE 2)**

---

## 2. Como rodar

### Dentro do Docker (`fsi-openfoam:latest`)

```bash
cd /simulation/sugestao
./Allrun
```

O `Allrun` orquestra automaticamente:

1. Compila `libsolidTractionElasticFoundation.so` (mola de Winkler) se faltar
2. Gera `fluid/constant/polyMesh` via `build_artoph_tubular_meshes.py`
3. Roda `fluid/Allmesh` (checkMesh)
4. Roda `solid/Allmesh`:
   - `blockMesh` em `staging/nerve/` (gera nervo+ONS+lc+sclera+globo, com 5 cellZones)
   - `build_sugestao_solid_arteria.py` em `staging/arteria/` (extrusão + cellZone `arteria`)
   - `mergeMeshes` (combina, preservando todas as 6 cellZones)
   - `topoSet -dict topoSetDict_csf` (cria faceZone `csf_interface` na interface ON↔ONS)
   - `createBaffles -dict createBafflesDict_csf` (debond → patches `on_outer` e `ons_inner`)
   - Restaura `0/D` (createBaffles sobrescreveu BCs dos patches novos com `calculated`)
   - `checkMesh` final
5. Roda preCICE + pimpleFoam (fluido) + solids4Foam (sólido) acoplados

### Fora do Docker

```bash
./Allrun
# vai apenas gerar a polyMesh do fluido (Python puro), pular solver
# (precisa do WM_PROJECT_DIR)
```

### Limpar e re-rodar

```bash
./Allclean              # apaga time-dirs e logs (preserva mesh + 0/)
./Allrun
```

Para reset completo da malha (recompilação de tudo):
```bash
rm -rf {fluid,solid}/constant/polyMesh \
       solid/staging/{nerve,arteria}/constant/polyMesh
./Allrun
```

---

## 3. Parâmetros chave

| Item                    | Valor          | Local                                        |
|-------------------------|----------------|----------------------------------------------|
| HR                      | 69 bpm         | `fluid/constant/inlet_pressure.dat`          |
| Pressão sistólica       | 120 mmHg       | OMVS gen + `fluid/constant/inlet_pressure.dat` |
| Pressão diastólica      | 80 mmHg        | OMVS gen                                     |
| Δp inlet/outlet         | ~10 Pa + 5 ms phase shift | `fluid/constant/outlet_pressure.dat`        |
| `endTime`               | 0.870 s        | `solid/system/controlDict`, `fluid/system/controlDict`, `precice-config.xml` |
| `deltaT`                | 1 ms           | idem                                         |
| Penalty scale (solidContact) | 1         | `solid/0/D` em `arteria_externa`             |
| `relaxationFactor` D    | 0.5            | `solid/system/fvSolution`                    |
| nCorrectors             | 300            | `solid/constant/solidProperties`             |
| `solutionTolerance`     | 5e-2           | `solid/constant/solidProperties`             |

Para 3 ciclos cardíacos (mais robusto contra transiente), trocar `endTime` em
três arquivos para `2.609`s (`solid/system/controlDict`, `fluid/system/
controlDict`, `precice-config.xml/max-time`). Não exige re-malhar.

---

## 4. Pós-processamento

Os 3 scripts em `brunaStuff/` consomem os outputs da simulação:

| Script                                  | Saída                                      |
|-----------------------------------------|-------------------------------------------|
| `compute_nerve_tortuosity.py`           | `sugestao_nerve_tortuosity.csv` + PNG     |
| `extract_p_contact_from_sugestao.py`    | `sugestao_p_contact_summary.csv` + per-face CSV |
| `plot_sugestao_health.py`               | `sugestao_health_panorama.png` (6 painéis)|

Workflow típico após o `Allrun`:

```bash
python3 brunaStuff/extract_p_contact_from_sugestao.py
python3 brunaStuff/compute_nerve_tortuosity.py
python3 brunaStuff/plot_sugestao_health.py
```

### Interpretação rápida

- **P_contact_max(t)**: deve ser modulada pelo ciclo cardíaco. Se ≈ 0,
  o solidContact não está detectando contato (a artéria não toca o ONS no
  P_contact previsto). Tunar `penaltyScale` ou diminuir o gap geométrico.

- **A_contact(t)**: área de contato dinâmica. Com geometria translada com
  gap inicial de 33 µm, espera-se A_c na faixa 0–2 mm² (ordem de grandeza
  de uma face de mesh).

- **Tortuosidade**: para o caso atual (sem CSF), valores < 0.5% são
  esperados. Em FASE 2 (CSF=20 mmHg + DBON), 1–10% indica acoplamento real
  artéria↔nervo via bainha distendida.

- **Razão P_contact / P_lumen**: 0.1–0.8 no peak sistólico indica
  acoplamento físico coerente; razão > 1 ou ≈ 0 indica overshoot do penalty
  ou ausência de contato, respectivamente.

---

## 5. FASE 2 — ativando CSF

Quando quiser modelar pressão CSF elevada (e.g. 20 mmHg = 2667 Pa em
microgravidade/SANS), trocar `pressure 0` → `pressure 2667` em `solid/0/D`
nos seguintes patches (3 alterações):

```diff
 posterior_ons {
     type        solidTraction;
     traction    uniform ( 0 0 0 );
-    pressure    uniform 0;
+    pressure    uniform 2667;     // CSF = 20 mmHg
     value       uniform ( 0 0 0 );
 }
 on_outer {
     type        solidTraction;
     traction    uniform ( 0 0 0 );
-    pressure    uniform 0;
+    pressure    uniform 2667;     // CSF empurra ON pra dentro
     value       uniform ( 0 0 0 );
 }
 ons_inner {
     type        solidTraction;
     traction    uniform ( 0 0 0 );
-    pressure    uniform 0;
+    pressure    uniform 2667;     // CSF empurra ONS pra fora (DBON)
     value       uniform ( 0 0 0 );
 }
```

A bainha (`ons`) vai dilatar radialmente, aproximando geometricamente a face
externa do ONS da face externa da artéria. O `solidContact` vai detectar
mais faces ativas, **expandindo dinamicamente** o patch de contato — sem
reescrita do caso, sem nova malha.

Para fazer um sweep de PIC: parametrizar `pressure` via `pressureSeries`
(análogo ao on-mestrado) e usar tabela `constant/csf_pressure.dat`.

---

## 6. Limitações conhecidas

1. **One-way FSI**: malha do fluido fica estática (`staticFvMesh`); a
   pressão luminal deforma a artéria, mas a deformação NÃO retroage no
   fluxo. Subestima Q (mas NÃO P_contact, que é dominado pela pressão
   interna ≫ pulsação local de fluxo).

2. **Linear elástico em todas as zonas**: subestima rigidez fisiológica
   em ε > 10% (validação teórica em conversa anterior, ~25% erro biaxial).
   Compensável ajustando `E_arteria` de 0.3 → 1.0 MPa em runs subsequentes,
   ou trocando para `neoHookeanElastic` (mantendo o mesmo solid model).

3. **Gordura como Winkler omitida nas faces NÃO-contato do solidContact**:
   no smoke test, faces de `arteria_externa`/`ons_outer` que NÃO entram em
   contato ficam com tracção zero (livres). A literatura sugere que a
   gordura orbital impõe ~0.5–0.9 kPa/m de rigidez radial, o que
   reduziria a deformação livre em ~10%. Para refinamento, pode-se dividir
   `arteria_externa` em sub-patches (contato + Winkler) via `topoSet`
   pré-merge.

4. **`solidContact` requer tunar `penaltyScale`** se não convergir; pode
   demandar Δt menor que 1 ms se o gap inicial for muito apertado.

5. **Razão de rigidez E_sclera/E_on = 167×**: mal-condicionamento da matriz
   de rigidez é tratado pelo `relTol=0.05` em `fvSolution`. Já validado em
   `on-mestrado`.

---

## 7. Estrutura de arquivos

```
cases/sugestao/
├── README.md                              # este arquivo
├── Allrun                                 # pipeline completo
├── Allclean                               # limpa logs/time-dirs (preserva mesh)
├── _smoke_run.sh                          # helper (lançar solvers em paralelo)
├── precice-config.xml                     # one-way Fluid -> Solid
├── constant/
│   ├── triSurface/                        # STLs (artery, nerve, etc)
│   └── ...
├── fluid/                                 # idêntico a ao-mestrado
│   ├── 0/{U,p}
│   ├── Allmesh
│   ├── constant/{transportProperties, turbulenceProperties, dynamicMeshDict,
│   │             inlet_pressure.dat, outlet_pressure.dat}
│   └── system/{controlDict, fvSchemes, fvSolution, preciceDict, decomposeParDict}
├── solid/                                 # núcleo do caso
│   ├── 0/{D, solidForce}
│   ├── Allmesh                            # blockMesh + build_arteria + merge + baffles
│   ├── constant/
│   │   ├── physicsProperties              # type=solid
│   │   ├── solidProperties                # unsLinearGeometry, nCorr=300
│   │   ├── mechanicalProperties           # 6 zonas (arteria, on, ons, lc, sclera, globo)
│   │   ├── g
│   │   └── polyMesh/                      # gerado pelo Allmesh
│   ├── system/
│   │   ├── controlDict                    # endTime, libs Winkler, watchpoints
│   │   ├── fvSchemes
│   │   ├── fvSolution                     # PCG/FDIC, relTol=0.05, relaxD=0.5
│   │   ├── preciceDict                    # patches=(arteria_lumen)
│   │   ├── topoSetDict_csf                # cria faceZone csf_interface
│   │   ├── createBafflesDict_csf          # cria on_outer + ons_inner
│   │   └── decomposeParDict
│   └── staging/                           # dirs intermediários (apagáveis)
│       ├── nerve/{constant/polyMesh, system/blockMeshDict, system/controlDict}
│       └── arteria/{constant/polyMesh, system/controlDict}
├── scripts/                               # scripts brunaStuff sincronizados
│   ├── build_artoph_tubular_meshes.py
│   └── build_sugestao_solid_arteria.py
└── src/elasticFoundation/                 # lib custom Winkler (opcional)
```
