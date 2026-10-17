# WP1.4 sweep_full — notas de modelagem

Pipeline oficial em `cases/wp1.4/sweep_full/`. Referência read-only: `cases/claude-wp1.4-sweep/`.

## Geometria esférica (octante, NLGEOM)

- **Comprimento axial** `AL`: raio base da casca `R_base = AL/2` (mm).
- **Espessura variável** `t(θ)`: colatitude θ medida a partir do eixo +Z (polo da malha com θ→θ_min ≈ polo posterior). Transição **cosseno** entre `t_posterior_mm` (θ→θ_min) e `t_equatorial_mm` (θ→90°). Implementação FE: `ne` faixas de ELSET (`T_BAND_*`), cada uma com espessura na colatitude central da faixa.
- **ACD** e **estado do cristalino**: deslocam o raio de superfície média usado na malha (mm), mantendo AL como entrada LHS:
  - `ΔR_acd = −0,11 × (ACD − 3,25)` — câmara anterior mais profunda → menor raio efetivo do segmento posterior modelado.
  - `ΔR_lens`: fácico 0; pseudofácico −0,22; afácico +0,35 mm.
  - `R = R_base + ΔR_acd + ΔR_lens`.
- **Elipsoide prolato**: não implementado nesta rodada.

## Material

- Ogden N=1; `mu1`, `alpha1` da amostra LHS (fatores × nominal Friedenwald WP1.2).
- `D1` amarrado a `mu1` via `d1_from_ogden_mu1` (mesmo convenção wp1.2).
- **Sem MULF** (pré-tensionamento WP1.3).

## Vitrectomia

- Não há cavidade vítrea acoplada (sem FSI). Após extração da curva P–V, **`dV_uL ← dV_uL × 1,085`** se vitrectomia = sim (BSS menos viscoso → maior incremento de volume aparente para mesma pressão). Documentado como **proxy de complacência**; substituir por FSI ou volume efetivo no WP1.5+.

## Extração P–V

- `extract_pv` (wp1.2): `P0 = 16,9` mmHg, 16 passos até 50 mmHg.
- Malha reporta `t_mean_mm` para mapeamento FRD→midsurface.

## Parâmetros ignorados

Nenhum dos 8 inputs LHS é silenciosamente descartado; vitrectomia entra via escala pós-FE (ver acima).

## Sensibilidade OAT (nominal)

Teste one-at-a-time em `output_sensitivity/`: **α₁** com fatores 0,5 e 1,5 altera `V_max` em **&lt;1%** em relação ao nominal (Ogden N=1, octante, P0→50 mmHg). O parâmetro **entra no material FE**; o efeito é pequeno nesta configuração, não zero. Nos demais inputs, |ΔV_max| ≫ 1% nos extremos da faixa.
