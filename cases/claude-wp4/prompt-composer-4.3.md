Implemente o item 4.3 do WP4 do plano de tese: o resultado teorico H6
(versao corrigida, Secao 1/4.3) e suas tres consequencias, construido
sobre o 4.2 (cases/wp4/dose_isquemica.py, que voce ja fez).

CONTEXTO DO REPO:
- cases/wp4/dose_isquemica.py (seu proprio 4.2) ja tem validacao_fechada_H6(),
  que compara o 𝓘 numerico do solver 0D contra a formula fechada usando
  Protocol/PV concretos.
- Nao modifique nenhum arquivo existente. Crie arquivos novos em
  cases/wp4/.

O QUE 4.3 PEDE (diferente de "validar a formula", que voce ja fez): a
formula fechada reescrita em termos dos PARAMETROS PRIMITIVOS (K, dV,
C_out, dPth), para poder varrer cada um livremente sem rodar o solver 0D
a cada ponto -- e as tres consequencias explicitas do plano:

    I = dV/C - dPth/(C*K) * [1 + ln(K*dV/dPth)]   se K*dV > dPth
    I = 0                                          se K*dV <= dPth
    K_crit = dPth/dV

1. Sem limiar, K cancela -- I -> dV/C e o limite superior assintotico
   (K->infinito).
2. Com limiar, existe K_crit abaixo do qual a dose e EXATAMENTE zero --
   quase binario.
3. C_out escala tudo linearmente -- I(C/2) = 2*I(C) EXATAMENTE, para
   qualquer K (porque tau=1/(C*K) e o unico lugar em que C aparece na
   formula, e multiplica tudo).

ALERTA METODOLOGICO do plano (citacao literal): "todo o resultado
depende do valor de dPth, que e justamente o parametro mais mal
conhecido do modelo... Apresente 𝓘 e K_crit como funcao de dPth, nunca
com um valor fixo." Nenhuma funcao publica deste modulo deve ter dPth
hardcoded -- sempre parametro ou faixa de parametros.

CRIE um novo arquivo em cases/wp4/h6_teorico.py com:

1. dose_fechada_H6(K_mmHg_per_uL, dV_uL, C_out_uL_min_mmHg, dPth_mmHg) -> float
   - a formula acima, em termos primitivos
   - levante ValueError (nao NaN) se dPth_mmHg <= 0 (fora do dominio --
     perfusao basal ja abaixo do limiar mesmo sem injecao)

2. K_crit(dPth_mmHg, dV_uL) -> float
   - K_crit = dPth/dV
   - levante ValueError se dPth<=0 ou dV<=0

3. limite_superior_dV_sobre_C(dV_uL, C_out_uL_min_mmHg) -> float
   - dV/C -- confirme no teste que dose_fechada_H6 satura nesse valor
     para K grande e fica estritamente abaixo para qualquer K finito

4. curva_I_vs_K(K_range, dV, C, dPth) -> dict
   curva_I_vs_dPth(dPth_range, K, dV, C) -> dict  (marca None para dPth<=0,
     nao quebra a varredura inteira por um ponto fora de dominio)
   K_crit_vs_dPth(dPth_range, dV) -> dict  (idem, None para dPth<=0)

5. verificar_escala_linear_C_out(K, dV, dPth, C_ref, fator=0.5) -> dict
   - devolve I_ref, I_teste (C_teste=C_ref*fator), razao_observada
     (I_teste/I_ref) e razao_esperada (1/fator) -- devem bater a 1e-9
     (nao e aproximacao numerica, e a mesma formula fechada avaliada
     duas vezes)
   escala_C_out(K, dV, dPth, C_out_range) -> dict  (tabela para reportar
     ao lado da verificacao)

6. Testes em cases/wp4/test_h6_teorico.py (pytest):
   - K_crit reproduz o exemplo do proprio plano: dPth=15, dV=50 ->
     K_crit=0.30 mmHg/uL
   - dose EXATAMENTE zero abaixo de K_crit (nao so pequena), positiva
     acima, continua na fronteira (sem salto artificial em K=K_crit)
   - saturacao em dV/C para K grande (ex.: K=1e6), e I estritamente
     abaixo do limite para varios K finitos
   - curva_I_vs_K monotonica nao-decrescente
   - curva_I_vs_dPth e K_crit_vs_dPth marcam None corretamente para
     dPth<=0
   - escala linear em C_out EXATA (razao_observada == razao_esperada a
     1e-9), tanto na funcao de verificacao quanto na tabela
     (escala_C_out) usando um fator diferente (ex.: 2x em vez de 1/2x)
   - CONSISTENCIA COM O 4.2: dose_fechada_H6(K, dV, C, dPth) deve dar o
     MESMO resultado que validacao_fechada_H6() (dose_isquemica.py, seu
     4.2) calcula internamente, no mesmo cenario (extraia K, dV, C, dPth
     do dict que validacao_fechada_H6 ja devolve e passe para
     dose_fechada_H6 -- devem bater a 1e-9, sao a mesma formula por dois
     caminhos de codigo)

7. Atualize cases/wp4/README.md (ou crie uma secao 4.3 nele) com a
   verificacao numerica dos tres achados no cenario do proprio plano
   (dPth=15, dV=50, C=0.28): dV/C=178.57 mmHg.min; K_crit=0.30; e a
   tabela I(K) mostrando a transicao em K_crit e a saturacao.

Ao final, rode os testes e me mostre o resultado, incluindo a tabela
I(K) e a verificacao da escala linear em C_out.
