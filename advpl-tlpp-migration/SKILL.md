---
name: advpl-tlpp-migration
description: >
  Migracao de codigo ADVPL procedural (.prw) para TLPP orientado a objetos (.tlpp).
  Use quando o usuario pedir para migrar, converter, ou modernizar codigo ADVPL
  procedural (.prw) para TLPP orientado a objetos (.tlpp), incluindo refatoracao
  de funcoes para classes.
---

# ADVPL → TLPP Migration — Guia de Migracao

Skill para o PROCESSO de migracao de codigo ADVPL procedural (.prw) para TLPP
orientado a objetos (.tlpp). Para os templates de destino (como as classes devem
ficar), consulte `tlpp-classes`.

---

## 1. WORKFLOW DE MIGRACAO (7 ETAPAS)

```
1. ANALISAR    → Ler o .prw, mapear funcoes, variaveis compartilhadas, dependencias
2. IDENTIFICAR → Classificar cada funcao: Entry Point, Helper, Utilitario, Domain
3. MAPEAR      → Decidir quais classes criar e qual template usar (tlpp-classes)
4. APROVAR     → Apresentar plano ao usuario antes de gerar codigo
5. GERAR       → Criar .tlpp seguindo templates da skill tlpp-classes
6. VALIDAR     → Verificar wrapper, imports, testes, anti-patterns
7. COMPILAR    → Orientar compilacao e teste
```

### 1.1 Etapa 1: Analise do .prw

Ao receber um .prw para migracao, levantar os itens abaixo utilizando as ferramentas `view_file` (para ler o fonte) e `grep_search` (para rastrear uso de variaveis):

| Item | O que verificar |
|------|----------------|
| User Functions | Quais sao pontos de entrada (chamadas externamente) |
| Static Functions | Quais sao internas (candidatas a Private Method) |
| Variaveis Private | Quais sao compartilhadas entre funcoes (viram Data) |
| Variaveis Static | Estado global (viram Data com escopo controlado) |
| Dependencias externas | Chamadas a outras U_XXX, includes, libs |
| GetArea/RestArea | Padroes de salvamento de contexto |
| lMsErroAuto/lMsHelpAuto | DEVEM permanecer Private (nao migrar para Data) |
| Begin Sequence / ErrorBlock | Manter padrao de error handling |

### 1.2 Etapa 2: Classificacao de funcoes

| Tipo de funcao no .prw | Destino no .tlpp | Template (tlpp-classes) |
|------------------------|------------------|------------------------|
| User Function de API REST | REST API Class | Template REST |
| User Function de processamento | Domain Class | Template Domain |
| User Function de Job | Worker Class | Template Worker |
| User Function de relatorio | SmartView Class | Template SmartView |
| Static Function auxiliar | Private Method | Na classe correspondente |
| Static Function utilitaria generica | Utils Class | Classe separada |

### 1.3 Etapa 3: Mapeamento para classes

Regras de decisao:

```
1 .prw com 1 User Function + N Static Functions
  → 1 classe (User Function → Public, Static → Private)

1 .prw com N User Functions relacionadas
  → 1 classe (cada UF → Public Method, compartilham Data)

1 .prw com N User Functions NAO relacionadas
  → N classes (1 por UF, cada uma com seus Statics)

Static Functions usadas por MULTIPLOS .prw
  → Classe Utils separada
```

---

## 2. TABELA DE CONVERSAO

### 2.1 Estruturas

| ADVPL (.prw) | TLPP (.tlpp) | Notas |
|-------------|-------------|-------|
| `#include "totvs.ch"` | `namespace ...` + `#include "totvs.ch"` + `#include "tlpp-core.th"` | Adicionar namespace e manter includes obrigatorios |
| `User Function XXX()` | `Public Method XXX() as ...` | Ponto de entrada externo |
| `Static Function YYY()` | `Private Method YYY() as ...` | Funcao interna |
| `Private cVar := ""` | `Data cVar as character` | Variavel compartilhada entre funcoes |
| `Static cVar := ""` | `Data cVar as character` | Estado persistente |
| `Local cVar := ""` | `Local cVar := "" as character` | Sem mudanca (continua Local) |
| `Public cVar` | **REMOVER** | Public e anti-pattern, nao migrar |

### 2.2 Chamadas

| ADVPL (.prw) | TLPP (.tlpp) | Notas |
|-------------|-------------|-------|
| `Funcao(param)` | `Self:Funcao(param)` ou `::Funcao(param)` | Chamada interna vira Self: |
| `U_OutraFunc(param)` | `oOutra:Metodo(param)` | Dependencia externa vira composicao |
| `ExecBlock("PE", ...)` | Manter como esta | Ponto de Entrada nao muda |

### 2.3 Acesso a dados

