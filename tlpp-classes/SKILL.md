---
name: tlpp-classes
description: >
  Templates e regras para criacao de classes TLPP/ADVPL no Protheus.
  Use esta skill SEMPRE que o usuario pedir para criar, revisar ou corrigir
  classes em TLPP ou ADVPL, incluindo: REST API classes com anotacoes @Get/@Post,
  classes de negocio (domain/business), workers/orchestrators, SmartView/TReports,
  e qualquer codigo orientado a objetos no Protheus. Define templates obrigatorios,
  regras de nomenclatura, declaracao de propriedades, construtores, heranca vs
  composicao, e anti-patterns comuns.
---


> Prescritiva — toda classe gerada pelo Claude DEVE seguir este template e estas regras.

---

## 1. TEMPLATE PADRÃO DE CLASSE

### 1.1 REST API Class (Stateless Controller)

Quando o objetivo é expor endpoints REST.

```advpl
#Include "tlpp-core.th"
#Include "tlpp-rest.th"
#Include "Protheus.ch"

namespace custom.<projeto>.<modulo>.<funcionalidade>

using namespace custom.<projeto>.utils  // se precisar de utils

//-------------------------------------------------------------------
/*/{Protheus.doc} NomeDaClasse
Descrição breve do que a API faz
@type class
@author Nome
@since DD/MM/YYYY
/*/
//-------------------------------------------------------------------
Class NomeDaClasse

    Public Method New() Constructor

    @Get("/api/v1/<modulo>/<recurso>")
    Public Method Consultar() as logical

    @Post("/api/v1/<modulo>/<recurso>")
    Public Method Cadastrar() as logical

    @Put("/api/v1/<modulo>/<recurso>/:id")
    Public Method Alterar() as logical

    @Delete("/api/v1/<modulo>/<recurso>/:id")
    Public Method Deletar() as logical

EndClass

Method New() Class NomeDaClasse
Return Self

Method Consultar() as logical Class NomeDaClasse
    Local jResponse := JsonObject():New()
    Local cQuery    := ""

    // ... montar query ...
    // ... MPSysOpenQuery(ChangeQuery(cQuery), cAlias) ...
    // ... montar jResponse ...

    oRest:SetResponse(jResponse:ToJson())
Return .T.

Method Cadastrar() as logical Class NomeDaClasse
    Local jBody     := JsonObject():New()
    Local jResponse := JsonObject():New()

    jBody:FromJson(oRest:GetBodyRequest())

    // ... validar jBody ...
    // ... processar ...

    oRest:SetResponse(jResponse:ToJson())
Return .T.
```

### 1.2 Domain/Business Class (Stateful)

Quando a classe carrega estado e lógica de negócio.

```advpl
#Include "Protheus.ch"
#Include "tlpp-core.th"
#Include "TOPCONN.CH"

namespace custom.<projeto>.<modulo>

//-------------------------------------------------------------------
/*/{Protheus.doc} NomeDaClasse
Descrição da classe de negócio
@type class
@author Nome
@since DD/MM/YYYY
/*/
//-------------------------------------------------------------------
Class NomeDaClasse

    Private Data cCampo1    as character
    Private Data nCampo2    as numeric
    Private Data lStatus    as logical
    Private Data cMensagem  as character

    Public Method New(cParam1 as character, nParam2 as numeric) Constructor
    Public Method Processar() as logical
    Public Method getStatus() as logical
    Public Method getMensagem() as character

    Private Method Validar() as logical
    Private Method GravarLog(cOperacao as character, cStatus as character)

EndClass

Method New(cParam1 as character, nParam2 as numeric) Class NomeDaClasse
    Self:cCampo1   := cParam1
    Self:nCampo2   := nParam2
    Self:lStatus   := .T.
    Self:cMensagem := ""
Return Self

Method Processar() as logical Class NomeDaClasse
    If !Self:Validar()
        Return .F.
    EndIf
    // ... lógica de negócio ...
    Self:GravarLog("PROCESSAR", "OK")
Return Self:lStatus

Method getStatus() as logical Class NomeDaClasse
Return Self:lStatus

Method getMensagem() as character Class NomeDaClasse
Return Self:cMensagem

Method Validar() as logical Class NomeDaClasse
    // ... validações ...
Return .T.

Method GravarLog(cOperacao as character, cStatus as character) Class NomeDaClasse
    // RecLock na tabela de log
Return
```

