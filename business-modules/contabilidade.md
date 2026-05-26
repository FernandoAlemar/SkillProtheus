# Modulo de Contabilidade (CTB / SIGACTB)

## Visao Geral

O modulo de Contabilidade (SIGACTB) do TOTVS Protheus gerencia o plano de contas, lancamentos contabeis, balancetes, demonstracoes financeiras e obrigacoes contabeis. O codigo do modulo no Protheus eh **CTB** e o executavel padrao eh **SIGACTB**.

Este modulo eh responsavel por:
- Manutencao do plano de contas
- Lancamentos contabeis manuais e automaticos
- Geracao de balancete e razao contabil
- Demonstracao de Resultados do Exercicio (DRE)
- Balanco Patrimonial
- Controle de centros de custo
- Geracao do SPED Contabil (ECD)
- Apuracao de resultado do exercicio
- Conciliacao contabil
- Orcamento contabil

## Fluxo Principal

```
Plano de Contas (CT1)
        |
        +---> Centros de Custo (CTT)
        +---> Entidades Contabeis (CTS - item contabil, classe valor)
        |
        v
  Lancamentos Contabeis (CT2)
        |
        +---> Lancamentos manuais (CTBA102)
        +---> Lancamentos automaticos via LP (modulos integrados)
        +---> Lancamentos por lote/importacao
        |
        v
  Consultas e Relatorios
        |
        +---> Balancete (CTBA200)
        +---> Razao Contabil (CTBA210)
        +---> DRE
        +---> Balanco Patrimonial
        |
        v
  Apuracao de Resultado
        |
        v
  Demonstracoes Contabeis + SPED Contabil (ECD)
```

**Variacoes do fluxo:**
- Lancamento padrao (LP): Modulos geram lancamentos automaticos usando formulas pre-configuradas
- Lancamento de encerramento: Zeramento das contas de resultado no final do exercicio
- Lancamento de abertura: Transferencia de saldos do exercicio anterior
- Lancamentos entre filiais: Contabilidade centralizada ou descentralizada
- Multi-moeda: Lancamentos em moeda estrangeira com conversao

## Tabelas Principais

| Tabela | Descricao | Chave Primaria | Indices Principais | Relacionamentos |
|---|---|---|---|---|
| CT1 | Plano de Contas | CT1_FILIAL+CT1_CONTA | CT1_FILIAL+CT1_CONTA; CT1_FILIAL+CT1_DESC | CT2 (lancamentos), CTS (entidades) |
| CT2 | Lancamentos Contabeis | CT2_FILIAL+CT2_LOTE+CT2_SBLOTE+CT2_DOC+CT2_LINHA | CT2_FILIAL+CT2_LOTE+CT2_SBLOTE+CT2_DOC; CT2_FILIAL+CT2_DATA+CT2_DEBITO; CT2_FILIAL+CT2_DATA+CT2_CREDIT | CT1 (contas debito/credito), CTT (centro custo), CTH (historico) |
| CT5 | Lancamentos Padrao (LP) | CT5_FILIAL+CT5_LPADRAO+CT5_SEQUEN | CT5_FILIAL+CT5_LPADRAO | CT1 (contas), formulas de lancamento |
| CTT | Centros de Custo | CTT_FILIAL+CTT_CUSTO | CTT_FILIAL+CTT_CUSTO; CTT_FILIAL+CTT_DESC01 | CT2 (lancamentos), CT1 (contas) |
| CTS | Entidades Contabeis | CTS_FILIAL+CTS_ENTIDA+CTS_CODIGO | CTS_FILIAL+CTS_ENTIDA+CTS_CODIGO | CT2 (lancamentos) |
| CTH | Historico Padrao | CTH_FILIAL+CTH_CODIGO | CTH_FILIAL+CTH_CODIGO | CT2 (lancamentos) |
| CV0 | Orcamento Contabil | CV0_FILIAL+CV0_CONTA+CV0_CC+CV0_PERIOD | CV0_FILIAL+CV0_CONTA+CV0_CC | CT1 (conta), CTT (centro custo) |
| CT9 | Saldos Contabeis | CT9_FILIAL+CT9_CONTA+CT9_DATA | CT9_FILIAL+CT9_CONTA+CT9_DATA | CT1 (conta) |

## Rotinas Padrao

