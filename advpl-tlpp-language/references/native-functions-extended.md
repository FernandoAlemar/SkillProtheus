# Referencia Expandida de Funcoes ADVPL/TLPP

> 250+ funcoes documentadas. Para referencia rapida das top 100 com exemplos, consulte SKILL.md.
> Formato: Funcao | Assinatura | Descricao | Armadilha

---

## 1. String — Manipulacao de Texto

| Funcao | Assinatura | Descricao | Armadilha |
|--------|-----------|-----------|-----------|
| AllTrim | `AllTrim(cText) => C` | Remove espacos esquerda e direita | Use em vez de Trim |
| RTrim | `RTrim(cText) => C` | Remove espacos a direita | Alias: Trim |
| LTrim | `LTrim(cText) => C` | Remove espacos a esquerda | Menos usado que AllTrim |
| PadR | `PadR(cText, nTam, cFill) => C` | Preenche a direita ate nTam | cFill default = espaco |
| PadL | `PadL(cText, nTam, cFill) => C` | Preenche a esquerda ate nTam | Para numeros como string |
| PadC | `PadC(cText, nTam, cFill) => C` | Centraliza em nTam | Arredonda p/ esquerda |
| SubStr | `SubStr(cText, nInicio, nLen) => C` | Extrai substring | nInicio comeca em 1, nao 0 |
| Left | `Left(cText, nLen) => C` | Primeiros nLen caracteres | Equivale SubStr(c,1,n) |
| Right | `Right(cText, nLen) => C` | Ultimos nLen caracteres | — |
| At | `At(cBusca, cTexto) => N` | Posicao da primeira ocorrencia | Retorna 0 se nao encontrar |
| Rat | `Rat(cBusca, cTexto) => N` | Posicao da ultima ocorrencia | R = Reverse |
| Len | `Len(cText) => N` | Comprimento da string | Tambem funciona para arrays |
| Space | `Space(nTam) => C` | String de espacos | Para inicializar variaveis char |
| Replicate | `Replicate(cChar, nVezes) => C` | Repete caractere | Util para separadores |
| Upper | `Upper(cText) => C` | Converte para maiusculo | — |
| Lower | `Lower(cText) => C` | Converte para minusculo | — |
| StrTran | `StrTran(cOrigem, cDe, cPara) => C` | Substitui todas ocorrencias | Vazio em cPara = remove |
| Transform | `Transform(xValor, cPicture) => C` | Formata valor com picture | Picture Protheus: @E, @R |
| Chr | `Chr(nASCII) => C` | ASCII para caractere | Chr(13)+Chr(10) = CRLF |
| Asc | `Asc(cChar) => N` | Caractere para ASCII | So le primeiro char |
| Stuff | `Stuff(cText, nPos, nDel, cInsert) => C` | Insere/substitui em posicao | Combina delete + insert |
| StrToKArr | `StrToKArr(cText, cSep) => A` | Split string por separador | Retorna array |
| StrToKArr2 | `StrToKArr2(cText, cSep) => A` | Split preservando vazios | Diferente de StrToKArr |
| StrJoin | `StrJoin(aArray, cSep) => C` | Join de array em string | Inverso de StrToKArr |
| CharRem | `CharRem(cChars, cText) => C` | Remove caracteres de string | — |
| CharOnly | `CharOnly(cChars, cText) => C` | Mantem apenas esses chars | Util para limpar CPF/CNPJ |
| StrZero | `StrZero(nVal, nTam, nDec) => C` | Numero com zeros a esquerda | StrZero(5,3) = "005" |
| Str | `Str(nVal, nTam, nDec) => C` | Numero para string com espacos | Preferir StrZero ou cValToChar |
| FwNoAccent | `FwNoAccent(cText) => C` | Remove acentos | Para logs e msgs de erro |
| Encode64 | `Encode64(cText) => C` | Codifica Base64 | Para auth Bearer/Basic |
| Decode64 | `Decode64(cBase64) => C` | Decodifica Base64 | — |
| EncodeUTF8 | `EncodeUTF8(cText) => C` | Converte para UTF-8 | Para envio REST |
| DecodeUTF8 | `DecodeUTF8(cUtf8) => C` | Converte de UTF-8 | Para recepcao REST |

---

## 2. Conversao de Tipos

