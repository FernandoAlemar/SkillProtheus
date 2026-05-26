# Regras de Seguranca - ADVPL/TLPP

## SEC-01 - SQL Injection

**Risco**: CRITICAL

**Descricao**: Nunca concatene variaveis diretamente em queries SQL. Use `FwPreparedStatement` com parametros nomeados (`:param`) para prevenir SQL Injection. Qualquer dado que venha de entrada do usuario, parametros REST ou variaveis externas deve ser tratado.

**Dica de Deteccao**: Procure por `+ cVariavel +` ou `+ AllTrim(variavel) +` dentro de strings que contenham SELECT, INSERT, UPDATE ou DELETE.

**VULNERAVEL**:
```advpl
User Function BuscaCli(cCodCli)
    Local cQuery := ""
    Local cAlias := GetNextAlias()

    // PERIGO: concatenacao direta permite SQL injection
    cQuery := "SELECT A1_COD, A1_NOME FROM " + RetSqlName("SA1")
    cQuery += " WHERE D_E_L_E_T_ = ' '"
    cQuery += " AND A1_COD = '" + cCodCli + "'"

    MpSysOpenQuery(cQuery, cAlias)
    // ...
    (cAlias)->(DbCloseArea())
Return
```

**SEGURO**:
```advpl
User Function BuscaCli(cCodCli)
    Local cQuery := ""
    Local cAlias := GetNextAlias()
    Local oStmt  := Nil

    oStmt := FwPreparedStatement():New()
    oStmt:SetQuery("SELECT A1_COD, A1_NOME FROM " + RetSqlName("SA1"))
    oStmt:Add(" WHERE D_E_L_E_T_ = ' '")
    oStmt:Add(" AND A1_COD = :codCli")
    oStmt:SetParam("codCli", cCodCli)

    cQuery := oStmt:GetFixQuery()
    MpSysOpenQuery(cQuery, cAlias)

    // ... processamento
    (cAlias)->(DbCloseArea())
    FreeObj(oStmt)
Return
```

---

## SEC-02 - Credenciais Hardcoded

**Risco**: CRITICAL

**Descricao**: Nunca insira senhas, tokens, chaves de API ou credenciais diretamente no codigo fonte. Use parametros do sistema (SX6) via `SuperGetMV()` ou `GetNewPar()` para armazenar valores sensiveis.

**Dica de Deteccao**: Procure por atribuicoes a variaveis com nomes como `cSenha`, `cToken`, `cApiKey`, `cPassword`, `cSecret` com valores literais.

**VULNERAVEL**:
```advpl
User Function EnviaAPI()
    Local cUrl    := "https://api.exemplo.com/dados"
    Local cToken  := "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc123"
    Local cUser   := "admin"
    Local cSenha  := "S3nh@F0rt3!"
    Local oRest   := Nil

    oRest := FWRest():New(cUrl)
    oRest:SetHeader("Authorization", cToken)
    // ...
Return
```

**SEGURO**:
```advpl
User Function EnviaAPI()
    Local cUrl    := SuperGetMV("MV_XAPURL",, "")
    Local cToken  := SuperGetMV("MV_XAPTOK",, "")
    Local cUser   := SuperGetMV("MV_XAPUSR",, "")
    Local cSenha  := SuperGetMV("MV_XAPSEN",, "")
    Local oRest   := Nil

    If Empty(cUrl) .Or. Empty(cToken)
        ConOut("SEC-02: Parametros de API nao configurados no SX6")
        Return
    EndIf

    oRest := FWRest():New(cUrl)
    oRest:SetHeader("Authorization", "Bearer " + cToken)
    // ...
Return
```

---

## SEC-03 - TLS Obrigatorio

**Risco**: HIGH

**Descricao**: Todas as chamadas HTTP externas devem usar HTTPS (TLS). Conexoes HTTP planas transmitem dados em texto claro, expondo informacoes sensiveis a interceptacao.

