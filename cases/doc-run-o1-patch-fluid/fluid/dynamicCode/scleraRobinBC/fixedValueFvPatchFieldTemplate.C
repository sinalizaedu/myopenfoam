/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | www.openfoam.com
     \\/     M anipulation  |
-------------------------------------------------------------------------------
    Copyright (C) 2019-2021 OpenCFD Ltd.
    Copyright (C) YEAR AUTHOR, AFFILIATION
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.

\*---------------------------------------------------------------------------*/

#include "fixedValueFvPatchFieldTemplate.H"
#include "addToRunTimeSelectionTable.H"
#include "fvPatchFieldMapper.H"
#include "volFields.H"
#include "surfaceFields.H"
#include "unitConversion.H"
#include "PatchFunction1.H"

//{{{ begin codeInclude

//}}} end codeInclude


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// * * * * * * * * * * * * * * * Local Functions * * * * * * * * * * * * * * //

//{{{ begin localCode

//}}} end localCode


// * * * * * * * * * * * * * * * Global Functions  * * * * * * * * * * * * * //

// dynamicCode:
// SHA1 = 0328f93a5d9dadc3059e277deb41f3380d216a55
//
// unique function name that can be checked if the correct library version
// has been loaded
extern "C" void scleraRobinBC_0328f93a5d9dadc3059e277deb41f3380d216a55(bool load)
{
    if (load)
    {
        // Code that can be explicitly executed after loading
    }
    else
    {
        // Code that can be explicitly executed before unloading
    }
}

// * * * * * * * * * * * * * * Static Data Members * * * * * * * * * * * * * //

makeRemovablePatchTypeField
(
    fvPatchVectorField,
    scleraRobinBCFixedValueFvPatchVectorField
);

} // End namespace Foam


// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

Foam::
scleraRobinBCFixedValueFvPatchVectorField::
scleraRobinBCFixedValueFvPatchVectorField
(
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF
)
:
    parent_bctype(p, iF)
{
    if (false)
    {
        printMessage("Construct scleraRobinBC : patch/DimensionedField");
    }
}


Foam::
scleraRobinBCFixedValueFvPatchVectorField::
scleraRobinBCFixedValueFvPatchVectorField
(
    const scleraRobinBCFixedValueFvPatchVectorField& rhs,
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF,
    const fvPatchFieldMapper& mapper
)
:
    parent_bctype(rhs, p, iF, mapper)
{
    if (false)
    {
        printMessage("Construct scleraRobinBC : patch/DimensionedField/mapper");
    }
}


Foam::
scleraRobinBCFixedValueFvPatchVectorField::
scleraRobinBCFixedValueFvPatchVectorField
(
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF,
    const dictionary& dict
)
:
    parent_bctype(p, iF, dict)
{
    if (false)
    {
        printMessage("Construct scleraRobinBC : patch/dictionary");
    }
}


Foam::
scleraRobinBCFixedValueFvPatchVectorField::
scleraRobinBCFixedValueFvPatchVectorField
(
    const scleraRobinBCFixedValueFvPatchVectorField& rhs
)
:
    parent_bctype(rhs),
    dictionaryContent(rhs)
{
    if (false)
    {
        printMessage("Copy construct scleraRobinBC");
    }
}


Foam::
scleraRobinBCFixedValueFvPatchVectorField::
scleraRobinBCFixedValueFvPatchVectorField
(
    const scleraRobinBCFixedValueFvPatchVectorField& rhs,
    const DimensionedField<vector, volMesh>& iF
)
:
    parent_bctype(rhs, iF)
{
    if (false)
    {
        printMessage("Construct scleraRobinBC : copy/DimensionedField");
    }
}


// * * * * * * * * * * * * * * * * Destructor  * * * * * * * * * * * * * * * //

Foam::
scleraRobinBCFixedValueFvPatchVectorField::
~scleraRobinBCFixedValueFvPatchVectorField()
{
    if (false)
    {
        printMessage("Destroy scleraRobinBC");
    }
}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

void
Foam::
scleraRobinBCFixedValueFvPatchVectorField::updateCoeffs()
{
    if (this->updated())
    {
        return;
    }

    if (false)
    {
        printMessage("updateCoeffs scleraRobinBC");
    }

//{{{ begin code
    #line 53709 "/simulation/doc-run-o1-patch-fluid/fluid/4.8/U/boundaryField/wall"
const label timeIndex = this->db().time().timeIndex();
            static label lastIndex = -1;
            static scalar Un_hold = 0;

            if (timeIndex != lastIndex)
            {
                const fvMesh& mesh = patch().boundaryMesh().mesh();
                const label aci = mesh.boundaryMesh().findPatchID("ac_inlet");
                if (aci < 0)
                {
                    FatalErrorInFunction
                        << "scleraRobinBC: patch ac_inlet not found"
                        << exit(FatalError);
                }
                const fvPatch& acPatch = mesh.boundary()[aci];
                const fvPatchScalarField& pac =
                    acPatch.lookupPatchField<volScalarField, scalar>("p");

                const scalar area = gSum(acPatch.magSf());
                const scalar p_avg =
                    gSum(pac*acPatch.magSf())/max(area, SMALL);

                const scalar p_base = 2.01;
                const scalar K_comp = 1.0e-7;
                const scalar Un_target = K_comp*(p_avg - p_base);

                const scalar relax = 0.01;
                scalar Un = relax*Un_target + (1.0 - relax)*Un_hold;
                const scalar Un_max = 1.0e-5;
                Un = min(max(Un, -Un_max), Un_max);

                Un_hold = Un;
                lastIndex = timeIndex;

                Info<< "scleraRobinBC: t=" << this->db().time().value()
                    << " p_AC=" << p_avg
                    << " Un=" << Un_hold
                    << " Un_target=" << Un_target << endl;
            }

            operator==(Un_hold*patch().nf());
//}}} end code

    this->parent_bctype::updateCoeffs();
}


// ************************************************************************* //

