# Modulo de Estoque (EST / SIGAEST)

## Visao Geral

O modulo de Estoque (SIGAEST) do TOTVS Protheus gerencia o controle de materiais, saldos, movimentacoes, custeio e inventario. O codigo do modulo no Protheus eh **EST** e o executavel padrao eh **SIGAEST**.

Este modulo eh responsavel por:
- Cadastro de produtos e materiais
- Controle de saldos por armazem e endereco
- Movimentacoes internas (requisicoes, devolucoes, transferencias)
- Calculo de custo medio ponderado
- Processo de inventario fisico
- Controle de lotes e rastreabilidade
- Enderecamento (WMS basico)
- Ponto de pedido e estoque minimo

## Fluxo Principal

```
Cadastro de Produtos (SB1)
        |
        v
  Movimentacoes (SD3)
        |
        +---> Entradas: NF Entrada (Compras), Producao (PCP), Devolucao, Ajuste
        +---> Saidas: NF Saida (Faturamento), Requisicao (PCP), Transferencia, Ajuste
        |
        v
  Atualizacao de Saldos (SB2)
        |
        +---> Saldo por armazem (B2_QATU, B2_CM1)
        +---> Custo medio ponderado recalculado
        |
        v
  Custeio / Recalculo (SB9)
        |
        v
  Inventario Fisico
        |
        +---> Contagem (SB7)
        +---> Acerto de Inventario (SD3 ajuste)
```

**Variacoes do fluxo:**
- Transferencia entre armazens: Movimentacao interna sem nota fiscal
- Transferencia entre filiais: Gera NF de saida na origem e NF de entrada no destino
- Requisicao interna: Saida de material para consumo (centro de custo)
- Beneficiamento: Envio a terceiros com controle de poder de terceiros (SB5)
- Movimentacao por endereco: Controle de localizacao fisica no armazem

## Tabelas Principais

| Tabela | Descricao | Chave Primaria | Indices Principais | Relacionamentos |
|---|---|---|---|---|
| SB1 | Cadastro de Produtos | B1_FILIAL+B1_COD | B1_FILIAL+B1_COD; B1_FILIAL+B1_DESC; B1_FILIAL+B1_GRUPO | SBM (grupo), SB5 (poder terceiros), SB2 (saldos) |
| SB2 | Saldos em Estoque | B2_FILIAL+B2_COD+B2_LOCAL | B2_FILIAL+B2_COD+B2_LOCAL; B2_FILIAL+B2_LOCAL+B2_COD | SB1 (produto), NNR (armazem) |
| SB5 | Controle de Terceiros | B5_FILIAL+B5_FILENT+B5_DOC+B5_SERIE+B5_CLIFOR+B5_LOJA+B5_COD+B5_ITEM | B5_FILIAL+B5_COD+B5_CLIFOR | SB1 (produto), SA1/SA2 (terceiro) |
| SD3 | Movimentacoes de Estoque | D3_FILIAL+D3_DOC+D3_COD+D3_ITEM | D3_FILIAL+D3_DOC+D3_COD; D3_FILIAL+D3_EMISSAO+D3_COD; D3_FILIAL+D3_CF | SB1 (produto), SB2 (saldo), SF5 (TES interna) |
| SBZ | Enderecamento (Localizacao) | BZ_FILIAL+BZ_ARMAZEM+BZ_LOCALI+BZ_CODPRO+BZ_LOTECTL | BZ_FILIAL+BZ_ARMAZEM+BZ_LOCALI; BZ_FILIAL+BZ_CODPRO | SB1 (produto), NNR (armazem) |
| SB8 | Saldos por Lote | B8_FILIAL+B8_PRODUTO+B8_LOCAL+B8_LOTECTL | B8_FILIAL+B8_PRODUTO+B8_LOCAL+B8_LOTECTL | SB1 (produto), SB2 (saldo) |
| SB9 | Saldos Iniciais / Custeio | B9_FILIAL+B9_COD+B9_LOCAL+B9_DATA | B9_FILIAL+B9_COD+B9_LOCAL+B9_DATA | SB1 (produto), SB2 (saldo) |
| SB7 | Contagem de Inventario | B7_FILIAL+B7_COD+B7_LOCAL+B7_DOC+B7_NUMSEQ | B7_FILIAL+B7_COD+B7_LOCAL+B7_DOC | SB1 (produto), SB2 (saldo) |
| NNR | Cadastro de Armazens | NNR_FILIAL+NNR_CODIGO | NNR_FILIAL+NNR_CODIGO | SB2 (saldos) |

## Rotinas Padrao

