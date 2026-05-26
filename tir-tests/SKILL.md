---
name: tir-tests
description: >
  Gera scripts de teste automatizado TIR (TOTVS Interface Robot) para rotinas
  Protheus WebApp usando Python/unittest. Use esta skill SEMPRE que o usuario
  pedir para criar testes automatizados, testes TIR, testes de interface,
  testes de regressao, testes e2e, ou testar rotinas Protheus via browser.
  Tambem ativar quando o usuario mencionar "criar teste TIR", "teste automatizado",
  "testar rotina com TIR", "automated test", "test with TIR", "gerar TESTCASE.py",
  ou qualquer variacao de teste de interface para Protheus. NAO usar para testes
  unitarios de backend/jobs (esses usam ConOut direto) -- TIR e exclusivo para
  rotinas com interface visual (browse, cadastro, relatorio).
---

# TIR - TOTVS Interface Robot

Skill para gerar scripts de teste automatizado que simulam interacao de usuario
real no Protheus WebApp. O TIR controla o Firefox via Selenium, clicando botoes,
preenchendo campos e validando resultados -- como um QA faria manualmente.

## Quando TIR se aplica (e quando nao)

| Aplica (tem interface)             | NAO aplica (sem interface)         |
|------------------------------------|------------------------------------|
| Cadastros (MATA030, CRMA980...)    | Jobs/Workers (roda via Scheduler)  |
| Rotinas MVC (Model1/2/3)          | APIs REST (testar via HTTP client) |
| Relatorios (TReport com tela)      | Funcoes de biblioteca (testar com ConOut) |
| Browses com acoes                  | Processos batch                    |

---

## 1. Workflow obrigatorio

Ao receber um pedido de teste TIR, siga esta sequencia:

1. **Identificar a rotina** — pergunte ao usuario qual rotina testar se nao estiver claro no contexto.
2. **Ler o codigo-fonte** — use suas ferramentas `view_file` e `grep_search` para ler a rotina alvo e entender campos, botoes, abas, grids e o fluxo da rotina.
3. **Identificar o modulo** — mapeie a rotina para o modulo Protheus correto (SIGACOM, SIGAFAT, SIGAFIN, etc.).
4. **Gerar o arquivo de teste** — salve o script (usando `write_to_file`) como `{ROTINA}TESTCASE.py` (ex: `MATA030TESTCASE.py`) no local especificado pelo usuario, seguindo o template abaixo.
5. **Gerar config.json** — crie se nao existir no diretorio onde os testes vao rodar.

Ao ler o codigo-fonte, preste atencao especial a:
- Campos obrigatorios (usados em SetValue)
- Abas/folders (usados em ClickFolder)
- Botoes customizados (usados em SetButton)
- Grids editaveis (usados em ClickGridCell)
- Parametros SX6 necessarios (usados em AddParameter)
- Chave do browse (usada em SearchBrowse)

---

## 2. config.json

Se for solicitado para rodar ou se nao existir no diretorio raiz de testes, gere este arquivo:

```json
{
    "Url": "http://localhost:2023",
    "Browser": "Firefox",
    "Environment": "ENVIRONMENT",
    "Language": "pt-br",
    "User": "ADMIN",
    "Password": "1234",
    "Headless": true,
    "POUILogin": false,
    "NewLog": true,
    "MotExec": "HOMOLOGACAO_TIR",
    "ExecId": "20260101"
}
```

| Campo         | Descricao                                      |
|---------------|-------------------------------------------------|
| `Url`         | URL do WebApp Protheus (porta do HTTP do ini)   |
| `Browser`     | Sempre `"Firefox"` (unico suportado)            |
| `Environment` | Nome do environment no appserver.ini             |
| `Language`    | `"pt-br"` para Protheus Brasil                   |
| `User`        | Usuario de login do Protheus                      |
| `Password`    | Senha do usuario                                  |
| `Headless`    | `true` = sem janela visivel (CI/CD), `false` = debug visual |
| `POUILogin`   | `true` se a tela de login e PO-UI (Protheus mais recente) |

Lembre o usuario de ajustar `Url` e `Environment` para seu ambiente.

---

## 3. Template de teste

Todo arquivo de teste gerado DEVE seguir esta estrutura rigida:

```python
from tir import Webapp
import unittest

class NOME_ROTINA(unittest.TestCase):
    """Teste automatizado TIR para NOME_ROTINA"""

    @classmethod
    def setUpClass(inst):
        inst.oHelper = Webapp()
        inst.oHelper.Setup('MODULO', 'DD/MM/YYYY', 'T1', 'FILIAL ', 'COD_MOD')
        inst.oHelper.Program('NOME_ROTINA')

    def test_ROTINA_001(self):
        """Descricao do cenario"""
        # passos do teste
        self.oHelper.AssertTrue()

    @classmethod
    def tearDownClass(inst):
        inst.oHelper.TearDown()

if __name__ == '__main__':
    unittest.main()
```

### Regras do template

