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

Runs as `linux/amd64` via Rosetta 2 on Apple Silicon.
No native arm64 OpenFOAM apt packages exist. Expect ~30-40% performance
overhead vs native x86 — fine for development, use an x86 server for
production runs.

## Project Structure

```
myopenfoam/
├── Dockerfile              # Multi-stage build
├── docker-compose.yaml     # Container config + volume mounts
├── cases/                  # Your simulation cases (mounted at /simulation)
│   └── validation/         # Stack validation case
│       ├── Allrun
│       ├── Allclean
│       ├── fluid/          # Lid-driven cavity (pimpleFoam)
│       │   ├── 0/          # Initial conditions (U, p)
│       │   ├── constant/   # Transport, turbulence properties
│       │   └── system/     # controlDict, fvSchemes, fvSolution, blockMeshDict
│       └── solid/          # Cantilever beam (solids4Foam)
│           ├── 0/          # Initial conditions (D)
│           ├── constant/   # Material, solid properties, gravity
│           └── system/     # controlDict, fvSchemes, fvSolution, blockMeshDict
└── openfoam-filesv1/       # preCICE FSI templates (for custom cases)
    ├── precice-config.xml
    ├── fluid-preciceDict
    ├── solid-preciceDict
    ├── solid-interface-BC-snippet
    └── controlDict-functions-snippet
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

### 4. Visualise results

On your Mac, install ParaView (https://www.paraview.org/download/) and open:

- `cases/validation/fluid/case.foam` — velocity and pressure fields
- `cases/validation/solid/case.foam` — displacement and stress fields

The `case.foam` files are empty marker files that tell ParaView to read
the OpenFOAM directory structure.

## Running Simulations

### Interactive shell

```bash
docker compose run --rm fsi bash -l
```

### Run a specific case

```bash
docker compose run --rm fsi bash -lc "cd /simulation/myCase && ./Allrun"
```

### Two-terminal workflow (for coupled FSI)

```bash
# Terminal 1 — start container and run fluid
docker compose run --rm --name fsi-run fsi bash -l
cd /simulation/myFSICase/fluid && pimpleFoam

# Terminal 2 — attach and run solid
docker exec -it fsi-run bash -l
cd /simulation/myFSICase/solid && solids4Foam
```

## Creating a Coupled FSI Case

For 2-way FSI with preCICE, you need these additional files on top of
standard OpenFOAM cases:

### 1. precice-config.xml (case root)

Defines participants, data exchange, mapping, and coupling scheme.
Template in `openfoam-filesv1/precice-config.xml`.

### 2. fluid/system/preciceDict

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

### 3. solid/system/preciceDict

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

### 4. Both controlDicts — add preCICE function object

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

### 5. solid/0/D — solidForce BC on coupling patch

```
interface
{
    type        solidForce;
    forceField  solidForce;
    value       uniform (0 0 0);
}
```

## Available Solvers

Inside the container:

| Solver | Purpose |
|--------|---------|
| `pimpleFoam` | Incompressible transient flow (fluid side) |
| `solids4Foam` | Solid mechanics / FSI (solid side) |
| `blockMesh` | Structured mesh generation |
| `decomposePar` | Domain decomposition for parallel runs |
| `reconstructPar` | Recombine parallel results |

## Useful Commands

```bash
# List available solids4foam solid models
solids4Foam -listSolidModels 2>&1 || true

# Check what's available
ls /opt/of-user/lib/     # compiled libraries
ls /opt/of-user/bin/     # compiled binaries
ls /opt/s4f-tutorials/   # solids4foam tutorials

# Clean a case
foamCleanCase            # standard OpenFOAM clean
./Allclean               # case-specific clean script
```

## Troubleshooting

**OpenFOAM not sourced (empty $WM_PROJECT_VERSION)**
Use `bash -l` (login shell) when entering the container.

**BC type not found errors**
OpenFOAM v2512 renamed some boundary conditions vs older versions.
Common changes: `timeVaryingUniformFixedValue` → `uniformFixedValue`,
`symmetryPlane` patch type vs `symmetry`.

**solids4foam model not found**
Model names changed: `linearGeometry` → `unsLinearGeometry`.
Run `solids4Foam` with an invalid model name to see the full list.

**Slow performance on Mac**
Expected — Rosetta 2 emulation. For production runs, push the image
to an x86_64 Linux server.
