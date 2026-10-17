Implemente o item 4.4 do WP4 do plano de tese: validacao teorica contra
o zero observado, construida sobre o 4.3 (cases/wp4/h6_teorico.py) e o
4.1 (cases/wp4/opp_perfusion.py, opp_crit_efetivo).

CONTEXTO DO REPO:
- cases/wp4/h6_teorico.py (seu 4.3) ja tem dose_fechada_H6(K, dV, C,
  dPth) em termos primitivos.
- cases/wp4/opp_perfusion.py (seu 4.1) ja tem opp_crit_efetivo(OPP_crit_ref, phi_vasc).
- Nao modifique nenhum arquivo existente. Crie arquivos novos em
  cases/wp4/.

OBJETIVO (citacao do plano): "mostrar que o modelo reproduz corretamente
a ausencia de deficit perfusional relatada na literatura para injecao
unica, e delimitar a regiao parametrica onde essa previsao deixaria de
valer." Etapa INTEIRAMENTE COMPUTACIONAL (literatura publicada vs
simulacao 0D) -- sem dado proprio, sem precisar rodar o solver 0D
concreto (tudo em termos de dPth/K/dV primitivos, igual ao 4.3).

DADOS DA LITERATURA (documentar como constantes citadas, nao magic
numbers soltos):
- OCT-A 2026 (n=54): pico de IOP pos-IVI 14->31 mmHg, MOPP~31 mmHg
  RELATADO DIRETAMENTE pelo estudo durante o evento (nao recalcule esse
  MOPP a partir de MAP populacional generica -- o estudo tem seu proprio
  MAP de coorte que voce nao tem acesso). Resultado: SEM deficit de
  perfusao mensuravel.
- Damasceno et al. 2022: CRAO transitoria pos-IVI em 0.44% das injecoes
  (18/4069); destes, 66.6% tinham obstrucao carotidea >=70%.
- OCT ultra-precoce (PMC13307848): afinamento retiniano de 25% aos 15
  min pos-IVI, resolvido em 48h, atribuido a compressao mecanica (NAO
  isquemia).

CRIE um novo arquivo em cases/wp4/validacao_zero_observado.py com:

1. K_implicito_do_pico_observado(iop_basal=14.0, iop_pico=31.0, dV=50.0) -> float
   - K = (pico-basal)/dV -- NAO e K medido independentemente, e uma
     leitura do proprio pico relatado. Documente isso no docstring.

2. tabela_consistencia_zero_oct_a(OPP_crit_range, MOPP_min_observado=31.0) -> dict
   - para cada OPP_crit candidato, diz se o modelo prediz "zero"
     (OPP_crit <= MOPP_min_observado) ou "deficit>0" (OPP_crit >
     MOPP_min_observado)
   - responda explicitamente: o limiar cronico usualmente citado (~50
     mmHg) e consistente com o zero observado? (resposta esperada: NAO
     -- o limiar efetivo para eventos transitorios, se existir, tem que
     ser <=31 mmHg)

3. dPth_com_reserva_vascular(dPth_basal, OPP_crit_ref, phi_vasc) -> float
   - dPth(phi_vasc) = dPth_basal - OPP_crit_ref*(phi_vasc-1)
   - consequencia direta de OPP_crit_efetivo=OPP_crit_ref*phi_vasc (4.1)
     dentro de dPth = mopp_factor*MAP - P0 - OPP_crit_efetivo
   - ValueError se phi_vasc<1

4. subgrupo_risco_damasceno(K_tipico, K_alto, dV, C_out, dPth_basal,
   OPP_crit_ref, phi_vasc_risco) -> dict
   - compara paciente TIPICO (K_tipico, phi_vasc=1) vs subgrupo de risco
     (K_alto, phi_vasc_risco), no MESMO cenario basal
   - usa dose_fechada_H6 do seu 4.3
   - se dPth_risco (ou dPth_tipico) <= 0, marque status como "fora de
     dominio"/"regime cronico" (nao NaN, nao ValueError -- isso E um
     resultado esperado quando phi_vasc e alto o bastante)
   - cenario ilustrativo esperado (documente no teste): K_tipico=0.34,
     K_alto=1.0, dV=50, C=0.28, dPth_basal=20, OPP_crit_ref=25,
     phi_vasc_risco=1.3 -> tipico da I=0, risco da I=72.0 mmHg.min

5. controle_negativo_afinamento_mecanico() -> dict
   - NAO calcula nada -- documenta os fatos (25%, 15min, 48h,
     PMC13307848) e por que o modelo NAO PODE atribuir isso a isquemia
     (o modelo so tem variaveis de pressao de perfusao ao longo do
     tempo, nao espessura estrutural; a escala de tempo de resolucao,
     48h, e incompativel com um processo hemodinamico agudo)
   - retorne dict com compativel_com_dose_isquemica_do_modelo=False e
     um campo "motivo" explicando

6. Testes em cases/wp4/test_validacao_zero_observado.py (pytest):
   - K implicito bate com (31-14)/50=0.34
   - tabela de consistencia: veredito correto incluindo a FRONTEIRA
     (OPP_crit==MOPP_min_observado ainda conta como "zero")
   - dPth_com_reserva_vascular: identidade em phi_vasc=1, diminui com
     phi_vasc maior, ValueError se phi_vasc<1
   - subgrupo_risco_damasceno: tipico da I=0, risco da I>0, no MESMO
     cenario basal (o teste central deste item)
   - subgrupo_risco_damasceno marca "regime cronico" (nao quebra) quando
     phi_vasc e alto o bastante para dPth_risco<=0
   - estrutura e valores do controle negativo conferem com os numeros do
     plano (25%, 15min, 48h)

7. Atualize cases/wp4/README.md (ou crie uma secao 4.4) com a tabela de
   consistencia e o resultado do subgrupo de risco.

Ao final, rode os testes e me mostre o resultado, incluindo a tabela de
consistencia do OCT-A e a comparacao tipico-vs-risco de Damasceno.