| Codigo | Nome | Tipo |
|---|---|---|
| CTBA010 | Plano de Contas | Cadastro |
| CTBA102 | Lancamentos Contabeis | Cadastro |
| CTBA200 | Balancete | Relatorio |
| CTBA210 | Razao Contabil | Relatorio |
| CTBA500 | Apuracao de Resultado | Processo |
| CTBA105 | Lancamento Padrao (LP) | Cadastro |
| CTBA012 | Centros de Custo | Cadastro |
| CTBA015 | Entidades Contabeis | Cadastro |
| CTBA380 | Conciliacao Contabil | Processo |
| CTBA520 | Encerramento do Exercicio | Processo |
| CTBA530 | Lancamento de Abertura | Processo |
| CTBA400 | Orcamento Contabil | Cadastro |
| SPEDECD | SPED Contabil (ECD) | Processo |
| CTBR200 | Balanco Patrimonial | Relatorio |
| CTBR210 | DRE - Demonstracao de Resultado | Relatorio |

## Pontos de Entrada

| PE | Quando Executa | Parametros | Tabelas Posicionadas |
|---|---|---|---|
| CT100VALID | Validacao na inclusao/alteracao de conta no plano de contas | Nenhum parametro direto. Dados via M-> (campos da conta). Retorno .T. permite, .F. impede | CT1 (quando alteracao) |
| CT102INCL | Executado apos a inclusao de lancamento contabil | Nenhum parametro direto | CT2 posicionada no lancamento recem incluido |
| CT200FIM | Executado ao final da geracao do balancete, permite manipular o resultado | Nenhum parametro direto | Dados do balancete disponiveis em arrays internos |
| CT500POST | Executado apos a apuracao de resultado, permite acoes complementares | Nenhum parametro direto | CT2 posicionado no lancamento de apuracao gerado |
| CTBA102TOK | Validacao geral (TudoOk) na confirmacao do lancamento contabil | Nenhum parametro direto. Dados via M-> (cabecalho) e aCols (linhas do lancamento) | CT2 (quando alteracao) |
| CT102VALID | Validacao customizada de cada linha do lancamento contabil | Nenhum parametro direto. Dados da linha via aCols | CT1 posicionada na conta sendo lancada |
| CT102GRV | Executado apos a gravacao de cada linha do lancamento contabil | Nenhum parametro direto | CT2 posicionada na linha recem gravada |
| CT520POST | Executado apos o encerramento do exercicio | Nenhum parametro direto | CT2 posicionado nos lancamentos de encerramento gerados |
| CT530POST | Executado apos a geracao dos lancamentos de abertura | Nenhum parametro direto | CT2 posicionado nos lancamentos de abertura gerados |
| CT380FIM | Executado ao final da conciliacao contabil | Nenhum parametro direto | CT2 posicionados nos lancamentos conciliados |
| SPEDECDREG | Executado durante a geracao do SPED Contabil para cada registro, permite ajustes | PARAMIXB[1]: cRegistro (tipo do registro ECD), PARAMIXB[2]: cLinha (conteudo) | CT2 posicionada no lancamento sendo exportado |
| CTBA105LP | Executado durante a execucao do lancamento padrao (LP) automatico | PARAMIXB[1]: cLP (codigo do LP), PARAMIXB[2]: nValor (valor calculado) | Tabela origem posicionada (varia conforme modulo que acionou o LP) |

## Integracoes

### Financeiro -> Contabilidade
- Baixas de titulos (SE5) geram lancamentos contabeis via LP
- Inclusao de titulos pode gerar lancamento de provisao
- Juros, multas e descontos geram lancamentos contabeis separados
- LP tipicos: 503 (baixa a receber), 504 (baixa a pagar), 511 (juros), 512 (descontos)

### Estoque -> Contabilidade
- Movimentacoes de estoque (SD3) geram lancamentos contabeis via LP
- Entrada: Debito na conta de estoque, credito na conta de fornecedor/transito
- Saida: Debito na conta de custo (CMV), credito na conta de estoque
- LP tipicos: 200 (entrada), 201 (saida), 210 (transferencia)

### Fiscal -> Contabilidade
- Apuracao de impostos gera lancamentos de provisao
- Pagamento de guias gera lancamento de baixa da provisao
- LP tipicos: 300 (ICMS a recolher), 301 (IPI a recolher), 310 (PIS), 311 (COFINS)

### Faturamento -> Contabilidade
- NF de Saida gera lancamento de receita (credito) e contas a receber (debito)
- LP tipicos: 500 (faturamento saida)

### Compras -> Contabilidade
- NF de Entrada gera lancamento de estoque (debito) e contas a pagar (credito)
- LP tipicos: 100 (entrada de material)

