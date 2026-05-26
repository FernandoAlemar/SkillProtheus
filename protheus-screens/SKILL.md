---
name: protheus-screens
description: >
  Templates de telas e browses ADVPL/TLPP para Protheus.
  Use esta skill SEMPRE que o usuario pedir para criar telas, dialogs,
  formularios, browses com checkbox (FWMarkBrowse), grids editaveis
  (MsNewGetDados), browses customizados, telas com ParamBox,
  EnchoiceBar, TDialog, MSDIALOG, TCBrowse, ou qualquer componente
  visual de tela no Protheus que NAO seja MVC puro. Inclui templates
  para dialog simples, grid editavel, FWMarkBrowse com selecao,
  master-detail, e TCBrowse com array.
  Para exemplos completos, consulte [references/browse-examples.md](references/browse-examples.md).
---


---

## 1. TEMPLATES DE TELAS

### 1.1 Dialog Simples (Formulario de entrada)

**Quando usar:** Tela modal com campos de input e botoes Confirmar/Cancelar.

```advpl
#Include 'Protheus.ch'

User Function <<FUNCNAME>>()
    Local oDlg, oGroup1
    Local oSay1, oGet1, cGet1 := Space(<<TAM>>)
    Local oSay2, oGet2, cGet2 := Space(<<TAM>>)
    Local oBtn1, oBtn2
    Local lOk := .F.

    DEFINE MSDIALOG oDlg TITLE "<<TITULO>>" FROM 000, 000 TO <<ALTURA>>, <<LARGURA>> ;
        COLORS 0, 16777215 PIXEL

    // Grupo visual
    @ 005, 005 GROUP oGroup1 TO <<GRPALT>>, <<GRPLARG>> PROMPT "<<GRUPO>>" OF oDlg PIXEL

    // Labels + campos
    @ 015, 010 SAY oSay1 PROMPT "<<LABEL1>>:" SIZE 060, 010 OF oDlg PIXEL
    @ 030, 010 MSGET oGet1 VAR cGet1 SIZE 100, 010 OF oDlg <<F3>> PIXEL
    @ 045, 010 SAY oSay2 PROMPT "<<LABEL2>>:" SIZE 060, 010 OF oDlg PIXEL
    @ 060, 010 MSGET oGet2 VAR cGet2 SIZE 100, 010 OF oDlg PIXEL

    // Botoes
    @ <<BTNLIN>>, <<BTNCOL1>> BUTTON oBtn1 PROMPT "Cancelar" SIZE 037, 012 OF oDlg ;
        ACTION (oDlg:End()) PIXEL
    @ <<BTNLIN>>, <<BTNCOL2>> BUTTON oBtn2 PROMPT "Confirmar" SIZE 037, 012 OF oDlg ;
        ACTION (fConfirma(@lOk, oDlg, cGet1, cGet2)) PIXEL

    ACTIVATE MSDIALOG oDlg CENTERED
Return lOk

Static Function fConfirma(lOk, oDlg, cGet1, cGet2)
    If Empty(cGet1)
        MsgAlert("Campo obrigatorio!")
        Return
    EndIf

    // <<LOGICA_GRAVACAO>>
    lOk := .T.
    oDlg:End()
Return
```

**Variacoes:**
- Adicionar `F3 "<<ALIAS>>"` ao MSGET para consulta padrao
- Usar `READONLY` para campos somente leitura
- Usar `DEFINE FONT oFont NAME "Arial" SIZE 0, -16` se precisar fonte custom

---

### 1.2 Dialog com Grid Editavel (MsNewGetDados)

**Quando usar:** Tela com planilha editavel (cabecalho + itens ou lista editavel).

