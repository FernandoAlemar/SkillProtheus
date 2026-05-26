---
name: code-review
description: Revisao de codigo ADVPL/TLPP para Protheus com analise em 4 categorias - seguranca, performance, boas praticas e modernizacao
---

# Code Review - ADVPL/TLPP para TOTVS Protheus

## Objetivo

Realizar revisao sistematica de codigo ADVPL/TLPP aplicando regras de **seguranca**, **performance**, **boas praticas** e **modernizacao**, com classificacao automatica do tipo de fonte e aplicacao de regras especificas.

## Classificacao do Tipo de Codigo

Analise o codigo e classifique conforme a tabela abaixo. Um mesmo fonte pode ter multiplas classificacoes.

| Padrao no Codigo                        | Tipo Identificado    | Skill Adicional        |
|-----------------------------------------|----------------------|------------------------|
| `RpcSetEnv`, `LockByName`, `Schedule`   | protheus-jobs        | protheus-jobs          |
| `@Get`, `@Post`, `@Put`, `@Delete`      | protheus-rest        | protheus-rest          |
| `ModelDef`, `ViewDef`, `MenuDef`        | protheus-mvc         | protheus-mvc           |
| `TReport`, `TRSection`, `TRCell`        | protheus-reports     | protheus-reports       |
| `MsDialog`, `FWMBrowse`, `MsGetDados`  | protheus-screens     | protheus-screens       |
| `Class`, `Method`, `Data`, `EndClass`   | tlpp-classes         | tlpp-classes           |

> **IMPORTANTE**: SEMPRE aplique tambem a skill `protheus-data-model` quando o codigo contiver qualquer acesso a dados (DbSeek, RecLock, MpSysOpenQuery, BeginSQL, TCQuery, DbUseArea, SELECT, INSERT, UPDATE, DELETE).

## Passos da Revisao

### Passo 1 - Classificar o Tipo de Codigo

Leia o fonte completo e identifique todos os padroes presentes na tabela de classificacao acima. Um fonte pode pertencer a mais de um tipo (ex: um REST endpoint que usa MVC internamente).

### Passo 2 - Ler as 4 Regras Base

Leia e internalize as regras dos seguintes arquivos:

1. `rules/security.md` - Regras de seguranca (SEC-01 a SEC-09)
2. `rules/performance.md` - Regras de performance (PERF-01 a PERF-10)
3. `rules/best-practices.md` - Regras de boas praticas (BP-01 a BP-10)
4. `rules/modernization.md` - Regras de modernizacao (MOD-01 a MOD-10)

### Passo 3 - Ler Skills Especificas do Tipo

Com base na classificacao do Passo 1, leia as skills adicionais correspondentes. Exemplo: se identificou padrao REST, leia a skill `protheus-rest`.

### Passo 4 - Analisar Cada Regra

Para cada regra dos arquivos lidos, verifique se o codigo viola ou atende ao criterio. Registre:

- **Regra violada**: codigo de referencia, trecho do codigo, explicacao, sugestao de correcao
- **Regra atendida**: apenas contabilize para o resumo final
- **Regra nao aplicavel**: ignore silenciosamente

### Passo 5 - Gerar Relatorio

Monte o relatorio no formato definido abaixo.

## Formato do Relatorio

```markdown
# Code Review - [Nome do Fonte]

## Resumo Executivo

- **Tipo(s) identificado(s)**: [lista dos tipos]
- **Total de violacoes**: X (Y criticas, Z warnings, W informativas)
- **Nota geral**: [A/B/C/D/F]

## Violacoes Encontradas

### CRITICAL

#### [REF-CODE] Titulo da Regra
- **Arquivo**: `fonte.prw` linha XX
- **Trecho**:
```advpl
// codigo com problema
```
- **Problema**: Descricao do problema
- **Correcao sugerida**:
```advpl
// codigo corrigido
```

### WARNING

#### [REF-CODE] Titulo da Regra
...

### INFO

#### [REF-CODE] Titulo da Regra
...

## Regras Atendidas

- [X] REF-CODE - Titulo (total: N regras atendidas)

## Recomendacoes Prioritarias

1. [Acao mais critica]
2. [Segunda acao]
3. [Terceira acao]
```

## Codigos de Referencia

| Prefixo  | Categoria        | Severidade Padrao |
|----------|------------------|-------------------|
| SEC-XX   | Seguranca        | CRITICAL / HIGH   |
| PERF-XX  | Performance      | WARNING / HIGH    |
| BP-XX    | Boas Praticas    | WARNING / INFO    |
| MOD-XX   | Modernizacao     | INFO              |
| JOB-XX   | Jobs/Schedule    | WARNING           |
| REST-XX  | REST API         | WARNING           |
| MVC-XX   | MVC              | WARNING           |
| CLS-XX   | Classes TLPP     | INFO              |
| DM-XX    | Modelo de Dados  | WARNING           |

## Criterios de Nota

| Nota | Criterio                                                        |
|------|-----------------------------------------------------------------|
| A    | Nenhuma violacao CRITICAL, max 2 WARNING                        |
| B    | Nenhuma violacao CRITICAL, max 5 WARNING                        |
| C    | Max 1 CRITICAL, max 8 WARNING                                   |
| D    | Max 3 CRITICAL ou mais de 8 WARNING                              |
| F    | Mais de 3 CRITICAL ou problemas graves de seguranca              |