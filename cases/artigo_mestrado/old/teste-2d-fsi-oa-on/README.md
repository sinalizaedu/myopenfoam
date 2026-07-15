# teste-2d-fsi-oa-on

Caso 2D de **FSI one-way (preCICE)** entre lúmen pulsátil da artéria oftálmica
(OA) e parede arterial elástica, com o nervo óptico (ON), bainha (ONS) e
gordura orbital ao redor. Evolução natural do caso solid-only
`teste-2d-contato-oa-on/`, adicionando o sangue dentro da OA.

## Status: smoke test FSI funcional (sem contato)

| Componente                  | Status | Notas |
|-----------------------------|--------|-------|
| BlockMesh + topoSet         | OK     | 6240 (sólido) + 880 (fluido) cells, mesh OK |
| preCICE handshake           | OK     | serial-explicit, Force exchange one-way |
| Onda OMVS pulsátil          | OK     | 80-120 mmHg, HR=69 bpm, 3 ciclos, Hann ramp 100 ms |
| Fluido (pimpleFoam)         | OK     | converge em 2-3 PIMPLE corrs, Δp inlet/outlet de 5 ms |
| Sólido (solids4Foam)        | OK     | converge por relative residual (rTol=1e-2) em 95-210 iters |
| Watchpoints preCICE         | OK     | wallBotCenter e wallTopCenter logam Force(t) |
| **Contato OA × ONS**        | **DESLIGADO** | ver "Issue: contato + FSI" abaixo |

A simulação roda end-to-end com forcing pulsátil chegando ao sólido via
preCICE. Deslocamento máximo da parede no smoke (t=0.05s, ~35% da Hann ramp)
= 0.12 μm — consistente com traction de ~6 kPa sobre `oa_wall` (E = 0.3 MPa,
espessura 0.2 mm → Δh = 6e3 * 0.2e-3 / 0.3e6 = 4 μm para PAM completo).

## Arquitetura

### Geometria 2D (z = 1 mm de espessura, plane-strain)

```
y=20.00 ┌────────────────────────────────────────┐ outer_top (fixed)
        │  Block D (fat_above, E=100 kPa)        │ 8.5 mm, NY_D=34
y=11.50 ├────────────────────────────────────────┤
        │  Block C (oa_wall sup, E=0.3 MPa)      │ 0.2 mm, NY_C=2
y=11.30 ├────────────────────────────────────────┤ lumen_top  ◀── FSI superior
        │                                        │
        │   FLUIDO -- lumen (sangue)             │ 1.1 mm, NY_F=11
        │                                        │
y=10.20 ├────────────────────────────────────────┤ lumen_bot  ◀── FSI inferior
        │  Block B (oa_wall inf, E=0.3 MPa)      │ 0.2 mm, NY_B=2
y=10.00 ├────────────────────────────────────────┤ on/oa_mestrado (smoke: FIXED)
        │  Block A (fat_below + ON + ONS)        │ 10  mm, NY_A=40
        │  ─ ON  : disco  r ≤ 1.5 mm   E=30 kPa  │
        │  ─ ONS : anel   1.5<r≤2.5 mm  E=3 MPa  │
        │  ─ fat : resto                E=100 kPa│
y= 0.00 └────────────────────────────────────────┘ outer_bottom (fixed)
        x=0                                     x=20 mm
```

### Acoplamento preCICE

```
┌──────────────────┐                          ┌─────────────────────┐
│  Fluid           │   ─── Force ─────▶       │  Solid              │
│  (pimpleFoam)    │   serial-explicit        │  (solids4Foam)      │
│  Lumen 880 cells │   1 ms time-window       │  6240 cells, contact│
└──────────────────┘                          └─────────────────────┘
   wall_bot      ╱──────────────────────────╲      lumen_bot
   wall_top     ╱   nearest-neighbor map     ╲     lumen_top
              ╱     conservative, 80 faces    ╲
            ╱       (idênticas em x)            ╲
```

### Materiais (5 zonas)

| Zona       | E       | ρ        | ν     | Referência                |
|------------|---------|----------|-------|---------------------------|
| on         | 30 kPa  | 1000     | 0.49  | Sigal et al. 2004         |
| ons        | 3 MPa   | 1100     | 0.49  | Sigal et al. 2004         |
| fat_below  | 100 kPa | 900      | 0.49  | confined fat (não 500 Pa) |
| fat_above  | 100 kPa | 900      | 0.49  | confined fat              |
| oa_wall    | 0.3 MPa | 1050     | 0.49  | Holzapfel 2000            |

Sangue: ρ = 1050 kg/m³, ν = 3.5e-6 m²/s (≈ 37 °C).

### Loading

Onda OMVS 6-piece (Sala 2019 / Guidoboni et al.) parametrizada por SP=120,
DP=80 mmHg, HR=69 bpm, T = 0.8696 s. Hann ramp TOTAL nos primeiros 100 ms
(zero → fisiológico). Outlet defasado 5 ms vs inlet para gradiente
longitudinal pulsátil.

## Como rodar

```bash
# Smoke test (50 timesteps = 0.05 s ≈ início da rampa Hann):
docker compose run --rm fsi bash -lc "cd /simulation/teste-2d-fsi-oa-on && ./Allrun"

# Para 1 ciclo cardíaco completo, editar:
#   solid/system/controlDict    : endTime 0.87
#   fluid/system/controlDict    : endTime 0.87
#   precice-config.xml          : max-time 0.87
# Tempo estimado: ~15 min em 1 core

# Para 3 ciclos (smoke validado, refinamentos prontos):
#   endTime / max-time = 2.609
# Tempo estimado: ~45 min em 1 core
```

