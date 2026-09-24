"""Committee-owned slide values and their minimal YAML round-trip."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml

from ..contracts.slides_v1 import DATE_MEANING_TYPES, SlideRecord
from .links import is_azure_portal_link


_WRAPPED_FIELDS = frozenset({"comitato_descrizione", "descrizione_originale_completa"})
_WRAP_WIDTH = 100


class _CommitteeDumper(yaml.SafeDumper):
    pass


def _represent_mapping(dumper: yaml.SafeDumper, value: Mapping[str, Any]) -> yaml.Node:
    pairs = []
    for key in sorted(value):
        item = value[key]
        if key in _WRAPPED_FIELDS and isinstance(item, str) and len(item) > _WRAP_WIDTH:
            node = dumper.represent_scalar("tag:yaml.org,2002:str", item, style=">")
        else:
            node = dumper.represent_data(item)
        pairs.append((dumper.represent_data(key), node))
    return yaml.MappingNode("tag:yaml.org,2002:map", pairs)


_CommitteeDumper.add_representer(dict, _represent_mapping)


def _date_entries(value: str) -> list[dict[str, str]]:
    entries = []
    for line in value.splitlines():
        date_value, _, meaning = line.partition(" — ")
        if not date_value:
            continue
        tipo, fonte = DATE_MEANING_TYPES.get(meaning, ("", meaning))
        entries.append({"data": date_value, "tipo": tipo, "fonte": fonte})
    return entries


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
        updated[item_id] = {
            "comitato_descrizione": committee_description,
            "comitato_retirement_date": committee_date,
            "descrizione_originale_completa": description,
            "link_fonti": [
                value for value in str(row.get("link_fonti", "")).split("; ")
                if value and not is_azure_portal_link(value)
            ],
            "retirement_date": _date_entries(str(row.get("retirement_date", ""))),
        }
    return tuple(merged_rows), updated


def write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.dump(dict(value), Dumper=_CommitteeDumper, allow_unicode=True, width=_WRAP_WIDTH),
        encoding="utf-8",
    )


__all__ = ["load", "merge", "write"]
