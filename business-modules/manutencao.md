# Modulo de Manutencao de Ativos (MNT / SIGAMNT)

## Visao Geral

O modulo de Manutencao de Ativos (SIGAMNT) do TOTVS Protheus gerencia o ciclo de vida dos equipamentos e ativos da empresa, incluindo planos de manutencao preventiva, ordens de servico corretivas e indicadores de desempenho. O codigo do modulo no Protheus eh **MNT** e o executavel padrao eh **SIGAMNT**.

Este modulo eh responsavel por:
- Cadastro e hierarquia de equipamentos/ativos
- Planos de manutencao preventiva e preditiva
- Geracao e controle de ordens de servico (OS)
- Planejamento de recursos (mao de obra, pecas, ferramentas)
- Execucao e apontamento de servicos
- Encerramento e historico de manutencoes
- Calculo de indicadores (MTBF, MTTR, disponibilidade)
- Controle de custos de manutencao
- Calendario de paradas programadas

## Fluxo Principal

```
Cadastro de Equipamento (STG/STO)
        |
        +---> Hierarquia: Planta > Area > Linha > Equipamento > Componente
        |
        v
  Plano de Manutencao Preventiva (STK)
        |
        +---> Periodicidade (tempo, horimetro, contador)
        +---> Checklist de servicos
        +---> Pecas e materiais previstos
        |
        v
  Geracao de Ordem de Servico (ST9)
        |
        +---> Automatica (preventiva conforme plano)
        +---> Manual (corretiva por solicitacao)
        +---> Preditiva (baseada em condicao/medicao)
        |
        v
  Planejamento da OS
        |
        +---> Alocacao de tecnicos (STJ)
        +---> Reserva de pecas (estoque)
        +---> Programacao de parada
        |
        v
  Execucao da OS
        |
        +---> Apontamento de horas trabalhadas (STJ)
        +---> Consumo de pecas e materiais (requisicao estoque)
        +---> Registro de servicos executados
        |
        v
  Encerramento da OS
        |
        +---> Calculo de custo total (mao de obra + pecas + servicos terceiros)
        +---> Atualizacao de historico do equipamento
        +---> Atualizacao de indicadores (MTBF, MTTR)
```

**Variacoes do fluxo:**
- Manutencao corretiva emergencial: OS gerada diretamente sem planejamento previo
- Manutencao preditiva: OS gerada com base em medicoes e analises de condicao
- Parada programada: Conjunto de OS executadas durante parada planejada
- OS com servico terceirizado: Parte ou toda a execucao por empresa externa
- Lubrificacao e inspecao: OS simplificada para rotinas rapidas

## Tabelas Principais

| Tabela | Descricao | Chave Primaria | Indices Principais | Relacionamentos |
|---|---|---|---|---|
| ST9 | Ordens de Servico | T9_FILIAL+T9_CODBEM+T9_ORDEM | T9_FILIAL+T9_CODBEM+T9_ORDEM; T9_FILIAL+T9_ORDEM; T9_FILIAL+T9_DTPREV | STG (equipamento), STJ (apontamentos), STO (componentes) |
| STJ | Apontamentos de Mao de Obra / Insumos da OS | TJ_FILIAL+TJ_ORDEM+TJ_SEQMAN | TJ_FILIAL+TJ_ORDEM+TJ_SEQMAN; TJ_FILIAL+TJ_CODFUN | ST9 (OS), SRA (funcionario) |
| STO | Componentes do Equipamento | TO_FILIAL+TO_CODBEM+TO_ITEM | TO_FILIAL+TO_CODBEM+TO_ITEM | STG (equipamento pai), SB1 (produto/peca) |
| STK | Planos de Manutencao Preventiva | TK_FILIAL+TK_CDPREV+TK_SEQPRE | TK_FILIAL+TK_CDPREV; TK_FILIAL+TK_CODBEM | STG (equipamento), ST9 (OS geradas) |
| QO3 | Solicitacoes de Servico | QO3_FILIAL+QO3_NUMSS | QO3_FILIAL+QO3_NUMSS; QO3_FILIAL+QO3_CODBEM | STG (equipamento), ST9 (OS gerada) |
| STG | Cadastro de Bens / Equipamentos | TG_FILIAL+TG_CODBEM | TG_FILIAL+TG_CODBEM; TG_FILIAL+TG_DESCRI | STO (componentes), ST9 (OS), STK (planos) |
| STI | Especialidades de Manutencao | TI_FILIAL+TI_CODESP | TI_FILIAL+TI_CODESP | STJ (apontamentos) |
| STH | Servicos Padrao de Manutencao | TH_FILIAL+TH_CODSER | TH_FILIAL+TH_CODSER | STK (planos), ST9 (OS) |
| STL | Calendario de Manutencao | TL_FILIAL+TL_DATA+TL_CODBEM | TL_FILIAL+TL_DATA; TL_FILIAL+TL_CODBEM | STG (equipamento) |

