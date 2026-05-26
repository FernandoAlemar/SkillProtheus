# Exemplos de Browses - Referencia

Trechos de codigo de referencia para browses no Protheus.
Cada exemplo e identificado por padrao utilizado.

---

## 1. FWMarkBrowse Referencia Completa

**Arquivo:** `EXEM05A04.prw`
**Padrao:** FWMarkBrowse + FWTemporaryTable + ParamBox + FWBrwColumn + SetSeek

```advpl
// Parametros iniciais
aAdd(aPergs, {1, "Pedido de",xPar0,"", ".T.", "SC5", ".T.", 80, .F.})
aAdd(aPergs, {1, "Pedido ate",xPar1,"", ".T.", "SC5", ".T.", 80, .F.})
If ParamBox(aPergs,'Pedidos a Deletar',/*aRet*/)

// Tabela temporaria com campo OK para marcacao
aAdd(aCampos, {'OK',       'C', 2, 0})     // Campo de marcacao
aAdd(aCampos, {'C5_NUM',   'C', TamSX3("C5_NUM")[1], 0})
aAdd(aCampos, {'C5_EMISSAO','C', TamSX3("C5_EMISSAO")[1], 0})
aAdd(aCampos, {'C5_CLIENTE','C', TamSX3("C5_CLIENTE")[1], 0})
// ... demais campos

oTempTable := FWTemporaryTable():New(cTempAlias)
oTempTable:SetFields(aCampos)
oTempTable:AddIndex("1",{"C5_NUM"})
oTempTable:Create()

// Popular via query
Processa({|lEnd| ExemCarg(cTempAlias, @lEnd)},'Carregando pedidos')

// Colunas com FWBrwColumn
oColumn := FWBrwColumn():New()
oColumn:SetData(&('{|| '+cTempAlias+'->C5_NUM}'))
oColumn:SetTitle('Numero')
oColumn:SetType('C')
oColumn:SetSize(TamSX3("C5_NUM")[1])
oColumn:SetDecimal(0)
oColumn:SetPicture('')
aAdd(aColunas, oColumn)

// Pesquisa (SetSeek)
cCampoAux := "C5_NUM"
aAdd(aSeek,{GetSX3Cache(cCampoAux,"X3_TITULO"),{{"",
    GetSX3Cache(cCampoAux,"X3_TIPO"),
    GetSX3Cache(cCampoAux,"X3_TAMANHO"),
    GetSX3Cache(cCampoAux,"X3_DECIMAL"),
    AllTrim(GetSX3Cache(cCampoAux,"X3_TITULO")),
    AllTrim(GetSX3Cache(cCampoAux,"X3_PICTURE"))}}})

// Dialog + Panel
DEFINE MSDIALOG oDlgMark TITLE 'Deletar pedidos' FROM 0,0 TO nJanAltu,nJanLarg PIXEL
oPanGrid := tPanel():New(001,001,'',oDlgMark,,,,RGB(0,0,0),RGB(254,254,254),
    (nJanLarg/2)-1,(nJanAltu/2)-1)

// MarkBrowse com todas as configuracoes
oMarkBrowse := FWMarkBrowse():New()
oMarkBrowse:SetAlias(cTempAlias)
oMarkBrowse:SetDescription('Pedidos')
oMarkBrowse:oBrowse:SetDBFFilter(.T.)
oMarkBrowse:oBrowse:SetUseFilter(.T.)
oMarkBrowse:oBrowse:SetFixedBrowse(.T.)
oMarkBrowse:oBrowse:SetSeek(.T.,aSeek)
oMarkBrowse:oBrowse:SetFilterDefault("")
oMarkBrowse:SetFontBrowse(oFontGrid)
oMarkBrowse:SetFieldMark('OK')
oMarkBrowse:SetTemporary(.T.)
oMarkBrowse:SetColumns(aColunas)
oMarkBrowse:SetOwner(oPanGrid)
oMarkBrowse:Activate()

ACTIVATE MsDialog oDlgMark CENTERED

// Cleanup
oTempTable:Delete()
oMarkBrowse:DeActivate()

// Processar marcados
cMarca := oMarkBrowse:Mark()
(cTempAlias)->(DbGoTop())
While !(cTempAlias)->(EoF())
    If oMarkBrowse:IsMark(cMarca)
        // MsExecAuto para deletar pedido
    EndIf
    (cTempAlias)->(DbSkip())
EndDo
```

---

