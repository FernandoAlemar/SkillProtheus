# TReport - Exemplos de Referencia

---

## Exemplo 1: TReport Basico com Query SQL (ExemploRelSaldo)

**Arquivo**: ExemploRelSaldo.tlpp

```advpl
#include 'totvs.ch'
#include "tlpp-core.th"

User Function ExemploRelSaldo()
    Local cPerg := "EXEMSXR01" as character
    Local cBckFilial := cFilAnt
    Local oReport := Nil as object

    If !Pergunte(cPerg, .T.)
        Return
    Endif

    oReport := ReportDef()
    oReport:PrintDialog()

    cFilAnt := cBckFilial
Return


Static Function ReportDef()
    Local oProd as Object

    oReport := TReport():New('ExemploRelSaldo', ;
        'Analise de Saldo WMS x ERP', , ;
        {|oReport| PrintReport(oReport)}, ;
        'Analise de Saldos')

    Pergunte("EXEMSXR01", .F.)

    oReport:SetLandscape()
    oReport:nFontBody   := 08
    oReport:nLineHeight := 40
    oReport:SetColSpace(1)
    oReport:SetTotalInLine(.T.)

    oProd := TRSection():New(oReport, "Analise de Saldo", , )

    TRCell():New(oProd, "FILIAL", , "Filial", /*Pict*/, TamSx3("B2_FILIAL")[1]+5, ;
        /*lPixel*/, /*bBlock*/, , , , , , , , , .F.)
    TRCell():New(oProd, "PROD", , "Produto", /*Pict*/, TamSx3("B1_COD")[1], ;
        /*lPixel*/, /*bBlock*/, , , , , , , , , .F.)
    TRCell():New(oProd, "DESC", , "Descricao", /*Pict*/, TamSx3("B1_DESC")[1])
    TRCell():New(oProd, "SLDERP", , "Sld. Protheus", ;
        GetSx3Cache('B2_QATU','X3_PICTURE'), TamSx3("B2_QATU")[1])
    TRCell():New(oProd, "SLDWMS", , "Sld. WMS", ;
        GetSx3Cache('B2_QATU','X3_PICTURE'), TamSx3("B2_QATU")[1])
    TRCell():New(oProd, "RESULT", , "Resultado", ;
        GetSx3Cache('B2_QATU','X3_PICTURE'), TamSx3("B2_QATU")[1])
    TRCell():New(oProd, "MOTIVO", , "Motivo", "!@", 100)

Return oReport


Static Function PrintReport(oReport)
    Local cQuery        as Character
    Local nTotalRegistro as numeric
    Local oOP           := oReport:Section(1)
    Local cAliasPrc     := GetNextAlias() as character

    cQuery := " SELECT B2_FILIAL, B2_COD, B2_LOCAL, ZC9_SLDWMS " + CRLF
    cQuery += " FROM " + RetSqlname("SB2") + " SB2 " + CRLF
    cQuery += " INNER JOIN " + RetSqlname("ZC9") + " ZC9 " + CRLF
    cQuery += " ON ZC9_FILIAL=B2_FILIAL AND ZC9_COD=B2_COD " + CRLF
    cQuery += " AND SB2.D_E_L_E_T_ = ' ' " + CRLF
    cQuery += " WHERE ZC9.D_E_L_E_T_ = ' ' " + CRLF
    cQuery += " AND ZC9_FILIAL BETWEEN '" + MV_PAR02 + "' AND '" + MV_PAR03 + "' "

    MPSysOpenQuery(cQuery, cAliasPrc)

    (cAliasPrc)->(dbEval({||nTotalRegistro++}))
    (cAliasPrc)->(dbGoTop())

    oReport:SetMeter(nTotalRegistro)
    oOP:Init()

    Do While (cAliasPrc)->(!Eof())
        If oReport:Cancel()
            Exit
        Endif
        oReport:IncMeter()

        oOP:Cell("FILIAL"):SetValue((cAliasPrc)->B2_FILIAL)
        oOP:Cell("PROD"):SetValue((cAliasPrc)->B2_COD)
        // ... seta demais celulas
        oOP:Cell("MOTIVO"):SetValue("OK")

        oOP:PrintLine()
        (cAliasPrc)->(DbSkip())
    Enddo

    oOP:Finish()
    (cAliasPrc)->(dbCloseArea())
Return
```

