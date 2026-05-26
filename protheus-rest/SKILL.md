---
name: protheus-rest
description: >
  Guia para implementar e consumir APIs REST em ADVPL/TLPP no Protheus.
  Use esta skill SEMPRE que o usuario pedir para criar endpoints REST,
  consumir APIs externas, ou trabalhar com JSON no Protheus. Padrao do time:
  includes obrigatorios (tlpp-core, tlpp-rest, TOTVS, PROTHEUS, TBICONN, TOPCONN),
  bloco de documentacao de API no cabecalho do fonte, autenticacao header api-token
  via GetMV, envelope JSON Code/Message/itens, User Function com validadores estaticos
  e BeginSQL com paginacao ROW_NUMBER. Tambem cobre TLPP Class, WSRestful legado,
  cliente FWRest/OAuth2, e anti-patterns (Return .F., credenciais hardcoded, HTTP sem TLS).
---


---

## PARTE 1 — TEMPLATE SERVIDOR REST

### 1.1 Estrutura: TLPP Moderno com Anotacoes (PADRAO DO TIME)

O estilo **TLPP com anotacoes** e o padrao atual. Novos servicos REST devem usar este formato.

```tlpp
#include 'tlpp-core.th'
#include 'tlpp-rest.th'
#INCLUDE "TOTVS.CH"
#INCLUDE "PROTHEUS.CH"
#INCLUDE "TBICONN.CH"
#INCLUDE "TOPCONN.CH"

namespace custom.<projeto>.<modulo>.api

/*/{Protheus.doc} <NomeClasse>
Descricao do servico REST
@type class
@author <autor>
@since <data>
/*/

Class <NomeClasse>

    public Method New() CONSTRUCTOR

    @GET("/api/v1/<recurso>", description='Consulta <recurso>')
    public Method consultar() as logical

    @GET("/api/v1/<recurso>/:id", description='Consulta <recurso> por ID')
    public Method consultarPorId() as logical

    @POST("/api/v1/<recurso>", description='Inclusao de <recurso>')
    public Method incluir() as logical

    @PUT("/api/v1/<recurso>/:id", description='Alteracao de <recurso>')
    public Method alterar() as logical

    @DELETE("/api/v1/<recurso>/:id", description='Exclusao de <recurso>')
    public Method excluir() as logical

EndClass

Method New() class <NomeClasse>
Return Self
```

**Convencoes de rota:**
- Prefixo: `/api/v1/`
- Recurso em lowercase: `/api/v1/pedidovenda`
- Path params: `:id` — acessado via `oRest:getPathParamsRequest()`
- Versionamento no path: `/v1/`, `/v2/`

### 1.2 Includes Obrigatorios

**Regra:** nenhum endpoint REST novo sem estes 6 includes, nesta ordem:

```tlpp
#include 'tlpp-core.th'
#include 'tlpp-rest.th'
#INCLUDE "TOTVS.CH"
#INCLUDE "PROTHEUS.CH"
#INCLUDE "TBICONN.CH"
#INCLUDE "TOPCONN.CH"
```

| Include | Uso |
|---------|-----|
| `tlpp-core.th` | Core TLPP |
| `tlpp-rest.th` | Anotacoes `@Get`, `@Post`, objeto `oRest` |
| `TOTVS.CH` / `PROTHEUS.CH` | Macros e funcoes padrao Protheus |
| `TBICONN.CH` / `TOPCONN.CH` | `BeginSQL`, aliases, integracao SQL |

### 1.2.1 Documentacao Obrigatoria no Cabecalho do Fonte

Antes da primeira `User Function` ou `Class`, incluir bloco `/* ... */` com:

| Campo | Conteudo |
|-------|----------|
| `program` | Nome do arquivo `.tlpp` |
| `Funcao` | Nome da funcao ou metodo exposto |
| `Tipo` | Verbo HTTP + rota (ex.: `Metodo GET - /protheus/fin/prepagto/`) |
| `Descricao` | Resumo funcional |
| `Parametros` | Headers, query params e body JSON (exemplo indentado) |
| `Retorno` | Como a resposta e enviada (`oRest:setResponse`, formato JSON) |
| `Exemplo de Chamada` | URL/metodo |
| `Estrutura Retorno` | JSON de exemplo com `Code`, `Message`, `itens` |
| `Atualizacoes` | Historico (data, autor, origem — ex. SP, ticket) |

**Template copiavel:**

```tlpp
/*
------------------------------------------------------------------------------------------------------------
program     : <ARQUIVO>_rest.tlpp
Funcao      : <nomeFuncao>
Tipo        : Metodo <GET|POST|PUT|DELETE> - /protheus/<modulo>/<recurso>/
Descricao   : <descricao funcional>

Parametros  :
              - Header 'api-token' (Character): Token de seguranca (Obrigatorio)
              - Query Param 'startline' (Character): Linha inicial
              - Query Param 'lineperpage' (Character): Quantidade de linhas por pagina

              - Body Params
                {
                    "filial": "0401",
                    "dataInicial": "20260108",
                    "dataFinal": "20260108",
                    "cnpj": "",
                    "razaoSocial": ""
                }

Retorno     : Resposta via oRest:setResponse no formato JSON (Code, Message, itens)

Exemplo de Chamada:
GET /protheus/<modulo>/<recurso>

Estrutura Retorno:
{
    "Code": 200,
    "Message": "Solicitacao concluida - N registros",
    "itens": [ { } ]
}
------------------------------------------------------------------------------------------------------------
Atualizacoes:
- MM/AAAA - <AUTOR> - <descricao da alteracao>
------------------------------------------------------------------------------------------------------------
*/
```

### 1.2.2 Autenticacao — Header api-token + GetMV

**Padrao obrigatorio** para endpoints novos de integracao/consulta. Auth por header `CNPJ` (secoes Class abaixo) e **legado** — nao usar em endpoints novos do time.

```tlpp
Local oHeader    := oRest:getHeaderRequest()
Local tokenAtual := GetMV("BB_TOKFLG")   // MV do projeto — nunca hardcode o token
Local cApiToken  := oHeader["api-token"]
```

