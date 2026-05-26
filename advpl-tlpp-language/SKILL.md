---
name: advpl-tlpp-language
description: >
  Referencia de funcoes nativas da linguagem ADVPL/TLPP e xBase.
  Use esta skill APENAS quando: (1) o usuario pedir explicitamente referencia
  de uma funcao nativa especifica (ex: "como usar AScan?", "qual a sintaxe do AEval?"),
  ou (2) a funcao necessaria for obscura/pouco conhecida e nao estiver no CLAUDE.md.
  NAO ativar automaticamente para todo codigo ADVPL — as regras essenciais ja estao
  no CLAUDE.md (Local, hungaro, GetArea/RestArea, xFilial, Begin Sequence).
  Funcoes comuns (AllTrim, SubStr, Val, IIf, Empty, Date, Len, AAdd) nao requerem
  esta skill — use diretamente.
---

# ADVPL/TLPP — Referência de Funções da Linguagem

Referência prescritiva das funções nativas da linguagem ADVPL/TLPP, com padrões e boas práticas para desenvolvimento Protheus. Ordenada por frequência de uso e relevância técnica.

## 0. METODOLOGIA DE USO (Para o Agente)

Como desenvolvedor sênior, você deve utilizar esta skill como seu "dicionário de comandos" base. Antes de implementar qualquer lógica:
1. **Verifique a Função Nativa**: Sempre prefira funções nativas otimizadas listadas aqui em vez de recriar lógicas complexas.
2. **Respeite os Padrões**: Use os exemplos de código desta skill como template para garantir conformidade com a Notação Húngara e Declaração Local.
3. **Pule para Skills Especializadas**: Se a tarefa envolver Banco de Dados, REST, MVC ou Jobs, use as funções básicas daqui e consulte as skills específicas para a arquitetura completa.

---

## 1. REGRAS CRÍTICAS DE PROJETO (MANDATÓRIAS)

| Regra | Descrição | Exemplo |
|-------|-----------|---------|
| **Declaração Local** | TODAS as variáveis devem ser declaradas como `Local` no topo da função/método. | `Local nTotal := 0` |
| **Notação Húngara** | Prefixos obrigatórios baseados no tipo (c, n, d, l, a, o, b). | `aDados`, `cNome` |
| **Tratamento de Erros** | Use `Begin Sequence` / `End Sequence` para lógicas de negócio. | Veja seção de Lógica. |
| **Acesso a Dados** | Use `BeginSQL/EndSQL` para SELECT e `FWGetArea` para salvar contexto. | Consulte `protheus-data-model`. |
| **Namespaces** | Padrão `custom.<agrupador>.<servico>` para novos fontes `.tlpp`. | `Namespace custom.fin.integration` |

## 1. STRINGS — Manipulacao de Texto

### Funcoes de limpeza e padding

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| AllTrim | `AllTrim(cText) => character` | Remove espacos a esquerda e direita | 42.177 |
| RTrim | `RTrim(cText) => character` | Remove espacos a direita | 760 |
| LTrim | `LTrim(cText) => character` | Remove espacos a esquerda | 156 |
| Trim | `Trim(cText) => character` | Alias de RTrim | 611 |
| PadR | `PadR(xExp, nLen, [cFill]) => character` | Preenche com caractere a direita | 3.548 |
| PadL | `PadL(xExp, nLen, [cFill]) => character` | Preenche com caractere a esquerda | 328 |
| PadC | `PadC(xExp, nLen, [cFill]) => character` | Centraliza com preenchimento | 147 |
| Space | `Space(nCount) => character` | String de N espacos | 5.264 |
| Replicate | `Replicate(cStr, nTimes) => character` | Repete string N vezes | 1.021 |

**Padrao recomendado:** Usar `AllTrim` como padrao para limpar campos do banco.
`PadR` e obrigatorio ao montar chaves de busca concatenadas.

