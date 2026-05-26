---
name: protheus-data-model
description: >
  Padroes de acesso a dados no ERP Protheus (TOTVS) usando ADVPL/TLPP.
  Use esta skill SEMPRE que o usuario pedir codigo ADVPL ou TLPP que envolva:
  acesso a tabelas do Protheus, queries ao banco de dados, SELECT/consultas SQL,
  dicionarios de dados (SX2, SX3, SX5, SIX), posicionamento de registros,
  DbSelectArea, DbSeek, aliases, MpSysOpenQuery, GetNextAlias, workarea,
  abertura de tabelas, filtros, indices, ou qualquer operacao de leitura/escrita
  em tabelas do Protheus. Tambem use quando o usuario mencionar tabelas com
  codigos como SA1, SA2, SC5, SD1, SE1, SF1, etc. ou perguntar sobre a
  estrutura de dados do Protheus. Esta skill define os padroes de acesso via
  posicionamento e delega o padrao de queries (BeginSQL) para a skill
  advpl-embedded-sql.
---

# Protheus Data Model — Padroes Obrigatorios de Acesso a Dados

> [!IMPORTANT]
> **FONTE DA VERDADE — DICIONÁRIO LOCAL:**
> Consulte **SEMPRE** os metadados em `dicionario/{LETRA}/{ALIAS}.json` antes de gerar código que use campos, tipos, tamanhos, índices ou validações.
> 1. Caminho: `protheus-data-model/dicionario/{primeira letra do alias}/{ALIAS}.json` (ex.: `S/SA1.json`, `U/U97.json`).
> 2. Estrutura do JSON: `tabela`, `nome`, `modo`, `arquivo`, `campos[]`, `indices[]`, `gatilhos[]`, `relacionamentos[]`.
> 3. Referência rápida: [references/dicionario-top200.md](references/dicionario-top200.md) e [tabelas-modulos.md](tabelas-modulos.md).
> 
> **SE A TABELA NÃO EXISTIR NO DICIONÁRIO LOCAL:**
> Informe o usuário explicitamente e **NÃO invente** nomes/tipos/tamanhos de campos. Peça export SX2/SX3 ou confirmação manual antes de prosseguir.

Skill prescritiva com padroes obrigatorios de acesso a dados. Todo codigo ADVPL/TLPP gerado DEVE seguir estes padroes.

---

## 1. QUERIES — MpSysOpenQuery (Apenas para MANUTENÇÃO de código legado)

> [!IMPORTANT]
> Para código NOVO, o padrão obrigatório é **BeginSQL/EndSQL**.
> Consulte a skill `advpl-embedded-sql`. Use `MpSysOpenQuery` apenas se estiver
> alterando uma rotina que já utiliza esse padrão ou em casos onde o
> BeginSQL não seja aplicável.

### 1.1 Padrao basico: MpSysOpenQuery com concatenacao

```advpl
Local cAlias := GetNextAlias()
Local cQuery := ""

cQuery := " SELECT SA1.A1_COD, SA1.A1_LOJA, SA1.A1_NOME, SA1.A1_CGC " + CRLF
cQuery += " FROM " + RetSqlName("SA1") + " SA1 " + CRLF
cQuery += " WHERE SA1.D_E_L_E_T_ = ' ' " + CRLF
cQuery += "   AND SA1.A1_FILIAL = '" + xFilial("SA1") + "' " + CRLF
cQuery += "   AND SA1.A1_ATIVO = '1' " + CRLF

MpSysOpenQuery(ChangeQuery(cQuery), cAlias)

While !(cAlias)->(Eof())
    cCodCli := (cAlias)->A1_COD
    cNome   := (cAlias)->A1_NOME
    (cAlias)->(DbSkip())
EndDo

(cAlias)->(DbCloseArea())
```

### 1.2 Padrao avancado: MpSysOpenQuery + FwPreparedStatement (Para LER e MANTER codigo existente )

