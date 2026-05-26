---
name: advpl-debugging
description: >
  Diagnostico e debugging de erros no Protheus (ADVPL/TLPP).
  Use quando o usuario pedir para debugar, diagnosticar, corrigir erros,
  analisar logs, stack traces, erros de compilacao, runtime, performance
  lenta, ou locks no Protheus.
---

# ADVPL/TLPP Debugging — Guia de Diagnostico Protheus

Skill prescritiva para diagnostico sistematico de erros em ADVPL/TLPP.
Cobre erros de compilacao, runtime, performance, locks e analise de logs.

---

## 1. METODOLOGIA DE DIAGNOSTICO

### 1.1 Fluxo sistematico (sempre seguir esta ordem)

```
1. COLETAR    → Obter mensagem de erro exata, stack trace, log do AppServer
2. CLASSIFICAR → Compilacao? Runtime? Performance? Lock? Integracao?
3. LOCALIZAR  → Identificar arquivo, funcao e linha do erro
4. REPRODUZIR → Isolar cenario minimo que reproduz o problema
5. CORRIGIR   → Aplicar fix, validar, documentar causa raiz
```

### 1.2 Informacoes a coletar ANTES de diagnosticar

| Item | Onde encontrar |
|------|---------------|
| Mensagem de erro exata | Tela do SmartClient, console.log |
| Stack trace | console.log do AppServer, ErrorLog |
| Versao do AppServer | console.log (cabecalho) |
| RPO compilado? | SIGACFG > Compilar / TDS |
| Ultimo deploy | Verificar data do RPO |
| Ambiente (dev/hom/prod) | Perguntar ao usuario |
| Multiplos usuarios afetados? | Indica lock ou concorrencia |

---

## 2. TABELA RAPIDA: SINTOMA → CAUSA → PRIMEIRO CHECK

Use esta tabela para diagnostico rapido antes de investigar a fundo.

| Sintoma | Causa provavel | Primeiro check |
|---------|---------------|----------------|
| "Variable does not exist: CXXX" | Falta `Local`/`Private`/`Public` | Verificar declaracao da variavel na funcao |
| "Array index out of bounds" | `AScan` retornou 0, query vazia | Verificar `If nPos > 0` antes de acessar array |
| "Type mismatch on +/-/==" | Leitura apos `Eof()`, campo NIL | Verificar `If !(cAlias)->(Eof())` antes de ler |
| "THREAD ERROR" | `Private` nao declarada em Job | Declarar Private na funcao que chama, nao no caller |
| "WorkArea already in use" | Alias hardcoded ou leak | Usar `GetNextAlias()`, fechar aliases |
| "RecLock timeout" | Registro bloqueado por outro usuario/processo | Verificar quem tem o lock (ver secao 7) |
| "TOPCONN error" | Conexao com banco perdida | Verificar `TCIsConnected()`, reconectar |
| "Function not found: U_XXX" | Funcao nao compilada no RPO | Compilar o fonte no TDS/SIGACFG |
| "Error on OPEN TABLE" | Tabela inexistente ou corrompida | Verificar `RetSqlName()`, existencia no banco |
| Tela congela / "nao responde" | Loop infinito, falta `DbSkip()` | Verificar se todo `While !Eof()` tem `DbSkip()` |
| Dados errados / campo em branco | Leitura apos `Eof()` ou indice errado | Verificar `DbSetOrder()` e retorno do `MsSeek` |
| "Invalid column name" | Campo nao existe na tabela SQL | Verificar nome via `RetSqlName()` + SX3 |
| Job nao executa | Erro silencioso no `RpcSetEnv` | Verificar console.log do AppServer |
| Job processa duplicado | Sem `LockByName` | Adicionar controle de concorrencia |
| Lentidao progressiva | Memory leak de aliases abertos | Verificar `DbCloseArea()` em todos os caminhos |
| "Character length exceeds 1024K" | String crescendo em loop sem limite | Verificar concatenacao em loop |

---

## 3. ERROS DE COMPILACAO

### 3.1 Erros comuns e correcao

