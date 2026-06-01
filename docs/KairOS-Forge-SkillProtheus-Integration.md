# Guia de Integração: KairOS-Forge → SkillProtheus

**Documento de Referência**  
**Data:** Junho de 2026  
**Autor:** Fernando Alemar  
**Repositório:** https://github.com/FernandoAlemar/SkillProtheus

---

## 📋 Sumário Executivo

Este documento apresenta como aplicar os conceitos e arquitetura do **KairOS-Forge** (fábrica de software autônoma com 45 agentes em times coordenados) no seu projeto **SkillProtheus** (18 skills especializadas em ADVPL/TLPP para Protheus).

### Ganhos Esperados
- ✅ **Rastreabilidade**: Features com SPEC, gates e validação
- ✅ **Autonomia**: Agentes (personas) coordenados em squads
- ✅ **Qualidade**: Ciclos plan → execute → validate → review → audit
- ✅ **Escalabilidade**: Squads de apoio para artefatos textuais (docs, naming, segurança)

---

## 🏗️ 1. Estrutura de Squads/Times Autônomos

### 1.1 Visão Geral Atual

#### SkillProtheus Hoje
18 skills especializadas em categorias:
- **Planejamento**: `protheus-plan`
- **Implementação**: `protheus-exec`, `protheus-mvc`, `protheus-rest`, `protheus-jobs`, `protheus-reports`, etc.
- **Dados**: `protheus-data-model`, `advpl-embedded-sql`
- **Qualidade**: `code-review`, `teste-de-mesa`, `tir-tests`
- **Suporte**: `advpl-debugging`, `advpl-tlpp-migration`, `business-modules`

#### KairOS-Forge Paralelo
45 agentes em 16 times (24 core + 21 apoio) com personas explícitas, cada um com:
- Especialidade (frontend, backend, dados, QA, DevOps)
- Comportamento/tom
- Allow-list de funcionalidades
- Integração com squads de apoio

### 1.2 Modelo de Squads Proposto para SkillProtheus

```
SKILLPROTHEUS
│
├── 👩‍💼 SQUAD PLANEJAMENTO
│   ├─ Laura (Tech Lead)          [Orquestra: protheus-plan]
│   ├─ Diego (Arquiteto)          [Valida TDN e componentes]
│   └─ Fernanda (DBA/Dados)       [Valida dicionário]
│
├── ⚙️ SQUAD IMPLEMENTAÇÃO
│   ├─ Lucas (Backend)            [protheus-exec, protheus-jobs]
│   ├─ Marina (Frontend)          [protheus-mvc, protheus-screens]
│   ├─ Gabriel (IA/Integrações)   [protheus-rest]
│   ├─ Carlos (DBA)               [protheus-data-model, SQL]
│   ├─ Juliana (ETL)              [advpl-embedded-sql]
│   ├─ Beatriz (Docs)             [Documentação artefatos]
│   └─ Pablo (Padrões)            [tlpp-classes]
│
├── ✅ SQUAD QUALIDADE
│   ├─ Patrícia (QA Lead)         [code-review, validação]
│   ├─ Ricardo (Testes)           [teste-de-mesa, tir-tests]
│   ├─ Helena (Security)          [Análise de risco]
│   └─ Vinícius (Performance)     [Otimização]
│
└── 📡 SQUADS DE APOIO (Textuais - nunca codificam)
    ├─ apoio-naming              [Nomenclatura ADVPL/TLPP]
    ├─ apoio-seguranca           [Validação segurança (LGPD, PII, financeiro)]
    ├─ apoio-documentacao        [ADR, decisões técnicas]
    └─ apoio-acoplamento-dados   [Análise brownfield]
```

### 1.3 Mapping: Skills → Agentes

