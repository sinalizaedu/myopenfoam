# pimpleFoamMassSource

OpenFOAM 2512 `pimpleFoam` variant that applies scalar `fvOptions` registered
for `p` directly to the incompressible pressure equation.

For an absolute `scalarSemiImplicitSource`, positive `Su` injects volume and
negative `Su` removes volume:

```text
laplacian(rAU, p) + Su = div(phiHbyA)
div(phi) = Su
```

The normal `fvOptions(p)` operator is intentionally not used because it creates
an equation with `p*volume/time` dimensions. The pressure-correction equation
has `volume/time` dimensions, so the source must be added to the existing
`pEqn` with `fv::option::addSup`.

Build inside the OpenFOAM environment:

```bash
wmake
```

The repository Dockerfile builds and installs the executable automatically.
