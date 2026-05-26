---
name: business-modules
description: >
  Referencia dos 8 principais modulos de negocio do TOTVS Protheus -
  Compras, Faturamento, Financeiro, Estoque, Fiscal, Contabilidade, Manutencao e PCP.
  Contem tabelas, rotinas, pontos de entrada, integracoes e regras de negocio para cada modulo.
---

# Modulos de Negocio - TOTVS Protheus

Esta skill serve como orquestradora para acessar o conhecimento funcional de cada modulo do Protheus. Ela direciona a leitura para os arquivos detalhados de cada area.

---

## 1. Regra de Carregamento

Para manter o foco e performance, siga estas diretrizes:
1. **Limite:** Leia no maximo **2 arquivos de modulo** por consulta.
2. **Contexto:** Se o usuario perguntar sobre integracao, leia os dois modulos envolvidos.
3. **Selecao:** Use a tabela de roteamento abaixo para identificar qual arquivo `.md` ler usando a ferramenta `view_file`.

## 2. Tabela de Roteamento

| Palavras-chave | Arquivo | Modulo |
|---|---|---|
| compras, pedido compra, solicitacao compra, fornecedor, SC1, SC7, SD1, SF1, SA2, SIGACOM | `compras.md` | Compras (COM) |
| faturamento, venda, pedido venda, NF saida, cliente, SC5, SC6, SC9, SF2, SD2, SA1, SIGAFAT | `faturamento.md` | Faturamento (FAT) |
| financeiro, contas pagar, contas receber, titulo, baixa, banco, SE1, SE2, SE5, SIGAFIN | `financeiro.md` | Financeiro (FIN) |
| estoque, saldo, movimentacao, inventario, custo medio, SB1, SB2, SD3, SIGAEST | `estoque.md` | Estoque (EST) |
| fiscal, imposto, ICMS, IPI, apuracao, TES, CFOP, SF3, SF4, SFT, SIGAFIS | `fiscal.md` | Fiscal (FIS) |
| contabilidade, lancamento, plano contas, balancete, CT1, CT2, SIGACTB | `contabilidade.md` | Contabilidade (CTB) |
| manutencao, equipamento, ordem servico, OS, ST9, STJ, SIGAMNT | `manutencao.md` | Manutencao de Ativos (MNT) |
| pcp, producao, ordem producao, MRP, estrutura, empenho, SC2, SD4, SG1, SIGAPCP | `pcp.md` | PCP |

## 3. Tabela de Integracoes entre Modulos

Use esta tabela para identificar quando e necessario ler mais de um arquivo de modulo:

| Modulo Origem | Modulo Destino | Tipo de Integracao | Descricao |
|---|---|---|---|
| Compras | Estoque | Entrada automatica | NF Entrada (SD1) gera movimentacao no estoque (SD3) |
| Compras | Financeiro | Titulo a pagar | NF Entrada (SF1) gera titulo no contas a pagar (SE2) |
| Compras | Fiscal | Escrituracao | NF Entrada gera lancamento fiscal (SF3) |
| Faturamento | Estoque | Baixa automatica | NF Saida (SD2) gera movimentacao de saida (SD3) |
| Faturamento | Financeiro | Titulo a receber | NF Saida (SF2) gera titulo no contas a receber (SE1) |
| Faturamento | Fiscal | Escrituracao | NF Saida gera lancamento fiscal (SF3) |
| Financeiro | Contabilidade | Lancamento contabil | Baixas e movimentacoes geram CT2 via LP |
| Estoque | Contabilidade | Lancamento contabil | Movimentacoes de estoque geram lancamentos via LP |
| PCP | Estoque | Requisicao/Devolucao | Empenho (SD4) consome material, apontamento gera entrada |
| Manutencao | Estoque | Requisicao pecas | OS consome pecas do estoque |

---

## 4. Uso das Ferramentas

Para acessar o conteudo de um modulo:
1. Identifique o arquivo na tabela acima.
2. Use `view_file` apontando para o caminho: `.agents/skills/business-modules/<arquivo>.md`.
3. Extraia as tabelas, campos e rotinas necessarios para o planejamento.

---

## 5. CROSS-REFERENCES

| Topico | Skill |
|--------|-------|
| Planejamento de Solucoes | `protheus-plan` |
| Padroes de Acesso a Dados | `protheus-data-model` |
| Desenvolvimento de Telas | `protheus-screens` |
| Desenvolvimento MVC | `protheus-mvc` |