| Funcao | Assinatura | Descricao | Armadilha |
|--------|-----------|-----------|-----------|
| Val | `Val(cNum) => N` | String para numerico | Val("abc") retorna 0 |
| Str | `Str(nVal, nTam, nDec) => C` | Numerico para string | Preenche com espacos |
| StrZero | `StrZero(nVal, nTam, nDec) => C` | Numerico com zeros | StrZero(1,6) = "000001" |
| cValToChar | `cValToChar(xVal) => C` | Qualquer tipo para string | Para logs/ConOut |
| DToS | `DToS(dData) => C` | Data para AAAAMMDD | OBRIGATORIO em queries SQL |
| SToD | `SToD(cData) => D` | AAAAMMDD para data | Inverso de DToS |
| DToC | `DToC(dData) => C` | Data formatada (dd/mm/aa) | Depende de SetDateFormat |
| CToD | `CToD(cData) => D` | String para data | Depende de SetDateFormat |
| DToE | `DToE(dData) => C` | Data para formato europeu | — |
| Type | `Type(cExpr) => C` | Tipo de expressao (string) | Recebe STRING: Type("cVar") |
| ValType | `ValType(xVal) => C` | Tipo de valor (valor) | Recebe VALOR: ValType(cVar) |
| CToN | `CToN(cNum) => N` | String para numerico | Similar a Val |
| NToC | `NToC(nVal) => C` | Numerico para string | Sem formatacao |
| Empty | `Empty(xVal) => L` | Verifica se vazio/zero/nulo | "" = .T., " " = .T., 0 = .T. |

---

## 3. Arrays

| Funcao | Assinatura | Descricao | Armadilha |
|--------|-----------|-----------|-----------|
| AAdd | `AAdd(aArray, xVal) => xVal` | Adiciona elemento ao final | Retorna valor, nao array |
| ADel | `ADel(aArray, nPos) => A` | Remove elemento (nao reduz) | Use ASize apos para reduzir |
| AIns | `AIns(aArray, nPos) => A` | Insere posicao vazia | Elemento fica NIL |
| ASize | `ASize(aArray, nTam) => A` | Redimensiona array | Pre-alocar quando possivel |
| AScan | `AScan(aArray, xBusca) => N` | Busca valor no array | 0 se nao encontrar |
| ASort | `ASort(aArray, nIni, nFim, bOrdem) => A` | Ordena array | bOrdem = bloco comparador |
| ATail | `ATail(aArray) => xVal` | Retorna ultimo elemento | Equiv: aArray[Len(aArray)] |
| AClone | `AClone(aArray) => A` | Copia profunda do array | Para evitar referencia |
| ACopy | `ACopy(aOrig, aDest, nIni, nQtd, nDest) => A` | Copia parcial | — |
| AFill | `AFill(aArray, xVal, nIni, nQtd) => A` | Preenche com valor | Para inicializar |
| AEval | `AEval(aArray, bBloco) => NIL` | Executa bloco para cada | Equiv: FOR EACH |
| Array | `Array(nTam) => A` | Cria array com tamanho | Elementos iniciam NIL |
| TCSqlToArr | `TCSqlToArr(cQuery) => A` | Query para array 2D | Resultado completo em memoria |
| ARemove | `ARemove(aArray, nPos) => A` | Remove e reduz array | Diferente de ADel |

---

## 4. Data e Hora

| Funcao | Assinatura | Descricao | Armadilha |
|--------|-----------|-----------|-----------|
| Date | `Date() => D` | Data atual do servidor | — |
| Year | `Year(dData) => N` | Ano (4 digitos) | Year(Date()) => 2026 |
| Month | `Month(dData) => N` | Mes (1-12) | — |
| Day | `Day(dData) => N` | Dia (1-31) | — |
| DOW | `DOW(dData) => N` | Dia da semana (1=Dom) | — |
| CDOW | `CDOW(dData) => C` | Nome do dia (idioma) | — |
| DaysInMonth | `DaysInMonth(dData) => N` | Dias no mes | Trata bissexto |
| Time | `Time() => C` | Hora atual HH:MM:SS | Retorna string |
| Seconds | `Seconds() => N` | Segundos desde meia-noite | Para medir tempo |
| ElapTime | `ElapTime(cIni, cFim) => C` | Diferenca entre horas | Formato HH:MM:SS |
| DataValida | `DataValida(dData, lAdiante) => D` | Proximo dia util | lAdiante = busca pra frente |
| FWTimeStamp | `FWTimeStamp() => C` | Timestamp AAAA-MM-DD HH:MM:SS | Para logs |

