# Referencia Complementar — Tabelas, Utils e Metricas

Arquivo de apoio ao SKILL.md. Consulte quando precisar de detalhes sobre:
- Tabelas por modulo com campos e indices alternativos
- Funcoes utilitarias do time por projeto
- Metricas para priorizacao de refatoracao

---

## Tabelas por Modulo

### Cadastros Base

| Tabela | Refs | Descricao | Chave Ordem 1 |
|--------|------|-----------|---------------|
| SA1 | 29.681 | Clientes | A1_FILIAL+A1_COD+A1_LOJA |
| SA2 | 20.282 | Fornecedores | A2_FILIAL+A2_COD+A2_LOJA |
| SB1 | 23.675 | Produtos | B1_FILIAL+B1_COD |
| SB2 | 3.981 | Saldos em Estoque | B2_FILIAL+B2_COD+B2_LOCAL |
| SB5 | 3.148 | Dados Compl. Produtos | B5_FILIAL+B5_COD |
| SA4 | 2.428 | Transportadoras | A4_FILIAL+A4_COD |
| SA5 | 1.785 | Contatos | A5_FILIAL+A5_FORNECE+A5_LOJA+A5_NOMECOM |
| SM0 | 19.526 | Empresas/Filiais | M0_CODIGO+M0_CODFIL |

### Faturamento (SIGAFAT)

| Tabela | Refs | Descricao | Chave Ordem 1 |
|--------|------|-----------|---------------|
| SF2 | 35.656 | Cab. NF Saida | F2_FILIAL+F2_DOC+F2_SERIE+F2_CLIENTE+F2_LOJA |
| SD2 | 19.623 | Itens NF Saida | D2_FILIAL+D2_DOC+D2_SERIE+D2_CLIENTE+D2_LOJA+D2_COD+D2_ITEM |
| SC5 | 14.927 | Cab. Pedido Venda | C5_FILIAL+C5_NUM |
| SC6 | 10.548 | Itens Pedido Venda | C6_FILIAL+C6_NUM+C6_ITEM+C6_PRODUTO |
| SC9 | 2.783 | Liberacao Pedidos | C9_FILIAL+C9_PEDIDO+C9_ITEM |
| DA3 | 3.342 | Desconto por Cliente | DA3_FILIAL+DA3_CODTAB+DA3_ITEM |

### Compras (SIGACOM)

| Tabela | Refs | Descricao | Chave Ordem 1 |
|--------|------|-----------|---------------|
| SF1 | 28.165 | Cab. NF Entrada | F1_FILIAL+F1_DOC+F1_SERIE+F1_FORNECE+F1_LOJA+F1_TIPO |
| SD1 | 23.211 | Itens NF Entrada | D1_FILIAL+D1_DOC+D1_SERIE+D1_FORNECE+D1_LOJA+D1_COD+D1_ITEM |
| SC7 | 8.962 | Pedidos Compra | C7_FILIAL+C7_NUM+C7_ITEM+C7_SEQUEN |
| SC1 | 2.429 | Solic. Compra | C1_FILIAL+C1_NUM+C1_ITEM |

### Fiscal (SIGAFIS)

| Tabela | Refs | Descricao | Chave Ordem 1 |
|--------|------|-----------|---------------|
| SF3 | 19.392 | Livros Fiscais | F3_FILIAL+F3_CFO+F3_ESTADO |
| SF4 | 10.895 | TES (Tipos Ent/Saida) | F4_FILIAL+F4_CODIGO |

### Financeiro (SIGAFIN)

| Tabela | Refs | Descricao | Chave Ordem 1 |
|--------|------|-----------|---------------|
| SE1 | 18.486 | Titulos a Receber | E1_FILIAL+E1_PREFIXO+E1_NUM+E1_PARCELA+E1_TIPO |
| SE2 | 13.191 | Titulos a Pagar | E2_FILIAL+E2_PREFIXO+E2_NUM+E2_PARCELA+E2_TIPO+E2_FORNECE+E2_LOJA |
| SE5 | 4.112 | Movimentacao Bancaria | E5_FILIAL+E5_DATA+E5_SEQ |

### Estoque / PCP

| Tabela | Refs | Descricao | Chave Ordem 1 |
|--------|------|-----------|---------------|
| SD3 | 4.895 | Movimentacoes Internas | D3_FILIAL+D3_DOC+D3_COD+D3_ITEM |
| SC2 | 4.544 | Ordens Producao | C2_FILIAL+C2_NUM+C2_ITEM+C2_SEQUEN |

### Logistica / GFE / TMS

| Tabela | Refs | Descricao |
|--------|------|-----------|
| CD2 | 21.792 | Documentos de Carga (GFE) |
| DT6 | 3.426 | Romaneio (TMS) |