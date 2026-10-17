# O1 solid geometry — analytic specification (CAD / geometry rebuild)

Source of truth: `brunaStuff/o1_solid_anatomy.py` (surfaces, landmarks, thicknesses)
and the header of `fluid/system/blockMeshDict.O1` (analytic surface definitions).
Nothing here is measured from a mesh.

Original data: Missel (2012) / Lamminsalo (2018) ESM Tables SI–SII, **rabbit eye**.
Table units are cm; everything below is **millimetres**. OpenFOAM dicts apply
`scale 0.001`.

## Coordinate frame

| item | convention |
|------|------------|
| `y` | optical axis, **+y = posterior**, y = 0 is the vitreous-ellipsoid centre |
| `r` | radial distance from the axis, `r = hypot(x, z)` |
| anterior | negative `y` (cornea apex at y = −8.16 mm inner) |
| model extent | 90° wedge revolved about the `y` axis |

Note: `gen_o1_solid_bmd.py` writes the wedge about `+y`, then `transformPoints
-rotate-y 90` is applied. The spec below is in the pre-rotation `(r, y)` frame.

---

## 1. Shell surfaces (the six solid tissues)

All posterior surfaces are **concentric ellipses centred at the origin**,
parameterised by the polar angle `t` (0° = posterior pole, 90° = equator):

```
r(t) = a · sin(t)
y(t) = b · cos(t)
```

| surface | a (equatorial, mm) | b (polar, mm) | meaning |
|---------|-------------------:|--------------:|---------|
| `vitreous_retina` | 8.37 | 6.90 | **inner** face of retina = fluid wall |
| retina outer | 8.47 | 7.00 | retina / choroid interface |
| choroid outer | 8.67 | 7.20 | choroid / sclera interface |
| sclera outer | **9.00** | **7.53** | outer eye surface |

### Posterior coat thickness (measured along the local outward normal)

| t (°) | position (r, y) | retina | choroid | sclera | total |
|------:|-----------------|-------:|--------:|-------:|------:|
| 0 | (0.000, 6.900) | 0.1000 | 0.2000 | 0.3300 | 0.6300 |
| 18 | (2.586, 6.562) | 0.0999 | 0.1997 | 0.3296 | 0.6292 |
| 36 | (4.920, 5.582) | 0.0996 | 0.1993 | 0.3288 | 0.6277 |
| 54 | (6.771, 4.056) | 0.0996 | 0.1992 | 0.3287 | 0.6274 |
| 72 | (7.960, 2.132) | 0.0998 | 0.1996 | 0.3295 | 0.6289 |
| 90 | (8.370, 0.000) | 0.1000 | 0.2000 | 0.3300 | 0.6300 |
| 106.85 | (8.011, −2.000) | 0.0998 | 0.1997 | 0.3295 | 0.6290 |

Nominal design values: **retina 0.10 / choroid 0.20 / sclera 0.33 mm**
(sum 0.63 mm). Because the layers are built as *semi-axis* offsets rather than
true normal offsets, the real normal thickness dips ≤ 0.4 % (≈ 2.6 µm) at
t ≈ 54°. Treat the ellipse offsets as the definition, not the 0.63 mm.

### Cornea (spherical caps, centres on the axis)

| surface | centre (r, y) | radius (mm) | apex y (mm) |
|---------|---------------|------------:|------------:|
| `cornea_inside` | (0, −0.15) | 8.01 | **−8.16** |
| cornea outer | (0, −0.23) | 8.29 | **−8.52** |

- Central corneal thickness = **0.36 mm**.
- The cornea **does** bulge past the sclera: the outer corneal apex sits
  **0.99 mm** anterior to the sclera ellipse pole (y = −7.53).
- Cornea and sclera do not share a single surface; they meet at the limbus
  (section 4).

### Ciliary body

The ciliary body has **no analytic surface of its own**. It is built as:

- **inner face**: the polyline `E → F → G → H → I` (section 4), with the
  `H → I` segment following the **hyaloid circle: centre (0, +2.95), R = 9.41**.
- **outer faces**: that polyline projected radially onto the choroid ellipse
  (8.67, 7.20) and then the sclera ellipse (9.00, 7.53).

So the ciliary body occupies the same radial band as choroid + sclera in the
anterior transition, i.e. it is capped by the same 9.00/7.53 outer surface.

### Iris (flat plate, two straight/polyline faces)

