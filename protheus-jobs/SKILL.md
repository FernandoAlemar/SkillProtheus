---
name: protheus-jobs
description: >
  Padroes para criacao de Jobs e processos agendados no Protheus (ADVPL/TLPP).
  Use esta skill SEMPRE que o usuario pedir para criar, corrigir ou revisar Jobs,
  Schedules, processos batch, rotinas sem interface, processos agendados,
  ou qualquer funcao que roda via Scheduler do Protheus. Inclui arquitetura
  obrigatoria de 3 camadas (Entry+Lock+Worker), controle de concorrencia com
  LockByName, log estruturado com FwLogMsg, multi-thread com FWIPCWait,
  e anti-patterns criticos como credenciais hardcoded e RecLock sem verificacao.
---


---

## ARQUITETURA OBRIGATORIA: 3 CAMADAS

Todo Job DEVE seguir a separacao em 3 funcoes. Isso nao e sugestao, e o
padrao recomendado para Jobs Protheus.

```
User Function <NOME>(aDadosSistema)    CAMADA 1 - Entry Point + Environment
   |
   +-> Static Function PROC_<NOME>()   CAMADA 2 - Lock + Orquestrador
   |      |
   |      +-> Static Function WORKER_<NOME>()  CAMADA 3 - Logica de Negocio
   |
   +-> RpcClearEnv()                    Cleanup condicional
```

**Por que 3 camadas:**
- Camada 1 isola o setup/teardown de ambiente. Se algo falhar no RpcSetEnv,
  a camada 2 nunca executa.
- Camada 2 isola o lock. Se o Job ja esta rodando, a camada 3 nunca executa.
- Camada 3 contem apenas logica de negocio. Pode ser testada manualmente
  (via SmartClient) sem precisar do Scheduler.

---

## TEMPLATE COMPLETO

