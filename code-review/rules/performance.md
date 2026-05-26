# Regras de Performance - ADVPL/TLPP

## PERF-01 - Proibido SELECT *

**Impacto**: HIGH

**Descricao**: Nunca use `SELECT *` em queries. Sempre especifique explicitamente as colunas necessarias. O `SELECT *` trafega dados desnecessarios pela rede, consome mais memoria e impede o uso eficiente de indices cobrindo (covering index).

**ERRADO**:
```advpl
User Function ListaCli()
    Local cQuery := ""
    Local cAlias := GetNextAlias()

    cQuery := "SELECT * FROM " + RetSqlName("SA1")
    cQuery += " WHERE D_E_L_E_T_ = ' '"
    cQuery += " AND A1_FILIAL = '" + xFilial("SA1") + "'"

    MpSysOpenQuery(cQuery, cAlias)

    While !(cAlias)->(Eof())
        ConOut((cAlias)->A1_NOME)
        (cAlias)->(DbSkip())
    EndDo

    (cAlias)->(DbCloseArea())
Return
```

**CORRETO**:
```advpl
User Function ListaCli()
    Local cQuery := ""
    Local cAlias := GetNextAlias()

    cQuery := "SELECT A1_COD, A1_LOJA, A1_NOME, A1_CGC "
    cQuery += " FROM " + RetSqlName("SA1")
    cQuery += " WHERE D_E_L_E_T_ = ' '"
    cQuery += " AND A1_FILIAL = '" + xFilial("SA1") + "'"

    MpSysOpenQuery(cQuery, cAlias)

    While !(cAlias)->(Eof())
        ConOut((cAlias)->A1_NOME)
        (cAlias)->(DbSkip())
    EndDo

    (cAlias)->(DbCloseArea())
Return
```

**Explicacao**: Listar apenas as colunas necessarias reduz o trafego de rede, o consumo de memoria e permite ao otimizador do banco usar indices de cobertura.

---

## PERF-02 - WHERE com Campos Indexados

**Impacto**: HIGH

**Descricao**: Clausulas WHERE devem utilizar campos que fazem parte dos indices SIX da tabela. Consulte o indice da tabela (SIX) para garantir que os campos filtrados estao indexados. Sempre inclua a filial como primeiro campo do filtro.

**ERRADO**:
```advpl
User Function BuscaProd()
    Local cQuery := ""
    Local cAlias := GetNextAlias()

    // A1_EMAIL nao esta indexado no SIX padrao
    cQuery := "SELECT A1_COD, A1_NOME FROM " + RetSqlName("SA1")
    cQuery += " WHERE D_E_L_E_T_ = ' '"
    cQuery += " AND A1_EMAIL = 'teste@email.com'"

    MpSysOpenQuery(cQuery, cAlias)
    // ... processamento
    (cAlias)->(DbCloseArea())
Return
```

**CORRETO**:
```advpl
User Function BuscaProd()
    Local cQuery := ""
    Local cAlias := GetNextAlias()

    // A1_COD + A1_LOJA = indice 1 do SIX (SA1)
    cQuery := "SELECT A1_COD, A1_NOME, A1_EMAIL FROM " + RetSqlName("SA1")
    cQuery += " WHERE D_E_L_E_T_ = ' '"
    cQuery += " AND A1_FILIAL = '" + xFilial("SA1") + "'"
    cQuery += " AND A1_COD = '000001'"
    cQuery += " AND A1_LOJA = '01'"

    MpSysOpenQuery(cQuery, cAlias)
    // ... processamento
    (cAlias)->(DbCloseArea())
Return
```

**Explicacao**: Queries sem indice resultam em full table scan, degradando drasticamente a performance em tabelas com muitos registros.

---

## PERF-03 - N+1 Query Loop

**Impacto**: HIGH

**Descricao**: Nunca execute queries dentro de loops (While/For). Consolide em uma unica query usando `IN()`, `JOIN` ou subconsultas. O padrao N+1 eh uma das maiores causas de lentidao em rotinas Protheus.

