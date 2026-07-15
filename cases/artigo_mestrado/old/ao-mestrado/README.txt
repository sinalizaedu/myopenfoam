artoph-fsi-curva-mestrado
=========================

One-way FSI (preCICE): Newtonian blood in the lumen (pimpleFoam, static mesh)
and linear elastic arterial wall (solids4Foam).

GEOMETRIA (refeita 2026-05-23 com extrusao estruturada):
  Substitui o pipeline blockMesh + snappyHexMesh + STLs por uma malha
  estruturada extrudada ao longo da centerline da arteria. Construida por
  brunaStuff/build_artoph_tubular_meshes.py (copiada em scripts/):
    1. Centerline extraida da artery.stl original via PCA + relaxacao
       iterativa por centroide local; suavizada e reamostrada em Nz = 160
       secoes uniformes em comprimento de arco (L ≈ 40 mm).
    2. Frames ortonormais (T, N, B) propagados por parallel transport
       (rotacao minima entre tangentes consecutivas).
    3. Lumen (fluido): cilindro polar R = 0.55 mm, 32 setores x 4 aneis
       radiais x 159 segmentos axiais → 20352 cells hex puro.
    4. Annulus (solido): anel polar puro R_in=0.55 → R_out=0.75 mm
       (espessura h = 0.20 mm), 32 setores x 3 aneis radiais x 159
       segmentos axiais → 15264 cells hex puro.
    5. Conectividade construida explicitamente em 3 categorias (axial,
       radial, angular) com orientacao validada face a face contra a
       normal esperada (saindo do owner para o neighbour).
  Qualidade da malha (vs versao anterior com snappy):
    - Fluido: nonOrtho max 7.3° (era 180°), AR max 10.6, skewness 0.45
    - Solido: nonOrtho max 9.5° (era 179°), AR max 4.5, skewness 0.46
    - Sem cells negativas, sem concaveCells, checkMesh OK em ambos.
  Patches gerados:
    - Fluido: inlet, outlet (caps), wall (R_int, interface FSI),
              axis (parede virtual em R*0.05, BC slip — artefato da malha
                    polar para evitar singularidade no eixo)
    - Solido: inner_cap_back, inner_cap_front (caps engastadas),
              lumen (R_int, interface FSI), arteria_externa (R_ext, free)

HISTORICO (referencia):
  - Bug do snappy "fluido como caixa giga": resolvido com raycast-validado
    locationInMesh (2026-05-22), mas substituido completamente pela malha
    extrudada acima (2026-05-23).
  - Tentativa de meshear o annulus 0.2 mm com snappy + 2 surfaces falhou
    (volumes negativos, nonOrtho 179°, ~50k concave cells) — espessura
    comparavel ao cell size. Solucionado com extrusao estruturada.

Fluid BCs (atualizado 2026-05-23):
  - pressao pulsatil sistemica nas duas extremidades (PAM = 13.3 kPa, faixa
    10.7-16 kPa, T = 0.8 s, 75 bpm), gerada por
    brunaStuff/gen_artoph_pressure_waveform.py em:
      fluid/constant/inlet_pressure.dat
      fluid/constant/outlet_pressure.dat
  - desnivel residual Δp_drive = 10 Pa entre inlet e outlet (apenas para
    quebrar singularidade matematica do sistema de pressao com BCs identicas;
    hidrodinamicamente desprezivel perto da faixa pulsatil de 5300 Pa).
    A simulacao representa entao a CARGA RADIAL PULSATIL sobre a parede,
    sem flow significativo no lumen.
  - rampa Hann nos primeiros 100 ms para evitar choque hidrostatico /
    water-hammer numerico no startup.

Parametros que GARANTEM convergencia (calibrado 2026-05-23):
  fluid/system/controlDict:
    endTime         0.8        # 1 ciclo cardiaco
    deltaT          1e-3       # Co_max ~ 4 com PIMPLE robusto
    writeInterval   20         # 41 snapshots = 1 a cada 20 ms
  fluid/system/fvSolution PIMPLE:
    nOuterCorrectors  2        # estabilidade extra para BCs pulsateis
    nCorrectors       3
    nNonOrthogonalCorrectors  1
  solid/constant/solidProperties unsLinearGeometryCoeffs:
    nCorrectors             150       # afrouxado de 500
    solutionTolerance       5e-2      # afrouxado de 1e-2
    alternativeTolerance    1e-4
    materialTolerance       1e-4
  precice-config.xml:
    time-window-size 1e-3, max-time 0.8

Para regenerar as tabelas (apos editar amplitudes, T ou ρ):
  python3 brunaStuff/gen_artoph_pressure_waveform.py

Notas para hemodinamica realista (futuro trabalho):
  - Aumentar DELTA_P_DRIVE_PA no script para 200-500 Pa.
  - Reduzir deltaT para 5e-5 a 1e-4 s (Co<1 com flow real).
  - Aumentar nOuterCorrectors do PIMPLE para 3-4.
  - Custo computacional: ordens de magnitude maior.

Run (Docker / OpenFOAM + preCICE + solids4foam, from repo root):

  cd cases/artoph-fsi-curva-mestrado
  ./Allrun

If WM_PROJECT_DIR is unset, Allrun only regenerates STLs and JSON hints.

After a simulation:

  python3 ../../brunaStuff/post_artoph_fsi_export_csv.py

Do not edit cases/artoph-curva-mestrado, cases/on-mestrado, or cases/eye-fsi-tc0.

Measurement note: closest point is in constant/closest_to_ON_ref.json (fluid
probes p/U and solid solidPointDisplacement). preCICE watch-point uses the same
coordinates. solidForces on inner-wall is the resultant on the full FSI patch,
not a point value — subset the patch if you need a local force.

