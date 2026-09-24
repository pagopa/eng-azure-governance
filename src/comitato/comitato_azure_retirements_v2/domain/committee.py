"""Committee-owned slide values and their minimal YAML round-trip."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml

from ..contracts.slides_v1 import SlideRecord


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def merge(old: Mapping[str, Any], rows: Sequence[Mapping[str, str]]) -> tuple[tuple[SlideRecord, ...], dict[str, Any]]:
    merged_rows = []
    updated: dict[str, Any] = {}
    for row in rows:
        item_id = row["id_elemento"]
        previous = old.get(item_id, {})
        previous = previous if isinstance(previous, Mapping) else {}
        description = str(row.get("descrizione_originale_completa", ""))
        committee_description = str(previous.get("comitato_descrizione", ""))
        if str(previous.get("descrizione_originale_completa", "")) != description:
            committee_description = ""
        committee_date = str(previous.get("comitato_retirement_date", ""))
        values = dict(row)
        values["comitato_descrizione"] = committee_description
        values["comitato_retirement_date"] = committee_date
        merged_rows.append(SlideRecord(tuple((key, str(value)) for key, value in values.items())))
        date_lines = [
            line for line in str(row.get("retirement_date", "")).splitlines()
            if line and "Ultimo aggiornamento" not in line
        ]
        updated[item_id] = {
            "comitato_descrizione": committee_description,
            "comitato_retirement_date": committee_date,
            "descrizione_originale_completa": description,
            "link_fonti": [value for value in str(row.get("link_fonti", "")).split("; ") if value],
            "retirement_date": date_lines,
        }
    return tuple(merged_rows), updated


def write(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(
        yaml.safe_dump(dict(value), allow_unicode=True, sort_keys=True, width=10**9),
        encoding="utf-8",
    )


__all__ = ["load", "merge", "write"]