| Skill | Agente Primary | Squad | Quando |
|-------|---|---|---|
| `protheus-plan` | Laura | Planejamento | Feature nova, refatoração |
| `business-modules` | Diego | Planejamento | Validação regra de negócio |
| `protheus-data-model` | Carlos + Fernanda | Planejamento/Implantação | Qualquer acesso a DB |
| `protheus-exec` | Lucas | Implementação | Executar plano aprovado |
| `protheus-mvc` | Marina | Implementação | Cadastro MVC/FWBrowse |
| `protheus-screens` | Marina | Implementação | Tela dialog/clássico |
| `protheus-rest` | Gabriel | Implementação | API REST |
| `protheus-jobs` | Lucas | Implementação | Job/Schedule |
| `protheus-reports` | Juliana | Implementação | Relatório/Excel/PDF |
| `advpl-embedded-sql` | Juliana | Implementação | Query com BeginSQL |
| `tlpp-classes` | Pablo | Implementação | Classe TLPP/OOP |
| `advpl-tlpp-migration` | Pablo | Implementação | Migrar .prw → .tlpp |
| `code-review` | Patrícia | Qualidade | Revisão de PR |
| `teste-de-mesa` | Ricardo | Qualidade | Análise estática profunda |
| `tir-tests` | Ricardo | Qualidade | Teste E2E interface |
| `advpl-debugging` | Vinícius | Qualidade | Debug/error/performance |

---

## 🔄 2. Ciclo Orquestrado: Plan → Execute → Validate → Review → Audit

### 2.1 Fluxo Completo (estilo KairOS-Forge)

```
┌─────────────────────────────────────────────────┐
│  /skill-protheus:onboardar                      │
│  Entrevista 5 questões + contexto do projeto    │
└──────────────┬──────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────┐
│  /skill-protheus:mapear-arquitetura             │
│  (Opcional) Brownfield: inventário + plano      │
└──────────────┬──────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────┐
│  /skill-protheus:especificar <ideia>            │
│  Laura aciona Diego, Fernanda → SPEC-NNN        │
│  (Saída: plano rastreável com componentes)      │
└──────────────┬──────────────────────────────────┘
               ↓
        [Aprovação do Usuário]
               ↓
┌─────────────────────────────────────────────────┐
│  /skill-protheus:rodar [squad|skill]            │
│  Modo conversacional sequencial                 │
│  • Lucas (Backend) → Gabriel (REST) → Carlos    │
│  • Ricardo (Testes)                             │
└──────────────┬──────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────┐
│  /skill-protheus:validar SPEC-NNN               │
│  Ricardo + Patrícia validam contra requisitos   │
│  e gates (compilação, testes, segurança)        │
└──────────────┬──────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────┐
│  /skill-protheus:rodar apoio-seguranca          │
│  Helena analisa risco (LGPD, PII, financeiro)   │
└──────────────┬──────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────┐
│  /skill-protheus:revisar                        │
│  Patrícia + Helena + Ricardo → code-review      │
│  Pre-PR: segurança, performance, boas práticas  │
└──────────────┬──────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────┐
│  [MERGE PR]                                     │
└──────────────┬──────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────┐
│  /skill-protheus:auditar                        │
│  Semanal: pontuação 0-100 em 5 dimensões        │
│  • Fundação (estrutura, padrões)                │
│  • Pipeline (testes, cobertura)                 │
│  • Guardrails (segurança, performance)          │
│  • Conhecimento (documentação)                  │
│  • Estrutura (modularidade, acoplamento)        │
└──────────────┬──────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────┐
│  /skill-protheus:evoluir                        │
│  Pós-auditoria: 1 capacidade nova/semana        │
│  (refatoração, otimização, nova skill)          │
└─────────────────────────────────────────────────┘
```

### 2.2 Skills Orquestradoras Novas

#### `/skill-protheus:onboardar`
**Fase:** Inicial (primeira sessão)  
**Orquestrador:** Laura

**Fluxo:**
1. Pergunta 1: "Qual é o escopo do seu projeto? (Novo / Brownfield)"
2. Pergunta 2: "Qual é o módulo principal? (Vendas, Compras, Financeiro, etc.)"
3. Pergunta 3: "Tem integrações externas? (REST, XML, arquivo)"
4. Pergunta 4: "Qual nível de compliance? (Padrão / LGPD / Fiscal)"
5. Pergunta 5: "Qual é a prioridade? (Rapidez / Qualidade / Segurança)"

**Saída:** Perfil do projeto + skills recomendadas para primeira feature

---

#### `/skill-protheus:mapear-arquitetura`
**Fase:** Inicial (opcional, brownfield)  
**Orquestrador:** Diego + Fernanda

**Entrada:** Repositório existente  
**Fluxo:**
1. Inventário: quantas funções, classes, tabelas
2. Acoplamento: análise de dependências entre módulos
3. Dívida técnica: identificar anti-patterns
4. Plano de decomposição: sprints de refatoração

**Saída:** Documento `arquitetura-brownfield.md` com riscos e roadmap

