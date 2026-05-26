---
name: protheus-reports
description: >
  Templates para relatorios no Protheus (ADVPL/TLPP).
  Use esta skill SEMPRE que o usuario pedir para criar relatorios, exportacoes
  Excel, documentos PDF, ou qualquer saida impressa no Protheus. Cobre TReport
  (framework oficial TOTVS), FwPrinterXlsx (Excel), FWMSPrinter (PDF),
  perguntas SX1 com Pergunte/AjustaSX1/ParamBox, barras de progresso,
  e anti-patterns como uso de SetPrint classico em codigo novo.
  Para exemplos completos, consulte [references/treport-examples.md](references/treport-examples.md).
---


---

## QUANDO USAR CADA ESTILO

| Situacao | Estilo | Motivo |
|----------|--------|--------|
| Relatorio novo qualquer | **TReport** | Framework oficial TOTVS, exporta PDF/Excel/impressora automaticamente |
| Exportacao de dados tabulares | **Excel (FwPrinterXlsx)** | Controle total sobre formatacao, abre no Excel |
| Documento formatado (fatura, boleto, romaneio) | **PDF (FWMSPrinter)** | Layout pixel-perfect com logo, boxes, linhas |
| Relatorio classico existente para manter | **Classico (SetPrint)** | Somente manutencao - NAO criar novos neste estilo |

---

## 1. TEMPLATE TREPORT

### 1.1 Estrutura Basica

```advpl
#Include "totvs.ch"
#Include "topconn.ch"
#Include "report.ch"

/*/{Protheus.doc} NOMERELATORIO
Descricao do relatorio
@type User Function
@author nome.sobrenome
@since DD/MM/YYYY
/*/
User Function NOMERELATORIO()
    Local cPerg   := "GRUPO_SX1" as character
    Local oReport := Nil as object

    // Carrega perguntas
    If !Pergunte(cPerg, .T.)
        Return
    Endif

    // Define e exibe
    oReport := ReportDef()
    oReport:PrintDialog()
Return


/*/{Protheus.doc} ReportDef
Define estrutura do relatorio TReport
@type Static Function
/*/
Static Function ReportDef()
    Local oReport   as object
    Local oSection1 as object

    oReport := TReport():New( ;
        "NOMERELATORIO",;            // Nome interno (unico)
        "Titulo do Relatorio",;      // Titulo exibido
        ,;                           // Pergunta (nil = usa Pergunte separado)
        {|oReport| PrintReport(oReport)},;  // Bloco de impressao
        "Descricao do Relatorio")    // Descricao

    oReport:SetLandscape()           // ou SetPortrait()
    oReport:SetTotalInLine(.T.)
    oReport:nFontBody   := 08
    oReport:nLineHeight := 40
    oReport:SetColSpace(1)

    // === SECAO PRINCIPAL ===
    oSection1 := TRSection():New(oReport, "Nome da Secao", , )
    // Para celulas com campo do dicionario:
    TRCell():New(oSection1, "CAMPO1", , "Titulo Coluna", ;
        PesqPict("ALIAS","CAMPO1"), TamSx3("CAMPO1")[1])
    // Para celulas customizadas:
    TRCell():New(oSection1, "CUSTOM", , "Titulo Custom", ;
        "@E 999,999,999.99", 18)
    // Para celulas texto simples:
    TRCell():New(oSection1, "TEXTO", , "Descricao", "!@", 40)

    // === SECAO DETALHE (opcional) ===
    // oSection2 := TRSection():New(oReport, "Detalhe", , )
    // TRCell():New(oSection2, ...)

    // === QUEBRAS E TOTALIZADORES (opcional) ===
    // oBreak := TRBreak():New(oSection1, ;
    //     oSection1:Cell("CAMPO_QUEBRA"), "Total do Grupo", .F.)
    // TRFunction():New(oSection1:Cell("VALOR"), , "SUM", oBreak, , ;
    //     "@E 999,999,999.99", , .F.)

Return oReport


/*/{Protheus.doc} PrintReport
Executa a impressao do relatorio
@type Static Function
/*/
Static Function PrintReport(oReport)
    Local cQuery        as character
    Local cAliasPrc     := GetNextAlias() as character
    Local nTotalRegistro as numeric
    Local oSection1     := oReport:Section(1)

    // === MONTA QUERY ===
    cQuery := " SELECT CAMPOS " + CRLF
    cQuery += " FROM " + RetSqlName("ALIAS") + " TAB (NOLOCK) " + CRLF
    cQuery += " WHERE TAB.D_E_L_E_T_ = ' ' " + CRLF
    // Aplica filtros dos parametros
    If !Empty(MV_PAR01) .And. !Empty(MV_PAR02)
        cQuery += " AND CAMPO BETWEEN '" + MV_PAR01 + "' AND '" + MV_PAR02 + "' " + CRLF
    Endif
    cQuery += " ORDER BY CAMPO "

    // === ABRE QUERY ===
    MPSysOpenQuery(cQuery, cAliasPrc)

    // === CONTA REGISTROS E SETA BARRA ===
    (cAliasPrc)->(dbEval({||nTotalRegistro++}))
    (cAliasPrc)->(dbGoTop())
    oReport:SetMeter(nTotalRegistro)

    // === LOOP DE IMPRESSAO ===
    oSection1:Init()
    Do While (cAliasPrc)->(!Eof())
        // Verifica cancelamento
        If oReport:Cancel()
            Exit
        Endif
        oReport:IncMeter()

        // Seta valores
        oSection1:Cell("CAMPO1"):SetValue((cAliasPrc)->CAMPO1)
        oSection1:Cell("CUSTOM"):SetValue(nValor)
        oSection1:Cell("TEXTO"):SetValue(cTexto)

        // Imprime linha
        oSection1:PrintLine()

        (cAliasPrc)->(DbSkip())
    Enddo
    oSection1:Finish()

    // === FECHA QUERY ===
    (cAliasPrc)->(dbCloseArea())
Return
```