Funcao estatica `ValidToken` (retorno via `@oRetGet` + `BREAK` no entry point):

```tlpp
Static Function ValidToken(tokenAtual, cApiToken, oRetGet)

    Local lRet := .T.

    If Empty(tokenAtual)
        oRetGet := BuildResponse(HTTP_STATUS_BAD_REQUEST, "Erro token procurar ADM integracao", {} )
        lRet := .F.
    EndIf

    If Empty(cApiToken)
        oRetGet := BuildResponse(HTTP_STATUS_UNAUTHORIZED, "Token nao informado no header", {} )
        lRet := .F.
    EndIf

    If AllTrim(cApiToken) <> AllTrim(tokenAtual)
        oRetGet := BuildResponse(HTTP_STATUS_FORBIDDEN, "Token de Seguranca invalido", {} )
        lRet := .F.
    EndIf

Return lRet
```

| Condicao | HTTP Code | Message (exemplo) |
|----------|-----------|-------------------|
| `Empty(tokenAtual)` — MV nao configurada | 400 | Erro token — procurar ADM integracao |
| `Empty(cApiToken)` | 401 | Token nao informado no header |
| Token divergente de `GetMV` | 403 | Token de Seguranca invalido |

Constantes HTTP recomendadas no topo do fonte:

```tlpp
Static HTTP_STATUS_OK           := 200
Static HTTP_STATUS_NO_CONTENT   := 204
Static HTTP_STATUS_BAD_REQUEST  := 400
Static HTTP_STATUS_UNAUTHORIZED := 401
Static HTTP_STATUS_FORBIDDEN    := 403
Static HTTP_STATUS_NOT_FOUND    := 404
```

### 1.3 Metodo GET — Consulta Paginada (Template Completo)

```tlpp
Method consultar() as logical Class <NomeClasse>

    Local nStatusRestHTTP := 200 as numeric
    Local jQueryString    := JsonObject():new() as object
    Local jHeader         := JsonObject():new() as object
    Local oJson           := JsonObject():New() as object
    Local aList           := {} as array
    Local cAlias          := GetNextAlias() as character
    Local cQuery          as character
    Local nPagina         as numeric
    Local nTotalPagina    as numeric
    Local oCustomLog        := CustomLog():New() as object
    Local cIdtoken        := oCustomLog:IDTOKEN as character
    Local cFilBkp         := cFilAnt as character

    Private cErrorLog     := ""
    Private bLastError    := {|oError| cErrorLog := oError:Description + oError:ErrorStack, Break(oError)}
    ErrorBlock(bLastError)

    // 1. Leitura dos parametros
    jHeader      := oRest:GetHeaderRequest()
    jQueryString := oRest:getQueryRequest()
    cFilSel      := U_GetFilByCnpj(jHeader['CNPJ'])

    Begin Sequence

        // 2. Validar filial
        If Empty(cFilSel)
            nStatusRestHTTP := 400
            Break
        Endif
        cFilAnt := cFilSel

        // 3. Paginacao
        nPagina      := Iif(!Empty(jQueryString['Page']), Val(jQueryString['Page']), 1)
        nTotalPagina := Iif(!Empty(jQueryString['PageSize']), Val(jQueryString['PageSize']), 100)

        // 4. Montar query
        cQuery := " SELECT CAMPO1, CAMPO2 "
        cQuery += " FROM " + RetSqlName("TABELA") + " (NOLOCK) "
        cQuery += " WHERE D_E_L_E_T_ = ' ' "
        cQuery += " AND FILIAL = '" + xFilial("TABELA") + "' "

        // Filtros opcionais
        If !Empty(jQueryString['filtro1'])
            cQuery += " AND CAMPO1 = '" + jQueryString['filtro1'] + "' "
        Endif

        cQuery += " ORDER BY CAMPO1 "
        cQuery += " OFFSET (" + cValToChar(nPagina - 1) + " * " + cValToChar(nTotalPagina) + ") "
        cQuery += " ROWS FETCH NEXT " + cValToChar(nTotalPagina) + " ROWS ONLY "

        MPSysOpenQuery(ChangeQuery(cQuery), cAlias)

        // 5. Montar array de resultados
        Do while (cAlias)->(!eof())
            aAdd(aList, JsonObject():New())
            aList[Len(aList)]['campo1'] := Alltrim((cAlias)->CAMPO1)
            aList[Len(aList)]['campo2'] := Alltrim((cAlias)->CAMPO2)
            (cAlias)->(dbSkip())
        End
        (cAlias)->(dbCloseArea())

        // 6. Response paginada
        oJson['hasNext'] := (Len(aList) >= nTotalPagina)
        oJson['items']   := aList

    Recover

        nStatusRestHTTP := 500

    End Sequence

    // 7. Retorno padronizado
    If nStatusRestHTTP == 200
        oRest:SetStatusCode(200)
        oRest:SetResponse(oJson:toJson())
        oCustomLog:GRAVALOG("CXXX", cIdtoken, 'Consulta OK',, , NIL, "1")
    Else
        Local jResponse := JsonObject():new()
        jResponse["code"]        := nStatusRestHTTP
        jResponse["message"]     := Iif(nStatusRestHTTP == 400, "CNPJ nao localizado", "Erro interno: " + cErrorLog)
        jResponse["transaction"] := cIdtoken
        jResponse["date"]        := FWTimeStamp(2)
        oRest:SetStatusCode(nStatusRestHTTP)
        oRest:SetResponse(jResponse:toJson())
        oCustomLog:GRAVALOG("CXXX", cIdtoken, jResponse["message"], cErrorLog, , NIL, "2")
    Endif

    cFilAnt := cFilBkp
Return .T.
```

### 1.4 Metodo POST — Inclusao (Template Completo)