```advpl
#Include "totvs.ch"
#Include "tlpp-core.th"
#Include "topconn.ch"

namespace custom.<projeto>.job.<modulo>

//================================================================
/*/{Protheus.doc} <NOME_JOB>
<Descricao clara do que o Job faz em uma linha>

@param aDadosSistema Array com [1] = Empresa, [2] = Filial
@author <nome>
@since <DD/MM/AAAA>
/*/
//================================================================
User Function <NOME_JOB>(aDadosSistema as array)

    Local lJob := .F.

    If GetRemoteType() == -1 .OR. (!Type("cFilAnt") == "C" .AND. !TCIsConnected())
        lJob := .T.
        RpcClearEnv()
        ConOut("U_<NOME_JOB> via SCHEDULER, iniciando....")
        RpcSetEnv(aDadosSistema[1], aDadosSistema[2],,,,'<MODULO>')
    Endif

    PROC_<NOME>()

    If lJob
        RpcClearEnv()
        ConOut("U_<NOME_JOB> via SCHEDULER, finalizado....")
    Endif

Return

//================================================================
/*/{Protheus.doc} PROC_<NOME>
Controlador de execucao e lock da rotina.
/*/
//================================================================
Static Function PROC_<NOME>()

    Local cLockName := "<NOME_JOB>" + Alltrim(SM0->M0_CODIGO) + Alltrim(SM0->M0_CODFIL)
    Private lMsErroAuto    := .F.
    Private lMsHelpAuto    := .F.
    Private lAutoErrNoFile := .T.

    If !LockByName(cLockName, .F., .F., .T.)
        FwLogMsg("WARNING", /*cTransactionId*/, "U_<NOME_JOB>", FunName(), ;
            "", "01", "Job ja em execucao por outro processo.", 0, 0, {})
        Return
    EndIf

    FwLogMsg("INFO", /*cTransactionId*/, "U_<NOME_JOB>", FunName(), ;
        "", "01", "Iniciando processamento.", 0, 0, {})

    WORKER_<NOME>()

    FwLogMsg("INFO", /*cTransactionId*/, "U_<NOME_JOB>", FunName(), ;
        "", "01", "Finalizando processamento.", 0, 0, {})

    UnLockByName(cLockName, .F., .F., .T.)

Return

//================================================================
/*/{Protheus.doc} WORKER_<NOME>
Logica de negocio do Job.
/*/
//================================================================
Static Function WORKER_<NOME>()

    Local aArea        := FWGetArea()
    Local cAliasQry    := ""
    Local cQuery       := ""
    Local cLogMsg      := ""
    Local nProcessados := 0
    Local nErros       := 0

    // Parametros via SX6 - NUNCA hardcoded
    Local cParam1 := SuperGetMV("<PRJ>_PARAM1", .F., "<default>")

    // Validacao obrigatoria de parametros
    If Empty(cParam1)
        FwLogMsg("ERROR", /*cTransactionId*/, "U_<NOME_JOB>", FunName(), ;
            "", "01", "Parametros nao configurados.", 0, 0, {})
        FWRestArea(aArea)
        Return
    EndIf

    // Query de registros pendentes
    cQuery := " SELECT ... "
    cQuery += " FROM " + RetSqlName("<TABELA>") + " T1 "
    cQuery += " WHERE T1.<CAMPO_STATUS> = '<PENDENTE>' "
    cQuery += "   AND T1.D_E_L_E_T_ = '' "

    cAliasQry := MPSysOpenQuery(ChangeQuery(cQuery))
    (cAliasQry)->(DbGoTop())

    While !(cAliasQry)->(Eof())

        cLogMsg := "<identificador>: " + AllTrim((cAliasQry)-><CAMPO>)

        Begin Sequence

            lMsErroAuto := .F.

            // --- Logica de negocio aqui ---
            // MSExecAuto, RecLock, chamadas de API, etc.

            If lMsErroAuto
                nErros++
                FwLogMsg("ERROR", /*cTransactionId*/, "U_<NOME_JOB>", ;
                    FunName(), "<ROTINA>", "01", ;
                    "Erro. " + cLogMsg + " " + AutoGrLogToStr(), ;
                    0, 0, GetAutoGrLog())
                Break
            EndIf

            // Transacao para updates de status
            Begin Transaction

                If !RecLock("<TABELA>", .F.)
                    FwLogMsg("ERROR", /*cTransactionId*/, "U_<NOME_JOB>", ;
                        FunName(), "", "01", ;
                        "Falha no RecLock. " + cLogMsg, 0, 0, {})
                    DisarmTransaction()
                    Break
                EndIf

                <TABELA>-><CAMPO_STATUS> := '<PROCESSADO>'
                <TABELA>->(MsUnlock())

            End Transaction

            nProcessados++
            FwLogMsg("INFO", /*cTransactionId*/, "U_<NOME_JOB>", ;
                FunName(), "", "01", ;
                "Sucesso. " + cLogMsg, 0, 0, {})

        End Sequence

        (cAliasQry)->(DbSkip())
    EndDo

    // Cleanup de aliases
    (cAliasQry)->(DbCloseArea())

    // Totalizadores
    FwLogMsg("INFO", /*cTransactionId*/, "U_<NOME_JOB>", FunName(), ;
        "", "01", ;
        "Concluido. Processados: " + cValToChar(nProcessados) + ;
        " | Erros: " + cValToChar(nErros), 0, 0, {})

    FWRestArea(aArea)

Return
```

---

## FUNCAO AUXILIAR: AutoGrLogToStr

Muitos Jobs precisam extrair o log do MSExecAuto em string. Inclua esta
funcao auxiliar no fonte (ou em uma lib compartilhada):

```advpl
//================================================================
/*/{Protheus.doc} AutoGrLogToStr
Converte o array de log do MSExecAuto em string unica.
/*/
//================================================================
Static Function AutoGrLogToStr()
    Local aLog   := GetAutoGrLog()
    Local cRet   := ""
    Local nI     := 0

    For nI := 1 To Len(aLog)
        cRet += aLog[nI] + CRLF
    Next nI

Return cRet
```

---

## REGRAS OBRIGATORIAS

### R01 - Deteccao de contexto Job

SEMPRE use esta verificacao. E a mais robusta, cobre tanto execucao via
Scheduler quanto StartJob/CallProc:

```advpl
If GetRemoteType() == -1 .OR. (!Type("cFilAnt") == "C" .AND. !TCIsConnected())
```

NAO use `Type("cEmpAnt") == "U"` nem `Select("SX6") <= 0` - sao
alternativas menos confiaveis.