```advpl
// Criar o prepared statement UMA VEZ (pode ser Static para reuso)
Static __oQryTit := Nil

If __oQryTit == Nil
    cQuery := " SELECT SE1.E1_FILIAL, SE1.E1_PREFIXO, SE1.E1_NUM, "
    cQuery += "   SE1.E1_SALDO, SE1.R_E_C_N_O_ "
    cQuery += " FROM ? SE1 "
    cQuery += " WHERE SE1.E1_FILIAL = ? "
    cQuery += "   AND SE1.E1_CLIENTE = ? "
    cQuery += "   AND SE1.E1_LOJA = ? "
    cQuery += "   AND SE1.E1_SALDO > 0 "
    cQuery += "   AND SE1.D_E_L_E_T_ = ' ' "

    cQuery := ChangeQuery(cQuery)
    __oQryTit := FWPreparedStatement():New(cQuery)
EndIf

// Bindar parametros (? na ordem)
__oQryTit:SetNumeric(1, RetSqlName("SE1"))
__oQryTit:SetString(2,  FwxFilial("SE1"))
__oQryTit:SetString(3,  cCliente)
__oQryTit:SetString(4,  cLoja)

// Executar via MpSysOpenQuery
cAlias := MpSysOpenQuery(__oQryTit:GetFixQuery())

While !(cAlias)->(Eof())
    nSaldo := (cAlias)->E1_SALDO
    (cAlias)->(DbSkip())
EndDo

(cAlias)->(DbCloseArea())
```

### 1.3 Padrao para valor escalar: MpSysExecScalar (Para LER e MANTER codigo existente)

```advpl
cQuery := " SELECT MAX(R_E_C_N_O_) AS RECNO "
cQuery += " FROM " + RetSqlName("SE1") + " SE1 "
cQuery += " WHERE SE1.E1_FILIAL = '" + xFilial("SE1") + "' "
cQuery += "   AND SE1.E1_NUM = '" + cNumTit + "' "
cQuery += "   AND SE1.D_E_L_E_T_ = ' ' "

nRecno := MpSysExecScalar(ChangeQuery(cQuery), 'RECNO')
```

### 1.4 Padrao DML (INSERT/UPDATE/DELETE): TCSqlExec

Use TCSqlExec APENAS para operacoes DML que nao retornam resultset.

```advpl
cSql := "DELETE FROM " + cTmpTable
If TCSqlExec(cSql) < 0
    ConOut("Erro SQL: " + TCSqlError())
EndIf
```

### 1.5 Checklist obrigatorio para toda query (Para LER e MANTER codigo existente)

1. `GetNextAlias()` para alias — NUNCA hardcode "QRY", "TRB", "TMP"
2. `RetSqlName("XXX")` para nome fisico da tabela — NUNCA nome direto
3. `D_E_L_E_T_ = ' '` (espaço entre aspas simples) — NUNCA `= ''` nem `<> '*'`
4. `xFilial("XXX")` ou `FwxFilial("XXX")` para filtro de filial
5. `ChangeQuery(cQuery)` antes de executar — garante portabilidade entre DBs
6. `MpSysOpenQuery(cQuery, cAlias)` para abrir
7. `While !(cAlias)->(Eof())` + `(cAlias)->(DbSkip())` para navegar
8. `(cAlias)->(DbCloseArea())` SEMPRE ao final — evita leak de alias
9. Listar campos explicitamente — NUNCA `SELECT *`

---

## 2. METODOS PROIBIDOS para queries SELECT

| Metodo | Status | Motivo |
|--------|--------|--------|
| `TCQuery` | PROIBIDO | Legado — deve ser migrado para BeginSQL |
| `DbUseArea(.T.,"TOPCONN",TcGenQry(,,cQuery),...)` | PROIBIDO | Legado — substituir por BeginSQL |
| `SELECT *` | PROIBIDO | Listar campos explicitamente |
| `MpSysOpenQuery` | LEGADO | Usar apenas para manutenção. Priorizar BeginSQL em código novo. |
| Alias hardcoded `"QRY"`, `"TRB"`, `"TMP"` | PROIBIDO | Risco de colisao. Usar GetNextAlias() |
| Nome de tabela hardcoded `"SA1010"` | PROIBIDO | Usar RetSqlName("SA1") |