---

#### `/skill-protheus:especificar <ideia>`
**Fase:** Planejamento  
**Orquestrador:** Laura  
**Acionados:** Diego (TDN), Fernanda (dicionário), especialista regra (business-modules)

**Entrada:** Descrição informal da ideia  
**Fluxo:**
1. **Análise de Requisitos** — Laura estrutura a ideia
2. **Validação TDN** — Diego aprova ou pede ajustes (DB?, tabelas?, campos?)
3. **Validação Dicionário** — Fernanda confirma se campos/tabelas existem ou precisam ser criados
4. **Identificar Skill** — Qual tipo? (MVC? REST? Job? Integ?)
5. **Gerar SPEC** — Documento `SPEC-NNN.md` com componentes, dependências, riscos

**Saída:** Arquivo `SPEC-NNN.md` rastreável

**Exemplo SPEC-001:**
```markdown
# SPEC-001: Sincronizar Pedidos para CRM

**Solicitado por:** Gerente Vendas  
**Tech Lead:** Laura  
**Data:** 2026-06-01  
**Status:** ✅ Aprovado

## 📌 Resumo
Integrar pedidos (SC5) do Protheus com CRM externo via REST.

## ✅ Requisitos
- [ ] Sincronizar novos pedidos (SC5) em tempo real
- [ ] Incluir dados do cliente (SA1)
- [ ] Retry automático em caso de falha
- [ ] Log auditável

## 🛠️ Componentes

| Tipo | Artefato | Skill | Owner | Status |
|------|----------|-------|-------|--------|
| API | POST /crm/pedidos | protheus-rest | Gabriel | ⏳ |
| Job | Sincronizador | protheus-jobs | Lucas | ⏳ |
| Tabela | SC5, SA1 | protheus-data-model | Carlos | ✅ |
| Query | Extrato SC5 | advpl-embedded-sql | Juliana | ⏳ |
| Testes | E2E CRM | tir-tests | Ricardo | ⏳ |

## 🚨 Validações
- TDN: ✅ Diego
- Dicionário: ✅ Fernanda
- Segurança: ⏳ Helena
- Performance: ⏳ Vinícius

## 🔗 Dependências
- SPEC-000 (configuração base)
- Tabela SF2 (faturamento) — compatível

## ⚠️ Riscos
| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| CRM indisponível | Alto | Retry + fila local |
| Descalibro data | Médio | Testes E2E |
```

---

#### `/skill-protheus:validar SPEC-NNN`
**Fase:** Pós-implementação  
**Orquestrador:** Patrícia (QA Lead)  
**Validadores:** Ricardo (testes), Helena (segurança)

**Entrada:** `SPEC-NNN.md` + código implementado  
**Fluxo:**
1. ✅ **Gates obrigatórios:**
   - Compilação sem warnings
   - Cobertura testes ≥ 80%
   - Code review aprovado
   - Segurança validada (LGPD, PII, auth)

2. ✅ **Validação de Requisitos:**
   - Cada req. em SPEC tem caso de teste?
   - Todos os cenários cobertos?

3. ✅ **Saída:** `SPEC-NNN-validacao.md` com resultado (Aceito / Rejeitar + motivos)

---

#### `/skill-protheus:revisar`
**Fase:** Pré-PR  
**Orquestrador:** Patrícia (QA Lead)  
**Revisores:** Helena (segurança), Ricardo (testes), especialista por tipo (MVC/REST/Job)

**Entrada:** Código pronto para PR  
**Fluxo:**
1. **Classificação automática** — detecta tipo (MVC, REST, Job, etc.)
2. **Ativa skills relevantes:**
   - `code-review` (sempre)
   - `protheus-data-model` (se houver DB)
   - `protheus-rest` (se for API)
   - `protheus-jobs` (se for job)
   - etc.
3. **Dimensões de revisão:**
   - 🔒 Segurança (LGPD, auth, validação)
   - ⚡ Performance (queries, locks)
   - 📐 Boas práticas (nomeação, padrões)
   - 🚀 Modernização (TLPP vs ADVPL, OOP)

**Saída:** Relatório com achados + score de aprovação

---

#### `/skill-protheus:auditar`
**Fase:** Semanal (pós-merge)  
**Orquestrador:** Vinícius (Observabilidade)

