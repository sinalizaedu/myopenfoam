FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      dynamicMeshDict;
}

// Two-way FSI: fluid mesh follows solid deformation on the shared wall patch.
// preCICE (RBF) writes pointDisplacement on wall; quadratic inverseDistance
// concentrates mesh motion near the FSI patch and pins the far field.

dynamicFvMesh   dynamicMotionSolverFvMesh;

motionSolverLibs ( "libfvMotionSolvers.so" );

motionSolver    displacementLaplacian;

displacementLaplacianCoeffs
{
    diffusivity  quadratic inverseDistance ( wall );
}
