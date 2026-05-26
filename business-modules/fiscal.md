# Modulo Fiscal (FIS / SIGAFIS)

## Visao Geral

O modulo Fiscal (SIGAFIS) do TOTVS Protheus gerencia a escrituracao fiscal, apuracao de impostos, obrigacoes acessorias e integracao com o SPED. O codigo do modulo no Protheus eh **FIS** e o executavel padrao eh **SIGAFIS**.

Este modulo eh responsavel por:
- Escrituracao de livros fiscais de entrada e saida
- Apuracao de ICMS, IPI, PIS, COFINS, ISS e retencoes
- Geracao do SPED Fiscal (EFD ICMS/IPI)
- Geracao do SPED Contribuicoes (EFD PIS/COFINS)
- Configuracao e manutencao de TES (Tipo Entrada/Saida)
- Controle de NCM, CFOP, CST e aliquotas
- Calculo de substituicao tributaria (ICMS-ST)
- Calculo de DIFAL (Diferencial de Aliquota)
- Geracao e transmissao de NF-e/NFS-e

## Fluxo Principal

```
Notas Fiscais (Entrada SF1/SD1 e Saida SF2/SD2)
        |
        v
  Lancamentos Fiscais (SF3)
        |
        v
  Apuracao de Impostos
        |
        +---> ICMS (SFT/CDO): Debitos - Creditos = Saldo
        +---> IPI (SFT/CDO): Debitos - Creditos = Saldo
        +---> PIS/COFINS (SFT/CDO): Debitos - Creditos = Saldo (nao-cumulativo)
        +---> ISS: Apuracao por municipio
        |
        v
  SPED Fiscal (EFD ICMS/IPI) + SPED Contribuicoes (EFD PIS/COFINS)
        |
        v
  Guias de Recolhimento (DARE, DARF, GPS)
        |
        v
  Obrigacoes Acessorias (GIA, DCTF, DIRF, ECD, ECF)
```

**Variacoes do fluxo:**
- Regime Simples Nacional: Apuracao simplificada via DAS
- Lucro Presumido: PIS/COFINS cumulativo, IRPJ/CSLL por presuncao
- Lucro Real: PIS/COFINS nao-cumulativo com creditos, IRPJ/CSLL pelo lucro efetivo
- Substituicao Tributaria: ICMS-ST recolhido antecipadamente pelo substituto
- Importacao: Impostos especificos (II, IPI vinculado, PIS/COFINS importacao)

## Tabelas Principais

| Tabela | Descricao | Chave Primaria | Indices Principais | Relacionamentos |
|---|---|---|---|---|
| SF3 | Livros Fiscais | F3_FILIAL+F3_CFO+F3_NFISCAL+F3_SERIE+F3_CLIEFOR+F3_LOJA+F3_IDENTFT | F3_FILIAL+F3_NFISCAL+F3_SERIE+F3_CLIEFOR; F3_FILIAL+F3_ENTRADA; F3_FILIAL+F3_CFO | SF1/SF2 (NF origem), SF4 (TES) |
| SFT | Itens Fiscais / Apuracao | FT_FILIAL+FT_TIPOMOV+FT_NFISCAL+FT_SERIE+FT_CLIEFOR+FT_LOJA+FT_PRODUTO+FT_ITEM | FT_FILIAL+FT_NFISCAL+FT_SERIE; FT_FILIAL+FT_PRODUTO | SF3 (livro fiscal), SB1 (produto) |
| CDO | Apuracao de ICMS | CDO_FILIAL+CDO_PERIOD+CDO_TIPOMV+CDO_SEQ | CDO_FILIAL+CDO_PERIOD; CDO_FILIAL+CDO_TIPOMV | SF3 (livros fiscais) |
| CDA | Apuracao de ICMS-ST | CDA_FILIAL+CDA_PERIOD+CDA_SEQ | CDA_FILIAL+CDA_PERIOD | SF3 (livros fiscais com ST) |
| SF4 | Tipo de Entrada e Saida (TES) | F4_FILIAL+F4_CODIGO | F4_FILIAL+F4_CODIGO | SD1/SD2 (itens NF), SF3 (livro fiscal) |
| SFB | Tabela de NCM | FB_FILIAL+FB_NCM | FB_FILIAL+FB_NCM | SB1 (produto via B1_POSIPI) |
| CC2 | Amarracao CFOP | CC2_FILIAL+CC2_CODTAB+CC2_EST+CC2_CFOP | CC2_FILIAL+CC2_CODTAB | SF4 (TES) |
| SFC | Tabela de CST | FC_FILIAL+FC_CODIGO+FC_TIPO | FC_FILIAL+FC_CODIGO | SF4 (TES) |
| CDH | DIFAL - Diferencial de Aliquota | CDH_FILIAL+CDH_ESTADO+CDH_ALIQ | CDH_FILIAL+CDH_ESTADO | Calculo DIFAL |

