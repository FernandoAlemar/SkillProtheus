# Regras de Modernizacao - ADVPL/TLPP

## MOD-01 - BeginSQL para MpSysOpenQuery

**Esforco**: LOW

**Descricao**: Substitua `BeginSQL` por `MpSysOpenQuery` com montagem explicita da query. O `BeginSQL` usa macros que dificultam debug e manutencao. Use a tabela de conversao abaixo para migrar as macros.

**Tabela de Conversao de Macros BeginSQL**:

| Macro BeginSQL         | Equivalente Explicito                              |
|------------------------|----------------------------------------------------|
| `%table:XX%`           | `RetSqlName("XX")`                                 |
| `%xfilial:XX%`         | `xFilial("XX")`                                    |
| `%notDel%`             | `"D_E_L_E_T_ = ' '"`                               |
| `%exp:cVariavel%`      | Valor da variavel `cVariavel` diretamente na query  |
| `%Alias.campo%`        | `RetSqlName("Alias") + ".campo"`                    |

**LEGADO**:
```advpl
User Function ConsCli()
    Local cCodCli := "000001"

    BeginSQL Alias "QRY"
        SELECT A1_COD, A1_NOME, A1_CGC
        FROM %table:SA1%
        WHERE %notDel%
        AND A1_FILIAL = %xfilial:SA1%
        AND A1_COD = %exp:cCodCli%
    EndSQL

    While !QRY->(Eof())
        ConOut(QRY->A1_NOME)
        QRY->(DbSkip())
    EndDo

    QRY->(DbCloseArea())
Return
```

**MODERNO**:
```advpl
User Function ConsCli()
    Local cCodCli := "000001"
    Local cQuery  := ""
    Local cAlias  := GetNextAlias()
    Local oStmt   := FwPreparedStatement():New()

    oStmt:SetQuery("SELECT A1_COD, A1_NOME, A1_CGC")
    oStmt:Add(" FROM " + RetSqlName("SA1"))
    oStmt:Add(" WHERE D_E_L_E_T_ = ' '")
    oStmt:Add(" AND A1_FILIAL = '" + xFilial("SA1") + "'")
    oStmt:Add(" AND A1_COD = :codCli")
    oStmt:SetParam("codCli", cCodCli)

    cQuery := oStmt:GetFixQuery()
    MpSysOpenQuery(cQuery, cAlias)

    While !(cAlias)->(Eof())
        ConOut((cAlias)->A1_NOME)
        (cAlias)->(DbSkip())
    EndDo

    (cAlias)->(DbCloseArea())
    FreeObj(oStmt)
Return
```

**Notas de Migracao**: Substitua cada macro pela funcao correspondente na tabela. Use `FwPreparedStatement` para parametros vindos de variaveis externas.

---

## MOD-02 - TCQuery para MpSysOpenQuery

**Esforco**: LOW

**Descricao**: Substitua `TCQuery` por `MpSysOpenQuery`. O `MpSysOpenQuery` eh mais robusto, trata melhor erros de conexao e segue o padrao recomendado pela TOTVS.

**LEGADO**:
```advpl
User Function ListaVend()
    Local cQuery := ""

    cQuery := "SELECT A3_COD, A3_NOME FROM " + RetSqlName("SA3")
    cQuery += " WHERE D_E_L_E_T_ = ' '"
    cQuery += " AND A3_FILIAL = '" + xFilial("SA3") + "'"

    TCQuery cQuery New Alias "QRY"

    While !QRY->(Eof())
        ConOut(QRY->A3_NOME)
        QRY->(DbSkip())
    EndDo

    QRY->(DbCloseArea())
Return
```

**MODERNO**:
```advpl
User Function ListaVend()
    Local cQuery := ""
    Local cAlias := GetNextAlias()

    cQuery := "SELECT A3_COD, A3_NOME FROM " + RetSqlName("SA3")
    cQuery += " WHERE D_E_L_E_T_ = ' '"
    cQuery += " AND A3_FILIAL = '" + xFilial("SA3") + "'"

    cQuery := ChangeQuery(cQuery)
    MpSysOpenQuery(cQuery, cAlias)

    While !(cAlias)->(Eof())
        ConOut((cAlias)->A3_NOME)
        (cAlias)->(DbSkip())
    EndDo

    (cAlias)->(DbCloseArea())
Return
```

**Notas de Migracao**: Troque `TCQuery cQuery New Alias "NOME"` por `MpSysOpenQuery(cQuery, cAlias)` com alias dinamico via `GetNextAlias()`. Sempre aplique `ChangeQuery()` antes.

---

## MOD-03 - MBrowse para FWMBrowse

