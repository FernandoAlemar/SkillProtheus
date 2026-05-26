---
name: protheus-mvc
description: >
  Padroes MVC do Protheus (FWFormModel/FWFormView) para ADVPL/TLPP.
  Use esta skill SEMPRE que o usuario pedir para criar ou manter rotinas MVC,
  cadastros CRUD, browses FWMBrowse, telas master-detail, monitores,
  ou qualquer rotina que use MPFormModel, FWFormView, FWFormStruct,
  ModelDef, ViewDef, MenuDef, ou FWMBrowse. Inclui templates para
  cadastro simples (Model 1), master-detail (Model 2), multiplos grids
  com abas (Model 3), e monitores/consultas virtuais (Model 4).
---


---

## CONTEXTO CRITICO

MVC no Protheus NAO e MVC web. Aqui:
- **Model** = `MPFormModel` — define campos, grids, relacoes, validacoes e regras de negocio
- **View** = `FWFormView` — define layout visual (boxes, grids, campos) e propriedades de tela
- **MenuDef** = define opcoes do browse (Incluir, Alterar, Excluir, etc.)
- **Browse** = `FWMBrowse` — lista de registros com legendas, filtros e acoes

Classes recomendadas:
- `MPFormModel():New()` — instancia o modelo (977 ocorrencias)
- `FWFormView():New()` — instancia a view (436 ocorrencias)
- `FWFormStruct(1, 'TAB')` — struct de model a partir do dicionario SX3
- `FWFormStruct(2, 'TAB')` — struct de view a partir do dicionario SX3
- `FWFormModelStruct():New()` — struct manual (monitores/consultas virtuais)
- `FWFormViewStruct():New()` — struct de view manual
- `FWMBrowse():New()` — browse MVC

Classes que o time NAO USA:
- ~~FWMVCModel~~ / ~~FWMVCView~~ / ~~FWLoadBrush~~ / ~~FWViewAction~~
- ~~AddPostValidate~~ / ~~AddPreValidate~~ / ~~SetModelAction~~ / ~~SetTrigger~~

---

## ASSINATURA DO MPFormModel():New()

```
MPFormModel():New( cModelId, bPreValidacao, bTudoOK, bCommit, bCancel )
```

| Param | Tipo | Descricao |
|-------|------|-----------|
| cModelId | C | ID unico do modelo (max 10 chars, sem "U_") |
| bPreValidacao | B | Bloco executado ANTES de abrir a tela |
| bTudoOK | B | Bloco executado ao confirmar (validacao final). Recebe `\|oModel\|` |
| bCommit | B | Bloco executado para gravar. Recebe `\|oModel\|`. Se nil, usa FWFormCommit |
| bCancel | B | Bloco executado ao cancelar |

---

## ASSINATURA DO AddField (FWFormModelStruct — struct manual)

Usado em monitores/consultas com campos virtuais. 14 parametros:

```
oStruct:AddField(
    cTitulo      ,;  // [01] Titulo do campo
    cToolTip     ,;  // [02] ToolTip
    cIdField     ,;  // [03] ID do campo (nome unico)
    cTipo        ,;  // [04] Tipo: 'C','N','D','L','M','BT'
    nTamanho     ,;  // [05] Tamanho
    nDecimal     ,;  // [06] Decimais
    bValid       ,;  // [07] Bloco de validacao (FwBuildFeature)
    bWhen        ,;  // [08] Bloco When — controla editabilidade
    aLista       ,;  // [09] Lista de valores (combo)
    lObrigat     ,;  // [10] Obrigatorio (.T./.F.)
    bInic        ,;  // [11] Bloco de inicializacao (FwBuildFeature)
    lChave       ,;  // [12] Campo chave (.T./.F.)
    lUpdate      ,;  // [13] Permite update (.T./.F.)
    lVirtual     )   // [14] Campo virtual (.T./.F.)
```

## ASSINATURA DO AddField (FWFormViewStruct — struct manual view)

16 parametros:

```
oStruct:AddField(
    cIdField     ,;  // [01] ID do campo
    cOrdem       ,;  // [02] Ordem (StrZero(n,2))
    cTitulo      ,;  // [03] Titulo
    cDescricao   ,;  // [04] Descricao
    cHelp        ,;  // [05] Help
    cTipoCampo   ,;  // [06] Tipo visual: 'GET','COMBO','CHECK','BT'
    cPicture     ,;  // [07] Picture
    cPictVar     ,;  // [08] PictVar
    cF3          ,;  // [09] Consulta F3 (alias)
    lEditavel    ,;  // [10] Editavel (.T./.F.)
    cFolder      ,;  // [11] Folder (pasta)
    cGroup       ,;  // [12] Grupo
    aListaCombo  ,;  // [13] Opcoes do combo
    nTamMaxCombo ,;  // [14] Tamanho maximo combo
    cInicBrowse  ,;  // [15] Inicializador browse
    lVirtual     )   // [16] Virtual (.T./.F.)
```

---

## INCLUDES OBRIGATORIOS

```prw
#Include 'Protheus.ch'
#Include 'FWMVCDef.ch'
```

Opcionais (monitores com paineis):
```prw
#Include 'FWEditPanel.ch'
#Include 'Topconn.ch'     // Para TCQuery
```

---

## TEMPLATE 1 — MODEL 1 (Cadastro Simples)

