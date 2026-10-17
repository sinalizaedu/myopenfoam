# fea-simplf — spherical sclera + cornea (CalculiX)

90° spherical shell with B2 inner/outer radii, two Neo-Hooke tissues.
Living IOP = **15 mmHg**. Extra volume inverted at 50 µL. Goldmann TM drain
is a 0D ODE on the FEA \(P(V)\) curve (rabbit \(C=0.48\) µL/min/mmHg,
\(\tau\approx 5.5\) min, \(P(\infty)=15\) mmHg).

```bash
docker compose run --rm fsi bash -lc 'cd /simulation/fea-simplf && ./Allrun'
```

| | inner | outer |
|---|---|---|
| sclera | 8.67 mm | 9.00 mm |
| cornea | 8.16 mm | 8.52 mm |

Limbus at 54.7° from the anterior pole. 5° polar holes, `C3D8I`.
Posterior ring: \(U_y=0\) only (radial expansion free). Units SI (m, Pa).
