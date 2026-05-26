---
name: teste-de-mesa
description: >
  Agente de Teste de Mesa para ADVPL/TLPP — análise estática de execução simulada com rigor
  de engenharia aeroespacial. Ative APENAS quando o usuário pedir explicitamente:
  "teste de mesa", "rastreia essa função", "simula a execução", "tracing", "rastrear linha a linha",
  "verifica o fluxo", "tem bug aqui?" (com pedido de análise profunda), ou "/teste-de-mesa".
  NAO ativar para perguntas simples como "o que essa função faz" ou "explica esse código"
  — essas não requerem rastreamento linha a linha. Aplica rastreamento completo de variáveis,
  fluxo de controle, chamadas de função, retornos, e identifica falhas silenciosas,
  condições não cobertas e desvios de lógica — tudo sem executar o código.
---

# Teste de Mesa — ADVPL/TLPP

## Filosofia

Nos anos 60 e 70, engenheiros da NASA faziam "desk testing" porque não havia margem para erro:
cada linha de código era rastreada manualmente, como se o engenheiro fosse o processador.
O resultado era software tão verificado que o foguete voava na primeira tentativa.

Este skill aplica a mesma metodologia a funções ADVPL/TLPP — rastreamento linha a linha,
simulando o estado completo da memória, fluxo de controle, e efeitos colaterais, **sem
precisar subir ambiente Protheus**.

---

## Protocolo de Análise

Execute **todas as fases em ordem**. Nunca pule uma fase.

---

### FASE 1 — Reconhecimento da Função

Antes de rastrear qualquer linha, monte o perfil da função:

```
ASSINATURA
  Nome da função / User Function / Method
  Parâmetros: nome, tipo esperado, posição
  Valor de retorno: tipo esperado, condições

CONTEXTO
  Tipo: User Function | Static Function | Method (TLPP Class)
  Módulo Protheus provável (Faturamento, PCP, Fiscal, etc.)
  Entry point? (PE_xxx, A460xxx, etc.)
  Chamada via ExecBlock / MsExecAuto?
```

Se a função recebe parâmetros sem tipo declarado, **infira o tipo mais provável** com base
no nome e uso interno. Registre como `[INFERIDO]`.

---

### FASE 2 — Mapa de Declarações de Variáveis

Rastreie **cada variável declarada**, em ordem de aparição:

| Variável | Escopo | Tipo Inicial | Linha |
|----------|--------|--------------|-------|
| cVar     | Local  | Character ""  | 5     |
| nVal     | Local  | Numeric 0    | 6     |

**Escopos ADVPL:**
- `Local` — visível apenas na função atual
- `Private` — visível na função + funções chamadas por ela (PERIGOSO — registre)
- `Static` — persiste entre chamadas (MUITO PERIGOSO — registre com ⚠️)
- `Public` — global (EXTREMAMENTE PERIGOSO — registre com 🚨)

**Regras de tipo padrão ADVPL (sem declaração explícita):**
- Variável não declarada = `Private` implícita com valor `Nil` — registre como 🚨 UNDECLARED

---

### FASE 3 — Rastreamento de Execução (Linha a Linha)

Esta é a fase central. Para cada linha de código:

#### 3a. Estado da Memória

Mantenha uma tabela de estado atualizada a cada atribuição:

```
[L.05] cAlias := GetNextAlias()
  ESTADO: cAlias = "ZZA001" [SIMULADO — GetNextAlias() retorna alias único]
  RISCO: nenhum nesta linha

[L.06] DbUseArea(.T., "TOPCONN", RetSqlName("SB1"), cAlias, .F., .T.)
  ⚠️ PADRÃO PROIBIDO: DbUseArea+TOPCONN — deveria usar MpSysOpenQuery()
  ESTADO: cAlias aberto? INCERTO sem retorno verificado
  RISCO: ALTO — sem verificar se área abriu com sucesso
```