| ADVPL (.prw) | TLPP (.tlpp) | Notas |
|-------------|-------------|-------|
| `cVar := cValor` (Private) | `Self:cVar := cValor` | Private vira Data |
| `AAdd(aItens, x)` | `AAdd(Self:aItens, x)` | Array Private vira Data |

---

## 3. CONVENCAO DE NAMESPACE

```
custom.<projeto>.<modulo>.<tipo>

Exemplos:
custom.wms.expedicao.domain      → Classes de negocio
custom.wms.expedicao.rest        → APIs REST
custom.wms.expedicao.job         → Jobs/Workers
custom.wms.expedicao.utils       → Utilitarios
custom.fiscal.nfe.domain         → Classes de negocio fiscal
custom.exemplo.faturamento.nf.rest       → APIs REST de faturamento
```

**Regras:**
- Sempre `custom.` como raiz (customizacao, nao padrao TOTVS)
- Projeto em minusculas, sem acentos
- Modulo representa a area funcional
- Tipo representa o papel da classe

---

## 4. ARMADILHAS COMUNS NA MIGRACAO

### 4.1 Private compartilhada vira Data (muda escopo!)

```advpl
// ANTES (.prw) — Private e visivel em funcoes chamadas
User Function MinhaFunc()
    Private cStatus := "A"
    HELPER()  // cStatus e visivel aqui
Return

Static Function HELPER()
    If cStatus == "A"  // Funciona — Private herdada
        cStatus := "B"
    EndIf
Return
```

```tlpp
// DEPOIS (.tlpp) — Data precisa de Self:
Class MinhaClasse
    Data cStatus as character

    Public Method MinhaFunc() as logical
    Private Method Helper() as logical
EndClass

Method MinhaFunc() Class MinhaClasse
    Self:cStatus := "A"
    Self:Helper()
Return .T.

Method Helper() Class MinhaClasse
    If Self:cStatus == "A"  // Precisa de Self:!
        Self:cStatus := "B"
    EndIf
Return .T.
```

### 4.2 lMsErroAuto / lMsHelpAuto DEVEM permanecer Private

```tlpp
// ERRADO — migrar lMsErroAuto para Data
Class MinhaClasse
    Data lMsErroAuto as logical  // NAO! MSExecAuto nao ve Data!
EndClass

// CORRETO — manter como Private dentro do metodo
Method Processar() Class MinhaClasse
    Private lMsErroAuto    := .F.   // MSExecAuto precisa de Private
    Private lMsHelpAuto    := .T.
    Private lAutoErrNoFile := .T.

    MsExecAuto({|x,y,z| MATA410(x,y,z)}, aCampos,, 3)

    If lMsErroAuto  // Verifica a Private, nao Self:
        // tratar erro
    EndIf
Return
```

### 4.3 GetArea/RestArea deve sobreviver a migracao

```tlpp
// CORRETO — GetArea/RestArea continua funcionando em metodos
Method Processar() Class MinhaClasse
    Local aAreaSA1 := SA1->(GetArea())

    // ... processamento ...

    SA1->(RestArea(aAreaSA1))  // Restaurar SEMPRE
Return
```

### 4.4 ErrorBlock nao muda

```tlpp
// ErrorBlock continua identico — nao migrar para try/catch (nao existe em TLPP)
Method Processar() Class MinhaClasse
    Local cErr := ""
    Local bOld := ErrorBlock({|e| cErr := e:Description + CRLF + e:ErrorStack, Break(e)})

    Begin Sequence
        // processamento
    Recover
        FwLogMsg("ERROR", , "MinhaClasse", "Processar", "", "01", cErr, 0, 0, {})
    End Sequence

    ErrorBlock(bOld)
Return
```

### 4.5 Construtores — inicializar TODAS as Data

```tlpp
// CORRETO — construtor inicializa todas as propriedades
Method New(cCodigo) Class MinhaClasse
    Self:cCodigo  := cCodigo
    Self:cNome    := ""
    Self:nTotal   := 0
    Self:aItens   := {}
    Self:lAtivo   := .T.
    Self:oLogger  := Nil
Return Self  // SEMPRE retornar Self
```

---

## 5. PADRAO DE WRAPPER .prw (backward compatibility)

Quando o .prw original e chamado por outros fontes, pontos de entrada,
ou Scheduler, criar um wrapper que mantem a interface original:

```advpl
// Arquivo: ORIGINAL.prw (wrapper — manter para compatibilidade)
#Include "totvs.ch"

//================================================================
// Wrapper para compatibilidade — delega para classe TLPP
// A logica real esta em MinhaClasse.tlpp
//================================================================
User Function ORIGINAL(xParam1, xParam2)
    Local oObj := Nil

    // Instanciar a classe TLPP
    oObj := custom.projeto.modulo.MinhaClasse():New(xParam1)

    // Chamar o metodo correspondente
    oObj:Processar(xParam2)

    FreeObj(oObj)
    oObj := Nil
Return
```

