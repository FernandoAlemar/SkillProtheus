# Regras de Boas Praticas - ADVPL/TLPP

## BP-01 - Notacao Hungara

**Severidade**: WARNING

**Descricao**: Todas as variaveis devem seguir a notacao hungara padrao do Protheus. O prefixo indica o tipo de dado armazenado na variavel.

**Tabela de Prefixos**:

| Prefixo | Tipo        | Exemplo      |
|---------|-------------|--------------|
| c       | Character   | cNome        |
| n       | Numeric     | nValor       |
| d       | Date        | dEmissao     |
| l       | Logical     | lConfirma    |
| a       | Array       | aItens       |
| o       | Object      | oModel       |
| b       | Block       | bCondicao    |
| x       | Variant     | xRetorno     |
| j       | JSON        | jPayload     |

**ERRADO**:
```advpl
User Function Teste()
    Local nome     := "Joao"
    Local valor    := 100.50
    Local ativo    := .T.
    Local lista    := {}
    Local dt       := dDataBase
    Local retorno  := Nil
Return
```

**CORRETO**:
```advpl
User Function Teste()
    Local cNome    := "Joao"
    Local nValor   := 100.50
    Local lAtivo   := .T.
    Local aLista   := {}
    Local dData    := dDataBase
    Local xRetorno := Nil
Return
```

---

## BP-02 - Escopo de Variaveis

**Severidade**: CRITICAL

**Descricao**: Variaveis devem ser declaradas como `Local` por padrao. O uso de `Private` deve ser reservado EXCLUSIVAMENTE para variaveis de interface do framework Protheus que exigem escopo Private.

**Variaveis que DEVEM ser Private**:
- `aHeader` - Cabecalho de GetDados/EnchoiceBar
- `aCols` - Colunas de GetDados/EnchoiceBar
- `aRotina` - Array de rotinas do MBrowse/FWMBrowse
- `aCpoEnchoice` - Campos do Enchoice
- `lMsErroAuto` - Flag de erro do MsExecAuto
- `lMsHelpAuto` - Flag de help do MsExecAuto
- `nOpcx` - Opcao selecionada no AxCadastro
- `cCadastro` - Titulo do cadastro

**ERRADO**:
```advpl
User Function MinhaFunc()
    Private cNome   := ""
    Private nValor  := 0
    Private dData   := dDataBase
    Private lStatus := .T.

    // logica de negocio
    cNome := "Cliente Teste"
    nValor := CalcValor()
Return
```

**CORRETO**:
```advpl
User Function MinhaFunc()
    Local cNome   := ""
    Local nValor  := 0
    Local dData   := dDataBase
    Local lStatus := .T.

    // logica de negocio
    cNome := "Cliente Teste"
    nValor := CalcValor()
Return
```

**CORRETO - Uso legitimo de Private**:
```advpl
User Function CadCli()
    Private aRotina   := {}
    Private cCadastro := "Cadastro de Clientes"

    aRotina := MenuDef()
    FWMBrowse():New():Activate()
Return
```

---

## BP-03 - Protheus.doc

**Severidade**: WARNING

**Descricao**: Toda User Function deve ser documentada com o padrao Protheus.doc, incluindo tipo, autor, data de criacao, versao, parametros e retorno.

**ERRADO**:
```advpl
// Funcao que calcula desconto
User Function CalcDesc(nVlrBrt, nPercDs)
    Local nVlrDesc := 0
    nVlrDesc := nVlrBrt * (nPercDs / 100)
Return nVlrDesc
```

**CORRETO**:
```advpl
/*/{Protheus.doc} CalcDesc
Calcula o valor do desconto sobre o valor bruto informado,
aplicando o percentual de desconto parametrizado.

@type Function
@author Joao Silva
@since 15/01/2025
@version 1.0

@param nVlrBrt, Numeric, Valor bruto base para calculo
@param nPercDs, Numeric, Percentual de desconto a aplicar (0-100)

@return Numeric, Valor do desconto calculado

@example
    Local nDesc := U_CalcDesc(1000.00, 10) // Retorna 100.00

@see U_AplDesc
/*/
User Function CalcDesc(nVlrBrt, nPercDs)
    Local nVlrDesc := 0
    nVlrDesc := nVlrBrt * (nPercDs / 100)
Return nVlrDesc
```

---

## BP-04 - GetArea/RestArea

**Severidade**: CRITICAL

**Descricao**: Sempre que o codigo manipular posicionamento de tabelas, deve-se salvar a area atual e restaura-la ao final. Prefira `FWGetArea`/`FWRestArea` ao inves de `GetArea`/`RestArea` pois a versao FW eh mais performatica.

**ERRADO**:
```advpl
User Function BuscaCli(cCodCli)
    Local cNomeCli := ""

    DbSelectArea("SA1")
    DbSetOrder(1)
    If DbSeek(xFilial("SA1") + cCodCli)
        cNomeCli := SA1->A1_NOME
    EndIf
Return cNomeCli
```