## 2. FWMarkBrowse Master-Detail

**Arquivo:** `ExemploMasterDetail.tlpp`
**Padrao:** 2x FWMarkBrowse + 2x TPanel + bChange + EnchoiceBar

```advpl
// Tamanho dinamico
aTamanho := MsAdvSize()
nJanLarg := aTamanho[5]
nJanAltu := aTamanho[6]
nColMeio := (nJanLarg / 2) / 2

// Dialog principal
oDlgMark := TDialog():New(0, 0, nJanAltu, nJanLarg, cJanTitulo, , , , , , , , , .T.)

// Painel esquerdo (Master - Pedidos)
oPanelEst := tPanel():New(030, 001, '', oDlgMark, , , ,
    RGB(0,0,0), RGB(254,254,254), nColMeio - 1, (nJanAltu/2 - 1))

oMarkEst := FWMarkBrowse():New()
oMarkEst:SetAlias(cAliasEstMun)
oMarkEst:SetDescription("Pedidos")
oMarkEst:SetFieldMark('OK')
oMarkEst:SetTemporary(.T.)
oMarkEst:SetColumns(aColunEstMun)
oMarkEst:SetFontBrowse(oFontGrid)
oMarkEst:AddLegend(cAliasEstMun+"->STATUS == '1'", 'BR_VERDE',    'Pendente')
oMarkEst:AddLegend(cAliasEstMun+"->STATUS == '2'", 'BR_VERMELHO', 'Integrado')
oMarkEst:AddLegend(cAliasEstMun+"->STATUS == '3'", 'BR_AMARELO',  'Erro')
oMarkEst:oBrowse:bChange := {|| fMudaLin()}    // Filtra detail
oMarkEst:AddButton("Replicar", {|| fReplicar()})
oMarkEst:AddButton("Legenda",  {|| fLegenda()})
oMarkEst:SetOwner(oPanelEst)
oMarkEst:Activate()

// Painel direito (Detail - Itens)
oPanelMun := tPanel():New(030, nColMeio + 1, '', oDlgMark, , , ,
    RGB(0,0,0), RGB(254,254,254), (nJanLarg/2 - 10), (nJanAltu/2 - 1))

oMarkMun := FWMarkBrowse():New()
oMarkMun:SetAlias(cAliasMunPed)
oMarkMun:SetDescription("Itens")
oMarkMun:SetTemporary(.T.)
oMarkMun:SetColumns(aColunMunPed)
oMarkMun:SetFontBrowse(oFontGrid)
oMarkMun:DisableFilter()
oMarkMun:DisableSeek()
oMarkMun:SetOwner(oPanelMun)
oMarkMun:Activate()

// EnchoiceBar via bBlocoIni
bBlocoOk  := {|| oDlgMark:End()}
bBlocoCan := {|| oDlgMark:End()}
bBlocoIni := {|| EnchoiceBar(oDlgMark, bBlocoOk, bBlocoCan, , aOutrasAc)}
oDlgMark:Activate(, , , .T., , , bBlocoIni)

// Funcao de filtro master-detail
Static Function fMudaLin()
    cFiltro := cAliasMunPed + "->PEDIDO == '" + (cAliasEstMun)->PEDIDO + "'"
    (cAliasMunPed)->(DbClearFilter())
    (cAliasMunPed)->(DbSetFilter({|| &(cFiltro)}, cFiltro))
    oMarkMun:Refresh(.T.)
Return
```

---

## 3. FWMBrowse MVC com Legendas

**Arquivo:** `EXEMCAD.prw`
**Padrao:** FWMBrowse + ModelDef + ViewDef + AddLegend