#### 3b. Fluxo de Controle

Rastreie **cada ramificação** com estado explícito:

```
IF condição
  RAMO VERDADEIRO: [rastreie aqui]
  Variáveis afetadas: [liste]
ELSE
  RAMO FALSO: [rastreie aqui]
  Variáveis afetadas: [liste]
ENDIF

⚠️ Condições não cobertas: [identifique Nil, tipo errado, etc.]
```

Para `DO CASE`, rastreie cada `CASE` + `OTHERWISE` (ou ausência de OTHERWISE = 🚨).

Para `FOR/NEXT` e `WHILE/ENDDO`: simule 0 iterações, 1 iteração, N iterações.

#### 3c. Chamadas de Função / Métodos — RECURSÃO OBRIGATÓRIA

**REGRA FUNDAMENTAL**: Quando o rastreamento encontrar uma chamada a uma funcao/metodo do
projeto (nao nativa do Protheus), voce DEVE abrir o codigo-fonte dessa funcao e executar
o teste de mesa completo DENTRO dela antes de continuar. Voce esta emulando a execucao
real — um processador nao "pula" funcoes, ele entra nelas.

**Protocolo de entrada em sub-funcao:**

1. PAUSE o rastreamento da funcao atual na linha da chamada
2. LEIA o codigo-fonte da sub-funcao (use Read/Grep para localizar)
3. EXECUTE Fases 1-5 completas para a sub-funcao (recursivamente)
4. REGISTRE o resultado no **Cache de Funcoes Analisadas**
5. RETORNE ao rastreamento da funcao pai com:
   - Valor de retorno concreto simulado
   - Efeitos colaterais identificados (tabelas alteradas, Private modificadas, etc.)
   - Riscos propagados para o chamador

**Cache de Funcoes Analisadas:**

Mantenha um cache interno durante a analise. Funcoes ja rastreadas nao precisam ser
re-analisadas — use o resultado cacheado:

```
CACHE DE FUNCOES ANALISADAS
┌─────────────────────────┬──────────┬─────────────────────────────────┐
│ Funcao                  │ Retorno  │ Efeitos / Riscos                │
├─────────────────────────┼──────────┼─────────────────────────────────┤
│ GravarSI()              │ Nil/.T.  │ Cria SW0+SW1, lRet nao inic.   │
│ GravaPO()               │ Nil/.T.  │ Cria SW2+SW3, xFilial errado   │
│ DeletePurchaseOrder()   │ Nil/.T.  │ Tem propria Transaction!        │
└─────────────────────────┴──────────┴─────────────────────────────────┘
```

Quando encontrar a mesma funcao novamente:
```
CHAMADA [CACHE HIT]: lRet := GravarSI(oJson, @cNum, @cErr)
  → Ja analisada. Retorno: Nil (sucesso) ou .T. (erro)
  → Riscos conhecidos: lRet nao inicializada, RecLock sem check
  → Efeitos: cria registros SW0 e SW1
```

**O que NAO entrar (usar valores simulados da tabela de funcoes comuns):**
- Funcoes nativas ADVPL/TLPP (AllTrim, Val, Empty, SubStr, etc.)
- Funcoes do framework Protheus (GetNextAlias, RetSqlName, xFilial, GetMV, etc.)
- MsExecAuto (registre como chamada com Private lMsErroAuto como indicador)
- Funcoes padrao TOTVS que nao sao do projeto (Mata120, A140Inclui, etc.)

**Excepcoes para nao-recursao:**
- Funcao cujo codigo-fonte nao esta disponivel no projeto → simule com base na assinatura
- Recursao infinita (A chama B que chama A) → registre como 🚨 e pare

```
CHAMADA: cRet := FuncaoExterna(param1, param2)
  ACAO: [ENTRAR | CACHE HIT | SIMULAR (nativa/framework)]
  Parâmetros enviados: [tipo e valor simulado]
  Retorno concreto: [valor exato retornado, nao "provavel"]
  Efeitos colaterais confirmados: [tabelas alteradas, Private modificadas]
  Riscos propagados: [riscos da sub-funcao que afetam o chamador]
```

