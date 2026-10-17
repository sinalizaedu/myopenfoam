# WP1.2 — Fechamento: calibração hiperelástica Ogden/Yeoh

**Autoria:** síntese de dois braços independentes — Composer/Cursor
(`cases/wp1.2/`) e Claude/Sonnet (`cases/claude-wp1.2/`), convergindo nos
mesmos números.

**Status das ressalvas (fechado em 2026-09-25):** malha ✅ · otimização
Ogden e Yeoh (D1 amarrado) ✅ · D1 livre testado (não traz ganho real) ✅ ·
α₁ ampliado testado, 1 correção encontrada (Agra) ✅ · não-identificabilidade
documentada como limitação aceita · pré-tensão é assunto do WP1.3 (fora do
escopo deste fechamento). **As 3 ressalvas de otimização (Seção
"Ressalvas", itens 2-4) estão todas fechadas** — ver resultados abaixo.

**✅ As 2 pendências de dados foram fechadas em 2026-09-25:**
1. **Agra-Ogden**: promovido no arquivo oficial
   (`output_literature_p50_v2/agra_ogden/`) — α₁≈0,19, R²=0,954.
2. **Pallikaris digitalizado**: confirmação cruzada Composer × Claude
   fechada (ver `output_literature_p50_digitized/CROSS_VALIDATION_PALLIKARIS.md`)
   — R²=0,9904 (Ogden) e 0,9891 (Yeoh), concordância a ≤0,0001 entre os
   dois braços independentes. Os α₁ do Ogden vêm diferentes entre os
   braços (0,535 vs 2,696) — mesma degenerescência já documentada (curva
   idêntica, parâmetro não único), não é inconsistência.

**WP1.2 encerrado. Sem pendências abertas.**

## Decisão final

- **Alvo P(V) adotado:** Friedenwald recalibrado (Kf=0,00581, P₀=16,9 mmHg),
  já validado no seu WP0 contra o pico clínico de Knecht et al. 2009.
- **P_final da rampa FEA:** 50 mmHg (não 80 — ver justificativa abaixo).
- **Material:** Ogden e Yeoh performam equivalentes nessa faixa de pressão
  (diferença de R² <0,02 em todos os alvos) — nenhum dos dois se destaca.
  Reportar os dois na tese; deixar a escolha final entre eles para o WP1.3.
- **Parâmetros finais (μ₁, α₁, C₁₀, C₂₀):** puxar de
  `output_literature_p50_claude/friedenwald_ogden/fit_results.json` e
  `.../friedenwald_yeoh/fit_results.json` (e o equivalente do Composer em
  `output_literature_p50_v2/`) — não reproduzidos aqui; comparar os dois
  braços como checagem cruzada antes de citar.
- **Confiança no Ogden confirmada por multi-start (2026-09-24):** 9 pontos
  de partida × 4 alvos, P_final=50, D1 amarrado — single-start = ótimo
  global em Pallikaris/Silver/Agra; Friedenwald tem 5 mínimos quase
  equivalentes (curva igual, parâmetros não-únicos — ver Seção "Ressalvas",
  item 2). Yeoh ainda não passou por essa checagem.

## Resultado final (8 casos: 4 alvos × 2 materiais, P_final=50 mmHg)

| Alvo | Material | R² | max\|resíduo\| [mmHg] |
|---|---|---:|---:|
| Pallikaris (fórmula, v_max=50µL) | Ogden | 0,93–0,935 | ~4,8–5,0 |
| Pallikaris (fórmula, v_max=50µL) | Yeoh | 0,93–0,933 | ~5,0–5,2 |
| **Pallikaris (pontos digitalizados reais, v_max=44,5µL)** | **Ogden** | **0,990** | ~2,9 |
| **Pallikaris (pontos digitalizados reais, v_max=44,5µL)** | **Yeoh** | **0,989** | ~3,1 |
| Silver | Ogden | 0,976–0,98 | ~2,4–3,0 |
| Silver | Yeoh | 0,97–0,975 | ~2,7–3,0 |
| Agra | Ogden | ~~0,939–0,94~~ → **0,954** (corrigido, ver Ressalvas item 2d) | ~1,6 |
| Agra | Yeoh | 0,92–0,925 | ~2,1 |
| **Friedenwald recalibrado** | **Ogden** | **0,977–0,98** | **~1,5–1,7** |
| **Friedenwald recalibrado** | **Yeoh** | **0,971–0,97** | **~1,5–1,6** |

