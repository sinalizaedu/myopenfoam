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
Date   : Jul 18 2026
Time   : 01:22:09
Host   : 82703a17521a
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


surfaceFieldValue pressureACinlet:
    operation     = areaAverage


Time = 1

smoothSolver:  Solving for Ux, Initial residual = 1, Final residual = 9.1650873e-09, No Iterations 10
smoothSolver:  Solving for Uy, Initial residual = 0.99999998, Final residual = 9.1650903e-09, No Iterations 10
GAMG:  Solving for p, Initial residual = 0.99999995, Final residual = 0.0039781712, No Iterations 51
GAMG:  Solving for p, Initial residual = 0.78954235, Final residual = 0.0074302232, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.10673288, Final residual = 0.00091138614, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.071619961, Final residual = 0.00020635198, No Iterations 22
time step continuity errors : sum local = 2.69623e-05, global = -1.1185744e-08, cumulative = -1.1185744e-08
ExecutionTime = 9.81 s  ClockTime = 10 s

Time = 2

smoothSolver:  Solving for Ux, Initial residual = 0.2760476, Final residual = 4.7976123e-09, No Iterations 7
smoothSolver:  Solving for Uy, Initial residual = 0.094434848, Final residual = 6.90483e-09, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.20652064, Final residual = 0.00061171748, No Iterations 29
GAMG:  Solving for p, Initial residual = 0.35487768, Final residual = 0.0032646958, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.069772662, Final residual = 0.00055325969, No Iterations 10
GAMG:  Solving for p, Initial residual = 0.045290858, Final residual = 0.00038309757, No Iterations 4
time step continuity errors : sum local = 3.6415538e-05, global = -1.0956259e-07, cumulative = -1.2074833e-07
ExecutionTime = 10.9 s  ClockTime = 11 s

Time = 3

smoothSolver:  Solving for Ux, Initial residual = 0.1787798, Final residual = 2.982426e-09, No Iterations 7
smoothSolver:  Solving for Uy, Initial residual = 0.050942689, Final residual = 3.5657557e-09, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.22805469, Final residual = 0.001937726, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.204603, Final residual = 0.0017953138, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.048360578, Final residual = 0.00017165794, No Iterations 20
GAMG:  Solving for p, Initial residual = 0.045352017, Final residual = 0.00033098414, No Iterations 3
time step continuity errors : sum local = 1.5756863e-05, global = -2.0578191e-07, cumulative = -3.2653025e-07
ExecutionTime = 11.76 s  ClockTime = 12 s

Time = 4

smoothSolver:  Solving for Ux, Initial residual = 0.11954739, Final residual = 8.9143948e-09, No Iterations 6
smoothSolver:  Solving for Uy, Initial residual = 0.031277, Final residual = 9.7965683e-09, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.2356774, Final residual = 0.0019450134, No Iterations 13
GAMG:  Solving for p, Initial residual = 0.51796711, Final residual = 0.0049210159, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.13302631, Final residual = 0.00051831697, No Iterations 11
GAMG:  Solving for p, Initial residual = 0.10621746, Final residual = 0.00055894951, No Iterations 3
time step continuity errors : sum local = 2.6872347e-05, global = -3.4662653e-09, cumulative = -3.2999651e-07
ExecutionTime = 12.59 s  ClockTime = 12 s

Time = 5

smoothSolver:  Solving for Ux, Initial residual = 0.08012739, Final residual = 3.8633472e-09, No Iterations 6
smoothSolver:  Solving for Uy, Initial residual = 0.019122595, Final residual = 3.9293039e-09, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.22348451, Final residual = 0.00093016982, No Iterations 25
GAMG:  Solving for p, Initial residual = 0.65339031, Final residual = 0.0055512311, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.13405714, Final residual = 0.0011138683, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.070897944, Final residual = 0.0004781633, No Iterations 10
time step continuity errors : sum local = 2.9553801e-05, global = 3.4751127e-08, cumulative = -2.9524538e-07
ExecutionTime = 13.65 s  ClockTime = 13 s

Time = 6

smoothSolver:  Solving for Ux, Initial residual = 0.047898917, Final residual = 3.3646241e-09, No Iterations 5
smoothSolver:  Solving for Uy, Initial residual = 0.010433046, Final residual = 4.0237992e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.25528186, Final residual = 0.0014670777, No Iterations 18
GAMG:  Solving for p, Initial residual = 0.61671603, Final residual = 0.0043144754, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.10641113, Final residual = 0.0010547395, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0557885, Final residual = 0.00027446373, No Iterations 13
time step continuity errors : sum local = 1.5756174e-05, global = 2.4195335e-08, cumulative = -2.7105005e-07
ExecutionTime = 14.58 s  ClockTime = 14 s

Time = 7

smoothSolver:  Solving for Ux, Initial residual = 0.017459602, Final residual = 3.1883947e-09, No Iterations 6
smoothSolver:  Solving for Uy, Initial residual = 0.0040512181, Final residual = 3.0438626e-09, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.31459087, Final residual = 0.001948317, No Iterations 16
GAMG:  Solving for p, Initial residual = 0.27634467, Final residual = 0.0019231442, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.058259643, Final residual = 0.00053860213, No Iterations 16
GAMG:  Solving for p, Initial residual = 0.058263306, Final residual = 0.00050328148, No Iterations 3
time step continuity errors : sum local = 2.0170194e-05, global = 4.6090802e-08, cumulative = -2.2495925e-07
ExecutionTime = 15.56 s  ClockTime = 15 s

Time = 8

smoothSolver:  Solving for Ux, Initial residual = 0.01271202, Final residual = 4.0600905e-09, No Iterations 6
smoothSolver:  Solving for Uy, Initial residual = 0.0031756726, Final residual = 4.1563909e-09, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.33961874, Final residual = 0.0028711549, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.2847031, Final residual = 0.0024120107, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.07010762, Final residual = 0.00045720493, No Iterations 12
GAMG:  Solving for p, Initial residual = 0.065397868, Final residual = 0.00052257973, No Iterations 6
time step continuity errors : sum local = 1.1654744e-05, global = 7.7073696e-09, cumulative = -2.1725188e-07
ExecutionTime = 16.34 s  ClockTime = 16 s

Time = 9

smoothSolver:  Solving for Ux, Initial residual = 0.023776596, Final residual = 3.3526704e-09, No Iterations 6
smoothSolver:  Solving for Uy, Initial residual = 0.0061222794, Final residual = 3.5942586e-09, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.3462319, Final residual = 0.0013065119, No Iterations 9
GAMG:  Solving for p, Initial residual = 0.52584254, Final residual = 0.0042472032, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.12938406, Final residual = 0.0012400783, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.058510334, Final residual = 0.0004804044, No Iterations 20
time step continuity errors : sum local = 1.3963815e-05, global = 1.6425418e-08, cumulative = -2.0082646e-07
ExecutionTime = 17.39 s  ClockTime = 17 s

Time = 10

smoothSolver:  Solving for Ux, Initial residual = 0.03032498, Final residual = 8.2799674e-09, No Iterations 5
smoothSolver:  Solving for Uy, Initial residual = 0.0076905998, Final residual = 8.9374166e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.32040537, Final residual = 0.0014148146, No Iterations 16
GAMG:  Solving for p, Initial residual = 0.56314809, Final residual = 0.0035493452, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.11390659, Final residual = 0.0010234842, No Iterations 11
GAMG:  Solving for p, Initial residual = 0.067232959, Final residual = 0.00063272179, No Iterations 2
time step continuity errors : sum local = 2.3395074e-05, global = 4.8863433e-08, cumulative = -1.5196303e-07
ExecutionTime = 18.31 s  ClockTime = 18 s

surfaceFieldValue flowRateTM write:
    total faces   = 4
    total area    = 3.471311e-07

    sum(outlet_tm) of phi = 2.4659644e-11

surfaceFieldValue flowRateTM_left write:
    total faces   = 5
    total area    = 3.471311e-07

    sum(outlet_tm_left) of phi = 2.5347505e-11

surfaceFieldValue pressureACinlet write:
    total faces   = 7
    total area    = 5.1623638e-07

    areaAverage(ac_inlet) of p = 1.8243533

Time = 11

smoothSolver:  Solving for Ux, Initial residual = 0.029837069, Final residual = 5.0938284e-09, No Iterations 5
smoothSolver:  Solving for Uy, Initial residual = 0.007077663, Final residual = 5.3712597e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.2485683, Final residual = 0.001158385, No Iterations 19
GAMG:  Solving for p, Initial residual = 0.44384746, Final residual = 0.0040857535, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.080107982, Final residual = 0.00068737492, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.044456456, Final residual = 0.00038050569, No Iterations 10
time step continuity errors : sum local = 1.2920527e-05, global = -2.3491653e-09, cumulative = -1.5431219e-07
ExecutionTime = 19.27 s  ClockTime = 19 s

Time = 12

smoothSolver:  Solving for Ux, Initial residual = 0.01920607, Final residual = 2.4427278e-09, No Iterations 6
smoothSolver:  Solving for Uy, Initial residual = 0.0047986581, Final residual = 2.5456373e-09, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.22078465, Final residual = 0.0021945397, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.13215255, Final residual = 0.0012844356, No Iterations 23
GAMG:  Solving for p, Initial residual = 0.088050371, Final residual = 0.0005612905, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.025155392, Final residual = 0.00025000294, No Iterations 14
time step continuity errors : sum local = 6.4575474e-06, global = -3.5599794e-09, cumulative = -1.5787217e-07
ExecutionTime = 20.35 s  ClockTime = 20 s

Time = 13

smoothSolver:  Solving for Ux, Initial residual = 0.0084014461, Final residual = 2.6246479e-09, No Iterations 6
smoothSolver:  Solving for Uy, Initial residual = 0.0022455043, Final residual = 2.9147852e-09, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.22183122, Final residual = 0.0021090058, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.23591113, Final residual = 0.0013251619, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.056188263, Final residual = 0.00032624613, No Iterations 13
GAMG:  Solving for p, Initial residual = 0.042410057, Final residual = 0.00030780308, No Iterations 3
time step continuity errors : sum local = 6.3857875e-06, global = 1.4547063e-08, cumulative = -1.4332511e-07
ExecutionTime = 21.17 s  ClockTime = 21 s

Time = 14

smoothSolver:  Solving for Ux, Initial residual = 0.0050669003, Final residual = 9.4754146e-09, No Iterations 5
smoothSolver:  Solving for Uy, Initial residual = 0.0012996958, Final residual = 2.0250791e-09, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.1998093, Final residual = 0.0013280447, No Iterations 8
GAMG:  Solving for p, Initial residual = 0.34332088, Final residual = 0.0031738497, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.079128104, Final residual = 0.0006360746, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.044754987, Final residual = 0.0003457649, No Iterations 4
time step continuity errors : sum local = 8.6848396e-06, global = -4.0957936e-09, cumulative = -1.474209e-07
ExecutionTime = 21.88 s  ClockTime = 22 s

Time = 15

smoothSolver:  Solving for Ux, Initial residual = 0.0080870846, Final residual = 3.4242249e-09, No Iterations 5
smoothSolver:  Solving for Uy, Initial residual = 0.0019514349, Final residual = 4.2054281e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.14912132, Final residual = 0.0013168918, No Iterations 9
GAMG:  Solving for p, Initial residual = 0.33221524, Final residual = 0.0021766779, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.074367788, Final residual = 0.00063356681, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.033933316, Final residual = 0.0002341387, No Iterations 11
time step continuity errors : sum local = 6.2701045e-06, global = -1.0680839e-09, cumulative = -1.4848898e-07
ExecutionTime = 22.7 s  ClockTime = 23 s

Time = 16

smoothSolver:  Solving for Ux, Initial residual = 0.0099166548, Final residual = 3.5771521e-09, No Iterations 5
smoothSolver:  Solving for Uy, Initial residual = 0.0021999969, Final residual = 3.6904488e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.11900289, Final residual = 0.0009573722, No Iterations 25
GAMG:  Solving for p, Initial residual = 0.23602779, Final residual = 0.00093800514, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.051983174, Final residual = 0.00048873335, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.025674179, Final residual = 0.00025051093, No Iterations 3
time step continuity errors : sum local = 5.9151599e-06, global = 4.4982938e-09, cumulative = -1.4399069e-07
ExecutionTime = 23.62 s  ClockTime = 23 s

Time = 17

smoothSolver:  Solving for Ux, Initial residual = 0.0087351777, Final residual = 6.5474407e-09, No Iterations 5
smoothSolver:  Solving for Uy, Initial residual = 0.0019297192, Final residual = 5.8435472e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.13829193, Final residual = 0.0011289677, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.08107013, Final residual = 0.00078531674, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.024137282, Final residual = 9.9584076e-05, No Iterations 25
GAMG:  Solving for p, Initial residual = 0.041494343, Final residual = 0.00024053143, No Iterations 3
time step continuity errors : sum local = 4.5352655e-06, global = 9.0985021e-09, cumulative = -1.3489219e-07
ExecutionTime = 24.58 s  ClockTime = 24 s

Time = 18

smoothSolver:  Solving for Ux, Initial residual = 0.0058931219, Final residual = 6.3561445e-09, No Iterations 5
smoothSolver:  Solving for Uy, Initial residual = 0.0014032135, Final residual = 5.9587777e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.14701424, Final residual = 0.001329379, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.16936081, Final residual = 0.0013798331, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.03987013, Final residual = 0.00023040334, No Iterations 17
GAMG:  Solving for p, Initial residual = 0.037540866, Final residual = 0.00021547798, No Iterations 3
time step continuity errors : sum local = 3.7502892e-06, global = -1.6783567e-08, cumulative = -1.5167576e-07
ExecutionTime = 25.41 s  ClockTime = 25 s

Time = 19

smoothSolver:  Solving for Ux, Initial residual = 0.0032936396, Final residual = 4.0559889e-09, No Iterations 5
smoothSolver:  Solving for Uy, Initial residual = 0.00085300395, Final residual = 3.973349e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.12823716, Final residual = 0.00065324012, No Iterations 8
GAMG:  Solving for p, Initial residual = 0.23164652, Final residual = 0.0020352245, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.054409256, Final residual = 0.0004137409, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.031585997, Final residual = 0.00021016083, No Iterations 3
time step continuity errors : sum local = 3.9977564e-06, global = 1.7020615e-08, cumulative = -1.3465514e-07
ExecutionTime = 26.1 s  ClockTime = 26 s

Time = 20

smoothSolver:  Solving for Ux, Initial residual = 0.0020670607, Final residual = 6.9165801e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 0.00053984213, Final residual = 8.9221433e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.091148822, Final residual = 0.00044159308, No Iterations 9
GAMG:  Solving for p, Initial residual = 0.20955665, Final residual = 0.0019130646, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.047438405, Final residual = 0.00038056496, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.028568235, Final residual = 0.00021223019, No Iterations 3
time step continuity errors : sum local = 4.0967491e-06, global = 3.4601864e-09, cumulative = -1.3119495e-07
ExecutionTime = 26.81 s  ClockTime = 27 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4650313e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5350193e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.011947

Time = 21

smoothSolver:  Solving for Ux, Initial residual = 0.0024201124, Final residual = 2.3384065e-09, No Iterations 5
smoothSolver:  Solving for Uy, Initial residual = 0.00056621876, Final residual = 2.3129896e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.076482574, Final residual = 0.0005915885, No Iterations 20
GAMG:  Solving for p, Initial residual = 0.13294427, Final residual = 0.0013202744, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.031011052, Final residual = 0.00023363193, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.018316276, Final residual = 0.0001391377, No Iterations 3
time step continuity errors : sum local = 2.5008369e-06, global = -1.2677819e-08, cumulative = -1.4387277e-07
ExecutionTime = 27.65 s  ClockTime = 27 s

Time = 22

smoothSolver:  Solving for Ux, Initial residual = 0.0027323069, Final residual = 3.4403175e-09, No Iterations 5
smoothSolver:  Solving for Uy, Initial residual = 0.00064538155, Final residual = 3.2910713e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.084939928, Final residual = 0.00073401234, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.06146126, Final residual = 0.00057523896, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.022119966, Final residual = 0.0002115258, No Iterations 19
GAMG:  Solving for p, Initial residual = 0.020366597, Final residual = 0.00013119474, No Iterations 3
time step continuity errors : sum local = 2.1390523e-06, global = -1.3689795e-08, cumulative = -1.5756257e-07
ExecutionTime = 28.61 s  ClockTime = 28 s

Time = 23

smoothSolver:  Solving for Ux, Initial residual = 0.0025262718, Final residual = 3.1591969e-09, No Iterations 5
smoothSolver:  Solving for Uy, Initial residual = 0.00060320001, Final residual = 3.2343133e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.084241536, Final residual = 0.00058251411, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.10872471, Final residual = 0.0010450106, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.024342428, Final residual = 0.00019594197, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.018652281, Final residual = 0.00014395212, No Iterations 3
time step continuity errors : sum local = 2.3331796e-06, global = -8.0833278e-09, cumulative = -1.656459e-07
ExecutionTime = 29.33 s  ClockTime = 29 s

Time = 24

smoothSolver:  Solving for Ux, Initial residual = 0.0019414399, Final residual = 9.8322125e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 0.00046828125, Final residual = 2.0776533e-09, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.068721328, Final residual = 0.00065082762, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.12415803, Final residual = 0.0011634844, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.029626135, Final residual = 0.00021255226, No Iterations 8
GAMG:  Solving for p, Initial residual = 0.020819581, Final residual = 0.00016599192, No Iterations 3
time step continuity errors : sum local = 2.7996706e-06, global = -7.9797638e-09, cumulative = -1.7362566e-07
ExecutionTime = 30.06 s  ClockTime = 30 s

Time = 25

smoothSolver:  Solving for Ux, Initial residual = 0.0013318759, Final residual = 3.8869649e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 0.00032887962, Final residual = 6.3622416e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.049532941, Final residual = 0.00033087113, No Iterations 8
GAMG:  Solving for p, Initial residual = 0.10455711, Final residual = 0.0009749936, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.024510826, Final residual = 0.00019816828, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.014889761, Final residual = 0.00010404772, No Iterations 4
time step continuity errors : sum local = 1.7596322e-06, global = -1.7258238e-09, cumulative = -1.7535148e-07
ExecutionTime = 30.91 s  ClockTime = 31 s

Time = 26

smoothSolver:  Solving for Ux, Initial residual = 0.00090839692, Final residual = 6.4884865e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 0.00023376086, Final residual = 7.5352152e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.045651947, Final residual = 0.00044613481, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.055517041, Final residual = 0.00026864477, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.015236464, Final residual = 0.00011433766, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.0091729488, Final residual = 5.3465181e-05, No Iterations 3
time step continuity errors : sum local = 8.7187173e-07, global = -5.8215747e-09, cumulative = -1.8117306e-07
ExecutionTime = 31.69 s  ClockTime = 32 s

Time = 27

smoothSolver:  Solving for Ux, Initial residual = 0.00080315853, Final residual = 8.9493132e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 0.00019188168, Final residual = 8.5910795e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.050623331, Final residual = 0.00040277161, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.035321389, Final residual = 0.00022687331, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0092643188, Final residual = 6.0584987e-05, No Iterations 15
GAMG:  Solving for p, Initial residual = 0.0080353275, Final residual = 3.0951503e-05, No Iterations 7
time step continuity errors : sum local = 4.8639934e-07, global = -4.3081703e-10, cumulative = -1.8160387e-07
ExecutionTime = 32.6 s  ClockTime = 32 s

Time = 28

smoothSolver:  Solving for Ux, Initial residual = 0.00081223494, Final residual = 7.7635352e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 0.0001880782, Final residual = 7.1840269e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.049200566, Final residual = 0.00029518365, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.055100295, Final residual = 0.00029021712, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.013509913, Final residual = 0.00010507618, No Iterations 16
GAMG:  Solving for p, Initial residual = 0.0093251814, Final residual = 8.2839061e-05, No Iterations 3
time step continuity errors : sum local = 1.3052337e-06, global = -4.6060392e-10, cumulative = -1.8206448e-07
ExecutionTime = 33.52 s  ClockTime = 33 s

Time = 29

smoothSolver:  Solving for Ux, Initial residual = 0.00076613185, Final residual = 4.2652068e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 0.00017609542, Final residual = 4.1909602e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.039890649, Final residual = 0.00029457523, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.060101954, Final residual = 0.0005446922, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.014609415, Final residual = 6.3295063e-05, No Iterations 10
GAMG:  Solving for p, Initial residual = 0.010780847, Final residual = 8.277738e-05, No Iterations 9
time step continuity errors : sum local = 1.3204518e-06, global = 3.2201532e-10, cumulative = -1.8174246e-07
ExecutionTime = 34.74 s  ClockTime = 35 s

Time = 30

smoothSolver:  Solving for Ux, Initial residual = 0.00065091761, Final residual = 2.3258533e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 0.00014532998, Final residual = 2.8151782e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.030510343, Final residual = 0.00010736972, No Iterations 8
GAMG:  Solving for p, Initial residual = 0.052054187, Final residual = 0.00045118993, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.012301906, Final residual = 0.00010573667, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0071362079, Final residual = 5.8102908e-05, No Iterations 4
time step continuity errors : sum local = 9.2648785e-07, global = 7.6791817e-10, cumulative = -1.8097455e-07
ExecutionTime = 35.91 s  ClockTime = 36 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.466786e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5332253e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0153813

Time = 31

smoothSolver:  Solving for Ux, Initial residual = 0.00050756026, Final residual = 3.7141078e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 0.00011050918, Final residual = 3.5571108e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.028319892, Final residual = 0.00024783377, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.029037663, Final residual = 0.00013441035, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0079332143, Final residual = 7.5869968e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0038110112, Final residual = 2.0066094e-05, No Iterations 5
time step continuity errors : sum local = 3.1474305e-07, global = 1.8428152e-10, cumulative = -1.8079026e-07
ExecutionTime = 36.86 s  ClockTime = 37 s

Time = 32

smoothSolver:  Solving for Ux, Initial residual = 0.00037158742, Final residual = 4.6270351e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 8.6453573e-05, Final residual = 4.1329976e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.029590602, Final residual = 0.00025032912, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.020387688, Final residual = 0.00012591805, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0055255769, Final residual = 1.9340745e-05, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.0031953926, Final residual = 1.7369468e-05, No Iterations 3
time step continuity errors : sum local = 2.6860762e-07, global = 5.8267725e-10, cumulative = -1.8020759e-07
ExecutionTime = 38.18 s  ClockTime = 38 s

Time = 33

smoothSolver:  Solving for Ux, Initial residual = 0.00028495066, Final residual = 3.9671424e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 7.167224e-05, Final residual = 3.6988183e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.028031292, Final residual = 0.00014601204, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.027324309, Final residual = 0.00019513725, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0062000398, Final residual = 5.8215892e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0029317075, Final residual = 2.8995404e-05, No Iterations 14
time step continuity errors : sum local = 4.4751669e-07, global = 2.6021193e-10, cumulative = -1.7994737e-07
ExecutionTime = 39.22 s  ClockTime = 39 s

Time = 34

smoothSolver:  Solving for Ux, Initial residual = 0.00025707051, Final residual = 2.490141e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 6.4264913e-05, Final residual = 2.6416055e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.023014949, Final residual = 0.00022552628, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.028163501, Final residual = 0.00021464732, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0069554626, Final residual = 4.4175514e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0045371309, Final residual = 1.4473711e-05, No Iterations 9
time step continuity errors : sum local = 2.2403449e-07, global = 2.9328881e-11, cumulative = -1.7991805e-07
ExecutionTime = 40.04 s  ClockTime = 40 s

Time = 35

smoothSolver:  Solving for Ux, Initial residual = 0.00023512737, Final residual = 8.5297603e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 5.7198333e-05, Final residual = 2.1137262e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.01864705, Final residual = 0.00010551628, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.023743124, Final residual = 0.00022053246, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.005279603, Final residual = 5.0309654e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0034687595, Final residual = 2.4712975e-05, No Iterations 6
time step continuity errors : sum local = 3.8260087e-07, global = 3.8885344e-11, cumulative = -1.7987916e-07
ExecutionTime = 40.73 s  ClockTime = 41 s

Time = 36

smoothSolver:  Solving for Ux, Initial residual = 0.00020412724, Final residual = 9.5053038e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 4.8213629e-05, Final residual = 2.2059803e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.017460504, Final residual = 6.4715861e-05, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.014546363, Final residual = 7.3836266e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0033026393, Final residual = 2.7167139e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0020514926, Final residual = 1.6333162e-05, No Iterations 3
time step continuity errors : sum local = 2.5230511e-07, global = 2.4855704e-10, cumulative = -1.796306e-07
ExecutionTime = 41.46 s  ClockTime = 41 s

Time = 37

smoothSolver:  Solving for Ux, Initial residual = 0.00016849842, Final residual = 2.0533205e-09, No Iterations 4
smoothSolver:  Solving for Uy, Initial residual = 3.8417529e-05, Final residual = 2.2949984e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.017740978, Final residual = 0.00011729552, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0096553458, Final residual = 4.9870641e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0024493985, Final residual = 9.7215846e-06, No Iterations 13
GAMG:  Solving for p, Initial residual = 0.001304145, Final residual = 8.0002958e-06, No Iterations 3
time step continuity errors : sum local = 1.2340999e-07, global = 7.9345106e-10, cumulative = -1.7883715e-07
ExecutionTime = 42.24 s  ClockTime = 42 s

Time = 38

smoothSolver:  Solving for Ux, Initial residual = 0.00013553512, Final residual = 9.8657948e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 3.1539417e-05, Final residual = 2.0521105e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.017116744, Final residual = 9.3735323e-05, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.011188806, Final residual = 9.1220525e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.002689258, Final residual = 1.3548727e-05, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.0017217283, Final residual = 8.0290365e-06, No Iterations 3
time step continuity errors : sum local = 1.2401949e-07, global = 8.0942948e-10, cumulative = -1.7802772e-07
ExecutionTime = 42.97 s  ClockTime = 43 s

Time = 39

smoothSolver:  Solving for Ux, Initial residual = 0.00011334264, Final residual = 7.4465019e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 2.7242553e-05, Final residual = 8.5893895e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.015064787, Final residual = 0.00010611529, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.012794251, Final residual = 9.3270691e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0030994535, Final residual = 1.3014531e-05, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.0019842827, Final residual = 9.1574838e-06, No Iterations 3
time step continuity errors : sum local = 1.4174568e-07, global = 7.3790547e-10, cumulative = -1.7728982e-07
ExecutionTime = 43.72 s  ClockTime = 44 s

Time = 40

smoothSolver:  Solving for Ux, Initial residual = 0.00010155116, Final residual = 6.3827005e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 2.3683115e-05, Final residual = 7.3498196e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.012761355, Final residual = 0.00010688508, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.012086945, Final residual = 0.00011827396, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0027051702, Final residual = 2.2524004e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0021872863, Final residual = 1.2195634e-05, No Iterations 3
time step continuity errors : sum local = 1.8884785e-07, global = 4.3178264e-10, cumulative = -1.7685803e-07
ExecutionTime = 44.37 s  ClockTime = 44 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4663261e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5336802e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0123851

Time = 41

smoothSolver:  Solving for Ux, Initial residual = 9.4162613e-05, Final residual = 6.9979348e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 2.1152279e-05, Final residual = 7.4123552e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.011459011, Final residual = 3.8765565e-05, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.0091965102, Final residual = 8.6994475e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0020257451, Final residual = 6.4525193e-06, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.0014324705, Final residual = 5.4603056e-06, No Iterations 3
time step continuity errors : sum local = 8.4444765e-08, global = 4.0964188e-10, cumulative = -1.7644839e-07
ExecutionTime = 45.09 s  ClockTime = 45 s

Time = 42

smoothSolver:  Solving for Ux, Initial residual = 8.4722393e-05, Final residual = 7.7498089e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.8812725e-05, Final residual = 7.7072238e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.011146841, Final residual = 5.8224167e-05, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.0059743766, Final residual = 5.5944972e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0014020092, Final residual = 3.9001484e-06, No Iterations 6
GAMG:  Solving for p, Initial residual = 0.00085405509, Final residual = 3.1064514e-06, No Iterations 3
time step continuity errors : sum local = 4.7949639e-08, global = 3.3535386e-10, cumulative = -1.7611304e-07
ExecutionTime = 45.8 s  ClockTime = 46 s

Time = 43

smoothSolver:  Solving for Ux, Initial residual = 7.2228153e-05, Final residual = 7.7062007e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.604932e-05, Final residual = 7.4772688e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.010737239, Final residual = 6.4011723e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.005443319, Final residual = 3.5697844e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.001365173, Final residual = 7.4148822e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00082180562, Final residual = 5.186436e-06, No Iterations 3
time step continuity errors : sum local = 7.9952338e-08, global = 3.1221859e-10, cumulative = -1.7580082e-07
ExecutionTime = 46.49 s  ClockTime = 46 s

Time = 44

smoothSolver:  Solving for Ux, Initial residual = 6.1022865e-05, Final residual = 6.9613377e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.3596952e-05, Final residual = 6.7952583e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0097150131, Final residual = 9.0020026e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0057841946, Final residual = 4.6528747e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0014717269, Final residual = 8.7064749e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00095977289, Final residual = 6.1136134e-06, No Iterations 3
time step continuity errors : sum local = 9.4202814e-08, global = 2.2488532e-10, cumulative = -1.7557593e-07
ExecutionTime = 47.29 s  ClockTime = 47 s

Time = 45

smoothSolver:  Solving for Ux, Initial residual = 5.2190103e-05, Final residual = 6.032783e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.1637675e-05, Final residual = 6.1695131e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0084715351, Final residual = 7.1181846e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.005575945, Final residual = 4.6336162e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0012994752, Final residual = 1.1736623e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00082980511, Final residual = 6.6150385e-06, No Iterations 3
time step continuity errors : sum local = 1.0194716e-07, global = 2.1595867e-10, cumulative = -1.7535998e-07
ExecutionTime = 48.15 s  ClockTime = 48 s

Time = 46

smoothSolver:  Solving for Ux, Initial residual = 4.5118149e-05, Final residual = 5.420632e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.0178242e-05, Final residual = 5.9100216e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0076513859, Final residual = 5.5420754e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0044897438, Final residual = 3.6860193e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0010333972, Final residual = 6.5451922e-06, No Iterations 7
GAMG:  Solving for p, Initial residual = 0.00069815003, Final residual = 4.5427383e-06, No Iterations 3
time step continuity errors : sum local = 7.0040882e-08, global = 5.0841692e-11, cumulative = -1.7530913e-07
ExecutionTime = 48.92 s  ClockTime = 49 s

Time = 47

smoothSolver:  Solving for Ux, Initial residual = 3.9081022e-05, Final residual = 5.1590494e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 8.9360394e-06, Final residual = 5.8341543e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0073297242, Final residual = 4.0201922e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0033261816, Final residual = 2.4411225e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00078788233, Final residual = 1.8928811e-06, No Iterations 15
GAMG:  Solving for p, Initial residual = 0.00058932777, Final residual = 2.9757998e-06, No Iterations 3
time step continuity errors : sum local = 4.5902921e-08, global = 9.2963984e-11, cumulative = -1.7521617e-07
ExecutionTime = 49.77 s  ClockTime = 50 s

Time = 48

smoothSolver:  Solving for Ux, Initial residual = 3.3298874e-05, Final residual = 5.0281006e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 7.6664627e-06, Final residual = 5.7403817e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0071764709, Final residual = 6.0341399e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0028503745, Final residual = 2.5016502e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00072540603, Final residual = 4.5741813e-06, No Iterations 13
GAMG:  Solving for p, Initial residual = 0.00043531707, Final residual = 3.1973246e-06, No Iterations 3
time step continuity errors : sum local = 4.9344691e-08, global = 4.9742752e-11, cumulative = -1.7516643e-07
ExecutionTime = 50.61 s  ClockTime = 50 s

Time = 49

smoothSolver:  Solving for Ux, Initial residual = 2.7940721e-05, Final residual = 4.9402481e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 6.4038222e-06, Final residual = 5.5916781e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.006834338, Final residual = 6.6492315e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0028717833, Final residual = 1.8290515e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00073967823, Final residual = 3.7797075e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0004622448, Final residual = 1.2811851e-06, No Iterations 10
time step continuity errors : sum local = 1.9779964e-08, global = -6.4041327e-12, cumulative = -1.7517283e-07
ExecutionTime = 51.66 s  ClockTime = 52 s

Time = 50

smoothSolver:  Solving for Ux, Initial residual = 2.3422007e-05, Final residual = 4.9083372e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 5.2503783e-06, Final residual = 5.4656579e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0062638337, Final residual = 3.6660342e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0028734982, Final residual = 1.0119072e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00085343526, Final residual = 7.529467e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00033122166, Final residual = 2.4510568e-06, No Iterations 4
time step continuity errors : sum local = 3.7843332e-08, global = -3.9380498e-11, cumulative = -1.7521221e-07
ExecutionTime = 52.86 s  ClockTime = 53 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4661287e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5338708e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122368

Time = 51

smoothSolver:  Solving for Ux, Initial residual = 2.0008602e-05, Final residual = 4.9308322e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 4.4705088e-06, Final residual = 5.3691722e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0057023857, Final residual = 2.8096459e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0025546782, Final residual = 1.8060658e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00066277528, Final residual = 3.2055493e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00039829871, Final residual = 3.4440837e-06, No Iterations 3
time step continuity errors : sum local = 5.3165009e-08, global = -5.6133812e-11, cumulative = -1.7526835e-07
ExecutionTime = 53.64 s  ClockTime = 54 s

Time = 52

smoothSolver:  Solving for Ux, Initial residual = 1.7618496e-05, Final residual = 4.9630118e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 3.9995795e-06, Final residual = 5.2763744e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0053307833, Final residual = 4.3912378e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0019408993, Final residual = 1.8388841e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00056532979, Final residual = 2.9968429e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00035800366, Final residual = 1.1718812e-06, No Iterations 4
time step continuity errors : sum local = 1.808452e-08, global = 1.1668467e-11, cumulative = -1.7525668e-07
ExecutionTime = 54.4 s  ClockTime = 54 s

Time = 53

smoothSolver:  Solving for Ux, Initial residual = 1.5729438e-05, Final residual = 4.9451229e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 3.5676025e-06, Final residual = 5.1486335e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0050879113, Final residual = 3.4149573e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0016651615, Final residual = 1.345877e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00045023903, Final residual = 2.0491202e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00024162861, Final residual = 9.08979e-07, No Iterations 10
time step continuity errors : sum local = 1.4023456e-08, global = -1.1340158e-11, cumulative = -1.7526802e-07
ExecutionTime = 55.11 s  ClockTime = 55 s

Time = 54

smoothSolver:  Solving for Ux, Initial residual = 1.3851174e-05, Final residual = 4.8502608e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 3.1193505e-06, Final residual = 4.9833989e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0048406775, Final residual = 3.6207383e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0015287336, Final residual = 6.7416998e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00048194975, Final residual = 2.3899169e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00021172558, Final residual = 1.5140741e-06, No Iterations 6
time step continuity errors : sum local = 2.3354583e-08, global = -1.7160645e-11, cumulative = -1.7528518e-07
ExecutionTime = 55.78 s  ClockTime = 56 s

Time = 55

smoothSolver:  Solving for Ux, Initial residual = 1.2065945e-05, Final residual = 4.7038378e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 2.7154221e-06, Final residual = 4.8135172e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0045500789, Final residual = 4.5305561e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0015059198, Final residual = 1.118983e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00046380418, Final residual = 3.787885e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00017773567, Final residual = 4.0561948e-07, No Iterations 11
time step continuity errors : sum local = 6.2568167e-09, global = 4.780311e-12, cumulative = -1.752804e-07
ExecutionTime = 56.58 s  ClockTime = 57 s

Time = 56

smoothSolver:  Solving for Ux, Initial residual = 1.0379923e-05, Final residual = 4.5511514e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 2.3191004e-06, Final residual = 4.680927e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0042791261, Final residual = 1.4137459e-05, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.0014035263, Final residual = 4.7827099e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00039156587, Final residual = 2.0194736e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00017879261, Final residual = 4.4724657e-07, No Iterations 5
time step continuity errors : sum local = 6.8993614e-09, global = 9.397163e-12, cumulative = -1.75271e-07
ExecutionTime = 57.37 s  ClockTime = 57 s

Time = 57

smoothSolver:  Solving for Ux, Initial residual = 9.0643881e-06, Final residual = 4.4192051e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 2.0166917e-06, Final residual = 4.5928761e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0040817751, Final residual = 2.7910175e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0011451139, Final residual = 5.458146e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00039888746, Final residual = 3.9443662e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00015713141, Final residual = 1.0686194e-06, No Iterations 4
time step continuity errors : sum local = 1.6486748e-08, global = 8.7399502e-12, cumulative = -1.7526226e-07
ExecutionTime = 58.06 s  ClockTime = 58 s

Time = 58

smoothSolver:  Solving for Ux, Initial residual = 7.9706092e-06, Final residual = 4.3208829e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.7603232e-06, Final residual = 4.5364291e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0039390986, Final residual = 2.4420131e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0010125495, Final residual = 9.3385939e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00029690333, Final residual = 2.441909e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00018065762, Final residual = 1.5679243e-06, No Iterations 3
time step continuity errors : sum local = 2.4193265e-08, global = 3.1970585e-11, cumulative = -1.7523029e-07
ExecutionTime = 59.07 s  ClockTime = 59 s

Time = 59

smoothSolver:  Solving for Ux, Initial residual = 7.0280491e-06, Final residual = 4.2538346e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.5133771e-06, Final residual = 4.4944901e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0038059312, Final residual = 2.1887517e-05, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00092606864, Final residual = 8.8168536e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00027636108, Final residual = 2.0370931e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00012333085, Final residual = 8.2052126e-07, No Iterations 4
time step continuity errors : sum local = 1.2662395e-08, global = 1.5504401e-11, cumulative = -1.7521479e-07
ExecutionTime = 59.88 s  ClockTime = 60 s

Time = 60

smoothSolver:  Solving for Ux, Initial residual = 6.1866919e-06, Final residual = 4.2080334e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.3076959e-06, Final residual = 4.4568909e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0036605295, Final residual = 3.3931928e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00080283953, Final residual = 8.0020283e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00032534346, Final residual = 2.6509227e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00013721172, Final residual = 5.0778329e-07, No Iterations 6
time step continuity errors : sum local = 7.8369323e-09, global = 3.213837e-12, cumulative = -1.7521157e-07
ExecutionTime = 60.67 s  ClockTime = 61 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660833e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339168e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122691

Time = 61

smoothSolver:  Solving for Ux, Initial residual = 5.4106072e-06, Final residual = 4.1706217e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.1344232e-06, Final residual = 4.4104337e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0035135721, Final residual = 3.0125627e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00072813877, Final residual = 3.5586267e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00028414124, Final residual = 9.7123984e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00013096068, Final residual = 5.2462751e-07, No Iterations 5
time step continuity errors : sum local = 8.0970128e-09, global = -1.099038e-11, cumulative = -1.7522256e-07
ExecutionTime = 61.35 s  ClockTime = 61 s

Time = 62

smoothSolver:  Solving for Ux, Initial residual = 4.7696888e-06, Final residual = 4.1316448e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 9.8667504e-07, Final residual = 4.3499788e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0033761391, Final residual = 2.553572e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0006605307, Final residual = 3.5073031e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00025998869, Final residual = 1.7440605e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00010695012, Final residual = 8.1060855e-07, No Iterations 4
time step continuity errors : sum local = 1.250975e-08, global = -1.8775347e-11, cumulative = -1.7524134e-07
ExecutionTime = 61.99 s  ClockTime = 62 s

Time = 63

smoothSolver:  Solving for Ux, Initial residual = 4.3065072e-06, Final residual = 4.0851102e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 8.6365884e-07, Final residual = 4.2771508e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0032519197, Final residual = 2.3651372e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00060990951, Final residual = 1.5393848e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00024613939, Final residual = 2.3999137e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.8645621e-05, Final residual = 6.7513491e-07, No Iterations 3
time step continuity errors : sum local = 1.0418947e-08, global = -6.344855e-12, cumulative = -1.7524768e-07
ExecutionTime = 62.63 s  ClockTime = 63 s

Time = 64

smoothSolver:  Solving for Ux, Initial residual = 3.9274127e-06, Final residual = 4.0304565e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 7.6579577e-07, Final residual = 4.196448e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0031437208, Final residual = 2.1003395e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00057530416, Final residual = 3.189091e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00022056728, Final residual = 1.2192971e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.3219724e-05, Final residual = 7.9881121e-07, No Iterations 10
time step continuity errors : sum local = 1.2327418e-08, global = -1.1758832e-11, cumulative = -1.7525944e-07
ExecutionTime = 63.4 s  ClockTime = 63 s

Time = 65

smoothSolver:  Solving for Ux, Initial residual = 3.5841255e-06, Final residual = 3.9707308e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 6.8748006e-07, Final residual = 4.1157472e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0030502121, Final residual = 1.8879337e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00054651151, Final residual = 4.3327918e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00021668772, Final residual = 9.9787053e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.4814054e-05, Final residual = 6.8168503e-07, No Iterations 6
time step continuity errors : sum local = 1.0520025e-08, global = -1.210455e-12, cumulative = -1.7526065e-07
ExecutionTime = 64.2 s  ClockTime = 64 s

Time = 66

smoothSolver:  Solving for Ux, Initial residual = 3.2671323e-06, Final residual = 3.909049e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 6.1698616e-07, Final residual = 4.0417024e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0029669035, Final residual = 1.7350079e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00051573376, Final residual = 4.2426406e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00020432267, Final residual = 9.8051695e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.9153132e-05, Final residual = 7.701324e-07, No Iterations 11
time step continuity errors : sum local = 1.1885119e-08, global = 1.0478711e-11, cumulative = -1.7525017e-07
ExecutionTime = 65.03 s  ClockTime = 65 s

Time = 67

smoothSolver:  Solving for Ux, Initial residual = 2.9764136e-06, Final residual = 3.8491637e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 5.6111753e-07, Final residual = 3.9773434e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0028907633, Final residual = 1.5364964e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00048492222, Final residual = 2.2326256e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00018131319, Final residual = 1.5028353e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.5917041e-05, Final residual = 7.5104103e-07, No Iterations 7
time step continuity errors : sum local = 1.1590339e-08, global = 5.9777555e-12, cumulative = -1.752442e-07
ExecutionTime = 65.69 s  ClockTime = 66 s

Time = 68

smoothSolver:  Solving for Ux, Initial residual = 2.6912225e-06, Final residual = 3.7934508e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 5.0872007e-07, Final residual = 3.9230507e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00281659, Final residual = 1.3612694e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00045887526, Final residual = 1.0669072e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 0.00017321321, Final residual = 9.3910906e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.0969762e-05, Final residual = 5.7073252e-07, No Iterations 7
time step continuity errors : sum local = 8.8082851e-09, global = 8.2587174e-12, cumulative = -1.7523594e-07
ExecutionTime = 66.65 s  ClockTime = 67 s

Time = 69

smoothSolver:  Solving for Ux, Initial residual = 2.431002e-06, Final residual = 3.7430986e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 4.62135e-07, Final residual = 3.8763896e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0027451409, Final residual = 1.2147754e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00043535559, Final residual = 3.4377432e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00015983933, Final residual = 7.2725153e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.7552569e-05, Final residual = 2.4015196e-07, No Iterations 4
time step continuity errors : sum local = 3.7069825e-09, global = 3.5760044e-12, cumulative = -1.7523236e-07
ExecutionTime = 67.5 s  ClockTime = 68 s

Time = 70

smoothSolver:  Solving for Ux, Initial residual = 2.2118364e-06, Final residual = 3.6973109e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 4.2498688e-07, Final residual = 3.8346618e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.002676842, Final residual = 1.0809405e-05, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00041285029, Final residual = 4.0451325e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00014081604, Final residual = 5.0802801e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.1096894e-05, Final residual = 6.3127354e-07, No Iterations 3
time step continuity errors : sum local = 9.7434707e-09, global = 1.5858387e-11, cumulative = -1.752165e-07
ExecutionTime = 68.43 s  ClockTime = 69 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660792e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.533921e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122698

Time = 71

smoothSolver:  Solving for Ux, Initial residual = 2.0232025e-06, Final residual = 3.6550145e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 3.9117197e-07, Final residual = 3.7933678e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.002611321, Final residual = 9.5987986e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00039379189, Final residual = 3.743955e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00013340245, Final residual = 9.6015314e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.22398e-05, Final residual = 3.164787e-07, No Iterations 6
time step continuity errors : sum local = 4.8851071e-09, global = 1.8372169e-12, cumulative = -1.7521467e-07
ExecutionTime = 69.39 s  ClockTime = 69 s

Time = 72

smoothSolver:  Solving for Ux, Initial residual = 1.8447072e-06, Final residual = 3.6140878e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 3.5896063e-07, Final residual = 3.7499696e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0025510147, Final residual = 8.7288706e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00037667778, Final residual = 3.4188524e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00012682842, Final residual = 5.4685418e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.1775572e-05, Final residual = 2.8628559e-07, No Iterations 5
time step continuity errors : sum local = 4.4191224e-09, global = 4.8339839e-13, cumulative = -1.7521418e-07
ExecutionTime = 70.34 s  ClockTime = 70 s

Time = 73

smoothSolver:  Solving for Ux, Initial residual = 1.6797357e-06, Final residual = 3.5731056e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 3.2713921e-07, Final residual = 3.7041112e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0024935858, Final residual = 2.4857283e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00035537371, Final residual = 3.2651368e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00014232564, Final residual = 1.1178248e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.0322441e-05, Final residual = 3.9964232e-07, No Iterations 3
time step continuity errors : sum local = 6.1686028e-09, global = 3.22248e-12, cumulative = -1.7521096e-07
ExecutionTime = 71.25 s  ClockTime = 71 s

Time = 74

smoothSolver:  Solving for Ux, Initial residual = 1.5335287e-06, Final residual = 3.5318345e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 2.9736634e-07, Final residual = 3.656916e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0024397325, Final residual = 2.3489889e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00034171668, Final residual = 3.3387552e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00014315651, Final residual = 1.1019213e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.8495575e-05, Final residual = 5.8269452e-07, No Iterations 10
time step continuity errors : sum local = 8.9942424e-09, global = -4.5871202e-12, cumulative = -1.7521555e-07
ExecutionTime = 72.2 s  ClockTime = 72 s

Time = 75

smoothSolver:  Solving for Ux, Initial residual = 1.4209294e-06, Final residual = 3.4906896e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 2.726459e-07, Final residual = 3.6090146e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0023896403, Final residual = 2.2285321e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00032984309, Final residual = 2.9447986e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00014019344, Final residual = 9.3852195e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.6979986e-05, Final residual = 2.8302748e-07, No Iterations 4
time step continuity errors : sum local = 4.3690506e-09, global = -1.3563677e-12, cumulative = -1.752169e-07
ExecutionTime = 72.96 s  ClockTime = 73 s

Time = 76

smoothSolver:  Solving for Ux, Initial residual = 1.3073601e-06, Final residual = 3.4494452e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 2.4857773e-07, Final residual = 3.5618462e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0023414926, Final residual = 2.1103786e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00031948756, Final residual = 2.7775952e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00013660233, Final residual = 4.5274966e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.2995659e-05, Final residual = 5.2122919e-07, No Iterations 9
time step continuity errors : sum local = 8.0456281e-09, global = 1.4093799e-12, cumulative = -1.7521549e-07
ExecutionTime = 73.94 s  ClockTime = 74 s

Time = 77

smoothSolver:  Solving for Ux, Initial residual = 1.2226119e-06, Final residual = 3.4092275e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 2.2838017e-07, Final residual = 3.5168027e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0022958821, Final residual = 2.0126025e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00031206903, Final residual = 2.6078717e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0001315257, Final residual = 1.0876881e-06, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.3857857e-05, Final residual = 4.823433e-07, No Iterations 6
time step continuity errors : sum local = 7.4455323e-09, global = -1.7639768e-12, cumulative = -1.7521726e-07
ExecutionTime = 74.86 s  ClockTime = 75 s

Time = 78

smoothSolver:  Solving for Ux, Initial residual = 1.1422407e-06, Final residual = 3.3701736e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 2.1131045e-07, Final residual = 3.4746423e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0022512986, Final residual = 1.9241167e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00030450174, Final residual = 2.4511836e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00012550787, Final residual = 1.2358543e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.1802681e-05, Final residual = 2.0906844e-07, No Iterations 5
time step continuity errors : sum local = 3.2275631e-09, global = 1.4045541e-12, cumulative = -1.7521585e-07
ExecutionTime = 75.61 s  ClockTime = 76 s

Time = 79

smoothSolver:  Solving for Ux, Initial residual = 1.0681657e-06, Final residual = 3.3324462e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.96264e-07, Final residual = 3.4349108e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0022083236, Final residual = 1.8419917e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00029585996, Final residual = 2.2846472e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00011909263, Final residual = 5.4744966e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.8068051e-05, Final residual = 2.1112312e-07, No Iterations 7
time step continuity errors : sum local = 3.2594168e-09, global = 2.6211211e-13, cumulative = -1.7521559e-07
ExecutionTime = 76.28 s  ClockTime = 76 s

Time = 80

smoothSolver:  Solving for Ux, Initial residual = 1.0061133e-06, Final residual = 3.2960527e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.8474033e-07, Final residual = 3.3971018e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0021672342, Final residual = 1.773045e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00028867232, Final residual = 2.1387729e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00011394471, Final residual = 4.7317299e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.6481935e-05, Final residual = 2.7378451e-07, No Iterations 3
time step continuity errors : sum local = 4.2266874e-09, global = 1.5205773e-12, cumulative = -1.7521407e-07
ExecutionTime = 76.99 s  ClockTime = 77 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660791e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.533921e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122693

Time = 81

smoothSolver:  Solving for Ux, Initial residual = 9.530658e-07, Final residual = 3.2608717e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.7552444e-07, Final residual = 3.3606498e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0021274082, Final residual = 1.7185135e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00028265309, Final residual = 1.2879791e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00010809114, Final residual = 7.5937691e-07, No Iterations 7
GAMG:  Solving for p, Initial residual = 4.9365911e-05, Final residual = 4.375385e-07, No Iterations 5
time step continuity errors : sum local = 6.7544234e-09, global = 9.6586226e-12, cumulative = -1.7520441e-07
ExecutionTime = 77.91 s  ClockTime = 78 s

Time = 82

smoothSolver:  Solving for Ux, Initial residual = 9.1207088e-07, Final residual = 3.2265165e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.6894469e-07, Final residual = 3.3240115e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0020892227, Final residual = 1.6717788e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00027824789, Final residual = 1.2362818e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00010682982, Final residual = 8.3649774e-07, No Iterations 6
GAMG:  Solving for p, Initial residual = 5.0306936e-05, Final residual = 1.2501245e-07, No Iterations 6
time step continuity errors : sum local = 1.9303384e-09, global = 1.4954949e-12, cumulative = -1.7520292e-07
ExecutionTime = 78.78 s  ClockTime = 79 s

Time = 83

smoothSolver:  Solving for Ux, Initial residual = 8.7859099e-07, Final residual = 3.1928116e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.6445636e-07, Final residual = 3.2870075e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0020524895, Final residual = 1.6244463e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00027302573, Final residual = 2.1265375e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00010859585, Final residual = 3.3867027e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.4391037e-05, Final residual = 1.3896854e-07, No Iterations 9
time step continuity errors : sum local = 2.1457251e-09, global = 2.5982024e-12, cumulative = -1.7520032e-07
ExecutionTime = 79.56 s  ClockTime = 80 s

Time = 84

smoothSolver:  Solving for Ux, Initial residual = 8.4571876e-07, Final residual = 3.1596968e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.5985815e-07, Final residual = 3.2500437e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0020173813, Final residual = 1.5805886e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00026767766, Final residual = 2.1063873e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.0001080123, Final residual = 1.0698527e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.3812243e-05, Final residual = 1.321387e-07, No Iterations 11
time step continuity errors : sum local = 2.0402635e-09, global = 1.4534194e-12, cumulative = -1.7519886e-07
ExecutionTime = 80.43 s  ClockTime = 81 s

Time = 85

smoothSolver:  Solving for Ux, Initial residual = 8.1519153e-07, Final residual = 3.1271508e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.5497554e-07, Final residual = 3.2131433e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0019839918, Final residual = 1.5452673e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00026291423, Final residual = 2.0402391e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00010690883, Final residual = 1.0585726e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.3209114e-05, Final residual = 3.1065449e-07, No Iterations 3
time step continuity errors : sum local = 4.7961214e-09, global = 2.6218295e-12, cumulative = -1.7519624e-07
ExecutionTime = 81.04 s  ClockTime = 81 s

Time = 86

smoothSolver:  Solving for Ux, Initial residual = 7.7759644e-07, Final residual = 3.0949906e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.4895825e-07, Final residual = 3.1764435e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0019517787, Final residual = 1.5112167e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00025848931, Final residual = 2.0605311e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00010669734, Final residual = 7.0584914e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.461019e-05, Final residual = 1.6961155e-07, No Iterations 4
time step continuity errors : sum local = 2.6190825e-09, global = -1.3497314e-12, cumulative = -1.7519759e-07
ExecutionTime = 81.69 s  ClockTime = 82 s

Time = 87

smoothSolver:  Solving for Ux, Initial residual = 7.4687188e-07, Final residual = 3.0635709e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.4358276e-07, Final residual = 3.1404356e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0019207652, Final residual = 1.4737412e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00025443888, Final residual = 2.0617002e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00010529136, Final residual = 7.2673858e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.4976354e-05, Final residual = 4.4873579e-07, No Iterations 9
time step continuity errors : sum local = 6.9276955e-09, global = 5.7626099e-12, cumulative = -1.7519183e-07
ExecutionTime = 82.4 s  ClockTime = 83 s

Time = 88

smoothSolver:  Solving for Ux, Initial residual = 7.2311269e-07, Final residual = 3.0329309e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.3877788e-07, Final residual = 3.1055203e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0018909635, Final residual = 1.4401321e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00025112632, Final residual = 1.9406957e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 0.00010190179, Final residual = 6.5578684e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.2482808e-05, Final residual = 3.1170029e-07, No Iterations 11
time step continuity errors : sum local = 4.8126295e-09, global = 4.9486405e-12, cumulative = -1.7518688e-07
ExecutionTime = 83.23 s  ClockTime = 83 s

Time = 89

smoothSolver:  Solving for Ux, Initial residual = 7.010332e-07, Final residual = 3.0028385e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.3387373e-07, Final residual = 3.0721526e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0018625768, Final residual = 1.4099358e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00024758173, Final residual = 1.8073546e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.9575048e-05, Final residual = 9.7301559e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.0549446e-05, Final residual = 3.8917802e-07, No Iterations 8
time step continuity errors : sum local = 6.0085931e-09, global = 5.5335077e-12, cumulative = -1.7518135e-07
ExecutionTime = 84.02 s  ClockTime = 84 s

Time = 90

smoothSolver:  Solving for Ux, Initial residual = 6.7822171e-07, Final residual = 2.9733169e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.2878611e-07, Final residual = 3.0402462e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0018349345, Final residual = 1.3815695e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00024275887, Final residual = 1.7307937e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.6889228e-05, Final residual = 9.0756023e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.1794369e-05, Final residual = 1.2262024e-07, No Iterations 5
time step continuity errors : sum local = 1.8937611e-09, global = 1.3261404e-12, cumulative = -1.7518002e-07
ExecutionTime = 84.75 s  ClockTime = 85 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.46608e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.53392e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012269

Time = 91

smoothSolver:  Solving for Ux, Initial residual = 6.5578578e-07, Final residual = 2.9441666e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.2380249e-07, Final residual = 3.0093474e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0018076956, Final residual = 1.3522679e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00023807931, Final residual = 1.6971999e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.4905137e-05, Final residual = 8.6620161e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.0987827e-05, Final residual = 1.6369313e-07, No Iterations 4
time step continuity errors : sum local = 2.5277413e-09, global = 5.8649641e-13, cumulative = -1.7517944e-07
ExecutionTime = 85.41 s  ClockTime = 86 s

Time = 92

smoothSolver:  Solving for Ux, Initial residual = 6.3138189e-07, Final residual = 2.9156234e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.1912766e-07, Final residual = 2.9793235e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0017812731, Final residual = 1.3287213e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00023442264, Final residual = 1.6964238e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.3749501e-05, Final residual = 9.3535175e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.8582338e-05, Final residual = 2.2876793e-07, No Iterations 3
time step continuity errors : sum local = 3.5321848e-09, global = 8.200779e-13, cumulative = -1.7517862e-07
ExecutionTime = 85.96 s  ClockTime = 86 s

Time = 93

smoothSolver:  Solving for Ux, Initial residual = 6.1146166e-07, Final residual = 2.8875426e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.1555718e-07, Final residual = 2.9498619e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0017548382, Final residual = 1.3097742e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00023070888, Final residual = 1.7653363e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.2758307e-05, Final residual = 8.9313708e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.9978923e-05, Final residual = 1.7460143e-07, No Iterations 3
time step continuity errors : sum local = 2.696335e-09, global = -3.1208766e-14, cumulative = -1.7517865e-07
ExecutionTime = 86.57 s  ClockTime = 87 s

Time = 94

smoothSolver:  Solving for Ux, Initial residual = 5.979379e-07, Final residual = 2.8600275e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.1298498e-07, Final residual = 2.9207521e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0017295672, Final residual = 1.2886029e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00022756164, Final residual = 1.8639184e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.2142683e-05, Final residual = 8.8891179e-07, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.8674204e-05, Final residual = 1.7364113e-07, No Iterations 5
time step continuity errors : sum local = 2.681406e-09, global = 1.8698853e-12, cumulative = -1.7517678e-07
ExecutionTime = 87.24 s  ClockTime = 87 s

Time = 95

smoothSolver:  Solving for Ux, Initial residual = 5.8433943e-07, Final residual = 2.8329957e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.1031058e-07, Final residual = 2.8920232e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0017052065, Final residual = 1.2664054e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00022402684, Final residual = 1.8376638e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.1131097e-05, Final residual = 8.2215204e-07, No Iterations 7
GAMG:  Solving for p, Initial residual = 3.8531209e-05, Final residual = 1.5657724e-07, No Iterations 4
time step continuity errors : sum local = 2.4179694e-09, global = 1.2632128e-12, cumulative = -1.7517551e-07
ExecutionTime = 87.9 s  ClockTime = 88 s

Time = 96

smoothSolver:  Solving for Ux, Initial residual = 5.7577593e-07, Final residual = 2.8064616e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.0879898e-07, Final residual = 2.8637224e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0016813668, Final residual = 1.2431482e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00022030982, Final residual = 1.7582792e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.9429644e-05, Final residual = 6.0891398e-07, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.8041218e-05, Final residual = 1.457095e-07, No Iterations 4
time step continuity errors : sum local = 2.2502364e-09, global = 1.444017e-12, cumulative = -1.7517407e-07
ExecutionTime = 88.59 s  ClockTime = 89 s

Time = 97

smoothSolver:  Solving for Ux, Initial residual = 5.6871904e-07, Final residual = 2.7805518e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.078595e-07, Final residual = 2.8358659e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0016578945, Final residual = 1.2207781e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00021677101, Final residual = 1.6554257e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.7612257e-05, Final residual = 6.7502168e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.774068e-05, Final residual = 1.9397788e-07, No Iterations 3
time step continuity errors : sum local = 2.9951996e-09, global = 4.1971057e-13, cumulative = -1.7517365e-07
ExecutionTime = 89.17 s  ClockTime = 89 s

Time = 98

smoothSolver:  Solving for Ux, Initial residual = 5.5734856e-07, Final residual = 2.7552738e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.0611418e-07, Final residual = 2.8085174e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0016346054, Final residual = 1.2036916e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00021367873, Final residual = 1.611838e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.5914638e-05, Final residual = 7.4421966e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.6984718e-05, Final residual = 3.6639922e-07, No Iterations 5
time step continuity errors : sum local = 5.6575003e-09, global = 6.660524e-12, cumulative = -1.7516699e-07
ExecutionTime = 89.82 s  ClockTime = 90 s

Time = 99

smoothSolver:  Solving for Ux, Initial residual = 5.4781821e-07, Final residual = 2.7306998e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.043962e-07, Final residual = 2.7818152e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0016117306, Final residual = 1.1882137e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00021121338, Final residual = 1.5404303e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.3901955e-05, Final residual = 6.8853562e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.6131711e-05, Final residual = 1.2274772e-07, No Iterations 5
time step continuity errors : sum local = 1.8958249e-09, global = 4.0314268e-13, cumulative = -1.7516659e-07
ExecutionTime = 90.46 s  ClockTime = 91 s

Time = 100

smoothSolver:  Solving for Ux, Initial residual = 5.3490078e-07, Final residual = 2.7065633e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.0229086e-07, Final residual = 2.7557009e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0015898181, Final residual = 1.1749235e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00020879243, Final residual = 1.5085298e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.2664576e-05, Final residual = 6.723136e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.5925707e-05, Final residual = 1.6443492e-07, No Iterations 5
time step continuity errors : sum local = 2.5396596e-09, global = -1.295603e-13, cumulative = -1.7516672e-07
ExecutionTime = 91.48 s  ClockTime = 92 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660803e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339197e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122688

Time = 101

smoothSolver:  Solving for Ux, Initial residual = 5.2399283e-07, Final residual = 2.6830015e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 1.0041543e-07, Final residual = 2.7299869e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0015682935, Final residual = 1.1643957e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00020558982, Final residual = 1.4635125e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.049138e-05, Final residual = 6.671425e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.5181723e-05, Final residual = 9.4404101e-08, No Iterations 6
time step continuity errors : sum local = 1.4581717e-09, global = 8.4796049e-13, cumulative = -1.7516587e-07
ExecutionTime = 92.09 s  ClockTime = 92 s

Time = 102

smoothSolver:  Solving for Ux, Initial residual = 5.1633484e-07, Final residual = 2.6599267e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 9.8887945e-08, Final residual = 2.7047811e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0015468662, Final residual = 1.1521844e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00020272389, Final residual = 1.4092552e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.9317756e-05, Final residual = 6.6883855e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4647559e-05, Final residual = 7.6371547e-08, No Iterations 9
time step continuity errors : sum local = 1.180245e-09, global = 7.4423003e-13, cumulative = -1.7516512e-07
ExecutionTime = 92.91 s  ClockTime = 93 s

Time = 103

smoothSolver:  Solving for Ux, Initial residual = 5.1101659e-07, Final residual = 2.6371263e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 9.7549824e-08, Final residual = 2.6801811e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0015263292, Final residual = 1.1395857e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00020004319, Final residual = 1.3519014e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.8221063e-05, Final residual = 6.829062e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4039558e-05, Final residual = 2.9043522e-07, No Iterations 7
time step continuity errors : sum local = 4.4852111e-09, global = 3.1389592e-12, cumulative = -1.7516198e-07
ExecutionTime = 94.1 s  ClockTime = 94 s

Time = 104

smoothSolver:  Solving for Ux, Initial residual = 5.0416532e-07, Final residual = 2.6144732e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 9.5992403e-08, Final residual = 2.6560438e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0015063846, Final residual = 1.1249705e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00019788222, Final residual = 1.3079824e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.6794729e-05, Final residual = 7.5972004e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.1610023e-05, Final residual = 2.9368277e-07, No Iterations 9
time step continuity errors : sum local = 4.5352448e-09, global = 3.0192339e-12, cumulative = -1.7515896e-07
ExecutionTime = 94.76 s  ClockTime = 95 s

Time = 105

smoothSolver:  Solving for Ux, Initial residual = 4.9592878e-07, Final residual = 2.591844e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 9.4318532e-08, Final residual = 2.6325259e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.001486539, Final residual = 1.104798e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00019596678, Final residual = 1.290399e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.6142666e-05, Final residual = 7.4111003e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.1354788e-05, Final residual = 2.9436902e-07, No Iterations 6
time step continuity errors : sum local = 4.5460212e-09, global = 3.2515528e-12, cumulative = -1.7515571e-07
ExecutionTime = 95.45 s  ClockTime = 96 s

Time = 106

smoothSolver:  Solving for Ux, Initial residual = 4.8557532e-07, Final residual = 2.5695321e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 9.2455008e-08, Final residual = 2.6090766e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0014672034, Final residual = 1.0819261e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00019324084, Final residual = 1.2785378e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.5137356e-05, Final residual = 7.2626819e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.0936609e-05, Final residual = 2.4248491e-07, No Iterations 12
time step continuity errors : sum local = 3.7448312e-09, global = 3.8464119e-12, cumulative = -1.7515187e-07
ExecutionTime = 96.16 s  ClockTime = 96 s

Time = 107

smoothSolver:  Solving for Ux, Initial residual = 4.8022345e-07, Final residual = 2.5473528e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 9.1356356e-08, Final residual = 2.586737e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0014490255, Final residual = 1.0604587e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0001905106, Final residual = 1.2723168e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.3963993e-05, Final residual = 7.2049509e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.0405669e-05, Final residual = 9.0888098e-08, No Iterations 7
time step continuity errors : sum local = 1.4042966e-09, global = -2.8055504e-14, cumulative = -1.751519e-07
ExecutionTime = 96.81 s  ClockTime = 97 s

Time = 108

smoothSolver:  Solving for Ux, Initial residual = 4.7365517e-07, Final residual = 2.5262491e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 9.0158803e-08, Final residual = 2.5635119e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0014301642, Final residual = 1.0456855e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00018747991, Final residual = 1.2774054e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.2622419e-05, Final residual = 7.0523884e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.9959589e-05, Final residual = 2.1612275e-07, No Iterations 11
time step continuity errors : sum local = 3.3376994e-09, global = 3.8728029e-12, cumulative = -1.7514802e-07
ExecutionTime = 97.57 s  ClockTime = 98 s

Time = 109

smoothSolver:  Solving for Ux, Initial residual = 4.6927541e-07, Final residual = 2.5049063e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 8.9329188e-08, Final residual = 2.5415997e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0014128427, Final residual = 1.0338364e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00018486754, Final residual = 1.2670446e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.1479202e-05, Final residual = 6.9167329e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.9533559e-05, Final residual = 2.5746376e-07, No Iterations 12
time step continuity errors : sum local = 3.9761011e-09, global = 4.214812e-12, cumulative = -1.7514381e-07
ExecutionTime = 98.3 s  ClockTime = 99 s

Time = 110

smoothSolver:  Solving for Ux, Initial residual = 4.6562594e-07, Final residual = 2.4846974e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 8.8642432e-08, Final residual = 2.5187901e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0013949796, Final residual = 1.0241628e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00018190198, Final residual = 1.2409982e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.0613869e-05, Final residual = 6.8108209e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.9199329e-05, Final residual = 2.7137634e-07, No Iterations 9
time step continuity errors : sum local = 4.1909654e-09, global = 4.5269527e-12, cumulative = -1.7513928e-07
ExecutionTime = 98.95 s  ClockTime = 99 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660805e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339196e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122687

Time = 111

smoothSolver:  Solving for Ux, Initial residual = 4.6105686e-07, Final residual = 2.463814e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 8.8031184e-08, Final residual = 2.4983615e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0013790769, Final residual = 1.0061297e-05, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00018006306, Final residual = 1.2416072e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.0084366e-05, Final residual = 6.8458692e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.9044263e-05, Final residual = 1.0658531e-07, No Iterations 7
time step continuity errors : sum local = 1.6468265e-09, global = 4.0464909e-13, cumulative = -1.7513888e-07
ExecutionTime = 99.64 s  ClockTime = 100 s

Time = 112

smoothSolver:  Solving for Ux, Initial residual = 4.5542043e-07, Final residual = 2.4446577e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 8.687487e-08, Final residual = 2.4754505e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0013600171, Final residual = 9.8479935e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00017696135, Final residual = 1.2238564e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.9099819e-05, Final residual = 6.6361095e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.8603618e-05, Final residual = 2.6430847e-07, No Iterations 10
time step continuity errors : sum local = 4.0819775e-09, global = 4.4550493e-12, cumulative = -1.7513442e-07
ExecutionTime = 100.46 s  ClockTime = 101 s

Time = 113

smoothSolver:  Solving for Ux, Initial residual = 4.5028613e-07, Final residual = 2.4243291e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 8.6117093e-08, Final residual = 2.4554078e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0013440274, Final residual = 9.6352542e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00017496361, Final residual = 1.1939743e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.8192485e-05, Final residual = 6.6330632e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.835403e-05, Final residual = 9.6044024e-08, No Iterations 9
time step continuity errors : sum local = 1.4837741e-09, global = 6.6218579e-13, cumulative = -1.7513376e-07
ExecutionTime = 101.16 s  ClockTime = 101 s

Time = 114

smoothSolver:  Solving for Ux, Initial residual = 4.4591314e-07, Final residual = 2.405783e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 8.5127303e-08, Final residual = 2.4333141e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0013257141, Final residual = 9.5190214e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00017231341, Final residual = 1.1507767e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.6928332e-05, Final residual = 6.4892901e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.7921259e-05, Final residual = 6.0540967e-08, No Iterations 10
time step continuity errors : sum local = 9.3549008e-10, global = 5.8521283e-13, cumulative = -1.7513317e-07
ExecutionTime = 101.91 s  ClockTime = 102 s

Time = 115

smoothSolver:  Solving for Ux, Initial residual = 4.4143634e-07, Final residual = 2.3860751e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 8.4366689e-08, Final residual = 2.4140931e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0013099883, Final residual = 9.4489503e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00017067817, Final residual = 1.1240331e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.6137477e-05, Final residual = 6.4517811e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.774272e-05, Final residual = 2.6115029e-07, No Iterations 9
time step continuity errors : sum local = 4.033519e-09, global = 2.7914691e-12, cumulative = -1.7513038e-07
ExecutionTime = 102.69 s  ClockTime = 103 s

Time = 116

smoothSolver:  Solving for Ux, Initial residual = 4.3648747e-07, Final residual = 2.368092e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 8.3331799e-08, Final residual = 2.3928515e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0012934301, Final residual = 9.4259004e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00016827407, Final residual = 1.6626212e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.2028924e-05, Final residual = 3.8052735e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.0379314e-05, Final residual = 2.7220476e-07, No Iterations 7
time step continuity errors : sum local = 4.2042446e-09, global = 2.7631477e-12, cumulative = -1.7512762e-07
ExecutionTime = 103.73 s  ClockTime = 104 s

Time = 117

smoothSolver:  Solving for Ux, Initial residual = 4.3214732e-07, Final residual = 2.3488971e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 8.2645722e-08, Final residual = 2.3742127e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0012782317, Final residual = 9.3128874e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00016653279, Final residual = 1.6171676e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.1334917e-05, Final residual = 3.4668975e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.0440857e-05, Final residual = 6.5986632e-08, No Iterations 6
time step continuity errors : sum local = 1.0199572e-09, global = -9.2114791e-14, cumulative = -1.7512771e-07
ExecutionTime = 104.54 s  ClockTime = 105 s

Time = 118

smoothSolver:  Solving for Ux, Initial residual = 4.2655024e-07, Final residual = 2.3314596e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 8.1453629e-08, Final residual = 2.3536437e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.001262819, Final residual = 9.2123856e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00016458185, Final residual = 1.5964049e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.0575587e-05, Final residual = 3.4527268e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.9965002e-05, Final residual = 2.6827477e-07, No Iterations 7
time step continuity errors : sum local = 4.1434334e-09, global = 2.4599309e-12, cumulative = -1.7512525e-07
ExecutionTime = 105.35 s  ClockTime = 106 s

Time = 119

smoothSolver:  Solving for Ux, Initial residual = 4.2247649e-07, Final residual = 2.3129733e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 8.078297e-08, Final residual = 2.3357115e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0012483863, Final residual = 9.0773631e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00016308149, Final residual = 1.5871617e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.0141046e-05, Final residual = 3.3042092e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.9971741e-05, Final residual = 2.6993989e-07, No Iterations 5
time step continuity errors : sum local = 4.1692449e-09, global = 2.5866801e-12, cumulative = -1.7512266e-07
ExecutionTime = 106.18 s  ClockTime = 106 s

Time = 120

smoothSolver:  Solving for Ux, Initial residual = 4.1776614e-07, Final residual = 2.2960407e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 7.9841292e-08, Final residual = 2.3160958e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.001233247, Final residual = 8.9768476e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00016097933, Final residual = 1.5966835e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.9562885e-05, Final residual = 3.6223142e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.9652605e-05, Final residual = 2.2292265e-07, No Iterations 9
time step continuity errors : sum local = 3.4429874e-09, global = 3.2453147e-12, cumulative = -1.7511942e-07
ExecutionTime = 108.01 s  ClockTime = 108 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660805e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339195e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122686

Time = 121

smoothSolver:  Solving for Ux, Initial residual = 4.1396725e-07, Final residual = 2.2782929e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 7.9166807e-08, Final residual = 2.298408e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0012198522, Final residual = 8.8986198e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00015982976, Final residual = 1.5974993e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.9317993e-05, Final residual = 3.4965998e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.9705873e-05, Final residual = 2.7437143e-07, No Iterations 5
time step continuity errors : sum local = 4.2378216e-09, global = 3.6994369e-12, cumulative = -1.7511572e-07
ExecutionTime = 109.57 s  ClockTime = 110 s

Time = 122

smoothSolver:  Solving for Ux, Initial residual = 4.1101388e-07, Final residual = 2.2618994e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 7.8441144e-08, Final residual = 2.2792599e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0012051789, Final residual = 8.8047292e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00015771263, Final residual = 1.017128e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.1267324e-05, Final residual = 5.8955809e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5983999e-05, Final residual = 9.615262e-08, No Iterations 7
time step continuity errors : sum local = 1.4854785e-09, global = 5.8304219e-13, cumulative = -1.7511514e-07
ExecutionTime = 110.5 s  ClockTime = 111 s

Time = 123

smoothSolver:  Solving for Ux, Initial residual = 4.0656419e-07, Final residual = 2.2446129e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 7.765965e-08, Final residual = 2.2622527e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0011916788, Final residual = 8.6989419e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00015622213, Final residual = 1.0236392e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.0668643e-05, Final residual = 5.7530144e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5810493e-05, Final residual = 2.4652137e-07, No Iterations 8
time step continuity errors : sum local = 3.8078241e-09, global = 4.4028961e-12, cumulative = -1.7511073e-07
ExecutionTime = 111.15 s  ClockTime = 111 s

Time = 124

smoothSolver:  Solving for Ux, Initial residual = 4.0359382e-07, Final residual = 2.2283562e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 7.6979471e-08, Final residual = 2.2445025e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0011777679, Final residual = 8.5912997e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00015455707, Final residual = 1.0106427e-06, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.0126394e-05, Final residual = 5.7043563e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5718284e-05, Final residual = 5.6714152e-08, No Iterations 9
time step continuity errors : sum local = 8.7655537e-10, global = 1.2234479e-12, cumulative = -1.7510951e-07
ExecutionTime = 111.91 s  ClockTime = 112 s

Time = 125

smoothSolver:  Solving for Ux, Initial residual = 4.0084988e-07, Final residual = 2.2118327e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 7.6361549e-08, Final residual = 2.227404e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0011651185, Final residual = 8.4968989e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00015319881, Final residual = 1.5260129e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.6859416e-05, Final residual = 4.8915857e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.8232337e-05, Final residual = 1.1298881e-07, No Iterations 3
time step continuity errors : sum local = 1.7457327e-09, global = -1.5476862e-13, cumulative = -1.7510966e-07
ExecutionTime = 112.58 s  ClockTime = 113 s

Time = 126

smoothSolver:  Solving for Ux, Initial residual = 3.9697888e-07, Final residual = 2.1961329e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 7.5606968e-08, Final residual = 2.2094584e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0011520219, Final residual = 8.402362e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00015149813, Final residual = 1.503851e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.6396491e-05, Final residual = 5.3793124e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.8157872e-05, Final residual = 2.7337665e-07, No Iterations 5
time step continuity errors : sum local = 4.2224912e-09, global = 3.6444207e-12, cumulative = -1.7510602e-07
ExecutionTime = 113.4 s  ClockTime = 114 s

Time = 127

smoothSolver:  Solving for Ux, Initial residual = 3.9348577e-07, Final residual = 2.1796862e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 7.5021384e-08, Final residual = 2.1933993e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0011398346, Final residual = 8.2783903e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00015020875, Final residual = 1.4729872e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.5993272e-05, Final residual = 4.9933308e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.8055407e-05, Final residual = 2.0155111e-07, No Iterations 7
time step continuity errors : sum local = 3.1137214e-09, global = 3.7058747e-12, cumulative = -1.7510231e-07
ExecutionTime = 114.18 s  ClockTime = 114 s

Time = 128

smoothSolver:  Solving for Ux, Initial residual = 3.9194233e-07, Final residual = 2.16416e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 7.4563839e-08, Final residual = 2.1770105e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0011281239, Final residual = 8.1217536e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00014898898, Final residual = 1.4447836e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.509837e-05, Final residual = 4.7826402e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.7492564e-05, Final residual = 2.6809651e-07, No Iterations 4
time step continuity errors : sum local = 4.1414286e-09, global = 3.7697941e-12, cumulative = -1.7509854e-07
ExecutionTime = 114.86 s  ClockTime = 115 s

Time = 129

smoothSolver:  Solving for Ux, Initial residual = 3.8919011e-07, Final residual = 2.1486758e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 7.4008161e-08, Final residual = 2.1604612e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0011160767, Final residual = 7.9660098e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00014724236, Final residual = 1.4341479e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.4505313e-05, Final residual = 4.2752327e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.7278709e-05, Final residual = 1.0247409e-07, No Iterations 3
time step continuity errors : sum local = 1.5832877e-09, global = -8.4447324e-14, cumulative = -1.7509863e-07
ExecutionTime = 115.53 s  ClockTime = 116 s

Time = 130

smoothSolver:  Solving for Ux, Initial residual = 3.847829e-07, Final residual = 2.1332897e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 7.3180906e-08, Final residual = 2.1445114e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0011044961, Final residual = 7.8308307e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00014563193, Final residual = 1.4399164e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.4164128e-05, Final residual = 4.4091064e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.7474557e-05, Final residual = 2.6178283e-07, No Iterations 4
time step continuity errors : sum local = 4.0437983e-09, global = 3.6227687e-12, cumulative = -1.7509501e-07
ExecutionTime = 116.17 s  ClockTime = 116 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660805e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339195e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122685

Time = 131

smoothSolver:  Solving for Ux, Initial residual = 3.824637e-07, Final residual = 2.1183354e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 7.2676772e-08, Final residual = 2.1286469e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0010930821, Final residual = 7.7187914e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00014398865, Final residual = 1.4310238e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.3711643e-05, Final residual = 4.4631518e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.7223747e-05, Final residual = 9.372596e-08, No Iterations 4
time step continuity errors : sum local = 1.4483147e-09, global = 2.8966826e-13, cumulative = -1.7509472e-07
ExecutionTime = 116.84 s  ClockTime = 117 s

Time = 132

smoothSolver:  Solving for Ux, Initial residual = 3.7954618e-07, Final residual = 2.1036075e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 7.2092532e-08, Final residual = 2.1128541e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0010820147, Final residual = 7.6314992e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00014250759, Final residual = 1.4179699e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.317555e-05, Final residual = 4.638472e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.6835099e-05, Final residual = 2.2937129e-07, No Iterations 5
time step continuity errors : sum local = 3.5432951e-09, global = 3.2515358e-12, cumulative = -1.7509147e-07
ExecutionTime = 117.46 s  ClockTime = 118 s

Time = 133

smoothSolver:  Solving for Ux, Initial residual = 3.7827528e-07, Final residual = 2.0890192e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 7.173616e-08, Final residual = 2.0972034e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0010711458, Final residual = 7.5524798e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00014097405, Final residual = 1.3935672e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.2394954e-05, Final residual = 4.7121672e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.5972186e-05, Final residual = 2.0182168e-07, No Iterations 5
time step continuity errors : sum local = 3.1174229e-09, global = 3.4524599e-12, cumulative = -1.7508801e-07
ExecutionTime = 118.15 s  ClockTime = 118 s

Time = 134

smoothSolver:  Solving for Ux, Initial residual = 3.7574546e-07, Final residual = 2.0745981e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 7.1258357e-08, Final residual = 2.0817813e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0010602077, Final residual = 7.4666751e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00013929826, Final residual = 1.3652354e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.1768302e-05, Final residual = 3.4358023e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.5849486e-05, Final residual = 2.510856e-07, No Iterations 4
time step continuity errors : sum local = 3.8787609e-09, global = 3.931692e-12, cumulative = -1.7508408e-07
ExecutionTime = 118.84 s  ClockTime = 119 s

Time = 135

smoothSolver:  Solving for Ux, Initial residual = 3.7307719e-07, Final residual = 2.060371e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 7.0771674e-08, Final residual = 2.0666124e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0010493781, Final residual = 7.3864991e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00013777165, Final residual = 1.3277224e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.1247564e-05, Final residual = 2.708483e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.5645824e-05, Final residual = 9.0963926e-08, No Iterations 3
time step continuity errors : sum local = 1.4056409e-09, global = 3.4928001e-13, cumulative = -1.7508373e-07
ExecutionTime = 119.5 s  ClockTime = 120 s

Time = 136

smoothSolver:  Solving for Ux, Initial residual = 3.6856239e-07, Final residual = 2.046284e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 6.9932104e-08, Final residual = 2.0517323e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0010386552, Final residual = 7.3128635e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0001361487, Final residual = 1.3200254e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.0638241e-05, Final residual = 3.0748577e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.5155283e-05, Final residual = 8.1868533e-08, No Iterations 3
time step continuity errors : sum local = 1.2653462e-09, global = -1.6943312e-13, cumulative = -1.750839e-07
ExecutionTime = 120.14 s  ClockTime = 120 s

Time = 137

smoothSolver:  Solving for Ux, Initial residual = 3.6601494e-07, Final residual = 2.0324653e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 6.9483443e-08, Final residual = 2.0371046e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0010281671, Final residual = 7.2523416e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00013458774, Final residual = 1.3278792e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.0230639e-05, Final residual = 4.0931208e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.5004566e-05, Final residual = 2.4531939e-07, No Iterations 4
time step continuity errors : sum local = 3.78972e-09, global = 2.7572869e-12, cumulative = -1.7508114e-07
ExecutionTime = 120.79 s  ClockTime = 121 s

Time = 138

smoothSolver:  Solving for Ux, Initial residual = 3.6301762e-07, Final residual = 2.0188918e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 6.8912815e-08, Final residual = 2.0227031e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00101819, Final residual = 7.1919566e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00013313584, Final residual = 1.3295685e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.9663357e-05, Final residual = 4.330658e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.4648929e-05, Final residual = 2.3598551e-07, No Iterations 4
time step continuity errors : sum local = 3.6455351e-09, global = 2.7499095e-12, cumulative = -1.7507839e-07
ExecutionTime = 121.44 s  ClockTime = 122 s

Time = 139

smoothSolver:  Solving for Ux, Initial residual = 3.607947e-07, Final residual = 2.005434e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 6.8431894e-08, Final residual = 2.0085429e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0010084608, Final residual = 7.1315914e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00013191363, Final residual = 8.336685e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.1250357e-05, Final residual = 4.8871681e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.3076027e-05, Final residual = 5.3333437e-08, No Iterations 8
time step continuity errors : sum local = 8.2429678e-10, global = 6.0001337e-13, cumulative = -1.7507779e-07
ExecutionTime = 122.15 s  ClockTime = 122 s

Time = 140

smoothSolver:  Solving for Ux, Initial residual = 3.5965767e-07, Final residual = 1.9921008e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 6.8085542e-08, Final residual = 1.9943939e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00099889238, Final residual = 7.0836194e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00013065891, Final residual = 1.2920504e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.8463491e-05, Final residual = 3.2261361e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.426088e-05, Final residual = 2.0853617e-07, No Iterations 4
time step continuity errors : sum local = 3.2218107e-09, global = 2.5753497e-12, cumulative = -1.7507522e-07
ExecutionTime = 122.8 s  ClockTime = 123 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660805e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339195e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122685

Time = 141

smoothSolver:  Solving for Ux, Initial residual = 3.5848669e-07, Final residual = 1.9789828e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 6.7817699e-08, Final residual = 1.9804966e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00098954378, Final residual = 7.0326532e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00012949727, Final residual = 1.2633116e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.8034866e-05, Final residual = 2.5232263e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.4022788e-05, Final residual = 2.0184904e-07, No Iterations 6
time step continuity errors : sum local = 3.1186512e-09, global = 2.7840181e-12, cumulative = -1.7507243e-07
ExecutionTime = 123.47 s  ClockTime = 124 s

Time = 142

smoothSolver:  Solving for Ux, Initial residual = 3.5578194e-07, Final residual = 1.966118e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 6.730494e-08, Final residual = 1.9664061e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0009801911, Final residual = 6.9801783e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00012830506, Final residual = 1.2356547e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.7658683e-05, Final residual = 2.3868377e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.40343e-05, Final residual = 6.6935106e-08, No Iterations 4
time step continuity errors : sum local = 1.0346635e-09, global = 2.4608559e-13, cumulative = -1.7507219e-07
ExecutionTime = 124.23 s  ClockTime = 125 s

Time = 143

smoothSolver:  Solving for Ux, Initial residual = 3.5184686e-07, Final residual = 1.9534684e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 6.6543875e-08, Final residual = 1.9523335e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00097086366, Final residual = 6.9435825e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00012701599, Final residual = 1.2196178e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.6986848e-05, Final residual = 2.3831723e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.3504053e-05, Final residual = 6.5759211e-08, No Iterations 4
time step continuity errors : sum local = 1.0161082e-09, global = -9.7675283e-14, cumulative = -1.7507229e-07
ExecutionTime = 125.02 s  ClockTime = 125 s

Time = 144

smoothSolver:  Solving for Ux, Initial residual = 3.4867515e-07, Final residual = 1.9409581e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 6.5966727e-08, Final residual = 1.9386519e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00096181402, Final residual = 6.9205349e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00012609519, Final residual = 1.2143478e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.6405024e-05, Final residual = 2.3608402e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.3420987e-05, Final residual = 2.1458277e-07, No Iterations 5
time step continuity errors : sum local = 3.3153218e-09, global = 2.146179e-12, cumulative = -1.7507014e-07
ExecutionTime = 126.2 s  ClockTime = 126 s

Time = 145

smoothSolver:  Solving for Ux, Initial residual = 3.4586035e-07, Final residual = 1.9285837e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 6.5484204e-08, Final residual = 1.9252563e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00095303756, Final residual = 6.9014627e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00012492055, Final residual = 1.2003062e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.5983444e-05, Final residual = 2.4204547e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.3389685e-05, Final residual = 1.2061482e-07, No Iterations 4
time step continuity errors : sum local = 1.8637565e-09, global = 2.2111691e-12, cumulative = -1.7506793e-07
ExecutionTime = 126.97 s  ClockTime = 127 s

Time = 146

smoothSolver:  Solving for Ux, Initial residual = 3.4396443e-07, Final residual = 1.9162705e-09, No Iterations 3
smoothSolver:  Solving for Uy, Initial residual = 6.5045663e-08, Final residual = 1.9121875e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00094461844, Final residual = 6.8702483e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00012358299, Final residual = 1.1838653e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.558483e-05, Final residual = 2.4934112e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.3549362e-05, Final residual = 1.0864151e-07, No Iterations 4
time step continuity errors : sum local = 1.6786434e-09, global = 2.4178353e-12, cumulative = -1.7506551e-07
ExecutionTime = 127.68 s  ClockTime = 128 s

Time = 147

smoothSolver:  Solving for Ux, Initial residual = 3.4258445e-07, Final residual = 9.9772751e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 6.4749584e-08, Final residual = 1.8996495e-09, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0009347906, Final residual = 6.7661799e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00012222137, Final residual = 1.1739469e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.5431794e-05, Final residual = 2.5268391e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.3707534e-05, Final residual = 1.7576651e-07, No Iterations 4
time step continuity errors : sum local = 2.7158223e-09, global = 2.7184048e-12, cumulative = -1.7506279e-07
ExecutionTime = 128.47 s  ClockTime = 129 s

Time = 148

smoothSolver:  Solving for Ux, Initial residual = 3.3965298e-07, Final residual = 9.913177e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 6.4139307e-08, Final residual = 9.9437604e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00092154326, Final residual = 8.1433634e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00012373164, Final residual = 6.8355712e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.1533275e-05, Final residual = 3.4705293e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.2342573e-05, Final residual = 1.0057601e-07, No Iterations 3
time step continuity errors : sum local = 1.5541891e-09, global = 2.7748226e-13, cumulative = -1.7506252e-07
ExecutionTime = 129.17 s  ClockTime = 129 s

Time = 149

smoothSolver:  Solving for Ux, Initial residual = 3.3589296e-07, Final residual = 9.8138678e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 6.395582e-08, Final residual = 9.8888338e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00090941207, Final residual = 4.0759451e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00013639786, Final residual = 1.0653326e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.8138497e-05, Final residual = 4.2003777e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.3294996e-05, Final residual = 5.615184e-08, No Iterations 4
time step continuity errors : sum local = 8.676477e-10, global = 3.5416775e-13, cumulative = -1.7506216e-07
ExecutionTime = 129.81 s  ClockTime = 130 s

Time = 150

smoothSolver:  Solving for Ux, Initial residual = 3.3196584e-07, Final residual = 9.6944382e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 6.4106829e-08, Final residual = 9.896293e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00089848002, Final residual = 4.2502043e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.00013785853, Final residual = 1.0904362e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.8432551e-05, Final residual = 4.2259416e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.3344453e-05, Final residual = 4.9067333e-08, No Iterations 4
time step continuity errors : sum local = 7.5887604e-10, global = -1.0226868e-13, cumulative = -1.7506226e-07
ExecutionTime = 130.82 s  ClockTime = 131 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660805e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339195e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122684

Time = 151

smoothSolver:  Solving for Ux, Initial residual = 3.2795336e-07, Final residual = 9.5742564e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 6.4301846e-08, Final residual = 9.9179834e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00088889614, Final residual = 3.7432e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 0.0001315735, Final residual = 1.0633735e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.6093231e-05, Final residual = 4.2331708e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.2376266e-05, Final residual = 1.7232962e-07, No Iterations 4
time step continuity errors : sum local = 2.6630398e-09, global = 1.2306333e-12, cumulative = -1.7506103e-07
ExecutionTime = 131.4 s  ClockTime = 132 s

Time = 152

smoothSolver:  Solving for Ux, Initial residual = 3.2419175e-07, Final residual = 9.4691457e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 6.4324458e-08, Final residual = 9.9238056e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00088020165, Final residual = 7.9389325e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00012056964, Final residual = 6.6040011e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.9465173e-05, Final residual = 3.1409357e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.1266426e-05, Final residual = 1.696092e-07, No Iterations 4
time step continuity errors : sum local = 2.620785e-09, global = 1.0682266e-12, cumulative = -1.7505996e-07
ExecutionTime = 132 s  ClockTime = 132 s

Time = 153

smoothSolver:  Solving for Ux, Initial residual = 3.2180148e-07, Final residual = 9.3869999e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 6.4220053e-08, Final residual = 9.8993933e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00087141575, Final residual = 7.0602158e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00011764483, Final residual = 1.0957283e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.4000527e-05, Final residual = 2.5750292e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.2392117e-05, Final residual = 1.9053242e-07, No Iterations 3
time step continuity errors : sum local = 2.9438132e-09, global = 1.0711151e-12, cumulative = -1.7505889e-07
ExecutionTime = 132.67 s  ClockTime = 133 s

Time = 154

smoothSolver:  Solving for Ux, Initial residual = 3.2070164e-07, Final residual = 9.3272722e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 6.3982389e-08, Final residual = 9.8439996e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00086227681, Final residual = 6.6999863e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00011668354, Final residual = 1.0849712e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.3674685e-05, Final residual = 2.3753399e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.2489509e-05, Final residual = 2.2448829e-07, No Iterations 3
time step continuity errors : sum local = 3.4684767e-09, global = 1.2343513e-12, cumulative = -1.7505766e-07
ExecutionTime = 133.26 s  ClockTime = 134 s

Time = 155

smoothSolver:  Solving for Ux, Initial residual = 3.1941524e-07, Final residual = 9.2845194e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 6.3493674e-08, Final residual = 9.7644136e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00085294024, Final residual = 6.8209603e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00011587659, Final residual = 7.3413741e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.6205354e-05, Final residual = 3.9858271e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.0856642e-05, Final residual = 1.8088186e-07, No Iterations 4
time step continuity errors : sum local = 2.7950682e-09, global = 1.6913052e-12, cumulative = -1.7505597e-07
ExecutionTime = 133.87 s  ClockTime = 134 s

Time = 156

smoothSolver:  Solving for Ux, Initial residual = 3.1839662e-07, Final residual = 9.2504581e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 6.2959075e-08, Final residual = 9.6727949e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00084372881, Final residual = 6.7804472e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00011411053, Final residual = 7.5597929e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.5965564e-05, Final residual = 4.1884371e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.0676859e-05, Final residual = 1.976572e-07, No Iterations 4
time step continuity errors : sum local = 3.0542112e-09, global = 1.9692676e-12, cumulative = -1.75054e-07
ExecutionTime = 134.45 s  ClockTime = 135 s

Time = 157

smoothSolver:  Solving for Ux, Initial residual = 3.1686544e-07, Final residual = 9.2170876e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 6.2314332e-08, Final residual = 9.581352e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00083515568, Final residual = 6.4818496e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00011205761, Final residual = 7.6589967e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.5005919e-05, Final residual = 4.2309585e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.0386939e-05, Final residual = 1.6982487e-07, No Iterations 6
time step continuity errors : sum local = 2.6239273e-09, global = 2.6695427e-12, cumulative = -1.7505133e-07
ExecutionTime = 135.09 s  ClockTime = 136 s

Time = 158

smoothSolver:  Solving for Ux, Initial residual = 3.1494123e-07, Final residual = 9.1784957e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 6.1690636e-08, Final residual = 9.4976035e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00082746651, Final residual = 6.1602232e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0001104104, Final residual = 7.5273605e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.3801344e-05, Final residual = 4.1252598e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.0019002e-05, Final residual = 6.7329707e-08, No Iterations 6
time step continuity errors : sum local = 1.040912e-09, global = 2.6157679e-13, cumulative = -1.7505107e-07
ExecutionTime = 135.75 s  ClockTime = 136 s

Time = 159

smoothSolver:  Solving for Ux, Initial residual = 3.1242619e-07, Final residual = 9.1324175e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 6.1069879e-08, Final residual = 9.4255963e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00082018326, Final residual = 6.005557e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00010906503, Final residual = 7.3478199e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.3125688e-05, Final residual = 3.9709513e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.9758931e-05, Final residual = 1.7650943e-07, No Iterations 6
time step continuity errors : sum local = 2.7272399e-09, global = 3.0191025e-12, cumulative = -1.7504805e-07
ExecutionTime = 136.39 s  ClockTime = 137 s

Time = 160

smoothSolver:  Solving for Ux, Initial residual = 3.1053402e-07, Final residual = 9.078939e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 6.0699733e-08, Final residual = 9.3646853e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00081299336, Final residual = 5.962961e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00010773441, Final residual = 7.0121127e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.242329e-05, Final residual = 3.927952e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.9432232e-05, Final residual = 6.4336678e-08, No Iterations 4
time step continuity errors : sum local = 9.9475745e-10, global = -1.5163017e-15, cumulative = -1.7504805e-07
ExecutionTime = 137.09 s  ClockTime = 138 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660805e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339195e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122684

Time = 161

smoothSolver:  Solving for Ux, Initial residual = 3.0849012e-07, Final residual = 9.0201133e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 6.0321383e-08, Final residual = 9.3134484e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00080607633, Final residual = 5.9234467e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00010662908, Final residual = 6.7367781e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.2049078e-05, Final residual = 4.1355592e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.9325486e-05, Final residual = 5.1302533e-08, No Iterations 7
time step continuity errors : sum local = 7.9317801e-10, global = 6.327824e-13, cumulative = -1.7504742e-07
ExecutionTime = 137.79 s  ClockTime = 138 s

Time = 162

smoothSolver:  Solving for Ux, Initial residual = 3.0671989e-07, Final residual = 8.9590025e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 6.0093909e-08, Final residual = 9.2672169e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00079933703, Final residual = 5.866873e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00010561982, Final residual = 1.0489357e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.9915401e-05, Final residual = 3.1750527e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.0219505e-05, Final residual = 2.0149233e-07, No Iterations 4
time step continuity errors : sum local = 3.1135477e-09, global = 2.0563747e-12, cumulative = -1.7504536e-07
ExecutionTime = 138.48 s  ClockTime = 139 s

Time = 163

smoothSolver:  Solving for Ux, Initial residual = 3.042986e-07, Final residual = 8.8985431e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.9735234e-08, Final residual = 9.2219919e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00079263719, Final residual = 5.7949237e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0001046712, Final residual = 1.0197768e-06, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.966799e-05, Final residual = 3.1304374e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.0168552e-05, Final residual = 1.8390364e-07, No Iterations 6
time step continuity errors : sum local = 2.8414039e-09, global = 2.1308798e-12, cumulative = -1.7504323e-07
ExecutionTime = 139.12 s  ClockTime = 140 s

Time = 164

smoothSolver:  Solving for Ux, Initial residual = 3.0320097e-07, Final residual = 8.8407516e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.9535486e-08, Final residual = 9.1749753e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00078615097, Final residual = 5.7235322e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.0001037402, Final residual = 9.8945006e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.907955e-05, Final residual = 2.3001491e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.0167772e-05, Final residual = 1.5804865e-07, No Iterations 4
time step continuity errors : sum local = 2.4424052e-09, global = 2.1156951e-12, cumulative = -1.7504111e-07
ExecutionTime = 139.79 s  ClockTime = 140 s

Time = 165

smoothSolver:  Solving for Ux, Initial residual = 3.0170835e-07, Final residual = 8.7868449e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.9259797e-08, Final residual = 9.1239911e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00077973969, Final residual = 5.6488015e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00010309376, Final residual = 9.7941889e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.8679183e-05, Final residual = 2.0953043e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.9975928e-05, Final residual = 1.5940483e-07, No Iterations 4
time step continuity errors : sum local = 2.4635087e-09, global = 2.4543202e-12, cumulative = -1.7503866e-07
ExecutionTime = 140.43 s  ClockTime = 141 s

Time = 166

smoothSolver:  Solving for Ux, Initial residual = 2.9910993e-07, Final residual = 8.7361604e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.8794525e-08, Final residual = 9.0695652e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00077348393, Final residual = 5.5684794e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00010242394, Final residual = 9.7162969e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.8274792e-05, Final residual = 2.1172179e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.9932437e-05, Final residual = 6.4480824e-08, No Iterations 3
time step continuity errors : sum local = 9.968544e-10, global = 9.9287719e-14, cumulative = -1.7503856e-07
ExecutionTime = 141.14 s  ClockTime = 142 s

Time = 167

smoothSolver:  Solving for Ux, Initial residual = 2.9643374e-07, Final residual = 8.6877972e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.8272084e-08, Final residual = 9.0131375e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00076738582, Final residual = 5.478183e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00010157634, Final residual = 9.7293377e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.7960216e-05, Final residual = 2.3435413e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.9780235e-05, Final residual = 1.6357547e-07, No Iterations 4
time step continuity errors : sum local = 2.5278408e-09, global = 2.3391392e-12, cumulative = -1.7503622e-07
ExecutionTime = 141.8 s  ClockTime = 142 s

Time = 168

smoothSolver:  Solving for Ux, Initial residual = 2.9499767e-07, Final residual = 8.6407936e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.7919074e-08, Final residual = 8.9561623e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00076148906, Final residual = 5.3925328e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.00010065514, Final residual = 9.6972992e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.7754889e-05, Final residual = 2.8740034e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.9534296e-05, Final residual = 1.7641355e-07, No Iterations 4
time step continuity errors : sum local = 2.7260593e-09, global = 2.5097286e-12, cumulative = -1.7503371e-07
ExecutionTime = 142.49 s  ClockTime = 143 s

Time = 169

smoothSolver:  Solving for Ux, Initial residual = 2.9343858e-07, Final residual = 8.5942422e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.7578803e-08, Final residual = 8.9001319e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0007557373, Final residual = 5.3238946e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.9630245e-05, Final residual = 9.6318006e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.7498116e-05, Final residual = 2.8584895e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 1.9394007e-05, Final residual = 7.0899114e-08, No Iterations 3
time step continuity errors : sum local = 1.0958914e-09, global = 1.6717988e-13, cumulative = -1.7503354e-07
ExecutionTime = 143.5 s  ClockTime = 144 s

Time = 170

smoothSolver:  Solving for Ux, Initial residual = 2.9169326e-07, Final residual = 8.5470941e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.719239e-08, Final residual = 8.8459119e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00075004115, Final residual = 5.2687603e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.8589069e-05, Final residual = 9.5333178e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.7023416e-05, Final residual = 3.176774e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 1.8934245e-05, Final residual = 1.6924681e-07, No Iterations 5
time step continuity errors : sum local = 2.6152385e-09, global = 2.4555455e-12, cumulative = -1.7503109e-07
ExecutionTime = 144.17 s  ClockTime = 145 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339195e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122684

Time = 171

smoothSolver:  Solving for Ux, Initial residual = 2.9081135e-07, Final residual = 8.4993041e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.6949974e-08, Final residual = 8.7938698e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00074441617, Final residual = 5.2306737e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.7583321e-05, Final residual = 9.2968057e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.6544754e-05, Final residual = 2.8668236e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 1.8755567e-05, Final residual = 6.5553238e-08, No Iterations 3
time step continuity errors : sum local = 1.0134093e-09, global = 5.2089225e-15, cumulative = -1.7503108e-07
ExecutionTime = 144.78 s  ClockTime = 145 s

Time = 172

smoothSolver:  Solving for Ux, Initial residual = 2.891173e-07, Final residual = 8.4509277e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.6618811e-08, Final residual = 8.7439151e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00073877005, Final residual = 5.1988962e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.6589444e-05, Final residual = 9.1715548e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.6172362e-05, Final residual = 2.7903873e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 1.849204e-05, Final residual = 1.3075144e-07, No Iterations 4
time step continuity errors : sum local = 2.0208072e-09, global = 2.0406407e-12, cumulative = -1.7502904e-07
ExecutionTime = 145.38 s  ClockTime = 146 s

Time = 173

smoothSolver:  Solving for Ux, Initial residual = 2.8731282e-07, Final residual = 8.4024672e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.6274072e-08, Final residual = 8.6959199e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00073325886, Final residual = 5.1784048e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.5892405e-05, Final residual = 9.0025298e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.6001044e-05, Final residual = 2.6972694e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.8414498e-05, Final residual = 1.6325777e-07, No Iterations 6
time step continuity errors : sum local = 2.5227055e-09, global = 1.9991623e-12, cumulative = -1.7502704e-07
ExecutionTime = 146.02 s  ClockTime = 147 s

Time = 174

smoothSolver:  Solving for Ux, Initial residual = 2.8610456e-07, Final residual = 8.3537786e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.6044205e-08, Final residual = 8.6493065e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00072792316, Final residual = 5.1547607e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.5423353e-05, Final residual = 8.924746e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.5863234e-05, Final residual = 1.9917831e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.8614771e-05, Final residual = 1.4698754e-07, No Iterations 4
time step continuity errors : sum local = 2.2713139e-09, global = 2.0764699e-12, cumulative = -1.7502497e-07
ExecutionTime = 146.64 s  ClockTime = 147 s

Time = 175

smoothSolver:  Solving for Ux, Initial residual = 2.842932e-07, Final residual = 8.305538e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.5738642e-08, Final residual = 8.6028733e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00072269934, Final residual = 5.1301989e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.4949084e-05, Final residual = 8.9697964e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.5678815e-05, Final residual = 1.9089944e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.8605522e-05, Final residual = 1.4465323e-07, No Iterations 4
time step continuity errors : sum local = 2.235619e-09, global = 2.3578649e-12, cumulative = -1.7502261e-07
ExecutionTime = 147.23 s  ClockTime = 148 s

Time = 176

smoothSolver:  Solving for Ux, Initial residual = 2.8321768e-07, Final residual = 8.2580313e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.552403e-08, Final residual = 8.5565312e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00071755354, Final residual = 5.1031481e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.4399616e-05, Final residual = 8.9890884e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.5426331e-05, Final residual = 1.7502558e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.8501937e-05, Final residual = 6.5119171e-08, No Iterations 3
time step continuity errors : sum local = 1.0067486e-09, global = 2.1713096e-13, cumulative = -1.7502239e-07
ExecutionTime = 147.82 s  ClockTime = 148 s

Time = 177

smoothSolver:  Solving for Ux, Initial residual = 2.8018545e-07, Final residual = 8.2112628e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.4994068e-08, Final residual = 8.5093812e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.000712376, Final residual = 5.0786616e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.363767e-05, Final residual = 8.9653129e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.5052887e-05, Final residual = 1.8218508e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.8148746e-05, Final residual = 1.2889879e-07, No Iterations 4
time step continuity errors : sum local = 1.9921556e-09, global = 2.493344e-12, cumulative = -1.750199e-07
ExecutionTime = 148.42 s  ClockTime = 149 s

Time = 178

smoothSolver:  Solving for Ux, Initial residual = 2.7847934e-07, Final residual = 8.1653279e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.4688507e-08, Final residual = 8.4619916e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00070729754, Final residual = 5.0781485e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.285793e-05, Final residual = 8.8203814e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4761307e-05, Final residual = 1.7898618e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.8106708e-05, Final residual = 5.7581336e-08, No Iterations 3
time step continuity errors : sum local = 8.9042683e-10, global = 1.257649e-13, cumulative = -1.7501977e-07
ExecutionTime = 149 s  ClockTime = 149 s

Time = 179

smoothSolver:  Solving for Ux, Initial residual = 2.7701554e-07, Final residual = 8.1201729e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.4409376e-08, Final residual = 8.4148329e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00070223086, Final residual = 5.078046e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.2233924e-05, Final residual = 8.8070861e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4744392e-05, Final residual = 2.2242508e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.797641e-05, Final residual = 1.6175759e-07, No Iterations 4
time step continuity errors : sum local = 2.4997165e-09, global = 2.0108352e-12, cumulative = -1.7501776e-07
ExecutionTime = 149.6 s  ClockTime = 150 s

Time = 180

smoothSolver:  Solving for Ux, Initial residual = 2.7533004e-07, Final residual = 8.0757029e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.4071257e-08, Final residual = 8.3675706e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00069728069, Final residual = 5.0561782e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.1487242e-05, Final residual = 8.7960854e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4725144e-05, Final residual = 3.2233393e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.7665955e-05, Final residual = 1.2897219e-07, No Iterations 7
time step continuity errors : sum local = 1.9931995e-09, global = 2.1642345e-12, cumulative = -1.750156e-07
ExecutionTime = 150.24 s  ClockTime = 151 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339195e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122683

Time = 181

smoothSolver:  Solving for Ux, Initial residual = 2.7383956e-07, Final residual = 8.0319566e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.377434e-08, Final residual = 8.3205409e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00069228988, Final residual = 4.9971139e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 9.0681403e-05, Final residual = 8.6883167e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4402942e-05, Final residual = 2.4050159e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.77728e-05, Final residual = 1.6238217e-07, No Iterations 5
time step continuity errors : sum local = 2.5096996e-09, global = 2.2660653e-12, cumulative = -1.7501333e-07
ExecutionTime = 150.85 s  ClockTime = 151 s

Time = 182

smoothSolver:  Solving for Ux, Initial residual = 2.7263796e-07, Final residual = 7.9887984e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.3519833e-08, Final residual = 8.2740438e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00068725803, Final residual = 4.9141871e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.9930936e-05, Final residual = 8.5880421e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4012716e-05, Final residual = 2.0951432e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.7604424e-05, Final residual = 5.4500586e-08, No Iterations 4
time step continuity errors : sum local = 8.4296817e-10, global = 2.8934635e-13, cumulative = -1.7501304e-07
ExecutionTime = 151.47 s  ClockTime = 152 s

Time = 183

smoothSolver:  Solving for Ux, Initial residual = 2.7104622e-07, Final residual = 7.9454493e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.3176828e-08, Final residual = 8.2278682e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00068211348, Final residual = 4.8455045e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.9174967e-05, Final residual = 8.4840147e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.3820391e-05, Final residual = 2.1341152e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.7609328e-05, Final residual = 1.6065275e-07, No Iterations 5
time step continuity errors : sum local = 2.4829221e-09, global = 2.1431933e-12, cumulative = -1.750109e-07
ExecutionTime = 152.11 s  ClockTime = 153 s

Time = 184

smoothSolver:  Solving for Ux, Initial residual = 2.6956386e-07, Final residual = 7.90238e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.2882778e-08, Final residual = 8.1819444e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00067701147, Final residual = 4.7942277e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.8475923e-05, Final residual = 8.4112573e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.3613396e-05, Final residual = 2.0343351e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.7691091e-05, Final residual = 1.5026051e-07, No Iterations 6
time step continuity errors : sum local = 2.3225195e-09, global = 2.2560521e-12, cumulative = -1.7500864e-07
ExecutionTime = 152.96 s  ClockTime = 153 s

Time = 185

smoothSolver:  Solving for Ux, Initial residual = 2.6843645e-07, Final residual = 7.8598836e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.2645334e-08, Final residual = 8.136444e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00067187269, Final residual = 4.7627918e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.7659756e-05, Final residual = 8.3161623e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.3314944e-05, Final residual = 7.2679381e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.6797949e-05, Final residual = 1.4036399e-07, No Iterations 4
time step continuity errors : sum local = 2.1697124e-09, global = 3.2475484e-13, cumulative = -1.7500832e-07
ExecutionTime = 153.89 s  ClockTime = 154 s

Time = 186

smoothSolver:  Solving for Ux, Initial residual = 2.6716601e-07, Final residual = 7.8182813e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.2345369e-08, Final residual = 8.0908169e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00066663589, Final residual = 4.7425192e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.7047236e-05, Final residual = 8.2564515e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.3029584e-05, Final residual = 2.1027994e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.7244401e-05, Final residual = 1.00693e-07, No Iterations 4
time step continuity errors : sum local = 1.5569475e-09, global = 1.9741009e-12, cumulative = -1.7500634e-07
ExecutionTime = 155.13 s  ClockTime = 156 s

Time = 187

smoothSolver:  Solving for Ux, Initial residual = 2.6628785e-07, Final residual = 7.7768984e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.2121511e-08, Final residual = 8.0459964e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00066161491, Final residual = 4.7159567e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.675582e-05, Final residual = 8.2422581e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.2534188e-05, Final residual = 2.0687996e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.7112771e-05, Final residual = 1.6802515e-07, No Iterations 3
time step continuity errors : sum local = 2.5969117e-09, global = 1.940638e-12, cumulative = -1.750044e-07
ExecutionTime = 156.04 s  ClockTime = 157 s

Time = 188

smoothSolver:  Solving for Ux, Initial residual = 2.6379931e-07, Final residual = 7.7360112e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.1708988e-08, Final residual = 8.0018549e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00065658113, Final residual = 4.6746729e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.6320517e-05, Final residual = 8.2027413e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.2265511e-05, Final residual = 2.022595e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.7033119e-05, Final residual = 1.2690298e-07, No Iterations 5
time step continuity errors : sum local = 1.9617371e-09, global = 2.1180793e-12, cumulative = -1.7500229e-07
ExecutionTime = 157.14 s  ClockTime = 158 s

Time = 189

smoothSolver:  Solving for Ux, Initial residual = 2.6241641e-07, Final residual = 7.6954714e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.1438733e-08, Final residual = 7.9591691e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00065184332, Final residual = 4.636073e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.5662136e-05, Final residual = 8.2030943e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.1989063e-05, Final residual = 1.9892299e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.6964233e-05, Final residual = 1.4617907e-07, No Iterations 3
time step continuity errors : sum local = 2.2593854e-09, global = 2.296216e-12, cumulative = -1.7499999e-07
ExecutionTime = 157.87 s  ClockTime = 158 s

Time = 190

smoothSolver:  Solving for Ux, Initial residual = 2.6055247e-07, Final residual = 7.6552111e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.1142064e-08, Final residual = 7.917575e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00064739132, Final residual = 4.5978377e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.4669224e-05, Final residual = 8.1871653e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.1649587e-05, Final residual = 7.4656571e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.6237497e-05, Final residual = 1.3476125e-07, No Iterations 4
time step continuity errors : sum local = 2.0828318e-09, global = 3.3412496e-13, cumulative = -1.7499966e-07
ExecutionTime = 158.59 s  ClockTime = 159 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122683

Time = 191

smoothSolver:  Solving for Ux, Initial residual = 2.5963945e-07, Final residual = 7.6157243e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.0909336e-08, Final residual = 7.8770661e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0006428221, Final residual = 4.5314019e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.3531701e-05, Final residual = 8.0300656e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.1352472e-05, Final residual = 1.956634e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.6410393e-05, Final residual = 6.9573192e-08, No Iterations 3
time step continuity errors : sum local = 1.0758328e-09, global = -9.2555762e-14, cumulative = -1.7499975e-07
ExecutionTime = 159.37 s  ClockTime = 160 s

Time = 192

smoothSolver:  Solving for Ux, Initial residual = 2.5935375e-07, Final residual = 7.5762647e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.0796875e-08, Final residual = 7.8370044e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00063821148, Final residual = 4.4643731e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.2597206e-05, Final residual = 7.9558546e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.1235873e-05, Final residual = 2.413353e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 1.6065983e-05, Final residual = 1.5732054e-07, No Iterations 4
time step continuity errors : sum local = 2.4316878e-09, global = 1.5625734e-12, cumulative = -1.7499819e-07
ExecutionTime = 160.12 s  ClockTime = 161 s

Time = 193

smoothSolver:  Solving for Ux, Initial residual = 2.5659838e-07, Final residual = 7.5364873e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.0334041e-08, Final residual = 7.7980616e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00063369312, Final residual = 4.4160295e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.2220874e-05, Final residual = 7.904913e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.1127049e-05, Final residual = 2.3645334e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 1.6038719e-05, Final residual = 1.4898777e-07, No Iterations 4
time step continuity errors : sum local = 2.3030138e-09, global = 1.4653712e-12, cumulative = -1.7499672e-07
ExecutionTime = 160.79 s  ClockTime = 161 s

Time = 194

smoothSolver:  Solving for Ux, Initial residual = 2.5557896e-07, Final residual = 7.4967627e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 5.0134402e-08, Final residual = 7.7593721e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.000629192, Final residual = 4.3767318e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.1788384e-05, Final residual = 7.8263001e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.0904882e-05, Final residual = 2.3450056e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.5962202e-05, Final residual = 1.4212654e-07, No Iterations 6
time step continuity errors : sum local = 2.1966867e-09, global = 1.529476e-12, cumulative = -1.7499519e-07
ExecutionTime = 161.49 s  ClockTime = 162 s

Time = 195

smoothSolver:  Solving for Ux, Initial residual = 2.5461754e-07, Final residual = 7.4567263e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.9944937e-08, Final residual = 7.7208635e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00062488758, Final residual = 4.3661608e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.1241435e-05, Final residual = 7.7161992e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.0447503e-05, Final residual = 1.7146669e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.5787248e-05, Final residual = 1.3115952e-07, No Iterations 4
time step continuity errors : sum local = 2.0274788e-09, global = 1.6112645e-12, cumulative = -1.7499358e-07
ExecutionTime = 162.18 s  ClockTime = 163 s

Time = 196

smoothSolver:  Solving for Ux, Initial residual = 2.5346965e-07, Final residual = 7.4179101e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.9729067e-08, Final residual = 7.6827208e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0006205226, Final residual = 4.3553119e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.0703099e-05, Final residual = 7.6593098e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.0289486e-05, Final residual = 1.5499301e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.5659731e-05, Final residual = 1.1851156e-07, No Iterations 4
time step continuity errors : sum local = 1.8318982e-09, global = 1.9138714e-12, cumulative = -1.7499167e-07
ExecutionTime = 162.9 s  ClockTime = 163 s

Time = 197

smoothSolver:  Solving for Ux, Initial residual = 2.5143163e-07, Final residual = 7.37918e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.9395424e-08, Final residual = 7.6450591e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00061622408, Final residual = 4.3368141e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 8.0166166e-05, Final residual = 7.5478326e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.0055809e-05, Final residual = 6.3961861e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.5202071e-05, Final residual = 1.1599561e-07, No Iterations 4
time step continuity errors : sum local = 1.79337e-09, global = 2.4932219e-13, cumulative = -1.7499142e-07
ExecutionTime = 163.88 s  ClockTime = 164 s

Time = 198

smoothSolver:  Solving for Ux, Initial residual = 2.4948269e-07, Final residual = 7.340629e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.9075481e-08, Final residual = 7.6075689e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00061204069, Final residual = 4.3045626e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.9511367e-05, Final residual = 7.490724e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.9727012e-05, Final residual = 1.753131e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.5559511e-05, Final residual = 1.2782963e-07, No Iterations 4
time step continuity errors : sum local = 1.9758398e-09, global = 1.780852e-12, cumulative = -1.7498964e-07
ExecutionTime = 164.55 s  ClockTime = 165 s

Time = 199

smoothSolver:  Solving for Ux, Initial residual = 2.481319e-07, Final residual = 7.3025663e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.8828492e-08, Final residual = 7.5697844e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00060802598, Final residual = 4.2608965e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.8821761e-05, Final residual = 7.4456505e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.9535926e-05, Final residual = 1.8134151e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.5402777e-05, Final residual = 1.3085442e-07, No Iterations 7
time step continuity errors : sum local = 2.0226721e-09, global = 1.9614096e-12, cumulative = -1.7498767e-07
ExecutionTime = 165.17 s  ClockTime = 166 s

Time = 200

smoothSolver:  Solving for Ux, Initial residual = 2.4708953e-07, Final residual = 7.2650018e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.8603712e-08, Final residual = 7.5314478e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00060412662, Final residual = 4.2238933e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.8176694e-05, Final residual = 7.3850339e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.9371277e-05, Final residual = 1.7730164e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.5354678e-05, Final residual = 6.5823932e-08, No Iterations 3
time step continuity errors : sum local = 1.0179093e-09, global = -6.7702498e-17, cumulative = -1.7498767e-07
ExecutionTime = 166.16 s  ClockTime = 167 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122683

Time = 201

smoothSolver:  Solving for Ux, Initial residual = 2.4593557e-07, Final residual = 7.2281467e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.8367277e-08, Final residual = 7.4932678e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00060032662, Final residual = 4.1935996e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.7535575e-05, Final residual = 7.3804931e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.9367971e-05, Final residual = 2.4497187e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.5016316e-05, Final residual = 4.7005704e-08, No Iterations 4
time step continuity errors : sum local = 7.2719316e-10, global = -1.0139357e-14, cumulative = -1.7498768e-07
ExecutionTime = 166.82 s  ClockTime = 167 s

Time = 202

smoothSolver:  Solving for Ux, Initial residual = 2.4479305e-07, Final residual = 7.1920634e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.8139402e-08, Final residual = 7.4552542e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00059654965, Final residual = 4.1634202e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.6978768e-05, Final residual = 7.3443914e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.9267153e-05, Final residual = 2.1523092e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 1.5001278e-05, Final residual = 1.4166479e-07, No Iterations 4
time step continuity errors : sum local = 2.1900845e-09, global = 1.2900479e-12, cumulative = -1.7498639e-07
ExecutionTime = 167.58 s  ClockTime = 168 s

Time = 203

smoothSolver:  Solving for Ux, Initial residual = 2.4373443e-07, Final residual = 7.1569042e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.787532e-08, Final residual = 7.417017e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00059277319, Final residual = 4.1393789e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.652701e-05, Final residual = 7.2385918e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.904615e-05, Final residual = 2.6250266e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.480765e-05, Final residual = 1.476031e-07, No Iterations 5
time step continuity errors : sum local = 2.2814186e-09, global = 1.2768505e-12, cumulative = -1.7498512e-07
ExecutionTime = 168.25 s  ClockTime = 169 s

Time = 204

smoothSolver:  Solving for Ux, Initial residual = 2.4276129e-07, Final residual = 7.1226386e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.764949e-08, Final residual = 7.3782879e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00058899233, Final residual = 4.1217776e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.6157539e-05, Final residual = 7.1755679e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.8897224e-05, Final residual = 1.7594121e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.5000242e-05, Final residual = 1.1880578e-07, No Iterations 6
time step continuity errors : sum local = 1.8366965e-09, global = 1.3033753e-12, cumulative = -1.7498381e-07
ExecutionTime = 168.95 s  ClockTime = 170 s

Time = 205

smoothSolver:  Solving for Ux, Initial residual = 2.4174928e-07, Final residual = 7.0889783e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.7429084e-08, Final residual = 7.3392119e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00058522682, Final residual = 4.1062884e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.5993666e-05, Final residual = 7.1213395e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.8859725e-05, Final residual = 1.5820683e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.5066844e-05, Final residual = 1.2410853e-07, No Iterations 4
time step continuity errors : sum local = 1.9187493e-09, global = 1.4221346e-12, cumulative = -1.7498239e-07
ExecutionTime = 169.61 s  ClockTime = 170 s

Time = 206

smoothSolver:  Solving for Ux, Initial residual = 2.4048822e-07, Final residual = 7.0554814e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.7176802e-08, Final residual = 7.3010861e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00058150898, Final residual = 4.0861901e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.5762751e-05, Final residual = 7.1027012e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.8839999e-05, Final residual = 1.5703431e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.5167463e-05, Final residual = 1.195934e-07, No Iterations 4
time step continuity errors : sum local = 1.8487557e-09, global = 1.6989027e-12, cumulative = -1.7498069e-07
ExecutionTime = 170.27 s  ClockTime = 171 s

Time = 207

smoothSolver:  Solving for Ux, Initial residual = 2.397181e-07, Final residual = 7.0221914e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.6995494e-08, Final residual = 7.2640822e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0005779071, Final residual = 4.0620306e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.5389448e-05, Final residual = 7.0790236e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.8756497e-05, Final residual = 1.5105296e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.5134887e-05, Final residual = 1.109137e-07, No Iterations 4
time step continuity errors : sum local = 1.7146815e-09, global = 2.0256705e-12, cumulative = -1.7497867e-07
ExecutionTime = 170.87 s  ClockTime = 172 s

Time = 208

smoothSolver:  Solving for Ux, Initial residual = 2.3784973e-07, Final residual = 6.9890639e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.667056e-08, Final residual = 7.2277366e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00057440708, Final residual = 4.0397286e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.4776223e-05, Final residual = 7.004231e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.8473614e-05, Final residual = 5.9463804e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.4661263e-05, Final residual = 1.294828e-07, No Iterations 4
time step continuity errors : sum local = 2.0020264e-09, global = 4.7131241e-13, cumulative = -1.749782e-07
ExecutionTime = 171.5 s  ClockTime = 172 s

Time = 209

smoothSolver:  Solving for Ux, Initial residual = 2.362592e-07, Final residual = 6.955704e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.6379146e-08, Final residual = 7.1926646e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00057085572, Final residual = 4.0165824e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.4103064e-05, Final residual = 6.9856286e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.8301244e-05, Final residual = 1.5964113e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.4953304e-05, Final residual = 6.4265825e-08, No Iterations 3
time step continuity errors : sum local = 9.9404111e-10, global = 1.6093806e-13, cumulative = -1.7497803e-07
ExecutionTime = 172.12 s  ClockTime = 173 s

Time = 210

smoothSolver:  Solving for Ux, Initial residual = 2.3598579e-07, Final residual = 6.9220575e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.627404e-08, Final residual = 7.158965e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0005672137, Final residual = 3.9934838e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.3338598e-05, Final residual = 6.9124355e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.8146989e-05, Final residual = 2.2715758e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.4492564e-05, Final residual = 1.3439735e-07, No Iterations 5
time step continuity errors : sum local = 2.0775819e-09, global = 1.6423889e-12, cumulative = -1.7497639e-07
ExecutionTime = 172.76 s  ClockTime = 173 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339195e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122682

Time = 211

smoothSolver:  Solving for Ux, Initial residual = 2.3396997e-07, Final residual = 6.8881177e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.5928083e-08, Final residual = 7.1264196e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0005635006, Final residual = 3.9747578e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.3037207e-05, Final residual = 6.8723673e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.7983747e-05, Final residual = 1.8556153e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.4581856e-05, Final residual = 1.1886145e-07, No Iterations 5
time step continuity errors : sum local = 1.8374658e-09, global = 1.6118345e-12, cumulative = -1.7497478e-07
ExecutionTime = 173.39 s  ClockTime = 174 s

Time = 212

smoothSolver:  Solving for Ux, Initial residual = 2.3274461e-07, Final residual = 6.8540828e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.5717199e-08, Final residual = 7.0949035e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00055979123, Final residual = 3.9592358e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.280575e-05, Final residual = 6.8030167e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.7621352e-05, Final residual = 1.719354e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.4382931e-05, Final residual = 1.1588142e-07, No Iterations 5
time step continuity errors : sum local = 1.7915282e-09, global = 1.6822283e-12, cumulative = -1.749731e-07
ExecutionTime = 174.08 s  ClockTime = 175 s

Time = 213

smoothSolver:  Solving for Ux, Initial residual = 2.3165903e-07, Final residual = 6.8200811e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.5539101e-08, Final residual = 7.064297e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00055638648, Final residual = 3.9381781e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.232329e-05, Final residual = 6.689183e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.7106692e-05, Final residual = 1.6545575e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.4186591e-05, Final residual = 1.2117549e-07, No Iterations 5
time step continuity errors : sum local = 1.8733609e-09, global = 1.834407e-12, cumulative = -1.7497126e-07
ExecutionTime = 174.76 s  ClockTime = 175 s

Time = 214

smoothSolver:  Solving for Ux, Initial residual = 2.3059556e-07, Final residual = 6.7861398e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.5358654e-08, Final residual = 7.0338166e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00055321209, Final residual = 3.9102636e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.176273e-05, Final residual = 6.567786e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.6885356e-05, Final residual = 1.6356365e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.4080594e-05, Final residual = 1.4026496e-07, No Iterations 5
time step continuity errors : sum local = 2.1684632e-09, global = 2.0573574e-12, cumulative = -1.7496921e-07
ExecutionTime = 175.45 s  ClockTime = 176 s

Time = 215

smoothSolver:  Solving for Ux, Initial residual = 2.2958039e-07, Final residual = 6.7524826e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.5179493e-08, Final residual = 7.002961e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0005499341, Final residual = 3.8773297e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.1048169e-05, Final residual = 6.4687256e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.6641408e-05, Final residual = 1.6078416e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.3935538e-05, Final residual = 5.9256124e-08, No Iterations 3
time step continuity errors : sum local = 9.1662903e-10, global = 2.7677647e-13, cumulative = -1.7496893e-07
ExecutionTime = 176.09 s  ClockTime = 177 s

Time = 216

smoothSolver:  Solving for Ux, Initial residual = 2.2821888e-07, Final residual = 6.7194632e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.4931146e-08, Final residual = 6.9713096e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00054665998, Final residual = 3.8541531e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 7.036347e-05, Final residual = 6.4045667e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.6444906e-05, Final residual = 5.664041e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.35301e-05, Final residual = 1.3158823e-07, No Iterations 3
time step continuity errors : sum local = 2.0343325e-09, global = 2.6811753e-13, cumulative = -1.7496866e-07
ExecutionTime = 176.74 s  ClockTime = 177 s

Time = 217

smoothSolver:  Solving for Ux, Initial residual = 2.2759151e-07, Final residual = 6.6872196e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.4790074e-08, Final residual = 6.9387713e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00054336427, Final residual = 3.8529377e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.9929126e-05, Final residual = 6.3736584e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.6214149e-05, Final residual = 1.963826e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 1.3530325e-05, Final residual = 1.32631e-07, No Iterations 4
time step continuity errors : sum local = 2.0503974e-09, global = 1.5508725e-12, cumulative = -1.7496711e-07
ExecutionTime = 177.37 s  ClockTime = 178 s

Time = 218

smoothSolver:  Solving for Ux, Initial residual = 2.2637915e-07, Final residual = 6.6560369e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.4532038e-08, Final residual = 6.9057635e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00054002808, Final residual = 3.8489189e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.9698958e-05, Final residual = 6.2698636e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.6090461e-05, Final residual = 1.7424738e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 1.361251e-05, Final residual = 1.0160067e-07, No Iterations 4
time step continuity errors : sum local = 1.570763e-09, global = 1.4365221e-12, cumulative = -1.7496567e-07
ExecutionTime = 178.05 s  ClockTime = 179 s

Time = 219

smoothSolver:  Solving for Ux, Initial residual = 2.2571733e-07, Final residual = 6.6256137e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.4363178e-08, Final residual = 6.8722039e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00053669175, Final residual = 3.8346734e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.9437703e-05, Final residual = 6.2117071e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.6015477e-05, Final residual = 1.868825e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.3597992e-05, Final residual = 1.1850091e-07, No Iterations 5
time step continuity errors : sum local = 1.8322077e-09, global = 1.5039484e-12, cumulative = -1.7496417e-07
ExecutionTime = 178.71 s  ClockTime = 179 s

Time = 220

smoothSolver:  Solving for Ux, Initial residual = 2.2471972e-07, Final residual = 6.5956368e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.4150715e-08, Final residual = 6.8383152e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00053357973, Final residual = 3.8029777e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.9018094e-05, Final residual = 6.1436152e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.6021187e-05, Final residual = 1.5866812e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.3733397e-05, Final residual = 1.135651e-07, No Iterations 6
time step continuity errors : sum local = 1.7559313e-09, global = 1.6019624e-12, cumulative = -1.7496257e-07
ExecutionTime = 179.35 s  ClockTime = 180 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339195e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122682

Time = 221

smoothSolver:  Solving for Ux, Initial residual = 2.2385752e-07, Final residual = 6.5658107e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.3957313e-08, Final residual = 6.8043247e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00053041833, Final residual = 3.7683075e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.864955e-05, Final residual = 6.1225574e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.58567e-05, Final residual = 1.5297394e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.3681184e-05, Final residual = 1.0942461e-07, No Iterations 4
time step continuity errors : sum local = 1.6915798e-09, global = 1.7574175e-12, cumulative = -1.7496081e-07
ExecutionTime = 180.03 s  ClockTime = 181 s

Time = 222

smoothSolver:  Solving for Ux, Initial residual = 2.2268638e-07, Final residual = 6.5361186e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.3723069e-08, Final residual = 6.7703741e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00052724052, Final residual = 3.7387368e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.853668e-05, Final residual = 6.1589919e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.5910305e-05, Final residual = 5.2622502e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.3277794e-05, Final residual = 9.7820456e-08, No Iterations 4
time step continuity errors : sum local = 1.5123805e-09, global = 4.1893964e-13, cumulative = -1.7496039e-07
ExecutionTime = 180.72 s  ClockTime = 181 s

Time = 223

smoothSolver:  Solving for Ux, Initial residual = 2.2101002e-07, Final residual = 6.5069958e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.3404778e-08, Final residual = 6.7367831e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00052407194, Final residual = 3.7131382e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.8387423e-05, Final residual = 6.1657742e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.5919707e-05, Final residual = 1.5834901e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.3815896e-05, Final residual = 1.1310238e-07, No Iterations 4
time step continuity errors : sum local = 1.7487918e-09, global = 1.6950646e-12, cumulative = -1.749587e-07
ExecutionTime = 181.38 s  ClockTime = 182 s

Time = 224

smoothSolver:  Solving for Ux, Initial residual = 2.1985033e-07, Final residual = 6.4781923e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.3183032e-08, Final residual = 6.7043437e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00052097375, Final residual = 3.6855689e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.8032616e-05, Final residual = 6.1588528e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.5754134e-05, Final residual = 1.6183731e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.3722645e-05, Final residual = 1.2275322e-07, No Iterations 6
time step continuity errors : sum local = 1.8979858e-09, global = 1.8147143e-12, cumulative = -1.7495688e-07
ExecutionTime = 182.09 s  ClockTime = 183 s

Time = 225

smoothSolver:  Solving for Ux, Initial residual = 2.1907246e-07, Final residual = 6.4493679e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.3007838e-08, Final residual = 6.672884e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00051801959, Final residual = 3.6621455e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.7534991e-05, Final residual = 6.1224147e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.5492272e-05, Final residual = 1.5854054e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.3541023e-05, Final residual = 1.2381603e-07, No Iterations 6
time step continuity errors : sum local = 1.9141287e-09, global = 1.9720359e-12, cumulative = -1.7495491e-07
ExecutionTime = 182.89 s  ClockTime = 184 s

Time = 226

smoothSolver:  Solving for Ux, Initial residual = 2.1828599e-07, Final residual = 6.4206752e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.2838155e-08, Final residual = 6.6421318e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00051511194, Final residual = 3.6465644e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.6978489e-05, Final residual = 6.075323e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.528733e-05, Final residual = 5.0554312e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2940863e-05, Final residual = 9.0792842e-08, No Iterations 6
time step continuity errors : sum local = 1.4039564e-09, global = 4.8315981e-13, cumulative = -1.7495443e-07
ExecutionTime = 183.99 s  ClockTime = 185 s

Time = 227

smoothSolver:  Solving for Ux, Initial residual = 2.1756891e-07, Final residual = 6.3916049e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.266352e-08, Final residual = 6.6128797e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00051207178, Final residual = 3.6402034e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.6141848e-05, Final residual = 6.0197657e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.4989606e-05, Final residual = 4.9735387e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2683665e-05, Final residual = 1.0031565e-07, No Iterations 4
time step continuity errors : sum local = 1.551004e-09, global = 1.9090321e-13, cumulative = -1.7495424e-07
ExecutionTime = 184.77 s  ClockTime = 185 s

Time = 228

smoothSolver:  Solving for Ux, Initial residual = 2.1625545e-07, Final residual = 6.3622734e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.2465635e-08, Final residual = 6.5843011e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00050895536, Final residual = 3.6357553e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.5508878e-05, Final residual = 5.962136e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.4788916e-05, Final residual = 1.4420024e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2993344e-05, Final residual = 1.0052236e-07, No Iterations 4
time step continuity errors : sum local = 1.5543812e-09, global = 1.2186058e-12, cumulative = -1.7495302e-07
ExecutionTime = 185.52 s  ClockTime = 186 s

Time = 229

smoothSolver:  Solving for Ux, Initial residual = 2.150038e-07, Final residual = 6.3327393e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.2240083e-08, Final residual = 6.5563812e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00050580295, Final residual = 3.6241743e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.5392438e-05, Final residual = 5.9564327e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.468481e-05, Final residual = 1.4540972e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2998752e-05, Final residual = 1.0498141e-07, No Iterations 4
time step continuity errors : sum local = 1.6234081e-09, global = 1.102822e-12, cumulative = -1.7495191e-07
ExecutionTime = 186.32 s  ClockTime = 187 s

Time = 230

smoothSolver:  Solving for Ux, Initial residual = 2.138237e-07, Final residual = 6.303213e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.2037584e-08, Final residual = 6.5294761e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00050272192, Final residual = 3.6166366e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.5194181e-05, Final residual = 5.9137223e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.4529119e-05, Final residual = 1.5118278e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2897464e-05, Final residual = 1.1550216e-07, No Iterations 6
time step continuity errors : sum local = 1.7857091e-09, global = 1.1258517e-12, cumulative = -1.7495079e-07
ExecutionTime = 187.12 s  ClockTime = 188 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122682

Time = 231

smoothSolver:  Solving for Ux, Initial residual = 2.1281451e-07, Final residual = 6.2737358e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.1861552e-08, Final residual = 6.5024114e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00049997753, Final residual = 3.5996024e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.4698587e-05, Final residual = 5.8378476e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.4289405e-05, Final residual = 1.4881424e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2730486e-05, Final residual = 1.0648911e-07, No Iterations 6
time step continuity errors : sum local = 1.6468611e-09, global = 1.2076756e-12, cumulative = -1.7494958e-07
ExecutionTime = 187.92 s  ClockTime = 189 s

Time = 232

smoothSolver:  Solving for Ux, Initial residual = 2.1199575e-07, Final residual = 6.244369e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.1724124e-08, Final residual = 6.4752881e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00049738947, Final residual = 3.5714723e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.4216781e-05, Final residual = 5.7662358e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.408212e-05, Final residual = 1.4101845e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2600398e-05, Final residual = 1.1620986e-07, No Iterations 4
time step continuity errors : sum local = 1.7968449e-09, global = 1.3360502e-12, cumulative = -1.7494825e-07
ExecutionTime = 188.67 s  ClockTime = 189 s

Time = 233

smoothSolver:  Solving for Ux, Initial residual = 2.1090131e-07, Final residual = 6.2156259e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.1544457e-08, Final residual = 6.447862e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00049475008, Final residual = 3.5415786e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.3710491e-05, Final residual = 5.7232701e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.3899051e-05, Final residual = 1.4581681e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2492092e-05, Final residual = 9.8812529e-08, No Iterations 5
time step continuity errors : sum local = 1.527833e-09, global = 1.5564601e-12, cumulative = -1.7494669e-07
ExecutionTime = 189.41 s  ClockTime = 190 s

Time = 234

smoothSolver:  Solving for Ux, Initial residual = 2.0999876e-07, Final residual = 6.187746e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.137367e-08, Final residual = 6.4207552e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00049204321, Final residual = 3.5166877e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.3264508e-05, Final residual = 5.7019453e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.3749447e-05, Final residual = 1.4581473e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2447393e-05, Final residual = 9.2589434e-08, No Iterations 5
time step continuity errors : sum local = 1.4314078e-09, global = 1.8186672e-12, cumulative = -1.7494487e-07
ExecutionTime = 190.22 s  ClockTime = 191 s

Time = 235

smoothSolver:  Solving for Ux, Initial residual = 2.0921938e-07, Final residual = 6.1605188e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.1207654e-08, Final residual = 6.3929714e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0004892889, Final residual = 3.4884776e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.2875395e-05, Final residual = 5.6756638e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.3639641e-05, Final residual = 4.6620977e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.20716e-05, Final residual = 8.1506797e-08, No Iterations 6
time step continuity errors : sum local = 1.2608841e-09, global = 6.5980447e-13, cumulative = -1.7494421e-07
ExecutionTime = 191.03 s  ClockTime = 192 s

Time = 236

smoothSolver:  Solving for Ux, Initial residual = 2.0838989e-07, Final residual = 6.1339401e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.0996784e-08, Final residual = 6.3646251e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00048655384, Final residual = 3.4573157e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.2463429e-05, Final residual = 5.6119202e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.342821e-05, Final residual = 4.6246802e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.190065e-05, Final residual = 1.0561814e-07, No Iterations 4
time step continuity errors : sum local = 1.6331507e-09, global = 4.9085534e-13, cumulative = -1.7494372e-07
ExecutionTime = 191.8 s  ClockTime = 192 s

Time = 237

smoothSolver:  Solving for Ux, Initial residual = 2.077066e-07, Final residual = 6.1076721e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.0848513e-08, Final residual = 6.3358222e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00048380396, Final residual = 3.4301098e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.2080633e-05, Final residual = 5.5579834e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.313808e-05, Final residual = 1.355901e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.220011e-05, Final residual = 4.8358811e-08, No Iterations 3
time step continuity errors : sum local = 7.4830859e-10, global = 1.0440142e-13, cumulative = -1.7494362e-07
ExecutionTime = 192.69 s  ClockTime = 193 s

Time = 238

smoothSolver:  Solving for Ux, Initial residual = 2.0650822e-07, Final residual = 6.0816288e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.0654611e-08, Final residual = 6.3066742e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00048098696, Final residual = 3.4109432e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.1650299e-05, Final residual = 5.5016828e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.3016777e-05, Final residual = 1.389881e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2146298e-05, Final residual = 1.1365068e-07, No Iterations 4
time step continuity errors : sum local = 1.757147e-09, global = 9.9352958e-13, cumulative = -1.7494262e-07
ExecutionTime = 193.38 s  ClockTime = 194 s

Time = 239

smoothSolver:  Solving for Ux, Initial residual = 2.0548724e-07, Final residual = 6.0560741e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.0433645e-08, Final residual = 6.2776852e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00047821423, Final residual = 3.3928436e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.1161193e-05, Final residual = 5.4158896e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.3020099e-05, Final residual = 1.4093667e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.213715e-05, Final residual = 8.6460536e-08, No Iterations 5
time step continuity errors : sum local = 1.3372075e-09, global = 9.0061586e-13, cumulative = -1.7494172e-07
ExecutionTime = 194.1 s  ClockTime = 195 s

Time = 240

smoothSolver:  Solving for Ux, Initial residual = 2.0452322e-07, Final residual = 6.0306825e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.0218214e-08, Final residual = 6.2488915e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00047546639, Final residual = 3.3776329e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.0901561e-05, Final residual = 5.3379662e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.2863568e-05, Final residual = 1.4048713e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2125521e-05, Final residual = 8.7237202e-08, No Iterations 5
time step continuity errors : sum local = 1.3492929e-09, global = 8.790554e-13, cumulative = -1.7494084e-07
ExecutionTime = 194.79 s  ClockTime = 195 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122682

Time = 241

smoothSolver:  Solving for Ux, Initial residual = 2.0365119e-07, Final residual = 6.0051239e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 4.0030937e-08, Final residual = 6.2204438e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00047278186, Final residual = 3.3717659e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.091732e-05, Final residual = 5.2901617e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.273985e-05, Final residual = 1.3571309e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2067902e-05, Final residual = 9.5249552e-08, No Iterations 5
time step continuity errors : sum local = 1.473141e-09, global = 9.2061388e-13, cumulative = -1.7493992e-07
ExecutionTime = 195.6 s  ClockTime = 196 s

Time = 242

smoothSolver:  Solving for Ux, Initial residual = 2.0281534e-07, Final residual = 5.9795763e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.9863674e-08, Final residual = 6.1924452e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00047022058, Final residual = 3.3733263e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.0918219e-05, Final residual = 5.2631126e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.2784662e-05, Final residual = 1.3410929e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.2025476e-05, Final residual = 1.077319e-07, No Iterations 4
time step continuity errors : sum local = 1.6659606e-09, global = 1.0328699e-12, cumulative = -1.7493889e-07
ExecutionTime = 196.34 s  ClockTime = 197 s

Time = 243

smoothSolver:  Solving for Ux, Initial residual = 2.018765e-07, Final residual = 5.9541972e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.9689965e-08, Final residual = 6.1652435e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00046777592, Final residual = 3.3751747e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.0660319e-05, Final residual = 5.2182611e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.2664999e-05, Final residual = 1.3439992e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1910676e-05, Final residual = 1.0725799e-07, No Iterations 4
time step continuity errors : sum local = 1.6585406e-09, global = 1.2120038e-12, cumulative = -1.7493768e-07
ExecutionTime = 197.05 s  ClockTime = 198 s

Time = 244

smoothSolver:  Solving for Ux, Initial residual = 2.0100638e-07, Final residual = 5.928912e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.9527934e-08, Final residual = 6.1390367e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00046533442, Final residual = 3.3724456e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 6.0159321e-05, Final residual = 5.1703383e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.2433373e-05, Final residual = 1.360149e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1819119e-05, Final residual = 5.1816465e-08, No Iterations 3
time step continuity errors : sum local = 8.01825e-10, global = -3.915824e-14, cumulative = -1.7493772e-07
ExecutionTime = 197.74 s  ClockTime = 198 s

Time = 245

smoothSolver:  Solving for Ux, Initial residual = 2.0032633e-07, Final residual = 5.9036358e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.9362575e-08, Final residual = 6.1132791e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00046284214, Final residual = 3.3664128e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.9600549e-05, Final residual = 5.1741389e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.2241216e-05, Final residual = 1.6558389e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1837659e-05, Final residual = 9.9152233e-08, No Iterations 5
time step continuity errors : sum local = 1.5331329e-09, global = 1.2508312e-12, cumulative = -1.7493646e-07
ExecutionTime = 198.5 s  ClockTime = 199 s

Time = 246

smoothSolver:  Solving for Ux, Initial residual = 1.9938614e-07, Final residual = 5.8783896e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.9188689e-08, Final residual = 6.0879652e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00046033946, Final residual = 3.3615254e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.8965824e-05, Final residual = 5.1558189e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.2110894e-05, Final residual = 1.3294584e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1752609e-05, Final residual = 1.0360313e-07, No Iterations 6
time step continuity errors : sum local = 1.6021574e-09, global = 1.3283793e-12, cumulative = -1.7493514e-07
ExecutionTime = 199.34 s  ClockTime = 200 s

Time = 247

smoothSolver:  Solving for Ux, Initial residual = 1.9867755e-07, Final residual = 5.8528268e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.9058162e-08, Final residual = 6.0635596e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00045790685, Final residual = 3.3571781e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.844825e-05, Final residual = 5.1684446e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.1884292e-05, Final residual = 1.2257814e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1538356e-05, Final residual = 8.6575883e-08, No Iterations 4
time step continuity errors : sum local = 1.338949e-09, global = 1.4481326e-12, cumulative = -1.7493369e-07
ExecutionTime = 200.09 s  ClockTime = 201 s

Time = 248

smoothSolver:  Solving for Ux, Initial residual = 1.9777414e-07, Final residual = 5.8270335e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.8905659e-08, Final residual = 6.0397635e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00045547648, Final residual = 3.3500505e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.8273741e-05, Final residual = 5.2285099e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.1804027e-05, Final residual = 1.1678632e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.143976e-05, Final residual = 4.0176772e-08, No Iterations 3
time step continuity errors : sum local = 6.2179662e-10, global = 3.3165737e-13, cumulative = -1.7493336e-07
ExecutionTime = 200.77 s  ClockTime = 201 s

Time = 249

smoothSolver:  Solving for Ux, Initial residual = 1.9663006e-07, Final residual = 5.8010945e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.8708112e-08, Final residual = 6.0155582e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00045313222, Final residual = 3.3348211e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.7905566e-05, Final residual = 5.2574907e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.1701247e-05, Final residual = 1.2182449e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1410757e-05, Final residual = 4.5338215e-08, No Iterations 3
time step continuity errors : sum local = 7.0139308e-10, global = 4.9726156e-14, cumulative = -1.7493331e-07
ExecutionTime = 201.53 s  ClockTime = 202 s

Time = 250

smoothSolver:  Solving for Ux, Initial residual = 1.9649846e-07, Final residual = 5.7755945e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.8653421e-08, Final residual = 5.9916493e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00045094742, Final residual = 3.3144168e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.7526463e-05, Final residual = 5.2636891e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.1583511e-05, Final residual = 1.5143733e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1375671e-05, Final residual = 9.7584996e-08, No Iterations 5
time step continuity errors : sum local = 1.508799e-09, global = 1.1654315e-12, cumulative = -1.7493214e-07
ExecutionTime = 202.77 s  ClockTime = 204 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122682

Time = 251

smoothSolver:  Solving for Ux, Initial residual = 1.9509863e-07, Final residual = 5.7506337e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.8413103e-08, Final residual = 5.9680922e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00044875789, Final residual = 3.294444e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.7140154e-05, Final residual = 5.2071236e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.1329353e-05, Final residual = 1.403024e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1237565e-05, Final residual = 9.1776254e-08, No Iterations 5
time step continuity errors : sum local = 1.4191131e-09, global = 1.1365369e-12, cumulative = -1.74931e-07
ExecutionTime = 203.46 s  ClockTime = 204 s

Time = 252

smoothSolver:  Solving for Ux, Initial residual = 1.9401207e-07, Final residual = 5.726102e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.8230385e-08, Final residual = 5.9441573e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.000446489, Final residual = 3.2730884e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.6698534e-05, Final residual = 5.1277168e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.1032992e-05, Final residual = 1.3024557e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1098538e-05, Final residual = 1.0886685e-07, No Iterations 5
time step continuity errors : sum local = 1.6835719e-09, global = 1.1301724e-12, cumulative = -1.7492987e-07
ExecutionTime = 204.2 s  ClockTime = 205 s

Time = 253

smoothSolver:  Solving for Ux, Initial residual = 1.9327601e-07, Final residual = 5.7017238e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.8092968e-08, Final residual = 5.9197504e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00044416301, Final residual = 3.2541284e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.6268602e-05, Final residual = 5.0661561e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.0822867e-05, Final residual = 1.2693045e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0964854e-05, Final residual = 8.4044316e-08, No Iterations 4
time step continuity errors : sum local = 1.2997362e-09, global = 1.222149e-12, cumulative = -1.7492865e-07
ExecutionTime = 204.84 s  ClockTime = 206 s

Time = 254

smoothSolver:  Solving for Ux, Initial residual = 1.9251171e-07, Final residual = 5.677877e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.7943912e-08, Final residual = 5.8949201e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00044180032, Final residual = 3.2415691e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.590953e-05, Final residual = 4.97616e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.0642627e-05, Final residual = 1.2302879e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0889935e-05, Final residual = 8.2348088e-08, No Iterations 4
time step continuity errors : sum local = 1.273523e-09, global = 1.3758602e-12, cumulative = -1.7492728e-07
ExecutionTime = 205.47 s  ClockTime = 206 s

Time = 255

smoothSolver:  Solving for Ux, Initial residual = 1.9181055e-07, Final residual = 5.6544253e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.7799165e-08, Final residual = 5.8698745e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00043941827, Final residual = 3.2387917e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.5594115e-05, Final residual = 4.9338372e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.0472527e-05, Final residual = 1.1483651e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0761093e-05, Final residual = 3.9057015e-08, No Iterations 3
time step continuity errors : sum local = 6.0464679e-10, global = 3.341148e-13, cumulative = -1.7492694e-07
ExecutionTime = 206.09 s  ClockTime = 207 s

Time = 256

smoothSolver:  Solving for Ux, Initial residual = 1.9087529e-07, Final residual = 5.6311604e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.7601526e-08, Final residual = 5.8449503e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00043704079, Final residual = 3.2422383e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.5269468e-05, Final residual = 4.9070441e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.0294422e-05, Final residual = 1.2158166e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0702073e-05, Final residual = 8.8739231e-08, No Iterations 4
time step continuity errors : sum local = 1.3726523e-09, global = 1.4066407e-12, cumulative = -1.7492554e-07
ExecutionTime = 206.81 s  ClockTime = 208 s

Time = 257

smoothSolver:  Solving for Ux, Initial residual = 1.9016109e-07, Final residual = 5.6078931e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.745906e-08, Final residual = 5.8206092e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00043473271, Final residual = 3.2406868e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.4970615e-05, Final residual = 4.8937425e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.0119519e-05, Final residual = 1.3404018e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0612702e-05, Final residual = 5.2169377e-08, No Iterations 3
time step continuity errors : sum local = 8.0717624e-10, global = -2.8266191e-14, cumulative = -1.7492556e-07
ExecutionTime = 207.48 s  ClockTime = 208 s

Time = 258

smoothSolver:  Solving for Ux, Initial residual = 1.8984208e-07, Final residual = 5.5846532e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.7372283e-08, Final residual = 5.7968772e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0004324716, Final residual = 3.2337387e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.462116e-05, Final residual = 4.9024936e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.0019999e-05, Final residual = 1.281789e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 1.0463558e-05, Final residual = 3.4549605e-08, No Iterations 4
time step continuity errors : sum local = 5.3472603e-10, global = -3.3031946e-14, cumulative = -1.749256e-07
ExecutionTime = 208.17 s  ClockTime = 209 s

Time = 259

smoothSolver:  Solving for Ux, Initial residual = 1.8862607e-07, Final residual = 5.5613437e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.7185753e-08, Final residual = 5.77338e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00043027115, Final residual = 3.2251621e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.4312982e-05, Final residual = 4.8855657e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.9954611e-05, Final residual = 1.6570864e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0466703e-05, Final residual = 9.3309741e-08, No Iterations 5
time step continuity errors : sum local = 1.4430538e-09, global = 7.8855462e-13, cumulative = -1.7492481e-07
ExecutionTime = 208.9 s  ClockTime = 210 s

Time = 260

smoothSolver:  Solving for Ux, Initial residual = 1.8814685e-07, Final residual = 5.5382674e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.7057062e-08, Final residual = 5.7504952e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00042809734, Final residual = 3.2020936e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.3979064e-05, Final residual = 4.853216e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.9827317e-05, Final residual = 1.1603451e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0385481e-05, Final residual = 9.4058169e-08, No Iterations 4
time step continuity errors : sum local = 1.4549119e-09, global = 6.6940171e-13, cumulative = -1.7492414e-07
ExecutionTime = 209.61 s  ClockTime = 210 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122681

Time = 261

smoothSolver:  Solving for Ux, Initial residual = 1.8701212e-07, Final residual = 5.5152593e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.6859905e-08, Final residual = 5.7278192e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00042591705, Final residual = 3.1745602e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.3701167e-05, Final residual = 4.8186019e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.9719539e-05, Final residual = 1.1267201e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0317417e-05, Final residual = 8.2705921e-08, No Iterations 4
time step continuity errors : sum local = 1.2791911e-09, global = 6.4558945e-13, cumulative = -1.7492349e-07
ExecutionTime = 210.36 s  ClockTime = 211 s

Time = 262

smoothSolver:  Solving for Ux, Initial residual = 1.8609586e-07, Final residual = 5.4924259e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.6698412e-08, Final residual = 5.7053912e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00042370451, Final residual = 3.1380843e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.3429474e-05, Final residual = 4.7788442e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.9582235e-05, Final residual = 1.1040015e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0232344e-05, Final residual = 8.2540722e-08, No Iterations 4
time step continuity errors : sum local = 1.2770982e-09, global = 7.0217066e-13, cumulative = -1.7492279e-07
ExecutionTime = 211.01 s  ClockTime = 212 s

Time = 263

smoothSolver:  Solving for Ux, Initial residual = 1.8533251e-07, Final residual = 5.4699159e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.6560047e-08, Final residual = 5.6830844e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00042151224, Final residual = 3.0984734e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.3169206e-05, Final residual = 4.7360793e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.9480908e-05, Final residual = 1.0711936e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.017811e-05, Final residual = 8.3519913e-08, No Iterations 4
time step continuity errors : sum local = 1.2917858e-09, global = 8.1590325e-13, cumulative = -1.7492198e-07
ExecutionTime = 211.78 s  ClockTime = 213 s

Time = 264

smoothSolver:  Solving for Ux, Initial residual = 1.8469004e-07, Final residual = 5.4476786e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.6435736e-08, Final residual = 5.6608668e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00041932528, Final residual = 3.0639603e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.2912742e-05, Final residual = 4.6945155e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.9382332e-05, Final residual = 1.034556e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0131634e-05, Final residual = 5.8233343e-08, No Iterations 4
time step continuity errors : sum local = 9.0111253e-10, global = 1.0126811e-12, cumulative = -1.7492096e-07
ExecutionTime = 212.5 s  ClockTime = 213 s

Time = 265

smoothSolver:  Solving for Ux, Initial residual = 1.8418763e-07, Final residual = 5.4257862e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.6327527e-08, Final residual = 5.6386971e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00041716289, Final residual = 3.037438e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.2649477e-05, Final residual = 4.6387501e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.9310708e-05, Final residual = 1.0246815e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0098878e-05, Final residual = 3.1512713e-08, No Iterations 3
time step continuity errors : sum local = 4.8807026e-10, global = 8.5758294e-14, cumulative = -1.7492088e-07
ExecutionTime = 213.2 s  ClockTime = 214 s

Time = 266

smoothSolver:  Solving for Ux, Initial residual = 1.8296071e-07, Final residual = 5.4040517e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.6120735e-08, Final residual = 5.6164612e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00041500468, Final residual = 3.0181955e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.2417757e-05, Final residual = 4.6017757e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.9227105e-05, Final residual = 1.0747894e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0082792e-05, Final residual = 5.2265797e-08, No Iterations 4
time step continuity errors : sum local = 8.089987e-10, global = 1.0782656e-12, cumulative = -1.749198e-07
ExecutionTime = 214 s  ClockTime = 215 s

Time = 267

smoothSolver:  Solving for Ux, Initial residual = 1.8231809e-07, Final residual = 5.3825447e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.5991018e-08, Final residual = 5.5944644e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00041286177, Final residual = 3.0078746e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.2198255e-05, Final residual = 4.5711855e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.9168965e-05, Final residual = 1.1105209e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0064718e-05, Final residual = 6.3126394e-08, No Iterations 4
time step continuity errors : sum local = 9.7662171e-10, global = 1.1752978e-12, cumulative = -1.7491862e-07
ExecutionTime = 214.73 s  ClockTime = 216 s

Time = 268

smoothSolver:  Solving for Ux, Initial residual = 1.8155672e-07, Final residual = 5.3609838e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.5859911e-08, Final residual = 5.5726432e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00041072163, Final residual = 3.0002642e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.1945709e-05, Final residual = 4.526398e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.9067495e-05, Final residual = 1.156895e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0001432e-05, Final residual = 5.4843949e-08, No Iterations 4
time step continuity errors : sum local = 8.4858949e-10, global = 1.3277472e-12, cumulative = -1.749173e-07
ExecutionTime = 215.52 s  ClockTime = 216 s

Time = 269

smoothSolver:  Solving for Ux, Initial residual = 1.8093173e-07, Final residual = 5.3394408e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.5732315e-08, Final residual = 5.5510215e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00040863777, Final residual = 2.9923114e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.1689686e-05, Final residual = 4.51564e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.8979186e-05, Final residual = 1.8928907e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.5569882e-06, Final residual = 4.5109287e-08, No Iterations 3
time step continuity errors : sum local = 6.9802314e-10, global = 1.1471336e-13, cumulative = -1.7491718e-07
ExecutionTime = 216.34 s  ClockTime = 217 s

Time = 270

smoothSolver:  Solving for Ux, Initial residual = 1.8011448e-07, Final residual = 5.3178101e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.5565389e-08, Final residual = 5.5296311e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00040656232, Final residual = 2.9811252e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.1396733e-05, Final residual = 4.5605443e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.8915381e-05, Final residual = 1.1437494e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.91449e-06, Final residual = 5.3504086e-08, No Iterations 4
time step continuity errors : sum local = 8.2776875e-10, global = 1.2991229e-12, cumulative = -1.7491588e-07
ExecutionTime = 217.12 s  ClockTime = 218 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122681

Time = 271

smoothSolver:  Solving for Ux, Initial residual = 1.7928946e-07, Final residual = 5.2963694e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.5416767e-08, Final residual = 5.508332e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00040453015, Final residual = 2.9707786e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.1072454e-05, Final residual = 4.5484455e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.8843333e-05, Final residual = 1.1192221e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.8608546e-06, Final residual = 5.2130502e-08, No Iterations 4
time step continuity errors : sum local = 8.0661569e-10, global = 1.3625531e-12, cumulative = -1.7491452e-07
ExecutionTime = 217.84 s  ClockTime = 219 s

Time = 272

smoothSolver:  Solving for Ux, Initial residual = 1.7866934e-07, Final residual = 5.2750378e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.5294192e-08, Final residual = 5.4871524e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0004025114, Final residual = 2.9576491e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.0738115e-05, Final residual = 4.5068555e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.8671814e-05, Final residual = 1.8605237e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.4306766e-06, Final residual = 4.0330768e-08, No Iterations 3
time step continuity errors : sum local = 6.2465847e-10, global = 1.0194011e-13, cumulative = -1.7491442e-07
ExecutionTime = 218.52 s  ClockTime = 219 s

Time = 273

smoothSolver:  Solving for Ux, Initial residual = 1.7800085e-07, Final residual = 5.2538025e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.5158718e-08, Final residual = 5.4661447e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00040046041, Final residual = 2.9364706e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.0428676e-05, Final residual = 4.5178122e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.8574349e-05, Final residual = 1.0979182e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.7772967e-06, Final residual = 3.7286241e-08, No Iterations 3
time step continuity errors : sum local = 5.7721023e-10, global = 5.8718232e-14, cumulative = -1.7491436e-07
ExecutionTime = 219.18 s  ClockTime = 220 s

Time = 274

smoothSolver:  Solving for Ux, Initial residual = 1.7775926e-07, Final residual = 5.232836e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.5087326e-08, Final residual = 5.4450573e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00039843163, Final residual = 2.9173032e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 5.0168699e-05, Final residual = 4.5036581e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.8478366e-05, Final residual = 1.3599799e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.7857319e-06, Final residual = 8.0830325e-08, No Iterations 5
time step continuity errors : sum local = 1.2501898e-09, global = 8.7819834e-13, cumulative = -1.7491348e-07
ExecutionTime = 219.89 s  ClockTime = 221 s

Time = 275

smoothSolver:  Solving for Ux, Initial residual = 1.7660137e-07, Final residual = 5.2119802e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.4887427e-08, Final residual = 5.4239482e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00039646284, Final residual = 2.8978775e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.9967834e-05, Final residual = 4.4486496e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.8372276e-05, Final residual = 1.5177478e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.7158934e-06, Final residual = 8.2424144e-08, No Iterations 5
time step continuity errors : sum local = 1.2748279e-09, global = 8.046917e-13, cumulative = -1.7491268e-07
ExecutionTime = 220.59 s  ClockTime = 221 s

Time = 276

smoothSolver:  Solving for Ux, Initial residual = 1.7603326e-07, Final residual = 5.191195e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.4764366e-08, Final residual = 5.4030128e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00039455477, Final residual = 2.8806984e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.9731476e-05, Final residual = 4.3986456e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.8259098e-05, Final residual = 1.1750567e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.6618272e-06, Final residual = 7.9353945e-08, No Iterations 5
time step continuity errors : sum local = 1.227383e-09, global = 7.9792224e-13, cumulative = -1.7491188e-07
ExecutionTime = 221.29 s  ClockTime = 222 s

Time = 277

smoothSolver:  Solving for Ux, Initial residual = 1.752957e-07, Final residual = 5.1704613e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.463052e-08, Final residual = 5.3821943e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00039267786, Final residual = 2.8651711e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.9542622e-05, Final residual = 4.3639582e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.821197e-05, Final residual = 1.1455657e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.6576429e-06, Final residual = 8.8159253e-08, No Iterations 4
time step continuity errors : sum local = 1.3637179e-09, global = 8.6685849e-13, cumulative = -1.7491101e-07
ExecutionTime = 222.04 s  ClockTime = 223 s

Time = 278

smoothSolver:  Solving for Ux, Initial residual = 1.7449138e-07, Final residual = 5.1499673e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.449024e-08, Final residual = 5.3614479e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00039083008, Final residual = 2.8499183e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.9336854e-05, Final residual = 4.3128548e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.8120395e-05, Final residual = 1.1595738e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.6286296e-06, Final residual = 8.2654638e-08, No Iterations 5
time step continuity errors : sum local = 1.2787312e-09, global = 9.7776198e-13, cumulative = -1.7491003e-07
ExecutionTime = 222.75 s  ClockTime = 224 s

Time = 279

smoothSolver:  Solving for Ux, Initial residual = 1.7386646e-07, Final residual = 5.1295561e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.4368881e-08, Final residual = 5.3408872e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00038900279, Final residual = 2.8375374e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.9115072e-05, Final residual = 4.2901691e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.8039721e-05, Final residual = 1.16561e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.5873074e-06, Final residual = 7.8838527e-08, No Iterations 5
time step continuity errors : sum local = 1.21947e-09, global = 1.1296215e-12, cumulative = -1.749089e-07
ExecutionTime = 223.48 s  ClockTime = 224 s

Time = 280

smoothSolver:  Solving for Ux, Initial residual = 1.7324002e-07, Final residual = 5.1092848e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.4246052e-08, Final residual = 5.3204573e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0003872167, Final residual = 2.8254659e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.8833267e-05, Final residual = 4.2700865e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.7953324e-05, Final residual = 1.2030102e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.61233e-06, Final residual = 9.4327739e-08, No Iterations 6
time step continuity errors : sum local = 1.4587361e-09, global = 1.319303e-12, cumulative = -1.7490758e-07
ExecutionTime = 224.19 s  ClockTime = 225 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122681

Time = 281

smoothSolver:  Solving for Ux, Initial residual = 1.7275644e-07, Final residual = 5.0893355e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.4139529e-08, Final residual = 5.3000801e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00038543883, Final residual = 2.817071e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.8553183e-05, Final residual = 4.2047465e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.7889482e-05, Final residual = 3.8239989e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.2067532e-06, Final residual = 7.1791909e-08, No Iterations 4
time step continuity errors : sum local = 1.11079e-09, global = 2.6068292e-13, cumulative = -1.7490732e-07
ExecutionTime = 224.87 s  ClockTime = 226 s

Time = 282

smoothSolver:  Solving for Ux, Initial residual = 1.7169272e-07, Final residual = 5.0694514e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.3946182e-08, Final residual = 5.2799972e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00038360698, Final residual = 2.810534e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.8309483e-05, Final residual = 4.1819933e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.7783674e-05, Final residual = 1.29826e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.5617009e-06, Final residual = 8.4358053e-08, No Iterations 4
time step continuity errors : sum local = 1.304866e-09, global = 1.2472359e-12, cumulative = -1.7490608e-07
ExecutionTime = 225.53 s  ClockTime = 226 s

Time = 283

smoothSolver:  Solving for Ux, Initial residual = 1.7103165e-07, Final residual = 5.0497604e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.3814965e-08, Final residual = 5.2601246e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00038176482, Final residual = 2.8064688e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.8030452e-05, Final residual = 4.1737857e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.7681688e-05, Final residual = 1.3314054e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.5446026e-06, Final residual = 9.0154433e-08, No Iterations 4
time step continuity errors : sum local = 1.394749e-09, global = 1.2992441e-12, cumulative = -1.7490478e-07
ExecutionTime = 226.21 s  ClockTime = 227 s

Time = 284

smoothSolver:  Solving for Ux, Initial residual = 1.705272e-07, Final residual = 5.0303165e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.3711635e-08, Final residual = 5.2403651e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00037994088, Final residual = 2.797595e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.7725737e-05, Final residual = 4.172721e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.7560587e-05, Final residual = 1.2742051e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.477621e-06, Final residual = 3.8406921e-08, No Iterations 3
time step continuity errors : sum local = 5.9440947e-10, global = 3.5361827e-13, cumulative = -1.7490442e-07
ExecutionTime = 227.49 s  ClockTime = 228 s

Time = 285

smoothSolver:  Solving for Ux, Initial residual = 1.6965593e-07, Final residual = 5.0111585e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.3560579e-08, Final residual = 5.2206519e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00037810831, Final residual = 2.7813752e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.7470241e-05, Final residual = 4.149433e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.7462536e-05, Final residual = 1.2974084e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.4821223e-06, Final residual = 8.2466945e-08, No Iterations 6
time step continuity errors : sum local = 1.2757597e-09, global = 1.2386692e-12, cumulative = -1.7490319e-07
ExecutionTime = 228.28 s  ClockTime = 229 s

Time = 286

smoothSolver:  Solving for Ux, Initial residual = 1.6897049e-07, Final residual = 4.9922252e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.3425122e-08, Final residual = 5.2011226e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00037636918, Final residual = 2.7667866e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.7234384e-05, Final residual = 4.1135672e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.7358861e-05, Final residual = 1.296214e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.4181252e-06, Final residual = 9.3307936e-08, No Iterations 4
time step continuity errors : sum local = 1.4433322e-09, global = 1.2240652e-12, cumulative = -1.7490196e-07
ExecutionTime = 229.05 s  ClockTime = 230 s

Time = 287

smoothSolver:  Solving for Ux, Initial residual = 1.6829422e-07, Final residual = 4.9735362e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.3301562e-08, Final residual = 5.1816912e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00037466682, Final residual = 2.7501391e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.7015805e-05, Final residual = 4.0443106e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.7195225e-05, Final residual = 1.2118749e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.3256417e-06, Final residual = 7.7538642e-08, No Iterations 5
time step continuity errors : sum local = 1.1995113e-09, global = 1.3079716e-12, cumulative = -1.7490065e-07
ExecutionTime = 229.85 s  ClockTime = 231 s

Time = 288

smoothSolver:  Solving for Ux, Initial residual = 1.6772738e-07, Final residual = 4.9549104e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.318829e-08, Final residual = 5.1625115e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00037295443, Final residual = 2.7320151e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.6769348e-05, Final residual = 3.9776561e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.7090954e-05, Final residual = 3.531966e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.8561273e-06, Final residual = 5.5117542e-08, No Iterations 6
time step continuity errors : sum local = 8.529186e-10, global = 3.7822849e-13, cumulative = -1.7490027e-07
ExecutionTime = 230.65 s  ClockTime = 232 s

Time = 289

smoothSolver:  Solving for Ux, Initial residual = 1.672625e-07, Final residual = 4.9363323e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.3074341e-08, Final residual = 5.1434334e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00037124821, Final residual = 2.7192111e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.6551826e-05, Final residual = 3.9122435e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.6975068e-05, Final residual = 1.192928e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.1552929e-06, Final residual = 8.5335488e-08, No Iterations 4
time step continuity errors : sum local = 1.3199882e-09, global = 1.1577176e-12, cumulative = -1.7489912e-07
ExecutionTime = 231.41 s  ClockTime = 232 s

Time = 290

smoothSolver:  Solving for Ux, Initial residual = 1.6650983e-07, Final residual = 4.9177255e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.2934576e-08, Final residual = 5.1243493e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00036956572, Final residual = 2.7048176e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.6315917e-05, Final residual = 3.8587293e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.6870516e-05, Final residual = 1.1721807e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.0479544e-06, Final residual = 7.8472522e-08, No Iterations 4
time step continuity errors : sum local = 1.2140744e-09, global = 1.1632405e-12, cumulative = -1.7489795e-07
ExecutionTime = 232.24 s  ClockTime = 233 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122681

Time = 291

smoothSolver:  Solving for Ux, Initial residual = 1.6585494e-07, Final residual = 4.8992581e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.2813535e-08, Final residual = 5.105521e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00036790528, Final residual = 2.6909471e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.6144974e-05, Final residual = 3.8322769e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.6774514e-05, Final residual = 1.1042239e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.9598882e-06, Final residual = 7.5364859e-08, No Iterations 4
time step continuity errors : sum local = 1.1657866e-09, global = 1.2171094e-12, cumulative = -1.7489674e-07
ExecutionTime = 232.98 s  ClockTime = 234 s

Time = 292

smoothSolver:  Solving for Ux, Initial residual = 1.6524322e-07, Final residual = 4.8809697e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.2699969e-08, Final residual = 5.0869013e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00036627101, Final residual = 2.674684e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.5960528e-05, Final residual = 3.8220026e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.6727218e-05, Final residual = 3.6048681e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.5868789e-06, Final residual = 6.8485892e-08, No Iterations 4
time step continuity errors : sum local = 1.059579e-09, global = 2.5825861e-13, cumulative = -1.7489648e-07
ExecutionTime = 233.72 s  ClockTime = 235 s

Time = 293

smoothSolver:  Solving for Ux, Initial residual = 1.6457454e-07, Final residual = 4.8627935e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.2583105e-08, Final residual = 5.0684607e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00036462565, Final residual = 2.6480378e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.5768484e-05, Final residual = 3.8256202e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.6670872e-05, Final residual = 1.1775491e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.915533e-06, Final residual = 3.5361678e-08, No Iterations 3
time step continuity errors : sum local = 5.4743565e-10, global = -3.2934444e-14, cumulative = -1.7489651e-07
ExecutionTime = 234.39 s  ClockTime = 235 s

Time = 294

smoothSolver:  Solving for Ux, Initial residual = 1.6434122e-07, Final residual = 4.8447382e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.2520255e-08, Final residual = 5.0502003e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00036298576, Final residual = 2.6230178e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.5629547e-05, Final residual = 3.8424129e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.6661063e-05, Final residual = 1.3037537e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.9492054e-06, Final residual = 8.7774488e-08, No Iterations 5
time step continuity errors : sum local = 1.3576942e-09, global = 7.1541068e-13, cumulative = -1.748958e-07
ExecutionTime = 235.16 s  ClockTime = 236 s

Time = 295

smoothSolver:  Solving for Ux, Initial residual = 1.6342478e-07, Final residual = 4.8267464e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.2359307e-08, Final residual = 5.0320551e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00036137688, Final residual = 2.6061223e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.5495378e-05, Final residual = 3.8608926e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.6587034e-05, Final residual = 1.3862632e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.9169154e-06, Final residual = 8.1465298e-08, No Iterations 5
time step continuity errors : sum local = 1.2603417e-09, global = 6.5083038e-13, cumulative = -1.7489515e-07
ExecutionTime = 235.9 s  ClockTime = 237 s

Time = 296

smoothSolver:  Solving for Ux, Initial residual = 1.6270487e-07, Final residual = 4.8089674e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.2215713e-08, Final residual = 5.0138955e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0003597722, Final residual = 2.59584e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.5379232e-05, Final residual = 3.8388278e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.6524401e-05, Final residual = 1.3930166e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.8583291e-06, Final residual = 7.1165215e-08, No Iterations 7
time step continuity errors : sum local = 1.1009057e-09, global = 6.3745927e-13, cumulative = -1.7489451e-07
ExecutionTime = 236.67 s  ClockTime = 238 s

Time = 297

smoothSolver:  Solving for Ux, Initial residual = 1.6239155e-07, Final residual = 4.7912279e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.2131448e-08, Final residual = 4.9958923e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00035814634, Final residual = 2.5873282e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.5192363e-05, Final residual = 3.7709551e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.6443876e-05, Final residual = 1.3243e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.7489739e-06, Final residual = 8.3910754e-08, No Iterations 4
time step continuity errors : sum local = 1.2980909e-09, global = 6.4875488e-13, cumulative = -1.7489386e-07
ExecutionTime = 237.38 s  ClockTime = 238 s

Time = 298

smoothSolver:  Solving for Ux, Initial residual = 1.6195411e-07, Final residual = 4.773457e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.2044844e-08, Final residual = 4.978001e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00035651947, Final residual = 2.5762429e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.4930858e-05, Final residual = 3.7545948e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.635531e-05, Final residual = 1.2056835e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.6528249e-06, Final residual = 5.5168973e-08, No Iterations 4
time step continuity errors : sum local = 8.539037e-10, global = 7.9478494e-13, cumulative = -1.7489306e-07
ExecutionTime = 238.22 s  ClockTime = 239 s

Time = 299

smoothSolver:  Solving for Ux, Initial residual = 1.6150203e-07, Final residual = 4.7557915e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.1953603e-08, Final residual = 4.9601771e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00035487824, Final residual = 2.565375e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.4674527e-05, Final residual = 3.7017243e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.6265617e-05, Final residual = 1.1283333e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.5728273e-06, Final residual = 2.9952841e-08, No Iterations 3
time step continuity errors : sum local = 4.6437949e-10, global = -1.2423055e-13, cumulative = -1.7489319e-07
ExecutionTime = 238.97 s  ClockTime = 240 s

Time = 300

smoothSolver:  Solving for Ux, Initial residual = 1.6043653e-07, Final residual = 4.7380823e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.1764846e-08, Final residual = 4.9424319e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00035319902, Final residual = 2.5519001e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.4394622e-05, Final residual = 3.6858907e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.6169297e-05, Final residual = 1.1342826e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.5839419e-06, Final residual = 6.0552929e-08, No Iterations 4
time step continuity errors : sum local = 9.3726872e-10, global = 7.5063239e-13, cumulative = -1.7489244e-07
ExecutionTime = 240.23 s  ClockTime = 241 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122681

Time = 301

smoothSolver:  Solving for Ux, Initial residual = 1.5988458e-07, Final residual = 4.7205316e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.1657208e-08, Final residual = 4.9246872e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00035155646, Final residual = 2.5374079e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.4158447e-05, Final residual = 3.6504495e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.6062638e-05, Final residual = 1.0797574e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.5456302e-06, Final residual = 5.2946728e-08, No Iterations 4
time step continuity errors : sum local = 8.193402e-10, global = 7.9868935e-13, cumulative = -1.7489164e-07
ExecutionTime = 241 s  ClockTime = 242 s

Time = 302

smoothSolver:  Solving for Ux, Initial residual = 1.5940622e-07, Final residual = 4.7029892e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.1562468e-08, Final residual = 4.9070781e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00034992457, Final residual = 2.5215965e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.395582e-05, Final residual = 3.6315273e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5972566e-05, Final residual = 1.0241457e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.5030966e-06, Final residual = 4.3792742e-08, No Iterations 4
time step continuity errors : sum local = 6.7803378e-10, global = 8.8123423e-13, cumulative = -1.7489076e-07
ExecutionTime = 241.73 s  ClockTime = 243 s

Time = 303

smoothSolver:  Solving for Ux, Initial residual = 1.5888828e-07, Final residual = 4.685503e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.1461061e-08, Final residual = 4.8896188e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00034833388, Final residual = 2.5096586e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.3820916e-05, Final residual = 3.6426576e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5917289e-05, Final residual = 1.5906082e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.1762184e-06, Final residual = 6.225031e-08, No Iterations 5
time step continuity errors : sum local = 9.632422e-10, global = 9.6757548e-13, cumulative = -1.7488979e-07
ExecutionTime = 242.5 s  ClockTime = 244 s

Time = 304

smoothSolver:  Solving for Ux, Initial residual = 1.5837556e-07, Final residual = 4.6681437e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.1357923e-08, Final residual = 4.8722356e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00034677806, Final residual = 2.5031978e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.3753752e-05, Final residual = 3.6614194e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5893407e-05, Final residual = 1.5565386e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.1736387e-06, Final residual = 1.992051e-08, No Iterations 4
time step continuity errors : sum local = 3.089416e-10, global = 2.4727804e-13, cumulative = -1.7488954e-07
ExecutionTime = 243.2 s  ClockTime = 244 s

Time = 305

smoothSolver:  Solving for Ux, Initial residual = 1.5736243e-07, Final residual = 4.6508931e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.1189208e-08, Final residual = 4.854914e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00034528376, Final residual = 2.5002225e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.3660048e-05, Final residual = 3.6852278e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5877364e-05, Final residual = 9.4875602e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.4600491e-06, Final residual = 3.1070647e-08, No Iterations 3
time step continuity errors : sum local = 4.8148751e-10, global = 1.5186521e-13, cumulative = -1.7488939e-07
ExecutionTime = 243.93 s  ClockTime = 245 s

Time = 306

smoothSolver:  Solving for Ux, Initial residual = 1.569786e-07, Final residual = 4.6337483e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.1105984e-08, Final residual = 4.8376777e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00034384228, Final residual = 2.4983229e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.3578376e-05, Final residual = 3.7125232e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5804796e-05, Final residual = 1.0227002e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.5099857e-06, Final residual = 7.7097413e-08, No Iterations 4
time step continuity errors : sum local = 1.1927843e-09, global = 8.1321378e-13, cumulative = -1.7488858e-07
ExecutionTime = 244.72 s  ClockTime = 246 s

Time = 307

smoothSolver:  Solving for Ux, Initial residual = 1.5640366e-07, Final residual = 4.6168111e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.097983e-08, Final residual = 4.8203878e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00034240616, Final residual = 2.4996708e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.3479956e-05, Final residual = 3.7062167e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5809541e-05, Final residual = 1.1821497e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.5698059e-06, Final residual = 6.6073966e-08, No Iterations 5
time step continuity errors : sum local = 1.0222886e-09, global = 8.268415e-13, cumulative = -1.7488775e-07
ExecutionTime = 245.49 s  ClockTime = 247 s

Time = 308

smoothSolver:  Solving for Ux, Initial residual = 1.5564082e-07, Final residual = 4.6000752e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.0847389e-08, Final residual = 4.8031779e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00034100157, Final residual = 2.5047743e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.3280928e-05, Final residual = 3.6054394e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.576065e-05, Final residual = 1.166669e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.4838421e-06, Final residual = 6.0132302e-08, No Iterations 5
time step continuity errors : sum local = 9.303698e-10, global = 8.7814469e-13, cumulative = -1.7488687e-07
ExecutionTime = 246.22 s  ClockTime = 247 s

Time = 309

smoothSolver:  Solving for Ux, Initial residual = 1.5553302e-07, Final residual = 4.5834295e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.0803075e-08, Final residual = 4.7861192e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0003396202, Final residual = 2.5183603e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.3087531e-05, Final residual = 3.5999732e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5626842e-05, Final residual = 1.2816137e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.3395664e-06, Final residual = 3.8421362e-08, No Iterations 3
time step continuity errors : sum local = 5.9515868e-10, global = 3.1176752e-13, cumulative = -1.7488656e-07
ExecutionTime = 246.99 s  ClockTime = 248 s

Time = 310

smoothSolver:  Solving for Ux, Initial residual = 1.5456326e-07, Final residual = 4.5667989e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.0632323e-08, Final residual = 4.7691821e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00033820862, Final residual = 2.5393937e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.2952138e-05, Final residual = 3.6898035e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5559101e-05, Final residual = 1.4440285e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.4289744e-06, Final residual = 4.6263904e-08, No Iterations 3
time step continuity errors : sum local = 7.1613887e-10, global = 3.3012601e-13, cumulative = -1.7488623e-07
ExecutionTime = 247.74 s  ClockTime = 249 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122681

Time = 311

smoothSolver:  Solving for Ux, Initial residual = 1.5395419e-07, Final residual = 4.5505461e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.0525425e-08, Final residual = 4.7523132e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00033676846, Final residual = 2.5533092e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.2837098e-05, Final residual = 3.7810101e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5544986e-05, Final residual = 1.1307771e-07, No Iterations 6
GAMG:  Solving for p, Initial residual = 8.4884894e-06, Final residual = 6.3326903e-08, No Iterations 3
time step continuity errors : sum local = 9.8018094e-10, global = 7.520717e-13, cumulative = -1.7488548e-07
ExecutionTime = 248.49 s  ClockTime = 250 s

Time = 312

smoothSolver:  Solving for Ux, Initial residual = 1.5332736e-07, Final residual = 4.5342865e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.0413599e-08, Final residual = 4.7355835e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00033531002, Final residual = 2.5491581e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.262045e-05, Final residual = 3.7935854e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5491235e-05, Final residual = 1.1695702e-07, No Iterations 6
GAMG:  Solving for p, Initial residual = 8.5145234e-06, Final residual = 6.3347807e-08, No Iterations 3
time step continuity errors : sum local = 9.8017431e-10, global = 7.8474952e-13, cumulative = -1.7488469e-07
ExecutionTime = 249.25 s  ClockTime = 250 s

Time = 313

smoothSolver:  Solving for Ux, Initial residual = 1.5283239e-07, Final residual = 4.5181078e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.0320196e-08, Final residual = 4.7188947e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00033384849, Final residual = 2.5392824e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.238035e-05, Final residual = 3.7802835e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5421696e-05, Final residual = 1.2294975e-07, No Iterations 6
GAMG:  Solving for p, Initial residual = 8.5356201e-06, Final residual = 7.582323e-08, No Iterations 4
time step continuity errors : sum local = 1.1731597e-09, global = 8.5996336e-13, cumulative = -1.7488383e-07
ExecutionTime = 250.07 s  ClockTime = 251 s

Time = 314

smoothSolver:  Solving for Ux, Initial residual = 1.5254361e-07, Final residual = 4.5020749e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.0240172e-08, Final residual = 4.7022869e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0003323837, Final residual = 2.5211743e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.2091746e-05, Final residual = 3.7505191e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5339665e-05, Final residual = 1.1305068e-07, No Iterations 6
GAMG:  Solving for p, Initial residual = 8.4401524e-06, Final residual = 4.9025391e-08, No Iterations 3
time step continuity errors : sum local = 7.5904517e-10, global = 5.4346572e-13, cumulative = -1.7488329e-07
ExecutionTime = 250.88 s  ClockTime = 252 s

Time = 315

smoothSolver:  Solving for Ux, Initial residual = 1.5194036e-07, Final residual = 4.4862425e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.0123771e-08, Final residual = 4.6857347e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00033093513, Final residual = 2.4984304e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.1824665e-05, Final residual = 3.6998994e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5229712e-05, Final residual = 1.453322e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.3713667e-06, Final residual = 3.9501573e-08, No Iterations 4
time step continuity errors : sum local = 6.1179063e-10, global = 1.0331188e-12, cumulative = -1.7488226e-07
ExecutionTime = 251.68 s  ClockTime = 253 s

Time = 316

smoothSolver:  Solving for Ux, Initial residual = 1.5165918e-07, Final residual = 4.4706369e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 3.0056819e-08, Final residual = 4.6693132e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00032954921, Final residual = 2.4755946e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.1586356e-05, Final residual = 3.5935516e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.5115549e-05, Final residual = 1.2927041e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.2041728e-06, Final residual = 6.3373697e-08, No Iterations 4
time step continuity errors : sum local = 9.8068484e-10, global = 1.1089178e-12, cumulative = -1.7488115e-07
ExecutionTime = 252.44 s  ClockTime = 254 s

Time = 317

smoothSolver:  Solving for Ux, Initial residual = 1.5125077e-07, Final residual = 4.4551459e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.9970415e-08, Final residual = 4.653092e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00032813525, Final residual = 2.4474792e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.1354024e-05, Final residual = 3.5139276e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4936995e-05, Final residual = 1.0267164e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.0357111e-06, Final residual = 3.1650829e-08, No Iterations 3
time step continuity errors : sum local = 4.9042228e-10, global = 1.7215663e-13, cumulative = -1.7488098e-07
ExecutionTime = 253.14 s  ClockTime = 254 s

Time = 318

smoothSolver:  Solving for Ux, Initial residual = 1.5030778e-07, Final residual = 4.4396395e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.9804753e-08, Final residual = 4.6369355e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00032672129, Final residual = 2.4159279e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.1212402e-05, Final residual = 3.4669521e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.488068e-05, Final residual = 1.0075948e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.9554298e-06, Final residual = 2.7213374e-08, No Iterations 3
time step continuity errors : sum local = 4.2185174e-10, global = 2.9077226e-13, cumulative = -1.7488069e-07
ExecutionTime = 253.81 s  ClockTime = 255 s

Time = 319

smoothSolver:  Solving for Ux, Initial residual = 1.4967309e-07, Final residual = 4.4242657e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.9703624e-08, Final residual = 4.6210361e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00032534499, Final residual = 2.3939439e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.1121064e-05, Final residual = 3.5079519e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4808358e-05, Final residual = 1.0561925e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.9911131e-06, Final residual = 4.5904421e-08, No Iterations 4
time step continuity errors : sum local = 7.1055201e-10, global = 8.6360648e-13, cumulative = -1.7487982e-07
ExecutionTime = 254.54 s  ClockTime = 256 s

Time = 320

smoothSolver:  Solving for Ux, Initial residual = 1.4918636e-07, Final residual = 4.4090142e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.959296e-08, Final residual = 4.6052187e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00032400115, Final residual = 2.3665641e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.1023508e-05, Final residual = 3.4506094e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4745735e-05, Final residual = 1.0387663e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.8795534e-06, Final residual = 4.3194241e-08, No Iterations 4
time step continuity errors : sum local = 6.6871584e-10, global = 8.414796e-13, cumulative = -1.7487898e-07
ExecutionTime = 255.34 s  ClockTime = 256 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122681

Time = 321

smoothSolver:  Solving for Ux, Initial residual = 1.4871654e-07, Final residual = 4.3938256e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.9494554e-08, Final residual = 4.5895999e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00032269385, Final residual = 2.3460691e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.0981709e-05, Final residual = 3.3857212e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4707383e-05, Final residual = 1.0288705e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7655332e-06, Final residual = 4.7827776e-08, No Iterations 4
time step continuity errors : sum local = 7.403417e-10, global = 8.2641386e-13, cumulative = -1.7487815e-07
ExecutionTime = 256.14 s  ClockTime = 257 s

Time = 322

smoothSolver:  Solving for Ux, Initial residual = 1.4800488e-07, Final residual = 4.3786181e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.9378954e-08, Final residual = 4.573995e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00032138234, Final residual = 2.3306986e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.0951073e-05, Final residual = 3.3162655e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4763205e-05, Final residual = 1.0724122e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7456253e-06, Final residual = 2.4038538e-08, No Iterations 4
time step continuity errors : sum local = 3.7271007e-10, global = 7.5021581e-14, cumulative = -1.7487808e-07
ExecutionTime = 256.89 s  ClockTime = 258 s

Time = 323

smoothSolver:  Solving for Ux, Initial residual = 1.4762002e-07, Final residual = 4.3637672e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.9293221e-08, Final residual = 4.5584039e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00032002889, Final residual = 2.3215623e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.0882704e-05, Final residual = 3.2604282e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4797563e-05, Final residual = 1.1373644e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7623555e-06, Final residual = 5.4197938e-08, No Iterations 4
time step continuity errors : sum local = 8.3835851e-10, global = 7.1503095e-13, cumulative = -1.7487736e-07
ExecutionTime = 257.68 s  ClockTime = 259 s

Time = 324

smoothSolver:  Solving for Ux, Initial residual = 1.4714474e-07, Final residual = 4.3489632e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.9190725e-08, Final residual = 4.542863e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00031868645, Final residual = 2.3163262e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.0734721e-05, Final residual = 3.2614332e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.48065e-05, Final residual = 1.2141759e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7892808e-06, Final residual = 5.3439573e-08, No Iterations 4
time step continuity errors : sum local = 8.2707909e-10, global = 7.4317446e-13, cumulative = -1.7487662e-07
ExecutionTime = 258.41 s  ClockTime = 260 s

Time = 325

smoothSolver:  Solving for Ux, Initial residual = 1.4661143e-07, Final residual = 4.3341213e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.9089328e-08, Final residual = 4.527484e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00031734193, Final residual = 2.3125533e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.0501265e-05, Final residual = 3.280837e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4766273e-05, Final residual = 1.2745896e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7977068e-06, Final residual = 5.0833826e-08, No Iterations 4
time step continuity errors : sum local = 7.8674607e-10, global = 8.1131555e-13, cumulative = -1.7487581e-07
ExecutionTime = 259.14 s  ClockTime = 260 s

Time = 326

smoothSolver:  Solving for Ux, Initial residual = 1.4596246e-07, Final residual = 4.3192466e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.8980569e-08, Final residual = 4.5122077e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00031596055, Final residual = 2.3058331e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.0268533e-05, Final residual = 3.3077608e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4703168e-05, Final residual = 1.279343e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7624211e-06, Final residual = 3.7575171e-08, No Iterations 3
time step continuity errors : sum local = 5.8207776e-10, global = 2.775194e-13, cumulative = -1.7487553e-07
ExecutionTime = 259.85 s  ClockTime = 261 s

Time = 327

smoothSolver:  Solving for Ux, Initial residual = 1.4553913e-07, Final residual = 4.3043806e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.8874874e-08, Final residual = 4.4970605e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00031453643, Final residual = 2.2965395e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 4.0027903e-05, Final residual = 3.3837222e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.462153e-05, Final residual = 1.3598163e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7917718e-06, Final residual = 3.473253e-08, No Iterations 4
time step continuity errors : sum local = 5.3808888e-10, global = 8.3666006e-13, cumulative = -1.748747e-07
ExecutionTime = 260.57 s  ClockTime = 262 s

Time = 328

smoothSolver:  Solving for Ux, Initial residual = 1.451752e-07, Final residual = 4.2895921e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.8803393e-08, Final residual = 4.4819634e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00031312596, Final residual = 2.2862946e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.9773476e-05, Final residual = 3.4275029e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4568905e-05, Final residual = 1.2709842e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7372979e-06, Final residual = 3.7907048e-08, No Iterations 3
time step continuity errors : sum local = 5.872699e-10, global = 1.9553775e-13, cumulative = -1.748745e-07
ExecutionTime = 261.32 s  ClockTime = 262 s

Time = 329

smoothSolver:  Solving for Ux, Initial residual = 1.4447225e-07, Final residual = 4.2748107e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.8679054e-08, Final residual = 4.4670657e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00031167792, Final residual = 2.2713568e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.9450876e-05, Final residual = 3.4943236e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4486629e-05, Final residual = 1.3134756e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7758902e-06, Final residual = 3.4000055e-08, No Iterations 4
time step continuity errors : sum local = 5.2685454e-10, global = 7.8013954e-13, cumulative = -1.7487372e-07
ExecutionTime = 262.01 s  ClockTime = 263 s

Time = 330

smoothSolver:  Solving for Ux, Initial residual = 1.4429342e-07, Final residual = 4.2600849e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.8624495e-08, Final residual = 4.4522751e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00031023742, Final residual = 2.2600402e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.9193374e-05, Final residual = 3.5337131e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4379805e-05, Final residual = 1.2147601e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7187077e-06, Final residual = 5.6666486e-08, No Iterations 4
time step continuity errors : sum local = 8.7695588e-10, global = 8.0513556e-13, cumulative = -1.7487291e-07
ExecutionTime = 262.73 s  ClockTime = 264 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122681

Time = 331

smoothSolver:  Solving for Ux, Initial residual = 1.4368126e-07, Final residual = 4.2453552e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.8517142e-08, Final residual = 4.4376819e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00030880965, Final residual = 2.2464084e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.90291e-05, Final residual = 3.5628095e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4263912e-05, Final residual = 1.17376e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7034507e-06, Final residual = 3.6064853e-08, No Iterations 3
time step continuity errors : sum local = 5.5874999e-10, global = 1.7972795e-13, cumulative = -1.7487274e-07
ExecutionTime = 263.45 s  ClockTime = 265 s

Time = 332

smoothSolver:  Solving for Ux, Initial residual = 1.4295265e-07, Final residual = 4.2305591e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.8391676e-08, Final residual = 4.4232513e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.000307377, Final residual = 2.2301527e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.8927384e-05, Final residual = 3.5883978e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4168873e-05, Final residual = 1.2117741e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7580114e-06, Final residual = 6.5395786e-08, No Iterations 4
time step continuity errors : sum local = 1.0118113e-09, global = 7.6452028e-13, cumulative = -1.7487197e-07
ExecutionTime = 264.19 s  ClockTime = 265 s

Time = 333

smoothSolver:  Solving for Ux, Initial residual = 1.4275105e-07, Final residual = 4.2158399e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.833106e-08, Final residual = 4.4089334e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00030600817, Final residual = 2.2166708e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.8820108e-05, Final residual = 3.6114111e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4103489e-05, Final residual = 1.0934315e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7279495e-06, Final residual = 6.7789066e-08, No Iterations 4
time step continuity errors : sum local = 1.0489279e-09, global = 7.9036941e-13, cumulative = -1.7487118e-07
ExecutionTime = 264.92 s  ClockTime = 266 s

Time = 334

smoothSolver:  Solving for Ux, Initial residual = 1.4248866e-07, Final residual = 4.2011111e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.827348e-08, Final residual = 4.3947118e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00030479048, Final residual = 2.2103394e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.8796031e-05, Final residual = 3.620547e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4019931e-05, Final residual = 9.9934353e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.6251476e-06, Final residual = 2.6373934e-08, No Iterations 3
time step continuity errors : sum local = 4.0894226e-10, global = 8.3685224e-14, cumulative = -1.748711e-07
ExecutionTime = 265.66 s  ClockTime = 267 s

Time = 335

smoothSolver:  Solving for Ux, Initial residual = 1.4169436e-07, Final residual = 4.1864284e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.8134864e-08, Final residual = 4.3804902e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00030369477, Final residual = 2.2136151e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.8775915e-05, Final residual = 3.6267856e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4016554e-05, Final residual = 1.104723e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.665e-06, Final residual = 5.3626535e-08, No Iterations 4
time step continuity errors : sum local = 8.3039001e-10, global = 7.4705793e-13, cumulative = -1.7487035e-07
ExecutionTime = 266.37 s  ClockTime = 267 s

Time = 336

smoothSolver:  Solving for Ux, Initial residual = 1.4139659e-07, Final residual = 4.1718878e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.8063934e-08, Final residual = 4.3663762e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00030266035, Final residual = 2.2270636e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.8803193e-05, Final residual = 3.6211311e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.404919e-05, Final residual = 1.087366e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.6159155e-06, Final residual = 3.49061e-08, No Iterations 3
time step continuity errors : sum local = 5.4079959e-10, global = 1.1116909e-13, cumulative = -1.7487024e-07
ExecutionTime = 267.09 s  ClockTime = 268 s

Time = 337

smoothSolver:  Solving for Ux, Initial residual = 1.4067795e-07, Final residual = 4.1575513e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.7949316e-08, Final residual = 4.352346e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00030168916, Final residual = 2.2460359e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.8751355e-05, Final residual = 3.447529e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4229593e-05, Final residual = 1.0571312e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.6534437e-06, Final residual = 6.5252162e-08, No Iterations 4
time step continuity errors : sum local = 1.0095453e-09, global = 6.0484538e-13, cumulative = -1.7486963e-07
ExecutionTime = 267.82 s  ClockTime = 269 s

Time = 338

smoothSolver:  Solving for Ux, Initial residual = 1.4027752e-07, Final residual = 4.1432669e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.7862435e-08, Final residual = 4.3383192e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00030072738, Final residual = 2.2801166e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.8650884e-05, Final residual = 3.4700411e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4220112e-05, Final residual = 1.3027443e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.6484697e-06, Final residual = 5.6235671e-08, No Iterations 4
time step continuity errors : sum local = 8.70444e-10, global = 6.2656698e-13, cumulative = -1.7486901e-07
ExecutionTime = 268.58 s  ClockTime = 270 s

Time = 339

smoothSolver:  Solving for Ux, Initial residual = 1.3966957e-07, Final residual = 4.1292721e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.7763713e-08, Final residual = 4.3241982e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00029978385, Final residual = 2.3281152e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.8521688e-05, Final residual = 3.694949e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4120998e-05, Final residual = 1.0727996e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 8.1581219e-06, Final residual = 5.9704413e-08, No Iterations 3
time step continuity errors : sum local = 9.2400741e-10, global = 6.6243243e-13, cumulative = -1.7486834e-07
ExecutionTime = 269.34 s  ClockTime = 270 s

Time = 340

smoothSolver:  Solving for Ux, Initial residual = 1.3920132e-07, Final residual = 4.1158179e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.7687272e-08, Final residual = 4.3099803e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00029874889, Final residual = 2.3664e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.8517674e-05, Final residual = 3.7806219e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.4077782e-05, Final residual = 1.3377558e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 8.3750468e-06, Final residual = 6.4848894e-08, No Iterations 3
time step continuity errors : sum local = 1.003819e-09, global = 7.2735871e-13, cumulative = -1.7486762e-07
ExecutionTime = 270.11 s  ClockTime = 271 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122681

Time = 341

smoothSolver:  Solving for Ux, Initial residual = 1.3884504e-07, Final residual = 4.1022393e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.7610301e-08, Final residual = 4.2958476e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00029758968, Final residual = 2.3697574e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.8338647e-05, Final residual = 3.715649e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3980755e-05, Final residual = 7.8349207e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 8.1242324e-06, Final residual = 5.6442632e-08, No Iterations 3
time step continuity errors : sum local = 8.7377008e-10, global = 8.2332857e-13, cumulative = -1.7486679e-07
ExecutionTime = 270.96 s  ClockTime = 272 s

Time = 342

smoothSolver:  Solving for Ux, Initial residual = 1.3829077e-07, Final residual = 4.0885837e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.7514323e-08, Final residual = 4.2817861e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00029636795, Final residual = 2.3702177e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.8108803e-05, Final residual = 3.7017859e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3894279e-05, Final residual = 7.6614321e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 8.1086281e-06, Final residual = 5.9823026e-08, No Iterations 3
time step continuity errors : sum local = 9.2606075e-10, global = 9.4968094e-13, cumulative = -1.7486584e-07
ExecutionTime = 271.76 s  ClockTime = 273 s

Time = 343

smoothSolver:  Solving for Ux, Initial residual = 1.3785869e-07, Final residual = 4.0751624e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.7429611e-08, Final residual = 4.2677171e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00029509371, Final residual = 2.3595453e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.788581e-05, Final residual = 3.6797895e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3819211e-05, Final residual = 1.3295608e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 8.3006401e-06, Final residual = 6.408007e-08, No Iterations 3
time step continuity errors : sum local = 9.9199102e-10, global = 1.1059533e-12, cumulative = -1.7486474e-07
ExecutionTime = 272.85 s  ClockTime = 274 s

Time = 344

smoothSolver:  Solving for Ux, Initial residual = 1.3738545e-07, Final residual = 4.0619129e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.7347426e-08, Final residual = 4.2535933e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00029376858, Final residual = 2.3381528e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.759544e-05, Final residual = 3.6057151e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3761517e-05, Final residual = 3.0913805e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.7903145e-06, Final residual = 4.7293521e-08, No Iterations 4
time step continuity errors : sum local = 7.3236949e-10, global = 2.80502e-13, cumulative = -1.7486446e-07
ExecutionTime = 273.72 s  ClockTime = 275 s

Time = 345

smoothSolver:  Solving for Ux, Initial residual = 1.3714022e-07, Final residual = 4.0486556e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.7265182e-08, Final residual = 4.2396236e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00029254839, Final residual = 2.3151336e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.7379452e-05, Final residual = 3.5020556e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3656153e-05, Final residual = 1.1289104e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.8339757e-06, Final residual = 5.7530405e-08, No Iterations 3
time step continuity errors : sum local = 8.9031382e-10, global = 1.0489652e-12, cumulative = -1.7486341e-07
ExecutionTime = 274.48 s  ClockTime = 276 s

Time = 346

smoothSolver:  Solving for Ux, Initial residual = 1.365948e-07, Final residual = 4.0354614e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.7162991e-08, Final residual = 4.2256017e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00029132655, Final residual = 2.2852904e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.7180962e-05, Final residual = 3.3965375e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3575477e-05, Final residual = 2.5593531e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.4811202e-06, Final residual = 3.598575e-08, No Iterations 4
time step continuity errors : sum local = 5.5743273e-10, global = 2.3631317e-13, cumulative = -1.7486317e-07
ExecutionTime = 275.29 s  ClockTime = 276 s

Time = 347

smoothSolver:  Solving for Ux, Initial residual = 1.3659639e-07, Final residual = 4.022269e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.714235e-08, Final residual = 4.2119566e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00029012039, Final residual = 2.2552419e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.7018083e-05, Final residual = 3.2316888e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3407503e-05, Final residual = 1.0627252e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.3337571e-06, Final residual = 2.6160403e-08, No Iterations 3
time step continuity errors : sum local = 4.0564903e-10, global = 7.1611428e-14, cumulative = -1.748631e-07
ExecutionTime = 276.26 s  ClockTime = 277 s

Time = 348

smoothSolver:  Solving for Ux, Initial residual = 1.360158e-07, Final residual = 4.0091357e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.7042906e-08, Final residual = 4.1983611e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00028892553, Final residual = 2.2225705e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.6938728e-05, Final residual = 3.3221892e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.328356e-05, Final residual = 1.0559517e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.2676977e-06, Final residual = 3.757036e-08, No Iterations 4
time step continuity errors : sum local = 5.8176112e-10, global = 5.4307529e-13, cumulative = -1.7486256e-07
ExecutionTime = 277.02 s  ClockTime = 278 s

Time = 349

smoothSolver:  Solving for Ux, Initial residual = 1.3548434e-07, Final residual = 3.9963239e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.6935127e-08, Final residual = 4.1848427e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.000287803, Final residual = 2.201235e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.6895051e-05, Final residual = 3.4025546e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3231631e-05, Final residual = 1.0594885e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.2902511e-06, Final residual = 4.9582625e-08, No Iterations 4
time step continuity errors : sum local = 7.6778432e-10, global = 4.1259872e-13, cumulative = -1.7486214e-07
ExecutionTime = 277.7 s  ClockTime = 279 s

Time = 350

smoothSolver:  Solving for Ux, Initial residual = 1.3479089e-07, Final residual = 3.9837134e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.6810802e-08, Final residual = 4.1713776e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00028671383, Final residual = 2.1570659e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.6819011e-05, Final residual = 3.3438629e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3132761e-05, Final residual = 1.1420967e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.177883e-06, Final residual = 5.8026974e-08, No Iterations 4
time step continuity errors : sum local = 8.9796044e-10, global = 3.6185955e-13, cumulative = -1.7486178e-07
ExecutionTime = 278.81 s  ClockTime = 280 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012268

Time = 351

smoothSolver:  Solving for Ux, Initial residual = 1.342111e-07, Final residual = 3.9710739e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.67085e-08, Final residual = 4.1581623e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0002857399, Final residual = 2.1201618e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.6794061e-05, Final residual = 3.231078e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3165117e-05, Final residual = 1.2198802e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.1230216e-06, Final residual = 6.9839243e-08, No Iterations 5
time step continuity errors : sum local = 1.08084e-09, global = 3.8304482e-13, cumulative = -1.748614e-07
ExecutionTime = 279.44 s  ClockTime = 281 s

Time = 352

smoothSolver:  Solving for Ux, Initial residual = 1.3378327e-07, Final residual = 3.958518e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.6620893e-08, Final residual = 4.1450077e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00028476242, Final residual = 2.1077114e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.6785211e-05, Final residual = 3.0851437e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3284591e-05, Final residual = 1.2903209e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.0823918e-06, Final residual = 6.0546457e-08, No Iterations 5
time step continuity errors : sum local = 9.3698232e-10, global = 4.1616672e-13, cumulative = -1.7486098e-07
ExecutionTime = 280.22 s  ClockTime = 282 s

Time = 353

smoothSolver:  Solving for Ux, Initial residual = 1.3338707e-07, Final residual = 3.9460723e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.6541208e-08, Final residual = 4.1318759e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00028373963, Final residual = 2.1053114e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.6689409e-05, Final residual = 3.0234889e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.33088e-05, Final residual = 9.3958955e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.3541287e-06, Final residual = 5.5252142e-08, No Iterations 3
time step continuity errors : sum local = 8.5522241e-10, global = 4.9202541e-13, cumulative = -1.7486049e-07
ExecutionTime = 280.94 s  ClockTime = 282 s

Time = 354

smoothSolver:  Solving for Ux, Initial residual = 1.331617e-07, Final residual = 3.9338843e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.6477793e-08, Final residual = 4.1187576e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00028269353, Final residual = 2.1102656e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.6530623e-05, Final residual = 3.0281753e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3317795e-05, Final residual = 1.3314725e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.6309034e-06, Final residual = 5.3711423e-08, No Iterations 6
time step continuity errors : sum local = 8.3108988e-10, global = 5.9739656e-13, cumulative = -1.7485989e-07
ExecutionTime = 281.71 s  ClockTime = 283 s

Time = 355

smoothSolver:  Solving for Ux, Initial residual = 1.3263314e-07, Final residual = 3.9215346e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.6384013e-08, Final residual = 4.1057701e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0002816495, Final residual = 2.1175346e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.6336264e-05, Final residual = 3.071372e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3309629e-05, Final residual = 8.4221589e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 7.2245263e-06, Final residual = 4.7186439e-08, No Iterations 3
time step continuity errors : sum local = 7.3062853e-10, global = 7.1357363e-13, cumulative = -1.7485918e-07
ExecutionTime = 282.42 s  ClockTime = 284 s

Time = 356

smoothSolver:  Solving for Ux, Initial residual = 1.3240207e-07, Final residual = 3.9090538e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.6318239e-08, Final residual = 4.0929563e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00028057668, Final residual = 2.1234564e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.6152354e-05, Final residual = 3.1705725e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3296246e-05, Final residual = 2.6642348e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.103089e-06, Final residual = 4.9214637e-08, No Iterations 4
time step continuity errors : sum local = 7.616866e-10, global = 4.6548732e-14, cumulative = -1.7485913e-07
ExecutionTime = 283.11 s  ClockTime = 284 s

Time = 357

smoothSolver:  Solving for Ux, Initial residual = 1.3205793e-07, Final residual = 3.896503e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.6229365e-08, Final residual = 4.080203e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00027950194, Final residual = 2.1310049e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.5991347e-05, Final residual = 3.2323591e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3217563e-05, Final residual = 1.0794534e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.3262534e-06, Final residual = 5.4040014e-08, No Iterations 3
time step continuity errors : sum local = 8.3658789e-10, global = 6.951146e-13, cumulative = -1.7485844e-07
ExecutionTime = 283.95 s  ClockTime = 285 s

Time = 358

smoothSolver:  Solving for Ux, Initial residual = 1.316124e-07, Final residual = 3.8838416e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.6144178e-08, Final residual = 4.0674749e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00027836269, Final residual = 2.1338454e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.5813615e-05, Final residual = 3.3140677e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.319529e-05, Final residual = 1.0492367e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.4306925e-06, Final residual = 5.4731654e-08, No Iterations 3
time step continuity errors : sum local = 8.4707787e-10, global = 7.2905702e-13, cumulative = -1.7485771e-07
ExecutionTime = 284.74 s  ClockTime = 286 s

Time = 359

smoothSolver:  Solving for Ux, Initial residual = 1.3126408e-07, Final residual = 3.8711102e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.6075096e-08, Final residual = 4.054778e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00027720053, Final residual = 2.1327964e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.5586079e-05, Final residual = 3.3915282e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3159491e-05, Final residual = 1.018705e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.4963014e-06, Final residual = 5.4077931e-08, No Iterations 3
time step continuity errors : sum local = 8.3681702e-10, global = 7.8994507e-13, cumulative = -1.7485692e-07
ExecutionTime = 285.46 s  ClockTime = 287 s

Time = 360

smoothSolver:  Solving for Ux, Initial residual = 1.3092597e-07, Final residual = 3.8583219e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.6009506e-08, Final residual = 4.0421888e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00027602829, Final residual = 2.1271895e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.5425443e-05, Final residual = 3.4360947e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3068292e-05, Final residual = 2.4110818e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.2720049e-06, Final residual = 4.0318885e-08, No Iterations 4
time step continuity errors : sum local = 6.2442864e-10, global = 1.8523969e-13, cumulative = -1.7485673e-07
ExecutionTime = 286.13 s  ClockTime = 287 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012268

Time = 361

smoothSolver:  Solving for Ux, Initial residual = 1.3077513e-07, Final residual = 3.8455139e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.596846e-08, Final residual = 4.0298834e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00027488753, Final residual = 2.1170581e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.5384191e-05, Final residual = 3.4111335e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2933059e-05, Final residual = 1.2745339e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.2722792e-06, Final residual = 4.2341339e-08, No Iterations 4
time step continuity errors : sum local = 6.5569934e-10, global = 7.1825931e-13, cumulative = -1.7485602e-07
ExecutionTime = 286.87 s  ClockTime = 288 s

Time = 362

smoothSolver:  Solving for Ux, Initial residual = 1.3032098e-07, Final residual = 3.8326063e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.589011e-08, Final residual = 4.0177198e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00027374051, Final residual = 2.103666e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.5365683e-05, Final residual = 3.3889318e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2855799e-05, Final residual = 1.1819675e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.2714024e-06, Final residual = 4.2746175e-08, No Iterations 4
time step continuity errors : sum local = 6.6206707e-10, global = 7.3858341e-13, cumulative = -1.7485528e-07
ExecutionTime = 287.53 s  ClockTime = 289 s

Time = 363

smoothSolver:  Solving for Ux, Initial residual = 1.2983631e-07, Final residual = 3.8196125e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.580636e-08, Final residual = 4.005597e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00027273048, Final residual = 2.0914303e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.5291846e-05, Final residual = 3.3984038e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.275488e-05, Final residual = 1.119756e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.2483244e-06, Final residual = 4.7180123e-08, No Iterations 4
time step continuity errors : sum local = 7.3040115e-10, global = 8.0064699e-13, cumulative = -1.7485448e-07
ExecutionTime = 288.16 s  ClockTime = 289 s

Time = 364

smoothSolver:  Solving for Ux, Initial residual = 1.2953126e-07, Final residual = 3.8066044e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.5745305e-08, Final residual = 3.993532e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00027185541, Final residual = 2.0867514e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.5362489e-05, Final residual = 3.4168084e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2680748e-05, Final residual = 1.0560962e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.1747261e-06, Final residual = 3.2198362e-08, No Iterations 3
time step continuity errors : sum local = 4.9859419e-10, global = 3.6275359e-13, cumulative = -1.7485411e-07
ExecutionTime = 288.89 s  ClockTime = 290 s

Time = 365

smoothSolver:  Solving for Ux, Initial residual = 1.287809e-07, Final residual = 3.7938427e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.5614005e-08, Final residual = 3.9815157e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00027108665, Final residual = 2.0948534e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.5521078e-05, Final residual = 3.4408546e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2714624e-05, Final residual = 1.2045224e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.2350364e-06, Final residual = 3.1849252e-08, No Iterations 3
time step continuity errors : sum local = 4.936349e-10, global = 3.0633096e-13, cumulative = -1.7485381e-07
ExecutionTime = 289.61 s  ClockTime = 291 s

Time = 366

smoothSolver:  Solving for Ux, Initial residual = 1.2819428e-07, Final residual = 3.7814562e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.551222e-08, Final residual = 3.9696627e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00027032268, Final residual = 2.1103444e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.5710264e-05, Final residual = 3.4571976e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2831551e-05, Final residual = 1.0119518e-07, No Iterations 6
GAMG:  Solving for p, Initial residual = 7.2751494e-06, Final residual = 5.5414963e-08, No Iterations 4
time step continuity errors : sum local = 8.5794264e-10, global = 7.0299882e-13, cumulative = -1.7485311e-07
ExecutionTime = 290.36 s  ClockTime = 292 s

Time = 367

smoothSolver:  Solving for Ux, Initial residual = 1.2799124e-07, Final residual = 3.7692428e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.5456515e-08, Final residual = 3.9578441e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00026960422, Final residual = 2.1357313e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.5705574e-05, Final residual = 3.2488517e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3053391e-05, Final residual = 1.2995447e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.3772061e-06, Final residual = 6.3587553e-08, No Iterations 5
time step continuity errors : sum local = 9.8395398e-10, global = 7.5375856e-13, cumulative = -1.7485235e-07
ExecutionTime = 291.11 s  ClockTime = 292 s

Time = 368

smoothSolver:  Solving for Ux, Initial residual = 1.2796477e-07, Final residual = 3.7572143e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.5431188e-08, Final residual = 3.9459213e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00026886919, Final residual = 2.1844944e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.5619013e-05, Final residual = 3.2709865e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3073511e-05, Final residual = 9.1311274e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 7.286338e-06, Final residual = 6.2439751e-08, No Iterations 3
time step continuity errors : sum local = 9.6637814e-10, global = 7.8979395e-13, cumulative = -1.7485156e-07
ExecutionTime = 291.87 s  ClockTime = 293 s

Time = 369

smoothSolver:  Solving for Ux, Initial residual = 1.2769975e-07, Final residual = 3.7455131e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.5380606e-08, Final residual = 3.9339513e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00026817714, Final residual = 2.2455835e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.5490461e-05, Final residual = 3.4319246e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.3003706e-05, Final residual = 1.2505948e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.8304788e-06, Final residual = 6.3802196e-08, No Iterations 3
time step continuity errors : sum local = 9.8728202e-10, global = 8.3814364e-13, cumulative = -1.7485072e-07
ExecutionTime = 292.63 s  ClockTime = 294 s

Time = 370

smoothSolver:  Solving for Ux, Initial residual = 1.2693153e-07, Final residual = 3.7340863e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.5261856e-08, Final residual = 3.9218961e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00026737463, Final residual = 2.290392e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.5573031e-05, Final residual = 3.3607464e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2997873e-05, Final residual = 1.0040589e-07, No Iterations 7
GAMG:  Solving for p, Initial residual = 7.9383326e-06, Final residual = 6.7605711e-08, No Iterations 3
time step continuity errors : sum local = 1.0464828e-09, global = 8.181732e-13, cumulative = -1.7484991e-07
ExecutionTime = 293.47 s  ClockTime = 295 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012268

Time = 371

smoothSolver:  Solving for Ux, Initial residual = 1.2652272e-07, Final residual = 3.7226183e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.5189081e-08, Final residual = 3.9099881e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00026640282, Final residual = 2.2913744e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.5456135e-05, Final residual = 3.2926378e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2953404e-05, Final residual = 9.8931229e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 7.9122936e-06, Final residual = 6.7080103e-08, No Iterations 3
time step continuity errors : sum local = 1.0382164e-09, global = 8.0149623e-13, cumulative = -1.748491e-07
ExecutionTime = 294.23 s  ClockTime = 296 s

Time = 372

smoothSolver:  Solving for Ux, Initial residual = 1.2609192e-07, Final residual = 3.711533e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.5109979e-08, Final residual = 3.8980038e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00026526372, Final residual = 2.2735149e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.52279e-05, Final residual = 3.2623344e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2874124e-05, Final residual = 9.8230787e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 7.8676451e-06, Final residual = 6.6502243e-08, No Iterations 3
time step continuity errors : sum local = 1.0291971e-09, global = 8.2511942e-13, cumulative = -1.7484828e-07
ExecutionTime = 294.97 s  ClockTime = 296 s

Time = 373

smoothSolver:  Solving for Ux, Initial residual = 1.256411e-07, Final residual = 3.7000672e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.5030871e-08, Final residual = 3.8860923e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0002640204, Final residual = 2.2516362e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.4827454e-05, Final residual = 3.2608471e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2785077e-05, Final residual = 9.6429225e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 7.8291138e-06, Final residual = 6.4319513e-08, No Iterations 3
time step continuity errors : sum local = 9.9563647e-10, global = 9.5443325e-13, cumulative = -1.7484732e-07
ExecutionTime = 295.87 s  ClockTime = 297 s

Time = 374

smoothSolver:  Solving for Ux, Initial residual = 1.2513502e-07, Final residual = 3.6885703e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.4945348e-08, Final residual = 3.8741283e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00026269095, Final residual = 2.2320407e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.4309004e-05, Final residual = 3.2583141e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2672534e-05, Final residual = 1.2257637e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.7679303e-06, Final residual = 6.4311581e-08, No Iterations 3
time step continuity errors : sum local = 9.9561897e-10, global = 7.8736504e-13, cumulative = -1.7484654e-07
ExecutionTime = 296.76 s  ClockTime = 298 s

Time = 375

smoothSolver:  Solving for Ux, Initial residual = 1.2434336e-07, Final residual = 3.6772084e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.4822416e-08, Final residual = 3.8620699e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00026155979, Final residual = 2.2118111e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.3963974e-05, Final residual = 3.2157948e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2509849e-05, Final residual = 1.2211638e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.6089848e-06, Final residual = 5.8706623e-08, No Iterations 3
time step continuity errors : sum local = 9.0861407e-10, global = 1.0838352e-12, cumulative = -1.7484545e-07
ExecutionTime = 297.53 s  ClockTime = 299 s

Time = 376

smoothSolver:  Solving for Ux, Initial residual = 1.2390763e-07, Final residual = 3.6659572e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.474914e-08, Final residual = 3.8499906e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0002604201, Final residual = 2.1798704e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.37732e-05, Final residual = 3.1302773e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2377323e-05, Final residual = 2.8995117e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.0593922e-06, Final residual = 4.7370368e-08, No Iterations 4
time step continuity errors : sum local = 7.3356181e-10, global = 2.3625966e-13, cumulative = -1.7484522e-07
ExecutionTime = 298.22 s  ClockTime = 300 s

Time = 377

smoothSolver:  Solving for Ux, Initial residual = 1.2366906e-07, Final residual = 3.6548179e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.4685174e-08, Final residual = 3.8381233e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00025928192, Final residual = 2.1390428e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.3662516e-05, Final residual = 2.9797771e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.215377e-05, Final residual = 9.0788655e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.6915303e-06, Final residual = 2.5883979e-08, No Iterations 3
time step continuity errors : sum local = 4.0133769e-10, global = -2.0129645e-13, cumulative = -1.7484542e-07
ExecutionTime = 298.92 s  ClockTime = 300 s

Time = 378

smoothSolver:  Solving for Ux, Initial residual = 1.2358472e-07, Final residual = 3.6437519e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.4649549e-08, Final residual = 3.8262603e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00025821904, Final residual = 2.0910132e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.3595493e-05, Final residual = 2.9695464e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2120269e-05, Final residual = 9.0010973e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 6.6731056e-06, Final residual = 6.5932477e-08, No Iterations 4
time step continuity errors : sum local = 1.020625e-09, global = 5.0804509e-13, cumulative = -1.7484491e-07
ExecutionTime = 299.8 s  ClockTime = 301 s

Time = 379

smoothSolver:  Solving for Ux, Initial residual = 1.2348963e-07, Final residual = 3.6330153e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.4599892e-08, Final residual = 3.8146469e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00025725065, Final residual = 2.0680802e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.3592729e-05, Final residual = 3.0249811e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2076407e-05, Final residual = 1.00317e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.0686833e-06, Final residual = 5.9828766e-08, No Iterations 3
time step continuity errors : sum local = 9.260754e-10, global = 3.5282141e-13, cumulative = -1.7484456e-07
ExecutionTime = 300.43 s  ClockTime = 302 s

Time = 380

smoothSolver:  Solving for Ux, Initial residual = 1.2289377e-07, Final residual = 3.6222758e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.4489811e-08, Final residual = 3.803225e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00025631783, Final residual = 2.0392264e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.3562658e-05, Final residual = 2.9869963e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2062866e-05, Final residual = 9.7697595e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 7.0269377e-06, Final residual = 6.2667286e-08, No Iterations 4
time step continuity errors : sum local = 9.6979961e-10, global = 2.7261516e-13, cumulative = -1.7484428e-07
ExecutionTime = 301.09 s  ClockTime = 302 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012268

Time = 381

smoothSolver:  Solving for Ux, Initial residual = 1.2244058e-07, Final residual = 3.6119455e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.4400982e-08, Final residual = 3.7919566e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00025547952, Final residual = 1.9831234e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.3541643e-05, Final residual = 2.8406192e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2060322e-05, Final residual = 9.0107862e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.8927471e-06, Final residual = 5.6504687e-08, No Iterations 4
time step continuity errors : sum local = 8.746788e-10, global = 2.5974514e-13, cumulative = -1.7484403e-07
ExecutionTime = 301.8 s  ClockTime = 303 s

Time = 382

smoothSolver:  Solving for Ux, Initial residual = 1.221663e-07, Final residual = 3.6016235e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.4337489e-08, Final residual = 3.7808881e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00025468037, Final residual = 1.9557829e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.3481421e-05, Final residual = 2.7073818e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2137383e-05, Final residual = 1.2113936e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.5220585e-06, Final residual = 5.5480434e-08, No Iterations 3
time step continuity errors : sum local = 8.5851661e-10, global = 2.1848869e-13, cumulative = -1.7484381e-07
ExecutionTime = 302.53 s  ClockTime = 304 s

Time = 383

smoothSolver:  Solving for Ux, Initial residual = 1.2145684e-07, Final residual = 3.5910643e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.4222017e-08, Final residual = 3.7699154e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00025380327, Final residual = 1.9441964e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.3358181e-05, Final residual = 2.6547089e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2148861e-05, Final residual = 1.1345879e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.1049731e-06, Final residual = 4.9326254e-08, No Iterations 8
time step continuity errors : sum local = 7.6354683e-10, global = 3.0233387e-13, cumulative = -1.748435e-07
ExecutionTime = 303.35 s  ClockTime = 305 s

Time = 384

smoothSolver:  Solving for Ux, Initial residual = 1.2111029e-07, Final residual = 3.5807165e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.4153049e-08, Final residual = 3.7589736e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00025290411, Final residual = 1.9392656e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.3201155e-05, Final residual = 2.6539821e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2144059e-05, Final residual = 1.0923751e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.0710415e-06, Final residual = 5.2418266e-08, No Iterations 7
time step continuity errors : sum local = 8.1148946e-10, global = 3.7748333e-13, cumulative = -1.7484313e-07
ExecutionTime = 304.08 s  ClockTime = 305 s

Time = 385

smoothSolver:  Solving for Ux, Initial residual = 1.2073092e-07, Final residual = 3.5706324e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.4079035e-08, Final residual = 3.747965e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00025200324, Final residual = 1.9379709e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.3001799e-05, Final residual = 2.6581116e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.2061214e-05, Final residual = 1.0924015e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.0349132e-06, Final residual = 6.0150689e-08, No Iterations 7
time step continuity errors : sum local = 9.309261e-10, global = 4.6199213e-13, cumulative = -1.7484266e-07
ExecutionTime = 304.77 s  ClockTime = 306 s

Time = 386

smoothSolver:  Solving for Ux, Initial residual = 1.2044425e-07, Final residual = 3.5603462e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.4013021e-08, Final residual = 3.737022e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00025107145, Final residual = 1.9372743e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.2762506e-05, Final residual = 2.6805961e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1982836e-05, Final residual = 1.1118771e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.0156263e-06, Final residual = 1.301814e-08, No Iterations 7
time step continuity errors : sum local = 2.0230391e-10, global = -8.4499453e-14, cumulative = -1.7484275e-07
ExecutionTime = 305.5 s  ClockTime = 307 s

Time = 387

smoothSolver:  Solving for Ux, Initial residual = 1.2013748e-07, Final residual = 3.5498015e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.3934054e-08, Final residual = 3.7261782e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0002500911, Final residual = 1.9341384e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.2477721e-05, Final residual = 2.7509007e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1869149e-05, Final residual = 1.1686036e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.9833408e-06, Final residual = 4.374258e-08, No Iterations 9
time step continuity errors : sum local = 6.7761943e-10, global = 4.4731721e-13, cumulative = -1.748423e-07
ExecutionTime = 306.23 s  ClockTime = 308 s

Time = 388

smoothSolver:  Solving for Ux, Initial residual = 1.19962e-07, Final residual = 3.5392432e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.3885555e-08, Final residual = 3.7154088e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00024909956, Final residual = 1.9315707e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.2176819e-05, Final residual = 2.8220001e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1753106e-05, Final residual = 8.8763605e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.6264738e-06, Final residual = 4.4971934e-08, No Iterations 3
time step continuity errors : sum local = 6.9642959e-10, global = 4.7726501e-13, cumulative = -1.7484182e-07
ExecutionTime = 306.91 s  ClockTime = 308 s

Time = 389

smoothSolver:  Solving for Ux, Initial residual = 1.1942042e-07, Final residual = 3.5286704e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.3794172e-08, Final residual = 3.7047089e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00024804513, Final residual = 1.9257059e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.1820799e-05, Final residual = 2.8679645e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1617236e-05, Final residual = 8.7795084e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.5543168e-06, Final residual = 4.5364619e-08, No Iterations 3
time step continuity errors : sum local = 7.022501e-10, global = 5.5748066e-13, cumulative = -1.7484127e-07
ExecutionTime = 307.71 s  ClockTime = 309 s

Time = 390

smoothSolver:  Solving for Ux, Initial residual = 1.1901829e-07, Final residual = 3.5180466e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.3723244e-08, Final residual = 3.6939643e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0002469495, Final residual = 1.9163518e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.1498915e-05, Final residual = 2.9286105e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1516602e-05, Final residual = 8.0987809e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 6.2920566e-06, Final residual = 5.0622614e-08, No Iterations 5
time step continuity errors : sum local = 7.8370333e-10, global = 6.5533246e-13, cumulative = -1.7484061e-07
ExecutionTime = 308.58 s  ClockTime = 310 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012268

Time = 391

smoothSolver:  Solving for Ux, Initial residual = 1.1918691e-07, Final residual = 3.5072663e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.3722545e-08, Final residual = 3.6833269e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0002458202, Final residual = 1.9037078e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.1336366e-05, Final residual = 2.9816197e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1385417e-05, Final residual = 6.3346186e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 6.3404036e-06, Final residual = 4.1407813e-08, No Iterations 3
time step continuity errors : sum local = 6.4138537e-10, global = 7.443817e-13, cumulative = -1.7483987e-07
ExecutionTime = 309.32 s  ClockTime = 311 s

Time = 392

smoothSolver:  Solving for Ux, Initial residual = 1.1897555e-07, Final residual = 3.4964775e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.3682043e-08, Final residual = 3.6728664e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00024469783, Final residual = 1.8900748e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.1225396e-05, Final residual = 3.0290748e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1309185e-05, Final residual = 1.1164274e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.352733e-06, Final residual = 4.2476537e-08, No Iterations 4
time step continuity errors : sum local = 6.5787498e-10, global = 8.4171403e-13, cumulative = -1.7483903e-07
ExecutionTime = 310.09 s  ClockTime = 311 s

Time = 393

smoothSolver:  Solving for Ux, Initial residual = 1.1843378e-07, Final residual = 3.4856069e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.3599061e-08, Final residual = 3.6625534e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00024355906, Final residual = 1.8788627e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.1145637e-05, Final residual = 3.0215986e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1218036e-05, Final residual = 1.0741544e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.3669581e-06, Final residual = 4.3806366e-08, No Iterations 4
time step continuity errors : sum local = 6.7836874e-10, global = 8.9473928e-13, cumulative = -1.7483813e-07
ExecutionTime = 310.84 s  ClockTime = 312 s

Time = 394

smoothSolver:  Solving for Ux, Initial residual = 1.180053e-07, Final residual = 3.4747015e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.3522975e-08, Final residual = 3.6524278e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00024265762, Final residual = 1.8676744e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.1123877e-05, Final residual = 3.0129067e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.114128e-05, Final residual = 1.0693266e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.3896046e-06, Final residual = 1.3790292e-08, No Iterations 5
time step continuity errors : sum local = 2.1442999e-10, global = 3.0850672e-13, cumulative = -1.7483782e-07
ExecutionTime = 311.66 s  ClockTime = 313 s

Time = 395

smoothSolver:  Solving for Ux, Initial residual = 1.176658e-07, Final residual = 3.4638043e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.3451612e-08, Final residual = 3.6424054e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00024190503, Final residual = 1.8643498e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.1296291e-05, Final residual = 3.0350281e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1105438e-05, Final residual = 1.075313e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.3520881e-06, Final residual = 2.2585856e-08, No Iterations 3
time step continuity errors : sum local = 3.5022878e-10, global = 2.010737e-13, cumulative = -1.7483762e-07
ExecutionTime = 312.42 s  ClockTime = 314 s

Time = 396

smoothSolver:  Solving for Ux, Initial residual = 1.172394e-07, Final residual = 3.4531017e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.3379303e-08, Final residual = 3.6324803e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00024124702, Final residual = 1.874423e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.1544544e-05, Final residual = 3.0818917e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1193101e-05, Final residual = 8.8196924e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 6.4154804e-06, Final residual = 1.9887967e-08, No Iterations 4
time step continuity errors : sum local = 3.0861947e-10, global = 8.6508651e-14, cumulative = -1.7483753e-07
ExecutionTime = 313.18 s  ClockTime = 314 s

Time = 397

smoothSolver:  Solving for Ux, Initial residual = 1.1702066e-07, Final residual = 3.4425657e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.3337322e-08, Final residual = 3.6224526e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00024068584, Final residual = 1.8993661e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.1793073e-05, Final residual = 3.1098305e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1397501e-05, Final residual = 8.6272159e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 6.4207553e-06, Final residual = 5.2706129e-08, No Iterations 3
time step continuity errors : sum local = 8.1591156e-10, global = 4.9819896e-13, cumulative = -1.7483704e-07
ExecutionTime = 313.93 s  ClockTime = 315 s

Time = 398

smoothSolver:  Solving for Ux, Initial residual = 1.1682575e-07, Final residual = 3.4321563e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.3284311e-08, Final residual = 3.6124953e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00024016205, Final residual = 1.9324479e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.1816771e-05, Final residual = 2.9407391e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1688255e-05, Final residual = 6.9199284e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.3110259e-06, Final residual = 3.5574632e-08, No Iterations 4
time step continuity errors : sum local = 5.5122049e-10, global = 4.442772e-13, cumulative = -1.7483659e-07
ExecutionTime = 314.77 s  ClockTime = 316 s

Time = 399

smoothSolver:  Solving for Ux, Initial residual = 1.1678079e-07, Final residual = 3.4219263e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.3253565e-08, Final residual = 3.6023994e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00023966511, Final residual = 1.9852237e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.1721535e-05, Final residual = 2.9453212e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1673285e-05, Final residual = 1.0150755e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.7393173e-06, Final residual = 5.2507418e-08, No Iterations 3
time step continuity errors : sum local = 8.1293133e-10, global = 4.0910775e-13, cumulative = -1.7483618e-07
ExecutionTime = 315.71 s  ClockTime = 317 s

Time = 400

smoothSolver:  Solving for Ux, Initial residual = 1.1618923e-07, Final residual = 3.4125156e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.3152e-08, Final residual = 3.5919966e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00023915748, Final residual = 2.0404334e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.1643695e-05, Final residual = 2.9792971e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.157748e-05, Final residual = 1.0372166e-07, No Iterations 6
GAMG:  Solving for p, Initial residual = 6.6174228e-06, Final residual = 5.9257254e-08, No Iterations 3
time step continuity errors : sum local = 9.1735996e-10, global = 3.6524678e-13, cumulative = -1.7483582e-07
ExecutionTime = 316.85 s  ClockTime = 318 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012268

Time = 401

smoothSolver:  Solving for Ux, Initial residual = 1.1583936e-07, Final residual = 3.4026601e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.3088418e-08, Final residual = 3.5817821e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00023852172, Final residual = 2.0803125e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.1673571e-05, Final residual = 2.9438291e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1567437e-05, Final residual = 1.0391035e-07, No Iterations 6
GAMG:  Solving for p, Initial residual = 7.2278659e-06, Final residual = 6.9413305e-08, No Iterations 3
time step continuity errors : sum local = 1.0743756e-09, global = 4.5298209e-13, cumulative = -1.7483537e-07
ExecutionTime = 317.52 s  ClockTime = 319 s

Time = 402

smoothSolver:  Solving for Ux, Initial residual = 1.1548024e-07, Final residual = 3.393367e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.3020265e-08, Final residual = 3.5714522e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00023765565, Final residual = 2.0765128e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.1543852e-05, Final residual = 2.9413427e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.15354e-05, Final residual = 8.5971229e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 7.3795417e-06, Final residual = 6.6254017e-08, No Iterations 3
time step continuity errors : sum local = 1.025387e-09, global = 5.0297837e-13, cumulative = -1.7483486e-07
ExecutionTime = 318.29 s  ClockTime = 320 s

Time = 403

smoothSolver:  Solving for Ux, Initial residual = 1.149533e-07, Final residual = 3.3837676e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.2938112e-08, Final residual = 3.5612872e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00023665891, Final residual = 2.0652729e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.1287298e-05, Final residual = 2.9699322e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1500735e-05, Final residual = 9.1442481e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 7.3178145e-06, Final residual = 6.5247094e-08, No Iterations 3
time step continuity errors : sum local = 1.0098653e-09, global = 5.8162594e-13, cumulative = -1.7483428e-07
ExecutionTime = 319.04 s  ClockTime = 321 s

Time = 404

smoothSolver:  Solving for Ux, Initial residual = 1.1448144e-07, Final residual = 3.3739337e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.287093e-08, Final residual = 3.5511881e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00023554243, Final residual = 2.0536705e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.0864031e-05, Final residual = 2.9882795e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1405641e-05, Final residual = 1.0928103e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.9053343e-06, Final residual = 6.058495e-08, No Iterations 3
time step continuity errors : sum local = 9.3804926e-10, global = 4.2996805e-13, cumulative = -1.7483385e-07
ExecutionTime = 319.83 s  ClockTime = 321 s

Time = 405

smoothSolver:  Solving for Ux, Initial residual = 1.1397269e-07, Final residual = 3.3639773e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.279261e-08, Final residual = 3.5411063e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00023442714, Final residual = 2.0406586e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.0427328e-05, Final residual = 2.9767207e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1278611e-05, Final residual = 1.0753009e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.7833391e-06, Final residual = 5.8324712e-08, No Iterations 3
time step continuity errors : sum local = 9.0304146e-10, global = 5.4653204e-13, cumulative = -1.748333e-07
ExecutionTime = 320.74 s  ClockTime = 322 s

Time = 406

smoothSolver:  Solving for Ux, Initial residual = 1.1347147e-07, Final residual = 3.3541881e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.2708559e-08, Final residual = 3.5308413e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00023350162, Final residual = 2.0214374e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.0224625e-05, Final residual = 2.9285205e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.1087109e-05, Final residual = 1.0867664e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.6681165e-06, Final residual = 6.4719825e-08, No Iterations 3
time step continuity errors : sum local = 1.0019136e-09, global = 7.028641e-13, cumulative = -1.748326e-07
ExecutionTime = 321.59 s  ClockTime = 323 s

Time = 407

smoothSolver:  Solving for Ux, Initial residual = 1.1306827e-07, Final residual = 3.3445141e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.2630519e-08, Final residual = 3.5204645e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00023249121, Final residual = 1.9907393e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 3.0039326e-05, Final residual = 2.848403e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0896032e-05, Final residual = 9.18486e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.4741949e-06, Final residual = 4.1318813e-08, No Iterations 3
time step continuity errors : sum local = 6.4002376e-10, global = 8.0253415e-13, cumulative = -1.748318e-07
ExecutionTime = 322.27 s  ClockTime = 324 s

Time = 408

smoothSolver:  Solving for Ux, Initial residual = 1.1264435e-07, Final residual = 3.3350909e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.2556354e-08, Final residual = 3.5100865e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00023153342, Final residual = 1.9410319e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.9887038e-05, Final residual = 2.7385377e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0772244e-05, Final residual = 8.5741325e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 6.1068455e-06, Final residual = 2.5084266e-08, No Iterations 3
time step continuity errors : sum local = 3.8898329e-10, global = 2.4630219e-13, cumulative = -1.7483155e-07
ExecutionTime = 323.13 s  ClockTime = 325 s

Time = 409

smoothSolver:  Solving for Ux, Initial residual = 1.1232324e-07, Final residual = 3.3258759e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.2479163e-08, Final residual = 3.4998306e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00023066475, Final residual = 1.9078449e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.9853505e-05, Final residual = 2.7729314e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0682733e-05, Final residual = 7.0119484e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 6.0975441e-06, Final residual = 4.7803254e-08, No Iterations 3
time step continuity errors : sum local = 7.3996757e-10, global = 7.9307383e-13, cumulative = -1.7483076e-07
ExecutionTime = 323.98 s  ClockTime = 325 s

Time = 410

smoothSolver:  Solving for Ux, Initial residual = 1.1216792e-07, Final residual = 3.3167052e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.2428041e-08, Final residual = 3.4898441e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00022989881, Final residual = 1.8911407e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.9853966e-05, Final residual = 2.7990076e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0648394e-05, Final residual = 2.491747e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.0294525e-06, Final residual = 4.7367768e-08, No Iterations 4
time step continuity errors : sum local = 7.3348047e-10, global = 6.4023736e-14, cumulative = -1.748307e-07
ExecutionTime = 324.67 s  ClockTime = 326 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012268

Time = 411

smoothSolver:  Solving for Ux, Initial residual = 1.1202163e-07, Final residual = 3.3075415e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.2387981e-08, Final residual = 3.4798891e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00022909458, Final residual = 1.8219586e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.9871088e-05, Final residual = 2.6658522e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0603722e-05, Final residual = 9.8072047e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.2103521e-06, Final residual = 5.9673618e-08, No Iterations 4
time step continuity errors : sum local = 9.2386592e-10, global = 5.6279367e-13, cumulative = -1.7483013e-07
ExecutionTime = 325.58 s  ClockTime = 327 s

Time = 412

smoothSolver:  Solving for Ux, Initial residual = 1.1175404e-07, Final residual = 3.2986669e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.2323676e-08, Final residual = 3.4700281e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0002284357, Final residual = 1.7763954e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.9816025e-05, Final residual = 2.5411008e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.063598e-05, Final residual = 8.5370894e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.0773497e-06, Final residual = 5.0250159e-08, No Iterations 4
time step continuity errors : sum local = 7.7787258e-10, global = 5.2841767e-13, cumulative = -1.748296e-07
ExecutionTime = 326.31 s  ClockTime = 328 s

Time = 413

smoothSolver:  Solving for Ux, Initial residual = 1.1154728e-07, Final residual = 3.2897697e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.2270892e-08, Final residual = 3.460356e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00022775216, Final residual = 1.7544057e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.9706575e-05, Final residual = 2.4362792e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0710224e-05, Final residual = 7.3785253e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.9597056e-06, Final residual = 3.3597077e-08, No Iterations 4
time step continuity errors : sum local = 5.2059736e-10, global = 4.6215677e-13, cumulative = -1.7482914e-07
ExecutionTime = 327.06 s  ClockTime = 329 s

Time = 414

smoothSolver:  Solving for Ux, Initial residual = 1.11036e-07, Final residual = 3.2806597e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.218079e-08, Final residual = 3.4507377e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00022702361, Final residual = 1.7439232e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.9563229e-05, Final residual = 2.3834235e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0743626e-05, Final residual = 1.0118881e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.3522509e-06, Final residual = 4.2948168e-08, No Iterations 6
time step continuity errors : sum local = 6.6496988e-10, global = 5.2674177e-13, cumulative = -1.7482862e-07
ExecutionTime = 327.77 s  ClockTime = 329 s

Time = 415

smoothSolver:  Solving for Ux, Initial residual = 1.1071925e-07, Final residual = 3.271649e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.2115698e-08, Final residual = 3.4411668e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00022623841, Final residual = 1.7349152e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.939136e-05, Final residual = 2.4063704e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.074224e-05, Final residual = 9.7700324e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.3335062e-06, Final residual = 5.2548006e-08, No Iterations 5
time step continuity errors : sum local = 8.1361008e-10, global = 5.6366814e-13, cumulative = -1.7482805e-07
ExecutionTime = 328.54 s  ClockTime = 330 s

Time = 416

smoothSolver:  Solving for Ux, Initial residual = 1.1027179e-07, Final residual = 3.2629854e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.2035386e-08, Final residual = 3.4315282e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.000225435, Final residual = 1.7306733e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.9189016e-05, Final residual = 2.4615933e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0715184e-05, Final residual = 9.9472329e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.3377594e-06, Final residual = 1.4184614e-08, No Iterations 5
time step continuity errors : sum local = 2.2048157e-10, global = -3.0666413e-14, cumulative = -1.7482808e-07
ExecutionTime = 329.49 s  ClockTime = 331 s

Time = 417

smoothSolver:  Solving for Ux, Initial residual = 1.0993091e-07, Final residual = 3.2540939e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.1968873e-08, Final residual = 3.4221045e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0002246088, Final residual = 1.7300773e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.896357e-05, Final residual = 2.5213661e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0660689e-05, Final residual = 1.0556107e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.3669911e-06, Final residual = 5.0741931e-08, No Iterations 6
time step continuity errors : sum local = 7.8585061e-10, global = 4.8709671e-13, cumulative = -1.748276e-07
ExecutionTime = 330.24 s  ClockTime = 332 s

Time = 418

smoothSolver:  Solving for Ux, Initial residual = 1.0964493e-07, Final residual = 3.2450781e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.1899536e-08, Final residual = 3.4127038e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.000223771, Final residual = 1.7292583e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.8761922e-05, Final residual = 2.5897082e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0603073e-05, Final residual = 7.7731236e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.9847437e-06, Final residual = 4.2393057e-08, No Iterations 3
time step continuity errors : sum local = 6.5669593e-10, global = 4.7012243e-13, cumulative = -1.7482712e-07
ExecutionTime = 331 s  ClockTime = 332 s

Time = 419

smoothSolver:  Solving for Ux, Initial residual = 1.0924824e-07, Final residual = 3.2360248e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.1828194e-08, Final residual = 3.4033548e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00022287208, Final residual = 1.7231245e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.8527987e-05, Final residual = 2.6199182e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0506807e-05, Final residual = 7.8100617e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.0110061e-06, Final residual = 4.4915336e-08, No Iterations 3
time step continuity errors : sum local = 6.9559009e-10, global = 5.223779e-13, cumulative = -1.748266e-07
ExecutionTime = 331.77 s  ClockTime = 333 s

Time = 420

smoothSolver:  Solving for Ux, Initial residual = 1.089636e-07, Final residual = 3.2270243e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.1772174e-08, Final residual = 3.3939652e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00022191312, Final residual = 1.715787e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.8237321e-05, Final residual = 2.6140207e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0373552e-05, Final residual = 2.1078828e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.7149736e-06, Final residual = 3.1178749e-08, No Iterations 4
time step continuity errors : sum local = 4.8336161e-10, global = -7.6590038e-14, cumulative = -1.7482668e-07
ExecutionTime = 332.66 s  ClockTime = 334 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012268

Time = 421

smoothSolver:  Solving for Ux, Initial residual = 1.0888266e-07, Final residual = 3.2179004e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.1738809e-08, Final residual = 3.3846402e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00022093831, Final residual = 1.7090314e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.7969783e-05, Final residual = 2.5989672e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0249556e-05, Final residual = 6.9885838e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 5.6533453e-06, Final residual = 5.2858312e-08, No Iterations 3
time step continuity errors : sum local = 8.1865758e-10, global = 3.9876065e-13, cumulative = -1.7482628e-07
ExecutionTime = 333.55 s  ClockTime = 335 s

Time = 422

smoothSolver:  Solving for Ux, Initial residual = 1.0875881e-07, Final residual = 3.2086479e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.1707342e-08, Final residual = 3.3754374e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0002199613, Final residual = 1.700522e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.7825443e-05, Final residual = 2.6273318e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0130238e-05, Final residual = 5.4238617e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 5.7366996e-06, Final residual = 4.0098783e-08, No Iterations 3
time step continuity errors : sum local = 6.2121169e-10, global = 3.9863388e-13, cumulative = -1.7482588e-07
ExecutionTime = 334.32 s  ClockTime = 336 s

Time = 423

smoothSolver:  Solving for Ux, Initial residual = 1.0857731e-07, Final residual = 3.1992423e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.1665277e-08, Final residual = 3.3664088e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00021905581, Final residual = 1.6903676e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.7748381e-05, Final residual = 2.6522896e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0037142e-05, Final residual = 1.0011099e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.6734384e-06, Final residual = 3.7190316e-08, No Iterations 4
time step continuity errors : sum local = 5.7597265e-10, global = 4.1171941e-13, cumulative = -1.7482547e-07
ExecutionTime = 335.04 s  ClockTime = 337 s

Time = 424

smoothSolver:  Solving for Ux, Initial residual = 1.0815613e-07, Final residual = 3.1897398e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.1597427e-08, Final residual = 3.3574951e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00021817126, Final residual = 1.6797059e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.7699589e-05, Final residual = 2.6605368e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.9639701e-06, Final residual = 9.5292952e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.685615e-06, Final residual = 3.1742155e-08, No Iterations 4
time step continuity errors : sum local = 4.9179248e-10, global = 4.6514528e-13, cumulative = -1.74825e-07
ExecutionTime = 335.74 s  ClockTime = 337 s

Time = 425

smoothSolver:  Solving for Ux, Initial residual = 1.0792046e-07, Final residual = 3.1801956e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.15507e-08, Final residual = 3.3488449e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00021747888, Final residual = 1.6718041e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.778384e-05, Final residual = 2.682909e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.9126344e-06, Final residual = 9.1022788e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.6654834e-06, Final residual = 2.7795435e-08, No Iterations 4
time step continuity errors : sum local = 4.309425e-10, global = 5.3423826e-13, cumulative = -1.7482447e-07
ExecutionTime = 336.5 s  ClockTime = 338 s

Time = 426

smoothSolver:  Solving for Ux, Initial residual = 1.0775443e-07, Final residual = 3.1706746e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.1511987e-08, Final residual = 3.3403608e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0002169392, Final residual = 1.6766363e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.7983758e-05, Final residual = 2.7554464e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.9538578e-06, Final residual = 9.2922854e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.6438941e-06, Final residual = 3.6619922e-08, No Iterations 4
time step continuity errors : sum local = 5.6742629e-10, global = 5.8605401e-13, cumulative = -1.7482388e-07
ExecutionTime = 337.26 s  ClockTime = 339 s

Time = 427

smoothSolver:  Solving for Ux, Initial residual = 1.0735193e-07, Final residual = 3.1613243e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.144046e-08, Final residual = 3.3318631e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00021639013, Final residual = 1.6870963e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.8209416e-05, Final residual = 1.9954145e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0471596e-05, Final residual = 8.6223398e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.0890819e-06, Final residual = 4.5758676e-08, No Iterations 5
time step continuity errors : sum local = 7.0857614e-10, global = 6.6457664e-13, cumulative = -1.7482322e-07
ExecutionTime = 338.04 s  ClockTime = 340 s

Time = 428

smoothSolver:  Solving for Ux, Initial residual = 1.0699831e-07, Final residual = 3.1521894e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.1378603e-08, Final residual = 3.3233939e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00021589555, Final residual = 1.6991173e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.8516211e-05, Final residual = 2.0618929e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0759249e-05, Final residual = 1.0023754e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.2052691e-06, Final residual = 1.4780866e-08, No Iterations 4
time step continuity errors : sum local = 2.2988535e-10, global = 8.4277369e-14, cumulative = -1.7482314e-07
ExecutionTime = 338.82 s  ClockTime = 340 s

Time = 429

smoothSolver:  Solving for Ux, Initial residual = 1.0655486e-07, Final residual = 3.1432965e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.1294193e-08, Final residual = 3.3148162e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00021544446, Final residual = 1.7212193e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.8582467e-05, Final residual = 1.9263604e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1043282e-05, Final residual = 1.0517896e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.3426085e-06, Final residual = 3.0956491e-08, No Iterations 3
time step continuity errors : sum local = 4.8002719e-10, global = 1.0696594e-13, cumulative = -1.7482303e-07
ExecutionTime = 339.53 s  ClockTime = 341 s

Time = 430

smoothSolver:  Solving for Ux, Initial residual = 1.0617564e-07, Final residual = 3.1350081e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.1238503e-08, Final residual = 3.3060482e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00021498237, Final residual = 1.7573072e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.8431259e-05, Final residual = 1.9289096e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.1063648e-05, Final residual = 8.0222262e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.3254734e-06, Final residual = 4.0996569e-08, No Iterations 9
time step continuity errors : sum local = 6.351062e-10, global = 5.5943804e-13, cumulative = -1.7482247e-07
ExecutionTime = 340.37 s  ClockTime = 342 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012268

Time = 431

smoothSolver:  Solving for Ux, Initial residual = 1.0627396e-07, Final residual = 3.1268777e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.1236011e-08, Final residual = 3.2970721e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00021459028, Final residual = 1.8066584e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.8272691e-05, Final residual = 2.0373236e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0898642e-05, Final residual = 8.7376407e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.4370541e-06, Final residual = 4.2250777e-08, No Iterations 8
time step continuity errors : sum local = 6.5451093e-10, global = 5.340668e-13, cumulative = -1.7482194e-07
ExecutionTime = 341.4 s  ClockTime = 343 s

Time = 432

smoothSolver:  Solving for Ux, Initial residual = 1.0606747e-07, Final residual = 3.1187349e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.1191455e-08, Final residual = 3.2881759e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00021411963, Final residual = 1.8569712e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.831958e-05, Final residual = 2.6961847e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0451649e-05, Final residual = 6.2964423e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 6.7470413e-06, Final residual = 6.2526441e-08, No Iterations 3
time step continuity errors : sum local = 9.6783557e-10, global = 5.5066427e-13, cumulative = -1.7482138e-07
ExecutionTime = 342.43 s  ClockTime = 344 s

Time = 433

smoothSolver:  Solving for Ux, Initial residual = 1.0590397e-07, Final residual = 3.1108759e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.1150851e-08, Final residual = 3.2792486e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00021334998, Final residual = 1.8637659e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.8174334e-05, Final residual = 2.6500839e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0400935e-05, Final residual = 8.0062364e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 6.7494972e-06, Final residual = 6.3001203e-08, No Iterations 3
time step continuity errors : sum local = 9.7551944e-10, global = 5.7956195e-13, cumulative = -1.7482081e-07
ExecutionTime = 343.27 s  ClockTime = 345 s

Time = 434

smoothSolver:  Solving for Ux, Initial residual = 1.0530314e-07, Final residual = 3.1024997e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.1058323e-08, Final residual = 3.270374e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00021246648, Final residual = 1.8635729e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.790778e-05, Final residual = 2.6923103e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0382503e-05, Final residual = 8.5073956e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 6.6488052e-06, Final residual = 6.1545138e-08, No Iterations 3
time step continuity errors : sum local = 9.5250781e-10, global = 6.2731104e-13, cumulative = -1.7482018e-07
ExecutionTime = 344.07 s  ClockTime = 346 s

Time = 435

smoothSolver:  Solving for Ux, Initial residual = 1.0479865e-07, Final residual = 3.0939057e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.0984293e-08, Final residual = 3.2614763e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00021146865, Final residual = 1.8579312e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.7542137e-05, Final residual = 2.7318485e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0334802e-05, Final residual = 1.0026843e-07, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.2661505e-06, Final residual = 5.8447416e-08, No Iterations 3
time step continuity errors : sum local = 9.0485181e-10, global = 6.5991127e-13, cumulative = -1.7481952e-07
ExecutionTime = 345.06 s  ClockTime = 347 s

Time = 436

smoothSolver:  Solving for Ux, Initial residual = 1.0438513e-07, Final residual = 3.0852465e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.0917757e-08, Final residual = 3.2525185e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00021051416, Final residual = 1.844978e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.7205003e-05, Final residual = 2.0005967e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 1.0633296e-05, Final residual = 9.2806898e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.2978124e-06, Final residual = 2.2398307e-08, No Iterations 5
time step continuity errors : sum local = 3.4730862e-10, global = -7.3560555e-14, cumulative = -1.7481959e-07
ExecutionTime = 345.89 s  ClockTime = 347 s

Time = 437

smoothSolver:  Solving for Ux, Initial residual = 1.0400162e-07, Final residual = 3.0766794e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.0849822e-08, Final residual = 3.2435242e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00020966823, Final residual = 1.8236487e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.7040298e-05, Final residual = 2.6973266e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.0060486e-05, Final residual = 9.8280773e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 6.0854284e-06, Final residual = 5.2113123e-08, No Iterations 3
time step continuity errors : sum local = 8.071992e-10, global = 5.8257632e-13, cumulative = -1.7481901e-07
ExecutionTime = 346.86 s  ClockTime = 348 s

Time = 438

smoothSolver:  Solving for Ux, Initial residual = 1.03595e-07, Final residual = 3.0683756e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.0772315e-08, Final residual = 3.2344434e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00020877078, Final residual = 1.7927403e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.6819031e-05, Final residual = 2.6356193e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.8020486e-06, Final residual = 8.3856168e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.8604159e-06, Final residual = 3.9270541e-08, No Iterations 3
time step continuity errors : sum local = 6.0836761e-10, global = 5.9697758e-13, cumulative = -1.7481841e-07
ExecutionTime = 347.68 s  ClockTime = 349 s

Time = 439

smoothSolver:  Solving for Ux, Initial residual = 1.0323054e-07, Final residual = 3.0602307e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.0705731e-08, Final residual = 3.2254549e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0002080248, Final residual = 1.754291e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.6732028e-05, Final residual = 2.6069606e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.730938e-06, Final residual = 6.5492608e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 5.5352169e-06, Final residual = 5.0505183e-08, No Iterations 3
time step continuity errors : sum local = 7.8188745e-10, global = 6.089742e-13, cumulative = -1.748178e-07
ExecutionTime = 348.44 s  ClockTime = 350 s

Time = 440

smoothSolver:  Solving for Ux, Initial residual = 1.0310081e-07, Final residual = 3.0523031e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.0659633e-08, Final residual = 3.2166512e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00020728842, Final residual = 1.7303852e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.6677627e-05, Final residual = 2.622672e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.6719855e-06, Final residual = 8.563949e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.8227224e-06, Final residual = 4.4350684e-08, No Iterations 3
time step continuity errors : sum local = 6.870262e-10, global = 6.291168e-13, cumulative = -1.7481717e-07
ExecutionTime = 349.7 s  ClockTime = 351 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012268

Time = 441

smoothSolver:  Solving for Ux, Initial residual = 1.0275956e-07, Final residual = 3.0443687e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.0597905e-08, Final residual = 3.2080432e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00020656575, Final residual = 1.6738454e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.6690862e-05, Final residual = 2.5190674e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.5607887e-06, Final residual = 8.5908232e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.666767e-06, Final residual = 5.5289887e-08, No Iterations 4
time step continuity errors : sum local = 8.5586636e-10, global = 6.7953451e-13, cumulative = -1.7481649e-07
ExecutionTime = 350.47 s  ClockTime = 352 s

Time = 442

smoothSolver:  Solving for Ux, Initial residual = 1.0255104e-07, Final residual = 3.0364104e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.054695e-08, Final residual = 3.1994873e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00020598211, Final residual = 1.6247732e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.6686373e-05, Final residual = 2.379723e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.5333482e-06, Final residual = 7.8189721e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.5213632e-06, Final residual = 1.9783878e-08, No Iterations 3
time step continuity errors : sum local = 3.0715699e-10, global = 1.1731712e-13, cumulative = -1.7481638e-07
ExecutionTime = 351.42 s  ClockTime = 353 s

Time = 443

smoothSolver:  Solving for Ux, Initial residual = 1.0218303e-07, Final residual = 3.0287459e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.0479731e-08, Final residual = 3.1910016e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0002054515, Final residual = 1.5929481e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.6604455e-05, Final residual = 2.2234125e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.5492028e-06, Final residual = 7.7551963e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.4343517e-06, Final residual = 5.0314502e-08, No Iterations 4
time step continuity errors : sum local = 7.7898462e-10, global = 6.2102726e-13, cumulative = -1.7481576e-07
ExecutionTime = 352.38 s  ClockTime = 354 s

Time = 444

smoothSolver:  Solving for Ux, Initial residual = 1.0194443e-07, Final residual = 3.0209294e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.0424223e-08, Final residual = 3.1826106e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00020488801, Final residual = 1.5748737e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.6475005e-05, Final residual = 2.1184451e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.5640108e-06, Final residual = 9.5385418e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.1059277e-06, Final residual = 4.4696712e-08, No Iterations 5
time step continuity errors : sum local = 6.9197791e-10, global = 6.3185664e-13, cumulative = -1.7481512e-07
ExecutionTime = 353.23 s  ClockTime = 355 s

Time = 445

smoothSolver:  Solving for Ux, Initial residual = 1.0183386e-07, Final residual = 3.0129991e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.0387692e-08, Final residual = 3.1742983e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00020428614, Final residual = 1.5646442e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.6361415e-05, Final residual = 2.1179914e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.6157574e-06, Final residual = 9.0131831e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.8110032e-06, Final residual = 1.5263655e-08, No Iterations 5
time step continuity errors : sum local = 2.3712964e-10, global = -7.5810916e-15, cumulative = -1.7481513e-07
ExecutionTime = 353.89 s  ClockTime = 355 s

Time = 446

smoothSolver:  Solving for Ux, Initial residual = 1.0141283e-07, Final residual = 3.0049873e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.0324456e-08, Final residual = 3.1659826e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00020363191, Final residual = 1.5525879e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.6233854e-05, Final residual = 2.1561998e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.6226648e-06, Final residual = 8.9715309e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.819726e-06, Final residual = 4.4974574e-08, No Iterations 7
time step continuity errors : sum local = 6.9649847e-10, global = 5.0346042e-13, cumulative = -1.7481463e-07
ExecutionTime = 354.63 s  ClockTime = 356 s

Time = 447

smoothSolver:  Solving for Ux, Initial residual = 1.0127751e-07, Final residual = 2.9974859e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.0273059e-08, Final residual = 3.1575286e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00020298009, Final residual = 1.5438116e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.6089315e-05, Final residual = 2.1962101e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.6303171e-06, Final residual = 9.315856e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.8398173e-06, Final residual = 4.2440128e-08, No Iterations 7
time step continuity errors : sum local = 6.5747569e-10, global = 4.8482305e-13, cumulative = -1.7481414e-07
ExecutionTime = 355.7 s  ClockTime = 357 s

Time = 448

smoothSolver:  Solving for Ux, Initial residual = 1.0100054e-07, Final residual = 2.989843e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.0210456e-08, Final residual = 3.1491693e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00020233531, Final residual = 1.5431791e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.591705e-05, Final residual = 2.2421987e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.5806516e-06, Final residual = 8.9519149e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.1038563e-06, Final residual = 3.5835509e-08, No Iterations 3
time step continuity errors : sum local = 5.5543188e-10, global = 4.6055189e-13, cumulative = -1.7481368e-07
ExecutionTime = 356.56 s  ClockTime = 358 s

Time = 449

smoothSolver:  Solving for Ux, Initial residual = 1.0059066e-07, Final residual = 2.9820189e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.0138545e-08, Final residual = 3.1408598e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0002016401, Final residual = 1.5447067e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5724844e-05, Final residual = 2.3092702e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.5112743e-06, Final residual = 9.2897508e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.1377619e-06, Final residual = 3.1898011e-08, No Iterations 3
time step continuity errors : sum local = 4.944313e-10, global = 2.3828502e-13, cumulative = -1.7481344e-07
ExecutionTime = 357.51 s  ClockTime = 359 s

Time = 450

smoothSolver:  Solving for Ux, Initial residual = 1.0035278e-07, Final residual = 2.9741537e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.0085018e-08, Final residual = 3.1326459e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00020088731, Final residual = 1.5492496e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5511732e-05, Final residual = 2.3496136e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.4251038e-06, Final residual = 6.5232811e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 5.1851742e-06, Final residual = 4.6827157e-08, No Iterations 3
time step continuity errors : sum local = 7.252555e-10, global = 4.7979868e-13, cumulative = -1.7481296e-07
ExecutionTime = 358.91 s  ClockTime = 361 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012268

Time = 451

smoothSolver:  Solving for Ux, Initial residual = 1.0008761e-07, Final residual = 2.9661743e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 2.0034185e-08, Final residual = 3.1244471e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00020010026, Final residual = 1.5484541e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5299792e-05, Final residual = 2.3565565e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.3390073e-06, Final residual = 6.7895354e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 5.1797214e-06, Final residual = 3.1960646e-08, No Iterations 3
time step continuity errors : sum local = 4.9511879e-10, global = 2.6255443e-13, cumulative = -1.748127e-07
ExecutionTime = 359.59 s  ClockTime = 361 s

Time = 452

smoothSolver:  Solving for Ux, Initial residual = 9.9917723e-08, Final residual = 2.9580461e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.9992124e-08, Final residual = 3.116325e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00019930159, Final residual = 1.5417194e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5143785e-05, Final residual = 2.3621532e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.2436129e-06, Final residual = 8.7088458e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.9831365e-06, Final residual = 4.2805913e-08, No Iterations 5
time step continuity errors : sum local = 6.6293806e-10, global = 5.0488864e-13, cumulative = -1.748122e-07
ExecutionTime = 360.24 s  ClockTime = 362 s

Time = 453

smoothSolver:  Solving for Ux, Initial residual = 9.9776583e-08, Final residual = 2.9498379e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.995927e-08, Final residual = 3.1082735e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00019852306, Final residual = 1.531839e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5063265e-05, Final residual = 2.3505053e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.1544937e-06, Final residual = 7.2088549e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.9644504e-06, Final residual = 2.9069503e-08, No Iterations 7
time step continuity errors : sum local = 4.5068512e-10, global = 5.6353616e-13, cumulative = -1.7481163e-07
ExecutionTime = 361.02 s  ClockTime = 363 s

Time = 454

smoothSolver:  Solving for Ux, Initial residual = 9.9869473e-08, Final residual = 2.9415889e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.9961283e-08, Final residual = 3.1003904e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00019777374, Final residual = 1.521511e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5028501e-05, Final residual = 2.333062e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.0535819e-06, Final residual = 7.976141e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.1107128e-06, Final residual = 3.9507485e-08, No Iterations 4
time step continuity errors : sum local = 6.118709e-10, global = 5.8913763e-13, cumulative = -1.7481104e-07
ExecutionTime = 361.74 s  ClockTime = 364 s

Time = 455

smoothSolver:  Solving for Ux, Initial residual = 9.973634e-08, Final residual = 2.9332256e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.99303e-08, Final residual = 3.092603e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001971597, Final residual = 1.5128087e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.509133e-05, Final residual = 2.3544614e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.0145824e-06, Final residual = 6.7853877e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.0586452e-06, Final residual = 2.9403453e-08, No Iterations 4
time step continuity errors : sum local = 4.5573224e-10, global = 6.5959615e-13, cumulative = -1.7481038e-07
ExecutionTime = 362.46 s  ClockTime = 364 s

Time = 456

smoothSolver:  Solving for Ux, Initial residual = 9.9364954e-08, Final residual = 2.9248979e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.9865259e-08, Final residual = 3.0848777e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00019666062, Final residual = 1.5152049e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5272082e-05, Final residual = 2.3858662e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.0302571e-06, Final residual = 6.8720576e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.0288398e-06, Final residual = 2.1343395e-08, No Iterations 3
time step continuity errors : sum local = 3.3101972e-10, global = 2.3413331e-13, cumulative = -1.7481015e-07
ExecutionTime = 363.18 s  ClockTime = 365 s

Time = 457

smoothSolver:  Solving for Ux, Initial residual = 9.8831994e-08, Final residual = 2.9166428e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.9774503e-08, Final residual = 3.0772693e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001961922, Final residual = 1.5243618e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5441335e-05, Final residual = 2.4742483e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.0948101e-06, Final residual = 7.9042938e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.0733053e-06, Final residual = 1.3238299e-08, No Iterations 4
time step continuity errors : sum local = 2.0583327e-10, global = 1.1153382e-13, cumulative = -1.7481004e-07
ExecutionTime = 363.87 s  ClockTime = 366 s

Time = 458

smoothSolver:  Solving for Ux, Initial residual = 9.8473455e-08, Final residual = 2.9085974e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.9717803e-08, Final residual = 3.0697154e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00019574043, Final residual = 1.5318171e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5614035e-05, Final residual = 2.5450762e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.2174538e-06, Final residual = 7.3207305e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.4506214e-06, Final residual = 3.6759724e-08, No Iterations 3
time step continuity errors : sum local = 5.6963271e-10, global = 5.1451768e-13, cumulative = -1.7480952e-07
ExecutionTime = 364.71 s  ClockTime = 367 s

Time = 459

smoothSolver:  Solving for Ux, Initial residual = 9.8117677e-08, Final residual = 2.9007216e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.9650884e-08, Final residual = 3.0622206e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00019531418, Final residual = 1.5391996e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5851061e-05, Final residual = 1.7894668e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 9.7651005e-06, Final residual = 9.6249156e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.7790404e-06, Final residual = 4.4599994e-08, No Iterations 4
time step continuity errors : sum local = 6.9087604e-10, global = 4.7909035e-13, cumulative = -1.7480905e-07
ExecutionTime = 365.71 s  ClockTime = 368 s

Time = 460

smoothSolver:  Solving for Ux, Initial residual = 9.7822619e-08, Final residual = 2.8933944e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.959846e-08, Final residual = 3.0546016e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00019491249, Final residual = 1.5479685e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5858073e-05, Final residual = 2.5284833e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.5998617e-06, Final residual = 5.5068809e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.2625041e-06, Final residual = 3.1839775e-08, No Iterations 4
time step continuity errors : sum local = 4.9348239e-10, global = 5.1008769e-13, cumulative = -1.7480854e-07
ExecutionTime = 366.75 s  ClockTime = 369 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012268

Time = 461

smoothSolver:  Solving for Ux, Initial residual = 9.7951661e-08, Final residual = 2.8862264e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.9607977e-08, Final residual = 3.0468384e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00019454196, Final residual = 1.5700256e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5679786e-05, Final residual = 2.45318e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.5415861e-06, Final residual = 1.9496937e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.2686697e-06, Final residual = 2.7901216e-08, No Iterations 4
time step continuity errors : sum local = 4.3274609e-10, global = -2.8257287e-14, cumulative = -1.7480856e-07
ExecutionTime = 367.87 s  ClockTime = 370 s

Time = 462

smoothSolver:  Solving for Ux, Initial residual = 9.7913356e-08, Final residual = 2.8789376e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.959427e-08, Final residual = 3.0391066e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00019414284, Final residual = 1.6098453e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5468836e-05, Final residual = 2.4496693e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.4495137e-06, Final residual = 7.9853402e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 5.4254391e-06, Final residual = 4.8026975e-08, No Iterations 3
time step continuity errors : sum local = 7.4397826e-10, global = 3.4069479e-13, cumulative = -1.7480822e-07
ExecutionTime = 369.32 s  ClockTime = 371 s

Time = 463

smoothSolver:  Solving for Ux, Initial residual = 9.7575486e-08, Final residual = 2.8719233e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.9530874e-08, Final residual = 3.0312937e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00019360512, Final residual = 1.6535324e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5453779e-05, Final residual = 2.3788801e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.3974713e-06, Final residual = 8.3264373e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 6.0530892e-06, Final residual = 5.7680518e-08, No Iterations 3
time step continuity errors : sum local = 8.9291722e-10, global = 3.5854327e-13, cumulative = -1.7480786e-07
ExecutionTime = 370.49 s  ClockTime = 372 s

Time = 464

smoothSolver:  Solving for Ux, Initial residual = 9.7132764e-08, Final residual = 2.8647787e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.9448689e-08, Final residual = 3.0233789e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00019283022, Final residual = 1.6618059e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.5275304e-05, Final residual = 2.3766984e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.3698697e-06, Final residual = 7.7064781e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 6.0211531e-06, Final residual = 5.6718802e-08, No Iterations 3
time step continuity errors : sum local = 8.7807647e-10, global = 3.524468e-13, cumulative = -1.7480751e-07
ExecutionTime = 371.46 s  ClockTime = 373 s

Time = 465

smoothSolver:  Solving for Ux, Initial residual = 9.6702986e-08, Final residual = 2.8573458e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.9382484e-08, Final residual = 3.015382e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00019197335, Final residual = 1.6624763e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.4999111e-05, Final residual = 2.4151123e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.330945e-06, Final residual = 1.8676167e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 5.6823792e-06, Final residual = 5.2026939e-08, No Iterations 3
time step continuity errors : sum local = 8.0570799e-10, global = -2.3514788e-13, cumulative = -1.7480775e-07
ExecutionTime = 372.55 s  ClockTime = 374 s

Time = 466

smoothSolver:  Solving for Ux, Initial residual = 9.6435876e-08, Final residual = 2.849699e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.9342379e-08, Final residual = 3.0073171e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00019109781, Final residual = 1.6568142e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.4701121e-05, Final residual = 2.4270885e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.2435323e-06, Final residual = 7.6646357e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 5.7331651e-06, Final residual = 5.4434425e-08, No Iterations 3
time step continuity errors : sum local = 8.4265344e-10, global = 2.0564779e-13, cumulative = -1.7480754e-07
ExecutionTime = 373.63 s  ClockTime = 375 s

Time = 467

smoothSolver:  Solving for Ux, Initial residual = 9.6069079e-08, Final residual = 2.8421911e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.9274447e-08, Final residual = 2.9991103e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00019031859, Final residual = 1.6404447e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.4562015e-05, Final residual = 2.4055627e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 9.12666e-06, Final residual = 8.5570661e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.4094173e-06, Final residual = 4.4605611e-08, No Iterations 3
time step continuity errors : sum local = 6.9121363e-10, global = 1.4463763e-13, cumulative = -1.748074e-07
ExecutionTime = 374.42 s  ClockTime = 376 s

Time = 468

smoothSolver:  Solving for Ux, Initial residual = 9.5779772e-08, Final residual = 2.8346983e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.9215513e-08, Final residual = 2.9909354e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001895378, Final residual = 1.60958e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.4337347e-05, Final residual = 2.3231313e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.9080461e-06, Final residual = 8.5166494e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.069663e-06, Final residual = 4.3937606e-08, No Iterations 6
time step continuity errors : sum local = 6.8022122e-10, global = 1.4404473e-13, cumulative = -1.7480725e-07
ExecutionTime = 375.3 s  ClockTime = 377 s

Time = 469

smoothSolver:  Solving for Ux, Initial residual = 9.5590254e-08, Final residual = 2.8272832e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.9170311e-08, Final residual = 2.9829455e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00018889726, Final residual = 1.5832458e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.425603e-05, Final residual = 2.3511672e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.8588787e-06, Final residual = 7.5266118e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.0810669e-06, Final residual = 3.8670293e-08, No Iterations 3
time step continuity errors : sum local = 5.9916557e-10, global = 1.4342671e-13, cumulative = -1.7480711e-07
ExecutionTime = 376.03 s  ClockTime = 378 s

Time = 470

smoothSolver:  Solving for Ux, Initial residual = 9.5168452e-08, Final residual = 2.8200651e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.9099861e-08, Final residual = 2.9750294e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00018820129, Final residual = 1.5444978e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.4209745e-05, Final residual = 2.3169422e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.783373e-06, Final residual = 7.8894144e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.0008354e-06, Final residual = 4.0774633e-08, No Iterations 3
time step continuity errors : sum local = 6.3163315e-10, global = 1.6335881e-13, cumulative = -1.7480695e-07
ExecutionTime = 376.68 s  ClockTime = 378 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012268

Time = 471

smoothSolver:  Solving for Ux, Initial residual = 9.4840694e-08, Final residual = 2.8128247e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.9043684e-08, Final residual = 2.9672824e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00018755391, Final residual = 1.4947392e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.4250851e-05, Final residual = 2.1975461e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.7031439e-06, Final residual = 8.6669623e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.8701872e-06, Final residual = 3.8086207e-08, No Iterations 7
time step continuity errors : sum local = 5.8969736e-10, global = 2.2744432e-13, cumulative = -1.7480672e-07
ExecutionTime = 377.58 s  ClockTime = 379 s

Time = 472

smoothSolver:  Solving for Ux, Initial residual = 9.4627091e-08, Final residual = 2.805579e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.8996222e-08, Final residual = 2.9596191e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00018701344, Final residual = 1.4615193e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.431648e-05, Final residual = 2.0696616e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.6972891e-06, Final residual = 6.2524946e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.0072699e-06, Final residual = 2.7373018e-08, No Iterations 4
time step continuity errors : sum local = 4.2411595e-10, global = 2.8708293e-13, cumulative = -1.7480643e-07
ExecutionTime = 378.52 s  ClockTime = 380 s

Time = 473

smoothSolver:  Solving for Ux, Initial residual = 9.4550643e-08, Final residual = 2.7989043e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.896297e-08, Final residual = 2.9520412e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00018650807, Final residual = 1.436753e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.4240355e-05, Final residual = 1.9434295e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.6810275e-06, Final residual = 8.3322687e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.6777094e-06, Final residual = 2.8309983e-08, No Iterations 5
time step continuity errors : sum local = 4.3897294e-10, global = 3.3289852e-13, cumulative = -1.748061e-07
ExecutionTime = 379.28 s  ClockTime = 381 s

Time = 474

smoothSolver:  Solving for Ux, Initial residual = 9.4186731e-08, Final residual = 2.7919099e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.890341e-08, Final residual = 2.9444577e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001860207, Final residual = 1.4248769e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.4131047e-05, Final residual = 1.8307088e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.6891541e-06, Final residual = 8.4958109e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.3614943e-06, Final residual = 1.037929e-08, No Iterations 5
time step continuity errors : sum local = 1.6155627e-10, global = -3.7726319e-14, cumulative = -1.7480614e-07
ExecutionTime = 380.04 s  ClockTime = 382 s

Time = 475

smoothSolver:  Solving for Ux, Initial residual = 9.3862673e-08, Final residual = 2.7847878e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.8841116e-08, Final residual = 2.9370262e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00018544273, Final residual = 1.4167687e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3948249e-05, Final residual = 1.7816705e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.6658416e-06, Final residual = 7.6320196e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.3173415e-06, Final residual = 3.4629825e-08, No Iterations 6
time step continuity errors : sum local = 5.3662083e-10, global = 3.3848241e-13, cumulative = -1.748058e-07
ExecutionTime = 380.71 s  ClockTime = 383 s

Time = 476

smoothSolver:  Solving for Ux, Initial residual = 9.3594685e-08, Final residual = 2.7775695e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.8789463e-08, Final residual = 2.9295196e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00018485625, Final residual = 1.402965e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3819614e-05, Final residual = 1.8057343e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.6734424e-06, Final residual = 7.3138741e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.3134413e-06, Final residual = 3.3754864e-08, No Iterations 6
time step continuity errors : sum local = 5.2315327e-10, global = 3.5823396e-13, cumulative = -1.7480544e-07
ExecutionTime = 381.55 s  ClockTime = 383 s

Time = 477

smoothSolver:  Solving for Ux, Initial residual = 9.3413153e-08, Final residual = 2.7707046e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.8743335e-08, Final residual = 2.9221062e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001842101, Final residual = 1.385728e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3681211e-05, Final residual = 1.8490999e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.6795628e-06, Final residual = 7.2968581e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.3257918e-06, Final residual = 3.4188021e-08, No Iterations 6
time step continuity errors : sum local = 5.2980284e-10, global = 4.0493841e-13, cumulative = -1.7480503e-07
ExecutionTime = 382.27 s  ClockTime = 384 s

Time = 478

smoothSolver:  Solving for Ux, Initial residual = 9.3228079e-08, Final residual = 2.7639334e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.8696681e-08, Final residual = 2.9144312e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00018362588, Final residual = 1.3818859e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3577319e-05, Final residual = 1.8818971e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.685181e-06, Final residual = 7.529888e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.3683876e-06, Final residual = 1.0997445e-08, No Iterations 5
time step continuity errors : sum local = 1.7123302e-10, global = 1.86565e-14, cumulative = -1.7480502e-07
ExecutionTime = 383.8 s  ClockTime = 386 s

Time = 479

smoothSolver:  Solving for Ux, Initial residual = 9.2981342e-08, Final residual = 2.7572007e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.863905e-08, Final residual = 2.907092e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00018296649, Final residual = 1.3866079e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3397877e-05, Final residual = 1.8795497e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.5939495e-06, Final residual = 7.9344194e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.3721591e-06, Final residual = 3.7973833e-08, No Iterations 6
time step continuity errors : sum local = 5.8820853e-10, global = 3.6967723e-13, cumulative = -1.7480465e-07
ExecutionTime = 384.84 s  ClockTime = 387 s

Time = 480

smoothSolver:  Solving for Ux, Initial residual = 9.2715656e-08, Final residual = 2.7501165e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.8587023e-08, Final residual = 2.8996197e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001823513, Final residual = 1.3884979e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3221652e-05, Final residual = 1.8810426e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.5379717e-06, Final residual = 8.4712532e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.3846017e-06, Final residual = 3.8976464e-08, No Iterations 6
time step continuity errors : sum local = 6.0364397e-10, global = 3.8520294e-13, cumulative = -1.7480426e-07
ExecutionTime = 385.91 s  ClockTime = 388 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012268

Time = 481

smoothSolver:  Solving for Ux, Initial residual = 9.2543539e-08, Final residual = 2.7429959e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.8544524e-08, Final residual = 2.8924864e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00018166649, Final residual = 1.3842148e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2985115e-05, Final residual = 1.8863861e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.4222384e-06, Final residual = 7.7096856e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.6076135e-06, Final residual = 3.0191245e-08, No Iterations 3
time step continuity errors : sum local = 4.6795696e-10, global = 3.8447665e-13, cumulative = -1.7480388e-07
ExecutionTime = 386.83 s  ClockTime = 389 s

Time = 482

smoothSolver:  Solving for Ux, Initial residual = 9.2225177e-08, Final residual = 2.7355387e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.8494615e-08, Final residual = 2.8851682e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00018104059, Final residual = 1.3792926e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2816313e-05, Final residual = 1.8946788e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.323264e-06, Final residual = 7.6688717e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.5921764e-06, Final residual = 3.2535674e-08, No Iterations 3
time step continuity errors : sum local = 5.0426875e-10, global = 4.3047537e-13, cumulative = -1.7480345e-07
ExecutionTime = 387.84 s  ClockTime = 390 s

Time = 483

smoothSolver:  Solving for Ux, Initial residual = 9.2076643e-08, Final residual = 2.7281658e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.8456252e-08, Final residual = 2.878122e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00018031722, Final residual = 1.3732405e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2702457e-05, Final residual = 1.9037749e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.2229459e-06, Final residual = 8.0967946e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.6261709e-06, Final residual = 3.7798374e-08, No Iterations 4
time step continuity errors : sum local = 5.8556789e-10, global = 5.028306e-13, cumulative = -1.7480294e-07
ExecutionTime = 389.04 s  ClockTime = 391 s

Time = 484

smoothSolver:  Solving for Ux, Initial residual = 9.1738522e-08, Final residual = 2.7205125e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.8412053e-08, Final residual = 2.8708193e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017964962, Final residual = 1.3701018e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2691313e-05, Final residual = 1.9262541e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.2034754e-06, Final residual = 6.156491e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.4843039e-06, Final residual = 3.8346497e-08, No Iterations 6
time step continuity errors : sum local = 5.9404326e-10, global = 5.6293397e-13, cumulative = -1.7480238e-07
ExecutionTime = 390.15 s  ClockTime = 392 s

Time = 485

smoothSolver:  Solving for Ux, Initial residual = 9.1617684e-08, Final residual = 2.7131272e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.8380538e-08, Final residual = 2.8640289e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017898904, Final residual = 1.3664066e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2670605e-05, Final residual = 1.9580806e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.1518216e-06, Final residual = 8.0967363e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.7028719e-06, Final residual = 4.2109185e-08, No Iterations 5
time step continuity errors : sum local = 6.5238029e-10, global = 6.2206168e-13, cumulative = -1.7480176e-07
ExecutionTime = 392.14 s  ClockTime = 394 s

Time = 486

smoothSolver:  Solving for Ux, Initial residual = 9.1458125e-08, Final residual = 2.7055003e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.835033e-08, Final residual = 2.8569222e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017855228, Final residual = 1.3708867e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2869769e-05, Final residual = 2.0265849e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.2084004e-06, Final residual = 8.1260553e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.6728692e-06, Final residual = 4.3952434e-08, No Iterations 5
time step continuity errors : sum local = 6.8061782e-10, global = 7.1945862e-13, cumulative = -1.7480104e-07
ExecutionTime = 393.62 s  ClockTime = 395 s

Time = 487

smoothSolver:  Solving for Ux, Initial residual = 9.1322133e-08, Final residual = 2.6983061e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.8311036e-08, Final residual = 2.8502416e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017816219, Final residual = 1.3786711e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3032503e-05, Final residual = 2.1131666e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.2539433e-06, Final residual = 8.104648e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.6471252e-06, Final residual = 1.9778775e-08, No Iterations 3
time step continuity errors : sum local = 3.0713553e-10, global = 2.8746834e-13, cumulative = -1.7480075e-07
ExecutionTime = 394.52 s  ClockTime = 396 s

Time = 488

smoothSolver:  Solving for Ux, Initial residual = 9.0979845e-08, Final residual = 2.690844e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.8250156e-08, Final residual = 2.8430985e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017781341, Final residual = 1.3859886e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3234971e-05, Final residual = 2.2205601e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.3930452e-06, Final residual = 1.6205386e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.7150132e-06, Final residual = 2.5697666e-08, No Iterations 4
time step continuity errors : sum local = 3.9810662e-10, global = 2.9462087e-13, cumulative = -1.7480046e-07
ExecutionTime = 395.62 s  ClockTime = 397 s

Time = 489

smoothSolver:  Solving for Ux, Initial residual = 9.1094991e-08, Final residual = 2.6839006e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.8249787e-08, Final residual = 2.836528e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017745224, Final residual = 1.3885993e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.33979e-05, Final residual = 2.2982133e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.4519334e-06, Final residual = 1.7791088e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.8013915e-06, Final residual = 3.8236786e-08, No Iterations 4
time step continuity errors : sum local = 5.9233298e-10, global = 1.0159924e-13, cumulative = -1.7480036e-07
ExecutionTime = 397.22 s  ClockTime = 399 s

Time = 490

smoothSolver:  Solving for Ux, Initial residual = 9.0973396e-08, Final residual = 2.6770532e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.8234534e-08, Final residual = 2.8294129e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017717714, Final residual = 1.3949769e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3550503e-05, Final residual = 1.659873e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.9588853e-06, Final residual = 8.3199528e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 4.3338204e-06, Final residual = 4.3277789e-08, No Iterations 5
time step continuity errors : sum local = 6.7033072e-10, global = 3.7409436e-13, cumulative = -1.7479998e-07
ExecutionTime = 398.79 s  ClockTime = 401 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012268

Time = 491

smoothSolver:  Solving for Ux, Initial residual = 9.0803199e-08, Final residual = 2.6709602e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.8191504e-08, Final residual = 2.8228295e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017686544, Final residual = 1.4003773e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.3383466e-05, Final residual = 2.2588456e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.6828286e-06, Final residual = 8.2664696e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.8221204e-06, Final residual = 4.3622906e-08, No Iterations 4
time step continuity errors : sum local = 6.7563719e-10, global = 3.1492826e-13, cumulative = -1.7479967e-07
ExecutionTime = 400.19 s  ClockTime = 402 s

Time = 492

smoothSolver:  Solving for Ux, Initial residual = 9.0630938e-08, Final residual = 2.6643649e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.8160575e-08, Final residual = 2.8156915e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017658971, Final residual = 1.4110813e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.320053e-05, Final residual = 2.2828991e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.625084e-06, Final residual = 7.1367209e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 5.031526e-06, Final residual = 3.8977835e-08, No Iterations 3
time step continuity errors : sum local = 6.0405285e-10, global = 2.8042314e-13, cumulative = -1.7479939e-07
ExecutionTime = 403.51 s  ClockTime = 405 s

Time = 493

smoothSolver:  Solving for Ux, Initial residual = 9.0141623e-08, Final residual = 2.6585904e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.8069353e-08, Final residual = 2.8089674e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017618559, Final residual = 1.4371749e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2920939e-05, Final residual = 2.2488826e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.564867e-06, Final residual = 6.0582135e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 5.0551862e-06, Final residual = 4.3645464e-08, No Iterations 3
time step continuity errors : sum local = 6.7637446e-10, global = 2.6396172e-13, cumulative = -1.7479912e-07
ExecutionTime = 415.35 s  ClockTime = 417 s

Time = 494

smoothSolver:  Solving for Ux, Initial residual = 8.991714e-08, Final residual = 2.6523061e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.8035192e-08, Final residual = 2.8015855e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017571004, Final residual = 1.4749874e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2905023e-05, Final residual = 2.1437071e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.4633032e-06, Final residual = 7.0807288e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 5.4269218e-06, Final residual = 5.3444138e-08, No Iterations 3
time step continuity errors : sum local = 8.2748948e-10, global = 2.9171747e-13, cumulative = -1.7479883e-07
ExecutionTime = 417.22 s  ClockTime = 419 s

Time = 495

smoothSolver:  Solving for Ux, Initial residual = 8.9586544e-08, Final residual = 2.6461571e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7968881e-08, Final residual = 2.7947913e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017503005, Final residual = 1.4932162e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2678213e-05, Final residual = 2.1167716e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.3565366e-06, Final residual = 7.417809e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 5.3061389e-06, Final residual = 5.2188462e-08, No Iterations 3
time step continuity errors : sum local = 8.0823564e-10, global = 3.1810025e-13, cumulative = -1.7479851e-07
ExecutionTime = 419.66 s  ClockTime = 422 s

Time = 496

smoothSolver:  Solving for Ux, Initial residual = 8.9299312e-08, Final residual = 2.6395179e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7929054e-08, Final residual = 2.7871903e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017431315, Final residual = 1.5063205e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2422666e-05, Final residual = 2.1387523e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.3025559e-06, Final residual = 8.1033139e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.9576906e-06, Final residual = 4.6657718e-08, No Iterations 3
time step continuity errors : sum local = 7.2257226e-10, global = 3.1651817e-13, cumulative = -1.747982e-07
ExecutionTime = 421.34 s  ClockTime = 423 s

Time = 497

smoothSolver:  Solving for Ux, Initial residual = 8.9053391e-08, Final residual = 2.633069e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7874466e-08, Final residual = 2.7803648e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017361382, Final residual = 1.5011124e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2284418e-05, Final residual = 2.1461094e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.1471819e-06, Final residual = 7.6302989e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.7625385e-06, Final residual = 4.2258214e-08, No Iterations 3
time step continuity errors : sum local = 6.5463523e-10, global = 3.7778246e-13, cumulative = -1.7479782e-07
ExecutionTime = 422.33 s  ClockTime = 424 s

Time = 498

smoothSolver:  Solving for Ux, Initial residual = 8.884124e-08, Final residual = 2.6261604e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7843191e-08, Final residual = 2.7728707e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017295451, Final residual = 1.4734565e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2219744e-05, Final residual = 2.1167457e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.0995177e-06, Final residual = 7.5597874e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.582805e-06, Final residual = 4.4604859e-08, No Iterations 5
time step continuity errors : sum local = 6.9079318e-10, global = 4.2409295e-13, cumulative = -1.7479739e-07
ExecutionTime = 424.19 s  ClockTime = 426 s

Time = 499

smoothSolver:  Solving for Ux, Initial residual = 8.8753253e-08, Final residual = 2.6198193e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.780617e-08, Final residual = 2.7662986e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017237272, Final residual = 1.4546685e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2204128e-05, Final residual = 2.2091425e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.0852966e-06, Final residual = 7.0232818e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.6514038e-06, Final residual = 3.0283357e-08, No Iterations 3
time step continuity errors : sum local = 4.6942252e-10, global = 4.647758e-13, cumulative = -1.7479693e-07
ExecutionTime = 425.74 s  ClockTime = 428 s

Time = 500

smoothSolver:  Solving for Ux, Initial residual = 8.8310399e-08, Final residual = 2.6130639e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7745643e-08, Final residual = 2.7591723e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017175374, Final residual = 1.4053199e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2197658e-05, Final residual = 2.1644296e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.0102663e-06, Final residual = 7.3858542e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.5790107e-06, Final residual = 2.4820617e-08, No Iterations 3
time step continuity errors : sum local = 3.8536216e-10, global = 1.6150849e-13, cumulative = -1.7479677e-07
ExecutionTime = 427.05 s  ClockTime = 429 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012268

Time = 501

smoothSolver:  Solving for Ux, Initial residual = 8.7921468e-08, Final residual = 2.6069818e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7665768e-08, Final residual = 2.7529035e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017120477, Final residual = 1.3668856e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2234014e-05, Final residual = 2.0821578e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.9438952e-06, Final residual = 6.0312108e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.6704633e-06, Final residual = 3.8093355e-08, No Iterations 4
time step continuity errors : sum local = 5.902654e-10, global = 3.776948e-13, cumulative = -1.7479639e-07
ExecutionTime = 427.68 s  ClockTime = 430 s

Time = 502

smoothSolver:  Solving for Ux, Initial residual = 8.7645101e-08, Final residual = 2.6003813e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7631141e-08, Final residual = 2.7459468e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017079017, Final residual = 1.3461737e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2312447e-05, Final residual = 1.9700134e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.9613792e-06, Final residual = 6.3107785e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.6224832e-06, Final residual = 1.5337914e-08, No Iterations 3
time step continuity errors : sum local = 2.3850116e-10, global = -7.2335808e-14, cumulative = -1.7479646e-07
ExecutionTime = 428.29 s  ClockTime = 430 s

Time = 503

smoothSolver:  Solving for Ux, Initial residual = 8.763331e-08, Final residual = 2.594615e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7603811e-08, Final residual = 2.7399419e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017039705, Final residual = 1.3323584e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2242117e-05, Final residual = 1.8289412e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.9375952e-06, Final residual = 6.6191514e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.5445903e-06, Final residual = 3.7265487e-08, No Iterations 4
time step continuity errors : sum local = 5.7757353e-10, global = 3.2938731e-13, cumulative = -1.7479613e-07
ExecutionTime = 428.91 s  ClockTime = 431 s

Time = 504

smoothSolver:  Solving for Ux, Initial residual = 8.725741e-08, Final residual = 2.5883256e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7555206e-08, Final residual = 2.7330997e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00017001796, Final residual = 1.3271228e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.2153088e-05, Final residual = 1.6981043e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.9434103e-06, Final residual = 7.9023869e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.9998585e-06, Final residual = 2.5339018e-08, No Iterations 10
time step continuity errors : sum local = 3.9313445e-10, global = 2.8871281e-13, cumulative = -1.7479584e-07
ExecutionTime = 429.58 s  ClockTime = 432 s

Time = 505

smoothSolver:  Solving for Ux, Initial residual = 8.7119803e-08, Final residual = 2.5824858e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7499556e-08, Final residual = 2.7271261e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00016954972, Final residual = 1.3194833e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1961795e-05, Final residual = 1.6125898e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.9016645e-06, Final residual = 7.0124981e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.9188253e-06, Final residual = 3.7033181e-08, No Iterations 6
time step continuity errors : sum local = 5.733982e-10, global = 2.622273e-13, cumulative = -1.7479558e-07
ExecutionTime = 430.21 s  ClockTime = 432 s

Time = 506

smoothSolver:  Solving for Ux, Initial residual = 8.6951413e-08, Final residual = 2.5758908e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7476394e-08, Final residual = 2.7202442e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00016904638, Final residual = 1.3118131e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1838624e-05, Final residual = 1.6144033e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.874169e-06, Final residual = 6.6818129e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.9042569e-06, Final residual = 1.051104e-08, No Iterations 5
time step continuity errors : sum local = 1.6380993e-10, global = -1.3053436e-13, cumulative = -1.7479571e-07
ExecutionTime = 430.93 s  ClockTime = 433 s

Time = 507

smoothSolver:  Solving for Ux, Initial residual = 8.6714784e-08, Final residual = 2.5699767e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7418057e-08, Final residual = 2.7141333e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00016847027, Final residual = 1.2945552e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1646717e-05, Final residual = 1.5992021e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.7913473e-06, Final residual = 6.5251674e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.8657916e-06, Final residual = 1.058559e-08, No Iterations 5
time step continuity errors : sum local = 1.6507445e-10, global = -3.2876413e-13, cumulative = -1.7479604e-07
ExecutionTime = 431.54 s  ClockTime = 434 s

Time = 508

smoothSolver:  Solving for Ux, Initial residual = 8.6522326e-08, Final residual = 2.5637758e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7396769e-08, Final residual = 2.7070781e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00016795567, Final residual = 1.2908945e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1531877e-05, Final residual = 1.5785845e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.7708732e-06, Final residual = 6.5823387e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.8761714e-06, Final residual = 3.8115398e-08, No Iterations 6
time step continuity errors : sum local = 5.9051147e-10, global = -1.2217845e-14, cumulative = -1.7479605e-07
ExecutionTime = 432.18 s  ClockTime = 434 s

Time = 509

smoothSolver:  Solving for Ux, Initial residual = 8.6326311e-08, Final residual = 2.5581109e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7331123e-08, Final residual = 2.7011331e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00016740749, Final residual = 1.2814588e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.134788e-05, Final residual = 1.5651004e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.7043373e-06, Final residual = 6.7589323e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.8618205e-06, Final residual = 3.5735499e-08, No Iterations 7
time step continuity errors : sum local = 5.5366334e-10, global = -4.0496862e-14, cumulative = -1.7479609e-07
ExecutionTime = 432.87 s  ClockTime = 435 s

Time = 510

smoothSolver:  Solving for Ux, Initial residual = 8.6042021e-08, Final residual = 2.5515076e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7293727e-08, Final residual = 2.6942536e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00016688952, Final residual = 1.2732424e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1216871e-05, Final residual = 1.5686192e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.6628483e-06, Final residual = 7.1129242e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.8671478e-06, Final residual = 3.7977858e-08, No Iterations 6
time step continuity errors : sum local = 5.8801586e-10, global = -9.7574063e-14, cumulative = -1.7479619e-07
ExecutionTime = 433.73 s  ClockTime = 436 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012268

Time = 511

smoothSolver:  Solving for Ux, Initial residual = 8.585594e-08, Final residual = 2.5454566e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7233675e-08, Final residual = 2.6884271e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00016630876, Final residual = 1.2627183e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1007249e-05, Final residual = 1.5850151e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.5881447e-06, Final residual = 7.5388282e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.8500076e-06, Final residual = 2.81805e-08, No Iterations 9
time step continuity errors : sum local = 4.3699828e-10, global = -9.7631487e-14, cumulative = -1.7479629e-07
ExecutionTime = 434.58 s  ClockTime = 437 s

Time = 512

smoothSolver:  Solving for Ux, Initial residual = 8.5665513e-08, Final residual = 2.5385604e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7212354e-08, Final residual = 2.6815953e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001657518, Final residual = 1.2605893e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0873975e-05, Final residual = 1.6127494e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.5474174e-06, Final residual = 6.376719e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.047488e-06, Final residual = 3.0933257e-08, No Iterations 3
time step continuity errors : sum local = 4.7965627e-10, global = -1.0731482e-13, cumulative = -1.747964e-07
ExecutionTime = 435.38 s  ClockTime = 438 s

Time = 513

smoothSolver:  Solving for Ux, Initial residual = 8.5368932e-08, Final residual = 2.53241e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.714669e-08, Final residual = 2.6757785e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00016511387, Final residual = 1.2616323e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0759798e-05, Final residual = 1.6512522e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.478656e-06, Final residual = 6.4919647e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.0652198e-06, Final residual = 2.9272465e-08, No Iterations 4
time step continuity errors : sum local = 4.5412913e-10, global = -7.2907995e-14, cumulative = -1.7479647e-07
ExecutionTime = 436.06 s  ClockTime = 438 s

Time = 514

smoothSolver:  Solving for Ux, Initial residual = 8.5102289e-08, Final residual = 2.5254307e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7125087e-08, Final residual = 2.6689445e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00016453024, Final residual = 1.2705539e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0767627e-05, Final residual = 1.7057364e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.440038e-06, Final residual = 6.7913252e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1240034e-06, Final residual = 2.8138717e-08, No Iterations 4
time step continuity errors : sum local = 4.3635196e-10, global = -1.36104e-14, cumulative = -1.7479648e-07
ExecutionTime = 436.88 s  ClockTime = 439 s

Time = 515

smoothSolver:  Solving for Ux, Initial residual = 8.5022566e-08, Final residual = 2.5192801e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7084256e-08, Final residual = 2.6632842e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00016389541, Final residual = 1.2728455e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0751496e-05, Final residual = 1.7878219e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.4073557e-06, Final residual = 6.5201747e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1427285e-06, Final residual = 3.3534792e-08, No Iterations 4
time step continuity errors : sum local = 5.1985726e-10, global = 3.0036153e-14, cumulative = -1.7479645e-07
ExecutionTime = 437.69 s  ClockTime = 440 s

Time = 516

smoothSolver:  Solving for Ux, Initial residual = 8.4935765e-08, Final residual = 2.5122737e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7081331e-08, Final residual = 2.6566449e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00016344317, Final residual = 1.2771521e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0905145e-05, Final residual = 1.8664771e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.4274115e-06, Final residual = 6.3318237e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1829e-06, Final residual = 3.0246223e-08, No Iterations 4
time step continuity errors : sum local = 4.6875862e-10, global = 9.1619062e-14, cumulative = -1.7479636e-07
ExecutionTime = 438.73 s  ClockTime = 441 s

Time = 517

smoothSolver:  Solving for Ux, Initial residual = 8.4861248e-08, Final residual = 2.5061465e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.703852e-08, Final residual = 2.6511883e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00016308097, Final residual = 1.2784927e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1072781e-05, Final residual = 1.9534892e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.4251222e-06, Final residual = 6.210796e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.1727841e-06, Final residual = 2.2535683e-08, No Iterations 4
time step continuity errors : sum local = 3.4996672e-10, global = 1.5364301e-13, cumulative = -1.7479621e-07
ExecutionTime = 439.56 s  ClockTime = 442 s

Time = 518

smoothSolver:  Solving for Ux, Initial residual = 8.4612498e-08, Final residual = 2.4991805e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.7013642e-08, Final residual = 2.6446579e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00016279488, Final residual = 1.2859281e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1278241e-05, Final residual = 2.0186359e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.5351403e-06, Final residual = 6.956781e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.2023515e-06, Final residual = 2.7878683e-08, No Iterations 4
time step continuity errors : sum local = 4.3202423e-10, global = 2.052185e-13, cumulative = -1.74796e-07
ExecutionTime = 440.49 s  ClockTime = 443 s

Time = 519

smoothSolver:  Solving for Ux, Initial residual = 8.4431302e-08, Final residual = 2.4931376e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6956727e-08, Final residual = 2.6393266e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00016248463, Final residual = 1.2884026e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.142628e-05, Final residual = 2.0903424e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.6662668e-06, Final residual = 6.1588747e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.4663482e-06, Final residual = 4.0902002e-08, No Iterations 4
time step continuity errors : sum local = 6.3364417e-10, global = 2.8446219e-13, cumulative = -1.7479572e-07
ExecutionTime = 441.19 s  ClockTime = 443 s

Time = 520

smoothSolver:  Solving for Ux, Initial residual = 8.4288248e-08, Final residual = 2.486353e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6947216e-08, Final residual = 2.6325947e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00016224483, Final residual = 1.2940484e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1672463e-05, Final residual = 2.1321293e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.8677744e-06, Final residual = 6.6933529e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.5980218e-06, Final residual = 3.5654651e-08, No Iterations 3
time step continuity errors : sum local = 5.5244428e-10, global = 3.4606152e-13, cumulative = -1.7479537e-07
ExecutionTime = 441.95 s  ClockTime = 444 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012268

Time = 521

smoothSolver:  Solving for Ux, Initial residual = 8.4045762e-08, Final residual = 2.4812708e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6886869e-08, Final residual = 2.6274529e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00016197235, Final residual = 1.3017284e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1711098e-05, Final residual = 2.154001e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.8704771e-06, Final residual = 7.634877e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 4.4361317e-06, Final residual = 2.1028091e-08, No Iterations 3
time step continuity errors : sum local = 3.2655836e-10, global = -5.5569454e-14, cumulative = -1.7479543e-07
ExecutionTime = 442.62 s  ClockTime = 445 s

Time = 522

smoothSolver:  Solving for Ux, Initial residual = 8.3693046e-08, Final residual = 2.4751362e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6850279e-08, Final residual = 2.6209885e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00016179366, Final residual = 1.3071553e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1643228e-05, Final residual = 2.0799174e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 8.0431726e-06, Final residual = 4.904005e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.3088865e-06, Final residual = 3.3718384e-08, No Iterations 4
time step continuity errors : sum local = 5.2270353e-10, global = 3.7119133e-13, cumulative = -1.7479506e-07
ExecutionTime = 443.48 s  ClockTime = 446 s

Time = 523

smoothSolver:  Solving for Ux, Initial residual = 8.3693297e-08, Final residual = 2.4699624e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6817881e-08, Final residual = 2.6156373e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00016149246, Final residual = 1.3107517e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1400651e-05, Final residual = 2.0734515e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.9724452e-06, Final residual = 4.4541215e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.5454626e-06, Final residual = 3.577651e-08, No Iterations 3
time step continuity errors : sum local = 5.5438931e-10, global = 3.9839647e-13, cumulative = -1.7479466e-07
ExecutionTime = 444.2 s  ClockTime = 446 s

Time = 524

smoothSolver:  Solving for Ux, Initial residual = 8.3708499e-08, Final residual = 2.4644283e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6833871e-08, Final residual = 2.6088501e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00016114264, Final residual = 1.3135509e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.1244291e-05, Final residual = 2.104405e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.9530513e-06, Final residual = 4.5335421e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.5549075e-06, Final residual = 3.8955962e-08, No Iterations 3
time step continuity errors : sum local = 6.0349973e-10, global = 4.0911224e-13, cumulative = -1.7479425e-07
ExecutionTime = 444.93 s  ClockTime = 447 s

Time = 525

smoothSolver:  Solving for Ux, Initial residual = 8.3569472e-08, Final residual = 2.4594671e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6779441e-08, Final residual = 2.603199e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001605923, Final residual = 1.3318593e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.105708e-05, Final residual = 2.0025238e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.8272412e-06, Final residual = 1.5362898e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.6968772e-06, Final residual = 4.1474329e-08, No Iterations 3
time step continuity errors : sum local = 6.4243747e-10, global = -2.5220996e-14, cumulative = -1.7479427e-07
ExecutionTime = 445.7 s  ClockTime = 448 s

Time = 526

smoothSolver:  Solving for Ux, Initial residual = 8.3249198e-08, Final residual = 2.4533347e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.675482e-08, Final residual = 2.5962428e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00015997368, Final residual = 1.3594291e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0897256e-05, Final residual = 1.9258521e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.7196968e-06, Final residual = 4.2913369e-08, No Iterations 7
GAMG:  Solving for p, Initial residual = 4.7463172e-06, Final residual = 4.6315184e-08, No Iterations 3
time step continuity errors : sum local = 7.1747179e-10, global = 3.5217849e-13, cumulative = -1.7479392e-07
ExecutionTime = 446.5 s  ClockTime = 449 s

Time = 527

smoothSolver:  Solving for Ux, Initial residual = 8.3177957e-08, Final residual = 2.4481841e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6702129e-08, Final residual = 2.5905105e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00015925129, Final residual = 1.3670095e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0644641e-05, Final residual = 1.9271905e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.5530028e-06, Final residual = 7.2206018e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.5039017e-06, Final residual = 3.1044218e-08, No Iterations 3
time step continuity errors : sum local = 4.8138661e-10, global = 3.1265085e-13, cumulative = -1.7479361e-07
ExecutionTime = 447.28 s  ClockTime = 450 s

Time = 528

smoothSolver:  Solving for Ux, Initial residual = 8.272251e-08, Final residual = 2.4419238e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6653346e-08, Final residual = 2.5833675e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00015864742, Final residual = 1.3547397e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0615997e-05, Final residual = 1.9808953e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.5019321e-06, Final residual = 6.0503174e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.4920452e-06, Final residual = 3.1669975e-08, No Iterations 3
time step continuity errors : sum local = 4.9110016e-10, global = 3.1897353e-13, cumulative = -1.7479329e-07
ExecutionTime = 448.07 s  ClockTime = 450 s

Time = 529

smoothSolver:  Solving for Ux, Initial residual = 8.2374352e-08, Final residual = 2.4367466e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6563794e-08, Final residual = 2.5775534e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00015800333, Final residual = 1.3185285e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0545092e-05, Final residual = 1.4569119e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.759597e-06, Final residual = 7.4661409e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.8488549e-06, Final residual = 3.4340261e-08, No Iterations 3
time step continuity errors : sum local = 5.3212895e-10, global = 3.1330956e-13, cumulative = -1.7479298e-07
ExecutionTime = 448.83 s  ClockTime = 451 s

Time = 530

smoothSolver:  Solving for Ux, Initial residual = 8.2019238e-08, Final residual = 2.4304017e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6533516e-08, Final residual = 2.5707017e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00015749179, Final residual = 1.2761034e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0621188e-05, Final residual = 1.44968e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7552312e-06, Final residual = 7.3365508e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.766568e-06, Final residual = 1.3373834e-08, No Iterations 4
time step continuity errors : sum local = 2.0819706e-10, global = -1.9021155e-13, cumulative = -1.7479317e-07
ExecutionTime = 449.53 s  ClockTime = 452 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.012268

Time = 531

smoothSolver:  Solving for Ux, Initial residual = 8.184015e-08, Final residual = 2.4253138e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6475683e-08, Final residual = 2.5654341e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00015700691, Final residual = 1.2430603e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0681058e-05, Final residual = 1.9917688e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.4169238e-06, Final residual = 6.1090408e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.3025139e-06, Final residual = 3.5615447e-08, No Iterations 4
time step continuity errors : sum local = 5.5177544e-10, global = 2.2293753e-13, cumulative = -1.7479294e-07
ExecutionTime = 450.27 s  ClockTime = 453 s

Time = 532

smoothSolver:  Solving for Ux, Initial residual = 8.1619264e-08, Final residual = 2.4191364e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.645625e-08, Final residual = 2.5589333e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00015666992, Final residual = 1.2263438e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0773253e-05, Final residual = 1.8691026e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.4432012e-06, Final residual = 5.8765271e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.245814e-06, Final residual = 2.9022289e-08, No Iterations 4
time step continuity errors : sum local = 4.5018036e-10, global = 1.9897117e-13, cumulative = -1.7479275e-07
ExecutionTime = 451.05 s  ClockTime = 453 s

Time = 533

smoothSolver:  Solving for Ux, Initial residual = 8.1375832e-08, Final residual = 2.4141679e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6383779e-08, Final residual = 2.5539777e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00015634829, Final residual = 1.2133011e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0675274e-05, Final residual = 1.7331937e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.4115035e-06, Final residual = 5.7270138e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.1815892e-06, Final residual = 3.1671434e-08, No Iterations 4
time step continuity errors : sum local = 4.9114229e-10, global = 1.8582339e-13, cumulative = -1.7479256e-07
ExecutionTime = 451.94 s  ClockTime = 454 s

Time = 534

smoothSolver:  Solving for Ux, Initial residual = 8.114183e-08, Final residual = 2.4083607e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6369619e-08, Final residual = 2.547566e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00015607899, Final residual = 1.212985e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0617927e-05, Final residual = 1.5882599e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.404188e-06, Final residual = 5.5491447e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.1207969e-06, Final residual = 2.6178342e-08, No Iterations 4
time step continuity errors : sum local = 4.0598834e-10, global = 1.9634229e-13, cumulative = -1.7479236e-07
ExecutionTime = 452.9 s  ClockTime = 455 s

Time = 535

smoothSolver:  Solving for Ux, Initial residual = 8.0989632e-08, Final residual = 2.4035605e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6306678e-08, Final residual = 2.542628e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00015564774, Final residual = 1.2026617e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0505073e-05, Final residual = 1.5057893e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.3796754e-06, Final residual = 6.9870908e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.7094092e-06, Final residual = 3.65463e-08, No Iterations 6
time step continuity errors : sum local = 5.6627129e-10, global = 2.2052668e-13, cumulative = -1.7479214e-07
ExecutionTime = 453.74 s  ClockTime = 456 s

Time = 536

smoothSolver:  Solving for Ux, Initial residual = 8.0781602e-08, Final residual = 2.3974997e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6295905e-08, Final residual = 2.5361188e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00015520348, Final residual = 1.1933436e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0446e-05, Final residual = 1.5005513e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.3823697e-06, Final residual = 6.7984799e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.7076052e-06, Final residual = 1.0570031e-08, No Iterations 5
time step continuity errors : sum local = 1.645743e-10, global = -1.9669247e-13, cumulative = -1.7479234e-07
ExecutionTime = 454.44 s  ClockTime = 457 s

Time = 537

smoothSolver:  Solving for Ux, Initial residual = 8.0632944e-08, Final residual = 2.3926523e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6233815e-08, Final residual = 2.5311518e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001547229, Final residual = 1.1715423e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0305607e-05, Final residual = 1.5088872e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.3711061e-06, Final residual = 6.7025166e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.6953389e-06, Final residual = 3.3235414e-08, No Iterations 6
time step continuity errors : sum local = 5.1487839e-10, global = 1.4722022e-13, cumulative = -1.7479219e-07
ExecutionTime = 455.14 s  ClockTime = 457 s

Time = 538

smoothSolver:  Solving for Ux, Initial residual = 8.0467988e-08, Final residual = 2.3867643e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6224112e-08, Final residual = 2.5246278e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00015429443, Final residual = 1.166412e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0215817e-05, Final residual = 1.5263255e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.3703328e-06, Final residual = 6.7512056e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.6991939e-06, Final residual = 2.5443175e-08, No Iterations 6
time step continuity errors : sum local = 3.944925e-10, global = 1.5097601e-13, cumulative = -1.7479204e-07
ExecutionTime = 455.81 s  ClockTime = 458 s

Time = 539

smoothSolver:  Solving for Ux, Initial residual = 8.0339444e-08, Final residual = 2.3822687e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6153639e-08, Final residual = 2.5196505e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00015379706, Final residual = 1.1583618e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 2.0010613e-05, Final residual = 1.5309197e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.3177858e-06, Final residual = 6.7676092e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.6770677e-06, Final residual = 3.3264696e-08, No Iterations 5
time step continuity errors : sum local = 5.1551266e-10, global = 1.6364928e-13, cumulative = -1.7479188e-07
ExecutionTime = 456.45 s  ClockTime = 459 s

Time = 540

smoothSolver:  Solving for Ux, Initial residual = 8.0082283e-08, Final residual = 2.3762855e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6140502e-08, Final residual = 2.5131803e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00015334633, Final residual = 1.1589749e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9869457e-05, Final residual = 1.5252092e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.2705739e-06, Final residual = 7.0218466e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.684533e-06, Final residual = 3.6336415e-08, No Iterations 5
time step continuity errors : sum local = 5.6329873e-10, global = 1.8118077e-13, cumulative = -1.747917e-07
ExecutionTime = 457.15 s  ClockTime = 459 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122679

Time = 541

smoothSolver:  Solving for Ux, Initial residual = 7.9967531e-08, Final residual = 2.371455e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6077597e-08, Final residual = 2.5083095e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00015277815, Final residual = 1.1540207e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9657868e-05, Final residual = 1.5094727e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.2059675e-06, Final residual = 5.7471403e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.830672e-06, Final residual = 3.0168699e-08, No Iterations 3
time step continuity errors : sum local = 4.6755437e-10, global = 1.7974981e-13, cumulative = -1.7479152e-07
ExecutionTime = 458.46 s  ClockTime = 461 s

Time = 542

smoothSolver:  Solving for Ux, Initial residual = 7.9748567e-08, Final residual = 2.3650911e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6070979e-08, Final residual = 2.5019536e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00015224445, Final residual = 1.1570081e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9535819e-05, Final residual = 1.5045926e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.1511111e-06, Final residual = 5.6938694e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.849731e-06, Final residual = 3.3994973e-08, No Iterations 3
time step continuity errors : sum local = 5.2669487e-10, global = 2.1924009e-13, cumulative = -1.747913e-07
ExecutionTime = 459.34 s  ClockTime = 462 s

Time = 543

smoothSolver:  Solving for Ux, Initial residual = 7.9607875e-08, Final residual = 2.3600157e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6008344e-08, Final residual = 2.4971421e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00015159444, Final residual = 1.1535515e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9378939e-05, Final residual = 1.5319094e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.0922288e-06, Final residual = 6.0124786e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.860411e-06, Final residual = 3.2102074e-08, No Iterations 4
time step continuity errors : sum local = 4.975302e-10, global = 2.595851e-13, cumulative = -1.7479104e-07
ExecutionTime = 460.15 s  ClockTime = 462 s

Time = 544

smoothSolver:  Solving for Ux, Initial residual = 7.9331615e-08, Final residual = 2.3534697e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.6002866e-08, Final residual = 2.4907891e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00015101484, Final residual = 1.161113e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9351523e-05, Final residual = 1.5812901e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.0314769e-06, Final residual = 6.2426231e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.895407e-06, Final residual = 2.8057936e-08, No Iterations 4
time step continuity errors : sum local = 4.3523162e-10, global = 3.2424152e-13, cumulative = -1.7479071e-07
ExecutionTime = 461.24 s  ClockTime = 464 s

Time = 545

smoothSolver:  Solving for Ux, Initial residual = 7.9152156e-08, Final residual = 2.3483281e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5939248e-08, Final residual = 2.4859492e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00015037447, Final residual = 1.1565314e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9312635e-05, Final residual = 1.661881e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.9879407e-06, Final residual = 6.4078954e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.9127057e-06, Final residual = 3.076169e-08, No Iterations 4
time step continuity errors : sum local = 4.767956e-10, global = 3.8707755e-13, cumulative = -1.7479033e-07
ExecutionTime = 462 s  ClockTime = 464 s

Time = 546

smoothSolver:  Solving for Ux, Initial residual = 7.8979168e-08, Final residual = 2.3417401e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5942275e-08, Final residual = 2.4796174e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014988444, Final residual = 1.1607067e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9415957e-05, Final residual = 1.7405845e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.9831315e-06, Final residual = 6.5154362e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.9839028e-06, Final residual = 1.8483153e-08, No Iterations 3
time step continuity errors : sum local = 2.8711975e-10, global = -3.7162824e-14, cumulative = -1.7479036e-07
ExecutionTime = 462.94 s  ClockTime = 465 s

Time = 547

smoothSolver:  Solving for Ux, Initial residual = 7.877365e-08, Final residual = 2.3366349e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5862672e-08, Final residual = 2.4749448e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014948588, Final residual = 1.1530085e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9544757e-05, Final residual = 1.8328974e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.9639169e-06, Final residual = 5.0589497e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.8176879e-06, Final residual = 2.7862643e-08, No Iterations 4
time step continuity errors : sum local = 4.320415e-10, global = 3.701171e-13, cumulative = -1.7478999e-07
ExecutionTime = 463.75 s  ClockTime = 466 s

Time = 548

smoothSolver:  Solving for Ux, Initial residual = 7.8660411e-08, Final residual = 2.3300105e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5863162e-08, Final residual = 2.4679778e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014920612, Final residual = 1.1622351e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9730811e-05, Final residual = 1.8916217e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.0712714e-06, Final residual = 3.1664899e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.1632201e-06, Final residual = 2.972514e-08, No Iterations 3
time step continuity errors : sum local = 4.6070269e-10, global = 3.815741e-13, cumulative = -1.7478961e-07
ExecutionTime = 464.51 s  ClockTime = 467 s

Time = 549

smoothSolver:  Solving for Ux, Initial residual = 7.8790177e-08, Final residual = 2.3250009e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5831693e-08, Final residual = 2.4631962e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014884445, Final residual = 1.1553628e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9770799e-05, Final residual = 1.9487848e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.1757668e-06, Final residual = 6.7597513e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.2642575e-06, Final residual = 4.1096744e-08, No Iterations 3
time step continuity errors : sum local = 6.3642342e-10, global = 3.8709663e-13, cumulative = -1.7478922e-07
ExecutionTime = 465.22 s  ClockTime = 468 s

Time = 550

smoothSolver:  Solving for Ux, Initial residual = 7.8619029e-08, Final residual = 2.3187365e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5832492e-08, Final residual = 2.4570939e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014854832, Final residual = 1.1530421e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9840532e-05, Final residual = 1.9342462e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.3149185e-06, Final residual = 1.8521735e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.0743731e-06, Final residual = 3.3791091e-08, No Iterations 4
time step continuity errors : sum local = 5.2368119e-10, global = -4.0582048e-14, cumulative = -1.7478927e-07
ExecutionTime = 467.35 s  ClockTime = 470 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122679

Time = 551

smoothSolver:  Solving for Ux, Initial residual = 7.8532192e-08, Final residual = 2.3146278e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5774278e-08, Final residual = 2.4526012e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014822666, Final residual = 1.1492171e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9806768e-05, Final residual = 1.915747e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.3833136e-06, Final residual = 3.7299253e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.1574745e-06, Final residual = 2.066392e-08, No Iterations 4
time step continuity errors : sum local = 3.2093294e-10, global = 3.1395161e-13, cumulative = -1.7478895e-07
ExecutionTime = 469.97 s  ClockTime = 473 s

Time = 552

smoothSolver:  Solving for Ux, Initial residual = 7.8440129e-08, Final residual = 2.3092744e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5793781e-08, Final residual = 2.4464566e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014801478, Final residual = 1.1560314e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9767562e-05, Final residual = 1.8330553e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.366243e-06, Final residual = 7.0847261e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.2697317e-06, Final residual = 3.1980008e-08, No Iterations 3
time step continuity errors : sum local = 4.957322e-10, global = 2.8475997e-13, cumulative = -1.7478867e-07
ExecutionTime = 472.2 s  ClockTime = 475 s

Time = 553

smoothSolver:  Solving for Ux, Initial residual = 7.8187366e-08, Final residual = 2.3053602e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.570586e-08, Final residual = 2.4418428e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014774211, Final residual = 1.1576263e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9622825e-05, Final residual = 1.7657193e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.3054407e-06, Final residual = 6.9972731e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.2217551e-06, Final residual = 3.1311205e-08, No Iterations 3
time step continuity errors : sum local = 4.8559938e-10, global = 2.8456957e-13, cumulative = -1.7478838e-07
ExecutionTime = 474.42 s  ClockTime = 477 s

Time = 554

smoothSolver:  Solving for Ux, Initial residual = 7.7851158e-08, Final residual = 2.2997175e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5689369e-08, Final residual = 2.4355247e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014748963, Final residual = 1.1659384e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9578888e-05, Final residual = 1.6818701e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.2713505e-06, Final residual = 3.7948283e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.1466732e-06, Final residual = 3.3148708e-08, No Iterations 3
time step continuity errors : sum local = 5.135961e-10, global = 3.0298031e-13, cumulative = -1.7478808e-07
ExecutionTime = 475.88 s  ClockTime = 479 s

Time = 555

smoothSolver:  Solving for Ux, Initial residual = 7.775759e-08, Final residual = 2.2957623e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5625396e-08, Final residual = 2.4308436e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014706628, Final residual = 1.1702951e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9460087e-05, Final residual = 1.6297974e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.2024923e-06, Final residual = 7.1440924e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 4.2288024e-06, Final residual = 3.7045479e-08, No Iterations 3
time step continuity errors : sum local = 5.7417144e-10, global = 3.4419301e-13, cumulative = -1.7478773e-07
ExecutionTime = 477.38 s  ClockTime = 480 s

Time = 556

smoothSolver:  Solving for Ux, Initial residual = 7.749294e-08, Final residual = 2.2902263e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5620394e-08, Final residual = 2.4244996e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014664253, Final residual = 1.176438e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.929921e-05, Final residual = 1.5710776e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.1513662e-06, Final residual = 3.3124599e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 4.0743591e-06, Final residual = 3.5853829e-08, No Iterations 3
time step continuity errors : sum local = 5.5562471e-10, global = 3.8182861e-13, cumulative = -1.7478735e-07
ExecutionTime = 478.92 s  ClockTime = 482 s

Time = 557

smoothSolver:  Solving for Ux, Initial residual = 7.7500585e-08, Final residual = 2.2860607e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5572652e-08, Final residual = 2.4198824e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014607998, Final residual = 1.1768027e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8960275e-05, Final residual = 1.5927572e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.0564602e-06, Final residual = 3.7033215e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.9657368e-06, Final residual = 2.5120132e-08, No Iterations 3
time step continuity errors : sum local = 3.8968021e-10, global = 4.1363468e-13, cumulative = -1.7478694e-07
ExecutionTime = 480.55 s  ClockTime = 484 s

Time = 558

smoothSolver:  Solving for Ux, Initial residual = 7.733297e-08, Final residual = 2.280159e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5586562e-08, Final residual = 2.4135055e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014556922, Final residual = 1.1834753e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8832006e-05, Final residual = 1.5879712e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.8930103e-06, Final residual = 1.4094882e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.8459042e-06, Final residual = 2.5948947e-08, No Iterations 4
time step continuity errors : sum local = 4.0242413e-10, global = 5.3088557e-14, cumulative = -1.7478689e-07
ExecutionTime = 481.5 s  ClockTime = 485 s

Time = 559

smoothSolver:  Solving for Ux, Initial residual = 7.7300391e-08, Final residual = 2.2760166e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5526014e-08, Final residual = 2.4086101e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014501908, Final residual = 1.184397e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8824322e-05, Final residual = 1.6172027e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.830879e-06, Final residual = 6.0463302e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.867139e-06, Final residual = 3.1080509e-08, No Iterations 4
time step continuity errors : sum local = 4.8177999e-10, global = 3.5301246e-13, cumulative = -1.7478653e-07
ExecutionTime = 482.42 s  ClockTime = 486 s

Time = 560

smoothSolver:  Solving for Ux, Initial residual = 7.6974649e-08, Final residual = 2.2701372e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5511745e-08, Final residual = 2.4019136e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014454236, Final residual = 1.1884671e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.892319e-05, Final residual = 1.6536664e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.8330113e-06, Final residual = 5.570031e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.8606508e-06, Final residual = 3.3539525e-08, No Iterations 3
time step continuity errors : sum local = 5.1998251e-10, global = 3.4337485e-13, cumulative = -1.7478619e-07
ExecutionTime = 483.94 s  ClockTime = 487 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122679

Time = 561

smoothSolver:  Solving for Ux, Initial residual = 7.6656302e-08, Final residual = 2.266023e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.541042e-08, Final residual = 2.3970031e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014406965, Final residual = 1.1680498e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.900372e-05, Final residual = 1.6874118e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.8703464e-06, Final residual = 6.8673548e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.8086497e-06, Final residual = 9.4208763e-09, No Iterations 4
time step continuity errors : sum local = 1.4680746e-10, global = -6.2192193e-14, cumulative = -1.7478625e-07
ExecutionTime = 485.24 s  ClockTime = 489 s

Time = 562

smoothSolver:  Solving for Ux, Initial residual = 7.6325066e-08, Final residual = 2.2602002e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5403948e-08, Final residual = 2.3905551e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014373887, Final residual = 1.1482283e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9162664e-05, Final residual = 1.6751483e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.9421382e-06, Final residual = 4.8481571e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.9908918e-06, Final residual = 1.9198506e-08, No Iterations 3
time step continuity errors : sum local = 2.9832647e-10, global = -1.1342157e-13, cumulative = -1.7478637e-07
ExecutionTime = 486.35 s  ClockTime = 490 s

Time = 563

smoothSolver:  Solving for Ux, Initial residual = 7.6153517e-08, Final residual = 2.2560264e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5328741e-08, Final residual = 2.386062e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014340383, Final residual = 1.1175629e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9184698e-05, Final residual = 1.6728984e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.0111739e-06, Final residual = 5.0571846e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.9901168e-06, Final residual = 2.6730354e-08, No Iterations 3
time step continuity errors : sum local = 4.1469798e-10, global = 8.9910601e-14, cumulative = -1.7478628e-07
ExecutionTime = 487.53 s  ClockTime = 491 s

Time = 564

smoothSolver:  Solving for Ux, Initial residual = 7.592749e-08, Final residual = 2.2503221e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5331508e-08, Final residual = 2.3800763e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014315178, Final residual = 1.1028853e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9183191e-05, Final residual = 1.6146586e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.0467722e-06, Final residual = 4.9942227e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.9582792e-06, Final residual = 2.4581397e-08, No Iterations 3
time step continuity errors : sum local = 3.8157703e-10, global = 3.21803e-14, cumulative = -1.7478624e-07
ExecutionTime = 488.46 s  ClockTime = 492 s

Time = 565

smoothSolver:  Solving for Ux, Initial residual = 7.5895308e-08, Final residual = 2.2463438e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5266816e-08, Final residual = 2.3760089e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014281559, Final residual = 1.0919541e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9079241e-05, Final residual = 1.5694225e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 7.0210344e-06, Final residual = 7.0124935e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.7371662e-06, Final residual = 3.0832809e-08, No Iterations 3
time step continuity errors : sum local = 4.779597e-10, global = -1.5429406e-14, cumulative = -1.7478626e-07
ExecutionTime = 489.23 s  ClockTime = 493 s

Time = 566

smoothSolver:  Solving for Ux, Initial residual = 7.5705529e-08, Final residual = 2.2403521e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5278e-08, Final residual = 2.3703769e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014252645, Final residual = 1.0899951e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.9022643e-05, Final residual = 1.5240867e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.9955402e-06, Final residual = 5.2804255e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.9137712e-06, Final residual = 2.6800526e-08, No Iterations 4
time step continuity errors : sum local = 4.153323e-10, global = -3.5161534e-15, cumulative = -1.7478626e-07
ExecutionTime = 490.16 s  ClockTime = 494 s

Time = 567

smoothSolver:  Solving for Ux, Initial residual = 7.5560692e-08, Final residual = 2.236237e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5201363e-08, Final residual = 2.3664501e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001422455, Final residual = 1.0848061e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8877845e-05, Final residual = 1.4882121e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.9444153e-06, Final residual = 5.324716e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.8718613e-06, Final residual = 2.6657791e-08, No Iterations 4
time step continuity errors : sum local = 4.1354161e-10, global = -8.0650026e-15, cumulative = -1.7478627e-07
ExecutionTime = 491.13 s  ClockTime = 495 s

Time = 568

smoothSolver:  Solving for Ux, Initial residual = 7.5276109e-08, Final residual = 2.2302739e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5201687e-08, Final residual = 2.3607349e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014199464, Final residual = 1.0859547e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8794274e-05, Final residual = 1.4340857e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.9136093e-06, Final residual = 6.845767e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4940034e-06, Final residual = 2.6606581e-08, No Iterations 8
time step continuity errors : sum local = 4.1268579e-10, global = 1.2639225e-14, cumulative = -1.7478626e-07
ExecutionTime = 492 s  ClockTime = 496 s

Time = 569

smoothSolver:  Solving for Ux, Initial residual = 7.5037772e-08, Final residual = 2.2264451e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5111599e-08, Final residual = 2.3565854e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014164089, Final residual = 1.0790292e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8614138e-05, Final residual = 1.4157525e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.8615979e-06, Final residual = 6.6764212e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4581249e-06, Final residual = 2.9778734e-08, No Iterations 6
time step continuity errors : sum local = 4.6163157e-10, global = 3.4898107e-14, cumulative = -1.7478622e-07
ExecutionTime = 493.02 s  ClockTime = 497 s

Time = 570

smoothSolver:  Solving for Ux, Initial residual = 7.4882009e-08, Final residual = 2.220801e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5124529e-08, Final residual = 2.3506473e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014128464, Final residual = 1.0830334e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8484335e-05, Final residual = 1.3942798e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.8360183e-06, Final residual = 6.6041357e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4602361e-06, Final residual = 1.9685753e-08, No Iterations 6
time step continuity errors : sum local = 3.0568727e-10, global = 7.5763933e-14, cumulative = -1.7478615e-07
ExecutionTime = 494.23 s  ClockTime = 498 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122679

Time = 571

smoothSolver:  Solving for Ux, Initial residual = 7.4813898e-08, Final residual = 2.2169973e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5050452e-08, Final residual = 2.3463707e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001408326, Final residual = 1.0803068e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8269777e-05, Final residual = 1.388338e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.7499811e-06, Final residual = 5.2750544e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.5790696e-06, Final residual = 2.5512281e-08, No Iterations 3
time step continuity errors : sum local = 3.9569563e-10, global = 9.1041495e-14, cumulative = -1.7478606e-07
ExecutionTime = 495.04 s  ClockTime = 499 s

Time = 572

smoothSolver:  Solving for Ux, Initial residual = 7.4537176e-08, Final residual = 2.2110257e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.5052951e-08, Final residual = 2.3404522e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00014038901, Final residual = 1.0863865e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8121878e-05, Final residual = 1.377459e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.6695504e-06, Final residual = 4.7595139e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.5701525e-06, Final residual = 2.296691e-08, No Iterations 3
time step continuity errors : sum local = 3.5619344e-10, global = 1.3559992e-13, cumulative = -1.7478592e-07
ExecutionTime = 495.83 s  ClockTime = 499 s

Time = 573

smoothSolver:  Solving for Ux, Initial residual = 7.4444058e-08, Final residual = 2.2069658e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4978261e-08, Final residual = 2.336264e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013987788, Final residual = 1.0836693e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7928422e-05, Final residual = 1.3931168e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.6110497e-06, Final residual = 4.7797837e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.555972e-06, Final residual = 2.1737737e-08, No Iterations 3
time step continuity errors : sum local = 3.3755631e-10, global = 1.8264827e-13, cumulative = -1.7478574e-07
ExecutionTime = 496.69 s  ClockTime = 500 s

Time = 574

smoothSolver:  Solving for Ux, Initial residual = 7.4274413e-08, Final residual = 2.2008044e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4996629e-08, Final residual = 2.3304174e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013937999, Final residual = 1.0908249e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7837792e-05, Final residual = 1.4046363e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.5470681e-06, Final residual = 4.9525405e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.5773515e-06, Final residual = 3.297313e-08, No Iterations 3
time step continuity errors : sum local = 5.1137341e-10, global = 2.3900384e-13, cumulative = -1.747855e-07
ExecutionTime = 497.82 s  ClockTime = 501 s

Time = 575

smoothSolver:  Solving for Ux, Initial residual = 7.422305e-08, Final residual = 2.1966333e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.493205e-08, Final residual = 2.3262337e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013885072, Final residual = 1.0875743e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7782045e-05, Final residual = 1.4682738e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.5088828e-06, Final residual = 5.6147096e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.6032654e-06, Final residual = 2.4300926e-08, No Iterations 4
time step continuity errors : sum local = 3.7700888e-10, global = 2.9173686e-13, cumulative = -1.7478521e-07
ExecutionTime = 498.84 s  ClockTime = 502 s

Time = 576

smoothSolver:  Solving for Ux, Initial residual = 7.3936843e-08, Final residual = 2.1903256e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4943122e-08, Final residual = 2.3204114e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001383688, Final residual = 1.0962758e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7825859e-05, Final residual = 1.4951098e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.4731108e-06, Final residual = 6.2231619e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.6679883e-06, Final residual = 3.5805112e-08, No Iterations 4
time step continuity errors : sum local = 5.5450313e-10, global = 3.5386762e-13, cumulative = -1.7478485e-07
ExecutionTime = 499.66 s  ClockTime = 503 s

Time = 577

smoothSolver:  Solving for Ux, Initial residual = 7.369248e-08, Final residual = 2.1859283e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4846038e-08, Final residual = 2.3158757e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001379429, Final residual = 1.0849655e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7909499e-05, Final residual = 1.5835674e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.5018461e-06, Final residual = 6.2415641e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.6546211e-06, Final residual = 2.0661834e-08, No Iterations 4
time step continuity errors : sum local = 3.2087314e-10, global = 4.2422761e-13, cumulative = -1.7478443e-07
ExecutionTime = 500.89 s  ClockTime = 505 s

Time = 578

smoothSolver:  Solving for Ux, Initial residual = 7.3642655e-08, Final residual = 2.1794605e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4881997e-08, Final residual = 2.3098044e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013765494, Final residual = 1.0827431e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8027339e-05, Final residual = 1.6112946e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.5519938e-06, Final residual = 6.3220356e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.6289336e-06, Final residual = 2.564066e-08, No Iterations 4
time step continuity errors : sum local = 3.9775763e-10, global = 4.8047583e-13, cumulative = -1.7478395e-07
ExecutionTime = 501.87 s  ClockTime = 506 s

Time = 579

smoothSolver:  Solving for Ux, Initial residual = 7.3598812e-08, Final residual = 2.1753609e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4812496e-08, Final residual = 2.3057831e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013730963, Final residual = 1.0598786e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8047061e-05, Final residual = 1.6293347e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.6369788e-06, Final residual = 6.2051796e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.6244736e-06, Final residual = 2.0058623e-08, No Iterations 3
time step continuity errors : sum local = 3.1134069e-10, global = 3.7776811e-16, cumulative = -1.7478395e-07
ExecutionTime = 502.79 s  ClockTime = 506 s

Time = 580

smoothSolver:  Solving for Ux, Initial residual = 7.3301812e-08, Final residual = 2.1693096e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4812819e-08, Final residual = 2.3001374e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013697436, Final residual = 1.0552633e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.8010734e-05, Final residual = 1.5939691e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.6744781e-06, Final residual = 6.3163137e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.6070239e-06, Final residual = 1.9192533e-08, No Iterations 3
time step continuity errors : sum local = 2.9801466e-10, global = 2.3185005e-13, cumulative = -1.7478372e-07
ExecutionTime = 503.68 s  ClockTime = 507 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122679

Time = 581

smoothSolver:  Solving for Ux, Initial residual = 7.3211549e-08, Final residual = 2.165732e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4734795e-08, Final residual = 2.2960665e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013661057, Final residual = 1.0470332e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7982528e-05, Final residual = 1.5989792e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.7361882e-06, Final residual = 3.333602e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.7296756e-06, Final residual = 2.6584386e-08, No Iterations 3
time step continuity errors : sum local = 4.1228663e-10, global = 3.8838383e-13, cumulative = -1.7478333e-07
ExecutionTime = 504.56 s  ClockTime = 508 s

Time = 582

smoothSolver:  Solving for Ux, Initial residual = 7.3105516e-08, Final residual = 2.1602106e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4764307e-08, Final residual = 2.2902612e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013625979, Final residual = 1.0535063e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7918133e-05, Final residual = 1.5541713e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.6924356e-06, Final residual = 3.9461991e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.655122e-06, Final residual = 2.7312749e-08, No Iterations 3
time step continuity errors : sum local = 4.2322982e-10, global = 3.7224137e-13, cumulative = -1.7478296e-07
ExecutionTime = 505.36 s  ClockTime = 509 s

Time = 583

smoothSolver:  Solving for Ux, Initial residual = 7.3162733e-08, Final residual = 2.1571243e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4704489e-08, Final residual = 2.2860931e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013594926, Final residual = 1.0462477e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7898616e-05, Final residual = 1.5407643e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.6908209e-06, Final residual = 6.5411161e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.6327638e-06, Final residual = 3.3059133e-08, No Iterations 3
time step continuity errors : sum local = 5.1243112e-10, global = 3.6549875e-13, cumulative = -1.7478259e-07
ExecutionTime = 506.17 s  ClockTime = 510 s

Time = 584

smoothSolver:  Solving for Ux, Initial residual = 7.2801964e-08, Final residual = 2.1516477e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4702441e-08, Final residual = 2.280369e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013566667, Final residual = 1.0570138e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7838088e-05, Final residual = 1.4762019e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.590104e-06, Final residual = 5.6877264e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.771393e-06, Final residual = 2.6195101e-08, No Iterations 3
time step continuity errors : sum local = 4.0658339e-10, global = 4.0252309e-13, cumulative = -1.7478219e-07
ExecutionTime = 507.24 s  ClockTime = 511 s

Time = 585

smoothSolver:  Solving for Ux, Initial residual = 7.2732255e-08, Final residual = 2.1483493e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4624263e-08, Final residual = 2.2763334e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013531727, Final residual = 1.0469974e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7820746e-05, Final residual = 1.4760481e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.6044364e-06, Final residual = 5.6893274e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.81732e-06, Final residual = 2.5126616e-08, No Iterations 3
time step continuity errors : sum local = 3.8990333e-10, global = 4.2100284e-13, cumulative = -1.7478177e-07
ExecutionTime = 508.03 s  ClockTime = 512 s

Time = 586

smoothSolver:  Solving for Ux, Initial residual = 7.2453957e-08, Final residual = 2.1426411e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4635744e-08, Final residual = 2.2706673e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013497972, Final residual = 1.0571256e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7721853e-05, Final residual = 1.4307874e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.5411107e-06, Final residual = 6.4891509e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.7926098e-06, Final residual = 2.483015e-08, No Iterations 3
time step continuity errors : sum local = 3.8527197e-10, global = 4.6519515e-13, cumulative = -1.747813e-07
ExecutionTime = 508.9 s  ClockTime = 513 s

Time = 587

smoothSolver:  Solving for Ux, Initial residual = 7.2409439e-08, Final residual = 2.139234e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4563654e-08, Final residual = 2.2666814e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013460499, Final residual = 1.0455046e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7682347e-05, Final residual = 1.4393146e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.5819114e-06, Final residual = 6.5657374e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.5882334e-06, Final residual = 2.959818e-08, No Iterations 4
time step continuity errors : sum local = 4.5873976e-10, global = 4.9551462e-13, cumulative = -1.7478081e-07
ExecutionTime = 509.82 s  ClockTime = 514 s

Time = 588

smoothSolver:  Solving for Ux, Initial residual = 7.2214833e-08, Final residual = 2.1334664e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4588093e-08, Final residual = 2.2611111e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001342396, Final residual = 1.052027e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7521544e-05, Final residual = 1.4089716e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.5216272e-06, Final residual = 6.4003402e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.5330089e-06, Final residual = 1.9261524e-08, No Iterations 3
time step continuity errors : sum local = 2.9944945e-10, global = 2.2699365e-13, cumulative = -1.7478058e-07
ExecutionTime = 510.57 s  ClockTime = 514 s

Time = 589

smoothSolver:  Solving for Ux, Initial residual = 7.2046722e-08, Final residual = 2.1301567e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4496906e-08, Final residual = 2.2570954e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013381513, Final residual = 1.0404526e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7408462e-05, Final residual = 1.4710255e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.521351e-06, Final residual = 6.4973264e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.5848873e-06, Final residual = 2.6311076e-08, No Iterations 4
time step continuity errors : sum local = 4.0827437e-10, global = 5.0551511e-13, cumulative = -1.7478007e-07
ExecutionTime = 512.07 s  ClockTime = 516 s

Time = 590

smoothSolver:  Solving for Ux, Initial residual = 7.1796923e-08, Final residual = 2.1246481e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.451367e-08, Final residual = 2.251315e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013338763, Final residual = 1.0454278e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7216819e-05, Final residual = 1.4465682e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.3913256e-06, Final residual = 4.1963097e-08, No Iterations 6
GAMG:  Solving for p, Initial residual = 3.5373344e-06, Final residual = 3.3748299e-08, No Iterations 3
time step continuity errors : sum local = 5.2337812e-10, global = 5.2513486e-13, cumulative = -1.7477955e-07
ExecutionTime = 512.94 s  ClockTime = 517 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122679

Time = 591

smoothSolver:  Solving for Ux, Initial residual = 7.1789931e-08, Final residual = 2.1214755e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4445528e-08, Final residual = 2.2470777e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013292991, Final residual = 1.0349861e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7244335e-05, Final residual = 1.460658e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.3670645e-06, Final residual = 5.9039685e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.598054e-06, Final residual = 2.4625161e-08, No Iterations 4
time step continuity errors : sum local = 3.8201498e-10, global = 5.4495365e-13, cumulative = -1.74779e-07
ExecutionTime = 513.8 s  ClockTime = 518 s

Time = 592

smoothSolver:  Solving for Ux, Initial residual = 7.1520227e-08, Final residual = 2.1158528e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4458186e-08, Final residual = 2.2412325e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013249602, Final residual = 1.0480282e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7195651e-05, Final residual = 1.4251077e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.2642371e-06, Final residual = 5.4391839e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.5431599e-06, Final residual = 1.7678463e-08, No Iterations 3
time step continuity errors : sum local = 2.7468083e-10, global = 1.8897481e-13, cumulative = -1.7477881e-07
ExecutionTime = 514.48 s  ClockTime = 518 s

Time = 593

smoothSolver:  Solving for Ux, Initial residual = 7.1350318e-08, Final residual = 2.1126852e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4363966e-08, Final residual = 2.2369342e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001320896, Final residual = 1.0331088e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7279613e-05, Final residual = 1.4820522e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.3244685e-06, Final residual = 5.7333921e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.5562177e-06, Final residual = 3.1083985e-08, No Iterations 4
time step continuity errors : sum local = 4.8204799e-10, global = 4.8326214e-13, cumulative = -1.7477833e-07
ExecutionTime = 515.17 s  ClockTime = 519 s

Time = 594

smoothSolver:  Solving for Ux, Initial residual = 7.1078046e-08, Final residual = 2.1070343e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4375472e-08, Final residual = 2.2312218e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013179873, Final residual = 1.0374239e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7270754e-05, Final residual = 1.4803185e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.2603188e-06, Final residual = 5.9979447e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.4598005e-06, Final residual = 3.4200843e-08, No Iterations 4
time step continuity errors : sum local = 5.3003888e-10, global = 4.7209322e-13, cumulative = -1.7477786e-07
ExecutionTime = 515.95 s  ClockTime = 520 s

Time = 595

smoothSolver:  Solving for Ux, Initial residual = 7.0957259e-08, Final residual = 2.1040748e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4286541e-08, Final residual = 2.2271646e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013148245, Final residual = 1.0180738e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7413819e-05, Final residual = 1.5336283e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.3799267e-06, Final residual = 4.7297602e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.6884206e-06, Final residual = 2.1820566e-08, No Iterations 4
time step continuity errors : sum local = 3.3852813e-10, global = 4.9438461e-13, cumulative = -1.7477736e-07
ExecutionTime = 517.26 s  ClockTime = 521 s

Time = 596

smoothSolver:  Solving for Ux, Initial residual = 7.0728269e-08, Final residual = 2.0985028e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4308456e-08, Final residual = 2.2218191e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013125072, Final residual = 1.0174292e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7399558e-05, Final residual = 1.4949698e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.3516998e-06, Final residual = 4.4714209e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.583367e-06, Final residual = 2.253266e-08, No Iterations 4
time step continuity errors : sum local = 3.4961966e-10, global = 5.09338e-13, cumulative = -1.7477686e-07
ExecutionTime = 518.87 s  ClockTime = 523 s

Time = 597

smoothSolver:  Solving for Ux, Initial residual = 7.0621747e-08, Final residual = 2.0954159e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4225414e-08, Final residual = 2.2181129e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013098917, Final residual = 1.0064852e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7512634e-05, Final residual = 1.5147641e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.4802956e-06, Final residual = 4.341735e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.6533455e-06, Final residual = 2.2810598e-08, No Iterations 3
time step continuity errors : sum local = 3.5396651e-10, global = 5.1875991e-13, cumulative = -1.7477634e-07
ExecutionTime = 519.85 s  ClockTime = 524 s

Time = 598

smoothSolver:  Solving for Ux, Initial residual = 7.0361418e-08, Final residual = 2.0896497e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4248486e-08, Final residual = 2.2129434e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013072325, Final residual = 1.0078562e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7390591e-05, Final residual = 1.4367232e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.4082935e-06, Final residual = 4.2083058e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.5422424e-06, Final residual = 1.9104562e-08, No Iterations 3
time step continuity errors : sum local = 2.967407e-10, global = 2.6067791e-13, cumulative = -1.7477608e-07
ExecutionTime = 520.71 s  ClockTime = 525 s

Time = 599

smoothSolver:  Solving for Ux, Initial residual = 7.0312914e-08, Final residual = 2.0865258e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4167091e-08, Final residual = 2.2093445e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001304558, Final residual = 9.9888573e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7410084e-05, Final residual = 1.4509624e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.4960903e-06, Final residual = 4.3885695e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.6367968e-06, Final residual = 2.3305338e-08, No Iterations 3
time step continuity errors : sum local = 3.6167498e-10, global = 4.8862911e-13, cumulative = -1.7477559e-07
ExecutionTime = 521.99 s  ClockTime = 526 s

Time = 600

smoothSolver:  Solving for Ux, Initial residual = 7.0143616e-08, Final residual = 2.08076e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4194489e-08, Final residual = 2.2041974e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00013023867, Final residual = 1.0010801e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7206145e-05, Final residual = 1.3592963e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.3830017e-06, Final residual = 4.3602568e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.5143473e-06, Final residual = 3.3489358e-08, No Iterations 3
time step continuity errors : sum local = 5.1909053e-10, global = 5.0226825e-13, cumulative = -1.7477508e-07
ExecutionTime = 523.57 s  ClockTime = 528 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122679

Time = 601

smoothSolver:  Solving for Ux, Initial residual = 7.0119119e-08, Final residual = 2.0778418e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4113854e-08, Final residual = 2.2004714e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012998395, Final residual = 9.9232733e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.7161779e-05, Final residual = 1.368251e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.4101478e-06, Final residual = 6.2588697e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.4400447e-06, Final residual = 2.9170679e-08, No Iterations 3
time step continuity errors : sum local = 4.5221861e-10, global = 4.9689118e-13, cumulative = -1.7477459e-07
ExecutionTime = 524.47 s  ClockTime = 529 s

Time = 602

smoothSolver:  Solving for Ux, Initial residual = 6.9964296e-08, Final residual = 2.0722764e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4143137e-08, Final residual = 2.1952068e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012968318, Final residual = 9.9754208e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6891626e-05, Final residual = 1.286686e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.2525345e-06, Final residual = 5.4257895e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.3381961e-06, Final residual = 1.6144455e-08, No Iterations 3
time step continuity errors : sum local = 2.5106427e-10, global = 4.90053e-14, cumulative = -1.7477454e-07
ExecutionTime = 525.37 s  ClockTime = 529 s

Time = 603

smoothSolver:  Solving for Ux, Initial residual = 6.9972398e-08, Final residual = 2.0692989e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4070529e-08, Final residual = 2.1914732e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012932809, Final residual = 9.892435e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6844093e-05, Final residual = 1.3305594e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.3235509e-06, Final residual = 5.7085175e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.4605783e-06, Final residual = 2.3906277e-08, No Iterations 4
time step continuity errors : sum local = 3.7094059e-10, global = 4.1118652e-13, cumulative = -1.7477413e-07
ExecutionTime = 526.06 s  ClockTime = 530 s

Time = 604

smoothSolver:  Solving for Ux, Initial residual = 6.9673397e-08, Final residual = 2.0634812e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4087942e-08, Final residual = 2.1862299e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012891895, Final residual = 9.9785038e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6592862e-05, Final residual = 1.2569567e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.1860518e-06, Final residual = 3.8234287e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.2749626e-06, Final residual = 1.4541135e-08, No Iterations 3
time step continuity errors : sum local = 2.2614829e-10, global = 5.1827682e-14, cumulative = -1.7477408e-07
ExecutionTime = 526.88 s  ClockTime = 531 s

Time = 605

smoothSolver:  Solving for Ux, Initial residual = 6.9557051e-08, Final residual = 2.0603447e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4004613e-08, Final residual = 2.1824601e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012846733, Final residual = 9.9031181e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6580497e-05, Final residual = 1.3374103e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.2553747e-06, Final residual = 6.097623e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.4781016e-06, Final residual = 2.6544473e-08, No Iterations 4
time step continuity errors : sum local = 4.1179124e-10, global = 2.7723351e-13, cumulative = -1.747738e-07
ExecutionTime = 527.71 s  ClockTime = 532 s

Time = 606

smoothSolver:  Solving for Ux, Initial residual = 6.9278054e-08, Final residual = 2.0543461e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.4028348e-08, Final residual = 2.1771727e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012797319, Final residual = 1.0037191e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6391851e-05, Final residual = 1.3094813e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.1064914e-06, Final residual = 3.1927584e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.2964675e-06, Final residual = 2.1585981e-08, No Iterations 4
time step continuity errors : sum local = 3.3483359e-10, global = 2.4683134e-13, cumulative = -1.7477355e-07
ExecutionTime = 528.73 s  ClockTime = 533 s

Time = 607

smoothSolver:  Solving for Ux, Initial residual = 6.9376845e-08, Final residual = 2.0510916e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3959811e-08, Final residual = 2.1730584e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012751446, Final residual = 9.9551539e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6520445e-05, Final residual = 1.4113997e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.1747749e-06, Final residual = 5.3351253e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.4527083e-06, Final residual = 2.7383505e-08, No Iterations 3
time step continuity errors : sum local = 4.2466867e-10, global = 2.1949443e-13, cumulative = -1.7477333e-07
ExecutionTime = 530.21 s  ClockTime = 534 s

Time = 608

smoothSolver:  Solving for Ux, Initial residual = 6.8990124e-08, Final residual = 2.0447923e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3966976e-08, Final residual = 2.1671726e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012704352, Final residual = 1.0065081e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6367956e-05, Final residual = 1.3820877e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.0896745e-06, Final residual = 5.2037173e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.3337507e-06, Final residual = 2.0343299e-08, No Iterations 4
time step continuity errors : sum local = 3.1602779e-10, global = 2.3536011e-13, cumulative = -1.747731e-07
ExecutionTime = 531.2 s  ClockTime = 535 s

Time = 609

smoothSolver:  Solving for Ux, Initial residual = 6.8944126e-08, Final residual = 2.0414806e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3882758e-08, Final residual = 2.1633801e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012668187, Final residual = 9.7801587e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6486745e-05, Final residual = 1.4238809e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.1681748e-06, Final residual = 5.5983735e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.3965437e-06, Final residual = 2.6221982e-08, No Iterations 3
time step continuity errors : sum local = 4.0661313e-10, global = 2.3052583e-13, cumulative = -1.7477287e-07
ExecutionTime = 532.02 s  ClockTime = 536 s

Time = 610

smoothSolver:  Solving for Ux, Initial residual = 6.8655956e-08, Final residual = 2.035421e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3903622e-08, Final residual = 2.1581374e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012633233, Final residual = 9.7333748e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6288786e-05, Final residual = 1.3267343e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.0443617e-06, Final residual = 5.1703356e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2592631e-06, Final residual = 1.6137711e-08, No Iterations 3
time step continuity errors : sum local = 2.5120662e-10, global = -1.4139656e-13, cumulative = -1.7477301e-07
ExecutionTime = 532.94 s  ClockTime = 537 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122679

Time = 611

smoothSolver:  Solving for Ux, Initial residual = 6.8604572e-08, Final residual = 2.032546e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3819867e-08, Final residual = 2.1543547e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012600154, Final residual = 9.4817817e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6367073e-05, Final residual = 1.408094e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.1454168e-06, Final residual = 5.7825676e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.403213e-06, Final residual = 3.2986981e-08, No Iterations 3
time step continuity errors : sum local = 5.1144325e-10, global = 1.5835798e-13, cumulative = -1.7477285e-07
ExecutionTime = 534.02 s  ClockTime = 538 s

Time = 612

smoothSolver:  Solving for Ux, Initial residual = 6.8333743e-08, Final residual = 2.026916e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3840373e-08, Final residual = 2.1490189e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012563222, Final residual = 9.559109e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6148998e-05, Final residual = 1.3166925e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.0147909e-06, Final residual = 3.2924268e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.231926e-06, Final residual = 2.2816666e-08, No Iterations 4
time step continuity errors : sum local = 3.5406932e-10, global = 1.5856539e-13, cumulative = -1.7477269e-07
ExecutionTime = 535.26 s  ClockTime = 539 s

Time = 613

smoothSolver:  Solving for Ux, Initial residual = 6.8387421e-08, Final residual = 2.0243669e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3764552e-08, Final residual = 2.1450855e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012526946, Final residual = 9.3446317e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.621538e-05, Final residual = 1.3415256e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 6.0814168e-06, Final residual = 5.9999092e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.4000705e-06, Final residual = 2.6036646e-08, No Iterations 4
time step continuity errors : sum local = 4.04362e-10, global = 1.4628318e-13, cumulative = -1.7477254e-07
ExecutionTime = 536.32 s  ClockTime = 540 s

Time = 614

smoothSolver:  Solving for Ux, Initial residual = 6.8191085e-08, Final residual = 2.0187841e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3797e-08, Final residual = 2.1397617e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012484807, Final residual = 9.4508159e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5985336e-05, Final residual = 1.2291155e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.902527e-06, Final residual = 3.2958614e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.1617708e-06, Final residual = 2.2814475e-08, No Iterations 4
time step continuity errors : sum local = 3.5377981e-10, global = 1.7304531e-13, cumulative = -1.7477237e-07
ExecutionTime = 537.18 s  ClockTime = 541 s

Time = 615

smoothSolver:  Solving for Ux, Initial residual = 6.8236357e-08, Final residual = 2.016176e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3723638e-08, Final residual = 2.1359451e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012446229, Final residual = 9.2173255e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6066345e-05, Final residual = 1.2609976e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.9689976e-06, Final residual = 5.4307753e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.3012935e-06, Final residual = 3.2216358e-08, No Iterations 3
time step continuity errors : sum local = 4.9953495e-10, global = 1.8223491e-13, cumulative = -1.7477219e-07
ExecutionTime = 537.84 s  ClockTime = 542 s

Time = 616

smoothSolver:  Solving for Ux, Initial residual = 6.7927054e-08, Final residual = 2.0103948e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3744122e-08, Final residual = 2.1308131e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012407609, Final residual = 9.3561839e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5856471e-05, Final residual = 1.1787216e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.8176262e-06, Final residual = 5.3369311e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.184786e-06, Final residual = 3.040432e-08, No Iterations 4
time step continuity errors : sum local = 4.7103927e-10, global = 2.1982238e-13, cumulative = -1.7477197e-07
ExecutionTime = 538.49 s  ClockTime = 543 s

Time = 617

smoothSolver:  Solving for Ux, Initial residual = 6.7948557e-08, Final residual = 2.0076491e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3667319e-08, Final residual = 2.1272142e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001237457, Final residual = 9.1283964e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5936745e-05, Final residual = 1.2635914e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.9134738e-06, Final residual = 5.2149199e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2679387e-06, Final residual = 2.3820731e-08, No Iterations 3
time step continuity errors : sum local = 3.6938947e-10, global = 2.4236449e-13, cumulative = -1.7477173e-07
ExecutionTime = 539.55 s  ClockTime = 544 s

Time = 618

smoothSolver:  Solving for Ux, Initial residual = 6.7614696e-08, Final residual = 2.0018017e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3686674e-08, Final residual = 2.1222002e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012338575, Final residual = 9.3000685e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5730038e-05, Final residual = 1.2121042e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.7837446e-06, Final residual = 4.9985924e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.1657714e-06, Final residual = 2.6772517e-08, No Iterations 4
time step continuity errors : sum local = 4.1514902e-10, global = 2.9145117e-13, cumulative = -1.7477144e-07
ExecutionTime = 540.42 s  ClockTime = 545 s

Time = 619

smoothSolver:  Solving for Ux, Initial residual = 6.7657177e-08, Final residual = 1.9991292e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3610973e-08, Final residual = 2.118575e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012306884, Final residual = 9.0991659e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5829928e-05, Final residual = 1.3047224e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.8979583e-06, Final residual = 5.1211251e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2711564e-06, Final residual = 2.1645505e-08, No Iterations 3
time step continuity errors : sum local = 3.3611886e-10, global = 3.2433915e-13, cumulative = -1.7477111e-07
ExecutionTime = 541.61 s  ClockTime = 546 s

Time = 620

smoothSolver:  Solving for Ux, Initial residual = 6.731808e-08, Final residual = 1.9933977e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3630537e-08, Final residual = 2.1135292e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012272583, Final residual = 9.2707076e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5655332e-05, Final residual = 1.262444e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.7858538e-06, Final residual = 1.7313163e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.0402234e-06, Final residual = 2.6420783e-08, No Iterations 6
time step continuity errors : sum local = 4.0957538e-10, global = -2.5065107e-14, cumulative = -1.7477114e-07
ExecutionTime = 542.44 s  ClockTime = 547 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122679

Time = 621

smoothSolver:  Solving for Ux, Initial residual = 6.7280968e-08, Final residual = 1.9910049e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3542486e-08, Final residual = 2.1098227e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012242622, Final residual = 9.0665501e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5767303e-05, Final residual = 1.3137898e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.8904729e-06, Final residual = 5.0873596e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2624022e-06, Final residual = 2.4339769e-08, No Iterations 3
time step continuity errors : sum local = 3.7780366e-10, global = 2.632756e-13, cumulative = -1.7477087e-07
ExecutionTime = 543.2 s  ClockTime = 547 s

Time = 622

smoothSolver:  Solving for Ux, Initial residual = 6.6981803e-08, Final residual = 1.9853074e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3567045e-08, Final residual = 2.1048054e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012209383, Final residual = 9.2190613e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5602117e-05, Final residual = 1.2432183e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.770433e-06, Final residual = 5.0518445e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.1544214e-06, Final residual = 2.4744346e-08, No Iterations 4
time step continuity errors : sum local = 3.8366961e-10, global = 2.5752407e-13, cumulative = -1.7477062e-07
ExecutionTime = 544.28 s  ClockTime = 548 s

Time = 623

smoothSolver:  Solving for Ux, Initial residual = 6.7021958e-08, Final residual = 1.9828377e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3487332e-08, Final residual = 2.1011633e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001217969, Final residual = 9.006012e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5704867e-05, Final residual = 1.2906931e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.8743086e-06, Final residual = 4.9453297e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2563143e-06, Final residual = 2.3571787e-08, No Iterations 3
time step continuity errors : sum local = 3.6586353e-10, global = 2.4732092e-13, cumulative = -1.7477037e-07
ExecutionTime = 545.52 s  ClockTime = 550 s

Time = 624

smoothSolver:  Solving for Ux, Initial residual = 6.6721412e-08, Final residual = 1.9770862e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3513448e-08, Final residual = 2.0962146e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012148259, Final residual = 9.1676197e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5541334e-05, Final residual = 1.227152e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.7542514e-06, Final residual = 4.8718941e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.1498922e-06, Final residual = 1.5359393e-08, No Iterations 3
time step continuity errors : sum local = 2.3914449e-10, global = -2.585237e-14, cumulative = -1.7477039e-07
ExecutionTime = 546.7 s  ClockTime = 551 s

Time = 625

smoothSolver:  Solving for Ux, Initial residual = 6.6667628e-08, Final residual = 1.9746479e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3425143e-08, Final residual = 2.0926001e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012119621, Final residual = 8.9431374e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5649004e-05, Final residual = 1.2739182e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.8630604e-06, Final residual = 5.1766391e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.280129e-06, Final residual = 2.392435e-08, No Iterations 4
time step continuity errors : sum local = 3.71524e-10, global = 1.9037807e-13, cumulative = -1.747702e-07
ExecutionTime = 547.62 s  ClockTime = 552 s

Time = 626

smoothSolver:  Solving for Ux, Initial residual = 6.6436197e-08, Final residual = 1.9688732e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3459619e-08, Final residual = 2.0876841e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012087797, Final residual = 9.1040973e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5483995e-05, Final residual = 1.2150666e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.7339254e-06, Final residual = 5.2599422e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.177295e-06, Final residual = 2.9815127e-08, No Iterations 4
time step continuity errors : sum local = 4.624073e-10, global = 1.8744843e-13, cumulative = -1.7477002e-07
ExecutionTime = 548.55 s  ClockTime = 553 s

Time = 627

smoothSolver:  Solving for Ux, Initial residual = 6.6455631e-08, Final residual = 1.9664575e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3376119e-08, Final residual = 2.0840857e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012057985, Final residual = 8.8665081e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5570779e-05, Final residual = 1.2690844e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.8282171e-06, Final residual = 5.0315559e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2734136e-06, Final residual = 3.1148298e-08, No Iterations 3
time step continuity errors : sum local = 4.8291372e-10, global = 1.8418028e-13, cumulative = -1.7476983e-07
ExecutionTime = 549.86 s  ClockTime = 554 s

Time = 628

smoothSolver:  Solving for Ux, Initial residual = 6.6145274e-08, Final residual = 1.9606809e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3403487e-08, Final residual = 2.0792266e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00012026622, Final residual = 9.0389488e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5404104e-05, Final residual = 1.2208498e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.7094159e-06, Final residual = 5.1025515e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.1729503e-06, Final residual = 2.9322922e-08, No Iterations 4
time step continuity errors : sum local = 4.5451011e-10, global = 1.9999756e-13, cumulative = -1.7476963e-07
ExecutionTime = 551.4 s  ClockTime = 556 s

Time = 629

smoothSolver:  Solving for Ux, Initial residual = 6.6194558e-08, Final residual = 1.9583631e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3324764e-08, Final residual = 2.0756533e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011997779, Final residual = 8.7976596e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5473262e-05, Final residual = 1.2772366e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.8013974e-06, Final residual = 4.9268976e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2722205e-06, Final residual = 2.6553299e-08, No Iterations 4
time step continuity errors : sum local = 4.1195102e-10, global = 2.2029278e-13, cumulative = -1.7476941e-07
ExecutionTime = 552.3 s  ClockTime = 556 s

Time = 630

smoothSolver:  Solving for Ux, Initial residual = 6.5964268e-08, Final residual = 1.9526152e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3364247e-08, Final residual = 2.0708191e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011966092, Final residual = 8.980335e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5310548e-05, Final residual = 1.2177744e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.6744915e-06, Final residual = 4.6914402e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.1394104e-06, Final residual = 1.524749e-08, No Iterations 3
time step continuity errors : sum local = 2.3699339e-10, global = -7.2306474e-14, cumulative = -1.7476948e-07
ExecutionTime = 553 s  ClockTime = 557 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122679

Time = 631

smoothSolver:  Solving for Ux, Initial residual = 6.5845905e-08, Final residual = 1.9503528e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3262163e-08, Final residual = 2.0672475e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011936143, Final residual = 8.7392171e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5386781e-05, Final residual = 1.2611568e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.7632183e-06, Final residual = 4.9321454e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2556173e-06, Final residual = 2.9048311e-08, No Iterations 3
time step continuity errors : sum local = 4.506068e-10, global = 1.7975706e-13, cumulative = -1.747693e-07
ExecutionTime = 553.75 s  ClockTime = 558 s

Time = 632

smoothSolver:  Solving for Ux, Initial residual = 6.5543424e-08, Final residual = 1.94458e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3292451e-08, Final residual = 2.0624795e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011903712, Final residual = 8.9337357e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5238407e-05, Final residual = 1.1960007e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.6490335e-06, Final residual = 5.1693322e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.1536598e-06, Final residual = 2.9753209e-08, No Iterations 4
time step continuity errors : sum local = 4.610964e-10, global = 1.8033901e-13, cumulative = -1.7476912e-07
ExecutionTime = 554.53 s  ClockTime = 559 s

Time = 633

smoothSolver:  Solving for Ux, Initial residual = 6.5561132e-08, Final residual = 1.9423627e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3205523e-08, Final residual = 2.058925e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011873287, Final residual = 8.6803204e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5300483e-05, Final residual = 1.2505611e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.7258612e-06, Final residual = 5.0614242e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2513737e-06, Final residual = 2.0944595e-08, No Iterations 4
time step continuity errors : sum local = 3.2512102e-10, global = 1.8785608e-13, cumulative = -1.7476894e-07
ExecutionTime = 555.58 s  ClockTime = 560 s

Time = 634

smoothSolver:  Solving for Ux, Initial residual = 6.5354064e-08, Final residual = 1.936592e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3249878e-08, Final residual = 2.0541641e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011840965, Final residual = 8.8718554e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5161809e-05, Final residual = 1.1904586e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.6118122e-06, Final residual = 4.9732121e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.1383822e-06, Final residual = 2.7418376e-08, No Iterations 4
time step continuity errors : sum local = 4.2483422e-10, global = 2.0597668e-13, cumulative = -1.7476873e-07
ExecutionTime = 556.5 s  ClockTime = 561 s

Time = 635

smoothSolver:  Solving for Ux, Initial residual = 6.5379065e-08, Final residual = 1.9344621e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3165157e-08, Final residual = 2.0505827e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001181278, Final residual = 8.6029926e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5237228e-05, Final residual = 1.2467491e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.689062e-06, Final residual = 4.761459e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2321519e-06, Final residual = 2.4928919e-08, No Iterations 3
time step continuity errors : sum local = 3.8690416e-10, global = 2.2463697e-13, cumulative = -1.7476851e-07
ExecutionTime = 557.34 s  ClockTime = 562 s

Time = 636

smoothSolver:  Solving for Ux, Initial residual = 6.5074753e-08, Final residual = 1.9287109e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3197518e-08, Final residual = 2.0457943e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011782953, Final residual = 8.8030007e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5116375e-05, Final residual = 1.1875857e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.5948827e-06, Final residual = 4.6997262e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.1219402e-06, Final residual = 2.3910855e-08, No Iterations 4
time step continuity errors : sum local = 3.7081621e-10, global = 2.5820515e-13, cumulative = -1.7476825e-07
ExecutionTime = 559.08 s  ClockTime = 563 s

Time = 637

smoothSolver:  Solving for Ux, Initial residual = 6.5125602e-08, Final residual = 1.9266497e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3114313e-08, Final residual = 2.0421985e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011755726, Final residual = 8.5345916e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.518501e-05, Final residual = 1.247041e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.6615476e-06, Final residual = 4.626528e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2040526e-06, Final residual = 2.0869121e-08, No Iterations 3
time step continuity errors : sum local = 3.2381891e-10, global = 2.3159493e-13, cumulative = -1.7476802e-07
ExecutionTime = 560.06 s  ClockTime = 564 s

Time = 638

smoothSolver:  Solving for Ux, Initial residual = 6.4798689e-08, Final residual = 1.9209031e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.314411e-08, Final residual = 2.0374095e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011727136, Final residual = 8.7598153e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5083023e-05, Final residual = 1.1853403e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.5672309e-06, Final residual = 4.4156622e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.0893105e-06, Final residual = 1.8192167e-08, No Iterations 4
time step continuity errors : sum local = 2.8275188e-10, global = 3.1332355e-13, cumulative = -1.747677e-07
ExecutionTime = 560.67 s  ClockTime = 565 s

Time = 639

smoothSolver:  Solving for Ux, Initial residual = 6.4767174e-08, Final residual = 1.9189136e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3049135e-08, Final residual = 2.0337947e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011700205, Final residual = 8.5190698e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5178009e-05, Final residual = 1.244755e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.6471861e-06, Final residual = 4.6935646e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.1967882e-06, Final residual = 2.0990607e-08, No Iterations 3
time step continuity errors : sum local = 3.2570792e-10, global = 3.3165632e-13, cumulative = -1.7476737e-07
ExecutionTime = 561.43 s  ClockTime = 566 s

Time = 640

smoothSolver:  Solving for Ux, Initial residual = 6.4481889e-08, Final residual = 1.9131453e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3087285e-08, Final residual = 2.0290942e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001167223, Final residual = 8.7598195e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5104578e-05, Final residual = 1.175222e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.5861227e-06, Final residual = 4.5113864e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.0942527e-06, Final residual = 1.879765e-08, No Iterations 4
time step continuity errors : sum local = 2.9193178e-10, global = 3.7306128e-13, cumulative = -1.74767e-07
ExecutionTime = 562.19 s  ClockTime = 566 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122679

Time = 641

smoothSolver:  Solving for Ux, Initial residual = 6.4453876e-08, Final residual = 1.911163e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.2991377e-08, Final residual = 2.0255865e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011645759, Final residual = 8.5183932e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5176734e-05, Final residual = 1.2456359e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.6567536e-06, Final residual = 4.8887114e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2058055e-06, Final residual = 2.4385275e-08, No Iterations 3
time step continuity errors : sum local = 3.7829011e-10, global = 4.0360092e-13, cumulative = -1.7476659e-07
ExecutionTime = 563.03 s  ClockTime = 567 s

Time = 642

smoothSolver:  Solving for Ux, Initial residual = 6.4190834e-08, Final residual = 1.9053466e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.3034189e-08, Final residual = 2.0210365e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011618495, Final residual = 8.7614669e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5098021e-05, Final residual = 1.1689514e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.6019887e-06, Final residual = 4.7614621e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.1094598e-06, Final residual = 2.2201738e-08, No Iterations 4
time step continuity errors : sum local = 3.4473391e-10, global = 4.0556086e-13, cumulative = -1.7476619e-07
ExecutionTime = 563.85 s  ClockTime = 568 s

Time = 643

smoothSolver:  Solving for Ux, Initial residual = 6.4161626e-08, Final residual = 1.9033782e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.2935788e-08, Final residual = 2.0175835e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001159396, Final residual = 8.5070892e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5143919e-05, Final residual = 1.2474698e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.6693115e-06, Final residual = 5.1014543e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2217707e-06, Final residual = 2.5791458e-08, No Iterations 3
time step continuity errors : sum local = 4.0010184e-10, global = 4.6780907e-13, cumulative = -1.7476572e-07
ExecutionTime = 564.81 s  ClockTime = 569 s

Time = 644

smoothSolver:  Solving for Ux, Initial residual = 6.390132e-08, Final residual = 1.8975266e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.2980453e-08, Final residual = 2.0130731e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001156909, Final residual = 8.7531962e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5049412e-05, Final residual = 1.167695e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.6066971e-06, Final residual = 5.1227721e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.1341744e-06, Final residual = 1.881878e-08, No Iterations 3
time step continuity errors : sum local = 2.9249084e-10, global = 2.4551363e-13, cumulative = -1.7476548e-07
ExecutionTime = 565.49 s  ClockTime = 570 s

Time = 645

smoothSolver:  Solving for Ux, Initial residual = 6.3831039e-08, Final residual = 9.9934318e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2876948e-08, Final residual = 2.0096549e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011447411, Final residual = 6.2045247e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.8266183e-05, Final residual = 1.3457737e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.9282761e-06, Final residual = 6.1874887e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.3780027e-06, Final residual = 3.345716e-08, No Iterations 5
time step continuity errors : sum local = 5.1868219e-10, global = 4.9781381e-13, cumulative = -1.7476498e-07
ExecutionTime = 566.21 s  ClockTime = 570 s

Time = 646

smoothSolver:  Solving for Ux, Initial residual = 6.4022908e-08, Final residual = 9.9668301e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2869319e-08, Final residual = 1.9932238e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011348943, Final residual = 8.1439165e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.1468347e-05, Final residual = 1.4151353e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 8.0131126e-06, Final residual = 7.204695e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.7089651e-06, Final residual = 3.5090598e-08, No Iterations 5
time step continuity errors : sum local = 5.4386653e-10, global = 5.2569462e-13, cumulative = -1.7476445e-07
ExecutionTime = 566.92 s  ClockTime = 571 s

Time = 647

smoothSolver:  Solving for Ux, Initial residual = 6.4518126e-08, Final residual = 1.8973678e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.2676839e-08, Final residual = 1.9717852e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011371311, Final residual = 9.8210412e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5516323e-05, Final residual = 1.512779e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.1536263e-06, Final residual = 7.1231778e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.2636794e-06, Final residual = 2.672172e-08, No Iterations 8
time step continuity errors : sum local = 4.1446634e-10, global = 5.6107844e-13, cumulative = -1.7476389e-07
ExecutionTime = 567.71 s  ClockTime = 572 s

Time = 648

smoothSolver:  Solving for Ux, Initial residual = 6.448312e-08, Final residual = 1.9029925e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.2693159e-08, Final residual = 1.9610274e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011400179, Final residual = 9.528326e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5354957e-05, Final residual = 1.5074466e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.9136028e-06, Final residual = 4.6025151e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.2618802e-06, Final residual = 3.2047371e-08, No Iterations 4
time step continuity errors : sum local = 4.9673044e-10, global = 5.7423722e-13, cumulative = -1.7476332e-07
ExecutionTime = 568.55 s  ClockTime = 573 s

Time = 649

smoothSolver:  Solving for Ux, Initial residual = 6.4369085e-08, Final residual = 1.9007307e-09, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 1.26159e-08, Final residual = 1.9616102e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011397821, Final residual = 1.1010423e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6623253e-05, Final residual = 1.4761732e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.7861992e-06, Final residual = 6.2190121e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.4662091e-06, Final residual = 1.4216355e-08, No Iterations 4
time step continuity errors : sum local = 2.2121096e-10, global = 3.7690333e-14, cumulative = -1.7476328e-07
ExecutionTime = 569.56 s  ClockTime = 574 s

Time = 650

smoothSolver:  Solving for Ux, Initial residual = 6.3843674e-08, Final residual = 9.9568013e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2728748e-08, Final residual = 1.9682669e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011256382, Final residual = 8.8366668e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4757378e-05, Final residual = 1.1761631e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.537397e-06, Final residual = 1.6379035e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.0455835e-06, Final residual = 3.0183695e-08, No Iterations 6
time step continuity errors : sum local = 4.6759428e-10, global = -3.6765506e-14, cumulative = -1.7476332e-07
ExecutionTime = 571.21 s  ClockTime = 576 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122679

Time = 651

smoothSolver:  Solving for Ux, Initial residual = 6.4056349e-08, Final residual = 9.9015351e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2678309e-08, Final residual = 1.9661933e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011149686, Final residual = 9.130966e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4978009e-05, Final residual = 1.3788642e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.8493992e-06, Final residual = 6.1735306e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.1675015e-06, Final residual = 2.9646132e-08, No Iterations 5
time step continuity errors : sum local = 4.596863e-10, global = 2.8486437e-13, cumulative = -1.7476303e-07
ExecutionTime = 571.91 s  ClockTime = 576 s

Time = 652

smoothSolver:  Solving for Ux, Initial residual = 6.386299e-08, Final residual = 9.884237e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2665778e-08, Final residual = 1.9555083e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011084268, Final residual = 5.5894365e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.7247697e-05, Final residual = 1.1697769e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.6327781e-06, Final residual = 5.4337768e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.2209126e-06, Final residual = 2.9252123e-08, No Iterations 3
time step continuity errors : sum local = 4.5356396e-10, global = 1.8432353e-13, cumulative = -1.7476285e-07
ExecutionTime = 572.66 s  ClockTime = 577 s

Time = 653

smoothSolver:  Solving for Ux, Initial residual = 6.3946555e-08, Final residual = 9.9082139e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2486971e-08, Final residual = 1.9412037e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00011030165, Final residual = 6.0960864e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 1.7745082e-05, Final residual = 1.4208669e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.7997007e-06, Final residual = 6.4835476e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.3667128e-06, Final residual = 3.2435434e-08, No Iterations 5
time step continuity errors : sum local = 5.0284963e-10, global = 1.5713756e-13, cumulative = -1.7476269e-07
ExecutionTime = 573.44 s  ClockTime = 578 s

Time = 654

smoothSolver:  Solving for Ux, Initial residual = 6.3975094e-08, Final residual = 9.9185677e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2468718e-08, Final residual = 1.9255883e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010974058, Final residual = 1.0941243e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.55119e-05, Final residual = 1.4517511e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 7.4917596e-06, Final residual = 7.0762809e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.2750407e-06, Final residual = 3.1189185e-08, No Iterations 7
time step continuity errors : sum local = 4.8372019e-10, global = 1.4035143e-13, cumulative = -1.7476255e-07
ExecutionTime = 574.88 s  ClockTime = 579 s

Time = 655

smoothSolver:  Solving for Ux, Initial residual = 6.4141133e-08, Final residual = 9.9386177e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.230583e-08, Final residual = 1.9132123e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010922637, Final residual = 8.7578039e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.464634e-05, Final residual = 1.2954684e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.5361567e-06, Final residual = 6.084548e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2217057e-06, Final residual = 2.4610218e-08, No Iterations 5
time step continuity errors : sum local = 3.8212112e-10, global = 1.4119209e-13, cumulative = -1.7476241e-07
ExecutionTime = 575.92 s  ClockTime = 580 s

Time = 656

smoothSolver:  Solving for Ux, Initial residual = 6.4156882e-08, Final residual = 9.9301068e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2326092e-08, Final residual = 1.9044034e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010925202, Final residual = 8.592842e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.468477e-05, Final residual = 9.7702617e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.8816387e-06, Final residual = 5.3900608e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.9403568e-06, Final residual = 2.8013948e-08, No Iterations 6
time step continuity errors : sum local = 4.3429198e-10, global = 1.3980842e-13, cumulative = -1.7476227e-07
ExecutionTime = 576.73 s  ClockTime = 581 s

Time = 657

smoothSolver:  Solving for Ux, Initial residual = 6.4218798e-08, Final residual = 9.9253403e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2249341e-08, Final residual = 1.8998621e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010917782, Final residual = 8.7527339e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5019696e-05, Final residual = 1.4401692e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.7450719e-06, Final residual = 5.1961369e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.5453713e-06, Final residual = 2.4381326e-08, No Iterations 3
time step continuity errors : sum local = 3.7839673e-10, global = 1.5104891e-13, cumulative = -1.7476212e-07
ExecutionTime = 577.64 s  ClockTime = 582 s

Time = 658

smoothSolver:  Solving for Ux, Initial residual = 6.3819271e-08, Final residual = 9.8861456e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.229903e-08, Final residual = 1.8981247e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010819197, Final residual = 8.7365574e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4499522e-05, Final residual = 9.1055424e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.9027429e-06, Final residual = 4.5841772e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.8936196e-06, Final residual = 1.6340433e-08, No Iterations 8
time step continuity errors : sum local = 2.5384287e-10, global = 1.9092498e-13, cumulative = -1.7476193e-07
ExecutionTime = 578.61 s  ClockTime = 583 s

Time = 659

smoothSolver:  Solving for Ux, Initial residual = 6.3848735e-08, Final residual = 9.8589282e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2235389e-08, Final residual = 1.898793e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010716656, Final residual = 8.2443509e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.3851304e-05, Final residual = 1.2600307e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.4343379e-06, Final residual = 5.1609215e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.7067709e-06, Final residual = 2.6617457e-08, No Iterations 5
time step continuity errors : sum local = 4.1306827e-10, global = 2.022446e-13, cumulative = -1.7476172e-07
ExecutionTime = 579.48 s  ClockTime = 584 s

Time = 660

smoothSolver:  Solving for Ux, Initial residual = 6.3552549e-08, Final residual = 9.8198188e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2286913e-08, Final residual = 1.9002329e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010781213, Final residual = 8.652173e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4632498e-05, Final residual = 9.6590258e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.9914233e-06, Final residual = 4.1997697e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.9188591e-06, Final residual = 2.7633976e-08, No Iterations 3
time step continuity errors : sum local = 4.2834961e-10, global = 2.1980512e-13, cumulative = -1.747615e-07
ExecutionTime = 580.25 s  ClockTime = 585 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122679

Time = 661

smoothSolver:  Solving for Ux, Initial residual = 6.349499e-08, Final residual = 9.8049702e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2286092e-08, Final residual = 1.8991404e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010840227, Final residual = 8.5467725e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5224327e-05, Final residual = 1.1203042e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.2113502e-06, Final residual = 5.3055321e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.183332e-06, Final residual = 3.102553e-08, No Iterations 3
time step continuity errors : sum local = 4.8099199e-10, global = 2.5202045e-13, cumulative = -1.7476125e-07
ExecutionTime = 581.03 s  ClockTime = 585 s

Time = 662

smoothSolver:  Solving for Ux, Initial residual = 6.3089719e-08, Final residual = 9.7614766e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2318757e-08, Final residual = 1.8966006e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010676247, Final residual = 8.3574563e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.3938784e-05, Final residual = 1.1855888e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.2235101e-06, Final residual = 3.5073879e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.911903e-06, Final residual = 1.8562604e-08, No Iterations 3
time step continuity errors : sum local = 2.8844069e-10, global = 1.5734212e-13, cumulative = -1.7476109e-07
ExecutionTime = 581.76 s  ClockTime = 586 s

Time = 663

smoothSolver:  Solving for Ux, Initial residual = 6.2704799e-08, Final residual = 9.7459593e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.21997e-08, Final residual = 1.8962571e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001071628, Final residual = 8.515187e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4580464e-05, Final residual = 1.2657065e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.569413e-06, Final residual = 4.6154799e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.1483387e-06, Final residual = 2.3214472e-08, No Iterations 3
time step continuity errors : sum local = 3.6044823e-10, global = 2.7747422e-13, cumulative = -1.7476082e-07
ExecutionTime = 582.55 s  ClockTime = 587 s

Time = 664

smoothSolver:  Solving for Ux, Initial residual = 6.2790937e-08, Final residual = 9.7433792e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2194641e-08, Final residual = 1.8892092e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010750499, Final residual = 8.3437638e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4977395e-05, Final residual = 1.2164928e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.1820319e-06, Final residual = 5.9313216e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.0461128e-06, Final residual = 2.7201213e-08, No Iterations 5
time step continuity errors : sum local = 4.2160619e-10, global = 3.0774924e-13, cumulative = -1.7476051e-07
ExecutionTime = 583.27 s  ClockTime = 588 s

Time = 665

smoothSolver:  Solving for Ux, Initial residual = 6.2527374e-08, Final residual = 9.7122165e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2209206e-08, Final residual = 1.8837944e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010602186, Final residual = 8.0127961e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.383521e-05, Final residual = 8.9221495e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.5275481e-06, Final residual = 3.9496749e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.7175004e-06, Final residual = 2.2648907e-08, No Iterations 3
time step continuity errors : sum local = 3.5162924e-10, global = 3.1801201e-13, cumulative = -1.7476019e-07
ExecutionTime = 584.32 s  ClockTime = 589 s

Time = 666

smoothSolver:  Solving for Ux, Initial residual = 6.2364823e-08, Final residual = 9.7037775e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2102708e-08, Final residual = 1.8816089e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001065219, Final residual = 8.4995354e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4517342e-05, Final residual = 1.4154043e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.6148921e-06, Final residual = 5.324762e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.1789611e-06, Final residual = 2.3704066e-08, No Iterations 3
time step continuity errors : sum local = 3.6794357e-10, global = 3.4113526e-13, cumulative = -1.7475985e-07
ExecutionTime = 585.16 s  ClockTime = 590 s

Time = 667

smoothSolver:  Solving for Ux, Initial residual = 6.2565289e-08, Final residual = 9.7032044e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2106409e-08, Final residual = 1.8741406e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010680471, Final residual = 8.2606709e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4862455e-05, Final residual = 1.0851685e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.0717376e-06, Final residual = 5.8973869e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.0282438e-06, Final residual = 1.0242732e-08, No Iterations 6
time step continuity errors : sum local = 1.5955937e-10, global = -4.9288861e-14, cumulative = -1.747599e-07
ExecutionTime = 586.02 s  ClockTime = 590 s

Time = 668

smoothSolver:  Solving for Ux, Initial residual = 6.2420566e-08, Final residual = 9.6696759e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2140038e-08, Final residual = 1.8695134e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010541483, Final residual = 8.1720286e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.380518e-05, Final residual = 1.167594e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.1647332e-06, Final residual = 1.0360194e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.9406829e-06, Final residual = 2.045889e-08, No Iterations 4
time step continuity errors : sum local = 3.1793247e-10, global = -3.7496312e-14, cumulative = -1.7475994e-07
ExecutionTime = 586.86 s  ClockTime = 591 s

Time = 669

smoothSolver:  Solving for Ux, Initial residual = 6.2116109e-08, Final residual = 9.6563426e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2033334e-08, Final residual = 1.8686385e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010595281, Final residual = 8.4590003e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4521578e-05, Final residual = 1.2265176e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.5087274e-06, Final residual = 5.451325e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.1224654e-06, Final residual = 2.8518031e-08, No Iterations 5
time step continuity errors : sum local = 4.4209895e-10, global = 1.3839295e-13, cumulative = -1.747598e-07
ExecutionTime = 587.63 s  ClockTime = 592 s

Time = 670

smoothSolver:  Solving for Ux, Initial residual = 6.2367976e-08, Final residual = 9.650652e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2052564e-08, Final residual = 1.8625944e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001061927, Final residual = 8.264176e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4867443e-05, Final residual = 8.855921e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.9607032e-06, Final residual = 5.9073269e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.0191211e-06, Final residual = 2.301563e-08, No Iterations 6
time step continuity errors : sum local = 3.5715566e-10, global = 8.1192811e-14, cumulative = -1.7475972e-07
ExecutionTime = 588.42 s  ClockTime = 593 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122679

Time = 671

smoothSolver:  Solving for Ux, Initial residual = 6.2073012e-08, Final residual = 9.6126352e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.2072779e-08, Final residual = 1.8591495e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010484525, Final residual = 8.2227086e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.3817404e-05, Final residual = 1.1018814e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.1167214e-06, Final residual = 4.4740373e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.8955549e-06, Final residual = 2.3363826e-08, No Iterations 5
time step continuity errors : sum local = 3.6240711e-10, global = 4.1176798e-14, cumulative = -1.7475968e-07
ExecutionTime = 589.21 s  ClockTime = 594 s

Time = 672

smoothSolver:  Solving for Ux, Initial residual = 6.1872999e-08, Final residual = 9.5980345e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1968009e-08, Final residual = 1.8585597e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010521481, Final residual = 8.3386213e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4367832e-05, Final residual = 1.2021026e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.4317066e-06, Final residual = 5.0067397e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.0929432e-06, Final residual = 2.640634e-08, No Iterations 3
time step continuity errors : sum local = 4.0974666e-10, global = 5.0097042e-15, cumulative = -1.7475967e-07
ExecutionTime = 589.92 s  ClockTime = 594 s

Time = 673

smoothSolver:  Solving for Ux, Initial residual = 6.1942561e-08, Final residual = 9.5917366e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1976818e-08, Final residual = 1.8529204e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010565051, Final residual = 8.1665083e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4865639e-05, Final residual = 9.3565089e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.9901141e-06, Final residual = 5.2071008e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.1446866e-06, Final residual = 3.061639e-08, No Iterations 3
time step continuity errors : sum local = 4.746304e-10, global = -6.9744896e-15, cumulative = -1.7475968e-07
ExecutionTime = 590.63 s  ClockTime = 595 s

Time = 674

smoothSolver:  Solving for Ux, Initial residual = 6.1610531e-08, Final residual = 9.5555909e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1996843e-08, Final residual = 1.8495194e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010428949, Final residual = 8.0947488e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.3817571e-05, Final residual = 1.1973072e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.1439755e-06, Final residual = 5.0920063e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.9949084e-06, Final residual = 2.2456634e-08, No Iterations 3
time step continuity errors : sum local = 3.4848286e-10, global = -3.8541964e-15, cumulative = -1.7475968e-07
ExecutionTime = 591.33 s  ClockTime = 596 s

Time = 675

smoothSolver:  Solving for Ux, Initial residual = 6.1311815e-08, Final residual = 9.5430436e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1875728e-08, Final residual = 1.8485738e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010469773, Final residual = 8.3056464e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4398124e-05, Final residual = 1.2940862e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.4866578e-06, Final residual = 3.8098987e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.3482461e-06, Final residual = 2.590739e-08, No Iterations 3
time step continuity errors : sum local = 4.016965e-10, global = 8.0574608e-15, cumulative = -1.7475967e-07
ExecutionTime = 592.13 s  ClockTime = 597 s

Time = 676

smoothSolver:  Solving for Ux, Initial residual = 6.1458013e-08, Final residual = 9.5388013e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1890567e-08, Final residual = 1.842505e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010513282, Final residual = 8.1904282e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4859251e-05, Final residual = 1.0436733e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.067351e-06, Final residual = 5.8399595e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2084454e-06, Final residual = 3.1221851e-08, No Iterations 3
time step continuity errors : sum local = 4.8403369e-10, global = 9.7228832e-15, cumulative = -1.7475966e-07
ExecutionTime = 592.99 s  ClockTime = 597 s

Time = 677

smoothSolver:  Solving for Ux, Initial residual = 6.1285897e-08, Final residual = 9.5041949e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1926716e-08, Final residual = 1.8388265e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010387877, Final residual = 8.0831558e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.3919067e-05, Final residual = 1.3131691e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.2045682e-06, Final residual = 4.1529824e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.2207092e-06, Final residual = 2.5945473e-08, No Iterations 4
time step continuity errors : sum local = 4.0210096e-10, global = 5.7800726e-14, cumulative = -1.7475961e-07
ExecutionTime = 593.92 s  ClockTime = 598 s

Time = 678

smoothSolver:  Solving for Ux, Initial residual = 6.1052608e-08, Final residual = 9.4928751e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1810098e-08, Final residual = 1.8375644e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010427058, Final residual = 8.375559e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4456616e-05, Final residual = 1.3832694e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.5199529e-06, Final residual = 4.4585928e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.3927712e-06, Final residual = 2.564318e-08, No Iterations 3
time step continuity errors : sum local = 3.9801767e-10, global = 6.8487237e-14, cumulative = -1.7475954e-07
ExecutionTime = 594.91 s  ClockTime = 599 s

Time = 679

smoothSolver:  Solving for Ux, Initial residual = 6.1232915e-08, Final residual = 9.4889801e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1829812e-08, Final residual = 1.8316543e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010475555, Final residual = 8.3833036e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4929354e-05, Final residual = 1.0431535e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.107358e-06, Final residual = 5.773013e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.1751255e-06, Final residual = 3.0306631e-08, No Iterations 3
time step continuity errors : sum local = 4.6997636e-10, global = 8.1156444e-14, cumulative = -1.7475946e-07
ExecutionTime = 595.7 s  ClockTime = 600 s

Time = 680

smoothSolver:  Solving for Ux, Initial residual = 6.103519e-08, Final residual = 9.4542796e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1867182e-08, Final residual = 1.8283481e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010353718, Final residual = 8.1589453e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.40799e-05, Final residual = 1.3044264e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.289727e-06, Final residual = 4.5542977e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.1831596e-06, Final residual = 2.5887026e-08, No Iterations 4
time step continuity errors : sum local = 4.0182234e-10, global = 1.388207e-13, cumulative = -1.7475932e-07
ExecutionTime = 596.62 s  ClockTime = 601 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122679

Time = 681

smoothSolver:  Solving for Ux, Initial residual = 6.0761011e-08, Final residual = 9.4427725e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1747678e-08, Final residual = 1.8273979e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010391283, Final residual = 8.5407814e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4616598e-05, Final residual = 1.3602561e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.628699e-06, Final residual = 4.0475101e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.3240894e-06, Final residual = 2.4546296e-08, No Iterations 3
time step continuity errors : sum local = 3.8091406e-10, global = 1.4928093e-13, cumulative = -1.7475917e-07
ExecutionTime = 597.68 s  ClockTime = 602 s

Time = 682

smoothSolver:  Solving for Ux, Initial residual = 6.0887322e-08, Final residual = 9.4370919e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1759293e-08, Final residual = 1.8219804e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010428867, Final residual = 8.5864912e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5065216e-05, Final residual = 1.0805619e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.2337612e-06, Final residual = 5.6798888e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.2564214e-06, Final residual = 3.1132064e-08, No Iterations 3
time step continuity errors : sum local = 4.8287034e-10, global = 1.7363125e-13, cumulative = -1.7475899e-07
ExecutionTime = 598.35 s  ClockTime = 603 s

Time = 683

smoothSolver:  Solving for Ux, Initial residual = 6.0683341e-08, Final residual = 9.4036637e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1801217e-08, Final residual = 1.8189848e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010334157, Final residual = 8.336457e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4345818e-05, Final residual = 1.4148558e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.4714002e-06, Final residual = 3.8570781e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.2337995e-06, Final residual = 2.1841749e-08, No Iterations 3
time step continuity errors : sum local = 3.3903922e-10, global = 2.1261323e-13, cumulative = -1.7475878e-07
ExecutionTime = 599.06 s  ClockTime = 604 s

Time = 684

smoothSolver:  Solving for Ux, Initial residual = 6.0539446e-08, Final residual = 9.3931681e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.167e-08, Final residual = 1.8168822e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.000103257, Final residual = 8.4813494e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4365842e-05, Final residual = 1.4183971e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.4680563e-06, Final residual = 3.8261468e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.2212331e-06, Final residual = 2.331153e-08, No Iterations 3
time step continuity errors : sum local = 3.615712e-10, global = 2.4242842e-13, cumulative = -1.7475854e-07
ExecutionTime = 599.78 s  ClockTime = 604 s

Time = 685

smoothSolver:  Solving for Ux, Initial residual = 6.0468608e-08, Final residual = 9.374572e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1661399e-08, Final residual = 1.8132969e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010341822, Final residual = 8.6393657e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4534683e-05, Final residual = 1.0113274e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.7792885e-06, Final residual = 5.6040936e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.8614094e-06, Final residual = 1.9590751e-08, No Iterations 6
time step continuity errors : sum local = 3.0426165e-10, global = 2.8171427e-13, cumulative = -1.7475826e-07
ExecutionTime = 600.55 s  ClockTime = 605 s

Time = 686

smoothSolver:  Solving for Ux, Initial residual = 6.04437e-08, Final residual = 9.3609285e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1638911e-08, Final residual = 1.8104939e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001028874, Final residual = 8.4354137e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4275064e-05, Final residual = 1.0585417e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.6476889e-06, Final residual = 5.6349168e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.7784733e-06, Final residual = 2.4656217e-08, No Iterations 6
time step continuity errors : sum local = 3.8262046e-10, global = 3.0635117e-13, cumulative = -1.7475795e-07
ExecutionTime = 601.31 s  ClockTime = 606 s

Time = 687

smoothSolver:  Solving for Ux, Initial residual = 6.0316215e-08, Final residual = 9.3398557e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1686525e-08, Final residual = 1.8082466e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010387075, Final residual = 8.8912448e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5014832e-05, Final residual = 1.1039076e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.1746514e-06, Final residual = 5.5866712e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.1932088e-06, Final residual = 3.0960722e-08, No Iterations 3
time step continuity errors : sum local = 4.7991348e-10, global = 3.2723735e-13, cumulative = -1.7475762e-07
ExecutionTime = 601.99 s  ClockTime = 606 s

Time = 688

smoothSolver:  Solving for Ux, Initial residual = 6.0482394e-08, Final residual = 9.3426437e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.168262e-08, Final residual = 1.8049153e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.0001049334, Final residual = 9.5126685e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6062971e-05, Final residual = 1.3281434e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.9474227e-06, Final residual = 4.9776274e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.7841189e-06, Final residual = 3.219751e-08, No Iterations 3
time step continuity errors : sum local = 4.991698e-10, global = 3.6014801e-13, cumulative = -1.7475726e-07
ExecutionTime = 602.69 s  ClockTime = 607 s

Time = 689

smoothSolver:  Solving for Ux, Initial residual = 6.0348568e-08, Final residual = 9.3083528e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1731282e-08, Final residual = 1.8015581e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010367726, Final residual = 9.06705e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4875447e-05, Final residual = 1.2728593e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.0939283e-06, Final residual = 4.2122858e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.3074083e-06, Final residual = 2.4382059e-08, No Iterations 3
time step continuity errors : sum local = 3.7835422e-10, global = 3.8944765e-13, cumulative = -1.7475688e-07
ExecutionTime = 603.39 s  ClockTime = 608 s

Time = 690

smoothSolver:  Solving for Ux, Initial residual = 6.0229787e-08, Final residual = 9.2992904e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1603244e-08, Final residual = 1.8000142e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010361889, Final residual = 9.2811016e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4987249e-05, Final residual = 1.2458671e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.1605652e-06, Final residual = 4.3487212e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.3430237e-06, Final residual = 2.4735978e-08, No Iterations 3
time step continuity errors : sum local = 3.8394201e-10, global = 4.175404e-13, cumulative = -1.7475646e-07
ExecutionTime = 604.12 s  ClockTime = 609 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122679

Time = 691

smoothSolver:  Solving for Ux, Initial residual = 6.0219892e-08, Final residual = 9.2832841e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1592688e-08, Final residual = 1.7961471e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010345747, Final residual = 9.5079896e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4833474e-05, Final residual = 1.2407565e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.8946871e-06, Final residual = 4.5955663e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.2129406e-06, Final residual = 2.4785428e-08, No Iterations 3
time step continuity errors : sum local = 3.8469971e-10, global = 4.4544315e-13, cumulative = -1.7475601e-07
ExecutionTime = 605.03 s  ClockTime = 609 s

Time = 692

smoothSolver:  Solving for Ux, Initial residual = 6.0180381e-08, Final residual = 9.2643408e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.164104e-08, Final residual = 1.7955006e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010471045, Final residual = 1.0207322e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5858734e-05, Final residual = 1.2691676e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.4064322e-06, Final residual = 3.9955295e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.4485072e-06, Final residual = 2.7897522e-08, No Iterations 3
time step continuity errors : sum local = 4.3250521e-10, global = 4.7239655e-13, cumulative = -1.7475554e-07
ExecutionTime = 606.57 s  ClockTime = 611 s

Time = 693

smoothSolver:  Solving for Ux, Initial residual = 6.0277481e-08, Final residual = 9.259673e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1656231e-08, Final residual = 1.7924373e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010559582, Final residual = 1.0515373e-06, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.6620399e-05, Final residual = 1.3658554e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.7867099e-06, Final residual = 4.5298742e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.8343894e-06, Final residual = 2.9707236e-08, No Iterations 3
time step continuity errors : sum local = 4.6067498e-10, global = 5.0304422e-13, cumulative = -1.7475504e-07
ExecutionTime = 607.41 s  ClockTime = 612 s

Time = 694

smoothSolver:  Solving for Ux, Initial residual = 6.0056178e-08, Final residual = 9.2245616e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1698305e-08, Final residual = 1.7890499e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010414197, Final residual = 9.9542649e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5029408e-05, Final residual = 1.1853583e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.6801173e-06, Final residual = 5.0714899e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.0183228e-06, Final residual = 2.4155559e-08, No Iterations 3
time step continuity errors : sum local = 3.7469482e-10, global = 5.2983013e-13, cumulative = -1.7475451e-07
ExecutionTime = 608.26 s  ClockTime = 613 s

Time = 695

smoothSolver:  Solving for Ux, Initial residual = 5.9754029e-08, Final residual = 9.2133729e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1554192e-08, Final residual = 1.7879446e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010384501, Final residual = 9.9160525e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4820143e-05, Final residual = 1.0174442e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.6341769e-06, Final residual = 5.402658e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.8123853e-06, Final residual = 2.5288823e-08, No Iterations 4
time step continuity errors : sum local = 3.9242465e-10, global = 5.6118828e-13, cumulative = -1.7475395e-07
ExecutionTime = 609.27 s  ClockTime = 614 s

Time = 696

smoothSolver:  Solving for Ux, Initial residual = 5.9642601e-08, Final residual = 9.1939084e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1522018e-08, Final residual = 1.7836313e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010325356, Final residual = 9.4344352e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4213951e-05, Final residual = 1.2241235e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.1327287e-06, Final residual = 4.5258268e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.845406e-06, Final residual = 2.1353455e-08, No Iterations 3
time step continuity errors : sum local = 3.3166926e-10, global = 4.8833447e-13, cumulative = -1.7475346e-07
ExecutionTime = 610.34 s  ClockTime = 615 s

Time = 697

smoothSolver:  Solving for Ux, Initial residual = 5.9401254e-08, Final residual = 9.1680963e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1543883e-08, Final residual = 1.7814369e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010386319, Final residual = 9.1779308e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4716414e-05, Final residual = 1.2775386e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.5274445e-06, Final residual = 4.7544133e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 3.155223e-06, Final residual = 2.5087052e-08, No Iterations 3
time step continuity errors : sum local = 3.893599e-10, global = 5.7847335e-13, cumulative = -1.7475288e-07
ExecutionTime = 611.13 s  ClockTime = 616 s

Time = 698

smoothSolver:  Solving for Ux, Initial residual = 5.9419706e-08, Final residual = 9.1634699e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1522298e-08, Final residual = 1.7767616e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010420715, Final residual = 8.6741418e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.5218494e-05, Final residual = 1.1256606e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.2854152e-06, Final residual = 6.0813709e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.1754618e-06, Final residual = 1.0076942e-08, No Iterations 5
time step continuity errors : sum local = 1.5708689e-10, global = 2.3273119e-13, cumulative = -1.7475265e-07
ExecutionTime = 611.92 s  ClockTime = 616 s

Time = 699

smoothSolver:  Solving for Ux, Initial residual = 5.9151123e-08, Final residual = 9.1235028e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1547075e-08, Final residual = 1.7719576e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010230032, Final residual = 8.0682472e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.3818105e-05, Final residual = 8.728462e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.6354027e-06, Final residual = 3.8645632e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.8032724e-06, Final residual = 1.7385085e-08, No Iterations 3
time step continuity errors : sum local = 2.7017658e-10, global = -1.251045e-14, cumulative = -1.7475266e-07
ExecutionTime = 612.63 s  ClockTime = 617 s

Time = 700

smoothSolver:  Solving for Ux, Initial residual = 5.8903311e-08, Final residual = 9.1114473e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1393169e-08, Final residual = 1.7682405e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010141687, Final residual = 7.9022678e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.3559555e-05, Final residual = 1.2862404e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.3387746e-06, Final residual = 1.5019542e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 2.8010179e-06, Final residual = 2.57326e-08, No Iterations 4
time step continuity errors : sum local = 3.9885086e-10, global = -2.7427735e-14, cumulative = -1.7475269e-07
ExecutionTime = 614.23 s  ClockTime = 619 s

surfaceFieldValue flowRateTM write:
    sum(outlet_tm) of phi = 2.4660806e-11

surfaceFieldValue flowRateTM_left write:
    sum(outlet_tm_left) of phi = 2.5339194e-11

surfaceFieldValue pressureACinlet write:
    areaAverage(ac_inlet) of p = 2.0122679

Time = 701

smoothSolver:  Solving for Ux, Initial residual = 5.8564545e-08, Final residual = 9.0919324e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1373991e-08, Final residual = 1.7638678e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010142659, Final residual = 8.2135287e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.391788e-05, Final residual = 9.4584369e-08, No Iterations 4
GAMG:  Solving for p, Initial residual = 5.8269231e-06, Final residual = 5.3951655e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 2.8630641e-06, Final residual = 2.6679106e-08, No Iterations 4
time step continuity errors : sum local = 4.1386839e-10, global = 1.2973273e-13, cumulative = -1.7475256e-07
ExecutionTime = 615.03 s  ClockTime = 620 s

Time = 702

smoothSolver:  Solving for Ux, Initial residual = 5.8674802e-08, Final residual = 9.087468e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1368706e-08, Final residual = 1.7588814e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010176108, Final residual = 8.4192332e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.4526862e-05, Final residual = 1.2007812e-07, No Iterations 4
GAMG:  Solving for p, Initial residual = 6.2500801e-06, Final residual = 5.6330091e-08, No Iterations 3
GAMG:  Solving for p, Initial residual = 3.1442017e-06, Final residual = 2.8403185e-08, No Iterations 5
time step continuity errors : sum local = 4.4031148e-10, global = 3.0041675e-14, cumulative = -1.7475253e-07
ExecutionTime = 615.81 s  ClockTime = 621 s

Time = 703

smoothSolver:  Solving for Ux, Initial residual = 5.8532605e-08, Final residual = 9.0553966e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1413764e-08, Final residual = 1.7546865e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.00010036534, Final residual = 8.224328e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.3468034e-05, Final residual = 1.3338759e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.2836727e-06, Final residual = 3.4173899e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 3.020459e-06, Final residual = 2.309754e-08, No Iterations 4
time step continuity errors : sum local = 3.5853463e-10, global = -2.0509145e-14, cumulative = -1.7475255e-07
ExecutionTime = 616.54 s  ClockTime = 621 s

Time = 704

smoothSolver:  Solving for Ux, Initial residual = 5.8705728e-08, Final residual = 9.0468622e-09, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1.1313996e-08, Final residual = 1.7508282e-09, No Iterations 1
GAMG:  Solving for p, Initial residual = 9.9539173e-05, Final residual = 8.29613e-07, No Iterations 2
GAMG:  Solving for p, Initial residual = 1.3073887e-05, Final residual = 1.1743904e-07, No Iterations 3
GAMG:  Solving for p, Initial residual = 5.0369269e-06, Final residual = 2.8805337e-08, No Iterations 5
GAMG:  Solving for p, Initial residual = 2.916795e-06, Final residual = 2.3828101e-08, No Iterations 4
time step continuity errors : sum local = 3.6951544e-10, global = -7.8433892e-14, cumulative = -1.7475263e-07
ExecutionTime = 617.29 s  ClockTime = 622 s


SIMPLE solution converged in 704 iterations

End