```advpl
#Include 'Protheus.ch'

User Function <<FUNCNAME>>()
    Local oDlg, oMsGet
    Local lOk     := .F.
    Local bOk     := {|| lOk := .T., oDlg:End()}
    Local bCancel := {|| lOk := .F., oDlg:End()}
    Private aHeader := {}
    Private aCols   := {}

    fMontaHeader()
    fMontaCols()

    DEFINE MSDIALOG oDlg TITLE "<<TITULO>>" FROM 000, 000 TO 400, 600 ;
        COLORS 0, 16777215 PIXEL

    oMsGet := MsNewGetDados():New( ;
        020, 005, 180, 295, ;               // nTop, nLeft, nBottom, nRight
        GD_INSERT+GD_DELETE+GD_UPDATE, ;    // nStyle (flags de operacao)
        "AllwaysTrue", ;                     // cLinOk (validacao por linha)
        "AllwaysTrue", ;                     // cAllOk (validacao geral)
        "", ;                                // cIniCpos
        {}, ;                                // aAlterFields (vazio = todos editaveis)
        , ;                                  // nFreeze
        999, ;                               // nMax linhas
        "AllwaysTrue", ;                     // cFieldOk
        "", ;                                // cSuperDel
        "AllwaysTrue", ;                     // cDelOk
        oDlg, ;                              // oWnd
        aHeader, ;                           // aHeader
        aCols ;                              // aCols
    )

    ACTIVATE MSDIALOG oDlg ON INIT EnchoiceBar(oDlg, bOk, bCancel) CENTERED

    If lOk
        Processa({|| fGravar()}, "<<TITULO>>", "Gravando...")
    EndIf
Return

Static Function fMontaHeader()
    Local aCampos := { "<<CAMPO1>>", "<<CAMPO2>>", "<<CAMPO3>>" }
    Local nX

    aHeader := {}
    DbSelectArea("SX3")
    SX3->(DbSetOrder(2))
    For nX := 1 To Len(aCampos)
        If SX3->(DbSeek(aCampos[nX]))
            aAdd(aHeader, { ;
                Trim(X3_TITULO), ;    // [1] Titulo
                X3_CAMPO, ;           // [2] Campo
                X3_PICTURE, ;         // [3] Picture
                X3_TAMANHO, ;         // [4] Tamanho
                X3_DECIMAL, ;         // [5] Decimal
                X3_VLDUSER, ;         // [6] Validacao
                X3_USADO, ;           // [7] Usado
                X3_TIPO, ;            // [8] Tipo
                X3_ARQUIVO, ;         // [9] Arquivo
                X3_CONTEXT ;          // [10] Contexto (R=Real, V=Virtual)
            })
        EndIf
    Next nX
Return

Static Function fMontaCols()
    Local nX
    aCols := {}

    // <<QUERY OU NAVEGACAO NA TABELA>>
    While !Eof()
        aAdd(aCols, Array(Len(aHeader) + 1))
        For nX := 1 To Len(aHeader)
            aCols[Len(aCols)][nX] := FieldGet(FieldPos(aHeader[nX][2]))
        Next nX
        aCols[Len(aCols)][Len(aHeader) + 1] := .F.   // Flag exclusao (obrigatorio)
        DbSkip()
    EndDo
Return

Static Function fGravar()
    Local nI, nCpo, nPosCpo
    For nI := 1 To Len(aCols)
        If !aCols[nI, Len(aHeader) + 1]    // Nao excluido
            // <<LOGICA DE GRAVACAO>>
        EndIf
    Next nI
Return
```

**Flags do nStyle:**
- `GD_INSERT` - permite incluir linhas
- `GD_DELETE` - permite excluir linhas
- `GD_UPDATE` - permite alterar linhas
- Combine com `+` : `GD_INSERT+GD_DELETE+GD_UPDATE`

---

### 1.3 Dialog com EnchoiceBar (Padrao Confirmar/Cancelar)

**Quando usar:** Qualquer dialog que precise de barra padrao Ok/Cancelar.

```advpl
#Include 'Protheus.ch'

User Function <<FUNCNAME>>()
    Local oDlg
    Local lOk     := .F.
    Local bOk     := {|| lOk := fValida(), If(lOk, oDlg:End(), Nil)}
    Local bCancel := {|| lOk := .F., oDlg:End()}

    DEFINE MSDIALOG oDlg TITLE "<<TITULO>>" FROM 000, 000 TO <<ALT>>, <<LARG>> ;
        COLORS 0, 16777215 PIXEL

    // <<COMPONENTES>>

    ACTIVATE MSDIALOG oDlg ON INIT EnchoiceBar(oDlg, bOk, bCancel) CENTERED

    If lOk
        // <<PROCESSAR>>
    EndIf
Return
```

---

### 1.4 Dialog Dinamico (tamanho proporcional a tela)

**Quando usar:** Telas que devem se adaptar a resolucao do usuario.

```advpl
Local aTamanho := MsAdvSize()
Local nJanLarg := aTamanho[5]
Local nJanAltu := aTamanho[6]

oDlg := TDialog():New(0, 0, nJanAltu, nJanLarg, "<<TITULO>>", , , , , , , , , .T.)

oPanel := tPanel():New(030, 001, '', oDlg, , , , ;
    RGB(0,0,0), RGB(254,254,254), (nJanLarg/2)-1, (nJanAltu/2)-1)

// <<COMPONENTES DENTRO DO PANEL>>

oDlg:Activate(,,,.T.)
```

---

## 2. TEMPLATES DE BROWSES

### 2.1 FWMBrowse + MVC Completo (CRUD padrao)

**Quando usar:** Cadastro CRUD de tabela customizada (ZXX).