---

## Exemplo 2: TReport com Secoes Master/Detail (ExemploRelConferencia)

**Arquivo**: ExemploRelConferencia.tlpp

```advpl
#Include "totvs.ch"
#include 'tlpp-core.th'

User Function ExemploRelConferencia()
    Local aPergs := {} as array

    aAdd(aPergs, {1, "Filial De", Space(6), "", ".T.", "SM0", ".T.", 80, .F.})
    aAdd(aPergs, {1, "Filial Ate", 'ZZZZZZ', "", ".T.", "SM0", ".T.", 80, .T.})

    IF !ParamBox(aPergs, "Informe os parametros", , , , , , , , "", .F., .F.)
        Return
    ENDIF

    oReport := ReportDef()
    oReport:PrintDialog()
Return


Static Function ReportDef()
    Local oRegraFilial as Object
    Local oDetalhe as Object

    oReport := TReport():New('ExemploRelConferencia', ;
        'Conferencia de Titulo', , ;
        {|oReport| PrintReport(oReport)}, ;
        'Conferencia de Titulo')

    oReport:SetLandscape()
    oReport:SetTotalInLine(.T.)

    // Secao Master: consolidado por filial
    oRegraFilial := TRSection():New(oReport, 'Consolidado por filial', , )
    TRCell():New(oRegraFilial, "FILIAL", , "FILIAL", /*Pict*/, 6)
    TRCell():New(oRegraFilial, "SOMATOTAL", , "Saldo Total", ;
        GetSx3Cache('E1_VALOR','X3_PICTURE'), TamSx3("E1_VALOR")[1])

    // Secao Detail: detalhe da conferencia
    oDetalhe := TRSection():New(oReport, "Detalhe da conferencia")
    oDetalhe:SetTotalInLine(.F.)
    TRCell():New(oDetalhe, "TIPOPROC", , "Tp. Baixa", /*Pict*/, 20)
    TRCell():New(oDetalhe, "VLRTOTAL", , "Valor", ;
        GetSx3Cache('E1_VALOR','X3_PICTURE'), TamSx3("E1_VALOR")[1])

Return oReport


Static Function PrintReport(oReport)
    Local oRegraFilial := oReport:Section(1)
    Local oDetalhe     := oReport:Section(2)
    Local cQuery as character
    Local cAlias := GetNextAlias()
    Local nTotalRegistro as numeric

    cQuery := " SELECT DISTINCT SUBSTRING(E2_FILIAL,1,6) E2_FILIAL " + CRLF
    cQuery += " FROM " + RETSQLNAME("SE2") + " SE2 " + CRLF
    cQuery += " WHERE E2_SALDO > 0 AND SE2.D_E_L_E_T_ = ' ' " + CRLF
    cQuery += " AND SUBSTRING(E2_FILIAL,1,6) BETWEEN '" + MV_PAR01 + "' AND '" + MV_PAR02 + "'"
    cQuery := ChangeQuery(cQuery)
    MPSysOpenQuery(cQuery, cAlias)

    (cAlias)->(dbEval({||nTotalRegistro++}))
    (cAlias)->(dbGoTop())
    oReport:SetMeter(nTotalRegistro)

    While (cAlias)->(!EOF())
        oReport:IncMeter()
        If oReport:Cancel()
            Exit
        Endif

        // Imprime secao master
        oRegraFilial:Init()
        oRegraFilial:Cell("FILIAL"):SetValue((cAlias)->E2_FILIAL)
        oRegraFilial:Cell("SOMATOTAL"):SetValue(nTotalSaldo)
        oRegraFilial:PrintLine()
        oRegraFilial:Finish()

        // Imprime secao detail
        oDetalhe:Init()
        For x1 := 1 To Len(aItens)
            oDetalhe:Cell("TIPOPROC"):SetValue(aItens[x1][1])
            oDetalhe:Cell("VLRTOTAL"):SetValue(aItens[x1][2])
            oDetalhe:PrintLine()
        Next
        oDetalhe:Finish()

        (cAlias)->(dbSkip())
    Enddo
Return
```

