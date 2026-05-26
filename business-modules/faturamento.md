# Modulo de Faturamento (FAT / SIGAFAT)

## Visao Geral

O modulo de Faturamento (SIGAFAT) do TOTVS Protheus gerencia o ciclo de vendas, desde o pedido de venda ate a emissao da nota fiscal de saida. O codigo do modulo no Protheus eh **FAT** e o executavel padrao eh **SIGAFAT**.

Este modulo eh responsavel por:
- Cadastro e manutencao de clientes
- Cadastro de tabelas de preco
- Emissao e acompanhamento de pedidos de venda
- Liberacao de pedidos (credito, estoque, regras comerciais)
- Emissao de notas fiscais de saida
- Controle de condicoes de pagamento e descontos
- Calculo de impostos na saida (ICMS, IPI, PIS, COFINS, ISS)

## Fluxo Principal

```
Pedido de Venda (SC5 cabecalho + SC6 itens)
        |
        v
  [Liberacao de Pedido (SC9)]
        |
        +---> Credito OK? (A1_LC - limite de credito)
        +---> Estoque OK? (saldo SB2)
        +---> Regras comerciais OK?
        |
        v
  Preparacao / Separacao
        |
        v
  Nota Fiscal de Saida (SF2 cabecalho + SD2 itens)
        |
        +-------> Estoque: Movimentacao saida (SD3) + Saldo (SB2)
        |
        +-------> Financeiro: Titulo a Receber (SE1)
        |
        +-------> Fiscal: Livro Fiscal de Saida (SF3)
        |
        +-------> NF-e: Transmissao SEFAZ (se nota eletronica)
```

**Variacoes do fluxo:**
- Venda direta: Nota fiscal sem pedido de venda previo
- Devolucao de venda: NF de entrada referenciando NF de saida original
- Complemento: NF complementar de preco ou imposto
- Bonificacao: Venda com valor zero ou desconto total
- Venda futura / Faturamento antecipado: Faturamento antes da entrega fisica
- Pedido de venda com entrega parcial: Liberacao e faturamento em lotes

## Tabelas Principais

| Tabela | Descricao | Chave Primaria | Indices Principais | Relacionamentos |
|---|---|---|---|---|
| SC5 | Cabecalho Pedido de Venda | C5_FILIAL+C5_NUM | C5_FILIAL+C5_NUM; C5_FILIAL+C5_CLIENTE+C5_LOJACLI+C5_NUM | SA1 (cliente), SE4 (condicao pagamento), SC6 (itens) |
| SC6 | Itens do Pedido de Venda | C6_FILIAL+C6_NUM+C6_ITEM+C6_PRODUTO | C6_FILIAL+C6_NUM+C6_ITEM; C6_FILIAL+C6_PRODUTO | SC5 (cabecalho), SB1 (produto), SC9 (liberacao) |
| SC9 | Liberacao de Pedidos | C9_FILIAL+C9_PEDIDO+C9_ITEM+C9_SEQUEN | C9_FILIAL+C9_PEDIDO+C9_ITEM; C9_FILIAL+C9_CLIENTE+C9_LOJA | SC5/SC6 (pedido), SA1 (cliente) |
| SF2 | Cabecalho NF de Saida | F2_FILIAL+F2_DOC+F2_SERIE+F2_CLIENTE+F2_LOJA+F2_TIPO | F2_FILIAL+F2_DOC+F2_SERIE; F2_FILIAL+F2_CLIENTE+F2_LOJA | SA1 (cliente), SD2 (itens), SE1 (titulo gerado) |
| SD2 | Itens da NF de Saida | D2_FILIAL+D2_DOC+D2_SERIE+D2_CLIENTE+D2_LOJA+D2_COD+D2_ITEM | D2_FILIAL+D2_DOC+D2_SERIE+D2_CLIENTE+D2_LOJA; D2_FILIAL+D2_COD | SF2 (cabecalho), SB1 (produto), SC6 (pedido origem) |
| SA1 | Cadastro de Clientes | A1_FILIAL+A1_COD+A1_LOJA | A1_FILIAL+A1_COD+A1_LOJA; A1_FILIAL+A1_NOME; A1_FILIAL+A1_CGC | AI0 (enderecos), SC5 (pedidos) |
| SA4 | Cadastro de Transportadoras | A4_FILIAL+A4_COD | A4_FILIAL+A4_COD; A4_FILIAL+A4_NOME | SF2 (notas fiscais) |
| DA0 | Cabecalho Tabela de Preco | DA0_FILIAL+DA0_CODTAB | DA0_FILIAL+DA0_CODTAB | DA1 (itens da tabela) |
| DA1 | Itens da Tabela de Preco | DA1_FILIAL+DA1_CODTAB+DA1_ITEM | DA1_FILIAL+DA1_CODTAB+DA1_CODPRO | DA0 (cabecalho), SB1 (produto) |
| SE4 | Condicoes de Pagamento | E4_FILIAL+E4_CODIGO | E4_FILIAL+E4_CODIGO | SC5 (pedidos), SF2 (notas) |
| SF4 | Tipo de Entrada e Saida (TES) | F4_FILIAL+F4_CODIGO | F4_FILIAL+F4_CODIGO | SD2 (itens NF), configuracao fiscal |