## Rotinas Padrao

| Codigo | Nome | Tipo |
|---|---|---|
| MNTA010 | Cadastro de Bens/Equipamentos | Cadastro |
| MNTA400 | Ordem de Servico | Cadastro |
| MNTA430 | Apontamento de OS | Processo |
| MNTA450 | Encerramento de OS | Processo |
| MNTA440 | Planejamento de OS | Processo |
| MNTA100 | Plano de Manutencao Preventiva | Cadastro |
| MNTA110 | Geracao Automatica de OS Preventiva | Processo |
| MNTA200 | Solicitacao de Servico | Cadastro |
| MNTA015 | Cadastro de Servicos Padrao | Cadastro |
| MNTA020 | Especialidades de Manutencao | Cadastro |
| MNTA460 | Consulta de Historico de OS | Consulta |
| MNTR400 | Relatorio de Ordens de Servico | Relatorio |
| MNTR450 | Relatorio de Indicadores (MTBF/MTTR) | Relatorio |
| MNTA470 | Calendario de Manutencao | Consulta |

## Pontos de Entrada

| PE | Quando Executa | Parametros | Tabelas Posicionadas |
|---|---|---|---|
| MT400LOK | Validacao de cada item (LinhaOk) na inclusao/alteracao da Ordem de Servico | Nenhum parametro direto. Dados via M-> (cabecalho OS) e aCols (itens/insumos) | ST9 (quando alteracao), STG posicionado no equipamento |
| MT430OK | Validacao geral (TudoOk) na confirmacao do apontamento de OS | Nenhum parametro direto. Dados via M-> (campos do apontamento) | ST9 posicionada na OS, STJ (quando alteracao) |
| MT450FIM | Executado ao final do encerramento da OS, apos todas as gravacoes | Nenhum parametro direto | ST9 posicionada na OS encerrada, STJ posicionados nos apontamentos |
| MT440TOK | Validacao geral (TudoOk) na confirmacao do planejamento da OS | Nenhum parametro direto. Dados via M-> e aCols | ST9 posicionada na OS sendo planejada |
| A400GRAV | Executado apos a gravacao da Ordem de Servico (inclusao ou alteracao) | Nenhum parametro direto. Operacao identificavel via INCLUI/ALTERA | ST9 posicionada na OS recem gravada |
| A400MENU | Permite incluir opcoes extras no menu de contexto da OS | Nenhum parametro direto. Retorno: array bidimensional {cTitulo, bBloco} | ST9 posicionada na OS selecionada |
| MT400TOK | Validacao geral (TudoOk) ao confirmar a inclusao/alteracao da OS | Nenhum parametro direto. Dados via M-> (cabecalho) e aCols (itens) | ST9 (quando alteracao), STG posicionado no equipamento |
| A430GRAV | Executado apos a gravacao do apontamento de OS | Nenhum parametro direto | STJ posicionada no apontamento gravado, ST9 posicionada na OS |
| A450GRAV | Executado apos a gravacao do encerramento, antes da finalizacao completa | Nenhum parametro direto | ST9 posicionada na OS sendo encerrada |
| MT110GER | Executado durante a geracao automatica de OS preventiva para cada plano processado | PARAMIXB[1]: cCdPrev (codigo do plano preventivo) | STK posicionada no plano, STG posicionado no equipamento |
| A200GRAV | Executado apos a gravacao da solicitacao de servico | Nenhum parametro direto | QO3 posicionada na solicitacao gravada |
| MT200TOK | Validacao geral na confirmacao da solicitacao de servico | Nenhum parametro direto. Dados via M-> | QO3 (quando alteracao) |

## Integracoes

### Manutencao -> Estoque
- A OS pode requisitar pecas e materiais diretamente do estoque
- A requisicao gera movimentacao de saida (SD3 tipo RE) no estoque
- O custo das pecas eh incorporado ao custo total da OS
- Pecas devolvidas geram movimentacao de devolucao (SD3 tipo DE)

### Manutencao -> Compras
- Quando a peca necessaria nao tem saldo em estoque, a OS pode gerar solicitacao de compra (SC1)
- A solicitacao segue o fluxo normal de compras (cotacao, pedido, NF entrada)
- Apos o recebimento, a peca eh requisitada para a OS

### Manutencao -> Financeiro
- Servicos terceirizados podem gerar titulo a pagar (SE2)
- O custo de mao de obra externa eh vinculado a OS

### Manutencao -> Contabilidade
- O encerramento da OS pode gerar lancamentos contabeis
- Custo de manutencao debitado no centro de custo do equipamento
- Contabilizacao via LP (lancamento padrao) especifico do modulo MNT

## Regras de Negocio Comuns