```advpl
#Include 'Protheus.ch'
#Include 'FWMVCDef.ch'

User Function <<FUNCNAME>>()
    Local oBrowse := FWMBrowse():New()
    oBrowse:SetAlias("<<ALIAS>>")
    oBrowse:SetDescription("<<TITULO>>")
    oBrowse:SetMenuDef('<<FUNCNAME>>')
    // Legendas (opcional)
    // oBrowse:AddLegend("<<COND1>>", "GREEN", "<<DESC_VERDE>>")
    // oBrowse:AddLegend("<<COND2>>", "RED", "<<DESC_VERMELHO>>")
    oBrowse:Activate()
Return

Static Function MenuDef()
    Local aRot := {}
    ADD OPTION aRot TITLE 'Visualizar' ACTION 'VIEWDEF.<<FUNCNAME>>' OPERATION MODEL_OPERATION_VIEW   ACCESS 0
    ADD OPTION aRot TITLE 'Incluir'    ACTION 'VIEWDEF.<<FUNCNAME>>' OPERATION MODEL_OPERATION_INSERT  ACCESS 0
    ADD OPTION aRot TITLE 'Alterar'    ACTION 'VIEWDEF.<<FUNCNAME>>' OPERATION MODEL_OPERATION_UPDATE  ACCESS 0
    ADD OPTION aRot TITLE 'Excluir'    ACTION 'VIEWDEF.<<FUNCNAME>>' OPERATION MODEL_OPERATION_DELETE  ACCESS 0
Return aRot

Static Function ModelDef()
    Local oModel
    Local oStPai := FWFormStruct(1, '<<ALIAS>>')

    oModel := MPFormModel():New('<<FUNCNAME>>M')
    oModel:AddFields('<<ALIAS>>MASTER', /*cOwner*/, oStPai)
    oModel:SetDescription("<<TITULO>>")
    oModel:SetPrimaryKey({'<<ALIAS>>_FILIAL', '<<ALIAS>>_CODIGO'})
Return oModel

Static Function ViewDef()
    Local oView
    Local oModel := FWLoadModel('<<FUNCNAME>>')
    Local oStPai := FWFormStruct(2, '<<ALIAS>>')

    oView := FWFormView():New()
    oView:SetModel(oModel)
    oView:AddField('VIEW_<<ALIAS>>', oStPai, '<<ALIAS>>MASTER')
    oView:CreateHorizontalBox('TELA', 100)
    oView:SetOwnerView('VIEW_<<ALIAS>>', 'TELA')
Return oView
```

**Variacao - FwLoadBrw (mais enxuto, mesma funcionalidade):**
```advpl
User Function <<FUNCNAME>>()
    Local oBrowse := FwLoadBrw("<<FUNCNAME>>")
    oBrowse:Activate()
Return

Static Function BrowseDef()
    Local oBrowse := FwMBrowse():New()
    oBrowse:SetAlias("<<ALIAS>>")
    oBrowse:SetDescription("<<TITULO>>")
    oBrowse:SetMenuDef("<<FUNCNAME>>")
Return (oBrowse)
```

---

### 2.2 FWMarkBrowse (Selecao com checkbox)

**Quando usar:** Tela onde o usuario marca registros e depois processa em lote.

