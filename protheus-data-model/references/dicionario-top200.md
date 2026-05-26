# Tabelas Mais Usadas do Protheus — Referencia Rapida

> Para detalhes completos (todos os campos), consulte os arquivos individuais em `dicionario/{PREFIXO}/{TABELA}.md`

## Cadastros Base

| Tabela | Descricao | Chave | Campos-chave |
|--------|-----------|-------|-------------|
| SA1 | Clientes | A1_COD+A1_LOJA | A1_NOME, A1_NREDUZ, A1_CGC, A1_PESSOA, A1_END, A1_EST, A1_MUN, A1_CEP, A1_TEL, A1_EMAIL |
| SA2 | Fornecedores | A2_COD+A2_LOJA | A2_NOME, A2_NREDUZ, A2_CGC, A2_PESSOA, A2_END, A2_EST, A2_MUN, A2_CEP, A2_TEL |
| SA3 | Vendedores | A3_COD | A3_NOME, A3_NREDUZ, A3_END, A3_COMIS, A3_TIPO |
| SA4 | Transportadoras | A4_COD | A4_NOME, A4_NREDUZ, A4_CGC, A4_END |
| SA5 | Amarracao Produto x Fornecedor | A5_FORNECE+A5_LOJA+A5_PRODUTO | A5_QUANT, A5_PRECO, A5_LTIME |
| SA6 | Bancos | A6_COD+A6_AGENCIA+A6_NUMCON | A6_NOME, A6_NREDUZ |
| SA7 | Agenda Compromisso | A7_DATA+A7_NUM | A7_DESCRI, A7_TIPO, A7_HORA |
| SB1 | Produtos | B1_COD | B1_DESC, B1_TIPO, B1_UM, B1_LOCPAD, B1_GRUPO, B1_PRV1, B1_CUSTD, B1_PESO, B1_CODBAR, B1_ORIGEM |
| SB2 | Saldos de Estoque | B2_COD+B2_LOCAL | B2_QATU, B2_QRES, B2_QEMP, B2_QPROD, B2_CM1, B2_VATU1 |
| SB5 | Dados Adicionais Produto | B5_COD | B5_CEME, B5_IMPORT, B5_PESO, B5_CODBAR |
| SBZ | Ativo Imobilizado | BZ_COD | BZ_DESC, BZ_DTAQUI, BZ_VAQUIS, BZ_GRUPO |

## Compras

| Tabela | Descricao | Chave | Campos-chave |
|--------|-----------|-------|-------------|
| SC1 | Solicitacao de Compras | C1_NUM+C1_ITEM | C1_PRODUTO, C1_QUANT, C1_EMISSAO, C1_OBS, C1_SOLICIT, C1_LOCAL |
| SC7 | Pedido de Compras | C7_NUM+C7_ITEM | C7_PRODUTO, C7_QUANT, C7_PRECO, C7_TOTAL, C7_FORNECE, C7_LOJA, C7_COND, C7_DATPRF, C7_EMISSAO |
| SC8 | Mapa de Cotacoes | C8_NUM+C8_ITEM | C8_PRODUTO, C8_QUANT, C8_PRECO, C8_FORNECE |

## Faturamento / Vendas

| Tabela | Descricao | Chave | Campos-chave |
|--------|-----------|-------|-------------|
| SC5 | Pedidos de Venda | C5_NUM | C5_CLIENTE, C5_LOJACLI, C5_CONDPAG, C5_EMISSAO, C5_VEND1, C5_TIPO, C5_NOTA, C5_TRANSP |
| SC6 | Itens Pedidos de Venda | C6_NUM+C6_ITEM | C6_PRODUTO, C6_QTDVEN, C6_PRCVEN, C6_VALOR, C6_TES, C6_LOCAL, C6_ENTREG |
| SC9 | Liberacao Pedidos de Venda | C9_PEDIDO+C9_ITEM | C9_PRODUTO, C9_QTDLIB, C9_NFISCAL, C9_BLCRED |
| SD2 | Itens de Venda NF Saida | D2_DOC+D2_SERIE+D2_COD+D2_ITEM | D2_CLIENTE, D2_LOJA, D2_QUANT, D2_PRCVEN, D2_TOTAL, D2_TES, D2_CF, D2_EMISSAO |
| SF2 | Cabecalho NF Saida | F2_DOC+F2_SERIE+F2_CLIENTE+F2_LOJA | F2_EMISSAO, F2_VALBRUT, F2_VALIPI, F2_VALICM, F2_CHVNFE |

## Estoque / Movimentacoes

