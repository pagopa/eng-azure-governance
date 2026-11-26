from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..domain.links import is_azure_portal_link
from .date_presentation import (
    detect_slash_date_style,
    display_date_to_iso,
    format_italian_date_text,
)
from .slides_v1 import DATE_MEANING_TYPES, SlideRecord


def _committee_text(previous: Mapping[str, Any], name: str) -> str:
    value = previous.get(name, "")
    if value is None:
        return ""
    text = str(value)
    return text if text.strip() else ""


def _date_entries(value: str) -> list[dict[str, str]]:
    entries = []
    for line in value.splitlines():
        date_value, _, meaning = line.partition(" — ")
        if not date_value:
            continue
        tipo, fonte = DATE_MEANING_TYPES.get(meaning, ("", meaning))
        entries.append(
            {
                "data": display_date_to_iso(date_value),
                "tipo": tipo,
                "fonte": fonte,
            }
        )
    return entries


def merge(
    old: Mapping[str, Any], rows: Sequence[Mapping[str, str]]
) -> tuple[tuple[SlideRecord, ...], dict[str, Any]]:
    merged_rows = []
    updated: dict[str, Any] = {}
    committee_date_style = detect_slash_date_style(
        str(entry.get("comitato_retirement_date", ""))
        for entry in old.values()
        if isinstance(entry, Mapping)
    )
    for row in rows:
        item_id = row["id_elemento"]
        previous = old.get(item_id, {})
        previous = previous if isinstance(previous, Mapping) else {}
        description = str(row.get("descrizione_originale_completa", ""))
        committee_description = _committee_text(previous, "comitato_descrizione")
        committee_sources = previous.get("comitato_fonti", [])
        if str(previous.get("descrizione_originale_completa", "")) != description:
            committee_description = ""
            committee_sources = []
            committee_date = ""
        else:
            committee_date = format_italian_date_text(
                _committee_text(previous, "comitato_retirement_date"),
                slash_style=committee_date_style,
            )
        values = dict(row)
        values["comitato_descrizione"] = committee_description
        values["comitato_retirement_date"] = committee_date
        merged_rows.append(
            SlideRecord(tuple((key, str(value)) for key, value in values.items()))
        )
        updated[item_id] = {
            "comitato_descrizione": committee_description,
            "comitato_fonti": committee_sources,
            "comitato_retirement_date": committee_date,
            "descrizione_originale_completa": description,
            "link_fonti": [
                value
                for value in str(row.get("link_fonti", "")).split("; ")
                if value and not is_azure_portal_link(value)
            ],
            "retirement_date": _date_entries(str(row.get("retirement_date", ""))),
        }
    return tuple(merged_rows), updated


__all__ = ["merge"]
