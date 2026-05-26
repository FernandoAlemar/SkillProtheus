---
name: advpl-embedded-sql
description: >
  SQL embarcado (BeginSQL/EndSQL) em ADVPL/TLPP. Este é o padrão PRIORITÁRIO
  para novas queries no projeto. Use quando precisar realizar consultas SQL,
  filtros complexos ou JOINs, garantindo performance e legibilidade via macros
  (%table:, %xfilial:, %notDel%).
---

# ADVPL/TLPP Embedded SQL — BeginSQL/EndSQL (Padrão Prioritário)

Skill de desenvolvimento e manutenção de queries usando BeginSQL/EndSQL.
**Para código NOVO, este é o padrão obrigatório.** O `MpSysOpenQuery` deve ser
usado apenas em casos de queries dinâmicas complexas ou manutenção (ver `protheus-data-model`).

---

## 1. POSICIONAMENTO

| Contexto | Padrão | Skill |
|----------|--------|-------|
| Código NOVO | **BeginSQL (Prioridade)** | **esta skill** |
| Código NOVO (Dinâmico) | MpSysOpenQuery (Secundário) | `protheus-data-model` |
| Código EXISTENTE | Manter padrão atual | Respectiva skill |

---

## 2. SINTAXE BASICA

### 2.1 Estrutura BeginSQL/EndSQL

```advpl
// BeginSQL abre um alias automaticamente
BeginSQL Alias cAlias
    SELECT A1_COD, A1_NOME, A1_CGC
    FROM %table:SA1% SA1
    WHERE SA1.A1_FILIAL = %xfilial:SA1%
      AND SA1.A1_ATIVO  = '1'
      AND SA1.%notDel%
EndSQL

// Navegar como qualquer alias
While !(cAlias)->(Eof())
    cNome := (cAlias)->A1_NOME
    (cAlias)->(DbSkip())
EndDo

(cAlias)->(DbCloseArea())
```

### 2.2 Comparacao com MpSysOpenQuery

```advpl
// BeginSQL (Padrão Prioritário)             // MpSysOpenQuery (Secundário/Manutenção)
BeginSQL Alias cAlias                   cAlias := GetNextAlias()
    SELECT A1_COD, A1_NOME              cQuery := " SELECT A1_COD, A1_NOME "
    FROM %table:SA1% SA1                cQuery += " FROM " + RetSqlName("SA1") + " SA1 "
    WHERE A1_FILIAL = %xfilial:SA1%     cQuery += " WHERE A1_FILIAL = '" + xFilial("SA1") + "' "
      AND %notDel%                      cQuery += "   AND SA1.D_E_L_E_T_ = ' ' "
EndSQL                                  MpSysOpenQuery(ChangeQuery(cQuery), cAlias)
```

---

## 3. MACROS BeginSQL

Macros sao substituidas pelo pre-processador em tempo de compilacao.

### 3.1 Tabela de macros

| Macro | Expande para | Equivalente manual |
|-------|-------------|-------------------|
| `%table:SA1%` | Nome fisico da tabela (ex: `SA1010`) | `RetSqlName("SA1")` |
| `%xfilial:SA1%` | `'XX'` (filial corrente entre aspas) | `'" + xFilial("SA1") + "'` |
| `%notDel%` | `D_E_L_E_T_ <> '*'` | `D_E_L_E_T_ = ' '` |
| `%exp:cVar%` | Valor da variavel ADVPL interpolado | Concatenacao na string |
| `%Order:SA1%` | Expressao do indice atual | `IndexKey()` |

### 3.2 Detalhes criticos das macros

**`%notDel%` — Diferenca semantica importante:**

```sql
-- %notDel% expande para:
D_E_L_E_T_ <> '*'

-- Nosso padrao MpSysOpenQuery usa:
D_E_L_E_T_ = ' '

-- Diferenca pratica:
-- %notDel% aceita QUALQUER valor que nao seja '*' (incluindo '', 'X', etc.)
-- D_E_L_E_T_ = ' ' aceita APENAS espaco
-- Na pratica o resultado e o mesmo na maioria dos casos,
-- mas D_E_L_E_T_ = ' ' e mais preciso e mais performatico (usa indice)
```

**`%exp:cVar%` — Interpolacao de variavel:**

```advpl
Local cCodCli := "000001"
Local dDataIni := Date()

BeginSQL Alias cAlias
    SELECT E1_NUM, E1_VALOR
    FROM %table:SE1% SE1
    WHERE E1_FILIAL  = %xfilial:SE1%
      AND E1_CLIENTE = %exp:cCodCli%
      AND E1_EMISSAO >= %exp:DToS(dDataIni)%
      AND %notDel%
EndSQL
```

**`%exp:` com expressoes:**