**ERRADO**:
```advpl
User Function TotPed()
    Local cQryPed := ""
    Local cQryItm := ""
    Local cAlsPed := GetNextAlias()
    Local cAlsItm := ""
    Local nTotal  := 0

    cQryPed := "SELECT C5_NUM FROM " + RetSqlName("SC5")
    cQryPed += " WHERE D_E_L_E_T_ = ' '"
    cQryPed += " AND C5_FILIAL = '" + xFilial("SC5") + "'"

    MpSysOpenQuery(cQryPed, cAlsPed)

    While !(cAlsPed)->(Eof())
        // PROBLEMA: query dentro do loop = N+1
        cAlsItm := GetNextAlias()
        cQryItm := "SELECT SUM(C6_VALOR) AS TOTAL FROM " + RetSqlName("SC6")
        cQryItm += " WHERE D_E_L_E_T_ = ' '"
        cQryItm += " AND C6_FILIAL = '" + xFilial("SC6") + "'"
        cQryItm += " AND C6_NUM = '" + (cAlsPed)->C5_NUM + "'"

        MpSysOpenQuery(cQryItm, cAlsItm)
        nTotal += (cAlsItm)->TOTAL
        (cAlsItm)->(DbCloseArea())

        (cAlsPed)->(DbSkip())
    EndDo

    (cAlsPed)->(DbCloseArea())
Return nTotal
```

**CORRETO**:
```advpl
User Function TotPed()
    Local cQuery := ""
    Local cAlias := GetNextAlias()
    Local nTotal := 0

    // Uma unica query com JOIN resolve tudo
    cQuery := "SELECT SUM(C6.C6_VALOR) AS TOTAL "
    cQuery += " FROM " + RetSqlName("SC5") + " C5 "
    cQuery += " INNER JOIN " + RetSqlName("SC6") + " C6 "
    cQuery += "   ON C6.C6_FILIAL = C5.C5_FILIAL "
    cQuery += "  AND C6.C6_NUM = C5.C5_NUM "
    cQuery += "  AND C6.D_E_L_E_T_ = ' ' "
    cQuery += " WHERE C5.D_E_L_E_T_ = ' '"
    cQuery += " AND C5.C5_FILIAL = '" + xFilial("SC5") + "'"

    MpSysOpenQuery(cQuery, cAlias)
    nTotal := (cAlias)->TOTAL
    (cAlias)->(DbCloseArea())
Return nTotal
```

**Explicacao**: Cada query tem overhead de rede, parse e execucao. Com 1000 pedidos, o padrao N+1 gera 1001 queries; o JOIN resolve em 1.

---

## PERF-04 - Duracao Minima de Lock

**Impacto**: HIGH

**Descricao**: O `RecLock` deve ser seguido imediatamente pelas atribuicoes e pelo `MsUnLock`. Nunca execute logica de negocio, calculos complexos ou chamadas externas enquanto um registro estiver travado.

**ERRADO**:
```advpl
User Function AtuaSaldo(cProd, nQtd)
    DbSelectArea("SB2")
    DbSetOrder(1)
    DbSeek(xFilial("SB2") + cProd)

    RecLock("SB2", .F.)

    // PROBLEMA: calculo complexo com registro travado
    Local nSaldoAnt := SB2->B2_QATU
    Local nNovoSaldo := nSaldoAnt + nQtd
    Local nCustoMed := CalcCustoMedio(cProd)  // chamada externa!
    Local nValorTot := nNovoSaldo * nCustoMed

    SB2->B2_QATU  := nNovoSaldo
    SB2->B2_VATU1 := nValorTot
    SB2->B2_CM1   := nCustoMed
    MsUnLock()
Return
```

**CORRETO**:
```advpl
User Function AtuaSaldo(cProd, nQtd)
    Local nSaldoAnt  := 0
    Local nNovoSaldo := 0
    Local nCustoMed  := 0
    Local nValorTot  := 0

    DbSelectArea("SB2")
    DbSetOrder(1)
    DbSeek(xFilial("SB2") + cProd)

    // Leitura e calculos ANTES do lock
    nSaldoAnt  := SB2->B2_QATU
    nNovoSaldo := nSaldoAnt + nQtd
    nCustoMed  := CalcCustoMedio(cProd)
    nValorTot  := nNovoSaldo * nCustoMed

    // Lock apenas para gravacao imediata
    If RecLock("SB2", .F.)
        SB2->B2_QATU  := nNovoSaldo
        SB2->B2_VATU1 := nValorTot
        SB2->B2_CM1   := nCustoMed
        MsUnLock()
    EndIf
Return
```