## Rotinas Padrao

| Codigo | Nome | Tipo |
|---|---|---|
| MATA410 | Pedido de Venda | Cadastro |
| MATA460 | Documento de Saida (NF) | Processo |
| MATA461 | Geracao de Notas Fiscais (a partir de pedidos liberados) | Processo |
| MATA116 | NF Manual de Saida | Cadastro |
| MATA465 | Devolucao de NF de Saida | Processo |
| MATA415 | Liberacao de Pedidos de Venda | Processo |
| OMSA010 | Consulta de Pedidos | Consulta |
| MATA010 | Cadastro de Clientes | Cadastro |
| OMSA040 | Tabela de Precos | Cadastro |
| FATA050 | Condicoes de Pagamento | Cadastro |
| MATR410 | Relatorio de Pedidos de Venda | Relatorio |
| MATR460 | Relatorio de Notas Fiscais de Saida | Relatorio |
| MATA462 | Cancelamento de NF de Saida | Processo |

## Pontos de Entrada

| PE | Quando Executa | Parametros | Tabelas Posicionadas |
|---|---|---|---|
| M410ALDT | Executado apos a alteracao de qualquer campo do item do Pedido de Venda (evento de saida do campo) | Nenhum parametro direto. Dados acessiveis via aCols (itens) e M-> (cabecalho). A variavel ReadVar() retorna o nome do campo alterado | SC5 (quando alteracao), dados do item via aCols |
| MTA410OK | Validacao geral (TudoOk) ao confirmar o Pedido de Venda. Retorno .T. permite gravacao, .F. impede | Nenhum parametro direto. Dados via M-> (cabecalho) e aCols (itens) | SC5 (quando alteracao), SC6 (quando alteracao) |
| A410INCPOS | Executado apos a inclusao completa do Pedido de Venda, quando todos os itens ja estao gravados | Nenhum parametro direto | SC5 posicionado no pedido recem incluido, SC6 posicionados nos itens |
| MT460FIM | Executado ao final do processo de geracao da NF de Saida a partir de pedidos liberados | PARAMIXB[1]: cDoc (numero da NF gerada), PARAMIXB[2]: cSerie | SF2 posicionada na NF gerada, SD2 posicionados nos itens |
| M460MARK | Executado na marcacao/desmarcacao de cada item na tela de geracao de NF de Saida | PARAMIXB[1]: nLinha (linha marcada/desmarcada) | SC9 posicionada no item de liberacao |
| A460NFSE1 | Executado apos a geracao do titulo financeiro (SE1) a partir da NF de Saida | Nenhum parametro direto | SE1 posicionada no titulo recem gerado, SF2 posicionada na NF |
| M460TODO | Executado ao usar o botao "Marcar Todos" na tela de geracao de NF de Saida | Nenhum parametro direto. Retorno .T. permite marcar todos, .F. impede | SC9 com dados da liberacao |
| A410PESO | Executado no calculo do peso do item do Pedido de Venda | Nenhum parametro direto. Peso atual disponivel via variavel de memoria | SB1 posicionado no produto do item |
| MTA410LK | Validacao de cada item (LinhaOk) do Pedido de Venda | Nenhum parametro direto. Dados do item via aCols, cabecalho via M-> | SC5 (quando alteracao), SB1 posicionado no produto |
| A410NOPV | Permite alterar a numeracao do Pedido de Venda na inclusao | Nenhum parametro direto. Retorno: cNumPV (novo numero). Se nao retornar, usa numeracao padrao | Nenhuma tabela posicionada |
| A460NFGR | Executado apos a gravacao completa da NF de Saida (todos os itens e cabecalho ja gravados) | PARAMIXB[1]: cDoc, PARAMIXB[2]: cSerie, PARAMIXB[3]: cCliente, PARAMIXB[4]: cLoja | SF2 e SD2 posicionados na NF gerada |
| A410TPNF | Permite alterar o tipo da nota fiscal que sera gerada a partir do Pedido de Venda | Nenhum parametro direto. Retorno: cTipo (tipo da NF) | SC5 posicionado no pedido |
| MT461FIM | Executado ao final da geracao de NF de Saida pela rotina MATA461 | PARAMIXB[1]: cDoc, PARAMIXB[2]: cSerie | SF2 posicionada na NF gerada |