**Esforco**: LOW

**Descricao**: Substitua `MBrowse` pela classe `FWMBrowse`. O `FWMBrowse` suporta filtros avancados, legendas, duplo clique e outros recursos modernos.

**LEGADO**:
```advpl
#Include "Protheus.ch"

User Function CadCli()
    Private aRotina   := {}
    Private cCadastro := "Cadastro de Clientes"

    aRotina := {;
        {"Pesquisar" , "AxPesqui"  , 0, 1},;
        {"Visualizar", "AxVisual"  , 0, 2},;
        {"Incluir"   , "AxInclui"  , 0, 3},;
        {"Alterar"   , "AxAltera"  , 0, 4},;
        {"Excluir"   , "AxDeleta"  , 0, 5};
    }

    DbSelectArea("SA1")
    DbSetOrder(1)

    MBrowse(6, 1, 22, 75, "SA1")
Return
```

**MODERNO**:
```advpl
#Include "Protheus.ch"
#Include "FWBrowse.ch"

User Function CadCli()
    Local oBrowse := Nil
    Private aRotina   := {}
    Private cCadastro := "Cadastro de Clientes"

    aRotina := MenuDef()

    DbSelectArea("SA1")
    DbSetOrder(1)

    oBrowse := FWMBrowse():New()
    oBrowse:SetAlias("SA1")
    oBrowse:SetDescription(cCadastro)
    oBrowse:AddLegend("A1_MSBLQL == '1'", "RED"   , "Cliente Bloqueado")
    oBrowse:AddLegend("A1_MSBLQL != '1'", "GREEN" , "Cliente Ativo")
    oBrowse:Activate()
Return

Static Function MenuDef()
    Local aMenu := {}
    AAdd(aMenu, {"Pesquisar" , "AxPesqui"  , 0, 1})
    AAdd(aMenu, {"Visualizar", "AxVisual"  , 0, 2})
    AAdd(aMenu, {"Incluir"   , "AxInclui"  , 0, 3})
    AAdd(aMenu, {"Alterar"   , "AxAltera"  , 0, 4})
    AAdd(aMenu, {"Excluir"   , "AxDeleta"  , 0, 5})
Return aMenu
```

**Notas de Migracao**: `FWMBrowse` usa orientacao a objetos. Troque a chamada `MBrowse()` pela instanciacao da classe. Adicione legendas e filtros para melhorar a experiencia do usuario.

---

## MOD-04 - MsGetDados para MsNewGetDados

**Esforco**: MEDIUM

**Descricao**: Substitua `MsGetDados` por `MsNewGetDados`. A versao New suporta mais campos, melhor gerenciamento de memoria e compatibilidade com versoes recentes do Protheus.

**LEGADO**:
```advpl
User Function GridItens()
    Private aHeader  := {}
    Private aCols    := {}
    Private aRotina  := {}

    aHeader := FwGetSX3("SC6", "A", "MVC")
    aCols   := Array(1, Len(aHeader) + 1)
    aCols[1, Len(aHeader) + 1] := .F. // Flag de exclusao

    oGetD := MsGetDados():New(;
        nTop, nLeft, nBottom, nRight,;
        GD_INSERT + GD_UPDATE + GD_DELETE,;
        "AllwaysTrue()", "AllwaysTrue()",;
        "", {"C6_ITEM"})
Return
```

**MODERNO**:
```advpl
User Function GridItens()
    Private aHeader  := {}
    Private aCols    := {}
    Private aRotina  := {}
    Local oGetD      := Nil

    aHeader := FwGetSX3("SC6", "A", "MVC")
    aCols   := Array(1, Len(aHeader) + 1)
    aCols[1, Len(aHeader) + 1] := .F.

    oGetD := MsNewGetDados():New(;
        nTop, nLeft, nBottom, nRight,;
        GD_INSERT + GD_UPDATE + GD_DELETE,;
        "AllwaysTrue()", "AllwaysTrue()",;
        "", {"C6_ITEM"},, 999)
    //                     ^^^ Suporta ate 999 linhas
Return
```

**Notas de Migracao**: A interface eh praticamente identica. O `MsNewGetDados` aceita parametro adicional para limite de linhas e tem melhor performance com grandes volumes de dados.

---

## MOD-05 - Modelo3 para MVC

**Esforco**: HIGH

**Descricao**: Substitua rotinas no padrao Modelo3 (EnchoiceBar + GetDados) pelo framework MVC (FWFormModel + FWFormView). O MVC separa modelo de dados da interface, facilita testes e reuso.