```advpl
User Function EXEMCAD()
    Local oBrowse
    Local cTitulo := "Cadastro de Exemplo"

    oBrowse := FWMBrowse():New()
    oBrowse:SetAlias("ZPO")
    oBrowse:AddLegend("ZPO_BLOQ == '1'", "GREEN", "Usuario Ok")
    oBrowse:AddLegend("ZPO_BLOQ == '2'", "RED",   "Bloqueado")
    oBrowse:SetDescription(cTitulo)
    oBrowse:SetMenuDef('EXEMCAD')
    oBrowse:Activate()
Return

Static Function MenuDef()
    Local aRot := {}
    ADD OPTION aRot TITLE 'Visualizar' ACTION 'VIEWDEF.EXEMCAD' OPERATION MODEL_OPERATION_VIEW   ACCESS 0
    ADD OPTION aRot TITLE 'Incluir'    ACTION 'VIEWDEF.EXEMCAD' OPERATION MODEL_OPERATION_INSERT  ACCESS 0
    ADD OPTION aRot TITLE 'Alterar'    ACTION 'VIEWDEF.EXEMCAD' OPERATION MODEL_OPERATION_UPDATE  ACCESS 0
Return aRot

Static Function ModelDef()
    Local oModel
    Local oStPai := FWFormStruct(1,'ZPO')

    oModel := MPFormModel():New('EXEMCADM',,{|oModel| ValidOk(oModel)},{|oMld| MyCommit(oMld)})
    oModel:AddFields('ZPOMASTER',/*cOwner*/,oStPai)
    oModel:SetPrimaryKey({'ZPO_FILIAL','ZPO_USER','ZPO_CGC'})
Return oModel

Static Function ViewDef()
    Local oView
    Local oStr   := FWFormStruct(2,'ZPO')
    Local oModel := FWLoadModel('EXEMCAD')

    oView := FWFormView():New()
    oView:SetModel(oModel)
    oView:AddField('VIEW_ZPO', oStr, 'ZPOMASTER')
    oView:CreateHorizontalBox('CABEC',100)
    oView:SetOwnerView('VIEW_ZPO','CABEC')
Return oView
```

---

## 4. FWMBrowse em Dialog com TPanel

**Arquivo:** `EXEM06A02.tlpp`
**Padrao:** ParamBox + FWTemporaryTable (9 indices) + TDialog + TPanel + FWMBrowse + SetSeek

```advpl
// ParamBox para filtros
aAdd(aPergs, {1, "Filial De", Space(TamSX3("E1_FILIAL")[1]), ...})
aAdd(aPergs, {1, "Filial Ate", StrTran(Space(TamSX3("E1_FILIAL")[1]),' ','Z'), ...})
// ... mais parametros
If !ParamBox(aPergs, "Parametros - Liquidacao", @aParamBox, ...); Return; EndIf

// Tabela temporaria com multiplos indices
oTmpTable := FWTemporaryTable():New(cAliasTmp)
oTmpTable:SetFields(aFields)
oTmpTable:AddIndex("1",{"E1_FILIAL","E1_PREFIXO","E1_NUM","E1_PARCELA","E1_TIPO","E1_FORNECE","E1_LOJA"})
oTmpTable:AddIndex("2",{"E1_FILIAL","E1_VENCTO","E1_FORNECE","E1_LOJA"})
// ... ate indice 9
oTmpTable:Create()

// Colunas construidas uma a uma
oColumn := FWBrwColumn():New()
oColumn:SetData(&("{|| " + cAliasTmp + "->E1_FILIAL}"))
oColumn:SetTitle("Filial")
oColumn:SetType("C")
oColumn:SetSize(TamSX3("E1_FILIAL")[1])
oColumn:SetDecimal(0)
oColumn:SetAutoSize(.T.)
aAdd(aColunas, oColumn)
// ... repetir para cada coluna

// SetSeek com multiplos campos
fMontaSeek(@aSeek, "E1_FILIAL")
fMontaSeek(@aSeek, "E1_PREFIXO")
fMontaSeek(@aSeek, "E1_NUM")

// Dialog dinamico
aTamanho := MsAdvSize()
oDlgMain := TDialog():New(0, 0, aTamanho[6], aTamanho[5], 'Liquidacao', , , , , , , , , .T.)
oGridMain := tPanel():New(030, 001, '', oDlgMain, , , ,
    RGB(0,0,0), RGB(254,254,254), (aTamanho[5]/2)-1, (aTamanho[6]/2)-1)

// Browse com todas configs
oFwMBrMain := FWMBrowse():New()
oFwMBrMain:SetAlias(cAliasTmp)
oFwMBrMain:SetTemporary(.T.)
oFwMBrMain:SetColumns(aColunas)
oFwMBrMain:SetFontBrowse(TFont():New(,,-14))
oFwMBrMain:oBrowse:SetDBFFilter(.T.)
oFwMBrMain:oBrowse:SetUseFilter(.T.)
oFwMBrMain:oBrowse:SetSeek(.T., aSeek)
oFwMBrMain:AddButton("Liquidar", {|| fLiquidar()})
oFwMBrMain:SetOwner(oGridMain)
oFwMBrMain:Activate()

oDlgMain:Activate(,,,.T.)

oTmpTable:Delete()
oFwMBrMain:DeActivate()
```

