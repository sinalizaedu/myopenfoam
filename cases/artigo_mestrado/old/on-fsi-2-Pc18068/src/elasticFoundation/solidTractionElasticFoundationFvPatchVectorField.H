/*---------------------------------------------------------------------------*\
Class
    solidTractionElasticFoundationFvPatchVectorField

Description
    Winkler-type elastic foundation boundary condition for solid solvers.

    The boundary applies a normal traction proportional to the current normal
    displacement:

        t_n = -k * (D . n)

    Implemented by deriving from `solidTraction` and updating the `pressure`
    field each iteration: pressure_face = k * (D_face . n).

    Sign convention: in solidTraction, pressure > 0 means compressive (force
    along -n). For a body bulging outward (D.n > 0), the foundation pushes
    back (force along -n) -> pressure positive. For a body compressed inward
    (D.n < 0), the foundation pulls back (force along +n) -> pressure
    negative. Therefore: pressure = k * (D . n).

    Use case: orbital fat as an elastic foundation around the optic nerve
    sheath. Stiffness k [Pa/m] = E_fat / t_fat (Winkler equivalent).

Usage
    In the displacement boundaryField:

        ons_outer
        {
            type        solidTractionElasticFoundation;
            k           200e3;          // Pa/m (= E_fat / t_fat)
            traction    uniform (0 0 0);
            pressure    uniform 0;      // will be overwritten each iter
            value       uniform (0 0 0);
        }

\*---------------------------------------------------------------------------*/

#ifndef solidTractionElasticFoundationFvPatchVectorField_H
#define solidTractionElasticFoundationFvPatchVectorField_H

#include "solidTractionFvPatchVectorField.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

/*---------------------------------------------------------------------------*\
       Class solidTractionElasticFoundationFvPatchVectorField Declaration
\*---------------------------------------------------------------------------*/

class solidTractionElasticFoundationFvPatchVectorField
:
    public solidTractionFvPatchVectorField
{
    // Private Data

        //- Winkler stiffness [Pa/m] (= E_foundation / t_foundation)
        scalar k_;


public:

    //- Runtime type information
    TypeName("solidTractionElasticFoundation");


    // Constructors

        //- Construct from patch and internal field
        solidTractionElasticFoundationFvPatchVectorField
        (
            const fvPatch&,
            const DimensionedField<vector, volMesh>&
        );

        //- Construct from patch, internal field and dictionary
        solidTractionElasticFoundationFvPatchVectorField
        (
            const fvPatch&,
            const DimensionedField<vector, volMesh>&,
            const dictionary&
        );

        //- Construct by mapping given patch field onto a new patch
        solidTractionElasticFoundationFvPatchVectorField
        (
            const solidTractionElasticFoundationFvPatchVectorField&,
            const fvPatch&,
            const DimensionedField<vector, volMesh>&,
            const fvPatchFieldMapper&
        );

        //- Construct as copy
        solidTractionElasticFoundationFvPatchVectorField
        (
            const solidTractionElasticFoundationFvPatchVectorField&
        );

        //- Construct and return a clone
        virtual tmp<fvPatchVectorField> clone() const
        {
            return tmp<fvPatchVectorField>
            (
                new solidTractionElasticFoundationFvPatchVectorField(*this)
            );
        }

        //- Construct as copy setting internal field reference
        solidTractionElasticFoundationFvPatchVectorField
        (
            const solidTractionElasticFoundationFvPatchVectorField&,
            const DimensionedField<vector, volMesh>&
        );

        //- Construct and return a clone setting internal field reference
        virtual tmp<fvPatchVectorField> clone
        (
            const DimensionedField<vector, volMesh>& iF
        ) const
        {
            return tmp<fvPatchVectorField>
            (
                new solidTractionElasticFoundationFvPatchVectorField(*this, iF)
            );
        }


    // Member functions

        //- Winkler stiffness
        scalar k() const { return k_; }

        //- Update the coefficients associated with the patch field.
        //  Recomputes pressure_ = k * (D_face . n) before delegating to parent.
        virtual void updateCoeffs();

        //- Write
        virtual void write(Ostream&) const;
};


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif

// ************************************************************************* //
