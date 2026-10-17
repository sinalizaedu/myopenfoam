volScalarField rAU(1.0/UEqn.A());
volVectorField HbyA(constrainHbyA(rAU*UEqn.H(), U, p));
surfaceScalarField phiHbyA("phiHbyA", fvc::flux(HbyA));

if (pimple.ddtCorr())
{
    phiHbyA += MRF.zeroFilter(fvc::interpolate(rAU)*fvc::ddtCorr(U, phi, Uf));
}


MRF.makeRelative(phiHbyA);

if (p.needReference())
{
    fvc::makeRelative(phiHbyA, U);
    adjustPhi(phiHbyA, U, p);
    fvc::makeAbsolute(phiHbyA, U);
}

tmp<volScalarField> rAtU(rAU);

if (pimple.consistent())
{
    rAtU = 1.0/max(1.0/rAU - UEqn.H1(), 0.1/rAU);
    phiHbyA +=
        fvc::interpolate(rAtU() - rAU)*fvc::snGrad(p)*mesh.magSf();
    HbyA -= (rAU - rAtU())*fvc::grad(p);
}

if (pimple.nCorrPISO() <= 1)
{
    tUEqn.clear();
}

// Update the pressure BCs to ensure flux consistency
constrainPressure(p, U, phiHbyA, rAtU(), MRF);

// Non-orthogonal pressure corrector loop
while (pimple.correctNonOrthogonal())
{
    fvScalarMatrix pEqn
    (
        fvm::laplacian(rAtU(), p) == fvc::div(phiHbyA)
    );

    // Apply scalar fvOptions registered for p directly to the continuity
    // equation. optionList::operator()(p) cannot be used here because it
    // constructs momentum-style dimensions (p*V/t), whereas this pressure
    // equation has volumetric-flow dimensions (V/t).
    //
    // SemiImplicitSource::addSup adds +Su to the equation's left-hand side:
    //     laplacian(rAtU,p) + Su = div(phiHbyA)
    // so the corrected flux satisfies div(phi) = Su. Positive Su therefore
    // injects volume and negative Su removes volume.
    UPtrList<fv::option>& options = fvOptions;

    for (fv::option& source : options)
    {
        const label fieldi = source.applyToField(p.name());

        if (fieldi != -1)
        {
            source.setApplied(fieldi);

            if (source.isActive())
            {
                source.addSup(pEqn, fieldi);
            }
        }
    }

    pEqn.setReference(pRefCell, pRefValue);

    pEqn.solve(p.select(pimple.finalInnerIter()));

    if (pimple.finalNonOrthogonalIter())
    {
        phi = phiHbyA - pEqn.flux();
    }
}

#include "continuityErrs.H"

// Explicitly relax pressure for momentum corrector
p.relax();

U = HbyA - rAtU*fvc::grad(p);
U.correctBoundaryConditions();
fvOptions.correct(U);

// Correct Uf if the mesh is moving
fvc::correctUf(Uf, U, phi);

// Make the fluxes relative to the mesh motion
fvc::makeRelative(phi, U);