| face | from | to | mid control point |
|------|------|----|-------------------|
| posterior | P (3.00, −5.27) | G (6.92, −3.86) | (3.69, −4.81), (5.21718, −4.36083) |
| anterior | O (3.11, −5.38) | F (6.90, −4.02) | (3.78, −4.94), (6.075475, −4.26313) |

- **Pupil radius 3.00 mm** (pupil diameter 6.00 mm).
- Thickness at the pupil edge (|O−P|) = **0.156 mm**;
  at the root (|F−G|) = **0.161 mm**.
- Root-to-pupil span along the posterior line = **4.166 mm**.
- The iris is a separate body from the coat; it couples on `fsi_iris`.

---

## 2. Lens — the void to subtract

The lens is **not meshed as a solid by default**; it is an impermeable fluid
void (`lens_wall` on the fluid mesh, `fsi_lens` if `--with-lens` is used).
It is the intersection of two spherical caps, both centred on the axis:

| surface | centre (r, y) | radius (mm) | apex |
|---------|---------------|------------:|------|
| `lens_front` (anterior) | (0, −0.31) | 5.76 | M = (0, **−6.07**) |
| `lens_rear` (posterior) | (0, −4.15) | 4.79 | K = (0, **+0.64**) |

Derived dimensions:

| quantity | value |
|----------|------:|
| equator L | (r = **4.75**, y = **−3.57**) |
| equatorial diameter | **9.50 mm** |
| axial thickness (K − M) | **6.71 mm** |
| midpoint of the two apices on the axis | y = **−2.715 mm** |
| equator plane offset from that midpoint | −0.855 mm (equator is anterior of it) |

The equator L lies on both circles to within 1.1 µm (front) and 4.7 µm (rear),
so the two-cap construction closes cleanly — **do not** approximate it as one
sphere. If you must use a single sphere, note the body is strongly oblate
(9.50 mm wide × 6.71 mm thick), so a sphere is a poor substitute.

Boolean recipe: `lens = sphere(centre (0,−0.31), R 5.76) ∩ sphere(centre
(0,−4.15), R 4.79)`, then subtract from the fluid.

---

## 3. Injection sites (needles)

These live on the **fluid** side (source/sink patches), not the solid, but they
fix where the solid must not be cut.

| site | tip coordinates (mm) | compartment | cavity radius (topoSet) | physical 30 G lumen radius |
|------|----------------------|-------------|------------------------:|---------------------------:|
| **IVI** (intravitreal) | (0, **+3.000**, 0) | vitreous | 0.550 mm | 0.070 mm |
| **ACP** (anterior chamber paracentesis) | (0, **−7.000**, 0) | anterior chamber (station V) | 0.550 mm | 0.070 mm |

Both are **on the optical axis** (r = 0), Model B "patch" formulation: the tip
cell is removed and the exposed faces become the `ivi_tip` / `acp_tip` patches,
driven by a flow rate `Q(t)`. Defined in
`fluid/system/topoSetDict.iviTip` and `topoSetDict.acpTip`.

The ACP tip at y = −7.00 sits 1.16 mm behind the inner corneal apex
(−8.16), inside the anterior chamber. The IVI tip at y = +3.00 sits in the
vitreous, 3.90 mm anterior to the posterior pole (+6.90) and 2.36 mm behind
the lens rear apex (+0.64).

---

## 4. Landmark stations on the inner wall

Table SI/SII landmarks used verbatim (`stations()` in `o1_solid_anatomy.py`):

| id | (r, y) mm | anatomy |
|----|-----------|---------|
| A | (0.00, −8.16) | cornea inner apex (axis) |
| T | (3.11, −7.5316) | cornea at the iris-tip radius (derived) |
| U | (3.78, −7.2120) | cornea at the iris-turn radius (derived) |
| **B** | (6.61, −4.68) | **inner sclera–cornea junction (limbus, inner)** |
| C | (6.70, −4.75) | TM / cornea void |
| `lim_out` | (6.87, −4.87) | anatomic outer limbus |
| D | (6.93, −4.49) | TM / ciliary void |
| E | (6.84, −4.42) | ciliary–TM–aqueous–sclera meeting point |
| F | (6.90, −4.02) | iris–ciliary, anterior |
| G | (6.92, −3.86) | iris–ciliary, posterior |
| H | (7.00, −3.35) | ciliary tip (hyaloid curved→flat) |
| **I** | (8.01, −2.00) | **ora serrata** — on the vitreous ellipse *and* the hyaloid circle (11.6° tangent kink) |
| J | (0.00, +6.90) | posterior pole (axis) |
| K | (0.00, +0.64) | lens rear apex (axis) |
| L | (4.75, −3.57) | lens equator |
| M | (0.00, −6.07) | lens front apex (axis) |
| N | (3.78, −4.94) | iris turn, anterior |
| O | (3.11, −5.38) | iris tip, anterior |
| P | (3.00, −5.27) | iris tip, posterior |
| Q | (3.69, −4.81) | iris turn, posterior |
| V | (0.00, −7.00) | axis station = **ACP needle site** |
| V2 | (0.00, −7.60) | axis station |