```advpl
#Include 'Protheus.ch'

User Function <<FUNCNAME>>()
    Local aPergs := {}
    Private aParamMain := {}

    // 1. Parametros (opcional)
    aAdd(aPergs, {1, "Data De",  Date()-30, "@D", "", "", "", 50, .F.})
    aAdd(aPergs, {1, "Data Ate", Date(),    "@D", "", "", "", 50, .F.})

    If ParamBox(aPergs, 'Parametros', @aParamMain,,,,,,, .F., .F.)
        fTelaMark()
    EndIf
Return

Static Function fTelaMark()
    Local aTamanho   := MsAdvSize()
    Local nJanLarg   := aTamanho[5]
    Local nJanAltu   := aTamanho[6]
    Local oFontGrid  := TFont():New(,,-14)
    Local aCampos    := {}
    Local aColunas   := {}
    Local aSeek      := {}
    Local oDlgMark, oPanGrid, oMarkBrowse, oTempTable
    Local cAliasTmp  := GetNextAlias()

    // 2. Tabela temporaria
    aAdd(aCampos, {'OK',       'C', 2, 0})     // Campo de marcacao (OBRIGATORIO)
    aAdd(aCampos, {'<<CAMPO1>>','C', <<TAM1>>, 0})
    aAdd(aCampos, {'<<CAMPO2>>','C', <<TAM2>>, 0})
    // ... demais campos

    oTempTable := FWTemporaryTable():New(cAliasTmp)
    oTempTable:SetFields(aCampos)
    oTempTable:AddIndex("1", {"<<CAMPO1>>"})
    oTempTable:Create()

    // 3. Popular dados
    Processa({|| fPopula(cAliasTmp)}, 'Carregando...')

    // 4. Montar colunas
    aColunas := fCriaColunas(cAliasTmp)

    // 5. Pesquisa (opcional)
    fMontaSeek(@aSeek, "<<CAMPO1>>")

    // 6. Dialog + Panel
    DEFINE MSDIALOG oDlgMark TITLE "<<TITULO>>" FROM 0, 0 TO nJanAltu, nJanLarg PIXEL
    oPanGrid := tPanel():New(001, 001, '', oDlgMark, , , , ;
        RGB(0,0,0), RGB(254,254,254), (nJanLarg/2)-1, (nJanAltu/2)-1)

    // 7. MarkBrowse
    oMarkBrowse := FWMarkBrowse():New()
    oMarkBrowse:SetAlias(cAliasTmp)
    oMarkBrowse:SetDescription("<<TITULO>>")
    oMarkBrowse:SetFieldMark('OK')
    oMarkBrowse:SetTemporary(.T.)
    oMarkBrowse:SetColumns(aColunas)
    oMarkBrowse:SetFontBrowse(oFontGrid)
    oMarkBrowse:oBrowse:SetDBFFilter(.T.)
    oMarkBrowse:oBrowse:SetUseFilter(.T.)
    oMarkBrowse:oBrowse:SetSeek(.T., aSeek)
    // Legendas (opcional)
    // oMarkBrowse:AddLegend("<<COND1>>", "GREEN", "<<DESC1>>")
    // oMarkBrowse:AddLegend("<<COND2>>", "RED", "<<DESC2>>")
    // Botoes extras (opcional)
    oMarkBrowse:AddButton('<<ACAO>>', {|| fProcessar(oMarkBrowse, cAliasTmp)},,1,0)
    oMarkBrowse:SetOwner(oPanGrid)
    oMarkBrowse:Activate()

    ACTIVATE MSDIALOG oDlgMark CENTERED

    // 8. Cleanup
    oTempTable:Delete()
    oMarkBrowse:DeActivate()
Return

Static Function fPopula(cAliasTmp)
    Local cQuery := "<<SQL_QUERY>>"
    MPSysOpenQuery(cQuery, 'QRYTMP')
    While QRYTMP->(!Eof())
        RecLock(cAliasTmp, .T.)
        (cAliasTmp)->OK       := Space(2)
        (cAliasTmp)-><<CAMPO1>> := QRYTMP-><<CAMPO1>>
        (cAliasTmp)-><<CAMPO2>> := QRYTMP-><<CAMPO2>>
        (cAliasTmp)->(MsUnlock())
        QRYTMP->(DbSkip())
    EndDo
    QRYTMP->(DbCloseArea())
Return

Static Function fCriaColunas(cAliasTmp)
    Local aColunas := {}
    Local oColumn

    oColumn := FWBrwColumn():New()
    oColumn:SetData(&("{|| " + cAliasTmp + "->" + "<<CAMPO1>>" + "}"))
    oColumn:SetTitle("<<TITULO_COL>>")
    oColumn:SetType("C")
    oColumn:SetSize(<<TAM>>)
    aAdd(aColunas, oColumn)
    // Repetir para cada coluna
Return aColunas

Static Function fMontaSeek(aSeek, cCampo)
    aAdd(aSeek, { ;
        GetSX3Cache(cCampo, "X3_TITULO"), ;
        {{"", ;
            GetSX3Cache(cCampo, "X3_TIPO"), ;
            GetSX3Cache(cCampo, "X3_TAMANHO"), ;
            GetSX3Cache(cCampo, "X3_DECIMAL"), ;
            AllTrim(GetSX3Cache(cCampo, "X3_TITULO")), ;
            AllTrim(GetSX3Cache(cCampo, "X3_PICTURE"))}} ;
    })
Return

Static Function fProcessar(oMarkBrowse, cAliasTmp)
    Local cMarca := oMarkBrowse:Mark()
    Local nTotal := 0

    (cAliasTmp)->(DbGoTop())
    While !(cAliasTmp)->(Eof())
        If oMarkBrowse:IsMark(cMarca)
            nTotal++
            // <<LOGICA DE PROCESSAMENTO>>
        EndIf
        (cAliasTmp)->(DbSkip())
    EndDo

    If nTotal == 0
        MsgAlert("Nenhum registro selecionado!")
    Else
        MsgInfo(cValToChar(nTotal) + " registro(s) processado(s).")
        oMarkBrowse:Refresh(.T.)
    EndIf
Return
```

---

### 2.3 FWMarkBrowse Fullscreen (sem Dialog externo)

**Quando usar:** Browse de marcacao que ocupa a tela inteira.

