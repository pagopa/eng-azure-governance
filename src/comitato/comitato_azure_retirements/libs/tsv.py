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


def write_tsv(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=headers,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in rows:
            safe_row = {key: sanitize_cell(row.get(key, "")) for key in headers}
            writer.writerow(safe_row)


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


def sanitize_cell(value: str | None) -> str:
    if value is None:
        return ""
    return str(value).replace("\t", " ").replace("\r", " ").replace("\n", " ")