**Quando criar wrapper:**
- Funcao chamada pelo Scheduler (Job)
- Funcao chamada por MsExecAuto de outros fontes
- Funcao referenciada em menus (SIGAMDI)
- Funcao chamada por ExecBlock/pontos de entrada

**Quando NAO criar wrapper:**
- Static Functions (internas, ninguem chama de fora)
- Funcoes que so o proprio .prw usa
- Funcoes que serao migradas junto com seus chamadores

---

## 6. MAPEAMENTO PARA TEMPLATES (tlpp-classes)

| Cenario | Template em tlpp-classes | Decisao |
|---------|------------------------|---------|
| API REST (endpoints HTTP) | REST API Class | Usar anotacoes @Get/@Post |
| Processamento de negocio | Domain Class | Logica pura, sem UI |
| Job/Schedule | Worker Class | 3 camadas (Entry+Lock+Worker) |
| Relatorio | SmartView Class | TReport ou Excel |
| Utilitarios reutilizaveis | Utils (sem template fixo) | Metodos Static ou de instancia |

Consulte a skill `tlpp-classes` para os templates completos de cada tipo.

---

## 7. CHECKLIST DE VALIDACAO POS-MIGRACAO

### Estrutura
- [ ] Namespace segue `custom.<projeto>.<modulo>.<tipo>`
- [ ] Classe tem Protheus.doc com @author, @since
- [ ] Construtor (New) inicializa TODAS as Data
- [ ] Construtor retorna `Self`
- [ ] Destrutor libera objetos com `FreeObj`

### Conversao
- [ ] Toda `User Function` → `Public Method`
- [ ] Toda `Static Function` → `Private Method`
- [ ] Toda `Private cVar` compartilhada → `Data cVar`
- [ ] Chamadas internas usam `Self:` ou `::`
- [ ] `lMsErroAuto`/`lMsHelpAuto`/`lAutoErrNoFile` permanecem Private
- [ ] `GetArea`/`RestArea` mantidos em cada metodo que altera workarea

### Wrapper
- [ ] User Functions chamadas externamente tem wrapper .prw
- [ ] Wrapper instancia classe, chama metodo, FreeObj
- [ ] Scheduler aponta para o wrapper (nao para a classe)

### Funcional
- [ ] Mesmos dados de entrada produzem mesma saida
- [ ] Logs gerados nos mesmos pontos
- [ ] Error handling mantido (Begin Sequence, ErrorBlock)
- [ ] Cleanup de aliases e areas mantido

### Anti-patterns evitados
- [ ] Classe NAO e monolitica (>500 linhas → dividir)
- [ ] Error handling NAO foi removido na migracao
- [ ] Wrapper NAO tem logica de negocio (apenas delega)
- [ ] Nao ha `Public` variables (removidas ou convertidas para Data)
- [ ] Nao ha Data exposta sem necessidade (preferir Private Method de acesso)

---

## 8. EXEMPLO COMPLETO DE MIGRACAO

### ANTES: JOBEXAMPLE.prw

```advpl
#Include "totvs.ch"

User Function JOBEXAMPLE(aDadosSistema)
    Local lJob := .F.
    If GetRemoteType() == -1
        lJob := .T.
        RpcClearEnv()
        RpcSetEnv(aDadosSistema[1], aDadosSistema[2],,,,'FAT')
    Endif
    PROC_JOB()
    If lJob
        RpcClearEnv()
    Endif
Return

Static Function PROC_JOB()
    Private lMsErroAuto := .F.
    Private lMsHelpAuto := .T.
    If !LockByName("JOBEXAMPLE" + SM0->M0_CODIGO, .F., .F., .T.)
        Return
    EndIf
    WORKER_JOB()
    UnLockByName("JOBEXAMPLE" + SM0->M0_CODIGO, .F., .F., .T.)
Return

Static Function WORKER_JOB()
    Local aArea := FWGetArea()
    Local cAlias := GetNextAlias()
    Local nProc := 0

    Private cStatus := "P"  // Compartilhada com ATUALIZA

    cQuery := " SELECT ... FROM " + RetSqlName("SC5") + " SC5 "
    cQuery += " WHERE SC5.C5_ZSTATUS = 'P' AND SC5.D_E_L_E_T_ = ' ' "
    MpSysOpenQuery(ChangeQuery(cQuery), cAlias)

    While !(cAlias)->(Eof())
        Begin Sequence
            ATUALIZA((cAlias)->R_E_C_N_O_)
            nProc++
        End Sequence
        (cAlias)->(DbSkip())
    EndDo

    (cAlias)->(DbCloseArea())
    FWRestArea(aArea)
Return

Static Function ATUALIZA(nRecno)
    DbSelectArea("SC5")
    SC5->(DbGoTo(nRecno))
    If RecLock("SC5", .F.)
        SC5->C5_ZSTATUS := cStatus  // Usa Private do caller
        SC5->(MsUnlock())
    EndIf
Return
```