```tlpp
Method incluir() as logical Class <NomeClasse>

    Local nStatusRestHTTP := 201 as numeric
    Local jBody           := JsonObject():new() as object
    Local jHeader         := JsonObject():new() as object
    Local jResponse       := JsonObject():new() as object
    Local oModel          as object
    Local oCustomLog        := CustomLog():New() as object
    Local cIdtoken        := oCustomLog:IDTOKEN as character
    Local cFilBkp         := cFilAnt as character
    Local ret             as character

    Private cErrorLog     := ""
    Private bLastError    := {|oError| cErrorLog := oError:Description + oError:ErrorStack, Break(oError)}
    ErrorBlock(bLastError)

    jHeader := oRest:GetHeaderRequest()
    ret     := jBody:FromJson(oRest:GetBodyRequest())

    Begin Sequence

        // 1. Validar filial via CNPJ
        cFilSel := U_GetFilByCnpj(jHeader['CNPJ'])
        If Empty(cFilSel)
            nStatusRestHTTP := 400
            jResponse["message"] := "CNPJ nao localizado no Protheus"
            Break
        Endif
        cFilAnt := cFilSel

        // 2. Validar JSON
        if ValType(ret) == "C"
            nStatusRestHTTP := 400
            jResponse["message"] := "JSON invalido: " + ret
            Break
        endif

        // 3. Validar campos obrigatorios
        If Empty(jBody['campo_obrigatorio'])
            nStatusRestHTTP := 400
            jResponse["message"] := "Campo 'campo_obrigatorio' e obrigatorio"
            Break
        Endif

        // 4. Processar via MVC (FWLoadModel)
        oModel := FWLoadModel("MODELID")
        oModel:SetOperation(3)  // 3=Inclusao
        oModel:Activate()

        Local oMaster := oModel:GetModel("MASTER")
        oMaster:SetValue("CAMPO1", Padr(jBody['campo1'], TamSX3("CAMPO1")[1]))
        oMaster:SetValue("CAMPO2", Padr(jBody['campo2'], TamSX3("CAMPO2")[1]))

        If oModel:VldData()
            If oModel:CommitData()
                jResponse["code"]    := 201
                jResponse["message"] := "Registro criado com sucesso"
                jResponse["id"]      := AllTrim(TABELA->CAMPO_ID)
            Else
                nStatusRestHTTP := 400
                jResponse["message"] := "Erro ao gravar dados"
            EndIf
        Else
            nStatusRestHTTP := 400
            Local aErro := oModel:GetErrorMessage()
            jResponse["message"] := FwNoAccent(cValToChar(aErro[06]))
        EndIf

        oModel:DeActivate()

    Recover

        nStatusRestHTTP := 500
        jResponse["message"] := "Erro interno: " + cErrorLog

    End Sequence

    // 5. Response padronizada
    jResponse["transaction"] := cIdtoken
    jResponse["date"]        := FWTimeStamp(2)
    oRest:SetStatusCode(nStatusRestHTTP)
    oRest:SetResponse(jResponse:toJson())

    If nStatusRestHTTP < 300
        oCustomLog:GRAVALOG("CXXX", cIdtoken, jResponse["message"],, jBody:toJson(), NIL, "1")
    Else
        oCustomLog:GRAVALOG("CXXX", cIdtoken, jResponse["message"], cErrorLog, jBody:toJson(), NIL, "2")
    Endif

    cFilAnt := cFilBkp
Return .T.
```

### 1.5 Metodo PUT — Alteracao (Template)

```tlpp
Method alterar() as logical Class <NomeClasse>

    Local nStatusRestHTTP := 200 as numeric
    Local jBody           := JsonObject():new() as object
    Local jHeader         := JsonObject():new() as object
    Local jParams         := JsonObject():new() as object
    Local jResponse       := JsonObject():new() as object
    Local oCustomLog        := CustomLog():New() as object
    Local cIdtoken        := oCustomLog:IDTOKEN as character
    Local cFilBkp         := cFilAnt as character
    Local cId             as character

    Private cErrorLog     := ""
    Private bLastError    := {|oError| cErrorLog := oError:Description + oError:ErrorStack, Break(oError)}
    ErrorBlock(bLastError)

    jHeader := oRest:GetHeaderRequest()
    ret     := jBody:FromJson(oRest:GetBodyRequest())
    jParams := oRest:getPathParamsRequest()
    cId     := jParams['id']

    Begin Sequence

        // 1. Validar filial
        cFilSel := U_GetFilByCnpj(jHeader['CNPJ'])
        If Empty(cFilSel)
            nStatusRestHTTP := 400
            jResponse["message"] := "CNPJ nao localizado"
            Break
        Endif
        cFilAnt := cFilSel

        // 2. Validar JSON e ID
        if ValType(ret) == "C"
            nStatusRestHTTP := 400
            jResponse["message"] := "JSON invalido: " + ret
            Break
        endif

        If Empty(cId)
            nStatusRestHTTP := 400
            jResponse["message"] := "ID e obrigatorio"
            Break
        Endif

        // 3. Localizar registro
        TABELA->(DbSetOrder(1))
        If !TABELA->(MsSeek(xFilial("TABELA") + cId))
            nStatusRestHTTP := 404
            jResponse["message"] := "Registro nao localizado: " + cId
            Break
        Endif

        // 4. Alterar via MVC
        oModel := FWLoadModel("MODELID")
        oModel:SetOperation(4)  // 4=Alteracao
        oModel:Activate()

        Local oMaster := oModel:GetModel("MASTER")
        If !Empty(jBody['campo1'])
            oMaster:SetValue("CAMPO1", Padr(jBody['campo1'], TamSX3("CAMPO1")[1]))
        Endif

        If oModel:VldData() .And. oModel:CommitData()
            jResponse["message"] := "Registro atualizado com sucesso"
        Else
            nStatusRestHTTP := 400
            Local aErro := oModel:GetErrorMessage()
            jResponse["message"] := FwNoAccent(cValToChar(aErro[06]))
        EndIf

        oModel:DeActivate()

    Recover

        nStatusRestHTTP := 500
        jResponse["message"] := "Erro interno: " + cErrorLog

    End Sequence

    jResponse["transaction"] := cIdtoken
    jResponse["date"]        := FWTimeStamp(2)
    oRest:SetStatusCode(nStatusRestHTTP)
    oRest:SetResponse(jResponse:toJson())

    If nStatusRestHTTP < 300
        oCustomLog:GRAVALOG("CXXX", cIdtoken, jResponse["message"],, jBody:toJson(), NIL, "1")
    Else
        oCustomLog:GRAVALOG("CXXX", cIdtoken, jResponse["message"], cErrorLog, jBody:toJson(), NIL, "2")
    Endif

    cFilAnt := cFilBkp
Return .T.
```