```advpl
// Funcoes ADVPL dentro de %exp:
%exp:cCodigo%           // Valor da variavel
%exp:AllTrim(cCodigo)%  // Funcao aplicada
%exp:DToS(dData)%       // Conversao de data
%exp:cValToChar(nNum)%  // Conversao numerica
```

### 3.3 Uso de LIKE com %exp: (Escape de Percentual)

O parser do Embedded SQL (TopConn) consome um par de `%` ao resolver a macro `%exp:`. Para garantir que o SQL final contenha os caracteres de percentual do `LIKE`, deve-se "dobrar" ou envolver a string em um par extra de `%`.

**Padrão Recomendado:**

```advpl
// 1. Monte a string com aspas simples e percentuais internos
Local cLike := "'%" + AllTrim(cID) + "%'"

// 2. Adicione o par extra para o parser "consumir"
cLike := "%" + cLike + "%"

// 3. No SQL, use a macro normalmente
BeginSQL Alias cAlias
    SELECT * FROM %table:ZC1%
    WHERE ZC1_ORIGEM LIKE %exp:cLike%
EndSQL

// Resultado no Banco: LIKE '%VALOR%'
```

---

## 4. DECLARACAO DE TIPOS DE COLUNA

BeginSQL permite declarar o tipo de retorno das colunas com `column ... as ...`.
Isso e importante para colunas calculadas ou que o driver nao infere corretamente.

```advpl
BeginSQL Alias cAlias
    column E1_SALDO as Numeric
    column E1_VENCTO as Date
    column TOTAL_TITULOS as Numeric

    SELECT E1_PREFIXO, E1_NUM, E1_SALDO, E1_VENCTO,
           COUNT(*) AS TOTAL_TITULOS
    FROM %table:SE1% SE1
    WHERE E1_FILIAL = %xfilial:SE1%
      AND %notDel%
    GROUP BY E1_PREFIXO, E1_NUM, E1_SALDO, E1_VENCTO
EndSQL
```

### Tipos suportados

| Tipo | Quando usar |
|------|-------------|
| `as Numeric` | Campos calculados (SUM, COUNT, AVG), campos numericos |
| `as Date` | Campos de data, CONVERT/CAST para data |
| `as Character` | Campos string (geralmente inferido automaticamente) |
| `as Logical` | Campos logicos (raro) |
| `as Memo` | Campos memo/text |

---

## 5. JOINs DENTRO DE BeginSQL

```advpl
BeginSQL Alias cAlias
    SELECT SC5.C5_NUM, SC5.C5_EMISSAO, SA1.A1_NOME, SA1.A1_CGC
    FROM %table:SC5% SC5
    INNER JOIN %table:SA1% SA1
        ON SA1.A1_FILIAL = SC5.C5_FILIAL
       AND SA1.A1_COD    = SC5.C5_CLIENTE
       AND SA1.A1_LOJA   = SC5.C5_LOJACLI
       AND SA1.%notDel%
    WHERE SC5.C5_FILIAL = %xfilial:SC5%
      AND SC5.C5_TIPO   = 'N'
      AND SC5.%notDel%
EndSQL
```

**Nota:** `%notDel%` deve ser aplicado em CADA tabela do JOIN.
Erro comum: esquecer `%notDel%` na tabela JOINada.

---

## 6. AGREGACOES

```advpl
BeginSQL Alias cAlias
    column QTDE as Numeric
    column TOTAL as Numeric

    SELECT E1_CLIENTE, E1_LOJA,
           COUNT(*) AS QTDE,
           SUM(E1_SALDO) AS TOTAL
    FROM %table:SE1% SE1
    WHERE E1_FILIAL = %xfilial:SE1%
      AND E1_SALDO > 0
      AND %notDel%
    GROUP BY E1_CLIENTE, E1_LOJA
    HAVING SUM(E1_SALDO) > 1000
EndSQL
```

---

## 7. DML COM TCSqlExec

Para INSERT, UPDATE, DELETE usar `TCSqlExec()` (nao BeginSQL):

```advpl
// INSERT
cSql := "INSERT INTO " + RetSqlName("ZZ1") + " (ZZ1_FILIAL, ZZ1_CODIGO, ZZ1_DESCRI, D_E_L_E_T_) "
cSql += " VALUES ('" + xFilial("ZZ1") + "', '" + cCodigo + "', '" + cDescri + "', ' ') "
nRet := TCSqlExec(cSql)
If nRet < 0
    ConOut("Erro SQL: " + TCSqlError())
EndIf

// UPDATE
cSql := "UPDATE " + RetSqlName("ZZ1")
cSql += " SET ZZ1_STATUS = '2' "
cSql += " WHERE ZZ1_FILIAL = '" + xFilial("ZZ1") + "' "
cSql += "   AND ZZ1_CODIGO = '" + cCodigo + "' "
cSql += "   AND D_E_L_E_T_ = ' ' "
nRet := TCSqlExec(cSql)

// DELETE (soft delete — padrao Protheus)
cSql := "UPDATE " + RetSqlName("ZZ1")
cSql += " SET D_E_L_E_T_ = '*' "
cSql += " WHERE ZZ1_FILIAL = '" + xFilial("ZZ1") + "' "
cSql += "   AND ZZ1_CODIGO = '" + cCodigo + "' "
nRet := TCSqlExec(cSql)
```

