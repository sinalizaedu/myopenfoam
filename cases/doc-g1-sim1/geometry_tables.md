# G1 geometry tables (Missel / Lamminsalo ESM)

Source: Lamminsalo et al. Pharm Res 2018 electronic supplementary Tables SI–SII,
from Missel 2012. Units in tables: **cm**. OpenFOAM uses **metres** via
`x = X·10⁻²`, `y = Z·10⁻²`, slab `z ∈ [0, 10⁻³]` with `empty` front/back.

## Nomenclature

- **G1** = anatomical 2D planar bilateral (Missel/Lamminsalo).
- **Sim 1 fluid domain** = **AC + vitreous + TM only** (no sclera/choroid/retina/cornea stroma).
- **G2** = right-half revolved 90° calotte (`doc-g2-sim1`, `gen_lamminsalo_g2.py`).

## Table SI (selected)

| Surface | R1 [cm] | R2 [cm] | X-cent | Z-cent |
|---------|---------|---------|--------|--------|
| Outer sclera | 0.900 | 0.753 | 0 | 0 |
| Choroid–sclera | 0.867 | 0.720 | 0 | 0 |
| Retina–choroid | 0.847 | 0.700 | 0 | 0 |
| Vitreous–retina | 0.837 | 0.690 | 0 | 0 |
| Lens rear | 0.479 | — | 0 | −0.415 |
| Lens front | 0.576 | — | 0 | −0.031 |
| Cornea outside | 0.829 | — | 0 | −0.023 |
| Cornea inside | 0.801 | — | 0 | −0.015 |

## Key intersections (cm)

| Point | X | Z |
|-------|---|---|
| `lens_eq_hyaloid` | 0.475 | -0.357 |
| `hyaloid_curved_flat` | 0.7 | -0.335 |
| `hyaloid_retina` | 0.801 | -0.2 |
| `outer_sclera_cornea` | 0.687 | -0.487 |
| `inner_sclera_cornea` | 0.661 | -0.468 |
| `ciliary_tm_aqueous_sclera` | 0.684 | -0.442 |
| `iris_ciliary_post` | 0.692 | -0.386 |
| `iris_ciliary_ant` | 0.69 | -0.402 |
| `iris_turn_post` | 0.369 | -0.481 |
| `iris_turn_ant` | 0.378 | -0.494 |
| `iris_tip_post` | 0.3 | -0.527 |
| `iris_tip_ant` | 0.311 | -0.538 |
| `tm_cornea_void` | 0.67 | -0.475 |
| `tm_ciliary_void` | 0.693 | -0.449 |

## Model choices (G1)

- No canal of Petit (base model).
- **Iris = Table SII polyline** (cil → turn/dobra → tip), not a spline/curve.
- Iris–lens gap ≥ 30 µm at Table SII tip corners (tips not shifted).
- Bilateral mirror about the optical axis (`x = 0`).

## Generated artefacts

- `geometry/eye_g1_lamminsalo.geo` — Gmsh outline stub
- `geometry/eye_g1_lamminsalo.msh` — volume mesh (if `--mesh`)
- `figures/g1_anatomy_2d.png` — labelled geometry print