| Erro de compilacao | Causa | Correcao |
|-------------------|-------|----------|
| `Syntax error at 'xxx'` | Palavra reservada como variavel, falta operador | Renomear variavel ou adicionar operador |
| `Undeclared variable 'xxx'` | Variavel nao declarada | Adicionar `Local cXxx := ""` |
| `Function 'xxx' already defined` | Funcao duplicada no RPO | Remover duplicata ou renomear |
| `#include file not found` | .ch nao encontrado no includes do projeto | Verificar path no TDS, adicionar ao Includes |
| `Unbalanced BEGIN/END SEQUENCE` | Falta `End Sequence` ou `Recover` | Verificar pareamento de blocos |
| `Missing EndIf/EndDo/Next` | Bloco nao fechado | Verificar indentacao e fechar bloco |

### 3.2 Dica: erro em cascata

Quando o compilador mostra MUITOS erros, corrija apenas o PRIMEIRO. Erros
subsequentes frequentemente sao consequencia do primeiro (efeito cascata).

---

## 4. ERROS DE RUNTIME

### 4.1 "Variable does not exist"

**Causa raiz:** Variavel usada sem declaracao Local/Private/Public.

```advpl
// ERRADO — cStatus nunca foi declarado
User Function MinhaFunc()
    cStatus := "A"  // Runtime error: Variable does not exist

// CORRETO
User Function MinhaFunc()
    Local cStatus := "A"
```

**Em Jobs:** Private deve ser declarada na mesma funcao ou na funcao que
chama diretamente. Nao herda de funcoes anteriores da pilha.

```advpl
// ERRADO — Private declarada no Entry, usada no Worker via MSExecAuto
User Function MeuJob()
    Private lMsErroAuto := .F.  // OK aqui
    WORKER()

Static Function WORKER()
    // lMsErroAuto existe aqui (herdada)
    // MAS se MSExecAuto chamar sub-funcao que acessa, pode falhar
```

### 4.2 "Array index out of bounds"

**Causas comuns:**
1. `AScan` retornou 0 e o resultado foi usado direto como indice
2. Query nao retornou registros e tentou acessar array vazio
3. Loop com indice manual ultrapassou `Len(aArray)`

```advpl
// ERRADO
nPos := AScan(aCampos, {|x| x[1] == "XXX"})
cValor := aCampos[nPos][2]  // Se nPos = 0, CRASH!

// CORRETO
nPos := AScan(aCampos, {|x| x[1] == "XXX"})
If nPos > 0
    cValor := aCampos[nPos][2]
EndIf
```

### 4.3 "Type mismatch"

**Causa raiz:** Operacao entre tipos incompativeis (ex: string + numerico).

```advpl
// ERRADO — apos Eof(), campos retornam NIL em alias de query
(cAlias)->(DbSkip())  // Avancou para Eof
cNome := (cAlias)->A1_NOME  // NIL!
cMsg := "Cliente: " + cNome  // Type mismatch: string + NIL

// CORRETO — sempre checar Eof() ANTES de ler
While !(cAlias)->(Eof())
    cNome := (cAlias)->A1_NOME
    (cAlias)->(DbSkip())
EndDo
```

**Outra causa comum:** `Val()` em campo que pode conter letras.

```advpl
// PERIGOSO — se cCampo tiver espacos ou letras
nVal := Val(cCampo)  // Pode retornar 0 inesperadamente

// SEGURO — limpar antes
nVal := Val(AllTrim(cCampo))
```

### 4.4 "THREAD ERROR" em Jobs

**Causa:** Variavel Private acessada em thread diferente da que declarou.

```advpl
// ERRADO — Private em thread principal, Worker em outra thread via FWIPCWait
Private lMsErroAuto := .F.
oIPC:Start("U_WORKER")  // Worker roda em thread separada

// CORRETO — declarar Private DENTRO do Worker
User Function WORKER(aDados)
    Private lMsErroAuto    := .F.
    Private lMsHelpAuto    := .T.
    Private lAutoErrNoFile := .T.
    // ...
```

---

## 5. ErrorBlock — CAPTURA DE STACK TRACE

### 5.1 Padrao basico

**Padrao Begin Sequence:**
O bloco `Recover` e opcional, sendo usado apenas se houver necessidade de tratamento especifico.

