# OpenFOAM FSI Docker Environment

Dockerised environment for Fluid-Structure Interaction simulations using
OpenFOAM, preCICE, solids4foam, and CalculiX — built for Apple Silicon Macs.

## Software Versions

| Component                | Version             | Notes                                         |
| ------------------------ | ------------------- | --------------------------------------------- |
| Ubuntu                   | 24.04 LTS           | Base image                                    |
| OpenFOAM                 | v2512 (ESI/OpenCFD) | Released Dec 2025                             |
| preCICE                  | 3.3.1               | Built from source                             |
| OpenFOAM-preCICE adapter | 1.3.1               | Compiled against v2512                        |
| solids4foam              | master (v2.3+)      | Compiled against v2512                        |
| CalculiX (ccx_preCICE)   | 2.20                | Built with preCICE adapter v2.20.1            |
| Python                   | 3.12                | With numpy, scipy, matplotlib                 |

### Why CalculiX 2.20 instead of the latest 2.23

CalculiX itself is at v2.23, but the **CalculiX-preCICE adapter** (latest
release v2.20.1, March 2024) only supports CalculiX 2.20. The adapter
directly patches CalculiX source code to produce the `ccx_preCICE` binary,
so the versions must match exactly.

Since this image is FSI-focused (CalculiX coupled to OpenFOAM via preCICE),
v2.20 is the correct choice. Standalone CalculiX 2.23 would give newer
features but no preCICE coupling.

CalculiX 2.20 source is downloaded from dhondt.de, then the adapter at
tag `v2.20.1` is built against our source-built preCICE 3.3.1, producing
the `ccx_preCICE` binary used for FSI runs. SPOOLES and ARPACK come from
Ubuntu apt packages.

## Architecture

Runs as `linux/amd64` via Rosetta 2 on Apple Silicon (tested on M5).
No native arm64 OpenFOAM apt packages exist. Expect ~30-40% performance
overhead vs native x86 — fine for development, use an x86 server for
production runs.

## Project Structure

```
myopenfoam/
├── Dockerfile              # Multi-stage build
├── docker-compose.yaml     # Container config + volume mounts
├── README.md
├── cases/                  # Simulation cases (mounted at /simulation)
│   └── validation/         # Stack validation case
│       ├── Allrun
│       ├── Allclean
│       ├── fluid/          # Lid-driven cavity (pimpleFoam)
│       │   ├── 0/          # Initial conditions (U, p)
│       │   ├── constant/   # transportProperties, turbulenceProperties
│       │   └── system/     # controlDict, fvSchemes, fvSolution, blockMeshDict
│       └── solid/          # Cantilever beam (solids4Foam)
│           ├── 0/          # Initial conditions (D)
│           ├── constant/   # mechanicalProperties, solidProperties, g
│           └── system/     # controlDict, fvSchemes, fvSolution, blockMeshDict
└── openfoam-filesv1/       # preCICE FSI templates (for coupled cases)
    ├── precice-config.xml
    ├── fluid-preciceDict
    ├── solid-preciceDict
    ├── solid-interface-BC-snippet
    ├── controlDict-functions-snippet
    └── FSI-GUIDE.md
```

## Master's thesis cases (`cases/artigo_mestrado/on-*`)

Beyond the generic `validation/` case, this repository hosts the simulation
campaign for Bruna's master's thesis on **CFD/FEA modelling of the optic nerve
under CSF pressure** in normal and SANS (Spaceflight-Associated Neuro-ocular
Syndrome) conditions. Full technical details are in
[`brunaStuff/artigo_mestrado/relatorio_sans.tex`](brunaStuff/artigo_mestrado/relatorio_sans.tex).

| Case | Solver(s) | SAS model | Drainage | Scenario | Notes |
| --- | --- | --- | --- | --- | --- |
| `on-mestrado-1` | solids4foam | solid (lumped) | none | 1g | 5 zones, FEA baseline |
| `on-mestrado-2` | solids4foam | solid (anatomical) | none | 1g | 8 zones, FEA |
| `on-mestrado-3` | solids4foam | solid (anatomical) | none | SANS upper | 8 zones, FEA, P_CSF=3800 Pa |
| `on-fsi-2` | solids4foam + pimpleFluid | fluid (FSI cul-de-sac) | none | 1g | 7 zones, two-way FSI via preCICE |
| `on-fsi-3` | solids4foam + pimpleFluid | fluid (FSI cul-de-sac) | none | SANS upper | as fsi-2, P_CSF=3800 Pa |
| `on-caso-1` | solids4foam + pimpleFluid | fluid (FSI) | porous lid (Darcy) | 1g | 7 zones + outlet, **selective decoupling** |
| `on-caso-1.2` | **CalculiX** + pimpleFluid | fluid (FSI) | porous lid (Darcy) | 1g | as caso-1 but ccx_preCICE on the solid side |

