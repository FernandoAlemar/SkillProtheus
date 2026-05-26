# Modulo PCP - Planejamento e Controle de Producao (SIGAPCP)

## Visao Geral

O modulo PCP (SIGAPCP) do TOTVS Protheus gerencia o planejamento, programacao e controle da producao industrial. O codigo do modulo no Protheus eh **PCP** e o executavel padrao eh **SIGAPCP**.

Este modulo eh responsavel por:
- Cadastro de estrutura de produto (BOM - Bill of Materials)
- Cadastro de roteiro de operacoes
- Planejamento de necessidades de materiais (MRP)
- Geracao e controle de ordens de producao (OP)
- Empenho e requisicao de materiais
- Apontamento de producao (reporte)
- Encerramento de ordens de producao
- Calculo de carga-maquina (CRP)
- Controle de eficiencia e produtividade

## Fluxo Principal

```
Estrutura de Produto / BOM (SG1)
        |
        +---> Componentes e quantidades por nivel
        +---> Roteiro de Operacoes (SG2) - tempos e recursos
        |
        v
  Planejamento (MRP - MATA710/MATA711)
        |
        +---> Demanda: Pedidos venda (SC5), Previsao (SC4), Necessidade manual
        +---> Oferta: Saldo estoque (SB2), Pedidos compra (SC7), OP abertas (SC2)
        +---> Calculo: Necessidade liquida = Demanda - Oferta
        |
        v
  Resultado do MRP
        |
        +---> Itens fabricados: Gera Ordem de Producao (SC2)
        +---> Itens comprados: Gera Solicitacao de Compra (SC1)
        |
        v
  Ordem de Producao (SC2)
        |
        v
  Empenho de Materiais (SD4)
        |
        +---> Reserva de materiais no estoque (B2_QEMP)
        +---> Requisicao ao armazem quando necessario
        |
        v
  Producao / Apontamento
        |
        +---> Apontamento de producao (SD3 tipo PR - entrada produto acabado)
        +---> Requisicao de materiais (SD3 tipo RE - saida de componentes)
        +---> Devolucao de materiais (SD3 tipo DE - sobra)
        |
        v
  Encerramento da OP
        |
        +---> Baixa de empenhos remanescentes
        +---> Calculo de custo real da producao
        +---> Atualizacao de saldo do produto acabado (SB2)
```

**Variacoes do fluxo:**
- Producao sob encomenda: OP vinculada a pedido de venda especifico
- Producao para estoque: OP gerada por previsao de demanda ou ponto de pedido
- Producao em lote: Quantidade fixa por lote (ex: farmaceutico, alimenticio)
- Producao por processo: Producao continua com formula/receita
- Subcontratacao (beneficiamento): Envio de materiais a terceiro para processamento
- OP pai/filha: OP do produto acabado gera OP dos semi-acabados

## Tabelas Principais

| Tabela | Descricao | Chave Primaria | Indices Principais | Relacionamentos |
|---|---|---|---|---|
| SC2 | Ordens de Producao | C2_FILIAL+C2_NUM+C2_ITEM+C2_SEQUEN | C2_FILIAL+C2_NUM+C2_ITEM; C2_FILIAL+C2_PRODUTO+C2_NUM; C2_FILIAL+C2_DATPRI | SB1 (produto), SD4 (empenhos), SG1 (estrutura) |
| SD4 | Empenhos (Reserva de Material) | D4_FILIAL+D4_OP+D4_COD+D4_SEQ | D4_FILIAL+D4_OP+D4_COD; D4_FILIAL+D4_COD+D4_OP | SC2 (OP), SB1 (componente), SB2 (saldo) |
| SD3 | Movimentacoes de Estoque (Producao) | D3_FILIAL+D3_DOC+D3_COD+D3_ITEM | D3_FILIAL+D3_DOC+D3_COD; D3_FILIAL+D3_OP | SC2 (OP), SB1 (produto), SB2 (saldo) |
| SB1 | Cadastro de Produtos | B1_FILIAL+B1_COD | B1_FILIAL+B1_COD; B1_FILIAL+B1_DESC | SG1 (estrutura), SC2 (OPs) |
| SG1 | Estrutura de Produto (BOM) | G1_FILIAL+G1_COD+G1_COMP+G1_TRT | G1_FILIAL+G1_COD+G1_COMP; G1_FILIAL+G1_COMP+G1_COD | SB1 (produto pai e componente) |
| SG2 | Roteiro de Operacoes | G2_FILIAL+G2_CODIGO+G2_OPERAC+G2_GROPC | G2_FILIAL+G2_CODIGO+G2_OPERAC | SB1 (produto), SHB (recurso) |
| SHY | Previsao de Vendas | HY_FILIAL+HY_PRODUTO+HY_DATA | HY_FILIAL+HY_PRODUTO+HY_DATA | SB1 (produto) |
| SC4 | Previsao de Vendas (legada) | C4_FILIAL+C4_PRODUTO+C4_DATA | C4_FILIAL+C4_PRODUTO+C4_DATA | SB1 (produto) |
| SHB | Cadastro de Recursos (Maquinas/Centros de Trabalho) | HB_FILIAL+HB_CODIGO | HB_FILIAL+HB_CODIGO | SG2 (roteiro), SH6 (calendario) |
| SH6 | Calendario de Producao | H6_FILIAL+H6_RECURSO+H6_DATA | H6_FILIAL+H6_RECURSO+H6_DATA | SHB (recurso) |