```prw
#Include 'Protheus.ch'
#Include 'FWMVCDef.ch'

Static cTitulo := "Cadastro de Exemplo"

//-------------------------------------------------------------------
// Funcao principal — instancia e ativa o Browse
//-------------------------------------------------------------------
User Function MEUEXM1()
    Local aArea   := GetArea()
    Local oBrowse := FWMBrowse():New()

    oBrowse:SetAlias("ZZZ")
    oBrowse:SetDescription(cTitulo)
    oBrowse:SetMenuDef('MEUEXM1')
    oBrowse:AddLegend("ZZZ_STATUS == '1'", "GREEN", "Ativo")
    oBrowse:AddLegend("ZZZ_STATUS == '2'", "RED",   "Inativo")
    oBrowse:Activate()

    RestArea(aArea)
Return Nil

//-------------------------------------------------------------------
// MenuDef — opcoes do browse
//-------------------------------------------------------------------
Static Function MenuDef()
    Local aRot := {}

    ADD OPTION aRot TITLE 'Visualizar' ACTION 'VIEWDEF.MEUEXM1' OPERATION MODEL_OPERATION_VIEW   ACCESS 0
    ADD OPTION aRot TITLE 'Incluir'    ACTION 'VIEWDEF.MEUEXM1' OPERATION MODEL_OPERATION_INSERT ACCESS 0
    ADD OPTION aRot TITLE 'Alterar'    ACTION 'VIEWDEF.MEUEXM1' OPERATION MODEL_OPERATION_UPDATE ACCESS 0
    ADD OPTION aRot TITLE 'Excluir'    ACTION 'VIEWDEF.MEUEXM1' OPERATION MODEL_OPERATION_DELETE ACCESS 0

Return aRot

//-------------------------------------------------------------------
// ModelDef — modelo de dados
//-------------------------------------------------------------------
Static Function ModelDef()
    Local oStruct := FWFormStruct(1, 'ZZZ')
    Local oModel  := MPFormModel():New('MEUEXM1M', /*bPre*/, /*bTudoOK*/, /*bCommit*/)

    oModel:AddFields('ZZZMASTER', NIL, oStruct)
    oModel:SetPrimaryKey({'ZZZ_FILIAL', 'ZZZ_CODIGO'})
    oModel:SetDescription(cTitulo)
    oModel:GetModel('ZZZMASTER'):SetDescription('Dados do Cadastro')

Return oModel

//-------------------------------------------------------------------
// ViewDef — interface visual
//-------------------------------------------------------------------
Static Function ViewDef()
    Local oModel  := FWLoadModel('MEUEXM1')
    Local oStruct := FWFormStruct(2, 'ZZZ')
    Local oView   := FWFormView():New()

    oView:SetModel(oModel)
    oView:AddField('VIEW_ZZZ', oStruct, 'ZZZMASTER')
    oView:CreateHorizontalBox('TELA', 100)
    oView:SetOwnerView('VIEW_ZZZ', 'TELA')

Return oView
```

### Quando usar Model 1:
- Cadastros simples de uma unica tabela
- Tabelas de apoio (De/Para, Parametros, Config)
- Exemplos: cadastro de usuarios portal, parametros SX5, tabela de/para

---

## TEMPLATE 2 — MODEL 2 (Master-Detail)