```advpl
// Padrao: PadR para montar chave de seek
cChave := xFilial("SA1") + PadR(cCodigo, TamSX3("A1_COD")[1]) + PadR(cLoja, TamSX3("A1_LOJA")[1])
SA1->(MsSeek(cChave))

// Inicializar variavel de campo com tamanho correto
Local cDoc := Space(TamSX3("F1_DOC")[1])
```

### Funcoes de extracao e busca

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| SubStr | `SubStr(cText, nStart, [nLen]) => character` | Extrai parte da string | 18.554 |
| Subs | `Subs(cText, nStart, [nLen]) => character` | Alias abreviado de SubStr | 713 |
| Left | `Left(cText, nLen) => character` | N caracteres da esquerda | 776 |
| Right | `Right(cText, nLen) => character` | N caracteres da direita | 276 |
| Rat | `Rat(cSearch, cText) => numeric` | Posicao da ultima ocorrencia | 370 |

### Funcoes de transformacao

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| Upper | `Upper(cText) => character` | Converte para maiusculas | 3.818 |
| Lower | `Lower(cText) => character` | Converte para minusculas | 288 |
| Capital | `Capital(cText) => character` | Primeira letra maiuscula | 127 |
| StrTran | `StrTran(cStr, cSearch, [cReplace], [nStart], [nCount]) => character` | Substitui substrings | 4.123 |
| Transform | `Transform(xValue, cPicture) => character` | Formata com mascara | 5.622 |
| Chr | `Chr(nCode) => character` | ASCII para caractere | 3.071 |
| Asc | `Asc(cChar) => numeric` | Caractere para ASCII | 206 |
| OemToAnsi | `OemToAnsi(cText) => character` | Converte charset OEM para ANSI | 723 |

**Constantes comuns com Chr:**
```advpl
CRLF := Chr(13) + Chr(10)  // Quebra de linha Windows
cTab := Chr(9)              // Tabulacao
```

---

## 2. CONVERSAO DE TIPOS

### String <-> Numerico

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| Val | `Val(cString) => numeric` | String para numerico | 8.062 |
| Str | `Str(nNum, [nLen], [nDec]) => character` | Numero para string | 4.265 |
| StrZero | `StrZero(nVal, nLen, [nDec]) => character` | Numero para string com zeros a esquerda | 3.624 |
| cValToChar | `cValToChar(xParam) => character` | Qualquer tipo para string | 3.838 |
| AllToChar | `AllToChar(xParam) => character` | Qualquer tipo para string (alternativa) | 211 |

**Padrao recomendado:**
```advpl
// Para exibir/concatenar: cValToChar
ConOut("Total: " + cValToChar(nTotal))

// Para formatar numero com tamanho fixo: Str
cValor := Str(nPreco, 15, 2)

// Para codigos sequenciais: StrZero
cItem := StrZero(nItem, 4)  // "0001", "0002", ...
```

### String <-> Data

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| DToS | `DToS(dDate) => character` | Data para "AAAAMMDD" | 3.537 |
| SToD | `SToD(cDate) => date` | "AAAAMMDD" para data | 1.225 |
| DToC | `DToC(dDate) => character` | Data para formato local "DD/MM/AAAA" | 835 |
| CToD | `CToD(cDate) => date` | Formato local para data | 1.464 |

**Padrao obrigatorio:** Sempre usar `DToS` ao concatenar datas em chaves de busca ou queries SQL:
```advpl
cQuery += " AND E1_VENCTO >= '" + DToS(dDataDe) + "' "
```

### Verificacao de tipo

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| Type | `Type(cExpr) => character` | Tipo de expressao (string com nome) | 8.153 |
| ValType | `ValType(xVal) => character` | Tipo de valor ja avaliado | 3.523 |
| Empty | `Empty(xExp) => logical` | Verifica se vazio/nulo/zero/falso | 40.012 |
| IsNull | `IsNull(xVal) => logical` | Verifica se e NIL | 111 |
| IsAlpha | `IsAlpha(cText) => logical` | Verifica se e alfabetico | 231 |
| IsDigit | `IsDigit(cText) => logical` | Verifica se e numerico | 123 |