### 1.2 TReport com Secoes Master/Detail

```advpl
Static Function PrintReport(oReport)
    Local oMaster  := oReport:Section(1)
    Local oDetalhe := oReport:Section(2)

    // ... query e contagem ...

    While cAliasMaster->(!EOF())
        oReport:IncMeter()

        // Imprime master
        oMaster:Init()
        oMaster:Cell("CAMPO"):SetValue(valor)
        oMaster:PrintLine()
        oMaster:Finish()

        // Imprime detalhes
        oDetalhe:Init()
        While cAliasDetalhe->(!EOF()) .And. condicao_vinculo
            oDetalhe:Cell("CAMPO_DET"):SetValue(valor_det)
            oDetalhe:PrintLine()
            cAliasDetalhe->(DbSkip())
        EndDo
        oDetalhe:Finish()

        cAliasMaster->(DbSkip())
    EndDo
Return
```

### 1.3 TReport com TRBreak e TRFunction

```advpl
// No ReportDef():
oBreak := TRBreak():New(oSection, ;
    oSection:Cell("CAMPO_GRUPO"),;   // Campo que determina a quebra
    "Total do Grupo",;               // Label do subtotal
    .F.)                             // lNumeric

// SUM no campo de valor
TRFunction():New( ;
    oSection:Cell("VALOR"),;  // Celula a totalizar
    ,;                        // Nil
    "SUM",;                   // Funcao: SUM, COUNT, AVG, MIN, MAX
    oBreak,;                  // Objeto de quebra
    ,;                        // Nil
    "@E 999,999,999.99",;    // Picture do total
    ,;                        // Nil
    .F.)                      // lNumeric
```

---

## 2. TEMPLATE EXCEL (FwPrinterXlsx)

