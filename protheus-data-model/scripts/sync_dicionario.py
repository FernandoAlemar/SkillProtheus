#!/usr/bin/env python3
"""Sincroniza protheus-data-model/dicionario/ a partir de export SX2/SX3/SIX/SX7/SX9."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Set, TextIO

try:
    import openpyxl
except ImportError:  # pragma: no cover
    openpyxl = None


def trim(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def is_deleted(row: Dict[str, str]) -> bool:
    deleted = trim(row.get("D_E_L_E_T_", " ")).upper()
    return deleted in {"*", "D"}


def is_obrigatory(value: str) -> bool:
    text = trim(value).upper()
    return "X" in text or text in {"S", "1", "SIM", "Y", "YES"}


def is_combo(value: str) -> bool:
    text = trim(value)
    return "=" in text and ";" in text


def resolve_table_from_field(field: str, tables: Set[str]) -> str:
    prefix = trim(field).split("_", 1)[0].upper()
    if prefix in tables:
        return prefix
    candidate = f"S{prefix}"
    if candidate in tables:
        return candidate
    return prefix


def detect_encoding(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                handle.read(4096)
            return encoding
        except UnicodeDecodeError:
            continue
    return "latin-1"


def iter_csv_rows(path: Path) -> Iterator[Dict[str, str]]:
    encoding = detect_encoding(path)
    with path.open("r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            yield {key: trim(value) for key, value in row.items()}


def iter_xlsx_rows(path: Path) -> Iterator[Dict[str, str]]:
    if openpyxl is None:
        raise RuntimeError("openpyxl é necessário para ler SX3.xlsx (pip install openpyxl)")

    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    worksheet = workbook.active
    headers: Optional[List[str]] = None
    for row in worksheet.iter_rows(values_only=True):
        if headers is None:
            headers = [trim(cell) for cell in row]
            continue
        values = list(row[: len(headers)])
        while len(values) < len(headers):
            values.append("")
        yield {headers[index]: trim(values[index]) for index in range(len(headers))}
    workbook.close()


def iter_table_rows(path: Path) -> Iterator[Dict[str, str]]:
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        yield from iter_xlsx_rows(path)
    else:
        yield from iter_csv_rows(path)


def find_input_file(input_dir: Path, base_name: str) -> Optional[Path]:
    for suffix in (".csv", ".xlsx", ".CSV", ".XLSX"):
        candidate = input_dir / f"{base_name}{suffix}"
        if candidate.exists():
            return candidate
    return None


def load_sx2(path: Path) -> Dict[str, Dict[str, str]]:
    tables: Dict[str, Dict[str, str]] = {}
    for row in iter_table_rows(path):
        if is_deleted(row):
            continue
        alias = trim(row.get("X2_CHAVE")).upper()
        if not alias:
            continue
        tables[alias] = row
    return tables


def load_sx3(path: Path, aliases: Optional[Set[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in iter_table_rows(path):
        if is_deleted(row):
            continue
        alias = trim(row.get("X3_ARQUIVO")).upper()
        if not alias:
            continue
        if aliases is not None and alias not in aliases:
            continue

        field: Dict[str, Any] = {
            "campo": trim(row.get("X3_CAMPO")),
            "titulo": trim(row.get("X3_TITULO")),
            "tipo": trim(row.get("X3_TIPO")),
            "tam": int(float(row.get("X3_TAMANHO") or 0)),
            "dec": int(float(row.get("X3_DECIMAL") or 0)),
        }

        validacao = trim(row.get("X3_VALID"))
        if validacao:
            field["validacao"] = validacao

        combo = trim(row.get("X3_CBOX"))
        if is_combo(combo):
            field["combo"] = combo

        ini_padrao = trim(row.get("X3_RELACAO"))
        if ini_padrao:
            field["ini_padrao"] = ini_padrao

        if is_obrigatory(row.get("X3_OBRIGAT", "")):
            field["obrig"] = True

        grouped[alias].append(field)
    return grouped


def load_six(path: Path, aliases: Optional[Set[str]] = None) -> Dict[str, List[Dict[str, str]]]:
    grouped: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in iter_table_rows(path):
        if is_deleted(row):
            continue
        alias = trim(row.get("INDICE")).upper()
        if not alias:
            continue
        if aliases is not None and alias not in aliases:
            continue

        index: Dict[str, str] = {
            "ordem": trim(row.get("ORDEM")),
            "chave": trim(row.get("CHAVE")),
            "descricao": trim(row.get("DESCRICAO")),
        }
        nickname = trim(row.get("NICKNAME"))
        if nickname:
            index["nickname"] = nickname
        grouped[alias].append(index)
    return grouped


def load_sx7(path: Path, tables: Set[str], aliases: Optional[Set[str]] = None) -> Dict[str, List[Dict[str, str]]]:
    grouped: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in iter_table_rows(path):
        if is_deleted(row):
            continue
        campo = trim(row.get("X7_CAMPO"))
        if not campo:
            continue
        alias = resolve_table_from_field(campo, tables)
        if aliases is not None and alias not in aliases:
            continue

        trigger: Dict[str, str] = {
            "origem": campo,
            "tipo": trim(row.get("X7_TIPO")),
            "seq": trim(row.get("X7_SEQUENC")),
            "destino": trim(row.get("X7_CDOMIN")),
            "regra": trim(row.get("X7_REGRA")),
        }
        grouped[alias].append(trigger)
    return grouped


def load_sx9(path: Path, aliases: Optional[Set[str]] = None) -> Dict[str, List[Dict[str, str]]]:
    grouped: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in iter_table_rows(path):
        if is_deleted(row):
            continue
        alias = trim(row.get("X9_DOM")).upper()
        if not alias:
            continue
        if aliases is not None and alias not in aliases:
            continue

        relation: Dict[str, str] = {
            "dominio": alias,
            "expressao_dom": trim(row.get("X9_EXPDOM")),
            "identificador": trim(row.get("X9_IDENT")),
        }
        expressao_ident = trim(row.get("X9_EXPCDOM"))
        if expressao_ident:
            relation["expressao_ident"] = expressao_ident
        grouped[alias].append(relation)
    return grouped


def output_path(output_dir: Path, alias: str) -> Path:
    return output_dir / alias[0].upper() / f"{alias.upper()}.json"


def read_existing_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_table_json(
    alias: str,
    sx2_row: Dict[str, str],
    campos: List[Dict[str, Any]],
    indices: List[Dict[str, str]],
    gatilhos: List[Dict[str, str]],
    relacionamentos: List[Dict[str, str]],
    existing: Optional[Dict[str, Any]] = None,
    merge: bool = False,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "tabela": alias,
        "nome": trim(sx2_row.get("X2_NOME")),
        "nome_eng": trim(sx2_row.get("X2_NOMEENG")),
        "modo": trim(sx2_row.get("X2_MODO")),
        "arquivo": trim(sx2_row.get("X2_ARQUIVO")),
    }

    if campos:
        payload["campos"] = campos
    elif merge and existing.get("campos"):
        payload["campos"] = existing["campos"]
    else:
        payload["campos"] = []

    if indices:
        payload["indices"] = indices
    elif merge and existing.get("indices"):
        payload["indices"] = existing["indices"]

    if gatilhos:
        payload["gatilhos"] = gatilhos
    elif merge and existing.get("gatilhos"):
        payload["gatilhos"] = existing["gatilhos"]

    if relacionamentos:
        payload["relacionamentos"] = relacionamentos
    elif merge and existing.get("relacionamentos"):
        payload["relacionamentos"] = existing["relacionamentos"]

    return payload


def write_json(path: Path, payload: Dict[str, Any], dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, separators=(",", ":"))


def parse_aliases(raw: Optional[str]) -> Optional[Set[str]]:
    if not raw:
        return None
    return {item.strip().upper() for item in raw.split(",") if item.strip()}


def is_custom_alias(alias: str) -> bool:
    alias = alias.upper()
    if alias.startswith(("U", "Z")) and len(alias) == 3:
        return True
    return False


def has_custom_fields(campos: List[Dict[str, Any]]) -> bool:
    for field in campos:
        name = trim(field.get("campo")).upper()
        if "_X" in name or "_U" in name or name.startswith(("X", "U")):
            return True
    return False


def sync_dicionario(
    input_dir: Path,
    output_dir: Path,
    mode: str,
    aliases_filter: Optional[Set[str]] = None,
    dry_run: bool = False,
    report_file: Optional[TextIO] = None,
) -> Dict[str, Any]:
    sx2_path = find_input_file(input_dir, "SX2")
    if sx2_path is None:
        raise FileNotFoundError("SX2.csv ou SX2.xlsx não encontrado no diretório de entrada")

    sx3_path = find_input_file(input_dir, "SX3")
    six_path = find_input_file(input_dir, "SIX")
    sx7_path = find_input_file(input_dir, "SX7")
    sx9_path = find_input_file(input_dir, "SX9")

    print(f"Lendo {sx2_path.name}...", flush=True)
    sx2 = load_sx2(sx2_path)
    table_set = set(sx2.keys())

    target_aliases = aliases_filter or set(sx2.keys())
    if mode == "rebuild" and aliases_filter is None:
        target_aliases = set(sx2.keys())

    campos_by_alias: Dict[str, List[Dict[str, Any]]] = {}
    indices_by_alias: Dict[str, List[Dict[str, str]]] = {}
    gatilhos_by_alias: Dict[str, List[Dict[str, str]]] = {}
    relacoes_by_alias: Dict[str, List[Dict[str, str]]] = {}

    if sx3_path:
        print(f"Lendo {sx3_path.name}...", flush=True)
        campos_by_alias = load_sx3(sx3_path, target_aliases if mode == "merge" else None)
    if six_path:
        print(f"Lendo {six_path.name}...", flush=True)
        indices_by_alias = load_six(six_path, target_aliases if mode == "merge" else None)
    if sx7_path:
        print(f"Lendo {sx7_path.name}...", flush=True)
        gatilhos_by_alias = load_sx7(sx7_path, table_set, target_aliases if mode == "merge" else None)
    if sx9_path:
        print(f"Lendo {sx9_path.name}...", flush=True)
        relacoes_by_alias = load_sx9(sx9_path, target_aliases if mode == "merge" else None)

    stats = {
        "mode": mode,
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "custom_tables": [],
        "custom_field_tables": [],
        "missing_sx3": [],
    }

    merge = mode == "merge"
    for alias in sorted(target_aliases):
        sx2_row = sx2.get(alias)
        if sx2_row is None:
            stats["skipped"] += 1
            continue

        path = output_path(output_dir, alias)
        existing = read_existing_json(path) if merge else {}
        existed_before = path.exists()

        payload = build_table_json(
            alias,
            sx2_row,
            campos_by_alias.get(alias, []),
            indices_by_alias.get(alias, []),
            gatilhos_by_alias.get(alias, []),
            relacoes_by_alias.get(alias, []),
            existing=existing,
            merge=merge,
        )

        write_json(path, payload, dry_run)

        if existed_before:
            stats["updated"] += 1
        else:
            stats["created"] += 1

        if is_custom_alias(alias):
            stats["custom_tables"].append(alias)
        elif has_custom_fields(payload.get("campos", [])):
            stats["custom_field_tables"].append(alias)
        elif not payload.get("campos"):
            stats["missing_sx3"].append(alias)

    if report_file:
        report_file.write(json.dumps(stats, ensure_ascii=False, indent=2))
        report_file.write("\n")

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync do dicionário Protheus para Skills")
    parser.add_argument("--input-dir", required=True, help="Pasta com SX2/SX3/SIX/SX7/SX9")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1] / "dicionario"),
        help="Pasta de saída dicionario/",
    )
    parser.add_argument("--mode", choices=("rebuild", "merge"), default="rebuild")
    parser.add_argument("--aliases", help="Lista separada por vírgula (ex.: U98,SRA)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report", help="Arquivo JSON de relatório")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    aliases_filter = parse_aliases(args.aliases)

    report_handle = open(args.report, "w", encoding="utf-8") if args.report else None
    try:
        stats = sync_dicionario(
            input_dir=input_dir,
            output_dir=output_dir,
            mode=args.mode,
            aliases_filter=aliases_filter,
            dry_run=args.dry_run,
            report_file=report_handle,
        )
    finally:
        if report_handle:
            report_handle.close()

    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
