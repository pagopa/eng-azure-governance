"""TSV serialization helpers."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def compact_json(value: Any) -> str:
    if value is None:
        return ""
    return json.dumps(value, separators=(",", ":"), sort_keys=True, ensure_ascii=True)


def unique_tsv_rows(headers: list[str], rows: list[dict[str, str]]) -> list[dict[str, str]]:
    unique_rows: list[dict[str, str]] = []
    seen_fingerprints: set[tuple[str, ...]] = set()

    for row in rows:
        safe_row = {key: sanitize_cell(row.get(key, "")) for key in headers}
        fingerprint = tuple(safe_row[key] for key in headers)
        if fingerprint in seen_fingerprints:
            continue
        seen_fingerprints.add(fingerprint)
        unique_rows.append(safe_row)

    return unique_rows


def write_tsv(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    unique_rows = unique_tsv_rows(headers, rows)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=headers,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in unique_rows:
            writer.writerow(row)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
        handle.write("\n")


def write_jsonl(path: Path, items: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(compact_json(item))
            handle.write("\n")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows: list[dict[str, str]] = []
        for row in reader:
            rows.append({str(key): sanitize_cell(value) for key, value in row.items() if key is not None})
        return rows


def sanitize_cell(value: str | None) -> str:
    if value is None:
        return ""
    return str(value).replace("\t", " ").replace("\r", " ").replace("\n", " ")