**Entrada:** Histórico de semana (PRs merged, bugs abertos/fechados)  
**Fluxo:**
1. **Fundação (0-20)** — padrões, estrutura, nomenclatura consistentes?
2. **Pipeline (20-40)** — testes, cobertura, compilação clean?
3. **Guardrails (40-60)** — segurança, performance, logs auditáveis?
4. **Conhecimento (60-80)** — documentação, comentários, ADRs?
5. **Estrutura (80-100)** — modularidade, couplamento baixo, escalabilidade?

**Saída:** Scorecard semanal (0-100) + top 3 prioridades de evolução

---

#### `/skill-protheus:evoluir`
**Fase:** Semanal (pós-auditoria)  
**Orquestrador:** Laura (Tech Lead)

**Entrada:** Resultado de `/auditar`  
**Fluxo:**
1. Identificar 1 capacidade nova por semana:
   - Refatoração em módulo baixo score?
   - Nova pattern/template?
   - Nova skill técnica?
   - Automação de processo?
2. Propor plano de melhoria
3. Priorizar para sprint seguinte

**Saída:** Épica `EVOL-NNN` para roadmap

---

### 2.3 Fluxo Simplificado para Bug Fixes

Nem toda mudança precisa de SPEC completa. Para bug fixes isolados:

```
Bug relatado
    ↓
/skill-protheus:rodar [especialista]
(Ex.: /skill-protheus:rodar teste-de-mesa)
    ↓
/skill-protheus:revisar
    ↓
MERGE
```

---

## 🛠️ 3. Squads de Apoio (Artefatos Textuais)

KairOS-Forge tem 21 agentes de apoio em 7 squads. Adaptar 4 principais para Protheus:

### 3.1 apoio-naming 🏷️

**Agentes:** Elisa (Naming), Bruno, Cora  
**Quando:** Antes de planejar ou durante design review  
**Saída:** Documento de naming conventions

**Contexto Protheus:**
- Nomenclatura em ADVPL/TLPP seguindo padrões TOTVS
- Variáveis: `cVariavel`, `nNumero`, `aArray`
- Funções: `u_ProcessarPedido()`, `ValidarCliente()`
- Classes: `PedidoController`, `ClienteRepository`
- Constantes: `cMODULO := "02"`

**Ativar com:**
```
/skill-protheus:rodar apoio-naming
```

**Saída:** Documento `naming-SPEC-NNN.md`

---

### 3.2 apoio-seguranca 🔐

**Agentes:** Helena (Security), especialista LGPD  
**Quando:** Features com dados sensíveis (auth, PII, pagamento, fiscal)  
**Saída:** Análise de risco + checklist de validação

**Validações Protheus:**
- Autenticação: OAuth2? Bearer token?
- PII: CNPJ, CPF, email — criptografado?
- Fiscal: Seguir regras SEFAZ/NF-e?
- Auditoria: Quem? Quando? O quê? (log completo)
- Acesso: Permissões por módulo/tabela?

**Ativar com:**
```
/skill-protheus:rodar apoio-seguranca
```

**Saída:** Documento `seguranca-SPEC-NNN.md` + checklist

---

### 3.3 apoio-documentacao 📝

**Agentes:** Beatriz (Docs), Felipe (API Docs)  
**Quando:** Após implementação, pré-merge  
**Saída:** ADR, decisões técnicas, exemplos de uso

**Artefatos para Protheus:**
- **ADR-NNNN.md** — decisão arquitetural (por quê escolhemos REST vs batch?)
- **API-docs.md** — endpoints, exemplos curl
- **Data-dictionary.md** — mapeamento campos SPEC → tabelas
- **Integration-guide.md** — como consumir a feature

**Ativar com:**
```
/skill-protheus:rodar apoio-documentacao
```

**Saída:** Pasta `docs/SPEC-NNN/` com ADR, API docs, exemplos

---

### 3.4 apoio-acoplamento-dados 🔄

**Agentes:** Álvaro (Revisão Arquitetural), especialista brownfield  
**Quando:** Feature que toca múltiplas tabelas ou módulos  
**Saída:** Análise de dependências, risco de cascata, plano de decomposição

**Análises:**
- Mapeamento de tabelas afetadas
- Dependências entre módulos
- Risco de cascata (1 mudança afeta tudo?)
- Sugestões de decomposição/refatoração

**Ativar com:**
```
/skill-protheus:rodar apoio-acoplamento-dados
```