```prw
#Include 'Protheus.ch'
#Include 'FWMVCDef.ch'

Static cTitulo := "Pedido com Itens"

//-------------------------------------------------------------------
// Funcao principal
//-------------------------------------------------------------------
User Function MEUEXM2()
    Local aArea   := GetArea()
    Local oBrowse := FWMBrowse():New()

    oBrowse:SetAlias("ZCA")
    oBrowse:SetDescription(cTitulo)
    oBrowse:SetMenuDef('MEUEXM2')
    oBrowse:AddLegend("ZCA_STATUS == '1'", "GREEN",  "Aberto")
    oBrowse:AddLegend("ZCA_STATUS == '2'", "YELLOW", "Parcial")
    oBrowse:AddLegend("ZCA_STATUS == '3'", "RED",    "Fechado")
    oBrowse:Activate()

    RestArea(aArea)
Return Nil

//-------------------------------------------------------------------
// MenuDef
//-------------------------------------------------------------------
Static Function MenuDef()
    Local aRot := {}

    ADD OPTION aRot TITLE 'Visualizar' ACTION 'VIEWDEF.MEUEXM2' OPERATION MODEL_OPERATION_VIEW   ACCESS 0
    ADD OPTION aRot TITLE 'Incluir'    ACTION 'VIEWDEF.MEUEXM2' OPERATION MODEL_OPERATION_INSERT ACCESS 0
    ADD OPTION aRot TITLE 'Alterar'    ACTION 'VIEWDEF.MEUEXM2' OPERATION MODEL_OPERATION_UPDATE ACCESS 0
    ADD OPTION aRot TITLE 'Excluir'    ACTION 'VIEWDEF.MEUEXM2' OPERATION MODEL_OPERATION_DELETE ACCESS 0

Return aRot

//-------------------------------------------------------------------
// ModelDef — cabecalho + itens
//-------------------------------------------------------------------
Static Function ModelDef()
    Local oStCab  := FWFormStruct(1, 'ZCA')
    Local oStIte  := FWFormStruct(1, 'ZCB')
    Local oModel  := MPFormModel():New('MEUEXM2M', /*bPre*/, {|oModel| fTudoOK(oModel)})
    Local aAux    := {}

    // Trigger: produto -> descricao
    aAux := FwStruTrigger('ZCB_PRODUT', 'ZCB_DESC', 'SB1->B1_DESC', .T., 'SB1', 1, ;
                           'xFilial("SB1")+M->ZCB_PRODUT')
    oStIte:AddTrigger(aAux[1], aAux[2], aAux[3], aAux[4])

    // Validacao de campo no detalhe
    oStIte:SetProperty('ZCB_PRODUT', MODEL_FIELD_VALID, ;
        FwBuildFeature(STRUCT_FEATURE_VALID, 'ExistCpo("SB1", M->ZCB_PRODUT, 1)'))

    // Montar modelo
    oModel:AddFields('ZCAMASTER', /*cOwner*/, oStCab)
    oModel:AddGrid('ZCBDETAIL', 'ZCAMASTER', oStIte, /*bLinePre*/, /*bLinePost*/)

    // Relacionamento master-detail
    oModel:SetRelation('ZCBDETAIL', ;
        { {'ZCB_FILIAL', 'xFilial("ZCB")'}, {'ZCB_CODCAB', 'ZCA_CODIGO'} }, ;
        ZCB->(IndexKey(1)))

    // Configuracoes
    oModel:SetPrimaryKey({'ZCA_FILIAL', 'ZCA_CODIGO'})
    oModel:SetDescription(cTitulo)
    oModel:GetModel('ZCAMASTER'):SetDescription('Cabecalho')
    oModel:GetModel('ZCBDETAIL'):SetDescription('Itens')
    oModel:GetModel('ZCBDETAIL'):SetUniqueLine({'ZCB_ITEM'})

Return oModel

//-------------------------------------------------------------------
// ViewDef — cabecalho 30% + grid 70%
//-------------------------------------------------------------------
Static Function ViewDef()
    Local oModel  := FWLoadModel('MEUEXM2')
    Local oStCab  := FWFormStruct(2, 'ZCA')
    Local oStIte  := FWFormStruct(2, 'ZCB')
    Local oView   := FWFormView():New()

    oView:SetModel(oModel)

    oView:AddField('VIEW_ZCA', oStCab, 'ZCAMASTER')
    oView:AddGrid('VIEW_ZCB', oStIte, 'ZCBDETAIL')

    oView:CreateHorizontalBox('CABEC', 30)
    oView:CreateHorizontalBox('GRID', 70)

    oView:SetOwnerView('VIEW_ZCA', 'CABEC')
    oView:SetOwnerView('VIEW_ZCB', 'GRID')

    oView:EnableTitleView('VIEW_ZCA', 'Cabecalho')
    oView:EnableTitleView('VIEW_ZCB', 'Itens')

    oView:AddIncrementField('VIEW_ZCB', 'ZCB_ITEM')

    oView:SetCloseOnOk({||.T.})
    oView:SetViewProperty("VIEW_ZCB", "ENABLENEWGRID")
    oView:SetViewProperty("VIEW_ZCB", "GRIDFILTER", {.T.})
    oView:SetViewProperty("VIEW_ZCB", "GRIDSEEK", {.T.})

Return oView

//-------------------------------------------------------------------
// Validacao final (bTudoOK)
//-------------------------------------------------------------------
Static Function fTudoOK(oModel)
    Local lRet     := .T.
    Local oMaster  := oModel:GetModel('ZCAMASTER')
    Local oDetail  := oModel:GetModel('ZCBDETAIL')

    // Exemplo: validar se tem ao menos 1 item
    If oDetail:Length() < 1 .Or. Empty(oDetail:GetValue('ZCB_PRODUT'))
        Help(,, 'Sem Itens',, 'Informe ao menos um item.', 1, 0)
        lRet := .F.
    EndIf

Return lRet
```

### Quando usar Model 2:
- Documentos com cabecalho + itens (pedidos, notas, requisicoes)
- Relacao 1:N entre duas tabelas
- Exemplos: cadastro produto x necessidade, importacao XML, transferencia entre armazens

---

## TEMPLATE 3 — MODEL 3 (Master + 2 Details com Abas)

