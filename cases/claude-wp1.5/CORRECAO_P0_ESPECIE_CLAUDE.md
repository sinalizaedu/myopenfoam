# Correção — P0 (basal) por espécie no WP1.5

## O bug

`cases/claude-wp1.5/scripts/run_pilot_species_claude.py`, e os módulos que
ele chama (`ogden_forward_run.py` local, e `cases/wp1.2/scripts/yeoh_forward_run.py`
do Composer), usam **`P0_MMHG = 16.9` fixo** — hardcoded dentro do próprio
`ogden_forward_run.py`, não vindo de fora — para **as duas espécies**:
humano e coelho.

Esse P0 entra em dois lugares mecanicamente importantes:

1. **Na malha de referência**: a geometria medida do coelho (R=7,6 mm,
   t=0,33 mm) é tratada como o estado *sem tensão* logo no primeiro passo
   da rampa de pressão (que começa em 16,9 mmHg). Fisiologicamente, o
   coelho anestesiado está em equilíbrio a **26,7 mmHg**, não 16,9 — essa
   geometria medida corresponde (aproximadamente) ao estado tensionado a
   26,7 mmHg, não a 16,9.
2. **Na janela de pressão aplicada**: a rampa vai de 16,9 a 50 mmHg para
   as duas espécies. Para o coelho isso não cobre a faixa fisiológica
   relevante em torno do seu próprio basal.

## Por que isso importa (achado desta sessão)

O basal correto de cada espécie vem do equilíbrio de Goldmann com os
parâmetros de vazão ancorados na literatura — os MESMOS já usados no
relatório WP0 (LaTeX, seção "Produção trabecular e uveoescleral") e
reconciliados no WP4.2 (`cases/claude-wp4/claude_dose_isquemica.py`,
`derivar_P0_equilibrio()`):

| espécie              | Q_prod (µL/min) | C_out (µL/min/mmHg) | Pev (mmHg) | frac_uv | **P0 (mmHg)** |
|---|---:|---:|---:|---:|---:|
| humano               | 2,4  (Goel et al. 2010)        | 0,28 | 10,0 | 0,20 | **16,9** |
| coelho anestesiado   | 3,06 (Kiel 2011/2015; Fourman & Garner 1989) | 0,26 | 15,5 | 0,05 | **26,7** |

O script original usa 16,9 para o coelho — um erro de ~9,8 mmHg no
basal, na direção que **infla artificialmente** a rigidez relativa medida
do coelho (ver diagnóstico abaixo).

## Diagnóstico: dá para corrigir sem rodar CalculiX de novo?

**Não.** Testado diretamente (`scripts/diag_reprocess_p0_claude.py`,
reprocessando os `.frd`/`.inp` já existentes em
`output_pilot_species_claude/ccx_runs/` com `extract_pv(..., p0_mmhg=26.7)`
em vez de rodar CCX de novo):

```
rabbit_ogden: K_eff com p0=16.9 (original) = 1.2318 mmHg/uL
              K_eff só trocando p0_mmhg->26.7 (sem rerun) = -4.6034 mmHg/uL  (sem sentido físico)
rabbit_yeoh:  K_eff com p0=16.9 (original) = 1.6119 mmHg/uL
              K_eff só trocando p0_mmhg->26.7 (sem rerun) = -6.0240 mmHg/uL  (sem sentido físico)
```

O motivo: a rampa de pressão gravada no `.inp` do coelho é 16,9→50 mmHg
(9 passos de ~2,07 mmHg); nenhum desses passos cai perto de 26,7 mmHg, e
o volume de referência (V=0) cai de volta no primeiro passo calculado
(~16,9-19,0 mmHg), que **não é o volume físico do coelho em 26,7 mmHg** —
esse volume nunca foi calculado, porque a malha nunca foi assumida sem
tensão nesse ponto. **É preciso rodar o CalculiX de novo com a rampa
certa para o coelho.**　Não posso executar CalculiX/Docker neste ambiente
(restrição do projeto) — só escrever o script corrigido e dar o comando
exato para você rodar.

## A correção

Criados (todos novos, nenhum arquivo existente foi editado):

- `scripts/ogden_forward_run_v2_claude.py` — igual a
  `ogden_forward_run.py`, mas `p0_mmhg` e `p_final_mmhg` vêm de fora
  (parâmetro), não fixos no módulo.
- `scripts/yeoh_forward_run_v2_claude.py` — mesma ideia para Yeoh
  (reusa `load_yeoh_params()` do Composer, que não depende de P0, mas
  não reusa o `p_targets()`/`yeoh_forward_run.py` originais, que fixam
  P0=16,9).
- `scripts/run_pilot_species_corrected_claude.py` — usa P0 por espécie
  (16,9 humano / 26,7 coelho) e a **mesma amplitude ΔP=33,1 mmHg** a
  partir do basal de cada espécie (humano 16,9→50,0; coelho
  26,7→**59,8**), para não confundir "diferença de complacência real"
  com "diferença por causa da janela de pressão absoluta ser diferente
  relativa ao basal de cada espécie". Essa escolha de ΔP igual é uma
  decisão de desenho — a alternativa seria usar a mesma pressão
  *absoluta* final (50 mmHg para as duas), o que dá ΔP menor para o
  coelho (23,3 mmHg) e é fisiologicamente menos comparável. Se preferir
  a alternativa, é só mudar `DELTA_P_MMHG` → usar `p_final` fixo em vez
  de derivado do P0.
- `Allrun_corrected` — roda o script acima dentro do container FSI.

**O que NÃO foi corrigido aqui** (já estava flagado no
`WP1_5_CLOSURE_REPORT_CLAUDE.md` original, é um problema separado): o
material (fit Ogden/Yeoh do Friedenwald) continua calibrado em dados
**humanos**, aplicado à geometria do coelho sem recalibração. A conclusão
de "coelho é ~4,1× menos complacente" do fechamento original pode ter
sido, em parte, coincidência com a razão geométrica pura
`(R_humano/R_coelho)^4 × (t_coelho/t_humano) = 4,102` — precisa ser
reavaliada depois que os números corrigidos de P0 saírem, e mais ainda
se/quando o material for recalibrado para coelho.

## Como rodar

```bash
docker compose run --rm fsi bash -lc "cd claude-wp1.5 && ./Allrun_corrected"
```

Saída em `cases/claude-wp1.5/output_pilot_species_corrected_claude/`:
`pilot_species_corrected_results.json` e `RESULTS_CORRIGIDO_CLAUDE.md`
(com os valores novos lado a lado com os valores originais com bug, para
comparação direta).

## Testes

Ainda não escrevi testes automatizados para os módulos `_v2_claude` porque
eles chamam CalculiX de verdade (não dá para rodar aqui). O que valida
sem CCX:
- `scripts/diag_reprocess_p0_claude.py` (já rodei — ver diagnóstico acima)
  confirma que o bug é real e que a correção exige um novo run.
- Depois que você rodar `Allrun_corrected`, o ideal é conferir manualmente
  que `RESULTS_CORRIGIDO_CLAUDE.md` bate com a expectativa: coelho deve
  continuar mais rígido que humano (razão geométrica ainda domina), mas o
  K_eff absoluto do coelho deve mudar em relação ao valor com bug — e o
  quanto muda é justamente o que este script existe para medir.
