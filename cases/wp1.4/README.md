# WP1.4 — piloto de biometria (14 casos)

Varredura R×t em `data/biometry_14.csv` (proxy esférico octante; elipsoide 1/4 pendente).

## Piloto atual (pós-fechamento WP1.2)

- **Materiais**: Ogden N=1 e Yeoh-2, ambos calibrados em **Friedenwald**
  (`wp1.2/output_literature_p50_v2/friedenwald_{ogden,yeoh}/fit_results.json`).
- **Carga**: P₀→**50** mmHg (não 80).
- **Saída**: `output_pilot_biometry_p50/RESULTS.md` — V_max Ogden vs Yeoh por caso.

```bash
./Allrun
# ou
python3 scripts/run_pilot_biometry.py --ne 8 --out output_pilot_biometry_p50
```

## Legado (22/set, desatualizado)

`output_pilot_yeoh/` — só Yeoh, params E3 (C10≈4.36), P_final=80. Mantido como histórico.