## Rotinas Padrao

| Codigo | Nome | Tipo |
|---|---|---|
| MATA630 | Estrutura de Produto (BOM) | Cadastro |
| MATA650 | Ordem de Producao | Cadastro |
| MATA250 | Apontamento de Producao | Processo |
| MATA681 | MRP - Calculo de Necessidades | Processo |
| MATA682 | MRP - Geracao de Ordens e Solicitacoes | Processo |
| MATA640 | Roteiro de Operacoes | Cadastro |
| MATA651 | Empenho Manual | Cadastro |
| MATA655 | Encerramento de OP | Processo |
| MATA260 | Requisicao de Materiais (Manual) | Processo |
| MATA710 | MRP (versao completa) | Processo |
| MATA711 | MRP (versao simplificada) | Processo |
| MATR680 | Relatorio de Ordens de Producao | Relatorio |
| MATA685 | Carga Maquina (CRP) | Consulta |
| MATA690 | Consulta de OP | Consulta |

## Pontos de Entrada

| PE | Quando Executa | Parametros | Tabelas Posicionadas |
|---|---|---|---|
| M650LOK | Validacao de cada item (LinhaOk) na inclusao/alteracao da Ordem de Producao | Nenhum parametro direto. Dados via M-> (cabecalho OP) e aCols (itens/empenhos) | SC2 (quando alteracao), SB1 posicionado no produto |
| MT250TOK | Validacao geral (TudoOk) na confirmacao do apontamento de producao | Nenhum parametro direto. Dados via M-> (campos do apontamento: produto, quantidade, OP) | SC2 posicionada na OP, SB2 posicionada no saldo |
| MT681FIM | Executado ao final do calculo do MRP, apos processar todas as necessidades | Nenhum parametro direto | Nenhuma tabela posicionada especificamente. Resultados do MRP em tabelas temporarias |
| A650GRVA | Executado apos a gravacao da Ordem de Producao (inclusao ou alteracao) | Nenhum parametro direto. Operacao identificavel via INCLUI/ALTERA | SC2 posicionada na OP recem gravada, SD4 posicionados nos empenhos |
| MT650LOK | Validacao geral (TudoOk - apesar do nome LOK, funciona como TOK nesta rotina) na confirmacao da OP | Nenhum parametro direto. Dados via M-> e aCols | SC2 (quando alteracao), SG1 posicionada na estrutura |
| A681MRP | Executado durante o calculo do MRP para cada item processado, permite ajustar a necessidade calculada | PARAMIXB[1]: cProduto (codigo do produto), PARAMIXB[2]: nNecessidade (quantidade calculada), PARAMIXB[3]: dData (data da necessidade) | SB1 posicionado no produto, SB2 posicionada no saldo |
| A250GRVA | Executado apos a gravacao do apontamento de producao | Nenhum parametro direto | SD3 posicionada no movimento de producao, SC2 posicionada na OP |
| MT250LOK | Validacao de item no apontamento de producao | Nenhum parametro direto. Dados via aCols | SC2 posicionada na OP, SB1 posicionado no produto |
| A655ENCER | Executado apos o encerramento da OP | Nenhum parametro direto | SC2 posicionada na OP encerrada |
| M630LOK | Validacao na inclusao/alteracao de componente na estrutura de produto | Nenhum parametro direto. Dados via M-> e aCols | SG1 (quando alteracao), SB1 posicionado no componente |
| A650EMPN | Executado apos a geracao automatica de empenhos da OP | Nenhum parametro direto | SC2 posicionada na OP, SD4 posicionados nos empenhos gerados |
| M682GERA | Executado durante a geracao de OP/SC1 pelo MRP (MATA682) para cada item gerado | PARAMIXB[1]: cProduto (codigo do produto), PARAMIXB[2]: nQuantidade, PARAMIXB[3]: cTipo ("OP" ou "SC") | SB1 posicionado no produto |
| MT655TOK | Validacao geral na confirmacao do encerramento da OP | Nenhum parametro direto. Dados via M-> | SC2 posicionada na OP sendo encerrada |