### DEPOIS: JobExampleWorker.tlpp + JOBEXAMPLE.prw (wrapper)

**Classe TLPP:**
```tlpp
#Include "totvs.ch"
#Include "tlpp-core.th"

namespace custom.exemplo.faturamento.job

//================================================================
/*/{Protheus.doc} JobExampleWorker
Worker para processamento de pedidos pendentes.
@author Dev
@since 04/03/2026
/*/
//================================================================
Class JobExampleWorker

    Data cStatus   as character
    Data nProc     as numeric
    Data nErros    as numeric

    Public Method New() as object
    Public Method Processar() as logical
    Private Method Atualizar(nRecno as numeric) as logical

EndClass

Method New() Class JobExampleWorker
    Self:cStatus := "P"
    Self:nProc   := 0
    Self:nErros  := 0
Return Self

Method Processar() Class JobExampleWorker
    Local aArea   := FWGetArea()
    Local cAlias  := GetNextAlias()
    Local cQuery  := ""

    cQuery := " SELECT SC5.R_E_C_N_O_ AS RECNO "
    cQuery += " FROM " + RetSqlName("SC5") + " SC5 "
    cQuery += " WHERE SC5.C5_ZSTATUS = 'P' "
    cQuery += "   AND SC5.D_E_L_E_T_ = ' ' "

    MpSysOpenQuery(ChangeQuery(cQuery), cAlias)

    While !(cAlias)->(Eof())
        Begin Sequence
            If Self:Atualizar((cAlias)->RECNO)
                Self:nProc++
            Else
                Self:nErros++
            EndIf
        End Sequence
        (cAlias)->(DbSkip())
    EndDo

    (cAlias)->(DbCloseArea())
    FWRestArea(aArea)

    FwLogMsg("INFO", , "JobExampleWorker", "Processar", "", "01", ;
        "Concluido. Proc: " + cValToChar(Self:nProc) + ;
        " Erros: " + cValToChar(Self:nErros), 0, 0, {})

Return (Self:nErros == 0)

Method Atualizar(nRecno) Class JobExampleWorker
    Local lRet := .F.

    DbSelectArea("SC5")
    SC5->(DbGoTo(nRecno))

    If SC5->(!Eof()) .And. RecLock("SC5", .F.)
        SC5->C5_ZSTATUS := Self:cStatus
        SC5->(MsUnlock())
        lRet := .T.
    Else
        FwLogMsg("ERROR", , "JobExampleWorker", "Atualizar", "", "01", ;
            "Falha RecLock. Recno: " + cValToChar(nRecno), 0, 0, {})
    EndIf

Return lRet
```

**Wrapper .prw (mantido para Scheduler):**
```advpl
#Include "totvs.ch"

// Wrapper para compatibilidade com Scheduler
User Function JOBEXAMPLE(aDadosSistema)
    Local lJob := .F.
    Local oWorker := Nil

    If GetRemoteType() == -1 .Or. (!Type("cFilAnt") == "C" .And. !TCIsConnected())
        lJob := .T.
        RpcClearEnv()
        RpcSetEnv(aDadosSistema[1], aDadosSistema[2],,,,'FAT')
    Endif

    If LockByName("JOBEXAMPLE" + AllTrim(SM0->M0_CODIGO) + AllTrim(SM0->M0_CODFIL), .F., .F., .T.)
        oWorker := custom.exemplo.faturamento.job.JobExampleWorker():New()
        oWorker:Processar()
        FreeObj(oWorker)
        oWorker := Nil
        UnLockByName("JOBEXAMPLE" + AllTrim(SM0->M0_CODIGO) + AllTrim(SM0->M0_CODFIL), .F., .F., .T.)
    Else
        FwLogMsg("WARNING", , "U_JOBEXAMPLE", FunName(), "", "01", ;
            "Job ja em execucao.", 0, 0, {})
    EndIf

    If lJob
        RpcClearEnv()
    Endif
Return
```

---

## 9. CROSS-REFERENCES

| Topico | Skill |
|--------|-------|
| Templates de classes TLPP (destino) | `tlpp-classes` |
| Jobs e Workers | `protheus-jobs` |
| APIs REST em TLPP | `protheus-rest` |
| Padroes de acesso a dados | `protheus-data-model` |
| Funcoes nativas da linguagem | `advpl-tlpp-language` |
| Debug de problemas na migracao | `advpl-debugging` |