```advpl
// Padrao simples (sem Recover)
Begin Sequence
    // codigo que pode falhar
    If lErro
        Break
    EndIf
End Sequence

// Padrao com Recover (Sugerido para captura de erros via ErrorBlock)
Local bAnterior := ErrorBlock({|oErr| oErr:Break()})
Begin Sequence
    // codigo que pode falhar
Recover Using oErr
    ConOut("Erro: " + oErr:Description)
End Sequence
ErrorBlock(bAnterior) // SEMPRE restaurar
```

### 5.2 Propriedades do objeto Error

| Propriedade | Tipo | Descricao |
|-------------|------|-----------|
| `oError:Description` | Character | Mensagem do erro |
| `oError:ErrorStack` | Character | Stack trace completo |
| `oError:GenCode` | Numeric | Codigo generico do erro |
| `oError:SubCode` | Numeric | Subcoidgo do erro |
| `oError:SubSystem` | Character | Subsistema que gerou o erro |
| `oError:OsCode` | Numeric | Codigo de erro do SO |
| `oError:FileName` | Character | Arquivo relacionado |
| `oError:Args` | Array | Argumentos que causaram o erro |

### 5.3 Boas praticas de ErrorBlock e Begin Sequence

```advpl
// CORRETO — Begin Sequence simples para interrupcao de fluxo
Begin Sequence
    // codigo
    If lErro
        Break // Pula direto para o End Sequence
    EndIf
End Sequence

// SUGERIDO — Sempre que houver necessidade de logar o erro fatal ou tratar a pilha
Local bOld := ErrorBlock({|e| cErr := e:Description + CRLF + e:ErrorStack, Break(e)})
Begin Sequence
    // codigo perigoso
Recover Using oError
    FwLogMsg("ERROR", , cSource, FunName(), "", "01", cErr, 0, 0, {})
End Sequence
ErrorBlock(bOld)
```

---

## 6. ANALISE DE LOGS

### 6.1 Fontes de log no Protheus

| Fonte | Onde encontrar | Conteudo |
|-------|---------------|----------|
| Console.log | Diretorio do AppServer (rootpath) | Erros fatais, THREAD ERROR, stack traces |
| FwLogMsg | Console.log + FwMonitor | Log estruturado (INFO/WARNING/ERROR) |
| ConOut | Console.log | Output manual do desenvolvedor |
| ErrorLog | `\system\` no rootpath | Erros nao tratados |
| DBAccess log | Configuracao do DBAccess | Queries SQL executadas |

### 6.2 Leitura de console.log

```
// Formato tipico de erro no console.log:
[ERROR][2024/01/15 14:32:05] THREAD ERROR : Variable does not exist CMYVARIABLE
  Called from U_MYFUNC(123) in source MYFUNC.PRW
  Called from PROC_MYJOB(45) in source MYJOB.PRW
  Called from U_MYJOB(28) in source MYJOB.PRW
```

**Como ler:**
1. Primeira linha: tipo e mensagem do erro
2. Stack trace: de cima para baixo = mais recente para mais antigo
3. A primeira linha do stack trace e onde o erro OCORREU
4. As linhas seguintes mostram a cadeia de chamadas

### 6.3 FwLogMsg — formato e busca

```advpl
// Gerar log estruturado
FwLogMsg(cSeverity, cTransactionId, cSource, cFunction, cOperation, cCode, cMessage, nP1, nP2, aExtras)

// Exemplo de saida no console.log:
// [INFO] [U_MEUJOB] [WORKER_MEUJOB] [] [01] Iniciando processamento.
// [ERROR] [U_MEUJOB] [WORKER_MEUJOB] [MATA410] [01] Erro ao gerar Pedido. NF: 001234 Cliente: 000001
```

**Para buscar erros no log:**
```
// Buscar por severidade:
grep "ERROR" console.log | grep "U_MEUJOB"

// Buscar por periodo:
grep "2024/01/15 14:3" console.log
```

### 6.4 ConOut para debug temporario

```advpl
// Debug temporario — REMOVER antes de deploy
ConOut(">>> DEBUG: cStatus = " + cValToChar(cStatus))
ConOut(">>> DEBUG: nRecno = " + cValToChar(nRecno))
ConOut(">>> DEBUG: Len(aItens) = " + cValToChar(Len(aItens)))