## Rotinas Padrao

| Codigo | Nome | Tipo |
|---|---|---|
| MATA950 | Lancamento Fiscal Manual | Cadastro |
| MATXFISA | Apuracao de ICMS | Processo |
| MATXFISB | Apuracao de IPI | Processo |
| MATXFISC | Apuracao de PIS/COFINS | Processo |
| SPEDFISCAL | SPED Fiscal (EFD ICMS/IPI) | Processo |
| SPEDCONTRIB | SPED Contribuicoes (EFD PIS/COFINS) | Processo |
| MATXNFE | Monitor NF-e | Processo |
| FISA010 | Cadastro de TES | Cadastro |
| FISA050 | Tabela de NCM | Cadastro |
| MATA926 | Livros Fiscais (consulta) | Consulta |
| MATR950 | Relatorio de Apuracao de ICMS | Relatorio |
| MATR951 | Relatorio de Apuracao de IPI | Relatorio |
| FISA070 | Amarracao de CFOP | Cadastro |
| MATA953 | Guia de Recolhimento | Processo |

## Pontos de Entrada

| PE | Quando Executa | Parametros | Tabelas Posicionadas |
|---|---|---|---|
| SPEDXNFE | Executado durante a geracao do arquivo XML da NF-e, permite incluir tags adicionais ou alterar valores | PARAMIXB[1]: cXML (XML atual da NF-e) | SF2 posicionada na NF de saida sendo transmitida, SD2 nos itens |
| SPEDXDOC | Executado durante a geracao do SPED Fiscal para cada documento fiscal, permite alterar registros | PARAMIXB[1]: cRegistro (tipo do registro SPED, ex: C100, C170), PARAMIXB[2]: cLinha (conteudo da linha) | SF3 posicionada no lancamento fiscal |
| M950MEN | Executado na abertura do lancamento fiscal manual, permite configurar campos e validacoes iniciais | Nenhum parametro direto | Nenhuma tabela posicionada especificamente |
| MATABUT | Permite incluir botoes extras na barra de ferramentas de rotinas fiscais | Nenhum parametro direto. Retorno: array bidimensional {cTitulo, bBloco} | Depende da rotina onde esta sendo chamado |
| A950VTES | Validacao da TES informada no lancamento fiscal manual | PARAMIXB[1]: cTES (codigo da TES informada) | SF4 posicionada na TES informada, SF3 (quando alteracao) |
| SPEDXITEM | Executado durante a geracao do SPED Fiscal para cada item do documento (registro C170) | PARAMIXB[1]: cLinha (conteudo da linha do registro C170) | SF3 posicionada, SFT posicionada no item fiscal |
| SPEDXREG | Executado durante a geracao do SPED Fiscal, permite incluir registros extras no arquivo | PARAMIXB[1]: cBloco (bloco atual do SPED, ex: C, D, E), PARAMIXB[2]: cRegistro (ultimo registro gerado) | Nenhuma tabela posicionada especificamente |
| NFECXML | Executado apos a montagem do XML da NF-e, antes da assinatura digital | PARAMIXB[1]: cXML (XML completo da NF-e) | SF2 posicionada na NF, SD2 nos itens |
| FA950TOK | Validacao geral (TudoOk) na confirmacao do lancamento fiscal manual | Nenhum parametro direto. Dados via M-> | SF3 (quando alteracao) |
| SPEDXC100 | Executado especificamente no registro C100 (documento fiscal) do SPED Fiscal | PARAMIXB[1]: cLinha (conteudo do registro C100) | SF3 posicionada no documento |
| MATXFIS01 | Executado durante o processo de apuracao de ICMS, permite ajustes nos valores apurados | PARAMIXB[1]: nValorICMS (valor apurado), PARAMIXB[2]: cPeriodo (periodo da apuracao) | CDO posicionada no periodo |
| SPEDCONT01 | Executado durante a geracao do SPED Contribuicoes, permite ajustes nos registros | PARAMIXB[1]: cRegistro (tipo do registro), PARAMIXB[2]: cLinha (conteudo) | SFT posicionada no item fiscal |