## Regras de Negocio Comuns

### Partida Dobrada
- Todo lancamento contabil deve ter debito igual ao credito
- Validacao automatica pelo sistema: soma de debitos deve igualar soma de creditos
- Lancamento desbalanceado nao eh permitido

### Centro de Custo Obrigatorio
- Contas de resultado (receita e despesa) normalmente exigem centro de custo
- Configuracao via campo CT1_CCUSTO (S=Obrigatorio, N=Nao usa)
- Permite rateio entre multiplos centros de custo

### Alocacao Automatica (Rateio)
- Lancamentos podem ser rateados automaticamente entre centros de custo
- Configuracao via tabela de rateio (CTF)
- Percentuais de rateio devem somar 100%
- Usado tipicamente para despesas compartilhadas (aluguel, energia, etc.)

### Lancamento Padrao (LP)
- Formulas pre-configuradas que geram lancamentos automaticos
- Definidos na tabela CT5 com sequencia de debitos e creditos
- Usam variaveis do contexto (valor NF, valor titulo, etc.)
- Cada modulo tem seus LPs especificos (serie 100 para compras, 200 para estoque, 500 para financeiro)
- LP pode ter condicao de execucao (formula que retorna .T. ou .F.)

### Conciliacao Contabil
- Processo de verificacao de saldos entre contabilidade e modulos de origem
- Compara saldo contabil com saldo do modulo (financeiro, estoque, etc.)
- Divergencias indicam lancamentos faltantes ou incorretos

### Periodos Contabeis
- Parametro MV_ULMES define o ultimo mes fechado
- Lancamentos em periodos fechados nao sao permitidos
- Encerramento do exercicio zera contas de resultado e transfere para patrimonio liquido
- Abertura do exercicio seguinte copia saldos patrimoniais

### Parametros MV_ Relevantes
| Parametro | Descricao | Valor Padrao |
|---|---|---|
| MV_ULMES | Ultimo mes de fechamento contabil | (data) |
| MV_MOTEFIN | Moeda padrao da contabilidade | 1 |
| MV_ABORCTB | Aborta operacao se contabilizacao falhar | N |
| MV_CONTBIL | Ativa contabilizacao automatica | S |
| MV_CENTCST | Centro de custo obrigatorio em contas de resultado | S |
| MV_CTLOTE | Controle de lote contabil | S |
| MV_CTALIAS | Permite alias de conta contabil | N |
| MV_CTABCZ | Balancete exibe contas com saldo zero | N |
| MV_MESSION | Mascara do plano de contas | (mascara) |
| MV_CTMKCC | Mascara do centro de custo | (mascara) |
| MV_CONTSB | Conta contabil de estoque (padrao SB1) | S |
| MV_INTCTB | Integracao contabil online | S |

## Padroes de Customizacao

### Cenario: Validacao customizada no lancamento contabil
- **PE recomendado:** CTBA102TOK (geral) e CT102VALID (por linha)
- **Abordagem:** CTBA102TOK para validar o lancamento completo (ex: valor minimo, tipo de documento). CT102VALID para validar cada linha (ex: conta compativel com centro de custo, conta permite lancamento direto)
- **Armadilha comum:** O lancamento contabil deve sempre estar balanceado. Nao usar o PE para alterar valores sem garantir que debito = credito

### Cenario: Complementar lancamento automatico (LP)
- **PE recomendado:** CTBA105LP
- **Abordagem:** Interceptar a execucao do LP para ajustar valores, incluir centro de custo, ou adicionar entidades contabeis extras
- **Armadilha comum:** O LP eh executado por outros modulos automaticamente. Alterar o valor sem ajustar a contrapartida causa desbalanceamento. Sempre testar com lancamentos de todos os modulos integrados

### Cenario: Ajustar relatorio de balancete
- **PE recomendado:** CT200FIM
- **Abordagem:** Manipular os dados do balancete apos a geracao para incluir informacoes adicionais ou alterar a apresentacao
- **Armadilha comum:** Este PE eh de pos-processamento. Para alterar a selecao de dados, considerar parametros de filtro da propria rotina

### Cenario: Customizar SPED Contabil (ECD)
- **PE recomendado:** SPEDECDREG
- **Abordagem:** Ajustar registros do SPED Contabil antes de gravar no arquivo. Util para incluir informacoes complementares ou ajustar dados
- **Armadilha comum:** O layout da ECD eh validado pelo PVA da Receita Federal. Alteracoes devem respeitar o schema oficial