// Padrao para debug de query
ConOut(">>> QUERY: " + cQuery)
```

**IMPORTANTE:** Remover todos os `ConOut` de debug antes de enviar para producao.
Usar `FwLogMsg` para logs permanentes.

---

## 7. DEBUG DE LOCKS

### 7.1 Tipos de lock no Protheus

| Tipo | Mecanismo | Causa comum |
|------|-----------|-------------|
| RecLock timeout | `RecLock("XXX", .F.)` | Outro usuario/processo editando o registro |
| LockByName | `LockByName(cName)` | Job ja em execucao |
| SM0 lock | Tabela SM0 bloqueada | Operacao em empresa/filial em andamento |
| Deadlock SQL | Duas transacoes se bloqueiam | BEGIN TRANSACTION com tabelas cruzadas |

### 7.2 Diagnostico de RecLock timeout

```advpl
// 1. Identificar QUEM tem o lock
// No SQL Server:
cQuery := " SELECT request_session_id, resource_type, resource_description "
cQuery += " FROM sys.dm_tran_locks "
cQuery += " WHERE resource_database_id = DB_ID() "

// 2. Verificar se e processo ativo ou abandonado
// Locks abandonados geralmente sao de processos que crasharam

// 3. Solucao temporaria: matar sessao bloqueadora (com cautela!)
// Solucao definitiva: corrigir o codigo que nao libera o lock
```

### 7.3 Diagnostico de LockByName

```advpl
// Se Job reporta "ja em execucao" mas nao esta rodando:
// Causa: UnLockByName nao foi chamado (crash anterior)

// Verificar no console.log se houve crash
// Se confirmado, liberar manualmente:
UnLockByName(cLockName, .F., .F., .T.)
```

### 7.4 Deadlock — como prevenir

```advpl
// ERRADO — ordem de lock inconsistente entre funcoes
// Funcao A: lock SA1 -> lock SA2
// Funcao B: lock SA2 -> lock SA1  // DEADLOCK!

// CORRETO — sempre mesma ordem de lock
// Funcao A: lock SA1 -> lock SA2
// Funcao B: lock SA1 -> lock SA2  // Mesma ordem!

// Regra geral: lockar tabelas em ordem alfabetica
```

---

## 8. DEBUG DE PERFORMANCE

### 8.1 Sintomas e causas

| Sintoma | Causa provavel | Diagnostico |
|---------|---------------|-------------|
| Tela demora para abrir | Query sem indice / SELECT * | Verificar query no DBAccess log |
| Job leva horas | Loop N+1, query por registro | Refatorar para query unica |
| Servidor lento para todos | Memory leak / alias leak | Verificar aliases abertos |
| Query especifica lenta | Falta de indice SQL | Analisar plano de execucao |

### 8.2 Query lenta — diagnostico

```advpl
// 1. Capturar tempo de execucao
Local nStart := Seconds()
MpSysOpenQuery(ChangeQuery(cQuery), cAlias)
Local nElapsed := Seconds() - nStart
ConOut(">>> Query executou em " + cValToChar(nElapsed) + " segundos")

// 2. Se > 2 segundos, verificar:
//    a) SELECT * ? Trocar por campos explicitos
//    b) Falta indice no WHERE? Verificar SIX
//    c) Tabela muito grande sem filtro de filial?
//    d) JOIN sem condicao adequada?
```

### 8.3 Loop N+1 — o vilao silencioso

```advpl
// ERRADO — 1 query por iteracao (N+1)
While !(cAlias)->(Eof())
    cCodCli := (cAlias)->A1_COD
    // Query DENTRO do loop!
    cQuery := "SELECT E1_SALDO FROM " + RetSqlName("SE1") + " WHERE E1_CLIENTE = '" + cCodCli + "'"
    MpSysOpenQuery(ChangeQuery(cQuery), cAlias2)
    // ...
    (cAlias2)->(DbCloseArea())
    (cAlias)->(DbSkip())
EndDo