### 1.3 Worker/Service Class (Orchestrator)

Quando a classe coordena múltiplos serviços/colaboradores.

```advpl
#Include "Protheus.ch"
#Include "tlpp-core.th"
#Include "TOPCONN.CH"

namespace custom.<projeto>.<modulo>

using namespace custom.<projeto>.servico1
using namespace custom.<projeto>.servico2

Class NomeDaWorker

    Private Data oServico1  as object
    Private Data oServico2  as object
    Private Data oLogger    as object

    Public Method New() Constructor
    Public Method Executar() as logical

    Private Method ProcessarItem() as logical
    Private Method GravarLog(cOperacao as character, cProcesso as character, cErro as character, cStatus as character)

EndClass

Method New() Class NomeDaWorker
    Self:oServico1 := custom.<ns>.Servico1():New()
    Self:oServico2 := custom.<ns>.Servico2():New()
    Self:oLogger   := Nil
Return Self

Method Executar() as logical Class NomeDaWorker
    Local lRet as logical
    lRet := .T.
    // ... buscar fila, iterar, processar ...
Return lRet
```

### 1.4 SmartView / TReports Class

Quando precisa criar um relatório SmartView.

```advpl
#Include "msobject.ch"
#Include "protheus.ch"
#Include "totvs.framework.treports.integratedprovider.th"

namespace custom.<projeto>.smartview

@totvsFrameworkTReportsIntegratedProvider(active=.T.)
Class NomeDoRelatorio from totvs.framework.treports.integratedprovider.IntegratedProvider

    Public Method New() as object
    Public Method getDisplayName() as character
    Public Method getDescription() as character
    Public Method getData(nPage as numeric, oFilter as object) as object
    Public Method getSchema() as object

EndClass

Method New() Class NomeDoRelatorio
    _Super:New()
    Self:appendArea("Nome da Area")
Return Self

Method getDisplayName() as character Class NomeDoRelatorio
Return "Nome Exibição"

Method getDescription() as character Class NomeDoRelatorio
Return "Descrição do relatório"

Method getSchema() as object Class NomeDoRelatorio
    Self:oSchema:addProperty("CAMPO1", "campo1", "string", "Titulo Campo 1", "ALIAS_CAMPO1")
    // ... mais campos ...
Return Self:oSchema

Method getData(nPage as numeric, oFilter as object) as object Class NomeDoRelatorio
    Local cQuery as character
    Local cAlias as character

    cQuery := "SELECT ..."
    // ... aplicar filtros via oFilter ...

    MPSysOpenQuery(ChangeQuery(cQuery), cAlias)
    Self:setPageSize(100)

    (cAlias)->(DbGoTop())
    While !(cAlias)->(Eof())
        Self:oData:appendData({;
            {"campo1", (cAlias)->CAMPO1};
        })
        (cAlias)->(DbSkip())
    EndDo

    Self:setHasNext(!(cAlias)->(Eof()))
    (cAlias)->(DbCloseArea())
Return Self:oData
```

---

## 2. REGRAS OBRIGATÓRIAS

### 2.1 Declaração de Propriedades

| Regra | Correto | Errado |
|-------|---------|--------|
| Sempre declarar visibilidade | `Private Data cCampo as character` | `Data cCampo` |
| Sempre declarar tipo | `Private Data nValor as numeric` | `Private Data nValor` |
| Default: `Private Data` | `Private Data cNome as character` | `Public Data cNome` |
| Público somente quando necessário | `Public Data cError as character` | — |

**Tipos permitidos:** `character`, `numeric`, `logical`, `date`, `array`, `object`, `json`, `codeblock`

### 2.2 Construtor New()

| Regra | Detalhe |
|-------|---------|
| Nome | Sempre `New()`, nunca `NEW()` nem `new()` |
| Keyword | Sempre usar `Constructor`: `Public Method New() Constructor` |
| Return | **SEMPRE** retornar `Self`: `Return Self` |
| Acesso a membros | Usar `Self:campo`, nunca `::campo` |
| Inicializar TUDO | Todo Private Data DEVE ser inicializado no New() |