---

## 5. Matematica

| Funcao | Assinatura | Descricao | Armadilha |
|--------|-----------|-----------|-----------|
| Round | `Round(nVal, nDec) => N` | Arredonda (padrao contabil) | Arredondamento ABNT |
| NoRound | `NoRound(nVal, nDec) => N` | Trunca sem arredondar | Para calculos fiscais |
| Abs | `Abs(nVal) => N` | Valor absoluto | — |
| Max | `Max(nA, nB) => N` | Maior valor | Apenas 2 params |
| Min | `Min(nA, nB) => N` | Menor valor | Apenas 2 params |
| Int | `Int(nVal) => N` | Parte inteira | Trunca, nao arredonda |
| Mod | `Mod(nVal, nDiv) => N` | Resto da divisao | nDiv != 0 |
| Ceiling | `Ceiling(nVal) => N` | Arredonda para cima | — |
| Sqrt | `Sqrt(nVal) => N` | Raiz quadrada | nVal >= 0 |
| Log | `Log(nVal) => N` | Logaritmo natural | nVal > 0 |
| Exp | `Exp(nVal) => N` | Exponencial (e^n) | — |

---

## 6. Logica e Controle

| Funcao | Assinatura | Descricao | Armadilha |
|--------|-----------|-----------|-----------|
| IIf | `IIf(lCond, xTrue, xFalse) => X` | If inline | Avalia AMBOS os lados |
| ExistBlock | `ExistBlock(cBloco) => L` | PE existe? | Verifica antes de ExecBlock |
| Eval | `Eval(bBloco, ...) => X` | Executa codeblock | Parametros opcionais |
| ErrorBlock | `ErrorBlock(bBloco) => bAnterior` | Define handler de erro | Sempre restaurar anterior |
| Empty | `Empty(xVal) => L` | Vazio/zero/nulo? | Space = .T., CtoD("") = .T. |
| GetRemoteType | `GetRemoteType() => N` | Tipo de acesso | -1=Job, 1=SmartClient |
| IsBlind | `IsBlind() => L` | Sem interface? | .T. em Jobs/Web |
| Coalesce | `Coalesce(x1, x2, ...) => X` | Primeiro nao-nulo | — |
| FunName | `FunName() => C` | Nome da funcao atual | Para logs |
| ProcName | `ProcName(nLevel) => C` | Nome na pilha | 0=atual, 1=chamador |
| ProcLine | `ProcLine(nLevel) => N` | Linha na pilha | Para stack trace |

---

## 7. Arquivo I/O

| Funcao | Assinatura | Descricao | Armadilha |
|--------|-----------|-----------|-----------|
| File | `File(cPath) => L` | Arquivo existe? | — |
| FCreate | `FCreate(cPath, nAtrib) => N` | Cria arquivo | Retorna handle, -1=erro |
| FOpen | `FOpen(cPath, nMode) => N` | Abre arquivo | nMode: 0=read, 1=write, 2=rw |
| FWrite | `FWrite(nHandle, cBuffer, nBytes) => N` | Escreve em arquivo | Retorna bytes escritos |
| FRead | `FRead(nHandle, @cBuffer, nBytes) => N` | Le de arquivo | cBuffer por referencia |
| FSeek | `FSeek(nHandle, nOffset, nOrigin) => N` | Posiciona ponteiro | 0=inicio, 1=atual, 2=fim |
| FClose | `FClose(nHandle) => L` | Fecha arquivo | SEMPRE fechar |
| FErase | `FErase(cPath) => N` | Deleta arquivo | 0=OK, -1=erro |
| MemoWrite | `MemoWrite(cPath, cConteudo) => L` | Escreve texto em arquivo | Simples, sem handle |
| MemoRead | `MemoRead(cPath) => C` | Le arquivo inteiro | Cuidado com arquivos grandes |
| MakeDir | `MakeDir(cPath) => N` | Cria diretorio | 0=OK |
| DirRemove | `DirRemove(cPath) => N` | Remove diretorio vazio | Deve estar vazio |