```prw
#Include 'Protheus.ch'
#Include 'FWMVCDef.ch'

Static cTitulo := "Regra com Dois Detalhes"

//-------------------------------------------------------------------
// Funcao principal
//-------------------------------------------------------------------
User Function MEUEXM3()
    Local aArea   := GetArea()
    Local oBrowse := FWMBrowse():New()

    oBrowse:SetAlias("ZMA")
    oBrowse:SetDescription(cTitulo)
    oBrowse:SetMenuDef('MEUEXM3')
    oBrowse:Activate()

    RestArea(aArea)
Return Nil

//-------------------------------------------------------------------
// MenuDef
//-------------------------------------------------------------------
Static Function MenuDef()
    Local aRot := {}

    ADD OPTION aRot TITLE 'Visualizar' ACTION 'VIEWDEF.MEUEXM3' OPERATION MODEL_OPERATION_VIEW   ACCESS 0
    ADD OPTION aRot TITLE 'Incluir'    ACTION 'VIEWDEF.MEUEXM3' OPERATION MODEL_OPERATION_INSERT ACCESS 0
    ADD OPTION aRot TITLE 'Alterar'    ACTION 'VIEWDEF.MEUEXM3' OPERATION MODEL_OPERATION_UPDATE ACCESS 0
    ADD OPTION aRot TITLE 'Excluir'    ACTION 'VIEWDEF.MEUEXM3' OPERATION MODEL_OPERATION_DELETE ACCESS 0

Return aRot

//-------------------------------------------------------------------
// ModelDef — master + 2 grids
//-------------------------------------------------------------------
Static Function ModelDef()
    Local oStMaster  := FWFormStruct(1, 'ZMA')
    Local oStDetail1 := FWFormStruct(1, 'ZMB')
    Local oStDetail2 := FWFormStruct(1, 'ZMC')
    Local oModel     := MPFormModel():New('MEUEXM3M', /*bPre*/, {|oModel| fTudoOK(oModel)})
    Local aAux       := {}

    // Trigger no master: cliente -> nome
    aAux := FwStruTrigger('ZMA_CLIENT', 'ZMA_NOME', 'SA1->A1_NOME', .T., ;
                           'SA1', 1, 'xFilial("SA1")+M->ZMA_CLIENT')
    oStMaster:AddTrigger(aAux[1], aAux[2], aAux[3], aAux[4])

    // Trigger no detalhe 1: vendedor -> nome
    aAux := FwStruTrigger('ZMB_VEND', 'ZMB_NOME', 'SA3->A3_NOME', .T., ;
                           'SA3', 1, 'xFilial("SA3")+M->ZMB_VEND')
    oStDetail1:AddTrigger(aAux[1], aAux[2], aAux[3], aAux[4])

    // Montar estrutura
    oModel:AddFields('ZMAMASTER', /*cOwner*/, oStMaster)
    oModel:AddGrid('ZMBDETAIL', 'ZMAMASTER', oStDetail1)
    oModel:AddGrid('ZMCDETAIL', 'ZMAMASTER', oStDetail2)

    // Relacionamentos
    oModel:SetRelation('ZMBDETAIL', ;
        { {'ZMB_FILIAL', 'xFilial("ZMB")'}, {'ZMB_COD', 'ZMA_CODIGO'} }, ;
        ZMB->(IndexKey(1)))
    oModel:SetRelation('ZMCDETAIL', ;
        { {'ZMC_FILIAL', 'xFilial("ZMC")'}, {'ZMC_COD', 'ZMA_CODIGO'} }, ;
        ZMC->(IndexKey(1)))

    // Configuracoes
    oModel:SetPrimaryKey({'ZMA_FILIAL', 'ZMA_CODIGO'})
    oModel:SetDescription(cTitulo)
    oModel:GetModel('ZMAMASTER'):SetDescription('Regra')
    oModel:GetModel('ZMBDETAIL'):SetDescription('Vendedores')
    oModel:GetModel('ZMCDETAIL'):SetDescription('Faixas')

    // Ambos os grids opcionais (podem ficar vazios)
    oModel:GetModel('ZMBDETAIL'):SetOptional(.T.)
    oModel:GetModel('ZMCDETAIL'):SetOptional(.T.)

    // Impedir duplicata
    oModel:GetModel('ZMBDETAIL'):SetUniqueLine({'ZMB_VEND'})

Return oModel

//-------------------------------------------------------------------
// ViewDef — cabecalho 25% + abas 75%
//-------------------------------------------------------------------
Static Function ViewDef()
    Local oModel    := FWLoadModel('MEUEXM3')
    Local oStMaster := FWFormStruct(2, 'ZMA')
    Local oStDet1   := FWFormStruct(2, 'ZMB')
    Local oStDet2   := FWFormStruct(2, 'ZMC')
    Local oView     := FWFormView():New()

    oView:SetModel(oModel)

    oView:AddField('VIEW_ZMA', oStMaster, 'ZMAMASTER')
    oView:AddGrid('VIEW_ZMB', oStDet1, 'ZMBDETAIL')
    oView:AddGrid('VIEW_ZMC', oStDet2, 'ZMCDETAIL')

    // Layout: cabecalho em cima, abas embaixo
    oView:CreateHorizontalBox('CABEC', 25)
    oView:CreateHorizontalBox('GRIDS', 75)

    // Criar abas (Folder + Sheets)
    oView:CreateFolder('PASTA', 'GRIDS')
    oView:AddSheet('PASTA', 'ABA01', 'Vendedores')
    oView:AddSheet('PASTA', 'ABA02', 'Faixas')
    oView:CreateHorizontalBox('BOX_ABA01', 100,,, 'PASTA', 'ABA01')
    oView:CreateHorizontalBox('BOX_ABA02', 100,,, 'PASTA', 'ABA02')

    // Vincular views aos containers
    oView:SetOwnerView('VIEW_ZMA', 'CABEC')
    oView:SetOwnerView('VIEW_ZMB', 'BOX_ABA01')
    oView:SetOwnerView('VIEW_ZMC', 'BOX_ABA02')

    // Titulos
    oView:EnableTitleView('VIEW_ZMA', 'Regra')
    oView:EnableTitleView('VIEW_ZMB', 'Vendedores')
    oView:EnableTitleView('VIEW_ZMC', 'Faixas')

    // Auto-incremento e grid features
    oView:AddIncrementField('VIEW_ZMB', 'ZMB_ITEM')
    oView:SetCloseOnOk({||.T.})
    oView:SetViewProperty("VIEW_ZMB", "ENABLENEWGRID")
    oView:SetViewProperty("VIEW_ZMB", "GRIDFILTER", {.T.})
    oView:SetViewProperty("VIEW_ZMC", "ENABLENEWGRID")

Return oView

//-------------------------------------------------------------------
// Validacao final
//-------------------------------------------------------------------
Static Function fTudoOK(oModel)
    Local lRet := .T.
    // Validacoes globais aqui
Return lRet
```

