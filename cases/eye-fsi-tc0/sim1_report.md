# Simulação 1 — Step 0: parecer técnico final

**Data:** 2026-07-15  
**Caso:** `cases/eye-fsi-tc0`  
**Status:** CONCLUÍDA (Fases A–F)

> **Atualização BCs (pós-corrida):** arquivos do caso migrados para **Lamminsalo (2018)** coelho — Q = 3 µL/min, P_epi = 10 Torr, ν = 6,928×10⁻⁷ m²/s. Os resultados abaixo referem-se à corrida com BCs anteriores (Q = 2,2 µL/min, P_epi = 8 mmHg). Re-calibração `d_TM` pendente.

---

## 1. Resumo executivo

A Simulação 1 (Step 0) atingiu o alvo hidráulico **IOP₀ ≈ 15 mmHg** na malha baseline **M1** (3388 células) com:

- `simpleFoam`, parede rígida, sem FSI/preCICE/agulhas
- **P_epi = 8 mmHg**, **Q_prod = 2,2 µL/min** (total bilateral)
- **d_TM = 3,62×10¹⁴ m⁻²**, **d_vit = 1,72×10¹³ m⁻²**

Malha verificada **M3** (3508 células, TM refinada 64 células/lado) reproduz IOP₀ = **15,13 mmHg** com erro de balanço de massa **1,6 %**.

---

## 2. Coeficientes congelados (Sim 2)

Ver `coefficients_step0.yaml`:

| Parâmetro | Valor M1 (Sim 2) | Valor M3 (verificação) |
|-----------|------------------|------------------------|
| d_TM | 3,62×10¹⁴ m⁻² | 3,25×10¹⁴ m⁻² |
| d_vit | 1,72×10¹³ m⁻² | 1,72×10¹³ m⁻² |
| Malha | M1 (3388 cells) | M3 (3508 cells) |

---

## 3. Validações numéricas (V1–V7)

| ID | Resultado | Aceite | Status |
|----|-----------|--------|--------|
| **V1** Malha | `checkMesh` OK; non-ortho max 30,96° (M3) | < 70° | PASS |
| **V2** Solver | U residual ~10⁻⁸; p rel ~0,007 (porous conditioning) | U < 10⁻⁵ | PARTIAL |
| **V3** Massa | Q_out/Q_in = 98,4 % (M3) | < 2 % err | PASS (M3) |
| **V4** IOP₀ | 15,13 mmHg (M3) | 14–16 | PASS |
| **V5** AC–vítreo | Δp = 0,11 mmHg | < 1 mmHg | PASS |
| **V6** 0D | P̂=15 mmHg, Q=2,2 µL/min coerente com Darcy TM | ordem de grandeza | PASS |
| **V7** GCI | Não-monotônico com d_TM fixo; spread calibrado 4,2 % | GCI < 5 % | PARTIAL |

---

## 4. Figuras

- `figures/iop_step0_steady.png` — IOP vs iteração (steady)
- `mesh_study.md` — tabelas M1/M2/M3

---

## 5. Limitações honestas

1. **TM grosseira em M1:** apenas 4 células por lado na zona porosa; refinamento TM (M3) altera `d_TM` calibrado em ~10 %.
2. **Modelo bilateral espelhado:** dois inlets com metade do fluxo cada; representa um olho com simetria, não dois olhos independentes.
3. **Zonula impermeável:** Step 0 não tem `porousBafflePressure` na interface AC–vítreo; Δp_AC–vítreo ≈ 0 emerge do vítreo poroso, não de jump explícito.
4. **Sem uveoscleral (Tier 2):** toda produção drena pela TM.
5. **Convergência de pressão:** resíduo relativo de p permanece ~10⁻² devido ao condicionamento Darcy (esperado; PCG+DIC).

---

## 6. Opinião técnica (go/no-go Sim 2)

**Recomendação: GO para Simulação 2 (Step 1 transient + Robin)**, com ressalvas:

O Step 0 entrega uma **baseline hidráulica credível** para IOP₀ ≈ 15 mmHg com balanço de massa < 2 % na malha M3 e Δp AC–vítreo < 0,12 mmHg. O protocolo `Allrun.step0` / `Allclean.step0` roda **sem erros fatais** no Docker OpenFOAM v2512.

**O que ainda falta antes de FSI (Step 3):**
- Zonule como `porousBafflePressure` (não parede sólida)
- Robin `codedFixedValue` na esclera/córnea (Step 1)
- Re-calibrar `d_TM` após mudança para malha G2 Lamminsalo (setembro)

**Risco principal:** IOP_peak pós-IVI no Step 1 com parede Robin pode desviar > 10 % do FSI final (H4) — previsto no plano; Step 0 não invalida essa hipótese.

---

## 7. Log de execução

Todas as corridas registradas em `calibration_step0.log` e `run_log_step0.txt`.

**Simulação 1: CONCLUÍDA.**