## Integracoes

### PCP -> Estoque
- Empenho (SD4) reserva materiais no estoque: B2_QEMP eh incrementado
- Requisicao de material (SD3 tipo RE) baixa do estoque: B2_QATU eh decrementado
- Apontamento de producao (SD3 tipo PR) gera entrada do produto acabado: B2_QATU eh incrementado
- Devolucao de materiais (SD3 tipo DE) retorna ao estoque
- O custo do produto acabado inclui o custo dos materiais consumidos

### PCP -> Compras
- MRP gera solicitacoes de compra (SC1) para itens comprados
- A quantidade eh calculada com base na necessidade liquida
- A data de necessidade considera o lead time de compra (B1_PE)
- A solicitacao segue o fluxo normal de compras

### PCP -> Faturamento
- Producao sob encomenda: OP vinculada ao pedido de venda (C2_PEDIDO)
- Ao encerrar a OP, o pedido de venda pode ser liberado para faturamento
- O custo de producao influencia a margem de venda

### PCP -> Contabilidade
- Movimentacoes de producao geram lancamentos contabeis via LP
- Entrada de produto acabado: Debito em estoque de acabados, credito em producao em processo
- Requisicao de materiais: Debito em producao em processo, credito em estoque de materias-primas

## Regras de Negocio Comuns

### Explosao de Estrutura (BOM)
- A estrutura de produto (SG1) define os componentes necessarios para fabricar o produto
- Explosao multinivel: Produto acabado > Semi-acabado > Materia-prima
- Campo G1_QUANT define a quantidade de componente por unidade de produto pai
- Campo G1_PERDA define o percentual de perda esperado
- Quantidade empenhada = G1_QUANT * (1 + G1_PERDA/100) * Quantidade da OP
- Estrutura fantasma (G1_INF = "S"): Componente nao gera OP, seus filhos sao empenhados diretamente

### Lead Time
- B1_PE: Prazo de entrega padrao do produto (dias)
- Usado pelo MRP para calcular a data de inicio da OP ou pedido de compra
- Data inicio = Data necessidade - Lead time
- Para itens fabricados, o lead time pode ser calculado pelo roteiro de operacoes

### Estoque de Seguranca
- B1_EMIN: Estoque minimo (seguranca)
- O MRP considera o estoque de seguranca como demanda adicional
- Quando o saldo projetado fica abaixo do estoque minimo, o MRP gera necessidade

### Roteiro de Operacoes
- SG2 define a sequencia de operacoes para fabricar o produto
- Cada operacao tem: recurso (maquina), tempo de preparacao (setup), tempo de execucao por unidade
- G2_TEMPOS: Tempo de setup (minutos)
- G2_TEMPOP: Tempo de operacao por peca (minutos)
- G2_RECURSO: Recurso/maquina utilizado
- Usado para calculo de carga-maquina (CRP) e custeio da mao de obra