```advpl
#Include "totvs.ch"
#Include "topconn.ch"

User Function NOMEEXCEL()
    Local cPerg := "GRUPO_SX1" as character

    If !Pergunte(cPerg, .T.)
        Return
    Endif

    // Valida caminho obrigatorio
    If Empty(MV_PARxx)
        FWAlertInfo('Informe o caminho para salvar o arquivo.', 'NOMEEXCEL')
        Return
    Endif

    FWMsgRun(, {|oSay| GeraExcel(@oSay)}, 'Gerando Excel', 'Aguarde...')
Return


Static Function GeraExcel(oSay)
    Local nLinha     := 1 as numeric
    Local nCol       as numeric
    Local nTotal     as numeric
    Local cAliasPrc  := GetNextAlias() as character
    Private oPrtXlsx as object
    Private cNomeArq := "NomeRelatorio_" + dtos(date()) as character
    Private cCaminho := Alltrim(MV_PARxx) as character

    // === CRIA ARQUIVO EXCEL ===
    Local oFileW := FwFileWriter():New(cCaminho + cNomeArq)
    oPrtXlsx := FwPrinterXlsx():New()
    oPrtXlsx:Activate(cCaminho + cNomeArq, oFileW)
    oPrtXlsx:AddSheet("Dados")

    // === FORMATO DO CABECALHO ===
    oPrtXlsx:SetFont(FwPrinterFont():Calibri(), 12, .F., .T., .F.)
    oPrtXlsx:SetCellsFormat( ;
        FwXlsxHorizontalAlignment():Center():Center(), ;
        FwXlsxCellAlignment():Vertical():Center(), ;
        .T., 0, "0d0c0c", "C0C0C0", "")
    oPrtXlsx:SetBorder(.T., .T., .T., .T., ;
        FwXlsxBorderStyle():Thin(), "0d0c0c")
    oPrtXlsx:SetColumnsWidth(1, 10, 25)  // colunas 1-10, largura 25

    // === CABECALHO ===
    nCol := 1
    oPrtXlsx:SetText(nLinha, nCol++, "Coluna 1")
    oPrtXlsx:SetText(nLinha, nCol++, "Coluna 2")
    oPrtXlsx:SetText(nLinha, nCol++, "Valor")
    // ...

    // === RESET FORMATO PARA DADOS ===
    oPrtXlsx:ResetCellsFormat()
    oPrtXlsx:ResetFont()
    oPrtXlsx:SetFont(FwPrinterFont():Calibri(), 12, .F., .F., .F.)
    oPrtXlsx:SetCellsFormat( ;
        FwXlsxHorizontalAlignment():Left():Left(), ;
        FwXlsxCellAlignment():Vertical():Center(), ;
        .T., 0, "000000", "FFFFFF", "")

    // === QUERY DE DADOS ===
    // ... monta cQuery ...
    MPSysOpenQuery(cQuery, cAliasPrc)
    (cAliasPrc)->(dbEval({||nTotal++}))
    (cAliasPrc)->(dbGoTop())

    // === LOOP DE DADOS ===
    Do While (cAliasPrc)->(!Eof())
        nLinha++
        nCol := 1

        If oSay != Nil
            oSay:SetText("Processando " + cValToChar(nLinha) + " de " + cValToChar(nTotal))
            ProcessMessages()
        Endif

        oPrtXlsx:SetText(nLinha, nCol++, (cAliasPrc)->CAMPO_TEXTO)
        oPrtXlsx:SetNumber(nLinha, nCol++, (cAliasPrc)->CAMPO_NUM)
        oPrtXlsx:SetText(nLinha, nCol++, ;
            Alltrim(Transform((cAliasPrc)->VALOR, GetSx3Cache('CAMPO','X3_PICTURE'))))

        (cAliasPrc)->(DbSkip())
    EndDo

    (cAliasPrc)->(DbCloseArea())

    // === GERA E ABRE ===
    oPrtXlsx:toXlsx()
    oPrtXlsx:DeActivate()
    ShellExecute("Open", cCaminho, "", cCaminho, 3)
Return
```