---

## Exemplo 3: TReport com TRBreak e TRFunction (EXEMR01)

**Arquivo**: EXEMR01.tlpp

```advpl
Static Function fReportDef()
    oReport := TReport():New(cNameRelat, ;
        "Relatorio de Despesas de Viagem", , ;
        {|oReport| fRepPrint(oReport)})
    oReport:SetTotalInLine(.F.)
    oReport:lParamPage := .F.

    oSection := TRSection():New(oReport, cSectionName, {"QRY_Z10"})

    TRCell():New(oSection, "Z10_VIAGEM", "QRY_Z10", "Viagem", , 15)
    TRCell():New(oSection, "Z10_DESCRI", "QRY_Z10", "Descricao", , 40)
    TRCell():New(oSection, "Z10_ZVLRD",  "QRY_Z10", "Valor", ;
        "@E 999,999,999.99", 18)

    // Quebra por viagem com totalizador SUM
    oBreak := TRBreak():New(oSection, ;
        oSection:Cell("Z10_VIAGEM"), "Total da Viagem", .F.)
    TRFunction():New(oSection:Cell("Z10_ZVLRD"), , "SUM", oBreak, , ;
        "@E 999,999,999.99", , .F.)
Return oReport
```

---

## Exemplo 4: TReport com Tabela Temporaria (ExemploRelGrid)

**Arquivo**: ExemploRelGrid.tlpp

```advpl
User Function ExemRelGrid(aData)
    Local aCampos := {}
    Private aLines := aData
    Private cTable01 := GetNextAlias()
    Private oTmpTable := Nil

    // Define campos da tabela temporaria
    aAdd(aCampos, {'E2_FILIAL', GetSx3Cache("E2_FILIAL","X3_TIPO"), ;
        GetSx3Cache("E2_FILIAL","X3_TAMANHO"), 0})
    aAdd(aCampos, {'E2_SALDO', GetSx3Cache("E2_SALDO","X3_TIPO"), ;
        GetSx3Cache("E2_SALDO","X3_TAMANHO"), 0})
    // ... mais campos

    // Cria tabela temporaria
    oTmpTable := FWTemporaryTable():New(cTable01)
    oTmpTable:SetFields(aCampos)
    oTmpTable:Create()

    oReport := fReportDef()
    oReport:PrintDialog()
Return

Static Function fRepPrint(oReport)
    // Popula tabela temporaria com dados do array
    For nAtual := 1 To Len(aLines)
        RecLock(cTable01, .T.)
        (cTable01)->E2_FILIAL := aLines[nAtual, 1]
        (cTable01)->E2_SALDO  := aLines[nAtual, 10]
        // ... preenche campos
        (cTable01)->(MsUnlock())
    Next

    // Imprime da tabela temporaria
    oSectDad:Init()
    (cTable01)->(DbGoTop())
    While !(cTable01)->(Eof())
        oSectDad:PrintLine()
        (cTable01)->(DbSkip())
    EndDo
    oSectDad:Finish()
    (cTable01)->(DbCloseArea())
Return
```

---

## Exemplo 5: TReport com BEGIN REPORT QUERY (EXEMR02)

**Arquivo**: EXEMR02.prw

```advpl
// Usa Embedded SQL com BEGIN REPORT QUERY
Static Function PrintReport(oReport)
    BEGIN REPORT QUERY oSection1
        BeginSql Alias "QRY"
            SELECT
                %Exp:cQrySel%
            FROM
                %table:SE1% SE1 (NOLOCK)
            LEFT JOIN %table:SA1% SA1 (NOLOCK)
                ON SA1.%notDel%
                AND %Exp:cLFSA1%
            LEFT JOIN %table:CT1% CT1 (NOLOCK)
                ON CT1.%notDel%
                AND %Exp:cLFCT1%
            WHERE
                %Exp:cQryWhr%
            ORDER BY
                %Exp:cQryOrde%
        EndSql
    END REPORT QUERY oSection1

    // Loop manual com controle de quebra
    While QRY->(!EOF())
        oSection1:Init()
        oSection1:PrintLine()

        oSection2:Init()
        While cQuebra == QRY->(campos_quebra)
            oSection2:PrintLine()
            QRY->(dbSkip())
        EndDo
    EndDo
Return
```