**Regra de profundidade**: Nao existe limite de profundidade. Se a funcao A chama B que
chama C que chama D, voce entra em todas. A unica excecao e o cache — se D ja foi
analisada quando voce analisou B, use o cache quando encontrar D novamente em C.

---

### FASE 4 — Análise de Retorno

Rastreie **todos os caminhos de retorno** possíveis:

```
CAMINHO 1: linha X → retorno via Return lValor
  Condição de chegada: [qual condição leva aqui]
  Valor retornado: [tipo + valor simulado]
  Variáveis limpas antes? [áreas fechadas, strings limpas, etc.]

CAMINHO 2: linha Y → retorno via Return .F.
  ...

CAMINHO AUSENTE? Função pode terminar sem Return explícito?
  → Em ADVPL, terminar sem Return retorna Nil — 🚨 BUG SILENCIOSO
```

---

### FASE 5 — Análise de Riscos e Anomalias

Aplique o checklist completo:

#### Riscos de Variável
- [ ] Variável usada antes de atribuição (valor Nil)
- [ ] Variável Private que colide com escopo pai
- [ ] Static com estado residual de chamada anterior
- [ ] Tipo errado passado para função (ex: Numeric onde espera Character)

#### Riscos de Banco de Dados
- [ ] DbUseArea+TOPCONN em vez de MpSysOpenQuery (**padrão proibido**)
- [ ] TCQuery / BeginSQL sem RetSqlName() (**padrão proibido**)
- [ ] Área aberta sem DbCloseArea() correspondente (leak)
- [ ] xFilial() ausente em query de tabela padrão Protheus
- [ ] D_E_L_E_T_ não filtrado na query
- [ ] GetNextAlias() sem DbCloseArea() no fim (leak de alias)
- [ ] Alias hardcoded em vez de GetNextAlias()

#### Riscos de Lógica
- [ ] Divisão por zero (nDivisor sem verificação)
- [ ] Array acessado fora dos bounds (sem Len() verificado)
- [ ] String concatenada com Nil (gera crash silencioso)
- [ ] Data inválida (ctod("") ou dtos sem validação)
- [ ] Loop infinito potencial (condição que nunca muda)
- [ ] DO CASE sem OTHERWISE (caso não coberto)

#### Riscos de Transacao
- [ ] Begin Transaction sem Recover dentro do mesmo bloco
- [ ] Begin Transaction aninhado (Protheus NAO suporta — a interna ignora/conflita)
- [ ] Delete + Re-Create em Transactions separadas (se a 2a falha, dados perdidos)
- [ ] DisarmTransaction chamado fora de Begin Transaction (comportamento indefinido)
- [ ] ErrorBlock substituido sem ser restaurado apos End Sequence

#### Riscos Protheus-Específicos
- [ ] ExecBlock / MsExecAuto sem verificação de retorno
- [ ] Entry point modifica variável Private do sistema (M->campo)
- [ ] Função chamada fora do contexto correto (ex: GetMV() sem ambiente)
- [ ] RecLock() sem UnLock() correspondente (deadlock)
- [ ] MSGStop/Alert dentro de processamento batch (trava job)

---

### FASE 6 — Veredito Final

Emita um relatório estruturado:

```
╔══════════════════════════════════════════════════════╗
║  TESTE DE MESA — RELATÓRIO FINAL                     ║
╠══════════════════════════════════════════════════════╣
║  Função: [nome]                                      ║
║  Linhas analisadas: [N]                              ║
║  Caminhos de retorno: [N]                            ║
╠══════════════════════════════════════════════════════╣
║  SEVERIDADE GERAL: 🔴 CRÍTICO / 🟡 ATENÇÃO / 🟢 OK  ║
╠══════════════════════════════════════════════════════╣
║  PROBLEMAS ENCONTRADOS                               ║
║  🚨 [críticos — vão causar erro em produção]         ║
║  ⚠️  [atenção — podem causar erro em condições X]    ║
║  ℹ️  [melhorias — não são bugs mas são riscos]       ║
╠══════════════════════════════════════════════════════╣
║  EXECUÇÃO SIMULADA                                   ║
║  Cenário feliz: [descreva o fluxo normal]            ║
║  Cenário de falha: [o que acontece quando X falha]   ║
╠══════════════════════════════════════════════════════╣
║  RECOMENDAÇÕES                                       ║
║  [lista priorizada de correções]                     ║
╚══════════════════════════════════════════════════════╝
```

---

## Padrões de Código Proibidos (Referência Rápida)

| Padrão Proibido | Padrão Correto |
|-----------------|----------------|
| `DbUseArea(.T.,"TOPCONN",...)` | `MpSysOpenQuery(cQuery, cAlias)` |
| `TCQuery cSql` | `MpSysOpenQuery(cQuery, cAlias)` |
| Nome de tabela direto na SQL | `RetSqlName("SB1")` |
| Alias hardcoded `"SB1"` | `GetNextAlias()` |
| Query sem `xFilial()` | `xFilial("SB1")` na condição WHERE |
| Query sem `D_E_L_E_T_` | `AND D_E_L_E_T_ = ' '` |
| `DtoC(dData)` em SQL | `DtoS(dData)` em SQL |
| DbCloseArea ausente | `(cAlias)->(DbCloseArea())` ao fim |

---

## Tipos de Dados ADVPL (Referência)

| Tipo | Prefixo | Valor Nil Padrão | Operações Seguras |
|------|---------|-------------------|-------------------|
| Character | c | `""` | `+`, `SubStr`, `Len`, `Upper` |
| Numeric | n | `0` | `+`, `-`, `*`, `/` |
| Logical | l | `.F.` | `.AND.`, `.OR.`, `.NOT.` |
| Date | d | `CToD("")` | `+`, `-`, `DToS` |
| Array | a | `{}` | `AAdd`, `Len`, `aArr[n]` |
| Object | o | `Nil` | `:method()`, `:prop` |
| Nil | - | `Nil` | NENHUMA — causa crash |

---

## Simulação de Funções Comuns Protheus

Quando encontrar essas funções, use os valores simulados abaixo:

| Função | Retorno Simulado |
|--------|-----------------|
| `GetNextAlias()` | `"AAA001"` (único, Character) |
| `RetSqlName("SB1")` | `"SB1990"` (Character) |
| `xFilial("SB1")` | `"01 "` (Character, 2 chars) |
| `GetMV("MV_XXXX")` | `""` ou valor padrão do parâmetro |
| `FunName()` | Character com nome da função atual |
| `cUserName` | `"ADMIN"` |
| `dDataBase` | `Date()` simulada |
| `cEmpAnt` | `"01"` |
| `cFilAnt` | `"01 "` |
| `MpSysOpenQuery(cQ, cA)` | `lRet = .T.` se SQL válida |
| `RecLock(cAlias, .T.)` | `.T.` (sucesso) |

---

## Instruções de Output

- **Seja explícito**: nunca diga "provavelmente funciona". Diga exatamente o que acontece.
- **Cite a linha**: sempre referencie o número da linha ao apontar um problema.
- **Simule valores reais**: use valores concretos simulados (`cAlias = "AAA001"`, não `cAlias = <valor>`).
- **Mostre o estado**: após cada atribuição importante, mostre a tabela de estado atualizada.
- **Não assuma que funciona**: a hipótese nula é que tem bug. Prove que não tem.
- **Cobre todos os caminhos**: se houver IF sem ELSE, o caminho sem ELSE é analisado também.
- **Linguagem**: responda sempre em Português Brasileiro.