### R02 - RpcClearEnv ANTES do RpcSetEnv

Sempre limpe estado residual antes de abrir o ambiente:

```advpl
RpcClearEnv()
RpcSetEnv(aDadosSistema[1], aDadosSistema[2],,,,'<MODULO>')
```

### R03 - Parametros do Scheduler via array, NUNCA hardcoded

O Scheduler do Protheus (CFGA020) envia empresa/filial no array `aDadosSistema`.
NUNCA escreva empresa/filial/usuario/senha no fonte:

```advpl
// ERRADO - credenciais expostas no fonte
RpcSetEnv("01", "99", "usuario_real", "SenhaAqui123")

// CERTO - recebe do Scheduler
RpcSetEnv(aDadosSistema[1], aDadosSistema[2],,,,'FAT')
```

### R04 - LockByName com empresa+filial no nome

O nome do lock DEVE incluir empresa e filial para permitir execucao
simultanea em filiais diferentes sem colisao:

```advpl
Local cLockName := "<NOME_JOB>" + Alltrim(SM0->M0_CODIGO) + Alltrim(SM0->M0_CODFIL)
If !LockByName(cLockName, .F., .F., .T.)
    FwLogMsg("WARNING", ...)
    Return   // Sai imediatamente, sem retry
EndIf
```

Alternativa com retry (padrao JobSetRunning):

```advpl
cProcesso := Lower(ProcName()) + cFilAnt
cLockFile := cProcesso + ".lck"
For nX := 1 To 2
    nHdlJob := JobSetRunning(cProcesso, .T.)
    If nHdlJob > 0
        // processar
        JobSetRunning(cLockFile, .F., nHdlJob)
        Exit
    Else
        Sleep(3000)
    Endif
Next
```

Prefira LockByName (fail-fast) para Jobs simples. Use JobSetRunning apenas
quando precisar de retry ou quando usar FWIPCWait para multi-thread.

### R05 - Log estruturado com FwLogMsg

Use FwLogMsg com severidade correta. A assinatura:

```advpl
FwLogMsg(cSeverity, cTransactionId, cSource, cFunction, cOperation, cCode, cMessage, nParam1, nParam2, aExtras)
```

Severidades:
- `"INFO"` - inicio, fim, sucesso por registro, totalizadores
- `"WARNING"` - job ja rodando, parametro opcional vazio
- `"ERROR"` - falha no MSExecAuto, falha no RecLock, parametro obrigatorio vazio

Sempre identifique a funcao origem e a operacao:

```advpl
FwLogMsg("ERROR", /*cTransactionId*/, "U_MEUJOB", FunName(), "MATA410", "01", ;
    "Erro ao gerar Pedido de Servico. " + cLogMsg, 0, 0, GetAutoGrLog())
```

### R06 - Begin Sequence no loop, NAO fora

O Begin Sequence deve envolver CADA iteracao, nao o loop inteiro. Isso
garante que um erro em um registro nao aborte o processamento dos demais:

```advpl
While !(cAliasQry)->(Eof())
    Begin Sequence          // <-- DENTRO do While
        // processar um registro
        If lMsErroAuto
            Break           // Pula para o proximo registro
        EndIf
    End Sequence
    (cAliasQry)->(DbSkip())
EndDo
```

### R07 - Begin Transaction para updates de status

Quando atualizar mais de uma tabela como consequencia de um processamento,
envolva em Begin Transaction. Use DisarmTransaction() para rollback:

```advpl
Begin Transaction
    If RecLock("SC5", .F.)
        SC5->C5_ZGSSTAT := '1'
        SC5->(MsUnlock())
    Else
        DisarmTransaction()
        Break
    EndIf
    // segundo update na mesma transacao
    If RecLock("SF2", .F.)
        SF2->F2_ZSERVPR := '1'
        SF2->(MsUnlock())
    Else
        DisarmTransaction()
        Break
    EndIf
End Transaction
```

### R08 - RecLock SEMPRE com verificacao de retorno

NUNCA faca RecLock sem verificar se o bloqueio foi obtido:

```advpl
// ERRADO - ignora falha no lock
RecLock("SC5", .F.)
SC5->C5_CAMPO := 'X'
SC5->(MsUnlock())

// CERTO - verifica retorno
If RecLock("SC5", .F.)
    SC5->C5_CAMPO := 'X'
    SC5->(MsUnlock())
Else
    FwLogMsg("ERROR", ...)
    DisarmTransaction()
    Break
EndIf
```

### R09 - Cleanup obrigatorio

Todo Job DEVE:
1. Fechar aliases abertos: `(cAliasQry)->(DbCloseArea())`
2. Restaurar areas: `FWRestArea(aArea)`
3. Liberar lock: `UnLockByName(cLockName, ...)` ou `JobSetRunning(cLockFile, .F., nHdlJob)`
4. Limpar ambiente (se Job): `RpcClearEnv()`

### R10 - ZERO interface

Job nao tem usuario na tela. NUNCA use:
- `MsgBox`, `MsgStop`, `MsgInfo`, `MsgYesNo`, `Alert`
- `FWAlertError`, `FWAlertInfo`, `FWAlertSuccess`
- `MSDIALOG`, `TDialog`, qualquer componente visual
- `Processa({||...})` (barra de progresso)

Use `ConOut()` e `FwLogMsg()` como unico output.

Se o Job for dual-mode (roda tanto via Schedule quanto via SmartClient),
use a flag `lJob` para condicionar:

```advpl
If !lJob
    FWMsgRun(, {|oSay| WORKER(oSay)}, "Processando", "Aguarde...")
Else
    WORKER()
Endif
```

### R11 - Parametros de negocio via SuperGetMV

Nunca faça hardcode de valores de negocio. Use parametros SX6:

```advpl
Local cProdServ  := SuperGetMV("XX_PRODSC", .F.)
Local cNatServ   := SuperGetMV("XX_NATSC", .F.)
Local cTesServ   := SuperGetMV("XX_TESSC", .F., "537")
Local cSerieServ := SuperGetMV("XX_SERIESC", .F.)
Local nValorUnit := SuperGetMV("XX_VLUNIT", .F., 4.50)
```

### R12 - Queries com RetSqlName e D_E_L_E_T_

Sempre use `RetSqlName("<alias>")` para nome de tabela e inclua filtro de
registro deletado:

```advpl
cQuery := " SELECT ... FROM " + RetSqlName("SF2") + " SF2 "
cQuery += " WHERE SF2.D_E_L_E_T_ = '' "
```

### R13 - Totalizadores no log de conclusao

Todo Job deve registrar quantos registros processou e quantos falharam:

```advpl
FwLogMsg("INFO", ..., "Concluido. Processados: " + cValToChar(nProcessados) + ;
    " | Erros: " + cValToChar(nErros), ...)
```

---

## VARIANTE: JOB COM MULTI-THREAD (FWIPCWait)

Para processamento pesado, use FWIPCWait. Padrao recomendado para
Jobs de importacao de pedidos, expedicao WMS e integracao fiscal:

```advpl
#DEFINE SEMAFORO_JOB '<NOME_SEMAFORO>'

// Na funcao principal (apos lock)
Local nThreads := SuperGetMV("<PRJ>_THREADS", .F., 4)
Local oIPC     := Nil

If nThreads > 1
    oIPC := FWIPCWait():New(SEMAFORO_JOB, 10000)
    oIPC:SetThreads(nThreads)
    oIPC:SetEnvironment(FWGrpCompany(), FWCodFil())
    oIPC:Start("U_<WORKER_FUNC>")
    oIPC:StopProcessOnError(.T.)
    oIPC:SetNoErrorStop(.T.)
    Sleep(600)
Endif

// No loop de dados
While !(cAliasQry)->(Eof())
    aAdd(aDados, {(cAliasQry)->CAMPO1, (cAliasQry)->CAMPO2})

    If nThreads > 1
        If !oIPC:Go(aDados, lJob)
            Exit
        Endif
        aDados := {}
    Else
        U_<WORKER_FUNC>(aDados, lJob)
        aDados := {}
    Endif

    (cAliasQry)->(DbSkip())
EndDo

// Finalizacao multi-thread
If nThreads > 1 .And. oIPC != Nil
    oIPC:Stop()
    cError := oIPC:GetError()
    oIPC:removeThread(.T.)
    FreeObj(oIPC)
    oIPC := Nil
    If !Empty(cError)
        FwLogMsg("ERROR", ..., "Erro em thread: " + cError, ...)
    Endif
Endif
```