---

## Nota sobre BeginSQL/EndSQL em codigo EXISTENTE

O padrao para codigo NOVO e BeginSQL/EndSQL (obrigatorio como padrao unico). 
consulte a skill `advpl-embedded-sql`.
Ela cobre sintaxe completa de macros (`%table:`, `%xfilial:`, `%notDel%`,
`%exp:`), declaracao de tipos de coluna.

---

## 3. POSICIONAMENTO DE REGISTROS (sem query)

### 3.1 Padrao: DbSelectArea + DbSetOrder + MsSeek

O padrao dominante e recomendado. Use para buscar
registros por chave de indice.

```advpl
// Posicionar em pedido de compra
DbSelectArea("SC7")
SC7->(DbSetOrder(1))  // C7_FILIAL+C7_NUM+C7_ITEM+C7_SEQUEN
If SC7->(MsSeek(xFilial("SC7") + cNumPed))
    While !SC7->(Eof()) .And. SC7->C7_FILIAL == xFilial("SC7") .And. SC7->C7_NUM == cNumPed
        If SC7->C7_QUJE == 0 .And. Empty(SC7->C7_CONTRA)
            lPossuiItem := .T.
            Exit
        EndIf
        SC7->(DbSkip())
    EndDo
EndIf
```

### 3.2 Cascata de Seeks (posicionamento entre tabelas relacionadas)

Padrao comum para navegar entre NF > Livro Fiscal > Itens > TES:

```advpl
DbSelectArea("SF2")
SF2->(DbSetOrder(1))
If SF2->(MsSeek(xFilial("SF2") + cNota + cSerie + cClieFor + cLoja))
    DbSelectArea("SF3")
    SF3->(DbSetOrder(4))
    If SF3->(MsSeek(xFilial("SF3") + cClieFor + cLoja + cNota + cSerie))
        DbSelectArea("SD2")
        SD2->(DbSetOrder(3))
        SD2->(MsSeek(xFilial("SD2") + cNota + cSerie + cClieFor + cLoja))
    EndIf
EndIf
```

### 3.3 Posicione() para leitura rapida de campo unico

Quando precisa apenas de UM campo, sem navegar na tabela:

```advpl
// Buscar CGC do fornecedor sem posicionar a workarea
cCgc := AllTrim(Posicione("SA2", 1, xFilial("SA2") + cFornece + cLoja, "A2_CGC"))

// Buscar nome do cliente
cNome := AllTrim(Posicione("SA1", 1, xFilial("SA1") + cCliente + cLoja, "A1_NOME"))
```

### 3.4 Quando usar query vs posicionamento direto

| Cenario | Abordagem |
|---------|-----------|
| Buscar 1 registro por chave de indice | DbSetOrder + MsSeek |
| Ler 1 campo de 1 registro | Posicione() |
| Listar registros com filtros complexos | MpSysOpenQuery |
| JOINs entre tabelas | MpSysOpenQuery |
| Agregacoes (SUM, COUNT, GROUP BY) | MpSysOpenQuery |
| Varrer registros sequencialmente por indice | DbSetOrder + While !Eof() |
| Valor escalar unico (MAX, COUNT) | MpSysExecScalar |

---

## 4. GRAVACAO DE DADOS

### 4.1 RecLock + MsUnLock (padrao dominante)

Sempre usar para operacoes diretas em registros.

```advpl
// UPDATE de registro existente (2o param = .F.)
DbSelectArea("SC9")
SC9->(DbGoto(nRecno))
If SC9->(!EOF())
    RecLock("SC9", .F.)
    SC9->C9_ZSTZION := '2'
    SC9->C9_DTSEP   := dDataBase
    SC9->(MsUnLock())
EndIf

// INSERT de registro novo (2o param = .T.)
DbSelectArea("ZZA")
RecLock("ZZA", .T.)
ZZA->ZZA_FILIAL := xFilial("ZZA")
ZZA->ZZA_CODIGO := cCodigo
ZZA->ZZA_DESCRI := cDescri
ZZA->(MsUnLock())
```