## Integracoes

### Compras -> Fiscal
- NF de Entrada gera lancamento no livro fiscal de entrada (SF3 com F3_ENTRADA = "S")
- Impostos de entrada geram credito fiscal (ICMS, IPI, PIS, COFINS)
- CFOP de entrada (1xxx para interna, 2xxx para interestadual, 3xxx para importacao)

### Faturamento -> Fiscal
- NF de Saida gera lancamento no livro fiscal de saida (SF3 com F3_ENTRADA = "N")
- Impostos de saida geram debito fiscal (ICMS, IPI, PIS, COFINS)
- CFOP de saida (5xxx para interna, 6xxx para interestadual, 7xxx para exportacao)

### Fiscal -> Contabilidade
- Apuracao de impostos gera lancamentos contabeis de provisao de imposto
- O pagamento da guia gera lancamento contabil de baixa da provisao
- Lancamentos contabeis automaticos via LP (lancamento padrao)

### Fiscal -> SEFAZ
- NF-e transmitida eletronicamente via TSS ou conexao direta
- Retorno da SEFAZ atualiza status da NF (autorizada, rejeitada, cancelada)
- Eventos da NF-e (carta de correcao, cancelamento) tambem transmitidos

## Regras de Negocio Comuns

### TES - Tipo de Entrada e Saida
A TES eh o principal configurador fiscal do Protheus. Cada item de NF usa uma TES que define:
- F4_ICM: Calcula ICMS (S/N)
- F4_IPI: Calcula IPI (S/N)
- F4_CREDICM: Credita ICMS (S/N)
- F4_CREDIPI: Credita IPI (S/N)
- F4_CF: CFOP padrao
- F4_ESTOQUE: Movimenta estoque (S/N)
- F4_DUPLIC: Gera titulo financeiro (S/N)
- F4_TEXTO: Texto legal padrao para a NF
- F4_CSTPIS / F4_CSTCOF: CST de PIS e COFINS
- F4_PISCOF: Calcula PIS/COFINS (S/N)

### NCM - Nomenclatura Comum do Mercosul
- Classificacao fiscal do produto (campo B1_POSIPI)
- Define aliquota de IPI (SFB)
- Obrigatorio na NF-e
- Usado no SPED Fiscal para validacao cruzada

### CFOP - Codigo Fiscal de Operacao e Prestacao
- Define a natureza da operacao fiscal
- Varia conforme tipo de operacao e localizacao (interna, interestadual, exterior)
- Configurado na TES (F4_CF) ou via amarracao (CC2)
- Exemplo: 5102 (venda interna), 6102 (venda interestadual), 1102 (compra interna)

### CST - Codigo de Situacao Tributaria
- **CST ICMS:** Define a tributacao de ICMS (00=Tributada integral, 10=Com ST, 20=Reducao base, 60=ICMS cobrado por ST)
- **CST IPI:** Define a tributacao de IPI (00=Entrada com credito, 50=Saida tributada, 99=Outras)
- **CST PIS/COFINS:** Define a tributacao de PIS e COFINS (01=Tributada aliquota basica, 06=Aliquota zero, 73=Credito presumido)