| Codigo | Nome | Tipo |
|---|---|---|
| MATA010 | Cadastro de Produtos | Cadastro |
| MATA240 | Movimentacoes Internas (Requisicoes/Devolucoes) | Processo |
| MATA241 | Transferencia entre Armazens | Processo |
| MATA260 | Documento de Inventario (Geracao) | Processo |
| MATA265 | Acerto de Inventario | Processo |
| MATA300 | Solicitacao ao Armazem | Cadastro |
| MATA330 | Atualizacao do Custo Medio | Processo |
| MATA225 | Transferencias entre Filiais | Processo |
| MATA261 | Contagem de Inventario | Cadastro |
| MATA280 | Virada de Saldos | Processo |
| MATA290 | Recalculo de Saldos | Processo |
| MATR240 | Relatorio de Movimentacoes | Relatorio |
| MATR260 | Relatorio de Inventario | Relatorio |
| MATA270 | Consulta de Saldos | Consulta |
| MATA380 | Cadastro de Grupo de Produtos | Cadastro |

## Pontos de Entrada

| PE | Quando Executa | Parametros | Tabelas Posicionadas |
|---|---|---|---|
| MT240LOK | Validacao de cada item (LinhaOk) na tela de movimentacao interna | Nenhum parametro direto. Dados via M-> (cabecalho) e aCols (itens) | SD3 (quando alteracao), SB1 posicionado no produto, SB2 posicionado no saldo |
| A240GRVA | Executado apos a gravacao de cada item de movimentacao interna | PARAMIXB[1]: nLinha (numero da linha do aCols gravada) | SD3 posicionada no item recem gravado, SB2 posicionada no saldo atualizado |
| MT260TOK | Validacao geral (TudoOk) ao confirmar a geracao do documento de inventario | Nenhum parametro direto. Dados dos itens selecionados para inventario disponiveis via aCols | SB2 posicionada |
| MT300TOK | Validacao geral (TudoOk) na confirmacao da solicitacao ao armazem | Nenhum parametro direto. Dados via M-> (cabecalho) e aCols (itens) | SB1 posicionado no produto |
| A260VALID | Validacao customizada durante a geracao do documento de inventario. Permite filtrar ou incluir produtos | Nenhum parametro direto. Retorno .T. inclui o produto no inventario, .F. exclui | SB1 posicionado no produto sendo avaliado, SB2 posicionada no saldo |
| MT265TOK | Validacao geral (TudoOk) na confirmacao do acerto de inventario | Nenhum parametro direto. Dados dos acertos via aCols | SB7 posicionada na contagem, SB2 posicionada no saldo |
| MT240TOK | Validacao geral (TudoOk) ao confirmar movimentacao interna (todos os itens) | Nenhum parametro direto. Dados via M-> e aCols | SD3 (quando alteracao) |
| A265GRAVA | Executado apos a gravacao do acerto de inventario para cada item | Nenhum parametro direto | SD3 posicionada no movimento de acerto gerado, SB2 posicionada no saldo |
| A240GRVSD3 | Executado apos a gravacao do registro em SD3 na movimentacao interna | Nenhum parametro direto | SD3 posicionada no registro recem gravado |
| A330CPMED | Executado durante o recalculo de custo medio, permite intervencao no calculo | PARAMIXB[1]: cProduto (codigo do produto), PARAMIXB[2]: nCustoCalc (custo calculado) | SB2 posicionada no produto, SB9 posicionada no saldo do periodo |
| MT241LOK | Validacao de item na transferencia entre armazens | Nenhum parametro direto. Dados via aCols | SB2 posicionada no saldo de origem |
| A241GRVA | Executado apos a gravacao de cada item de transferencia entre armazens | PARAMIXB[1]: nLinha (numero da linha gravada) | SD3 posicionada no movimento, SB2 posicionada |

## Integracoes

### Compras -> Estoque
- A classificacao da NF de Entrada gera movimentacao de entrada em SD3
- O saldo (SB2) eh atualizado: B2_QATU += quantidade, B2_CM1 recalculado
- O custo medio ponderado eh recalculado: (saldo_atual * custo_atual + qtd_entrada * custo_entrada) / (saldo_atual + qtd_entrada)

### Faturamento -> Estoque
- A NF de Saida gera movimentacao de saida em SD3
- O saldo (SB2) eh atualizado: B2_QATU -= quantidade
- A saida eh valorizada pelo custo medio atual (B2_CM1)

### PCP -> Estoque
- Empenho (SD4) reserva material no estoque (B2_QEMP)
- Requisicao de material (SD3 tipo RE) baixa do estoque para a ordem de producao
- Apontamento de producao (SD3 tipo PR) gera entrada do produto acabado

### Estoque -> Contabilidade
- Movimentacoes de estoque geram lancamentos contabeis via lancamento padrao (LP)
- A virada de saldos (MATA280) gera lancamentos de fechamento do periodo
- O inventario com acerto gera lancamentos de ajuste contabil

## Regras de Negocio Comuns