// CORRETO — JOIN na query principal
cQuery := " SELECT SA1.A1_COD, SA1.A1_NOME, SE1.E1_SALDO "
cQuery += " FROM " + RetSqlName("SA1") + " SA1 "
cQuery += " LEFT JOIN " + RetSqlName("SE1") + " SE1 "
cQuery += "   ON SE1.E1_FILIAL = SA1.A1_FILIAL "
cQuery += "  AND SE1.E1_CLIENTE = SA1.A1_COD "
cQuery += " WHERE SA1.D_E_L_E_T_ = ' ' "
```

### 8.4 Indices ausentes

```advpl
// Verificar se o indice existe para o campo filtrado
// No dicionario SIX:
cQuery := " SELECT INDICE, ORDEM, CHAVE FROM " + RetSqlName("SIX")
cQuery += " WHERE X6_ARQUIVO = 'SA1' AND D_E_L_E_T_ = ' ' "

// Se o campo do WHERE nao esta em nenhum indice:
// Opcao 1: Adicionar indice via SIGACFG
// Opcao 2: Usar campo que JA tem indice no WHERE
// Opcao 3: Para queries ad-hoc, criar indice temporario (DBA)
```

### 8.5 Memory leak de aliases

```advpl
// ERRADO — alias aberto em cada iteracao, nunca fechado
For nI := 1 To 1000
    cAlias := GetNextAlias()
    MpSysOpenQuery(cQuery, cAlias)
    nVal := (cAlias)->CAMPO
    // FALTA: (cAlias)->(DbCloseArea())  ← LEAK!
Next

// Diagnostico: verificar consumo de memoria crescente no AppServer
// AppServer pode negar novos aliases apos ~32.000 abertos
```

---

## 9. DEBUG DE MSExecAuto

### 9.1 Padrao de diagnostico

```advpl
// SEMPRE verificar e logar o erro do MSExecAuto
Private lMsErroAuto    := .F.
Private lMsHelpAuto    := .T.
Private lAutoErrNoFile := .T.

MsExecAuto({|x,y,z| ROTINA(x,y,z)}, aCampos,, nOpc)

If lMsErroAuto
    aLog := GetAutoGRLog()
    cErro := ""
    For nI := 1 To Len(aLog)
        cErro += aLog[nI] + CRLF
    Next
    ConOut("MSExecAuto ERRO: " + cErro)
    // Log com contexto
    FwLogMsg("ERROR", , "MINHA_FUNC", FunName(), "MATA410", "01", ;
        "Erro MSExecAuto: " + cErro, 0, 0, aLog)
EndIf
```

### 9.2 Erros frequentes em MSExecAuto

| Mensagem no GetAutoGRLog | Causa | Correcao |
|--------------------------|-------|----------|
| "Campo obrigatorio: XXX" | Campo obrigatorio faltando no array | Adicionar campo ao array |
| "Valor invalido para o campo XXX" | Valor fora do range do SX3 | Verificar tipo/tamanho no SX3 |
| "Registro ja existe" | Inclusao (nOpc=3) with chave duplicada | Verificar se registro ja existe |
| "Registro nao encontrado" | Alteracao (nOpc=4) sem posicionar antes | `DbSelectArea` + `MsSeek` antes |
| "Filial invalida" | `xFilial` nao bate com registro | Verificar filial corrente |

### 9.3 Posicionamento obrigatorio para alteracao/exclusao

```advpl
// Para nOpc = 4 (Alterar) ou 5 (Excluir), POSICIONAR antes!
DbSelectArea("SC5")
SC5->(DbSetOrder(1))
If SC5->(MsSeek(xFilial("SC5") + cNumPed))
    MsExecAuto({|x,y,z| MATA410(x,y,z)}, aCampos,, 4)  // Alterar
Else
    ConOut("Registro nao encontrado para alteracao!")
EndIf
```

---

## 10. DEBUG DE INTEGRACAO REST

### 10.1 Checklist de diagnostico

```advpl
// 1. Log da requisicao
ConOut(">>> URL: " + cUrl)
ConOut(">>> METHOD: " + cMethod)
ConOut(">>> BODY: " + cBody)

// 2. Log da resposta
ConOut(">>> STATUS: " + cValToChar(nStatus))
ConOut(">>> RESPONSE: " + cResponse)

// 3. Verificar certificado SSL
// Se erro de SSL: verificar se certificado esta no AppServer