**Explicacao**: Locks prolongados bloqueiam outros usuarios e processos. Calcule tudo antes, trave apenas para gravar.

---

## PERF-05 - Pre-alocacao de Arrays

**Impacto**: MEDIUM

**Descricao**: Quando o tamanho do array eh conhecido ou estimavel, use `ASize()` com indice direto ao inves de `AAdd()` em loops grandes. O `AAdd()` realoca memoria a cada chamada.

**ERRADO**:
```advpl
User Function GeraArray()
    Local aResult := {}
    Local cAlias  := GetNextAlias()
    Local cQuery  := ""

    cQuery := "SELECT COUNT(*) AS QTD FROM " + RetSqlName("SA1")
    cQuery += " WHERE D_E_L_E_T_ = ' '"
    // Sabe quantos registros tem, mas nao pre-aloca

    cQuery := "SELECT A1_COD, A1_NOME FROM " + RetSqlName("SA1")
    cQuery += " WHERE D_E_L_E_T_ = ' '"

    MpSysOpenQuery(cQuery, cAlias)

    While !(cAlias)->(Eof())
        AAdd(aResult, {(cAlias)->A1_COD, (cAlias)->A1_NOME})
        (cAlias)->(DbSkip())
    EndDo

    (cAlias)->(DbCloseArea())
Return aResult
```

**CORRETO**:
```advpl
User Function GeraArray()
    Local aResult := {}
    Local cAlias  := GetNextAlias()
    Local cAlsCnt := GetNextAlias()
    Local cQuery  := ""
    Local nCount  := 0
    Local nIdx    := 0

    // Primeiro obtem a contagem
    cQuery := "SELECT COUNT(*) AS QTD FROM " + RetSqlName("SA1")
    cQuery += " WHERE D_E_L_E_T_ = ' '"
    MpSysOpenQuery(cQuery, cAlsCnt)
    nCount := (cAlsCnt)->QTD
    (cAlsCnt)->(DbCloseArea())

    If nCount == 0
        Return aResult
    EndIf

    // Pre-aloca o array com tamanho conhecido
    aResult := Array(nCount)

    cQuery := "SELECT A1_COD, A1_NOME FROM " + RetSqlName("SA1")
    cQuery += " WHERE D_E_L_E_T_ = ' '"

    MpSysOpenQuery(cQuery, cAlias)

    While !(cAlias)->(Eof())
        nIdx++
        aResult[nIdx] := {(cAlias)->A1_COD, (cAlias)->A1_NOME}
        (cAlias)->(DbSkip())
    EndDo

    (cAlias)->(DbCloseArea())
Return aResult
```

**Explicacao**: Para 10.000 registros, `AAdd` faz 10.000 realocacoes de memoria. Com `Array(nCount)`, aloca uma unica vez.

---

## PERF-06 - Concatenacao de Strings em Loop

**Impacto**: MEDIUM

**Descricao**: Nunca concatene strings dentro de loops usando `+=`. Strings em ADVPL sao imutaveis; cada concatenacao cria uma nova string. Use array com posterior conversao.

**ERRADO**:
```advpl
User Function GeraCSV()
    Local cResult := ""
    Local cAlias  := GetNextAlias()
    Local cQuery  := ""

    cQuery := "SELECT A1_COD, A1_NOME FROM " + RetSqlName("SA1")
    cQuery += " WHERE D_E_L_E_T_ = ' '"

    MpSysOpenQuery(cQuery, cAlias)

    While !(cAlias)->(Eof())
        // PROBLEMA: concatenacao em loop
        cResult += (cAlias)->A1_COD + ";" + (cAlias)->A1_NOME + CRLF
        (cAlias)->(DbSkip())
    EndDo

    (cAlias)->(DbCloseArea())
Return cResult
```