**LEGADO**:
```advpl
#Include "Protheus.ch"

User Function PedVenda(cOpc)
    Private aRotina  := {}
    Private aHeader  := {}
    Private aCols    := {}
    Private aCpoEnchoice := {}

    aHeader := FwGetSX3("SC6", "A", "MVC")
    Modelo3(cOpc, "SC5", "SC6", "C5_NUM", "C6_ITEM")
Return
```

**MODERNO**:
```advpl
#Include "Protheus.ch"
#Include "FWMVCDef.ch"

User Function PedVenda()
    Local oBrowse := FWMBrowse():New()
    oBrowse:SetAlias("SC5")
    oBrowse:SetDescription("Pedidos de Venda")
    oBrowse:Activate()
Return

Static Function MenuDef()
    Local aMenu := {}
    AAdd(aMenu, {"Visualizar", "VIEWDEF.PEDVENDA", 0, 2})
    AAdd(aMenu, {"Incluir"   , "VIEWDEF.PEDVENDA", 0, 3})
    AAdd(aMenu, {"Alterar"   , "VIEWDEF.PEDVENDA", 0, 4})
    AAdd(aMenu, {"Excluir"   , "VIEWDEF.PEDVENDA", 0, 5})
Return aMenu

Static Function ModelDef()
    Local oModel := MPFormModel():New("PEDVMD")

    oModel:AddFields("SC5MASTER",, FWFormStruct(1, "SC5"))
    oModel:AddGrid("SC6DETAIL", "SC5MASTER", FWFormStruct(1, "SC6"))
    oModel:SetRelation("SC6DETAIL", {{"C6_FILIAL", "xFilial('SC6')"}, {"C6_NUM", "C5_NUM"}}, SC6->(IndexKey(1)))

    oModel:GetModel("SC5MASTER"):SetDescription("Cabecalho do Pedido")
    oModel:GetModel("SC6DETAIL"):SetDescription("Itens do Pedido")
    oModel:SetPrimaryKey({"C5_FILIAL", "C5_NUM"})
Return oModel

Static Function ViewDef()
    Local oView  := FWFormView():New()
    Local oModel := FWLoadModel("PEDVENDA")
    Local oStCab := FWFormStruct(2, "SC5")
    Local oStItm := FWFormStruct(2, "SC6")

    oView:SetModel(oModel)
    oView:AddField("VIEW_SC5", oStCab, "SC5MASTER")
    oView:AddGrid("VIEW_SC6", oStItm, "SC6DETAIL")

    oView:CreateHorizontalBox("BOX_CAB", 40)
    oView:CreateHorizontalBox("BOX_ITM", 60)
    oView:SetOwnerView("VIEW_SC5", "BOX_CAB")
    oView:SetOwnerView("VIEW_SC6", "BOX_ITM")
Return oView
```

**Notas de Migracao**: Migracao de Modelo3 para MVC requer reescrita significativa. O MVC exige `ModelDef` (regras de negocio), `ViewDef` (interface) e `MenuDef` (menu) como Static Functions. O beneficio eh separacao de responsabilidades e suporte a REST automatico.

---

## MOD-06 - Procedural para OOP (Classes TLPP)

**Esforco**: MEDIUM

**Descricao**: Substitua codigo procedural com muitas funcoes relacionadas por classes TLPP com namespace. Classes organizam melhor o codigo, encapsulam dados e facilitam testes unitarios.

**LEGADO**:
```advpl
#Include "Protheus.ch"

// Funcoes procedurais espalhadas
User Function CalcImp(nBase, cUF)
    Local nICMS := CalcICMS(nBase, cUF)
    Local nPIS  := CalcPIS(nBase)
    Local nCOF  := CalcCOFINS(nBase)
Return nICMS + nPIS + nCOF

Static Function CalcICMS(nBase, cUF)
    Local nAliq := GetAliqICMS(cUF)
Return nBase * (nAliq / 100)

Static Function CalcPIS(nBase)
Return nBase * 0.0165

Static Function CalcCOFINS(nBase)
Return nBase * 0.076
```