### Quando usar Model 3:
- Documentos com multiplos tipos de detalhe
- Regras de comissao (vendedor + faixa), marketplace (periodo + CNPJ)
- Exemplos: comissao vendedor x ICMS, repasse marketplace, cadastro com multiplos grids

---

## TEMPLATE 4 — MONITOR / CONSULTA (Virtual, sem CRUD)

```prw
#Include 'Protheus.ch'
#Include 'FWMVCDef.ch'
#Include 'FWEditPanel.ch'
#Include 'Topconn.ch'

//-------------------------------------------------------------------
// Funcao principal — abre direto via FWExecView (sem browse)
//-------------------------------------------------------------------
User Function MEUMON()
    Private aEnableButtons := { ;
        {.F.,Nil},{.F.,Nil},{.F.,Nil},{.F.,Nil},{.F.,Nil}, ;
        {.F.,Nil},{.F.,Nil},{.T.,"Fechar"},{.F.,Nil},{.F.,Nil}, ;
        {.F.,Nil},{.F.,Nil},{.F.,Nil},{.F.,Nil} }

    FWExecView("Monitor", "VIEWDEF.MEUMON", MODEL_OPERATION_INSERT, ;
        /*oDlg*/, {||.T.}, /*bOk*/, /*nPerc*/, aEnableButtons)
Return

//-------------------------------------------------------------------
// ModelDef — modelo virtual (nao grava)
//-------------------------------------------------------------------
Static Function ModelDef()
    Local oModel
    Local oStrCab := GetStrCab(1)
    Local oStrGrd := GetStrGrd(1)

    oModel := MPFormModel():New('MEUMONM')
    oModel:SetDescription('Monitor')
    oModel:AddFields('MASTER', , oStrCab)
    oModel:AddGrid('GRID1', 'MASTER', oStrGrd)

    oModel:SetPrimaryKey({})
    oModel:SetActivate({|oModel| IniDados(oModel)})
    oModel:GetModel('MASTER'):SetOnlyQuery(.T.)
    oModel:GetModel('GRID1'):SetOptional(.T.)
    oModel:GetModel('GRID1'):SetMaxLine(99999)

Return oModel

//-------------------------------------------------------------------
// ViewDef
//-------------------------------------------------------------------
Static Function ViewDef()
    Local oModel  := ModelDef()
    Local oStrCab := GetStrCab(2)
    Local oStrGrd := GetStrGrd(2)
    Local oView   := FWFormView():New()

    oView:SetModel(oModel)
    oView:AddField('FORMCAB', oStrCab, 'MASTER')
    oView:AddGrid('FORMGRD', oStrGrd, 'GRID1')

    oView:CreateHorizontalBox('BOXCAB', 10)
    oView:CreateHorizontalBox('BOXGRD', 90)

    oView:SetOwnerView('FORMCAB', 'BOXCAB')
    oView:SetOwnerView('FORMGRD', 'BOXGRD')

    oView:AddUserButton('Atualizar', '', {|oView| Atualizar()})
    oView:SetViewProperty("FORMGRD", "ENABLENEWGRID")
    oView:SetViewProperty("FORMGRD", "GRIDFILTER", {.T.})
    oView:SetViewProperty("FORMGRD", "GRIDSEEK", {.T.})

Return oView

//-------------------------------------------------------------------
// Struct do cabecalho (filtros)
//-------------------------------------------------------------------
Static Function GetStrCab(nTipo)
    Local oStruct := NIL
    Local aCampos := { ;
        {'Data De', 'Data Inicial', 'DTINI', 'D', 8, 0, , ''}, ;
        {'Data Ate','Data Final',   'DTFIM', 'D', 8, 0, , ''}, ;
        {'Consultar','Consultar',   'LOAD',  'C', 1, 0, , ''} }

    If nTipo == 1
        oStruct := FWFormModelStruct():New()
        oStruct:AddTable('TMP',,'TMP')
        Local nI
        For nI := 1 To Len(aCampos)
            Local bValid := ""
            Local bInic  := ""
            Local bWhen  := Nil
            If aCampos[nI,3] == "LOAD"
                bValid := "U_MonLoad()"
                aCampos[nI,4] := 'BT'
            EndIf
            bValid := FwBuildFeature(1, bValid)
            bInic  := FwBuildFeature(3, bInic)

            oStruct:AddField( ;
                aCampos[nI,1], aCampos[nI,2], aCampos[nI,3], ;
                aCampos[nI,4], aCampos[nI,5], aCampos[nI,6], ;
                bValid, bWhen, NIL, NIL, bInic, NIL, .F., .T.)
        Next nI
    Else
        oStruct := FWFormViewStruct():New()
        Local nI
        For nI := 1 To Len(aCampos)
            Local cTipo := IIF(aCampos[nI,3] == "LOAD", 'BT', 'GET')
            oStruct:AddField( ;
                aCampos[nI,3], StrZero(nI,2), aCampos[nI,1], ;
                aCampos[nI,2], NIL, cTipo, aCampos[nI,7], NIL, ;
                aCampos[nI,8], .T., NIL, NIL, NIL, NIL, NIL, .T.)
        Next nI
    EndIf

Return oStruct

//-------------------------------------------------------------------
// Struct do grid (resultados)
//-------------------------------------------------------------------
Static Function GetStrGrd(nTipo)
    // Mesmo padrao de GetStrCab, mas com campos do grid
    // ... (definir aCampos com os campos de resultado)
Return oStruct

//-------------------------------------------------------------------
// Carga de dados via query
//-------------------------------------------------------------------
Static Function IniDados(oModel)
    If !oModel:IsActive()
        oModel:Activate()
    EndIf
Return

Static Function Atualizar()
    Local oModel     := FWModelActive()
    Local oMaster    := oModel:GetModel("MASTER")
    Local oGrid      := oModel:GetModel("GRID1")
    Local oView      := FWViewActive()
    Local cAlias     := GetNextAlias()
    Local cSql       := ""

    // Limpar grid
    oModel:DeActivate()
    oModel:SetOperation(MODEL_OPERATION_INSERT)
    oModel:Activate()

    // Montar query
    cSql := "SELECT * FROM ... WHERE ..."
    TCQuery cSql NEW ALIAS cAlias

    (cAlias)->(DbGoTop())
    While !(cAlias)->(Eof())
        oGrid:LoadValue('CAMPO1', (cAlias)->CAMPO1)
        oGrid:LoadValue('CAMPO2', (cAlias)->CAMPO2)
        (cAlias)->(DbSkip())
        If !(cAlias)->(Eof())
            oGrid:AddLine()
        EndIf
    EndDo
    (cAlias)->(DbCloseArea())

    oGrid:GoLine(1)
    oGrid:SetNoInsertLine(.T.)
    If oView:lActivate
        oView:Refresh()
    EndIf

Return
```