| Tabela | Descricao | Chave | Campos-chave |
|--------|-----------|-------|-------------|
| SB2 | Saldos de Estoque | B2_COD+B2_LOCAL | B2_QATU, B2_QRES, B2_QEMP, B2_CM1, B2_VATU1 |
| SB9 | Mov. Interna (Requisicoes) | B9_DOC+B9_ITEM | B9_COD, B9_QUANT, B9_LOCAL, B9_LOCALIZ |
| SD1 | Itens NF Entrada | D1_DOC+D1_SERIE+D1_COD+D1_ITEM | D1_FORNECE, D1_LOJA, D1_QUANT, D1_VUNIT, D1_TOTAL, D1_TES, D1_CF, D1_EMISSAO |
| SD3 | Movimentacoes Internas | D3_DOC+D3_COD | D3_QUANT, D3_EMISSAO, D3_TM, D3_LOCAL, D3_CUSTO1 |
| SF1 | Cabecalho NF Entrada | F1_DOC+F1_SERIE+F1_FORNECE+F1_LOJA+F1_TIPO | F1_EMISSAO, F1_VALBRUT, F1_VALIPI, F1_VALICM, F1_CHVNFE |

## Financeiro

| Tabela | Descricao | Chave | Campos-chave |
|--------|-----------|-------|-------------|
| SE1 | Contas a Receber | E1_PREFIXO+E1_NUM+E1_PARCELA+E1_TIPO | E1_CLIENTE, E1_LOJA, E1_EMISSAO, E1_VENCTO, E1_VALOR, E1_SALDO, E1_NATUREZ, E1_PORTADO |
| SE2 | Contas a Pagar | E2_PREFIXO+E2_NUM+E2_PARCELA+E2_TIPO | E2_FORNECE, E2_LOJA, E2_EMISSAO, E2_VENCTO, E2_VALOR, E2_SALDO, E2_NATUREZ, E2_PORTADO |
| SE5 | Movimentacao Bancaria | E5_DATA+E5_SEQ | E5_BANCO, E5_AGENCIA, E5_CONTA, E5_VALOR, E5_MOTBX, E5_TIPODOC, E5_RECPAG |
| SFK | Extratos Bancarios | FK_DATA+FK_SEQ | FK_BANCO, FK_AGENCIA, FK_CONTA, FK_VALOR, FK_HIST |
| SED | Naturezas Financeiras | ED_CODIGO | ED_DESCRIC, ED_TIPO, ED_CONTA |
| SEE | Parametros Financeiros | EE_BANCO+EE_AGENCIA+EE_CONTA | EE_NOMBCO, EE_SALDO |

## Fiscal / Tributacao

| Tabela | Descricao | Chave | Campos-chave |
|--------|-----------|-------|-------------|
| SF3 | Livros Fiscais | F3_CFO+F3_ESTADO | F3_BASEICM, F3_VALICM, F3_BASEIPI, F3_VALIPI |
| SF4 | TES (Tipo Entrada/Saida) | F4_CODIGO | F4_TEXTO, F4_TIPO, F4_CF, F4_ICM, F4_IPI, F4_ESTOQUE, F4_DUPLIC, F4_PODER3, F4_CONSUMO |
| SFB | ICMS por UF | FB_UF+FB_TIPO | FB_ALIQ, FB_MARGEM, FB_DIFAL |
| SFC | ISS Municipio | FC_COD | FC_DESCRI, FC_ALIQISS |
| SF7 | GNRE | F7_EST+F7_COD | F7_VALOR, F7_VENCTO |
| CDH | Regras Fiscais (Configurador Tributos) | CDH_GRUPO | CDH_DESCRI, CDH_IMPSTO, CDH_PERINI, CDH_PERFIM |
| CDA | Amarracao TES Inteligente | CDA_CODTES | CDA_DESCRI |

## Producao / PCP

| Tabela | Descricao | Chave | Campos-chave |
|--------|-----------|-------|-------------|
| SC2 | Ordens de Producao | C2_NUM+C2_ITEM | C2_PRODUTO, C2_QUANT, C2_DATPRI, C2_DATPRF, C2_QUJE, C2_SEQUEN |
| SC4 | Apontamento de Producao | C4_OP+C4_PRODUTO | C4_QUANT, C4_DATA, C4_RECURSO |
| SG1 | Estrutura do Produto | G1_COD+G1_COMP | G1_QUANT, G1_PERDA, G1_INI, G1_FIM |
| SG2 | Roteiro de Operacoes | G2_CODIGO+G2_OPERAC | G2_DESCRI, G2_RECURSO, G2_TEMPO |
| SH1 | Recursos de Producao | H1_CODIGO | H1_DESCRI, H1_TIPO, H1_CUSTHR |
| SHB | Calendario de Producao | HB_CODIGO | HB_DESCRI, HB_HRINID, HB_HRFIMD |

## Manutencao de Ativos

| Tabela | Descricao | Chave | Campos-chave |
|--------|-----------|-------|-------------|
| ST9 | Bens / Equipamentos | T9_CODBEM | T9_NOME, T9_TIPO, T9_SITUAC, T9_LOCALI, T9_DTAQUI, T9_AREA |
| STJ | Ordens de Servico | TJ_ORDEM | TJ_CODBEM, TJ_TIPO, TJ_PRIORI, TJ_DTPREV, TJ_SITUAC |
| STK | Insumos da OS | TK_ORDEM+TK_ITEM | TK_PRODUT, TK_QUANT, TK_CUSTO |
| STO | Planos de Manutencao | TO_CODPLA | TO_DESCRI, TO_TIPO, TO_PERIOD |
| STQ | Servicos de Manutencao | TQ_SERVIC | TQ_DESCRI, TQ_TEMPO, TQ_CUSTO |

