# G2 geometry tables (Missel / Lamminsalo ESM)

Same SI–SII tables as G1. Units in tables: **cm**. OpenFOAM uses **metres**.

## Nomenclature

- **G1** = anatomical 2D planar bilateral (empty slab in z).
- **G2** = G1 **right-half** meridional fluid silhouette, **revolved 90°**
  about the optical axis (`+y`) → 3D quarter-calotte.
- Two planar cut faces = **symmetry** patches; **4 × 90° = 360°** of the eye.
- **Sim 1 fluid domain** = AC + vitreous + TM only (lens / iris are holes).

## Construction

1. Build right-half rings in the plane `z = 0`, `x ≥ 0` (same curves as G1).
2. Fuse AC ∪ vitreous, cut iris hole.
3. `OCC revolve` about `(0,1,0)` by `90°`.
4. Physical patches:
   - `symmetry_0` — original meridional plane (`z = 0`)
   - `symmetry_90` — revolved plane (`x = 0`, `z ≥ 0`)
   - `ac_inlet`, `outlet_tm`, `lens_wall`, `iris_wall`, `wall`

## Coordinate map

| Missel | OpenFOAM G2 |
|--------|-------------|
| X (radial) | `x = X·10⁻²` (half-plane, then revolved) |
| Z (optical) | `y = Z·10⁻²` (**revolve axis**) |
| — | `z` from revolution |

## Model choices (shared with G1)

- No canal of Petit.
- Iris = Table SII polyline; iris–lens gap ≥ 30 µm.
- Single-sided TM / inlet (no left mirrors).

## Generated artefacts

- `geometry/eye_g2_lamminsalo.{geo,msh,vtk}`
- `figures/g2_half_meridional.png`
- `figures/g2_calotte_3d.png`