- **Classe** = nome da rotina (ex: `MATA030`, `ASC0201`, `CRMA980`)
- **Metodos** = `test_{ROTINA}_{NNN}` com numero sequencial para ordenacao (ex: `test_MATA030_001`)
- **Todo metodo termina** com `self.oHelper.AssertTrue()` — sem isso o TIR nao registra resultado.
- **setUpClass/tearDownClass** sao `@classmethod` e recebem `inst` (nao `cls`).
- **Setup()** recebe: modulo, data, grupo, filial (com espaco no final se necessario), codigo do modulo.
- **Arquivo** salvar como `{ROTINA}TESTCASE.py` (ex: `MATA030TESTCASE.py`).

### Mapeamento modulo -> codigo

| Modulo   | Codigo | Sigla    |
|----------|--------|----------|
| Compras  | 02     | SIGACOM  |
| Estoque  | 04     | SIGAEST  |
| Faturamento | 05  | SIGAFAT  |
| Financeiro | 06   | SIGAFIN  |
| Contabil | 09     | SIGACTB  |
| Fiscal   | 10     | SIGAFIS  |
| RH/Gestao Pessoal | 12 | SIGAGPE |
| PCP      | 23     | SIGAPCP  |

---

## 4. API do Webapp — metodos disponiveis

### Ciclo de vida

| Metodo | Descricao |
|--------|-----------|
| `Setup(modulo, data, grupo, filial, cod_mod)` | Faz login e configura ambiente |
| `Program('ROTINA')` | Abre a rotina no menu |
| `TearDown()` | Fecha browser e encerra sessao |
| `AssertTrue()` | Finaliza teste — registra sucesso ou falha |
| `ChangeEnvironment(data, grupo, filial, cod_mod)` | Troca ambiente sem fechar browser |

### Botoes e navegacao

| Metodo | Descricao |
|--------|-----------|
| `SetButton('Nome')` | Clica em botao pelo label visivel |
| `SetButton('Outras Acoes', 'SubItem')` | Clica em submenu de acoes |
| `SetBranch('D MG 01')` | Seleciona filial no dialog |
| `ClickFolder('NomeAba')` | Clica em aba/folder |
| `ClickCheckBox('Label', posicao)` | Marca/desmarca checkbox |
| `SetKey('F12')` | Simula tecla de atalho |
| `SetKey('Enter', grid=True, grid_number=1)` | Tecla dentro de contexto grid |

### Campos

| Metodo | Descricao |
|--------|-----------|
| `SetValue('Campo', 'valor')` | Preenche campo (aceita label ou ID tipo A1_COD) |
| `SetValue('Campo', 'descricao - Texto')` | Para combos, usar "valor - descricao" |
| `GetValue('Campo')` | Retorna valor atual do campo |
| `CheckResult('Campo', 'valor_esperado')` | Valida que campo tem valor esperado |

### Browse e busca

| Metodo | Descricao |
|--------|-----------|
| `SearchBrowse('FilialChave')` | Posiciona no registro pelo conteudo das colunas do browse |
| `SearchBrowse('Chave', key=1, index=True)` | Busca usando indice especifico |

A chave do SearchBrowse e a concatenacao dos valores visiveis nas colunas do browse
(tipicamente filial + codigo). Verificar no fonte qual e a chave do browse.

### Grid

| Metodo | Descricao |
|--------|-----------|
| `ClickGridCell('Coluna', linha, grid_number)` | Clica em celula do grid |
| `SetValue('Coluna', 'valor', grid=True, grid_number=1, row=1)` | Preenche celula do grid |
| `GetValue('Coluna', grid=True, grid_number=1, row=1)` | Le valor de celula do grid |
| `CheckResult('Coluna', 'valor', grid=True, grid_number=1, row=1)` | Valida celula do grid |
| `LoadGrid()` | Carrega dados do grid |
| `LengthGridLines()` | Retorna quantidade de linhas do grid |

### Espera e sincronizacao

| Metodo | Descricao |
|--------|-----------|
| `WaitShow('Titulo')` | Aguarda janela/dialog aparecer |
| `WaitHide('Titulo')` | Aguarda janela fechar |
| `WaitProcessing()` | Aguarda processamento do servidor |

Preferir WaitShow/WaitProcessing em vez de `time.sleep()`. Usar sleep somente
como ultimo recurso e com valores pequenos (3-5 segundos).

### Parametros SX6

| Metodo | Descricao |
|--------|-----------|
| `AddParameter('MV_PARAM', '', 'val_todas', 'val_emp', 'val_fil')` | Configura parametro |
| `SetParameters()` | Aplica todos os parametros configurados |

Usar quando a rotina depende de parametros especificos para funcionar.
Chamar AddParameter para cada parametro, depois SetParameters() uma vez.

### Validacao de alertas

| Metodo | Descricao |
|--------|-----------|
| `CheckHelp(text_help='MSGID', button='Fechar')` | Valida mensagem de help/alerta |

---

## 5. Padroes CRUD

Os 4 cenarios padrao que toda rotina de cadastro deve testar:

### 5.1 Inclusao (test_XXX_001)