### 4.2 BEGIN/END TRANSACTION (operacoes multi-registro)

Use quando precisa garantir atomicidade de multiplos RecLock.

```advpl
BEGIN TRANSACTION
    For nI := 1 To Len(aRecnos)
        SC9->(DbGoto(aRecnos[nI]))
        If SC9->(!EOF())
            RecLock("SC9", .F.)
            SC9->C9_ZSTZION := cStatus
            SC9->(MsUnLock())
        EndIf
    Next nI
END TRANSACTION
```

### 4.3 MsExecAuto (execucao de rotinas padrao TOTVS)

Use para incluir/alterar/excluir via rotinas padrao do Protheus.
Padrao encapsulado em classe:

```advpl
// Variaveis Private OBRIGATORIAS
Private lAutoErrNoFile := .T.
Private lMsErroAuto    := .F.
Private lMsHelpAuto    := .T.

// Montar array de campos
Local aFina050 := {}
aAdd(aFina050, {"E2_PREFIXO", SE2->E2_PREFIXO, Nil})
aAdd(aFina050, {"E2_NUM",     SE2->E2_NUM,     Nil})
aAdd(aFina050, {"E2_PARCELA", SE2->E2_PARCELA, Nil})

// Executar rotina automatica (nOpc: 3=Incluir, 4=Alterar, 5=Excluir)
MsExecAuto({|x,y,z| FINA050(x,y,z)}, aFina050,, nOpc)

// SEMPRE verificar erro
If lMsErroAuto
    aLogAuto := GetAutoGRLog()
    cErro := ""
    For nI := 1 To Len(aLogAuto)
        cErro += aLogAuto[nI] + CRLF
    Next nI
    ConOut("Erro MsExecAuto: " + cErro)
EndIf
```

### 4.4 Metodos de gravacao NAO recomendados

| Metodo | Status |
|--------|--------|
| FwStdLock | Nao adotado — manter RecLock |
| FWMVCModel para gravacao | Apenas 3 ocorrencias — nao e padrao do time |

---

## 5. TABELAS E INDICES — Referencia rapida inline

Ao gerar codigo que envolva tabelas Protheus, consulte esta secao para chaves
de indice corretas. Para detalhes adicionais por modulo (campos complementares,
indices alternativos), leia o arquivo [tabelas-modulos.md](tabelas-modulos.md).

### Tabelas principais — chaves e indices mais usados

