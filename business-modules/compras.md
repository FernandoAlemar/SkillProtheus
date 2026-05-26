# Modulo de Compras (COM / SIGACOM)

## Visao Geral

O modulo de Compras (SIGACOM) do TOTVS Protheus gerencia todo o ciclo de aquisicao de materiais e servicos, desde a solicitacao interna ate o recebimento da nota fiscal de entrada. O codigo do modulo no Protheus eh **COM** e o executavel padrao eh **SIGACOM**.

Este modulo eh responsavel por:
- Controle de solicitacoes de compra internas
- Processo de cotacao com fornecedores
- Emissao e acompanhamento de pedidos de compra
- Recebimento de materiais via nota fiscal de entrada
- Manutencao do cadastro de fornecedores e vinculo produto/fornecedor
- Controle de alcadas de aprovacao

## Fluxo Principal

```
Solicitacao de Compra (SC1)
        |
        v
  [Aprovacao por alcada?]---Sim---> Cotacao de Precos (SC8/SCJ)
        |                                    |
       Nao (compra direta)                   v
        |                          Analise de Cotacao
        |                                    |
        v                                    v
  Pedido de Compra (SC7) <------ Gerar Pedido da Cotacao
        |
        v
  Documento de Entrada / NF Entrada (SF1 cabecalho + SD1 itens)
        |
        +-------> Estoque: Movimentacao entrada (SD3) + Saldo (SB2)
        |
        +-------> Financeiro: Titulo a Pagar (SE2)
        |
        +-------> Fiscal: Livro Fiscal de Entrada (SF3)
```

**Variacoes do fluxo:**
- Compra direta: SC1 direto para SC7, sem cotacao
- Compra por contrato: Vinculo com contrato de fornecimento
- Compra importacao: Fluxo adicional com processo de importacao (embarque, desembaraco)
- Solicitacao automatica do MRP: PCP gera SC1 automaticamente
- Pre-nota: Documento de entrada sem classificacao fiscal, classificado depois

## Tabelas Principais

| Tabela | Descricao | Chave Primaria | Indices Principais | Relacionamentos |
|---|---|---|---|---|
| SC1 | Solicitacoes de Compra | C1_FILIAL+C1_NUM+C1_ITEM | C1_FILIAL+C1_NUM+C1_ITEM; C1_FILIAL+C1_PRODUTO+C1_NUM | SA2 (fornecedor sugerido), SB1 (produto), CTT (centro custo) |
| SC7 | Pedidos de Compra | C7_FILIAL+C7_NUM+C7_ITEM | C7_FILIAL+C7_NUM+C7_ITEM; C7_FILIAL+C7_FORNECE+C7_LOJA+C7_NUM | SA2 (fornecedor), SB1 (produto), SC1 (solicitacao origem) |
| SD1 | Itens de NF Entrada | D1_FILIAL+D1_DOC+D1_SERIE+D1_FORNECE+D1_LOJA+D1_COD+D1_ITEM | D1_FILIAL+D1_DOC+D1_SERIE+D1_FORNECE+D1_LOJA; D1_FILIAL+D1_COD | SF1 (cabecalho NF), SC7 (pedido origem), SB1 (produto) |
| SF1 | Cabecalho NF Entrada | F1_FILIAL+F1_DOC+F1_SERIE+F1_FORNECE+F1_LOJA+F1_TIPO | F1_FILIAL+F1_DOC+F1_SERIE+F1_FORNECE+F1_LOJA | SA2 (fornecedor), SD1 (itens), SE2 (titulo gerado) |
| SA2 | Cadastro de Fornecedores | A2_FILIAL+A2_COD+A2_LOJA | A2_FILIAL+A2_COD+A2_LOJA; A2_FILIAL+A2_NOME | AI0 (enderecos), SA5 (amarracao) |
| SA5 | Amarracao Produto x Fornecedor | A5_FILIAL+A5_FORNECE+A5_LOJA+A5_PRODUTO | A5_FILIAL+A5_FORNECE+A5_LOJA+A5_PRODUTO; A5_FILIAL+A5_PRODUTO | SA2 (fornecedor), SB1 (produto) |
| SC8 | Cabecalho de Cotacao | C8_FILIAL+C8_NUM | C8_FILIAL+C8_NUM | SCJ (itens da cotacao) |
| SCJ | Itens de Cotacao | CJ_FILIAL+CJ_NUM+CJ_ITEM+CJ_FORNECE+CJ_LOJA | CJ_FILIAL+CJ_NUM+CJ_ITEM | SC8 (cabecalho), SA2 (fornecedor) |

## Rotinas Padrao

