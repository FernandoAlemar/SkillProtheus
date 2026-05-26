# Template REST — User Function (Integracao / Consulta)

Referencia completa para endpoints `@Get` + `User Function` com auth `api-token`, envelope `Code/Message/itens` e `BeginSQL`.

Skill principal: [../SKILL.md](../SKILL.md)

---

## Includes obrigatorios

```tlpp
#include 'tlpp-core.th'
#include 'tlpp-rest.th'
#INCLUDE "TOTVS.CH"
#INCLUDE "PROTHEUS.CH"
#INCLUDE "TBICONN.CH"
#INCLUDE "TOPCONN.CH"
```

---

## Constantes

```tlpp
Static DATE_CHAR_LEN            := 08
Static LINE_PER_PAGE_DEFAULT    := 10
Static START_LINE_DEFAULT       := 01
Static YEAR_SUBTRACTION         := 01
Static TAMX3_FILIAL             := 12

Static HTTP_STATUS_OK           := 200
Static HTTP_STATUS_NO_CONTENT   := 204
Static HTTP_STATUS_BAD_REQUEST  := 400
Static HTTP_STATUS_UNAUTHORIZED := 401
Static HTTP_STATUS_FORBIDDEN    := 403
Static HTTP_STATUS_NOT_FOUND    := 404
```

---

## Documentacao de API (caber no fonte)

```tlpp
/*
------------------------------------------------------------------------------------------------------------
program     : <ARQUIVO>_rest.tlpp
Funcao      : get<Recurso>
Tipo        : Metodo GET - /protheus/<modulo>/<recurso>/
Descricao   : <descricao>

Parametros  :
              - Header 'api-token' (Character): Token de seguranca (Obrigatorio)
              - Query Param 'startline' (Character): Linha inicial
              - Query Param 'lineperpage' (Character): Quantidade de linhas por pagina
              - Body Params { "filial": "", "dataInicial": "", "dataFinal": "", "cnpj": "", "razaoSocial": "" }

Retorno     : JSON via oRest:setResponse (Code, Message, itens)

Estrutura Retorno:
{ "Code": 200, "Message": "...", "itens": [ ] }
------------------------------------------------------------------------------------------------------------
Atualizacoes:
- MM/AAAA - AUTOR - Criacao
------------------------------------------------------------------------------------------------------------
*/
```

---

## Entry point

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
    Local cAlias       := ""
    Local cWhere       := ""

    Local cFil         := ""
    Local cDtIni       := ""
    Local cDtFim       := ""
    Local cCnpj        := ""
    Local cRazaoSocial := ""
    Local nStartLine   := 0
    Local nLinePerPage := 0

    oRest:setKeyHeaderResponse("Content-Type", "application/json", "charset=utf-8")

    oHeader := oRest:getHeaderRequest()
    aNames  := oRest:getQueryRequest()
    cBody   := oRest:getBodyRequest()
    oBody:fromJson(cBody)

    ConOut("Requisicao recebida - Processando...")

    BEGIN SEQUENCE

        cApiToken    := oHeader["api-token"]
        nStartLine   := If(Empty(aNames["startline"]), START_LINE_DEFAULT, Val(aNames["startline"]))
        nLinePerPage := If(Empty(aNames["lineperpage"]), LINE_PER_PAGE_DEFAULT, Val(aNames["lineperpage"]))

        oBody := setDateRange(oBody)

        If ValidToken(tokenAtual, cApiToken, @oRetGet) == .F.
            BREAK
        EndIf

        If ValidParams(@nStartLine, @nLinePerPage, @oRetGet) == .F.
            BREAK
        EndIf

        setDefaultParam(@nStartLine, @nLinePerPage)

        cFil         := oBody["filial"]
        cDtIni       := oBody["dataInicial"]
        cDtFim       := oBody["dataFinal"]
        cCnpj        := If(oBody["cnpj"] == NIL, "", oBody["cnpj"])
        cRazaoSocial := If(oBody["razaoSocial"] == NIL, "", oBody["razaoSocial"])

        If ValidFilial(cFil, @oRetGet) == .F.
            BREAK
        EndIf

        If ValidDateParams(cDtIni, cDtFim, @oRetGet) == .F.
            BREAK
        EndIf

        If ValidCnpjParams(cCnpj, @oRetGet) == .F.
            BREAK
        EndIf

        If ValidOptionalParams(cCnpj, cRazaoSocial, @oRetGet) == .F.
            BREAK
        EndIf

        cWhere := SetWhere(cFil, cCnpj, cRazaoSocial, cDtIni, cDtFim)
        cAlias := executeQuery(cWhere)
        oRetGet := formatResponse(cAlias)

    END SEQUENCE

    oRest:setStatusCode(oRetGet["Code"])
    oRest:setResponse(oRetGet:toJson())

