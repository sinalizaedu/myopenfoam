Achado + correção no WP1.5 (piloto de espécie humano/coelho): o P0
(basal fisiológico) do coelho estava errado.

CONTEXTO: `cases/claude-wp1.5/scripts/run_pilot_species_claude.py` e os
módulos que ele chama usam `P0_MMHG = 16.9` (basal HUMANO) fixo para as
DUAS espécies. O basal do coelho anestesiado é **26,7 mmHg**, não 16,9 —
derivado do equilíbrio de Goldmann com parâmetros de vazão ancorados na
literatura (Q_prod=3,06 µL/min, C_out=0,26 µL/min/mmHg, Pev=15,5 mmHg,
frac_uveoscleral=0,05; Kiel et al. 2011/2015, Fourman & Garner 1989),
igual ao que já está no relatório WP0 em LaTeX ("Produção trabecular e
uveoescleral") e reconciliado no WP4.2
(`cases/claude-wp4/claude_dose_isquemica.py::derivar_P0_equilibrio()`).

Isso afeta DOIS pontos mecanicamente relevantes no FEA:
1. A malha medida do coelho (R=7,6mm, t=0,33mm) é tratada como
   "sem tensão" no P0 errado (16,9), não no basal real (26,7).
2. A rampa de pressão aplicada (16,9→50 mmHg) não cobre a faixa
   fisiológica correta do coelho.

VERIFIQUEI (reprocessando os .frd/.inp JÁ EXISTENTES em
`output_pilot_species_claude/ccx_runs/`, sem rodar CalculiX de novo, com
`extract_pv(..., p0_mmhg=26.7)`) que **não dá para corrigir isso só
trocando o parâmetro de pós-processamento**: nenhum passo da rampa
gravada cai perto de 26,7 mmHg, então o volume de referência (V=0) cai
de volta num ponto que não é o volume físico do coelho em 26,7 mmHg —
o K_eff sai negativo (sem sentido físico) quando eu forço isso. É preciso
rodar o CalculiX de novo com a rampa certa.

CRIEI (todos arquivos novos, nada existente foi editado) em
`cases/claude-wp1.5/scripts/`:
- `ogden_forward_run_v2_claude.py` e `yeoh_forward_run_v2_claude.py` —
  mesma lógica dos originais, mas com `p0_mmhg` e `p_final_mmhg`
  parametrizados por fora (os originais fixam P0=16,9 internamente e não
  expõem isso).
- `run_pilot_species_corrected_claude.py` — usa P0=16,9 (humano) / 26,7
  (coelho), e a MESMA amplitude ΔP=33,1 mmHg a partir do basal de cada
  espécie (humano 16,9→50,0; coelho 26,7→**59,8**) — para isolar
  "diferença de complacência real" de "diferença por causa da janela de
  pressão absoluta". Essa escolha de ΔP igual é uma decisão de desenho,
  não a única válida (ver `CORRECAO_P0_ESPECIE_CLAUDE.md` para a
  alternativa de p_final fixo).
- `Allrun_corrected` — roda o script acima no container FSI.
- `CORRECAO_P0_ESPECIE_CLAUDE.md` — documenta tudo isso em detalhe.

NÃO CORRIGIDO (fora do escopo, já flagado no fechamento original): o
material (fit Ogden/Yeoh do Friedenwald) continua calibrado em dados
HUMANOS, aplicado à geometria do coelho sem recalibração. A conclusão de
"coelho é ~4,1× menos complacente" pode ter sido parcialmente coincidência
com a razão geométrica pura (R_h/R_c)^4×(t_c/t_h)=4,102 — precisa ser
reavaliada com os números de P0 corrigidos, e mais ainda se/quando o
material for recalibrado.

PRECISO QUE VOCÊ (rode e valide, já que eu não executo CalculiX aqui):
1. Rode `docker compose run --rm fsi bash -lc "cd claude-wp1.5 && ./Allrun_corrected"`.
2. Confira `output_pilot_species_corrected_claude/RESULTS_CORRIGIDO_CLAUDE.md`
   (tem os valores novos lado a lado com os valores originais com bug).
3. Se os números baterem com o esperado (coelho ainda mais rígido que
   humano, mas K_eff absoluto diferente do valor com bug), atualize a
   conclusão do `WP1_5_CLOSURE_REPORT_CLAUDE.md` para referenciar os
   valores corrigidos e a ressalva sobre a razão geométrica pura.
4. Decida (e documente a decisão) entre ΔP igual vs p_final absoluto
   igual para a janela do coelho — é uma escolha de metodologia, não um
   bug, então cabe a você/à Bruna decidir qual entra na tese.