```python
def test_ROTINA_001(self):
    """Inclui registro e valida"""
    self.oHelper.SetButton('Incluir')
    self.oHelper.SetBranch('D MG 01')          # se pedir filial
    self.oHelper.ClickFolder('Cadastrais')      # se tiver abas
    self.oHelper.SetValue('CAMPO1', 'VALOR1')
    self.oHelper.SetValue('CAMPO2', 'VALOR2')
    self.oHelper.SetButton('Confirmar')
    self.oHelper.AssertTrue()
```

### 5.2 Alteracao (test_XXX_002)

```python
def test_ROTINA_002(self):
    """Altera registro existente"""
    self.oHelper.SearchBrowse('D MG 01 CHAVE_BROWSE')
    self.oHelper.SetButton('Alterar')
    self.oHelper.SetValue('CAMPO2', 'VALOR_ALTERADO')
    self.oHelper.SetButton('Confirmar')
    self.oHelper.AssertTrue()
```

### 5.3 Visualizacao (test_XXX_003)

```python
def test_ROTINA_003(self):
    """Visualiza e valida campos"""
    self.oHelper.SearchBrowse('D MG 01 CHAVE_BROWSE')
    self.oHelper.SetButton('Visualizar')
    self.oHelper.CheckResult('CAMPO1', 'VALOR1')
    self.oHelper.CheckResult('CAMPO2', 'VALOR_ALTERADO')
    self.oHelper.SetButton('Cancelar')
    self.oHelper.AssertTrue()
```

### 5.4 Exclusao (test_XXX_004)

```python
def test_ROTINA_004(self):
    """Exclui registro"""
    self.oHelper.SearchBrowse('D MG 01 CHAVE_BROWSE')
    self.oHelper.SetButton('Outras Acoes', 'Excluir')
    self.oHelper.SetButton('Confirmar')
    self.oHelper.AssertTrue()
```

---

## 6. Padroes especiais

### 6.1 Rotina com grid (master-detail)

```python
def test_ROTINA_005(self):
    """Inclui com itens no grid"""
    self.oHelper.SetButton('Incluir')
    # Cabecalho
    self.oHelper.SetValue('CAMPO_CAB', 'VALOR')
    # Grid de itens
    self.oHelper.SetValue('COLUNA1', 'VAL1', grid=True, grid_number=1, row=1)
    self.oHelper.SetValue('COLUNA2', 'VAL2', grid=True, grid_number=1, row=1)
    self.oHelper.SetButton('Confirmar')
    self.oHelper.AssertTrue()
```

### 6.2 Rotina que requer parametros

```python
@classmethod
def setUpClass(inst):
    inst.oHelper = Webapp()
    inst.oHelper.Setup('SIGAFIN', '14/03/2026', 'T1', 'D MG 01 ', '06')
    # Configurar parametros antes de abrir a rotina
    inst.oHelper.AddParameter('MV_COMPCP', '', 'T', 'T', 'T')
    inst.oHelper.SetParameters()
    inst.oHelper.Program('FINA340')
```

### 6.3 Teste negativo (validacao de help)

```python
def test_ROTINA_006(self):
    """Valida que sistema bloqueia data invalida"""
    self.oHelper.SetButton('Incluir')
    self.oHelper.SetValue('DATA', '01/01/1900')
    self.oHelper.SetButton('Confirmar')
    self.oHelper.CheckHelp(text_help='DATAINV', button='Fechar')
    self.oHelper.SetButton('Cancelar')
    self.oHelper.AssertTrue()
```

### 6.4 Troca de ambiente entre testes

```python
def test_ROTINA_007(self):
    """Testa em filial diferente"""
    self.oHelper.SetButton('x')
    self.oHelper.ChangeEnvironment('14/03/2026', 'T1', 'M SP 01 ', '06')
    self.oHelper.Program('FINA340')
    self.oHelper.WaitShow('Titulo da Janela')
    # continua o teste...
    self.oHelper.AssertTrue()
```

---

## 7. Boas praticas

- **Dados de teste com prefixo unico** — usar prefixo como `TIR` nos codigos para evitar conflito
  com dados reais (ex: `A1_COD = 'TIRC001'`).
- **Testes independentes** — cada test method deve funcionar isolado quando possivel;
  se houver dependencia (ex: alterar o que foi incluido), documentar a ordem.
- **Fechar dialogs** — sempre fechar alertas e janelas antes de terminar o teste,
  senao o proximo teste falha por tela suja.
- **Combo/Select** — para campos com combo, usar formato `'valor - descricao'`
  (ex: `SetValue('A1_TIPO', 'F - Cons.Final')`).
- **Filial no SearchBrowse** — a chave inclui filial com espacos conforme aparece no browse;
  verificar o formato exato no fonte da rotina.
- **Executar** — rodar os comandos no terminal `python -m pytest ROTINA_TESTCASE.py -v` ou `python ROTINA_TESTCASE.py` usando a ferramenta de linha de comando (`run_command`).

---

## 8. Instalacao do TIR (referencia rapida)

Para rodar os testes localmente ou em CI:

```bash
# Pre-requisitos: Python 3.12 + Firefox
pip install tir_framework --upgrade
```

O Protheus precisa estar rodando com WebApp acessivel na URL configurada no `config.json`.