## Integracoes

### Faturamento -> Estoque
- A emissao da NF de Saida gera automaticamente movimentacao de saida no estoque (SD3)
- O saldo do produto (SB2) eh reduzido pela quantidade faturada
- O custo medio eh usado para valorizar a saida (B2_CM1)
- A TES (SF4) define se o item movimenta estoque (F4_ESTOQUE = "S")
- Se o produto usa enderecamento (armazem WMS), eh necessario informar o endereco de saida

### Faturamento -> Financeiro
- A NF de Saida gera automaticamente titulo a receber (SE1)
- O desdobramento em parcelas segue a condicao de pagamento (SE4)
- A TES define se gera duplicata (F4_DUPLIC = "S")
- O titulo eh vinculado ao cliente (E1_CLIENTE+E1_LOJA) e ao documento (E1_NUM+E1_PREFIXO)

### Faturamento -> Fiscal
- A NF de Saida gera automaticamente lancamento no livro fiscal de saida (SF3)
- Os impostos sao calculados com base na TES, NCM, e regras de ICMS/IPI/PIS/COFINS
- O CFOP eh definido pela TES (F4_CF) e pode variar por estado (operacao interna vs interestadual)

### Faturamento -> NF-e
- Notas fiscais eletronicas sao transmitidas automaticamente para a SEFAZ
- O processo usa TSS (TOTVS Service SOA) ou SEFAZ direta
- Status da NF-e eh atualizado no campo F2_CHVNFE (chave de acesso)

## Regras de Negocio Comuns

### Limite de Credito
- Campo A1_LC armazena o limite de credito do cliente
- Campo A1_SALDUP armazena o saldo de duplicatas em aberto
- Credito disponivel = A1_LC - A1_SALDUP
- Parametro MV_VLCRED define se valida credito no pedido ou na liberacao
- Parametro MV_CREDITO define se bloqueia ou apenas avisa quando credito insuficiente

### Bloqueio de Cliente
- Campo A1_MSBLQL controla o bloqueio do cliente
- Cliente bloqueado nao permite inclusao de pedido ou emissao de NF
- Bloqueio pode ser manual ou automatico (ex: inadimplencia)

### Tabela de Precos (DA0/DA1)
- Tabelas de preco definem preco por produto, com vigencia por data
- Permite precos diferenciados por cliente, regiao, grupo
- Campo DA1_PRCVEN armazena o preco de venda
- Parametro MV_TABPVEN define a tabela de preco padrao
- Desconto maximo pode ser controlado por alcada