```advpl
// CORRETO
Public Method New(cParam as character) Constructor

Method New(cParam as character) Class MinhaClasse
    Self:cCampo1 := cParam
    Self:nCampo2 := 0
    Self:lAtivo  := .T.
Return Self

// ERRADO — não inicializa propriedades, não retorna Self
Method New() Class MinhaClasse
Return
```

### 2.3 Implementação de Métodos

| Regra | Detalhe |
|-------|---------|
| Onde implementar | **SEMPRE fora** do bloco `Class...EndClass` |
| Assinatura | `Method Nome(params) as tipo Class NomeDaClasse` |
| Visibilidade na declaração | `Public Method Nome()` ou `Private Method Nome()` |
| Return type | Sempre declarar: `as logical`, `as character`, `as numeric`, `as object`, `as array` |
| Parâmetros tipados | Sempre: `(cNome as character, nValor as numeric)` |

```advpl
// CORRETO — dentro do bloco (declaração)
Class MinhaClasse
    Public Method Processar(cDado as character) as logical
EndClass

// CORRETO — fora do bloco (implementação)
Method Processar(cDado as character) as logical Class MinhaClasse
    // ... lógica ...
Return .T.

// ERRADO — implementação dentro do bloco Class
Class MinhaClasse
    Public Method Processar(cDado as character) as logical
        // ... lógica aqui dentro ...  ← NUNCA FAZER
    Return .T.
EndClass
```

### 2.4 Herança vs Composição

| Usar Herança | Usar Composição |
|-------------|-----------------|
| Para aderir a framework TOTVS (IntegratedProvider, FWModelEvent, FWAdapterBaseV2, LongNameClass) | Para tudo mais |
| Quando o framework EXIGE `FROM` | Quando precisa usar outra classe |

```advpl
// HERANÇA — somente para frameworks
Class MeuRelatorio from totvs.framework.treports.integratedprovider.IntegratedProvider
    // Chamar _Super:New() no construtor
EndClass

// COMPOSIÇÃO — para tudo mais
Class MeuWorker
    Private Data oServico as object
    Public Method New() Constructor
EndClass

Method New() Class MeuWorker
    Self:oServico := OutraClasse():New()  // composição, não herança
Return Self
```

### 2.5 Convenção de Nomenclatura

| Elemento | Convenção | Exemplo |
|----------|-----------|---------|
| Nome da classe | PascalCase | `ExemploDomainManager` |
| Nome do arquivo | Dotted namespace | `custom.exemplo.manager.ExemploDomain.tlpp` |
| Namespace | Dotted lowercase | `namespace custom.exemplo.manager.ExemploDomain` |
| Métodos públicos | PascalCase | `ProcessarOrdem()` |
| Métodos privados | PascalCase | `ValidarDados()` |
| Getters | `get` + PascalCase | `getStatus()`, `getMensagem()` |
| Setters | `set` + PascalCase | `setStatus()`, `setMensagem()` |
| Data fields | Prefixo húngaro | `cNome`, `nValor`, `lAtivo`, `aItens`, `oServico`, `dData`, `jResponse` |
| Variáveis locais | Prefixo húngaro | `Local cQuery as character` |

**Prefixos húngaros:**
- `c` = character
- `n` = numeric
- `l` = logical
- `d` = date
- `a` = array
- `o` = object
- `j` = json
- `x` = multi-type/variant

### 2.6 Destrutor

**Regra:** NÃO implementar `Destroy()` a menos que a classe aloque recursos que precisem ser liberados explicitamente (connections, file handles, etc.).

O garbage collector do Protheus cuida da memória. Se precisar de cleanup:

```advpl
// Use Finalize() ou destroy() para casos excepcionais
Method destroy() Class MinhaClasse
    If ValType(Self:oConnection) == "O"
        FreeObj(Self:oConnection)
    EndIf
Return
```

### 2.7 Namespace e Includes