**CORRETO**:
```advpl
User Function BuscaCli(cCodCli)
    Local cNomeCli := ""
    Local aAreaSA1 := {}

    aAreaSA1 := SA1->(FWGetArea())

    DbSelectArea("SA1")
    DbSetOrder(1)
    If DbSeek(xFilial("SA1") + cCodCli)
        cNomeCli := SA1->A1_NOME
    EndIf

    FWRestArea(aAreaSA1)
Return cNomeCli
```

---

## BP-05 - Gerenciamento de Alias

**Severidade**: WARNING

**Descricao**: Utilize `GetNextAlias()` para gerar alias dinamicos e unicos. Nunca hardcode alias de queries. Sempre feche o alias apos o uso com `DbCloseArea()`.

**ERRADO**:
```advpl
User Function ConsVend()
    Local cQuery := ""

    cQuery := "SELECT A3_COD, A3_NOME FROM " + RetSqlName("SA3")
    cQuery += " WHERE D_E_L_E_T_ = ' '"

    TCQuery cQuery New Alias "QRY"

    While !QRY->(Eof())
        ConOut(QRY->A3_NOME)
        QRY->(DbSkip())
    EndDo

    QRY->(DbCloseArea())
Return
```

**CORRETO**:
```advpl
User Function ConsVend()
    Local cQuery  := ""
    Local cAlias  := GetNextAlias()

    cQuery := "SELECT A3_COD, A3_NOME FROM " + RetSqlName("SA3")
    cQuery += " WHERE D_E_L_E_T_ = ' '"
    cQuery += " AND " + RetSqlName("SA3") + ".xFilial('SA3')"

    MpSysOpenQuery(cQuery, cAlias)

    While !(cAlias)->(Eof())
        ConOut((cAlias)->A3_NOME)
        (cAlias)->(DbSkip())
    EndDo

    (cAlias)->(DbCloseArea())
Return
```

---

## BP-06 - Tratamento de Erros

**Severidade**: CRITICAL

**Descricao**: Use `Begin Sequence` para envolver lógicas de negócio críticas. O uso do bloco `Recover` e a captura via `ErrorBlock` são **altamente sugeridos** quando houver necessidade de tratamento específico da falha ou log detalhado, mas não são obrigatórios caso o objetivo seja apenas a interrupção segura do fluxo via `Break`. Verifique sempre o retorno de `RecLock` antes de gravar dados.

**ERRADO**:
```advpl
User Function GravaCli(cCod, cNome)
    DbSelectArea("SA1")
    RecLock("SA1", .T.)
    SA1->A1_COD  := cCod
    SA1->A1_NOME := cNome
    MsUnLock()
Return .T.
```

**CORRETO (Com Recover - Sugerido para Log/Tratamento)**:
```advpl
User Function GravaCli(cCod, cNome)
    Local lRet      := .T.
    Local oError    := Nil
    Local bErrorBlk := {|e| oError := e, Break(e)}

    Begin Sequence With bErrorBlk
        DbSelectArea("SA1")
        If RecLock("SA1", .T.)
            SA1->A1_COD  := cCod
            SA1->A1_NOME := cNome
            MsUnLock()
        Else
            lRet := .F.
        EndIf
    Recover Using oError
        lRet := .F.
        ConOut("BP-06: Erro ao gravar SA1 - " + oError:Description)
    End Sequence
Return lRet
```

**CORRETO (Simples - Sem Recover)**:
```advpl
User Function GravaCli(cCod, cNome)
    Local lRet := .T.

    Begin Sequence
        DbSelectArea("SA1")
        If !RecLock("SA1", .T.)
            Break // Interrompe o fluxo sem necessidade de Recover
        EndIf
        
        SA1->A1_COD  := cCod
        SA1->A1_NOME := cNome
        MsUnLock()
    End Sequence
Return lRet
```

---

## BP-07 - Limpeza de Recursos

**Severidade**: CRITICAL

**Descricao**: Todo recurso alocado deve ser liberado ao final da execucao: objetos com `FreeObj()`, locks com `UnLockByName()`, ambiente RPC com `RpcClearEnv()`, alias com `DbCloseArea()`, areas com `FWRestArea()`. Use bloco `Finally` ou garanta a limpeza apos `End Sequence`.

**ERRADO**:
```advpl
User Function ProcJob()
    Local oObj := Nil

    RpcSetType(3)
    RpcSetEnv("01", "01")
    LockByName("MYJOB", .T.)

    oObj := MyClass():New()
    oObj:Execute()

    // Se ocorrer erro acima, recursos ficam alocados
Return
```

