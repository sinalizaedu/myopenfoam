# Propriedades físicas — coelho (Lamminsalo 2018)

**Documento canônico:** [`referencias_doutorado.md`](../../../Doutorado/referencias_doutorado.md) → Lamminsalo 2018

## Política

Para espécie **coelho**, Sim 1 e G2 usam **Lamminsalo (2018)** — Tabela I (materiais) + Methods (BCs operacionais). Ruffini (2024) aplica-se apenas ao modelo humano/0D do plano.

## Tabela I — materiais

Ver `fluid/constant/phaseProperties` e `simulacao_doutorado.md` §1.1.

## Zonas porosas G1 — κ e d (`fvOptions`)

Relação Brinkman → OpenFOAM: **d = 1/κ** (isotrópico), $f = 0$.

| Zona | cellZone | **κ** [m²] | **d** [m⁻²] | Arquivo |
|------|----------|------------|-------------|---------|
| **Vítreo** | `vitreous_zone` | **5,8×10⁻¹⁴** (Tabela I ᵉᶜ) | **1,724×10¹³** | `phaseProperties` + `fvOptions` |
| **TM** | `tm_zone`, `tm_zone_left` | ajustada ᵍ | a recalibrar | `fvOptions` |

Verificação vítreo: $d = 1 / (5{,}8\times10^{-14}) = 1{,}724\times10^{13}$ m⁻².

## Lamminsalo (2018) — condições operacionais adotadas (Sim 1 G1)

| Parâmetro | Valor | Arquivo |
|-----------|-------|---------|
| T | **37 °C** | `phaseProperties` |
| ρ | **995** kg/m³ (Tabela I ᵈ @ 37 °C) | `phaseProperties` |
| **μ** | **6,89×10⁻⁴** Pa·s | `phaseProperties` |
| **ν** | **6,925×10⁻⁷** m²/s (= μ/ρ) | `transportProperties` |
| Q_prod | **3 µL/min** | `0.step0/U` |
| P_outlet TM / esclera | **10 Torr** → p_kin = 1,340 m²/s² | `0.step0/p` |
| P_córnea externa | **0 Torr** | N/A G1 (G2) |
| IOP calibração TM | **15 Torr** (faixa 10,1–20) | calibração `d_TM` |
| U_inlet (referência Missel) | 0,1332 mm/min (sem Petit) | G1 usa Q imposta |

## Lamminsalo (2018) — equações governantes

| COMSOL | OpenFOAM Sim 1 |
|--------|----------------|
| Brinkman: $-\mu\mathbf{u}/\kappa$ | `fvOptions` $d=1/\kappa$, $f=0$ |
| $\varepsilon_p$ (Tabela I) | `porousMediaProperties` |
| Boussinesq + Nonisothermal | **Não implementar** (drug delivery only) |

Ver `constant/lamminsaloGoverningEquations.md` e plano §13.1.

## Limitações G1

- Geometria-alvo **G1** = silhueta anatômica Missel/Lamminsalo 2D planar bilateral (ver `geometry_tables.md` e `figures/g1_anatomy_2d.png`). O `blockMesh` retangular antigo é **G1 legacy** (`*.blockMeshDict.legacy`).
- **G2** = futuro 2D-axisimétrico / 3D (não este caso).
- Sem canal de Petit no modelo base.
- Inlet: G1 usa Q imposta (área do inlet planar ≠ Missel 360°).

## Corrida anterior (jul/2026)

Resultados numéricos em `sim1_report.md` / `mesh_study.md` usaram a malha **retangular legacy** e BCs antigas (Q = 2,2 µL/min, P_epi = 8 mmHg). Re-calibração `d_TM` pendente na malha anatômica G1.