**Diferenca critica Type vs ValType:**
```advpl
// Type: recebe STRING com o nome da variavel (avalia se existe)
If Type("cMeuVar") != "U"  // "U" = undefined (nao existe)
    // variavel existe
EndIf

// ValType: recebe o VALOR diretamente (variavel ja deve existir)
If ValType(xParam) == "C"  // "C"=char, "N"=num, "D"=date, "L"=logic, "A"=array, "O"=obj
    // e string
EndIf
```

---

## 3. ARRAYS

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| AAdd | `AAdd(aDest, xExpr) => variant` | Adiciona elemento ao final | 57.630 |
| AScan | `AScan(aArr, xExpr, [nStart], [nCount]) => numeric` | Busca elemento, retorna posicao | 5.378 |
| ATail | `ATail(aArr) => variant` | Retorna ultimo elemento | 5.087 |
| ASize | `ASize(aArr, nNewSize) => NIL` | Redimensiona array | 1.899 |
| AClone | `AClone(aArr) => array` | Cria copia do array | 763 |
| AEval | `AEval(aArr, bBlock, [nStart], [nCount]) => NIL` | Executa bloco para cada elemento | 540 |
| ASort | `ASort(aArr, [nStart], [nCount], [bOrder]) => array` | Ordena array | 387 |
| ADel | `ADel(aArr, nPos) => NIL` | Remove elemento (nao redimensiona) | 88 |
| AFill | `AFill(aArr, xVal, [nStart], [nCount]) => NIL` | Preenche array com valor | 84 |
| Len | `Len(xVal) => numeric` | Tamanho de string ou array | 27.660 |

**Padrao para remover elemento corretamente:**
```advpl
// ADel apenas marca como NIL — precisa redimensionar depois
ADel(aArr, nPos)
ASize(aArr, Len(aArr) - 1)
```

**Padrao AScan com bloco de codigo:**
```advpl
// Buscar em array bidimensional
nPos := AScan(aCampos, {|x| AllTrim(x[1]) == "D1_COD"})
If nPos > 0
    cValor := aCampos[nPos][2]
EndIf
```

---

## 4. DATA E HORA

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| Date | `Date() => date` | Data atual do sistema | 1.177 |
| Year | `Year(dDate) => numeric` | Extrai ano | 523 |
| Month | `Month(dDate) => numeric` | Extrai mes | 487 |
| Day | `Day(dDate) => numeric` | Extrai dia | 408 |
| Time | `Time() => character` | Hora atual "HH:MM:SS" | 774 |
| Seconds | `Seconds() => numeric` | Segundos desde meia-noite | 110 |

---

## 5. MATEMATICA

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| Round | `Round(nVal, nDec) => numeric` | Arredonda | 1.526 |
| NoRound | `NoRound(nVal, nDec) => numeric` | Trunca sem arredondar | 308 |
| Abs | `Abs(nVal) => numeric` | Valor absoluto | 199 |
| Max | `Max(nVal1, nVal2) => numeric` | Maior valor | 497 |
| Min | `Min(nVal1, nVal2) => numeric` | Menor valor | 434 |
| Int | `Int(nVal) => numeric` | Parte inteira | 151 |
| Mod | `Mod(nVal, nDiv) => numeric` | Resto da divisao | 210 |
| Ceiling | `Ceiling(nVal) => numeric` | Arredonda para cima | 103 |

**Atencao com NoRound vs Round:**
```advpl
// NoRound TRUNCA, nao arredonda — usar para calculos fiscais quando exigido
NoRound(10.456, 2)  // => 10.45
Round(10.456, 2)     // => 10.46
```

---

