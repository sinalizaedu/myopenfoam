FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}

// Transient pimpleFoam + preCICE two-way FSI (Force + Displacement).
// Timing patched by Allrun: startTime=0, endTime=FSI_END_TIME, fixed deltaT (= preCICE window).

application     pimpleFoam;

startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         2;

deltaT          0.05;
maxCo           100;
adjustTimeStep  no;
maxDeltaT       0.05;

writeControl    runTime;
writeInterval   1;
purgeWrite      0;
writeFormat     ascii;
writePrecision  8;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable true;

functions
{
    preCICE_Adapter
    {
        type preciceAdapterFunctionObject;
        libs ("libpreciceAdapterFunctionObject.so");
    }

    flowRateTM
    {
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        fields          (phi);
        operation       sum;
        regionType      patch;
        name            outlet_tm;
        writeFields     false;
        log             true;
        writeControl    timeStep;
        writeInterval   1;
    }

    pressureACinlet
    {
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        fields          (p);
        operation       areaAverage;
        regionType      patch;
        name            ac_inlet;
        writeFields     false;
        log             true;
        writeControl    timeStep;
        writeInterval   1;
    }

    iop_probe
    {
        type            probes;
        libs            (sampling);
        fields          (p);
        probeLocations
        (
            ( 0.0015   -0.0068   0.0000)
            ( 0.00106  -0.0068  -0.00106)
            ( 0.0020    0.0030   0.0000)
            ( 0.00141   0.0030  -0.00141)
        );
        writeControl    timeStep;
        writeInterval   1;
    }
}