| Codigo | Nome | Tipo |
|---|---|---|
| MATA105 | Solicitacoes de Compras | Cadastro |
| MATA120 | Pedidos de Compra | Cadastro |
| MATA103 | Cotacao de Precos | Processo |
| MATA135 | Analise de Cotacao | Processo |
| MATA140 | Documento de Entrada | Cadastro |
| MATA116 | Classificacao de NF Entrada | Processo |
| MATA126 | Aprovacao de Pedidos de Compra | Processo |
| MATA130 | Geracao de Pedidos de Compra (da cotacao) | Processo |
| MATA145 | Pre-Nota de Entrada | Cadastro |
| MATA150 | Contratos de Parceria | Cadastro |
| CNTA210 | Cadastro de Fornecedores | Cadastro |
| MATA185 | Mapa de Cotacao | Consulta |
| MATR110 | Relatorio de Pedidos de Compra | Relatorio |
| MATR120 | Relatorio de Solicitacoes de Compra | Relatorio |

## Pontos de Entrada

| PE | Quando Executa | Parametros | Tabelas Posicionadas |
|---|---|---|---|
| MT100LOK | Validacao na confirmacao da inclusao/alteracao de itens da NF de Entrada (LinhaOk do aCols) | Nenhum parametro direto. Dados disponiveis via INCLUI/ALTERA e variaveis M-> para cabecalho, aCols para itens | SF1 (cabecalho quando alteracao), SD1 (item atual via aCols) |
| MT120LOK | Validacao na confirmacao da inclusao/alteracao de itens do Pedido de Compra | Nenhum parametro direto. Dados disponiveis via M-> para cabecalho, aCols para itens | SC7 (quando alteracao) |
| M103MANU | Manipulacao da tela de cotacao de precos, permite incluir botoes ou campos adicionais | Nenhum parametro direto | SC8, SCJ posicionados no registro atual |
| MA103BUT | Adiciona botoes extras na barra de ferramentas da cotacao de precos | Nenhum parametro direto. Retorno: array bidimensional {cTitulo, bBloco} | SC8 posicionado |
| MT100GRV | Executado apos a gravacao de cada item da NF de Entrada | PARAMIXB[1]: nLinha (numero da linha do aCols sendo gravada) | SF1 (cabecalho gravado), SD1 (item recem gravado e posicionado) |
| A103MSQL | Permite alterar a query SQL usada na rotina de cotacao de precos para busca de dados | PARAMIXB[1]: cQuery (query original) | Nenhuma tabela posicionada especificamente |
| MT120TOK | Validacao geral (TudoOk) na confirmacao do Pedido de Compra, executado apos validacao de todos os itens | Nenhum parametro direto. Dados via M-> (cabecalho) e aCols (itens) | SC7 (quando alteracao) |
| A120ALTPRD | Executado na alteracao do produto no item do Pedido de Compra, permite manipular valores do item | Nenhum parametro direto. Produto disponivel via aCols na coluna correspondente | SC7, SA5 posicionados |
| M120VLPRD | Validacao do preco unitario do produto no Pedido de Compra | Nenhum parametro direto. Valor disponivel via variavel de memoria do campo | SC7, SA5 posicionados |
| A140INSP | Executado durante o processo de inspecao de entrada na classificacao de NF | PARAMIXB[1]: cDoc (numero documento), PARAMIXB[2]: cSerie, PARAMIXB[3]: cFornece, PARAMIXB[4]: cLoja | SF1 posicionada no documento |
| MT140LOK | Validacao na confirmacao dos itens do Documento de Entrada (pre-nota) | Nenhum parametro direto. Dados via M-> e aCols | SF1 (cabecalho), SD1 (itens via aCols) |
| A105SOLC | Executado na inclusao de Solicitacao de Compra, permite manipular dados antes da gravacao | Nenhum parametro direto. Dados via M-> e aCols | SC1 (quando alteracao) |
| MT105LOK | Validacao na confirmacao dos itens da Solicitacao de Compra | Nenhum parametro direto. Dados via M-> (cabecalho) e aCols (itens) | SC1 (quando alteracao) |
| A120VERBA | Executado na verificacao de verba/orcamento do Pedido de Compra | PARAMIXB[1]: nValor (valor total do pedido) | SC7 posicionado |
| M140IEXT | Permite incluir campos extras na integracao do Documento de Entrada com outros modulos | Nenhum parametro direto | SF1 e SD1 posicionados no registro sendo integrado |

## Integracoes

### Compras -> Estoque
- A classificacao da NF de Entrada (MATA140/MATA116) gera automaticamente movimentacao de entrada no estoque (SD3)
- O saldo do produto (SB2) eh atualizado automaticamente com a quantidade recebida
- O custo medio ponderado (B2_CM1) eh recalculado com base no valor da NF
- A TES (SF4) define se o item movimenta estoque (F4_ESTOQUE = "S")

### Compras -> Financeiro
- A classificacao da NF de Entrada gera automaticamente titulo a pagar (SE2)
- O titulo eh gerado com base na condicao de pagamento (E4_CODIGO) informada na NF
- Desdobramento automatico em parcelas conforme condicao de pagamento
- A TES define se gera duplicata (F4_DUPLIC = "S")

### Compras -> Fiscal
- A NF de Entrada gera automaticamente lancamento no livro fiscal de entrada (SF3)
- Os impostos (ICMS, IPI, PIS, COFINS) sao calculados com base na TES e NCM
- O CFOP eh definido pela TES (F4_CF) ou pela amarracao de CFOP