## 6. LOGICA E CONTROLE

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| IIf | `IIf(lCond, xTrue, xFalse) => variant` | Ternario inline | 29.874 |
| ExistBlock | `ExistBlock(cBlock) => logical` | Verifica se bloco de codigo existe | 739 |
| Eval | `Eval(bBlock, [...]) => variant` | Executa bloco de codigo | 432 |
| ErrorBlock | `ErrorBlock([bNewBlock]) => codeblock` | Define/obtem tratamento de erro | 136 |
| PCount | `PCount() => numeric` | Numero de parametros recebidos | 267 |
| Sleep | `Sleep(nMs) => NIL` | Pausa execucao em milissegundos | 145 |
| Coalesce | `Coalesce(x1, x2, ...) => variant` | Retorna primeiro valor nao nulo | 162 |

**Padrao IIf (recomendado):**
```advpl
cTipo := IIf(Len(cCGC) == 11, "F", "J")  // Pessoa Fisica ou Juridica
```

---

## 7. ARQUIVOS

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| File | `File(cPath) => logical` | Verifica se arquivo existe | 767 |
| FCreate | `FCreate(cPath) => numeric` | Cria arquivo, retorna handle | 93 |
| FWrite | `FWrite(nHandle, cData) => numeric` | Escreve em arquivo | 174 |
| FSeek | `FSeek(nHandle, nOffset, [nOrigin]) => numeric` | Posiciona ponteiro | 103 |
| FClose | `FClose(nHandle) => logical` | Fecha arquivo | 128 |
| FErase | `FErase(cPath) => numeric` | Apaga arquivo | 424 |
| FError | `FError() => numeric` | Ultimo codigo de erro | 88 |
| MemoWrite | `MemoWrite(cPath, cContent) => logical` | Grava texto em arquivo | 144 |
| MemoLine | `MemoLine(cText, nWidth, nLine) => character` | Retorna linha de texto memo | 122 |

**Padrao para escrita em arquivo:**
```advpl
nHandle := FCreate(cPath)
If nHandle >= 0
    FWrite(nHandle, cConteudo)
    FClose(nHandle)
Else
    ConOut("Erro ao criar arquivo: " + cValToChar(FError()))
EndIf
```

---

## 8. TOKENIZACAO

| Funcao | Assinatura | Descricao | Chamadas |
|--------|-----------|-----------|----------|
| StrToKArr | `StrToKArr(cStr, cSep) => array` | Quebra string em array pelo separador | 311 |
| StrToKArr2 | `StrToKArr2(cStr, cSep) => array` | Versao 2, trata separadores consecutivos | 221 |

```advpl
// Quebrar lista separada por virgula
aItens := StrToKArr("001,002,003", ",")
// aItens = {"001", "002", "003"}
```

---

## 9. LOG E DIAGNOSTICO

### Funcoes de output e log

| Funcao | Assinatura | Descricao | Uso |
|--------|-----------|-----------|-----|
| ConOut | `ConOut(cMsg) => NIL` | Escreve no console.log do AppServer | Debug temporario |
| FwLogMsg | `FwLogMsg(cSeverity, cTransId, cSource, cFunction, cOper, cCode, cMsg, nP1, nP2, aExtras) => NIL` | Log estruturado com severidade | Log permanente |

**ConOut — debug temporario (remover antes de deploy):**
```advpl
ConOut(">>> DEBUG: cStatus = " + cValToChar(cStatus))
ConOut(">>> DEBUG: nRecno = " + cValToChar(nRecno))
```

**FwLogMsg — log permanente e estruturado:**
```advpl
// Severidades: "INFO", "WARNING", "ERROR"
FwLogMsg("INFO", /*cTransId*/, "U_MEUFUNC", FunName(), "", "01", ;
    "Processamento concluido. Total: " + cValToChar(nTotal), 0, 0, {})

FwLogMsg("ERROR", /*cTransId*/, "U_MEUFUNC", FunName(), "MATA410", "01", ;
    "Erro ao gerar pedido: " + cErroMsg, 0, 0, GetAutoGrLog())
```

Para guia completo de debugging e diagnóstico, consulte a skill `advpl-debugging`.
Para simulação lógica e análise estática, utilize `teste-de-mesa`.

---

## 10. FRAMEWORK — Acesso a Dados