A funcao worker (`U_<WORKER_FUNC>`) e uma User Function separada que
recebe o array de dados como parametro. Ela roda em thread propria com
ambiente ja configurado pelo FWIPCWait.

---

## VARIANTE: JOB COM ErrorBlock (captura stack trace)

Para Jobs que precisam capturar stack trace completo (integracao com API
externa, processamento critico). O bloco `Recover` e sugerido para logar o erro fatal:

```advpl
Static Function WORKER_<NOME>()

    Local cErrorLog  := ""
    Local bOldError  := ErrorBlock({|oError| ;
        cErrorLog := oError:Description + CRLF + oError:ErrorStack, ;
        Break(oError)})

    Begin Sequence

        // Logica de negocio que pode gerar erro fatal

    Recover // Sugestao: usar para logar o erro capturado pelo ErrorBlock

        FwLogMsg("ERROR", /*cTransactionId*/, "U_<NOME_JOB>", FunName(), ;
            "", "01", "Erro fatal: " + cErrorLog, 0, 0, {})

    End Sequence

    ErrorBlock(bOldError)

Return
```

---

## VARIANTE: JOB COM TROCA DE FILIAL (multi-filial)

Quando o Job processa dados de multiplas filiais:

```advpl
While !(cAliasQry)->(Eof())

    // Troca de filial quando necessario
    If cFilAnt != (cAliasQry)->CAMPO_FILIAL
        cFilAnt := (cAliasQry)->CAMPO_FILIAL
        FWSM0Util():setSM0PositionBycFilAnt()
    Endif

    // Processar registro na filial correta
    // ...

    (cAliasQry)->(DbSkip())
EndDo
```

---

## ANTI-PATTERNS

### AP01 - Credenciais hardcoded no fonte

```advpl
// ERRADO - credenciais hardcoded no fonte
RpcSetEnv("01", "99", "usuario", "SenhaAqui123")
RpcSetEnv(cGrupo, cFIlEmp, "usuario_job", "SenhaAqui456", "FAT")
RpcSetEnv("01", "0101", "Admin", "SenhaAqui789")

// Tambem encontrado: client_id e client_secret de API
Local cClientId  := 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
Local cCliSecret := 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'
```

**Correcao:** Use `aDadosSistema` do Scheduler para empresa/filial.
Para credenciais de API, use `SuperGetMV` ou tabela de configuracao.

### AP02 - Job sem controle de concorrencia

```advpl
// ERRADO
User Function MEUJOB(aParam)
    // ...
    RpcSetEnv(cEmpCod, cFilCod)
    MEUJOBA(.T.)            // <-- Nenhum lock! Pode rodar em paralelo
    RpcClearEnv()
```

**Risco:** Se o Scheduler disparar novamente antes do anterior terminar,
dois processos modificam os mesmos registros simultaneamente.

**Correcao:** Adicionar LockByName na camada 2.

### AP03 - RecLock sem verificacao de retorno

```advpl
// ERRADO
RecLock("SC5", .F.)         // Se falhar, continua executando!
SC5->C5_ZGSSTAT := '2'
SC5->(MsUnlock())

RecLock("SZ1", .F.)         // Se falhar, grava em registro errado
SZ1->Z1_CLASSIF := "3"
SZ1->(MsUnlock())
```

**Correcao:** Sempre verifique o retorno:
```advpl
If RecLock("SC5", .F.)
    SC5->C5_ZGSSTAT := '2'
    SC5->(MsUnlock())
Else
    FwLogMsg("ERROR", ...)
    DisarmTransaction()
    Break
EndIf
```

### AP04 - Begin Sequence FORA do loop

```advpl
// ERRADO - um erro no registro 5 aborta registros 6, 7, 8...
Begin Sequence
    While !(cAlias)->(Eof())
        // processar
        (cAlias)->(DbSkip())
    EndDo
Recover
    // log do erro
End Sequence
```

**Correcao:** Mover Begin Sequence para DENTRO do loop (ver regra R06).