**CORRETO**:
```advpl
User Function GeraCSV()
    Local aLines  := {}
    Local cAlias  := GetNextAlias()
    Local cQuery  := ""
    Local cResult := ""

    cQuery := "SELECT A1_COD, A1_NOME FROM " + RetSqlName("SA1")
    cQuery += " WHERE D_E_L_E_T_ = ' '"

    MpSysOpenQuery(cQuery, cAlias)

    While !(cAlias)->(Eof())
        AAdd(aLines, (cAlias)->A1_COD + ";" + AllTrim((cAlias)->A1_NOME))
        (cAlias)->(DbSkip())
    EndDo

    (cAlias)->(DbCloseArea())

    // Junta tudo de uma vez
    cResult := ArrTokStr(aLines, CRLF)
Return cResult
```

**Explicacao**: Cada `+=` cria uma copia completa da string acumulada. Com 5.000 linhas de 100 chars, sao ~250MB de alocacoes temporarias. O array acumula referencias e a juncao final eh uma unica operacao.

---

## PERF-07 - Fechamento Imediato de Alias

**Impacto**: MEDIUM

**Descricao**: Feche alias de queries (`DbCloseArea`) imediatamente apos extrair os dados necessarios. Alias abertos consomem conexoes do pool de banco de dados e memoria do servidor.

**ERRADO**:
```advpl
User Function ProcessaDados()
    Local cAlias1 := GetNextAlias()
    Local cAlias2 := GetNextAlias()
    Local cAlias3 := GetNextAlias()

    MpSysOpenQuery(cQuery1, cAlias1)
    MpSysOpenQuery(cQuery2, cAlias2)
    MpSysOpenQuery(cQuery3, cAlias3)

    // Processa todos, mas so fecha no final
    While !(cAlias1)->(Eof())
        // ... processamento longo
        (cAlias1)->(DbSkip())
    EndDo

    While !(cAlias2)->(Eof())
        // ... processamento longo
        (cAlias2)->(DbSkip())
    EndDo

    While !(cAlias3)->(Eof())
        // ... processamento longo
        (cAlias3)->(DbSkip())
    EndDo

    // Fecha tudo junto - alias1 e alias2 ficaram abertos sem necessidade
    (cAlias1)->(DbCloseArea())
    (cAlias2)->(DbCloseArea())
    (cAlias3)->(DbCloseArea())
Return
```

**CORRETO**:
```advpl
User Function ProcessaDados()
    Local cAlias := ""

    // Processa e fecha cada alias imediatamente
    cAlias := GetNextAlias()
    MpSysOpenQuery(cQuery1, cAlias)
    While !(cAlias)->(Eof())
        // ... processamento
        (cAlias)->(DbSkip())
    EndDo
    (cAlias)->(DbCloseArea())

    cAlias := GetNextAlias()
    MpSysOpenQuery(cQuery2, cAlias)
    While !(cAlias)->(Eof())
        // ... processamento
        (cAlias)->(DbSkip())
    EndDo
    (cAlias)->(DbCloseArea())

    cAlias := GetNextAlias()
    MpSysOpenQuery(cQuery3, cAlias)
    While !(cAlias)->(Eof())
        // ... processamento
        (cAlias)->(DbSkip())
    EndDo
    (cAlias)->(DbCloseArea())
Return
```

**Explicacao**: Cada alias aberto consome uma conexao do pool. Em ambiente com muitos usuarios, alias desnecessariamente abertos causam esgotamento de conexoes.

---

## PERF-08 - MsSeek ao inves de DbSeek

**Impacto**: LOW

**Descricao**: Use `MsSeek()` ao inves de `DbSeek()` quando precisar posicionar e testar o resultado. `MsSeek` combina posicionamento e retorno logico em uma unica operacao otimizada.

**ERRADO**:
```advpl
User Function BuscaCli(cCod)
    Local cNome := ""

    DbSelectArea("SA1")
    DbSetOrder(1)
    DbSeek(xFilial("SA1") + cCod)

    If Found()
        cNome := SA1->A1_NOME
    EndIf
Return cNome
```

**CORRETO**:
```advpl
User Function BuscaCli(cCod)
    Local cNome := ""

    DbSelectArea("SA1")
    DbSetOrder(1)

    If MsSeek(1, xFilial("SA1") + cCod)
        cNome := SA1->A1_NOME
    EndIf
Return cNome
```