### Manutencao Preventiva vs Corretiva
- **Preventiva:** Planejada com antecedencia, baseada em periodicidade (tempo, horimetro, ciclos). Objetivo: evitar falhas
- **Corretiva:** Executada apos a ocorrencia de falha. Pode ser emergencial (nao planejada) ou programada (falha identificada mas sem urgencia)
- **Preditiva:** Baseada em monitoramento de condicao (vibracao, temperatura, analise de oleo). Objetivo: intervir no momento ideal
- Campo T9_TPMANT na OS identifica o tipo: P=Preventiva, C=Corretiva, D=Preditiva

### Criticidade do Equipamento
- Campo TG_PRIOR no cadastro do equipamento define a criticidade: A=Alta, B=Media, C=Baixa
- Equipamentos criticos (A) tem prioridade na alocacao de recursos e prazos menores de atendimento
- A criticidade influencia o calculo de prioridade da OS
- Pode ser usada para definir SLAs internos de atendimento

### Custo da OS
- Custo total da OS = Mao de obra interna + Pecas/materiais + Servicos terceiros
- Mao de obra interna: Horas apontadas (STJ) x Valor hora do tecnico
- Pecas/materiais: Custo medio do estoque x Quantidade consumida
- Servicos terceiros: Valor do contrato ou NF de servico
- O custo eh acumulado no campo T9_VLRTOT da OS
- Relatorios de custo por equipamento, area, tipo de manutencao

### Disponibilidade e Indicadores
- **MTBF (Mean Time Between Failures):** Tempo medio entre falhas. Calculado pela soma dos tempos de funcionamento dividido pelo numero de falhas
- **MTTR (Mean Time To Repair):** Tempo medio de reparo. Calculado pela soma dos tempos de reparo dividido pelo numero de reparos
- **Disponibilidade:** MTBF / (MTBF + MTTR) x 100%
- Indicadores calculados com base no historico de OS encerradas
- Acompanhamento por equipamento, area e periodo

### Status da OS
A OS possui ciclo de vida controlado pelo campo T9_STATUS:
- 01 = Aberta (aguardando planejamento)
- 02 = Planejada (recursos alocados)
- 03 = Em execucao (trabalho em andamento)
- 04 = Encerrada (concluida)
- 05 = Cancelada
- A transicao entre status segue regras de negocio e pode exigir aprovacao

### Parametros MV_ Relevantes
| Parametro | Descricao | Valor Padrao |
|---|---|---|
| MV_MNTTPOS | Tipo de OS padrao (P=Preventiva, C=Corretiva) | C |
| MV_MNTPRIO | Prioridade padrao da OS | 3 |
| MV_MNTALOC | Permite alocacao automatica de tecnicos | S |
| MV_MNTREQ | Gera requisicao automatica de pecas | S |
| MV_MNTCUST | Calcula custo automatico no encerramento | S |
| MV_MNTHIST | Grava historico automatico | S |
| MV_MNTPREV | Dias de antecedencia para geracao de preventiva | 7 |
| MV_MNTSOL | Exige solicitacao para abrir OS corretiva | N |
| MV_MNTENCE | Permite encerrar OS sem apontamento | N |
| MV_MNTGOS | Geracao automatica de OS preventiva | S |

## Padroes de Customizacao

### Cenario: Validacao customizada na abertura de OS
- **PE recomendado:** MT400TOK (validacao geral) e MT400LOK (validacao por item)
- **Abordagem:** MT400TOK para validar a OS como um todo (ex: equipamento disponivel, tecnico habilitado para o tipo de servico). MT400LOK para validar cada insumo ou servico da OS
- **Armadilha comum:** A OS pode ser gerada automaticamente pela preventiva (MNTA110). Nesse caso, o PE de validacao da tela nao executa. Para validar OS automaticas, usar MT110GER

### Cenario: Acoes automaticas no encerramento de OS
- **PE recomendado:** MT450FIM
- **Abordagem:** Apos o encerramento, executar acoes como: enviar notificacao ao solicitante, atualizar indicadores customizados, gerar relatorio automatico, integrar com sistema externo
- **Armadilha comum:** O encerramento ja esta gravado quando o PE executa. Nao tentar reverter o encerramento dentro do PE. Para impedir o encerramento, usar validacao antes (ex: via workflow)

### Cenario: Complementar apontamento de OS
- **PE recomendado:** A430GRAV
- **Abordagem:** Apos gravar o apontamento, complementar com dados extras (ex: codigo de falha detalhado, fotos, observacoes tecnicas em tabela auxiliar)
- **Armadilha comum:** O apontamento (STJ) ja esta gravado. Usar RecLock para alterar. Cuidado com campos que afetam o custo (horas, valor)

### Cenario: Customizar geracao de OS preventiva
- **PE recomendado:** MT110GER
- **Abordagem:** Interceptar a geracao automatica para ajustar dados da OS (ex: prioridade baseada em historico, alocacao automatica de tecnico por especialidade)
- **Armadilha comum:** O PE executa para cada plano preventivo processado. A OS ainda nao esta gravada neste ponto - os dados estao sendo preparados. Manipular os dados antes da gravacao