Return .T.
```

---

## Validadores

### ValidToken

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

### ValidParams / setDefaultParam

```tlpp
Static Function ValidParams(nStartLine, nLinePerPage, oRetGet)

    Local lRet := .T.

    If nStartLine == 0
        oRetGet := BuildResponse(HTTP_STATUS_FORBIDDEN, "Parametro linha inicial (startline) obrigatorio nao informado", {} )
        lRet := .F.
    EndIf

    If nLinePerPage == 0
        oRetGet := BuildResponse(HTTP_STATUS_FORBIDDEN, "Parametro linhas por pagina (lineperpage) obrigatorio nao informado", {} )
        lRet := .F.
    EndIf

Return lRet

Static Function setDefaultParam(nStartLine, nLinePerPage)

    If nLinePerPage == 0
        nLinePerPage := LINE_PER_PAGE_DEFAULT
    EndIf

    If nStartLine == 0
        nStartLine := START_LINE_DEFAULT
    EndIf

Return
```

### ValidFilial

```tlpp
Static Function ValidFilial(cFil, oRetGet)

    Local lRet := .T.

    SM0->(DbSetOrder(1))
    If SM0->(!DbSeek(M->CEMPANT + Padr(cFil, TAMX3_FILIAL)))
        oRetGet := BuildResponse(HTTP_STATUS_BAD_REQUEST, "Filial " + cFil + " nao encontrada para empresa " + M->CEMPANT, {} )
        lRet := .F.
    EndIf

Return lRet
```

### ValidDateParams

```tlpp
Static Function ValidDateParams(cDtIni, cDtFim, oRetGet)

    Local lRet           := .T.
    Local cDtIniMaisAno  := ""

    If !Empty(cDtIni)
        If Len(AllTrim(cDtIni)) != DATE_CHAR_LEN .Or. !IsDigit(AllTrim(cDtIni))
            oRetGet := BuildResponse(HTTP_STATUS_BAD_REQUEST, "Parametro dataInicial deve estar no formato YYYYMMDD", {} )
            lRet := .F.
        EndIf
    EndIf

    If !Empty(cDtFim)
        If Len(AllTrim(cDtFim)) != DATE_CHAR_LEN .Or. !IsDigit(AllTrim(cDtFim))
            oRetGet := BuildResponse(HTTP_STATUS_BAD_REQUEST, "Parametro dataFinal deve estar no formato YYYYMMDD", {} )
            lRet := .F.
        EndIf
    EndIf

    If cDtFim > DTOS(Date())
        oRetGet := BuildResponse(HTTP_STATUS_BAD_REQUEST, "Parametro dataFinal nao pode ser maior que data atual: " + DtoC(Date()), {} )
        lRet := .F.
    EndIf

    If cDtIni > cDtFim
        oRetGet := BuildResponse(HTTP_STATUS_BAD_REQUEST, "Parametro dataInicial nao pode ser maior que dataFinal", {} )
        lRet := .F.
    EndIf

    cDtIniMaisAno := DtoS(YearSum(StoD(cDtIni), YEAR_SUBTRACTION))
    If cDtFim > cDtIniMaisAno
        oRetGet := BuildResponse(HTTP_STATUS_BAD_REQUEST, "Periodo superior ao permitido de 1 ano", {} )
        lRet := .F.
    EndIf

Return lRet
```

### ValidCnpjParams (corrigido — StrTran em cInscMF)

```tlpp
Static Function ValidCnpjParams(cCpfCnpj, oRetGet)

    Local lRet    := .T.
    Local cInscMF := ""
    Local lValid  := .F.

    If Empty(cCpfCnpj)
        Return .T.
    EndIf

    cInscMF := StrTran(cCpfCnpj, ".", "")
    cInscMF := StrTran(cInscMF, "-", "")
    cInscMF := StrTran(cInscMF, "/", "")

    lValid := !Empty(cInscMF)

    If lValid .And. Len(AllTrim(cInscMF)) == 14
        If CNPJ(cInscMF) == .F.
            oRetGet := BuildResponse(HTTP_STATUS_BAD_REQUEST, "Parametro CNPJ tem formato invalido", {} )
            lRet := .F.
        EndIf

        DbSelectArea("SA2")
        SA2->(DbSetOrder(3))
        If !SA2->(DbSeek(xFilial("SA2") + cInscMF))
            oRetGet := BuildResponse(HTTP_STATUS_BAD_REQUEST, "Parametro CNPJ nao encontrado na base de dados", {} )
            lRet := .F.
        EndIf
    EndIf

Return lRet
```

### ValidOptionalParams

```tlpp
Static Function ValidOptionalParams(cCnpj, cRazaoSocial, oRetGet)

    Local lRet := .T.

    If Empty(cCnpj) .And. Empty(cRazaoSocial)
        oRetGet := BuildResponse(HTTP_STATUS_BAD_REQUEST, "Parametros CNPJ e Razao Social: informe ao menos um", {} )
        lRet := .F.
    EndIf

