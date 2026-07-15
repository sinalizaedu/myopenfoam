# Por que o teste 2D estava lento + mudanças aplicadas (2026-05-24)

## TL;DR do diagnóstico

O 2D **NÃO** estava lento por causa do tamanho da malha (eram só ~7 mil
células no total). Estava lento por **não-convergência do solver do sólido**:

- Cada timestep de 2 ms levava ~130 segundos de wall time.
- Em todos os passos o `solids4Foam` batia o teto de `nCorrectors = 5000`
  **sem convergir**, com o residual oscilando entre 0.005 e 0.04
  (limit cycle clássico — relaxation alta + FSI + contato).
- Para 1 ciclo cardíaco (435 timesteps): ~16 horas. Para 3 ciclos: ~47 h.

O fluido em si rodou em **4.3 segundos de CPU** (mesh de 880 cells, tudo bem).

## Arquivos modificados

### 1) Solver do sólido (impacto principal — 10–50×)
`cases/teste-2d-fsi-oa-on/solid/constant/solidProperties`
- `nCorrectors`: 5000 → 800
- `solutionTolerance`: 1e-06 → 1e-04
- `alternativeTolerance`: 1e-07 → 1e-05
- `infoFrequency`: 500 → 50 (pra ver progresso por log)

`cases/teste-2d-fsi-oa-on/solid/system/fvSolution`
- Linear PCG/FDIC `tolerance`: 1e-12 → 1e-08 (1e-12 era exagero — o outer
  segregated só precisa de 1e-4; cada solve linear pagava o preço de 1e-12
  desnecessariamente)
- Linear PCG/FDIC `relTol`: 0.1 → 0.01
- `relaxationFactors.fields."D|DD"`: 0.5 → 0.3 (0.5 estava causando a
  oscilação no segregated loop; 0.3 amortece e converge)

### 2) Malha (impacto ~3–4×)
`brunaStuff/gen_teste_2d_fsi_blockmesh.py`
- `NX`: 80 → 40 (consistente entre fluido e sólido → mapping preCICE
  nearest-neighbor segue 1:1)
- `NY_A`: 40 → 20 (Block A, fat_below + ON + ONS)
- `NY_D`: 34 → 17 (fat_above)
- `NY_FLUID`: 11 → 6 (lumen — ainda dá perfil parabólico decente)
- `NY_B`, `NY_C`: 2 (mantidos — parede arterial muito fina, importante)

Totais novos:
- Sólido: 1640 cells (era 6240)
- Fluido: 240 cells (era 880)

### 3) Fluido (impacto ~2×, mas fluido já era rápido)
`cases/teste-2d-fsi-oa-on/fluid/system/fvSolution`
- `nOuterCorrectors`: 2 → 1 (one-way FSI com mesh estática, basta 1)
- `nCorrectors`: 3 → 2
- `nNonOrthogonalCorrectors`: 1 → 0 (mesh cartesiana perfeita)

## Tempo esperado depois das mudanças

Estimativa (a confirmar com o run real):

| Item                          | Antes      | Depois      |
|-------------------------------|------------|-------------|
| Wall time por timestep solid  | ~130 s     | ~3–8 s      |
| 1 ciclo (435 steps)           | ~16 h      | ~30 min – 1 h |
| 3 ciclos (1305 steps)         | ~47 h      | ~1.5–3 h    |

## Como rodar pra validar

```bash
docker compose run --rm fsi bash -c '
  cd /simulation/teste-2d-fsi-oa-on
  ./Allclean
  ./Allrun
'
```

Acompanhar com:
```bash
tail -f cases/teste-2d-fsi-oa-on/solid/log.solids4Foam
tail -f cases/teste-2d-fsi-oa-on/fluid/log.pimpleFoam
```

O que olhar no log do sólido:
- Os corretores devem agora **convergir** (relRes caindo abaixo de 1e-4),
  e o `Max iterations reached within momentum loop` deve sumir, OU
  pelo menos só aparecer no primeiro 1–2 timesteps de transiente.
- Cada timestep deve fechar em ~3–8 segundos em vez de ~130 s.

## Se ainda estiver lento ou divergir

Em ordem de impacto:

1. Reduzir `relaxationFactor` ainda mais (0.3 → 0.2).
2. Aumentar `nCorrectors` (800 → 1500) — mas só vale a pena se o residual
   está *caindo* até bater o teto, não se está oscilando.
3. Trocar `nonLinearGeometryUpdatedLagrangian` → `linearGeometryTotalDisplacement`
   (arquivos `solidProperties.linearGeom` e `0/D.linearGeom` já existem;
   é só copiar por cima). Linear geometry é ~5× mais rápido por iteração e
   é OK para deslocamentos pequenos (μm) deste caso.
4. Aumentar o `penaltyScale` lentamente em vez de jogar tudo de uma vez
   (atualmente já está em 0.1 = 10× reduzido, mas pode ser que esteja
   *baixo demais* causando interpenetração que o solver precisa corrigir
   iterativamente).
5. Para FSI one-way puro: trocar `solidContact` por `solidTraction` zero
   no `on_mestrado`/`oa_mestrado` (ou seja, desabilitar o contato
   completamente como sanity check do FSI).

## O que NÃO está sendo simplificado por enquanto

Você optou por manter:
- Todas as 5 zonas de material (on, ons, fat_below, fat_above, oa_wall).
- Contato OA↔ONS habilitado.
- FSI two-way via preCICE (one-way no momento, mas configurável).
- 1 ciclo cardíaco completo (`endTime = 0.87`).

Se mesmo com essas mudanças continuar inviável, vale considerar:
- Rodar **um meio ciclo** (`endTime = 0.435`) só pra debug.
- **Desligar o contato temporariamente** (substituir as BCs `solidContact`
  por `solidTraction` zero) — separa o problema de FSI do problema de
  contato.