### PCP -> Compras
- O MRP (MATA710/MATA711) gera solicitacoes de compra (SC1) automaticamente para itens comprados
- A quantidade eh calculada com base na necessidade liquida (demanda - estoque - pedidos pendentes)

### Compras -> Contabilidade
- A classificacao da NF de Entrada pode gerar lancamentos contabeis automaticos
- A contabilizacao usa lancamento padrao (LP) configurado para o tipo de movimentacao

## Regras de Negocio Comuns

### Aprovacao por Alcada
- Solicitacoes e pedidos podem exigir aprovacao conforme valor e nivel hierarquico
- Configuracao via tabela SAK (Alcadas de Aprovacao) e SAL (Aprovadores)
- Parametro MV_APROVAL ativa/desativa o controle de aprovacao
- Parametro MV_APRCOTS controla aprovacao de cotacoes

### Quantidade Minima de Cotacao
- Parametro MV_NUMCOT define o numero minimo de fornecedores a cotar
- Se nao atingir o minimo, a analise de cotacao emite aviso mas permite prosseguir

### Saldo SC1 vs SC7
- A solicitacao de compra (SC1) controla o saldo entre quantidade solicitada e quantidade ja atendida por pedido
- Campo C1_QUPTS armazena a quantidade ja transformada em pedido
- Saldo disponivel = C1_QUANT - C1_QUPTS - C1_QUJE (quantidade ja recebida)

### Amarracao Produto x Fornecedor (SA5)
- Permite vincular produtos a fornecedores preferenciais com preco e prazo
- Parametro MV_PRODFOR controla se a amarracao eh obrigatoria
- Quando ativa, so permite comprar de fornecedores vinculados ao produto

### Bloqueio de Fornecedor
- Campo A2_MSBLQL controla o bloqueio do fornecedor
- Fornecedor bloqueado nao pode ser usado em pedidos de compra ou NFs de entrada
- Bloqueio pode ser por inadimplencia, problemas de qualidade, etc.

### Rateio por Centro de Custo
- Itens de compra podem ser rateados entre centros de custo
- Configuracao via tabela SCK (Rateio de Itens)
- Usado principalmente para compras de servicos e materiais de uso e consumo

### Parametros MV_ Relevantes
| Parametro | Descricao | Valor Padrao |
|---|---|---|
| MV_APROVAL | Ativa aprovacao de compras | .F. |
| MV_NUMCOT | Numero minimo de fornecedores para cotacao | 3 |
| MV_PRODFOR | Obriga amarracao produto/fornecedor | N |
| MV_ULTPRC | Considera ultimo preco de compra como sugestao | S |
| MV_PRECNFE | Valida preco do pedido x NF de entrada | N |
| MV_TOLERPC | Percentual de tolerancia entre preco pedido e NF | 0 |
| MV_RELACOT | Gera relatorio automatico na analise de cotacao | N |
| MV_COMPam | Permite compra com saldo em outra filial | N |
| MV_TESSION | TES inteligente para notas de entrada | N |
| MV_PCOTGER | Gera pedido automatico na cotacao | N |

## Padroes de Customizacao

### Cenario: Validacao customizada no Pedido de Compra
- **PE recomendado:** MT120LOK (validacao de item) e MT120TOK (validacao geral)
- **Abordagem:** Usar MT120LOK para validar cada item individualmente (ex: limite de valor por item). Usar MT120TOK para validacoes que dependem do conjunto de itens (ex: valor total do pedido)
- **Armadilha comum:** Nao confundir LOK (linha) com TOK (tudo). LOK executa para cada item, TOK executa uma vez ao confirmar

### Cenario: Campos adicionais na NF de Entrada
- **PE recomendado:** MT100GRV (apos gravacao de item) e M140IEXT (integracao)
- **Abordagem:** Usar MT100GRV para gravar campos extras no SD1 apos cada item ser gravado. Usar M140IEXT para incluir dados extras na integracao com outros modulos
- **Armadilha comum:** No MT100GRV, o SD1 ja esta gravado e posicionado. Para alterar, usar RecLock. Nao tentar alterar via Replace direto

### Cenario: Aprovacao customizada de Solicitacao de Compra
- **PE recomendado:** MT105LOK
- **Abordagem:** Validar campos obrigatorios, centro de custo, verba disponivel antes de permitir a inclusao
- **Armadilha comum:** A aprovacao por alcada (SAK/SAL) eh separada da validacao do PE. O PE valida na inclusao, a alcada valida na liberacao

### Cenario: Integracao com sistema externo na entrada de NF
- **PE recomendado:** MT100GRV
- **Abordagem:** Apos a gravacao de cada item, enviar dados para sistema externo via REST/SOAP
- **Armadilha comum:** O PE executa dentro da transacao. Se a chamada externa falhar, pode travar a transacao. Considerar gravacao em tabela intermediaria e processamento assincrono via schedule