**Dica de Deteccao**: Procure por `"http://"` em strings usadas como URL de API ou servico externo.

**VULNERAVEL**:
```advpl
User Function IntegExt()
    Local cUrl  := "http://api.parceiro.com/v1/pedidos"
    Local oRest := FWRest():New(cUrl)

    oRest:SetHeader("Content-Type", "application/json")
    oRest:Post(cPayload)
Return
```

**SEGURO**:
```advpl
User Function IntegExt()
    Local cUrl  := SuperGetMV("MV_XINTURL",, "")
    Local oRest := Nil

    // Valida que a URL usa HTTPS
    If Left(Upper(cUrl), 5) <> "HTTPS"
        ConOut("SEC-03: URL de integracao deve usar HTTPS")
        Return
    EndIf

    oRest := FWRest():New(cUrl)
    oRest:SetHeader("Content-Type", "application/json")
    oRest:Post(cPayload)
Return
```

---

## SEC-04 - Dados Sensiveis em Logs

**Risco**: HIGH

**Descricao**: Nunca registre em log (ConOut, FWLogMsg, arquivo texto) dados sensiveis como CPF, CNPJ, senhas, tokens ou numeros de cartao. Use mascaramento para exibir apenas parte da informacao quando necessario para debug.

**Dica de Deteccao**: Procure por `ConOut` ou `FWLogMsg` cujo conteudo inclua variaveis com nomes como `cCPF`, `cCNPJ`, `cSenha`, `cToken`, `cCartao`, `A1_CGC`, `A2_CGC`.

**VULNERAVEL**:
```advpl
User Function LogCliente(cCodCli)
    Local cCPF   := SA1->A1_CGC
    Local cToken := GetToken()

    ConOut("Cliente: " + cCodCli + " CPF: " + cCPF)
    ConOut("Token utilizado: " + cToken)
    ConOut("Senha informada: " + cSenha)
Return
```

**SEGURO**:
```advpl
Static Function MascaraDado(cDado, nVisivel)
    Local cMasked := ""
    Local nTam    := Len(AllTrim(cDado))

    Default nVisivel := 4

    If nTam <= nVisivel
        cMasked := Replicate("*", nTam)
    Else
        cMasked := Replicate("*", nTam - nVisivel) + Right(AllTrim(cDado), nVisivel)
    EndIf
Return cMasked

User Function LogCliente(cCodCli)
    Local cCPF := SA1->A1_CGC

    // Mostra apenas os ultimos 4 digitos
    ConOut("Cliente: " + cCodCli + " CPF: " + MascaraDado(cCPF, 4))
    // NUNCA logar tokens ou senhas, nem mascarados
    ConOut("Operacao realizada com sucesso para cliente " + cCodCli)
Return
```

---

## SEC-05 - Validacao de RecLock

**Risco**: HIGH

**Descricao**: Sempre verifique o retorno de `RecLock()`. Quando `RecLock` falha (retorna `.F.`), o registro NAO esta travado e qualquer gravacao pode corromper dados ou sobrescrever alteracoes de outro usuario.

**Dica de Deteccao**: Procure por `RecLock(` que nao esteja dentro de um `If RecLock(`.

**VULNERAVEL**:
```advpl
User Function AtuaPreco(cProd, nPreco)
    DbSelectArea("SB1")
    DbSetOrder(1)
    DbSeek(xFilial("SB1") + cProd)

    // PERIGO: nao verifica retorno do RecLock
    RecLock("SB1", .F.)
    SB1->B1_PRV1 := nPreco
    MsUnLock()
Return .T.
```

**SEGURO**:
```advpl
User Function AtuaPreco(cProd, nPreco)
    Local lRet := .F.

    DbSelectArea("SB1")
    DbSetOrder(1)

    If DbSeek(xFilial("SB1") + cProd)
        If RecLock("SB1", .F.)
            SB1->B1_PRV1 := nPreco
            MsUnLock()
            lRet := .T.
        Else
            ConOut("SEC-05: Falha ao obter lock em SB1 para produto " + cProd)
        EndIf
    Else
        ConOut("SEC-05: Produto " + cProd + " nao encontrado em SB1")
    EndIf
Return lRet
```

