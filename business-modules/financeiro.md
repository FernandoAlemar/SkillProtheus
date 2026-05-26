# Modulo Financeiro (FIN / SIGAFIN)

## Visao Geral

O modulo Financeiro (SIGAFIN) do TOTVS Protheus gerencia as operacoes de contas a pagar, contas a receber, fluxo de caixa e conciliacao bancaria. O codigo do modulo no Protheus eh **FIN** e o executavel padrao eh **SIGAFIN**.

Este modulo eh responsavel por:
- Gestao de titulos a receber (clientes)
- Gestao de titulos a pagar (fornecedores)
- Controle de borderos e pagamentos em lote
- Baixas manuais e automaticas de titulos
- Compensacao de titulos
- Geracao e leitura de arquivos CNAB (240 e 400)
- Conciliacao bancaria
- Fluxo de caixa
- Controle de adiantamentos
- Comunicacao bancaria via PIX e API bancaria

## Fluxo Principal

```
Origem dos Titulos:
  NF Saida (Faturamento) -----> Titulo a Receber (SE1)
  NF Entrada (Compras) -------> Titulo a Pagar (SE2)
  Inclusao Manual ------------> SE1 ou SE2

Titulos a Receber (SE1):
  SE1 -> Bordero (SEA) -> Envio banco (CNAB remessa) -> Retorno banco (CNAB retorno)
                                                              |
                                                              v
                                                     Baixa automatica (SE5)

Titulos a Pagar (SE2):
  SE2 -> Bordero (SEA) -> Envio banco (CNAB pagamento) -> Retorno banco
                                                              |
                                                              v
                                                     Baixa automatica (SE5)

Baixa Manual:
  SE1/SE2 -> Baixa (SE5) -> Lancamento Contabil (CT2)

Conciliacao:
  Extrato Bancario (FI9) <-> Movimentacao Bancaria (SE5) -> Conciliacao
```

**Variacoes do fluxo:**
- Baixa parcial: Titulo recebe valor menor que o total, gerando saldo remanescente
- Baixa com desconto: Desconto financeiro por pagamento antecipado
- Baixa com juros e multa: Acrescimos por atraso
- Compensacao: Titulo a receber compensa titulo a pagar do mesmo cliente/fornecedor
- Adiantamento: Pagamento/recebimento antecipado sem titulo de origem
- Provisao: Titulo previsto sem documento fiscal vinculado

## Tabelas Principais

| Tabela | Descricao | Chave Primaria | Indices Principais | Relacionamentos |
|---|---|---|---|---|
| SE1 | Titulos a Receber | E1_FILIAL+E1_PREFIXO+E1_NUM+E1_PARCELA+E1_TIPO+E1_FORNECE+E1_LOJA | E1_FILIAL+E1_NUM+E1_PREFIXO+E1_PARCELA+E1_TIPO; E1_FILIAL+E1_CLIENTE+E1_LOJA | SA1 (cliente), SE5 (baixas), SF2 (NF origem) |
| SE2 | Titulos a Pagar | E2_FILIAL+E2_PREFIXO+E2_NUM+E2_PARCELA+E2_TIPO+E2_FORNECE+E2_LOJA | E2_FILIAL+E2_NUM+E2_PREFIXO+E2_PARCELA+E2_TIPO; E2_FILIAL+E2_FORNECE+E2_LOJA | SA2 (fornecedor), SE5 (baixas), SF1 (NF origem) |
| SE5 | Movimentacao Bancaria / Baixas | E5_FILIAL+E5_DATA+E5_SEQ | E5_FILIAL+E5_DATA+E5_SEQ; E5_FILIAL+E5_BANCO+E5_AGENCIA+E5_CONTA | SA6 (banco), SE1/SE2 (titulo origem) |
| SEA | Bordero | EA_FILIAL+EA_NUMBOR+EA_PREFIXO+EA_NUM+EA_PARCELA+EA_TIPO | EA_FILIAL+EA_NUMBOR; EA_FILIAL+EA_NUM+EA_PREFIXO | SE1/SE2 (titulos do bordero), SA6 (banco) |
| FK2 | Arquivo CNAB (cabecalho) | FK2_FILIAL+FK2_NUMARQ | FK2_FILIAL+FK2_NUMARQ | FK3 (detalhes CNAB) |
| SA6 | Cadastro de Bancos | A6_FILIAL+A6_COD+A6_AGENCIA+A6_NUMCON | A6_FILIAL+A6_COD+A6_AGENCIA+A6_NUMCON | SE5 (movimentacoes), SEA (borderos) |
| FI9 | Extrato Bancario | FI9_FILIAL+FI9_BANCO+FI9_AGENCI+FI9_CONTA+FI9_DATA+FI9_SEQ | FI9_FILIAL+FI9_BANCO+FI9_AGENCI+FI9_CONTA+FI9_DATA | SA6 (banco) |
| SEK | Saldo Bancario | EK_FILIAL+EK_BANCO+EK_AGENCIA+EK_CONTA+EK_DATA | EK_FILIAL+EK_BANCO+EK_AGENCIA+EK_CONTA | SA6 (banco) |