### AP05 - Job sem nenhum tratamento de erros

```advpl
// ERRADO
User Function EXEMJOB01()
    RpcSetType(3)
    PREPARE ENVIRONMENT EMPRESA "01" FILIAL "01"
    // Processa sem qualquer protecao
    // Se der erro fatal, o Job morre silenciosamente
    RESET ENVIRONMENT
Return
```

**Correcao:** Envolver processamento em Begin Sequence com log de erro.

### AP06 - FreeObj APOS atribuir NIL

```advpl
// ERRADO
oIPC := NIL         // Objeto ja e NIL...
FreeObj(oIPC)       // ...FreeObj de NIL nao faz nada

oRestClient := nil  // Mesma coisa
FreeObj(oRestClient)
```

**Correcao:** FreeObj primeiro, depois NIL:
```advpl
FreeObj(oIPC)
oIPC := Nil
```

### AP07 - MsgStop dentro de contexto Job

```advpl
// ERRADO
If nStatus < 200 .Or. nStatus > 299
    MsgStop(cError)     // <-- Trava o Job esperando click que nunca vem
Endif
```

**Correcao:** Usar FwLogMsg ou ConOut em contexto Job.

### AP08 - Aliases nao fechados em caminhos de erro

```advpl
// ERRADO - se Break ocorrer, cAliasQry fica aberto
While !(cAliasQry)->(Eof())
    Begin Sequence
        // ... processamento ...
        If lMsErroAuto
            Break          // <-- cAliasQry nunca e fechado se todos derem erro
        EndIf
    End Sequence
    (cAliasQry)->(DbSkip())
EndDo
// OK se chegar aqui, mas e se tiver Return antes?
(cAliasQry)->(DbCloseArea())
```

**Correcao:** O DbCloseArea esta FORA do Begin Sequence, apos o loop.
Isso funciona porque o Break pula para End Sequence (nao para fora do
While). O alias e fechado apos o loop independente de erros.
O problema real e quando ha um `Return` antes do fechamento. Evite
`Return` precoce apos abrir aliases.

### AP09 - Duplicacao de Jobs inteiros

```
// ERRADO - 2 arquivos 95% identicos
ExemploJobExpedicao.tlpp   (semaforo: EXEMSEMAF)
ExemploJobExpedicao2.tlpp  (semaforo: EXEMSEMA1)
```

**Correcao:** Parametrizar a diferenca (semaforo, modo de dispatch) e
usar um unico fonte.

---

## EXEMPLOS DE REFERENCIA

### Exemplo 1: Job de Geracao de NF de Servico

Este e o Job mais bem estruturado encontrado. Anatomia:

**Camada 1 (Entry):** Linhas 17-35
- Detecta Job, abre ambiente com modulo FAT, limpa ao sair

**Camada 2 (Lock):** Linhas 42-62
- Lock: `"MEUJOB" + empresa + filial`
- Log de inicio/fim com FwLogMsg

**Camada 3 (Worker):** Linhas 69-277
- 9 parametros via SuperGetMV (produto, natureza, TES, serie, valor, filiais, banco, agencia, conta)
- Validacao upfront de todos os parametros
- Query com 4 JOINs (SF2, SD2, SB1, SC5) filtrando registros pendentes
- Loop com Begin Sequence por registro
- MSExecAuto MATA410 para gerar Pedido de Venda
- Begin Transaction para atualizar SC5.C5_ZGSSTAT e SF2.F2_ZSERVPR
- RecLock com verificacao + DisarmTransaction em falha
- Log INFO por sucesso, ERROR por falha, com contexto (NF, cliente, pedido)
- Fecha alias + FWRestArea no final

### Exemplo 2: Job de Monitoramento de Ordens de Coleta

Job dual-mode (Schedule ou SmartClient):

**Entry:** Linhas 13-38
- Aceita parametros flexiveis (array ou default)
- Via Schedule: RpcSetEnv + worker(.T.)
- Via SmartClient: Processa({||worker(.F.)})

**Worker:** Linhas 40-160
- Usa TCSqlToArr ao inves de MPSysOpenQuery (alternativa valida)
- Processa array com For...Next ao inves de While...Eof
- Logica de maquina de estados (status da coleta)
- Parametros de prazo por status via SuperGetMV

