from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from hashlib import sha256
import json
import re

from ..contracts.aggregate_v1 import AGGREGATE_V1
from ..contracts.model import Artifact
from ..contracts.slides_v1 import SLIDES_V1, SlideRecord
from .dates import CommitteeWindow
from .diagnostics import Diagnostic, ValidationResult


_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True, slots=True)
class SlideSelection:
    artifact: Artifact
    excluded_by_reason: dict[str, tuple[str, ...]]
    committee_document: dict | None = None


def _json_values(row, column: str) -> list[str]:
    try:
        value = json.loads(row[column])
    except (KeyError, TypeError, json.JSONDecodeError):
        return []
    return sorted({str(item).strip() for item in value if str(item).strip()}) if isinstance(value, list) else []


def _group_key(row) -> str:
    advisor_types = _json_values(row, "advisor_recommendation_type_ids_json")
    if advisor_types:
        return f"advisor-type:{advisor_types[0]}"
    tracking_ids = _json_values(row, "service_health_tracking_ids_json")
    if tracking_ids:
        return f"service-health:{tracking_ids[0]}"
    return f"aggregate:{row['aggregate_id']}"


def _retirement_dates(rows) -> tuple[str, ...]:
    dates = set()
    for row in rows:
        try:
            events = json.loads(row["date_events_json"])
        except (KeyError, TypeError, json.JSONDecodeError):
            events = []
        if isinstance(events, list):
            dates.update(
                str(item.get("date", ""))
                for item in events
                if isinstance(item, dict)
                and item.get("kind") == "retirement"
                and _ISO_DATE.fullmatch(str(item.get("date", "")))
            )
        try:
            claims = json.loads(row["retirement_dates_json"])
        except (KeyError, TypeError, json.JSONDecodeError):
            claims = []
        if isinstance(claims, list):
            dates.update(
                str(item.get("date", ""))
                for item in claims
                if isinstance(item, dict)
                and item.get("quality", "exact") == "exact"
                and _ISO_DATE.fullmatch(str(item.get("date", "")))
            )
    return tuple(sorted(dates))


def select_slides(aggregate: Artifact, context) -> ValidationResult:
    if aggregate.contract != AGGREGATE_V1.name or aggregate.schema_version != AGGREGATE_V1.schema_version:
        return ValidationResult.invalid((Diagnostic("error", "invalid_aggregate_input", "slides", "slides", context.run_id),))
    if aggregate.run_id != context.run_id:
        return ValidationResult.invalid((Diagnostic("error", "aggregate_context_mismatch", "slides", "slides", context.run_id),))

    window = CommitteeWindow(context.as_of_date, context.request.committee_window_months)
    groups = defaultdict(list)
    for row in aggregate.records:
        groups[_group_key(row)].append(row)

    selected = []
    excluded: dict[str, list[str]] = {}
    for key, rows in groups.items():
        dates = _retirement_dates(rows)
        primary_date = dates[0] if dates else ""
        if primary_date and date.fromisoformat(primary_date) > window.upper_bound:
            excluded.setdefault("beyond_committee_window", []).append(key)
            continue
        if not dates:
            status = "Data non disponibile"
        elif len(dates) > 1:
            status = "Date discordanti"
        elif date.fromisoformat(primary_date) < context.as_of_date:
            status = "Scaduta"
        else:
            status = "In scadenza"
        item_id = "azure-retirement:v2:" + sha256(key.encode("utf-8")).hexdigest()
        selected.append(SlideRecord.from_group(tuple(rows), item_id=item_id, primary_date=primary_date, status=status))
    selected.sort(key=lambda row: (row["retirement_date"][:10] or "9999-99-99", row["id_elemento"]))
    artifact = Artifact(contract=SLIDES_V1.name, schema_version=SLIDES_V1.schema_version, run_id=context.run_id, records=tuple(selected))
    checked = SLIDES_V1.validate(artifact, context)
    if not checked.is_valid:
        return ValidationResult.invalid(checked.diagnostics)
    return ValidationResult.valid(SlideSelection(artifact=artifact, excluded_by_reason={key: tuple(sorted(value)) for key, value in sorted(excluded.items())}))


def project_slides(aggregate: Artifact, context) -> ValidationResult[Artifact]:
    result = select_slides(aggregate, context)
    if not result.is_valid or result.value is None:
        return ValidationResult.invalid(result.diagnostics)
    return ValidationResult.valid(result.value.artifact)


__all__ = ["SlideSelection", "project_slides", "select_slides"]