**Saída:** Documento `acoplamento-SPEC-NNN.md` + diagrama

---

## 📁 4. Estrutura de Diretórios Proposta

```
SkillProtheus/
├── README.md                           ← Índice principal + fluxo
├── LICENSE
├── .gitignore
│
├── .claude-plugin/
│   └── marketplace.json                ← Catalog Claude Code
├── .agents/plugins/
│   └── marketplace.json                ← Catalog Codex CLI
│
├── agents/                             ← NOVO: Personas/Agentes
│   ├── AGENTS.md                       ← Manifesto dos agentes
│   ├── laura.md                        (Tech Lead - Orquestração)
│   ├── diego.md                        (Arquiteto - Validação TDN)
│   ├── fernanda.md                     (DBA - Dados)
│   ├── lucas.md                        (Backend - Exec)
│   ├── marina.md                       (Frontend - Screens/MVC)
│   ├── gabriel.md                      (IA/Integ - REST)
│   ├── carlos.md                       (DBA - Data Model)
│   ├── juliana.md                      (ETL - SQL)
│   ├── beatriz.md                      (Docs)
│   ├── pablo.md                        (Padrões - Classes)
│   ├── patricia.md                     (QA Lead - Review)
│   ├── ricardo.md                      (QA - Testes)
│   ├── helena.md                       (Security)
│   └── vinicius.md                     (Performance)
│
├── skills/
│   ├── README.md                       ← Guia de skills (este arquivo)
│   │
│   ├── protheus-plan/
│   │   └── SKILL.md
│   ├── protheus-exec/
│   │   └── SKILL.md
│   ├── protheus-loop/
│   │   └── SKILL.md
│   │
│   ├── protheus-mvc/
│   │   └── SKILL.md
│   ├── protheus-screens/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── protheus-rest/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── protheus-jobs/
│   │   └── SKILL.md
│   ├── protheus-reports/
│   │   ├── SKILL.md
│   │   └── references/
│   │
│   ├── protheus-data-model/
│   │   ├── SKILL.md
│   │   ├── tabelas-modulos.md
│   │   ├── references/
│   │   ├── scripts/
│   │   └── dicionario/
│   ├── advpl-embedded-sql/
│   │   └── SKILL.md
│   ├── advpl-debugging/
│   │   └── SKILL.md
│   ├── advpl-tlpp-language/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── advpl-tlpp-migration/
│   │   └── SKILL.md
│   ├── tlpp-classes/
│   │   └── SKILL.md
│   │
│   ├── business-modules/
│   │   ├── SKILL.md
│   │   ├── compras.md
│   │   ├── faturamento.md
│   │   ├── financeiro.md
│   │   ├── estoque.md
│   │   ├── fiscal.md
│   │   ├── contabilidade.md
│   │   ├── manutencao.md
│   │   └── pcp.md
│   │
│   ├── code-review/
│   │   ├── SKILL.md
│   │   └── rules/
│   ├── teste-de-mesa/
│   │   └── SKILL.md
│   ├── tir-tests/
│   │   └── SKILL.md
│   │
│   └── apoio/                          ← NOVO: Squads de apoio (textuais)
│       ├── apoio-naming/
│       │   └── SKILL.md
│       ├── apoio-seguranca/
│       │   └── SKILL.md
│       ├── apoio-documentacao/
│       │   └── SKILL.md
│       └── apoio-acoplamento-dados/
│           └── SKILL.md
│
├── docs/
│   ├── adr/                            ← Architecture Decision Records
│   │   ├── 0001-estrutura-agentes.md
│   │   ├── 0002-ciclo-orquestrado.md
│   │   └── ...
│   ├── templates/
│   │   ├── SPEC-template.md
│   │   ├── ADR-template.md
│   │   └── validacao-template.md
│   ├── exemplos/
│   │   └── SPEC-001-exemplo.md
│   └── integracao-kairos/              ← NOVO
│       └── KairOS-Forge-SkillProtheus-Integration.md
│
└── scripts/
    ├── sync-multi-cli.py               (sync agents entre plataformas)
    ├── sync-dicionario.py              (já existe)
    └── generate-spec.py                ← NOVO (scaffold SPEC a partir de template)
```

---

## 💾 5. Exemplo Prático: Primeira SPEC

### 5.1 Input do Usuário
```
Quero exportar relatórios mensais em CSV, com dados de pedidos, 
clientes e vendedor, agrupado por região.
```