### 1.6 Padrao de Response JSON

#### 1.6.1 Padrao principal do time — `Code` / `Message` / `itens`

Envelope obrigatorio para endpoints de integracao/consulta (PascalCase nas chaves):

```json
{
  "Code": 200,
  "Message": "Solicitacao concluida - 10 registros",
  "itens": [
    {
      "filial": "01",
      "codigo": "000009",
      "documento": [ { "dtemissao": "20250721", "saldo": 799.7 } ]
    }
  ]
}
```

Funcao `BuildResponse`:

```tlpp
Static Function BuildResponse(nCode, cMessage, aItems)

    Local oRet := JsonObject():New()

    oRet["Code"]    := nCode
    oRet["Message"] := cMessage
    oRet["itens"]   := aItems

Return oRet
```

Saida no entry point (sempre `Return .T.` — status via `setStatusCode`):

```tlpp
Local cRetJson := ""
Local nCode    := 0

oRest:setKeyHeaderResponse("Content-Type", "application/json", "charset=utf-8")

// ... Begin Sequence com validacoes e oRetGet := BuildResponse(...) ...

nCode    := oRetGet["Code"]
cRetJson := oRetGet:toJson()
oRest:setStatusCode(nCode)
oRest:setResponse(cRetJson)

Return .T.
```

| Situacao | Code tipico |
|----------|-------------|
| Sucesso com dados | 200 |
| Sucesso sem dados | 404 — `"Nao ha dados para o periodo informado"` |
| Validacao | 400 |
| Token ausente | 401 |
| Token invalido | 403 |

#### 1.6.2 Padroes legados (Class / APIs antigas)

**GET paginado (Class):**
```json
{
  "hasNext": true,
  "items": [
    {"campo1": "valor1", "campo2": "valor2"}
  ]
}
```

**POST/PUT/DELETE (Class + CustomLog):**
```json
{
  "code": 201,
  "message": "Registro criado com sucesso",
  "id": "000001",
  "transaction": "uuid-de-rastreio",
  "date": "2024-01-15 10:30:00"
}
```

### 1.8 Padrao User Function — Integracao / Consulta (PADRAO DO TIME)

Template completo e anotado: [references/rest-integracao-template.md](references/rest-integracao-template.md).

**Quando usar:** APIs de consulta/integracao com `@Get` + `User Function`, body JSON, paginacao `startline`/`lineperpage`, validadores estaticos.

**Quando usar Class (secao 1.1):** CRUD com MVC, multiplos verbos na mesma classe, rotas `/api/v1/`.

#### Arquitetura do fonte

| Funcao estatica | Responsabilidade |
|-----------------|------------------|
| Constantes `Static` | `HTTP_STATUS_*`, `LINE_PER_PAGE_DEFAULT`, `START_LINE_DEFAULT`, `DATE_CHAR_LEN` |
| `User Function` + `@Get("/protheus/<mod>/<recurso>")` | Entry point — leitura header/query/body, `Begin Sequence`, resposta |
| `ValidToken` | Auth `api-token` vs `GetMV` |
| `ValidParams` | Query `startline` / `lineperpage` obrigatorios |
| `setDefaultParam` | Defaults se zero |
| `setDateRange` | Defaults `dataInicial` / `dataFinal` no body |
| `ValidFilial` | `SM0` + `M->CEMPANT` |
| `ValidDateParams` | `YYYYMMDD`, max 1 ano, `dataFinal` <= hoje |
| `ValidCnpjParams` | `CNPJ()` + `DbSeek` SA2 se informado |
| `ValidOptionalParams` | Ao menos um: `cnpj` ou `razaoSocial` |
| `SetWhere` | Clausulas `AND` dinamicas |
| `executeQuery` | `BeginSQL` + `ROW_NUMBER` + paginacao `BETWEEN` |
| `formatResponse` | Monta array `itens` (arrays aninhados ex. `documento`) |
| `BuildResponse` | Envelope `Code` / `Message` / `itens` |

#### Entry point — fluxo obrigatorio

```tlpp
@Get("/protheus/<modulo>/<recurso>")
User Function get<Recurso>()

    Local cRetJson     := ""
    Local cBody        := ""
    Local aNames       := {}
    Local oRetGet      := JsonObject():New()
    Local oHeader      := NIL
    Local oBody        := JsonObject():New()
    Local tokenAtual   := GetMV("BB_TOKFLG")
    Local cApiToken    := ""
    Local nStartLine   := 0
    Local nLinePerPage := 0

    oRest:setKeyHeaderResponse("Content-Type", "application/json", "charset=utf-8")

    oHeader := oRest:getHeaderRequest()
    aNames  := oRest:getQueryRequest()
    cBody   := oRest:getBodyRequest()
    oBody:fromJson(cBody)

    BEGIN SEQUENCE

        nStartLine   := If(Empty(aNames["startline"]), START_LINE_DEFAULT, Val(aNames["startline"]))
        nLinePerPage := If(Empty(aNames["lineperpage"]), LINE_PER_PAGE_DEFAULT, Val(aNames["lineperpage"]))

        oBody := setDateRange(oBody)

        If ValidToken(tokenAtual, cApiToken := oHeader["api-token"], @oRetGet) == .F.
            BREAK
        EndIf

        If ValidParams(@nStartLine, @nLinePerPage, @oRetGet) == .F.
            BREAK
        EndIf

        setDefaultParam(@nStartLine, @nLinePerPage)

        // ... demais validacoes, SetWhere, executeQuery, formatResponse ...

    END SEQUENCE

    cRetJson := oRetGet:toJson()
    oRest:setStatusCode(oRetGet["Code"])
    oRest:setResponse(cRetJson)

Return .T.
```