```advpl
// Includes obrigatórios
#Include "tlpp-core.th"      // SEMPRE para TLPP
#Include "Protheus.ch"       // SEMPRE
#Include "tlpp-rest.th"      // SOMENTE se usa @Get/@Post/@Put/@Delete
#Include "TOPCONN.CH"        // SOMENTE se usa SQL (TcGenQry, MpSysOpenQuery)

// Namespace obrigatório
namespace custom.<projeto>.<modulo>.<funcionalidade>

// Using — somente quando precisa importar classes externas
using namespace custom.<projeto>.utils
```

### 2.8 REST Annotations

```advpl
// Formato padrão de rota
@Get("/api/v1/<modulo>/<recurso>")
@Post("/api/v1/<modulo>/<recurso>")
@Put("/api/v1/<modulo>/<recurso>/:id")
@Delete("/api/v1/<modulo>/<recurso>/:id")

// SEMPRE com barra inicial /
// SEMPRE com versionamento /api/v1/
// SEMPRE com módulo: /api/v1/compras/pedido
```

---

## 3. EXEMPLOS DE REFERENCIA (padrão correto)

### 3.1 REST API (melhor exemplo: ExemploAprovacaoAPI)

```advpl
// Arquivo: custom.exemplo.api.ExemploAprovacaoAPI.tlpp
namespace custom.exemplo.api.ExemploAprovacaoAPI

Class ExemploAprovacaoAPI
    @GET("/api/v1/approvals/pending")
    Public Method getPendingApprovals() As Logical

    @PUT("/api/v1/approvals/process")
    Public Method processApproval() As Logical

    public Method New()

    Private Method getPurchaseOrders(cApprovers As Character)
    Private Method getPurchaseRequisitions(cApprovers As Character)
    Private Method groupDocuments(aFlatList As Array)
    Private Method executeApprovalAction(oData as Json)
EndClass
```

**Por que é bom:** Separação clara de público (REST) vs privado (helpers). Rotas seguem `/api/v1/`. Parâmetros tipados.

### 3.2 Domain Class (melhor exemplo: ExemploDomainManager)

```advpl
// Arquivo: custom.exemplo.manager.ExemploDomain.tlpp
namespace custom.exemplo.manager.ExemploDomain

Class ExemploDomainManager
    private data cTipoOS        as character
    private data lStatus        as logical
    private data cMensagemErro  as character
    // ... mais campos ...

    Public Method New(oJson as JSON, cTipoOS as character, cProcesso as character, cUUID) Constructor
    Public Method getStatus() as logical
    Public Method setStatus() as logical
    Public Method ProcessarDocumento()
    Public Method ValidarDocumento()
    Public Method Destroy()

    Private Method GravaTecnico()
    Private Method OSRequisicao()
EndClass

Method New(oJson as JSON, cTipoOS as character, cProcesso as character, cUUID) Class ExemploDomainManager
    self:jsonResponse := oJson
    self:cTipoOS := cTipoOS
    self:lStatus := .t.
    self:cProcesso := cProcesso
Return Self
```

**Por que é bom:** Private Data com tipos, getters/setters, construtor parametrizado com inicialização, separação público/privado.

### 3.3 Worker/Orchestrator (melhor exemplo: ExemploWorker)

```advpl
// Arquivo: custom.exemplo.integracao.ExemploWorker.tlpp
Namespace custom.exemplo.integracao.ExemploWorker
using namespace custom.exemplo.integracao.utils

Class ExemploWorker
    Private Data oServicoGED      as object
    Private Data oServicoProcesso as object
    Private Data oLogger      as object
    Private Data nDiasAtraso  as numeric

    Public Method New() Constructor
    Public Method ProcessarFila() as logical

    Private Method BuscarFilaVirtual(cAlias as character) as logical
    Private Method IniciarLogger(cW6Filial, cW6Hawb, cChaveLog) as logical
    // ... mais private methods ...
EndClass

Method New() Class ExemploWorker
    Self:oServicoGED      := custom.exemplo.integracao.ServicoGED.ServicoGED():New()
    Self:oServicoProcesso := custom.exemplo.integracao.ServicoProcesso.ServicoProcesso():New()
    Self:oLogger      := Nil
    Self:nDiasAtraso  := 2
Return Self
```