### Custo Medio Ponderado
- Metodo padrao do Protheus para custeio: Media Ponderada Movel
- A cada entrada, o custo eh recalculado: novo_custo = (saldo * custo_atual + qtd * custo_novo) / (saldo + qtd)
- Saidas sao valorizadas pelo custo medio vigente
- Parametro MV_CUSMED define o tipo de custeio (1=Online, 2=Pelo fechamento)
- Recalculo mensal via MATA330 corrige divergencias

### Saldo Negativo
- Parametro MV_ESTNEG define se permite saldo negativo de estoque
- S = Permite saldo negativo
- N = Nao permite (bloqueia a movimentacao)
- A = Avisa mas permite
- Saldo negativo causa distorcoes no custo medio e deve ser evitado

### Controle de Lote
- Campo B1_RASTRO define se o produto usa rastreabilidade (L=Lote, S=SubLote, N=Nao)
- Saldo por lote controlado na tabela SB8
- Lote obrigatorio nas movimentacoes quando B1_RASTRO <> "N"
- Permite rastreabilidade completa: origem (NF entrada) ate destino (NF saida)
- Validade do lote controlada pelo campo B8_DTVALID

### Enderecamento (WMS Basico)
- Tabela SBZ controla a localizacao fisica dos produtos no armazem
- Endereco composto por: Armazem + Corredor + Prateleira + Nivel + Coluna
- Parametro MV_ALMOXAR define se usa enderecamento
- Movimentacoes exigem endereco de origem e destino quando ativo

### Unidade de Medida
- Campo B1_UM define a unidade de medida principal
- Campo B1_SEGUM define a segunda unidade de medida
- Fator de conversao em B1_CONV (entre primeira e segunda UM)
- Parametro MV_SEGUM ativa controle de segunda unidade de medida

### Estoque Minimo e Ponto de Pedido
- B1_EMIN: Estoque minimo (seguranca)
- B1_EMAX: Estoque maximo
- B1_PE: Ponto de pedido (quando saldo atinge este nivel, dispara reposicao)
- Usado pelo MRP e relatorios de ressuprimento

### Parametros MV_ Relevantes
| Parametro | Descricao | Valor Padrao |
|---|---|---|
| MV_ESTNEG | Permite saldo negativo de estoque | N |
| MV_CUSMED | Tipo de custeio (1=Online, 2=Fechamento) | 1 |
| MV_ALMOXAR | Usa enderecamento/localizacao | N |
| MV_SEGUM | Controle de segunda unidade de medida | N |
| MV_RASTRO | Obriga rastreabilidade quando produto exige | S |
| MV_ARESSION | Armazem padrao para requisicoes | 01 |
| MV_LOCPAD | Armazem padrao | 01 |
| MV_CONTAM | Numero de contagens no inventario | 2 |
| MV_VIRASI | Virada de saldos automatica | N |
| MV_ULMES | Ultimo mes de fechamento de estoque | (data) |
| MV_ULTPRC | Considera ultimo preco na entrada | S |

## Padroes de Customizacao

### Cenario: Validacao customizada na movimentacao interna
- **PE recomendado:** MT240LOK (por item) e MT240TOK (geral)
- **Abordagem:** MT240LOK para validar cada item (ex: verificar se centro de custo eh valido para o produto, se a quantidade nao excede limite). MT240TOK para validacoes de conjunto (ex: valor total da requisicao)
- **Armadilha comum:** A movimentacao interna usa TES interna (SF5) diferente da TES de NF (SF4). Nao confundir as tabelas de configuracao

### Cenario: Complementar dados apos movimentacao
- **PE recomendado:** A240GRVA ou A240GRVSD3
- **Abordagem:** Apos a gravacao do SD3, complementar com campos customizados, enviar dados para integracao externa, gerar log
- **Armadilha comum:** O SD3 ja esta gravado e o SB2 ja esta atualizado. Se precisar alterar o SD3, usar RecLock. Cuidado para nao alterar campos que afetem o saldo (D3_QUANT, D3_CUSTO1)

### Cenario: Filtro customizado no inventario
- **PE recomendado:** A260VALID
- **Abordagem:** Filtrar produtos especificos para o inventario (ex: apenas produtos de determinado grupo, armazem, ou com movimentacao no periodo)
- **Armadilha comum:** O PE executa para cada produto. Retornar .F. para excluir o produto do inventario. Nao confundir com a contagem (SB7) que eh etapa posterior

### Cenario: Ajuste no calculo do custo medio
- **PE recomendado:** A330CPMED
- **Abordagem:** Intervir no calculo do custo medio para considerar custos adicionais (frete, seguro) ou aplicar regras especificas de custeio
- **Armadilha comum:** Alterar o custo medio incorretamente causa efeito cascata em todas as saidas posteriores. Testar extensivamente antes de produzir