## Contabilidade

| Tabela | Descricao | Chave | Campos-chave |
|--------|-----------|-------|-------------|
| CT1 | Plano de Contas | CT1_CONTA | CT1_DESC01, CT1_CLASSE, CT1_NORMAL, CT1_GRUPO |
| CT2 | Lancamentos Contabeis | CT2_DATA+CT2_LOTE+CT2_SUBLOT+CT2_DOC | CT2_DEBITO, CT2_CREDIT, CT2_VALOR, CT2_HIST |
| CVD | Centro de Custo | CVD_CC | CVD_DESC, CVD_CLASSE |
| CTH | Entidades Contabeis | CTH_CUSTO | CTH_DESC01, CTH_CLASSE |
| CTT | Centro de Custo (legado) | CTT_CUSTO | CTT_DESC01, CTT_CLASSE |

## Tabelas de Apoio / Configuracao

| Tabela | Descricao | Chave | Campos-chave |
|--------|-----------|-------|-------------|
| SX1 | Perguntas | X1_GRUPO+X1_ORDEM | X1_PERGUNT, X1_VARIAVL, X1_TIPO, X1_TAMANHO |
| SX2 | Tabelas | X2_CHAVE | X2_NOME, X2_ARQUIVO, X2_MODO |
| SX3 | Campos | X3_ARQUIVO+X3_CAMPO | X3_TITULO, X3_TIPO, X3_TAMANHO, X3_DECIMAL, X3_OBRIGAT, X3_BROWSE |
| SX5 | Tabelas Genericas | X5_TABELA+X5_CHAVE | X5_DESCRI, X5_DESCSPA, X5_DESCENG |
| SX6 | Parametros | X6_VAR | X6_DESCRIC, X6_CONTEUD, X6_TIPO |
| SX7 | Gatilhos | X7_CAMPO+X7_SEQUENC | X7_CDOMIN, X7_REGRA, X7_TIPO |
| SIX | Indices | INDICE+ORDEM | CHAVE, DESCRICAO, SHOWPESQ |
| SXB | Consulta Padrao | XB_ALIAS+XB_TIPO | XB_DESCRIC, XB_CHAVE |
| SXE | Sequencia de Documentos | XE_ID | XE_CONTEUD, XE_FILIAL |

## Recursos Humanos (Tabelas Essenciais)

| Tabela | Descricao | Chave | Campos-chave |
|--------|-----------|-------|-------------|
| SRA | Funcionarios | RA_MAT | RA_NOME, RA_CC, RA_ADMISSA, RA_DEMISSA, RA_CARGO, RA_SALARIO, RA_CPF |
| SRB | Dependentes | RB_MAT+RB_DESSION | RB_NOME, RB_DTNASC, RB_GRAU |
| SRC | Mov.Periodo (Folha) | RC_MAT+RC_PD | RC_VALOR, RC_HORAS |
| SRJ | Cargos | RJ_CODIGO | RJ_DESC, RJ_CODSIND |
| SRV | Ferias | RV_MAT+RV_PERAQU | RV_DATINI, RV_DATFIM, RV_NDIAS |

## Tabelas Auxiliares Frequentes

| Tabela | Descricao | Chave | Campos-chave |
|--------|-----------|-------|-------------|
| DA0 | Tabelas de Preco Cab. | DA0_CODTAB | DA0_DESCRI, DA0_DATDE, DA0_DATATE |
| DA1 | Tabelas de Preco Item | DA1_CODTAB+DA1_CODPRO | DA1_PRCVEN, DA1_DATVIG |
| SE4 | Condicao de Pagamento | E4_CODIGO | E4_DESCRI, E4_TIPO, E4_COND |
| SAE | Administr. Financeira | AE_COD | AE_DESC |
| SM0 | Empresas/Filiais | M0_CODIGO+M0_CODFIL | M0_NOME, M0_NOMECOM, M0_CGC, M0_ENDERE, M0_ESTADO |
| SX9 | Rel. entre Tabelas | X9_DOM+X9_ESSION | X9_EXPDOM, X9_EXPFOR |
| SB3 | Rastreabilidade | B3_COD+B3_LOTECTL | B3_QUANT, B3_VALIDADE, B3_NUMLOTE |
| SB8 | Saldos por Lote | B8_PRODUTO+B8_LOCAL+B8_LOTECTL | B8_SALDO, B8_LOCALIZ |
| SD4 | Solicitacao ao Armazem | D4_DOC+D4_COD | D4_QUANT, D4_LOCAL, D4_EMISSAO |
| SC0 | Contratos | C0_NUM | C0_FORNECE, C0_OBJETO, C0_DATINI, C0_DATFIM, C0_VALOR |
| SF5 | Complemento de NF | F5_NFISCAL+F5_SERIE | F5_FRETE, F5_SEGURO, F5_DESPESA |

---

> **Nota:** Esta e uma referencia rapida. Para a lista completa de campos de qualquer tabela, consulte o arquivo individual em `dicionario/{PREFIXO}/{TABELA}.md` (10.630 tabelas disponiveis).