---

## 3. TEMPLATE PDF (FWMSPrinter)

```advpl
#Include "totvs.ch"
#Include "topconn.ch"
#Include "FWPrintSetup.ch"

#Define PAD_LEFT   0
#Define PAD_RIGHT  1
#Define PAD_CENTER 2
#Define COR_PRETO  RGB(000, 000, 000)
#Define COR_CINZA  RGB(180, 180, 180)

User Function NOMEPDF(cJob)
    Default cJob := "N"
    Local cPerg := "GRUPO_SX1" as character

    If cJob == "S"
        fMontaRel(cJob)
    Else
        If !Pergunte(cPerg, .T.)
            Return
        Endif
        Processa({|| fMontaRel()}, "Processando...")
    Endif
Return


Static Function fMontaRel(cJob)
    Local cBitmap := SuperGetMV("PARAM_LOGO", .F., "\system\logo.png")
    Private nLinAtu  := 0 as numeric
    Private nTamLin  := 10 as numeric
    Private nLinFin  := 820 as numeric
    Private nColIni  := 10 as numeric
    Private nColFin  := 550 as numeric
    Private oPrintPvt as object

    // Fontes
    Private oFontDet  := TFont():New("Arial", 9, -10, .T., .F.) as object
    Private oFontDetN := TFont():New("Arial", 9, -10, .T., .T.) as object  // Negrito
    Private oFontTit  := TFont():New("Arial", 9, -13, .T., .F.) as object
    Private oFontRod  := TFont():New("Arial", 9, -08, .T., .F.) as object

    // === CRIA PDF ===
    If cJob == "S"
        cCaminho := SuperGetMV('PARAM_PATH', , "\spool\")
        cArquivo := "NomeRelatorio_" + dToS(Date()) + ".pdf"
        oPrintPvt := FWMSPrinter():New(cArquivo, IMP_PDF, .F., '', .T., .F.)
        oPrintPvt:cPathPDF := cCaminho
    Else
        cCaminho := GetTempPath()
        cArquivo := "NomeRelatorio_" + dToS(Date())
        oPrintPvt := FWMSPrinter():New(cArquivo, IMP_PDF, .F., "", .T., , @oPrintPvt, "", , , , .T.)
    Endif

    oPrintPvt:SetResolution(72)
    oPrintPvt:SetPortrait()          // ou SetLandscape()
    oPrintPvt:SetPaperSize(DMPAPER_A4)
    oPrintPvt:SetMargin(60, 60, 60, 60)

    // === QUERY ===
    // ... monta cQuery ...

    While !QRY->(EOF())
        nLinAtu := 0

        oPrintPvt:StartPage()

        // Logo (canto superior)
        oPrintPvt:SayBitmap(10, nColIni, cBitmap, 150, 40)

        // Titulo
        nLinAtu := 60
        oPrintPvt:SayAlign(nLinAtu, nColIni, "TITULO DO DOCUMENTO", ;
            oFontTit, nColFin, nTamLin, COR_PRETO, PAD_CENTER, 0)

        // Box com dados
        nLinAtu += 30
        oPrintPvt:Box(nLinAtu, nColIni, nLinAtu + 100, nColFin)

        // Campos dentro do box
        nLinAtu += 10
        oPrintPvt:SayAlign(nLinAtu, nColIni + 5, "Campo: " + valor, ;
            oFontDet, 200, nTamLin, COR_PRETO, PAD_LEFT, 0)

        // Linha separadora
        nLinAtu += 20
        oPrintPvt:Line(nLinAtu, nColIni, nLinAtu, nColFin, COR_CINZA)

        // Rodape
        oPrintPvt:SayAlign(nLinFin, nColIni, ;
            "Gerado em " + DToC(Date()) + " " + Time(), ;
            oFontRod, nColFin, nTamLin, COR_PRETO, PAD_CENTER, 0)

        oPrintPvt:EndPage()
        QRY->(DbSkip())
    EndDo

    // === SAIDA ===
    If cJob == "S"
        oPrintPvt:Print()
    Else
        oPrintPvt:Preview()
    Endif
Return
```