### 5.2 Execução: `/skill-protheus:especificar`

**Laura (Tech Lead):**
> Ótimo! Vou estruturar isso. Diego, você valida a TDN? Fernanda, dicionário?

**Diego (Arquiteto):**
> Preciso de: SC5 (pedidos), SA1 (cliente), SA3 (vendedor), região — qual tabela tem região?

**Fernanda (DBA):**
> Encontrei: SA1.A1_ESTC (estado) ou custom Z* para região? Vou verificar dicionário...
> ✅ OK: SA1, SC5, SA3 existem. Precisa de campo customizado para região.

**Laura:**
> Perfeito! Vou gerar a SPEC...

### 5.3 Output: `SPEC-001.md`

```markdown
# SPEC-001: Exportar Relatório Mensal de Pedidos por Região

**Solicitado por:** Gerente Operacional  
**Tech Lead:** Laura  
**Arquiteto:** Diego  
**DBA:** Fernanda  
**Data:** 2026-06-01  
**Status:** ✅ Aprovado

## 📌 Resumo
Gerar relatório mensal em CSV com pedidos, clientes, vendedores, 
agrupado por região (estado ou custom Z_REGIAO).

## ✅ Requisitos Funcionais
- [ ] Extrair pedidos do mês (SC5.C5_EMISSAO)
- [ ] Incluir cliente (SA1.A1_NOME, A1_CNPJ)
- [ ] Incluir vendedor (SA3.A3_NOME)
- [ ] Incluir região (SA1.A1_ESTC ou Z_REGIAO)
- [ ] Gerar CSV com delimitador `;`
- [ ] Permitir download direto no Protheus

## ✅ Requisitos Não-Funcionais
- Relatório < 30s para 100k linhas
- Arquivo max 50MB
- Retenção 3 meses em servidor

## 🛠️ Componentes

| Componente | Tipo | Artefato | Skill | Owner | Esforço |
|-----------|------|----------|-------|-------|---------|
| Tela de parâmetros | Tela | U_RELPED01 | protheus-screens | Marina | 4h |
| Rotina principal | Função | U_GERPED01 | protheus-exec | Lucas | 6h |
| Query pedidos | SQL | BeginSQL | advpl-embedded-sql | Juliana | 3h |
| Geração CSV | Utilitário | U_CSVPED01 | protheus-reports | Juliana | 4h |
| Testes E2E | Testes | TESTCASE_001.py | tir-tests | Ricardo | 5h |

**Total:** ~22h | **Timeline:** 3 dias (1 dev)

## 📋 Tabelas Afetadas

| Tabela | Operação | Campos | Status |
|--------|----------|--------|--------|
| SC5 | SELECT | C5_EMISSAO, C5_NUM, C5_VALOR | ✅ |
| SA1 | SELECT | A1_NOME, A1_CNPJ, A1_ESTC | ✅ |
| SA3 | SELECT | A3_NOME, A3_CODIGO | ✅ |
| Z_REGIAO | SELECT | Z_REG_ESTC, Z_REG_NOME | ⏳ (validar existência) |

## 🚨 Validações Técnicas

| Validação | Owner | Status |
|-----------|-------|--------|
| TDN | Diego | ✅ Aprovado |
| Dicionário | Fernanda | ✅ Aprovado (Z_REGIAO a confirmar) |
| Segurança | Helena | ⏳ (dados sensíveis: CNPJ → validar mascaramento) |
| Performance | Vinícius | ⏳ (100k linhas + índices) |

## 🔗 Dependências
- Nenhuma

## ⚠️ Riscos

| Risco | Impacto | Probab. | Mitigação |
|-------|---------|---------|-----------|
| Z_REGIAO não existe | Alto | Alta | Usar A1_ESTC como fallback |
| Performance Query | Médio | Média | Índice em C5_EMISSAO + SA1.A1_ESTC |
| PII (CNPJ) | Alto | Alta | Validar mascaramento com Helena |

## 📌 Próximos Passos
1. ✅ Confirmar existência de Z_REGIAO com Fernanda
2. ✅ Validação de segurança (CNPJ mascarado?) com Helena
3. → `/skill-protheus:rodar` (implementação)
4. → `/skill-protheus:validar SPEC-001`
```

---

## 🚀 6. Implementação Passo a Passo