### Architecture of `on-caso-1` and `on-caso-1.2`

These two cases share the same fluid topology (SAS regular + porous lid drain
modelled as Darcy-Forchheimer in `peri_porous`) and the same solid topology
(7 anatomical zones), differing only in the solid solver. They implement the
**Selective Decoupling Trick** to avoid added-mass instability at the
CSF-sclera interface:

- **FSI active** on `fsi_pia` and `fsi_dura` only (radial sheath patches in
  z=[0, 30] mm). The fluid sends Forces, the solid sends Displacements.
- **Static equivalent load** on the inner sclera faces (`fsi_sclera_peri` and
  `fsi_sclera_ring`): a constant pressure of 1333 Pa (= P_CSF baseline) is
  applied via `solidTraction` (solids4foam) or `*DLOAD` (CalculiX) instead
  of dynamic FSI coupling. Geometric continuity of the FEM mesh propagates
  the load coherently to `lc`, `globo`, `dura_outer` (Winkler 200 kPa/m,
  orbital fat), `contact_local` (9034 Pa, ophthalmic artery), etc.
- **Free outlet** at `outlet_peri` (z=30.5 mm, p=0): CSF leaves the domain
  through the porous lid without imposing tear-like stresses on the
  peripapillary sclera.

The CalculiX deck for `on-caso-1.2` is generated automatically by
`brunaStuff/gen_on_caso_1_2_ccx_inp.py` (mesh + NSETs in `all.msh` and
`all.nam`, included by `solid/main.inp`). The native `.frd` output is
converted to ParaView format (`.pvd` + `.vtu`) automatically by `Allrun`
via `ccx2paraview`.

#### `solids4foam` `pimpleFluid` + `fvOptions` patch (Darcy fix)

Upstream `solids4foam` v2512/ESI ships with `pimpleFluid.esi.C` lines that
explicitly disable `fvOptions` integration (commented as
`// fvOptions not implemented yet`). This means **any
`explicitPorositySource` in `system/fvOptions` is silently ignored** -
flow ignores the Darcy coefficient `d` regardless of value.

The Dockerfile applies an in-tree patch to `pimpleFluid.esi.C` before
`Allwmake`: it `#include`s `fvOptions.H`, instantiates
`fv::options& fvOptions = fv::options::New(mesh)` inside `evolve()`, adds
`== fvOptions(U)` to the `tUEqn` momentum source (matching canonical
`pimpleFoam/UEqn.H`), and uncomments `fvOptions.constrain(UEqn)` plus
`fvOptions.correct(U)`. The patched `libsolids4FoamModels.so` is then
bind-mounted into running containers via `docker-compose.yaml` (mount
target `/opt/of-user/lib/libsolids4FoamModels.so`, source
`./cases/_lib/libsolids4FoamModels.so`).

Validation - sweep on `on-caso-1.2` (saved in
`cases/on-caso-1.2/_sweep/d{1e13,1e15,1e17}/`):

| `d` (m^-2) | `\|U\|`_pp_max | Q_drainage (m³/s) | Regime |
| --- | --- | --- | --- |
| 1e13 | 1.19e-4 m/s | 9.96e-10 | open microdrainage |
| 1e15 | 1.19e-6 m/s | 9.96e-12 | healthy (~physiologic) |
| 1e17 | 1.19e-8 m/s | 9.96e-14 | **IIH/SANS-like (compartmentalized)** |

Pure Darcy scaling (100x change in `d` -> 100x change in flow). This sweep
used the **earlier Δp-anchored configuration** (both `inlet` p=1333 Pa and
`outlet_peri` p=0 `fixedValue`), where the total `dp` stays anchored, so
compartmentalization manifested as **reduced drainage flow** (Q -> 0 as
d -> infinity) rather than as elevated ICP. The live case has since moved to
the ICP-driven ramp described below (dura expansion); the `_sweep/` results
remain as the flow-compartmentalization reference.