---

## SEC-06 - Controle de Acesso

**Risco**: HIGH

**Descricao**: Funcoes internas criticas devem validar o contexto de chamada usando `FWIsInCallStack()`. Endpoints REST devem sempre validar autenticacao. Nunca confie que uma funcao sera chamada apenas pelo caminho esperado.

**Dica de Deteccao**: Funcoes que gravam dados ou executam operacoes criticas sem nenhuma validacao de contexto ou permissao.

**VULNERAVEL**:
```advpl
User Function DelCli(cCodCli)
    // Qualquer rotina pode chamar U_DelCli e deletar clientes
    DbSelectArea("SA1")
    DbSetOrder(1)
    If DbSeek(xFilial("SA1") + cCodCli)
        If RecLock("SA1", .F.)
            DbDelete()
            MsUnLock()
        EndIf
    EndIf
Return .T.
```

**SEGURO**:
```advpl
User Function DelCli(cCodCli)
    Local lRet := .F.

    // Valida que a chamada vem de rotina autorizada
    If !FWIsInCallStack("U_CADCLI") .And. !FWIsInCallStack("MATA030")
        ConOut("SEC-06: Chamada nao autorizada a U_DelCli")
        Return .F.
    EndIf

    // Valida permissao do usuario
    If !FWCheckPermission("DELCLI_PERM")
        ConOut("SEC-06: Usuario sem permissao para exclusao de cliente")
        Return .F.
    EndIf

    DbSelectArea("SA1")
    DbSetOrder(1)
    If DbSeek(xFilial("SA1") + cCodCli)
        If RecLock("SA1", .F.)
            DbDelete()
            MsUnLock()
            lRet := .T.
        EndIf
    EndIf
Return lRet
```

---

## SEC-07 - Retorno Nil de ExecBlock

**Risco**: MEDIUM

**Descricao**: Sempre valide o retorno de `ExecBlock()` e `U_Function()` antes de usa-lo. Ponto de entrada ou User Function chamada pode nao existir, retornar Nil ou retornar tipo inesperado.

**Dica de Deteccao**: Procure por `ExecBlock(` ou `U_` cujo retorno eh usado diretamente sem verificacao de tipo.

**VULNERAVEL**:
```advpl
User Function CalcFrete()
    Local nFrete := 0

    // PERIGO: se PE nao existir ou retornar Nil, causa erro
    nFrete := ExecBlock("CALCFRT", .F., .F.)

    // Usa diretamente sem validar
    nTotal := nSubTotal + nFrete
Return nTotal
```

**SEGURO**:
```advpl
User Function CalcFrete()
    Local nFrete   := 0
    Local xRetPE   := Nil

    // Verifica se o ponto de entrada existe
    If ExistBlock("CALCFRT")
        xRetPE := ExecBlock("CALCFRT", .F., .F.)

        // Valida tipo e conteudo do retorno
        If ValType(xRetPE) == "N"
            nFrete := xRetPE
        Else
            ConOut("SEC-07: PE CALCFRT retornou tipo invalido: " + ValType(xRetPE))
            nFrete := 0
        EndIf
    EndIf

    nTotal := nSubTotal + nFrete
Return nTotal
```

---

## SEC-08 - Autenticacao REST

**Risco**: CRITICAL

**Descricao**: Todo endpoint REST deve validar autenticacao antes de processar a requisicao. Endpoints sem autenticacao expoem dados e operacoes a qualquer chamador anonimo.

**Dica de Deteccao**: Metodos REST (`@Get`, `@Post`, etc.) que nao contem verificacao de token, Basic Auth ou OAuth no inicio do metodo.