> [!IMPORTANT]
> O padrão obrigatório para consultas no projeto é o uso de `BeginSQL/EndSQL`. Para detalhes sobre modelos de dados, índices e performance, consulte a skill `protheus-data-model`.

### Queries

| Funcao | Assinatura | Descricao |
|--------|-----------|-----------|
| MpSysOpenQuery | `MpSysOpenQuery(cQuery, cAlias) => NIL` | Abre query SQL em alias — UNICO padrao para SELECT |
| MpSysExecScalar | `MpSysExecScalar(cQuery) => cValor` | Retorna valor escalar (MAX, COUNT, SUM) |
| TCSqlExec | `TCSqlExec(cQuery) => nRet` | Executa DML (INSERT/UPDATE/DELETE). 0=OK |
| TCSqlToArr | `TCSqlToArr(cQuery) => aResult` | Retorna resultado como array bidimensional |
| FwPreparedStatement | Classe | Query parametrizada anti-SQL injection |
| RetSqlName | `RetSqlName(cTabela) => cNomeFisico` | Nome fisico da tabela no banco |
| GetNextAlias | `GetNextAlias() => cAlias` | Gera alias unico para query |
| ChangeQuery | `ChangeQuery(cQuery) => cQuery` | Ajusta query para portabilidade SQL |

```advpl
// Padrao MpSysOpenQuery
Local cAlias := GetNextAlias()
Local cQuery := "SELECT A1_COD, A1_NOME FROM " + RetSqlName("SA1")
cQuery += " WHERE A1_FILIAL = '" + xFilial("SA1") + "'"
cQuery += " AND D_E_L_E_T_ = ' '"
cQuery := ChangeQuery(cQuery)
MpSysOpenQuery(cQuery, cAlias)
While !(cAlias)->(Eof())
    // processar
    (cAlias)->(DbSkip())
EndDo
(cAlias)->(DbCloseArea())
```

```advpl
// FwPreparedStatement — anti SQL injection
Local oStmt := FwPreparedStatement():New()
oStmt:SetQuery("SELECT A1_COD, A1_NOME FROM " + RetSqlName("SA1"))
oStmt:And("A1_FILIAL = ?", xFilial("SA1"))
oStmt:And("A1_CGC = ?", cCGC)
oStmt:And("D_E_L_E_T_ = ' '")
Local cQuery := oStmt:GetFixQuery()
FreeObj(oStmt)
```

### Posicionamento Direto

| Funcao | Assinatura | Descricao |
|--------|-----------|-----------|
| DbSelectArea | `DbSelectArea(cAlias) => NIL` | Seleciona area de trabalho |
| DbSetOrder | `DbSetOrder(nOrdem) => NIL` | Define indice ativo |
| MsSeek | `MsSeek(xChave, lSoftSeek, cAlias) => lFound` | Posiciona + retorna .T./.F. (preferido) |
| DbSeek | `DbSeek(xChave, lSoftSeek) => lFound` | Posiciona no indice |
| Posicione | `Posicione(cAlias, nOrdem, xChave, cCampo) => xValor` | Retorna campo sem mudar area |
| DbGoTop | `DbGoTop() => NIL` | Vai para primeiro registro |
| DbSkip | `DbSkip(nRegs) => NIL` | Avanca registros |
| RecLock | `RecLock(cAlias, lInclui) => lOk` | Trava registro para edicao |
| MsUnLock | `MsUnLock(cAlias) => NIL` | Destrava registro |
| xFilial | `xFilial(cAlias) => cFilial` | Retorna filial da tabela |
| FwxFilial | `FwxFilial(cAlias, cFilial) => cFilial` | Filial com empresa especifica |

```advpl
// MsSeek — preferido sobre DbSeek (posiciona E retorna)
DbSelectArea("SA1")
DbSetOrder(1) // A1_FILIAL+A1_COD+A1_LOJA
If MsSeek(xFilial("SA1") + cCodCli + cLoja)
    cNome := SA1->A1_NOME
EndIf
```