### MVA - Margem de Valor Agregado
- Usada no calculo do ICMS-ST
- Define o percentual de agregacao sobre o valor da operacao para calcular a base do ICMS-ST
- Pode variar por estado e NCM
- MVA ajustada para operacoes interestaduais

### Substituicao Tributaria (ICMS-ST)
- Mecanismo onde um contribuinte (substituto) recolhe o ICMS de toda a cadeia
- Base de calculo: (Valor operacao + IPI + Frete + Seguro) * (1 + MVA%)
- ICMS-ST = Base_ST * Aliquota_interna - ICMS_proprio
- Configurado na TES e nas tabelas de MVA

### DIFAL - Diferencial de Aliquota
- Aplicavel em vendas interestaduais para consumidor final nao contribuinte (EC 87/2015)
- DIFAL = Base * (Aliquota_interna_destino - Aliquota_interestadual)
- Partilha entre estado de origem e destino (100% destino a partir de 2019)
- Configurado na tabela CDH

### Parametros MV_ Relevantes
| Parametro | Descricao | Valor Padrao |
|---|---|---|
| MV_TESSION | TES inteligente (sugere TES automaticamente) | N |
| MV_ICMPAD | Aliquota padrao de ICMS interna | 18 |
| MV_TXPIS | Aliquota padrao de PIS | 1.65 |
| MV_TXCOFIN | Aliquota padrao de COFINS | 7.60 |
| MV_SPESSION | Regime tributario para SPED (1=Real, 2=Presumido, 3=Simples) | 1 |
| MV_ESTADO | UF da empresa | (estado) |
| MV_MCSTIPI | Usa CST de IPI | S |
| MV_DIFAL | Calcula DIFAL | S |
| MV_STUF | Calcula ICMS-ST | S |
| MV_CSTICM | CST ICMS padrao | 00 |
| MV_NFCE | Emite NFC-e | N |
| MV_AMBSPED | Ambiente SPED (1=Producao, 2=Homologacao) | 2 |

## Padroes de Customizacao

### Cenario: Incluir tags customizadas na NF-e
- **PE recomendado:** SPEDXNFE ou NFECXML
- **Abordagem:** SPEDXNFE permite manipular o XML durante a montagem. NFECXML permite manipular apos a montagem completa. Usar para incluir informacoes adicionais (infAdFisco, infCpl) ou campos especificos do contribuinte
- **Armadilha comum:** O XML deve respeitar o schema da NF-e. Incluir tags fora da estrutura causa rejeicao pela SEFAZ. Sempre validar o XML contra o schema antes de enviar

### Cenario: Ajustar registros do SPED Fiscal
- **PE recomendado:** SPEDXDOC (por documento) e SPEDXITEM (por item)
- **Abordagem:** Manipular o conteudo dos registros antes de gravar no arquivo. Util para ajustar valores, incluir informacoes complementares, ou corrigir dados inconsistentes
- **Armadilha comum:** O layout do SPED eh rigido (posicional). Alterar a estrutura do registro causa erro na validacao do PVA. Apenas alterar conteudo, nao estrutura

### Cenario: Validacao customizada de TES
- **PE recomendado:** A950VTES
- **Abordagem:** Validar se a TES informada eh compativel com a operacao, cliente/fornecedor, ou produto. Util para evitar erros fiscais
- **Armadilha comum:** A TES eh o principal configurador fiscal. Uma TES incorreta causa erro em toda a cadeia fiscal. Validar cuidadosamente

### Cenario: Ajustar apuracao de ICMS
- **PE recomendado:** MATXFIS01
- **Abordagem:** Incluir ajustes de apuracao (creditos extemporaneos, estornos, outros debitos/creditos) no processo automatico de apuracao
- **Armadilha comum:** Ajustes na apuracao devem ter amparo legal. Documentar o motivo do ajuste e o dispositivo legal correspondente