**VULNERAVEL**:
```advpl
#Include "tlpp-core.th"
#Include "tlpp-rest.th"

Namespace custom.api.clientes

@Get("/api/v1/clientes")
Function ListaClientes()
    Local jResp := JsonObject():New()

    // PERIGO: sem autenticacao, qualquer um acessa
    jResp["data"] := GetAllClientes()

    oRest:SetResponse(jResp:ToJson())
Return .T.
```

**SEGURO**:
```advpl
#Include "tlpp-core.th"
#Include "tlpp-rest.th"

Namespace custom.api.clientes

@Get("/api/v1/clientes")
Function ListaClientes()
    Local jResp  := JsonObject():New()
    Local cToken := ""

    // Valida autenticacao
    cToken := oRest:GetHeader("Authorization")

    If Empty(cToken) .Or. !ValidaToken(cToken)
        oRest:SetStatusCode(401)
        jResp["error"] := "Token de autenticacao invalido ou ausente"
        oRest:SetResponse(jResp:ToJson())
        Return .F.
    EndIf

    jResp["data"] := GetAllClientes()
    oRest:SetResponse(jResp:ToJson())
Return .T.

Static Function ValidaToken(cToken)
    Local lValido := .F.
    // Implementar validacao do token (JWT, OAuth, etc.)
    // Verificar expiracao, assinatura, permissoes
    lValido := FWTokenValidate(cToken)
Return lValido
```

---

## SEC-09 - Integridade Transacional

**Risco**: CRITICAL

**Descricao**: Operacoes que alteram multiplas tabelas DEVEM usar `BEGIN TRANSACTION` / `END TRANSACTION` para garantir atomicidade. Se uma das operacoes falhar, todas devem ser revertidas com `DisarmTransaction()`.

**Dica de Deteccao**: Multiplos `RecLock` em tabelas diferentes sem `BEGIN TRANSACTION` envolvendo o bloco.

**VULNERAVEL**:
```advpl
User Function GravaPed(cNumPed, aItens)
    Local nI := 0

    // Grava cabecalho
    DbSelectArea("SC5")
    RecLock("SC5", .T.)
    SC5->C5_NUM := cNumPed
    SC5->C5_EMISSAO := dDataBase
    MsUnLock()

    // Grava itens - se falhar aqui, cabecalho fica orfao
    For nI := 1 To Len(aItens)
        DbSelectArea("SC6")
        RecLock("SC6", .T.)
        SC6->C6_NUM  := cNumPed
        SC6->C6_ITEM := StrZero(nI, 2)
        SC6->C6_PROD := aItens[nI][1]
        SC6->C6_QTDVEN := aItens[nI][2]
        MsUnLock()
    Next nI
Return .T.
```

**SEGURO**:
```advpl
User Function GravaPed(cNumPed, aItens)
    Local nI       := 0
    Local lRet     := .T.
    Local oError   := Nil
    Local bErrorBlk := {|e| oError := e, Break(e)}

    Begin Transaction

    Begin Sequence With bErrorBlk

        // Grava cabecalho
        DbSelectArea("SC5")
        If RecLock("SC5", .T.)
            SC5->C5_NUM    := cNumPed
            SC5->C5_EMISSAO := dDataBase
            MsUnLock()
        Else
            lRet := .F.
            Break
        EndIf

        // Grava itens
        For nI := 1 To Len(aItens)
            DbSelectArea("SC6")
            If RecLock("SC6", .T.)
                SC6->C6_NUM    := cNumPed
                SC6->C6_ITEM   := StrZero(nI, 2)
                SC6->C6_PROD   := aItens[nI][1]
                SC6->C6_QTDVEN := aItens[nI][2]
                MsUnLock()
            Else
                lRet := .F.
                Break
            EndIf
        Next nI

    Recover Using oError
        lRet := .F.
        ConOut("SEC-09: Erro na gravacao do pedido - " + oError:Description)
    End Sequence

    If lRet
        End Transaction
    Else
        DisarmTransaction()
    EndIf
Return lRet
```