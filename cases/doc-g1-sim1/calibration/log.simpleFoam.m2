/*---------------------------------------------------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  2512                                  |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
Build  : _bd2b6720-20260127 OPENFOAM=2512 version=2512
Arch   : "LSB;label=32;scalar=64"
Exec   : simpleFoam
Date   : Jul 19 2026
Time   : 23:32:17
Host   : 6e070a5d1098
PID    : 266
I/O    : uncollated
Case   : /simulation/doc-g1-sim1/fluid
nProcs : 1
trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).
memory pool : not available
fileModificationChecking : Monitoring run-time modified files using timeStampMaster (fileModificationSkew 5, maxFileModificationPolls 20)
allowSystemOperations : Allowing user-supplied system call operations

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
Create time

Create mesh for time = 0


SIMPLE: convergence criteria
    field p	 tolerance 0.0001
    field U	 tolerance 1e-05

Reading field p

Reading field U

Reading/calculating face flux field phi

Selecting incompressible transport model Newtonian
Selecting turbulence model type laminar
Selecting laminar stress model Stokes
No MRF models present

Creating finite-volume options from "system/fvOptions"

Selecting finite volume options type explicitPorositySource
    Source: tm_porous
    State: active
    - selecting cells using cellZones (tm_zone)
    - selected 280 cell(s) with volume 2.0234737e-10
Porosity region tm_porous:
    selecting model: DarcyForchheimer
--> FOAM IOWarning :
    Found [v1806] 'coordinateRotation' entry instead of 'rotation' in dictionary "system/fvOptions/tm_porous/explicitPorositySourceCoeffs/DarcyForchheimerCoeffs/coordinateSystem"

    This keyword is 90 months old.

Using [v1806] 'axesRotation' instead of 'axes' in selection table: coordinateRotation

    This lookup is 90 months old.

    creating porous zone: tm_zone
    origin: (0 0 0) e1: (1 0 0) e2: (0 1 0)
    local bounds: (0.0005093976 0.0006520705 0.001)

Selecting finite volume options type explicitPorositySource
    Source: tm_porous_left
    State: active
    - selecting cells using cellZones (tm_zone_left)
    - selected 276 cell(s) with volume 2.0259301e-10
Porosity region tm_porous_left:
    selecting model: DarcyForchheimer
--> FOAM IOWarning :
    Found [v1806] 'coordinateRotation' entry instead of 'rotation' in dictionary "system/fvOptions/tm_porous_left/explicitPorositySourceCoeffs/DarcyForchheimerCoeffs/coordinateSystem"

    This keyword is 90 months old.

Using [v1806] 'axesRotation' instead of 'axes' in selection table: coordinateRotation

    This lookup is 90 months old.

    creating porous zone: tm_zone_left
    origin: (0 0 0) e1: (1 0 0) e2: (0 1 0)
    local bounds: (0.0005093976 0.0006520705 0.001)

Selecting finite volume options type explicitPorositySource
    Source: vitreous_porous
    State: active
    - selecting cells using cellZones (vitreous_zone)
    - selected 78731 cell(s) with volume 1.0168395e-07
Porosity region vitreous_porous:
    selecting model: DarcyForchheimer
--> FOAM IOWarning :
    Found [v1806] 'coordinateRotation' entry instead of 'rotation' in dictionary "system/fvOptions/vitreous_porous/explicitPorositySourceCoeffs/DarcyForchheimerCoeffs/coordinateSystem"

    This keyword is 90 months old.

Using [v1806] 'axesRotation' instead of 'axes' in selection table: coordinateRotation

    This lookup is 90 months old.

    creating porous zone: vitreous_zone
    origin: (0 0 0) e1: (1 0 0) e2: (0 1 0)
    local bounds: (0.016059527 0.0084360467 0.001)


Starting time loop

surfaceFieldValue flowRateTM:
    operation     = sum


surfaceFieldValue flowRateTM_left:
    operation     = sum


surfaceFieldValue flowRateAC:
    operation     = sum


surfaceFieldValue flowRateAC_left:
    operation     = sum


surfaceFieldValue pressureACinlet:
    operation     = areaAverage


Time = 1

smoothSolver:  Solving for Ux, Initial residual = 0.99999995, Final residual = 9.1647517e-09, No Iterations 10
smoothSolver:  Solving for Uy, Initial residual = 0.99999966, Final residual = 9.1646243e-09, No Iterations 10
GAMG:  Solving for p, Initial residual = 0.99999892, Final residual = 0.0039824001, No Iterations 60
GAMG:  Solving for p, Initial residual = 0.79008306, Final residual = 0.0075247822, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.10674288, Final residual = 0.00099991802, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.06141278, Final residual = 0.00035391633, No Iterations 16
time step continuity errors : sum local = 2.0932032e-06, global = -2.9356748e-09, cumulative = -2.9356748e-09
ExecutionTime = 7.61 s  ClockTime = 8 s

Time = 2

smoothSolver:  Solving for Ux, Initial residual = 0.29276694, Final residual = 6.3396887e-09, No Iterations 5
smoothSolver:  Solving for Uy, Initial residual = 0.27177291, Final residual = 4.7271505e-09, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.20731575, Final residual = 0.0013453164, No Iterations 26
GAMG:  Solving for p, Initial residual = 0.35333589, Final residual = 0.0033164244, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.069300553, Final residual = 0.00044886282, No Iterations 17
GAMG:  Solving for p, Initial residual = 0.051128091, Final residual = 0.00037152326, No Iterations 4
time step continuity errors : sum local = 1.6191536e-06, global = -7.6102953e-09, cumulative = -1.054597e-08
ExecutionTime = 8.7 s  ClockTime = 9 s

Time = 3

smoothSolver:  Solving for Ux, Initial residual = 0.19661115, Final residual = 4.1086306e-09, No Iterations 5
smoothSolver:  Solving for Uy, Initial residual = 0.1779246, Final residual = 2.9781046e-09, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.22876456, Final residual = 0.0019383771, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.2030412, Final residual = 0.0017970183, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.048122151, Final residual = 0.00038967599, No Iterations 16
GAMG:  Solving for p, Initial residual = 0.043358667, Final residual = 0.00042754947, No Iterations 3
time step continuity errors : sum local = 9.342935e-07, global = -1.0073125e-08, cumulative = -2.0619095e-08
ExecutionTime = 9.52 s  ClockTime = 10 s

Time = 4

smoothSolver:  Solving for Ux, Initial residual = 0.13277643, Final residual = 2.3818033e-09, No Iterations 5
smoothSolver:  Solving for Uy, Initial residual = 0.11862601, Final residual = 8.9279013e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.23637775, Final residual = 0.0014620784, No Iterations 15
GAMG:  Solving for p, Initial residual = 0.52376295, Final residual = 0.0050063683, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.13445511, Final residual = 0.0012745112, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.083521672, Final residual = 0.00066066761, No Iterations 16
time step continuity errors : sum local = 1.4575484e-06, global = -5.0137894e-10, cumulative = -2.1120474e-08
ExecutionTime = 10.45 s  ClockTime = 11 s

Time = 5

smoothSolver:  Solving for Ux, Initial residual = 0.085431157, Final residual = 5.185929e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 0.075704692, Final residual = 3.6998243e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.22190943, Final residual = 0.0021106828, No Iterations 20
GAMG:  Solving for p, Initial residual = 0.6414618, Final residual = 0.0055390827, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.13256419, Final residual = 0.0012370262, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.069039074, Final residual = 0.00049030517, No Iterations 11
time step continuity errors : sum local = 1.3690083e-06, global = 1.7557926e-09, cumulative = -1.9364682e-08
ExecutionTime = 11.38 s  ClockTime = 12 s

Time = 6

smoothSolver:  Solving for Ux, Initial residual = 0.047627802, Final residual = 4.8069625e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 0.041977912, Final residual = 4.257671e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.2552813, Final residual = 0.0024358887, No Iterations 19
GAMG:  Solving for p, Initial residual = 0.60783305, Final residual = 0.0044050731, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.10575411, Final residual = 0.0010537623, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.058762953, Final residual = 0.00035190535, No Iterations 14
time step continuity errors : sum local = 9.1416822e-07, global = 1.6032659e-09, cumulative = -1.7761416e-08
ExecutionTime = 12.35 s  ClockTime = 13 s

Time = 7

smoothSolver:  Solving for Ux, Initial residual = 0.018411444, Final residual = 4.2344373e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 0.01615358, Final residual = 2.8917684e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.31719559, Final residual = 0.0013116412, No Iterations 18
GAMG:  Solving for p, Initial residual = 0.28430502, Final residual = 0.0027478582, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.057692401, Final residual = 0.00019603898, No Iterations 26
GAMG:  Solving for p, Initial residual = 0.061841787, Final residual = 0.00050542528, No Iterations 3
time step continuity errors : sum local = 9.3215372e-07, global = 5.3862042e-09, cumulative = -1.2375212e-08
ExecutionTime = 13.46 s  ClockTime = 14 s

Time = 8

smoothSolver:  Solving for Ux, Initial residual = 0.013946083, Final residual = 5.6436652e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 0.012455518, Final residual = 3.9215912e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.34210989, Final residual = 0.0028869926, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.28350275, Final residual = 0.0024340725, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.070010652, Final residual = 0.00052608901, No Iterations 13
GAMG:  Solving for p, Initial residual = 0.067151401, Final residual = 0.00033117114, No Iterations 7
time step continuity errors : sum local = 3.3895612e-07, global = 4.0758777e-10, cumulative = -1.1967624e-08
ExecutionTime = 14.29 s  ClockTime = 14 s

Time = 9

smoothSolver:  Solving for Ux, Initial residual = 0.026768432, Final residual = 4.7644925e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 0.023732499, Final residual = 3.345115e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.34980783, Final residual = 0.0021602822, No Iterations 8
GAMG:  Solving for p, Initial residual = 0.51240389, Final residual = 0.0050424144, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.13028552, Final residual = 0.001179489, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.065470668, Final residual = 0.00028604285, No Iterations 17
time step continuity errors : sum local = 3.7261374e-07, global = 6.0643837e-10, cumulative = -1.1361185e-08
ExecutionTime = 15.16 s  ClockTime = 15 s

Time = 10

smoothSolver:  Solving for Ux, Initial residual = 0.033102157, Final residual = 2.2088703e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 0.029300629, Final residual = 8.3173311e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.32230673, Final residual = 0.0021797618, No Iterations 13
GAMG:  Solving for p, Initial residual = 0.55509128, Final residual = 0.003794759, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.11342055, Final residual = 0.00049321687, No Iterations 13
GAMG:  Solving for p, Initial residual = 0.071861885, Final residual = 0.00068404913, No Iterations 2
time step continuity errors : sum local = 1.1415864e-06, global = 2.9034943e-09, cumulative = -8.4576911e-09
ExecutionTime = 15.94 s  ClockTime = 16 s

surfaceFieldValue flowRateTM write:
    total faces   = 4
    total area    = 3.471311e-07

    sum(outlet_tm) of phi = 1.1304895e-12

surfaceFieldValue flowRateTM_left write:
    total faces   = 5
    total area    = 3.471311e-07

    sum(outlet_tm_left) of phi = 1.1620248e-12

surfaceFieldValue flowRateAC write:
    total faces   = 7
    total area    = 5.1623638e-07

    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    total faces   = 7
    total area    = 5.1623638e-07

    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    total faces   = 7
    total area    = 5.1623638e-07

    areaAverage(ac_inlet) of p = 1.8221049

Time = 11

smoothSolver:  Solving for Ux, Initial residual = 0.030178295, Final residual = 6.6386854e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 0.026620614, Final residual = 5.0491429e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.25193475, Final residual = 0.00095765879, No Iterations 27
GAMG:  Solving for p, Initial residual = 0.44829164, Final residual = 0.0040957323, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.081028848, Final residual = 0.00062888305, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.044832925, Final residual = 0.00032147118, No Iterations 8
time step continuity errors : sum local = 5.0070864e-07, global = -1.0104466e-09, cumulative = -9.4681376e-09
ExecutionTime = 16.94 s  ClockTime = 17 s

Time = 12

smoothSolver:  Solving for Ux, Initial residual = 0.020357819, Final residual = 3.2305529e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 0.01800767, Final residual = 2.282631e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.22160915, Final residual = 0.0022036444, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.132734, Final residual = 0.00081652237, No Iterations 18
GAMG:  Solving for p, Initial residual = 0.082248068, Final residual = 0.00062267908, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.023751754, Final residual = 0.0001427676, No Iterations 22
time step continuity errors : sum local = 1.6756024e-07, global = -2.3566386e-10, cumulative = -9.7038015e-09
ExecutionTime = 18.06 s  ClockTime = 18 s

Time = 13

smoothSolver:  Solving for Ux, Initial residual = 0.0094338362, Final residual = 3.725617e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 0.008559695, Final residual = 2.6829079e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.22182887, Final residual = 0.0020643885, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.23329693, Final residual = 0.0013206926, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.055456053, Final residual = 0.00025734787, No Iterations 20
GAMG:  Solving for p, Initial residual = 0.045248782, Final residual = 0.00029781486, No Iterations 3
time step continuity errors : sum local = 2.8364888e-07, global = 7.6336883e-10, cumulative = -8.9404327e-09
ExecutionTime = 19.25 s  ClockTime = 19 s

Time = 14

smoothSolver:  Solving for Ux, Initial residual = 0.005753392, Final residual = 2.6418568e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 0.0050737313, Final residual = 1.9280581e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.19997712, Final residual = 0.0010456092, No Iterations 9
GAMG:  Solving for p, Initial residual = 0.33846562, Final residual = 0.0031747848, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.078177737, Final residual = 0.00072705952, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.046154654, Final residual = 0.00040285384, No Iterations 4
time step continuity errors : sum local = 4.6083328e-07, global = -1.2900694e-09, cumulative = -1.0230502e-08
ExecutionTime = 20.04 s  ClockTime = 20 s

Time = 15

smoothSolver:  Solving for Ux, Initial residual = 0.0087953502, Final residual = 5.0880268e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 0.0077789964, Final residual = 4.2766571e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.15004517, Final residual = 0.0012748992, No Iterations 9
GAMG:  Solving for p, Initial residual = 0.33131717, Final residual = 0.0024953475, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.074888031, Final residual = 0.00064113792, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.033089587, Final residual = 0.00023546106, No Iterations 14
time step continuity errors : sum local = 2.8925182e-07, global = -3.1452468e-10, cumulative = -1.0545027e-08
ExecutionTime = 21 s  ClockTime = 21 s

Time = 16

smoothSolver:  Solving for Ux, Initial residual = 0.010089885, Final residual = 4.6352762e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 0.0089175362, Final residual = 3.7062073e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.11908111, Final residual = 0.00070332917, No Iterations 16
GAMG:  Solving for p, Initial residual = 0.2331041, Final residual = 0.0010509031, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.051418766, Final residual = 0.00024837205, No Iterations 15
GAMG:  Solving for p, Initial residual = 0.040382368, Final residual = 0.00023301469, No Iterations 3
time step continuity errors : sum local = 2.5394058e-07, global = 1.0316128e-09, cumulative = -9.513414e-09
ExecutionTime = 21.94 s  ClockTime = 22 s

Time = 17

smoothSolver:  Solving for Ux, Initial residual = 0.0088627068, Final residual = 8.5349409e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 0.0078944396, Final residual = 5.8609419e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.13806529, Final residual = 0.0011194606, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.080988817, Final residual = 0.00078441631, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.023771766, Final residual = 0.00021145187, No Iterations 20
GAMG:  Solving for p, Initial residual = 0.04247741, Final residual = 0.00027750526, No Iterations 3
time step continuity errors : sum local = 2.406091e-07, global = 6.8947123e-11, cumulative = -9.4444668e-09
ExecutionTime = 22.78 s  ClockTime = 23 s

Time = 18

smoothSolver:  Solving for Ux, Initial residual = 0.0062262012, Final residual = 8.6390649e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 0.0057433593, Final residual = 5.9865031e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.14764294, Final residual = 0.0012422241, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.16827001, Final residual = 0.0014324147, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.039605788, Final residual = 0.0001484779, No Iterations 20
GAMG:  Solving for p, Initial residual = 0.036536409, Final residual = 0.0001976367, No Iterations 3
time step continuity errors : sum local = 1.5742545e-07, global = -8.5998646e-10, cumulative = -1.0304453e-08
ExecutionTime = 23.66 s  ClockTime = 24 s

Time = 19

smoothSolver:  Solving for Ux, Initial residual = 0.0034881937, Final residual = 5.6137774e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 0.0034489898, Final residual = 3.9974624e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.12941562, Final residual = 0.00052843146, No Iterations 9
GAMG:  Solving for p, Initial residual = 0.23078862, Final residual = 0.0020523026, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.05425843, Final residual = 0.0004665466, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.032603456, Final residual = 0.00023283715, No Iterations 3
time step continuity errors : sum local = 2.0243923e-07, global = 7.7099397e-10, cumulative = -9.5334593e-09
ExecutionTime = 24.32 s  ClockTime = 24 s

Time = 20

smoothSolver:  Solving for Ux, Initial residual = 0.0020897874, Final residual = 1.8542624e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 0.0021225335, Final residual = 9.2456346e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.092385228, Final residual = 0.00080046796, No Iterations 8
GAMG:  Solving for p, Initial residual = 0.20715268, Final residual = 0.0019364034, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.047238383, Final residual = 0.00042224485, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.031962949, Final residual = 0.00028027474, No Iterations 3
time step continuity errors : sum local = 2.4681522e-07, global = -6.2122256e-10, cumulative = -1.0154682e-08
ExecutionTime = 25.03 s  ClockTime = 25 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1300073e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1619913e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0095402

Time = 21

smoothSolver:  Solving for Ux, Initial residual = 0.0023317419, Final residual = 2.9403456e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 0.002172987, Final residual = 2.2057399e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.077056714, Final residual = 0.00075549213, No Iterations 8
GAMG:  Solving for p, Initial residual = 0.12750252, Final residual = 0.00072011681, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.030375372, Final residual = 0.00021933858, No Iterations 17
GAMG:  Solving for p, Initial residual = 0.035088924, Final residual = 0.00019436189, No Iterations 3
time step continuity errors : sum local = 1.6062069e-07, global = -1.1514132e-09, cumulative = -1.1306095e-08
ExecutionTime = 25.9 s  ClockTime = 26 s

Time = 22

smoothSolver:  Solving for Ux, Initial residual = 0.0027350234, Final residual = 4.4929727e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 0.0024685007, Final residual = 3.1042719e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.085409112, Final residual = 0.00074933905, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.061278854, Final residual = 0.00027783175, No Iterations 16
GAMG:  Solving for p, Initial residual = 0.034448959, Final residual = 0.00026840382, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.010437723, Final residual = 4.8117733e-05, No Iterations 18
time step continuity errors : sum local = 3.6252123e-08, global = -6.754641e-11, cumulative = -1.1373642e-08
ExecutionTime = 26.89 s  ClockTime = 27 s

Time = 23

smoothSolver:  Solving for Ux, Initial residual = 0.0026162527, Final residual = 4.3150163e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 0.0023130262, Final residual = 3.1057662e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.085227036, Final residual = 0.00047136619, No Iterations 11
GAMG:  Solving for p, Initial residual = 0.10838367, Final residual = 0.0006426235, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.025223716, Final residual = 0.00011802566, No Iterations 11
GAMG:  Solving for p, Initial residual = 0.018489104, Final residual = 0.0001150241, No Iterations 3
time step continuity errors : sum local = 8.5854616e-08, global = -4.7216417e-10, cumulative = -1.1845806e-08
ExecutionTime = 27.77 s  ClockTime = 28 s

Time = 24

smoothSolver:  Solving for Ux, Initial residual = 0.0020488132, Final residual = 2.6971996e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 0.0018235116, Final residual = 2.0762254e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.070316496, Final residual = 0.00043942536, No Iterations 9
GAMG:  Solving for p, Initial residual = 0.12483018, Final residual = 0.0011898054, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.029656902, Final residual = 0.00023753654, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.019531503, Final residual = 0.00015290718, No Iterations 4
time step continuity errors : sum local = 1.1820325e-07, global = -2.0352767e-10, cumulative = -1.2049333e-08
ExecutionTime = 28.49 s  ClockTime = 29 s

Time = 25

smoothSolver:  Solving for Ux, Initial residual = 0.0013883274, Final residual = 5.7972749e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 0.0012914205, Final residual = 6.5636938e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.050675157, Final residual = 0.00046135686, No Iterations 8
GAMG:  Solving for p, Initial residual = 0.10358978, Final residual = 0.00099369205, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.024409959, Final residual = 0.00023489324, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.017946787, Final residual = 0.00017749754, No Iterations 3
time step continuity errors : sum local = 1.3773555e-07, global = -5.4504876e-10, cumulative = -1.2594382e-08
ExecutionTime = 29.18 s  ClockTime = 29 s

Time = 26

smoothSolver:  Solving for Ux, Initial residual = 0.00090646663, Final residual = 8.6138473e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 0.00091695751, Final residual = 7.5448295e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.045932239, Final residual = 0.00023937536, No Iterations 8
GAMG:  Solving for p, Initial residual = 0.05997807, Final residual = 0.00052016304, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.015158987, Final residual = 0.00014975299, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.010318094, Final residual = 8.7332925e-05, No Iterations 10
time step continuity errors : sum local = 6.5610259e-08, global = -5.6504622e-11, cumulative = -1.2650887e-08
ExecutionTime = 29.96 s  ClockTime = 30 s

Time = 27

smoothSolver:  Solving for Ux, Initial residual = 0.0007683441, Final residual = 2.210637e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 0.00075390378, Final residual = 8.6089341e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.050865795, Final residual = 0.00040212641, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.03535677, Final residual = 0.00024278021, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0093018918, Final residual = 8.528487e-05, No Iterations 15
GAMG:  Solving for p, Initial residual = 0.010645471, Final residual = 8.0867352e-05, No Iterations 3
time step continuity errors : sum local = 5.8409499e-08, global = -1.1523728e-10, cumulative = -1.2766124e-08
ExecutionTime = 30.7 s  ClockTime = 31 s

Time = 28

smoothSolver:  Solving for Ux, Initial residual = 0.00078306138, Final residual = 1.961928e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 0.00074781989, Final residual = 7.3898036e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.050123595, Final residual = 0.00036968224, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.053868202, Final residual = 0.00035674535, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.013524517, Final residual = 7.8268342e-05, No Iterations 13
GAMG:  Solving for p, Initial residual = 0.010608061, Final residual = 7.2814141e-05, No Iterations 11
time step continuity errors : sum local = 5.2574299e-08, global = -6.2028261e-11, cumulative = -1.2828152e-08
ExecutionTime = 31.57 s  ClockTime = 32 s

Time = 29

smoothSolver:  Solving for Ux, Initial residual = 0.00076323666, Final residual = 6.1596783e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 0.00071016017, Final residual = 4.5508081e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.041380029, Final residual = 0.00020922367, No Iterations 10
GAMG:  Solving for p, Initial residual = 0.061795243, Final residual = 0.00058799542, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.014890213, Final residual = 0.00014516733, No Iterations 11
GAMG:  Solving for p, Initial residual = 0.01141082, Final residual = 7.7765965e-05, No Iterations 3
time step continuity errors : sum local = 5.687487e-08, global = -4.5613053e-12, cumulative = -1.2832714e-08
ExecutionTime = 32.33 s  ClockTime = 32 s

Time = 30

smoothSolver:  Solving for Ux, Initial residual = 0.00065866006, Final residual = 3.3372562e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 0.00058859801, Final residual = 3.0606368e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.031651484, Final residual = 0.00024063288, No Iterations 8
GAMG:  Solving for p, Initial residual = 0.051940254, Final residual = 0.00049015344, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.012333707, Final residual = 0.00010747825, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0088975297, Final residual = 6.9991294e-05, No Iterations 3
time step continuity errors : sum local = 5.111486e-08, global = 2.0412989e-10, cumulative = -1.2628584e-08
ExecutionTime = 33 s  ClockTime = 33 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1309213e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1611981e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0130048

Time = 31

smoothSolver:  Solving for Ux, Initial residual = 0.00050160177, Final residual = 4.7567017e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 0.00044220622, Final residual = 3.5775683e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.028776115, Final residual = 0.00026933467, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.031007226, Final residual = 0.00015902608, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0087011587, Final residual = 7.4130086e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0041792306, Final residual = 3.9338348e-05, No Iterations 3
time step continuity errors : sum local = 2.8334115e-08, global = 1.1807385e-10, cumulative = -1.251051e-08
ExecutionTime = 33.65 s  ClockTime = 34 s

Time = 32

smoothSolver:  Solving for Ux, Initial residual = 0.00035529051, Final residual = 5.8953941e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 0.00033943875, Final residual = 4.0567345e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.029892135, Final residual = 0.00023312068, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.020584406, Final residual = 0.00012301971, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0055708179, Final residual = 4.5916097e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0028899475, Final residual = 1.4482372e-05, No Iterations 14
time step continuity errors : sum local = 1.0278745e-08, global = 1.7910181e-11, cumulative = -1.24926e-08
ExecutionTime = 34.41 s  ClockTime = 35 s

Time = 33

smoothSolver:  Solving for Ux, Initial residual = 0.00027050721, Final residual = 5.2783913e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 0.00027876388, Final residual = 3.7034907e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.028540976, Final residual = 0.00021622156, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.025850651, Final residual = 0.00025451705, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0061259758, Final residual = 3.7637708e-05, No Iterations 11
GAMG:  Solving for p, Initial residual = 0.0049919017, Final residual = 2.0534973e-05, No Iterations 9
time step continuity errors : sum local = 1.4531835e-08, global = 1.4148977e-11, cumulative = -1.2478451e-08
ExecutionTime = 35.23 s  ClockTime = 35 s

Time = 34

smoothSolver:  Solving for Ux, Initial residual = 0.00024940854, Final residual = 3.5565167e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 0.00025149909, Final residual = 2.7368334e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.023906473, Final residual = 0.00018473149, No Iterations 8
GAMG:  Solving for p, Initial residual = 0.028334597, Final residual = 0.00017529668, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00660435, Final residual = 6.5469619e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0053338931, Final residual = 3.1847214e-05, No Iterations 7
time step continuity errors : sum local = 2.2590613e-08, global = 2.9107871e-11, cumulative = -1.2449343e-08
ExecutionTime = 35.95 s  ClockTime = 36 s

Time = 35

smoothSolver:  Solving for Ux, Initial residual = 0.00023373439, Final residual = 2.2552638e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 0.0002267052, Final residual = 2.1944568e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.019372711, Final residual = 0.0001158079, No Iterations 9
GAMG:  Solving for p, Initial residual = 0.024450286, Final residual = 0.00024243364, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0054353353, Final residual = 5.2476725e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0039245152, Final residual = 3.3425949e-05, No Iterations 3
time step continuity errors : sum local = 2.3726681e-08, global = 5.8630282e-11, cumulative = -1.2390713e-08
ExecutionTime = 36.64 s  ClockTime = 37 s

Time = 36

smoothSolver:  Solving for Ux, Initial residual = 0.00020416848, Final residual = 2.2729355e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 0.00019225168, Final residual = 2.2181826e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.017720282, Final residual = 0.00014301986, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.015327465, Final residual = 9.910113e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0034587387, Final residual = 1.6260993e-05, No Iterations 13
GAMG:  Solving for p, Initial residual = 0.0032058446, Final residual = 1.7112621e-05, No Iterations 3
time step continuity errors : sum local = 1.2125749e-08, global = 1.5487052e-11, cumulative = -1.2375226e-08
ExecutionTime = 37.42 s  ClockTime = 38 s

Time = 37

smoothSolver:  Solving for Ux, Initial residual = 0.00016701579, Final residual = 2.6226804e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 0.00015295554, Final residual = 2.3081339e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.017846046, Final residual = 0.00010198868, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0099337781, Final residual = 4.2390269e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0024399709, Final residual = 2.0367733e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0010554395, Final residual = 3.0766359e-06, No Iterations 20
time step continuity errors : sum local = 2.1773075e-09, global = -3.4852302e-12, cumulative = -1.2378711e-08
ExecutionTime = 38.29 s  ClockTime = 38 s

Time = 38

smoothSolver:  Solving for Ux, Initial residual = 0.00013216152, Final residual = 2.4829363e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 0.00012443068, Final residual = 2.0994924e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.01736938, Final residual = 0.00017330221, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.010129502, Final residual = 9.5316082e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0023861363, Final residual = 2.3236075e-05, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.0022619587, Final residual = 1.5092082e-05, No Iterations 3
time step continuity errors : sum local = 1.0685978e-08, global = 2.7716343e-11, cumulative = -1.2350994e-08
ExecutionTime = 38.94 s  ClockTime = 39 s

Time = 39

smoothSolver:  Solving for Ux, Initial residual = 0.0001097421, Final residual = 1.961886e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 0.00010772295, Final residual = 9.0963717e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.015471187, Final residual = 0.00014757737, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.012283353, Final residual = 8.0476224e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0028499196, Final residual = 1.4718218e-05, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.0023221701, Final residual = 1.208391e-05, No Iterations 3
time step continuity errors : sum local = 8.5737919e-09, global = 3.2115061e-11, cumulative = -1.2318879e-08
ExecutionTime = 39.63 s  ClockTime = 40 s

Time = 40

smoothSolver:  Solving for Ux, Initial residual = 9.8746734e-05, Final residual = 8.7684921e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.409662e-05, Final residual = 7.6404195e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.013076638, Final residual = 0.00012719075, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.011814118, Final residual = 8.8555638e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0028243382, Final residual = 2.1955417e-05, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.0024187615, Final residual = 1.5300611e-05, No Iterations 3
time step continuity errors : sum local = 1.0866481e-08, global = 2.4208347e-11, cumulative = -1.2294671e-08
ExecutionTime = 40.27 s  ClockTime = 40 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1307068e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1613863e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0100043

Time = 41

smoothSolver:  Solving for Ux, Initial residual = 9.1897775e-05, Final residual = 9.0664489e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 8.4435233e-05, Final residual = 7.5624614e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.011506443, Final residual = 0.00011273397, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.0091989848, Final residual = 7.6468516e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0022293956, Final residual = 1.3459097e-05, No Iterations 9
GAMG:  Solving for p, Initial residual = 0.002206086, Final residual = 9.7511526e-06, No Iterations 3
time step continuity errors : sum local = 6.9192332e-09, global = 1.8957614e-11, cumulative = -1.2275713e-08
ExecutionTime = 40.95 s  ClockTime = 41 s

Time = 42

smoothSolver:  Solving for Ux, Initial residual = 8.2574645e-05, Final residual = 1.8591398e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 7.4997819e-05, Final residual = 7.8457683e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.011108063, Final residual = 4.0159033e-05, No Iterations 8
GAMG:  Solving for p, Initial residual = 0.0063602902, Final residual = 5.6941906e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0014898399, Final residual = 1.1621538e-05, No Iterations 11
GAMG:  Solving for p, Initial residual = 0.0010789928, Final residual = 7.9131035e-06, No Iterations 3
time step continuity errors : sum local = 5.6043599e-09, global = 1.8600355e-11, cumulative = -1.2257113e-08
ExecutionTime = 41.69 s  ClockTime = 42 s

Time = 43

smoothSolver:  Solving for Ux, Initial residual = 7.0097436e-05, Final residual = 1.9009002e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 6.3901984e-05, Final residual = 7.6948158e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.010818763, Final residual = 7.3411419e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0053166508, Final residual = 3.8728262e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0013916179, Final residual = 1.2724268e-05, No Iterations 9
GAMG:  Solving for p, Initial residual = 0.00095801806, Final residual = 7.2628545e-06, No Iterations 3
time step continuity errors : sum local = 5.136244e-09, global = 1.6835902e-11, cumulative = -1.2240277e-08
ExecutionTime = 42.39 s  ClockTime = 43 s

Time = 44

smoothSolver:  Solving for Ux, Initial residual = 5.913251e-05, Final residual = 9.4407734e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 5.4049839e-05, Final residual = 7.0888917e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0098850992, Final residual = 5.6088341e-05, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.0056918101, Final residual = 5.5332244e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0012715806, Final residual = 9.7170292e-06, No Iterations 9
GAMG:  Solving for p, Initial residual = 0.00098959413, Final residual = 6.367392e-06, No Iterations 3
time step continuity errors : sum local = 4.5004281e-09, global = 1.537563e-11, cumulative = -1.2224901e-08
ExecutionTime = 43.06 s  ClockTime = 43 s

Time = 45

smoothSolver:  Solving for Ux, Initial residual = 5.075644e-05, Final residual = 8.2438639e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 4.6258192e-05, Final residual = 6.4097511e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0085941761, Final residual = 4.7058201e-05, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.0055639421, Final residual = 4.4430092e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0012558854, Final residual = 9.6404405e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00082420827, Final residual = 6.2551584e-06, No Iterations 3
time step continuity errors : sum local = 4.4207702e-09, global = 1.2327201e-11, cumulative = -1.2212574e-08
ExecutionTime = 43.71 s  ClockTime = 44 s

Time = 46

smoothSolver:  Solving for Ux, Initial residual = 4.3985016e-05, Final residual = 7.355268e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 4.0509236e-05, Final residual = 6.044271e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0076076774, Final residual = 3.6528133e-05, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.0047020769, Final residual = 3.4280014e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0010358735, Final residual = 6.6371027e-06, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.00069360856, Final residual = 4.7069114e-06, No Iterations 3
time step continuity errors : sum local = 3.3281017e-09, global = 9.748363e-12, cumulative = -1.2202826e-08
ExecutionTime = 44.35 s  ClockTime = 45 s

Time = 47

smoothSolver:  Solving for Ux, Initial residual = 3.7962251e-05, Final residual = 6.9506073e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 3.5523571e-05, Final residual = 5.9072438e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0071519542, Final residual = 6.3721366e-05, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.0034675607, Final residual = 2.8080412e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00080756065, Final residual = 7.3065192e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00054442629, Final residual = 5.1486111e-06, No Iterations 3
time step continuity errors : sum local = 3.6418164e-09, global = 1.3838018e-11, cumulative = -1.2188988e-08
ExecutionTime = 45.01 s  ClockTime = 45 s

Time = 48

smoothSolver:  Solving for Ux, Initial residual = 3.2298328e-05, Final residual = 6.7576211e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 3.0410595e-05, Final residual = 5.807669e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0069667889, Final residual = 4.3394911e-05, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.0028610883, Final residual = 1.5810324e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00067780326, Final residual = 2.670832e-06, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.00036875475, Final residual = 2.9678716e-06, No Iterations 3
time step continuity errors : sum local = 2.1008126e-09, global = 8.3002762e-12, cumulative = -1.2180688e-08
ExecutionTime = 45.68 s  ClockTime = 46 s

Time = 49

smoothSolver:  Solving for Ux, Initial residual = 2.6978963e-05, Final residual = 6.6270143e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.5254449e-05, Final residual = 5.6538803e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0067023481, Final residual = 5.1446414e-05, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.0025915068, Final residual = 2.3199792e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00072445455, Final residual = 6.1326366e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00041464255, Final residual = 1.8701091e-06, No Iterations 6
time step continuity errors : sum local = 1.3245451e-09, global = -2.6407045e-12, cumulative = -1.2183328e-08
ExecutionTime = 46.37 s  ClockTime = 47 s

Time = 50

smoothSolver:  Solving for Ux, Initial residual = 2.2372483e-05, Final residual = 6.5494405e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.0542802e-05, Final residual = 5.5029306e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0062104901, Final residual = 5.5463632e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0025696261, Final residual = 2.5144529e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0007896085, Final residual = 3.5103637e-06, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.0005248969, Final residual = 3.6439409e-06, No Iterations 3
time step continuity errors : sum local = 2.5807914e-09, global = -5.8281497e-12, cumulative = -1.2189156e-08
ExecutionTime = 47.45 s  ClockTime = 48 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1306168e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614719e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098571

Time = 51

smoothSolver:  Solving for Ux, Initial residual = 1.893065e-05, Final residual = 6.5433961e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.7280262e-05, Final residual = 5.3936525e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0056471167, Final residual = 3.6168118e-05, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.0024506475, Final residual = 2.0251806e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00073047711, Final residual = 5.0781977e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00040592975, Final residual = 3.9154775e-06, No Iterations 3
time step continuity errors : sum local = 2.7727012e-09, global = -3.1953485e-12, cumulative = -1.2192352e-08
ExecutionTime = 48.09 s  ClockTime = 48 s

Time = 52

smoothSolver:  Solving for Ux, Initial residual = 1.6381875e-05, Final residual = 6.5632232e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.535344e-05, Final residual = 5.3161075e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0052095042, Final residual = 4.994582e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0018336919, Final residual = 1.059631e-05, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.00086654696, Final residual = 7.4038789e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00027053017, Final residual = 2.1360599e-06, No Iterations 6
time step continuity errors : sum local = 1.512703e-09, global = -1.9214262e-12, cumulative = -1.2194273e-08
ExecutionTime = 48.78 s  ClockTime = 49 s

Time = 53

smoothSolver:  Solving for Ux, Initial residual = 1.4431791e-05, Final residual = 6.549541e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.363042e-05, Final residual = 5.2307884e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0049327437, Final residual = 3.6781371e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0016438202, Final residual = 1.4143064e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00043645848, Final residual = 3.6264439e-06, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.00034085742, Final residual = 2.7096828e-06, No Iterations 3
time step continuity errors : sum local = 1.9181182e-09, global = -3.935817e-12, cumulative = -1.2198209e-08
ExecutionTime = 49.39 s  ClockTime = 50 s

Time = 54

smoothSolver:  Solving for Ux, Initial residual = 1.2666873e-05, Final residual = 6.457932e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1873082e-05, Final residual = 5.1070074e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0047093819, Final residual = 4.5424076e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0014684357, Final residual = 1.4236864e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00038996894, Final residual = 2.7373918e-06, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.0002743217, Final residual = 1.857931e-06, No Iterations 3
time step continuity errors : sum local = 1.3149842e-09, global = -3.3182153e-12, cumulative = -1.2201527e-08
ExecutionTime = 50.1 s  ClockTime = 50 s

Time = 55

smoothSolver:  Solving for Ux, Initial residual = 1.1007526e-05, Final residual = 6.2991621e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0318071e-05, Final residual = 4.9599202e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.004460296, Final residual = 3.7792112e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0013743611, Final residual = 1.1780475e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00045774795, Final residual = 4.2576387e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00017265313, Final residual = 1.3409828e-06, No Iterations 6
time step continuity errors : sum local = 9.4968921e-10, global = -2.741885e-12, cumulative = -1.2204269e-08
ExecutionTime = 50.77 s  ClockTime = 51 s

Time = 56

smoothSolver:  Solving for Ux, Initial residual = 9.4934359e-06, Final residual = 6.1106609e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 8.8141218e-06, Final residual = 4.818752e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0041919583, Final residual = 2.4583382e-05, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.0013862892, Final residual = 7.2166753e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00035291932, Final residual = 2.3312007e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00019704235, Final residual = 1.8063595e-06, No Iterations 3
time step continuity errors : sum local = 1.2786387e-09, global = 2.2937371e-12, cumulative = -1.2201975e-08
ExecutionTime = 51.43 s  ClockTime = 52 s

Time = 57

smoothSolver:  Solving for Ux, Initial residual = 8.2898639e-06, Final residual = 5.9320143e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 7.6464492e-06, Final residual = 4.7086524e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0039645909, Final residual = 1.4229009e-05, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.0012212192, Final residual = 7.806843e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0003216193, Final residual = 2.8414543e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00022076194, Final residual = 1.9193626e-06, No Iterations 3
time step continuity errors : sum local = 1.3584558e-09, global = 1.9963178e-12, cumulative = -1.2199979e-08
ExecutionTime = 52.05 s  ClockTime = 52 s

Time = 58

smoothSolver:  Solving for Ux, Initial residual = 7.2074724e-06, Final residual = 5.7840307e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 6.6040099e-06, Final residual = 4.6329749e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0037986493, Final residual = 2.4565452e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0010077113, Final residual = 5.3676051e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00035692371, Final residual = 1.5029536e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00017044468, Final residual = 1.3134253e-06, No Iterations 3
time step continuity errors : sum local = 9.2977918e-10, global = 8.0950041e-13, cumulative = -1.219917e-08
ExecutionTime = 52.73 s  ClockTime = 53 s

Time = 59

smoothSolver:  Solving for Ux, Initial residual = 6.208831e-06, Final residual = 5.6713988e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 5.5870204e-06, Final residual = 4.5764109e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0036697809, Final residual = 3.2292018e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00085529744, Final residual = 8.4607729e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00033319227, Final residual = 1.3307969e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00015442495, Final residual = 1.1475212e-06, No Iterations 3
time step continuity errors : sum local = 8.13094e-10, global = 8.7371061e-13, cumulative = -1.2198296e-08
ExecutionTime = 53.38 s  ClockTime = 54 s

Time = 60

smoothSolver:  Solving for Ux, Initial residual = 5.3262123e-06, Final residual = 5.5909922e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 4.7391985e-06, Final residual = 4.5290344e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0035473741, Final residual = 2.531806e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00079181297, Final residual = 1.6775826e-06, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.00032273039, Final residual = 2.2572984e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00011932951, Final residual = 6.2014076e-07, No Iterations 8
time step continuity errors : sum local = 4.3961758e-10, global = 5.4461148e-13, cumulative = -1.2197751e-08
ExecutionTime = 54.1 s  ClockTime = 54 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305968e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614928e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 61

smoothSolver:  Solving for Ux, Initial residual = 4.626828e-06, Final residual = 5.5316577e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 4.0723466e-06, Final residual = 4.4835252e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0034183806, Final residual = 2.1663242e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00072945663, Final residual = 6.9406801e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00029438582, Final residual = 1.944961e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00011289888, Final residual = 1.0193369e-06, No Iterations 4
time step continuity errors : sum local = 7.2230541e-10, global = -1.3506676e-12, cumulative = -1.2199102e-08
ExecutionTime = 54.75 s  ClockTime = 55 s

Time = 62

smoothSolver:  Solving for Ux, Initial residual = 4.0680304e-06, Final residual = 5.4812235e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 3.5187697e-06, Final residual = 4.4352943e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0032914283, Final residual = 1.8931238e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00065831782, Final residual = 3.3511216e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00025811271, Final residual = 1.3154554e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0001142109, Final residual = 9.4082363e-07, No Iterations 3
time step continuity errors : sum local = 6.665264e-10, global = -1.1388585e-12, cumulative = -1.2200241e-08
ExecutionTime = 55.39 s  ClockTime = 56 s

Time = 63

smoothSolver:  Solving for Ux, Initial residual = 3.5995613e-06, Final residual = 5.4260931e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 3.0243783e-06, Final residual = 4.3779319e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0031731023, Final residual = 1.692457e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00059940478, Final residual = 2.089591e-06, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.00024592112, Final residual = 7.7243853e-07, No Iterations 8
GAMG:  Solving for p, Initial residual = 0.00010743395, Final residual = 7.6324991e-07, No Iterations 3
time step continuity errors : sum local = 5.4119717e-10, global = -7.7562553e-13, cumulative = -1.2201016e-08
ExecutionTime = 56.1 s  ClockTime = 56 s

Time = 64

smoothSolver:  Solving for Ux, Initial residual = 3.1660249e-06, Final residual = 5.3612663e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.6008423e-06, Final residual = 4.3114585e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0030632253, Final residual = 2.9741868e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00053929688, Final residual = 3.5791085e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0002390854, Final residual = 1.1652591e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00010041647, Final residual = 5.9150662e-07, No Iterations 8
time step continuity errors : sum local = 4.1954481e-10, global = -3.7156349e-13, cumulative = -1.2201388e-08
ExecutionTime = 56.81 s  ClockTime = 57 s

Time = 65

smoothSolver:  Solving for Ux, Initial residual = 2.8015055e-06, Final residual = 5.2892707e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.2355254e-06, Final residual = 4.2406735e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0029654612, Final residual = 2.5890225e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00050959573, Final residual = 1.2718383e-06, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.00024371826, Final residual = 2.2582763e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.2908274e-05, Final residual = 4.4669166e-07, No Iterations 5
time step continuity errors : sum local = 3.1741109e-10, global = -6.8478701e-13, cumulative = -1.2202073e-08
ExecutionTime = 57.49 s  ClockTime = 58 s

Time = 66

smoothSolver:  Solving for Ux, Initial residual = 2.4822786e-06, Final residual = 5.2117846e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.930262e-06, Final residual = 4.1693107e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0028801866, Final residual = 2.2366608e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0004817087, Final residual = 4.6268763e-06, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.00024807874, Final residual = 1.1030811e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.6358569e-05, Final residual = 5.4361939e-07, No Iterations 4
time step continuity errors : sum local = 3.8559789e-10, global = 2.1055065e-13, cumulative = -1.2201862e-08
ExecutionTime = 58.12 s  ClockTime = 58 s

Time = 67

smoothSolver:  Solving for Ux, Initial residual = 2.1891165e-06, Final residual = 5.1330368e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.6755934e-06, Final residual = 4.1013014e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0028055625, Final residual = 1.9350534e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00045515978, Final residual = 1.3227217e-06, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.00022107881, Final residual = 1.0549605e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.8925679e-05, Final residual = 4.0567322e-07, No Iterations 5
time step continuity errors : sum local = 2.8802632e-10, global = 3.226659e-13, cumulative = -1.220154e-08
ExecutionTime = 58.75 s  ClockTime = 59 s

Time = 68

smoothSolver:  Solving for Ux, Initial residual = 1.9369762e-06, Final residual = 5.0561411e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.4917672e-06, Final residual = 4.040595e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0027363506, Final residual = 1.7260196e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00043211229, Final residual = 2.950066e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00019107476, Final residual = 1.5755066e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.4260742e-05, Final residual = 4.515851e-07, No Iterations 5
time step continuity errors : sum local = 3.2064096e-10, global = 1.4350179e-13, cumulative = -1.2201396e-08
ExecutionTime = 59.44 s  ClockTime = 60 s

Time = 69

smoothSolver:  Solving for Ux, Initial residual = 1.7248049e-06, Final residual = 4.9843475e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.3318607e-06, Final residual = 3.9878099e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0026701595, Final residual = 1.6037687e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00041355897, Final residual = 2.5219099e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00017255151, Final residual = 1.3631379e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.9828835e-05, Final residual = 2.971585e-07, No Iterations 6
time step continuity errors : sum local = 2.1171653e-10, global = 3.0198039e-13, cumulative = -1.2201094e-08
ExecutionTime = 60.14 s  ClockTime = 60 s

Time = 70

smoothSolver:  Solving for Ux, Initial residual = 1.5343312e-06, Final residual = 4.9185418e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1993354e-06, Final residual = 3.9412461e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0026056751, Final residual = 1.4713712e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00039739328, Final residual = 2.9420545e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00016172493, Final residual = 1.0268173e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.6019723e-05, Final residual = 3.7500371e-07, No Iterations 5
time step continuity errors : sum local = 2.6648067e-10, global = 3.6557112e-13, cumulative = -1.2200729e-08
ExecutionTime = 60.76 s  ClockTime = 61 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.130595e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614945e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098918

Time = 71

smoothSolver:  Solving for Ux, Initial residual = 1.3564382e-06, Final residual = 4.8583876e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0725046e-06, Final residual = 3.8993235e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0025434819, Final residual = 1.3128345e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00038126723, Final residual = 1.6784474e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00014842038, Final residual = 4.5085357e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.4812107e-05, Final residual = 5.1886797e-07, No Iterations 3
time step continuity errors : sum local = 3.6821499e-10, global = 7.3287346e-13, cumulative = -1.2199996e-08
ExecutionTime = 61.35 s  ClockTime = 62 s

Time = 72

smoothSolver:  Solving for Ux, Initial residual = 1.1905105e-06, Final residual = 4.8022732e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.554784e-07, Final residual = 3.8589734e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0024854136, Final residual = 1.1702651e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00036704833, Final residual = 1.145448e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00013790013, Final residual = 1.2463504e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.9600457e-05, Final residual = 4.2165836e-07, No Iterations 4
time step continuity errors : sum local = 2.9917591e-10, global = 1.8968147e-13, cumulative = -1.2199806e-08
ExecutionTime = 61.97 s  ClockTime = 62 s

Time = 73

smoothSolver:  Solving for Ux, Initial residual = 1.0472728e-06, Final residual = 4.7481711e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 8.4551163e-07, Final residual = 3.8178795e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0024314565, Final residual = 1.0675068e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00035406003, Final residual = 2.2758247e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00013216711, Final residual = 4.3438027e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.9626339e-05, Final residual = 2.9765524e-07, No Iterations 5
time step continuity errors : sum local = 2.1145019e-10, global = 2.3207839e-13, cumulative = -1.2199574e-08
ExecutionTime = 62.64 s  ClockTime = 63 s

Time = 74

smoothSolver:  Solving for Ux, Initial residual = 9.2495102e-07, Final residual = 4.6949905e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 7.404768e-07, Final residual = 3.7750136e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.002380465, Final residual = 1.022558e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00034216878, Final residual = 2.3675547e-06, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.00012969324, Final residual = 8.1178619e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.5937309e-05, Final residual = 5.1620268e-07, No Iterations 11
time step continuity errors : sum local = 3.6620105e-10, global = 2.2139263e-13, cumulative = -1.2199353e-08
ExecutionTime = 63.36 s  ClockTime = 64 s

Time = 75

smoothSolver:  Solving for Ux, Initial residual = 8.0752617e-07, Final residual = 4.6422434e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 6.3799302e-07, Final residual = 3.7307405e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0023320032, Final residual = 1.0110083e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00033032692, Final residual = 2.469834e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00013055691, Final residual = 1.0164316e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.525284e-05, Final residual = 4.6237782e-07, No Iterations 11
time step continuity errors : sum local = 3.2833424e-10, global = -2.2670892e-13, cumulative = -1.2199579e-08
ExecutionTime = 64.46 s  ClockTime = 65 s

Time = 76

smoothSolver:  Solving for Ux, Initial residual = 6.9930314e-07, Final residual = 4.588764e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 5.5030512e-07, Final residual = 3.6851441e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0022849083, Final residual = 9.8439639e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0003189648, Final residual = 3.1404235e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00012018706, Final residual = 8.625277e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.5338349e-05, Final residual = 4.8793166e-07, No Iterations 5
time step continuity errors : sum local = 3.4652984e-10, global = -3.1272348e-13, cumulative = -1.2199892e-08
ExecutionTime = 65.27 s  ClockTime = 66 s

Time = 77

smoothSolver:  Solving for Ux, Initial residual = 6.0545891e-07, Final residual = 4.5358176e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 4.7207278e-07, Final residual = 3.6406559e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0022405846, Final residual = 9.3182321e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0003092057, Final residual = 3.0070121e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00011866919, Final residual = 9.1081836e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.4298464e-05, Final residual = 1.6244386e-07, No Iterations 5
time step continuity errors : sum local = 1.1616684e-10, global = 2.584765e-13, cumulative = -1.2199633e-08
ExecutionTime = 66.07 s  ClockTime = 66 s

Time = 78

smoothSolver:  Solving for Ux, Initial residual = 5.3444445e-07, Final residual = 4.4834755e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 4.0254425e-07, Final residual = 3.5976351e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0021984816, Final residual = 8.6631904e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00030198394, Final residual = 2.8961283e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00011539424, Final residual = 1.110743e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.9422065e-05, Final residual = 4.8755264e-07, No Iterations 6
time step continuity errors : sum local = 3.4624856e-10, global = 4.3834195e-13, cumulative = -1.2199195e-08
ExecutionTime = 66.82 s  ClockTime = 67 s

Time = 79

smoothSolver:  Solving for Ux, Initial residual = 4.7197342e-07, Final residual = 4.4320405e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 3.4730516e-07, Final residual = 3.5568636e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0021577261, Final residual = 8.0080329e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00029467744, Final residual = 2.7595151e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00011179057, Final residual = 1.0643299e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.8082507e-05, Final residual = 2.3499076e-07, No Iterations 4
time step continuity errors : sum local = 1.6732184e-10, global = 2.5343695e-13, cumulative = -1.2198942e-08
ExecutionTime = 67.5 s  ClockTime = 68 s

Time = 80

smoothSolver:  Solving for Ux, Initial residual = 4.2159093e-07, Final residual = 4.3823838e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 3.0331711e-07, Final residual = 3.5183379e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0021178084, Final residual = 7.4087444e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00028752058, Final residual = 2.6127338e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00010800766, Final residual = 6.3548913e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.9500249e-05, Final residual = 2.0430525e-07, No Iterations 5
time step continuity errors : sum local = 1.4573291e-10, global = -3.8976999e-14, cumulative = -1.2198981e-08
ExecutionTime = 68.16 s  ClockTime = 69 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305949e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614946e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098913

Time = 81

smoothSolver:  Solving for Ux, Initial residual = 3.7870557e-07, Final residual = 4.3340379e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.7032133e-07, Final residual = 3.4813116e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.002079487, Final residual = 2.0232574e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00027757934, Final residual = 8.8308949e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0001133262, Final residual = 1.0875978e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.7150986e-05, Final residual = 2.5438755e-07, No Iterations 5
time step continuity errors : sum local = 1.8130283e-10, global = 1.9486824e-13, cumulative = -1.2198786e-08
ExecutionTime = 68.84 s  ClockTime = 69 s

Time = 82

smoothSolver:  Solving for Ux, Initial residual = 3.3934917e-07, Final residual = 4.2873617e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.4206588e-07, Final residual = 3.4455134e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0020430522, Final residual = 1.9234759e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00027147566, Final residual = 7.2553703e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00010995713, Final residual = 1.0113026e-06, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.8801214e-05, Final residual = 2.0380797e-07, No Iterations 6
time step continuity errors : sum local = 1.4550597e-10, global = -2.5028959e-14, cumulative = -1.2198811e-08
ExecutionTime = 69.56 s  ClockTime = 70 s

Time = 83

smoothSolver:  Solving for Ux, Initial residual = 3.1199146e-07, Final residual = 4.2418583e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.2489109e-07, Final residual = 3.4099343e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0020078629, Final residual = 1.8247952e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00026674421, Final residual = 6.3433439e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0001072607, Final residual = 8.3031733e-07, No Iterations 8
GAMG:  Solving for p, Initial residual = 4.783291e-05, Final residual = 4.2530155e-07, No Iterations 4
time step continuity errors : sum local = 3.0215119e-10, global = 4.9273872e-13, cumulative = -1.2198318e-08
ExecutionTime = 70.23 s  ClockTime = 71 s

Time = 84

smoothSolver:  Solving for Ux, Initial residual = 2.8877555e-07, Final residual = 4.1981204e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.140718e-07, Final residual = 3.3750299e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0019741449, Final residual = 1.7304041e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0002620956, Final residual = 2.4456266e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00010457284, Final residual = 3.1373514e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.4954202e-05, Final residual = 4.4841846e-07, No Iterations 9
time step continuity errors : sum local = 3.1857712e-10, global = 4.3779681e-13, cumulative = -1.219788e-08
ExecutionTime = 71.05 s  ClockTime = 71 s

Time = 85

smoothSolver:  Solving for Ux, Initial residual = 2.6570164e-07, Final residual = 4.1555542e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.0178457e-07, Final residual = 3.3402338e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0019419706, Final residual = 1.6457751e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00025716169, Final residual = 2.2411022e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00010309359, Final residual = 7.2949804e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.4928621e-05, Final residual = 2.3960985e-07, No Iterations 3
time step continuity errors : sum local = 1.7115851e-10, global = 3.6356443e-13, cumulative = -1.2197517e-08
ExecutionTime = 71.63 s  ClockTime = 72 s

Time = 86

smoothSolver:  Solving for Ux, Initial residual = 2.431897e-07, Final residual = 4.1137106e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.8781718e-07, Final residual = 3.3052665e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0019107603, Final residual = 1.5791856e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00025231498, Final residual = 2.1395201e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00010185798, Final residual = 8.4906144e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.379347e-05, Final residual = 2.1481495e-07, No Iterations 3
time step continuity errors : sum local = 1.5340558e-10, global = 2.5792839e-14, cumulative = -1.2197491e-08
ExecutionTime = 72.37 s  ClockTime = 73 s

Time = 87

smoothSolver:  Solving for Ux, Initial residual = 2.2091028e-07, Final residual = 4.0727404e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.7344548e-07, Final residual = 3.2706198e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0018807201, Final residual = 1.5361528e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00024775015, Final residual = 2.0749401e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00010125484, Final residual = 9.2498545e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.2870182e-05, Final residual = 2.2873351e-07, No Iterations 3
time step continuity errors : sum local = 1.6306671e-10, global = -7.1034603e-15, cumulative = -1.2197498e-08
ExecutionTime = 73 s  ClockTime = 73 s

Time = 88

smoothSolver:  Solving for Ux, Initial residual = 1.9862609e-07, Final residual = 4.0324438e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.5759063e-07, Final residual = 3.2365826e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0018518764, Final residual = 1.5083346e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00024366126, Final residual = 2.0411309e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.000100394, Final residual = 9.6411125e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1361777e-05, Final residual = 3.9109019e-07, No Iterations 8
time step continuity errors : sum local = 2.7811801e-10, global = 1.5831132e-13, cumulative = -1.219734e-08
ExecutionTime = 73.83 s  ClockTime = 74 s

Time = 89

smoothSolver:  Solving for Ux, Initial residual = 1.7731654e-07, Final residual = 3.9929175e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.4072196e-07, Final residual = 3.2031506e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0018240703, Final residual = 1.4888562e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0002402839, Final residual = 1.9431031e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.890327e-05, Final residual = 7.3312077e-07, No Iterations 7
GAMG:  Solving for p, Initial residual = 4.2131684e-05, Final residual = 3.9600161e-07, No Iterations 7
time step continuity errors : sum local = 2.8134032e-10, global = 1.0468441e-13, cumulative = -1.2197235e-08
ExecutionTime = 74.84 s  ClockTime = 75 s

Time = 90

smoothSolver:  Solving for Ux, Initial residual = 1.5730732e-07, Final residual = 3.9540476e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2391511e-07, Final residual = 3.1707217e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0017971612, Final residual = 1.4666868e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00023728766, Final residual = 1.8881439e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.7056658e-05, Final residual = 8.2856724e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.1604498e-05, Final residual = 3.8438863e-07, No Iterations 5
time step continuity errors : sum local = 2.7308299e-10, global = 1.0407341e-13, cumulative = -1.2197131e-08
ExecutionTime = 75.5 s  ClockTime = 76 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305953e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614942e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098911

Time = 91

smoothSolver:  Solving for Ux, Initial residual = 1.4033139e-07, Final residual = 3.9157589e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0829853e-07, Final residual = 3.1391351e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0017710858, Final residual = 1.4402179e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00023423957, Final residual = 1.8191929e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.4611846e-05, Final residual = 5.8991059e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.0247379e-05, Final residual = 3.9344692e-07, No Iterations 5
time step continuity errors : sum local = 2.7962728e-10, global = 1.470225e-13, cumulative = -1.2196984e-08
ExecutionTime = 76.24 s  ClockTime = 77 s

Time = 92

smoothSolver:  Solving for Ux, Initial residual = 1.2635211e-07, Final residual = 3.8782189e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.4124121e-08, Final residual = 3.1083719e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0017459325, Final residual = 1.4087864e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00023167778, Final residual = 1.8057852e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.2349342e-05, Final residual = 5.7055723e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.9919371e-05, Final residual = 3.5829731e-07, No Iterations 7
time step continuity errors : sum local = 2.5473463e-10, global = 2.2733889e-13, cumulative = -1.2196757e-08
ExecutionTime = 76.96 s  ClockTime = 77 s

Time = 93

smoothSolver:  Solving for Ux, Initial residual = 1.1286617e-07, Final residual = 3.8415802e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 8.2512064e-08, Final residual = 3.0784458e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0017213449, Final residual = 1.3734749e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00022924844, Final residual = 1.7757342e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.1789793e-05, Final residual = 5.8351915e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.0220138e-05, Final residual = 1.5747447e-07, No Iterations 5
time step continuity errors : sum local = 1.1307489e-10, global = 8.7192362e-14, cumulative = -1.2196669e-08
ExecutionTime = 77.85 s  ClockTime = 78 s

Time = 94

smoothSolver:  Solving for Ux, Initial residual = 1.0325866e-07, Final residual = 3.8055719e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 7.3641191e-08, Final residual = 3.0493717e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0016974197, Final residual = 1.3384279e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00022476396, Final residual = 1.7267821e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.9557416e-05, Final residual = 2.1818484e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.8964359e-05, Final residual = 3.4677013e-07, No Iterations 7
time step continuity errors : sum local = 2.4649037e-10, global = 1.5648918e-13, cumulative = -1.2196513e-08
ExecutionTime = 78.66 s  ClockTime = 79 s

Time = 95

smoothSolver:  Solving for Ux, Initial residual = 9.4630617e-08, Final residual = 3.770265e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 6.6896935e-08, Final residual = 3.0211481e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0016741167, Final residual = 1.3034114e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00022097652, Final residual = 1.7062613e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.8328093e-05, Final residual = 6.3557521e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.8586229e-05, Final residual = 1.8952623e-07, No Iterations 3
time step continuity errors : sum local = 1.3547908e-10, global = 2.1589305e-13, cumulative = -1.2196297e-08
ExecutionTime = 79.5 s  ClockTime = 80 s

Time = 96

smoothSolver:  Solving for Ux, Initial residual = 8.6316457e-08, Final residual = 3.7357304e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 6.1005243e-08, Final residual = 2.9934095e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0016513582, Final residual = 1.269852e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00021779005, Final residual = 1.7255776e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.7827263e-05, Final residual = 3.3277487e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.6590153e-05, Final residual = 3.0353162e-07, No Iterations 10
time step continuity errors : sum local = 2.1601298e-10, global = 1.8639492e-14, cumulative = -1.2196278e-08
ExecutionTime = 80.42 s  ClockTime = 81 s

Time = 97

smoothSolver:  Solving for Ux, Initial residual = 7.9714461e-08, Final residual = 3.7016487e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 5.804895e-08, Final residual = 2.9659207e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0016292621, Final residual = 1.2426349e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0002149623, Final residual = 1.7094545e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.6738287e-05, Final residual = 8.6012217e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.7605146e-05, Final residual = 3.4259854e-07, No Iterations 7
time step continuity errors : sum local = 2.4360805e-10, global = 4.4383689e-14, cumulative = -1.2196234e-08
ExecutionTime = 81.15 s  ClockTime = 81 s

Time = 98

smoothSolver:  Solving for Ux, Initial residual = 7.5463351e-08, Final residual = 3.6681842e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 5.7138816e-08, Final residual = 2.9388701e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0016078637, Final residual = 1.2175606e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0002122573, Final residual = 1.6596337e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.5481026e-05, Final residual = 8.38582e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.6915727e-05, Final residual = 1.6606336e-07, No Iterations 5
time step continuity errors : sum local = 1.1885828e-10, global = 7.5790951e-15, cumulative = -1.2196226e-08
ExecutionTime = 81.75 s  ClockTime = 82 s

Time = 99

smoothSolver:  Solving for Ux, Initial residual = 7.0980973e-08, Final residual = 3.6351711e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 5.5334029e-08, Final residual = 2.9121905e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0015865473, Final residual = 1.1934356e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00020973421, Final residual = 1.6180143e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.4052729e-05, Final residual = 7.9892145e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.6333101e-05, Final residual = 3.3922645e-07, No Iterations 9
time step continuity errors : sum local = 2.4110656e-10, global = 1.9276654e-13, cumulative = -1.2196034e-08
ExecutionTime = 82.42 s  ClockTime = 83 s

Time = 100

smoothSolver:  Solving for Ux, Initial residual = 6.6272157e-08, Final residual = 3.602841e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 5.2400561e-08, Final residual = 2.8859419e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0015660734, Final residual = 1.1696158e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00020658536, Final residual = 1.5604917e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.2727403e-05, Final residual = 7.5822763e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.5719415e-05, Final residual = 1.6406717e-07, No Iterations 4
time step continuity errors : sum local = 1.1756527e-10, global = -2.0817898e-14, cumulative = -1.2196054e-08
ExecutionTime = 83.39 s  ClockTime = 84 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305954e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.009891

Time = 101

smoothSolver:  Solving for Ux, Initial residual = 6.1333146e-08, Final residual = 3.5710302e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 4.9576003e-08, Final residual = 2.8600738e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0015456134, Final residual = 1.1464598e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00020317358, Final residual = 1.5363442e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.1693245e-05, Final residual = 7.1756757e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.5309879e-05, Final residual = 2.8962586e-07, No Iterations 9
time step continuity errors : sum local = 2.0647804e-10, global = 1.1810223e-13, cumulative = -1.2195936e-08
ExecutionTime = 84.04 s  ClockTime = 85 s

Time = 102

smoothSolver:  Solving for Ux, Initial residual = 5.6193506e-08, Final residual = 3.5400261e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 4.6097812e-08, Final residual = 2.8344073e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0015254907, Final residual = 1.129443e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00019994284, Final residual = 1.4914687e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.0216229e-05, Final residual = 7.1146666e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4692127e-05, Final residual = 1.1863317e-07, No Iterations 6
time step continuity errors : sum local = 8.5524959e-11, global = -2.8085417e-13, cumulative = -1.2196217e-08
ExecutionTime = 84.67 s  ClockTime = 85 s

Time = 103

smoothSolver:  Solving for Ux, Initial residual = 5.1914077e-08, Final residual = 3.5097216e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 4.3723238e-08, Final residual = 2.8094026e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0015058879, Final residual = 1.1174275e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00019719191, Final residual = 1.447704e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.8692618e-05, Final residual = 6.9126092e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.3914049e-05, Final residual = 1.1615297e-07, No Iterations 7
time step continuity errors : sum local = 8.3640048e-11, global = -1.6632867e-13, cumulative = -1.2196384e-08
ExecutionTime = 85.28 s  ClockTime = 86 s

Time = 104

smoothSolver:  Solving for Ux, Initial residual = 4.795945e-08, Final residual = 3.4804783e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 4.0470959e-08, Final residual = 2.7851443e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0014863781, Final residual = 1.1030654e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00019478077, Final residual = 1.4000314e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7346141e-05, Final residual = 6.9128066e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.340268e-05, Final residual = 1.4783386e-07, No Iterations 5
time step continuity errors : sum local = 1.0606085e-10, global = 1.6249803e-14, cumulative = -1.2196367e-08
ExecutionTime = 85.84 s  ClockTime = 87 s

Time = 105

smoothSolver:  Solving for Ux, Initial residual = 4.4217139e-08, Final residual = 3.4516355e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 3.6451649e-08, Final residual = 2.7614548e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0014675682, Final residual = 1.0879475e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00019280948, Final residual = 1.3817702e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.6167459e-05, Final residual = 6.5856885e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.310217e-05, Final residual = 1.0755999e-07, No Iterations 6
time step continuity errors : sum local = 7.7771832e-11, global = 3.3324091e-14, cumulative = -1.2196334e-08
ExecutionTime = 86.44 s  ClockTime = 87 s

Time = 106

smoothSolver:  Solving for Ux, Initial residual = 4.1308163e-08, Final residual = 3.4233515e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 3.2801404e-08, Final residual = 2.7381437e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0014489083, Final residual = 1.0780896e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00019008619, Final residual = 1.3493319e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.4787947e-05, Final residual = 6.5187339e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.2546801e-05, Final residual = 1.3484822e-07, No Iterations 5
time step continuity errors : sum local = 9.68835e-11, global = 1.3720637e-13, cumulative = -1.2196197e-08
ExecutionTime = 87.07 s  ClockTime = 88 s

Time = 107

smoothSolver:  Solving for Ux, Initial residual = 3.8792454e-08, Final residual = 3.3953603e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.9732655e-08, Final residual = 2.7152617e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0014303381, Final residual = 1.0678662e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0001881451, Final residual = 1.3260306e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.4182994e-05, Final residual = 6.4231936e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.2164343e-05, Final residual = 3.0036522e-07, No Iterations 7
time step continuity errors : sum local = 2.1388852e-10, global = -2.6471598e-14, cumulative = -1.2196223e-08
ExecutionTime = 88.13 s  ClockTime = 89 s

Time = 108

smoothSolver:  Solving for Ux, Initial residual = 3.6921385e-08, Final residual = 3.3676302e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.7653036e-08, Final residual = 2.6927928e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0014127468, Final residual = 1.0571058e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00018572234, Final residual = 1.2958228e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.3104759e-05, Final residual = 6.5454999e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.1880631e-05, Final residual = 2.8345583e-07, No Iterations 7
time step continuity errors : sum local = 2.0199984e-10, global = 1.3866144e-15, cumulative = -1.2196222e-08
ExecutionTime = 88.8 s  ClockTime = 89 s

Time = 109

smoothSolver:  Solving for Ux, Initial residual = 3.5252216e-08, Final residual = 3.3399945e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.6115546e-08, Final residual = 2.6707305e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0013954817, Final residual = 1.0414722e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00018390616, Final residual = 1.2693517e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.235703e-05, Final residual = 6.6506948e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.139362e-05, Final residual = 2.5923634e-07, No Iterations 7
time step continuity errors : sum local = 1.8499617e-10, global = 2.0775088e-14, cumulative = -1.2196201e-08
ExecutionTime = 89.6 s  ClockTime = 90 s

Time = 110

smoothSolver:  Solving for Ux, Initial residual = 3.3620244e-08, Final residual = 3.3125635e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.4865725e-08, Final residual = 2.6489783e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0013784646, Final residual = 1.0205177e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00018215418, Final residual = 1.2531111e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.1669933e-05, Final residual = 6.7011656e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.1223078e-05, Final residual = 1.4459765e-07, No Iterations 4
time step continuity errors : sum local = 1.0385393e-10, global = -1.246195e-13, cumulative = -1.2196326e-08
ExecutionTime = 90.15 s  ClockTime = 91 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305954e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.009891

Time = 111

smoothSolver:  Solving for Ux, Initial residual = 3.2555275e-08, Final residual = 3.2855139e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.4446473e-08, Final residual = 2.6279403e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0013619132, Final residual = 1.0016482e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00018038437, Final residual = 1.2575845e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.0873862e-05, Final residual = 6.7321113e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.1046015e-05, Final residual = 2.6148224e-07, No Iterations 7
time step continuity errors : sum local = 1.8642589e-10, global = -1.2224752e-14, cumulative = -1.2196338e-08
ExecutionTime = 90.82 s  ClockTime = 92 s

Time = 112

smoothSolver:  Solving for Ux, Initial residual = 3.1780177e-08, Final residual = 3.259076e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.4233781e-08, Final residual = 2.6064007e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.001345594, Final residual = 9.871311e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00017760668, Final residual = 1.2399647e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.9683712e-05, Final residual = 6.742277e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.0604442e-05, Final residual = 2.5708455e-07, No Iterations 8
time step continuity errors : sum local = 1.8347326e-10, global = -3.2418664e-14, cumulative = -1.219637e-08
ExecutionTime = 91.49 s  ClockTime = 92 s

Time = 113

smoothSolver:  Solving for Ux, Initial residual = 3.0991923e-08, Final residual = 3.2330134e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.3908166e-08, Final residual = 2.5856761e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0013298957, Final residual = 9.7815334e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00017515354, Final residual = 1.2062303e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.8374954e-05, Final residual = 6.6313373e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.9999928e-05, Final residual = 1.3447258e-07, No Iterations 4
time step continuity errors : sum local = 9.6696347e-11, global = 1.4280172e-13, cumulative = -1.2196228e-08
ExecutionTime = 92.06 s  ClockTime = 93 s

Time = 114

smoothSolver:  Solving for Ux, Initial residual = 2.9892922e-08, Final residual = 3.2076382e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.3462014e-08, Final residual = 2.5649225e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0013142269, Final residual = 9.6963948e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00017243861, Final residual = 1.19802e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.7263193e-05, Final residual = 6.5115184e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.9540469e-05, Final residual = 2.5336305e-07, No Iterations 7
time step continuity errors : sum local = 1.8070115e-10, global = -1.747587e-13, cumulative = -1.2196402e-08
ExecutionTime = 92.73 s  ClockTime = 93 s

Time = 115

smoothSolver:  Solving for Ux, Initial residual = 2.9032006e-08, Final residual = 3.1822304e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.2923194e-08, Final residual = 2.5460192e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0013006593, Final residual = 9.6018479e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00017081795, Final residual = 1.1971733e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.6441384e-05, Final residual = 6.2092628e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.9025693e-05, Final residual = 1.0080361e-07, No Iterations 6
time step continuity errors : sum local = 7.3109007e-11, global = 6.6677324e-14, cumulative = -1.2196336e-08
ExecutionTime = 93.39 s  ClockTime = 94 s

Time = 116

smoothSolver:  Solving for Ux, Initial residual = 2.7764114e-08, Final residual = 3.158124e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.2183703e-08, Final residual = 2.52443e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0012840717, Final residual = 9.4708819e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00016766422, Final residual = 1.1816898e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.5523644e-05, Final residual = 6.1712356e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.8648044e-05, Final residual = 9.7091342e-08, No Iterations 6
time step continuity errors : sum local = 7.0465163e-11, global = 1.3137138e-13, cumulative = -1.2196204e-08
ExecutionTime = 94.01 s  ClockTime = 95 s

Time = 117

smoothSolver:  Solving for Ux, Initial residual = 2.6740228e-08, Final residual = 3.1336015e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.1769354e-08, Final residual = 2.5045593e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0012690395, Final residual = 9.3048022e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00016561586, Final residual = 1.1506411e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.4915006e-05, Final residual = 6.1064823e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.8374833e-05, Final residual = 2.2365284e-07, No Iterations 9
time step continuity errors : sum local = 1.5961027e-10, global = 1.0541794e-14, cumulative = -1.2196194e-08
ExecutionTime = 94.65 s  ClockTime = 95 s

Time = 118

smoothSolver:  Solving for Ux, Initial residual = 2.5719944e-08, Final residual = 3.1095061e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 2.0967825e-08, Final residual = 2.4861927e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0012558066, Final residual = 9.0913486e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00016428017, Final residual = 1.124861e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.4218964e-05, Final residual = 6.1004672e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.8239328e-05, Final residual = 2.4120126e-07, No Iterations 5
time step continuity errors : sum local = 1.7206865e-10, global = -2.0178161e-13, cumulative = -1.2196396e-08
ExecutionTime = 95.25 s  ClockTime = 96 s

Time = 119

smoothSolver:  Solving for Ux, Initial residual = 2.4987271e-08, Final residual = 3.086415e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.9915937e-08, Final residual = 2.465656e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0012398976, Final residual = 8.9435111e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00016159068, Final residual = 1.106338e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.3002275e-05, Final residual = 5.870706e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.7619342e-05, Final residual = 2.3706794e-07, No Iterations 8
time step continuity errors : sum local = 1.6919702e-10, global = -3.7006265e-14, cumulative = -1.2196433e-08
ExecutionTime = 95.94 s  ClockTime = 97 s

Time = 120

smoothSolver:  Solving for Ux, Initial residual = 2.4263202e-08, Final residual = 3.062601e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.9170178e-08, Final residual = 2.4475633e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0012263341, Final residual = 8.8345214e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00016023665, Final residual = 1.0801464e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.2164282e-05, Final residual = 5.7050283e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.7402081e-05, Final residual = 1.509068e-07, No Iterations 4
time step continuity errors : sum local = 1.0835952e-10, global = 1.121821e-13, cumulative = -1.219632e-08
ExecutionTime = 96.52 s  ClockTime = 97 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.009891

Time = 121

smoothSolver:  Solving for Ux, Initial residual = 2.3294436e-08, Final residual = 3.0403875e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.8483011e-08, Final residual = 2.4277862e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0012111122, Final residual = 8.8104862e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00015802062, Final residual = 1.0554609e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.1169018e-05, Final residual = 5.5730301e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.7066212e-05, Final residual = 1.0380738e-07, No Iterations 6
time step continuity errors : sum local = 7.5251813e-11, global = 8.7576983e-14, cumulative = -1.2196233e-08
ExecutionTime = 97.12 s  ClockTime = 98 s

Time = 122

smoothSolver:  Solving for Ux, Initial residual = 2.2973035e-08, Final residual = 3.0172126e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.8246426e-08, Final residual = 2.41027e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0011978203, Final residual = 8.7549835e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00015662022, Final residual = 1.561404e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.7867963e-05, Final residual = 4.5510373e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.8722195e-05, Final residual = 1.0687453e-07, No Iterations 5
time step continuity errors : sum local = 7.7208926e-11, global = -9.6187425e-14, cumulative = -1.2196329e-08
ExecutionTime = 97.7 s  ClockTime = 98 s

Time = 123

smoothSolver:  Solving for Ux, Initial residual = 2.234679e-08, Final residual = 2.9954148e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.7414272e-08, Final residual = 2.3912563e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0011841336, Final residual = 8.6904546e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00015464333, Final residual = 1.5321872e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.7148566e-05, Final residual = 1.751969e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.8497072e-05, Final residual = 2.7732322e-07, No Iterations 7
time step continuity errors : sum local = 1.9787326e-10, global = -2.1556155e-13, cumulative = -1.2196545e-08
ExecutionTime = 98.35 s  ClockTime = 99 s

Time = 124

smoothSolver:  Solving for Ux, Initial residual = 2.2572266e-08, Final residual = 2.9727647e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.7609153e-08, Final residual = 2.3743998e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0011714628, Final residual = 8.5527212e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00015334929, Final residual = 1.515392e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.6627985e-05, Final residual = 4.9048963e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.8638361e-05, Final residual = 2.4661968e-07, No Iterations 6
time step continuity errors : sum local = 1.7582943e-10, global = -6.9425394e-14, cumulative = -1.2196614e-08
ExecutionTime = 98.97 s  ClockTime = 100 s

Time = 125

smoothSolver:  Solving for Ux, Initial residual = 2.2107902e-08, Final residual = 2.9517083e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.7255437e-08, Final residual = 2.3560286e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.001158548, Final residual = 8.4546642e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00015175476, Final residual = 1.5114804e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.622115e-05, Final residual = 1.6207633e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.806018e-05, Final residual = 1.1555224e-07, No Iterations 6
time step continuity errors : sum local = 8.3418662e-11, global = -6.0466473e-14, cumulative = -1.2196674e-08
ExecutionTime = 99.58 s  ClockTime = 100 s

Time = 126

smoothSolver:  Solving for Ux, Initial residual = 2.1544364e-08, Final residual = 2.9298995e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.6891517e-08, Final residual = 2.3396325e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0011465245, Final residual = 8.3438692e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00015045989, Final residual = 9.8567746e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.8768896e-05, Final residual = 5.2730911e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.6332997e-05, Final residual = 2.3076971e-07, No Iterations 7
time step continuity errors : sum local = 1.6456672e-10, global = -9.5066701e-14, cumulative = -1.2196769e-08
ExecutionTime = 100.23 s  ClockTime = 101 s

Time = 127

smoothSolver:  Solving for Ux, Initial residual = 2.1204158e-08, Final residual = 2.9094121e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.6695913e-08, Final residual = 2.3220409e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0011335216, Final residual = 8.2542457e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0001485447, Final residual = 9.6982421e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.7993423e-05, Final residual = 5.1479947e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.5884368e-05, Final residual = 1.2876413e-07, No Iterations 5
time step continuity errors : sum local = 9.2827933e-11, global = -3.2469044e-13, cumulative = -1.2197094e-08
ExecutionTime = 100.9 s  ClockTime = 102 s

Time = 128

smoothSolver:  Solving for Ux, Initial residual = 2.1553921e-08, Final residual = 2.8884641e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.7225727e-08, Final residual = 2.3058489e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0011221978, Final residual = 8.1772555e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00014749929, Final residual = 9.7145281e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.7431884e-05, Final residual = 5.6947954e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.4510708e-05, Final residual = 1.3635458e-07, No Iterations 5
time step continuity errors : sum local = 9.8153036e-11, global = -3.3039711e-13, cumulative = -1.2197425e-08
ExecutionTime = 101.54 s  ClockTime = 102 s

Time = 129

smoothSolver:  Solving for Ux, Initial residual = 2.1702239e-08, Final residual = 2.8686167e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.7435559e-08, Final residual = 2.2885585e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0011094072, Final residual = 8.0873733e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00014565193, Final residual = 9.6932332e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.670196e-05, Final residual = 5.2232301e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.4148992e-05, Final residual = 2.2959258e-07, No Iterations 11
time step continuity errors : sum local = 1.6368207e-10, global = -4.20558e-14, cumulative = -1.2197467e-08
ExecutionTime = 102.26 s  ClockTime = 103 s

Time = 130

smoothSolver:  Solving for Ux, Initial residual = 2.0134926e-08, Final residual = 2.8481417e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.6096172e-08, Final residual = 2.2729819e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.001097865, Final residual = 7.9923132e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00014445536, Final residual = 9.4867404e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.6257139e-05, Final residual = 5.2228057e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.4142501e-05, Final residual = 1.3712867e-07, No Iterations 5
time step continuity errors : sum local = 9.8808619e-11, global = 3.1982956e-13, cumulative = -1.2197147e-08
ExecutionTime = 102.96 s  ClockTime = 104 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.009891

Time = 131

smoothSolver:  Solving for Ux, Initial residual = 2.1852656e-08, Final residual = 2.828637e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.7666564e-08, Final residual = 2.2573453e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0010865483, Final residual = 7.897202e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00014340973, Final residual = 9.5794589e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.5953712e-05, Final residual = 5.1829603e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.5345913e-05, Final residual = 1.1865314e-07, No Iterations 5
time step continuity errors : sum local = 8.5681204e-11, global = 8.889502e-14, cumulative = -1.2197058e-08
ExecutionTime = 103.65 s  ClockTime = 104 s

Time = 132

smoothSolver:  Solving for Ux, Initial residual = 2.1715e-08, Final residual = 2.8093474e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.7541705e-08, Final residual = 2.2406985e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0010749412, Final residual = 7.8302289e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00014170473, Final residual = 9.446721e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.5429769e-05, Final residual = 5.5366019e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.5436316e-05, Final residual = 2.4978836e-07, No Iterations 8
time step continuity errors : sum local = 1.7858471e-10, global = 8.2643747e-14, cumulative = -1.2196975e-08
ExecutionTime = 104.32 s  ClockTime = 105 s

Time = 133

smoothSolver:  Solving for Ux, Initial residual = 2.1076068e-08, Final residual = 2.7896861e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.6965166e-08, Final residual = 2.225686e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0010643079, Final residual = 7.7415201e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00014044352, Final residual = 1.388415e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.2403073e-05, Final residual = 4.5785507e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.642401e-05, Final residual = 2.5942809e-07, No Iterations 7
time step continuity errors : sum local = 1.8507847e-10, global = 1.602942e-13, cumulative = -1.2196815e-08
ExecutionTime = 105.06 s  ClockTime = 106 s

Time = 134

smoothSolver:  Solving for Ux, Initial residual = 2.0605661e-08, Final residual = 2.7708556e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.6476636e-08, Final residual = 2.2106256e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0010539981, Final residual = 7.6324997e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00013939256, Final residual = 1.3612353e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.1810788e-05, Final residual = 3.3672185e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.62064e-05, Final residual = 1.1399094e-07, No Iterations 3
time step continuity errors : sum local = 8.2417102e-11, global = 9.0041021e-14, cumulative = -1.2196725e-08
ExecutionTime = 106.03 s  ClockTime = 107 s

Time = 135

smoothSolver:  Solving for Ux, Initial residual = 1.9480049e-08, Final residual = 2.7519465e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.5482192e-08, Final residual = 2.1953621e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0010436315, Final residual = 7.5062464e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00013813352, Final residual = 1.3609025e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.1254507e-05, Final residual = 3.7814613e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.5851333e-05, Final residual = 1.5913066e-07, No Iterations 4
time step continuity errors : sum local = 1.1422966e-10, global = 5.5428508e-14, cumulative = -1.2196669e-08
ExecutionTime = 106.81 s  ClockTime = 108 s

Time = 136

smoothSolver:  Solving for Ux, Initial residual = 1.8873065e-08, Final residual = 2.7331894e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.4934787e-08, Final residual = 2.1805327e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0010335856, Final residual = 7.3952515e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00013665781, Final residual = 1.3574322e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.0941809e-05, Final residual = 3.3747775e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.5491375e-05, Final residual = 9.6081205e-08, No Iterations 7
time step continuity errors : sum local = 6.9779132e-11, global = 3.3230609e-13, cumulative = -1.2196337e-08
ExecutionTime = 107.71 s  ClockTime = 108 s

Time = 137

smoothSolver:  Solving for Ux, Initial residual = 1.8822554e-08, Final residual = 2.7147518e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.487155e-08, Final residual = 2.1658098e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.001023514, Final residual = 7.293292e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00013515766, Final residual = 1.3466742e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.0485706e-05, Final residual = 3.5316407e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.5294187e-05, Final residual = 2.3907267e-07, No Iterations 6
time step continuity errors : sum local = 1.704717e-10, global = 2.4038852e-13, cumulative = -1.2196097e-08
ExecutionTime = 108.33 s  ClockTime = 109 s

Time = 138

smoothSolver:  Solving for Ux, Initial residual = 1.8538061e-08, Final residual = 2.6966448e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.4633049e-08, Final residual = 2.1512341e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0010136708, Final residual = 7.2068502e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00013372651, Final residual = 1.3285032e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.9961843e-05, Final residual = 1.427088e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.5005373e-05, Final residual = 9.7127087e-08, No Iterations 5
time step continuity errors : sum local = 7.0640915e-11, global = 4.5711458e-13, cumulative = -1.219564e-08
ExecutionTime = 108.92 s  ClockTime = 110 s

Time = 139

smoothSolver:  Solving for Ux, Initial residual = 1.899984e-08, Final residual = 2.6787756e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.5121779e-08, Final residual = 2.1367828e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0010040145, Final residual = 7.1097521e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00013247213, Final residual = 8.4425505e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.1785925e-05, Final residual = 4.6907556e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.3355039e-05, Final residual = 1.0375658e-07, No Iterations 6
time step continuity errors : sum local = 7.5160112e-11, global = 3.8943163e-14, cumulative = -1.2195601e-08
ExecutionTime = 109.51 s  ClockTime = 110 s

Time = 140

smoothSolver:  Solving for Ux, Initial residual = 1.812115e-08, Final residual = 2.6611652e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.4376372e-08, Final residual = 2.1223683e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00099460828, Final residual = 7.0227819e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00013121261, Final residual = 1.3012498e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.8852788e-05, Final residual = 3.3063814e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.4397595e-05, Final residual = 1.1684705e-07, No Iterations 3
time step continuity errors : sum local = 8.4348765e-11, global = 1.3247109e-13, cumulative = -1.2195468e-08
ExecutionTime = 110.03 s  ClockTime = 111 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.009891

Time = 141

smoothSolver:  Solving for Ux, Initial residual = 1.8445979e-08, Final residual = 2.6438038e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.4706956e-08, Final residual = 2.1081241e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00098520436, Final residual = 6.9511925e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00012972959, Final residual = 1.2955354e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.8355279e-05, Final residual = 1.4441512e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.406654e-05, Final residual = 1.0280002e-07, No Iterations 4
time step continuity errors : sum local = 7.4445663e-11, global = -7.1712256e-14, cumulative = -1.219554e-08
ExecutionTime = 110.6 s  ClockTime = 111 s

Time = 142

smoothSolver:  Solving for Ux, Initial residual = 1.9561877e-08, Final residual = 2.6266663e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.5702819e-08, Final residual = 2.0940881e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00097593895, Final residual = 6.898588e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00012828142, Final residual = 8.3115941e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.0157262e-05, Final residual = 1.638058e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.1680963e-05, Final residual = 9.7780343e-08, No Iterations 9
time step continuity errors : sum local = 7.1029039e-11, global = 7.0812129e-14, cumulative = -1.2195469e-08
ExecutionTime = 111.3 s  ClockTime = 112 s

Time = 143

smoothSolver:  Solving for Ux, Initial residual = 1.9203229e-08, Final residual = 2.6097093e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.5422493e-08, Final residual = 2.0802364e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00096681546, Final residual = 6.8487469e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00012688056, Final residual = 8.1639586e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.9545946e-05, Final residual = 1.6207575e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.1399851e-05, Final residual = 2.0667893e-07, No Iterations 8
time step continuity errors : sum local = 1.4764961e-10, global = 2.2704334e-13, cumulative = -1.2195242e-08
ExecutionTime = 111.92 s  ClockTime = 113 s

Time = 144

smoothSolver:  Solving for Ux, Initial residual = 1.769199e-08, Final residual = 2.5930483e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.4072785e-08, Final residual = 2.0666388e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00095783324, Final residual = 6.7970304e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00012543464, Final residual = 1.2434931e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.6789513e-05, Final residual = 3.9903088e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.2955314e-05, Final residual = 9.1545147e-08, No Iterations 5
time step continuity errors : sum local = 6.6263366e-11, global = 2.0001856e-13, cumulative = -1.2195042e-08
ExecutionTime = 112.53 s  ClockTime = 113 s

Time = 145

smoothSolver:  Solving for Ux, Initial residual = 1.755056e-08, Final residual = 2.5766052e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.3980686e-08, Final residual = 2.0533021e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00094911432, Final residual = 6.7379235e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00012418307, Final residual = 1.2309846e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.6303514e-05, Final residual = 2.8570356e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.2842639e-05, Final residual = 8.1883275e-08, No Iterations 6
time step continuity errors : sum local = 5.9812059e-11, global = -8.6791321e-14, cumulative = -1.2195129e-08
ExecutionTime = 113.13 s  ClockTime = 114 s

Time = 146

smoothSolver:  Solving for Ux, Initial residual = 1.7343164e-08, Final residual = 2.5602534e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.3780453e-08, Final residual = 2.0402087e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00094078942, Final residual = 6.6775691e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00012302826, Final residual = 1.2232782e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.5875731e-05, Final residual = 1.2973617e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.2509958e-05, Final residual = 2.0883506e-07, No Iterations 5
time step continuity errors : sum local = 1.4916423e-10, global = -1.7362628e-13, cumulative = -1.2195303e-08
ExecutionTime = 113.72 s  ClockTime = 114 s

Time = 147

smoothSolver:  Solving for Ux, Initial residual = 1.8145067e-08, Final residual = 2.5440165e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.4532875e-08, Final residual = 2.0272054e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00093246718, Final residual = 6.6254991e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00012180386, Final residual = 1.2146023e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.5272518e-05, Final residual = 1.3027009e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.2316934e-05, Final residual = 1.0803339e-07, No Iterations 4
time step continuity errors : sum local = 7.8194793e-11, global = 4.9439192e-14, cumulative = -1.2195253e-08
ExecutionTime = 114.43 s  ClockTime = 115 s

Time = 148

smoothSolver:  Solving for Ux, Initial residual = 1.7181998e-08, Final residual = 2.5280094e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.3672434e-08, Final residual = 2.0143642e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00092418272, Final residual = 6.578501e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00012064415, Final residual = 7.6465124e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.6826528e-05, Final residual = 4.4911691e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.1076298e-05, Final residual = 8.1875129e-08, No Iterations 6
time step continuity errors : sum local = 5.9879932e-11, global = -3.9604453e-14, cumulative = -1.2195293e-08
ExecutionTime = 115.07 s  ClockTime = 116 s

Time = 149

smoothSolver:  Solving for Ux, Initial residual = 1.6819441e-08, Final residual = 2.5121892e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.3367537e-08, Final residual = 2.0016182e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00091598514, Final residual = 6.5254462e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00011974953, Final residual = 1.1916574e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.4553525e-05, Final residual = 3.4584123e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.2340861e-05, Final residual = 1.8355955e-07, No Iterations 5
time step continuity errors : sum local = 1.3135316e-10, global = -5.4042987e-14, cumulative = -1.2195347e-08
ExecutionTime = 115.68 s  ClockTime = 116 s

Time = 150

smoothSolver:  Solving for Ux, Initial residual = 1.6618205e-08, Final residual = 2.4967271e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.3194625e-08, Final residual = 1.988755e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00090790025, Final residual = 6.4699022e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00011890035, Final residual = 1.1698902e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.4220889e-05, Final residual = 3.1392785e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.2276799e-05, Final residual = 2.2111627e-07, No Iterations 4
time step continuity errors : sum local = 1.5825972e-10, global = -6.2635929e-14, cumulative = -1.2195409e-08
ExecutionTime = 116.72 s  ClockTime = 118 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 151

smoothSolver:  Solving for Ux, Initial residual = 1.6445749e-08, Final residual = 2.4815387e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.3044226e-08, Final residual = 1.9758247e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00089992212, Final residual = 6.4366372e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00011758676, Final residual = 1.1591625e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.3731378e-05, Final residual = 3.4554335e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.1785457e-05, Final residual = 1.1467338e-07, No Iterations 3
time step continuity errors : sum local = 8.2778303e-11, global = 8.6449372e-14, cumulative = -1.2195323e-08
ExecutionTime = 117.26 s  ClockTime = 118 s

Time = 152

smoothSolver:  Solving for Ux, Initial residual = 1.6647255e-08, Final residual = 2.4664731e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.3246689e-08, Final residual = 1.9632288e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00089213225, Final residual = 6.4181226e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00011684041, Final residual = 1.1675571e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.3361089e-05, Final residual = 3.7930232e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.1837423e-05, Final residual = 1.8913947e-07, No Iterations 4
time step continuity errors : sum local = 1.3554304e-10, global = -2.3546892e-14, cumulative = -1.2195346e-08
ExecutionTime = 118.33 s  ClockTime = 119 s

Time = 153

smoothSolver:  Solving for Ux, Initial residual = 1.6439914e-08, Final residual = 2.4514693e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.3072335e-08, Final residual = 1.9509865e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00088456624, Final residual = 6.4126358e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00011620722, Final residual = 1.1589746e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.2964638e-05, Final residual = 3.6400775e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.1660387e-05, Final residual = 1.0726301e-07, No Iterations 3
time step continuity errors : sum local = 7.7369653e-11, global = -2.1264636e-13, cumulative = -1.2195559e-08
ExecutionTime = 118.99 s  ClockTime = 120 s

Time = 154

smoothSolver:  Solving for Ux, Initial residual = 1.6435945e-08, Final residual = 2.4365932e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.3072541e-08, Final residual = 1.9390253e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00087730575, Final residual = 6.3932398e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00011539714, Final residual = 7.3137489e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.4788805e-05, Final residual = 1.4618694e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.0589926e-05, Final residual = 1.8478598e-07, No Iterations 4
time step continuity errors : sum local = 1.3244443e-10, global = 1.2576756e-13, cumulative = -1.2195433e-08
ExecutionTime = 119.6 s  ClockTime = 121 s

Time = 155

smoothSolver:  Solving for Ux, Initial residual = 1.6390163e-08, Final residual = 2.421857e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.3037246e-08, Final residual = 1.9273589e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00087020344, Final residual = 6.3740561e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00011411216, Final residual = 1.1283284e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.2395364e-05, Final residual = 3.5024197e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.1774885e-05, Final residual = 1.0497529e-07, No Iterations 4
time step continuity errors : sum local = 7.6004482e-11, global = 1.3032589e-13, cumulative = -1.2195303e-08
ExecutionTime = 120.23 s  ClockTime = 121 s

Time = 156

smoothSolver:  Solving for Ux, Initial residual = 1.6788318e-08, Final residual = 2.4071935e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.3402196e-08, Final residual = 1.915972e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00086303444, Final residual = 6.3488611e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0001129853, Final residual = 1.110583e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.23796e-05, Final residual = 1.2179897e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.150131e-05, Final residual = 1.1478888e-07, No Iterations 3
time step continuity errors : sum local = 8.267135e-11, global = -2.2485944e-13, cumulative = -1.2195528e-08
ExecutionTime = 120.92 s  ClockTime = 122 s

Time = 157

smoothSolver:  Solving for Ux, Initial residual = 1.6068681e-08, Final residual = 2.3927215e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2799786e-08, Final residual = 1.9047412e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00085592176, Final residual = 6.3296999e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00011224109, Final residual = 1.11517e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.2228073e-05, Final residual = 1.2742173e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.1397574e-05, Final residual = 2.0232501e-07, No Iterations 5
time step continuity errors : sum local = 1.4476066e-10, global = -1.3453332e-14, cumulative = -1.2195541e-08
ExecutionTime = 122.37 s  ClockTime = 123 s

Time = 158

smoothSolver:  Solving for Ux, Initial residual = 1.5948736e-08, Final residual = 2.3784387e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2691714e-08, Final residual = 1.8935989e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00084905631, Final residual = 6.317596e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0001120059, Final residual = 7.2687811e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.4334548e-05, Final residual = 3.9057747e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.0432483e-05, Final residual = 7.6669685e-08, No Iterations 6
time step continuity errors : sum local = 5.5940369e-11, global = 2.2153145e-15, cumulative = -1.2195539e-08
ExecutionTime = 123.01 s  ClockTime = 124 s

Time = 159

smoothSolver:  Solving for Ux, Initial residual = 1.5551938e-08, Final residual = 2.3643465e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2338647e-08, Final residual = 1.8823876e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00084219419, Final residual = 6.2634232e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00011160733, Final residual = 7.3048188e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.4053606e-05, Final residual = 4.3640688e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.0376547e-05, Final residual = 1.2337766e-07, No Iterations 5
time step continuity errors : sum local = 8.8947784e-11, global = 1.4457841e-13, cumulative = -1.2195395e-08
ExecutionTime = 123.69 s  ClockTime = 125 s

Time = 160

smoothSolver:  Solving for Ux, Initial residual = 1.6003046e-08, Final residual = 2.3505557e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2760239e-08, Final residual = 1.8713002e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00083546355, Final residual = 6.1966521e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00011134868, Final residual = 7.3212324e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.3839276e-05, Final residual = 4.3494717e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.019088e-05, Final residual = 1.4042517e-07, No Iterations 4
time step continuity errors : sum local = 1.0100985e-10, global = 2.198873e-13, cumulative = -1.2195175e-08
ExecutionTime = 124.37 s  ClockTime = 125 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.009891

Time = 161

smoothSolver:  Solving for Ux, Initial residual = 1.6610507e-08, Final residual = 2.3370293e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.3324431e-08, Final residual = 1.8602879e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00082875633, Final residual = 6.1286801e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00011038873, Final residual = 1.1023428e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.1410301e-05, Final residual = 1.2641212e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.0977769e-05, Final residual = 7.9126979e-08, No Iterations 6
time step continuity errors : sum local = 5.7856806e-11, global = -2.7456921e-13, cumulative = -1.2195449e-08
ExecutionTime = 125.1 s  ClockTime = 126 s

Time = 162

smoothSolver:  Solving for Ux, Initial residual = 1.5830229e-08, Final residual = 2.323558e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2626851e-08, Final residual = 1.8494118e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00082212741, Final residual = 6.0862845e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00010931905, Final residual = 1.0737831e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.1090976e-05, Final residual = 2.8621833e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.1333518e-05, Final residual = 2.1168636e-07, No Iterations 4
time step continuity errors : sum local = 1.5156529e-10, global = 1.6106342e-14, cumulative = -1.2195433e-08
ExecutionTime = 125.68 s  ClockTime = 127 s

Time = 163

smoothSolver:  Solving for Ux, Initial residual = 1.563182e-08, Final residual = 2.3101072e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2447736e-08, Final residual = 1.8387168e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00081547692, Final residual = 6.0742887e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00010835906, Final residual = 1.0590835e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.0664469e-05, Final residual = 2.6451821e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.0900562e-05, Final residual = 1.9126264e-07, No Iterations 5
time step continuity errors : sum local = 1.3694408e-10, global = 1.3172735e-13, cumulative = -1.2195301e-08
ExecutionTime = 126.39 s  ClockTime = 127 s

Time = 164

smoothSolver:  Solving for Ux, Initial residual = 1.5116995e-08, Final residual = 2.2967173e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2023401e-08, Final residual = 1.8280152e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00080887377, Final residual = 6.0465117e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.000107439, Final residual = 1.0514513e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.0432942e-05, Final residual = 1.1955414e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.0285344e-05, Final residual = 1.793786e-07, No Iterations 5
time step continuity errors : sum local = 1.2865911e-10, global = 1.3788469e-13, cumulative = -1.2195163e-08
ExecutionTime = 127.18 s  ClockTime = 128 s

Time = 165

smoothSolver:  Solving for Ux, Initial residual = 1.5621354e-08, Final residual = 2.2833431e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2463954e-08, Final residual = 1.8175531e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00080198885, Final residual = 5.943688e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00010611556, Final residual = 1.0517356e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.0001463e-05, Final residual = 2.9635033e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.0904571e-05, Final residual = 1.5454111e-07, No Iterations 6
time step continuity errors : sum local = 1.1094968e-10, global = 7.5138659e-14, cumulative = -1.2195088e-08
ExecutionTime = 127.86 s  ClockTime = 129 s

Time = 166

smoothSolver:  Solving for Ux, Initial residual = 1.5425946e-08, Final residual = 2.2700483e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.22924e-08, Final residual = 1.8072525e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0007951828, Final residual = 5.8071286e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00010518304, Final residual = 6.5819583e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1363068e-05, Final residual = 2.1008761e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.8447338e-05, Final residual = 1.0045989e-07, No Iterations 4
time step continuity errors : sum local = 7.2638008e-11, global = -2.4927267e-13, cumulative = -1.2195338e-08
ExecutionTime = 128.67 s  ClockTime = 130 s

Time = 167

smoothSolver:  Solving for Ux, Initial residual = 1.5848369e-08, Final residual = 2.2569252e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2671174e-08, Final residual = 1.796897e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00078857408, Final residual = 5.6790719e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00010435533, Final residual = 6.7174826e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1110444e-05, Final residual = 2.0316187e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.8274776e-05, Final residual = 1.0302059e-07, No Iterations 7
time step continuity errors : sum local = 7.4433127e-11, global = 1.5227315e-15, cumulative = -1.2195336e-08
ExecutionTime = 129.41 s  ClockTime = 130 s

Time = 168

smoothSolver:  Solving for Ux, Initial residual = 1.5674396e-08, Final residual = 2.2441302e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2522249e-08, Final residual = 1.786354e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00078219197, Final residual = 5.5821986e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00010340885, Final residual = 6.6598557e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.0628313e-05, Final residual = 1.8869798e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.808734e-05, Final residual = 1.1631957e-07, No Iterations 3
time step continuity errors : sum local = 8.4180787e-11, global = -1.1111421e-13, cumulative = -1.2195447e-08
ExecutionTime = 130.22 s  ClockTime = 131 s

Time = 169

smoothSolver:  Solving for Ux, Initial residual = 1.5641592e-08, Final residual = 2.2314232e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2484554e-08, Final residual = 1.7759874e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00077588292, Final residual = 5.5035955e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00010248221, Final residual = 6.8440946e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.0337406e-05, Final residual = 3.8916959e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.8650266e-05, Final residual = 9.3304753e-08, No Iterations 4
time step continuity errors : sum local = 6.7647614e-11, global = 1.2891683e-14, cumulative = -1.2195434e-08
ExecutionTime = 131.03 s  ClockTime = 132 s

Time = 170

smoothSolver:  Solving for Ux, Initial residual = 1.4854022e-08, Final residual = 2.2187883e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1810803e-08, Final residual = 1.7656252e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00076989508, Final residual = 5.4607933e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00010162144, Final residual = 6.8263922e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.0031702e-05, Final residual = 1.3102867e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.7720908e-05, Final residual = 8.7909439e-08, No Iterations 6
time step continuity errors : sum local = 6.3972948e-11, global = 2.9249074e-14, cumulative = -1.2195405e-08
ExecutionTime = 131.76 s  ClockTime = 133 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 171

smoothSolver:  Solving for Ux, Initial residual = 1.4723446e-08, Final residual = 2.2063187e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1735639e-08, Final residual = 1.7553973e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00076406621, Final residual = 5.4479181e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00010080742, Final residual = 6.8114499e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.9776344e-05, Final residual = 3.7781501e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.752717e-05, Final residual = 9.6565936e-08, No Iterations 9
time step continuity errors : sum local = 7.0145267e-11, global = -2.4062759e-14, cumulative = -1.2195429e-08
ExecutionTime = 132.63 s  ClockTime = 134 s

Time = 172

smoothSolver:  Solving for Ux, Initial residual = 1.4870221e-08, Final residual = 2.1939972e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1871597e-08, Final residual = 1.7453263e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00075832029, Final residual = 5.4315319e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00010010636, Final residual = 6.5762616e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.9431539e-05, Final residual = 1.2920933e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.755556e-05, Final residual = 1.6120666e-07, No Iterations 3
time step continuity errors : sum local = 1.1558305e-10, global = 3.9428222e-13, cumulative = -1.2195035e-08
ExecutionTime = 133.4 s  ClockTime = 134 s

Time = 173

smoothSolver:  Solving for Ux, Initial residual = 1.6772309e-08, Final residual = 2.1817593e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.3531967e-08, Final residual = 1.7353813e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00075259301, Final residual = 5.4058736e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.9358901e-05, Final residual = 9.8702468e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.7468645e-05, Final residual = 1.9238576e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.803322e-05, Final residual = 8.2881601e-08, No Iterations 10
time step continuity errors : sum local = 6.0616832e-11, global = -1.2116982e-13, cumulative = -1.2195156e-08
ExecutionTime = 134.29 s  ClockTime = 135 s

Time = 174

smoothSolver:  Solving for Ux, Initial residual = 1.4954034e-08, Final residual = 2.1697234e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1911577e-08, Final residual = 1.7255859e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00074704304, Final residual = 5.3737895e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.8596211e-05, Final residual = 9.6769249e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.7129359e-05, Final residual = 3.2670477e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 1.8940421e-05, Final residual = 1.0816132e-07, No Iterations 3
time step continuity errors : sum local = 7.7949108e-11, global = 2.5854062e-13, cumulative = -1.2194897e-08
ExecutionTime = 134.92 s  ClockTime = 136 s

Time = 175

smoothSolver:  Solving for Ux, Initial residual = 1.5377497e-08, Final residual = 2.1577914e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2268168e-08, Final residual = 1.7158008e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00074139596, Final residual = 5.3347406e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.8003505e-05, Final residual = 9.5552015e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.6829672e-05, Final residual = 1.1086481e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.8644796e-05, Final residual = 1.574472e-07, No Iterations 6
time step continuity errors : sum local = 1.1288097e-10, global = 8.3289176e-14, cumulative = -1.2194814e-08
ExecutionTime = 136.12 s  ClockTime = 137 s

Time = 176

smoothSolver:  Solving for Ux, Initial residual = 1.4526348e-08, Final residual = 2.1459868e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1516662e-08, Final residual = 1.7061392e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00073605306, Final residual = 5.2871909e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.7342083e-05, Final residual = 9.448973e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.6483278e-05, Final residual = 2.2294386e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.7699159e-05, Final residual = 1.0905697e-07, No Iterations 3
time step continuity errors : sum local = 7.8849189e-11, global = -2.0083347e-13, cumulative = -1.2195015e-08
ExecutionTime = 136.72 s  ClockTime = 138 s

Time = 177

smoothSolver:  Solving for Ux, Initial residual = 1.5484256e-08, Final residual = 2.1342249e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2403275e-08, Final residual = 1.6966434e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00073071607, Final residual = 5.2207732e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.6565362e-05, Final residual = 9.5352644e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.6243733e-05, Final residual = 2.0073331e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.7532951e-05, Final residual = 9.0653745e-08, No Iterations 8
time step continuity errors : sum local = 6.5959708e-11, global = 4.5917733e-13, cumulative = -1.2194556e-08
ExecutionTime = 137.51 s  ClockTime = 138 s

Time = 178

smoothSolver:  Solving for Ux, Initial residual = 1.4500389e-08, Final residual = 2.1225628e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1528098e-08, Final residual = 1.6872412e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00072556689, Final residual = 5.1594948e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.5743657e-05, Final residual = 9.4414288e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.5974005e-05, Final residual = 1.0932565e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.8346367e-05, Final residual = 1.1143754e-07, No Iterations 3
time step continuity errors : sum local = 8.0545491e-11, global = 2.1712981e-13, cumulative = -1.2194339e-08
ExecutionTime = 138.2 s  ClockTime = 139 s

Time = 179

smoothSolver:  Solving for Ux, Initial residual = 1.4452617e-08, Final residual = 2.1110466e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1517752e-08, Final residual = 1.6780346e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00072048525, Final residual = 5.1077412e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.4957795e-05, Final residual = 9.3523866e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.578777e-05, Final residual = 3.1003906e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 1.8606692e-05, Final residual = 8.5593894e-08, No Iterations 7
time step continuity errors : sum local = 6.2433242e-11, global = -7.8455354e-14, cumulative = -1.2194417e-08
ExecutionTime = 138.87 s  ClockTime = 140 s

Time = 180

smoothSolver:  Solving for Ux, Initial residual = 1.4328471e-08, Final residual = 2.0996715e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1407456e-08, Final residual = 1.6689569e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00071539908, Final residual = 5.0670894e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.4105504e-05, Final residual = 9.1113491e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.5305084e-05, Final residual = 2.7245109e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.8323485e-05, Final residual = 1.3285373e-07, No Iterations 6
time step continuity errors : sum local = 9.5484505e-11, global = 1.7231381e-13, cumulative = -1.2194245e-08
ExecutionTime = 140.1 s  ClockTime = 141 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 181

smoothSolver:  Solving for Ux, Initial residual = 1.3995636e-08, Final residual = 2.0883835e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1121897e-08, Final residual = 1.6601127e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00071031488, Final residual = 5.0344818e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.3344425e-05, Final residual = 8.8514698e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.5019806e-05, Final residual = 2.4500022e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.845367e-05, Final residual = 1.8213124e-07, No Iterations 4
time step continuity errors : sum local = 1.3050799e-10, global = 1.0840427e-13, cumulative = -1.2194136e-08
ExecutionTime = 140.82 s  ClockTime = 142 s

Time = 182

smoothSolver:  Solving for Ux, Initial residual = 1.3820105e-08, Final residual = 2.0770796e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0969007e-08, Final residual = 1.6513497e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0007051466, Final residual = 5.0001276e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.255596e-05, Final residual = 8.7133759e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4791199e-05, Final residual = 2.3767564e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.8334846e-05, Final residual = 1.8328691e-07, No Iterations 6
time step continuity errors : sum local = 1.3102619e-10, global = -3.5962141e-14, cumulative = -1.2194172e-08
ExecutionTime = 141.47 s  ClockTime = 142 s

Time = 183

smoothSolver:  Solving for Ux, Initial residual = 1.438582e-08, Final residual = 2.0658492e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1459482e-08, Final residual = 1.6428631e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00070011144, Final residual = 4.9749428e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.2049015e-05, Final residual = 8.6914499e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4647767e-05, Final residual = 1.0485058e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.766046e-05, Final residual = 7.5522755e-08, No Iterations 5
time step continuity errors : sum local = 5.5557894e-11, global = -5.7569764e-16, cumulative = -1.2194173e-08
ExecutionTime = 142.11 s  ClockTime = 143 s

Time = 184

smoothSolver:  Solving for Ux, Initial residual = 1.4226134e-08, Final residual = 2.0546801e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1329494e-08, Final residual = 1.6343897e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00069527082, Final residual = 4.9563979e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.1482653e-05, Final residual = 8.7689105e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4447469e-05, Final residual = 2.4714291e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.8227454e-05, Final residual = 1.7755142e-07, No Iterations 5
time step continuity errors : sum local = 1.2709737e-10, global = -1.0270336e-13, cumulative = -1.2194276e-08
ExecutionTime = 142.87 s  ClockTime = 144 s

Time = 185

smoothSolver:  Solving for Ux, Initial residual = 1.4556922e-08, Final residual = 2.0436036e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1621154e-08, Final residual = 1.6259679e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00069050328, Final residual = 4.9459802e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.0847009e-05, Final residual = 8.7236616e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4122882e-05, Final residual = 2.4556809e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.8125738e-05, Final residual = 1.5812838e-07, No Iterations 7
time step continuity errors : sum local = 1.1343975e-10, global = 9.6165087e-14, cumulative = -1.219418e-08
ExecutionTime = 143.72 s  ClockTime = 145 s

Time = 186

smoothSolver:  Solving for Ux, Initial residual = 1.3514221e-08, Final residual = 2.032627e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0713675e-08, Final residual = 1.6176108e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00068586802, Final residual = 4.9438358e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.0139202e-05, Final residual = 8.6531813e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.371571e-05, Final residual = 2.0916226e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.7679841e-05, Final residual = 1.0251816e-07, No Iterations 4
time step continuity errors : sum local = 7.4308196e-11, global = 8.8866377e-14, cumulative = -1.2194091e-08
ExecutionTime = 144.36 s  ClockTime = 145 s

Time = 187

smoothSolver:  Solving for Ux, Initial residual = 1.3594961e-08, Final residual = 2.0217526e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.082279e-08, Final residual = 1.6093391e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00068125343, Final residual = 4.9505228e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.9480953e-05, Final residual = 8.6310077e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.3545402e-05, Final residual = 9.7402767e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.7008741e-05, Final residual = 1.5268534e-07, No Iterations 4
time step continuity errors : sum local = 1.0973506e-10, global = 1.1511416e-13, cumulative = -1.2193976e-08
ExecutionTime = 145.2 s  ClockTime = 146 s

Time = 188

smoothSolver:  Solving for Ux, Initial residual = 1.4025672e-08, Final residual = 2.0110031e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1221838e-08, Final residual = 1.6010036e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00067654403, Final residual = 4.9528373e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.8996295e-05, Final residual = 8.6830341e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.3646022e-05, Final residual = 1.838573e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.7387964e-05, Final residual = 1.0144963e-07, No Iterations 3
time step continuity errors : sum local = 7.3470425e-11, global = 1.6524597e-13, cumulative = -1.219381e-08
ExecutionTime = 145.77 s  ClockTime = 147 s

Time = 189

smoothSolver:  Solving for Ux, Initial residual = 1.4274156e-08, Final residual = 2.0004335e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1448427e-08, Final residual = 1.5926436e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00067182303, Final residual = 4.8932603e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.8372518e-05, Final residual = 8.6769249e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.3559462e-05, Final residual = 1.985935e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.733903e-05, Final residual = 1.6510945e-07, No Iterations 4
time step continuity errors : sum local = 1.1844554e-10, global = 1.1721643e-13, cumulative = -1.2193693e-08
ExecutionTime = 146.33 s  ClockTime = 147 s

Time = 190

smoothSolver:  Solving for Ux, Initial residual = 1.398428e-08, Final residual = 1.9900267e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1190819e-08, Final residual = 1.5842966e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00066708489, Final residual = 4.792615e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.7565111e-05, Final residual = 8.5990276e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.317757e-05, Final residual = 1.0029558e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.6830987e-05, Final residual = 8.3004249e-08, No Iterations 5
time step continuity errors : sum local = 6.0472974e-11, global = -2.7428196e-13, cumulative = -1.2193967e-08
ExecutionTime = 146.92 s  ClockTime = 148 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305954e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.161494e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 191

smoothSolver:  Solving for Ux, Initial residual = 1.4066007e-08, Final residual = 1.9797538e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1277505e-08, Final residual = 1.5760034e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00066235987, Final residual = 4.6993734e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.6697119e-05, Final residual = 8.4630569e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.2779686e-05, Final residual = 2.1016281e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.6957436e-05, Final residual = 8.9771104e-08, No Iterations 3
time step continuity errors : sum local = 6.5454095e-11, global = -1.8419666e-13, cumulative = -1.2194152e-08
ExecutionTime = 147.57 s  ClockTime = 148 s

Time = 192

smoothSolver:  Solving for Ux, Initial residual = 1.4892242e-08, Final residual = 1.9695532e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1993855e-08, Final residual = 1.5676875e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00065769313, Final residual = 4.626789e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.5915483e-05, Final residual = 8.376389e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.2547571e-05, Final residual = 9.9706437e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.6609808e-05, Final residual = 8.6558194e-08, No Iterations 3
time step continuity errors : sum local = 6.3191716e-11, global = -2.0865252e-13, cumulative = -1.219436e-08
ExecutionTime = 148.24 s  ClockTime = 149 s

Time = 193

smoothSolver:  Solving for Ux, Initial residual = 1.5084548e-08, Final residual = 1.9594374e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2144164e-08, Final residual = 1.5594706e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00065308129, Final residual = 4.5832953e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.5309182e-05, Final residual = 8.4196399e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.2471962e-05, Final residual = 1.1007567e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.6723504e-05, Final residual = 1.6065187e-07, No Iterations 3
time step continuity errors : sum local = 1.1539477e-10, global = 1.55992e-13, cumulative = -1.2194204e-08
ExecutionTime = 148.83 s  ClockTime = 150 s

Time = 194

smoothSolver:  Solving for Ux, Initial residual = 1.2899929e-08, Final residual = 1.9494024e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0268918e-08, Final residual = 1.5512298e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00064843936, Final residual = 4.5697486e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.4693692e-05, Final residual = 8.3210646e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.2203573e-05, Final residual = 2.9550984e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 1.6155403e-05, Final residual = 1.506216e-07, No Iterations 6
time step continuity errors : sum local = 1.0825028e-10, global = 6.7840086e-14, cumulative = -1.2194136e-08
ExecutionTime = 149.51 s  ClockTime = 150 s

Time = 195

smoothSolver:  Solving for Ux, Initial residual = 1.3414311e-08, Final residual = 1.9395526e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0716949e-08, Final residual = 1.5429408e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00064367839, Final residual = 4.5727077e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.4281917e-05, Final residual = 8.2385764e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.1994714e-05, Final residual = 2.2916123e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.6518494e-05, Final residual = 1.0353105e-07, No Iterations 4
time step continuity errors : sum local = 7.4758854e-11, global = -1.7810868e-13, cumulative = -1.2194314e-08
ExecutionTime = 150.12 s  ClockTime = 151 s

Time = 196

smoothSolver:  Solving for Ux, Initial residual = 1.2729584e-08, Final residual = 1.9297406e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0121502e-08, Final residual = 1.5347797e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00063891109, Final residual = 4.5756785e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.4064983e-05, Final residual = 8.2317676e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.1751045e-05, Final residual = 2.2111571e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.6656635e-05, Final residual = 1.4402058e-07, No Iterations 4
time step continuity errors : sum local = 1.0364554e-10, global = -7.3417941e-14, cumulative = -1.2194388e-08
ExecutionTime = 150.69 s  ClockTime = 152 s

Time = 197

smoothSolver:  Solving for Ux, Initial residual = 1.2675579e-08, Final residual = 1.9200291e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0064012e-08, Final residual = 1.5268398e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00063423083, Final residual = 4.5702831e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.3664945e-05, Final residual = 8.1900655e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.1677045e-05, Final residual = 1.0361706e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.6044506e-05, Final residual = 9.1170708e-08, No Iterations 3
time step continuity errors : sum local = 6.6354783e-11, global = -1.4924658e-13, cumulative = -1.2194537e-08
ExecutionTime = 151.25 s  ClockTime = 152 s

Time = 198

smoothSolver:  Solving for Ux, Initial residual = 1.2586454e-08, Final residual = 1.9103162e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.9917672e-09, Final residual = 9.9917672e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00061635283, Final residual = 4.7530174e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00028219765, Final residual = 2.8200401e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.4996528e-05, Final residual = 5.641167e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.3465434e-05, Final residual = 2.9735656e-07, No Iterations 3
time step continuity errors : sum local = 2.1163079e-10, global = -8.804908e-14, cumulative = -1.2194625e-08
ExecutionTime = 151.8 s  ClockTime = 153 s

Time = 199

smoothSolver:  Solving for Ux, Initial residual = 1.228475e-08, Final residual = 1.8422659e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0472183e-08, Final residual = 1.5942885e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00061581847, Final residual = 3.0532009e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00017391329, Final residual = 9.6532283e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.0665498e-05, Final residual = 4.8708616e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.5113716e-05, Final residual = 2.3576979e-07, No Iterations 5
time step continuity errors : sum local = 1.6853772e-10, global = -9.3668225e-14, cumulative = -1.2194719e-08
ExecutionTime = 152.43 s  ClockTime = 153 s

Time = 200

smoothSolver:  Solving for Ux, Initial residual = 1.1983548e-08, Final residual = 1.8026971e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0629401e-08, Final residual = 1.6159842e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00062304315, Final residual = 6.1028837e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.096824e-05, Final residual = 8.9549804e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4517213e-05, Final residual = 1.2544356e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.6857906e-05, Final residual = 9.5067257e-08, No Iterations 3
time step continuity errors : sum local = 6.8950934e-11, global = 1.52091e-13, cumulative = -1.2194567e-08
ExecutionTime = 153.4 s  ClockTime = 155 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.009891

Time = 201

smoothSolver:  Solving for Ux, Initial residual = 1.2846603e-08, Final residual = 1.7922012e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1417015e-08, Final residual = 1.6077105e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00062483122, Final residual = 4.6939268e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00012632418, Final residual = 1.0902139e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.2796721e-05, Final residual = 2.6411627e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.1230901e-05, Final residual = 1.3481692e-07, No Iterations 3
time step continuity errors : sum local = 9.7144245e-11, global = -1.6040201e-13, cumulative = -1.2194727e-08
ExecutionTime = 153.99 s  ClockTime = 155 s

Time = 202

smoothSolver:  Solving for Ux, Initial residual = 1.1950241e-08, Final residual = 1.8037707e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0405965e-08, Final residual = 1.5746433e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00061681837, Final residual = 3.1309784e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00017325052, Final residual = 1.0177865e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.0538764e-05, Final residual = 5.0496665e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.4553814e-05, Final residual = 1.1500452e-07, No Iterations 3
time step continuity errors : sum local = 8.3157715e-11, global = -2.0159884e-13, cumulative = -1.2194929e-08
ExecutionTime = 154.55 s  ClockTime = 156 s

Time = 203

smoothSolver:  Solving for Ux, Initial residual = 1.2520376e-08, Final residual = 1.8269583e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0442433e-08, Final residual = 1.5291999e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00060723744, Final residual = 3.2354165e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0001776992, Final residual = 1.09296e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.1616409e-05, Final residual = 1.4283568e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.4896137e-05, Final residual = 1.0423834e-07, No Iterations 3
time step continuity errors : sum local = 7.553921e-11, global = 1.1824457e-13, cumulative = -1.2194811e-08
ExecutionTime = 155.14 s  ClockTime = 156 s

Time = 204

smoothSolver:  Solving for Ux, Initial residual = 1.2975646e-08, Final residual = 1.8505317e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0361278e-08, Final residual = 1.4841867e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00060530416, Final residual = 5.8563212e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00014469175, Final residual = 1.4454694e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.8215022e-05, Final residual = 2.2583779e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.170218e-05, Final residual = 1.0119613e-07, No Iterations 6
time step continuity errors : sum local = 7.3145072e-11, global = 4.7669488e-13, cumulative = -1.2194334e-08
ExecutionTime = 155.75 s  ClockTime = 157 s

Time = 205

smoothSolver:  Solving for Ux, Initial residual = 1.548467e-08, Final residual = 1.8662615e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2201751e-08, Final residual = 1.4488742e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0006088654, Final residual = 4.0945558e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00011352867, Final residual = 6.807472e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1434273e-05, Final residual = 3.2794265e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.8546204e-05, Final residual = 1.7854542e-07, No Iterations 9
time step continuity errors : sum local = 1.2804483e-10, global = -1.7839914e-13, cumulative = -1.2194512e-08
ExecutionTime = 156.4 s  ClockTime = 158 s

Time = 206

smoothSolver:  Solving for Ux, Initial residual = 1.299609e-08, Final residual = 1.8701367e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.8909726e-09, Final residual = 9.8909726e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00059529085, Final residual = 4.3268812e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00025242684, Final residual = 1.3135736e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.9434585e-05, Final residual = 5.9769827e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.3585203e-05, Final residual = 3.1395599e-07, No Iterations 3
time step continuity errors : sum local = 2.2366284e-10, global = 1.2100559e-13, cumulative = -1.2194391e-08
ExecutionTime = 156.99 s  ClockTime = 158 s

Time = 207

smoothSolver:  Solving for Ux, Initial residual = 1.2298437e-08, Final residual = 1.8073706e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0040514e-08, Final residual = 1.4945756e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0005845458, Final residual = 3.3185179e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00018793634, Final residual = 1.0046515e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.3536282e-05, Final residual = 4.7994545e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.6260549e-05, Final residual = 2.3587002e-07, No Iterations 3
time step continuity errors : sum local = 1.6826865e-10, global = 1.3536569e-13, cumulative = -1.2194256e-08
ExecutionTime = 157.59 s  ClockTime = 159 s

Time = 208

smoothSolver:  Solving for Ux, Initial residual = 1.1802921e-08, Final residual = 1.7626751e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.01327e-08, Final residual = 1.5231295e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00058028774, Final residual = 3.6406849e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00010434876, Final residual = 8.2666385e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.5735652e-05, Final residual = 3.5536774e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.7405368e-05, Final residual = 1.5310137e-07, No Iterations 5
time step continuity errors : sum local = 1.0991479e-10, global = 1.4666674e-13, cumulative = -1.2194109e-08
ExecutionTime = 158.21 s  ClockTime = 159 s

Time = 209

smoothSolver:  Solving for Ux, Initial residual = 1.1642231e-08, Final residual = 1.7406338e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.017138e-08, Final residual = 1.5295638e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00058290914, Final residual = 5.4876579e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.5591418e-05, Final residual = 5.6167281e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.5200947e-05, Final residual = 3.3151617e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5970439e-05, Final residual = 1.2762611e-07, No Iterations 8
time step continuity errors : sum local = 9.1937476e-11, global = 1.5605807e-13, cumulative = -1.2193953e-08
ExecutionTime = 158.86 s  ClockTime = 160 s

Time = 210

smoothSolver:  Solving for Ux, Initial residual = 1.1622981e-08, Final residual = 1.7390936e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0056999e-08, Final residual = 1.5130956e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00058209122, Final residual = 4.6206491e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00012100512, Final residual = 1.0816522e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.1181134e-05, Final residual = 2.205931e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.0025921e-05, Final residual = 8.0821391e-08, No Iterations 4
time step continuity errors : sum local = 5.9310453e-11, global = -2.4349885e-14, cumulative = -1.2193977e-08
ExecutionTime = 159.48 s  ClockTime = 161 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 211

smoothSolver:  Solving for Ux, Initial residual = 1.2026129e-08, Final residual = 1.7511222e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0173186e-08, Final residual = 1.4812859e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00057620142, Final residual = 5.514835e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00013719163, Final residual = 1.2705501e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.5608207e-05, Final residual = 2.7631805e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.1594693e-05, Final residual = 8.3251599e-08, No Iterations 5
time step continuity errors : sum local = 6.0638392e-11, global = 8.9552472e-14, cumulative = -1.2193888e-08
ExecutionTime = 160.14 s  ClockTime = 161 s

Time = 212

smoothSolver:  Solving for Ux, Initial residual = 1.2242659e-08, Final residual = 1.7682501e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.996209e-09, Final residual = 9.996209e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00055488198, Final residual = 3.0715521e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00017190026, Final residual = 9.340296e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.9693791e-05, Final residual = 4.3661067e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.4568354e-05, Final residual = 1.1807219e-07, No Iterations 3
time step continuity errors : sum local = 8.5062024e-11, global = -8.6251482e-14, cumulative = -1.2193974e-08
ExecutionTime = 160.73 s  ClockTime = 162 s

Time = 213

smoothSolver:  Solving for Ux, Initial residual = 1.2532691e-08, Final residual = 1.7269047e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0714323e-08, Final residual = 1.4888153e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00055423964, Final residual = 3.6092361e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00010012443, Final residual = 8.1191972e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.5023844e-05, Final residual = 3.206012e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.7100525e-05, Final residual = 1.0928266e-07, No Iterations 4
time step continuity errors : sum local = 7.9360141e-11, global = 2.5725022e-14, cumulative = -1.2193948e-08
ExecutionTime = 161.34 s  ClockTime = 162 s

Time = 214

smoothSolver:  Solving for Ux, Initial residual = 1.2061599e-08, Final residual = 1.7046995e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0474663e-08, Final residual = 1.4918387e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00055485092, Final residual = 4.3916505e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.4629095e-05, Final residual = 4.693916e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.016884e-05, Final residual = 2.3793053e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3578673e-05, Final residual = 8.8249833e-08, No Iterations 3
time step continuity errors : sum local = 6.416485e-11, global = -2.6029542e-13, cumulative = -1.2194209e-08
ExecutionTime = 161.92 s  ClockTime = 163 s

Time = 215

smoothSolver:  Solving for Ux, Initial residual = 1.3031736e-08, Final residual = 1.700697e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1274448e-08, Final residual = 1.4779206e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00055470376, Final residual = 4.0749103e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0001077925, Final residual = 1.0070957e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.6833671e-05, Final residual = 2.0548248e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.7921323e-05, Final residual = 1.7822682e-07, No Iterations 3
time step continuity errors : sum local = 1.2769789e-10, global = -1.3221384e-13, cumulative = -1.2194341e-08
ExecutionTime = 162.49 s  ClockTime = 164 s

Time = 216

smoothSolver:  Solving for Ux, Initial residual = 1.2777261e-08, Final residual = 1.7098916e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0802117e-08, Final residual = 1.450114e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00055324707, Final residual = 5.1471218e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00012835175, Final residual = 1.2466084e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.3035296e-05, Final residual = 2.2050504e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.9498789e-05, Final residual = 8.3595749e-08, No Iterations 7
time step continuity errors : sum local = 6.0820177e-11, global = -8.346727e-14, cumulative = -1.2194424e-08
ExecutionTime = 163.14 s  ClockTime = 164 s

Time = 217

smoothSolver:  Solving for Ux, Initial residual = 1.1946897e-08, Final residual = 1.7249873e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.7557745e-09, Final residual = 9.7557745e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00053572987, Final residual = 2.9953525e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00016953763, Final residual = 9.0682418e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.8824379e-05, Final residual = 4.2678671e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.3961448e-05, Final residual = 8.7207721e-08, No Iterations 4
time step continuity errors : sum local = 6.3772056e-11, global = 7.9875439e-14, cumulative = -1.2194345e-08
ExecutionTime = 163.73 s  ClockTime = 165 s

Time = 218

smoothSolver:  Solving for Ux, Initial residual = 1.1690931e-08, Final residual = 1.6839689e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0075674e-08, Final residual = 1.4610674e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00053513834, Final residual = 3.3193028e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.4464514e-05, Final residual = 7.5223862e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.2911727e-05, Final residual = 2.9844781e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5893848e-05, Final residual = 7.0551326e-08, No Iterations 4
time step continuity errors : sum local = 5.2015872e-11, global = -3.9249725e-14, cumulative = -1.2194384e-08
ExecutionTime = 164.3 s  ClockTime = 165 s

Time = 219

smoothSolver:  Solving for Ux, Initial residual = 1.1728674e-08, Final residual = 1.6630944e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0285221e-08, Final residual = 1.4634921e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00053610327, Final residual = 4.4754551e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.2421121e-05, Final residual = 5.27539e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.0874052e-05, Final residual = 2.8779677e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3713055e-05, Final residual = 1.2342859e-07, No Iterations 4
time step continuity errors : sum local = 8.8956764e-11, global = 1.9936191e-13, cumulative = -1.2194184e-08
ExecutionTime = 164.89 s  ClockTime = 166 s

Time = 220

smoothSolver:  Solving for Ux, Initial residual = 1.2953879e-08, Final residual = 1.6607813e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1265331e-08, Final residual = 1.4484695e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00053674685, Final residual = 4.3105484e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00010964688, Final residual = 1.0377669e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.786935e-05, Final residual = 2.4207692e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.8215307e-05, Final residual = 7.774029e-08, No Iterations 4
time step continuity errors : sum local = 5.7024552e-11, global = 1.3481504e-13, cumulative = -1.219405e-08
ExecutionTime = 165.5 s  ClockTime = 167 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.009891

Time = 221

smoothSolver:  Solving for Ux, Initial residual = 1.304125e-08, Final residual = 1.6714286e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1068188e-08, Final residual = 1.419787e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00053573914, Final residual = 5.2478813e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00012954814, Final residual = 1.2650542e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.3472191e-05, Final residual = 1.3649353e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.0560049e-05, Final residual = 1.1095673e-07, No Iterations 6
time step continuity errors : sum local = 8.0227525e-11, global = 7.2392739e-14, cumulative = -1.2193977e-08
ExecutionTime = 166.73 s  ClockTime = 168 s

Time = 222

smoothSolver:  Solving for Ux, Initial residual = 1.2435461e-08, Final residual = 1.6874354e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0228791e-08, Final residual = 1.3859923e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0005358944, Final residual = 5.0373776e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00012490733, Final residual = 7.6327266e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.4161214e-05, Final residual = 1.4133743e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.8633073e-05, Final residual = 1.5487914e-07, No Iterations 11
time step continuity errors : sum local = 1.1125177e-10, global = -1.8494262e-14, cumulative = -1.2193996e-08
ExecutionTime = 167.42 s  ClockTime = 169 s

Time = 223

smoothSolver:  Solving for Ux, Initial residual = 1.1334734e-08, Final residual = 1.701423e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.0413283e-09, Final residual = 9.0413283e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00052267489, Final residual = 3.1856775e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00018214421, Final residual = 9.6447538e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.158413e-05, Final residual = 4.4253799e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.5228687e-05, Final residual = 2.4771585e-07, No Iterations 3
time step continuity errors : sum local = 1.7703822e-10, global = 1.4245654e-13, cumulative = -1.2193853e-08
ExecutionTime = 168.02 s  ClockTime = 169 s

Time = 224

smoothSolver:  Solving for Ux, Initial residual = 1.1061337e-08, Final residual = 1.6564844e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.2954552e-09, Final residual = 9.2954552e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00051236975, Final residual = 2.6133438e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00035306905, Final residual = 3.3903423e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.963352e-05, Final residual = 5.568668e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.8117745e-05, Final residual = 3.1397034e-07, No Iterations 3
time step continuity errors : sum local = 2.2355706e-10, global = 1.4194149e-13, cumulative = -1.2193711e-08
ExecutionTime = 168.63 s  ClockTime = 170 s

Time = 225

smoothSolver:  Solving for Ux, Initial residual = 1.080156e-08, Final residual = 1.575058e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.979446e-09, Final residual = 9.979446e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00050841949, Final residual = 3.1836886e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00042666553, Final residual = 4.0520596e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00010658698, Final residual = 7.1987389e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.589922e-05, Final residual = 4.2536537e-07, No Iterations 6
time step continuity errors : sum local = 3.0237401e-10, global = 1.390515e-13, cumulative = -1.2193572e-08
ExecutionTime = 169.27 s  ClockTime = 170 s

Time = 226

smoothSolver:  Solving for Ux, Initial residual = 1.0264145e-08, Final residual = 1.4815044e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0672785e-08, Final residual = 1.5975774e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00053792349, Final residual = 2.5050652e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0001449927, Final residual = 9.5149875e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.4530483e-05, Final residual = 3.7658395e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.232249e-05, Final residual = 8.8487574e-08, No Iterations 5
time step continuity errors : sum local = 6.4551636e-11, global = -7.5752319e-14, cumulative = -1.2193648e-08
ExecutionTime = 169.94 s  ClockTime = 171 s

Time = 227

smoothSolver:  Solving for Ux, Initial residual = 1.0622061e-08, Final residual = 1.4549045e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1334306e-08, Final residual = 1.6084608e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00056869847, Final residual = 3.2919096e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00018657067, Final residual = 1.036596e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.3615418e-05, Final residual = 5.1992659e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.6007631e-05, Final residual = 2.2168442e-07, No Iterations 5
time step continuity errors : sum local = 1.5852855e-10, global = 7.0924523e-14, cumulative = -1.2193577e-08
ExecutionTime = 170.53 s  ClockTime = 172 s

Time = 228

smoothSolver:  Solving for Ux, Initial residual = 1.0611351e-08, Final residual = 1.4832594e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.083136e-08, Final residual = 1.5533332e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0005620282, Final residual = 5.3341997e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00032675491, Final residual = 3.2229006e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.3450578e-05, Final residual = 5.8631542e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.660659e-05, Final residual = 3.2160311e-07, No Iterations 3
time step continuity errors : sum local = 2.2937317e-10, global = 4.3651902e-14, cumulative = -1.2193533e-08
ExecutionTime = 171.15 s  ClockTime = 172 s

Time = 229

smoothSolver:  Solving for Ux, Initial residual = 1.1152871e-08, Final residual = 1.5459914e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0261539e-08, Final residual = 1.4597037e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00053342723, Final residual = 2.9638298e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00037268587, Final residual = 3.5408447e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.2479157e-05, Final residual = 5.739653e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.7791498e-05, Final residual = 2.9207001e-07, No Iterations 3
time step continuity errors : sum local = 2.0819508e-10, global = 2.214733e-14, cumulative = -1.2193511e-08
ExecutionTime = 171.77 s  ClockTime = 173 s

Time = 230

smoothSolver:  Solving for Ux, Initial residual = 1.1855257e-08, Final residual = 1.6175051e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.7398925e-09, Final residual = 9.7398925e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00050488242, Final residual = 3.9053679e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00010494215, Final residual = 9.6314446e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.6141636e-05, Final residual = 3.3077903e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 1.7940104e-05, Final residual = 9.8752788e-08, No Iterations 3
time step continuity errors : sum local = 7.1527596e-11, global = -1.5298629e-13, cumulative = -1.2193664e-08
ExecutionTime = 172.35 s  ClockTime = 173 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.161494e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 231

smoothSolver:  Solving for Ux, Initial residual = 1.2356149e-08, Final residual = 1.622776e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0032384e-08, Final residual = 1.3498815e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00052416925, Final residual = 4.1354083e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00011377067, Final residual = 7.5853451e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1959479e-05, Final residual = 2.7884834e-07, No Iterations 6
GAMG:  Solving for p, Initial residual = 1.9827033e-05, Final residual = 1.2576883e-07, No Iterations 3
time step continuity errors : sum local = 9.0688634e-11, global = 1.6301123e-13, cumulative = -1.2193501e-08
ExecutionTime = 173 s  ClockTime = 174 s

Time = 232

smoothSolver:  Solving for Ux, Initial residual = 1.1243849e-08, Final residual = 1.626765e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.0105561e-09, Final residual = 9.0105561e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00051833771, Final residual = 3.5921148e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00020416243, Final residual = 1.1210904e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.7525364e-05, Final residual = 5.6043222e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.8366039e-05, Final residual = 1.2580093e-07, No Iterations 3
time step continuity errors : sum local = 9.0705536e-11, global = -2.428171e-13, cumulative = -1.2193744e-08
ExecutionTime = 173.58 s  ClockTime = 175 s

Time = 233

smoothSolver:  Solving for Ux, Initial residual = 1.1378322e-08, Final residual = 1.5776199e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.7256904e-09, Final residual = 9.7256904e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00049847306, Final residual = 2.5554859e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00035064561, Final residual = 3.3951115e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.9158781e-05, Final residual = 5.5780969e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.783278e-05, Final residual = 3.2754684e-07, No Iterations 3
time step continuity errors : sum local = 2.3311007e-10, global = -8.8721562e-14, cumulative = -1.2193833e-08
ExecutionTime = 174.37 s  ClockTime = 175 s

Time = 234

smoothSolver:  Solving for Ux, Initial residual = 1.0584449e-08, Final residual = 1.4981165e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0084613e-08, Final residual = 1.4600737e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00048253331, Final residual = 2.6534453e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00015461249, Final residual = 8.4495494e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.5204954e-05, Final residual = 4.4133147e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.2569579e-05, Final residual = 1.0155742e-07, No Iterations 3
time step continuity errors : sum local = 7.3357072e-11, global = -6.627178e-14, cumulative = -1.2193899e-08
ExecutionTime = 175.03 s  ClockTime = 176 s

Time = 235

smoothSolver:  Solving for Ux, Initial residual = 9.9669236e-09, Final residual = 9.9669236e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 9.8688273e-09, Final residual = 9.8688273e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00044279051, Final residual = 1.4871448e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.1639409e-05, Final residual = 5.4099277e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.6392365e-05, Final residual = 1.1536955e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3354453e-05, Final residual = 8.6050219e-08, No Iterations 5
time step continuity errors : sum local = 6.2555363e-11, global = 9.6027748e-14, cumulative = -1.2193803e-08
ExecutionTime = 175.67 s  ClockTime = 177 s

Time = 236

smoothSolver:  Solving for Ux, Initial residual = 1.0537089e-08, Final residual = 1.4717928e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0363127e-08, Final residual = 1.48425e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00046493667, Final residual = 3.0914011e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00017728766, Final residual = 1.0545373e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.0392169e-05, Final residual = 3.5937548e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.4531772e-05, Final residual = 1.9793276e-07, No Iterations 6
time step continuity errors : sum local = 1.4180103e-10, global = -4.6379667e-14, cumulative = -1.2193849e-08
ExecutionTime = 176.39 s  ClockTime = 178 s

Time = 237

smoothSolver:  Solving for Ux, Initial residual = 1.0540424e-08, Final residual = 1.4935759e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.8943451e-09, Final residual = 9.8943451e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00044812448, Final residual = 1.9470727e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.6319397e-05, Final residual = 5.4717414e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.6920432e-05, Final residual = 2.3715246e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3484485e-05, Final residual = 6.6468353e-08, No Iterations 4
time step continuity errors : sum local = 4.9082088e-11, global = 4.8003066e-14, cumulative = -1.2193801e-08
ExecutionTime = 177.14 s  ClockTime = 178 s

Time = 238

smoothSolver:  Solving for Ux, Initial residual = 1.0641135e-08, Final residual = 1.4833024e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0029771e-08, Final residual = 1.4335972e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00045462165, Final residual = 2.4240368e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0001358536, Final residual = 8.1513249e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.9647242e-05, Final residual = 2.3648785e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.9175727e-05, Final residual = 1.5405348e-07, No Iterations 5
time step continuity errors : sum local = 1.1070134e-10, global = 1.650356e-14, cumulative = -1.2193785e-08
ExecutionTime = 177.93 s  ClockTime = 179 s

Time = 239

smoothSolver:  Solving for Ux, Initial residual = 1.0478385e-08, Final residual = 1.5006956e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.5919061e-09, Final residual = 9.5919061e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00044106997, Final residual = 3.5230064e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.0792838e-05, Final residual = 7.7850668e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.1339274e-05, Final residual = 2.9956084e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5303779e-05, Final residual = 7.7996539e-08, No Iterations 4
time step continuity errors : sum local = 5.7229414e-11, global = -1.0049482e-13, cumulative = -1.2193885e-08
ExecutionTime = 178.53 s  ClockTime = 180 s

Time = 240

smoothSolver:  Solving for Ux, Initial residual = 9.7905064e-09, Final residual = 9.7905064e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 9.2327819e-09, Final residual = 9.2327819e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00040187244, Final residual = 3.6607904e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.6333996e-05, Final residual = 5.3211648e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.1955159e-05, Final residual = 1.4860037e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.073576e-05, Final residual = 6.7868891e-08, No Iterations 4
time step continuity errors : sum local = 4.9817727e-11, global = 2.3908841e-13, cumulative = -1.2193646e-08
ExecutionTime = 179.14 s  ClockTime = 180 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.009891

Time = 241

smoothSolver:  Solving for Ux, Initial residual = 1.0648283e-08, Final residual = 1.4867663e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.9582631e-09, Final residual = 9.9582631e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00040263205, Final residual = 2.6297414e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0001521462, Final residual = 8.2777112e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.3528687e-05, Final residual = 4.0744055e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.1535674e-05, Final residual = 1.0118736e-07, No Iterations 3
time step continuity errors : sum local = 7.352559e-11, global = 2.5739242e-13, cumulative = -1.2193389e-08
ExecutionTime = 179.7 s  ClockTime = 181 s

Time = 242

smoothSolver:  Solving for Ux, Initial residual = 1.1023023e-08, Final residual = 1.4438122e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.068011e-08, Final residual = 1.4432956e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00041916845, Final residual = 2.2137923e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.7986222e-05, Final residual = 5.6457011e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.3788128e-05, Final residual = 8.5482194e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1798354e-05, Final residual = 6.5616741e-08, No Iterations 4
time step continuity errors : sum local = 4.8356219e-11, global = 1.9123038e-13, cumulative = -1.2193198e-08
ExecutionTime = 180.32 s  ClockTime = 181 s

Time = 243

smoothSolver:  Solving for Ux, Initial residual = 1.0848269e-08, Final residual = 1.4427739e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0447415e-08, Final residual = 1.4205648e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00043460097, Final residual = 3.0866325e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00017645976, Final residual = 1.0208166e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.910776e-05, Final residual = 2.7675476e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.3671189e-05, Final residual = 1.9841989e-07, No Iterations 3
time step continuity errors : sum local = 1.4191472e-10, global = 2.2823813e-13, cumulative = -1.219297e-08
ExecutionTime = 180.94 s  ClockTime = 182 s

Time = 244

smoothSolver:  Solving for Ux, Initial residual = 1.0930526e-08, Final residual = 1.4705448e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.9995553e-09, Final residual = 9.9995553e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00042365724, Final residual = 4.2177625e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.0038338e-05, Final residual = 3.5800764e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.6087149e-05, Final residual = 1.1323183e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1193117e-05, Final residual = 6.4648612e-08, No Iterations 4
time step continuity errors : sum local = 4.7839138e-11, global = -1.6516464e-13, cumulative = -1.2193135e-08
ExecutionTime = 181.61 s  ClockTime = 183 s

Time = 245

smoothSolver:  Solving for Ux, Initial residual = 1.082266e-08, Final residual = 1.4581948e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0018965e-08, Final residual = 1.381536e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00043534538, Final residual = 4.0825731e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.9783653e-05, Final residual = 9.8540815e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.3942765e-05, Final residual = 1.1159892e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.6177325e-05, Final residual = 9.7736009e-08, No Iterations 6
time step continuity errors : sum local = 7.0873362e-11, global = -7.9509917e-14, cumulative = -1.2193214e-08
ExecutionTime = 182.34 s  ClockTime = 183 s

Time = 246

smoothSolver:  Solving for Ux, Initial residual = 1.1824445e-08, Final residual = 1.4690172e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0646907e-08, Final residual = 1.3484875e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00044667389, Final residual = 2.9343801e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00016166985, Final residual = 1.0191361e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.6180312e-05, Final residual = 3.8322004e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.2160757e-05, Final residual = 1.6480835e-07, No Iterations 7
time step continuity errors : sum local = 1.1823063e-10, global = 3.3155312e-14, cumulative = -1.2193181e-08
ExecutionTime = 183.18 s  ClockTime = 184 s

Time = 247

smoothSolver:  Solving for Ux, Initial residual = 1.152279e-08, Final residual = 1.4937246e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.9934094e-09, Final residual = 9.9934094e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00043978505, Final residual = 3.5611871e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.2580698e-05, Final residual = 7.844104e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.1717386e-05, Final residual = 3.0708199e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5366045e-05, Final residual = 8.950413e-08, No Iterations 3
time step continuity errors : sum local = 6.5038593e-11, global = 9.8710838e-15, cumulative = -1.2193171e-08
ExecutionTime = 183.76 s  ClockTime = 185 s

Time = 248

smoothSolver:  Solving for Ux, Initial residual = 1.0737498e-08, Final residual = 1.4713392e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.5202748e-09, Final residual = 9.5202748e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00043393647, Final residual = 3.7680132e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00023306363, Final residual = 1.2338122e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.3118644e-05, Final residual = 5.9461223e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.0556772e-05, Final residual = 2.572603e-07, No Iterations 3
time step continuity errors : sum local = 1.8352113e-10, global = -5.933672e-14, cumulative = -1.219323e-08
ExecutionTime = 184.33 s  ClockTime = 185 s

Time = 249

smoothSolver:  Solving for Ux, Initial residual = 1.0297822e-08, Final residual = 1.4170624e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.7511407e-09, Final residual = 9.7511407e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0004254258, Final residual = 2.3015917e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00031342818, Final residual = 3.097495e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.0032023e-05, Final residual = 5.0796529e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.29702e-05, Final residual = 2.727358e-07, No Iterations 3
time step continuity errors : sum local = 1.9463964e-10, global = -9.2120412e-14, cumulative = -1.2193323e-08
ExecutionTime = 184.95 s  ClockTime = 186 s

Time = 250

smoothSolver:  Solving for Ux, Initial residual = 9.9666629e-09, Final residual = 9.9666629e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 1.0266745e-08, Final residual = 1.4604352e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0004118908, Final residual = 2.6871903e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0001514299, Final residual = 8.6240197e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.3053724e-05, Final residual = 4.2222604e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.0976463e-05, Final residual = 9.8619699e-08, No Iterations 3
time step continuity errors : sum local = 7.158905e-11, global = -2.2784655e-15, cumulative = -1.2193325e-08
ExecutionTime = 185.97 s  ClockTime = 187 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 251

smoothSolver:  Solving for Ux, Initial residual = 9.4456003e-09, Final residual = 9.4456003e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 9.4563373e-09, Final residual = 9.4563373e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00038258646, Final residual = 3.3605429e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00020610356, Final residual = 2.0303091e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.4082549e-05, Final residual = 3.6711457e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.0975195e-05, Final residual = 2.251735e-07, No Iterations 3
time step continuity errors : sum local = 1.6082367e-10, global = -9.9125642e-14, cumulative = -1.2193424e-08
ExecutionTime = 186.54 s  ClockTime = 188 s

Time = 252

smoothSolver:  Solving for Ux, Initial residual = 9.4112279e-09, Final residual = 9.4112279e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.9014316e-09, Final residual = 8.9014316e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00034963547, Final residual = 3.4905875e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00022206783, Final residual = 2.1444366e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.7830582e-05, Final residual = 3.8718086e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2491076e-05, Final residual = 2.0771739e-07, No Iterations 3
time step continuity errors : sum local = 1.4877628e-10, global = -9.995384e-14, cumulative = -1.2193524e-08
ExecutionTime = 187.14 s  ClockTime = 188 s

Time = 253

smoothSolver:  Solving for Ux, Initial residual = 9.8650353e-09, Final residual = 9.8650353e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.5989547e-09, Final residual = 8.5989547e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0003276524, Final residual = 3.2334191e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00020613718, Final residual = 1.9678607e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.3892911e-05, Final residual = 3.8867593e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.0055641e-05, Final residual = 2.7049945e-07, No Iterations 7
time step continuity errors : sum local = 1.9317335e-10, global = -9.9860418e-14, cumulative = -1.2193624e-08
ExecutionTime = 187.81 s  ClockTime = 189 s

Time = 254

smoothSolver:  Solving for Ux, Initial residual = 1.014258e-08, Final residual = 1.5086677e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 8.2717504e-09, Final residual = 8.2717504e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00035311946, Final residual = 2.775524e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.5283215e-05, Final residual = 6.4263864e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.6338863e-05, Final residual = 9.1965313e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.3287835e-05, Final residual = 1.2556346e-07, No Iterations 3
time step continuity errors : sum local = 9.0316921e-11, global = -1.4674583e-13, cumulative = -1.2193771e-08
ExecutionTime = 188.44 s  ClockTime = 190 s

Time = 255

smoothSolver:  Solving for Ux, Initial residual = 9.976076e-09, Final residual = 9.976076e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.345289e-09, Final residual = 8.345289e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0003377997, Final residual = 1.9470782e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.3558645e-05, Final residual = 5.2859612e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.2872499e-05, Final residual = 2.0033466e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 1.228712e-05, Final residual = 9.7064426e-08, No Iterations 5
time step continuity errors : sum local = 7.0701559e-11, global = 5.5872618e-14, cumulative = -1.2193715e-08
ExecutionTime = 189.07 s  ClockTime = 190 s

Time = 256

smoothSolver:  Solving for Ux, Initial residual = 1.0173369e-08, Final residual = 1.4770102e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 8.6698575e-09, Final residual = 8.6698575e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00035369918, Final residual = 3.4974274e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00021758321, Final residual = 1.1496725e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.8468601e-05, Final residual = 5.5825583e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.8237684e-05, Final residual = 1.1868077e-07, No Iterations 3
time step continuity errors : sum local = 8.5698461e-11, global = 2.1155939e-13, cumulative = -1.2193503e-08
ExecutionTime = 189.68 s  ClockTime = 191 s

Time = 257

smoothSolver:  Solving for Ux, Initial residual = 1.1030646e-08, Final residual = 1.4176908e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0011926e-08, Final residual = 1.3163195e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00036466074, Final residual = 1.7237424e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.6895716e-05, Final residual = 5.6288667e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.9087972e-05, Final residual = 2.8833601e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4740996e-05, Final residual = 8.2842377e-08, No Iterations 3
time step continuity errors : sum local = 6.0264875e-11, global = 4.8698713e-14, cumulative = -1.2193454e-08
ExecutionTime = 190.24 s  ClockTime = 192 s

Time = 258

smoothSolver:  Solving for Ux, Initial residual = 1.0565788e-08, Final residual = 1.393276e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.8111825e-09, Final residual = 9.8111825e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00037041013, Final residual = 3.2589283e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00020103248, Final residual = 1.9847596e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.329278e-05, Final residual = 3.6141123e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.0632252e-05, Final residual = 2.0976681e-07, No Iterations 3
time step continuity errors : sum local = 1.499652e-10, global = 8.9814749e-14, cumulative = -1.2193365e-08
ExecutionTime = 190.81 s  ClockTime = 192 s

Time = 259

smoothSolver:  Solving for Ux, Initial residual = 1.0201321e-08, Final residual = 1.3470422e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0003858e-08, Final residual = 1.3792056e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00039594261, Final residual = 1.3195152e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.4822683e-05, Final residual = 4.6721307e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.2961531e-05, Final residual = 2.1252194e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1748989e-05, Final residual = 1.083174e-07, No Iterations 3
time step continuity errors : sum local = 7.8609937e-11, global = -1.0529958e-13, cumulative = -1.219347e-08
ExecutionTime = 191.38 s  ClockTime = 193 s

Time = 260

smoothSolver:  Solving for Ux, Initial residual = 9.2795925e-09, Final residual = 9.2795925e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 9.2124071e-09, Final residual = 9.2124071e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00036826937, Final residual = 1.8681639e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00010561786, Final residual = 6.2102851e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.1131959e-05, Final residual = 2.9994437e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5405031e-05, Final residual = 7.226806e-08, No Iterations 4
time step continuity errors : sum local = 5.3050637e-11, global = -2.2927344e-14, cumulative = -1.2193493e-08
ExecutionTime = 191.98 s  ClockTime = 193 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 261

smoothSolver:  Solving for Ux, Initial residual = 9.5578056e-09, Final residual = 9.5578056e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 9.2613641e-09, Final residual = 9.2613641e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00033988317, Final residual = 2.4990771e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00014800683, Final residual = 1.477107e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.9893573e-05, Final residual = 1.4176548e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.2606297e-05, Final residual = 1.9572915e-07, No Iterations 3
time step continuity errors : sum local = 1.4034011e-10, global = 2.937783e-13, cumulative = -1.2193199e-08
ExecutionTime = 192.55 s  ClockTime = 194 s

Time = 262

smoothSolver:  Solving for Ux, Initial residual = 9.8245472e-09, Final residual = 9.8245472e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 9.1190124e-09, Final residual = 9.1190124e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00031390081, Final residual = 2.6927025e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00016519953, Final residual = 1.6107876e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.3817484e-05, Final residual = 3.0378826e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.4682362e-05, Final residual = 9.863628e-08, No Iterations 3
time step continuity errors : sum local = 7.140961e-11, global = 2.6378501e-13, cumulative = -1.2192935e-08
ExecutionTime = 193.14 s  ClockTime = 194 s

Time = 263

smoothSolver:  Solving for Ux, Initial residual = 1.0683755e-08, Final residual = 1.4268984e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.3637636e-09, Final residual = 9.3637636e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00032604538, Final residual = 2.4972412e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.5367933e-05, Final residual = 5.7192224e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.2894331e-05, Final residual = 2.2751494e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1311253e-05, Final residual = 8.6822263e-08, No Iterations 3
time step continuity errors : sum local = 6.330185e-11, global = -3.1149096e-13, cumulative = -1.2193247e-08
ExecutionTime = 193.7 s  ClockTime = 195 s

Time = 264

smoothSolver:  Solving for Ux, Initial residual = 1.0643075e-08, Final residual = 1.402413e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.4901771e-09, Final residual = 9.4901771e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00034317003, Final residual = 3.2672465e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00020436656, Final residual = 1.069456e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.526484e-05, Final residual = 5.087143e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.6863037e-05, Final residual = 2.6509052e-07, No Iterations 3
time step continuity errors : sum local = 1.8906479e-10, global = 5.0583756e-14, cumulative = -1.2193196e-08
ExecutionTime = 194.27 s  ClockTime = 196 s

Time = 265

smoothSolver:  Solving for Ux, Initial residual = 9.9466682e-09, Final residual = 9.9466682e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 9.4980946e-09, Final residual = 9.4980946e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0003148399, Final residual = 1.8682248e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00010567733, Final residual = 5.8560392e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.0872375e-05, Final residual = 2.8069857e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5384983e-05, Final residual = 7.0487242e-08, No Iterations 4
time step continuity errors : sum local = 5.1821631e-11, global = -8.6275883e-14, cumulative = -1.2193282e-08
ExecutionTime = 194.87 s  ClockTime = 196 s

Time = 266

smoothSolver:  Solving for Ux, Initial residual = 1.0011609e-08, Final residual = 1.3373486e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.8161175e-09, Final residual = 9.8161175e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0003290014, Final residual = 2.9548809e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00018413165, Final residual = 1.8079606e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.8912891e-05, Final residual = 3.530474e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.8312927e-05, Final residual = 1.374083e-07, No Iterations 3
time step continuity errors : sum local = 9.8945016e-11, global = -2.5041548e-13, cumulative = -1.2193533e-08
ExecutionTime = 195.46 s  ClockTime = 197 s

Time = 267

smoothSolver:  Solving for Ux, Initial residual = 1.0713239e-08, Final residual = 1.2898873e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0893328e-08, Final residual = 1.3886483e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00036193067, Final residual = 2.3532764e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.8621516e-05, Final residual = 5.7528448e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.3773132e-05, Final residual = 2.3719903e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.176348e-05, Final residual = 1.0495631e-07, No Iterations 3
time step continuity errors : sum local = 7.631682e-11, global = -1.9467e-15, cumulative = -1.2193535e-08
ExecutionTime = 196.11 s  ClockTime = 197 s

Time = 268

smoothSolver:  Solving for Ux, Initial residual = 9.5333288e-09, Final residual = 9.5333288e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 9.7463655e-09, Final residual = 9.7463655e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00033882536, Final residual = 2.3729189e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00013792109, Final residual = 7.821982e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.8218383e-05, Final residual = 1.0657085e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.8543225e-05, Final residual = 1.7233647e-07, No Iterations 3
time step continuity errors : sum local = 1.2370107e-10, global = -3.0145603e-15, cumulative = -1.2193538e-08
ExecutionTime = 196.68 s  ClockTime = 198 s

Time = 269

smoothSolver:  Solving for Ux, Initial residual = 8.8046875e-09, Final residual = 8.8046875e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.7668813e-09, Final residual = 8.7668813e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00031339087, Final residual = 2.8915718e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00017986521, Final residual = 1.7564985e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.690831e-05, Final residual = 3.2641796e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.6893311e-05, Final residual = 1.8790943e-07, No Iterations 3
time step continuity errors : sum local = 1.3469637e-10, global = -1.3363055e-13, cumulative = -1.2193671e-08
ExecutionTime = 197.31 s  ClockTime = 199 s

Time = 270

smoothSolver:  Solving for Ux, Initial residual = 9.2041491e-09, Final residual = 9.2041491e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.5485592e-09, Final residual = 8.5485592e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0002935159, Final residual = 1.5536607e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00019486321, Final residual = 1.8784504e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.9937939e-05, Final residual = 3.4290968e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.648397e-05, Final residual = 2.3467981e-07, No Iterations 3
time step continuity errors : sum local = 1.6787862e-10, global = 7.1675605e-14, cumulative = -1.21936e-08
ExecutionTime = 197.94 s  ClockTime = 199 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 271

smoothSolver:  Solving for Ux, Initial residual = 1.0543671e-08, Final residual = 1.3985648e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.1494261e-09, Final residual = 9.1494261e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00031505198, Final residual = 1.6242953e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.4479381e-05, Final residual = 4.5220723e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.9943827e-05, Final residual = 7.538975e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 1.0413097e-05, Final residual = 8.248463e-08, No Iterations 4
time step continuity errors : sum local = 6.0417783e-11, global = -5.3868499e-15, cumulative = -1.2193605e-08
ExecutionTime = 198.55 s  ClockTime = 200 s

Time = 272

smoothSolver:  Solving for Ux, Initial residual = 1.0326763e-08, Final residual = 1.378863e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.0742386e-09, Final residual = 9.0742386e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00033631235, Final residual = 3.0924202e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00019203016, Final residual = 1.0174888e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.215704e-05, Final residual = 5.0187688e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.5443947e-05, Final residual = 2.3620275e-07, No Iterations 3
time step continuity errors : sum local = 1.6869602e-10, global = -7.6263191e-15, cumulative = -1.2193613e-08
ExecutionTime = 199.3 s  ClockTime = 201 s

Time = 273

smoothSolver:  Solving for Ux, Initial residual = 9.6230885e-09, Final residual = 9.6230885e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 9.0530737e-09, Final residual = 9.0530737e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00030601729, Final residual = 1.8171039e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00010341815, Final residual = 5.8089787e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.0388842e-05, Final residual = 3.0174434e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5291445e-05, Final residual = 9.522952e-08, No Iterations 3
time step continuity errors : sum local = 6.9094341e-11, global = -6.2573279e-14, cumulative = -1.2193675e-08
ExecutionTime = 200.03 s  ClockTime = 201 s

Time = 274

smoothSolver:  Solving for Ux, Initial residual = 8.8550468e-09, Final residual = 8.8550468e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.680353e-09, Final residual = 8.680353e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00028501768, Final residual = 2.5531479e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.9850494e-05, Final residual = 1.4702784e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.5953643e-05, Final residual = 1.0890035e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.0898527e-06, Final residual = 7.3343576e-08, No Iterations 3
time step continuity errors : sum local = 5.3843777e-11, global = 2.4302468e-13, cumulative = -1.2193432e-08
ExecutionTime = 200.61 s  ClockTime = 202 s

Time = 275

smoothSolver:  Solving for Ux, Initial residual = 1.0000029e-08, Final residual = 1.3142262e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.6505242e-09, Final residual = 9.6505242e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00030135413, Final residual = 2.0658711e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00011977813, Final residual = 6.6734897e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.386467e-05, Final residual = 1.0129082e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.6855296e-05, Final residual = 9.9887825e-08, No Iterations 4
time step continuity errors : sum local = 7.2181672e-11, global = -7.4129423e-14, cumulative = -1.2193506e-08
ExecutionTime = 201.22 s  ClockTime = 203 s

Time = 276

smoothSolver:  Solving for Ux, Initial residual = 8.6430058e-09, Final residual = 8.6430058e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.7890291e-09, Final residual = 8.7890291e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00028813818, Final residual = 2.6934425e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.2274769e-05, Final residual = 4.1795917e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.661626e-05, Final residual = 7.2911879e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.6338859e-06, Final residual = 6.4282713e-08, No Iterations 5
time step continuity errors : sum local = 4.7709427e-11, global = 6.1186748e-14, cumulative = -1.2193445e-08
ExecutionTime = 201.87 s  ClockTime = 203 s

Time = 277

smoothSolver:  Solving for Ux, Initial residual = 8.5535147e-09, Final residual = 8.5535147e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.7241638e-09, Final residual = 8.7241638e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00027851249, Final residual = 1.6533229e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.2320083e-05, Final residual = 5.6860509e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.642729e-05, Final residual = 8.9697278e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.3121388e-05, Final residual = 7.4309513e-08, No Iterations 5
time step continuity errors : sum local = 5.4740268e-11, global = 2.0766737e-13, cumulative = -1.2193238e-08
ExecutionTime = 202.55 s  ClockTime = 204 s

Time = 278

smoothSolver:  Solving for Ux, Initial residual = 8.9484616e-09, Final residual = 8.9484616e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.8171939e-09, Final residual = 8.8171939e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00026710701, Final residual = 2.3165318e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00014124315, Final residual = 1.3903886e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.706127e-05, Final residual = 1.3247968e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.0984341e-05, Final residual = 1.0558007e-07, No Iterations 5
time step continuity errors : sum local = 7.6872014e-11, global = 1.1396277e-13, cumulative = -1.2193124e-08
ExecutionTime = 203.22 s  ClockTime = 205 s

Time = 279

smoothSolver:  Solving for Ux, Initial residual = 9.0845995e-09, Final residual = 9.0845995e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.5622943e-09, Final residual = 8.5622943e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00025728046, Final residual = 2.5685226e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00016271317, Final residual = 1.5631438e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.2259157e-05, Final residual = 3.3118478e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.3820611e-05, Final residual = 9.6643643e-08, No Iterations 4
time step continuity errors : sum local = 6.9998531e-11, global = -1.6271756e-13, cumulative = -1.2193286e-08
ExecutionTime = 203.9 s  ClockTime = 205 s

Time = 280

smoothSolver:  Solving for Ux, Initial residual = 9.8030329e-09, Final residual = 9.8030329e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.7142053e-09, Final residual = 8.7142053e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00025694177, Final residual = 2.5339972e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00015966182, Final residual = 1.520196e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.1657825e-05, Final residual = 4.1460265e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.3743861e-05, Final residual = 1.183052e-07, No Iterations 4
time step continuity errors : sum local = 8.5204032e-11, global = -1.2070348e-13, cumulative = -1.2193407e-08
ExecutionTime = 204.66 s  ClockTime = 206 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.161494e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 281

smoothSolver:  Solving for Ux, Initial residual = 1.0683997e-08, Final residual = 1.3852088e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.0252888e-09, Final residual = 9.0252888e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0002928341, Final residual = 1.4077729e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.0589648e-05, Final residual = 4.7131465e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.4129577e-05, Final residual = 2.2052515e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 1.255572e-05, Final residual = 8.5315205e-08, No Iterations 3
time step continuity errors : sum local = 6.2128104e-11, global = 1.176175e-13, cumulative = -1.2193289e-08
ExecutionTime = 205.38 s  ClockTime = 207 s

Time = 282

smoothSolver:  Solving for Ux, Initial residual = 9.3232112e-09, Final residual = 9.3232112e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.0795815e-09, Final residual = 8.0795815e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00028195837, Final residual = 1.82712e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.5497163e-05, Final residual = 5.1398403e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.0005699e-05, Final residual = 1.2213573e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.8972845e-06, Final residual = 6.7269194e-08, No Iterations 9
time step continuity errors : sum local = 4.9636494e-11, global = -2.6519482e-13, cumulative = -1.2193555e-08
ExecutionTime = 206.1 s  ClockTime = 207 s

Time = 283

smoothSolver:  Solving for Ux, Initial residual = 1.050725e-08, Final residual = 1.3524916e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.1723726e-09, Final residual = 9.1723726e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00029983615, Final residual = 2.9592396e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00019079347, Final residual = 1.9069168e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.97478e-05, Final residual = 3.8163689e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.8872805e-05, Final residual = 1.3823574e-07, No Iterations 3
time step continuity errors : sum local = 9.9638793e-11, global = 2.5442742e-14, cumulative = -1.2193529e-08
ExecutionTime = 206.74 s  ClockTime = 208 s

Time = 284

smoothSolver:  Solving for Ux, Initial residual = 9.3569554e-09, Final residual = 9.3569554e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.7272026e-09, Final residual = 8.7272026e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00027434892, Final residual = 1.7676146e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00010378224, Final residual = 5.8719157e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.9575006e-05, Final residual = 1.0338355e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.4863358e-05, Final residual = 8.3211593e-08, No Iterations 3
time step continuity errors : sum local = 6.0748027e-11, global = -5.57593e-13, cumulative = -1.2194087e-08
ExecutionTime = 207.4 s  ClockTime = 209 s

Time = 285

smoothSolver:  Solving for Ux, Initial residual = 1.1264576e-08, Final residual = 1.2845324e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0615796e-08, Final residual = 1.2660006e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00030570793, Final residual = 2.4379646e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.2947506e-05, Final residual = 3.6168775e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.2264776e-05, Final residual = 1.5460124e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0012841e-05, Final residual = 6.8511189e-08, No Iterations 5
time step continuity errors : sum local = 5.0454869e-11, global = 8.3721135e-14, cumulative = -1.2194003e-08
ExecutionTime = 208.1 s  ClockTime = 209 s

Time = 286

smoothSolver:  Solving for Ux, Initial residual = 8.8141565e-09, Final residual = 8.8141565e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.3983158e-09, Final residual = 8.3983158e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00028854323, Final residual = 1.8553724e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00010588484, Final residual = 6.5595113e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.977132e-05, Final residual = 9.9454348e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.4816621e-05, Final residual = 1.1854323e-07, No Iterations 5
time step continuity errors : sum local = 8.5535242e-11, global = 4.7450717e-14, cumulative = -1.2193956e-08
ExecutionTime = 208.74 s  ClockTime = 210 s

Time = 287

smoothSolver:  Solving for Ux, Initial residual = 9.5982751e-09, Final residual = 9.5982751e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.8239071e-09, Final residual = 8.8239071e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00027280383, Final residual = 2.1151886e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0001271651, Final residual = 7.5078865e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4882214e-05, Final residual = 1.0665184e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.7077352e-05, Final residual = 7.7082805e-08, No Iterations 6
time step continuity errors : sum local = 5.679426e-11, global = 1.9031704e-13, cumulative = -1.2193765e-08
ExecutionTime = 209.39 s  ClockTime = 211 s

Time = 288

smoothSolver:  Solving for Ux, Initial residual = 1.1240227e-08, Final residual = 1.3322963e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.9110338e-09, Final residual = 9.9110338e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00028673019, Final residual = 1.3676926e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7133547e-05, Final residual = 4.5591276e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.2706349e-05, Final residual = 1.0058556e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1567799e-05, Final residual = 9.2604576e-08, No Iterations 4
time step continuity errors : sum local = 6.7538036e-11, global = -7.7354902e-14, cumulative = -1.2193843e-08
ExecutionTime = 210.26 s  ClockTime = 212 s

Time = 289

smoothSolver:  Solving for Ux, Initial residual = 1.0211372e-08, Final residual = 1.3062672e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.1864254e-09, Final residual = 9.1864254e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00030324821, Final residual = 1.5033736e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0002049084, Final residual = 2.0446238e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.285138e-05, Final residual = 3.6559725e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.9093919e-05, Final residual = 2.2280473e-07, No Iterations 3
time step continuity errors : sum local = 1.5937121e-10, global = 4.8189884e-14, cumulative = -1.2193795e-08
ExecutionTime = 211.21 s  ClockTime = 213 s

Time = 290

smoothSolver:  Solving for Ux, Initial residual = 9.7442209e-09, Final residual = 9.7442209e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 9.3010849e-09, Final residual = 9.3010849e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00028198636, Final residual = 1.7522256e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00010184778, Final residual = 5.8641775e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.9301155e-05, Final residual = 2.0439306e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.5021484e-05, Final residual = 1.3859076e-07, No Iterations 5
time step continuity errors : sum local = 9.9807281e-11, global = 9.5107467e-14, cumulative = -1.2193699e-08
ExecutionTime = 212.17 s  ClockTime = 213 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.009891

Time = 291

smoothSolver:  Solving for Ux, Initial residual = 9.3020903e-09, Final residual = 9.3020903e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 9.1878525e-09, Final residual = 9.1878525e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00027167752, Final residual = 2.4054992e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.8327279e-05, Final residual = 3.3935736e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4327756e-05, Final residual = 1.392257e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.2249926e-06, Final residual = 6.5000386e-08, No Iterations 4
time step continuity errors : sum local = 4.7821204e-11, global = -1.3481913e-13, cumulative = -1.2193834e-08
ExecutionTime = 212.92 s  ClockTime = 214 s

Time = 292

smoothSolver:  Solving for Ux, Initial residual = 8.5304279e-09, Final residual = 8.5304279e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.5725975e-09, Final residual = 8.5725975e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0002637129, Final residual = 1.5471784e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.8610565e-05, Final residual = 5.3745853e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.4938694e-05, Final residual = 8.6506636e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2337984e-05, Final residual = 8.4392126e-08, No Iterations 3
time step continuity errors : sum local = 6.1670624e-11, global = 2.9367836e-13, cumulative = -1.2193541e-08
ExecutionTime = 213.57 s  ClockTime = 215 s

Time = 293

smoothSolver:  Solving for Ux, Initial residual = 8.8407113e-09, Final residual = 8.8407113e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.5929652e-09, Final residual = 8.5929652e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00025307504, Final residual = 2.1118474e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00013080074, Final residual = 1.3048534e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.4233033e-05, Final residual = 2.5792467e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.977e-05, Final residual = 1.6976188e-07, No Iterations 3
time step continuity errors : sum local = 1.2182904e-10, global = 1.3441876e-13, cumulative = -1.2193406e-08
ExecutionTime = 214.19 s  ClockTime = 215 s

Time = 294

smoothSolver:  Solving for Ux, Initial residual = 8.9843527e-09, Final residual = 8.9843527e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.3080202e-09, Final residual = 8.3080202e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00024318, Final residual = 2.3246594e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00014825159, Final residual = 1.4372476e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.8460529e-05, Final residual = 2.8824951e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.1908953e-05, Final residual = 1.9229631e-07, No Iterations 3
time step continuity errors : sum local = 1.3756126e-10, global = 2.2182035e-13, cumulative = -1.2193184e-08
ExecutionTime = 214.77 s  ClockTime = 216 s

Time = 295

smoothSolver:  Solving for Ux, Initial residual = 9.5529562e-09, Final residual = 9.5529562e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.3634106e-09, Final residual = 8.3634106e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00024168824, Final residual = 2.2723049e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00014382608, Final residual = 1.3748595e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.7572372e-05, Final residual = 1.4116728e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.1221465e-05, Final residual = 1.2492488e-07, No Iterations 4
time step continuity errors : sum local = 8.9890151e-11, global = 4.4910284e-13, cumulative = -1.2192735e-08
ExecutionTime = 215.39 s  ClockTime = 217 s

Time = 296

smoothSolver:  Solving for Ux, Initial residual = 1.098934e-08, Final residual = 1.3372396e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.2042067e-09, Final residual = 9.2042067e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00027523736, Final residual = 1.5036725e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.5822552e-05, Final residual = 4.8418835e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.4837313e-05, Final residual = 1.9971968e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2863333e-05, Final residual = 7.5404648e-08, No Iterations 3
time step continuity errors : sum local = 5.5516466e-11, global = 2.6089933e-13, cumulative = -1.2192474e-08
ExecutionTime = 215.99 s  ClockTime = 217 s

Time = 297

smoothSolver:  Solving for Ux, Initial residual = 1.0063792e-08, Final residual = 1.3080257e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 8.6563461e-09, Final residual = 8.6563461e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00029711889, Final residual = 1.629353e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00023066575, Final residual = 8.284368e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.9159585e-05, Final residual = 5.2901864e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.8726516e-05, Final residual = 1.657813e-07, No Iterations 3
time step continuity errors : sum local = 1.1883384e-10, global = -9.7687335e-15, cumulative = -1.2192484e-08
ExecutionTime = 216.58 s  ClockTime = 218 s

Time = 298

smoothSolver:  Solving for Ux, Initial residual = 8.8166926e-09, Final residual = 8.8166926e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.3020954e-09, Final residual = 8.3020954e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00026819092, Final residual = 2.137111e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00013273214, Final residual = 7.3598016e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.664465e-05, Final residual = 1.1066758e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.8093204e-05, Final residual = 1.1144093e-07, No Iterations 3
time step continuity errors : sum local = 8.0640163e-11, global = -3.3239386e-13, cumulative = -1.2192816e-08
ExecutionTime = 217.2 s  ClockTime = 219 s

Time = 299

smoothSolver:  Solving for Ux, Initial residual = 1.1495814e-08, Final residual = 1.2312427e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0992224e-08, Final residual = 1.2331537e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00029518592, Final residual = 1.620419e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.9511173e-05, Final residual = 4.9290665e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.750584e-05, Final residual = 1.4659976e-07, No Iterations 7
GAMG:  Solving for p, Initial residual = 9.2212931e-06, Final residual = 6.916091e-08, No Iterations 3
time step continuity errors : sum local = 5.1048162e-11, global = 4.5457051e-14, cumulative = -1.2192771e-08
ExecutionTime = 217.85 s  ClockTime = 219 s

Time = 300

smoothSolver:  Solving for Ux, Initial residual = 1.100666e-08, Final residual = 1.226981e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0447732e-08, Final residual = 1.2144784e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00032209646, Final residual = 2.4575236e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00014584647, Final residual = 8.8354223e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.9719665e-05, Final residual = 1.1730532e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.9268871e-05, Final residual = 9.632915e-08, No Iterations 3
time step continuity errors : sum local = 7.0208563e-11, global = -3.5810155e-13, cumulative = -1.2193129e-08
ExecutionTime = 218.99 s  ClockTime = 221 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305954e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.161494e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 301

smoothSolver:  Solving for Ux, Initial residual = 1.2023166e-08, Final residual = 1.2503084e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.0939501e-08, Final residual = 1.17173e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00033559642, Final residual = 3.13384e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00019451803, Final residual = 1.8883615e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.0071402e-05, Final residual = 3.9954838e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.8430369e-05, Final residual = 2.2548671e-07, No Iterations 5
time step continuity errors : sum local = 1.6134853e-10, global = -6.4558583e-14, cumulative = -1.2193194e-08
ExecutionTime = 219.59 s  ClockTime = 221 s

Time = 302

smoothSolver:  Solving for Ux, Initial residual = 1.0626754e-08, Final residual = 1.2858323e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.1602396e-09, Final residual = 9.1602396e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00033117267, Final residual = 2.9967673e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.6310073e-05, Final residual = 2.110903e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.9726655e-05, Final residual = 1.0486969e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.9691871e-06, Final residual = 6.3586418e-08, No Iterations 7
time step continuity errors : sum local = 4.720473e-11, global = 6.4998125e-14, cumulative = -1.2193129e-08
ExecutionTime = 220.19 s  ClockTime = 222 s

Time = 303

smoothSolver:  Solving for Ux, Initial residual = 8.7605796e-09, Final residual = 8.7605796e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.6617348e-09, Final residual = 7.6617348e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00030718079, Final residual = 2.4809524e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.2782142e-05, Final residual = 4.265124e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.803298e-05, Final residual = 8.4565834e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 8.6081953e-06, Final residual = 7.4447338e-08, No Iterations 4
time step continuity errors : sum local = 5.4546719e-11, global = -1.5550975e-13, cumulative = -1.2193284e-08
ExecutionTime = 220.85 s  ClockTime = 222 s

Time = 304

smoothSolver:  Solving for Ux, Initial residual = 8.9519168e-09, Final residual = 8.9519168e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.8198159e-09, Final residual = 7.8198159e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00028757061, Final residual = 1.6413726e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.844742e-05, Final residual = 1.3380246e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.7234333e-05, Final residual = 1.489173e-07, No Iterations 7
GAMG:  Solving for p, Initial residual = 9.0844929e-06, Final residual = 7.3518653e-08, No Iterations 3
time step continuity errors : sum local = 5.3745991e-11, global = -5.5032868e-14, cumulative = -1.2193339e-08
ExecutionTime = 221.47 s  ClockTime = 223 s

Time = 305

smoothSolver:  Solving for Ux, Initial residual = 9.6303865e-09, Final residual = 9.6303865e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.3055026e-09, Final residual = 8.3055026e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00027187457, Final residual = 2.0863354e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.3948441e-05, Final residual = 1.6695918e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.8777095e-05, Final residual = 1.0914315e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.5952174e-06, Final residual = 7.2416634e-08, No Iterations 6
time step continuity errors : sum local = 5.3118356e-11, global = 1.0387742e-13, cumulative = -1.2193235e-08
ExecutionTime = 222.07 s  ClockTime = 224 s

Time = 306

smoothSolver:  Solving for Ux, Initial residual = 1.0753194e-08, Final residual = 1.292024e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.1470849e-09, Final residual = 9.1470849e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00028702617, Final residual = 2.343019e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00014554244, Final residual = 7.659663e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.9356056e-05, Final residual = 3.8597212e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.9237111e-05, Final residual = 9.5854284e-08, No Iterations 3
time step continuity errors : sum local = 6.965694e-11, global = 1.0795968e-13, cumulative = -1.2193127e-08
ExecutionTime = 222.64 s  ClockTime = 224 s

Time = 307

smoothSolver:  Solving for Ux, Initial residual = 1.0609101e-08, Final residual = 1.2500752e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.407464e-09, Final residual = 9.407464e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00029736254, Final residual = 1.8544347e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00025778856, Final residual = 2.5496532e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.503585e-05, Final residual = 4.4423805e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.4977766e-05, Final residual = 2.7598848e-07, No Iterations 3
time step continuity errors : sum local = 1.9676791e-10, global = 1.0098647e-13, cumulative = -1.2193026e-08
ExecutionTime = 223.26 s  ClockTime = 225 s

Time = 308

smoothSolver:  Solving for Ux, Initial residual = 1.002461e-08, Final residual = 1.1904153e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 9.5522809e-09, Final residual = 9.5522809e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0003116994, Final residual = 2.1925814e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00029970582, Final residual = 2.9815996e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.5167466e-05, Final residual = 5.8992682e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.0025281e-05, Final residual = 1.4709345e-07, No Iterations 6
time step continuity errors : sum local = 1.0574669e-10, global = -1.2294755e-13, cumulative = -1.2193149e-08
ExecutionTime = 223.87 s  ClockTime = 225 s

Time = 309

smoothSolver:  Solving for Ux, Initial residual = 8.1548678e-09, Final residual = 8.1548678e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.7810302e-09, Final residual = 8.7810302e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00030787876, Final residual = 2.2675294e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00013725562, Final residual = 9.0240619e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.9226444e-05, Final residual = 2.0663625e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.8591223e-05, Final residual = 1.696226e-07, No Iterations 11
time step continuity errors : sum local = 1.2169823e-10, global = -1.7591267e-13, cumulative = -1.2193325e-08
ExecutionTime = 224.52 s  ClockTime = 226 s

Time = 310

smoothSolver:  Solving for Ux, Initial residual = 8.9169406e-09, Final residual = 8.9169406e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 9.8535528e-09, Final residual = 9.8535528e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00031221856, Final residual = 1.8182423e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.5315006e-05, Final residual = 5.4428688e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.2384781e-05, Final residual = 9.1829098e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 1.2090203e-05, Final residual = 8.6653491e-08, No Iterations 4
time step continuity errors : sum local = 6.3045062e-11, global = -1.3451075e-14, cumulative = -1.2193339e-08
ExecutionTime = 225.16 s  ClockTime = 227 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 311

smoothSolver:  Solving for Ux, Initial residual = 8.7905109e-09, Final residual = 8.7905109e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 9.7020328e-09, Final residual = 9.7020328e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00030400029, Final residual = 2.4162647e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00014451302, Final residual = 8.6317113e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.8974574e-05, Final residual = 2.8223216e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.9599203e-05, Final residual = 1.4226241e-07, No Iterations 3
time step continuity errors : sum local = 1.0266709e-10, global = 7.0922227e-14, cumulative = -1.2193268e-08
ExecutionTime = 225.89 s  ClockTime = 227 s

Time = 312

smoothSolver:  Solving for Ux, Initial residual = 8.0908755e-09, Final residual = 8.0908755e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.6474745e-09, Final residual = 8.6474745e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00027992848, Final residual = 1.5483443e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00020717729, Final residual = 7.6244836e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.2261322e-05, Final residual = 5.0224825e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.5093911e-05, Final residual = 8.8303406e-08, No Iterations 4
time step continuity errors : sum local = 6.4338306e-11, global = 5.1536754e-14, cumulative = -1.2193216e-08
ExecutionTime = 227.09 s  ClockTime = 229 s

Time = 313

smoothSolver:  Solving for Ux, Initial residual = 8.075444e-09, Final residual = 8.075444e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.019608e-09, Final residual = 8.019608e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00025306024, Final residual = 1.6861743e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00022770622, Final residual = 8.2170642e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.7199847e-05, Final residual = 5.559599e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.7442847e-05, Final residual = 2.555477e-07, No Iterations 3
time step continuity errors : sum local = 1.8248592e-10, global = -2.9618897e-14, cumulative = -1.2193246e-08
ExecutionTime = 227.68 s  ClockTime = 229 s

Time = 314

smoothSolver:  Solving for Ux, Initial residual = 8.4881486e-09, Final residual = 8.4881486e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.6952614e-09, Final residual = 7.6952614e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00024451613, Final residual = 1.6426519e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00021578462, Final residual = 8.0819781e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.4612723e-05, Final residual = 3.5972187e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.6073438e-05, Final residual = 1.4536497e-07, No Iterations 4
time step continuity errors : sum local = 1.0449857e-10, global = -2.1888281e-13, cumulative = -1.2193465e-08
ExecutionTime = 228.28 s  ClockTime = 230 s

Time = 315

smoothSolver:  Solving for Ux, Initial residual = 9.6232176e-09, Final residual = 9.6232176e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.0354546e-09, Final residual = 8.0354546e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00025838313, Final residual = 1.4710029e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00018197165, Final residual = 1.8187537e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.6480039e-05, Final residual = 4.5564378e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.5298074e-05, Final residual = 2.2906667e-07, No Iterations 6
time step continuity errors : sum local = 1.636798e-10, global = -8.7719278e-14, cumulative = -1.2193552e-08
ExecutionTime = 228.88 s  ClockTime = 230 s

Time = 316

smoothSolver:  Solving for Ux, Initial residual = 9.4976844e-09, Final residual = 9.4976844e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.5124146e-09, Final residual = 7.5124146e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00027815502, Final residual = 2.282543e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00013583715, Final residual = 1.3384379e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.6675712e-05, Final residual = 3.3984364e-07, No Iterations 7
GAMG:  Solving for p, Initial residual = 2.1549257e-05, Final residual = 1.9978887e-07, No Iterations 6
time step continuity errors : sum local = 1.4300102e-10, global = 6.9376069e-15, cumulative = -1.2193546e-08
ExecutionTime = 229.57 s  ClockTime = 231 s

Time = 317

smoothSolver:  Solving for Ux, Initial residual = 8.8861921e-09, Final residual = 8.8861921e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.7502066e-09, Final residual = 6.7502066e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00029116827, Final residual = 1.7241273e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.7341183e-05, Final residual = 8.2427519e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.983161e-05, Final residual = 2.9599538e-07, No Iterations 7
GAMG:  Solving for p, Initial residual = 1.5149154e-05, Final residual = 1.0964673e-07, No Iterations 6
time step continuity errors : sum local = 7.9383027e-11, global = -2.1186719e-13, cumulative = -1.2193757e-08
ExecutionTime = 230.29 s  ClockTime = 232 s

Time = 318

smoothSolver:  Solving for Ux, Initial residual = 9.1721866e-09, Final residual = 9.1721866e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.8940123e-09, Final residual = 6.8940123e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00029247647, Final residual = 2.2552737e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.3532858e-05, Final residual = 6.05333e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.6292024e-05, Final residual = 1.9922733e-07, No Iterations 8
GAMG:  Solving for p, Initial residual = 1.2936471e-05, Final residual = 7.5535957e-08, No Iterations 6
time step continuity errors : sum local = 5.5441787e-11, global = 1.1832417e-13, cumulative = -1.2193639e-08
ExecutionTime = 230.97 s  ClockTime = 232 s

Time = 319

smoothSolver:  Solving for Ux, Initial residual = 9.5134788e-09, Final residual = 9.5134788e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.1641134e-09, Final residual = 7.1641134e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.000283198, Final residual = 2.026266e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.7986209e-05, Final residual = 6.1113604e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.2915313e-05, Final residual = 1.7190161e-07, No Iterations 7
GAMG:  Solving for p, Initial residual = 1.1855137e-05, Final residual = 7.2147435e-08, No Iterations 5
time step continuity errors : sum local = 5.2902868e-11, global = -1.4240412e-13, cumulative = -1.2193781e-08
ExecutionTime = 231.59 s  ClockTime = 233 s

Time = 320

smoothSolver:  Solving for Ux, Initial residual = 9.1311585e-09, Final residual = 9.1311585e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.8299801e-09, Final residual = 6.8299801e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00026748689, Final residual = 2.4536185e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.8953567e-05, Final residual = 5.621725e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.3254524e-05, Final residual = 1.7608006e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 1.2049765e-05, Final residual = 7.6930445e-08, No Iterations 4
time step continuity errors : sum local = 5.6479788e-11, global = 3.8448663e-14, cumulative = -1.2193743e-08
ExecutionTime = 232.18 s  ClockTime = 234 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 321

smoothSolver:  Solving for Ux, Initial residual = 9.4678408e-09, Final residual = 9.4678408e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.2331273e-09, Final residual = 7.2331273e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00025040571, Final residual = 1.2331749e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.284671e-05, Final residual = 4.0425233e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.1597645e-05, Final residual = 1.7623781e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1200376e-05, Final residual = 7.4397092e-08, No Iterations 4
time step continuity errors : sum local = 5.4601843e-11, global = 1.3828949e-13, cumulative = -1.2193605e-08
ExecutionTime = 232.78 s  ClockTime = 234 s

Time = 322

smoothSolver:  Solving for Ux, Initial residual = 9.9684052e-09, Final residual = 9.9684052e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.8184198e-09, Final residual = 7.8184198e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00023598289, Final residual = 1.2041939e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.9708039e-05, Final residual = 4.0874218e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.0458522e-05, Final residual = 1.5767213e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0603245e-05, Final residual = 9.2157203e-08, No Iterations 3
time step continuity errors : sum local = 6.7032805e-11, global = 9.3835377e-14, cumulative = -1.2193511e-08
ExecutionTime = 233.41 s  ClockTime = 235 s

Time = 323

smoothSolver:  Solving for Ux, Initial residual = 9.7892208e-09, Final residual = 9.7892208e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.8177275e-09, Final residual = 7.8177275e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00022635039, Final residual = 1.0827278e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.2658662e-05, Final residual = 3.8790161e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.8557899e-05, Final residual = 1.5531718e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.8200575e-06, Final residual = 6.9929306e-08, No Iterations 3
time step continuity errors : sum local = 5.1630157e-11, global = -1.0564455e-13, cumulative = -1.2193617e-08
ExecutionTime = 234 s  ClockTime = 236 s

Time = 324

smoothSolver:  Solving for Ux, Initial residual = 8.6175937e-09, Final residual = 8.6175937e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.9566506e-09, Final residual = 6.9566506e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00022084378, Final residual = 1.9883356e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.1788206e-05, Final residual = 2.7101082e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.7810889e-05, Final residual = 1.5041952e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.147225e-06, Final residual = 6.5926243e-08, No Iterations 4
time step continuity errors : sum local = 4.9050587e-11, global = -1.4800446e-14, cumulative = -1.2193631e-08
ExecutionTime = 234.61 s  ClockTime = 236 s

Time = 325

smoothSolver:  Solving for Ux, Initial residual = 8.6704731e-09, Final residual = 8.6704731e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.111703e-09, Final residual = 7.111703e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00021763514, Final residual = 1.5440031e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.4796783e-05, Final residual = 2.5209296e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.5607184e-05, Final residual = 1.4499287e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.4311576e-06, Final residual = 6.912555e-08, No Iterations 3
time step continuity errors : sum local = 5.1077569e-11, global = -3.9766294e-14, cumulative = -1.2193671e-08
ExecutionTime = 235.21 s  ClockTime = 237 s

Time = 326

smoothSolver:  Solving for Ux, Initial residual = 8.990654e-09, Final residual = 8.990654e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.4632121e-09, Final residual = 7.4632121e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0002150977, Final residual = 1.1734817e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.0104939e-05, Final residual = 3.7519012e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3486865e-05, Final residual = 8.3635945e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 7.8764891e-06, Final residual = 6.749113e-08, No Iterations 7
time step continuity errors : sum local = 4.9556153e-11, global = -1.9838766e-14, cumulative = -1.2193691e-08
ExecutionTime = 235.92 s  ClockTime = 237 s

Time = 327

smoothSolver:  Solving for Ux, Initial residual = 8.7634343e-09, Final residual = 8.7634343e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.3045294e-09, Final residual = 7.3045294e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00021223154, Final residual = 9.9462297e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.7433393e-05, Final residual = 3.265842e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2599308e-05, Final residual = 8.6931886e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.7759305e-06, Final residual = 6.1090835e-08, No Iterations 4
time step continuity errors : sum local = 4.5130675e-11, global = 2.8915259e-13, cumulative = -1.2193402e-08
ExecutionTime = 236.55 s  ClockTime = 238 s

Time = 328

smoothSolver:  Solving for Ux, Initial residual = 9.1422595e-09, Final residual = 9.1422595e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.6412727e-09, Final residual = 7.6412727e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00020905338, Final residual = 9.571695e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.6047823e-05, Final residual = 3.3691957e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2171171e-05, Final residual = 1.1658497e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.4072744e-06, Final residual = 6.3485227e-08, No Iterations 4
time step continuity errors : sum local = 4.7015698e-11, global = -1.9670323e-13, cumulative = -1.2193598e-08
ExecutionTime = 237.15 s  ClockTime = 239 s

Time = 329

smoothSolver:  Solving for Ux, Initial residual = 8.582286e-09, Final residual = 8.582286e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.1295257e-09, Final residual = 7.1295257e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0002061635, Final residual = 9.9875145e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.5073496e-05, Final residual = 2.3315454e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2414078e-05, Final residual = 1.2330095e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.1225881e-06, Final residual = 6.0278844e-08, No Iterations 5
time step continuity errors : sum local = 4.4860668e-11, global = 1.6452717e-13, cumulative = -1.2193434e-08
ExecutionTime = 237.86 s  ClockTime = 239 s

Time = 330

smoothSolver:  Solving for Ux, Initial residual = 8.3728134e-09, Final residual = 8.3728134e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.9435718e-09, Final residual = 6.9435718e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00020379595, Final residual = 1.0243345e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.3924059e-05, Final residual = 3.2721116e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1789785e-05, Final residual = 7.3022436e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.1652497e-06, Final residual = 6.0573907e-08, No Iterations 8
time step continuity errors : sum local = 4.4843465e-11, global = 4.2845254e-14, cumulative = -1.2193391e-08
ExecutionTime = 238.49 s  ClockTime = 240 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 331

smoothSolver:  Solving for Ux, Initial residual = 8.2383944e-09, Final residual = 8.2383944e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.7865878e-09, Final residual = 6.7865878e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00020201317, Final residual = 9.9729875e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.248306e-05, Final residual = 3.069559e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1495818e-05, Final residual = 7.5748447e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.9528071e-06, Final residual = 5.8273393e-08, No Iterations 6
time step continuity errors : sum local = 4.3323083e-11, global = -1.9779174e-13, cumulative = -1.2193589e-08
ExecutionTime = 239.18 s  ClockTime = 241 s

Time = 332

smoothSolver:  Solving for Ux, Initial residual = 9.2224861e-09, Final residual = 9.2224861e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.5915274e-09, Final residual = 7.5915274e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00020076501, Final residual = 9.4095499e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.0989432e-05, Final residual = 2.1800118e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1467219e-05, Final residual = 8.1198916e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.7200805e-06, Final residual = 5.620743e-08, No Iterations 6
time step continuity errors : sum local = 4.1900887e-11, global = 1.9914534e-14, cumulative = -1.2193569e-08
ExecutionTime = 239.95 s  ClockTime = 241 s

Time = 333

smoothSolver:  Solving for Ux, Initial residual = 8.6523455e-09, Final residual = 8.6523455e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.0557816e-09, Final residual = 7.0557816e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00019984525, Final residual = 8.5285536e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.9876512e-05, Final residual = 2.2348107e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1091994e-05, Final residual = 8.548262e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.7092328e-06, Final residual = 5.6315561e-08, No Iterations 8
time step continuity errors : sum local = 4.1774266e-11, global = -5.6035759e-14, cumulative = -1.2193625e-08
ExecutionTime = 240.66 s  ClockTime = 242 s

Time = 334

smoothSolver:  Solving for Ux, Initial residual = 8.5773306e-09, Final residual = 8.5773306e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.9730132e-09, Final residual = 6.9730132e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00019902542, Final residual = 7.5176706e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.8998202e-05, Final residual = 2.1907862e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0770768e-05, Final residual = 9.4253968e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.6211236e-06, Final residual = 5.6014415e-08, No Iterations 10
time step continuity errors : sum local = 4.1808317e-11, global = -3.1438574e-14, cumulative = -1.2193656e-08
ExecutionTime = 241.39 s  ClockTime = 243 s

Time = 335

smoothSolver:  Solving for Ux, Initial residual = 8.2991995e-09, Final residual = 8.2991995e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.7166435e-09, Final residual = 6.7166435e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00019816703, Final residual = 6.6945093e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.831168e-05, Final residual = 1.45616e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0332077e-05, Final residual = 7.9244188e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.5835602e-06, Final residual = 5.5301424e-08, No Iterations 11
time step continuity errors : sum local = 4.125019e-11, global = 2.8018406e-13, cumulative = -1.2193376e-08
ExecutionTime = 242.13 s  ClockTime = 244 s

Time = 336

smoothSolver:  Solving for Ux, Initial residual = 9.8732696e-09, Final residual = 9.8732696e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.0760548e-09, Final residual = 8.0760548e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00019723452, Final residual = 6.1785003e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.7724951e-05, Final residual = 2.5112551e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.9783471e-06, Final residual = 6.4909363e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.9159073e-06, Final residual = 5.8317295e-08, No Iterations 4
time step continuity errors : sum local = 4.3431411e-11, global = 2.5947948e-13, cumulative = -1.2193117e-08
ExecutionTime = 242.69 s  ClockTime = 244 s

Time = 337

smoothSolver:  Solving for Ux, Initial residual = 1.0595219e-08, Final residual = 1.2367697e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 8.7097356e-09, Final residual = 8.7097356e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00022656541, Final residual = 1.2948167e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00018364282, Final residual = 6.7318428e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.7389157e-05, Final residual = 4.5187215e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.313408e-05, Final residual = 1.9345586e-07, No Iterations 4
time step continuity errors : sum local = 1.382596e-10, global = 1.7951446e-13, cumulative = -1.2192937e-08
ExecutionTime = 243.39 s  ClockTime = 245 s

Time = 338

smoothSolver:  Solving for Ux, Initial residual = 9.8230214e-09, Final residual = 9.8230214e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.5661967e-09, Final residual = 8.5661967e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00021917538, Final residual = 1.9247705e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00012317806, Final residual = 7.0518687e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.3628178e-05, Final residual = 1.1730552e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.6789428e-05, Final residual = 1.1134237e-07, No Iterations 3
time step continuity errors : sum local = 8.0405225e-11, global = -1.7509418e-13, cumulative = -1.2193112e-08
ExecutionTime = 244.04 s  ClockTime = 246 s

Time = 339

smoothSolver:  Solving for Ux, Initial residual = 8.0562878e-09, Final residual = 8.0562878e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.355749e-09, Final residual = 7.355749e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00022047296, Final residual = 1.1518895e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.5509256e-05, Final residual = 4.3308135e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.9379844e-05, Final residual = 8.0718808e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0086231e-05, Final residual = 6.9059002e-08, No Iterations 5
time step continuity errors : sum local = 5.0937756e-11, global = -1.0512622e-13, cumulative = -1.2193218e-08
ExecutionTime = 244.67 s  ClockTime = 246 s

Time = 340

smoothSolver:  Solving for Ux, Initial residual = 9.2193947e-09, Final residual = 9.2193947e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.4971038e-09, Final residual = 8.4971038e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0002227937, Final residual = 8.6038477e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.7856215e-05, Final residual = 2.7368765e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3077929e-05, Final residual = 6.9916925e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.2174653e-06, Final residual = 6.6026798e-08, No Iterations 3
time step continuity errors : sum local = 4.8895362e-11, global = 2.5319291e-14, cumulative = -1.2193192e-08
ExecutionTime = 245.24 s  ClockTime = 247 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 341

smoothSolver:  Solving for Ux, Initial residual = 8.9877052e-09, Final residual = 8.9877052e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.2691532e-09, Final residual = 8.2691532e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00022043777, Final residual = 2.1944433e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.6169645e-05, Final residual = 3.1626332e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.9187126e-05, Final residual = 1.7947228e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.778694e-06, Final residual = 8.2993739e-08, No Iterations 3
time step continuity errors : sum local = 6.0536756e-11, global = -1.0759676e-13, cumulative = -1.21933e-08
ExecutionTime = 245.87 s  ClockTime = 247 s

Time = 342

smoothSolver:  Solving for Ux, Initial residual = 9.2308216e-09, Final residual = 9.2308216e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.3437658e-09, Final residual = 8.3437658e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00021287545, Final residual = 1.3608068e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.9460628e-05, Final residual = 5.1910288e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.2085309e-05, Final residual = 9.2915169e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1398802e-05, Final residual = 6.8888727e-08, No Iterations 4
time step continuity errors : sum local = 5.0837614e-11, global = 1.2083472e-13, cumulative = -1.2193179e-08
ExecutionTime = 246.46 s  ClockTime = 248 s

Time = 343

smoothSolver:  Solving for Ux, Initial residual = 7.9577462e-09, Final residual = 7.9577462e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.0548785e-09, Final residual = 7.0548785e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00020426719, Final residual = 1.4620322e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.7504004e-05, Final residual = 5.377585e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.3919814e-05, Final residual = 9.3840496e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2002427e-05, Final residual = 7.6717258e-08, No Iterations 3
time step continuity errors : sum local = 5.6186656e-11, global = 4.8046606e-14, cumulative = -1.2193131e-08
ExecutionTime = 247.03 s  ClockTime = 249 s

Time = 344

smoothSolver:  Solving for Ux, Initial residual = 8.0630954e-09, Final residual = 8.0630954e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.9064113e-09, Final residual = 6.9064113e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00019960066, Final residual = 1.4197207e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.3955616e-05, Final residual = 5.0999335e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.3300272e-05, Final residual = 9.2301159e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1395976e-05, Final residual = 7.4812598e-08, No Iterations 3
time step continuity errors : sum local = 5.4939904e-11, global = -4.9381873e-15, cumulative = -1.2193136e-08
ExecutionTime = 247.63 s  ClockTime = 249 s

Time = 345

smoothSolver:  Solving for Ux, Initial residual = 8.2243861e-09, Final residual = 8.2243861e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.8117405e-09, Final residual = 6.8117405e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00020032763, Final residual = 1.2800401e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.2636938e-05, Final residual = 4.6829967e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.0986493e-05, Final residual = 8.9092962e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0172127e-05, Final residual = 7.2507617e-08, No Iterations 4
time step continuity errors : sum local = 5.3333843e-11, global = 9.0491079e-14, cumulative = -1.2193045e-08
ExecutionTime = 248.24 s  ClockTime = 250 s

Time = 346

smoothSolver:  Solving for Ux, Initial residual = 8.8912658e-09, Final residual = 8.8912658e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.2007566e-09, Final residual = 7.2007566e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00020375825, Final residual = 1.0604541e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.8175205e-05, Final residual = 4.2849958e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.7708671e-05, Final residual = 8.6655084e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.7630467e-06, Final residual = 7.7151925e-08, No Iterations 4
time step continuity errors : sum local = 5.6618459e-11, global = -2.2895454e-13, cumulative = -1.2193274e-08
ExecutionTime = 248.87 s  ClockTime = 250 s

Time = 347

smoothSolver:  Solving for Ux, Initial residual = 8.7101474e-09, Final residual = 8.7101474e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.9001012e-09, Final residual = 6.9001012e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0002065275, Final residual = 1.6170794e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.390897e-05, Final residual = 1.4799893e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.5467153e-05, Final residual = 9.5321089e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.6215074e-06, Final residual = 6.9942573e-08, No Iterations 6
time step continuity errors : sum local = 5.1427461e-11, global = -3.7855929e-13, cumulative = -1.2193653e-08
ExecutionTime = 249.5 s  ClockTime = 251 s

Time = 348

smoothSolver:  Solving for Ux, Initial residual = 1.0437262e-08, Final residual = 1.2251614e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 8.3331434e-09, Final residual = 8.3331434e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00023528761, Final residual = 1.2303061e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00017410209, Final residual = 6.4411092e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.5161202e-05, Final residual = 4.3021054e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.1998376e-05, Final residual = 2.0694689e-07, No Iterations 3
time step continuity errors : sum local = 1.4841673e-10, global = -5.8041116e-15, cumulative = -1.2193659e-08
ExecutionTime = 250.09 s  ClockTime = 252 s

Time = 349

smoothSolver:  Solving for Ux, Initial residual = 8.7250912e-09, Final residual = 8.7250912e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.3833611e-09, Final residual = 7.3833611e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00021779806, Final residual = 1.9773733e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0001256115, Final residual = 7.2530632e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4240236e-05, Final residual = 2.4837912e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.7636919e-05, Final residual = 8.4072082e-08, No Iterations 3
time step continuity errors : sum local = 6.1315466e-11, global = 3.8676655e-16, cumulative = -1.2193658e-08
ExecutionTime = 250.69 s  ClockTime = 252 s

Time = 350

smoothSolver:  Solving for Ux, Initial residual = 7.6585233e-09, Final residual = 7.6585233e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.8339184e-09, Final residual = 6.8339184e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0002084561, Final residual = 1.2766889e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.4423995e-05, Final residual = 4.8351559e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.1396354e-05, Final residual = 1.8364964e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1506699e-05, Final residual = 9.2242138e-08, No Iterations 3
time step continuity errors : sum local = 6.6966941e-11, global = -1.1483656e-13, cumulative = -1.2193773e-08
ExecutionTime = 251.8 s  ClockTime = 254 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.161494e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 351

smoothSolver:  Solving for Ux, Initial residual = 7.6361616e-09, Final residual = 7.6361616e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.9698455e-09, Final residual = 6.9698455e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00020783545, Final residual = 1.0421919e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.5724245e-05, Final residual = 3.5507027e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2529737e-05, Final residual = 6.5905626e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.161952e-06, Final residual = 6.479977e-08, No Iterations 3
time step continuity errors : sum local = 4.804242e-11, global = 1.4576402e-13, cumulative = -1.2193627e-08
ExecutionTime = 252.37 s  ClockTime = 254 s

Time = 352

smoothSolver:  Solving for Ux, Initial residual = 8.9457129e-09, Final residual = 8.9457129e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 8.1390647e-09, Final residual = 8.1390647e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00020767832, Final residual = 1.537562e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.2504805e-05, Final residual = 2.8460217e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.5253545e-05, Final residual = 6.8389297e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.3047982e-06, Final residual = 6.6842427e-08, No Iterations 3
time step continuity errors : sum local = 4.9406753e-11, global = -2.2487097e-13, cumulative = -1.2193852e-08
ExecutionTime = 252.93 s  ClockTime = 255 s

Time = 353

smoothSolver:  Solving for Ux, Initial residual = 7.7430771e-09, Final residual = 7.7430771e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.0040179e-09, Final residual = 7.0040179e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0002037406, Final residual = 1.1574268e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.4988831e-05, Final residual = 4.6318061e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.8613446e-05, Final residual = 7.8632519e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.7484172e-06, Final residual = 6.9531048e-08, No Iterations 3
time step continuity errors : sum local = 5.1241503e-11, global = 5.2767725e-14, cumulative = -1.2193799e-08
ExecutionTime = 253.49 s  ClockTime = 255 s

Time = 354

smoothSolver:  Solving for Ux, Initial residual = 8.3325172e-09, Final residual = 8.3325172e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.3653477e-09, Final residual = 7.3653477e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00019746563, Final residual = 1.3218748e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.5980033e-05, Final residual = 5.2668412e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.1242959e-05, Final residual = 2.0730434e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1208341e-05, Final residual = 9.764269e-08, No Iterations 3
time step continuity errors : sum local = 7.0814999e-11, global = -1.0860642e-13, cumulative = -1.2193908e-08
ExecutionTime = 254.06 s  ClockTime = 256 s

Time = 355

smoothSolver:  Solving for Ux, Initial residual = 7.7248975e-09, Final residual = 7.7248975e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.6768683e-09, Final residual = 6.6768683e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00019264949, Final residual = 1.3226619e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.5940754e-05, Final residual = 4.9369598e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.1443545e-05, Final residual = 1.3508158e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0174311e-05, Final residual = 6.7612776e-08, No Iterations 8
time step continuity errors : sum local = 4.975612e-11, global = 3.9959063e-14, cumulative = -1.2193868e-08
ExecutionTime = 254.69 s  ClockTime = 256 s

Time = 356

smoothSolver:  Solving for Ux, Initial residual = 8.1048885e-09, Final residual = 8.1048885e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.8028864e-09, Final residual = 6.8028864e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00019202342, Final residual = 1.2262026e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.799115e-05, Final residual = 4.7021112e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.9670794e-05, Final residual = 1.4999636e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.3620649e-06, Final residual = 9.1575558e-08, No Iterations 8
time step continuity errors : sum local = 6.6817485e-11, global = 8.9797026e-14, cumulative = -1.2193778e-08
ExecutionTime = 255.3 s  ClockTime = 257 s

Time = 357

smoothSolver:  Solving for Ux, Initial residual = 8.5476117e-09, Final residual = 8.5476117e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.0127608e-09, Final residual = 7.0127608e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00019456845, Final residual = 1.0590232e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.6108662e-05, Final residual = 4.6332475e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.6868435e-05, Final residual = 9.1873893e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.5000889e-06, Final residual = 7.2492761e-08, No Iterations 4
time step continuity errors : sum local = 5.3110741e-11, global = -3.5936125e-13, cumulative = -1.2194138e-08
ExecutionTime = 255.89 s  ClockTime = 258 s

Time = 358

smoothSolver:  Solving for Ux, Initial residual = 9.1490124e-09, Final residual = 9.1490124e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.42634e-09, Final residual = 7.42634e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00019740863, Final residual = 1.6989899e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.2673666e-05, Final residual = 4.0353738e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.5842236e-05, Final residual = 9.5163694e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.602528e-06, Final residual = 7.300805e-08, No Iterations 5
time step continuity errors : sum local = 5.3702665e-11, global = 2.6008061e-13, cumulative = -1.2193878e-08
ExecutionTime = 256.5 s  ClockTime = 258 s

Time = 359

smoothSolver:  Solving for Ux, Initial residual = 8.1669982e-09, Final residual = 8.1669982e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.5035725e-09, Final residual = 6.5035725e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00019852726, Final residual = 1.1701099e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.5881683e-05, Final residual = 1.5911004e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2952233e-05, Final residual = 7.4940631e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 7.4369138e-06, Final residual = 6.5497919e-08, No Iterations 5
time step continuity errors : sum local = 4.8227441e-11, global = 1.0414836e-13, cumulative = -1.2193773e-08
ExecutionTime = 257.14 s  ClockTime = 259 s

Time = 360

smoothSolver:  Solving for Ux, Initial residual = 8.540129e-09, Final residual = 8.540129e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.8120153e-09, Final residual = 6.8120153e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00019743962, Final residual = 8.4147652e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.3519365e-05, Final residual = 2.485967e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 1.2296735e-05, Final residual = 1.0931272e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.9452273e-06, Final residual = 6.217579e-08, No Iterations 5
time step continuity errors : sum local = 4.6186521e-11, global = 6.4798757e-14, cumulative = -1.2193709e-08
ExecutionTime = 257.74 s  ClockTime = 259 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 361

smoothSolver:  Solving for Ux, Initial residual = 8.4886908e-09, Final residual = 8.4886908e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.7621936e-09, Final residual = 6.7621936e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00019466861, Final residual = 9.9860867e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.3106459e-05, Final residual = 1.853885e-07, No Iterations 6
GAMG:  Solving for p, Initial residual = 1.2802927e-05, Final residual = 6.5391872e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 6.6202242e-06, Final residual = 6.137404e-08, No Iterations 6
time step continuity errors : sum local = 4.5555821e-11, global = 1.4233222e-13, cumulative = -1.2193566e-08
ExecutionTime = 258.57 s  ClockTime = 260 s

Time = 362

smoothSolver:  Solving for Ux, Initial residual = 8.6251698e-09, Final residual = 8.6251698e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.8834729e-09, Final residual = 6.8834729e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00019139716, Final residual = 1.1438357e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.306365e-05, Final residual = 2.5270434e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2443564e-05, Final residual = 8.5774794e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.2652967e-06, Final residual = 6.1065495e-08, No Iterations 4
time step continuity errors : sum local = 4.5244606e-11, global = 4.0127501e-14, cumulative = -1.2193526e-08
ExecutionTime = 259.16 s  ClockTime = 261 s

Time = 363

smoothSolver:  Solving for Ux, Initial residual = 7.9670816e-09, Final residual = 7.9670816e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.3689189e-09, Final residual = 6.3689189e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00018853699, Final residual = 1.1693038e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.242347e-05, Final residual = 2.3298901e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2077299e-05, Final residual = 9.7435444e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.0428585e-06, Final residual = 5.8169807e-08, No Iterations 5
time step continuity errors : sum local = 4.3038596e-11, global = 2.3226295e-14, cumulative = -1.2193503e-08
ExecutionTime = 259.73 s  ClockTime = 261 s

Time = 364

smoothSolver:  Solving for Ux, Initial residual = 8.1698714e-09, Final residual = 8.1698714e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.5994747e-09, Final residual = 6.5994747e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00018637665, Final residual = 1.0975757e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.102135e-05, Final residual = 2.0925833e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1391065e-05, Final residual = 6.8090593e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.6271351e-06, Final residual = 5.5419531e-08, No Iterations 9
time step continuity errors : sum local = 4.1413593e-11, global = 5.6425398e-14, cumulative = -1.2193447e-08
ExecutionTime = 260.37 s  ClockTime = 262 s

Time = 365

smoothSolver:  Solving for Ux, Initial residual = 8.1581738e-09, Final residual = 8.1581738e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.6442883e-09, Final residual = 6.6442883e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00018495668, Final residual = 9.6665584e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.940996e-05, Final residual = 2.1283121e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0826086e-05, Final residual = 9.3999375e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.4555159e-06, Final residual = 5.4505778e-08, No Iterations 34
time step continuity errors : sum local = 4.0763706e-11, global = 1.0015984e-13, cumulative = -1.2193346e-08
ExecutionTime = 261.34 s  ClockTime = 263 s

Time = 366

smoothSolver:  Solving for Ux, Initial residual = 7.7901697e-09, Final residual = 7.7901697e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.3697424e-09, Final residual = 6.3697424e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00018410596, Final residual = 8.1427832e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.7936784e-05, Final residual = 2.1845442e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0293356e-05, Final residual = 8.923827e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.176921e-06, Final residual = 5.5659804e-08, No Iterations 100
time step continuity errors : sum local = 4.1258411e-11, global = -8.1814288e-14, cumulative = -1.2193428e-08
ExecutionTime = 263.25 s  ClockTime = 265 s

Time = 367

smoothSolver:  Solving for Ux, Initial residual = 8.5467431e-09, Final residual = 8.5467431e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.0400494e-09, Final residual = 7.0400494e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00018341228, Final residual = 6.6139448e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.6960319e-05, Final residual = 2.6245764e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.4861386e-06, Final residual = 7.6301023e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.6468283e-06, Final residual = 5.5747698e-08, No Iterations 5
time step continuity errors : sum local = 4.146055e-11, global = 8.1954337e-14, cumulative = -1.2193346e-08
ExecutionTime = 263.93 s  ClockTime = 266 s

Time = 368

smoothSolver:  Solving for Ux, Initial residual = 7.9178403e-09, Final residual = 7.9178403e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.5088914e-09, Final residual = 6.5088914e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00018280629, Final residual = 1.8148209e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.6082589e-05, Final residual = 2.1035268e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0124694e-05, Final residual = 6.2799712e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.0197239e-06, Final residual = 5.5542854e-08, No Iterations 100
time step continuity errors : sum local = 4.1530953e-11, global = 2.004911e-13, cumulative = -1.2193146e-08
ExecutionTime = 265.94 s  ClockTime = 268 s

Time = 369

smoothSolver:  Solving for Ux, Initial residual = 8.1041107e-09, Final residual = 8.1041107e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.688742e-09, Final residual = 6.688742e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001821914, Final residual = 1.718899e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5745929e-05, Final residual = 1.8081885e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0002478e-05, Final residual = 8.3103948e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.856216e-06, Final residual = 5.532482e-08, No Iterations 100
time step continuity errors : sum local = 4.1084962e-11, global = 1.2361373e-13, cumulative = -1.2193022e-08
ExecutionTime = 267.83 s  ClockTime = 270 s

Time = 370

smoothSolver:  Solving for Ux, Initial residual = 8.43182e-09, Final residual = 8.43182e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.9851352e-09, Final residual = 6.9851352e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001816212, Final residual = 1.6623124e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.544548e-05, Final residual = 2.4839191e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.8422751e-06, Final residual = 9.0475481e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.0998068e-06, Final residual = 5.5041843e-08, No Iterations 100
time step continuity errors : sum local = 4.121668e-11, global = 1.5457255e-13, cumulative = -1.2192868e-08
ExecutionTime = 269.77 s  ClockTime = 271 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 371

smoothSolver:  Solving for Ux, Initial residual = 8.482329e-09, Final residual = 8.482329e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.0127867e-09, Final residual = 7.0127867e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00018102516, Final residual = 1.6216422e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5055757e-05, Final residual = 1.7396431e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0120708e-05, Final residual = 7.6501724e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.9295849e-06, Final residual = 5.5690479e-08, No Iterations 100
time step continuity errors : sum local = 4.1473302e-11, global = 3.5353365e-13, cumulative = -1.2192514e-08
ExecutionTime = 271.76 s  ClockTime = 273 s

Time = 372

smoothSolver:  Solving for Ux, Initial residual = 9.3175164e-09, Final residual = 9.3175164e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.7083849e-09, Final residual = 7.7083849e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00018040689, Final residual = 1.581474e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.46177e-05, Final residual = 1.8542509e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.9905149e-06, Final residual = 9.2352013e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.9625166e-06, Final residual = 5.4236172e-08, No Iterations 100
time step continuity errors : sum local = 4.0603855e-11, global = -1.1132477e-13, cumulative = -1.2192625e-08
ExecutionTime = 273.85 s  ClockTime = 276 s

Time = 373

smoothSolver:  Solving for Ux, Initial residual = 7.8062554e-09, Final residual = 7.8062554e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.3951299e-09, Final residual = 6.3951299e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017976268, Final residual = 1.5424505e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.421089e-05, Final residual = 1.7728976e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.7203494e-06, Final residual = 6.387741e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.0298308e-06, Final residual = 5.5200461e-08, No Iterations 100
time step continuity errors : sum local = 4.1298459e-11, global = -6.9733688e-14, cumulative = -1.2192695e-08
ExecutionTime = 275.77 s  ClockTime = 278 s

Time = 374

smoothSolver:  Solving for Ux, Initial residual = 9.1240706e-09, Final residual = 9.1240706e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.5065204e-09, Final residual = 7.5065204e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017907284, Final residual = 1.5113841e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3950607e-05, Final residual = 2.053155e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.54817e-06, Final residual = 7.9316569e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.7863828e-06, Final residual = 5.5237694e-08, No Iterations 100
time step continuity errors : sum local = 4.1153077e-11, global = 6.8117814e-14, cumulative = -1.2192627e-08
ExecutionTime = 277.71 s  ClockTime = 279 s

Time = 375

smoothSolver:  Solving for Ux, Initial residual = 8.6651566e-09, Final residual = 8.6651566e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.0971139e-09, Final residual = 7.0971139e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017837858, Final residual = 1.4854742e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3851198e-05, Final residual = 2.087738e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.4164115e-06, Final residual = 8.4595443e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.7422569e-06, Final residual = 5.5310781e-08, No Iterations 100
time step continuity errors : sum local = 4.1297812e-11, global = 1.6781484e-13, cumulative = -1.2192459e-08
ExecutionTime = 279.61 s  ClockTime = 281 s

Time = 376

smoothSolver:  Solving for Ux, Initial residual = 7.6708086e-09, Final residual = 7.6708086e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.2355314e-09, Final residual = 6.2355314e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017772308, Final residual = 1.4622985e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3806491e-05, Final residual = 2.1228843e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.3664405e-06, Final residual = 8.0628358e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.7312681e-06, Final residual = 5.5654504e-08, No Iterations 100
time step continuity errors : sum local = 4.1377439e-11, global = 1.2736816e-13, cumulative = -1.2192332e-08
ExecutionTime = 281.61 s  ClockTime = 283 s

Time = 377

smoothSolver:  Solving for Ux, Initial residual = 7.4763018e-09, Final residual = 7.4763018e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.1089345e-09, Final residual = 6.1089345e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017706625, Final residual = 1.4473194e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3781806e-05, Final residual = 2.1375594e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.3448711e-06, Final residual = 7.0862333e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.6429236e-06, Final residual = 5.5400369e-08, No Iterations 100
time step continuity errors : sum local = 4.1090585e-11, global = -2.7927228e-14, cumulative = -1.219236e-08
ExecutionTime = 283.57 s  ClockTime = 285 s

Time = 378

smoothSolver:  Solving for Ux, Initial residual = 7.6630589e-09, Final residual = 7.6630589e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.2562537e-09, Final residual = 6.2562537e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017646167, Final residual = 1.4460617e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3844392e-05, Final residual = 2.1669264e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.2756615e-06, Final residual = 6.4090668e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.6480629e-06, Final residual = 5.542287e-08, No Iterations 100
time step continuity errors : sum local = 4.1409753e-11, global = -8.2005007e-14, cumulative = -1.2192442e-08
ExecutionTime = 285.44 s  ClockTime = 287 s

Time = 379

smoothSolver:  Solving for Ux, Initial residual = 8.0842187e-09, Final residual = 8.0842187e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.6176207e-09, Final residual = 6.6176207e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001761526, Final residual = 1.4549377e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3947374e-05, Final residual = 2.1797614e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.4233189e-06, Final residual = 6.2909084e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 4.9279457e-06, Final residual = 5.5417368e-08, No Iterations 100
time step continuity errors : sum local = 4.0977507e-11, global = 3.3980325e-15, cumulative = -1.2192438e-08
ExecutionTime = 287.42 s  ClockTime = 289 s

Time = 380

smoothSolver:  Solving for Ux, Initial residual = 7.8239194e-09, Final residual = 7.8239194e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.4006917e-09, Final residual = 6.4006917e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017594298, Final residual = 1.4723162e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3934048e-05, Final residual = 1.8539215e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.4604404e-06, Final residual = 9.3900269e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.4864921e-06, Final residual = 5.5606979e-08, No Iterations 100
time step continuity errors : sum local = 4.1373251e-11, global = -9.0091918e-14, cumulative = -1.2192528e-08
ExecutionTime = 289.88 s  ClockTime = 292 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 381

smoothSolver:  Solving for Ux, Initial residual = 7.9583289e-09, Final residual = 7.9583289e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.5187347e-09, Final residual = 6.5187347e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001758297, Final residual = 1.4995793e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3940374e-05, Final residual = 1.7272687e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.5700613e-06, Final residual = 7.318142e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.5733132e-06, Final residual = 5.5517059e-08, No Iterations 100
time step continuity errors : sum local = 4.137839e-11, global = -2.5628001e-13, cumulative = -1.2192785e-08
ExecutionTime = 291.85 s  ClockTime = 294 s

Time = 382

smoothSolver:  Solving for Ux, Initial residual = 8.7342347e-09, Final residual = 8.7342347e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.1915245e-09, Final residual = 7.1915245e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017579415, Final residual = 1.5541902e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3973004e-05, Final residual = 1.9509169e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.5760375e-06, Final residual = 8.7245604e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.8105188e-06, Final residual = 5.531166e-08, No Iterations 100
time step continuity errors : sum local = 4.1160641e-11, global = -1.2469615e-13, cumulative = -1.2192909e-08
ExecutionTime = 293.73 s  ClockTime = 295 s

Time = 383

smoothSolver:  Solving for Ux, Initial residual = 8.3794332e-09, Final residual = 8.3794332e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.8837932e-09, Final residual = 6.8837932e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017565989, Final residual = 1.5828382e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.4066047e-05, Final residual = 2.0144716e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.5337964e-06, Final residual = 7.9481007e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.9185125e-06, Final residual = 5.5096276e-08, No Iterations 100
time step continuity errors : sum local = 4.1031243e-11, global = -6.8283892e-15, cumulative = -1.2192916e-08
ExecutionTime = 295.65 s  ClockTime = 297 s

Time = 384

smoothSolver:  Solving for Ux, Initial residual = 7.387114e-09, Final residual = 7.387114e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.0469545e-09, Final residual = 6.0469545e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017540874, Final residual = 1.5959193e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.4036966e-05, Final residual = 1.8060524e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.3941194e-06, Final residual = 5.9195915e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 5.2320425e-06, Final residual = 5.554499e-08, No Iterations 100
time step continuity errors : sum local = 4.1316305e-11, global = 1.1379431e-13, cumulative = -1.2192802e-08
ExecutionTime = 297.55 s  ClockTime = 299 s

Time = 385

smoothSolver:  Solving for Ux, Initial residual = 8.7257389e-09, Final residual = 8.7257389e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.195229e-09, Final residual = 7.195229e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001750385, Final residual = 1.6063681e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3866323e-05, Final residual = 2.0130211e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.3483808e-06, Final residual = 9.2597652e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.9633143e-06, Final residual = 5.4316159e-08, No Iterations 100
time step continuity errors : sum local = 4.1023472e-11, global = -2.7671054e-13, cumulative = -1.2193079e-08
ExecutionTime = 299.35 s  ClockTime = 301 s

Time = 386

smoothSolver:  Solving for Ux, Initial residual = 7.3392813e-09, Final residual = 7.3392813e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.9942925e-09, Final residual = 5.9942925e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017452585, Final residual = 1.6104719e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3563526e-05, Final residual = 1.9922677e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.2399145e-06, Final residual = 8.3063407e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.869249e-06, Final residual = 5.5409488e-08, No Iterations 100
time step continuity errors : sum local = 4.1304802e-11, global = 6.882093e-14, cumulative = -1.219301e-08
ExecutionTime = 301.19 s  ClockTime = 303 s

Time = 387

smoothSolver:  Solving for Ux, Initial residual = 8.0931235e-09, Final residual = 8.0931235e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.6452972e-09, Final residual = 6.6452972e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001740004, Final residual = 1.6080615e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.328635e-05, Final residual = 1.9071195e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.1076976e-06, Final residual = 8.0395897e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.8771464e-06, Final residual = 5.4917165e-08, No Iterations 100
time step continuity errors : sum local = 4.0969793e-11, global = -6.5964212e-14, cumulative = -1.2193076e-08
ExecutionTime = 303.03 s  ClockTime = 305 s

Time = 388

smoothSolver:  Solving for Ux, Initial residual = 7.6988578e-09, Final residual = 7.6988578e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.3018709e-09, Final residual = 6.3018709e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017356173, Final residual = 1.5973795e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3168001e-05, Final residual = 1.8715595e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.0268831e-06, Final residual = 8.9020104e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.6869137e-06, Final residual = 5.5115401e-08, No Iterations 100
time step continuity errors : sum local = 4.110471e-11, global = -4.848097e-14, cumulative = -1.2193125e-08
ExecutionTime = 304.87 s  ClockTime = 307 s

Time = 389

smoothSolver:  Solving for Ux, Initial residual = 7.3820074e-09, Final residual = 7.3820074e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.0257368e-09, Final residual = 6.0257368e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017304783, Final residual = 1.5728957e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3099132e-05, Final residual = 1.8818294e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.9260956e-06, Final residual = 7.7700608e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.4438492e-06, Final residual = 5.5224712e-08, No Iterations 100
time step continuity errors : sum local = 4.1251129e-11, global = 7.0984478e-14, cumulative = -1.2193054e-08
ExecutionTime = 306.68 s  ClockTime = 308 s

Time = 390

smoothSolver:  Solving for Ux, Initial residual = 7.8233679e-09, Final residual = 7.8233679e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.4090926e-09, Final residual = 6.4090926e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017249225, Final residual = 1.5414043e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3231666e-05, Final residual = 2.0015952e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.0629352e-06, Final residual = 6.2344774e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.7265985e-06, Final residual = 5.5763491e-08, No Iterations 100
time step continuity errors : sum local = 4.15085e-11, global = -2.4973057e-13, cumulative = -1.2193303e-08
ExecutionTime = 308.5 s  ClockTime = 310 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.161494e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 391

smoothSolver:  Solving for Ux, Initial residual = 7.8527092e-09, Final residual = 7.8527092e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.4604395e-09, Final residual = 6.4604395e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017205492, Final residual = 1.526013e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3284039e-05, Final residual = 2.1499338e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.1244232e-06, Final residual = 8.9747117e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.6554941e-06, Final residual = 5.5037746e-08, No Iterations 100
time step continuity errors : sum local = 4.123296e-11, global = -2.5697383e-13, cumulative = -1.219356e-08
ExecutionTime = 310.38 s  ClockTime = 312 s

Time = 392

smoothSolver:  Solving for Ux, Initial residual = 8.875486e-09, Final residual = 8.875486e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.344608e-09, Final residual = 7.344608e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001716477, Final residual = 1.4640651e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3309724e-05, Final residual = 2.1390733e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.1061013e-06, Final residual = 7.8248033e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.5196726e-06, Final residual = 5.5152162e-08, No Iterations 100
time step continuity errors : sum local = 4.122625e-11, global = -9.2209419e-14, cumulative = -1.2193653e-08
ExecutionTime = 312.34 s  ClockTime = 314 s

Time = 393

smoothSolver:  Solving for Ux, Initial residual = 8.3235615e-09, Final residual = 8.3235615e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.8605189e-09, Final residual = 6.8605189e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017140891, Final residual = 1.4098971e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3198675e-05, Final residual = 1.8728256e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.9869023e-06, Final residual = 7.9018562e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.53099e-06, Final residual = 5.545663e-08, No Iterations 100
time step continuity errors : sum local = 4.1201349e-11, global = 7.4812944e-14, cumulative = -1.2193578e-08
ExecutionTime = 314.36 s  ClockTime = 316 s

Time = 394

smoothSolver:  Solving for Ux, Initial residual = 7.5222423e-09, Final residual = 7.5222423e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.1526134e-09, Final residual = 6.1526134e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017121726, Final residual = 1.3858612e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3175147e-05, Final residual = 1.6814635e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.0584112e-06, Final residual = 8.7132614e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.4437917e-06, Final residual = 5.5480939e-08, No Iterations 100
time step continuity errors : sum local = 4.1201417e-11, global = 4.1473373e-14, cumulative = -1.2193536e-08
ExecutionTime = 316.18 s  ClockTime = 318 s

Time = 395

smoothSolver:  Solving for Ux, Initial residual = 8.1779502e-09, Final residual = 8.1779502e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.7245689e-09, Final residual = 6.7245689e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017104018, Final residual = 1.388171e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3150281e-05, Final residual = 2.2502987e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.8246374e-06, Final residual = 7.0911413e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.8238653e-06, Final residual = 5.4667723e-08, No Iterations 100
time step continuity errors : sum local = 4.065335e-11, global = -7.1694022e-14, cumulative = -1.2193608e-08
ExecutionTime = 318.09 s  ClockTime = 320 s

Time = 396

smoothSolver:  Solving for Ux, Initial residual = 7.9484058e-09, Final residual = 7.9484058e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.5192901e-09, Final residual = 6.5192901e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017075536, Final residual = 1.4034559e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3014705e-05, Final residual = 1.6379083e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.0268595e-06, Final residual = 8.9597202e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.5945828e-06, Final residual = 5.5091607e-08, No Iterations 100
time step continuity errors : sum local = 4.0908756e-11, global = -1.0324288e-13, cumulative = -1.2193711e-08
ExecutionTime = 320 s  ClockTime = 322 s

Time = 397

smoothSolver:  Solving for Ux, Initial residual = 7.3128495e-09, Final residual = 7.3128495e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.9666788e-09, Final residual = 5.9666788e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00017034024, Final residual = 1.4178144e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2802951e-05, Final residual = 1.6867674e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.9119633e-06, Final residual = 8.4489525e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.7122433e-06, Final residual = 5.5211942e-08, No Iterations 100
time step continuity errors : sum local = 4.101372e-11, global = 8.0603494e-14, cumulative = -1.2193631e-08
ExecutionTime = 321.84 s  ClockTime = 324 s

Time = 398

smoothSolver:  Solving for Ux, Initial residual = 7.8597198e-09, Final residual = 7.8597198e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.4491679e-09, Final residual = 6.4491679e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016981495, Final residual = 1.4200326e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2581541e-05, Final residual = 1.7314951e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.8056382e-06, Final residual = 7.6677307e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.5420831e-06, Final residual = 5.5442412e-08, No Iterations 100
time step continuity errors : sum local = 4.1361256e-11, global = 2.3264564e-13, cumulative = -1.2193398e-08
ExecutionTime = 323.73 s  ClockTime = 325 s

Time = 399

smoothSolver:  Solving for Ux, Initial residual = 8.8005037e-09, Final residual = 8.8005037e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.2656543e-09, Final residual = 7.2656543e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016919719, Final residual = 1.4047238e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2411442e-05, Final residual = 1.8460321e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.7720237e-06, Final residual = 7.9394643e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.4938871e-06, Final residual = 5.4849825e-08, No Iterations 100
time step continuity errors : sum local = 4.0521908e-11, global = -1.6004291e-13, cumulative = -1.2193558e-08
ExecutionTime = 325.56 s  ClockTime = 327 s

Time = 400

smoothSolver:  Solving for Ux, Initial residual = 7.1543821e-09, Final residual = 7.1543821e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.8587854e-09, Final residual = 5.8587854e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016855433, Final residual = 1.3759574e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2357012e-05, Final residual = 1.4269783e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.764138e-06, Final residual = 8.0018899e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.5503334e-06, Final residual = 5.5447804e-08, No Iterations 100
time step continuity errors : sum local = 4.1267427e-11, global = 1.88928e-15, cumulative = -1.2193556e-08
ExecutionTime = 327.93 s  ClockTime = 330 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 401

smoothSolver:  Solving for Ux, Initial residual = 7.4544218e-09, Final residual = 7.4544218e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.1108794e-09, Final residual = 6.1108794e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001679544, Final residual = 1.3473634e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.234326e-05, Final residual = 2.0233329e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.8446221e-06, Final residual = 5.9577358e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.6232103e-06, Final residual = 5.5645767e-08, No Iterations 100
time step continuity errors : sum local = 4.1479976e-11, global = 5.1937403e-14, cumulative = -1.2193504e-08
ExecutionTime = 330.17 s  ClockTime = 332 s

Time = 402

smoothSolver:  Solving for Ux, Initial residual = 7.3712545e-09, Final residual = 7.3712545e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.0389432e-09, Final residual = 6.0389432e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016737152, Final residual = 1.3316919e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2350975e-05, Final residual = 2.044166e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.8639667e-06, Final residual = 8.2401932e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.4806624e-06, Final residual = 5.5497466e-08, No Iterations 100
time step continuity errors : sum local = 4.115361e-11, global = 7.9939743e-14, cumulative = -1.2193424e-08
ExecutionTime = 332.09 s  ClockTime = 334 s

Time = 403

smoothSolver:  Solving for Ux, Initial residual = 7.0473438e-09, Final residual = 7.0473438e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.7646242e-09, Final residual = 5.7646242e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016684055, Final residual = 1.3315621e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2447452e-05, Final residual = 1.5471848e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.7630332e-06, Final residual = 6.7875775e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.5622591e-06, Final residual = 5.5079539e-08, No Iterations 100
time step continuity errors : sum local = 4.1238281e-11, global = 1.3400807e-13, cumulative = -1.219329e-08
ExecutionTime = 334.07 s  ClockTime = 336 s

Time = 404

smoothSolver:  Solving for Ux, Initial residual = 7.6952287e-09, Final residual = 7.6952287e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.3104361e-09, Final residual = 6.3104361e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016659287, Final residual = 1.3425674e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2603319e-05, Final residual = 2.1231324e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.9285799e-06, Final residual = 8.1863115e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.52096e-06, Final residual = 5.4834919e-08, No Iterations 100
time step continuity errors : sum local = 4.1111355e-11, global = 5.3979223e-14, cumulative = -1.2193236e-08
ExecutionTime = 335.93 s  ClockTime = 338 s

Time = 405

smoothSolver:  Solving for Ux, Initial residual = 7.4904557e-09, Final residual = 7.4904557e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.1346441e-09, Final residual = 6.1346441e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016643365, Final residual = 1.364512e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2658826e-05, Final residual = 1.9129447e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.010546e-06, Final residual = 8.9732963e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.3885599e-06, Final residual = 5.5115297e-08, No Iterations 100
time step continuity errors : sum local = 4.0966723e-11, global = 4.1028986e-14, cumulative = -1.2193195e-08
ExecutionTime = 337.85 s  ClockTime = 340 s

Time = 406

smoothSolver:  Solving for Ux, Initial residual = 7.189573e-09, Final residual = 7.189573e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.8741001e-09, Final residual = 5.8741001e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016634848, Final residual = 1.393121e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.266769e-05, Final residual = 1.7010407e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.1725781e-06, Final residual = 8.4610968e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.4160527e-06, Final residual = 5.4875174e-08, No Iterations 100
time step continuity errors : sum local = 4.0863458e-11, global = -8.3738868e-14, cumulative = -1.2193279e-08
ExecutionTime = 339.69 s  ClockTime = 342 s

Time = 407

smoothSolver:  Solving for Ux, Initial residual = 7.7294879e-09, Final residual = 7.7294879e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.3363241e-09, Final residual = 6.3363241e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016635349, Final residual = 1.4449199e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2676491e-05, Final residual = 1.9097015e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.1882555e-06, Final residual = 7.5042263e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.6772855e-06, Final residual = 5.505543e-08, No Iterations 100
time step continuity errors : sum local = 4.1011081e-11, global = 1.0039514e-13, cumulative = -1.2193179e-08
ExecutionTime = 341.67 s  ClockTime = 344 s

Time = 408

smoothSolver:  Solving for Ux, Initial residual = 7.2181451e-09, Final residual = 7.2181451e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.8949422e-09, Final residual = 5.8949422e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016624788, Final residual = 1.4830851e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2857237e-05, Final residual = 1.9279107e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.2180099e-06, Final residual = 7.0315695e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.7927521e-06, Final residual = 5.5131062e-08, No Iterations 100
time step continuity errors : sum local = 4.1107092e-11, global = 2.9003188e-15, cumulative = -1.2193176e-08
ExecutionTime = 344.14 s  ClockTime = 346 s

Time = 409

smoothSolver:  Solving for Ux, Initial residual = 7.2968859e-09, Final residual = 7.2968859e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.9534355e-09, Final residual = 5.9534355e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016600874, Final residual = 1.4983803e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2895698e-05, Final residual = 2.03061e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.1029988e-06, Final residual = 7.2838548e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.8828684e-06, Final residual = 5.5066263e-08, No Iterations 100
time step continuity errors : sum local = 4.1228668e-11, global = -8.5255589e-15, cumulative = -1.2193184e-08
ExecutionTime = 346.41 s  ClockTime = 348 s

Time = 410

smoothSolver:  Solving for Ux, Initial residual = 7.4374166e-09, Final residual = 7.4374166e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.0896799e-09, Final residual = 6.0896799e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016567348, Final residual = 1.5099571e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2803169e-05, Final residual = 2.0297463e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.0293578e-06, Final residual = 6.4610779e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.9515184e-06, Final residual = 5.5326119e-08, No Iterations 100
time step continuity errors : sum local = 4.0957414e-11, global = -1.1649281e-13, cumulative = -1.2193301e-08
ExecutionTime = 348.45 s  ClockTime = 350 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.161494e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 411

smoothSolver:  Solving for Ux, Initial residual = 7.8649177e-09, Final residual = 7.8649177e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.4496201e-09, Final residual = 6.4496201e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016519254, Final residual = 1.5154866e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2527286e-05, Final residual = 1.9698163e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.9011064e-06, Final residual = 7.2367207e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.7671546e-06, Final residual = 5.5592821e-08, No Iterations 100
time step continuity errors : sum local = 4.1358243e-11, global = 9.1648579e-14, cumulative = -1.2193209e-08
ExecutionTime = 350.34 s  ClockTime = 352 s

Time = 412

smoothSolver:  Solving for Ux, Initial residual = 7.036258e-09, Final residual = 7.036258e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.7537951e-09, Final residual = 5.7537951e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016464407, Final residual = 1.5174813e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2208151e-05, Final residual = 1.9182363e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.7827088e-06, Final residual = 7.602272e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.7502009e-06, Final residual = 5.5128869e-08, No Iterations 100
time step continuity errors : sum local = 4.1102721e-11, global = 1.0488285e-13, cumulative = -1.2193104e-08
ExecutionTime = 352.15 s  ClockTime = 354 s

Time = 413

smoothSolver:  Solving for Ux, Initial residual = 7.468958e-09, Final residual = 7.468958e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.1389363e-09, Final residual = 6.1389363e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016424181, Final residual = 1.514599e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2103832e-05, Final residual = 1.8669297e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.6993868e-06, Final residual = 7.9333086e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.6139169e-06, Final residual = 5.5453572e-08, No Iterations 100
time step continuity errors : sum local = 4.1273634e-11, global = -8.33793e-14, cumulative = -1.2193188e-08
ExecutionTime = 353.95 s  ClockTime = 356 s

Time = 414

smoothSolver:  Solving for Ux, Initial residual = 6.9718029e-09, Final residual = 6.9718029e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6949722e-09, Final residual = 5.6949722e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016375425, Final residual = 1.5022359e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2057798e-05, Final residual = 1.8408346e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.5393491e-06, Final residual = 6.6836757e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.4071659e-06, Final residual = 5.5308646e-08, No Iterations 100
time step continuity errors : sum local = 4.1319671e-11, global = -1.1182413e-13, cumulative = -1.2193299e-08
ExecutionTime = 355.74 s  ClockTime = 358 s

Time = 415

smoothSolver:  Solving for Ux, Initial residual = 7.4411098e-09, Final residual = 7.4411098e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.1176169e-09, Final residual = 6.1176169e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016320374, Final residual = 1.475047e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.219336e-05, Final residual = 2.0137287e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.7313532e-06, Final residual = 7.9992161e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.4878712e-06, Final residual = 5.5475829e-08, No Iterations 100
time step continuity errors : sum local = 4.1243651e-11, global = 1.590915e-13, cumulative = -1.219314e-08
ExecutionTime = 357.55 s  ClockTime = 360 s

Time = 416

smoothSolver:  Solving for Ux, Initial residual = 7.2624276e-09, Final residual = 7.2624276e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.9503884e-09, Final residual = 5.9503884e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016277528, Final residual = 1.4659083e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2246402e-05, Final residual = 2.1459927e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.8811487e-06, Final residual = 6.3436567e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.7017773e-06, Final residual = 5.4881443e-08, No Iterations 100
time step continuity errors : sum local = 4.1105093e-11, global = 6.6901185e-14, cumulative = -1.2193073e-08
ExecutionTime = 359.4 s  ClockTime = 361 s

Time = 417

smoothSolver:  Solving for Ux, Initial residual = 7.5263955e-09, Final residual = 7.5263955e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.1761652e-09, Final residual = 6.1761652e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016239903, Final residual = 1.4078104e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2271004e-05, Final residual = 2.1520671e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.8567021e-06, Final residual = 6.3182679e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.5836166e-06, Final residual = 5.5124581e-08, No Iterations 100
time step continuity errors : sum local = 4.111788e-11, global = 6.1306847e-14, cumulative = -1.2193012e-08
ExecutionTime = 361.2 s  ClockTime = 363 s

Time = 418

smoothSolver:  Solving for Ux, Initial residual = 7.6356608e-09, Final residual = 7.6356608e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.2745939e-09, Final residual = 6.2745939e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016218736, Final residual = 1.3488737e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2179594e-05, Final residual = 1.9446701e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.6950405e-06, Final residual = 8.4141196e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.2900994e-06, Final residual = 5.5110591e-08, No Iterations 100
time step continuity errors : sum local = 4.1090233e-11, global = 2.3888807e-13, cumulative = -1.2192773e-08
ExecutionTime = 363.03 s  ClockTime = 365 s

Time = 419

smoothSolver:  Solving for Ux, Initial residual = 8.4346426e-09, Final residual = 8.4346426e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.9661715e-09, Final residual = 6.9661715e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016204833, Final residual = 1.3213513e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2188599e-05, Final residual = 2.2150999e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.473933e-06, Final residual = 6.0607807e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.7724507e-06, Final residual = 5.5287521e-08, No Iterations 100
time step continuity errors : sum local = 4.1108408e-11, global = -1.6159048e-13, cumulative = -1.2192935e-08
ExecutionTime = 364.88 s  ClockTime = 367 s

Time = 420

smoothSolver:  Solving for Ux, Initial residual = 7.1994021e-09, Final residual = 7.1994021e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.9016556e-09, Final residual = 5.9016556e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016193427, Final residual = 1.3246077e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2137214e-05, Final residual = 1.218262e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.7331301e-06, Final residual = 6.7442924e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.4499866e-06, Final residual = 5.4960168e-08, No Iterations 100
time step continuity errors : sum local = 4.1354263e-11, global = 1.6417498e-13, cumulative = -1.2192771e-08
ExecutionTime = 366.7 s  ClockTime = 369 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 421

smoothSolver:  Solving for Ux, Initial residual = 6.9075099e-09, Final residual = 6.9075099e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6552876e-09, Final residual = 5.6552876e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016169964, Final residual = 1.3391635e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1965227e-05, Final residual = 1.2094764e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.5657984e-06, Final residual = 7.5812195e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.4676582e-06, Final residual = 5.5160558e-08, No Iterations 100
time step continuity errors : sum local = 4.1261678e-11, global = 5.2164939e-14, cumulative = -1.2192719e-08
ExecutionTime = 368.49 s  ClockTime = 370 s

Time = 422

smoothSolver:  Solving for Ux, Initial residual = 7.1922199e-09, Final residual = 7.1922199e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.8771359e-09, Final residual = 5.8771359e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016132875, Final residual = 1.3564562e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1745499e-05, Final residual = 1.6745294e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.547659e-06, Final residual = 7.7179669e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.4081323e-06, Final residual = 5.5120544e-08, No Iterations 100
time step continuity errors : sum local = 4.1192068e-11, global = 3.7817985e-15, cumulative = -1.2192715e-08
ExecutionTime = 370.29 s  ClockTime = 372 s

Time = 423

smoothSolver:  Solving for Ux, Initial residual = 7.4420509e-09, Final residual = 7.4420509e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.0919141e-09, Final residual = 6.0919141e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016084298, Final residual = 1.3644776e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1513432e-05, Final residual = 1.7074133e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.4363252e-06, Final residual = 7.0917986e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.3859407e-06, Final residual = 5.643612e-08, No Iterations 100
time step continuity errors : sum local = 4.2016734e-11, global = 8.0724345e-14, cumulative = -1.2192634e-08
ExecutionTime = 372.1 s  ClockTime = 374 s

Time = 424

smoothSolver:  Solving for Ux, Initial residual = 7.0332044e-09, Final residual = 7.0332044e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.7405856e-09, Final residual = 5.7405856e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00016023997, Final residual = 1.3552178e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1296997e-05, Final residual = 1.7879455e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.364109e-06, Final residual = 8.0343814e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.3109824e-06, Final residual = 5.5185331e-08, No Iterations 100
time step continuity errors : sum local = 4.1185645e-11, global = -6.1176146e-14, cumulative = -1.2192695e-08
ExecutionTime = 373.88 s  ClockTime = 376 s

Time = 425

smoothSolver:  Solving for Ux, Initial residual = 7.4818652e-09, Final residual = 7.4818652e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.1365076e-09, Final residual = 6.1365076e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015961351, Final residual = 1.3265803e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1204889e-05, Final residual = 1.889475e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.3578529e-06, Final residual = 8.2335174e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.2664898e-06, Final residual = 5.5247203e-08, No Iterations 100
time step continuity errors : sum local = 4.1002298e-11, global = 4.063456e-14, cumulative = -1.2192655e-08
ExecutionTime = 375.69 s  ClockTime = 378 s

Time = 426

smoothSolver:  Solving for Ux, Initial residual = 7.0465206e-09, Final residual = 7.0465206e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.7645536e-09, Final residual = 5.7645536e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015905692, Final residual = 1.2964706e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1212789e-05, Final residual = 1.974812e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.409227e-06, Final residual = 5.9413849e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.3967702e-06, Final residual = 5.5585024e-08, No Iterations 100
time step continuity errors : sum local = 4.1373871e-11, global = -2.2141043e-13, cumulative = -1.2192876e-08
ExecutionTime = 377.58 s  ClockTime = 380 s

Time = 427

smoothSolver:  Solving for Ux, Initial residual = 7.9822046e-09, Final residual = 7.9822046e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.5797548e-09, Final residual = 6.5797548e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015852269, Final residual = 1.2766847e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1238145e-05, Final residual = 1.8303271e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.3086522e-06, Final residual = 8.1036641e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.3279318e-06, Final residual = 5.5364406e-08, No Iterations 100
time step continuity errors : sum local = 4.1340634e-11, global = 1.0791337e-13, cumulative = -1.2192768e-08
ExecutionTime = 379.38 s  ClockTime = 381 s

Time = 428

smoothSolver:  Solving for Ux, Initial residual = 6.8812288e-09, Final residual = 6.8812288e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6350564e-09, Final residual = 5.6350564e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015805731, Final residual = 1.2759896e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1380782e-05, Final residual = 1.8746426e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.4300245e-06, Final residual = 7.626922e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.2951721e-06, Final residual = 5.4975211e-08, No Iterations 100
time step continuity errors : sum local = 4.1113807e-11, global = -7.9157847e-14, cumulative = -1.2192847e-08
ExecutionTime = 381.19 s  ClockTime = 383 s

Time = 429

smoothSolver:  Solving for Ux, Initial residual = 6.7980782e-09, Final residual = 6.7980782e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.5602739e-09, Final residual = 5.5602739e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015781476, Final residual = 1.2866366e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1518674e-05, Final residual = 2.1185921e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.4948137e-06, Final residual = 6.2803604e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.3665181e-06, Final residual = 5.4956604e-08, No Iterations 100
time step continuity errors : sum local = 4.0902787e-11, global = -1.5741445e-13, cumulative = -1.2193005e-08
ExecutionTime = 383.13 s  ClockTime = 385 s

Time = 430

smoothSolver:  Solving for Ux, Initial residual = 7.2466641e-09, Final residual = 7.2466641e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.9463519e-09, Final residual = 5.9463519e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015772481, Final residual = 1.3071239e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1651234e-05, Final residual = 1.9747637e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.4503623e-06, Final residual = 6.0735418e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.5114414e-06, Final residual = 5.5379594e-08, No Iterations 100
time step continuity errors : sum local = 4.1454372e-11, global = 2.1769659e-13, cumulative = -1.2192787e-08
ExecutionTime = 384.99 s  ClockTime = 387 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 431

smoothSolver:  Solving for Ux, Initial residual = 7.789189e-09, Final residual = 7.789189e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.4041968e-09, Final residual = 6.4041968e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015766624, Final residual = 1.3330857e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1657225e-05, Final residual = 1.375745e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.6659504e-06, Final residual = 6.4000696e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.2656674e-06, Final residual = 5.5559385e-08, No Iterations 100
time step continuity errors : sum local = 4.1480174e-11, global = 1.7156235e-14, cumulative = -1.219277e-08
ExecutionTime = 386.94 s  ClockTime = 389 s

Time = 432

smoothSolver:  Solving for Ux, Initial residual = 7.5273743e-09, Final residual = 7.5273743e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.1838523e-09, Final residual = 6.1838523e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001577287, Final residual = 1.3762852e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.165528e-05, Final residual = 1.4496035e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.662804e-06, Final residual = 5.7685259e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.7190691e-06, Final residual = 5.5139144e-08, No Iterations 100
time step continuity errors : sum local = 4.1048086e-11, global = -5.1363342e-14, cumulative = -1.2192821e-08
ExecutionTime = 388.81 s  ClockTime = 391 s

Time = 433

smoothSolver:  Solving for Ux, Initial residual = 7.1169132e-09, Final residual = 7.1169132e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.8169841e-09, Final residual = 5.8169841e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015772972, Final residual = 1.42515e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1843659e-05, Final residual = 1.9576732e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.8392127e-06, Final residual = 7.040311e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.6528676e-06, Final residual = 5.511793e-08, No Iterations 100
time step continuity errors : sum local = 4.1036831e-11, global = 1.7024476e-13, cumulative = -1.2192651e-08
ExecutionTime = 390.68 s  ClockTime = 393 s

Time = 434

smoothSolver:  Solving for Ux, Initial residual = 7.8244408e-09, Final residual = 7.8244408e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.4402464e-09, Final residual = 6.4402464e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015755661, Final residual = 1.4419893e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1891128e-05, Final residual = 1.9976428e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.7568043e-06, Final residual = 7.3477927e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.6758423e-06, Final residual = 5.5410947e-08, No Iterations 100
time step continuity errors : sum local = 4.1441318e-11, global = 2.2081332e-13, cumulative = -1.219243e-08
ExecutionTime = 392.52 s  ClockTime = 394 s

Time = 435

smoothSolver:  Solving for Ux, Initial residual = 8.2305566e-09, Final residual = 8.2305566e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.7896705e-09, Final residual = 6.7896705e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015727887, Final residual = 1.4551819e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.18002e-05, Final residual = 1.9918067e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.6478589e-06, Final residual = 5.955483e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.8404773e-06, Final residual = 5.5010004e-08, No Iterations 100
time step continuity errors : sum local = 4.1085684e-11, global = 4.0954138e-14, cumulative = -1.2192389e-08
ExecutionTime = 394.37 s  ClockTime = 396 s

Time = 436

smoothSolver:  Solving for Ux, Initial residual = 7.2115068e-09, Final residual = 7.2115068e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.900999e-09, Final residual = 5.900999e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015685484, Final residual = 1.4642825e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1537159e-05, Final residual = 1.9168126e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.5246986e-06, Final residual = 8.3022296e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.6434555e-06, Final residual = 5.5017949e-08, No Iterations 100
time step continuity errors : sum local = 4.0985277e-11, global = -6.2674479e-14, cumulative = -1.2192452e-08
ExecutionTime = 396.18 s  ClockTime = 398 s

Time = 437

smoothSolver:  Solving for Ux, Initial residual = 7.3419633e-09, Final residual = 7.3419633e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.0467124e-09, Final residual = 6.0467124e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015628587, Final residual = 1.4691072e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1204538e-05, Final residual = 1.8969327e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.3955418e-06, Final residual = 5.893763e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.7364251e-06, Final residual = 5.5184194e-08, No Iterations 100
time step continuity errors : sum local = 4.1193013e-11, global = 7.0359511e-14, cumulative = -1.2192381e-08
ExecutionTime = 398.02 s  ClockTime = 400 s

Time = 438

smoothSolver:  Solving for Ux, Initial residual = 7.3296497e-09, Final residual = 7.3296497e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.0281333e-09, Final residual = 6.0281333e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015593345, Final residual = 1.4728442e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1102991e-05, Final residual = 1.8319384e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.329841e-06, Final residual = 7.0742415e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.5104548e-06, Final residual = 5.5173132e-08, No Iterations 100
time step continuity errors : sum local = 4.1207461e-11, global = 1.8225605e-13, cumulative = -1.2192199e-08
ExecutionTime = 399.82 s  ClockTime = 402 s

Time = 439

smoothSolver:  Solving for Ux, Initial residual = 6.6525671e-09, Final residual = 6.6525671e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.4517023e-09, Final residual = 5.4517023e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015549277, Final residual = 1.4660179e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.105787e-05, Final residual = 1.8273943e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.171272e-06, Final residual = 6.9967111e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1898098e-06, Final residual = 5.5693576e-08, No Iterations 100
time step continuity errors : sum local = 4.1372899e-11, global = -5.268398e-14, cumulative = -1.2192252e-08
ExecutionTime = 401.64 s  ClockTime = 404 s

Time = 440

smoothSolver:  Solving for Ux, Initial residual = 7.2945604e-09, Final residual = 7.2945604e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.9879187e-09, Final residual = 5.9879187e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015497271, Final residual = 1.4355893e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1157151e-05, Final residual = 1.9572056e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.3759277e-06, Final residual = 7.8829119e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.3228917e-06, Final residual = 5.5124636e-08, No Iterations 100
time step continuity errors : sum local = 4.1252197e-11, global = -8.0131434e-14, cumulative = -1.2192332e-08
ExecutionTime = 403.57 s  ClockTime = 406 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 441

smoothSolver:  Solving for Ux, Initial residual = 7.6486349e-09, Final residual = 7.6486349e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.2930362e-09, Final residual = 6.2930362e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001545775, Final residual = 1.425442e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1247426e-05, Final residual = 2.103739e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.5955226e-06, Final residual = 7.1864096e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.4563283e-06, Final residual = 5.5217219e-08, No Iterations 100
time step continuity errors : sum local = 4.1227548e-11, global = -2.0606445e-13, cumulative = -1.2192538e-08
ExecutionTime = 405.96 s  ClockTime = 408 s

Time = 442

smoothSolver:  Solving for Ux, Initial residual = 8.5802708e-09, Final residual = 8.5802708e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.1048024e-09, Final residual = 7.1048024e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015425335, Final residual = 1.3759859e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1276236e-05, Final residual = 1.4699232e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 8.8235142e-06, Final residual = 7.4884935e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1209146e-06, Final residual = 5.5558058e-08, No Iterations 100
time step continuity errors : sum local = 4.1580177e-11, global = -1.9879149e-14, cumulative = -1.2192558e-08
ExecutionTime = 407.84 s  ClockTime = 410 s

Time = 443

smoothSolver:  Solving for Ux, Initial residual = 7.8237736e-09, Final residual = 7.8237736e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.4484833e-09, Final residual = 6.4484833e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015404088, Final residual = 1.3091755e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.124006e-05, Final residual = 1.9579391e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.4070254e-06, Final residual = 7.5642696e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1626688e-06, Final residual = 5.5174589e-08, No Iterations 100
time step continuity errors : sum local = 4.1212725e-11, global = 4.7511949e-14, cumulative = -1.219251e-08
ExecutionTime = 409.68 s  ClockTime = 412 s

Time = 444

smoothSolver:  Solving for Ux, Initial residual = 6.8616553e-09, Final residual = 6.8616553e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6100226e-09, Final residual = 5.6100226e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015390979, Final residual = 1.2767053e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1242454e-05, Final residual = 1.6275721e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.2119065e-06, Final residual = 7.5704643e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.4178545e-06, Final residual = 5.4972167e-08, No Iterations 100
time step continuity errors : sum local = 4.1073462e-11, global = -2.7686944e-14, cumulative = -1.2192538e-08
ExecutionTime = 411.55 s  ClockTime = 414 s

Time = 445

smoothSolver:  Solving for Ux, Initial residual = 7.1121331e-09, Final residual = 7.1121331e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.831074e-09, Final residual = 5.831074e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015385147, Final residual = 1.2776e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1217529e-05, Final residual = 1.3329407e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.4172559e-06, Final residual = 6.7516309e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.2784857e-06, Final residual = 5.4884977e-08, No Iterations 100
time step continuity errors : sum local = 4.0948025e-11, global = 9.0238307e-14, cumulative = -1.2192448e-08
ExecutionTime = 413.43 s  ClockTime = 415 s

Time = 446

smoothSolver:  Solving for Ux, Initial residual = 7.8890842e-09, Final residual = 7.8890842e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.4928059e-09, Final residual = 6.4928059e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015369927, Final residual = 1.2912656e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1052988e-05, Final residual = 1.5226629e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.3556875e-06, Final residual = 7.7882113e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.2450433e-06, Final residual = 5.5098949e-08, No Iterations 100
time step continuity errors : sum local = 4.1217696e-11, global = 3.4998885e-14, cumulative = -1.2192413e-08
ExecutionTime = 415.5 s  ClockTime = 417 s

Time = 447

smoothSolver:  Solving for Ux, Initial residual = 7.9248047e-09, Final residual = 7.9248047e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.5272415e-09, Final residual = 6.5272415e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015339183, Final residual = 1.3066775e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0833297e-05, Final residual = 1.5943018e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.2181195e-06, Final residual = 7.6470796e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.2324599e-06, Final residual = 5.5150285e-08, No Iterations 100
time step continuity errors : sum local = 4.1238106e-11, global = -1.311899e-13, cumulative = -1.2192544e-08
ExecutionTime = 417.53 s  ClockTime = 420 s

Time = 448

smoothSolver:  Solving for Ux, Initial residual = 6.652616e-09, Final residual = 6.652616e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.4426426e-09, Final residual = 5.4426426e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015297547, Final residual = 1.3167661e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0594039e-05, Final residual = 1.6198913e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.0832323e-06, Final residual = 7.8607213e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.1706338e-06, Final residual = 5.5061042e-08, No Iterations 100
time step continuity errors : sum local = 4.1139517e-11, global = 1.9101744e-13, cumulative = -1.2192353e-08
ExecutionTime = 419.31 s  ClockTime = 421 s

Time = 449

smoothSolver:  Solving for Ux, Initial residual = 7.4006839e-09, Final residual = 7.4006839e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.0758925e-09, Final residual = 6.0758925e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015243265, Final residual = 1.3131145e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0342616e-05, Final residual = 1.5540968e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.9565721e-06, Final residual = 6.9895601e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.2433578e-06, Final residual = 5.5417028e-08, No Iterations 100
time step continuity errors : sum local = 4.1148115e-11, global = 1.9986777e-14, cumulative = -1.2192333e-08
ExecutionTime = 421.11 s  ClockTime = 423 s

Time = 450

smoothSolver:  Solving for Ux, Initial residual = 6.9772563e-09, Final residual = 6.9772563e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.7224729e-09, Final residual = 5.7224729e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015181688, Final residual = 1.2878632e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0209174e-05, Final residual = 1.8255519e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.9801649e-06, Final residual = 6.2731531e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.198694e-06, Final residual = 5.5326458e-08, No Iterations 100
time step continuity errors : sum local = 4.1420627e-11, global = 4.8798947e-14, cumulative = -1.2192284e-08
ExecutionTime = 423.34 s  ClockTime = 426 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 451

smoothSolver:  Solving for Ux, Initial residual = 6.746798e-09, Final residual = 6.746798e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.5228571e-09, Final residual = 5.5228571e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015125206, Final residual = 1.2557385e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0210156e-05, Final residual = 1.7467865e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.9668121e-06, Final residual = 7.0646553e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.2022315e-06, Final residual = 5.5198406e-08, No Iterations 100
time step continuity errors : sum local = 4.1170663e-11, global = -1.6704642e-13, cumulative = -1.2192451e-08
ExecutionTime = 425.5 s  ClockTime = 428 s

Time = 452

smoothSolver:  Solving for Ux, Initial residual = 7.746944e-09, Final residual = 7.746944e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.3850361e-09, Final residual = 6.3850361e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015070343, Final residual = 1.2325047e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0235792e-05, Final residual = 1.9950788e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.0665454e-06, Final residual = 7.2296538e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.0763234e-06, Final residual = 5.4932364e-08, No Iterations 100
time step continuity errors : sum local = 4.0780806e-11, global = -3.7882118e-14, cumulative = -1.2192489e-08
ExecutionTime = 427.27 s  ClockTime = 429 s

Time = 453

smoothSolver:  Solving for Ux, Initial residual = 7.7235873e-09, Final residual = 7.7235873e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.3575697e-09, Final residual = 6.3575697e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00015021214, Final residual = 1.2258216e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0351028e-05, Final residual = 1.7329743e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.0822516e-06, Final residual = 7.7485451e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.0875329e-06, Final residual = 5.5001328e-08, No Iterations 100
time step continuity errors : sum local = 4.1209278e-11, global = 6.2869691e-14, cumulative = -1.2192426e-08
ExecutionTime = 429.11 s  ClockTime = 431 s

Time = 454

smoothSolver:  Solving for Ux, Initial residual = 6.7446943e-09, Final residual = 6.7446943e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.5248122e-09, Final residual = 5.5248122e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014987619, Final residual = 1.2355976e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0498976e-05, Final residual = 1.3741173e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 8.2598105e-06, Final residual = 6.6281052e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.9404375e-06, Final residual = 5.5271348e-08, No Iterations 100
time step continuity errors : sum local = 4.1175076e-11, global = -1.6414707e-13, cumulative = -1.219259e-08
ExecutionTime = 430.99 s  ClockTime = 433 s

Time = 455

smoothSolver:  Solving for Ux, Initial residual = 7.3091006e-09, Final residual = 7.3091006e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.0036039e-09, Final residual = 6.0036039e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014976109, Final residual = 1.2543199e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0738032e-05, Final residual = 1.7257972e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.2586686e-06, Final residual = 7.9369642e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.2259824e-06, Final residual = 5.4600465e-08, No Iterations 100
time step continuity errors : sum local = 4.0915127e-11, global = -6.8210554e-14, cumulative = -1.2192659e-08
ExecutionTime = 432.88 s  ClockTime = 435 s

Time = 456

smoothSolver:  Solving for Ux, Initial residual = 6.9656341e-09, Final residual = 6.9656341e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.7093685e-09, Final residual = 5.7093685e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001497367, Final residual = 1.2811851e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0749409e-05, Final residual = 1.751857e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.3456173e-06, Final residual = 7.327971e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.9378257e-06, Final residual = 5.5141991e-08, No Iterations 100
time step continuity errors : sum local = 4.1098812e-11, global = -1.3968146e-13, cumulative = -1.2192798e-08
ExecutionTime = 434.74 s  ClockTime = 437 s

Time = 457

smoothSolver:  Solving for Ux, Initial residual = 6.9846433e-09, Final residual = 6.9846433e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.7174979e-09, Final residual = 5.7174979e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014979914, Final residual = 1.3165563e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0777878e-05, Final residual = 1.4436099e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.3703573e-06, Final residual = 7.2469457e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1486666e-06, Final residual = 5.5261491e-08, No Iterations 100
time step continuity errors : sum local = 4.1496049e-11, global = -5.1442603e-14, cumulative = -1.219285e-08
ExecutionTime = 436.59 s  ClockTime = 439 s

Time = 458

smoothSolver:  Solving for Ux, Initial residual = 6.6004499e-09, Final residual = 6.6004499e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.4056763e-09, Final residual = 5.4056763e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014992773, Final residual = 1.3738016e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0925018e-05, Final residual = 1.7198276e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.4613692e-06, Final residual = 8.2701813e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.4958278e-06, Final residual = 5.466424e-08, No Iterations 100
time step continuity errors : sum local = 4.0614375e-11, global = 2.0786148e-14, cumulative = -1.2192829e-08
ExecutionTime = 438.46 s  ClockTime = 441 s

Time = 459

smoothSolver:  Solving for Ux, Initial residual = 7.1943841e-09, Final residual = 7.1943841e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.9126242e-09, Final residual = 5.9126242e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014986524, Final residual = 1.3943617e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1049684e-05, Final residual = 1.8902562e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.2920443e-06, Final residual = 7.7782286e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.6960225e-06, Final residual = 5.5154854e-08, No Iterations 100
time step continuity errors : sum local = 4.1281318e-11, global = 8.8232515e-14, cumulative = -1.2192741e-08
ExecutionTime = 440.29 s  ClockTime = 442 s

Time = 460

smoothSolver:  Solving for Ux, Initial residual = 7.8904934e-09, Final residual = 7.8904934e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.5108042e-09, Final residual = 6.5108042e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014968555, Final residual = 1.4078119e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1019018e-05, Final residual = 1.9589905e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.3477248e-06, Final residual = 7.413965e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.5797235e-06, Final residual = 5.5371309e-08, No Iterations 100
time step continuity errors : sum local = 4.128293e-11, global = -4.5508039e-14, cumulative = -1.2192786e-08
ExecutionTime = 442.12 s  ClockTime = 444 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 461

smoothSolver:  Solving for Ux, Initial residual = 7.2919967e-09, Final residual = 7.2919967e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.9969072e-09, Final residual = 5.9969072e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014936704, Final residual = 1.415993e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0810487e-05, Final residual = 1.9186623e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.2255356e-06, Final residual = 8.2238102e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.5637325e-06, Final residual = 5.5358495e-08, No Iterations 100
time step continuity errors : sum local = 4.1260848e-11, global = 1.3713964e-13, cumulative = -1.2192649e-08
ExecutionTime = 444.01 s  ClockTime = 446 s

Time = 462

smoothSolver:  Solving for Ux, Initial residual = 7.5096535e-09, Final residual = 7.5096535e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.1914771e-09, Final residual = 6.1914771e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014885496, Final residual = 1.4215838e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0427178e-05, Final residual = 1.8542895e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.0907515e-06, Final residual = 7.4042166e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.5260004e-06, Final residual = 5.5244813e-08, No Iterations 100
time step continuity errors : sum local = 4.1200717e-11, global = 2.4205397e-13, cumulative = -1.2192407e-08
ExecutionTime = 445.86 s  ClockTime = 448 s

Time = 463

smoothSolver:  Solving for Ux, Initial residual = 7.9452491e-09, Final residual = 7.9452491e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.5719426e-09, Final residual = 6.5719426e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001484851, Final residual = 1.4272069e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0253405e-05, Final residual = 1.2248026e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.0264359e-06, Final residual = 7.5394708e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.4160017e-06, Final residual = 5.5059774e-08, No Iterations 100
time step continuity errors : sum local = 4.1039871e-11, global = -9.1458827e-14, cumulative = -1.2192499e-08
ExecutionTime = 447.67 s  ClockTime = 450 s

Time = 464

smoothSolver:  Solving for Ux, Initial residual = 6.5888563e-09, Final residual = 6.5888563e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.4195294e-09, Final residual = 5.4195294e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014811802, Final residual = 1.4269139e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0217195e-05, Final residual = 1.8156692e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.8917706e-06, Final residual = 7.705905e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1536324e-06, Final residual = 5.4829306e-08, No Iterations 100
time step continuity errors : sum local = 4.0980218e-11, global = -5.3193338e-14, cumulative = -1.2192552e-08
ExecutionTime = 449.55 s  ClockTime = 452 s

Time = 465

smoothSolver:  Solving for Ux, Initial residual = 7.5030711e-09, Final residual = 7.5030711e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.1892377e-09, Final residual = 6.1892377e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014766473, Final residual = 1.4050611e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.03089e-05, Final residual = 1.2950274e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.9961202e-06, Final residual = 7.1342486e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.2609833e-06, Final residual = 5.5469337e-08, No Iterations 100
time step continuity errors : sum local = 4.1509179e-11, global = 2.7831366e-13, cumulative = -1.2192273e-08
ExecutionTime = 451.35 s  ClockTime = 454 s

Time = 466

smoothSolver:  Solving for Ux, Initial residual = 6.4945929e-09, Final residual = 6.4945929e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.3153866e-09, Final residual = 5.3153866e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014725659, Final residual = 1.3948123e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0481526e-05, Final residual = 1.3719287e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.464785e-06, Final residual = 7.8167783e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1722926e-06, Final residual = 5.5264964e-08, No Iterations 100
time step continuity errors : sum local = 4.110508e-11, global = -1.5537582e-13, cumulative = -1.2192429e-08
ExecutionTime = 453.15 s  ClockTime = 455 s

Time = 467

smoothSolver:  Solving for Ux, Initial residual = 7.5320538e-09, Final residual = 7.5320538e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.2168663e-09, Final residual = 6.2168663e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014698752, Final residual = 1.3675117e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.053469e-05, Final residual = 1.4896094e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 8.6137e-06, Final residual = 8.6019302e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.0695559e-06, Final residual = 5.5214263e-08, No Iterations 100
time step continuity errors : sum local = 4.0997909e-11, global = -4.0457214e-14, cumulative = -1.2192469e-08
ExecutionTime = 454.98 s  ClockTime = 457 s

Time = 468

smoothSolver:  Solving for Ux, Initial residual = 7.4553498e-09, Final residual = 7.4553498e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.1451447e-09, Final residual = 6.1451447e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014670375, Final residual = 1.2924086e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0522175e-05, Final residual = 1.999927e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.190192e-06, Final residual = 7.7325387e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.078265e-06, Final residual = 5.4923542e-08, No Iterations 100
time step continuity errors : sum local = 4.1111153e-11, global = 1.1884642e-13, cumulative = -1.219235e-08
ExecutionTime = 456.86 s  ClockTime = 459 s

Time = 469

smoothSolver:  Solving for Ux, Initial residual = 6.3878541e-09, Final residual = 6.3878541e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.2285754e-09, Final residual = 5.2285754e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014660167, Final residual = 1.2501661e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0511915e-05, Final residual = 1.7649483e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.1435802e-06, Final residual = 7.2970773e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1096562e-06, Final residual = 5.5296607e-08, No Iterations 100
time step continuity errors : sum local = 4.1286114e-11, global = -4.6807857e-14, cumulative = -1.2192397e-08
ExecutionTime = 458.69 s  ClockTime = 461 s

Time = 470

smoothSolver:  Solving for Ux, Initial residual = 6.4600131e-09, Final residual = 6.4600131e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.2777837e-09, Final residual = 5.2777837e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014659774, Final residual = 1.2459558e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0531943e-05, Final residual = 1.4329276e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.0447478e-06, Final residual = 7.5916479e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.3005146e-06, Final residual = 5.5722626e-08, No Iterations 100
time step continuity errors : sum local = 4.1377763e-11, global = -5.1752407e-13, cumulative = -1.2192915e-08
ExecutionTime = 460.48 s  ClockTime = 463 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305954e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.161494e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 471

smoothSolver:  Solving for Ux, Initial residual = 8.9372456e-09, Final residual = 8.9372456e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.4031068e-09, Final residual = 7.4031068e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014654328, Final residual = 1.2623576e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0421357e-05, Final residual = 1.8847401e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.9449452e-06, Final residual = 6.8622416e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.3558566e-06, Final residual = 5.5153075e-08, No Iterations 100
time step continuity errors : sum local = 4.128428e-11, global = 1.0007991e-13, cumulative = -1.2192815e-08
ExecutionTime = 462.27 s  ClockTime = 464 s

Time = 472

smoothSolver:  Solving for Ux, Initial residual = 6.6621631e-09, Final residual = 6.6621631e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.4418394e-09, Final residual = 5.4418394e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014631555, Final residual = 1.2840085e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0238432e-05, Final residual = 1.4045981e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.9582961e-06, Final residual = 7.1513518e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1974127e-06, Final residual = 5.5403228e-08, No Iterations 100
time step continuity errors : sum local = 4.1015515e-11, global = -1.4847654e-14, cumulative = -1.219283e-08
ExecutionTime = 464.08 s  ClockTime = 466 s

Time = 473

smoothSolver:  Solving for Ux, Initial residual = 6.757739e-09, Final residual = 6.757739e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.5597278e-09, Final residual = 5.5597278e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014600415, Final residual = 1.3028069e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0033048e-05, Final residual = 1.4316733e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.8465117e-06, Final residual = 6.5015392e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.243428e-06, Final residual = 5.5042829e-08, No Iterations 100
time step continuity errors : sum local = 4.1064141e-11, global = -6.8902186e-14, cumulative = -1.2192898e-08
ExecutionTime = 465.89 s  ClockTime = 468 s

Time = 474

smoothSolver:  Solving for Ux, Initial residual = 6.9334918e-09, Final residual = 6.9334918e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.7127996e-09, Final residual = 5.7127996e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014557656, Final residual = 1.3050732e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9787398e-05, Final residual = 1.6232688e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.8151057e-06, Final residual = 6.529436e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1528879e-06, Final residual = 5.4413679e-08, No Iterations 100
time step continuity errors : sum local = 4.0600762e-11, global = -5.9044407e-14, cumulative = -1.2192957e-08
ExecutionTime = 467.69 s  ClockTime = 470 s

Time = 475

smoothSolver:  Solving for Ux, Initial residual = 6.8755944e-09, Final residual = 6.8755944e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6566725e-09, Final residual = 5.6566725e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014502283, Final residual = 1.2843106e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9626545e-05, Final residual = 1.2010486e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7059928e-06, Final residual = 6.5649272e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.2843365e-06, Final residual = 5.4324232e-08, No Iterations 100
time step continuity errors : sum local = 4.0534232e-11, global = 2.093711e-13, cumulative = -1.2192748e-08
ExecutionTime = 469.51 s  ClockTime = 472 s

Time = 476

smoothSolver:  Solving for Ux, Initial residual = 8.172996e-09, Final residual = 8.172996e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.7589146e-09, Final residual = 6.7589146e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014446946, Final residual = 1.2518555e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.960296e-05, Final residual = 1.7965241e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7987079e-06, Final residual = 6.6354499e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1346132e-06, Final residual = 5.5522564e-08, No Iterations 100
time step continuity errors : sum local = 4.1545834e-11, global = -2.4957637e-13, cumulative = -1.2192998e-08
ExecutionTime = 471.34 s  ClockTime = 474 s

Time = 477

smoothSolver:  Solving for Ux, Initial residual = 6.2612437e-09, Final residual = 6.2612437e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.1241074e-09, Final residual = 5.1241074e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014387865, Final residual = 1.2218622e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.961869e-05, Final residual = 1.8719416e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.8201614e-06, Final residual = 7.094911e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.0431083e-06, Final residual = 5.4282871e-08, No Iterations 100
time step continuity errors : sum local = 4.0527032e-11, global = 7.305255e-14, cumulative = -1.2192925e-08
ExecutionTime = 473.18 s  ClockTime = 475 s

Time = 478

smoothSolver:  Solving for Ux, Initial residual = 6.4521936e-09, Final residual = 6.4521936e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.2724991e-09, Final residual = 5.2724991e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014334009, Final residual = 1.206745e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9684292e-05, Final residual = 1.9305716e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.8502437e-06, Final residual = 6.7217227e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.0529526e-06, Final residual = 5.5060536e-08, No Iterations 100
time step continuity errors : sum local = 4.1005529e-11, global = 9.1707361e-15, cumulative = -1.2192915e-08
ExecutionTime = 475.01 s  ClockTime = 477 s

Time = 479

smoothSolver:  Solving for Ux, Initial residual = 6.3052665e-09, Final residual = 6.3052665e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.1626405e-09, Final residual = 5.1626405e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014287547, Final residual = 1.2072684e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.983049e-05, Final residual = 1.9644271e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.8723819e-06, Final residual = 5.7720942e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.1454484e-06, Final residual = 5.4715002e-08, No Iterations 100
time step continuity errors : sum local = 4.0886923e-11, global = 1.6026486e-13, cumulative = -1.2192755e-08
ExecutionTime = 476.83 s  ClockTime = 479 s

Time = 480

smoothSolver:  Solving for Ux, Initial residual = 6.9050534e-09, Final residual = 6.9050534e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6721906e-09, Final residual = 5.6721906e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014266078, Final residual = 1.2160646e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0042229e-05, Final residual = 1.0923903e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 8.0638544e-06, Final residual = 7.1076749e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.0462088e-06, Final residual = 5.5370448e-08, No Iterations 100
time step continuity errors : sum local = 4.1246152e-11, global = -7.417291e-14, cumulative = -1.2192829e-08
ExecutionTime = 479.06 s  ClockTime = 481 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 481

smoothSolver:  Solving for Ux, Initial residual = 6.4050258e-09, Final residual = 6.4050258e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.2567994e-09, Final residual = 5.2567994e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.000142613, Final residual = 1.237788e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0140165e-05, Final residual = 1.8591022e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.0551196e-06, Final residual = 7.5528728e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.9609081e-06, Final residual = 5.5112132e-08, No Iterations 100
time step continuity errors : sum local = 4.1025927e-11, global = 8.8346699e-14, cumulative = -1.2192741e-08
ExecutionTime = 480.85 s  ClockTime = 483 s

Time = 482

smoothSolver:  Solving for Ux, Initial residual = 6.2067238e-09, Final residual = 6.2067238e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.0781162e-09, Final residual = 5.0781162e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014260564, Final residual = 1.2668451e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0140684e-05, Final residual = 1.358036e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.1535607e-06, Final residual = 5.7790956e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.1869792e-06, Final residual = 5.539258e-08, No Iterations 100
time step continuity errors : sum local = 4.1288547e-11, global = -1.1127726e-13, cumulative = -1.2192852e-08
ExecutionTime = 482.67 s  ClockTime = 485 s

Time = 483

smoothSolver:  Solving for Ux, Initial residual = 6.8850928e-09, Final residual = 6.8850928e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6551226e-09, Final residual = 5.6551226e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014276924, Final residual = 1.3131097e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0152836e-05, Final residual = 1.7720141e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.0877505e-06, Final residual = 7.2850905e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.4256468e-06, Final residual = 5.5072225e-08, No Iterations 100
time step continuity errors : sum local = 4.1204577e-11, global = 2.4708927e-13, cumulative = -1.2192605e-08
ExecutionTime = 484.46 s  ClockTime = 487 s

Time = 484

smoothSolver:  Solving for Ux, Initial residual = 6.9329701e-09, Final residual = 6.9329701e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.7152887e-09, Final residual = 5.7152887e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014278433, Final residual = 1.3491212e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0377309e-05, Final residual = 1.7701857e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.2063401e-06, Final residual = 7.8886963e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.5515133e-06, Final residual = 5.6682037e-08, No Iterations 100
time step continuity errors : sum local = 4.2082852e-11, global = 3.6261009e-13, cumulative = -1.2192243e-08
ExecutionTime = 486.26 s  ClockTime = 488 s

Time = 485

smoothSolver:  Solving for Ux, Initial residual = 8.2725937e-09, Final residual = 8.2725937e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.8546108e-09, Final residual = 6.8546108e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014265274, Final residual = 8.9404877e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0637537e-05, Final residual = 2.0061082e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.7259302e-06, Final residual = 6.4285494e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.779671e-06, Final residual = 5.5363098e-08, No Iterations 100
time step continuity errors : sum local = 4.1043555e-11, global = -3.8018529e-13, cumulative = -1.2192623e-08
ExecutionTime = 488.06 s  ClockTime = 490 s

Time = 486

smoothSolver:  Solving for Ux, Initial residual = 7.4822069e-09, Final residual = 7.4822069e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.1757728e-09, Final residual = 6.1757728e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014239409, Final residual = 1.3648833e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0219435e-05, Final residual = 1.6009711e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.9356273e-06, Final residual = 6.6959467e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.7386062e-06, Final residual = 5.5993139e-08, No Iterations 100
time step continuity errors : sum local = 4.1664248e-11, global = -2.0806134e-13, cumulative = -1.2192831e-08
ExecutionTime = 489.87 s  ClockTime = 492 s

Time = 487

smoothSolver:  Solving for Ux, Initial residual = 8.6362285e-09, Final residual = 8.6362285e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.1716818e-09, Final residual = 7.1716818e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014194832, Final residual = 1.3667818e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9866321e-05, Final residual = 1.8179385e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.8888813e-06, Final residual = 7.1312614e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.5218552e-06, Final residual = 5.521217e-08, No Iterations 100
time step continuity errors : sum local = 4.1155588e-11, global = 1.1371659e-14, cumulative = -1.2192819e-08
ExecutionTime = 491.69 s  ClockTime = 494 s

Time = 488

smoothSolver:  Solving for Ux, Initial residual = 7.5815745e-09, Final residual = 7.5815745e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.2625858e-09, Final residual = 6.2625858e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001414889, Final residual = 1.3709635e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9545269e-05, Final residual = 1.5008581e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.6997372e-06, Final residual = 7.4220763e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.4623655e-06, Final residual = 5.4849257e-08, No Iterations 100
time step continuity errors : sum local = 4.0889927e-11, global = 6.1626816e-14, cumulative = -1.2192758e-08
ExecutionTime = 493.47 s  ClockTime = 496 s

Time = 489

smoothSolver:  Solving for Ux, Initial residual = 6.3102825e-09, Final residual = 6.3102825e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.1795098e-09, Final residual = 5.1795098e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014114643, Final residual = 1.3734097e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9495146e-05, Final residual = 1.7199375e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.6989884e-06, Final residual = 6.9648376e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.2777888e-06, Final residual = 5.5522629e-08, No Iterations 100
time step continuity errors : sum local = 4.1177197e-11, global = -1.0297036e-13, cumulative = -1.2192861e-08
ExecutionTime = 495.29 s  ClockTime = 497 s

Time = 490

smoothSolver:  Solving for Ux, Initial residual = 6.2651418e-09, Final residual = 6.2651418e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.1416688e-09, Final residual = 5.1416688e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014071854, Final residual = 1.3647424e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9489096e-05, Final residual = 1.7664049e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.6360578e-06, Final residual = 6.899687e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.0654716e-06, Final residual = 5.5764387e-08, No Iterations 100
time step continuity errors : sum local = 4.1299691e-11, global = -1.9104995e-13, cumulative = -1.2193052e-08
ExecutionTime = 497.09 s  ClockTime = 499 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.161494e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 491

smoothSolver:  Solving for Ux, Initial residual = 6.4789632e-09, Final residual = 6.4789632e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.3215424e-09, Final residual = 5.3215424e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00014025555, Final residual = 1.3494142e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9645329e-05, Final residual = 1.9479115e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.9424259e-06, Final residual = 7.0235437e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.1737286e-06, Final residual = 5.5079852e-08, No Iterations 100
time step continuity errors : sum local = 4.1259127e-11, global = -2.2393338e-14, cumulative = -1.2193074e-08
ExecutionTime = 498.92 s  ClockTime = 501 s

Time = 492

smoothSolver:  Solving for Ux, Initial residual = 6.1491392e-09, Final residual = 6.1491392e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.0566383e-09, Final residual = 5.0566383e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013997163, Final residual = 1.3366275e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.969517e-05, Final residual = 1.4848886e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 8.2899456e-06, Final residual = 7.5666614e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.9333853e-06, Final residual = 5.5402712e-08, No Iterations 100
time step continuity errors : sum local = 4.1429467e-11, global = 2.0944252e-13, cumulative = -1.2192865e-08
ExecutionTime = 500.79 s  ClockTime = 503 s

Time = 493

smoothSolver:  Solving for Ux, Initial residual = 7.6997366e-09, Final residual = 7.6997366e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.3931726e-09, Final residual = 6.3931726e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013959261, Final residual = 8.9242638e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.983554e-05, Final residual = 1.7076e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.4070066e-06, Final residual = 6.4265717e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.9500689e-06, Final residual = 5.4973458e-08, No Iterations 100
time step continuity errors : sum local = 4.0936566e-11, global = -4.071132e-13, cumulative = -1.2193272e-08
ExecutionTime = 502.62 s  ClockTime = 505 s

Time = 494

smoothSolver:  Solving for Ux, Initial residual = 6.8113408e-09, Final residual = 6.8113408e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6169108e-09, Final residual = 5.6169108e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001394661, Final residual = 1.2025119e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9606947e-05, Final residual = 1.7966172e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7895842e-06, Final residual = 6.6634423e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.9977269e-06, Final residual = 5.4302072e-08, No Iterations 100
time step continuity errors : sum local = 4.0661831e-11, global = 5.720741e-14, cumulative = -1.2193215e-08
ExecutionTime = 504.44 s  ClockTime = 507 s

Time = 495

smoothSolver:  Solving for Ux, Initial residual = 6.1075446e-09, Final residual = 6.1075446e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.0023316e-09, Final residual = 5.0023316e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013942074, Final residual = 1.1848664e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9639396e-05, Final residual = 1.3816247e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.8492048e-06, Final residual = 6.8146973e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.0152037e-06, Final residual = 5.50871e-08, No Iterations 100
time step continuity errors : sum local = 4.0970607e-11, global = 2.6054919e-14, cumulative = -1.2193189e-08
ExecutionTime = 506.32 s  ClockTime = 509 s

Time = 496

smoothSolver:  Solving for Ux, Initial residual = 6.5854265e-09, Final residual = 6.5854265e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.4015659e-09, Final residual = 5.4015659e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013940194, Final residual = 1.1919955e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9534671e-05, Final residual = 1.4099481e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.791024e-06, Final residual = 6.1920357e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.0360904e-06, Final residual = 5.534763e-08, No Iterations 100
time step continuity errors : sum local = 4.1386306e-11, global = -2.8773573e-13, cumulative = -1.2193476e-08
ExecutionTime = 508.13 s  ClockTime = 510 s

Time = 497

smoothSolver:  Solving for Ux, Initial residual = 6.7532415e-09, Final residual = 6.7532415e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.565824e-09, Final residual = 5.565824e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013919672, Final residual = 1.2079407e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9338928e-05, Final residual = 1.4526799e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.6655088e-06, Final residual = 6.4747815e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.9846789e-06, Final residual = 5.5376105e-08, No Iterations 100
time step continuity errors : sum local = 4.1412398e-11, global = -7.3101056e-14, cumulative = -1.219355e-08
ExecutionTime = 509.96 s  ClockTime = 512 s

Time = 498

smoothSolver:  Solving for Ux, Initial residual = 6.3883053e-09, Final residual = 6.3883053e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.2427653e-09, Final residual = 5.2427653e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013886914, Final residual = 1.2262259e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9088137e-05, Final residual = 1.4797556e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.5071634e-06, Final residual = 6.594454e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.963104e-06, Final residual = 5.5234186e-08, No Iterations 100
time step continuity errors : sum local = 4.1050644e-11, global = -1.1870176e-13, cumulative = -1.2193668e-08
ExecutionTime = 511.77 s  ClockTime = 514 s

Time = 499

smoothSolver:  Solving for Ux, Initial residual = 6.4291457e-09, Final residual = 6.4291457e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.2749039e-09, Final residual = 5.2749039e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013842011, Final residual = 1.2321042e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.882048e-05, Final residual = 1.3603541e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.3440941e-06, Final residual = 6.3432643e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.9743694e-06, Final residual = 5.4871218e-08, No Iterations 100
time step continuity errors : sum local = 4.097558e-11, global = 3.8719096e-14, cumulative = -1.219363e-08
ExecutionTime = 513.55 s  ClockTime = 516 s

Time = 500

smoothSolver:  Solving for Ux, Initial residual = 6.5421213e-09, Final residual = 6.5421213e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.3663271e-09, Final residual = 5.3663271e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013786658, Final residual = 1.2117825e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8591216e-05, Final residual = 1.4583247e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.3158392e-06, Final residual = 6.1841621e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.9959465e-06, Final residual = 5.4896811e-08, No Iterations 100
time step continuity errors : sum local = 4.1245524e-11, global = 6.0339321e-15, cumulative = -1.2193623e-08
ExecutionTime = 515.75 s  ClockTime = 518 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 501

smoothSolver:  Solving for Ux, Initial residual = 6.9051017e-09, Final residual = 6.9051017e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6706202e-09, Final residual = 5.6706202e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013726088, Final residual = 1.1710731e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8532259e-05, Final residual = 1.5558563e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.3309537e-06, Final residual = 7.0546589e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.9697084e-06, Final residual = 5.454015e-08, No Iterations 100
time step continuity errors : sum local = 4.0661239e-11, global = -1.0225365e-13, cumulative = -1.2193726e-08
ExecutionTime = 517.51 s  ClockTime = 520 s

Time = 502

smoothSolver:  Solving for Ux, Initial residual = 6.2753577e-09, Final residual = 6.2753577e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.1371035e-09, Final residual = 5.1371035e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013670839, Final residual = 1.1396149e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8541494e-05, Final residual = 1.8347404e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.430817e-06, Final residual = 6.6847539e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.880051e-06, Final residual = 5.5273873e-08, No Iterations 100
time step continuity errors : sum local = 4.1291744e-11, global = -2.4600014e-15, cumulative = -1.2193728e-08
ExecutionTime = 519.3 s  ClockTime = 522 s

Time = 503

smoothSolver:  Solving for Ux, Initial residual = 6.3600963e-09, Final residual = 6.3600963e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.2247316e-09, Final residual = 5.2247316e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013619449, Final residual = 1.1295502e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8617191e-05, Final residual = 1.2366705e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.6763152e-06, Final residual = 6.1353759e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.7583887e-06, Final residual = 5.5123621e-08, No Iterations 100
time step continuity errors : sum local = 4.1170305e-11, global = 1.8786417e-13, cumulative = -1.219354e-08
ExecutionTime = 521.11 s  ClockTime = 523 s

Time = 504

smoothSolver:  Solving for Ux, Initial residual = 7.4239628e-09, Final residual = 7.4239628e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.14851e-09, Final residual = 6.14851e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013576697, Final residual = 1.1379894e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8776027e-05, Final residual = 1.6917765e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.4168164e-06, Final residual = 6.9148701e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.9983861e-06, Final residual = 5.5038839e-08, No Iterations 100
time step continuity errors : sum local = 4.1056012e-11, global = -3.159603e-13, cumulative = -1.2193856e-08
ExecutionTime = 522.87 s  ClockTime = 525 s

Time = 505

smoothSolver:  Solving for Ux, Initial residual = 6.8194182e-09, Final residual = 6.8194182e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6237458e-09, Final residual = 5.6237458e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013555477, Final residual = 1.1552611e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.899523e-05, Final residual = 1.6015758e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.4783647e-06, Final residual = 5.7931689e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.9732168e-06, Final residual = 5.5170219e-08, No Iterations 100
time step continuity errors : sum local = 4.0898218e-11, global = -9.6427841e-14, cumulative = -1.2193953e-08
ExecutionTime = 524.74 s  ClockTime = 527 s

Time = 506

smoothSolver:  Solving for Ux, Initial residual = 7.0072279e-09, Final residual = 7.0072279e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.7902928e-09, Final residual = 5.7902928e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013552971, Final residual = 1.1784749e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9250468e-05, Final residual = 1.0590916e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.8266885e-06, Final residual = 5.9224949e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.9947502e-06, Final residual = 5.5078947e-08, No Iterations 100
time step continuity errors : sum local = 4.1033213e-11, global = -3.0694857e-13, cumulative = -1.219426e-08
ExecutionTime = 526.55 s  ClockTime = 529 s

Time = 507

smoothSolver:  Solving for Ux, Initial residual = 8.0804767e-09, Final residual = 8.0804767e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.7024703e-09, Final residual = 6.7024703e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013559428, Final residual = 1.2058469e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9230523e-05, Final residual = 1.2107474e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.6674315e-06, Final residual = 6.9865105e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.8441898e-06, Final residual = 5.528825e-08, No Iterations 100
time step continuity errors : sum local = 4.1195703e-11, global = 5.899415e-15, cumulative = -1.2194254e-08
ExecutionTime = 528.33 s  ClockTime = 531 s

Time = 508

smoothSolver:  Solving for Ux, Initial residual = 6.4271709e-09, Final residual = 6.4271709e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.2893324e-09, Final residual = 5.2893324e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013576372, Final residual = 1.2415924e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9219539e-05, Final residual = 1.4326249e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.8281832e-06, Final residual = 7.255406e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.0603279e-06, Final residual = 5.4745536e-08, No Iterations 100
time step continuity errors : sum local = 4.0942117e-11, global = -2.0363317e-14, cumulative = -1.2194274e-08
ExecutionTime = 530.11 s  ClockTime = 533 s

Time = 509

smoothSolver:  Solving for Ux, Initial residual = 6.1795291e-09, Final residual = 6.1795291e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.0733617e-09, Final residual = 5.0733617e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013592922, Final residual = 1.2925487e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9366803e-05, Final residual = 1.3655226e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.9243763e-06, Final residual = 6.9130474e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.3882747e-06, Final residual = 5.5283545e-08, No Iterations 100
time step continuity errors : sum local = 4.134528e-11, global = -1.9494812e-14, cumulative = -1.2194294e-08
ExecutionTime = 531.93 s  ClockTime = 534 s

Time = 510

smoothSolver:  Solving for Ux, Initial residual = 6.752749e-09, Final residual = 6.752749e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.5698994e-09, Final residual = 5.5698994e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013585839, Final residual = 1.3053911e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9445585e-05, Final residual = 1.7718134e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.8382575e-06, Final residual = 7.6331884e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.3908608e-06, Final residual = 5.5192986e-08, No Iterations 100
time step continuity errors : sum local = 4.131702e-11, global = 6.5212251e-14, cumulative = -1.2194228e-08
ExecutionTime = 533.71 s  ClockTime = 536 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 511

smoothSolver:  Solving for Ux, Initial residual = 7.5762693e-09, Final residual = 7.5762693e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.2573738e-09, Final residual = 6.2573738e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013565053, Final residual = 1.312165e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9372017e-05, Final residual = 1.8378963e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7336971e-06, Final residual = 6.1235274e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.5087312e-06, Final residual = 5.5654284e-08, No Iterations 100
time step continuity errors : sum local = 4.1360268e-11, global = 1.7169707e-13, cumulative = -1.2194057e-08
ExecutionTime = 535.7 s  ClockTime = 538 s

Time = 512

smoothSolver:  Solving for Ux, Initial residual = 7.9787193e-09, Final residual = 7.9787193e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.6091895e-09, Final residual = 6.6091895e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013528583, Final residual = 1.3134444e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9122998e-05, Final residual = 1.5770929e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.5181469e-06, Final residual = 6.9523528e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.5069066e-06, Final residual = 5.5324915e-08, No Iterations 100
time step continuity errors : sum local = 4.1271722e-11, global = -9.2061128e-14, cumulative = -1.2194149e-08
ExecutionTime = 537.56 s  ClockTime = 540 s

Time = 513

smoothSolver:  Solving for Ux, Initial residual = 6.4144611e-09, Final residual = 6.4144611e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.2713652e-09, Final residual = 5.2713652e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013475324, Final residual = 1.3156323e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8731717e-05, Final residual = 1.4347943e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.4000115e-06, Final residual = 6.02869e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.5128676e-06, Final residual = 5.539356e-08, No Iterations 100
time step continuity errors : sum local = 4.1342754e-11, global = -2.5124545e-13, cumulative = -1.21944e-08
ExecutionTime = 539.36 s  ClockTime = 542 s

Time = 514

smoothSolver:  Solving for Ux, Initial residual = 7.1504895e-09, Final residual = 7.1504895e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.9075488e-09, Final residual = 5.9075488e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013445596, Final residual = 1.3203682e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8614204e-05, Final residual = 1.6589748e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.3912721e-06, Final residual = 6.6437078e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.2031222e-06, Final residual = 5.4362426e-08, No Iterations 100
time step continuity errors : sum local = 4.0608133e-11, global = -2.2865605e-13, cumulative = -1.2194629e-08
ExecutionTime = 541.16 s  ClockTime = 544 s

Time = 515

smoothSolver:  Solving for Ux, Initial residual = 8.0144894e-09, Final residual = 8.0144894e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.6590594e-09, Final residual = 6.6590594e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013407406, Final residual = 1.3155533e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.856237e-05, Final residual = 1.6774833e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.2322117e-06, Final residual = 7.1039187e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.8683615e-06, Final residual = 5.5365453e-08, No Iterations 100
time step continuity errors : sum local = 4.1509918e-11, global = -2.50533e-14, cumulative = -1.2194654e-08
ExecutionTime = 542.97 s  ClockTime = 545 s

Time = 516

smoothSolver:  Solving for Ux, Initial residual = 7.1562208e-09, Final residual = 7.1562208e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.9148238e-09, Final residual = 5.9148238e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013363209, Final residual = 1.3009894e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8735576e-05, Final residual = 1.8543817e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.5630373e-06, Final residual = 7.263856e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.0185852e-06, Final residual = 5.5281742e-08, No Iterations 100
time step continuity errors : sum local = 4.1162109e-11, global = -1.2812934e-13, cumulative = -1.2194782e-08
ExecutionTime = 545.07 s  ClockTime = 547 s

Time = 517

smoothSolver:  Solving for Ux, Initial residual = 6.8066316e-09, Final residual = 6.8066316e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.617295e-09, Final residual = 5.617295e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013335677, Final residual = 1.2978204e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8844864e-05, Final residual = 1.4492245e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 8.0225865e-06, Final residual = 6.3073978e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.8155008e-06, Final residual = 5.5112928e-08, No Iterations 100
time step continuity errors : sum local = 4.1049028e-11, global = -1.663664e-13, cumulative = -1.2194948e-08
ExecutionTime = 546.87 s  ClockTime = 549 s

Time = 518

smoothSolver:  Solving for Ux, Initial residual = 6.3841719e-09, Final residual = 6.3841719e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.244561e-09, Final residual = 5.244561e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013299298, Final residual = 1.2328239e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.879282e-05, Final residual = 1.5556555e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.8933041e-06, Final residual = 6.7691023e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.8314914e-06, Final residual = 5.4956142e-08, No Iterations 100
time step continuity errors : sum local = 4.0961393e-11, global = -4.2600608e-14, cumulative = -1.2194991e-08
ExecutionTime = 548.66 s  ClockTime = 551 s

Time = 519

smoothSolver:  Solving for Ux, Initial residual = 6.1810425e-09, Final residual = 6.1810425e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.0881559e-09, Final residual = 5.0881559e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013281534, Final residual = 1.1699996e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8742712e-05, Final residual = 1.8422655e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.5175008e-06, Final residual = 7.1586377e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.8134516e-06, Final residual = 5.446133e-08, No Iterations 100
time step continuity errors : sum local = 4.0663568e-11, global = -2.0621539e-13, cumulative = -1.2195197e-08
ExecutionTime = 550.46 s  ClockTime = 553 s

Time = 520

smoothSolver:  Solving for Ux, Initial residual = 5.9382063e-09, Final residual = 5.9382063e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.8734612e-09, Final residual = 4.8734612e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001327771, Final residual = 1.1421665e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.881332e-05, Final residual = 1.3865376e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.5692983e-06, Final residual = 6.8614706e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.8716636e-06, Final residual = 5.5383081e-08, No Iterations 100
time step continuity errors : sum local = 4.1269775e-11, global = 1.8379762e-13, cumulative = -1.2195013e-08
ExecutionTime = 552.24 s  ClockTime = 555 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 521

smoothSolver:  Solving for Ux, Initial residual = 7.7173676e-09, Final residual = 7.7173676e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.3929572e-09, Final residual = 6.3929572e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013281415, Final residual = 1.1428756e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8705003e-05, Final residual = 1.3891045e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.5204914e-06, Final residual = 6.4378257e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.7876378e-06, Final residual = 5.5196116e-08, No Iterations 100
time step continuity errors : sum local = 4.1097113e-11, global = -2.2179633e-13, cumulative = -1.2195235e-08
ExecutionTime = 554.08 s  ClockTime = 556 s

Time = 522

smoothSolver:  Solving for Ux, Initial residual = 6.3639424e-09, Final residual = 6.3639424e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.2215525e-09, Final residual = 5.2215525e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013268285, Final residual = 1.1574033e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8489937e-05, Final residual = 1.3237588e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.3449256e-06, Final residual = 6.7486257e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.8471927e-06, Final residual = 5.5055686e-08, No Iterations 100
time step continuity errors : sum local = 4.0819445e-11, global = 3.5169461e-14, cumulative = -1.21952e-08
ExecutionTime = 555.86 s  ClockTime = 558 s

Time = 523

smoothSolver:  Solving for Ux, Initial residual = 6.6473152e-09, Final residual = 6.6473152e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.4800435e-09, Final residual = 5.4800435e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001324078, Final residual = 1.1780507e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8239989e-05, Final residual = 1.0965208e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.1920797e-06, Final residual = 6.4259599e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.8264203e-06, Final residual = 5.459658e-08, No Iterations 100
time step continuity errors : sum local = 4.100819e-11, global = -3.0944491e-14, cumulative = -1.2195231e-08
ExecutionTime = 557.67 s  ClockTime = 560 s

Time = 524

smoothSolver:  Solving for Ux, Initial residual = 6.2672761e-09, Final residual = 6.2672761e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.139936e-09, Final residual = 5.139936e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001320172, Final residual = 1.1912532e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7969799e-05, Final residual = 1.2335776e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.886745e-06, Final residual = 5.7415996e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.9044449e-06, Final residual = 5.5239529e-08, No Iterations 100
time step continuity errors : sum local = 4.1096813e-11, global = 2.3530878e-13, cumulative = -1.2194995e-08
ExecutionTime = 559.51 s  ClockTime = 562 s

Time = 525

smoothSolver:  Solving for Ux, Initial residual = 7.3401938e-09, Final residual = 7.3401938e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.0562594e-09, Final residual = 6.0562594e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013152504, Final residual = 1.1766872e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7732544e-05, Final residual = 1.1008699e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.9296574e-06, Final residual = 6.2660508e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.6822708e-06, Final residual = 5.5235818e-08, No Iterations 100
time step continuity errors : sum local = 4.1192233e-11, global = 6.5075118e-14, cumulative = -1.219493e-08
ExecutionTime = 561.34 s  ClockTime = 564 s

Time = 526

smoothSolver:  Solving for Ux, Initial residual = 6.6897219e-09, Final residual = 6.6897219e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.4975482e-09, Final residual = 5.4975482e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001309791, Final residual = 1.1321943e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7629657e-05, Final residual = 1.6026698e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.9801302e-06, Final residual = 6.3179831e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.6334355e-06, Final residual = 5.5129791e-08, No Iterations 100
time step continuity errors : sum local = 4.1286216e-11, global = 4.1800373e-14, cumulative = -1.2194889e-08
ExecutionTime = 563.16 s  ClockTime = 566 s

Time = 527

smoothSolver:  Solving for Ux, Initial residual = 6.0122656e-09, Final residual = 6.0122656e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.9169809e-09, Final residual = 4.9169809e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00013045155, Final residual = 1.0939805e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7631639e-05, Final residual = 1.580794e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.9794256e-06, Final residual = 6.1388229e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.7979567e-06, Final residual = 5.5134256e-08, No Iterations 100
time step continuity errors : sum local = 4.1142544e-11, global = 8.6772546e-14, cumulative = -1.2194802e-08
ExecutionTime = 564.98 s  ClockTime = 567 s

Time = 528

smoothSolver:  Solving for Ux, Initial residual = 5.8477501e-09, Final residual = 5.8477501e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.7978985e-09, Final residual = 4.7978985e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012994582, Final residual = 1.0848547e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7675921e-05, Final residual = 1.6493267e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.0142078e-06, Final residual = 6.6959751e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.7694522e-06, Final residual = 5.5176113e-08, No Iterations 100
time step continuity errors : sum local = 4.1316465e-11, global = 1.3855997e-13, cumulative = -1.2194663e-08
ExecutionTime = 566.78 s  ClockTime = 569 s

Time = 529

smoothSolver:  Solving for Ux, Initial residual = 5.8836753e-09, Final residual = 5.8836753e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.8329765e-09, Final residual = 4.8329765e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012952755, Final residual = 1.0968231e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7779406e-05, Final residual = 1.0020482e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.1935468e-06, Final residual = 6.1958294e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.5738833e-06, Final residual = 5.4799255e-08, No Iterations 100
time step continuity errors : sum local = 4.0914219e-11, global = 7.4160313e-14, cumulative = -1.2194589e-08
ExecutionTime = 568.66 s  ClockTime = 571 s

Time = 530

smoothSolver:  Solving for Ux, Initial residual = 5.8365465e-09, Final residual = 5.8365465e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.7880835e-09, Final residual = 4.7880835e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001292874, Final residual = 1.1130344e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7939169e-05, Final residual = 1.2625789e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.2743855e-06, Final residual = 6.6632995e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4566705e-06, Final residual = 5.4727757e-08, No Iterations 100
time step continuity errors : sum local = 4.0890671e-11, global = -1.3083638e-13, cumulative = -1.219472e-08
ExecutionTime = 570.51 s  ClockTime = 573 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.161494e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 531

smoothSolver:  Solving for Ux, Initial residual = 7.0064591e-09, Final residual = 7.0064591e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.7891648e-09, Final residual = 5.7891648e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012922417, Final residual = 1.1284983e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8286529e-05, Final residual = 1.425535e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.3180067e-06, Final residual = 6.9642749e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.6405614e-06, Final residual = 5.5323584e-08, No Iterations 100
time step continuity errors : sum local = 4.1352639e-11, global = 3.2436657e-13, cumulative = -1.2194396e-08
ExecutionTime = 572.29 s  ClockTime = 575 s

Time = 532

smoothSolver:  Solving for Ux, Initial residual = 6.1191509e-09, Final residual = 6.1191509e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.04347e-09, Final residual = 5.04347e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012929018, Final residual = 1.1515703e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8390379e-05, Final residual = 1.7767628e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.2526647e-06, Final residual = 6.4045181e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.6945818e-06, Final residual = 5.5336531e-08, No Iterations 100
time step continuity errors : sum local = 4.1068816e-11, global = 2.1595242e-13, cumulative = -1.219418e-08
ExecutionTime = 574.08 s  ClockTime = 576 s

Time = 533

smoothSolver:  Solving for Ux, Initial residual = 6.8635451e-09, Final residual = 6.8635451e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6755433e-09, Final residual = 5.6755433e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012938534, Final residual = 8.5185358e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8638967e-05, Final residual = 1.0885326e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.974123e-06, Final residual = 6.4954173e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.6427837e-06, Final residual = 5.5433933e-08, No Iterations 100
time step continuity errors : sum local = 4.1426849e-11, global = 1.2347281e-13, cumulative = -1.2194056e-08
ExecutionTime = 575.89 s  ClockTime = 578 s

Time = 534

smoothSolver:  Solving for Ux, Initial residual = 6.3438228e-09, Final residual = 6.3438228e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.2349403e-09, Final residual = 5.2349403e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012959983, Final residual = 1.2196178e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8392729e-05, Final residual = 1.1775138e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.6053714e-06, Final residual = 6.9759811e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.939841e-06, Final residual = 5.5829765e-08, No Iterations 100
time step continuity errors : sum local = 4.1708353e-11, global = -3.875018e-13, cumulative = -1.2194444e-08
ExecutionTime = 577.69 s  ClockTime = 580 s

Time = 535

smoothSolver:  Solving for Ux, Initial residual = 8.0182571e-09, Final residual = 8.0182571e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.6351289e-09, Final residual = 6.6351289e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012964841, Final residual = 1.2485684e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8588164e-05, Final residual = 1.7910696e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.5415129e-06, Final residual = 5.9722304e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.330211e-06, Final residual = 5.5703679e-08, No Iterations 100
time step continuity errors : sum local = 4.1747602e-11, global = -9.9130241e-14, cumulative = -1.2194543e-08
ExecutionTime = 579.52 s  ClockTime = 582 s

Time = 536

smoothSolver:  Solving for Ux, Initial residual = 7.8882568e-09, Final residual = 7.8882568e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.5193947e-09, Final residual = 6.5193947e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012953882, Final residual = 1.2554688e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8567862e-05, Final residual = 1.7821692e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.4376406e-06, Final residual = 6.6378859e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.3001963e-06, Final residual = 5.4788462e-08, No Iterations 100
time step continuity errors : sum local = 4.082643e-11, global = -7.7385641e-14, cumulative = -1.219462e-08
ExecutionTime = 581.33 s  ClockTime = 584 s

Time = 537

smoothSolver:  Solving for Ux, Initial residual = 7.4068555e-09, Final residual = 7.4068555e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.1153688e-09, Final residual = 6.1153688e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012927516, Final residual = 1.2550344e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8387412e-05, Final residual = 1.1628756e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.3562861e-06, Final residual = 6.6153429e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.2840191e-06, Final residual = 5.5124813e-08, No Iterations 100
time step continuity errors : sum local = 4.1196324e-11, global = -7.4048025e-14, cumulative = -1.2194694e-08
ExecutionTime = 583.13 s  ClockTime = 586 s

Time = 538

smoothSolver:  Solving for Ux, Initial residual = 6.6034082e-09, Final residual = 6.6034082e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.4320129e-09, Final residual = 5.4320129e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012882185, Final residual = 1.256242e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8007356e-05, Final residual = 1.0908374e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.3283978e-06, Final residual = 6.6178187e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1263969e-06, Final residual = 5.527692e-08, No Iterations 100
time step continuity errors : sum local = 4.1311347e-11, global = 1.9813678e-13, cumulative = -1.2194496e-08
ExecutionTime = 584.93 s  ClockTime = 587 s

Time = 539

smoothSolver:  Solving for Ux, Initial residual = 6.8052082e-09, Final residual = 6.8052082e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6292776e-09, Final residual = 5.6292776e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012847616, Final residual = 1.261834e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7770162e-05, Final residual = 1.5678154e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.1023041e-06, Final residual = 6.38303e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.1354181e-06, Final residual = 5.5617467e-08, No Iterations 100
time step continuity errors : sum local = 4.1268125e-11, global = 7.4484252e-14, cumulative = -1.2194422e-08
ExecutionTime = 586.75 s  ClockTime = 589 s

Time = 540

smoothSolver:  Solving for Ux, Initial residual = 7.1476137e-09, Final residual = 7.1476137e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.9243933e-09, Final residual = 5.9243933e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012813091, Final residual = 1.261195e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7721044e-05, Final residual = 1.0980605e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.9474357e-06, Final residual = 6.546164e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.7627645e-06, Final residual = 5.519518e-08, No Iterations 100
time step continuity errors : sum local = 4.1524871e-11, global = 3.2555003e-13, cumulative = -1.2194096e-08
ExecutionTime = 588.54 s  ClockTime = 591 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.009891

Time = 541

smoothSolver:  Solving for Ux, Initial residual = 8.5096509e-09, Final residual = 8.5096509e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 7.0796655e-09, Final residual = 7.0796655e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012771865, Final residual = 1.2494217e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7827282e-05, Final residual = 1.2657946e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.3195563e-06, Final residual = 7.2997348e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.6526779e-06, Final residual = 5.5428296e-08, No Iterations 100
time step continuity errors : sum local = 4.1314738e-11, global = -4.7080645e-14, cumulative = -1.2194143e-08
ExecutionTime = 590.32 s  ClockTime = 593 s

Time = 542

smoothSolver:  Solving for Ux, Initial residual = 6.6914066e-09, Final residual = 6.6914066e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.5042455e-09, Final residual = 5.5042455e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012737681, Final residual = 1.2444747e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8001203e-05, Final residual = 1.4535487e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.6413815e-06, Final residual = 7.0997897e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.7987003e-06, Final residual = 5.5508218e-08, No Iterations 100
time step continuity errors : sum local = 4.1316298e-11, global = 2.6863879e-13, cumulative = -1.2193875e-08
ExecutionTime = 592.11 s  ClockTime = 595 s

Time = 543

smoothSolver:  Solving for Ux, Initial residual = 6.8836439e-09, Final residual = 6.8836439e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6794192e-09, Final residual = 5.6794192e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012703958, Final residual = 1.2025831e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8011519e-05, Final residual = 1.6593874e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.714116e-06, Final residual = 6.7728413e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.6975992e-06, Final residual = 5.4789582e-08, No Iterations 100
time step continuity errors : sum local = 4.0666461e-11, global = -6.5105243e-15, cumulative = -1.2193881e-08
ExecutionTime = 593.91 s  ClockTime = 596 s

Time = 544

smoothSolver:  Solving for Ux, Initial residual = 5.8241537e-09, Final residual = 5.8241537e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.8346959e-09, Final residual = 4.8346959e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001267843, Final residual = 1.135616e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7903101e-05, Final residual = 1.4366434e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.3345167e-06, Final residual = 7.0934965e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.5922553e-06, Final residual = 5.5454018e-08, No Iterations 100
time step continuity errors : sum local = 4.1327243e-11, global = 6.5070363e-14, cumulative = -1.2193816e-08
ExecutionTime = 595.69 s  ClockTime = 598 s

Time = 545

smoothSolver:  Solving for Ux, Initial residual = 6.3406855e-09, Final residual = 6.3406855e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.2531399e-09, Final residual = 5.2531399e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012671639, Final residual = 8.2830198e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.829517e-05, Final residual = 1.7865676e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.5280544e-06, Final residual = 5.9576529e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.8964837e-06, Final residual = 5.5018473e-08, No Iterations 100
time step continuity errors : sum local = 4.0954166e-11, global = -2.4391229e-13, cumulative = -1.219406e-08
ExecutionTime = 597.5 s  ClockTime = 600 s

Time = 546

smoothSolver:  Solving for Ux, Initial residual = 8.1794333e-09, Final residual = 8.1794333e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.809318e-09, Final residual = 6.809318e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012676094, Final residual = 1.0928841e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7915819e-05, Final residual = 1.2614965e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.1910824e-06, Final residual = 6.6609637e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.6207274e-06, Final residual = 5.5080387e-08, No Iterations 100
time step continuity errors : sum local = 4.1217669e-11, global = 6.8726685e-14, cumulative = -1.2193991e-08
ExecutionTime = 599.48 s  ClockTime = 602 s

Time = 547

smoothSolver:  Solving for Ux, Initial residual = 7.1785989e-09, Final residual = 7.1785989e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.9391702e-09, Final residual = 5.9391702e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012670377, Final residual = 1.1009734e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7701882e-05, Final residual = 1.2677006e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.0630359e-06, Final residual = 6.7448831e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.6392291e-06, Final residual = 5.5304335e-08, No Iterations 100
time step continuity errors : sum local = 4.1152417e-11, global = -4.288002e-14, cumulative = -1.2194034e-08
ExecutionTime = 601.27 s  ClockTime = 604 s

Time = 548

smoothSolver:  Solving for Ux, Initial residual = 6.6653298e-09, Final residual = 6.6653298e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.4672025e-09, Final residual = 5.4672025e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001264795, Final residual = 1.1181439e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7441713e-05, Final residual = 1.0684257e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.8914633e-06, Final residual = 6.5966201e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.594087e-06, Final residual = 5.5294511e-08, No Iterations 100
time step continuity errors : sum local = 4.1039765e-11, global = 2.5137693e-13, cumulative = -1.2193783e-08
ExecutionTime = 603.04 s  ClockTime = 605 s

Time = 549

smoothSolver:  Solving for Ux, Initial residual = 6.4821949e-09, Final residual = 6.4821949e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.3824269e-09, Final residual = 5.3824269e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012614072, Final residual = 1.1362606e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7175181e-05, Final residual = 1.3233978e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.7004452e-06, Final residual = 6.1593456e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.5431246e-06, Final residual = 5.5099174e-08, No Iterations 100
time step continuity errors : sum local = 4.1233041e-11, global = -3.4438641e-14, cumulative = -1.2193817e-08
ExecutionTime = 604.84 s  ClockTime = 607 s

Time = 550

smoothSolver:  Solving for Ux, Initial residual = 6.1390549e-09, Final residual = 6.1390549e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.0766041e-09, Final residual = 5.0766041e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012567791, Final residual = 1.1318537e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6936812e-05, Final residual = 8.9651393e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.5983638e-06, Final residual = 6.2363559e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.5056847e-06, Final residual = 5.5069099e-08, No Iterations 100
time step continuity errors : sum local = 4.1240796e-11, global = -4.0107069e-13, cumulative = -1.2194218e-08
ExecutionTime = 607.04 s  ClockTime = 610 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305954e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.161494e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 551

smoothSolver:  Solving for Ux, Initial residual = 7.2968389e-09, Final residual = 7.2968389e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.0274693e-09, Final residual = 6.0274693e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012514847, Final residual = 1.0908269e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6795703e-05, Final residual = 1.0194518e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.6928671e-06, Final residual = 6.0448413e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.471219e-06, Final residual = 5.5362733e-08, No Iterations 100
time step continuity errors : sum local = 4.123218e-11, global = 8.4454646e-14, cumulative = -1.2194134e-08
ExecutionTime = 608.83 s  ClockTime = 611 s

Time = 552

smoothSolver:  Solving for Ux, Initial residual = 5.7767591e-09, Final residual = 5.7767591e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.7441265e-09, Final residual = 4.7441265e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012460313, Final residual = 1.0494076e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.679015e-05, Final residual = 1.4613159e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.69299e-06, Final residual = 6.2706947e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.5822866e-06, Final residual = 5.492272e-08, No Iterations 100
time step continuity errors : sum local = 4.1220101e-11, global = -5.3023035e-14, cumulative = -1.2194187e-08
ExecutionTime = 610.64 s  ClockTime = 613 s

Time = 553

smoothSolver:  Solving for Ux, Initial residual = 5.6217872e-09, Final residual = 5.6217872e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.6306665e-09, Final residual = 4.6306665e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012410426, Final residual = 1.0385575e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6839119e-05, Final residual = 1.348688e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.7680662e-06, Final residual = 6.2587994e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.4912632e-06, Final residual = 5.4839885e-08, No Iterations 100
time step continuity errors : sum local = 4.1029806e-11, global = 8.369995e-14, cumulative = -1.2194103e-08
ExecutionTime = 612.45 s  ClockTime = 615 s

Time = 554

smoothSolver:  Solving for Ux, Initial residual = 6.423654e-09, Final residual = 6.423654e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.3043386e-09, Final residual = 5.3043386e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012365717, Final residual = 1.0514058e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6943129e-05, Final residual = 1.2260861e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.9649331e-06, Final residual = 6.3804757e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.3724495e-06, Final residual = 5.52902e-08, No Iterations 100
time step continuity errors : sum local = 4.1300831e-11, global = -5.9944803e-14, cumulative = -1.2194163e-08
ExecutionTime = 614.3 s  ClockTime = 617 s

Time = 555

smoothSolver:  Solving for Ux, Initial residual = 6.1171073e-09, Final residual = 6.1171073e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.039181e-09, Final residual = 5.039181e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012333869, Final residual = 1.0699302e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7084833e-05, Final residual = 1.4294835e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.9316318e-06, Final residual = 6.6943047e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.3189044e-06, Final residual = 5.4494029e-08, No Iterations 100
time step continuity errors : sum local = 4.0732822e-11, global = 2.4091302e-14, cumulative = -1.2194139e-08
ExecutionTime = 616.12 s  ClockTime = 619 s

Time = 556

smoothSolver:  Solving for Ux, Initial residual = 6.0648919e-09, Final residual = 6.0648919e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.9919302e-09, Final residual = 4.9919302e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012326701, Final residual = 1.0858376e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7371553e-05, Final residual = 1.0176054e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.8205727e-06, Final residual = 6.4314407e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.3438554e-06, Final residual = 5.5311149e-08, No Iterations 100
time step continuity errors : sum local = 4.1097805e-11, global = 1.7893809e-13, cumulative = -1.219396e-08
ExecutionTime = 618.05 s  ClockTime = 621 s

Time = 557

smoothSolver:  Solving for Ux, Initial residual = 6.7846357e-09, Final residual = 6.7846357e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6063388e-09, Final residual = 5.6063388e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012329257, Final residual = 8.4061908e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7789876e-05, Final residual = 1.7072917e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.6186025e-06, Final residual = 6.5864205e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.578842e-06, Final residual = 5.514052e-08, No Iterations 100
time step continuity errors : sum local = 4.1132462e-11, global = -1.1466443e-13, cumulative = -1.2194075e-08
ExecutionTime = 619.92 s  ClockTime = 623 s

Time = 558

smoothSolver:  Solving for Ux, Initial residual = 5.6173613e-09, Final residual = 5.6173613e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.6141281e-09, Final residual = 4.6141281e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012337589, Final residual = 1.1215898e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7695098e-05, Final residual = 1.5727563e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.2344669e-06, Final residual = 6.1886921e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.4907892e-06, Final residual = 5.4952688e-08, No Iterations 100
time step continuity errors : sum local = 4.0951042e-11, global = -1.3023511e-13, cumulative = -1.2194205e-08
ExecutionTime = 621.72 s  ClockTime = 624 s

Time = 559

smoothSolver:  Solving for Ux, Initial residual = 6.4914669e-09, Final residual = 6.4914669e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.3752989e-09, Final residual = 5.3752989e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012356434, Final residual = 1.1504706e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7707385e-05, Final residual = 1.6234032e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.3461581e-06, Final residual = 6.4266003e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.6939454e-06, Final residual = 5.5431922e-08, No Iterations 100
time step continuity errors : sum local = 4.1382333e-11, global = -2.2556833e-13, cumulative = -1.219443e-08
ExecutionTime = 623.51 s  ClockTime = 626 s

Time = 560

smoothSolver:  Solving for Ux, Initial residual = 7.4511639e-09, Final residual = 7.4511639e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.2080299e-09, Final residual = 6.2080299e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012371484, Final residual = 1.1920058e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7831876e-05, Final residual = 1.2257788e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.3778993e-06, Final residual = 6.4799444e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.1028771e-06, Final residual = 5.4991993e-08, No Iterations 100
time step continuity errors : sum local = 4.1082683e-11, global = 1.4075592e-13, cumulative = -1.219429e-08
ExecutionTime = 625.39 s  ClockTime = 628 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 561

smoothSolver:  Solving for Ux, Initial residual = 5.7264919e-09, Final residual = 5.7264919e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.7086331e-09, Final residual = 4.7086331e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012365089, Final residual = 1.1992623e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7874394e-05, Final residual = 1.2845639e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.2712505e-06, Final residual = 6.4152557e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.1480261e-06, Final residual = 5.5198723e-08, No Iterations 100
time step continuity errors : sum local = 4.132554e-11, global = -4.9090872e-15, cumulative = -1.2194295e-08
ExecutionTime = 627.28 s  ClockTime = 630 s

Time = 562

smoothSolver:  Solving for Ux, Initial residual = 5.7405837e-09, Final residual = 5.7405837e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.7128769e-09, Final residual = 4.7128769e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012346781, Final residual = 1.1984875e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7727686e-05, Final residual = 1.7487091e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.1438638e-06, Final residual = 6.3727744e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.1905557e-06, Final residual = 5.5271598e-08, No Iterations 100
time step continuity errors : sum local = 4.1181673e-11, global = -2.3366997e-13, cumulative = -1.2194528e-08
ExecutionTime = 629.16 s  ClockTime = 632 s

Time = 563

smoothSolver:  Solving for Ux, Initial residual = 5.9685276e-09, Final residual = 5.9685276e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.9236869e-09, Final residual = 4.9236869e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012313605, Final residual = 1.1983619e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7426176e-05, Final residual = 1.6083928e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.0035811e-06, Final residual = 6.4542624e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.1037537e-06, Final residual = 5.4962121e-08, No Iterations 100
time step continuity errors : sum local = 4.1000318e-11, global = -6.8676346e-14, cumulative = -1.2194597e-08
ExecutionTime = 631 s  ClockTime = 634 s

Time = 564

smoothSolver:  Solving for Ux, Initial residual = 5.6216986e-09, Final residual = 5.6216986e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.6168538e-09, Final residual = 4.6168538e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012270855, Final residual = 7.5080976e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.708677e-05, Final residual = 1.350594e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.5954302e-06, Final residual = 6.410176e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.1189674e-06, Final residual = 5.4707745e-08, No Iterations 100
time step continuity errors : sum local = 4.0987896e-11, global = 2.3658179e-13, cumulative = -1.219436e-08
ExecutionTime = 632.86 s  ClockTime = 635 s

Time = 565

smoothSolver:  Solving for Ux, Initial residual = 7.1543838e-09, Final residual = 7.1543838e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.9392932e-09, Final residual = 5.9392932e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012244989, Final residual = 1.2086672e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7027398e-05, Final residual = 1.6851982e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.7910032e-06, Final residual = 6.6015768e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.8055394e-06, Final residual = 5.5128616e-08, No Iterations 100
time step continuity errors : sum local = 4.1366868e-11, global = 3.9911558e-14, cumulative = -1.219432e-08
ExecutionTime = 634.7 s  ClockTime = 637 s

Time = 566

smoothSolver:  Solving for Ux, Initial residual = 6.8635852e-09, Final residual = 6.8635852e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6906638e-09, Final residual = 5.6906638e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012207909, Final residual = 1.2041572e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7059129e-05, Final residual = 1.1875089e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.957443e-06, Final residual = 5.7889121e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.6750857e-06, Final residual = 5.4082547e-08, No Iterations 100
time step continuity errors : sum local = 4.0383698e-11, global = 2.8243276e-14, cumulative = -1.2194292e-08
ExecutionTime = 636.55 s  ClockTime = 639 s

Time = 567

smoothSolver:  Solving for Ux, Initial residual = 6.309821e-09, Final residual = 6.309821e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.2186523e-09, Final residual = 5.2186523e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012169746, Final residual = 1.1987163e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7253685e-05, Final residual = 1.3858118e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.4135228e-06, Final residual = 6.8097603e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.5632503e-06, Final residual = 5.5755977e-08, No Iterations 100
time step continuity errors : sum local = 4.1247725e-11, global = -7.8188069e-14, cumulative = -1.219437e-08
ExecutionTime = 638.47 s  ClockTime = 641 s

Time = 568

smoothSolver:  Solving for Ux, Initial residual = 5.4604006e-09, Final residual = 5.4604006e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.4876844e-09, Final residual = 4.4876844e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012135707, Final residual = 1.17694e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7296923e-05, Final residual = 1.3602329e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.5870641e-06, Final residual = 7.0418854e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4750139e-06, Final residual = 5.4889992e-08, No Iterations 100
time step continuity errors : sum local = 4.1341554e-11, global = -1.6142133e-13, cumulative = -1.2194532e-08
ExecutionTime = 640.81 s  ClockTime = 643 s

Time = 569

smoothSolver:  Solving for Ux, Initial residual = 6.7526344e-09, Final residual = 6.7526344e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6024275e-09, Final residual = 5.6024275e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012105521, Final residual = 1.1131803e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7132056e-05, Final residual = 1.5746456e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.2290164e-06, Final residual = 6.7573347e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.3762068e-06, Final residual = 5.5260994e-08, No Iterations 100
time step continuity errors : sum local = 4.1237746e-11, global = 1.7339165e-13, cumulative = -1.2194358e-08
ExecutionTime = 642.76 s  ClockTime = 645 s

Time = 570

smoothSolver:  Solving for Ux, Initial residual = 5.4742064e-09, Final residual = 5.4742064e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.4967536e-09, Final residual = 4.4967536e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012099636, Final residual = 1.0703336e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7201915e-05, Final residual = 1.3232961e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.9611354e-06, Final residual = 6.103231e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.5169505e-06, Final residual = 5.5123181e-08, No Iterations 100
time step continuity errors : sum local = 4.1111167e-11, global = -6.9505702e-14, cumulative = -1.2194428e-08
ExecutionTime = 644.77 s  ClockTime = 647 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 571

smoothSolver:  Solving for Ux, Initial residual = 5.7741996e-09, Final residual = 5.7741996e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.7533654e-09, Final residual = 4.7533654e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012100157, Final residual = 1.0554457e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7167807e-05, Final residual = 1.1129732e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.8147706e-06, Final residual = 6.2993575e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.566485e-06, Final residual = 5.5298774e-08, No Iterations 100
time step continuity errors : sum local = 4.116009e-11, global = 8.9488395e-14, cumulative = -1.2194338e-08
ExecutionTime = 646.65 s  ClockTime = 649 s

Time = 572

smoothSolver:  Solving for Ux, Initial residual = 5.6587324e-09, Final residual = 5.6587324e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.636978e-09, Final residual = 4.636978e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012102134, Final residual = 1.0563391e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.697031e-05, Final residual = 1.2112422e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.7775154e-06, Final residual = 6.6234399e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.3743023e-06, Final residual = 5.52576e-08, No Iterations 100
time step continuity errors : sum local = 4.1068738e-11, global = 1.9581213e-13, cumulative = -1.2194143e-08
ExecutionTime = 648.55 s  ClockTime = 651 s

Time = 573

smoothSolver:  Solving for Ux, Initial residual = 6.5281829e-09, Final residual = 6.5281829e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.3838476e-09, Final residual = 5.3838476e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012087709, Final residual = 7.6174697e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6791338e-05, Final residual = 9.6711577e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.309817e-06, Final residual = 6.3077531e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.4167815e-06, Final residual = 5.5103219e-08, No Iterations 100
time step continuity errors : sum local = 4.1190854e-11, global = 2.7834839e-14, cumulative = -1.2194115e-08
ExecutionTime = 650.37 s  ClockTime = 653 s

Time = 574

smoothSolver:  Solving for Ux, Initial residual = 6.0308854e-09, Final residual = 6.0308854e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.9657394e-09, Final residual = 4.9657394e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012059629, Final residual = 1.0874041e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6453636e-05, Final residual = 9.8588824e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.3457022e-06, Final residual = 6.2741397e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.4703718e-06, Final residual = 5.5035708e-08, No Iterations 100
time step continuity errors : sum local = 4.1137022e-11, global = 2.6807466e-14, cumulative = -1.2194088e-08
ExecutionTime = 652.24 s  ClockTime = 655 s

Time = 575

smoothSolver:  Solving for Ux, Initial residual = 5.4967965e-09, Final residual = 5.4967965e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.5154192e-09, Final residual = 4.5154192e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00012018191, Final residual = 1.0915774e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6202566e-05, Final residual = 1.1633937e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.1557978e-06, Final residual = 5.8814936e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 3.4893406e-06, Final residual = 5.4941388e-08, No Iterations 100
time step continuity errors : sum local = 4.1059334e-11, global = -1.9875708e-13, cumulative = -1.2194287e-08
ExecutionTime = 654.07 s  ClockTime = 657 s

Time = 576

smoothSolver:  Solving for Ux, Initial residual = 6.7552332e-09, Final residual = 6.7552332e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.566663e-09, Final residual = 5.566663e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011967646, Final residual = 1.0571961e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6014941e-05, Final residual = 1.389775e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.2867868e-06, Final residual = 6.1763386e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2917978e-06, Final residual = 5.4157767e-08, No Iterations 100
time step continuity errors : sum local = 4.0365402e-11, global = -4.348319e-14, cumulative = -1.219433e-08
ExecutionTime = 656.13 s  ClockTime = 659 s

Time = 577

smoothSolver:  Solving for Ux, Initial residual = 6.6658796e-09, Final residual = 6.6658796e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.4960021e-09, Final residual = 5.4960021e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011911363, Final residual = 1.0129138e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5949386e-05, Final residual = 1.4956161e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.3535658e-06, Final residual = 5.6002597e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.3806715e-06, Final residual = 5.5686796e-08, No Iterations 100
time step continuity errors : sum local = 4.1344669e-11, global = -1.8569056e-13, cumulative = -1.2194516e-08
ExecutionTime = 658 s  ClockTime = 661 s

Time = 578

smoothSolver:  Solving for Ux, Initial residual = 6.9733533e-09, Final residual = 6.9733533e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.7689016e-09, Final residual = 5.7689016e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011863235, Final residual = 9.979842e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5984578e-05, Final residual = 1.460398e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.3447922e-06, Final residual = 6.2902144e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.4055592e-06, Final residual = 5.4854082e-08, No Iterations 100
time step continuity errors : sum local = 4.0917099e-11, global = -1.1855435e-14, cumulative = -1.2194528e-08
ExecutionTime = 659.84 s  ClockTime = 662 s

Time = 579

smoothSolver:  Solving for Ux, Initial residual = 5.9192482e-09, Final residual = 5.9192482e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.8683875e-09, Final residual = 4.8683875e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011819565, Final residual = 7.0164949e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6251066e-05, Final residual = 1.5983249e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.80008e-06, Final residual = 5.6699138e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 3.6091519e-06, Final residual = 5.5309576e-08, No Iterations 100
time step continuity errors : sum local = 4.1363342e-11, global = 2.5694379e-13, cumulative = -1.2194271e-08
ExecutionTime = 661.67 s  ClockTime = 664 s

Time = 580

smoothSolver:  Solving for Ux, Initial residual = 6.7613617e-09, Final residual = 6.7613617e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6161995e-09, Final residual = 5.6161995e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011780838, Final residual = 1.0288104e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6202308e-05, Final residual = 1.4565588e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.3289285e-06, Final residual = 6.0133984e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.470215e-06, Final residual = 5.4826516e-08, No Iterations 100
time step continuity errors : sum local = 4.1085761e-11, global = 3.062756e-13, cumulative = -1.2193965e-08
ExecutionTime = 663.53 s  ClockTime = 666 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.009891

Time = 581

smoothSolver:  Solving for Ux, Initial residual = 8.328738e-09, Final residual = 8.328738e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.9531216e-09, Final residual = 6.9531216e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011767272, Final residual = 1.0431255e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.642355e-05, Final residual = 1.1222291e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.5010146e-06, Final residual = 6.2213075e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2336305e-06, Final residual = 5.5661778e-08, No Iterations 100
time step continuity errors : sum local = 4.1548828e-11, global = 2.5701624e-13, cumulative = -1.2193707e-08
ExecutionTime = 665.32 s  ClockTime = 668 s

Time = 582

smoothSolver:  Solving for Ux, Initial residual = 8.2023968e-09, Final residual = 8.2023968e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.8472308e-09, Final residual = 6.8472308e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011764363, Final residual = 7.5455625e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6948728e-05, Final residual = 1.5297483e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.0497477e-06, Final residual = 5.7513768e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.3925521e-06, Final residual = 5.5139805e-08, No Iterations 100
time step continuity errors : sum local = 4.11704e-11, global = -1.1030837e-13, cumulative = -1.2193818e-08
ExecutionTime = 667.13 s  ClockTime = 670 s

Time = 583

smoothSolver:  Solving for Ux, Initial residual = 5.5363386e-09, Final residual = 5.5363386e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.5431616e-09, Final residual = 4.5431616e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011770891, Final residual = 7.7379952e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7145877e-05, Final residual = 1.5626774e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.282147e-06, Final residual = 5.9078e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.349485e-06, Final residual = 5.5247292e-08, No Iterations 100
time step continuity errors : sum local = 4.1229074e-11, global = -4.8607129e-14, cumulative = -1.2193866e-08
ExecutionTime = 668.92 s  ClockTime = 672 s

Time = 584

smoothSolver:  Solving for Ux, Initial residual = 6.4365174e-09, Final residual = 6.4365174e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.3556033e-09, Final residual = 5.3556033e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011781199, Final residual = 1.0898451e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6925534e-05, Final residual = 1.3121677e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.9802387e-06, Final residual = 6.8983372e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.4510048e-06, Final residual = 5.5097277e-08, No Iterations 100
time step continuity errors : sum local = 4.1074161e-11, global = 4.874724e-14, cumulative = -1.2193818e-08
ExecutionTime = 670.71 s  ClockTime = 673 s

Time = 585

smoothSolver:  Solving for Ux, Initial residual = 6.6509278e-09, Final residual = 6.6509278e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.5090545e-09, Final residual = 5.5090545e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011800001, Final residual = 1.1206866e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6904108e-05, Final residual = 1.504454e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.9972869e-06, Final residual = 6.323779e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.8448349e-06, Final residual = 5.5466332e-08, No Iterations 100
time step continuity errors : sum local = 4.1365693e-11, global = 1.654398e-13, cumulative = -1.2193652e-08
ExecutionTime = 672.51 s  ClockTime = 675 s

Time = 586

smoothSolver:  Solving for Ux, Initial residual = 5.7205721e-09, Final residual = 5.7205721e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.7065565e-09, Final residual = 4.7065565e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011804416, Final residual = 1.1461994e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7044302e-05, Final residual = 1.2378836e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.2050617e-06, Final residual = 6.764588e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.8504107e-06, Final residual = 5.5046344e-08, No Iterations 100
time step continuity errors : sum local = 4.103586e-11, global = -3.3280168e-16, cumulative = -1.2193653e-08
ExecutionTime = 674.37 s  ClockTime = 677 s

Time = 587

smoothSolver:  Solving for Ux, Initial residual = 5.9533047e-09, Final residual = 5.9533047e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.9055994e-09, Final residual = 4.9055994e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011790517, Final residual = 1.1456718e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.695748e-05, Final residual = 9.7461564e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.9578152e-06, Final residual = 6.5292894e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.0302042e-06, Final residual = 5.5249416e-08, No Iterations 100
time step continuity errors : sum local = 4.1382396e-11, global = -2.4910618e-13, cumulative = -1.2193902e-08
ExecutionTime = 676.22 s  ClockTime = 679 s

Time = 588

smoothSolver:  Solving for Ux, Initial residual = 7.252617e-09, Final residual = 7.252617e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.0103308e-09, Final residual = 6.0103308e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011765936, Final residual = 1.1426449e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6711954e-05, Final residual = 1.5429382e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.683726e-06, Final residual = 5.955855e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.1373998e-06, Final residual = 5.4863111e-08, No Iterations 100
time step continuity errors : sum local = 4.1228295e-11, global = 3.5778049e-13, cumulative = -1.2193544e-08
ExecutionTime = 678.09 s  ClockTime = 681 s

Time = 589

smoothSolver:  Solving for Ux, Initial residual = 6.0376741e-09, Final residual = 6.0376741e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.0082687e-09, Final residual = 5.0082687e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001172377, Final residual = 1.1450322e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6346862e-05, Final residual = 1.5309598e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.6175746e-06, Final residual = 5.9462801e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.9997788e-06, Final residual = 5.505404e-08, No Iterations 100
time step continuity errors : sum local = 4.1122665e-11, global = 1.7179827e-15, cumulative = -1.2193542e-08
ExecutionTime = 679.91 s  ClockTime = 683 s

Time = 590

smoothSolver:  Solving for Ux, Initial residual = 5.7861214e-09, Final residual = 5.7861214e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.7878745e-09, Final residual = 4.7878745e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001169873, Final residual = 1.1515433e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6216409e-05, Final residual = 1.0480773e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.5683916e-06, Final residual = 5.9795635e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.7802589e-06, Final residual = 5.5319928e-08, No Iterations 100
time step continuity errors : sum local = 4.1389218e-11, global = -2.326441e-14, cumulative = -1.2193565e-08
ExecutionTime = 681.73 s  ClockTime = 684 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 591

smoothSolver:  Solving for Ux, Initial residual = 5.3867074e-09, Final residual = 5.3867074e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.45003e-09, Final residual = 4.45003e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011667781, Final residual = 1.1526352e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6170242e-05, Final residual = 1.1516064e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.5580734e-06, Final residual = 6.1179252e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.4689719e-06, Final residual = 5.5420247e-08, No Iterations 100
time step continuity errors : sum local = 4.1452718e-11, global = -7.5348123e-14, cumulative = -1.2193641e-08
ExecutionTime = 683.53 s  ClockTime = 686 s

Time = 592

smoothSolver:  Solving for Ux, Initial residual = 5.4645395e-09, Final residual = 5.4645395e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.4942304e-09, Final residual = 4.4942304e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001162831, Final residual = 1.1456859e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6378451e-05, Final residual = 1.3343797e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.0368541e-06, Final residual = 6.1941722e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.4308177e-06, Final residual = 5.4284188e-08, No Iterations 100
time step continuity errors : sum local = 4.0714477e-11, global = -6.6918361e-14, cumulative = -1.2193708e-08
ExecutionTime = 685.35 s  ClockTime = 688 s

Time = 593

smoothSolver:  Solving for Ux, Initial residual = 5.7612398e-09, Final residual = 5.7612398e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.75458e-09, Final residual = 4.75458e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011595383, Final residual = 1.1364897e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6480715e-05, Final residual = 1.2688651e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.3080789e-06, Final residual = 6.1396551e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.3736594e-06, Final residual = 5.5572698e-08, No Iterations 100
time step continuity errors : sum local = 4.1443271e-11, global = 7.6795434e-15, cumulative = -1.21937e-08
ExecutionTime = 687.22 s  ClockTime = 690 s

Time = 594

smoothSolver:  Solving for Ux, Initial residual = 5.4262238e-09, Final residual = 5.4262238e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.4745817e-09, Final residual = 4.4745817e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011560351, Final residual = 8.0440472e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6479299e-05, Final residual = 1.2215387e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.585483e-06, Final residual = 6.3508374e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.3231928e-06, Final residual = 5.502172e-08, No Iterations 100
time step continuity errors : sum local = 4.1157269e-11, global = -3.1577037e-13, cumulative = -1.2194016e-08
ExecutionTime = 689.02 s  ClockTime = 692 s

Time = 595

smoothSolver:  Solving for Ux, Initial residual = 7.0280521e-09, Final residual = 7.0280521e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.8492046e-09, Final residual = 5.8492046e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011549082, Final residual = 1.0330621e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6376152e-05, Final residual = 1.0443772e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.8246647e-06, Final residual = 6.6951411e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2460951e-06, Final residual = 5.5059628e-08, No Iterations 100
time step continuity errors : sum local = 4.1201115e-11, global = -1.4889096e-13, cumulative = -1.2194165e-08
ExecutionTime = 691.19 s  ClockTime = 694 s

Time = 596

smoothSolver:  Solving for Ux, Initial residual = 6.5624685e-09, Final residual = 6.5624685e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.4531576e-09, Final residual = 5.4531576e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001154518, Final residual = 1.0110391e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.638625e-05, Final residual = 1.4518396e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.7013424e-06, Final residual = 6.4079881e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.3370632e-06, Final residual = 5.5024024e-08, No Iterations 100
time step continuity errors : sum local = 4.1355465e-11, global = 3.2464372e-14, cumulative = -1.2194132e-08
ExecutionTime = 693.04 s  ClockTime = 696 s

Time = 597

smoothSolver:  Solving for Ux, Initial residual = 5.3388486e-09, Final residual = 5.3388486e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.3702123e-09, Final residual = 4.3702123e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011550129, Final residual = 1.0052563e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6212977e-05, Final residual = 1.2131552e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.575852e-06, Final residual = 6.3353868e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.3046663e-06, Final residual = 5.5117293e-08, No Iterations 100
time step continuity errors : sum local = 4.0986236e-11, global = -2.231756e-13, cumulative = -1.2194355e-08
ExecutionTime = 694.82 s  ClockTime = 697 s

Time = 598

smoothSolver:  Solving for Ux, Initial residual = 5.5432508e-09, Final residual = 5.5432508e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.5437559e-09, Final residual = 4.5437559e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011543059, Final residual = 1.0117672e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5956237e-05, Final residual = 1.2204267e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.3958226e-06, Final residual = 6.2906404e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.2740109e-06, Final residual = 5.4966919e-08, No Iterations 100
time step continuity errors : sum local = 4.1048278e-11, global = -2.7373733e-14, cumulative = -1.2194383e-08
ExecutionTime = 696.64 s  ClockTime = 699 s

Time = 599

smoothSolver:  Solving for Ux, Initial residual = 5.6524501e-09, Final residual = 5.6524501e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.6516864e-09, Final residual = 4.6516864e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011520886, Final residual = 6.8155333e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5789527e-05, Final residual = 1.1050786e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.8167006e-06, Final residual = 5.695055e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.2625197e-06, Final residual = 5.5034621e-08, No Iterations 100
time step continuity errors : sum local = 4.1020272e-11, global = 5.8361038e-14, cumulative = -1.2194324e-08
ExecutionTime = 698.48 s  ClockTime = 701 s

Time = 600

smoothSolver:  Solving for Ux, Initial residual = 6.5956519e-09, Final residual = 6.5956519e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.4634664e-09, Final residual = 5.4634664e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011486106, Final residual = 1.0389025e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5451187e-05, Final residual = 9.2858285e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.950176e-06, Final residual = 5.9090745e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.2819888e-06, Final residual = 5.5311114e-08, No Iterations 100
time step continuity errors : sum local = 4.1219208e-11, global = -1.4628745e-14, cumulative = -1.2194339e-08
ExecutionTime = 700.69 s  ClockTime = 703 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 601

smoothSolver:  Solving for Ux, Initial residual = 6.4650199e-09, Final residual = 6.4650199e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.3298822e-09, Final residual = 5.3298822e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011439398, Final residual = 6.3396644e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5265515e-05, Final residual = 1.3202394e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.5789549e-06, Final residual = 5.5258003e-08, No Iterations 10
GAMG:  Solving for p, Initial residual = 3.2477969e-06, Final residual = 5.5421279e-08, No Iterations 100
time step continuity errors : sum local = 4.1350649e-11, global = -5.2837183e-14, cumulative = -1.2194392e-08
ExecutionTime = 702.54 s  ClockTime = 705 s

Time = 602

smoothSolver:  Solving for Ux, Initial residual = 5.9868168e-09, Final residual = 5.9868168e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.9130259e-09, Final residual = 4.9130259e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011387487, Final residual = 9.7288698e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5101875e-05, Final residual = 1.3183342e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.0326442e-06, Final residual = 5.8057219e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.153112e-06, Final residual = 5.5227064e-08, No Iterations 100
time step continuity errors : sum local = 4.1115225e-11, global = 8.734651e-14, cumulative = -1.2194305e-08
ExecutionTime = 704.34 s  ClockTime = 707 s

Time = 603

smoothSolver:  Solving for Ux, Initial residual = 6.0877645e-09, Final residual = 6.0877645e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.00181e-09, Final residual = 5.00181e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011337751, Final residual = 9.5227208e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5105163e-05, Final residual = 1.1261615e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.9971605e-06, Final residual = 5.9613043e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.2409544e-06, Final residual = 5.5226844e-08, No Iterations 100
time step continuity errors : sum local = 4.1161081e-11, global = 9.2547839e-14, cumulative = -1.2194212e-08
ExecutionTime = 706.17 s  ClockTime = 709 s

Time = 604

smoothSolver:  Solving for Ux, Initial residual = 6.0938367e-09, Final residual = 6.0938367e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.0136861e-09, Final residual = 5.0136861e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011292886, Final residual = 9.6106804e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.517112e-05, Final residual = 1.0649293e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.1926308e-06, Final residual = 5.7610625e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.0665879e-06, Final residual = 5.4525009e-08, No Iterations 100
time step continuity errors : sum local = 4.0709181e-11, global = 3.8242129e-14, cumulative = -1.2194174e-08
ExecutionTime = 708.01 s  ClockTime = 711 s

Time = 605

smoothSolver:  Solving for Ux, Initial residual = 5.549916e-09, Final residual = 5.549916e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.5632816e-09, Final residual = 4.5632816e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011256006, Final residual = 9.7845188e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5298311e-05, Final residual = 1.1299881e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.251616e-06, Final residual = 5.748982e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.0430279e-06, Final residual = 5.5382995e-08, No Iterations 100
time step continuity errors : sum local = 4.1124715e-11, global = 8.3255715e-14, cumulative = -1.219409e-08
ExecutionTime = 709.83 s  ClockTime = 713 s

Time = 606

smoothSolver:  Solving for Ux, Initial residual = 5.2862544e-09, Final residual = 5.2862544e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.3389649e-09, Final residual = 4.3389649e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011232858, Final residual = 9.9450118e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5463241e-05, Final residual = 1.1217856e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.2877592e-06, Final residual = 6.1239502e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.9859738e-06, Final residual = 5.4731863e-08, No Iterations 100
time step continuity errors : sum local = 4.0684292e-11, global = 5.9816218e-14, cumulative = -1.2194031e-08
ExecutionTime = 711.69 s  ClockTime = 714 s

Time = 607

smoothSolver:  Solving for Ux, Initial residual = 5.2591908e-09, Final residual = 5.2591908e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.3348642e-09, Final residual = 4.3348642e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011230538, Final residual = 1.006727e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5818507e-05, Final residual = 1.2087188e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.2279682e-06, Final residual = 5.8826602e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.0015379e-06, Final residual = 5.5121662e-08, No Iterations 100
time step continuity errors : sum local = 4.1234728e-11, global = -8.4158406e-14, cumulative = -1.2194115e-08
ExecutionTime = 713.5 s  ClockTime = 716 s

Time = 608

smoothSolver:  Solving for Ux, Initial residual = 6.1883175e-09, Final residual = 6.1883175e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.1170758e-09, Final residual = 5.1170758e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011234344, Final residual = 1.0190989e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6122011e-05, Final residual = 1.375784e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.4900213e-06, Final residual = 6.2253019e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.3316179e-06, Final residual = 5.4669466e-08, No Iterations 100
time step continuity errors : sum local = 4.0803558e-11, global = 7.5575951e-14, cumulative = -1.2194039e-08
ExecutionTime = 715.32 s  ClockTime = 718 s

Time = 609

smoothSolver:  Solving for Ux, Initial residual = 5.6495575e-09, Final residual = 5.6495575e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.6462653e-09, Final residual = 4.6462653e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011243179, Final residual = 1.0315842e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6159923e-05, Final residual = 1.5287035e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.6871677e-06, Final residual = 6.3727308e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2184591e-06, Final residual = 5.5262359e-08, No Iterations 100
time step continuity errors : sum local = 4.1263594e-11, global = -1.4504389e-14, cumulative = -1.2194054e-08
ExecutionTime = 717.14 s  ClockTime = 720 s

Time = 610

smoothSolver:  Solving for Ux, Initial residual = 5.7347135e-09, Final residual = 5.7347135e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.7220927e-09, Final residual = 4.7220927e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011260424, Final residual = 8.1743735e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6303162e-05, Final residual = 1.2158077e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.4512906e-06, Final residual = 6.3437978e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.4419842e-06, Final residual = 5.5267583e-08, No Iterations 100
time step continuity errors : sum local = 4.1295135e-11, global = 2.0225011e-13, cumulative = -1.2193851e-08
ExecutionTime = 718.98 s  ClockTime = 722 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 611

smoothSolver:  Solving for Ux, Initial residual = 5.7221083e-09, Final residual = 5.7221083e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.7274464e-09, Final residual = 4.7274464e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011273682, Final residual = 1.085697e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6226789e-05, Final residual = 1.2940594e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.7858486e-06, Final residual = 6.0639063e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.8837847e-06, Final residual = 5.5531121e-08, No Iterations 100
time step continuity errors : sum local = 4.1403296e-11, global = 3.076364e-13, cumulative = -1.2193544e-08
ExecutionTime = 720.8 s  ClockTime = 724 s

Time = 612

smoothSolver:  Solving for Ux, Initial residual = 6.8411982e-09, Final residual = 6.8411982e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6888776e-09, Final residual = 5.6888776e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011267818, Final residual = 1.0925931e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6252124e-05, Final residual = 1.3360867e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.7792832e-06, Final residual = 6.1888116e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.8263232e-06, Final residual = 5.5321894e-08, No Iterations 100
time step continuity errors : sum local = 4.1310011e-11, global = 9.4106093e-14, cumulative = -1.219345e-08
ExecutionTime = 722.65 s  ClockTime = 725 s

Time = 613

smoothSolver:  Solving for Ux, Initial residual = 6.1052385e-09, Final residual = 6.1052385e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.0587422e-09, Final residual = 5.0587422e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011250858, Final residual = 1.0890823e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6070231e-05, Final residual = 1.1936466e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.7991621e-06, Final residual = 6.1083441e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.767823e-06, Final residual = 5.5226642e-08, No Iterations 100
time step continuity errors : sum local = 4.1382288e-11, global = 3.1192184e-13, cumulative = -1.2193138e-08
ExecutionTime = 724.46 s  ClockTime = 727 s

Time = 614

smoothSolver:  Solving for Ux, Initial residual = 6.7286803e-09, Final residual = 6.7286803e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6030172e-09, Final residual = 5.6030172e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011217714, Final residual = 1.0896997e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5729439e-05, Final residual = 1.0181734e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.5408671e-06, Final residual = 5.9765918e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.8038073e-06, Final residual = 5.4871672e-08, No Iterations 100
time step continuity errors : sum local = 4.0943575e-11, global = 1.7490266e-13, cumulative = -1.2192963e-08
ExecutionTime = 726.28 s  ClockTime = 729 s

Time = 615

smoothSolver:  Solving for Ux, Initial residual = 5.9646448e-09, Final residual = 5.9646448e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.9396531e-09, Final residual = 4.9396531e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011186059, Final residual = 1.096943e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5506086e-05, Final residual = 1.2977992e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.2104247e-06, Final residual = 5.8152309e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.9261624e-06, Final residual = 5.5583725e-08, No Iterations 100
time step continuity errors : sum local = 4.1465604e-11, global = -4.5237105e-15, cumulative = -1.2192967e-08
ExecutionTime = 728.09 s  ClockTime = 731 s

Time = 616

smoothSolver:  Solving for Ux, Initial residual = 5.661621e-09, Final residual = 5.661621e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.6801216e-09, Final residual = 4.6801216e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011160366, Final residual = 1.1014874e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5469483e-05, Final residual = 1.3575914e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.0379993e-06, Final residual = 5.6705589e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.5804776e-06, Final residual = 5.5076842e-08, No Iterations 100
time step continuity errors : sum local = 4.0977371e-11, global = 4.9914018e-14, cumulative = -1.2192918e-08
ExecutionTime = 729.9 s  ClockTime = 733 s

Time = 617

smoothSolver:  Solving for Ux, Initial residual = 6.3684895e-09, Final residual = 6.3684895e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.2880888e-09, Final residual = 5.2880888e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011126268, Final residual = 1.0975625e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5588912e-05, Final residual = 1.2594881e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.6698737e-06, Final residual = 6.355976e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.3488842e-06, Final residual = 5.5218286e-08, No Iterations 100
time step continuity errors : sum local = 4.11155e-11, global = 1.0940392e-13, cumulative = -1.2192808e-08
ExecutionTime = 731.7 s  ClockTime = 734 s

Time = 618

smoothSolver:  Solving for Ux, Initial residual = 6.1131055e-09, Final residual = 6.1131055e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.0658949e-09, Final residual = 5.0658949e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011094002, Final residual = 1.0975322e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5756384e-05, Final residual = 1.0838859e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.9828792e-06, Final residual = 5.9253546e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.3586773e-06, Final residual = 5.4838054e-08, No Iterations 100
time step continuity errors : sum local = 4.1169311e-11, global = -1.3164324e-13, cumulative = -1.219294e-08
ExecutionTime = 733.5 s  ClockTime = 736 s

Time = 619

smoothSolver:  Solving for Ux, Initial residual = 7.0607964e-09, Final residual = 7.0607964e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.8649774e-09, Final residual = 5.8649774e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011054659, Final residual = 1.0557577e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5658941e-05, Final residual = 1.0707058e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.9883165e-06, Final residual = 6.3725435e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2825105e-06, Final residual = 5.4930617e-08, No Iterations 100
time step continuity errors : sum local = 4.089145e-11, global = 2.3723734e-13, cumulative = -1.2192703e-08
ExecutionTime = 735.31 s  ClockTime = 738 s

Time = 620

smoothSolver:  Solving for Ux, Initial residual = 5.2420553e-09, Final residual = 5.2420553e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.324905e-09, Final residual = 4.324905e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011036786, Final residual = 1.0056348e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5657455e-05, Final residual = 1.3524449e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.5212234e-06, Final residual = 5.9317282e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.2673729e-06, Final residual = 5.5421058e-08, No Iterations 100
time step continuity errors : sum local = 4.1357843e-11, global = 1.3533759e-13, cumulative = -1.2192567e-08
ExecutionTime = 737.2 s  ClockTime = 740 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 621

smoothSolver:  Solving for Ux, Initial residual = 5.5297765e-09, Final residual = 5.5297765e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.5881098e-09, Final residual = 4.5881098e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011031967, Final residual = 9.7978476e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5734204e-05, Final residual = 1.5257929e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.4542235e-06, Final residual = 6.0169267e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.2312443e-06, Final residual = 5.5064122e-08, No Iterations 100
time step continuity errors : sum local = 4.1304756e-11, global = -5.060301e-14, cumulative = -1.2192618e-08
ExecutionTime = 739.49 s  ClockTime = 742 s

Time = 622

smoothSolver:  Solving for Ux, Initial residual = 5.1855606e-09, Final residual = 5.1855606e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.2790811e-09, Final residual = 4.2790811e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011036748, Final residual = 9.7162995e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5610991e-05, Final residual = 1.3162858e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.4209545e-06, Final residual = 6.0967546e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.2008843e-06, Final residual = 5.517456e-08, No Iterations 100
time step continuity errors : sum local = 4.1279945e-11, global = -5.4496517e-14, cumulative = -1.2192672e-08
ExecutionTime = 741.28 s  ClockTime = 744 s

Time = 623

smoothSolver:  Solving for Ux, Initial residual = 5.5550398e-09, Final residual = 5.5550398e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.5714157e-09, Final residual = 4.5714157e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001103794, Final residual = 9.7407615e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5356791e-05, Final residual = 1.0216486e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.1706375e-06, Final residual = 5.8318728e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.2486905e-06, Final residual = 5.5082828e-08, No Iterations 100
time step continuity errors : sum local = 4.1077279e-11, global = 3.1202088e-14, cumulative = -1.2192641e-08
ExecutionTime = 743.11 s  ClockTime = 746 s

Time = 624

smoothSolver:  Solving for Ux, Initial residual = 5.1606511e-09, Final residual = 5.1606511e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.2370914e-09, Final residual = 4.2370914e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00011023498, Final residual = 9.8610072e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5117089e-05, Final residual = 1.223104e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.957405e-06, Final residual = 5.8660369e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.2349887e-06, Final residual = 5.5289719e-08, No Iterations 100
time step continuity errors : sum local = 4.1325472e-11, global = 7.3185568e-14, cumulative = -1.2192568e-08
ExecutionTime = 744.91 s  ClockTime = 748 s

Time = 625

smoothSolver:  Solving for Ux, Initial residual = 5.1265787e-09, Final residual = 5.1265787e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.2103317e-09, Final residual = 4.2103317e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010996898, Final residual = 9.9985979e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4868289e-05, Final residual = 1.1354803e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.7943688e-06, Final residual = 5.5727479e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.1111856e-06, Final residual = 5.5689817e-08, No Iterations 100
time step continuity errors : sum local = 4.1521089e-11, global = -3.8846735e-14, cumulative = -1.2192607e-08
ExecutionTime = 746.79 s  ClockTime = 750 s

Time = 626

smoothSolver:  Solving for Ux, Initial residual = 5.0981162e-09, Final residual = 5.0981162e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.211093e-09, Final residual = 4.211093e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001095609, Final residual = 9.9187343e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4651799e-05, Final residual = 1.0974551e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.6790635e-06, Final residual = 5.6612735e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 3.1021501e-06, Final residual = 5.5591277e-08, No Iterations 100
time step continuity errors : sum local = 4.1533413e-11, global = -1.3005118e-13, cumulative = -1.2192737e-08
ExecutionTime = 748.72 s  ClockTime = 752 s

Time = 627

smoothSolver:  Solving for Ux, Initial residual = 5.6060178e-09, Final residual = 5.6060178e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.6497919e-09, Final residual = 4.6497919e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010910215, Final residual = 9.497184e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4487589e-05, Final residual = 9.7950195e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.6577156e-06, Final residual = 5.6448359e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 3.1461299e-06, Final residual = 5.5153428e-08, No Iterations 100
time step continuity errors : sum local = 4.1159229e-11, global = -8.456969e-14, cumulative = -1.2192821e-08
ExecutionTime = 750.54 s  ClockTime = 753 s

Time = 628

smoothSolver:  Solving for Ux, Initial residual = 5.6403602e-09, Final residual = 5.6403602e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.6793099e-09, Final residual = 4.6793099e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010862214, Final residual = 9.2174474e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4435057e-05, Final residual = 1.0346111e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.6761594e-06, Final residual = 5.5919554e-08, No Iterations 10
GAMG:  Solving for p, Initial residual = 3.1978803e-06, Final residual = 5.5383342e-08, No Iterations 100
time step continuity errors : sum local = 4.1396175e-11, global = 1.5173254e-13, cumulative = -1.219267e-08
ExecutionTime = 752.4 s  ClockTime = 755 s

Time = 629

smoothSolver:  Solving for Ux, Initial residual = 5.4766359e-09, Final residual = 5.4766359e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.500112e-09, Final residual = 4.500112e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001081859, Final residual = 9.2592667e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4494167e-05, Final residual = 1.1370939e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.7423732e-06, Final residual = 5.6007883e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.0400091e-06, Final residual = 5.5657939e-08, No Iterations 100
time step continuity errors : sum local = 4.1492652e-11, global = -5.9843312e-14, cumulative = -1.2192729e-08
ExecutionTime = 754.21 s  ClockTime = 757 s

Time = 630

smoothSolver:  Solving for Ux, Initial residual = 5.2814837e-09, Final residual = 5.2814837e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.3479331e-09, Final residual = 4.3479331e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010786034, Final residual = 9.4110204e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4620715e-05, Final residual = 1.2262031e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.8164769e-06, Final residual = 5.7516953e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.0387535e-06, Final residual = 5.5149601e-08, No Iterations 100
time step continuity errors : sum local = 4.0978738e-11, global = -1.7495707e-13, cumulative = -1.2192904e-08
ExecutionTime = 756.05 s  ClockTime = 759 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.161494e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 631

smoothSolver:  Solving for Ux, Initial residual = 5.5916846e-09, Final residual = 5.5916846e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.6137505e-09, Final residual = 4.6137505e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010760038, Final residual = 9.5722213e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4776701e-05, Final residual = 1.1417183e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.0123843e-06, Final residual = 5.7447022e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.8749136e-06, Final residual = 5.5084539e-08, No Iterations 100
time step continuity errors : sum local = 4.0977125e-11, global = -8.4670029e-14, cumulative = -1.2192989e-08
ExecutionTime = 757.85 s  ClockTime = 761 s

Time = 632

smoothSolver:  Solving for Ux, Initial residual = 5.6734431e-09, Final residual = 5.6734431e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.679012e-09, Final residual = 4.679012e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010756674, Final residual = 9.7085017e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5126707e-05, Final residual = 1.2385783e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.8834175e-06, Final residual = 5.6574847e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.0560836e-06, Final residual = 5.6023048e-08, No Iterations 100
time step continuity errors : sum local = 4.1368627e-11, global = 1.1583904e-13, cumulative = -1.2192873e-08
ExecutionTime = 759.69 s  ClockTime = 762 s

Time = 633

smoothSolver:  Solving for Ux, Initial residual = 5.284654e-09, Final residual = 5.284654e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.3620196e-09, Final residual = 4.3620196e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010761348, Final residual = 7.1201751e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5589937e-05, Final residual = 1.4103599e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.6758609e-06, Final residual = 5.6104593e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 3.1629071e-06, Final residual = 5.4496687e-08, No Iterations 100
time step continuity errors : sum local = 4.0678962e-11, global = -9.6388306e-14, cumulative = -1.219297e-08
ExecutionTime = 761.52 s  ClockTime = 764 s

Time = 634

smoothSolver:  Solving for Ux, Initial residual = 5.2398922e-09, Final residual = 5.2398922e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.3063659e-09, Final residual = 4.3063659e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010772994, Final residual = 9.9624045e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5568094e-05, Final residual = 1.2534676e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.5012602e-06, Final residual = 5.9027569e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.0962469e-06, Final residual = 5.56079e-08, No Iterations 100
time step continuity errors : sum local = 4.1310847e-11, global = -3.0135117e-13, cumulative = -1.2193271e-08
ExecutionTime = 763.3 s  ClockTime = 766 s

Time = 635

smoothSolver:  Solving for Ux, Initial residual = 6.1724828e-09, Final residual = 6.1724828e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.100775e-09, Final residual = 5.100775e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010786307, Final residual = 1.0091619e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5619629e-05, Final residual = 1.4739246e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.5517777e-06, Final residual = 6.3515234e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.1470462e-06, Final residual = 5.5261106e-08, No Iterations 100
time step continuity errors : sum local = 4.1219078e-11, global = -2.7680826e-13, cumulative = -1.2193548e-08
ExecutionTime = 765.14 s  ClockTime = 768 s

Time = 636

smoothSolver:  Solving for Ux, Initial residual = 6.6644076e-09, Final residual = 6.6644076e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.5307071e-09, Final residual = 5.5307071e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010803914, Final residual = 1.034208e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5595273e-05, Final residual = 1.3146538e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.6534563e-06, Final residual = 6.1848073e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.4338587e-06, Final residual = 5.5393479e-08, No Iterations 100
time step continuity errors : sum local = 4.1307818e-11, global = -2.0465394e-13, cumulative = -1.2193752e-08
ExecutionTime = 766.94 s  ClockTime = 770 s

Time = 637

smoothSolver:  Solving for Ux, Initial residual = 6.1312086e-09, Final residual = 6.1312086e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.0767415e-09, Final residual = 5.0767415e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010810641, Final residual = 8.2626914e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5814015e-05, Final residual = 1.4756386e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.2306202e-06, Final residual = 6.0219882e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 3.8602145e-06, Final residual = 5.5016236e-08, No Iterations 100
time step continuity errors : sum local = 4.0944427e-11, global = 8.9709864e-14, cumulative = -1.2193663e-08
ExecutionTime = 768.75 s  ClockTime = 772 s

Time = 638

smoothSolver:  Solving for Ux, Initial residual = 5.8908661e-09, Final residual = 5.8908661e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.8765358e-09, Final residual = 4.8765358e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010798166, Final residual = 1.0538242e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5550241e-05, Final residual = 1.1326664e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.5139951e-06, Final residual = 6.0895325e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.6853014e-06, Final residual = 5.5334872e-08, No Iterations 100
time step continuity errors : sum local = 4.1426286e-11, global = 9.9956909e-14, cumulative = -1.2193563e-08
ExecutionTime = 770.61 s  ClockTime = 773 s

Time = 639

smoothSolver:  Solving for Ux, Initial residual = 7.0594596e-09, Final residual = 7.0594596e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.8730633e-09, Final residual = 5.8730633e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010773134, Final residual = 1.0537218e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5243055e-05, Final residual = 1.1286042e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.3134677e-06, Final residual = 5.8571012e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.6656039e-06, Final residual = 5.5439082e-08, No Iterations 100
time step continuity errors : sum local = 4.1451179e-11, global = 1.6645288e-13, cumulative = -1.2193396e-08
ExecutionTime = 772.43 s  ClockTime = 775 s

Time = 640

smoothSolver:  Solving for Ux, Initial residual = 7.7018464e-09, Final residual = 7.7018464e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.4209049e-09, Final residual = 6.4209049e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010741113, Final residual = 1.0590766e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4936572e-05, Final residual = 1.4448295e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.0286713e-06, Final residual = 5.8027243e-08, No Iterations 8
GAMG:  Solving for p, Initial residual = 3.7065395e-06, Final residual = 5.4920824e-08, No Iterations 100
time step continuity errors : sum local = 4.1046045e-11, global = 2.8733406e-14, cumulative = -1.2193368e-08
ExecutionTime = 774.31 s  ClockTime = 777 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 641

smoothSolver:  Solving for Ux, Initial residual = 6.7901757e-09, Final residual = 6.7901757e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6317152e-09, Final residual = 5.6317152e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010719111, Final residual = 1.0661134e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4894074e-05, Final residual = 1.4831424e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.7578313e-06, Final residual = 5.6823831e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 3.4475161e-06, Final residual = 5.5353009e-08, No Iterations 100
time step continuity errors : sum local = 4.1113617e-11, global = 1.2142041e-13, cumulative = -1.2193246e-08
ExecutionTime = 776.31 s  ClockTime = 779 s

Time = 642

smoothSolver:  Solving for Ux, Initial residual = 6.3559626e-09, Final residual = 6.3559626e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.2532165e-09, Final residual = 5.2532165e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010688912, Final residual = 1.062898e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4914298e-05, Final residual = 9.349992e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.2249876e-06, Final residual = 5.6334311e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.3853906e-06, Final residual = 5.601004e-08, No Iterations 100
time step continuity errors : sum local = 4.1507614e-11, global = 8.7879686e-14, cumulative = -1.2193158e-08
ExecutionTime = 778.15 s  ClockTime = 781 s

Time = 643

smoothSolver:  Solving for Ux, Initial residual = 5.319565e-09, Final residual = 5.319565e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.3701837e-09, Final residual = 4.3701837e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010654535, Final residual = 1.0618243e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5082034e-05, Final residual = 1.3630269e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.6425242e-06, Final residual = 6.4643943e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2238992e-06, Final residual = 5.5354663e-08, No Iterations 100
time step continuity errors : sum local = 4.1349455e-11, global = 7.7333198e-14, cumulative = -1.2193081e-08
ExecutionTime = 779.94 s  ClockTime = 783 s

Time = 644

smoothSolver:  Solving for Ux, Initial residual = 5.1745688e-09, Final residual = 5.1745688e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.2557863e-09, Final residual = 4.2557863e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010614886, Final residual = 1.0299576e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5037803e-05, Final residual = 1.0424253e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.7433501e-06, Final residual = 6.4897853e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.1523241e-06, Final residual = 5.5251861e-08, No Iterations 100
time step continuity errors : sum local = 4.1050021e-11, global = 5.4787316e-14, cumulative = -1.2193026e-08
ExecutionTime = 781.75 s  ClockTime = 785 s

Time = 645

smoothSolver:  Solving for Ux, Initial residual = 5.4979192e-09, Final residual = 5.4979192e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.5384505e-09, Final residual = 4.5384505e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010593386, Final residual = 9.8187071e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4975543e-05, Final residual = 1.1061302e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.4333989e-06, Final residual = 6.232761e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.0358853e-06, Final residual = 5.5556596e-08, No Iterations 100
time step continuity errors : sum local = 4.1246428e-11, global = -7.6586206e-14, cumulative = -1.2193103e-08
ExecutionTime = 783.53 s  ClockTime = 786 s

Time = 646

smoothSolver:  Solving for Ux, Initial residual = 6.2999642e-09, Final residual = 6.2999642e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.2204097e-09, Final residual = 5.2204097e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010587455, Final residual = 9.5278822e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.509009e-05, Final residual = 1.1765089e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.1219161e-06, Final residual = 5.941197e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.3070705e-06, Final residual = 5.5633271e-08, No Iterations 100
time step continuity errors : sum local = 4.1333079e-11, global = -2.3690906e-13, cumulative = -1.219334e-08
ExecutionTime = 785.36 s  ClockTime = 788 s

Time = 647

smoothSolver:  Solving for Ux, Initial residual = 7.6907457e-09, Final residual = 7.6907457e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 6.3979214e-09, Final residual = 6.3979214e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010587192, Final residual = 9.4204705e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5013169e-05, Final residual = 1.2073019e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.1521903e-06, Final residual = 5.7936158e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.1254707e-06, Final residual = 5.4849767e-08, No Iterations 100
time step continuity errors : sum local = 4.0804663e-11, global = 1.7846558e-16, cumulative = -1.219334e-08
ExecutionTime = 787.18 s  ClockTime = 790 s

Time = 648

smoothSolver:  Solving for Ux, Initial residual = 6.44487e-09, Final residual = 6.44487e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.3336032e-09, Final residual = 5.3336032e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.000105909, Final residual = 9.3967602e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4773978e-05, Final residual = 1.2428861e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.0533205e-06, Final residual = 5.9147708e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.0225713e-06, Final residual = 5.5283686e-08, No Iterations 100
time step continuity errors : sum local = 4.135721e-11, global = -1.0925378e-13, cumulative = -1.2193449e-08
ExecutionTime = 788.98 s  ClockTime = 792 s

Time = 649

smoothSolver:  Solving for Ux, Initial residual = 5.8752622e-09, Final residual = 5.8752622e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.8356244e-09, Final residual = 4.8356244e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010580413, Final residual = 9.4752444e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4525508e-05, Final residual = 1.2470191e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.8599919e-06, Final residual = 5.7974443e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.0213997e-06, Final residual = 5.5263271e-08, No Iterations 100
time step continuity errors : sum local = 4.1014179e-11, global = -4.0758735e-13, cumulative = -1.2193856e-08
ExecutionTime = 790.8 s  ClockTime = 794 s

Time = 650

smoothSolver:  Solving for Ux, Initial residual = 6.8579829e-09, Final residual = 6.8579829e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.6957584e-09, Final residual = 5.6957584e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010557305, Final residual = 6.2323297e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4364882e-05, Final residual = 1.2196161e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.3050706e-06, Final residual = 5.5057848e-08, No Iterations 100
GAMG:  Solving for p, Initial residual = 3.0390501e-06, Final residual = 5.4508732e-08, No Iterations 100
time step continuity errors : sum local = 4.0624199e-11, global = 2.6265371e-13, cumulative = -1.2193594e-08
ExecutionTime = 794.24 s  ClockTime = 797 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 651

smoothSolver:  Solving for Ux, Initial residual = 6.1487231e-09, Final residual = 6.1487231e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.0993761e-09, Final residual = 5.0993761e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010520103, Final residual = 9.5670247e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4097283e-05, Final residual = 8.4665983e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.4818243e-06, Final residual = 5.4694857e-08, No Iterations 36
GAMG:  Solving for p, Initial residual = 3.0426936e-06, Final residual = 5.4881952e-08, No Iterations 100
time step continuity errors : sum local = 4.0917829e-11, global = 8.905729e-14, cumulative = -1.2193505e-08
ExecutionTime = 796.45 s  ClockTime = 799 s

Time = 652

smoothSolver:  Solving for Ux, Initial residual = 7.1981246e-09, Final residual = 7.1981246e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.9822298e-09, Final residual = 5.9822298e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010477626, Final residual = 9.2291428e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.39428e-05, Final residual = 1.148726e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.479538e-06, Final residual = 5.4615657e-08, No Iterations 11
GAMG:  Solving for p, Initial residual = 3.0244647e-06, Final residual = 5.5041766e-08, No Iterations 100
time step continuity errors : sum local = 4.0990242e-11, global = -9.7223069e-14, cumulative = -1.2193602e-08
ExecutionTime = 798.67 s  ClockTime = 802 s

Time = 653

smoothSolver:  Solving for Ux, Initial residual = 6.2039263e-09, Final residual = 6.2039263e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.1251536e-09, Final residual = 5.1251536e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010432767, Final residual = 8.9359913e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.3840104e-05, Final residual = 1.3160554e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.4981723e-06, Final residual = 5.4970201e-08, No Iterations 18
GAMG:  Solving for p, Initial residual = 2.9891588e-06, Final residual = 5.5268749e-08, No Iterations 100
time step continuity errors : sum local = 4.1252862e-11, global = -1.5123227e-13, cumulative = -1.2193753e-08
ExecutionTime = 800.71 s  ClockTime = 804 s

Time = 654

smoothSolver:  Solving for Ux, Initial residual = 4.9747642e-09, Final residual = 4.9747642e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.0823333e-09, Final residual = 4.0823333e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010389625, Final residual = 8.9122205e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.3859528e-05, Final residual = 1.0424432e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.4768512e-06, Final residual = 5.4476978e-08, No Iterations 11
GAMG:  Solving for p, Initial residual = 3.0027618e-06, Final residual = 5.5494172e-08, No Iterations 100
time step continuity errors : sum local = 4.1223385e-11, global = 2.9273174e-14, cumulative = -1.2193724e-08
ExecutionTime = 802.58 s  ClockTime = 806 s

Time = 655

smoothSolver:  Solving for Ux, Initial residual = 5.2358242e-09, Final residual = 5.2358242e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.321865e-09, Final residual = 4.321865e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010355325, Final residual = 9.0478829e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.3944565e-05, Final residual = 1.0558494e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.4859319e-06, Final residual = 5.4444621e-08, No Iterations 18
GAMG:  Solving for p, Initial residual = 3.0459486e-06, Final residual = 5.5319326e-08, No Iterations 100
time step continuity errors : sum local = 4.1196862e-11, global = -1.7513616e-13, cumulative = -1.2193899e-08
ExecutionTime = 804.56 s  ClockTime = 808 s

Time = 656

smoothSolver:  Solving for Ux, Initial residual = 5.3667801e-09, Final residual = 5.3667801e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.448236e-09, Final residual = 4.448236e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.000103271, Final residual = 9.1984069e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4072686e-05, Final residual = 9.0890411e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.6353916e-06, Final residual = 5.6031877e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 2.8779973e-06, Final residual = 5.5359905e-08, No Iterations 100
time step continuity errors : sum local = 4.1457816e-11, global = -2.5615527e-13, cumulative = -1.2194155e-08
ExecutionTime = 806.41 s  ClockTime = 809 s

Time = 657

smoothSolver:  Solving for Ux, Initial residual = 6.3277664e-09, Final residual = 6.3277664e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.2698385e-09, Final residual = 5.2698385e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010318449, Final residual = 9.3212244e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4337184e-05, Final residual = 9.1010116e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.7143439e-06, Final residual = 5.6537777e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 2.8182858e-06, Final residual = 5.4881113e-08, No Iterations 100
time step continuity errors : sum local = 4.1036941e-11, global = -8.6960613e-14, cumulative = -1.2194242e-08
ExecutionTime = 808.28 s  ClockTime = 811 s

Time = 658

smoothSolver:  Solving for Ux, Initial residual = 5.7803401e-09, Final residual = 5.7803401e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.7888914e-09, Final residual = 4.7888914e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010317529, Final residual = 9.4092701e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4626371e-05, Final residual = 9.4632007e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.7704863e-06, Final residual = 5.7666272e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.8429625e-06, Final residual = 5.5233002e-08, No Iterations 100
time step continuity errors : sum local = 4.1184276e-11, global = 1.8585637e-13, cumulative = -1.2194056e-08
ExecutionTime = 810.12 s  ClockTime = 813 s

Time = 659

smoothSolver:  Solving for Ux, Initial residual = 5.5922354e-09, Final residual = 5.5922354e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.6369928e-09, Final residual = 4.6369928e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010324955, Final residual = 9.4982931e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4836273e-05, Final residual = 1.1835753e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.1619504e-06, Final residual = 5.7397215e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.0051328e-06, Final residual = 5.523394e-08, No Iterations 100
time step continuity errors : sum local = 4.1347116e-11, global = -3.786748e-14, cumulative = -1.2194094e-08
ExecutionTime = 811.94 s  ClockTime = 815 s

Time = 660

smoothSolver:  Solving for Ux, Initial residual = 5.6969982e-09, Final residual = 5.6969982e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.7198449e-09, Final residual = 4.7198449e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010331403, Final residual = 7.192836e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5039207e-05, Final residual = 1.0597097e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.8212678e-06, Final residual = 5.7425659e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.9904427e-06, Final residual = 5.5399862e-08, No Iterations 100
time step continuity errors : sum local = 4.1426804e-11, global = 2.3111255e-13, cumulative = -1.2193863e-08
ExecutionTime = 813.73 s  ClockTime = 817 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 661

smoothSolver:  Solving for Ux, Initial residual = 6.9586778e-09, Final residual = 6.9586778e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.7958561e-09, Final residual = 5.7958561e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010343321, Final residual = 7.8091717e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.496512e-05, Final residual = 1.357401e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.0344127e-06, Final residual = 5.8434751e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.178477e-06, Final residual = 5.5097328e-08, No Iterations 100
time step continuity errors : sum local = 4.1144079e-11, global = 8.1189149e-14, cumulative = -1.2193782e-08
ExecutionTime = 815.55 s  ClockTime = 819 s

Time = 662

smoothSolver:  Solving for Ux, Initial residual = 6.3572439e-09, Final residual = 6.3572439e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.2755173e-09, Final residual = 5.2755173e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010350199, Final residual = 9.9267157e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4886459e-05, Final residual = 1.2812992e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.3022401e-06, Final residual = 6.2159572e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.5228946e-06, Final residual = 5.5071063e-08, No Iterations 100
time step continuity errors : sum local = 4.1032297e-11, global = 1.5159889e-14, cumulative = -1.2193767e-08
ExecutionTime = 817.35 s  ClockTime = 820 s

Time = 663

smoothSolver:  Solving for Ux, Initial residual = 5.3025325e-09, Final residual = 5.3025325e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.3789951e-09, Final residual = 4.3789951e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010341195, Final residual = 9.941934e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4841633e-05, Final residual = 1.4734188e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.2027292e-06, Final residual = 5.9876526e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 3.5906508e-06, Final residual = 5.5070523e-08, No Iterations 100
time step continuity errors : sum local = 4.0986832e-11, global = 1.7254877e-13, cumulative = -1.2193594e-08
ExecutionTime = 819.16 s  ClockTime = 822 s

Time = 664

smoothSolver:  Solving for Ux, Initial residual = 5.355096e-09, Final residual = 5.355096e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.4159025e-09, Final residual = 4.4159025e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010318118, Final residual = 7.763109e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4602998e-05, Final residual = 1.2440618e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.9143631e-06, Final residual = 5.8878228e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 3.6006876e-06, Final residual = 5.4775347e-08, No Iterations 100
time step continuity errors : sum local = 4.0960903e-11, global = -5.3911279e-14, cumulative = -1.2193648e-08
ExecutionTime = 821 s  ClockTime = 824 s

Time = 665

smoothSolver:  Solving for Ux, Initial residual = 5.4602124e-09, Final residual = 5.4602124e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.5201382e-09, Final residual = 4.5201382e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010285627, Final residual = 9.9558013e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4248561e-05, Final residual = 9.7715514e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.858776e-06, Final residual = 5.6987443e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 3.4734067e-06, Final residual = 5.5300009e-08, No Iterations 100
time step continuity errors : sum local = 4.1231432e-11, global = 1.8600185e-13, cumulative = -1.2193462e-08
ExecutionTime = 822.83 s  ClockTime = 826 s

Time = 666

smoothSolver:  Solving for Ux, Initial residual = 4.9881725e-09, Final residual = 4.9881725e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.1292384e-09, Final residual = 4.1292384e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010262633, Final residual = 1.0015199e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4200929e-05, Final residual = 1.3903144e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.6651977e-06, Final residual = 5.6533382e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 3.2360348e-06, Final residual = 5.4992922e-08, No Iterations 100
time step continuity errors : sum local = 4.0867195e-11, global = -1.0732774e-13, cumulative = -1.2193569e-08
ExecutionTime = 824.65 s  ClockTime = 828 s

Time = 667

smoothSolver:  Solving for Ux, Initial residual = 6.1098001e-09, Final residual = 6.1098001e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.0666978e-09, Final residual = 5.0666978e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010234106, Final residual = 9.9993867e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4186916e-05, Final residual = 1.1413173e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.8992158e-06, Final residual = 5.7874059e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.0438893e-06, Final residual = 5.5556606e-08, No Iterations 100
time step continuity errors : sum local = 4.1592176e-11, global = 1.4357481e-13, cumulative = -1.2193426e-08
ExecutionTime = 826.45 s  ClockTime = 829 s

Time = 668

smoothSolver:  Solving for Ux, Initial residual = 5.2224762e-09, Final residual = 5.2224762e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.3026863e-09, Final residual = 4.3026863e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.0001019945, Final residual = 9.9934231e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.43339e-05, Final residual = 1.1790652e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.2189543e-06, Final residual = 5.9836357e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.0504342e-06, Final residual = 5.5444205e-08, No Iterations 100
time step continuity errors : sum local = 4.1370179e-11, global = 1.3324531e-13, cumulative = -1.2193293e-08
ExecutionTime = 828.25 s  ClockTime = 831 s

Time = 669

smoothSolver:  Solving for Ux, Initial residual = 4.7949533e-09, Final residual = 4.7949533e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 3.9559469e-09, Final residual = 3.9559469e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010160606, Final residual = 7.319389e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.436319e-05, Final residual = 1.4288247e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.8499269e-06, Final residual = 5.8215466e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.0708889e-06, Final residual = 5.5324912e-08, No Iterations 100
time step continuity errors : sum local = 4.1311822e-11, global = 1.1979388e-13, cumulative = -1.2193173e-08
ExecutionTime = 830.07 s  ClockTime = 833 s

Time = 670

smoothSolver:  Solving for Ux, Initial residual = 5.1050176e-09, Final residual = 5.1050176e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.2247365e-09, Final residual = 4.2247365e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010135564, Final residual = 9.2733085e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.423852e-05, Final residual = 1.0583642e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.0394925e-06, Final residual = 5.7748858e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 2.9018715e-06, Final residual = 5.5713744e-08, No Iterations 100
time step continuity errors : sum local = 4.1587623e-11, global = 1.6408839e-13, cumulative = -1.2193009e-08
ExecutionTime = 831.91 s  ClockTime = 835 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 1.1305955e-12

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 1.1614941e-12

surfaceFieldValue flowRateAC write:
    sum(ac_inlet) of phi = -1.1460448e-12

surfaceFieldValue flowRateAC_left write:
    sum(ac_inlet_left) of phi = -1.1460448e-12

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0098909

Time = 671

smoothSolver:  Solving for Ux, Initial residual = 5.3362979e-09, Final residual = 5.3362979e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.4257293e-09, Final residual = 4.4257293e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010127095, Final residual = 8.9706101e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4378035e-05, Final residual = 9.103512e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.9276067e-06, Final residual = 5.8517595e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.8912436e-06, Final residual = 5.5229746e-08, No Iterations 100
time step continuity errors : sum local = 4.1282935e-11, global = 3.7805644e-14, cumulative = -1.2192971e-08
ExecutionTime = 833.71 s  ClockTime = 837 s

Time = 672

smoothSolver:  Solving for Ux, Initial residual = 4.9915802e-09, Final residual = 4.9915802e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.1227617e-09, Final residual = 4.1227617e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010121955, Final residual = 6.8264122e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.453017e-05, Final residual = 9.0360758e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.3945284e-06, Final residual = 5.5370396e-08, No Iterations 100
GAMG:  Solving for p, Initial residual = 3.0081403e-06, Final residual = 5.5658705e-08, No Iterations 100
time step continuity errors : sum local = 4.140191e-11, global = -2.2870956e-13, cumulative = -1.21932e-08
ExecutionTime = 836.76 s  ClockTime = 840 s

Time = 673

smoothSolver:  Solving for Ux, Initial residual = 6.1220322e-09, Final residual = 6.1220322e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 5.07895e-09, Final residual = 5.07895e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010125139, Final residual = 8.8161715e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.413856e-05, Final residual = 1.1747288e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.7275071e-06, Final residual = 5.5631098e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 2.8871172e-06, Final residual = 5.5111957e-08, No Iterations 100
time step continuity errors : sum local = 4.1298985e-11, global = 2.3974624e-14, cumulative = -1.2193176e-08
ExecutionTime = 838.62 s  ClockTime = 842 s

Time = 674

smoothSolver:  Solving for Ux, Initial residual = 5.6920352e-09, Final residual = 5.6920352e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.7101303e-09, Final residual = 4.7101303e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010118769, Final residual = 8.8925548e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.3913199e-05, Final residual = 1.164593e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.4783673e-06, Final residual = 5.4696958e-08, No Iterations 9
GAMG:  Solving for p, Initial residual = 2.9733623e-06, Final residual = 5.4935645e-08, No Iterations 100
time step continuity errors : sum local = 4.0921308e-11, global = -9.0610085e-15, cumulative = -1.2193185e-08
ExecutionTime = 840.98 s  ClockTime = 844 s

Time = 675

smoothSolver:  Solving for Ux, Initial residual = 5.2936903e-09, Final residual = 5.2936903e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.3706721e-09, Final residual = 4.3706721e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010099554, Final residual = 9.0138246e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.3714978e-05, Final residual = 1.0816361e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.4342018e-06, Final residual = 5.4211763e-08, No Iterations 59
GAMG:  Solving for p, Initial residual = 2.8821883e-06, Final residual = 5.5164206e-08, No Iterations 100
time step continuity errors : sum local = 4.1230489e-11, global = -1.3511969e-13, cumulative = -1.219332e-08
ExecutionTime = 843.56 s  ClockTime = 847 s

Time = 676

smoothSolver:  Solving for Ux, Initial residual = 5.5486729e-09, Final residual = 5.5486729e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.5900261e-09, Final residual = 4.5900261e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010066376, Final residual = 9.0074869e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.3522675e-05, Final residual = 8.7649377e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.2854564e-06, Final residual = 5.4885512e-08, No Iterations 100
GAMG:  Solving for p, Initial residual = 2.8967355e-06, Final residual = 5.5350589e-08, No Iterations 100
time step continuity errors : sum local = 4.1050358e-11, global = -9.3097079e-14, cumulative = -1.2193413e-08
ExecutionTime = 847 s  ClockTime = 850 s

Time = 677

smoothSolver:  Solving for Ux, Initial residual = 5.3021636e-09, Final residual = 5.3021636e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.3761618e-09, Final residual = 4.3761618e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 0.00010032334, Final residual = 8.8351697e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.3348562e-05, Final residual = 1.1681777e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.2535934e-06, Final residual = 5.5576452e-08, No Iterations 100
GAMG:  Solving for p, Initial residual = 2.8631515e-06, Final residual = 5.4277697e-08, No Iterations 100
time step continuity errors : sum local = 4.0515309e-11, global = -2.3552569e-13, cumulative = -1.2193648e-08
ExecutionTime = 850.54 s  ClockTime = 853 s

Time = 678

smoothSolver:  Solving for Ux, Initial residual = 5.8009782e-09, Final residual = 5.8009782e-09, No Iterations 0
smoothSolver:  Solving for Uy, Initial residual = 4.8068021e-09, Final residual = 4.8068021e-09, No Iterations 0
GAMG:  Solving for p, Initial residual = 9.993572e-05, Final residual = 5.4818892e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.3260516e-05, Final residual = 1.2062593e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.8335762e-06, Final residual = 5.4492937e-08, No Iterations 100
GAMG:  Solving for p, Initial residual = 3.0025921e-06, Final residual = 5.5028706e-08, No Iterations 100
time step continuity errors : sum local = 4.1091243e-11, global = -2.9935717e-14, cumulative = -1.2193678e-08
ExecutionTime = 853.55 s  ClockTime = 857 s


SIMPLE solution converged in 678 iterations

End