| Tabela | Descricao | Ordem 1 (chave primaria) | Ordens alternativas comuns |
|--------|-----------|--------------------------|---------------------------|
| **SF2** | Cab. NF Saida | F2_FILIAL+F2_DOC+F2_SERIE+F2_CLIENTE+F2_LOJA | — |
| **SA1** | Clientes | A1_FILIAL+A1_COD+A1_LOJA | 3: A1_FILIAL+A1_CGC |
| **SF1** | Cab. NF Entrada | F1_FILIAL+F1_DOC+F1_SERIE+F1_FORNECE+F1_LOJA+F1_TIPO | — |
| **SB1** | Produtos | B1_FILIAL+B1_COD | 2: B1_FILIAL+B1_DESC |
| **SD1** | Itens NF Entrada | D1_FILIAL+D1_DOC+D1_SERIE+D1_FORNECE+D1_LOJA+D1_COD+D1_ITEM | — |
| **SA2** | Fornecedores | A2_FILIAL+A2_COD+A2_LOJA | 3: A2_FILIAL+A2_CGC |
| **SD2** | Itens NF Saida | D2_FILIAL+D2_DOC+D2_SERIE+D2_CLIENTE+D2_LOJA+D2_COD+D2_ITEM | 3: D2_FILIAL+D2_DOC+D2_SERIE+D2_CLIENTE+D2_LOJA |
| **SM0** | Empresas/Filiais | M0_CODIGO+M0_CODFIL | — |
| **SF3** | Livros Fiscais | F3_FILIAL+F3_CFO+F3_ESTADO | 4: F3_FILIAL+F3_CLIEFOR+F3_LOJA+F3_NFISCAL+F3_SERIE |
| **SE1** | Contas a Receber | E1_FILIAL+E1_PREFIXO+E1_NUM+E1_PARCELA+E1_TIPO | — |
| **SC5** | Cab. Pedido Venda | C5_FILIAL+C5_NUM | — |
| **SE2** | Contas a Pagar | E2_FILIAL+E2_PREFIXO+E2_NUM+E2_PARCELA+E2_TIPO+E2_FORNECE+E2_LOJA | — |
| **SF4** | TES (Tipos E/S) | F4_FILIAL+F4_CODIGO | — |
| **SC6** | Itens Ped. Venda | C6_FILIAL+C6_NUM+C6_ITEM+C6_PRODUTO | — |
| **SC7** | Pedidos Compra | C7_FILIAL+C7_NUM+C7_ITEM+C7_SEQUEN | — |
| **SD3** | Mov. Internas Est. | D3_FILIAL+D3_DOC+D3_COD+D3_ITEM | — |
| **SC2** | Ordens Producao | C2_FILIAL+C2_NUM+C2_ITEM+C2_SEQUEN | — |
| **SE5** | Mov. Bancaria | E5_FILIAL+E5_DATA+E5_SEQ | — |
| **SB2** | Saldos Estoque | B2_FILIAL+B2_COD+B2_LOCAL | — |
| **SC9** | Liberacao Pedidos | C9_FILIAL+C9_PEDIDO+C9_ITEM | — |
| **SC1** | Solic. Compra | C1_FILIAL+C1_NUM+C1_ITEM | — |
| **CD2** | Doc. Carga (GFE) | Variavel por modulo | — |
| **DT6** | Romaneio (TMS) | Variavel por modulo | — |
| **SA4** | Transportadoras | A4_FILIAL+A4_COD | — |
| **SB5** | Dados Compl. Prod | B5_FILIAL+B5_COD | — |
| **DA3** | Desc. por Cliente | DA3_FILIAL+DA3_CODTAB+DA3_ITEM | — |

### Como usar esta tabela ao gerar codigo

Quando gerar um `DbSetOrder(n)`, SEMPRE comente a composicao do indice:

```advpl
DbSelectArea("SA1")
SA1->(DbSetOrder(1))  // A1_FILIAL+A1_COD+A1_LOJA
If SA1->(MsSeek(xFilial("SA1") + cCodCli + cLoja))
```

Quando gerar uma query com JOIN, use as chaves desta tabela para montar
as condicoes de JOIN corretamente. Se a tabela nao estiver listada aqui,
leia [tabelas-modulos.md](tabelas-modulos.md) para referencia completa.

---

## 6. FUNCOES ESSENCIAIS

### Funcoes de infraestrutura (usar SEMPRE)

| Funcao | Uso | Uso recomendado |
|--------|-----|---------------------|
| `xFilial("XXX")` | Filial corrente da tabela | 42.759 |
| `RetSqlName("XXX")` | Nome fisico da tabela no SQL | 7.050 |
| `GetNextAlias()` | Alias temporario unico | 3.366 |
| `ChangeQuery(cQuery)` | Adapta SQL entre DBs | 406 arquivos |
| `SuperGetMv("MV_XXX", .F., default)` | Ler parametro SX6 | 6.852 |

### Funcoes de posicionamento

| Funcao | Uso | Chamadas |
|--------|-----|----------|
| `DbSelectArea("XXX")` | Selecionar workarea | 28.350 |
| `DbSetOrder(n)` | Definir indice ativo | 26.684 |
| `DbSeek(cChave)` | Posicionar por chave (sem SoftSeek) | 17.243 |
| `MsSeek(cChave)` | Posicionar por chave (com SoftSeek, preserva filtros) | 10.873 |
| `DbSkip()` | Avancar registro | 12.152 |
| `Posicione(cAlias, nOrdem, cChave, cCampo)` | Ler campo unico direto | 4.371 |
| `DbGoTop()` | Ir ao primeiro registro | 3.301 |
| `RecLock(cAlias, lNovo)` | Bloquear para escrita | 6.566 |
| `MsUnLock()` | Liberar bloqueio | 6.337 |
| `DbCloseArea()` | Fechar alias | 5.593 |