Auxiliary derived points used to keep blocks convex (not anatomy):
`R (3.00, −5.2270723)`, `Z (6.075475, −4.26313)`, `Y (5.21718, −4.36082941)`.

### Limbus region, plainly

The cornea–sclera junction is the short chain **B → C → D → E** at
r ≈ 6.6–6.9 mm, y ≈ −4.4 to −4.8 mm. There is no single "limbus radius": the
cornea inner circle ends at B, the trabecular meshwork occupies B–C–D, and the
sclera/ciliary take over at E. The outer surface transitions from the corneal
circle (R 8.29 about y = −0.23) to the sclera ellipse (9.00, 7.53) across the
same band.

### Iris–lens clearance (for reference)

With the iris posterior face straight and the lens front spherical:

```
gap(r) = 6.96 − 0.66667·r − sqrt(33.1776 − r²)     [mm]
```

| r (mm) | gap |
|-------:|-----|
| 3.000 | 42.93 µm (pupil tip P) |
| 3.195 | **37.34 µm (minimum)** |
| 3.690 | 77.16 µm (turn Q) |

---

## 5. Quick summary of what you asked for

| question | answer |
|----------|--------|
| Sclera outer radius | ellipse **9.00 mm** equatorial / **7.53 mm** polar |
| Sclera inner radius | ellipse 8.67 / 7.20 (= choroid outer) |
| Sclera thickness | **0.33 mm** |
| Cornea outer radius | sphere **R 8.29**, centre (0, −0.23) |
| Cornea inner radius | sphere **R 8.01**, centre (0, −0.15) |
| Cornea thickness | **0.36 mm** |
| Cornea bulge past sclera | **0.99 mm** at the apex |
| Retina | 8.37/6.90 → 8.47/7.00, **0.10 mm** |
| Choroid | 8.47/7.00 → 8.67/7.20, **0.20 mm** |
| Ciliary body | polyline E→F→G→H→I, outer = choroid+sclera ellipses |
| Iris | plate, pupil radius **3.00 mm**, thickness **0.156–0.161 mm** |
| Lens equatorial diameter | **9.50 mm** |
| Lens axial thickness | **6.71 mm** |
| Lens centre on axis | apex midpoint y = **−2.715 mm**; equator plane at y = −3.57 mm |
| IVI needle tip | (0, **+3.00**, 0) mm, vitreous |
| ACP needle tip | (0, **−7.00**, 0) mm, anterior chamber |
| Needle cavity / lumen radius | 0.550 mm (mesh cavity) / 0.070 mm (30 G physical) |
| Limbus | B (6.61, −4.68) inner → `lim_out` (6.87, −4.87) |
| Ora serrata | I (8.01, −2.00) |

---

## 6. Reproducing these numbers

Run from the repository root (`brunaStuff` is a directory of scripts, not a
package, so it goes on `sys.path`):

```bash
python3 - <<'PY'
import sys; sys.path.insert(0, "brunaStuff")
from o1_solid_anatomy import (
    RETINA_AB, CHOROID_AB, SCLERA_AB, VITREOUS_AB,
    CORNEA_INNER, CORNEA_OUTER, HYALOID,
    T_RETINA, T_CHOROID, T_SCLERA, T_CORNEA, stations,
)
print(VITREOUS_AB, RETINA_AB, CHOROID_AB, SCLERA_AB)
print(CORNEA_INNER, CORNEA_OUTER, HYALOID)
print(T_RETINA, T_CHOROID, T_SCLERA, T_CORNEA)
for name, p in stations().items():
    print(f"{name:8s} r={p.r:7.4f}  y={p.y:8.4f}")
PY
```

Lens circles are hard-coded in `gen_o1_solid_bmd.py::add_lens_butterfly`
(`_con_circle(-0.31, 5.76, ...)` front, `_con_circle(-4.15, 4.79, ...)` rear)
and documented in the `blockMeshDict.O1` header.