### Condicao de Pagamento (SE4)
- Define o desdobramento das parcelas (ex: 30/60/90 dias)
- Campo E4_COND armazena a regra de desdobramento
- Permite condicoes especiais: a vista, entrada + parcelas, etc.
- Usada tanto no pedido de venda quanto na NF de saida

### TES - Tipo de Entrada e Saida (SF4)
- Define o comportamento fiscal e de integracao de cada item
- F4_ESTOQUE: movimenta estoque (S/N)
- F4_DUPLIC: gera titulo financeiro (S/N)
- F4_CF: CFOP padrao
- F4_ICM: calcula ICMS (S/N)
- F4_IPI: calcula IPI (S/N)
- F4_PODER3: controle de poder de terceiros

### Regras Fiscais de Saida
- ICMS: Aliquota varia por estado (interna vs interestadual). Base de calculo pode ter reducao
- IPI: Aliquota definida pela NCM do produto. Pode ter suspensao ou isencao
- PIS/COFINS: Regime cumulativo ou nao-cumulativo conforme enquadramento da empresa
- ISS: Aplicavel a servicos, aliquota definida pelo municipio
- ICMS-ST: Substituicao tributaria na saida, com MVA e calculo diferenciado
- DIFAL: Diferencial de aliquota para vendas interestaduais a consumidor final

### Parametros MV_ Relevantes
| Parametro | Descricao | Valor Padrao |
|---|---|---|
| MV_VLCRED | Valida credito: 1=Pedido, 2=Liberacao, 3=NF | 1 |
| MV_CREDITO | Bloqueia (S) ou avisa (N) credito insuficiente | S |
| MV_TABPVEN | Tabela de preco padrao de venda | 001 |
| MV_LIBAPOV | Liberacao de pedido automatica ou por aprovacao | N |
| MV_TESSION | TES inteligente | N |
| MV_DESCSAI | Permite desconto na saida | S |
| MV_NOTFIS | Ultima nota fiscal de saida | (sequencial) |
| MV_LITEFAT | Permite faturamento parcial do pedido | S |
| MV_VENDPED | Vendedor obrigatorio no pedido | N |
| MV_RETEFAT | Retem impostos no faturamento | N |

## Padroes de Customizacao

### Cenario: Validacao customizada no Pedido de Venda
- **PE recomendado:** MTA410OK (validacao geral) e MTA410LK (validacao por item)
- **Abordagem:** Usar MTA410LK para validar cada item (ex: quantidade minima, produto liberado para o cliente). Usar MTA410OK para validacoes globais (ex: valor minimo do pedido, combinacao de itens)
- **Armadilha comum:** O MTA410OK executa quando o usuario clica em Confirmar. Se retornar .F., o usuario volta para a tela de edicao. Nao fazer operacoes de gravacao neste PE

### Cenario: Manipular NF de Saida apos geracao
- **PE recomendado:** MT460FIM ou A460NFGR
- **Abordagem:** Usar MT460FIM para logica apos geracao pela MATA460. Usar A460NFGR para logica apos gravacao completa. Ambos permitem acessar SF2/SD2 posicionados
- **Armadilha comum:** Nao confundir MATA460 (geracao a partir de pedidos) com MATA461 (geracao em lote). Para MATA461, usar MT461FIM

### Cenario: Customizar calculo de preco no pedido
- **PE recomendado:** M410ALDT
- **Abordagem:** Interceptar a alteracao do campo de quantidade ou produto e recalcular o preco com base em regras especificas (desconto progressivo, preco por faixa de quantidade)
- **Armadilha comum:** O M410ALDT executa a cada saida de campo. Verificar qual campo foi alterado via ReadVar() antes de processar para evitar execucoes desnecessarias

### Cenario: Integracao com titulo financeiro gerado
- **PE recomendado:** A460NFSE1
- **Abordagem:** Apos a geracao do titulo (SE1), complementar com informacoes adicionais (centro de custo, natureza, campos customizados)
- **Armadilha comum:** O titulo ja esta gravado quando o PE executa. Usar RecLock para alterar. Cuidado para nao alterar campos que afetem a integridade do titulo (valor, vencimento original)