### Funcoes de campo e registro

| Funcao | Uso | Chamadas |
|--------|-----|----------|
| `FieldPos(cField)` | Posicao ordinal do campo no registro | 9.767 |
| `ColumnPos(cField)` | Posicao da coluna na tabela | 4.265 |
| `GetArea()` | Salva estado da workarea (alias, ordem, recno) | 3.801 |
| `RestArea(aArea)` | Restaura estado salvo por GetArea | 3.552 |
| `GetNewPar(cParam, xDefault)` | Busca parametro (similar SuperGetMV) | 2.468 |
| `GetSX3Cache(cField, cProp)` | Propriedade do campo no SX3 com cache | 1.886 |
| `ValToSql(xVal)` | Converte valor para formato SQL | 1.311 |
| `FWxFilial(cAlias)` | xFilial versao nova (framework) | 1.302 |
| `AliasIndic(cAlias)` | Retorna alias do indice | 1.069 |
| `PesqPict(cAlias, cField)` | Pesquisa picture do campo no SX3 | 1.028 |
| `DbGoTo(nRecno)` | Posiciona no registro pelo RecNo | 999 |
| `RecNo()` | Retorna numero do registro atual | 979 |
| `FieldGet(nPos)` | Obtem valor de campo por posicao | 823 |
| `DbUseArea(lNova, cDriver, cFile, cAlias)` | Abre tabela diretamente | 811 |
| `GetMV(cParam)` | Busca parametro MV_ (legado) | 760 |
| `ExecBlock(cBlock, lPar, lSeq, aParams)` | Executa bloco de codigo por nome | 492 |
| `DbDelete()` | Marca registro como deletado | 263 |
| `FWGetArea()` | GetArea versao nova (framework) | 245 |
| `X3Picture(cField)` | Retorna picture do campo | 272 |
| `FieldPut(nPos, xVal)` | Define valor de campo por posicao | 193 |
| `FieldName(nPos)` | Retorna nome do campo por posicao | 165 |
| `FCount()` | Numero de campos da tabela | 153 |
| `FWRestArea(aArea)` | RestArea versao nova (framework) | 151 |
| `DbStruct()` | Retorna estrutura da tabela como array | 139 |
| `X3Titulo(cField)` | Retorna titulo do campo (SX3) | 134 |
| `CriaTrab(aCampos, lIndice)` | Cria tabela temporaria de trabalho | 132 |
| `FWGetSX5(cTabela, cChave)` | Busca descricao na SX5 | 135 |
| `ExistCpo(cAlias, xChave, nOrdem)` | Verifica existencia de registro | 110 |
| `GetSXENum(cAlias, cField)` | Gera numeracao automatica (SXE/SXF) | 108 |
| `IndexKey(nOrder)` | Retorna expressao da chave do indice | 154 |
| `IndexOrd()` | Retorna ordem do indice atual | 108 |
| `DbClearFilter()` | Remove filtro da tabela | 210 |
| `DbSetIndex(cFile)` | Define arquivo de indice | 88 |
| `DbCommit()` | Confirma alteracoes pendentes | 88 |
| `DbEval(bBlock, bFor, bWhile, nCount)` | Executa bloco para cada registro | 95 |
| `ConfirmSX8()` | Confirma numeracao do SX8 | 91 |
| `RetIndex(cAlias, nOrdem)` | Retorna arquivo de indice | 91 |
| `FWExecStatement(cSql, aParams)` | Executa SQL parametrizado | 97 |
| `FWTemporaryTable()` | Gerencia tabela temporaria | 90 |
| `FWSizeFilial()` | Retorna tamanho do campo filial | 93 |
| `FWTamSX3(cField)` | TamSX3 versao nova (framework) | 103 |
| `RecCount()` | Retorna total de registros | 89 |
| `Alias()` | Retorna alias da area atual | 198 |
| `OrdBagExt()` | Retorna extensao do arquivo de indice | 174 |
| `GdFieldGet(cField, lFmt)` | Obtem valor de campo em grid MsGetDados | 292 |
| `GdFieldPos(cField)` | Posicao de campo em grid MsGetDados | 146 |
| `CheckSX3(cField, xVal)` | Valida campo pelo dicionario | 152 |
| `OpenAlias(cAlias)` | Abre alias para consulta | 87 |
| `FWFormStruct(nTipo, cAlias)` | Monta estrutura de formulario MVC | 235 |