**MODERNO**:
```advpl
#Include "tlpp-core.th"

Namespace custom.fiscal.impostos

Class CalculadoraImpostos

    Data nBase    As Numeric
    Data cUF      As Character
    Data nICMS    As Numeric
    Data nPIS     As Numeric
    Data nCOFINS  As Numeric

    Public Method New(nBase, cUF)
    Public Method Calcular()
    Public Method GetTotal()
    Private Method CalcICMS()
    Private Method CalcPIS()
    Private Method CalcCOFINS()

EndClass

Method New(nBase, cUF) Class CalculadoraImpostos
    ::nBase   := nBase
    ::cUF     := cUF
    ::nICMS   := 0
    ::nPIS    := 0
    ::nCOFINS := 0
Return Self

Method Calcular() Class CalculadoraImpostos
    ::CalcICMS()
    ::CalcPIS()
    ::CalcCOFINS()
Return

Method GetTotal() Class CalculadoraImpostos
Return ::nICMS + ::nPIS + ::nCOFINS

Method CalcICMS() Class CalculadoraImpostos
    Local nAliq := GetAliqICMS(::cUF)
    ::nICMS := ::nBase * (nAliq / 100)
Return

Method CalcPIS() Class CalculadoraImpostos
    ::nPIS := ::nBase * 0.0165
Return

Method CalcCOFINS() Class CalculadoraImpostos
    ::nCOFINS := ::nBase * 0.076
Return
```

**Notas de Migracao**: Agrupe funcoes relacionadas em classes. Use `Data` para estado compartilhado entre metodos. Use `Private Method` para logica interna. Sempre defina um namespace.

---

## MOD-07 - SetPrint para TReport

**Esforco**: MEDIUM

**Descricao**: Substitua relatorios baseados em `SetPrint`/`SetDefault`/`@...SAY` pelo framework `TReport`. O TReport gera PDF, oferece preview, filtros parametrizaveis e layout profissional.

**LEGADO**:
```advpl
#Include "Protheus.ch"

User Function RelCli()
    Local oPrint := Nil

    oPrint := SetPrint(,, .T., @cArq)
    SetDefault(aOrd, oPrint)

    oPrint:Say(nLin, 001, "Codigo")
    oPrint:Say(nLin, 040, "Nome")
    oPrint:Say(nLin, 120, "CNPJ")

    DbSelectArea("SA1")
    DbGoTop()
    While !Eof()
        nLin += 15
        oPrint:Say(nLin, 001, SA1->A1_COD)
        oPrint:Say(nLin, 040, SA1->A1_NOME)
        oPrint:Say(nLin, 120, SA1->A1_CGC)
        DbSkip()
    EndDo

    oPrint:Preview()
Return
```

**MODERNO**:
```advpl
#Include "Protheus.ch"

User Function RelCli()
    Local oReport  := Nil
    Local oSection := Nil

    oReport := TReport():New("RelCli", "Relatorio de Clientes",, {|oReport| PrintReport(oReport)})
    oReport:SetLandScape(.T.)

    oSection := TRSection():New(oReport, "Clientes",{"SA1"})
    TRCell():New(oSection, "A1_COD"  , "SA1", "Codigo" , "", 15)
    TRCell():New(oSection, "A1_NOME" , "SA1", "Nome"   , "", 40)
    TRCell():New(oSection, "A1_CGC"  , "SA1", "CNPJ"   , "", 20)
    TRCell():New(oSection, "A1_MUN"  , "SA1", "Cidade" , "", 25)

    oReport:PrintDialog()
Return

Static Function PrintReport(oReport)
    Local oSection := oReport:Section(1)

    DbSelectArea("SA1")
    DbSetOrder(1)
    DbGoTop()

    oSection:Init()

    While !Eof()
        oSection:Cell("A1_COD"):SetValue(SA1->A1_COD)
        oSection:Cell("A1_NOME"):SetValue(SA1->A1_NOME)
        oSection:Cell("A1_CGC"):SetValue(SA1->A1_CGC)
        oSection:Cell("A1_MUN"):SetValue(SA1->A1_MUN)
        oSection:PrintLine()

        DbSkip()
    EndDo

    oSection:Finish()
Return
```

**Notas de Migracao**: TReport exige definir sections e cells declarativamente. O metodo de impressao eh passado como code block. O framework cuida de paginacao, quebras e formatacao.

---

## MOD-08 - DbUseArea para MpSysOpenQuery

**Esforco**: LOW

**Descricao**: Substitua `DbUseArea` com `TCSetField` por `MpSysOpenQuery`. O `DbUseArea` abre a tabela inteira; queries SQL permitem filtrar e selecionar apenas os dados necessarios.

**LEGADO**:
```advpl
User Function ConsEst()
    Local cTabela := RetSqlName("SB2")

    DbUseArea(.T.,, cTabela, "TMP", .T., .T.)
    TCSetField("TMP", "B2_QATU", "N", 14, 2)
    TCSetField("TMP", "B2_QFIM", "N", 14, 2)

    DbSelectArea("TMP")
    DbGoTop()

    While !TMP->(Eof())
        ConOut(TMP->B2_COD + " Qtd: " + cValToChar(TMP->B2_QATU))
        TMP->(DbSkip())
    EndDo

    TMP->(DbCloseArea())
Return
```

