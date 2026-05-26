---
name: protheus-loop
description: Orquestrador Protheus — loop Dev → QA → Review até aprovação (sem subagents, serial, caveman). Use SOMENTE via /protheus-loop explícito. NAO ativar automaticamente.
---

# /protheus-loop — Orquestrador ADVPL/TLPP

Tarefa do usuário: $ARGUMENTS

CAVEMAN MODE ACTIVE (Ultra). Drop articles/filler/pleasantries/hedging. Fragments OK. Code/commits: write normal.

Você é orquestrador. NÃO escreve código direto. Invoca skills sequencialmente. Sem paralelismo. Sem subagents.

## Quando usar este orquestrador

**Use /protheus-loop quando a tarefa tiver:**
- 3 ou mais artefatos distintos (ex: MVC + Job + REST)
- Mudança estrutural que afeta múltiplos módulos
- Usuário pede ciclo completo dev→review explicitamente

**NÃO use para:**
- Bug fix isolado → use skill específica diretamente
- Novo campo/ajuste simples → use protheus-plan + protheus-exec
- Revisão de código → use /code-review diretamente

## Fluxo

### Fase 1 — Planejamento

Se `$ARGUMENTS` não referencia plano existente, use a skill de planejamento:
1. Ative a skill `protheus-plan`.
2. Siga o protocolo da skill para criar o `plano-*.md`.
3. Apresentar plano ao usuário. Aguardar aprovação explícita antes de seguir.

### Fase 2 — Loop iterativo

Estado: `iteracao = 0`, `max_iteracoes = 3`, `feedback = []`.

**Regras:**
- Cada skill roda sequencialmente — esperar resultado antes de chamar próxima.
- Sem paralelismo.
- Contexto passado via feedback acumulado.

Repita:

**1. Desenvolvedor (Execução)**
- Ative a skill `protheus-exec`.
- Passe o plano aprovado e o feedback acumulado como contexto.
- Aguardar conclusão. Anotar arquivos modificados.

**2. QA / Teste de mesa**
- Ative a skill `teste-de-mesa`.
- Analise os arquivos modificados frente ao plano.
- Aguardar resultado: bugs/desvios ou "APROVADO".

**3. Code Review**
- Ative a skill `code-review`.
- Revise os arquivos modificados.
- Aguardar resultado: issues ou "APROVADO".

**Checklist CLAUDE.md — GATE BLOQUEANTE** (qualquer item violado = REPROVADO):
- Variáveis Local no topo (nunca dentro de If/While/For)
- Notação húngara obrigatória (c/n/d/l/a/o/b)
- GetArea()/RestArea() em operações de banco
- Begin Sequence/Recover/End Sequence em lógica de negócio
- xFilial(cAlias) em todo seek
- RecLock/MsUnlock pareados
- NUNCA usar cFilial/cFilAnt/cEmpAnt como Local/Static
- JsonObject: só métodos válidos (GetNames, HasProperty, GetJsonText — NÃO existem Keys/HasKey/Count)
- TWsdlManager: só métodos válidos (sem GetSoapFault/ListServices/GetError)
- EnableTitleView (não EnableTitleGroup)
- Sem StaticCall/PTInternal
- Acesso SX via FWSX*Util (nunca DbSelectArea direto em SX3 etc)
- Includes .tlpp: TOTVS.CH + tlpp-core.th

**4. Decisão:**
- QA == "APROVADO" E Review == "APROVADO" → **fim, reportar sucesso**
- Se feedback contiver "ERRO ARQUITETURAL" ou "DESIGN FLAW" → voltar para **Fase 1 (Planejamento)** para atualizar o plano.
- Senão → consolidar issues em `feedback`, `iteracao++`, voltar passo 1.
- `iteracao >= max_iteracoes` → parar, reportar bloqueio com issues pendentes.

## Reporte por iteração

Ao final de cada iteração: "Iter N: Dev fez X. QA: Y. Review: Z."

## Saída final

Quando aprovado:
- Lista arquivos alterados
- Resumo iterações (quantas, principais correções)
- **Knowledge Item (KI):** Se `iteracao > 1` ou solução complexa, sugerir/criar KI em `.gemini/knowledge` com as lições aprendidas.
- Próximos passos (compilar, testar em ambiente, commit)

Não commitar sem pedido explícito do usuário.