#### Paginacao SQL (ROW_NUMBER)

```tlpp
BeginSQL Alias cAlias
    %noparser%
    SELECT X.*
      FROM (
            SELECT CAMPO1, CAMPO2
                  ,ROW_NUMBER() OVER (ORDER BY CAMPO1) AS linha
              FROM %table:TABELA% TAB (NOLOCK)
             WHERE TAB.%notDel%
                   %exp:cWhere%
           ) X
     WHERE X.linha BETWEEN %exp:nStartLine% AND (%exp:nStartLine% + (%exp:nLinePerPage% - 1))
EndSQL
```

Consulte `advpl-embedded-sql` para macros `%table:`, `%notDel:`, `%exp:`.

#### Convencoes de rota (integracao)

- Prefixo: `/protheus/<modulo>/` (ex.: `/protheus/fin/prepagto`)
- Modulo: `fin`, `contabil`, `est`, etc. (sigla do dominio)
- Query params: `startline`, `lineperpage` (case-insensitive no array de query)

### 1.7 Referencia: Estilo WSRestful Classico (Legado)

Nao usar para novos servicos. Referencia apenas para manutencao dos existentes.

**Includes:**
```advpl
#include 'totvs.ch'
#include 'restful.ch'
```

**Declaracao:**
```advpl
WSRESTFUL wsNomeServico DESCRIPTION 'Descricao' FORMAT APPLICATION_JSON
    WSDATA Page      AS INTEGER OPTIONAL
    WSDATA PageSize  AS INTEGER OPTIONAL
    WSDATA id        AS String  OPTIONAL

    WSMETHOD POST metodo; PATH '/v1/recurso'; PRODUCES APPLICATION_JSON
    WSMETHOD GET  metodo; PATH '/v1/recurso'; PRODUCES APPLICATION_JSON
ENDWSRESTFUL
```

**Implementacao:**
```advpl
WSMETHOD POST metodo WSRECEIVE WSSERVICE wsNomeServico
    Local cJsonCont := Self:GetContent()     // body
    Local cFilSel   := U_GetFilByCnpj(Self:GetHeader('CNPJ'))  // auth
    ...
    Self:SetStatus(201)
    Self:SetResponse(FWJsonSerialize(oReturn))
Return lRet

WSMETHOD PUT metodo PATHPARAM id WSRECEIVE WSSERVICE wsNomeServico
    Local cId := self:id       // path param
    ...
Return lRet
```

---

## PARTE 2 — TEMPLATE CLIENTE REST (Consumo de API Externa)

### 2.1 Cliente com FWRest (Padrao do Time)

```tlpp
/*/{Protheus.doc} ChamaAPIExterna
Exemplo de consumo de API externa com FWRest
@type function
@author <autor>
@since <data>
/*/
Static Function ChamaAPIExterna(cEndpoint, cMethod, cBody, cToken)

    Local oRest    := FWRest():New(SuperGetMV("MV_APIURL", .F., "https://api.exemplo.com"))
    Local oJson    := JsonObject():New()
    Local aHeaders := {} as array
    Local nStatus  as numeric
    Local cError   as character
    Local cResult  as character
    Local lRet     := .F. as logical

    // 1. Configurar request
    oRest:setPath(cEndpoint)
    oRest:SetChkStatus(.F.)

    // 2. Headers
    aAdd(aHeaders, "Content-Type: application/json")
    aAdd(aHeaders, "Accept: application/json")
    If !Empty(cToken)
        aAdd(aHeaders, "Authorization: Bearer " + cToken)
    Endif

    // 3. Body (para POST/PUT)
    If !Empty(cBody)
        oRest:SetPostParams(cBody)
    Endif

    // 4. Executar request
    If cMethod == "GET"
        lRet := oRest:Get(aHeaders)
    ElseIf cMethod == "POST"
        lRet := oRest:Post(aHeaders)
    ElseIf cMethod == "PUT"
        lRet := oRest:Put(aHeaders)
    ElseIf cMethod == "DELETE"
        lRet := oRest:Delete(aHeaders)
    Endif

    // 5. Verificar resultado
    If lRet
        nStatus := HTTPGetStatus(@cError)
        If nStatus >= 200 .And. nStatus <= 299
            cResult := oRest:GetResult()
            oJson:FromJson(cResult)
            // Processar oJson...
            lRet := .T.
        Else
            ConOut("HTTP Error " + cValToChar(nStatus) + ": " + cError)
            lRet := .F.
        Endif
    Else
        ConOut("Transport Error: " + oRest:GetLastError())
        lRet := .F.
    Endif

    FreeObj(oRest)
    FreeObj(oJson)

Return lRet
```

### 2.2 Cliente com HTTPQuote (Quando Precisa Ler Headers de Resposta)

```tlpp
Static Function ChamaComHeaders(cFullUrl, cMethod, cBody, aHeaders)

    Local cResponse   as character
    Local cHeaderRet  as character
    Local nStatus     as numeric
    Local cError      as character

    cResponse := HTTPQuote(cFullUrl, Upper(cMethod), "", cBody, 30, aHeaders, @cHeaderRet)
    nStatus   := HTTPGetStatus(@cError)

    If nStatus >= 200 .And. nStatus <= 299
        // Sucesso — cHeaderRet contem headers de resposta como string bruta
        // Parse manual se necessario (ex: extrair Set-Cookie, Location)
    Else
        ConOut("Erro HTTP " + cValToChar(nStatus) + ": " + cError)
    Endif

Return cResponse
```

### 2.3 Padrao de Autenticacao — OAuth2 Client Credentials