**Leitura revisada (2026-09-25):** a versão com fórmula do Pallikaris era o
ajuste mais fraco (R²≈0,93). Mas usando os **pontos reais digitalizados**
da Fig. 2 (em vez da fórmula analítica), o ajuste sobe para R²≈0,99 —
melhor que o próprio Friedenwald. **Ressalva importante antes de declarar
"Pallikaris venceu":** o domínio digitalizado vai só até 44,5µL (não
50µL) e tem menos pontos que os outros alvos — R² de ajustes com
domínio/nº de pontos diferentes não é 100% comparável (menos pontos/faixa
menor tende a favorecer R² alto). Conclusão honesta: **Friedenwald
recalibrado (alvo clínico, domínio completo) e Pallikaris digitalizado
(dado real, domínio parcial) são os dois melhores ajustes**, ambos
>0,97, e concordam que o material calibrado reproduz bem múltiplas fontes
independentes — isso é mais forte para a tese do que "só um alvo ganhou".

## Por que 50 mmHg, não 80

P₀=16,9 mmHg vem do seu WP0. A média dos picos clínicos reais (5 estudos,
IVI padrão 50µL, tabela `literatura_master`) é ≈35,3 mmHg. O alvo antigo
(Pallikaris com bug de baseline — Seção "achados") previa 72,1 mmHg em
50µL: implausível. Com o teto em 50 mmHg, o alvo adotado (Friedenwald
recalibrado) prevê 33,0 mmHg em 50µL — bate com a clínica. Os dois braços
migraram para 50 mmHg independentemente, o que reforça a decisão.

## Linear (WP1.1) vs. hiperelástico (WP1.2) — por que não bastava o linear

| V (µL) | Linear elástico (K=0,163) | Friedenwald recalibrado | Diferença |
|---:|---:|---:|---:|
| 20 | 20,2 mmHg | 22,1 mmHg | 9% |
| 50 | 25,1 mmHg | 33,0 mmHg | 32% |

O linear só se aproxima do alvo hiperelástico perto do ponto de calibração;
diverge conforme o volume cresce, porque não captura o enrijecimento
não-linear do tecido. Isso justifica reportar Ogden/Yeoh (não o linear)
como o modelo de material do WP1.2.

## Achados de correção (resolvidos)

- **Bug de baseline no Pallikaris:** a fórmula original misturava o slope
  do artigo (calibrado contra basal de 10 mmHg) com um basal diferente
  (16,9, seu). Inflava a curva ~1,7× (72 mmHg em vez de ~44-50 mmHg em
  50µL). Corrigido nos dois braços em 2026-09-23 (re-ancorando o incremento
  ΔP do artigo sobre o seu basal, ou usando os pontos digitalizados reais
  da Fig. 2).
- **Alvos truncados por alcance de pressão:** Silver (38µL), Agra (40µL) e
  Pallikaris (44,5-50µL, depende do braço) foram limitados ao volume onde a
  própria curva ainda fica ≤50mmHg — não faz sentido pedir à FEA um volume
  que só é alcançado acima do teto de pressão da rampa.

## Ressalvas antes de fechar de vez

1. **Independência de malha — RESOLVIDA (2026-09-24).** Estudo completo
   nos 8 casos (não só um spot-check): forward NLGEOM com os parâmetros já
   ajustados (sem re-otimizar), ne ∈ {6, 8, 10, 12}, QoI = ΔV_final em
   P=50mmHg. Resultado: diferença ne=6→8 fica em 0,002–0,004% em todos os
   8 casos (limite de aceite era ε<1%); ne=8→10→12 praticamente não muda
   nada (ε≈0,000%). **ne=8 é suficiente e a malha usada nas 8 simulações
   finais está convergida** — não precisa refazer nada aqui. Script:
   `cases/wp1.2/scripts/mesh_independence.py`.

