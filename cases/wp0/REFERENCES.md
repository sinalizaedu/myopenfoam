# WP0 — parameter references

Audit labels: **(verified, DOI)** | **(estimate, replace before publish)** | **(derived, not measured)**

## Verified (high confidence)

| parameter | value | source |
|---|---|---|
| human trabecular facility $C_{\text{out}}$ | ~0.28 µL/min/mmHg | Goel M et al. *Open Ophthalmol J* 2010;4:52–59 |
| aqueous production | ~2.4–3.0 µL/min (circadian) | Goel et al. 2010 |
| human episcleral pressure | ~8–10 mmHg | Goel et al. 2010 |
| Goldmann equation | IOP = EVP + (Q−U)/C | Goldmann H. *Ophthalmologica* 1951 (classic; secondary sources) |
| Friedenwald law | log₁₀(P) = log₁₀(P₀) + Kf(V−V₀) | Friedenwald JS. *Am J Ophthalmol* 1937;20:985–1024 (classic) |

## Estimates / not verified — do not cite as measured

| parameter | value | note |
|---|---|---|
| $E_{\text{sclera,human}}$ | 3.0 MPa | order-of-magnitude; check Elsheikh inflation data or WP2 |
| $E_{\text{sclera,rabbit}}$ | 2.54 MPa in old B2 files | may be **human** Karimi et al., not rabbit — verify `mechanicalProperties` |
| Friedenwald $K_f$ range | 0.0126–0.0221 µL⁻¹ | confirm primary tonography source before thesis citation |
| rabbit $C_{\text{out}}$ | ~0.57 µL/min/mmHg | **(derived)** from Q_prod and 5 % uveoscleral fraction, not direct measurement |

## Species — uveoscleral fraction

| species | fraction | confidence |
|---|---|---|
| human | ~15–25 % (default 20 %) | literature, method-dependent |
| rabbit | ~3–8 % (code uses 5 %) | Toris/Pederson reviews |
| pig | unknown | **measure in WP2** |

Using human fraction (20 %) in a rabbit scenario was a real bug in an earlier
version; corrected in `goldmann_iop_solver.py`.