---

## 8. Framework — Acesso a Dados

| Funcao | Assinatura | Descricao | Armadilha |
|--------|-----------|-----------|-----------|
| MpSysOpenQuery | `MpSysOpenQuery(cQuery, cAlias) => NIL` | Abre query em alias | UNICO padrao para SELECT |
| MpSysExecScalar | `MpSysExecScalar(cQuery) => C` | Valor escalar (MAX/COUNT) | Retorna sempre string |
| TCSqlExec | `TCSqlExec(cQuery) => N` | Executa DML | 0=OK, para INSERT/UPDATE/DELETE |
| TCSqlToArr | `TCSqlToArr(cQuery) => A` | Query para array 2D | Tudo em memoria |
| RetSqlName | `RetSqlName(cTabela) => C` | Nome fisico no banco | RetSqlName("SA1") => "SA1010" |
| GetNextAlias | `GetNextAlias() => C` | Alias unico | Nunca hardcodar alias |
| ChangeQuery | `ChangeQuery(cQuery) => C` | Portabilidade SQL | SEMPRE usar antes de executar |
| DbSelectArea | `DbSelectArea(cAlias) => NIL` | Seleciona workarea | — |
| DbSetOrder | `DbSetOrder(nOrdem) => NIL` | Define indice ativo | Ver SIX para ordens |
| DbGoTop | `DbGoTop() => NIL` | Primeiro registro | — |
| DbSkip | `DbSkip(nRegs) => NIL` | Avanca registros | Default nRegs=1 |
| DbSeek | `DbSeek(xChave, lSoft) => L` | Busca no indice | Preferir MsSeek |
| MsSeek | `MsSeek(xChave, lSoft, cAlias) => L` | Busca + posiciona | PREFERIDO sobre DbSeek |
| Posicione | `Posicione(cAlias, nOrd, xChave, cCampo) => X` | Retorna campo sem mudar area | Nao altera area atual |
| RecLock | `RecLock(cAlias, lInclui) => L` | Trava registro | SEMPRE verificar retorno |
| MsUnLock | `MsUnLock(cAlias) => NIL` | Destrava | Usar apos RecLock |
| DbCloseArea | `DbCloseArea() => NIL` | Fecha alias | OBRIGATORIO apos query |
| GetArea | `GetArea(cAlias) => A` | Salva estado area | Legado — usar FWGetArea |
| RestArea | `RestArea(aArea) => NIL` | Restaura area | Legado — usar FWRestArea |
| FWGetArea | `FWGetArea(cAlias) => A` | Salva estado (moderno) | SEMPRE em pares |
| FWRestArea | `FWRestArea(aArea) => NIL` | Restaura (moderno) | SEMPRE em pares |
| xFilial | `xFilial(cAlias) => C` | Filial da tabela | OBRIGATORIO em queries |
| FwxFilial | `FwxFilial(cAlias, cFil) => C` | Filial especifica | Para multi-filial |
| FieldPos | `FieldPos(cCampo) => N` | Posicao do campo | 0 se nao existir |
| FieldGet | `FieldGet(nPos) => X` | Valor por posicao | — |
| FieldPut | `FieldPut(nPos, xVal) => X` | Grava por posicao | — |

---

## 9. Framework — MVC

| Funcao | Assinatura | Descricao | Armadilha |
|--------|-----------|-----------|-----------|
| FWLoadModel | `FWLoadModel(cFonte) => O` | Carrega model existente | Para uso programatico |
| FWExecView | `FWExecView(cTit, cFonte, nOper) => N` | Abre tela MVC | nOper: MODEL_OPERATION_* |
| FwBuildFeature | `FwBuildFeature(nTipo, cConteudo) => A` | Campo virtual/feature | FWBUILDFEATURE_VALUE=2 |
| MPFormModel | `MPFormModel():New(cId, bPre, bOk, bCommit, bCancel)` | Cria model novo | 5 parametros |
| FWFormView | `FWFormView():New() => O` | Cria view nova | — |
| FWFormViewStruct | `FWFormViewStruct():New() => O` | Estrutura campos view | AddField com 16 params |
| FWFormModelStruct | `FWFormModelStruct():New() => O` | Estrutura campos model | AddField com 14 params |
| FWMBrowse | `FWMBrowse():New() => O` | Browse MVC | SetAlias, SetDescription |
| FWMarkBrowse | `FWMarkBrowse():New() => O` | Browse com checkbox | SetFieldMark obrigatorio |
| SetPrimaryKey | `oStruct:SetPrimaryKey(aCampos)` | Chave do model | Se nao setar, erro na gravacao |
| SetOnlyQuery | `oModel:SetOnlyQuery(.T.)` | Model somente leitura | Para monitores/consultas |
| FWFormCommit | `FWFormCommit(oModel) => NIL` | Commit padrao MVC | Usar se bCommit nao customizado |