## Rotinas Padrao

| Codigo | Nome | Tipo |
|---|---|---|
| FINA040 | Contas a Receber | Cadastro |
| FINA050 | Contas a Pagar | Cadastro |
| FINA100 | Bordero de Pagamento | Processo |
| FINA110 | Bordero de Cobranca | Processo |
| FINA460 | Baixas a Receber | Processo |
| FINA070 | Baixas a Pagar | Processo |
| FINA750 | Compensacao de Titulos | Processo |
| FINA010 | Cadastro de Bancos | Cadastro |
| FINA430 | CNAB - Transmissao/Recepcao | Processo |
| FINA850 | Conciliacao Bancaria | Processo |
| FINA200 | Fluxo de Caixa | Consulta |
| FINA740 | Comunicacao Bancaria | Processo |
| FINA060 | Adiantamentos a Fornecedores | Cadastro |
| FINA045 | Adiantamentos de Clientes | Cadastro |
| FINR010 | Relatorio de Contas a Receber | Relatorio |
| FINR020 | Relatorio de Contas a Pagar | Relatorio |

## Pontos de Entrada

| PE | Quando Executa | Parametros | Tabelas Posicionadas |
|---|---|---|---|
| F040GRV | Executado apos a gravacao do titulo a receber (inclusao ou alteracao) | Nenhum parametro direto. Operacao identificavel via INCLUI/ALTERA | SE1 posicionada no titulo recem gravado |
| FA040LOK | Validacao (LinhaOk) na inclusao/alteracao de titulo a receber. Retorno .T. permite, .F. impede | Nenhum parametro direto. Dados via M-> (campos do titulo) | SE1 (quando alteracao) |
| F050INCL | Executado apos a inclusao do titulo a pagar | Nenhum parametro direto | SE2 posicionada no titulo recem incluido |
| FA050TOK | Validacao geral (TudoOk) na inclusao/alteracao de titulo a pagar | Nenhum parametro direto. Dados via M-> (campos do titulo) | SE2 (quando alteracao) |
| F460CANC | Executado antes do cancelamento da baixa de titulo a receber. Retorno .T. permite cancelamento, .F. impede | Nenhum parametro direto | SE1 posicionada no titulo, SE5 posicionada na baixa a ser cancelada |
| FA100TOK | Validacao geral na confirmacao do bordero de pagamento | Nenhum parametro direto. Titulos do bordero acessiveis via SEA | SEA posicionada, SE2 posicionada no titulo atual |
| F040VLPR | Validacao do valor do titulo a receber antes da gravacao. Permite ajustar ou bloquear valores | Nenhum parametro direto. Valor disponivel via M->E1_VALOR | SE1 (quando alteracao) |
| F460BAIX | Executado apos a baixa do titulo a receber | PARAMIXB[1]: cPrefixo, PARAMIXB[2]: cNum, PARAMIXB[3]: cParcela, PARAMIXB[4]: cTipo | SE1 posicionada no titulo baixado, SE5 posicionada na movimentacao gerada |
| F070BAIX | Executado apos a baixa do titulo a pagar | PARAMIXB[1]: cPrefixo, PARAMIXB[2]: cNum, PARAMIXB[3]: cParcela, PARAMIXB[4]: cTipo | SE2 posicionada no titulo baixado, SE5 posicionada na movimentacao gerada |
| FA050LOK | Validacao (LinhaOk) na inclusao/alteracao de titulo a pagar | Nenhum parametro direto. Dados via M-> | SE2 (quando alteracao) |
| F750COMP | Executado apos a compensacao de titulos | Nenhum parametro direto | SE1 e SE2 posicionadas nos titulos compensados |
| FA850FIM | Executado ao final do processo de conciliacao bancaria | Nenhum parametro direto | FI9 posicionada, SE5 posicionada |
| F100BORD | Executado apos a inclusao de titulo no bordero | PARAMIXB[1]: cNumBord (numero do bordero) | SEA posicionada no item adicionado, SE2 posicionada no titulo |
| F430CNAB | Executado apos o processamento do arquivo CNAB de retorno | PARAMIXB[1]: cArquivo (nome do arquivo processado) | FK2 posicionada no cabecalho do arquivo |