#### ICP-driven **full 2-way FSI** with dura expansion (default `on-caso-1.2`)

The live `on-caso-1.2` now runs the **complete two-way FSI in ICP-driven mode**:
the inlet pressure (chiasmatic cistern) is **ramped from 1333 Pa (healthy) to
3800 Pa (SANS) over 6 coupling windows** (`fluid/0/p` `uniformFixedValue table`),
while the distal lid Darcy coefficient is set to the **compartmentalized
regime `d = 1e16`** so almost nothing drains. CSF therefore accumulates in the
perineural SAS, **distending the dura outward and compressing the optic nerve
(pia) inward** - the hallmark optic nerve sheath distension of SANS/IIH on MRI.

The ramp (small load increments per window) is what makes the Neo-Hookean
CalculiX Newton-Raphson converge: all 6 windows converge in 5-13 IQN-ILS
iterations (`time-windows-reused = 3` accelerates windows 2-6). This resolves
the divergence previously seen when the full SANS load was applied in a single
window. Radial displacement at z=30 mm, θ=0 (watchpoints `duraPeripapilar`
r=2.35 and `tampaPeripapilar` r=1.55):

| PIC (Pa) | dura `U_r` (µm) | pia `U_r` (µm) |
| --- | --- | --- |
| 1333 (healthy) | −0.281 (inward) | −0.604 |
| 3800 (SANS) | **+0.242 (outward)** | −0.933 |

Net over the ramp: dura **+0.52 µm outward** (sheath distension), pia
**−0.33 µm inward** (nerve compression). Even θ=0 sits directly under the
ophthalmic-artery sector (9034 Pa inward static load), so the off-artery
expansion is larger. Figure: `brunaStuff/figs/on-caso-1.2-dura-expansion.png`
(`python3 brunaStuff/plot_caso_1_2_dura_expansion.py`).

#### Auxiliary fluid-only ICP map (`on-caso-1.2-fluidonly`)

To map compartmentalization as elevated ICP purely on the fluid side, the
auxiliary case `cases/on-caso-1.2-fluidonly/` runs the same fluid mesh under
`flowRateInletVelocity` BC at the inlet (Q = 3e-11 m³/s prescribed) and
`zeroGradient` p, with `outlet_peri` p=0 as venous reference, using standalone
`pimpleFoam` (no preCICE/CalculiX).

| `d` (m^-2) | ICP_bulk (Pa) | Δp_lid (Pa) | Regime |
| --- | --- | --- | --- |
| 1e12 | -330 | -85 | lid wide open (Bernoulli transient) |
| 1e13 | -317 | -81 | lid wide open |
| 1e14 | -188 | -36 | barely permeable (no compartmentalization) |
| 1e15 | **1106** | 410 | **healthy (~P_CSF baseline 1333 Pa)** |
| 1e16 | **14039** | 4871 | **IIH/SANS severe (~105 mmHg)** |

A single decade of `d` (1e15 -> 1e16) drives ICP from physiologic to severe
intracranial hypertension - matching the clinical SANS hypothesis that
small changes in arachnoid villi permeability cause large ICP elevations.

To validate compartmentalization on a fresh checkout:

```bash
# Q-driven (FSI on-caso-1.2): show flow scales 100x with d
python3 brunaStuff/check_compartmentalization.py cases/on-caso-1.2
python3 brunaStuff/check_velocity.py cases/on-caso-1.2
python3 brunaStuff/sweep_d_table.py     # requires _sweep/ to exist

# ICP-driven (fluid-only on-caso-1.2-fluidonly): show ICP rises with d
python3 brunaStuff/sweep_icp_driven.py
# Figure: brunaStuff/figs/on-caso-1.2-icp-driven.png
```

## Quick Start

### 1. Build the image

```bash
docker compose build
```

First build takes 40-75 minutes (compiles preCICE, OpenFOAM adapter,
solids4foam, and CalculiX with its preCICE adapter). Subsequent rebuilds
use cached layers.

### 2. Verify the installation

```bash
docker compose run --rm fsi bash -lc '
echo "OpenFOAM: $WM_PROJECT_VERSION"
which pimpleFoam && echo "pimpleFoam: OK"
which solids4Foam && echo "solids4Foam: OK"
which ccx_preCICE && echo "ccx_preCICE: OK"
ls /opt/precice/lib/libprecice.so && echo "preCICE: OK"
ls /opt/of-user/lib/libpreciceAdapterFunctionObject.so && echo "OF adapter: OK"
ccx_preCICE -v 2>&1 | head -1
'
```