---

## REGRAS DE VALIDACAO — ONDE COLOCAR CADA TIPO

```
VALIDACAO DE CAMPO (ao sair do campo):
  oStruct:SetProperty('CAMPO', MODEL_FIELD_VALID, {|| MinhaValidacao()})
  oStruct:SetProperty('CAMPO', MODEL_FIELD_VALID, FwBuildFeature(STRUCT_FEATURE_VALID, 'ExistCpo(...)'))

CONTROLE DE EDITABILIDADE (quando o campo pode ser editado):
  oStruct:SetProperty('CAMPO', MODEL_FIELD_WHEN, {|| oModel:GetOperation() == 3})
  oStruct:SetProperty('CAMPO', MODEL_FIELD_WHEN, FwBuildFeature(STRUCT_FEATURE_WHEN, 'INCLUI'))

CAMPO OBRIGATORIO:
  oStruct:SetProperty('CAMPO', MODEL_FIELD_OBRIGAT, .T.)

VALOR INICIAL:
  oStruct:SetProperty('CAMPO', MODEL_FIELD_INIT, FwBuildFeature(STRUCT_FEATURE_INIPAD, 'cValor'))

BLOQUEIO NA VIEW (campo visivel mas nao editavel):
  oStructView:SetProperty('CAMPO', MVC_VIEW_CANCHANGE, .F.)

VALIDACAO DE LINHA DO GRID (bLinePost — ao sair da linha):
  oModel:AddGrid('DETAIL', 'MASTER', oStruct, /*bLinePre*/, {|oMdl| fValidaLinha(oMdl)})

VALIDACAO GLOBAL (bTudoOK — ao confirmar tudo):
  oModel := MPFormModel():New('ID', /*bPre*/, {|oModel| fValidaFinal(oModel)})

COMMIT CUSTOMIZADO (bCommit — grava com logica especial):
  oModel := MPFormModel():New('ID', /*bPre*/, /*bTudoOK*/, {|oModel| fMeuCommit(oModel)})
  // SEMPRE chamar FWFormCommit(oModel) dentro do commit customizado

TRIGGER (preenche campo automaticamente):
  aAux := FwStruTrigger('CAMPO_ORIGEM', 'CAMPO_DESTINO', 'TABELA->CAMPO', .T., 'ALIAS', nOrdem, 'cChave')
  oStruct:AddTrigger(aAux[1], aAux[2], aAux[3], aAux[4])
```

### Hierarquia de execucao:

```
1. MODEL_FIELD_WHEN  — Decide se o campo e editavel
2. MODEL_FIELD_VALID — Valida ao sair do campo
3. AddTrigger        — Dispara preenchimento automatico
4. bLinePre/bLinePost — Valida ao trocar de linha no grid
5. bTudoOK           — Valida ao clicar Confirmar
6. bCommit           — Executa gravacao customizada
```

---

## PADRAO DE BROWSE (FWMBrowse)

### Browse Simples (padrao do time)

```prw
oBrowse := FWMBrowse():New()
oBrowse:SetAlias("TABELA")
oBrowse:SetDescription("Titulo")
oBrowse:SetMenuDef('ROTINA')
oBrowse:Activate()
```

### Browse com Legendas

```prw
// Cores disponiveis: GREEN, RED, YELLOW, ORANGE, PINK, BR_VERMELHO, BLUE
oBrowse:AddLegend("CAMPO == '1'",                  "GREEN",  "Ativo")
oBrowse:AddLegend("CAMPO == '2'",                  "RED",    "Inativo")
oBrowse:AddLegend("CAMPO == '1' .and. DATE() <= CAMPO_DATA", "GREEN", "Valido")
```

### Browse com Filtro Fixo

```prw
oBrowse:SetFilterDefault("TAB->CAMPO = '" + cValor + "'")
```

### Browse com Filtro Dinamico (via SX1)

```prw
If !Pergunte("ROTINA", .T.)
    Return
EndIf
oBrowse:SetFilterDefault(MontaFiltro())
oBrowse:ExecuteFilter(.T.)
```

### Browse com BrowseDef