---

## 10. Framework — REST

| Funcao | Assinatura | Descricao | Armadilha |
|--------|-----------|-----------|-----------|
| SetStatusCode | `oRest:SetStatusCode(nCode) => NIL` | HTTP status | Return .T. CRITICO |
| SetResponse | `oRest:SetResponse(cJson) => NIL` | Corpo resposta | — |
| GetBody | `oRest:GetBody() => C` | Corpo requisicao | JSON string |
| GetQueryString | `oRest:GetQueryString() => C` | Params de URL | ?page=1&size=10 |
| GetPathParam | `GetPathParam(cNome) => C` | Param de rota | /clientes/:id |
| FWRest:New | `FWRest():New(cUrl) => O` | Cliente REST | Preferido para consumo |
| :SetPath | `oRest:SetPath(cPath) => NIL` | Endpoint | — |
| :Get | `oRest:Get() => L` | Executa GET | .T.=sucesso |
| :Post | `oRest:Post(cBody) => L` | Executa POST | — |
| :Put | `oRest:Put(cBody) => L` | Executa PUT | — |
| :Delete | `oRest:Delete() => L` | Executa DELETE | — |
| :GetResult | `oRest:GetResult() => C` | Le resposta | — |
| :GetLastError | `oRest:GetLastError() => C` | Ultimo erro | — |
| HTTPQuote | `HTTPQuote():New(cUrl) => O` | Cliente HTTP | Quando precisa ler headers |
| FWJsonSerialize | `FWJsonSerialize(xVal) => C` | Serializa para JSON | Qualquer tipo |
| FWJsonDeserialize | `FWJsonDeserialize(cJson) => X` | Parse JSON | — |
| JsonObject:New | `JsonObject():New() => O` | Cria obj JSON | — |
| :FromJson | `oJson:FromJson(cJson) => X` | Parse (NIL=ok, C=erro) | VERIFICAR tipo retorno |
| :ToJson | `oJson:ToJson() => C` | Serializa | — |

---

## 11. Framework — UI

| Funcao | Assinatura | Descricao | Armadilha |
|--------|-----------|-----------|-----------|
| MsDiaLog | `DEFINE MSDIALOG oD TITLE c FROM n,n TO n,n PIXEL` | Dialog padrao | Usar PIXEL sempre |
| TDialog | `TDialog():New(nT,nL,nB,nR,cTit) => O` | Dialog OOP | Para telas dinamicas |
| EnchoiceBar | `EnchoiceBar(oD, bOk, bCancel) => O` | Barra Ok/Cancel | Padrao para dialogs |
| MsNewGetDados | `MsNewGetDados():New(...) => O` | Grid editavel | Substituiu MsGetDados |
| TFont | `TFont():New(cNome,nW,nH) => O` | Fonte | TFont():New(,,-14) padrao |
| TSay | `TSay():New(nR,nC,bText,oWnd) => O` | Label/texto | — |
| TGet | `TGet():New(nR,nC,bSet,oWnd,nW,nH) => O` | Campo editavel | — |
| TButton | `TButton():New(nR,nC,cText,oWnd,bAction) => O` | Botao | — |
| TPanel | `TPanel():New(nR,nC,cText,oWnd) => O` | Painel container | — |
| MsgBox | `MsgBox(cMsg, cTit, nTipo) => N` | Mensagem generica | — |
| MsgStop | `MsgStop(cMsg, cTit) => NIL` | Erro/parada | Icone stop |
| MsgInfo | `MsgInfo(cMsg, cTit) => NIL` | Informacao | Icone info |
| MsgYesNo | `MsgYesNo(cMsg, cTit) => L` | Sim/Nao | .T.=Sim |
| Alert | `Alert(cMsg) => NIL` | Alerta simples | Legado |
| FWAlertError | `FWAlertError(cMsg, cTit) => NIL` | Erro moderno | — |

