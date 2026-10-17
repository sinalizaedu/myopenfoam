# Mesh independence — baseline O1 / O2 / O3

Structured `blockMesh` G2-fluid quarter eye. Division scaling relative to O1:
**O2 = 0.7×** (coarser), **O1 = 1.0×** (design), **O3 = 1.3×** (finer).
Steady `simpleFoam`, IOP target 15 mmHg via `d_TM` calibration.

## Model B (patch tips)

| Mesh | factor | cells | IOP AC (mmHg) | IOP vit (mmHg) | ΔAC–vit | Q_TM (m³/s) | Q err % | Umax (m/s) | iters | status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| O2 | 0.7 | 17624 | 15.89 | 15.9 | 0.0106 | 1.25e-11 | 0 | 0.0001316 | 250 | OK |
| O1 | 1.0 | 53532 | 15.2 | 15.21 | 0.00916 | 1.25e-11 | 0 | 0.0001295 | 834 | OK |
| O3 | 1.3 | 120208 | 14.9 | 14.91 | 0.00978 | 1.25e-11 | 0 | 0.0001307 | 1000 | OK |

### IOP change vs previous mesh (O2 → O1 → O3)

- **O2 → O1** AC IOP: 15.89 → 15.2 mmHg (-4.37 %)
- **O2 → O1** vitreous IOP: 15.9 → 15.21 mmHg (-4.38 %)
- **O1 → O3** AC IOP: 15.2 → 14.9 mmHg (-1.99 %)
- **O1 → O3** vitreous IOP: 15.21 → 14.91 mmHg (-1.99 %)

**Bracket O1↔O3 (AC IOP):** -1.99 % — **PASS (<2 %)** — accepted for production

## Model C (volume tips)

| Mesh | factor | cells | IOP AC (mmHg) | IOP vit (mmHg) | ΔAC–vit | Q_TM (m³/s) | Q err % | Umax (m/s) | iters | status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| O2 | 0.7 | 17984 | 15.89 | 15.9 | 0.0106 | 1.25e-11 | 0 | 0.0001316 | 252 | OK |
| O1 | 1.0 | 54672 | 15.2 | 15.21 | 0.00909 | 1.25e-11 | 0 | 0.0001295 | 794 | OK |
| O3 | 1.3 | 122752 | 14.9 | 14.91 | 0.00979 | 1.25e-11 | 0 | 0.0001312 | 1000 | OK |

### IOP change vs previous mesh (O2 → O1 → O3)

- **O2 → O1** AC IOP: 15.89 → 15.2 mmHg (-4.37 %)
- **O2 → O1** vitreous IOP: 15.9 → 15.21 mmHg (-4.38 %)
- **O1 → O3** AC IOP: 15.2 → 14.9 mmHg (-1.99 %)
- **O1 → O3** vitreous IOP: 15.21 → 14.91 mmHg (-1.99 %)

**Bracket O1↔O3 (AC IOP):** -1.99 % — **PASS (<2 %)** — accepted for production

## Decision

Fixed physical parameters across all meshes (`d_TM`, `d_vit`, BCs, `Q_TM`).
IOP decreases monotonically with refinement (O2 15.89 → O1 15.20 → O3 14.90 mmHg)
for both patch and volume tip models.

- **O2** rejected (coarse bracket; −4.4 % vs O1).
- **O1↔O3 bracket:** −1.99 % on AC IOP (patch and volume) — **accepted**.
- **Production mesh:** **O1** (`blockMesh`, ~54k cells).
- **Discretization uncertainty:** **15.2 ± 0.3 mmHg** (half the O1↔O3 bracket).

O3 reached `endTime = 1000`; late-step residuals were below tolerance and IOP
was stationary to the reported precision.