---

## Exemplo 6: PDF com FWMSPrinter (ExemploRelPDF)

**Arquivo**: ExemploRelPDF.tlpp

```advpl
Static Function fMontaRel(cJob, ...)
    // Fontes
    Private oFontDet  := TFont():New("Arial", 9, -10, .T., .F.)
    Private oFontTitN := TFont():New("Arial", 9, -13, .T., .T.)

    // Cria PDF
    oPrintPvt := FWMSPrinter():New(cArquivo, IMP_PDF, .F., "", .T.)
    oPrintPvt:cPathPDF := cCaminho
    oPrintPvt:SetResolution(72)
    oPrintPvt:SetPortrait()
    oPrintPvt:SetPaperSize(DMPAPER_A4)
    oPrintPvt:SetMargin(60, 60, 60, 60)

    While !QRY->(EOF())
        oPrintPvt:StartPage()
        // Logo
        oPrintPvt:SayBitmap(nLin, nCol, cBitmap, 200, 45)
        // Texto
        oPrintPvt:SayAlign(nLin, nCol, cTexto, oFont, nLarg, nAlt, COR_PRETO, PAD_CENTER, 0)
        // Box
        oPrintPvt:Box(nTop, nLeft, nBottom, nRight)
        // Linha
        oPrintPvt:Line(nY1, nX1, nY2, nX2, COR_PRETO)
        oPrintPvt:EndPage()
        QRY->(DbSkip())
    EndDo

    If cJob == "S"
        oPrintPvt:Print()
    Else
        oPrintPvt:Preview()
    EndIf
Return
```

---

## Exemplo 7: Excel com FwPrinterXlsx (ExemploRelExcel)

**Arquivo**: ExemploRelExcel.tlpp

```advpl
Static Function GeraExcelExemplo(oSay)
    Private oPrtXlsx
    Private cNomeArquivoExcel := "ExemploRelExcel_" + dtos(date())
    Private cCaminhoExcell := Alltrim(MV_PAR09)

    // Cria arquivo Excel
    oFileW := FwFileWriter():New(cCaminhoExcell + cNomeArquivoExcel)
    oPrtXlsx := FwPrinterXlsx():New()
    oPrtXlsx:Activate(cCaminhoExcell + cNomeArquivoExcel, oFileW)
    oPrtXlsx:AddSheet("Cambio")

    // Formato do cabecalho
    DefFont(FwPrinterFont():Calibri(), 12, .F., .T., .F.)
    oPrtXlsx:SetCellsFormat(;
        FwXlsxHorizontalAlignment():Center():Center(), ;
        FwXlsxCellAlignment():Vertical():Center(), ;
        .T., 0, "0d0c0c", "C0C0C0", "")
    oPrtXlsx:SetBorder(.T., .T., .T., .T., ;
        FwXlsxBorderStyle():Thin(), "0d0c0c")
    oPrtXlsx:SetColumnsWidth(1, 33, 33)

    // Cabecalho
    nLinha := 1
    oPrtXlsx:SetText(nLinha, 1, "Tipo")
    oPrtXlsx:SetText(nLinha, 2, "Filial")
    // ... colunas

    // Reset formato e popular dados
    oPrtXlsx:ResetCellsFormat()
    oPrtXlsx:ResetFont()
    DefFont(FwPrinterFont():Calibri(), 12, .F., .F., .F.)

    Do While cAlias->(!EOF())
        nLinha++
        oPrtXlsx:SetText(nLinha, 1, cAlias->CAMPO)
        oPrtXlsx:SetNumber(nLinha, 2, cAlias->VALOR)
        cAlias->(DbSkip())
    EndDo

    oPrtXlsx:toXlsx()
    oPrtXlsx:DeActivate()
    ShellExecute("Open", cCaminhoExcell, "", cCaminhoExcell, 3)
Return
```