## Integracoes

### Faturamento -> Financeiro
- A NF de Saida (SF2/SD2) gera automaticamente titulo a receber (SE1)
- O desdobramento segue a condicao de pagamento (SE4)
- Campos vinculados: E1_NUM (numero NF), E1_PREFIXO (serie NF), E1_CLIENTE/E1_LOJA

### Compras -> Financeiro
- A NF de Entrada (SF1/SD1) gera automaticamente titulo a pagar (SE2)
- O desdobramento segue a condicao de pagamento informada na NF
- Campos vinculados: E2_NUM (numero NF), E2_PREFIXO (serie NF), E2_FORNECE/E2_LOJA

### Financeiro -> Contabilidade
- Baixas de titulos geram lancamentos contabeis automaticos (CT2)
- A contabilizacao usa lancamento padrao (LP) configurado por natureza financeira
- Movimentacoes de juros, multa e desconto geram lancamentos contabeis separados
- Provisao financeira pode gerar lancamento contabil de provisao

### Financeiro -> Bancos (CNAB/PIX)
- CNAB 240 e 400 para envio e retorno de cobranca e pagamento
- Integracao via API bancaria para PIX (envio e conciliacao)
- Retorno bancario atualiza automaticamente o status dos titulos

## Regras de Negocio Comuns

### Baixa Parcial
- Permite pagar/receber valor menor que o titulo
- Gera saldo remanescente automaticamente no titulo original
- Campo E1_SALDO/E2_SALDO controla o saldo do titulo
- Parametro MV_BAIXPAR define se permite baixa parcial

### Desconto, Juros e Multa
- Desconto: Abatimento por pagamento antecipado (E1_DESCFIN/E2_DESCFIN)
- Juros: Acrescimo por atraso, calculado por dia (E1_JUROS/E2_JUROS)
- Multa: Percentual fixo por atraso (E1_MULTA/E2_MULTA)
- Parametro MV_JURONE define taxa de juros padrao mensal
- Parametro MV_MULTA define percentual de multa padrao
- Calculo pode ser diario (pro rata) ou fixo

### Compensacao
- Permite compensar titulo a receber com titulo a pagar do mesmo parceiro
- Gera movimentacao de compensacao (SE5 tipo CP)
- Diferenca de valor gera saldo remanescente ou titulo complementar
- Rotina FINA750 executa a compensacao

### Provisao
- Titulos podem ser provisionados antes do fato gerador
- Provisao gera lancamento contabil de provisao (debito em despesa/receita provisionada)
- Na efetivacao, a provisao eh revertida e o titulo real eh contabilizado