### 3. Run the validation case

```bash
docker compose run --rm fsi bash -l

# Inside the container:
cd /simulation/validation
chmod +x Allrun Allclean
./Allrun
```

Expected output: fluid writes timesteps 0.1-0.5, solid writes 0.1-1.0.

### 4. Visualise results

Install ParaView on your Mac ([https://www.paraview.org/download/](https://www.paraview.org/download/)) and open:

- `cases/validation/fluid/case.foam` — select `U` field to see cavity vortex
- `cases/validation/solid/case.foam` — select `D` field to see beam deflection

The `case.foam` files are empty markers that tell ParaView to read the
OpenFOAM directory structure. Results are visible on your Mac because the
`cases/` folder is a shared volume mount.

For CalculiX results, open the `.frd` output files directly in ParaView
(or use CGX on the host for CalculiX-native visualisation).

### 5. Clean results

```bash
# Inside container:
cd /simulation/validation
./Allclean
```

## Running Simulations

### Interactive shell

```bash
docker compose run --rm fsi bash -l
```

Always use `bash -l` (login shell) so OpenFOAM is sourced automatically.

### Run a specific case

```bash
docker compose run --rm fsi bash -lc "cd /simulation/myCase && ./Allrun"
```

### Two-terminal workflow (for coupled FSI via preCICE)

```bash
# Terminal 1 — start container and run fluid
docker compose run --rm --name fsi-run fsi bash -l
cd /simulation/myFSICase
(cd fluid && blockMesh) && (cd solid && blockMesh)
cd fluid && pimpleFoam

# Terminal 2 — attach and run solid (solids4foam OR CalculiX)
docker exec -it fsi-run bash -l
cd /simulation/myFSICase/solid && solids4Foam
# OR for CalculiX-based FSI:
# cd /simulation/myFSICase/solid && ccx_preCICE -i case -precice-participant Solid
```

Both solvers run simultaneously. preCICE handles the data exchange — the
fluid waits for displacement from the solid, the solid waits for forces
from the fluid. You will see convergence info printed each time window.

## Choosing a Solid Solver

You have two options for the solid side of FSI:

| Solver        | When to use                                                        |
| ------------- | ------------------------------------------------------------------ |
| `solids4Foam` | Native OpenFOAM workflow, shared mesh format, integrated dicts     |
| `ccx_preCICE` | ABAQUS-style input decks, broader material/element library, FEA   |

Both couple to OpenFOAM (pimpleFoam) via preCICE — pick based on which
input format and solver capabilities suit your problem.

## Creating a Coupled FSI Case

For 2-way FSI with preCICE, add these files on top of standard OpenFOAM cases.
Templates are in `openfoam-filesv1/`.

### Required layout (solids4foam variant)

```
myFSICase/
├── precice-config.xml          # coupling config (top level)
├── Allrun
├── Allclean
├── fluid/
│   ├── 0/                      # U, p
│   ├── constant/               # transportProperties, turbulenceProperties
│   └── system/
│       ├── blockMeshDict
│       ├── controlDict         # must include preCICE function object
│       ├── fvSchemes
│       ├── fvSolution
│       └── preciceDict         # adapter config
└── solid/
    ├── 0/                      # D with solidForce BC on interface
    ├── constant/               # mechanicalProperties, solidProperties, g
    └── system/
        ├── blockMeshDict
        ├── controlDict         # must include preCICE function object
        ├── fvSchemes
        ├── fvSolution
        └── preciceDict         # adapter config
```

### Required layout (CalculiX variant)

```
myFSICase/
├── precice-config.xml          # coupling config (top level)
├── Allrun
├── Allclean
├── fluid/                      # same as above
└── solid/
    ├── case.inp                # CalculiX ABAQUS-style input deck
    └── precice-config.yml      # CalculiX adapter config (YAML)
```

Run the CalculiX side with:
```bash
ccx_preCICE -i case -precice-participant Solid
```

### Key preCICE files

**precice-config.xml** — defines participants, data exchange, mapping, and
coupling scheme. See template in `openfoam-filesv1/precice-config.xml`.

**fluid/system/preciceDict:**

```
preciceConfig   "../precice-config.xml";
participant     Fluid;
modules         (FSI);
interfaces
{
    Interface1
    {
        mesh        Fluid-Mesh;
        patches     (interface);       // your coupling patch name
        locations   faceCenters;
        readData    (Displacement);
        writeData   (Force);
    }
}
```

**solid/system/preciceDict** (solids4foam):

```
preciceConfig   "../precice-config.xml";
participant     Solid;
modules         (FSI);
interfaces
{
    Interface1
    {
        mesh        Solid-Mesh;
        patches     (interface);
        locations   faceCenters;
        readData    (Force);
        writeData   (Displacement);
    }
}
FSI
{
    namePointDisplacement unused;
    nameCellDisplacement  D;
    nameForce             solidForce;
}
```

**Both controlDicts** — add the preCICE adapter function object:

```
functions
{
    preCICE_Adapter
    {
        type preciceAdapterFunctionObject;
        libs ("libpreciceAdapterFunctionObject.so");
    }
}
```

**solid/0/D** — use `solidForce` BC on the coupling interface patch:

```
interface
{
    type        solidForce;
    forceField  solidForce;
    value       uniform (0 0 0);
}
```

## OpenFOAM v2512 Gotchas

Things discovered during testing that differ from older OpenFOAM versions
and tutorials written for foam-extend:

**transportProperties** must include `transportModel Newtonian;` — older
examples only had the `nu` value which is no longer sufficient.

**fvSolution** for pimpleFoam needs `pRefCell 0; pRefValue 0;` in the
PIMPLE sub-dict, and solver entries should use regex patterns like
`"(U|UFinal)"` to cover both predictor and corrector steps.

**Boundary conditions renamed:**

- `timeVaryingUniformFixedValue` is replaced by `uniformFixedValue` with a
`uniformValue` sub-dict containing `type tableFile; file "path"; outOfBounds clamp;`
- `symmetryPlane` patch type — check consistency with BC type (`symmetry`
vs `symmetryPlane` are different in v2512)
- `solidSymmetry` (solids4foam) requires `symmetry` patch type in the mesh,
not `symmetryPlane`

**solids4foam model names changed:**

- `linearGeometry` is now `unsLinearGeometry`
- The coefficients sub-dict must match: `unsLinearGeometryCoeffs { ... }`
- Run `solids4Foam` with an invalid model name to see the full list of
available models

## Available Solvers and Tools

| Command          | Purpose                                              |
| ---------------- | ---------------------------------------------------- |
| `pimpleFoam`     | Incompressible transient flow (fluid side)           |
| `solids4Foam`    | Solid mechanics / FSI (solid side, OpenFOAM-native)  |
| `ccx_preCICE`    | CalculiX FEA solver with preCICE adapter (solid side) |
| `blockMesh`      | Structured mesh generation                           |
| `decomposePar`   | Domain decomposition for parallel runs               |
| `reconstructPar` | Recombine parallel results                           |

```bash
# Inside the container:
ls /opt/of-user/lib/     # compiled libraries (adapter, solids4foam)
ls /opt/of-user/bin/     # compiled binaries (solids4Foam, utilities)
ls /opt/calculix/bin/    # ccx_preCICE binary
ls /opt/s4f-tutorials/   # solids4foam tutorials (may need v2512 patches)
```

## Troubleshooting

**OpenFOAM not sourced (empty $WM_PROJECT_VERSION):**
Use `bash -l` (login shell) when entering the container. The environment
is auto-sourced via `/etc/profile.d/openfoam-fsi.sh`.

**Slow performance on Mac:**
Expected — Rosetta 2 emulation adds ~30-40% overhead. For production runs,
push the image to an x86_64 Linux server or cloud instance.

**solids4foam tutorials fail with BC errors:**
The bundled tutorials at `/opt/s4f-tutorials/` were written for older
OpenFOAM versions. They need manual patching for v2512. See the Gotchas
section above for common fixes.

**File permissions on Mac:**
Files created inside the container are owned by root. On your Mac you may
need `sudo chown -R $(whoami) cases/` to regain ownership after a run.

**CalculiX build fails on `Makefile.inc not found`:**
The adapter's Makefile uses `$(HOME)/CalculiX/ccx_2.20/src` as the default
CCX path. The Dockerfile sets `HOME=/build` during the make step so this
resolves to where the CalculiX source was extracted.

**CalculiX build fails on Fortran rank mismatch:**
GCC 10+ enforces stricter Fortran rules. The Dockerfile patches the
adapter's Makefile to add `-fallow-argument-mismatch` to FFLAGS.