```prw
User Function ROTINA()
    Local oBrowse := FwLoadBrw("ROTINA")
    oBrowse:Activate()
Return

Static Function BrowseDef()
    Local oBrowse := FwMBrowse():New()
    oBrowse:SetAlias("TAB")
    oBrowse:SetDescription("Titulo")
    oBrowse:SetMenuDef("ROTINA")
    oBrowse:SetUseFilter(.T.)
    oBrowse:SetFixedBrowse(.T.)
Return (oBrowse)
```

### Metodos adicionais do Browse

```prw
oBrowse:SetCacheView(.F.)          // Desabilita cache (dados em tempo real)
oBrowse:SetChgAll(.T.)             // Permite alterar em massa
oBrowse:SetSeeAll(.T.)             // Ver todos os registros
oBrowse:DisableDetails()           // Remove painel de detalhes
oBrowse:SetUseCaseFilter(.T.)      // Filtro case-sensitive
oBrowse:SetFixedBrowse(.T.)        // Browse fixo
```

---

## ANTI-PATTERNS ENCONTRADOS

### 1. Numeros literais no MenuDef (em vez de constantes)

```prw
// ERRADO:
ADD OPTION aRot TITLE 'Visualizar' ACTION 'VIEWDEF.ROTINA' OPERATION 2 ACCESS 0
ADD OPTION aRot TITLE 'Incluir'    ACTION 'VIEWDEF.ROTINA' OPERATION 3 ACCESS 0

// CORRETO:
ADD OPTION aRot TITLE 'Visualizar' ACTION 'VIEWDEF.ROTINA' OPERATION MODEL_OPERATION_VIEW   ACCESS 0
ADD OPTION aRot TITLE 'Incluir'    ACTION 'VIEWDEF.ROTINA' OPERATION MODEL_OPERATION_INSERT ACCESS 0
```

### 2. Chamar ModelDef() direto na ViewDef (instanciacao dupla)

```prw
// ERRADO:
Static Function ViewDef()
    Local oModel := ModelDef()       // Cria segunda instancia!

// CORRETO:
Static Function ViewDef()
    Local oModel := FWLoadModel('ROTINA')   // Reusa instancia registrada
```

**Excecao:** Monitores virtuais podem usar `ModelDef()` direto se nao registram o modelo.

### 3. Misturar OPERATION de acoes custom com MODEL_OPERATION_DELETE

```prw
// ERRADO:
ADD OPTION aRot TITLE 'Relatorio' ACTION 'U_MeuRelat' OPERATION MODEL_OPERATION_DELETE ACCESS 0

// CORRETO (usar operacao neutra — 2 ou MODEL_OPERATION_VIEW):
ADD OPTION aRot TITLE 'Relatorio' ACTION 'U_MeuRelat' OPERATION MODEL_OPERATION_VIEW ACCESS 0
```

### 4. Nao declarar SetPrimaryKey em cadastros CRUD

```prw
// ERRADO:
oModel:SetPrimaryKey({})   // Vazio em cadastro que grava!

// CORRETO:
oModel:SetPrimaryKey({'TAB_FILIAL', 'TAB_CODIGO'})
```

### 5. Nao usar FwBuildFeature para validacoes em string

```prw
// PROBLEMATICO (pode falhar em certas versoes):
oStruct:SetProperty('CAMPO', MODEL_FIELD_VALID, "MinhaFunc()")

// CORRETO:
oStruct:SetProperty('CAMPO', MODEL_FIELD_VALID, ;
    FwBuildFeature(STRUCT_FEATURE_VALID, 'MinhaFunc()'))
```

### 6. Esquecer RestArea / GetArea

```prw
// ERRADO:
User Function ROTINA()
    Local oBrowse := FWMBrowse():New()
    // ... sem salvar/restaurar area

// CORRETO:
User Function ROTINA()
    Local aArea := GetArea()
    Local oBrowse := FWMBrowse():New()
    // ...
    RestArea(aArea)
Return
```

### 7. Commit customizado sem chamar FWFormCommit

```prw
// ERRADO:
Static Function MeuCommit(oModel)
    // Faz coisas...
    // Esquece de gravar!
Return .T.

// CORRETO:
Static Function MeuCommit(oModel)
    // Faz tratamentos antes de gravar
    Local lRet := FWFormCommit(oModel)    // SEMPRE chamar
Return lRet
```

### 8. Nao usar SetOnlyQuery em monitores/consultas

```prw
// ERRADO (monitor que tenta gravar dados temporarios):
oModel:GetModel('MASTER'):SetOptional(.T.)

// CORRETO:
oModel:GetModel('MASTER'):SetOnlyQuery(.T.)   // Marca como somente consulta
```

---

## EXEMPLOS DE REFERENCIA

### Exemplo 1: Cadastro com Commit Customizado (EXEMCAD.prw)

Rotina de usuarios do portal com criptografia SHA256 de senha:

```prw
// ModelDef — registra bTudoOK e bCommit
oModel := MPFormModel():New('EXEMCADM', /*bPre*/,
    {|oModel| validaOK(oModel)},    // Valida e-mail e senha
    {|oMld| MyCommit(oMld)})        // Criptografa antes de gravar

// MyCommit — criptografa senha e gera ID unico
Static Function MyCommit(oModel)
    Local oModelZPO := oModel:GetModel('ZPOMASTER')
    IF ALLTRIM(oModelZPO:GetValue("ZPO_PASSW")) == '*******'
        oModelZPO:SetValue("ZPO_PASSW", cBPKPPSS)        // Mantem senha original
    ELSE
        oModelZPO:SetValue("ZPO_PASSW", SHA256(...))      // Criptografa nova senha
    ENDIF
    lRet := FWFormCommit(oModel)
Return lRet
```