```advpl
// Posicione — retorna campo sem mudar area atual
cNomeCli := Posicione("SA1", 1, xFilial("SA1") + cCodCli + cLoja, "A1_NOME")
```

### GetArea/RestArea

| Funcao | Assinatura | Descricao |
|--------|-----------|-----------|
| GetArea | `GetArea(cAlias) => aArea` | Salva estado da area (legado) |
| RestArea | `RestArea(aArea) => NIL` | Restaura estado da area (legado) |
| FWGetArea | `FWGetArea(cAlias) => aArea` | Salva estado — versao moderna |
| FWRestArea | `FWRestArea(aArea) => NIL` | Restaura estado — versao moderna |

```advpl
// SEMPRE em pares — usar FW* de preferencia
Local aAreaSA1 := FWGetArea("SA1")
// ... operacoes em SA1 ...
FWRestArea(aAreaSA1)
```

### Lock e Concorrencia

| Funcao | Assinatura | Descricao |
|--------|-----------|-----------|
| LockByName | `LockByName(cNomeLock, lAguardar) => lOk` | Lock nomeado para concorrencia |
| UnLockByName | `UnLockByName(cNomeLock) => NIL` | Libera lock nomeado |

```advpl
// Lock nomeado — SEMPRE com empresa+filial no nome
Local cLock := "MYJOB_" + cEmpAnt + cFilAnt
If LockByName(cLock, .F.) // .F. = nao aguardar
    // processar
    UnLockByName(cLock)
Else
    ConOut("Job ja em execucao")
EndIf
```

---

## 11. FRAMEWORK — REST e JSON

> [!TIP]
> Para implementação completa de endpoints REST modernos (TLPP) ou consumo de APIs externas (FWRest), consulte a skill `protheus-rest`. Para estruturação de classes de negócio, use `tlpp-classes`.

### REST Server (TLPP Anotacoes)

| Funcao | Assinatura | Descricao |
|--------|-----------|-----------|
| SetStatusCode | `oRest:SetStatusCode(nCode) => NIL` | Define HTTP status (200, 400, 404, 500) |
| SetResponse | `oRest:SetResponse(cJson) => NIL` | Define corpo da resposta |
| GetBody | `oRest:GetBody() => cJson` | Le corpo da requisicao |
| GetQueryString | `oRest:GetQueryString() => cParams` | Parametros de URL |
| GetPathParam | `GetPathParam(cNome) => cValor` | Parametro de rota |

```tlpp
@Get("/api/v1/clientes")
Method GetClientes() Class ClienteAPI
    // CRITICO: SEMPRE Return .T. — SetStatusCode controla HTTP status
    Self:oRest:SetStatusCode(200)
    Self:oRest:SetResponse(cJson)
Return .T.
```

### REST Client

| Funcao | Assinatura | Descricao |
|--------|-----------|-----------|
| FWRest:New | `FWRest():New(cUrl) => oRest` | Cria cliente REST |
| :SetPath | `oRest:SetPath(cPath) => NIL` | Define endpoint |
| :Get | `oRest:Get() => lOk` | Executa GET |
| :Post | `oRest:Post(cBody) => lOk` | Executa POST |
| :GetResult | `oRest:GetResult() => cBody` | Le resposta |

```advpl
Local oRest := FWRest():New(SuperGetMV("MV_XURL"))
oRest:SetPath("/api/v1/clientes")
If oRest:Get()
    cResp := oRest:GetResult()
Else
    ConOut("Erro: " + oRest:GetLastError())
EndIf
FreeObj(oRest)
```

### JSON

| Funcao | Assinatura | Descricao |
|--------|-----------|-----------|
| JsonObject:New | `JsonObject():New() => oJson` | Cria objeto JSON |
| :FromJson | `oJson:FromJson(cJson) => cErro ou NIL` | Parse JSON (NIL=ok, string=erro) |
| :ToJson | `oJson:ToJson() => cJson` | Serializa para string |
| :Set | `oJson[cChave] := xValor` | Define propriedade |
| FWJsonSerialize | `FWJsonSerialize(xValor) => cJson` | Serializa qualquer tipo |