**IMPORTANTE:** Protheus usa soft delete (`D_E_L_E_T_ = '*'`). NUNCA use `DELETE FROM` em tabelas Protheus.

---

## 8. MIGRACAO BeginSQL → MpSysOpenQuery

### 8.1 Tabela de conversao

| BeginSQL | MpSysOpenQuery |
|----------|---------------|
| `BeginSQL Alias cAlias` | `cAlias := GetNextAlias()` |
| `%table:SA1%` | `RetSqlName("SA1")` |
| `%xfilial:SA1%` | `'" + xFilial("SA1") + "'` |
| `%notDel%` | `D_E_L_E_T_ = ' '` |
| `%exp:cVar%` | `'" + cVar + "'` |
| `%exp:DToS(dData)%` | `'" + DToS(dData) + "'` |
| `%Order:SA1%` | Nao usar (montar ORDER BY explicito) |
| `column X as Numeric` | Remover (MpSysOpenQuery infere) |
| `EndSQL` | `MpSysOpenQuery(ChangeQuery(cQuery), cAlias)` |

### 8.2 Exemplo completo: antes e depois

**ANTES (BeginSQL):**
```advpl
Local cAlias := GetNextAlias()

BeginSQL Alias cAlias
    column E1_SALDO as Numeric

    SELECT E1_PREFIXO, E1_NUM, E1_PARCELA, E1_SALDO, E1_VENCTO
    FROM %table:SE1% SE1
    INNER JOIN %table:SA1% SA1
        ON SA1.A1_FILIAL = SE1.E1_FILIAL
       AND SA1.A1_COD    = SE1.E1_CLIENTE
       AND SA1.A1_LOJA   = SE1.E1_LOJA
       AND SA1.%notDel%
    WHERE SE1.E1_FILIAL  = %xfilial:SE1%
      AND SE1.E1_CLIENTE = %exp:cCliente%
      AND SE1.E1_SALDO   > 0
      AND SE1.%notDel%
    ORDER BY SE1.E1_VENCTO
EndSQL
```

**DEPOIS (MpSysOpenQuery):**
```advpl
Local cAlias := GetNextAlias()
Local cQuery := ""

cQuery := " SELECT SE1.E1_PREFIXO, SE1.E1_NUM, SE1.E1_PARCELA, "
cQuery += "   SE1.E1_SALDO, SE1.E1_VENCTO "
cQuery += " FROM " + RetSqlName("SE1") + " SE1 "
cQuery += " INNER JOIN " + RetSqlName("SA1") + " SA1 "
cQuery += "   ON SA1.A1_FILIAL = SE1.E1_FILIAL "
cQuery += "  AND SA1.A1_COD    = SE1.E1_CLIENTE "
cQuery += "  AND SA1.A1_LOJA   = SE1.E1_LOJA "
cQuery += "  AND SA1.D_E_L_E_T_ = ' ' "
cQuery += " WHERE SE1.E1_FILIAL = '" + xFilial("SE1") + "' "
cQuery += "   AND SE1.E1_CLIENTE = '" + cCliente + "' "
cQuery += "   AND SE1.E1_SALDO > 0 "
cQuery += "   AND SE1.D_E_L_E_T_ = ' ' "
cQuery += " ORDER BY SE1.E1_VENCTO "

MpSysOpenQuery(ChangeQuery(cQuery), cAlias)
```

### 8.3 Checklist de migracao

- [ ] Substituir `BeginSQL Alias cAlias` por `cAlias := GetNextAlias()`
- [ ] Substituir `%table:XXX%` por `RetSqlName("XXX")`
- [ ] Substituir `%xfilial:XXX%` por `'" + xFilial("XXX") + "'`
- [ ] Substituir `%notDel%` por `D_E_L_E_T_ = ' '` (nota: muda semantica!)
- [ ] Substituir `%exp:cVar%` por concatenacao: `'" + cVar + "'`
- [ ] Remover linhas `column X as Type` (MpSysOpenQuery infere tipos)
- [ ] Adicionar prefixo de tabela em todos os campos (`SE1.E1_NUM` nao apenas `E1_NUM`)
- [ ] Envolver query com `ChangeQuery()` antes de passar para MpSysOpenQuery
- [ ] Substituir `EndSQL` por `MpSysOpenQuery(ChangeQuery(cQuery), cAlias)`
- [ ] Testar: verificar se os dados retornados sao identicos