**Por que é bom:** Composição via construtor, um único método público (`ProcessarFila`), muitos private helpers, namespace completo.

---

## 4. ANTI-PATTERNS (o que NÃO fazer)

### 4.1 Construtor que NÃO retorna Self

```advpl
// ERRADO — IntegracaoExterna (APIExterna.tlpp)
Method New() Class IntegracaoExterna
Return                          // ← falta "Self"

// ERRADO — ExemploObserver (ExemploObserver.prw)
Method New() Class ExemploObserver
Return                          // ← falta "Self"

// CORRETO
Method New() Class MinhaClasse
Return Self
```

### 4.2 Data sem tipo e sem visibilidade

```advpl
// ERRADO — CustomLog3 (CustomLog3.prw)
Class CustomLog3
    Data tipo              // ← sem tipo, sem visibilidade
    Data dtger
    Data hrger
EndClass

// CORRETO
Class MinhaClasse
    Private Data cTipo   as character
    Private Data dDtGer  as date
    Private Data cHrGer  as character
EndClass
```

### 4.3 Usar `::` em vez de `Self:`

```advpl
// EVITAR — CustomLog2 (CustomLog2.prw)
METHOD New() CLASS CustomLog2
    ::cGroupLog  := ""        // ← use Self: no código novo
    ::cTimeIni   := Time()

// CORRETO
Method New() Class MinhaClasse
    Self:cGroupLog := ""
    Self:cTimeIni  := Time()
Return Self
```

### 4.4 Classe sem namespace (.tlpp)

```advpl
// ERRADO — exemploPedido (custom.exemplo.api.exemploPedido.tlpp)
#Include "Tlpp-Rest.th"
// FALTA: namespace custom.exemplo.api.exemploPedido

Class exemploPedido
    // ...
EndClass

// CORRETO
namespace custom.exemplo.api.exemploPedido

Class ExemploPedido
    // ...
EndClass
```

### 4.5 Private Data sem inicialização no construtor

```advpl
// ERRADO — ExemploUtils (custom.exemplo.fin.utils.tlpp)
Class ExemploUtils
    private data cDocumento as character
    private data cSerie     as character
    private data cArqXML    as character
    // ... 10 private data fields ...
EndClass

method new() class ExemploUtils
return self                     // ← NÃO inicializa nenhum campo!

// CORRETO
Method New() Class ExemploUtils
    Self:cDocumento := ""
    Self:cSerie     := ""
    Self:cArqXML    := ""
    // ... inicializar TODOS os campos ...
Return Self
```

### 4.6 Rotas REST sem padrão

```advpl
// INCONSISTENTE (anti-pattern):
@Post("exemplo/resultado-analise")     // sem /api/v1/, sem barra inicial
@Post("v1/exemplo/tituloPagar")               // sem barra inicial, sem /api/
@Post("exemplo/v1/pedido")                        // sem barra inicial
@POST("/api/v1/compras/exemploPedido")            // CORRETO

// CORRETO — sempre usar este formato:
@Post("/api/v1/<modulo>/<recurso>")
```

### 4.7 `CONSTRUCTOR` keyword inconsistente

```advpl
// INCONSISTENTE (anti-pattern):
Method NEW() constructor                // casing errado
Public Method New() Constructor         // CORRETO
Method New()                           // sem keyword — evitar
public Method New() CONSTRUCTOR         // casing misturado

// CORRETO — sempre assim:
Public Method New() Constructor
```

### 4.8 `EndClass` inconsistente

```advpl
// INCONSISTENTE (anti-pattern):
ENDCLASS          // all caps
End Class         // separado
endclass          // minúsculo

// CORRETO — sempre assim:
EndClass
```

### 4.9 Classe monolítica (muitas responsabilidades)

```advpl
// EVITAR — ExemploExcel (EXEMEXCEL.prw)
// ~82 Data fields, ~100+ métodos, ~10.000 linhas
// Faz TUDO: cria planilha, formata, grava, estila, importa...

// CORRETO — dividir em classes menores por responsabilidade:
// ExemploExcelWriter, ExemploExcelStyle, ExemploExcelCell, ExemploExcelTable, etc.
```