## Pós-processamento

```bash
python3 brunaStuff/plot_teste_2d_fsi.py
```

Gera em `brunaStuff/`:
- `teste_2d_fsi_pressure_input.png` -- onda OMVS de pressão inlet/outlet
- `teste_2d_fsi_force_watchpoints.png` -- F_y nas paredes lumen ao longo de t
- `teste_2d_fsi_uy_field.png` -- mapa 2D de Dy no sólido (último timestep)

## Issue: contato OA × ONS + FSI = blow-up

**Sintoma:** quando `oa_mestrado`/`on_mestrado` usam `solidContact` em vez de
`fixedDisplacement`, o solver explode no primeiro timestep com:

```
Initial Solution Norm = 2.2e+8 m   (vs 3e-9 m sem contato)
Iteration 2: Converged - Step norm relative tolerance met.   ← fake convergence
Dy_min em Block B (wall_inf): -5.2 MILHÕES de metros
```

**Raiz:** solids4foam seta automaticamente `extrapolateValue=true` em todos
os patches que herdam de `solidTraction` (inclusive `solidContact` E
`solidForce`). Quando o sólido tem DOIS BCs não-lineares ativos na mesma
fina camada (Block B de 0.2 mm: contato no fundo, FSI no topo), gradient(D)
diverge no init e o BC value extrapolado dispara. O solver então "converge"
prematuramente por `Step norm criterion` com `xNorm` astronômico.

**Tentativas que NÃO resolveram:**
- `penaltyScale 0.01` (100× menor que solid-only)
- `relaxationFactor 0.001` (50× menor)
- `sTol 1e-15` em `solidProperties` (desligar criterio step-norm)

**Workaround atual (no smoke):** ancorar `on_mestrado`/`oa_mestrado` em
`fixedDisplacement (0 0 0)` -- equivale a contato "tied constraint", o que
**contraria a especificação original do user**. Block A e Block B ficam
rigidamente fixos no plano y=10.

**Path forward para reativar contato + FSI (não tentado nesta iteração):**
1. **`nonLinearGeometryTotalLagrangianTotalDisplacement`** com Newton-Raphson:
   pode lidar melhor com gradient explosivo e step-control. Mas exige
   verificar se `solidContact` está compatível com nonLinearGeometry no
   solids4foam v2.3+.
2. **Initial gap > 0** offsetting Block B em +50 μm (não tangente em y=10):
   contato só engaja após FSI comprimir wall. Evita estado singular tangente.
3. **TWO-WAY FSI com Aitken/IQN-ILS:** suaviza a força por iteração
   (relaxationFactor 0.1), evitando "kicks" impulsivos. Exige
   `dynamicMeshDict` no fluido com mesh motion.
4. **`mortar` contact** em vez de `standardPenalty`: distribuição contínua
   da força em vez de penalty pointwise. Disponível no solids4foam? Verificar.

## Diferenças vs `cases/ao-mestrado` (caso 3D existente)

| Aspecto              | ao-mestrado (3D)             | teste-2d-fsi (2D)                |
|----------------------|------------------------------|----------------------------------|
| Geometria            | Centerline STL real          | Cartesiana retangular           |
| Mesh                 | Polyhedric extrudada O-grid  | hex 80×NY puramente Cartesian   |
| Tecidos ao redor     | Winkler spring (E_fat exterior)| 5 zonas (fat/ON/ONS/wall)      |
| Cap de artéria       | inner_cap_back/front fixed   | outer_left/right symmetry       |
| Contato              | ausente                      | desabilitado no smoke           |
| FSI direction        | one-way (Force)              | one-way (Force) idem            |
| Tempo de run         | ~25 min / 1 cycle            | ~10 min / 50 steps              |

## Próximos passos sugeridos (priorizados)

1. **Rodar 1 ciclo completo** (endTime 0.87) e validar:
   - Forças no watchpoint oscilam com a frequência cardíaca
   - Dy máximo do wall_inf segue P(t) com pequeno atraso de fase
   - Conservação de massa no fluido (∫Q_inlet - ∫Q_outlet ≈ 0 over T)
2. **Reativar contato** seguindo path forward A/B/C/D acima
3. **Two-way FSI** com `dynamicMotionSolverFvMesh` no fluido para capturar
   feedback da deformação da parede no escoamento
4. **Refinar mesh** do lumen (NY_F=22, dy=0.05 mm) para resolver perfil de
   velocidade parabólico melhor

## Arquivos do caso

```
teste-2d-fsi-oa-on/
├── README.md                    ← este arquivo
├── Allrun                       ← orquestrador
├── Allclean
├── precice-config.xml           ← config preCICE (serial-explicit Force)
├── scripts/                     ← geradores Python auto-contidos
│   ├── gen_teste_2d_fsi_blockmesh.py
│   ├── gen_teste_2d_fsi_omvs_pressure.py
│   └── plot_teste_2d_fsi.py
├── solid/
│   ├── 0/{D, solidForce}        ← BCs + campo de força preCICE
│   ├── 0/D.with-contact         ← backup com solidContact (blow-up)
│   ├── constant/{physicsProperties, mechanicalProperties, solidProperties, g}
│   └── system/{controlDict, topoSetDict, fvSchemes, fvSolution, preciceDict}
└── fluid/
    ├── 0/{U, p}                 ← BCs + pressao OMVS
    ├── constant/{fluidProperties, transportProperties, turbulenceProperties, dynamicMeshDict, inlet_pressure.dat, outlet_pressure.dat}
    └── system/{controlDict, fvSchemes, fvSolution, preciceDict}
```