```advpl
oMarkBrowse := FWMarkBrowse():New()
oMarkBrowse:SetAlias(cAliasTmp)
oMarkBrowse:SetFieldMark('OK')
oMarkBrowse:SetTemporary(.T.)
oMarkBrowse:SetColumns(aColunas)
oMarkBrowse:SetIgnoreARotina(.T.)      // Ignora aRotina global
oMarkBrowse:SetMenuDef("")              // Menu vazio
oMarkBrowse:AddButton("Confirmar", {|| fConfirmar()}, NIL, NIL, 2)
oMarkBrowse:SetValid({|| fValidaFecha()})
oMarkBrowse:Activate()                  // Fullscreen
oMarkBrowse:DeActivate()
```

---

### 2.4 FWMarkBrowse Master-Detail (dois paineis)

**Quando usar:** Selecao com detalhes dinamicos (ex: pedidos + itens).

```advpl
Static Function fTelaMasterDetail()
    Local aTamanho  := MsAdvSize()
    Local nJanLarg  := aTamanho[5]
    Local nJanAltu  := aTamanho[6]
    Local nColMeio  := (nJanLarg/2) / 2
    Local oFontGrid := TFont():New(,,-14)
    Local oDlg, oPanMaster, oPanDetail, oMarkMaster, oMarkDetail
    Local bBlocoOk, bBlocoCan, bBlocoIni

    oDlg := TDialog():New(0, 0, nJanAltu, nJanLarg, "<<TITULO>>", , , , , , , , , .T.)

    // Painel esquerdo (Master)
    oPanMaster := tPanel():New(030, 001, '', oDlg, , , , ;
        RGB(0,0,0), RGB(254,254,254), nColMeio - 1, (nJanAltu/2 - 1))

    oMarkMaster := FWMarkBrowse():New()
    oMarkMaster:SetAlias(cAliasMaster)
    oMarkMaster:SetFieldMark('OK')
    oMarkMaster:SetTemporary(.T.)
    oMarkMaster:SetColumns(aColMaster)
    oMarkMaster:SetFontBrowse(oFontGrid)
    oMarkMaster:oBrowse:bChange := {|| fFiltraDetail()}
    oMarkMaster:AddButton("Processar", {|| fProcessar()})
    oMarkMaster:SetOwner(oPanMaster)
    oMarkMaster:Activate()

    // Painel direito (Detail)
    oPanDetail := tPanel():New(030, nColMeio + 1, '', oDlg, , , , ;
        RGB(0,0,0), RGB(254,254,254), (nJanLarg/2 - 10), (nJanAltu/2 - 1))

    oMarkDetail := FWMarkBrowse():New()
    oMarkDetail:SetAlias(cAliasDetail)
    oMarkDetail:SetTemporary(.T.)
    oMarkDetail:SetColumns(aColDetail)
    oMarkDetail:SetFontBrowse(oFontGrid)
    oMarkDetail:DisableFilter()
    oMarkDetail:DisableSeek()
    oMarkDetail:SetOwner(oPanDetail)
    oMarkDetail:Activate()

    // EnchoiceBar via Activate
    bBlocoOk  := {|| oDlg:End()}
    bBlocoCan := {|| oDlg:End()}
    bBlocoIni := {|| EnchoiceBar(oDlg, bBlocoOk, bBlocoCan)}
    oDlg:Activate(, , , .T., , , bBlocoIni)

    // Cleanup
    oMarkMaster:DeActivate()
    oMarkDetail:DeActivate()
Return

Static Function fFiltraDetail()
    Local cFiltro := cAliasDetail + "->CHAVE == '" + (cAliasMaster)->CHAVE + "'"
    (cAliasDetail)->(DbClearFilter())
    (cAliasDetail)->(DbSetFilter({|| &(cFiltro)}, cFiltro))
    oMarkDetail:Refresh(.T.)
Return
```

---

### 2.5 FWMBrowse dentro de Dialog (Tabela Temporaria)

**Quando usar:** Browse customizado com ParamBox e tabela temporaria.