**Padrao GetArea/RestArea (obrigatorio):**
```advpl
Local aAreaSA1 := SA1->(GetArea())
Local aAreaSA2 := SA2->(GetArea())

// ... processamento que altera posicao das tabelas ...

SA2->(RestArea(aAreaSA2))
SA1->(RestArea(aAreaSA1))  // Restaurar na ordem inversa
```

### Preferencia: MsSeek vs DbSeek

Use `MsSeek` como padrao — preserva filtros e e mais seguro em contextos
com SetFilter ativo. Use `DbSeek` apenas quando precisar explicitamente
de SoftSeek `.F.`.

### FwxFilial vs xFilial

Ambos sao aceitos. `FwxFilial` e a versao mais moderna (framework), `xFilial`
e a classica. Use `FwxFilial` em codigo TLPP novo e `xFilial` em PRW existente.

---

## 7. FUNCOES UTILITARIAS DO TIME (reutilizar quando aplicavel)

O time organiza utilitarios em classes TLPP com namespace `custom.<org>.<modulo>.utils`.
Ao criar codigo novo para um projeto, verifique se ja existe uma classe utils no
diretorio do projeto antes de criar funcoes avulsas.

Para a lista completa de classes utils por projeto e exemplos de implementacao
(ExecAuto encapsulado, FwExecCachedQuery), leia [tabelas-modulos.md](tabelas-modulos.md).

---

## 8. ANTI-PATTERNS — O que NUNCA gerar

Todo codigo gerado DEVE evitar estes padroes. Ao detectar algum em codigo
existente, sinalizar ao usuario.

| # | Anti-pattern | Correto | Ocorrencias |
|---|-------------|---------|-------------|
| 8.1 | `SELECT *` | Listar campos explicitamente | 358 |
| 8.2 | SELECT sem `D_E_L_E_T_ = ' '` | SEMPRE incluir filtro D_E_L_E_T_ em toda query | 1.146 arqs |
| 8.3 | `D_E_L_E_T_ = ''` ou `<> '*'` | Sempre `D_E_L_E_T_ = ' '` (espaco) | Varios |
| 8.4 | Alias hardcoded `"QRY"`, `"TRB"` | `GetNextAlias()` | Varios |
| 8.5 | Alias aberto sem `DbCloseArea()` | SEMPRE fechar ao final | 123 arqs |
| 8.6 | Query sem `ChangeQuery()` | SEMPRE aplicar antes de executar | Varios |
| 8.7 | Seek sem `xFilial()` | SEMPRE incluir filial na chave | Varios |
| 8.8 | Usar campo sem checar `Eof()` | SEMPRE `If !(cAlias)->(Eof())` antes de ler | Varios |

### Exemplos ERRADO vs CORRETO dos mais criticos