### Eficiencia de Recurso
- SHB armazena a eficiencia padrao de cada recurso (HB_EFICIEN)
- Eficiencia de 100% = recurso opera na capacidade nominal
- O CRP ajusta a capacidade disponivel pela eficiencia
- Capacidade disponivel = Horas calendario * Eficiencia / 100

### Apontamento de Producao (Reporte)
- Apontamento parcial: Reporta quantidade parcial, OP continua aberta
- Apontamento total: Reporta quantidade restante, OP pode ser encerrada
- Apontamento gera: Entrada do produto acabado (SD3 tipo PR) + Baixa dos componentes (SD3 tipo RE)
- Baixa de componentes pode ser: Automatica (backflush) ou Manual (requisicao previa)
- Parametro MV_BACKFLU define o tipo de baixa: S=Backflush, N=Manual

### Status da OP
Campo C2_STATUS controla o ciclo de vida:
- 1 = Prevista (gerada pelo MRP, nao firme)
- 2 = Aberta/Firme (confirmada para producao)
- 3 = Iniciada (com apontamento parcial)
- 4 = Encerrada
- 5 = Cancelada
- A transicao de Prevista para Firme eh feita manualmente ou via MATA682

### Parametros MV_ Relevantes
| Parametro | Descricao | Valor Padrao |
|---|---|---|
| MV_BACKFLU | Baixa automatica de componentes (backflush) | S |
| MV_ESTZERO | Permite apontar com saldo zero de componente | N |
| MV_PCESSION | Calcula custo de producao | S |
| MV_TESSION | TES inteligente na producao | N |
| MV_MRPVLD | Dias de validade do calculo MRP | 7 |
| MV_LEADTIME | Considera lead time no MRP | S |
| MV_ESTOSEG | Considera estoque seguranca no MRP | S |
| MV_PRECISA | Precisao no calculo do MRP (casas decimais) | 2 |
| MV_EMESSION | Empenho automatico na geracao de OP | S |
| MV_OPCLOSE | Permite encerrar OP com saldo de empenho | S |
| MV_OPQTMIN | Quantidade minima de producao | 0 |
| MV_DESSION | Desconsiderar saldo negativo no MRP | N |

## Padroes de Customizacao

### Cenario: Validacao customizada na Ordem de Producao
- **PE recomendado:** MT650LOK (validacao geral) e M650LOK (validacao por item)
- **Abordagem:** MT650LOK para validar a OP inteira (ex: capacidade do recurso, disponibilidade de materia-prima critica). M650LOK para validar cada empenho (ex: componente alternativo, quantidade maxima)
- **Armadilha comum:** A OP pode ser gerada automaticamente pelo MRP (MATA682). Nesse caso, os PEs de tela nao executam. Para validar OP automaticas, usar M682GERA

### Cenario: Ajustar calculo do MRP
- **PE recomendado:** A681MRP
- **Abordagem:** Interceptar o calculo de necessidade para cada item e ajustar conforme regras especificas (ex: arredondar para lote economico, considerar sazonalidade, ajustar lead time dinamicamente)
- **Armadilha comum:** O MRP processa milhares de itens. O PE executa para cada um. Logica pesada dentro do PE causa lentidao severa. Otimizar ao maximo, evitar queries adicionais, usar cache quando possivel

### Cenario: Acoes apos apontamento de producao
- **PE recomendado:** A250GRVA
- **Abordagem:** Apos o apontamento, executar acoes como: enviar notificacao de producao, atualizar dashboard de producao, gerar etiqueta de identificacao, integrar com sistema MES
- **Armadilha comum:** O apontamento gera movimentacoes em SD3 (entrada do acabado e saida dos componentes se backflush). Nao tentar refazer essas movimentacoes no PE

### Cenario: Customizar encerramento de OP
- **PE recomendado:** A655ENCER e MT655TOK
- **Abordagem:** MT655TOK para validar antes do encerramento (ex: verificar se todas as operacoes foram apontadas, se qualidade aprovou). A655ENCER para acoes apos encerramento (ex: calcular custo real vs orcado, gerar relatorio de producao)
- **Armadilha comum:** O encerramento baixa empenhos remanescentes e fecha a OP. Apos encerrada, a OP nao aceita mais apontamentos. Garantir que todos os reportes foram feitos antes de encerrar