```advpl
#Include 'Protheus.ch'

User Function <<FUNCNAME>>()
    Local aPergs := {}
    Private aParamBox := {}

    aAdd(aPergs, {1, "Data De",  Date()-30, "@D", "", "", "", 50, .F.})
    aAdd(aPergs, {1, "Data Ate", Date(),    "@D", "", "", "", 50, .F.})

    If ParamBox(aPergs, 'Parametros', @aParamBox,,,,,,, .F., .F.)
        fTelaMain()
    EndIf
Return

Static Function fTelaMain()
    Local aTamanho   := MsAdvSize()
    Local nJanLarg   := aTamanho[5]
    Local nJanAltu   := aTamanho[6]
    Local oFontGrid  := TFont():New(,,-14)
    Local oDlgMain, oGridMain, oFwBrMain
    Local oTmpTable
    Local cTableTmp  := GetNextAlias()
    Local aCampos    := {}
    Local aColunas   := {}

    // Definir campos
    aAdd(aCampos, {'<<CAMPO1>>', '<<TIPO>>', <<TAM>>, <<DEC>>})
    // ... demais

    // Criar temporaria
    oTmpTable := FWTemporaryTable():New(cTableTmp)
    oTmpTable:SetFields(aCampos)
    oTmpTable:AddIndex("1", {"<<CAMPO1>>"})
    oTmpTable:Create()

    // Popular
    Processa({|| fPopula(cTableTmp)}, 'Carregando...')

    // Colunas
    aColunas := fCriaCols(cTableTmp)

    // Dialog
    oDlgMain := TDialog():New(0, 0, nJanAltu, nJanLarg, "<<TITULO>>", , , , , , , , , .T.)
    oGridMain := tPanel():New(030, 001, '', oDlgMain, , , , ;
        RGB(0,0,0), RGB(254,254,254), (nJanLarg/2)-1, (nJanAltu/2)-1)

    // Browse
    oFwBrMain := FWMBrowse():New()
    oFwBrMain:SetAlias(cTableTmp)
    oFwBrMain:SetTemporary(.T.)
    oFwBrMain:SetColumns(aColunas)
    oFwBrMain:SetFontBrowse(oFontGrid)
    oFwBrMain:AddButton("<<ACAO>>", {|| fProcessar(cTableTmp)})
    oFwBrMain:SetOwner(oGridMain)
    oFwBrMain:Activate()

    oDlgMain:Activate(,,,.T.)

    // Cleanup
    oTmpTable:Delete()
    oFwBrMain:DeActivate()
Return
```

---

### 2.6 TCBrowse (Array em memoria)

**Quando usar:** Browse simples com dados em array (poucos registros, telas auxiliares).

```advpl
Static Function fTelaTCBrowse(aDados)
    Local oDlg, oBrowse
    Local lRet    := .F.
    Local nSelIdx := 0

    DEFINE DIALOG oDlg TITLE "<<TITULO>>" FROM 180, 180 TO 550, 700 PIXEL

    oBrowse := TCBrowse():New(01, 01, 260, 156, , ;
        {'<<COL1>>', '<<COL2>>'}, ;     // Titulos das colunas
        {50, 50}, ;                      // Larguras
        oDlg, , , , , {||}, , , , , , , .F., , .T., , .F., , , )

    oBrowse:SetArray(aDados)

    oBrowse:AddColumn(TCColumn():New('<<COL1>>', ;
        {|| aDados[oBrowse:nAt, 1]}, , , , "LEFT", , .F., .T., , , , .F., ))
    oBrowse:AddColumn(TCColumn():New('<<COL2>>', ;
        {|| aDados[oBrowse:nAt, 2]}, , , , "LEFT", , .F., .T., , , , .F., ))

    // Duplo clique para selecionar
    oBrowse:bLDblClick := {|| nSelIdx := oBrowse:nAt, lRet := .T., oDlg:End()}

    // Botoes
    TButton():New(160, 002, "Confirmar", oDlg, ;
        {|| nSelIdx := oBrowse:nAt, lRet := .T., oDlg:End()}, 60, 15, , , .T.)
    TButton():New(160, 072, "Cancelar", oDlg, ;
        {|| lRet := .F., oDlg:End()}, 60, 15, , , .T.)

    ACTIVATE DIALOG oDlg CENTERED
Return IIf(lRet, nSelIdx, 0)
```

---

## 3. REGRAS DO TIME

### 3.1 Obrigatorias

| Regra | Descricao |
|-------|-----------|
| **ASCII-only** | Nunca usar acentos em codigo, comentarios, logs ou documentacao |
| **Protheus.doc** | Toda funcao publica (User Function) deve ter bloco Protheus.doc |
| **Variaveis tipadas** | Sempre declarar `Local`/`Private`/`Static` com tipo implicito no nome (c=char, n=num, l=logico, a=array, o=objeto, b=block, d=data) |
| **Private apenas quando obrigatorio** | `aHeader`, `aCols`, `aCpoEnchoice` devem ser Private. Demais variaveis devem ser Local |
| **Cleanup de areas** | Usar `FWGetArea(aArea)` no inicio e `FWRestArea(aArea)` no final de toda funcao que navega em tabelas |
| **Cleanup de temporarias** | Sempre chamar `oTmpTable:Delete()` e `oBrowse:DeActivate()` apos fechar dialog |
| **Begin/End Transaction** | Gravacoes em multiplas tabelas devem estar dentro de `Begin Transaction`...`End Transaction` |
| **RecLock/MsUnlock** | Sempre usar `RecLock(cAlias, .T.)` para incluir, `RecLock(cAlias, .F.)` para alterar. Sempre fechar com `MsUnlock()` |