---

## 9. TCQuery — LEGADO

TCQuery e o predecessor do BeginSQL e do MpSysOpenQuery. Ainda encontrado
em codigo antigo. NAO usar em codigo novo.

```advpl
// TCQuery (LEGADO — nao usar em codigo novo)
cQuery := "SELECT A1_COD, A1_NOME FROM SA1010 WHERE A1_FILIAL = '01'"
TCQuery cQuery New Alias cAlias

// Migrar para MpSysOpenQuery:
cAlias := GetNextAlias()
cQuery := " SELECT SA1.A1_COD, SA1.A1_NOME "
cQuery += " FROM " + RetSqlName("SA1") + " SA1 "
cQuery += " WHERE SA1.A1_FILIAL = '" + xFilial("SA1") + "' "
cQuery += "   AND SA1.D_E_L_E_T_ = ' ' "
MpSysOpenQuery(ChangeQuery(cQuery), cAlias)
```

---

## 10. ANTI-PATTERNS EM BeginSQL

### 10.1 Falta de %notDel%

```advpl
// ERRADO — retorna registros deletados
BeginSQL Alias cAlias
    SELECT A1_COD, A1_NOME
    FROM %table:SA1% SA1
    WHERE A1_FILIAL = %xfilial:SA1%
    // Falta %notDel% !
EndSQL

// CORRETO
BeginSQL Alias cAlias
    SELECT A1_COD, A1_NOME
    FROM %table:SA1% SA1
    WHERE A1_FILIAL = %xfilial:SA1%
      AND %notDel%
EndSQL
```

### 10.2 Falta de %xfilial% (dados de outra filial)

```advpl
// ERRADO — retorna dados de TODAS as filiais
BeginSQL Alias cAlias
    SELECT A1_COD, A1_NOME
    FROM %table:SA1% SA1
    WHERE %notDel%
    // Falta filtro de filial!
EndSQL
```

### 10.3 SELECT * em BeginSQL

```advpl
// ERRADO
BeginSQL Alias cAlias
    SELECT *
    FROM %table:SA1% SA1
    WHERE A1_FILIAL = %xfilial:SA1%
      AND %notDel%
EndSQL

// CORRETO — listar campos explicitamente
BeginSQL Alias cAlias
    SELECT A1_COD, A1_LOJA, A1_NOME, A1_CGC
    FROM %table:SA1% SA1
    WHERE A1_FILIAL = %xfilial:SA1%
      AND %notDel%
EndSQL
```

### 10.4 %notDel% faltando em tabela JOINada

```advpl
// ERRADO — JOIN sem %notDel% na SA1
BeginSQL Alias cAlias
    SELECT SC5.C5_NUM, SA1.A1_NOME
    FROM %table:SC5% SC5
    INNER JOIN %table:SA1% SA1
        ON SA1.A1_COD = SC5.C5_CLIENTE
    WHERE SC5.C5_FILIAL = %xfilial:SC5%
      AND SC5.%notDel%
    // SA1 pode retornar registros deletados!
EndSQL

// CORRETO — %notDel% em CADA tabela
BeginSQL Alias cAlias
    SELECT SC5.C5_NUM, SA1.A1_NOME
    FROM %table:SC5% SC5
    INNER JOIN %table:SA1% SA1
        ON SA1.A1_FILIAL = SC5.C5_FILIAL
       AND SA1.A1_COD    = SC5.C5_CLIENTE
       AND SA1.A1_LOJA   = SC5.C5_LOJACLI
       AND SA1.%notDel%
    WHERE SC5.C5_FILIAL = %xfilial:SC5%
      AND SC5.%notDel%
EndSQL
```

### 10.5 Uso de nome de tabela hardcoded

```advpl
// ERRADO — nome direto
BeginSQL Alias cAlias
    SELECT A1_COD FROM SA1010
    WHERE A1_FILIAL = '01'
EndSQL

// CORRETO — usar macros
BeginSQL Alias cAlias
    SELECT A1_COD FROM %table:SA1% SA1
    WHERE A1_FILIAL = %xfilial:SA1%
      AND %notDel%
EndSQL
```

---

## 11. CROSS-REFERENCES

| Topico | Skill |
|--------|-------|
| Padrao obrigatorio para codigo NOVO | `protheus-data-model` (secao 1) |
| MpSysOpenQuery completo | `protheus-data-model` (secao 1.1-1.4) |
| Metodos proibidos para SELECT | `protheus-data-model` (secao 2) |
| FwPreparedStatement | `protheus-data-model` (secao 1.2) |
| Debug de queries SQL | `advpl-debugging` (secao 8) |