```tlpp
Static Function ObtemTokenOAuth2()

    Local cUrl      := SuperGetMV("MV_AUTHURL", .F., "")
    Local cClientId := SuperGetMV("MV_CLID", .F., "")
    Local cSecret   := SuperGetMV("MV_CLSEC", .F., "")
    Local cToken    as character
    Local aHeaders  := {} as array
    Local cBody     as character
    Local cResponse as character
    Local cHeaderRet as character
    Local oJson     := JsonObject():New()

    aAdd(aHeaders, "Content-Type: application/x-www-form-urlencoded")

    cBody := "grant_type=client_credentials"
    cBody += "&client_id=" + cClientId
    cBody += "&client_secret=" + cSecret

    cResponse := HttpPost(cUrl, "", cBody, 30, aHeaders, @cHeaderRet)

    If HTTPGetStatus() >= 200 .And. HTTPGetStatus() <= 299
        oJson:FromJson(cResponse)
        cToken := oJson["access_token"]
    Endif

    FreeObj(oJson)

Return cToken
```

### 2.4 Padrao de Autenticacao — Bearer Token Login

```tlpp
Static Function ObtemTokenLogin()

    Local oRest   := FWRest():New(SuperGetMV("MV_APIURL", .F., ""))
    Local oJson   := JsonObject():New()
    Local oBody   := JsonObject():New()
    Local aHeaders := {} as array
    Local cToken  as character

    oRest:setPath("/api/auth/login")
    oRest:SetChkStatus(.F.)

    aAdd(aHeaders, "Content-Type: application/json")

    oBody["username"] := SuperGetMV("MV_APIUSR", .F., "")
    oBody["password"] := SuperGetMV("MV_APIPWD", .F., "")
    oRest:SetPostParams(oBody:ToJson())

    If oRest:Post(aHeaders)
        If HTTPGetStatus() >= 200 .And. HTTPGetStatus() <= 299
            oJson:FromJson(oRest:GetResult())
            cToken := oJson["access_token"]
        Endif
    Endif

    FreeObj(oRest)
    FreeObj(oJson)
    FreeObj(oBody)

Return cToken
```

### 2.5 Padrao de Retry

```tlpp
Static Function HttpComRetry(oRest, aHeaders, cMethod, nMaxRetry)

    Local lSucesso := .F. as logical
    Local nTentativa := 0 as numeric

    Default nMaxRetry := 3

    While nTentativa < nMaxRetry .And. !lSucesso
        nTentativa++

        If cMethod == "GET"
            lSucesso := oRest:Get(aHeaders)
        ElseIf cMethod == "POST"
            lSucesso := oRest:Post(aHeaders)
        Endif

        If lSucesso
            If HTTPGetStatus() >= 200 .And. HTTPGetStatus() <= 299
                lSucesso := .T.
            ElseIf HTTPGetStatus() >= 500   // Retry apenas em erros de servidor
                lSucesso := .F.
                TSleep(2000 * nTentativa)   // Backoff progressivo
            Else
                Exit  // Erro 4xx nao faz retry
            Endif
        Else
            TSleep(2000 * nTentativa)
        Endif
    EndDo

Return lSucesso
```

### 2.6 Parse de JSON — Padrao do Time

```tlpp
// PADRAO A — JsonObject (preferido para novos codigos)
oJson := JsonObject():New()
cParseErr := oJson:FromJson(cResponse)

If cParseErr == NIL        // NIL = parse OK
    cValue := oJson["chave"]
    aItens := oJson["items"]
Else
    ConOut("Erro parse JSON: " + cParseErr)
Endif
FreeObj(oJson)

// PADRAO B — FWJsonDeserialize (usado em codigo legado)
Local oJson
FWJsonDeserialize(cResponse, @oJson)
cValue := oJson:CHAVE          // dot-notation, MAIUSCULO
FreeObj(oJson)
```

### 2.7 Leitura de Response Headers (FWRest)

```tlpp
// Para acessar headers de resposta com FWRest:
For nI := 1 to Len(oRest:ORESPONSEH:AHEADERFIELDS)
    If Alltrim(oRest:ORESPONSEH:AHEADERFIELDS[nI][1]) == 'Location'
        cLocation := oRest:ORESPONSEH:AHEADERFIELDS[nI][2]
    Endif
Next nI
```

---

## PARTE 3 — REGRAS OBRIGATORIAS

### 3.1 Obrigatorias

1. **Sempre fazer backup e restore de cFilAnt:**
   ```tlpp
   Local cFilBkp := cFilAnt
   // ... codigo ...
   cFilAnt := cFilBkp   // restaura no final
   ```

2. **Sempre usar CustomLog para logging:**
   ```tlpp
   Local oCustomLog := CustomLog():New()
   Local cIdtoken  := oCustomLog:IDTOKEN    // UUID unico
   // Sucesso:
   oCustomLog:GRAVALOG("CXXX", cIdtoken, 'Msg',, jBody:toJson(), NIL, "1")
   // Erro:
   oCustomLog:GRAVALOG("CXXX", cIdtoken, 'Msg', cStack, jBody:toJson(), NIL, "2")
   ```

3. **Sempre validar o parse JSON antes de usar:**
   ```tlpp
   ret := jBody:FromJson(oRest:GetBodyRequest())
   if ValType(ret) == "C"
       // ret contem string de erro — JSON invalido
       Break
   endif
   ```

4. **Sempre usar `FreeObj()` ao final:**
   ```tlpp
   FreeObj(oRest)
   FreeObj(oJson)
   FreeObj(oCustomLog)
   ```

5. **URLs e credenciais via SuperGetMV (nunca hardcoded):**
   ```tlpp
   cUrl   := SuperGetMV("MV_APIURL", .F., "https://default.url")
   cToken := SuperGetMV("MV_TOKEN", .F., "")
   ```

6. **Paginacao padrao: `Page`/`PageSize` com response `hasNext`/`items`**

7. **Autenticacao endpoints novos: header `api-token` + `GetMV("<MV_TOKEN>")` + `ValidToken()`** — ver secao 1.2.2. Legado Class: CNPJ no header -> `U_GetFilByCnpj()`

8. **Usar `ErrorBlock` para capturar excecoes inesperadas:**
   ```tlpp
   Private cErrorLog := ""
   Private bLastError := {|oError| cErrorLog := oError:Description + oError:ErrorStack, Break(oError)}
   ErrorBlock(bLastError)
   ```