**Explicacao**: `MsSeek` realiza a selecao de area, posicionamento de ordem e busca em uma unica chamada, reduzindo overhead de chamadas internas.

---

## PERF-09 - ChangeQuery para Portabilidade SQL

**Impacto**: MEDIUM

**Descricao**: Sempre utilize `ChangeQuery()` para transformar queries SQL antes de executar. Esta funcao garante a portabilidade entre diferentes bancos de dados (SQL Server, Oracle, PostgreSQL) suportados pelo Protheus.

**ERRADO**:
```advpl
User Function ConsCliente()
    Local cQuery := ""
    Local cAlias := GetNextAlias()

    // Query com sintaxe especifica do SQL Server
    cQuery := "SELECT TOP 10 A1_COD, A1_NOME "
    cQuery += " FROM " + RetSqlName("SA1")
    cQuery += " WHERE D_E_L_E_T_ = ' '"
    cQuery += " AND A1_FILIAL = '" + xFilial("SA1") + "'"
    cQuery += " ORDER BY A1_NOME"

    MpSysOpenQuery(cQuery, cAlias)
    // ...
    (cAlias)->(DbCloseArea())
Return
```

**CORRETO**:
```advpl
User Function ConsCliente()
    Local cQuery := ""
    Local cAlias := GetNextAlias()

    cQuery := "SELECT A1_COD, A1_NOME "
    cQuery += " FROM " + RetSqlName("SA1")
    cQuery += " WHERE D_E_L_E_T_ = ' '"
    cQuery += " AND A1_FILIAL = '" + xFilial("SA1") + "'"
    cQuery += " ORDER BY A1_NOME"

    cQuery := ChangeQuery(cQuery)
    MpSysOpenQuery(cQuery, cAlias)
    // ...
    (cAlias)->(DbCloseArea())
Return
```

**Explicacao**: `ChangeQuery` adapta a sintaxe SQL para o banco de dados configurado no ambiente. Sem ela, queries podem falhar ao migrar de SQL Server para Oracle ou PostgreSQL.

---

## PERF-10 - Limpeza de Tabelas Temporarias

**Impacto**: MEDIUM

**Descricao**: Ao usar `FWTemporaryTable`, sempre crie com indice apropriado e chame `Delete()` ao final. Tabelas temporarias nao limpas consomem espaco no tempdb e podem causar problemas de performance no banco.

**ERRADO**:
```advpl
User Function ProcTemp()
    Local oTempTable := Nil
    Local cAlias     := GetNextAlias()

    oTempTable := FWTemporaryTable():New(cAlias)
    oTempTable:SetFields({;
        {"CAMPO1", "C", 10, 0},;
        {"CAMPO2", "N", 14, 2},;
        {"CAMPO3", "C", 30, 0};
    })
    // PROBLEMA: sem indice, buscas serao lentas
    oTempTable:Create()

    // ... popula e usa a tabela ...

    // PROBLEMA: nao limpa a tabela temporaria
    (cAlias)->(DbCloseArea())
Return
```

**CORRETO**:
```advpl
User Function ProcTemp()
    Local oTempTable := Nil
    Local cAlias     := GetNextAlias()
    Local oError     := Nil
    Local bErrorBlk  := {|e| oError := e, Break(e)}

    oTempTable := FWTemporaryTable():New(cAlias)
    oTempTable:SetFields({;
        {"CAMPO1", "C", 10, 0},;
        {"CAMPO2", "N", 14, 2},;
        {"CAMPO3", "C", 30, 0};
    })
    // Cria indice para otimizar buscas
    oTempTable:AddIndex("01", {"CAMPO1"})
    oTempTable:Create()

    Begin Sequence With bErrorBlk

        // ... popula e usa a tabela ...

    Recover Using oError
        ConOut("PERF-10: Erro no processamento - " + oError:Description)
    End Sequence

    // Sempre limpa a tabela temporaria
    oTempTable:Delete()
Return
```

**Explicacao**: `FWTemporaryTable:Delete()` remove a tabela do banco e libera o espaco no tempdb. Sem a chamada, tabelas acumulam e degradam o banco ao longo do tempo.