**CORRETO**:
```advpl
User Function ProcJob()
    Local oObj      := Nil
    Local oError    := Nil
    Local bErrorBlk := {|e| oError := e, Break(e)}

    RpcSetType(3)
    RpcSetEnv("01", "01")

    If !LockByName("MYJOB", .T.)
        ConOut("BP-07: Job MYJOB ja em execucao")
        RpcClearEnv()
        Return
    EndIf

    Begin Sequence With bErrorBlk

        oObj := MyClass():New()
        oObj:Execute()

    Recover Using oError
        ConOut("BP-07: Erro no job - " + oError:Description)
    End Sequence

    If oObj <> Nil
        FreeObj(oObj)
    EndIf

    UnLockByName("MYJOB")
    RpcClearEnv()
Return
```

---

## BP-08 - Somente ASCII

**Severidade**: WARNING

**Descricao**: Nao use caracteres acentuados em nomes de variaveis, funcoes, comentarios de codigo ou mensagens de log. Para mensagens exibidas ao usuario que precisam de acentuacao, use `FwNoAccent()` ou armazene em parametros SX6.

**ERRADO**:
```advpl
User Function CalculaComissao()
    // Calcula a comissao do funcionario
    Local nComissao := 0
    Local cMensagem := "Operacao realizada com sucesso"

    ConOut("Funcao de calculo de comissao iniciada")
Return nComissao
```

**CORRETO**:
```advpl
User Function CalcComis()
    // Calcula a comissao do funcionario
    Local nComissao := 0
    Local cMensagem := "Operacao realizada com sucesso"

    ConOut("Funcao de calculo de comissao iniciada")
Return nComissao
```

**Nota**: Em comentarios e strings literais destinadas a log, evite acentos. Para textos exibidos ao usuario final via interface, utilize dicionario de dados (SX6/SX1) ou funcoes de traducao.

---

## BP-09 - Includes Obrigatorios

**Severidade**: WARNING

**Descricao**: Todo fonte deve incluir os headers adequados ao tipo de codigo. A ausencia de includes gera comportamentos inesperados e erros de compilacao.

**Tabela de Includes**:

| Include          | Quando Usar                                    |
|------------------|------------------------------------------------|
| Protheus.ch      | SEMPRE - todo fonte ADVPL                       |
| FWMVCDef.ch      | Fontes que usam MVC (ModelDef/ViewDef)          |
| Topconn.ch       | Fontes que usam acesso SQL direto               |
| RESTFUL.ch       | Fontes REST em ADVPL classico                   |
| tlpp-core.th     | Fontes TLPP (substitui Protheus.ch)             |
| tlpp-rest.th     | Endpoints REST em TLPP                          |
| FWBrowse.ch      | Fontes que usam FWMBrowse                       |

**ERRADO**:
```advpl
User Function MvcCli()
    Local oModel := FWFormModel():New()
    // Erro: sem FWMVCDef.ch as constantes MVC nao existem
Return
```

**CORRETO**:
```advpl
#Include "Protheus.ch"
#Include "FWMVCDef.ch"

User Function MvcCli()
    Local oModel := FWFormModel():New()
    // Constantes MVC disponiveis
Return
```

---

## BP-10 - Tamanho de Funcao

**Severidade**: INFO

**Descricao**: Funcoes nao devem exceder aproximadamente 200 linhas. Decomponha logica complexa em `Static Function` para manter a legibilidade e facilitar manutencao e testes.

**ERRADO**:
```advpl
User Function ProcBig()
    // 300+ linhas de logica misturada:
    // - validacao de entrada
    // - consulta ao banco
    // - calculo de valores
    // - gravacao de dados
    // - envio de email
    // - geracao de log
    // Tudo em uma unica funcao
Return
```

**CORRETO**:
```advpl
#Include "Protheus.ch"

/*/{Protheus.doc} ProcBig
Processo principal que orquestra as etapas de processamento.
@type Function
@author Joao Silva
@since 10/01/2025
@version 1.0
/*/
User Function ProcBig()
    Local lRet    := .T.
    Local aData   := {}
    Local nResult := 0

    // Passo 1 - Validar entrada
    lRet := ValidaEntrada()
    If !lRet
        Return .F.
    EndIf

    // Passo 2 - Consultar dados
    aData := ConsultaDados()
    If Len(aData) == 0
        Return .F.
    EndIf

    // Passo 3 - Processar calculos
    nResult := ProcessaCalc(aData)

    // Passo 4 - Gravar resultados
    lRet := GravaResult(nResult)

    // Passo 5 - Notificar
    If lRet
        Notifica(nResult)
    EndIf
Return lRet

Static Function ValidaEntrada()
    Local lOk := .T.
    // Validacoes especificas (max 50 linhas)
Return lOk

Static Function ConsultaDados()
    Local aResult := {}
    // Consulta ao banco (max 50 linhas)
Return aResult

Static Function ProcessaCalc(aData)
    Local nTotal := 0
    // Calculos de negocio (max 50 linhas)
Return nTotal

Static Function GravaResult(nValor)
    Local lGravou := .T.
    // Gravacao em banco (max 50 linhas)
Return lGravou

Static Function Notifica(nValor)
    // Envio de notificacao (max 30 linhas)
Return
```