9. **SEMPRE retornar `.T.` em methods REST anotados (`@Get`/`@Post`/`@Put`/`@Delete`):**
   Em TLPP REST com anotacoes, o `Return` do method e um sinal para o **framework**, nao o HTTP status:
   - `Return .T.` = "eu tratei a requisicao" — framework usa o StatusCode/Response que voce definiu via `oRest:SetStatusCode()`
   - `Return .F.` = "eu falhei" — framework **descarta** seu SetStatusCode e retorna **HTTP 500**

   O HTTP status code e controlado **exclusivamente** por `oRest:SetStatusCode()`. O Return so diz ao framework se o method tratou a requisicao.
   ```tlpp
   // ERRADO — Return .F. causa HTTP 500 mesmo com SetStatusCode(400)
   oRest:SetStatusCode(400)
   oRest:SetResponse(oResponse:ToJson())
   Return .F.   // Framework sobrescreve com 500!

   // CORRETO — Return .T. respeita o SetStatusCode(400)
   oRest:SetStatusCode(400)
   oRest:SetResponse(oResponse:ToJson())
   Return .T.   // Framework devolve 400 conforme definido
   ```

### 3.2 Recomendadas

9. **Usar `TamSX3("CAMPO")[1]` ao setar valores com `Padr()`**

10. **Usar `DecodeUTF8()` para strings recebidas de APIs externas**

11. **Usar `FwNoAccent()` ao retornar mensagens de erro do MVC**

12. **Usar `ChangeQuery()` ao abrir queries SQL:**
    ```tlpp
    MPSysOpenQuery(ChangeQuery(cQuery), cAlias)
    ```

13. **Sempre fechar alias apos uso:**
    ```tlpp
    (cAlias)->(dbCloseArea())
    ```

14. **Para FWRest, sempre chamar `SetChkStatus(.F.)` e verificar status manualmente**

15. **Sempre chamar `HTTPGetStatus(@cError)` apos qualquer chamada HTTP**

---

## PARTE 4 — ANTI-PATTERNS ENCONTRADOS

### 4.1 CRITICO — Return .F. em Method REST TLPP (Causa HTTP 500 Silencioso)

**Problema:**
```tlpp
// ERRADO — Method REST retorna .F. em caso de erro de negocio
Method getPendingApprovals() Class MinhaAPI
    If Empty(cEmail)
        oRest:SetStatusCode(400)
        oResponse['message'] := "Email nao encontrado"
        oRest:SetResponse(oResponse:ToJson())
        Return .F.    // CAUSA HTTP 500! Framework ignora o SetStatusCode(400)
    EndIf
    ...
Return .T.
```

**Sintoma:** API retorna HTTP 500 mesmo tendo chamado `SetStatusCode(400)` corretamente. Logs mostram que o codigo executou ate o ponto de erro, mas o status HTTP final e 500.

**Causa:** Em TLPP REST com anotacoes (`@Get`/`@Post`/`@Put`/`@Delete`), `Return .F.` sinaliza ao framework que o method **falhou no tratamento da requisicao**. O framework entao descarta qualquer `SetStatusCode()` e `SetResponse()` que tenham sido chamados e retorna HTTP 500 automaticamente.

**Correto:**
```tlpp
// CORRETO — Sempre Return .T., status controlado por SetStatusCode()
Method getPendingApprovals() Class MinhaAPI
    If Empty(cEmail)
        oRest:SetStatusCode(400)
        oResponse['message'] := "Email nao encontrado"
        oRest:SetResponse(oResponse:ToJson())
        Return .T.    // Framework respeita o SetStatusCode(400)
    EndIf
    ...
Return .T.
```

**Regra:** Methods REST anotados devem **SEMPRE** retornar `.T.`. O HTTP status code e controlado exclusivamente por `oRest:SetStatusCode()`.

### 4.2 CRITICO — Credenciais Hardcoded

**Problema:**
```tlpp
// ERRADO — credenciais hardcoded no fonte
oBody["Login"] := "user@exemplo.com.br"
oBody["Senha"] := "SenhaAqui123"
```

**Correto:**
```tlpp
oBody["Login"] := SuperGetMV("XX_LOGIN", .F., "")
oBody["Senha"] := SuperGetMV("XX_PASSW", .F., "")
```

### 4.3 CRITICO — HTTP Sem TLS

**Problema:**
```tlpp
// ERRADO
cUrl := "http://www.api.exemplo.com.br:8080/"   // dados em texto plano
```

**Correto:** Sempre usar HTTPS. Se o servico externo nao suporta, documentar o risco.

### 4.4 ALTO — JSON Body via GET

**Problema:**
```tlpp
// ERRADO
HttpGet(cEndpoint, oJsonTkn:ToJson(), nTimeout, aHeader, @cHeaderGet)
// O 2o parametro de HttpGet e query string, nao body
```

**Correto:** Usar POST quando precisa enviar body JSON.

### 4.5 ALTO — Envelope de Response Inconsistente

**Problema:** POST retorna formatos diferentes entre servicos:
```json
// Servico A: {"id": "001", "status": true, "date": "..."}
// Servico B: {"code": 201, "message": "...", "transaction": "..."}
// Servico C: {"success": true, "message": "..."}
```

**Correto:** Usar sempre o envelope padrao:
```json
{"code": 201, "message": "...", "id": "...", "transaction": "uuid", "date": "..."}
```

### 4.6 MEDIO — Status Code Inconsistente

**Problema:** POST retorna 200, 201 ou 202 conforme o servico.

**Correto:**
- `200` = GET sucesso, PUT/DELETE sucesso
- `201` = POST sucesso (recurso criado)
- `400` = Validacao falhou
- `404` = Recurso nao encontrado
- `500` = Erro interno

### 4.7 MEDIO — Validacao Campo-a-Campo Sem Reutilizacao