### Exemplo 2: Browse com Filtro Dinamico SX1

```prw
// Pergunta via SX1 antes de abrir o browse
If !Pergunte("ROTINA", .T.)
    Return Nil
Endif
oBrowse:SetFilterDefault(Filtro())    // Funcao que monta WHERE dinamico

Static Function Filtro()
    Local cFiltro := ""
    If MV_PAR01 == 1
        cFiltro += "@ZA9_STATUS='1'"
    EndIf
    If !Empty(MV_PAR02) .And. !Empty(MV_PAR03)
        cFiltro += " AND ZA9_PRODUT >='" + MV_PAR02 + "' AND ZA9_PRODUT <= '" + MV_PAR03 + "'"
    EndIf
Return cFiltro
```

### Exemplo 3: Master com 7 Grids (EXEMPCHL.prw)

Caso avancado — Check List industrial:

```prw
// 7 grids de detalhe, todos filhos do master ZZ1
oModel:addGrid('ZZ2_VIEW', 'ZZ1', oStr2, bPreVld)   // Bicos
oModel:addGrid('ZZ4_VIEW', 'ZZ1', oStr4, bPreVld)   // (detalhes)
oModel:addGrid('ZZ6_VIEW', 'ZZ1', oStr6, bPreVld)   // Controladores Temp
oModel:addGrid('ZZ7_VIEW', 'ZZ1', oStr7, bPreVld)   // Controladores Seq
oModel:addGrid('ZZ8_VIEW', 'ZZ1', oStr8, bPreVld)   // Hot Half
oModel:addGrid('ZZA_VIEW', 'ZZ1', oStr9, bPreVld)   // (detalhes)
oModel:addGrid('ZZC_VIEW', 'ZZ1', oStr11, bPreVld)  // Servico Injecao

// Cada grid tem seu SetRelation individual
oModel:SetRelation('ZZ2_VIEW', {{'ZZ2_FILIAL','XFILIAL("ZZ2")'},{'ZZ2_CODIGO','ZZ1_CODIGO'}}, ...)
// ... (repetir para cada grid)

// Grids com restricoes especificas
oModel:GetModel('ZZ8_VIEW'):SetMaxLine(1)         // Maximo 1 linha
oModel:GetModel('ZZC_VIEW'):SetOptional(.T.)       // Opcional
oModel:GetModel('ZZ6_VIEW'):SetNoInsertLine(.T.)   // Nao permite inserir
```

### Exemplo 4: FWExecView para Abrir MVC Programaticamente

```prw
// Abrir inclusao direto (sem browse)
FWExecView("Incluir", "VIEWDEF.ROTINA", MODEL_OPERATION_INSERT, /*oDlg*/, {||.T.})

// Abrir alteracao direto
FWExecView("Alterar", "VIEWDEF.ROTINA", MODEL_OPERATION_UPDATE, /*oDlg*/, {||.T.})

// Abrir com botoes customizados (somente Fechar habilitado)
aEnableButtons := {{.F.,Nil},{.F.,Nil},{.F.,Nil},{.F.,Nil},{.F.,Nil}, ;
    {.F.,Nil},{.F.,Nil},{.T.,"Fechar"},{.F.,Nil},{.F.,Nil},{.F.,Nil},{.F.,Nil},{.F.,Nil},{.F.,Nil}}
FWExecView("Pesquisar", "VIEWDEF.MONITOR", 3, /*oDlg*/, {||.T.}, /*bOk*/, /*%*/, aEnableButtons)
```

---

## CHECKLIST DE REVISAO MVC

Ao criar ou revisar uma rotina MVC, verificar:

- [ ] Includes: `Protheus.ch` + `FWMVCDef.ch`
- [ ] MenuDef usa constantes `MODEL_OPERATION_*` (nao numeros)
- [ ] MenuDef: ACTION aponta para `'VIEWDEF.<ROTINA>'`
- [ ] ModelDef: cModelId unico, max 10 chars, sem `U_`
- [ ] ModelDef: `SetPrimaryKey` com campos reais (cadastros CRUD)
- [ ] ModelDef: `SetDescription` no modelo e em cada componente
- [ ] ModelDef: `SetRelation` para cada grid de detalhe
- [ ] ModelDef: `SetUniqueLine` para evitar duplicatas no grid
- [ ] ViewDef: carrega modelo via `FWLoadModel('ROTINA')`, nao `ModelDef()`
- [ ] ViewDef: struct via `FWFormStruct(2, 'TAB')` (tipo 2, nao 1)
- [ ] ViewDef: cada componente tem `SetOwnerView` para um box
- [ ] ViewDef: soma dos percentuais dos boxes = 100 por nivel
- [ ] Browse: `SetAlias` + `SetDescription` + `Activate` (minimo)
- [ ] Browse: `AddLegend` com cores coerentes (GREEN=ok, RED=erro)
- [ ] `GetArea()` no inicio e `RestArea(aArea)` no fim da funcao principal
- [ ] Commit customizado chama `FWFormCommit(oModel)` internamente
- [ ] Validacoes de campo usam `FwBuildFeature()` para strings
- [ ] Triggers usam `FwStruTrigger()` + `AddTrigger()`