Return lRet
```

### setDateRange

```tlpp
Static Function setDateRange(oBody)

    Local dSys := Date()

    oBody["dataInicial"] := If(oBody["dataInicial"] == NIL .Or. Empty(oBody["dataInicial"]), DtoS(YearSub(dSys, YEAR_SUBTRACTION)), oBody["dataInicial"])
    oBody["dataFinal"]   := If(oBody["dataFinal"] == NIL .Or. Empty(oBody["dataFinal"]), DtoS(dSys), oBody["dataFinal"])

Return oBody
```

### SetWhere

```tlpp
Static Function SetWhere(cFil, cCnpj, cRazaoSocial, cDtIni, cDtFim)

    Local cWhere := " AND (SE2.E2_EMISSAO BETWEEN '" + cDtIni + "' AND '" + cDtFim + "') "

    cWhere += If(!Empty(cFil), " AND SE2.E2_FILIAL = '" + cFil + "' ", "")
    cWhere += If(!Empty(cCnpj), " AND SA2.A2_CGC = '" + cCnpj + "' ", "")
    cWhere += If(!Empty(cRazaoSocial), " AND SA2.A2_NOME LIKE '%" + AllTrim(cRazaoSocial) + "%' ", "")

Return cWhere
```

---

## Query + resposta

### executeQuery

```tlpp
Static Function executeQuery(cWhere)

    Local cAlias := GetNextAlias()

    cWhere := "% " + cWhere + " %"

    BeginSQL Alias cAlias
        %noparser%
        SELECT XSAI.*
          FROM (
                SELECT SA2.A2_FILIAL, SA2.A2_COD, SA2.A2_CGC, SA2.A2_NOME
                      ,SE2.E2_EMISSAO, SE2.E2_BAIXA, SE2.E2_SALDO, SE2.E2_VALLIQ, SE2.E2_FILIAL
                      ,ROW_NUMBER() OVER (ORDER BY SA2.A2_COD) AS linha
                  FROM %table:SE2% SE2 (NOLOCK)
                 INNER JOIN %table:SA2% SA2 (NOLOCK)
                    ON SA2.A2_COD = SE2.E2_FORNECE
                 WHERE SE2.E2_TIPO = 'PA'
                   %exp:cWhere%
                   AND SE2.%notDel%
                   AND SA2.%notDel%
               ) XSAI
         WHERE XSAI.linha BETWEEN %exp:nStartLine% AND (%exp:nStartLine% + (%exp:nLinePerPage% - 1))
    EndSQL

Return cAlias
```

### formatResponse + BuildResponse

```tlpp
Static Function formatResponse(cAlias)

    Local aItens  := {}
    Local aDoc    := {}
    Local oRet    := JsonObject():New()
    Local nIdx    := 0

    (cAlias)->(DbGoTop())
    While !(cAlias)->(Eof())

        AAdd(aItens, JsonObject():New())
        nIdx := Len(aItens)

        aItens[nIdx]["filial"]   := AllTrim((cAlias)->A2_FILIAL)
        aItens[nIdx]["codigo"]   := AllTrim((cAlias)->A2_COD)
        aItens[nIdx]["cnpj"]     := AllTrim((cAlias)->A2_CGC)
        aItens[nIdx]["nome"]     := AllTrim((cAlias)->A2_NOME)

        AAdd(aDoc, JsonObject():New())
        aDoc[Len(aDoc)]["filial"]    := AllTrim((cAlias)->E2_FILIAL)
        aDoc[Len(aDoc)]["dtemissao"] := AllTrim((cAlias)->E2_EMISSAO)
        aDoc[Len(aDoc)]["dtbaixa"]   := AllTrim((cAlias)->E2_BAIXA)
        aDoc[Len(aDoc)]["saldo"]     := (cAlias)->E2_SALDO
        aDoc[Len(aDoc)]["vlliquido"] := (cAlias)->E2_VALLIQ

        aItens[nIdx]["documento"] := aDoc
        aDoc := {}

        (cAlias)->(DbSkip())
    EndDo
    (cAlias)->(DbCloseArea())

    If Len(aItens) == 0
        oRet := BuildResponse(HTTP_STATUS_NOT_FOUND, "Nao ha dados para o periodo informado", {} )
    Else
        oRet := BuildResponse(HTTP_STATUS_OK, "Solicitacao concluida - " + AllTrim(Str(Len(aItens))) + " registros", aItens )
    EndIf

Return oRet

Static Function BuildResponse(nCode, cMessage, aItems)

    Local oRet := JsonObject():New()

    oRet["Code"]    := nCode
    oRet["Message"] := cMessage
    oRet["itens"]   := aItems

Return oRet
```

---

## Checklist do template

- [ ] 6 includes no topo
- [ ] Bloco `/* program ... */` preenchido
- [ ] `GetMV` para token — sem hardcode
- [ ] `ValidToken` antes das demais validacoes
- [ ] `Return .T.` no entry point
- [ ] `setStatusCode` com `oRetGet["Code"]` antes de `toJson` na resposta
- [ ] `Content-Type: application/json; charset=utf-8`
- [ ] `BeginSQL` com `%table:`, `%notDel:`, `%exp:`
- [ ] `(cAlias)->(DbCloseArea())` apos uso