**MODERNO**:
```advpl
User Function ConsEst()
    Local cQuery := ""
    Local cAlias := GetNextAlias()

    cQuery := "SELECT B2_COD, B2_LOCAL, B2_QATU, B2_QFIM "
    cQuery += " FROM " + RetSqlName("SB2")
    cQuery += " WHERE D_E_L_E_T_ = ' '"
    cQuery += " AND B2_FILIAL = '" + xFilial("SB2") + "'"
    cQuery += " AND B2_QATU > 0"

    cQuery := ChangeQuery(cQuery)
    MpSysOpenQuery(cQuery, cAlias)

    While !(cAlias)->(Eof())
        ConOut((cAlias)->B2_COD + " Qtd: " + cValToChar((cAlias)->B2_QATU))
        (cAlias)->(DbSkip())
    EndDo

    (cAlias)->(DbCloseArea())
Return
```

**Notas de Migracao**: `DbUseArea` carrega todos os registros da tabela. `MpSysOpenQuery` com WHERE filtra no banco, reduzindo trafego de rede e consumo de memoria.

---

## MOD-09 - Excesso de Private para Local

**Esforco**: LOW

**Descricao**: Substitua variaveis `Private` por `Local` sempre que nao forem exigidas pelo framework. Variaveis Private poluem o escopo, dificultam debug e podem causar efeitos colaterais em funcoes chamadas.

**LEGADO**:
```advpl
User Function ProcessaLote()
    Private cFilial  := xFilial("SA1")
    Private nTotal   := 0
    Private cStatus  := "P"
    Private dDataIni := dDataBase
    Private dDataFim := dDataBase + 30
    Private aResult  := {}

    ExecutaProcesso()
    GeraRelatorio()
Return
```

**MODERNO**:
```advpl
User Function ProcessaLote()
    Local cFilial  := xFilial("SA1")
    Local nTotal   := 0
    Local cStatus  := "P"
    Local dDataIni := dDataBase
    Local dDataFim := dDataBase + 30
    Local aResult  := {}

    ExecutaProcesso(cFilial, cStatus, dDataIni, dDataFim, @aResult, @nTotal)
    GeraRelatorio(aResult, nTotal)
Return
```

**Notas de Migracao**: Troque `Private` por `Local` e passe os valores como parametros para as funcoes que precisam. Use passagem por referencia (`@`) quando a funcao precisar alterar o valor.

---

## MOD-10 - Sem Namespace para Namespace Organizado

**Esforco**: LOW

**Descricao**: Todo codigo TLPP deve definir um namespace no padrao `custom.projeto.modulo.tipo`. Namespaces evitam colisao de nomes entre diferentes projetos e modulos do Protheus.

**Padrao de Namespace**: `custom.<projeto>.<modulo>.<tipo>`

Exemplos:
- `custom.vendas.pedidos.services`
- `custom.financeiro.contas.models`
- `custom.fiscal.nfe.rest`
- `custom.rh.folha.jobs`

**LEGADO**:
```advpl
#Include "Protheus.ch"

// Sem namespace - risco de colisao com outras funcoes
User Function CalcFrete()
    // ...
Return

User Function ValFrete()
    // ...
Return

User Function GrvFrete()
    // ...
Return
```

**MODERNO**:
```advpl
#Include "tlpp-core.th"

Namespace custom.logistica.frete.services

Class FreteService

    Data nPeso     As Numeric
    Data cUFOrig   As Character
    Data cUFDest   As Character
    Data nValFrete As Numeric

    Public Method New(nPeso, cUFOrig, cUFDest)
    Public Method Calcular()
    Public Method Validar()
    Public Method Gravar()

EndClass

Method New(nPeso, cUFOrig, cUFDest) Class FreteService
    ::nPeso     := nPeso
    ::cUFOrig   := cUFOrig
    ::cUFDest   := cUFDest
    ::nValFrete := 0
Return Self

Method Calcular() Class FreteService
    // Logica de calculo de frete
    ::nValFrete := ::nPeso * GetTaxaFrete(::cUFOrig, ::cUFDest)
Return ::nValFrete

Method Validar() Class FreteService
    Local lOk := .T.
    If ::nPeso <= 0
        lOk := .F.
        ConOut("MOD-10: Peso invalido para calculo de frete")
    EndIf
Return lOk

Method Gravar() Class FreteService
    // Logica de gravacao
Return .T.
```

**Notas de Migracao**: Adicione `#Include "tlpp-core.th"` e defina o `Namespace` no topo do fonte. Agrupe funcoes relacionadas em classes dentro do namespace. O padrao `custom.*` evita conflito com namespaces internos da TOTVS.