---

## 4. TEMPLATE DE PERGUNTAS

### 4.1 Pergunte Tradicional (SX1 no dicionario)

```advpl
// Na funcao principal:
Local cPerg := "GRUPO_SX1" as character

If !Pergunte(cPerg, .T.)
    Return
Endif

// Na query:
cQuery += " AND CAMPO BETWEEN '" + MV_PAR01 + "' AND '" + MV_PAR02 + "' "
// Para datas:
cQuery += " AND DATA BETWEEN '" + DTOS(MV_PAR03) + "' AND '" + DTOS(MV_PAR04) + "' "
```

### 4.2 AjustaSX1 (criar perguntas via codigo)

```advpl
// Chamar antes do Pergunte():
AjustaSX1()
Pergunte(cPerg, .T.)

// Definicao da funcao:
Static Function AjustaSX1()
    Local aPergunte := {}

    // Range de codigo (De/Ate)
    aAdd(aPergunte, {cGrupo, "01", ;
        "Codigo De ?", "Code From ?", "Codigo Desde ?", ;
        "mv_ch1", "C", 15, 0, 0, "G", "", " ", ;
        "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""})

    aAdd(aPergunte, {cGrupo, "02", ;
        "Codigo Ate ?", "Code To ?", "Codigo Hasta ?", ;
        "mv_ch2", "C", 15, 0, 0, "G", "", "ZZZZZZZZZZZZZZ", ;
        "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""})

    // Range de data (De/Ate)
    aAdd(aPergunte, {cGrupo, "03", ;
        "Data De ?", "Date From ?", "Fecha Desde ?", ;
        "mv_ch3", "D", 8, 0, 0, "G", "", " ", ;
        "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""})

    aAdd(aPergunte, {cGrupo, "04", ;
        "Data Ate ?", "Date To ?", "Fecha Hasta ?", ;
        "mv_ch4", "D", 8, 0, 0, "G", "", " ", ;
        "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""})

    // Combo (Sim/Nao)
    aAdd(aPergunte, {cGrupo, "05", ;
        "Incluir Baixados ?", "Include Settled ?", "Incluir Liquidados ?", ;
        "mv_ch5", "C", 1, 0, 0, "C", "", "1", ;
        "Sim", "Nao", "", "", "", "", "", "", "", "", "", "", "", "", "", ""})

    Local nX
    For nX := 1 To Len(aPergunte)
        PutSX1(aPergunte[nX])
    Next
Return
```

### 4.3 ParamBox (alternativa moderna)

```advpl
Local aPergs := {} as array
Local aRet := {} as array

// Tipo 1: Get com consulta (F3)
aAdd(aPergs, {1, "Filial De",  Space(6),  "", ".T.", "SM0", ".T.", 80, .F.})
aAdd(aPergs, {1, "Filial Ate", 'ZZZZZZ',  "", ".T.", "SM0", ".T.", 80, .T.})

// Tipo 1: Get com data
aAdd(aPergs, {1, "Data De",  Date()-30, "", ".T.", "", ".T.", 80, .F.})
aAdd(aPergs, {1, "Data Ate", Date(),    "", ".T.", "", ".T.", 80, .T.})

// Tipo 2: Combo
aAdd(aPergs, {2, "Tipo Quebra", 1, {"Filial","Cliente","Processo"}, 80, ".T.", .F.})

// Tipo 5: CheckBox
aAdd(aPergs, {5, "Incluir Baixados", .F., "", ".T.", "", "", 80, .F.})

If !ParamBox(aPergs, "Informe os parametros", @aRet)
    Return
Endif

// Acessar valores via aRet[1], aRet[2], etc.
cFilDe  := aRet[1]
cFilAte := aRet[2]
```

