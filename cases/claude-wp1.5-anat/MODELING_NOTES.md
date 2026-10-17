# MODELING_NOTES — WP1.5 Modelo Anatômico 3D

## Fase 1: Teste de pipeline (material único)

### Geometria

- **Fonte:** Lamminsalo et al. 2018 (Pharm Res), baseado em Missel 2012
- **Espécie:** coelho (rabbit). Geometria humana é tarefa futura.
- **Malha:** `eye_g2_solid_lamminsalo_M1.msh` (Gmsh 2.2), localizada em `doc-g3-sim1/geometry/`
- **Tipo de elemento:** hexaedro linear de 8 nós (Gmsh type 5 → CalculiX C3D8)
- **Nós:** 3 780 | **Elementos de volume:** 2 406 | **Elementos de superfície:** 1 884
- **Domínio:** coat only (parede externa do olho)
  - cornea: 306 hex | sclera: 840 hex | choroid: 630 hex | retina: 630 hex
- **Coordenadas:** metros (valores ~0,007–0,009 m)
- **Rótulos de nó Gmsh:** 1537–5316; o conversor renumeria para 1–3780 (CalculiX exige que o primeiro nó seja 1)
- **Orientação C3D8I:** mapa Gmsh→CCX em duas etapas + probe `ccx_preCICE` por elemento (~30 hexes usam permutação alternativa)
- **Elementos:** C3D8I (não C3D8), alinhado a `fea-sim`
- **BCs extras:** `NAXIS` (interseção SYMMETRY_0 ∩ SYMMETRY_90) e `NPOSTERIOR_POLE` (nó de maior y), padrão `fea-sim/ccx/fea-sim.inp`
- **Carga:** `*DSLOAD` com amplitude `RAMP` no step 1 (não `*DLOAD`)
- **Calotte:** 90° de revolução (1/4 do olho), com simetria nos planos θ=0° (z=0) e θ=90° (x=0)

### Material (simplificação Fase 1)

- **Justificativa:** teste de pipeline. Todas as regiões recebem o mesmo material.
- **Material:** Ogden N=1, ajuste Friedenwald (WP1.2)
  - mu1 = 2,2708 MPa, alpha1 = 1,0562, D1 = 0,2247 1/MPa
- **Fonte:** resultado do WP1.2 (ajuste da curva pressão-volume de Friedenwald)

### Condições de contorno

- **Simetria:** SYMMETRY_0 (plano z=0, DOF 3 = 0) e SYMMETRY_90 (plano x=0, DOF 1 = 0)
- **Pressão interna:** SURFACE SINNER = FSI_ACTIVE + FSI_IRIS + FSI_LENS
  - P basal = 15 mmHg = 1 999,83 Pa — fonte: plano de tese, Ensaio A WP2
  - P pico = 50 mmHg = 6 666,1 Pa — fonte: plano de tese, Ensaio B WP2
- **Análise:** `*STEP, NLGEOM`

### Limitações desta fase

- Material único (esclera) para todos os tecidos
- Malha coat-only (sem íris, ciliary, cristalino, TM como volumes)
- Sem pré-tensionamento (MULF)
- Sem lâmina cribrosa

---

## Fase 2: Multi-material e três perguntas (plano, NÃO implementar agora)

### Materiais diferenciados (precisam de referência)

| Tecido | Parâmetro | Referências |
|---|---|---|
| Córnea | E ou hiperelástico | Woo et al. 1972; Elsheikh et al. 2007; Kling & Marcos 2013 |
| Íris | E ≈ 4 kPa (plano, l.592) | buscar fonte primária |
| Cristalino | E ou hiperelástico | Fisher 1971; Weeber & van der Heijde 2007 |
| Lâmina cribrosa | E ou hiperelástico | Sigal et al. 2004, 2005; Eilaghi et al. 2010 |

### Três perguntas

1. **Colapso CA:** retirar volume da CA, monitorar ACD. Requer malha com córnea + íris + cristalino sólidos.
2. **Lâmina cribrosa:** pressão no pico → tensão e deformação na LC. Requer criar região LC no polo posterior.
3. **Sítio de injeção:** pressão no pico → tensão na pars plana (3,5 mm posterior ao limbo).