---

## 12. Framework — Utilitarios

| Funcao | Assinatura | Descricao | Armadilha |
|--------|-----------|-----------|-----------|
| SuperGetMV | `SuperGetMV(cParam, lHelp, xDefault) => X` | Le param SX6 com cache | PREFERIDO sobre GetMV |
| GetMV | `GetMV(cParam) => X` | Le param SX6 sem cache | Sem cache = mais lento |
| PutMV | `PutMV(cParam, xVal) => NIL` | Grava param SX6 | — |
| LockByName | `LockByName(cNome, lWait) => L` | Lock nomeado | Incluir empresa+filial no nome |
| UnLockByName | `UnLockByName(cNome) => NIL` | Libera lock | SEMPRE em finally |
| Pergunte | `Pergunte(cGrupo, lMostra) => L` | Parametros SX1 | .T. mostra tela |
| ParamBox | `ParamBox(aParams, cTit, ...) => L` | Params modernos | — |
| AjustaSX1 | `AjustaSX1(cGrupo, ...) => NIL` | Cria perguntas SX1 | — |
| ExecBlock | `ExecBlock(cBloco, lP, lR, ...) => X` | Executa PE | Pode retornar NIL |
| FWExecBlock | `FWExecBlock(cBloco, aParams) => X` | PE com array params | — |
| MsExecAuto | `MsExecAuto({...}, cAlias, nOper, aFields)` | Execucao automatica | Setar lMsErroAuto antes |
| RpcSetEnv | `RpcSetEnv(cEmp, cFil) => NIL` | Abre ambiente Job | SEMPRE antes de RpcClearEnv |
| RpcClearEnv | `RpcClearEnv() => NIL` | Fecha ambiente Job | SEMPRE no final do Job |
| Sleep | `Sleep(nMs) => NIL` | Pausa (bloqueia thread) | Preferir TSleep |
| TSleep | `TSleep(nMs) => NIL` | Pausa (nao bloqueia) | PREFERIDO sobre Sleep |
| FWCodFil | `FWCodFil() => C` | Filial atual | — |
| FWUuidV4 | `FWUuidV4() => C` | Gera UUID v4 | Para IDs unicos |
| FWTimeStamp | `FWTimeStamp() => C` | Timestamp formatado | AAAA-MM-DD HH:MM:SS |
| FwNoAccent | `FwNoAccent(cText) => C` | Remove acentos | Para logs e erros |
| FwCallStack | `FwCallStack() => C` | Stack trace | Para debug |
| FreeObj | `FreeObj(oObj) => NIL` | Libera objeto | Usar antes de NIL |
| FunName | `FunName() => C` | Funcao atual | Para logs |

---

## 13. Framework — Dicionario

| Funcao | Assinatura | Descricao | Armadilha |
|--------|-----------|-----------|-----------|
| GetSx3Cache | `GetSx3Cache(cCampo, cProp) => X` | Propriedade SX3 com cache | Props: X3_TIPO, X3_TAMANHO |
| TamSx3 | `TamSx3(cCampo) => A` | Tamanho+decimal | Retorna {nTam, nDec} |
| X3Descric | `X3Descric() => C` | Descricao campo | SX3 deve estar posicionado |
| X3Picture | `X3Picture() => C` | Picture do campo | — |
| X3Tipo | `X3Tipo() => C` | Tipo (C/N/D/L/M) | — |
| X3CBox | `X3CBox() => C` | Opcoes combo | Formato: "1=Op1;2=Op2" |
| Sx3NumOpen | `Sx3NumOpen(cAlias) => N` | Abre SX3 da tabela | — |

---

## 14. Framework — Ambiente