**Pontos fracos (usar como contra-exemplo):**
- Sem LockByName
- Sem Begin Sequence
- RecLock sem verificacao de retorno

### Exemplo 3: Job de Integracao WMS Multi-thread

Job complexo com multi-threading e integracao REST:

**Entry:** Linhas 24-73
- Detecta Job, usa JobSetRunning com retry (2 tentativas, Sleep 3000)
- Troca de filial via FWSM0Util

**Dispatcher:** Linhas 86-201
- FWIPCWait com semaforo 'EXEMSEMAF' e threads configuravel
- Distribui lotes de separacao para threads
- Captura erro global via oIPC:GetError()
- Envia email de erro via classe customizada

**Worker (thread):** Linhas 215-441
- ErrorBlock capturando stack trace completo
- Begin Sequence envolvendo todo o processamento
- Integracao REST com WMS (consulta, geracao de identificador, criacao de lote)
- Registro de erros em tabela ZC6 + envio de email
- Recover envia email com stack trace e atualiza status de erro

---

## DEBUGGING DE JOBS (sem UI)

Jobs rodam sem interface grafica. Estrategias para debug:

1. **Testar Worker isolado via SmartClient:** Criar uma `User Function TST_WORKER()`
   que declara as Private necessarias e chama o Worker diretamente, sem Scheduler
   nem LockByName. Permite ver ConOut no console do SmartClient.

2. **Ler FwLogMsg no console.log:** Abrir o console.log do AppServer e filtrar
   pelo nome do Job. No Windows: `Get-Content console.log -Wait | Select-String "U_MEUJOB"`.

3. **Forcar execucao manual:** Abrir SmartClient com Programa Inicial `U_MEUJOB`
   ou criar funcao wrapper `U_TST_JOB()` que passa `{"01","0101"}` como aDadosSistema.

Para guia completo de diagnostico (erros, performance, locks), consulte `advpl-debugging`.

---

## CHECKLIST PARA REVISAO DE JOBS

Ao revisar ou criar um Job, verifique todos os itens:

**Estrutura:**
- [ ] Namespace: `custom.<projeto>.job.<modulo>`
- [ ] Protheus.doc com @param, @author, @since
- [ ] 3 camadas: Entry -> Lock -> Worker

**Inicializacao:**
- [ ] Deteccao: `GetRemoteType() == -1 .OR. (!Type("cFilAnt") == "C" .AND. !TCIsConnected())`
- [ ] `RpcClearEnv()` ANTES do `RpcSetEnv()`
- [ ] Empresa/filial via `aDadosSistema`, NAO hardcoded
- [ ] Modulo informado no RpcSetEnv (6o parametro)

**Concorrencia:**
- [ ] LockByName (ou JobSetRunning) com empresa+filial no nome
- [ ] UnLockByName garantido (mesmo em caso de erro)
- [ ] FwLogMsg WARNING quando lock falha

**Processamento:**
- [ ] Parametros de negocio via SuperGetMV
- [ ] Validacao de parametros obrigatorios antes de processar
- [ ] Query com RetSqlName + D_E_L_E_T_ = ''
- [ ] Begin Sequence DENTRO do loop (por registro)
- [ ] Begin Transaction para updates multi-tabela
- [ ] RecLock com verificacao de retorno
- [ ] DisarmTransaction + Break em falha de RecLock

**Log:**
- [ ] FwLogMsg INFO no inicio e fim
- [ ] FwLogMsg ERROR por falha, com contexto do registro
- [ ] Totalizadores no final (processados / erros)
- [ ] ZERO uso de MsgBox/MsgStop/Alert/FWAlertError

**Cleanup:**
- [ ] Todos os aliases fechados com DbCloseArea()
- [ ] FWRestArea(aArea) no final do Worker
- [ ] UnLockByName no final do Lock Controller
- [ ] RpcClearEnv() condicional (apenas se lJob)

**Seguranca:**
- [ ] Zero credenciais no fonte (usuario, senha, tokens, client_id)
- [ ] Zero caminhos absolutos
- [ ] Zero emails hardcoded (usar SuperGetMV)