```advpl
Local oJson := JsonObject():New()
Local xRet := oJson:FromJson(cBody)
If ValType(xRet) == "C" // String = erro de parse
    ConOut("Erro JSON: " + xRet)
Else
    cNome := oJson["nome"]
EndIf
FreeObj(oJson)
```

---

## 12. FRAMEWORK — MVC

> [!IMPORTANT]
> O framework MVC Protheus possui padrões específicos de Model, View e Menu. Para criar ou manter rotinas MVC, consulte obrigatoriamente a skill `protheus-mvc`.

| Funcao | Assinatura | Descricao |
|--------|-----------|-----------|
| FWLoadModel | `FWLoadModel(cFonte) => oModel` | Carrega model de rotina existente |
| FWExecView | `FWExecView(cTitulo, cFonte, nOper, ...) => nRet` | Abre tela MVC |
| FwBuildFeature | `FwBuildFeature(nTipo, cConteudo) => aFeature` | Configura campo virtual |
| MPFormModel | `MPFormModel():New(cId, bPre, bOk, bCommit, bCancel)` | Cria model |
| FWFormView | `FWFormView():New() => oView` | Cria view |
| FWMBrowse | `FWMBrowse():New() => oBrowse` | Cria browse MVC |
| SetPrimaryKey | `oStruct:SetPrimaryKey(aCampos)` | Define chave do model |

```advpl
// Abrir MVC programaticamente
Local oModel := FWLoadModel("MATA010")
oModel:SetOperation(MODEL_OPERATION_INSERT)
oModel:Activate()
oModel:SetValue("SA1MASTER", "A1_COD", "000001")
If oModel:VldData()
    oModel:CommitData()
EndIf
oModel:DeActivate()
FreeObj(oModel)
```

---

## 13. FRAMEWORK — Utilitários

> [!NOTE]
> Para criação de telas, diálogos e componentes visuais não-MVC, consulte a skill `protheus-screens`. Para processos em background e agendamentos, consulte `protheus-jobs`. Para relatórios e impressões, utilize `protheus-reports`.

| Funcao | Assinatura | Descricao |
|--------|-----------|-----------|
| SuperGetMV | `SuperGetMV(cParam, lHelp, xDefault) => xValor` | Le parametro SX6 (com cache) |
| GetMV | `GetMV(cParam) => xValor` | Le parametro SX6 (sem cache) |
| PutMV | `PutMV(cParam, xValor) => NIL` | Grava parametro SX6 |
| Pergunte | `Pergunte(cGrupo, lMostra) => lOk` | Abre parametros SX1 |
| ParamBox | `ParamBox(aParams, cTitulo, ...) => lOk` | Dialogo de parametros moderno |
| MsExecAuto | `MsExecAuto({|x,y| ROTINA(x,y)}, cAlias, nOper, aFields)` | Execucao automatica de rotina |
| ExecBlock | `ExecBlock(cBloco, lParams, lResult, ...) => xRet` | Executa ponto de entrada |
| RpcSetEnv | `RpcSetEnv(cEmp, cFil) => NIL` | Abre ambiente em Job |
| RpcClearEnv | `RpcClearEnv() => NIL` | Fecha ambiente em Job |
| Sleep | `Sleep(nMs) => NIL` | Pausa em milissegundos |
| TSleep | `TSleep(nMs) => NIL` | Pausa sem bloquear thread |
| FWUuidV4 | `FWUuidV4() => cUuid` | Gera UUID v4 |
| FWTimeStamp | `FWTimeStamp() => cTimestamp` | Timestamp formatado |
| FwNoAccent | `FwNoAccent(cTexto) => cTexto` | Remove acentos |
| FWCodFil | `FWCodFil() => cFilial` | Filial atual |
| GetRemoteType | `GetRemoteType() => nTipo` | -1=Job, 1=SmartClient |

