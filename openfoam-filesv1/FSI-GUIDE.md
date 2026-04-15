# FSI Case Setup Guide

## Quick start: run the built-in tutorial

The container ships with working preCICE FSI tutorials from solids4foam.
Copy one into your mounted workspace:

```bash
docker compose run --rm fsi bash -l

# Inside container:
bash /simulation/setup-fsi-tutorial.sh 3dTube
cd /simulation/3dTube
./Allrun
```

Results appear in `cases/3dTube/` on your Mac — open with ParaView.

## Create your own FSI case

### Required layout

```
cases/myCase/
├── precice-config.xml          # coupling config (top level)
├── Allrun                      # launches both solvers
├── Allclean
├── fluid/                      # pimpleFoam
│   ├── 0/                      # initial conditions (U, p)
│   ├── constant/
│   │   └── transportProperties
│   ├── system/
│   │   ├── blockMeshDict       # or use snappyHexMesh / cfMesh
│   │   ├── controlDict         # must include preCICE function object
│   │   ├── fvSchemes
│   │   ├── fvSolution
│   │   └── preciceDict         # adapter config for fluid side
│   └── case.foam               # empty file for ParaView
└── solid/                      # solids4Foam
    ├── 0/
    │   └── D                   # displacement field with solidForce BC on interface
    ├── constant/
    │   ├── mechanicalProperties
    │   └── solidProperties
    ├── system/
    │   ├── blockMeshDict
    │   ├── controlDict         # must include preCICE function object
    │   ├── fvSchemes
    │   ├── fvSolution
    │   └── preciceDict         # adapter config for solid side
    └── case.foam
```

### Key files to customize (templates/ folder has examples)

| File | What to set |
|------|-------------|
| `precice-config.xml` | dimensions (2 or 3), time window, convergence limits, mapping |
| `fluid/system/preciceDict` | participant=Fluid, coupling patch name, rho for incompressible |
| `solid/system/preciceDict` | participant=Solid, coupling patch name, nameForce=solidForce |
| `solid/0/D` | `solidForce` BC on the interface patch |
| Both `controlDict` | Add the preCICE_Adapter function object |

### Allrun pattern (two solvers in parallel)

```bash
#!/bin/bash
set -e
cd "${0%/*}" || exit 1

(cd fluid && blockMesh)
(cd solid && blockMesh)

(cd fluid && pimpleFoam > log.pimpleFoam 2>&1) &
(cd solid && solids4Foam > log.solids4Foam 2>&1) &
wait
```

### Volume mount

Your `cases/` folder is mounted at `/simulation` inside the container.
Any results written there are immediately visible on your Mac.
Open with ParaView: create an empty `case.foam` file and open it.
