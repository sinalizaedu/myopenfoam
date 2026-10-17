FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}
// FSI phase — equilibrated internal field comes from prewarm; wall follows ALE mesh.
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (0 0 0);
boundaryField
{
    iris_wall
    {
        type noSlip;
    }
    ac_inlet
    {
        type            flowRateInletVelocity;
        volumetricFlowRate constant 1.25e-11;
        value           uniform (0 0 0);
    }
    outlet_tm { type zeroGradient; }
    ivi_tip   { type noSlip; }
    acp_tip   { type noSlip; }
    wall
    {
        type            movingWallVelocity;
        value           uniform (0 0 0);
    }
    lens_wall { type noSlip; }
    symmetry_0 { type symmetry; }
    symmetry_90 { type symmetry; }
}
