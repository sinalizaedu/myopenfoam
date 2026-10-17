FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}
// FSI experiment: IVI/ACP patch injection + two-way ALE on wall (no Robin).
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (0 0 0);
boundaryField
{
    iris_wall { type noSlip; }
    ac_inlet
    {
        type            flowRateInletVelocity;
        volumetricFlowRate constant 1.25e-11;
        value           uniform (0 0 0);
    }
    outlet_tm { type zeroGradient; }

    ivi_tip
    {
        type            flowRateInletVelocity;
        volumetricFlowRate table
        (
            (0    0)
            (5    0)
            (6    2.08325e-9)
            (11   2.08325e-9)
            (12   0)
            (1e6  0)
        );
        value           uniform (0 0 0);
    }

    acp_tip
    {
        type            flowRateInletVelocity;
        volumetricFlowRate table
        (
            (0    0)
            (15   0)
            (16   -2.08325e-9)
            (21   -2.08325e-9)
            (22   0)
            (1e6  0)
        );
        value           uniform (0 0 0);
    }

    wall
    {
        type            movingWallVelocity;
        value           uniform (0 0 0);
    }

    lens_wall { type noSlip; }
    symmetry_0 { type symmetry; }
    symmetry_90 { type symmetry; }
}