### 6.1 Fase 1: Setup (1-2 semanas)

- [ ] Criar pasta `agents/` com 15 arquivos `.md` (personas)
- [ ] Criar skill `/onboardar` (entrevista 5q)
- [ ] Criar skill `/mapear-arquitetura` (brownfield)
- [ ] Criar skill `/especificar` (orquestradora)
- [ ] Criar skill `/validar` (gates)
- [ ] Criar skill `/revisar` (pre-PR)
- [ ] Criar skill `/auditar` (semanal)
- [ ] Criar skill `/evoluir` (semanal)
- [ ] Criar 4 skills de apoio (naming, segurança, docs, acoplamento)

### 6.2 Fase 2: Integração (2-3 semanas)

- [ ] Refatorar `README.md` com nova estrutura de squads
- [ ] Criar templates: `SPEC-template.md`, `ADR-template.md`, `validacao-template.md`
- [ ] Criar exemplo completo: `SPEC-001-exemplo.md`
- [ ] Criar documentação de ADRs (decisões arquiteturais)

### 6.3 Fase 3: Automação (2-3 semanas)

- [ ] Script `sync-multi-cli.py` (compatibilidade Claude Code/Codex)
- [ ] Script `generate-spec.py` (scaffold SPEC a partir de template)
- [ ] Validação automática de gates (compilação, testes, review)

### 6.4 Fase 4: Rollout (1 semana)

- [ ] Teste interno com 1 feature
- [ ] Publicar no marketplace
- [ ] Treinar time

---

## 🎯 7. Métricas de Sucesso

| Métrica | Baseline | Target (3 meses) |
|---------|----------|------------------|
| Features com SPEC | 0% | 100% |
| Tempo plan → deploy | 5 dias | 3 dias |
| Taxa revisão (defects/1k LOC) | 15 | < 5 |
| Cobertura testes | 60% | ≥ 85% |
| Tempo code-review | 2h | < 30min |
| Auditoria semanal score | - | ≥ 75 |

---

## 📚 8. Referências

### KairOS-Forge
- **Repo:** https://github.com/VilelaAI/KairOS-Forge
- **45 agentes** em 16 times + 10 skills + squads de apoio
- **Ciclo completo:** plan → exec → validate → review → audit → evolve

### SkillProtheus
- **Repo:** https://github.com/FernandoAlemar/SkillProtheus
- **18 skills** + dicionário Protheus com ~11k tabelas

### Compatibilidade
- Claude Code
- Codex CLI
- OpenCode

---

## ❓ FAQ

**P: Preciso refatorar tudo agora?**  
R: Não. Comece com 1 feature pequena (2-3 componentes) usando o fluxo novo. Depois expande.

**P: E bugs simples / hotfixes?**  
R: Use fluxo simplificado: rodar + revisar + merge (sem SPEC formal).

**P: Quem é "Laura"? É um agente real?**  
R: Não. É um rótulo (Tech Lead). Pode ser você, outro dev, ou até o próprio Cursor/Codex atuando no papel.

**P: Preciso de 15 agentes no meu time?**  
R: Não. Adapte aos papéis reais. Mínimo: Tech Lead + Arquiteto + QA. Máximo: conforme escala.

**P: Como validar segurança/performance?**  
R: Squads de apoio (`apoio-seguranca`, `apoio-acoplamento-dados`) geram artefatos textuais.

**P: Quando usar `/protheus-loop` vs `/skill-protheus:rodar`?**  
R: `/loop` é para features 3+ componentes ou multi-módulo (plan → exec → test → review em iteração).  
`/rodar` é conversacional, sequencial, mais simples.

---

## 🎓 Conclusão

Integrar os conceitos de **KairOS-Forge** no **SkillProtheus** trará:

1. ✅ **Rastreabilidade** de features com SPECs versão-controladas
2. ✅ **Autonomia** via agentes coordenados em squads
3. ✅ **Qualidade** com gates automáticos (compilação, testes, review)
4. ✅ **Escalabilidade** com squads de apoio (sem código, só artefatos)
5. ✅ **Observabilidade** semanal (auditoria + evolução)

Isso transforma **18 skills técnicas** em uma **fábrica de software coordenada por agentes**, gerando valor continuamente.

---

**Versão:** 1.0  
**Data:** Junho de 2026  
**Autor:** Fernando Alemar  
**Status:** ✅ Documento Completo
