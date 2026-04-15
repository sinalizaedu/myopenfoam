# OpenFOAM FSI Docker Environment

Dockerised environment for Fluid-Structure Interaction simulations using
OpenFOAM, preCICE, and solids4foam — built for Apple Silicon Macs.

## Software Versions

| Component | Version | Notes |
|-----------|---------|-------|
| Ubuntu | 24.04 LTS | Base image |
| OpenFOAM | v2512 (ESI/OpenCFD) | Released Dec 2025 |
| preCICE | 3.3.1 | Built from source |
| OpenFOAM-preCICE adapter | 1.3.1 | Compiled against v2512 |
| solids4foam | master (v2.3+) | Compiled against v2512 |
| Python | 3.12 | With numpy, scipy, matplotlib |

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

## Quick Start

### 1. Build the image

```bash
docker compose build
```

First build takes 30-60 minutes (compiles preCICE, adapter, solids4foam).
Subsequent rebuilds use cached layers.

### 2. Verify the installation

```bash
docker compose run --rm fsi bash -lc '
echo "OpenFOAM: $WM_PROJECT_VERSION"
which pimpleFoam && echo "pimpleFoam: OK"
which solids4Foam && echo "solids4Foam: OK"
ls /opt/precice/lib/libprecice.so && echo "preCICE: OK"
ls /opt/of-user/lib/libpreciceAdapterFunctionObject.so && echo "Adapter: OK"
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

Install ParaView on your Mac (https://www.paraview.org/download/) and open:

- `cases/validation/fluid/case.foam` — select `U` field to see cavity vortex
- `cases/validation/solid/case.foam` — select `D` field to see beam deflection

The `case.foam` files are empty markers that tell ParaView to read the
OpenFOAM directory structure. Results are visible on your Mac because the
`cases/` folder is a shared volume mount.

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

# Terminal 2 — attach and run solid
docker exec -it fsi-run bash -l
cd /simulation/myFSICase/solid && solids4Foam
```

Both solvers run simultaneously. preCICE handles the data exchange — the
fluid waits for displacement from the solid, the solid waits for forces
from the fluid. You will see convergence info printed each time window.

## Creating a Coupled FSI Case

For 2-way FSI with preCICE, add these files on top of standard OpenFOAM cases.
Templates are in `openfoam-filesv1/`.

### Required layout

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

**solid/system/preciceDict:**
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
  `uniformValue` sub-dict containing `type tableFile; file "path";
  outOfBounds clamp;`
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

| Command | Purpose |
|---------|---------|
| `pimpleFoam` | Incompressible transient flow (fluid side) |
| `solids4Foam` | Solid mechanics / FSI (solid side) |
| `blockMesh` | Structured mesh generation |
| `decomposePar` | Domain decomposition for parallel runs |
| `reconstructPar` | Recombine parallel results |

```bash
# Inside the container:
ls /opt/of-user/lib/     # compiled libraries (adapter, solids4foam)
ls /opt/of-user/bin/     # compiled binaries (solids4Foam, utilities)
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