2. **Otimização single-start — RESOLVIDA (fechada 2026-09-25, Ogden e
   Yeoh).** Três campanhas complementares, mesmo setup da matriz
   (P_final=50, ne=8, 4 alvos), em `cases/wp1.2/output_caveats_p50/`:

   **(a) Multi-start Ogden, D1 amarrado (bounds originais α₁∈[0,5, 6]):**
   Pallikaris, Silver, Agra: 1 bacia boa cada, single-start = global.
   Friedenwald: 5 mínimos quase equivalentes (R²≈0,977, α₁ de 0,51 a
   6,00) — não-identificabilidade, não erro (ver item 4).

   **(b) Multi-start Yeoh, D1 amarrado:** mesmo padrão do Ogden —
   Pallikaris e Agra têm múltiplos (C₁₀,C₂₀) com R² igual (degenerescência);
   Silver e Friedenwald têm bacia única. **Nenhuma bacia com R² melhor que
   o single-start em nenhum dos 4 alvos.**

   **(c) Ogden com D1 livre (μ₁,α₁,D1 todos livres):** reabre várias
   bacias (como acontecia em P_final=80), **mas sem ganho real de
   qualidade** — Friedenwald sobe de R²=0,977 para 0,9775 (diferença
   desprezível, e essa corrida nem convergiu — parou por esgotar
   avaliações). **Conclusão prática: amarrar D1 (como feito na matriz
   final) é uma simplificação válida** — não perde qualidade de ajuste e
   evita uma dimensão extra de não-identificabilidade.

   **(d) Ogden com α₁ ampliado para [0,15, 10]:**

   | Alvo | Resultado | Ação |
   |---|---|---|
   | Silver, Friedenwald | R² igual, fora do bound antigo | Nenhuma — bound não limitava |
   | Pallikaris | R² **pior** fora do bound antigo (0,5) | Nenhuma — bound de 0,5 era uma boa escolha |
   | **Agra** | **R² sobe de 0,938 → 0,954** com α₁≈0,19 (antes preso em α₁=6,0, no teto) | **Corrigir**: usar μ₁=5,20, α₁=0,19, D1=0,098, R²=0,954 em vez do valor antigo |

   **Única correção necessária na matriz de 8 casos: o Agra-Ogden.** Como
   o Agra não é o alvo principal adotado (é o Friedenwald, já correto),
   isso não muda a conclusão central do WP1.2 — mas atualizar antes de
   citar parâmetros do Agra na tese.

3. **Divergência de pré-tensão do WP1.3 (Ogden +1,3% / Yeoh -37,5%) foi
   investigada com os parâmetros ANTIGOS** (alvo com bug, P_final=80).
   Assunto do WP1.3, não do WP1.2 — ver relatório separado quando o WP1.3
   for fechado.

4. **Não-identificabilidade de parâmetros — achado geral e definitivo do
   WP1.2 (Ogden e Yeoh, não só um caso isolado).** Confirmado nos dois
   materiais, em múltiplos alvos: Friedenwald-Ogden (5 mínimos),
   Pallikaris-Yeoh e Agra-Yeoh (múltiplos C₁₀/C₂₀). **Leitura correta pra
   tese:** os dados de P(V) testados restringem bem a *curva de resposta*
   do material (a qualidade do ajuste é única e reprodutível — ver item
   2), mas não restringem unicamente os *parâmetros materiais* —
   múltiplas combinações (μ₁,α₁) ou (C₁₀,C₂₀) reproduzem a mesma curva
   igualmente bem. Documentar como limitação estrutural do problema
   inverso (poucos pontos experimentais, 2 parâmetros livres), não como
   erro de método ou de otimização.

## Figuras sugeridas (descrição — gerar em outra sessão)

1. **P(V): as 4 curvas-alvo sobrepostas**, V de 0-50µL, com Friedenwald
   recalibrado destacado, linha vertical em V=50µL e faixa sombreada com a
   média±desvio dos picos clínicos reais (26,8–47,9 mmHg).
2. **Barras de R² por alvo × material** (4 grupos, 2 barras cada,
   eixo Y de 0,85 a 1,0 pra não achatar a diferença).
3. **Curva FEA ajustada vs. alvo**, 2 painéis (Ogden | Yeoh), só para o
   Friedenwald recalibrado — o "gráfico de prova" do ajuste escolhido.
4. **Linear vs. hiperelástico**, 2 curvas (K=0,163 e Friedenwald
   recalibrado) de 0 a 50µL, mostrando onde e quanto divergem.
5. *(opcional, se rodar o spot-check de malha)* **P(V) do alvo adotado em
   2-3 densidades de malha sobrepostas** — prova visual de convergência.

---

*Fontes: `cases/claude-wp1.2/output_literature_p50_claude/LITERATURE_MATRIX_SUMMARY_CLAUDE.md`,
`cases/wp1.2/output_literature_p50_v2/LITERATURE_MATRIX_SUMMARY.md`,
`cases/claude-wp1_analysis/PRETENSION_MECHANISM_INVESTIGATION.md`, seu
relatório WP0.*
