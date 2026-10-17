# TEXT_UPDATES — resultados WP0 (código calibrado)

Gerado por `cases/wp0/generate_text_updates.py`. **Não edita `.tex`.**

## Desvio Q_prod Tabela (2,4) vs equilíbrio calibrado

| Grandeza | Δ (mmHg ou unidade) |
|---|---|
| Pico Friedenwald dinâmico | 0.000526 mmHg |
| IOP sem par @ 2 min | 0.008426 mmHg |

## Resultados atuais vs referência (recalibrada, Q_prod calibrado)

| Seção / grandeza | Referência | Código agora | Arquivo |
|---|---:|---:|---|
| §3.3 pico dinâmico recal. | 32,90 | 32.9023 | wp0_report.py / simulate_wp0_timeline |
| §3.3 queda refluxo recal. | 0,52 | 0.5197 | wp0_report.py reflux_metrics |
| §3.3 pico linear din. | 25,03 | 25.0314 | wp0_report.py |
| Fig.6 aumento linear | +8,13 | 8.1314 | wp0_report.py plot_camada2 |
| Fig.6 aumento recal. | +16,00 | 16.0023 | wp0_report.py plot_camada2 |
| §4.4 Soheilian 2 min | -12.48 | -12.479 | verify_wp0_standards.py |
| §4.4 Soheilian 30 min | -1.32 | -1.319 | verify_wp0_standards.py |
| §4.4 Chang 15 min | -4.77 | -4.772 | verify_wp0_standards.py |
| §4.4 Zaman 5 min | -10.75 | -10.753 | verify_wp0_standards.py |
| §4.4 Zaman 30 min | -1.68 | -1.674 | verify_wp0_standards.py |
| Paracentese profilatica_friedenwald duração (s) | — | 19.588 | goldmann_iop_solver events |
| Paracentese reativa_friedenwald duração (s) | — | 10.507 | goldmann_iop_solver events |
| Paracentese tardia_friedenwald duração (s) | — | 11.333 | goldmann_iop_solver events |

## LoBue (§4.3)

| Métrica | Código |
|---|---:|
| t retorno <4 mmHg (min) | 14.5628 |
| P(600 s)-P0 (mmHg) | 5.7991 |
| Queda pico→10 min (mmHg) | -10.2032 |
| Queda pico→30 min (mmHg) | -14.6906 |
| Queda pico→50 min (mmHg) | -15.6520 |
| Fig.5 fração excesso dissipada @ 10 min | 63.8 % (excesso 16.0023 mmHg) |
| Fig.5 fração excesso dissipada @ 50 min | 97.8 % |

## τ (§4.2 / §4.1)

| Espécie / teste | Valor | Origem |
|---|---:|---|
| Coelho τ (6 casas) | 5.757715 min | 1/(C_out*K) with K=0.668 literal (wp0.tex eq. casca fina), C_out=0.26 Tabela 3 |

## Changelog código

- `goldmann_iop_solver.py`: Q_prod calibrado; paracentese por evento; LoBue expandido
- `verify_ruffini.py`: teste §4.1
- `wp1_octant_ur_rms.py`: RMS u_r (B12)