### CNAB 240 e 400
- CNAB 400: Formato legado, mais simples, uma posicao por campo
- CNAB 240: Formato moderno, mais detalhado, suporte a PIX
- Remessa: Arquivo enviado ao banco com titulos para cobranca ou pagamento
- Retorno: Arquivo recebido do banco com confirmacoes e baixas
- Layout configurado via tabela SED (Layout CNAB)
- Bancos suportados: Banco do Brasil, Itau, Bradesco, Santander, Caixa, Sicoob, entre outros

### PIX
- Integracao via API bancaria ou CNAB 240
- Permite pagamento e recebimento instantaneo
- Chave PIX cadastrada no banco (SA6) e no fornecedor/cliente (SA2/SA1)
- Conciliacao automatica via webhook ou arquivo de retorno

### Conciliacao Bancaria
- Importacao de extrato bancario (FI9) via OFX, CSV ou CNAB
- Conciliacao automatica por valor, data e identificador
- Conciliacao manual para movimentacoes nao identificadas automaticamente
- Gera lancamentos para tarifas e movimentacoes bancarias nao previstas

### Parametros MV_ Relevantes
| Parametro | Descricao | Valor Padrao |
|---|---|---|
| MV_BAIXPAR | Permite baixa parcial de titulos | S |
| MV_JURONE | Taxa de juros mensal padrao (%) | 1.00 |
| MV_MULTA | Percentual de multa por atraso | 2.00 |
| MV_COMP | Permite compensacao de titulos | S |
| MV_MODFIN | Moeda padrao do financeiro | 1 |
| MV_BANCOCD | Banco padrao para cobranca | (vazio) |
| MV_CNABBCO | Layout CNAB padrao | 240 |
| MV_FLXCXA | Considera fluxo de caixa | S |
| MV_PROVCR | Permite provisao no contas a receber | S |
| MV_PROVCP | Permite provisao no contas a pagar | S |
| MV_BX2CONF | Baixa a pagar exige confirmacao | S |
| MV_BP10925 | Retencao de impostos (PIS/COFINS/CSLL) no pagamento | N |

## Padroes de Customizacao

### Cenario: Validacao customizada na baixa de titulo
- **PE recomendado:** F460BAIX (apos baixa a receber) ou F070BAIX (apos baixa a pagar)
- **Abordagem:** Usar o PE para executar logica apos a baixa, como enviar notificacao, atualizar sistema externo, gerar log customizado
- **Armadilha comum:** Esses PEs executam apos a baixa ja estar gravada. Para validar antes da baixa, nao ha PE padrao - considerar uso de gatilho ou workflow

### Cenario: Complementar titulo gerado pelo faturamento
- **PE recomendado:** F040GRV
- **Abordagem:** Apos a gravacao do titulo em SE1, complementar com centro de custo, natureza financeira customizada, campos extras
- **Armadilha comum:** O F040GRV executa tanto na inclusao manual quanto na inclusao automatica (via NF). Verificar o contexto de chamada antes de aplicar a logica

### Cenario: Integracao CNAB customizada
- **PE recomendado:** F430CNAB
- **Abordagem:** Apos o processamento do retorno CNAB, executar acoes adicionais como envio de email ao cliente, atualizacao de dashboard, log de auditoria
- **Armadilha comum:** O processamento do CNAB ja esta concluido quando o PE executa. Nao tentar reprocessar o arquivo. Usar os dados ja processados em FK2/FK3

### Cenario: Controle customizado de bordero
- **PE recomendado:** FA100TOK (validacao) e F100BORD (apos inclusao no bordero)
- **Abordagem:** FA100TOK para validar se os titulos selecionados atendem criterios especificos. F100BORD para executar acoes apos adicionar titulo ao bordero
- **Armadilha comum:** O bordero agrupa titulos para envio ao banco. Nao confundir bordero com baixa - o bordero eh um passo intermediario
