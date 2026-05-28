/*---------------------------------------------------------------------------*\
    solidTractionElasticFoundationFvPatchVectorField

    Implementation of Winkler elastic foundation BC.
\*---------------------------------------------------------------------------*/

#include "solidTractionElasticFoundationFvPatchVectorField.H"
#include "addToRunTimeSelectionTable.H"
#include "volFields.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * * //

solidTractionElasticFoundationFvPatchVectorField::
solidTractionElasticFoundationFvPatchVectorField
(
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF
)
:
    solidTractionFvPatchVectorField(p, iF),
    k_(0.0)
{}


solidTractionElasticFoundationFvPatchVectorField::
solidTractionElasticFoundationFvPatchVectorField
(
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF,
    const dictionary& dict
)
:
    solidTractionFvPatchVectorField(p, iF, dict),
    k_(readScalar(dict.lookup("k")))
{
    Info<< "    Winkler stiffness k = " << k_ << " Pa/m" << endl;
}


solidTractionElasticFoundationFvPatchVectorField::
solidTractionElasticFoundationFvPatchVectorField
(
    const solidTractionElasticFoundationFvPatchVectorField& pvf,
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF,
    const fvPatchFieldMapper& mapper
)
:
    solidTractionFvPatchVectorField(pvf, p, iF, mapper),
    k_(pvf.k_)
{}


solidTractionElasticFoundationFvPatchVectorField::
solidTractionElasticFoundationFvPatchVectorField
(
    const solidTractionElasticFoundationFvPatchVectorField& pvf
)
:
    solidTractionFvPatchVectorField(pvf),
    k_(pvf.k_)
{}


solidTractionElasticFoundationFvPatchVectorField::
solidTractionElasticFoundationFvPatchVectorField
(
    const solidTractionElasticFoundationFvPatchVectorField& pvf,
    const DimensionedField<vector, volMesh>& iF
)
:
    solidTractionFvPatchVectorField(pvf, iF),
    k_(pvf.k_)
{}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

void solidTractionElasticFoundationFvPatchVectorField::updateCoeffs()
{
    if (updated())
    {
        return;
    }

    // Outward-pointing unit normals on the patch faces
    const vectorField n(patch().nf());

    // Current displacement on the patch (use the cell-center adjacent value as
    // a stable proxy for the face value during iteration)
    const vectorField D(patchInternalField());

    // Winkler relation: pressure_face = k * (D_face . n)
    //   D . n > 0 (bulging out)   -> pressure > 0 (compressive, force in -n)
    //   D . n < 0 (compressed in) -> pressure < 0 (force in +n)
    pressure() = k_*(D & n);

    // Delegate to parent: converts (traction, pressure) into surface-normal
    // gradient via solidModel::tractionBoundarySnGrad
    solidTractionFvPatchVectorField::updateCoeffs();
}


void solidTractionElasticFoundationFvPatchVectorField::write(Ostream& os) const
{
    solidTractionFvPatchVectorField::write(os);

    os.writeKeyword("k") << k_ << token::END_STATEMENT << nl;
}


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

makePatchTypeField
(
    fvPatchVectorField,
    solidTractionElasticFoundationFvPatchVectorField
);


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// ************************************************************************* //
