# Lamminsalo (2018) — equações governantes e mapeamento OpenFOAM

**Fonte:** Lamminsalo M et al., *Pharm. Res.* 2018;35:178 — Methods (COMSOL Multiphysics).  
**Caso:** `eye-fsi-tc0` — Sim 1 Step 0 (`simpleFoam`).

---

## 1. Fluido livre (câmara anterior) — COMSOL

Lamminsalo resolve **Navier–Stokes incompressível** com aproximação **Boussinesq**:

- fluido incompressível;
- **include gravity** + **use reduced pressure**;
- acoplamento **Nonisothermal Flow** (transferência de calor + escoamento).

Em forma reduzida (momentum + continuidade):

$$\frac{\rho}{\varepsilon_p}\left(\frac{\partial \mathbf{u}}{\partial t} + \mathbf{u}\cdot\nabla\mathbf{u}\right) = -\nabla p_r + \frac{\mu}{\varepsilon_p}\nabla^2\mathbf{u} - \frac{\mu}{\boldsymbol{\kappa}}\mathbf{u} + \rho\mathbf{g} + \mathbf{S}_{mom}$$

$$\nabla\cdot\mathbf{u} = \frac{Q_{br}}{\rho}$$

onde $p_r$ é a pressão reduzida, $\mathbf{g}$ gravidade e $Q_{br}$ fonte/sumidouro de massa [kg m⁻³ s⁻¹].

### Mapeamento OpenFOAM — tese IVI/ACP

| COMSOL (Lamminsalo) | OpenFOAM `eye-fsi-tc0` | Status |
|---------------------|------------------------|--------|
| Incompressível | `simpleFoam` (Newtoniano) | **Ativo** |
| Pressão reduzida | `p` cinemática (p_kin = p/ρ) | **Ativo** |
| Gravidade + Boussinesq | `buoyantBoussinesqSimpleFoam` | **Não implementar** |
| Nonisothermal Flow | `buoyantBoussinesqPimpleFoam` + `T` | **Não implementar** |
| $Q_{br}$ na porta ciliar | `flowRateInletVelocity` em `ac_inlet` | **Ativo** (3 µL/min) |
| μ, ρ @ 37 °C | `phaseProperties` + `transportProperties` | **Ativo** (isotérmico) |

**Decisão:** física térmica do Lamminsalo é para **drug delivery** (PK, mistura AC). IVI/paracentese = segundos–minutos, dominados por volume e complacência — **sem** `buoyantBoussinesq*`, sem equação de energia (plano §13.1).

---

## 2. Meio poroso — equações de Brinkman (COMSOL)

Nos tecidos porosos (vítreo, TM, retina/esclera, córnea), Lamminsalo usa **Brinkman**:

- $\varepsilon_p$ — porosidade (Tabela I);
- $\boldsymbol{\kappa}$ — permeabilidade [m²] (tensor; isotrópico no caso);
- $Q_{br}$ — fonte de massa volumétrica [kg m⁻³ s⁻¹].

Termo de arrasto Darcy dentro do Brinkman: $-\frac{\mu}{\boldsymbol{\kappa}}\mathbf{u}$.

Termo viscoso Brinkman: $\frac{\mu}{\varepsilon_p}\nabla^2\mathbf{u}$ (difusão efetiva no meio poroso).

### Tabela I — porosidade e permeabilidade

| Tecido | $\varepsilon_p$ | $\kappa$ [m²] | OpenFOAM cellZone |
|--------|-----------------|---------------|-------------------|
| Humor aquoso (AC) | 0 | — (fluido livre) | fluido AC |
| Vítreo | 1 | **5,8×10⁻¹⁴** | `vitreous_zone` |
| TM | 1 | **ajustada** (ᵍ) | `tm_zone`, `tm_zone_left` |
| Córnea / retina / esclera | 1 | 1,04×10⁻¹⁸ | G2 (não no G1 Step 0) |

---

## 3. Aproximação OpenFOAM — limite Darcy do Brinkman

OpenFOAM v2512 não tem modelo `Brinkman` nativo. Usamos `fvOptions` → `explicitPorositySource` → **DarcyForchheimer** com $f=0$:

$$S = -(\mu \mathbf{d})\,\mathbf{u}, \qquad \mathbf{d} = \frac{1}{\boldsymbol{\kappa}} \;\text{(isotrópico)}$$

| Brinkman (COMSOL) | OpenFOAM | Arquivo |
|-------------------|----------|---------|
| $\mu/\kappa$ | $\mu\, d$, $d = 1/\kappa$ | `system/fvOptions` |
| $\varepsilon_p$ | documentado; termo $(\mu/\varepsilon)\nabla^2\mathbf{u}$ omitido | `porousMediaProperties` |
| $f \to 0$ (creeping) | `f = (0 0 0)` | `fvOptions` |
| $\kappa$ TM ajustada | calibrar $d_{TM}$ → IOP₀ = 15 Torr | `scripts/set_d_tm.py` |

**Critério de validade (número de Brinkman):**

$$\mathrm{Br} = \frac{\kappa}{L^2} \ll 1$$

- Vítreo: $\kappa = 5{,}8\times10^{-14}$ m², $L \sim 10$ mm → Br $\sim 10^{-9}$ → **limite Darcy adequado**.
- TM: $\kappa$ calibrada, resistência dominante → termo viscoso Brinkman secundário.

---

## 4. Fontes de massa $Q_{br}$

| Lamminsalo | OpenFOAM G1 |
|------------|-------------|
| Formação AH na porta posterior (3 mm³/min) | `flowRateInletVelocity` total ṁ = 4,97×10⁻⁸ kg/s |
| Velocidade 0,1332 mm/min (sem Petit) | equivalente hidráulico via Q (área inlet G1 ≠ Missel) |
| Sem $Q_{br}$ volumétrico no domínio | produção só na BC de inlet |

---

## 5. Pressão de saída (continuidade + BC)

| Outlet Lamminsalo | OpenFOAM |
|-------------------|----------|
| TM + esclera externa: **10 Torr** | `outlet_tm`: p_kin = 1,341 m²/s² |
| Córnea externa: **0 Torr** | N/A G1; G2 `fixedValue 0` |

---

## 6. Roadmap — o que se adota do Lamminsalo

| Fase | Solver | Física Lamminsalo adotada |
|------|--------|---------------------------|
| **Sim 1–4** (tese IVI/ACP) | `simpleFoam` / `pimpleFoam` + FSI | Brinkman→Darcy, isotérmico, Q + P outlet |
| **Não previsto** | `buoyantBoussinesq*` + `T` | Boussinesq, gravidade, Nonisothermal Flow — **apenas drug delivery no artigo original** |

Referências cruzadas: `fluid/constant/porousMediaProperties`, `fluid/constant/phaseProperties`, `simulacao_doutorado.md` §1.1, `plano_doutorado.md` §13.1.