### 3.2 Padronizacao

| Item | Padrao |
|------|--------|
| **Dialog** | Usar `DEFINE MSDIALOG` (nao TDialog) para dialogs simples |
| **Dialog dinamico** | Usar `TDialog():New()` + `MsAdvSize()` para telas com browse |
| **Browse padrao** | `FWMBrowse` + MVC (nunca MBrowse legado) |
| **Browse marcacao** | `FWMarkBrowse` + `FWTemporaryTable` |
| **Grid editavel** | `MsNewGetDados` (nunca MsGetDados legado) |
| **Barra Ok/Cancel** | `EnchoiceBar(oDlg, bOk, bCancel)` no ON INIT ou Activate |
| **Campo de marca** | Sempre chamar `OK` (C, 2) |
| **Cores** | `COLORS 0, 16777215` para dialog. `RGB(0,0,0), RGB(254,254,254)` para paineis |
| **Fonte do grid** | `TFont():New(,,-14)` |
| **Tamanho** | MsAdvSize() para telas com browse. Fixo (`FROM x,y TO w,h PIXEL`) para dialogs simples |
| **Coordenadas** | Sempre usar PIXEL (nunca coordenadas em caracteres) |
| **Validacao** | `"AllwaysTrue"` (string) para sem validacao. Funcao real para com validacao |

### 3.3 Legendas de cores padrao

| Cor | Constante | Quando usar |
|-----|-----------|-------------|
| Verde | `"GREEN"` | Disponivel, OK, Pendente de processamento |
| Vermelho | `"RED"` | Erro, Bloqueado, Ja processado |
| Amarelo | `"YELLOW"` | Alerta, Erro parcial |
| Azul | `"BLUE"` | Informativo, Processado com sucesso |

---

## 4. ANTI-PATTERNS

### 4.1 NUNCA faca

```advpl
// ERRADO: MBrowse legado
Private aRotina := {...}
MBrowse(6, 1, 22, 75, "ZZG")
// CORRETO: FWMBrowse
oBrowse := FWMBrowse():New()
oBrowse:SetAlias("ZZG")
oBrowse:Activate()

// ERRADO: MsGetDados (legado)
oGet := MSGETDADOS():New(...)
// CORRETO: MsNewGetDados (moderno)
oGet := MsNewGetDados():New(...)

// ERRADO: Coordenadas em caracteres (sem PIXEL)
DEFINE MSDIALOG oDlg FROM 7, 10 TO 30, 60
// CORRETO: Sempre usar PIXEL
DEFINE MSDIALOG oDlg FROM 000, 000 TO 300, 500 PIXEL

// ERRADO: Modelo3 (abandonado)
lRet := Modelo3(cCadastro, cAlias1, cAlias2, ...)
// CORRETO: MVC com FWMBrowse + ModelDef/ViewDef

// ERRADO: Tamanho fixo para browse
oDlg := TDialog():New(0, 0, 600, 800, ...)
// CORRETO: Tamanho dinamico
aTam := MsAdvSize()
oDlg := TDialog():New(0, 0, aTam[6], aTam[5], ...)

// ERRADO: Esquecer cleanup de temporaria
oTmpTable := FWTemporaryTable():New(...)
// ... usa e nunca deleta
// CORRETO: Sempre deletar
oTmpTable:Delete()
oBrowse:DeActivate()

// ERRADO: nomes de variavel inconsistentes
Local oDlgFil, oDlgMain, oFis, oDlgOrcCh
// CORRETO: nomes padronizados
Local oDlg           // dialog principal
Local oDlgMark       // dialog de markbrowse
Local oMarkBrowse    // markbrowse principal

// ERRADO: acentos no codigo
MsgAlert("Operacao nao encontrada!")   // OK
MsgAlert("Opera��o n�o encontrada!")    // ERRADO

// ERRADO: Private desnecessario
Private cQuery := "SELECT ..."
// CORRETO: Local sempre que possivel
Local cQuery := "SELECT ..."
```

### 4.2 Cuidados especiais