---

## 5. REGRAS E BOAS PRATICAS

### 5.1 Consulta de Dados
- **SEMPRE** usar `MPSysOpenQuery(cQuery, cAlias)` para abrir queries
- **SEMPRE** fechar o alias com `(cAlias)->(dbCloseArea())` no final
- **SEMPRE** usar `RetSqlName("ALIAS")` para nome da tabela SQL
- **SEMPRE** filtrar D_E_L_E_T_ = ' ' no WHERE
- **SEMPRE** usar `ChangeQuery()` quando necessario compatibilidade Oracle/MSSQL

### 5.2 Barra de Progresso
```advpl
// Contar registros
(cAlias)->(dbEval({||nTotal++}))
(cAlias)->(dbGoTop())

// TReport:
oReport:SetMeter(nTotal)
oReport:IncMeter()
oReport:Cancel()  // verificar cancelamento

// Processa (classico/PDF):
ProcRegua(nTotal)
IncProc("Processando...")
```

### 5.3 Tratamento de Filial
```advpl
// Salvar e restaurar filial
Local cBckFilial := cFilAnt

// Dentro do loop, quando muda filial:
If cFilAnt != cNovaFilial
    cFilAnt := cNovaFilial
    FWSM0Util():setSM0PositionBycFilAnt()
Endif

// No final:
cFilAnt := cBckFilial
```

### 5.4 Convencao de Nomes
```
Funcao principal:     User Function EXEMnnRnn() ou NomeDescritivo()
Definicao relatorio:  Static Function ReportDef()
Impressao:            Static Function PrintReport(oReport)
Perguntas:            Static Function AjustaSX1()
Alias da query:       GetNextAlias()
```

---

## 6. ANTI-PATTERNS (NAO FACA)

### 6.1 NAO use TCQuery direto sem alias nomeado
```advpl
// ERRADO:
TCQuery cQuery New Alias "QRY"
// CERTO:
Local cAlias := GetNextAlias()
MPSysOpenQuery(cQuery, cAlias)
```

### 6.2 NAO esqueca de verificar Cancel no loop
```advpl
// ERRADO:
While cAlias->(!EOF())
    oSection:PrintLine()
    cAlias->(DbSkip())
EndDo

// CERTO:
While cAlias->(!EOF())
    If oReport:Cancel()
        Exit
    Endif
    oReport:IncMeter()
    oSection:PrintLine()
    cAlias->(DbSkip())
EndDo
```

### 6.3 NAO some valores manualmente quando TRFunction resolve
```advpl
// ERRADO:
nTotal := 0
While ...
    nTotal += nValor
EndDo
// impressao manual do total

// CERTO:
oBreak := TRBreak():New(oSection, oSection:Cell("GRUPO"), "Total", .F.)
TRFunction():New(oSection:Cell("VALOR"), , "SUM", oBreak)
```

### 6.4 NAO deixe conout() de debug no codigo
```advpl
// ERRADO:
conout("stop")
conout("teste")

// CERTO: remova todos os debugs antes de entregar
```

### 6.5 NAO crie relatorio classico novo (SetPrint/@PSAY)
```advpl
// ERRADO para codigo novo:
wnrel := SetPrint(...)
@ nLin, nCol PSAY campo

// CERTO: use TReport para qualquer relatorio novo
oReport := TReport():New(...)
```

### 6.6 NAO manipule cFilAnt sem restaurar
```advpl
// ERRADO:
cFilAnt := cNovaFilial
// ... processamento ...
// esqueceu de restaurar!

// CERTO:
Local cBck := cFilAnt
cFilAnt := cNovaFilial
FWSM0Util():setSM0PositionBycFilAnt()
// ... processamento ...
cFilAnt := cBck
```