---

## 5. TCBrowse com SetArray

**Arquivo:** `EXEMREPOS.prw`
**Padrao:** TCBrowse + SetArray + TCColumn + eventos

```advpl
// Montar array de dados
aBrowse := {}
DbSelectArea("SC5")
SC5->(DbSetOrder(1))
SC5->(DbGoTop())
While SC5->(!EoF()) .AND. SC5->C5_PEDREPO = '1'
    aadd(aBrowse, {SC5->C5_NUM, SC5->C5_CLIENTE, SC5->C5_PEDREPO})
    SC5->(DbSkip())
ENDDO

// Dialog e Browse
DEFINE DIALOG oDlg TITLE "Pedido de Reposicao" FROM 180,180 TO 550,700 PIXEL
oBrowse := TCBrowse():New(01,01,260,156,,
    {'Pedido','Cliente','Tipo'},{50,50,50},
    oDlg,,,,,{||},,,,,,,.F.,,.T.,,.F.,,,)

oBrowse:SetArray(aBrowse)

// Colunas
oBrowse:AddColumn(TCColumn():New('Pedido',
    {|| aBrowse[oBrowse:nAt,1]},,,,"LEFT",,.F.,.T.,,,,.F.,))
oBrowse:AddColumn(TCColumn():New('Cliente',
    {|| aBrowse[oBrowse:nAt,2]},,,,"LEFT",,.F.,.T.,,,,.F.,))

// Eventos
oBrowse:bHeaderClick := {|o,x| Alert('Coluna:'+StrZero(x,3))}
oBrowse:bLDblClick   := {|z,x| Alert('Selecionou:'+aBrowse[oBrowse:nAt,1])}

// Botoes de navegacao
TButton():New(160,002,"GoUp()",   oDlg,{||oBrowse:GoUp(),   oBrowse:setFocus()},60,15,,,.T.)
TButton():New(160,052,"GoDown()", oDlg,{||oBrowse:GoDown(), oBrowse:setFocus()},60,15,,,.T.)
TButton():New(160,102,"GoTop()",  oDlg,{||oBrowse:GoTop(),  oBrowse:setFocus()},60,15,,,.T.)
TButton():New(160,152,"GoBottom()",oDlg,{||oBrowse:GoBottom(),oBrowse:setFocus()},60,15,,,.T.)

ACTIVATE DIALOG oDlg CENTERED
```

---

## 6. TCBrowse com Marcacao Bitmap

**Arquivo:** `EXEMFIN07.prw`
**Padrao:** TCBrowse + LoadBitmap + bLine + bLDblClick

```advpl
// Imagens para marcacao
oImgMark  := LoadBitmap(GetResources(), 'LBTIK')    // Check
oImgDMark := LoadBitmap(GetResources(), 'LBNO')     // X

// Array com flag booleano na posicao 1
aTitulos := {}
aAdd(aTitulos, {.F., cPrefixo, cNumero, cParcela, nValor, ...})

// Browse
oBrowse := TCBROWSE():New(001,001,350,170,,aCabec,{},_oDlg,,,,,{||},,
    _oDlg:oFont,,,,,.F.,,.T.,,.F.,,,)
oBrowse:SetArray(aTitulos)
oBrowse:lAdjustColSize := .T.

// bLine renderiza icone de marca
oBrowse:bLine := {|| { ;
    If(aTitulos[oBrowse:nAt,01], oImgMark, oImgDMark), ;
    aTitulos[oBrowse:nAt,02], ;
    aTitulos[oBrowse:nAt,03], ;
    aTitulos[oBrowse:nAt,04], ;
    Transform(aTitulos[oBrowse:nAt,05], "@E 999,999,999.99") ;
}}

// Duplo clique inverte marcacao
oBrowse:bLDblClick := {|nRow,nCol| ;
    aTitulos[oBrowse:nAt,01] := !aTitulos[oBrowse:nAt,01], ;
    oBrowse:Refresh() }

// Clique no cabecalho marca/desmarca todos
oBrowse:bHeaderClick := {|nRow,nCol| ;
    If(nCol == 1, (lMarcacao(), oBrowse:Refresh()), Nil) }

// Marcar/desmarcar todos
Static Function lMarcacao()
    lTodMarca := !lTodMarca
    For nI := 1 To Len(aTitulos)
        aTitulos[nI, 01] := lTodMarca
    Next nI
Return
```

