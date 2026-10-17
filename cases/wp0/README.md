# wp0 — 0D Goldmann IOP solver (post-IVI)

Purely numerical case: no FEA, no OpenFOAM. Solves the volume-balance ODE from
the thesis plan (Section 0) and returns IOP(t), ocular perfusion pressure MOPP(t),
and ischemic dose. **v0.1 — not validated for clinical use.**

```bash
# host (needs numpy, scipy, matplotlib)
cd cases/wp0 && ./Allrun

# or inside the FSI container (Python deps already installed)
docker compose run --rm fsi bash -lc 'cd /simulation/wp0 && ./Allrun'
```

**Tempo:** `t=0` is the **start of the IVI** (6 s ramp). Paracentesis labels
“−30 s”, “+30 s”, and “+2 min” are measured from that same origin (profilactic
ends before injection starts; see `verify_wp0_standards.py`).

Outputs land in `output_wp0/`:

| file | content |
|---|---|
| `figures/fig_*.png` | figures aligned with `brunaStuff/latex/report/wp0.tex` |
| `report_metrics.json` | simulated result scalars vs wp0.tex (informational; reconcile later) |
| `verify_wp0_standards.json` | **inputs + methodology** checks (CI gate) |

Entry point for the **thesis report**: `wp0_report.py` (called by `./Allrun`).
Legacy demo plots from `goldmann_iop_solver.py` main are **not** the report protocol.

## Model

$$\frac{dV}{dt} = Q_{\text{prod}} + Q_{\text{ivi}}(t) - C_{\text{out}}(P-P_{\text{ev}}) - Q_{\text{uv}} - Q_{\text{reflux}} - Q_{\text{par}}$$

with $P = P(V)$ from a swappable stiffness curve:

| piece | code | thesis |
|---|---|---|
| linear thin shell $P(V)$ | `ThinShellPV` | WP1.1 verification |
| Friedenwald exponential $P(V)$ | `FriedenwaldPV` | H2 |
| full ODE | `_rhs`, `simulate` | Section 0 |
| perfusion + ischemic dose | `perfusion_metrics`, `ischemic_dose_curve` | WP4 |
| paracentesis volume for target IOP | `volume_para_alvo` | WP5.3 |
| $K$ from axial length | `K_de_biometria` | H1, WP6 |
| pressure-dependent outflow (hook) | `Protocol.C_of_P` | WP7 |

Programmatic use: import from `goldmann_iop_solver.py` — see `Protocol`,
`simulate`, `FriedenwaldPV`, `ThinShellPV`.

## Warnings (read before reporting numbers)

1. **Friedenwald is exponential — peak IOP is very sensitive to $K_f$.**
   Default uses the lower literature bound ($K_f=0.0126\ \mu\text{L}^{-1}$).
   Always state which $K_f$ was used.

2. **`volume_para_alvo` uses the same $P(V)$ curve as the simulation** — do not
   mix a different $K$ for paracentesis estimates (thesis §5.3).

3. **`OPP_crit` is uncertain.** Report ischemic dose vs threshold via
   `ischemic_dose_curve`, not as a single fixed number (WP4.2).

4. **Species-specific uveoscleral fraction:** human ~20 %; rabbit ~5 % (not 20 %).
   Swine: measure in WP2 — do not assume rabbit values.

## Swapping $P(V)$ for measured data

Implement a class with `P`, `dPdV`, `V_of_P` (e.g. `scipy.interpolate.CubicSpline`
on inflation data from WP1 FEA or WP2 ex vivo) and pass it to `simulate(...)`.
The ODE, reflux, paracentesis, and perfusion code stay unchanged.

## Parameter provenance

See `REFERENCES.md` for verified citations vs order-of-magnitude estimates.
Label every `Protocol` parameter as **(verified, DOI)**, **(estimate)**, or
**(derived, not measured)** before publishing.

## Next step (not in this case)

Notebook or single-page web UI with inputs (axial length, volume, paracentesis
yes/no/when) and output plots — `Protocol` in, `simulate` + `perfusion_metrics` out.