```advpl
// 8.1 ERRADO: SELECT *
cQuery := " SELECT * FROM " + RetSqlName("SA1") + " SA1 "
// CORRETO:
cQuery := " SELECT SA1.A1_COD, SA1.A1_LOJA, SA1.A1_NOME FROM " + RetSqlName("SA1") + " SA1 "

// 8.2 ERRADO: Sem D_E_L_E_T_
cQuery += " WHERE A1_FILIAL = '" + xFilial("SA1") + "' "
// CORRETO:
cQuery += " WHERE SA1.D_E_L_E_T_ = ' ' AND SA1.A1_FILIAL = '" + xFilial("SA1") + "' "

// 8.3 ERRADO: Formato errado de D_E_L_E_T_
cQuery += " AND D_E_L_E_T_ = '' "      // vazio — ERRADO
cQuery += " AND D_E_L_E_T_ <> '*' "    // negacao — ERRADO
cQuery += " AND D_E_L_E_T_ = ' ' "     // espaco — CORRETO

// 8.5 ERRADO: Alias sem fechar — SEMPRE terminar com:
(cAlias)->(DbCloseArea())

// 8.7 ERRADO: Seek sem filial
DbSeek(cCodCli + cLoja)
// CORRETO:
MsSeek(xFilial("SA1") + cCodCli + cLoja)
```

---

## 9. DICIONARIOS DE DADOS

### 9.1 Consulta obrigatoria (Skills)

| Prioridade | Fonte | Uso |
|------------|-------|-----|
| **1** | `dicionario/{L}/{ALIAS}.json` | Metadados de tabela, campos, índices, gatilhos e relacionamentos |
| **2** | [references/dicionario-top200.md](references/dicionario-top200.md) | Referência rápida das tabelas mais usadas |
| **3** | [tabelas-modulos.md](tabelas-modulos.md) | Índices alternativos e mapeamento por módulo |

### 9.2 Tabelas SX no Protheus (runtime)

| Dicionario | Funcao | Como acessar no codigo |
|------------|--------|------------------------|
| SX1 | Perguntas | `Pergunte("MTXXX", .F.)` |
| SX2 | Cadastro de tabelas | `RetSqlName("XXX")` |
| SX3 | Campos | `GetSx3Cache()`, `TamSx3()` |
| SX5 | Tabelas genericas | `GetSx5("tabela", "chave")` |
| SX6 | Parametros MV_ | `SuperGetMv("MV_XXX", .F., default)` |
| SX7 | Gatilhos de campo | Configurar via SIGACFG, nao acessar direto |
| SIX | Indices | `IndRegua("XXX", nOrdem, ...)` |

### 9.3 Atualizar o dicionario local

Quando o usuario pedir para **atualizar/sincronizar o dicionario das Skills**, rode o script
[scripts/sync_dicionario.py](../scripts/sync_dicionario.py) apontando para a pasta do export.

**Arquivos na pasta de export:** `SX2.csv` (obrigatorio), `SX3.csv` ou `SX3.xlsx`, `SIX.csv`, `SX7.csv`, `SX9.csv`.

**Comando padrao (rebuild completo):**

```powershell
python d:\skills\protheus-data-model\scripts\sync_dicionario.py `
  --input-dir "C:\Dicionário" `
  --output-dir "d:\skills\protheus-data-model\dicionario" `
  --mode rebuild `
  --report "d:\skills\protheus-data-model\scripts\sync_report.json"
```

**Atualizacao parcial (merge):** use `--mode merge --aliases "U97,SRA"` quando o export trouxer so tabelas alteradas.

Detalhes, checklist e variacoes: [references/atualizar-dicionario.md](references/atualizar-dicionario.md).

---

## 10. SINTAXE ADVPL/TLPP — Erros comuns a evitar

| Correto (ADVPL/TLPP) | Errado |
|-----------------------|--------|
| `:=` para atribuicao | `=` tolerado mas `:=` e padrao |
| `.T.` e `.F.` | `True` / `False` |
| `NIL` | `null` / `None` |
| `nVar += 1` | `nVar++` NAO EXISTE em ADVPL |
| `aAdd(aArray, valor)` | `aArray.Add()` / `push()` |
| `AllTrim()` | `Trim()` existe mas AllTrim e padrao |

Notacao hungara obrigatoria: `c`=char, `n`=num, `d`=date, `l`=logic, `a`=array, `o`=obj, `b`=bloco.
Em TLPP, adicionar tipo: `Local cNome := "" As Character`.

Para metricas detalhadas e lista
de utilitarios por projeto, leia [tabelas-modulos.md](tabelas-modulos.md).