// 4. Verificar timeout
// FWRest padrao: 120 segundos
// Aumentar se necessario: oRest:SetTimeout(300)
```

### 10.2 HTTP status codes comuns

| Status | Significado | Acao |
|--------|------------|------|
| 200 | OK | Processar resposta |
| 201 | Created | Recurso criado com sucesso |
| 400 | Bad Request | Verificar body/parametros |
| 401 | Unauthorized | Verificar token/credenciais |
| 403 | Forbidden | Verificar permissoes |
| 404 | Not Found | Verificar URL/endpoint |
| 408 | Timeout | Aumentar timeout ou verificar rede |
| 500 | Internal Server Error | Erro no servidor destino |
| 503 | Service Unavailable | Servidor destino fora do ar |

---

## 11. DEBUG ESPECIFICO PARA JOBS (sem UI)

Jobs rodam sem interface. Estrategias especificas:

### 11.1 Testar Worker isolado via SmartClient

```advpl
// Criar funcao de teste que chama o Worker diretamente
User Function TST_WORKER()
    // Simular as Private que o Job declara
    Private lMsErroAuto    := .F.
    Private lMsHelpAuto    := .T.
    Private lAutoErrNoFile := .T.

    // Chamar o Worker diretamente (sem Scheduler, sem LockByName)
    WORKER_MEUJOB()

    MsgInfo("Concluido!")
Return
```

### 11.2 Ler FwLogMsg no console

```
// Abrir console.log em tempo real (tail -f no Linux, ou abrir no editor)
// Filtrar por nome do Job:
// grep "U_MEUJOB" console.log

// No Windows: abrir console.log com editor que faz auto-refresh
// Ou usar PowerShell: Get-Content console.log -Wait | Select-String "U_MEUJOB"
```

### 11.3 Forcar execucao com debug

```advpl
// Executar Job manualmente via SmartClient para ver ConOut em tempo real
// 1. Abrir SmartClient
// 2. Programa Inicial: U_MEUJOB
// 3. Parametros: (nao preencher — vai cair no modo nao-Job)
// 4. Observar output no console do SmartClient

// Se precisar simular parametros do Scheduler:
User Function TST_JOB()
    U_MEUJOB({"01", "0101"})  // Simula aDadosSistema
Return
```

---

## 12. CHECKLIST DE DIAGNOSTICO

Ao receber um erro para diagnosticar, siga esta checklist:

### Primeira triagem
- [ ] Obter mensagem de erro EXATA (copiar, nao parafrasear)
- [ ] Classificar: compilacao / runtime / performance / lock / integracao
- [ ] Identificar arquivo e funcao afetados

### Compilacao
- [ ] Erro no primeiro da lista? Corrigir e recompilar
- [ ] Include (.ch) encontrado? Verificar path
- [ ] Funcao duplicada? Verificar RPO

### Runtime
- [ ] Stack trace disponivel? Ler de baixo para cima
- [ ] Variavel declarada? Verificar Local/Private
- [ ] Eof() verificado antes de ler campos?
- [ ] AScan > 0 verificado antes de acessar array?
- [ ] Tipos compativeis na operacao?

### Performance
- [ ] Query tem SELECT *? Trocar por campos explicitos
- [ ] Query dentro de loop? Refatorar para JOIN
- [ ] Indice existe para campos do WHERE?
- [ ] Aliases fechados com DbCloseArea()?
- [ ] GetArea/RestArea pareados?

### Lock
- [ ] RecLock com timeout? Verificar quem tem o lock
- [ ] LockByName retornando .F.? Verificar se Job anterior crashou
- [ ] Deadlock? Verificar ordem de lock entre funcoes

### Job
- [ ] Console.log verificado?
- [ ] RpcSetEnv retornou OK?
- [ ] Private declarada na funcao correta?
- [ ] Worker testavel isolado via SmartClient?

---

## 13. CROSS-REFERENCES

| Topico | Skill |
|--------|-------|
| Debug de locks e RecLock | `protheus-data-model` (secao 4) |
| Debug de Jobs sem UI | `protheus-jobs` (R10, secao Debug) |
| ErrorBlock em Jobs | `protheus-jobs` (variante ErrorBlock) |
| Debug de queries SQL | `protheus-data-model` (secao 1) |
| Debug de BeginSQL existente | `advpl-embedded-sql` |
| Debug de APIs REST | `protheus-rest` |
| Erros de MSExecAuto | `protheus-data-model` (secao 4.3) |
