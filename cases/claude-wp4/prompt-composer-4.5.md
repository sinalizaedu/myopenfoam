Implemente o item 4.5 do WP4 do plano de tese: dose isquemica acumulada
ao longo de um regime terapeutico de injecoes repetidas (contribuicao
original -- nao existia em nenhum item anterior).

CONTEXTO DO REPO:
- Nao depende diretamente de nenhum modulo anterior do WP4 (e
  autocontido em termos de I_j por evento, que o chamador fornece --
  pode vir de dose_fechada_H6 do 4.3, de dose_isquemica_da_cadeia do
  4.2, ou de qualquer outra fonte).
- Nao modifique nenhum arquivo existente. Crie arquivos novos em
  cases/wp4/.

FORMULA (Secao 4.5 do plano):

    I_cum(N) = sum_{j=1..N} I_j * w(t_j - t_{j-1})

Dois limites de w(dt), AMBOS devem ser implementados -- nunca reporte
so um:
- Acumulacao perfeita: w=1 sempre -> I_cum = N*I (K constante).
- Recuperacao parcial: inspirado no modelo SF do rato
  (SF = 1 - b*(1-e^{-a*t})), reinterpretado como a FRACAO DE DANO QUE
  PERSISTE apos um intervalo dt:

      w(dt) = (1-b) + b*exp(-a*dt)

  dt>>1/a -> w->(1-b) (recuperacao quase completa se b=1); dt curto ->
  w->1 (quase todo dano acumula). Documente que a e b NAO tem
  calibracao direta na literatura -- sao parametros de sensibilidade,
  como phi_vasc (4.1) e OPP_crit (4.2/4.3).

Regimes terapeuticos a simular (tabela do plano, N em 2 anos):
| Regime | N (2 anos) | Intervalo tipico |
|---|---|---|
| Mensal fixo | 24 | 4 semanas |
| Treat-and-extend | ~12 | 8-12 semanas (use a media, 10) |
| Brolucizumabe | ~8 | 12 semanas |
| Faricimabe | ~6 | 16 semanas |

CRIE um novo arquivo em cases/wp4/dose_cumulativa.py com:

1. peso_geral(dt_min, a_per_min=None, b=1.0) -> float
   - a_per_min=None -> atalho para acumulacao perfeita (retorna 1.0
     sempre)
   - caso contrario: (1-b) + b*exp(-a*dt_min)
   - ValueError se a_per_min<=0 ou b fora de [0,1]

2. dose_cumulativa(I_por_evento: list[float], intervalos_min: list[float],
   a_per_min=None, b=1.0) -> dict
   - I_por_evento tem N elementos, intervalos_min tem N-1 (um entre cada
     par de eventos consecutivos) -- ValueError se os tamanhos nao
     baterem
   - peso do PRIMEIRO evento e SEMPRE 1.0 (nao ha intervalo anterior nem
     dano previo)
   - retorna dict com I_cum_mmHg_min, pesos (lista tamanho N), e
     contribuicoes_mmHg_min (I_j*peso_j, para auditoria)

3. regime_terapeutico(N, intervalo_semanas, I_por_evento_mmHg_min,
   a_per_min=None, b=1.0) -> dict
   - caso simples: N injecoes igualmente espacadas, mesmo I por evento
     (K constante) -- monta a lista/intervalos e chama dose_cumulativa()

4. comparar_regimes(I_por_evento_mmHg_min, a_per_min, b=1.0, regimes=None) -> dict
   - regimes padrao = os 4 da tabela acima (dict interno constante,
     N_2anos + intervalo_semanas por regime)
   - para cada regime, calcula I_cum sob os DOIS limites (perfeita E
     parcial) -- retorne ambos, nunca um so

5. Escolha (e documente como ILUSTRATIVA/nao calibrada) uma meia-vida de
   recuperacao de referencia para os exemplos/testes -- sugestao: 4
   semanas (mesma ordem de grandeza do intervalo terapeutico mais
   curto), a = ln(2)/(4 semanas em minutos).

6. Testes em cases/wp4/test_dose_cumulativa.py (pytest):
   - peso_geral: w=1 sempre com a=None; w(0)=1; w(infinito)->(1-b);
     monotonico decrescente em dt; ValueError para a<=0 ou b fora de
     [0,1]
   - dose_cumulativa: ValueError se tamanhos nao batem ou lista vazia;
     acumulacao perfeita com K constante = EXATAMENTE N*I; um evento so
     = o proprio I; recuperacao parcial sempre <= perfeita (para a>0);
     intervalo->infinito tende a contar so o primeiro evento;
     intervalo->0 tende a acumulacao perfeita
   - regime_terapeutico consistente com dose_cumulativa montado na mao
   - comparar_regimes: ordem preservada nos DOIS limites (mensal_fixo >
     treat_and_extend > brolucizumabe > faricimabe em I_cum, tanto
     perfeita quanto parcial, com a meia-vida ilustrativa escolhida);
     limite perfeito bate com N*I exatamente para cada regime
   - checagem de definicao: com a = ln(2)/(periodo_de_referencia),
     w(periodo_de_referencia) deve ser EXATAMENTE 0.5 (definicao de
     meia-vida)

7. Atualize cases/wp4/README.md (ou crie uma secao 4.5) com a tabela dos
   4 regimes (I_cum perfeita e parcial lado a lado) e uma tabela de
   sensibilidade a meia-vida de recuperacao (2, 4, 8, 12 semanas, regime
   mensal_fixo).

Ao final, rode os testes e me mostre a tabela dos 4 regimes e a tabela
de sensibilidade a meia-vida.
