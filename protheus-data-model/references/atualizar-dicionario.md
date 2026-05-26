# Atualizar o dicionário local das Skills

Sincroniza `protheus-data-model/dicionario/` a partir de export do Configurador Protheus.

## Arquivos de entrada

Coloque na **mesma pasta** (CSV ou Excel):

| Arquivo | Obrigatório | Conteúdo |
|---------|-------------|----------|
| `SX2.csv` | **Sim** | Tabelas |
| `SX3.csv` ou `SX3.xlsx` | Recomendado | Campos |
| `SIX.csv` | Recomendado | Índices |
| `SX7.csv` | Opcional | Gatilhos |
| `SX9.csv` | Opcional | Relacionamentos |

**Dependência:** `SX3.xlsx` exige `openpyxl` (`pip install openpyxl`).

## Modos

| Modo | Quando usar |
|------|-------------|
| `rebuild` | 1ª sync ou export **completo** do ambiente — regera JSON de todas as tabelas do `SX2.csv` |
| `merge` | Atualização parcial — só aliases presentes nos CSVs; blocos ausentes no export são **preservados** no JSON existente |

## Comandos (PowerShell)

Pasta de export (ajuste o caminho):

```powershell
$export = "C:\Dicionário"
$script = "d:\skills\protheus-data-model\scripts\sync_dicionario.py"
$dest   = "d:\skills\protheus-data-model\dicionario"
```

### Rebuild completo

```powershell
python $script --input-dir $export --output-dir $dest --mode rebuild --report "$dest\..\scripts\sync_report.json"
```

### Merge parcial (só tabelas alteradas)

```powershell
python $script --input-dir $export --output-dir $dest --mode merge --aliases "U97,U98,SRA"
```

### Simular sem gravar

```powershell
python $script --input-dir $export --mode rebuild --dry-run
```

## Saída

- JSON por alias: `dicionario/{LETRA}/{ALIAS}.json` (ex.: `U/U97.json`)
- Relatório opcional: `--report sync_report.json` (criadas, atualizadas, tabelas custom)

## Checklist pós-sync

1. Conferir amostras: `U97`, `U98`, `SRA`, tabelas do projeto
2. Validar campos custom (`*_X*`, tabelas `U*`, `Z*`)
3. Commit separado dos dados (`dicionario/`) se usar git — diff costuma ser grande