```advpl
// CUIDADO: EnchoiceBar DENTRO do bOk (loop infinito)
// ERRADO:
bOk := {|| EnchoiceBar(...)}
// CORRETO:
ACTIVATE MSDIALOG oDlg ON INIT EnchoiceBar(oDlg, bOk, bCancel)

// CUIDADO: Nao esquecer o campo flag no aCols
// ERRADO:
aAdd(aCols, {val1, val2, val3})           // Falta flag exclusao
// CORRETO:
aAdd(aCols, {val1, val2, val3, .F.})      // Ultimo = .F. (nao excluido)

// CUIDADO: FWMarkBrowse sem SetFieldMark
// ERRADO:
oMark := FWMarkBrowse():New()
oMark:SetAlias(cTmp)
oMark:Activate()
// CORRETO:
oMark := FWMarkBrowse():New()
oMark:SetAlias(cTmp)
oMark:SetFieldMark('OK')                  // OBRIGATORIO
oMark:SetTemporary(.T.)
oMark:Activate()

// CUIDADO: Query sem xFilial
// ERRADO:
cQuery := "SELECT * FROM " + RetSQLName("SC5")
// CORRETO:
cQuery := "SELECT * FROM " + RetSQLName("SC5") + " WHERE C5_FILIAL = '" + xFilial("SC5") + "'"

// CUIDADO: FWTemporaryTable sem indices
// ERRADO:
oTmpTable:SetFields(aCampos)
oTmpTable:Create()
// CORRETO:
oTmpTable:SetFields(aCampos)
oTmpTable:AddIndex("1", {"CAMPO_CHAVE"})  // Indice obrigatorio para SetSeek funcionar
oTmpTable:Create()
```

---

## 5. REFERENCIA RAPIDA

### 5.1 Qual template usar?

| Necessidade | Template | Secao |
|-------------|----------|-------|
| Formulario simples (input + confirmar) | Dialog Simples | 1.1 |
| Planilha editavel | Dialog com Grid | 1.2 |
| CRUD de tabela customizada | FWMBrowse + MVC | 2.1 |
| Selecao com checkbox + processamento | FWMarkBrowse | 2.2 |
| Browse fullscreen sem dialog | FWMarkBrowse Fullscreen | 2.3 |
| Master-detail com selecao | FWMarkBrowse Master-Detail | 2.4 |
| Browse customizado com ParamBox | FWMBrowse em Dialog | 2.5 |
| Lista simples em array | TCBrowse | 2.6 |
| Qualquer dialog com Ok/Cancel | EnchoiceBar | 1.3 |
| Tela responsiva a resolucao | Dialog Dinamico | 1.4 |

### 5.2 Metodos FWMarkBrowse

```
// Criacao
:New()                              -> Instancia
:SetAlias(cAlias)                   -> Define alias da tabela
:SetFieldMark(cCampo)               -> Campo C(2) de marcacao [OBRIGATORIO]
:SetTemporary(.T.)                  -> Marca como tabela temporaria
:SetColumns(aColunas)               -> Array de FWBrwColumn
:SetOwner(oPanel)                   -> Panel container
:SetFontBrowse(oFont)               -> Fonte do grid
:SetDescription(cTitulo)            -> Titulo do browse

// oBrowse interno
:oBrowse:SetDBFFilter(.T.)          -> Filtro por DBF (mais rapido)
:oBrowse:SetUseFilter(.T.)          -> Habilita filtros
:oBrowse:SetFixedBrowse(.T.)        -> Browse fixo
:oBrowse:SetSeek(.T., aSeek)        -> Pesquisa por campo
:oBrowse:SetEditCell(.T., bBlock)   -> Edicao inline
:oBrowse:bChange := bBlock          -> Evento ao mudar linha
:oBrowse:lHeaderClick := .T.        -> Permitir clique no cabecalho

// Legendas e botoes
:AddLegend(cCond, cCor, cDesc)      -> Legenda colorida
:AddButton(cTitulo, bAction,,n,n)   -> Botao na toolbar

// Marcacao
:Mark()                              -> Retorna string de marca
:IsMark(cMarca)                      -> .T. se registro marcado
:AllMark()                           -> Marca/desmarca todos

// Controle
:SetValid(bBlock)                   -> Validacao ao fechar
:SetIgnoreARotina(.T.)              -> Ignora aRotina global
:SetMenuDef("")                     -> Menu vazio
:DisableReport()                    -> Desabilita impressao
:DisableFilter()                    -> Desabilita filtro
:DisableSeek()                      -> Desabilita pesquisa

// Ciclo de vida
:Activate()                         -> Ativa o browse
:Refresh(.T.)                       -> Atualiza dados
:GoTop(.T.)                         -> Vai ao primeiro registro
:DeActivate()                       -> Desativa (cleanup)
```

### 5.3 Exemplos de referencia

Veja `references/browse-examples.md` para exemplos completos:
- FWMarkBrowse referencia completa com selecao
- Master-detail com 2 FWMarkBrowse
- FWMBrowse MVC com legendas coloridas
- FWMBrowse em Dialog com TPanel
- TCBrowse canonico com array
- TCBrowse com marcacao bitmap
- FWMarkBrowse fullscreen
- FWMarkBrowse com AllMark customizado