**Problema:**
```tlpp
// ERRADO — cada metodo repete validacao manual
If Empty(oJson:GetJsonObject('campo1'))
    SetRestFault(cIdtoken, "Campo1 obrigatorio", .T., 400)
    Break
Endif
If Empty(oJson:GetJsonObject('campo2'))
    SetRestFault(cIdtoken, "Campo2 obrigatorio", .T., 400)
    Break
Endif
// ... 20+ campos validados um a um
```

**Sugestao:** Criar funcao helper para validar campos obrigatorios:
```tlpp
Static Function ValidaCampos(jBody, aCamposObrig)
    Local nI as numeric
    For nI := 1 To Len(aCamposObrig)
        If Empty(jBody[aCamposObrig[nI]])
            Return "Campo '" + aCamposObrig[nI] + "' e obrigatorio"
        Endif
    Next nI
Return ""
```

### 4.8 MEDIO — Falta de Retry em Chamadas Externas

**Problema:** 13 de 15 integracoes nao tem retry.

**Correto:** Implementar retry com backoff para APIs externas (ver template 2.5).

### 4.9 BAIXO — Naming Convention Inconsistente nas Rotas

**Problema:**
```
/v1/tabelaPreco        (camelCase)
/api/v1/pedidovenda    (lowercase)
exemplo/resultado-analise  (kebab-case, sem /api/, sem versao)
```

**Correto:** Padronizar em `/api/v1/<recurso>` lowercase.

### 4.10 BAIXO — PageSize Default Inconsistente

**Problema:** Default varia entre 100, 500 e 10000.

**Correto:** Padronizar default em 100 com max configuravel via SuperGetMV.

---

## PARTE 5 — EXEMPLOS DE REFERENCIA

### 5.1 Servidor REST — TLPP Moderno (REFERENCIA)

Melhor exemplo de classe TLPP REST limpa:
- Declaracao com `@GET`/`@PUT` anotacoes
- Metodos private para logica de negocio
- Response padronizada com `success`/`message`
- Validacao de campos obrigatorios
- Sem dependencia de CNPJ (usa usuario logado)

### 5.2 Servidor REST — WSRestful Classico (REFERENCIA)

Exemplo mais completo de WSRestful com:
- 4 metodos (POST, PUT, GET lista, GET por ID)
- WSDATA com paginacao
- PATHPARAM para path params
- BeginSQL com `%Table%` e `%NotDel%`
- `FWLoadModel` para CRUD
- CustomLog para logging
- `U_GetFilByCnpj()` para autenticacao

### 5.3 Cliente HTTP — FWRest com OAuth2 (REFERENCIA)

Exemplo completo de OAuth2 client_credentials:
- `HttpPost` para token request
- `FWRest` para chamadas subsequentes
- Leitura de response headers via `:ORESPONSEH:AHEADERFIELDS`
- Notificacao de erro por email

### 5.4 Cliente HTTP — Session/Cookie Auth (REFERENCIA)

Exemplo avancado com:
- `HTTPQuote` para acesso a headers de resposta
- Regex para extrair cookie
- Cache de sessao em tabela (SZ0)
- Lock distribuido para prevenir login concorrente
- Retry com backoff

### 5.5 Cliente HTTP — Classe Dedicada (REFERENCIA)

Exemplo de wrapper OOP para API:
- Classe `ConsultaAPIWs` encapsula toda integracao
- Metodos dedicados: `BuscaCnpj()`, `GetHeader()`, `Consumo()`
- URL e headers configurados no construtor
- Mapeamento de response para campos Protheus

---

## RESUMO RAPIDO — CHECKLIST

### Novo Servico REST — Integracao (User Function, padrao do time):
- [ ] 6 includes obrigatorios (secao 1.2)
- [ ] Bloco `/* program/Funcao/Tipo/Parametros/Retorno/Atualizacoes */` no cabecalho
- [ ] `@Get("/protheus/<mod>/<recurso>")` + `User Function`
- [ ] Auth: header `api-token` + `GetMV("BB_TOKFLG")` + `ValidToken()`
- [ ] Response: `BuildResponse` com `Code`, `Message`, `itens` (secao 1.6.1)
- [ ] `oRest:setKeyHeaderResponse("Content-Type", "application/json", "charset=utf-8")`
- [ ] Paginacao: query `startline` / `lineperpage` + `ROW_NUMBER` no SQL
- [ ] Validadores estaticos com `@oRetGet` + `BREAK` em `Begin Sequence`
- [ ] `Return .T.` — status via `setStatusCode`, nunca `Return .F.` (secao 4.1)
- [ ] Template completo: [references/rest-integracao-template.md](references/rest-integracao-template.md)

### Novo Servico REST — Class (CRUD / MVC):
- [ ] Usar TLPP com anotacoes (`@GET`, `@POST`, etc.) + namespace
- [ ] Prefixo `/api/v1/<recurso>` lowercase
- [ ] Mesmos 6 includes da secao 1.2
- [ ] Auth legada: `U_GetFilByCnpj(jHeader['CNPJ'])` — preferir api-token em endpoints novos
- [ ] Backup: `cFilBkp := cFilAnt` no inicio, restaurar no final
- [ ] Log: `CustomLog():New()` com `GRAVALOG()` para sucesso ("1") e erro ("2")
- [ ] Erros: `ErrorBlock` + `Begin Sequence`
- [ ] GET paginado: `Page`/`PageSize`, response legado `{hasNext, items}`
- [ ] POST/PUT/DELETE: response legado `{code, message, id, transaction, date}`
- [ ] `FreeObj()` em todos os objetos ao final

### Nova Integracao Externa (Cliente):
- [ ] Usar `FWRest():New()` (preferido) ou `HTTPQuote` (quando precisa headers)
- [ ] `SetChkStatus(.F.)` + `HTTPGetStatus(@cError)` manual
- [ ] URLs e credenciais via `SuperGetMV()` — nunca hardcode
- [ ] Sempre HTTPS
- [ ] `JsonObject():FromJson()` para parse — validar retorno `!= NIL`
- [ ] Retry com backoff para APIs criticas
- [ ] Log da comunicacao (request/response)
- [ ] `FreeObj()` em todos os objetos
- [ ] Cache de token em tabela se token tiver validade longa