| Funcao | Assinatura | Descricao | Armadilha |
|--------|-----------|-----------|-----------|
| xFilial | `xFilial(cAlias) => C` | Filial da tabela | OBRIGATORIO em queries |
| FwxFilial | `FwxFilial(cAlias, cFil) => C` | Filial especifica | — |
| cFilAnt | Variavel | Filial atual | Variavel publica |
| cEmpAnt | Variavel | Empresa atual | Variavel publica |
| FWCodFil | `FWCodFil() => C` | Filial (funcao) | — |
| FWGrpCompany | `FWGrpCompany() => C` | Grupo empresa | — |
| cUserID | Variavel | ID usuario logado | Variavel publica |
| __cUserID | Variavel | ID usuario (alternativa) | — |
| RetCodUsr | `RetCodUsr() => C` | Codigo usuario | — |
| UsrRetName | `UsrRetName(cUserId) => C` | Nome usuario | — |
| ThreadID | `ThreadID() => N` | ID da thread | — |
| GetRemoteType | `GetRemoteType() => N` | -1=Job, 1=SmartClient | — |

---

## 15. Error Handling

| Funcao | Assinatura | Descricao | Armadilha |
|--------|-----------|-----------|-----------|
| ErrorBlock | `ErrorBlock(bBloco) => bAnterior` | Define handler erro | SEMPRE restaurar anterior |
| Break | `Break(oErr) => NIL` | Lanca excecao | Dentro de Recover |
| FWGrLog | `FWGrLog(cMsg) => NIL` | Adiciona ao log de erro | Dentro de ErrorBlock |
| AutoGrLogToStr | `AutoGrLogToStr() => C` | Log de erro como string | Apos MsExecAuto |
| GetLastAutoGrLog | `GetLastAutoGrLog() => C` | Ultimo log de erro | — |
| FWTraceLog | `FWTraceLog() => C` | Stack trace formatado | — |
| FWLogError | `FWLogError(cMsg) => NIL` | Log de erro permanente | — |
| FwLogMsg | `FwLogMsg(cSev, cTrans, cSrc, cFunc, cOp, cCod, cMsg, n1, n2, aExt) => NIL` | Log estruturado | Severidades: INFO/WARNING/ERROR |
| ConOut | `ConOut(cMsg) => NIL` | Log no console | APENAS para debug temporario |

**Padrao Begin Sequence:**
O bloco `Recover` e opcional, usado apenas para tratamento especifico.

```advpl
// Simples (apenas para Break)
Begin Sequence
    If lErro
        Break
    EndIf
End Sequence

// Com tratamento de erro (Sugerido)
Local bAnterior := ErrorBlock({|oErr| oErr:Break()})
Begin Sequence
    // codigo que pode falhar
Recover Using oErr
    ConOut("Erro: " + oErr:Description)
End Sequence
ErrorBlock(bAnterior) // SEMPRE restaurar
```

---

## 16. Crypto e Encoding

| Funcao | Assinatura | Descricao | Armadilha |
|--------|-----------|-----------|-----------|
| SHA256 | `SHA256(cText) => C` | Hash SHA-256 | — |
| HMACSHA256 | `HMACSHA256(cText, cChave) => C` | HMAC-SHA256 | Para assinaturas |
| MD5 | `MD5(cText) => C` | Hash MD5 | Nao usar para seguranca |
| HMACMD5 | `HMACMD5(cText, cChave) => C` | HMAC-MD5 | Legado |
| Encode64 | `Encode64(cText) => C` | Base64 encode | — |
| Decode64 | `Decode64(cText) => C` | Base64 decode | — |
| EncodeUTF8 | `EncodeUTF8(cText) => C` | Para UTF-8 | REST externo |
| DecodeUTF8 | `DecodeUTF8(cText) => C` | De UTF-8 | REST recebido |

---

## 17. Funcoes Deprecadas

| Deprecada | Substituir por | Motivo |
|-----------|---------------|--------|
| TCQuery | MpSysOpenQuery | Padrao obrigatorio |
| DbUseArea (TOPCONN) | MpSysOpenQuery | Acesso direto nao padrao |
| BeginSQL (codigo novo) | MpSysOpenQuery | Apenas manter existente |
| MBrowse | FWMBrowse | Legado |
| MsGetDados | MsNewGetDados | Legado |
| Modelo3 | MVC (FWFormModel) | Obsoleto |
| SetPrint | TReport | Framework oficial |
| Trim | AllTrim | AllTrim e padrao |
| DbSeek | MsSeek | MsSeek posiciona+retorna |
| MsgAlert | MsgInfo | Padronizacao |
| GetArea/RestArea | FWGetArea/FWRestArea | Versao moderna |