---

## 7. FWMarkBrowse Fullscreen

**Arquivo:** `EXEM08A01.prw`
**Padrao:** FWMarkBrowse sem Dialog externo + SetValid + SetIgnoreARotina

```advpl
oMarkBrowse1 := FWMarkBrowse():New()
oMarkBrowse1:SetAlias(cTempTable)
oMarkBrowse1:SetFieldMark('OK')
oMarkBrowse1:SetDescription("Solicitacao WMS")
oMarkBrowse1:SetTemporary(.T.)
oMarkBrowse1:SetColumns(aColunas)

// Sem aRotina e sem MenuDef
oMarkBrowse1:SetIgnoreARotina(.T.)
oMarkBrowse1:SetMenuDef("")

// Botao de confirmar na toolbar
oMarkBrowse1:AddButton("Confirmar", {|| CloseBrowse()}, NIL, NIL, 2)

// Validacao antes de fechar
oMarkBrowse1:SetValid({|| MARKED()})

// Fullscreen (sem dialog externo)
oMarkBrowse1:Activate()
oMarkBrowse1:DeActivate()
```

---

## 8. FWMarkBrowse com AllMark Customizado

**Arquivo:** `EXEMWC10.PRW`
**Padrao:** bAllMark customizado + coluna individual

```advpl
// Criar colunas individualmente (sem array)
oCol01 := FWBrwColumn():New()
oCol01:SetData(&('{|| '+cTable01+'->PRODUTO}'))
oCol01:SetTitle('Codigo')
oCol01:SetType('C')
oCol01:SetSize(15)
oCol01:SetAutoSize(.T.)

// MarkBrowse
oBrowse := FWMarkBrowse():New()
oBrowse:SetAlias(cTable01)
oBrowse:SetFieldMark('TR_OK')
oBrowse:SetTemporary(.T.)
oBrowse:SetColumns({oCol01, oCol02, oCol03, ...})
oBrowse:AddLegend(cTable01+"->STATUS=='1'", 'VERDE',    'Pendente')
oBrowse:AddLegend(cTable01+"->STATUS=='2'", 'VERMELHO', 'Impresso')

// AllMark customizado (inverte marcacao)
oBrowse:bAllMark := {|| MCFG6Invert(oBrowse:Mark(), lMarcar := !lMarcar), ;
                        oBrowse:Refresh(.T.)}

oBrowse:SetOwner(oPanel)
oBrowse:Activate()

// Funcao de inversao customizada
Static Function MCFG6Invert(cMarca, lMarcar)
    (cAlias)->(dbGoTop())
    While !(cAlias)->(Eof())
        RecLock(cAlias, .F.)
        (cAlias)->TR_OK := IIf(lMarcar, cMarca, '  ')
        (cAlias)->(MsUnlock())
        (cAlias)->(dbSkip())
    EndDo
Return .T.
```

---

## 9. FWMarkBrowse com Legendas e Botoes Extras

**Arquivo:** `EXEMR10.tlpp`
**Padrao:** AddLegend + AddButton + SetEditCell + lHeaderClick

```advpl
oFwMBrMain := FWMarkBrowse():New()
oFwMBrMain:SetAlias(cTable01)
oFwMBrMain:SetDescription("Impressao OP")
oFwMBrMain:SetFieldMark('FLAG_OK')
oFwMBrMain:SetTemporary(.T.)
oFwMBrMain:SetColumns(aColunas)
oFwMBrMain:SetFontBrowse(oFontGrid)

// Legendas
oFwMBrMain:AddLegend("("+cTable01+")->C2_ZIMPRST != 'S'", "GREEN", "Disponivel", "1")
oFwMBrMain:AddLegend("("+cTable01+")->C2_ZIMPRST == 'S'", "RED",   "Ja impresso", "1")

// Botoes
oFwMBrMain:AddButton('Selecionar todos', ;
    {|| oFwMBrMain:AllMark()}, , 1, 0)
oFwMBrMain:AddButton('Imprimir', ;
    {|| FWMsgRun(, {|o| fImprime(o)}, "Impressao", "Gerando impressao...")}, , 1, 0)

// Edicao inline e clique no cabecalho
oFwMBrMain:oBrowse:SetEditCell(.T., {|| .T.})
oFwMBrMain:oBrowse:lHeaderClick := .T.

oFwMBrMain:SetOwner(oGridMain)
oFwMBrMain:Activate()
```