---

## 5. INTEGRAÇÃO COM OUTRAS SKILLS

### 5.1 Acesso a Dados dentro de Métodos

Dentro de métodos de classe, usar os mesmos padrões da skill `data-model`:

```advpl
// Consulta SQL em método de classe REST
Method Consultar() as logical Class MinhaAPI
    Local cQuery  as character
    Local cAlias  as character

    cAlias := GetNextAlias()
    cQuery := " SELECT ... FROM " + RetSqlName("SA1") + " SA1 "
    cQuery += " WHERE SA1.D_E_L_E_T_ = ' ' "
    cQuery += "   AND SA1.A1_FILIAL = '" + xFilial("SA1") + "' "

    MPSysOpenQuery(ChangeQuery(cQuery), cAlias)

    While !(cAlias)->(Eof())
        // ... processar ...
        (cAlias)->(DbSkip())
    EndDo
    (cAlias)->(DbCloseArea())
Return .T.
```

### 5.2 Gravação via RecLock em Classes

```advpl
// Gravação em tabela custom dentro de método de classe
Method GravarLog(cOperacao as character, cStatus as character) Class MinhaClasse
    DbSelectArea("ZZ9")
    RecLock("ZZ9", .T.)
    ZZ9->ZZ9_FILIAL := xFilial("ZZ9")
    ZZ9->ZZ9_DATA   := Date()
    ZZ9->ZZ9_HORA   := Time()
    ZZ9->ZZ9_OPER   := cOperacao
    ZZ9->ZZ9_STATUS := cStatus
    ZZ9->(MsUnlock())
Return
```

### 5.3 MsExecAuto em Classes Wrapper

```advpl
// Padrão ExecAuto wrapper
Method Incluir(aParams) Class ExecAutoFINA040
    Private lAutoErrNoFile := .T.
    Private lMsErroAuto    := .F.
    Private lMsHelpAuto    := .T.

    // Montar array de campos
    Local aFina040 := {}
    aAdd(aFina040, {"E1_FILIAL", xFilial("SE1"), Nil})
    aAdd(aFina040, {"E1_TIPO",   aParams[1],     Nil})
    // ...

    MsExecAuto({|x,y,z| FINA040(x,y,z)}, aFina040, 3)  // 3=incluir

    If lMsErroAuto
        Self:cErro := GetAutoGRLog()
    EndIf
Return
```

### 5.4 Instanciação de Classes

```advpl
// Padrão universal de instanciação
Local oClasse := NomeDaClasse():New(params)

// Com namespace completo
Local oAuth := custom.exemplo.integracao.ServicoAuth.ServicoAuth():New(nFilial)

// Com using namespace
using namespace custom.exemplo.integracao.ServicoAuth
Local oAuth := ServicoAuth():New(nFilial)

// Escopo de variáveis para instâncias:
Local oObj    // uso em escopo local (método atual) — PREFERIR
Private oObj  // compartilhar com funções chamadas — EVITAR quando possível
Static oObj   // cache/singleton — USAR com cuidado
```

---

## 6. CHECKLIST RÁPIDO

Antes de entregar uma classe, verificar:

- [ ] Arquivo `.tlpp` (não `.prw`)
- [ ] `namespace` declarado
- [ ] Todos os `#Include` necessários
- [ ] `Class...EndClass` com declarações apenas
- [ ] Métodos implementados **fora** do bloco `Class...EndClass`
- [ ] Todo `Data` com `Private/Public` + tipo (`as character`, etc.)
- [ ] `New()` com keyword `Constructor`
- [ ] `New()` retorna `Self`
- [ ] `New()` inicializa todos os `Data` fields
- [ ] Todos os métodos com `Public/Private` + return type
- [ ] Parâmetros tipados nos métodos
- [ ] `Self:` para acesso a membros (não `::`)
- [ ] Nomenclatura PascalCase para classe e métodos
- [ ] Prefixo húngaro nos Data fields
- [ ] REST routes com `/api/v1/` se for API
- [ ] `EndClass` (junto, PascalCase)