```advpl
// Detectar se esta em Job ou SmartClient
If GetRemoteType() == -1
    FwLogMsg("INFO", "", "MYJOB", FunName(), "", "01", "Executando como Job", 0, 0, {})
Else
    MsgInfo("Executando com interface")
EndIf
```

---

## 14. FRAMEWORK — Dicionario

| Funcao | Assinatura | Descricao |
|--------|-----------|-----------|
| GetSx3Cache | `GetSx3Cache(cCampo, cProp) => xValor` | Le propriedade SX3 com cache |
| TamSx3 | `TamSx3(cCampo) => aInfo` | Retorna {nTam, nDec} do campo |
| X3Descric | `X3Descric() => cDescricao` | Descricao do campo (SX3 posicionado) |
| X3Picture | `X3Picture() => cPicture` | Picture do campo |
| X3Tipo | `X3Tipo() => cTipo` | Tipo do campo (C/N/D/L/M) |
| X3CBox | `X3CBox() => cComboBox` | Opcoes do combo (campo tipo C) |

```advpl
// Ler tamanho e decimal de um campo
Local aTam := TamSx3("A1_NOME")  // retorna {40, 0}
Local nTam := aTam[1]             // 40
Local nDec := aTam[2]             // 0
```

---

## 15. FRAMEWORK — Crypto e Encoding

| Funcao | Assinatura | Descricao |
|--------|-----------|-----------|
| SHA256 | `SHA256(cTexto) => cHash` | Hash SHA-256 |
| HMACSHA256 | `HMACSHA256(cTexto, cChave) => cHash` | HMAC com SHA-256 |
| Encode64 | `Encode64(cTexto) => cBase64` | Codifica Base64 |
| Decode64 | `Decode64(cBase64) => cTexto` | Decodifica Base64 |
| EncodeUTF8 | `EncodeUTF8(cTexto) => cUtf8` | Converte para UTF-8 |
| DecodeUTF8 | `DecodeUTF8(cUtf8) => cTexto` | Converte de UTF-8 |

```advpl
// Autenticacao Bearer com Base64
Local cAuth := "Basic " + Encode64(cUser + ":" + cPass)
```

> Para referencia expandida com 300+ funcoes, consulte:
> `references/native-functions-extended.md`

---

## 17. ANTI-PATTERNS — O que NUNCA gerar

| Errado | Correto | Motivo |
|--------|---------|--------|
| `nVar++` | `nVar += 1` ou `nVar := nVar + 1` | Operador `++` NAO existe em ADVPL |
| `True` / `False` | `.T.` / `.F.` | Booleanos ADVPL usam ponto |
| `null` / `None` | `NIL` | Nulo em ADVPL e NIL |
| `aArray.Add(x)` | `AAdd(aArray, x)` | ADVPL usa funcoes, nao metodos de array |
| `Trim(cTexto)` sem contexto | `AllTrim(cTexto)` | AllTrim e o padrao recomendado |
| Concatenar data sem DToS | `DToS(dData)` para chaves | Data deve ser string AAAAMMDD em queries |
| `If Type("x") == "C"` | `If ValType(x) == "C"` | Type recebe string, ValType recebe valor |
| `nVal++` | `nVal += 1` | O operador de incremento não existe |

Para revisões automáticas de segurança e performance, utilize a skill `code-review`.

---

## 18. NOTACAO HUNGARA (obrigatoria)

| Prefixo | Tipo | Exemplo |
|---------|------|---------|
| `c` | Character | `cNome`, `cCodigo` |
| `n` | Numeric | `nTotal`, `nQtd` |
| `d` | Date | `dDataIni`, `dVencto` |
| `l` | Logical | `lOk`, `lExiste` |
| `a` | Array | `aItens`, `aCampos` |
| `o` | Object | `oModel`, `oJson` |
| `b` | CodeBlock | `bBloco`, `bValid` |
| `x` | Indeterminado | `xParam`, `xRetorno` |

Em TLPP, adicionar tipo apos declaracao:
```tlpp
Local cNome := "" As Character
Local nTotal := 0 As Numeric
Local aItens := {} As Array
```
