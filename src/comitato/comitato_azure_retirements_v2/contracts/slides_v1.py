from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
import json
import re
from typing import Any

from ..domain.diagnostics import Diagnostic, ValidationResult
from ._base import TsvContract


HEADER = (
    "id_elemento", "titolo_breve", "descrizione_breve", "comitato_priorità",
    "comitato_descrizione", "comitato_retirement_date", "comitato_piattaforme",
    "retirement_date", "stato_data", "tipo_cambiamento", "stato_editoriale",
    "descrizione_originale_completa", "azione_originale", "fonti", "link_fonti",
    "ambito_impatto", "id_advisor", "id_service_health", "risorse_json",
)

_EXCEL_CELL_LIMIT = 32767
_SOURCE_NAMES = {
    "advisor": "Azure Advisor",
    "azure-advisor": "Azure Advisor",
    "service-health": "Azure Service Health",
    "azure-service-health": "Azure Service Health",
}


def _json_value(row: Mapping[str, str], column: str, default: Any) -> Any:
    try:
        value = json.loads(row[column])
    except (KeyError, TypeError, json.JSONDecodeError):
        return default
    return value


def _readable_item(value: Any) -> str:
    if isinstance(value, Mapping):
        for field in ("text", "action", "actionText", "caption", "label", "description", "title", "name"):
            text = str(value.get(field, "")).strip()
            if text:
                return text
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return str(value).strip()


def _readable(values: Any, separator: str = "; ") -> str:
    if not isinstance(values, (list, tuple)):
        return "" if values is None else str(values).strip()
    unique = sorted({_readable_item(value) for value in values if _readable_item(value)}, key=lambda item: (item.casefold(), item))
    return separator.join(unique)


def _source_name(value: str) -> str:
    return _SOURCE_NAMES.get(value.casefold(), value.replace("-", " ").title())


def _overflow(value: str, item_id: str, section: str) -> str:
    if len(value) <= _EXCEL_CELL_LIMIT:
        return value
    return f"OVERFLOW: complete value retained in aggregate/provenance for {item_id}.{section}"


def _editorial(row: Mapping[str, str]) -> Mapping[str, str]:
    provenance = _json_value(row, "provenance_json", {})
    value = provenance.get("editorial", {}) if isinstance(provenance, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _source_text(row: Mapping[str, str], column_values: tuple[tuple[str, str], ...]) -> str:
    sections = []
    for label, column in column_values:
        values = _json_value(row, column, [])
        text = _readable(values, separator="\n\n")
        if text:
            sections.append(f"{label}: {text}")
    return "\n\n".join(sections)


def _resource_hierarchy(row: Mapping[str, str]) -> dict[str, Any]:
    platforms = _json_value(row, "platforms_subscriptions_json", {})
    resource_ids = _json_value(row, "published_resource_ids_json", [])
    normalized_ids = _json_value(row, "normalized_resource_ids_json", [])
    ids_by_key = {}
    for value in (*resource_ids, *normalized_ids):
        text = str(value).strip()
        if text:
            ids_by_key.setdefault(text.casefold(), text)
    ids = sorted(ids_by_key.values(), key=str.casefold)
    provenance = _json_value(row, "provenance_json", {})
    evidence = provenance.get("resource_evidence", ()) if isinstance(provenance, Mapping) else ()
    evidence_by_subscription: dict[str, list[Mapping[str, str]]] = {}
    if isinstance(evidence, list):
        for item in evidence:
            if isinstance(item, (list, tuple)) and len(item) == 5:
                subscription_id, resource_name, resource_group, resource_id, status = item
                evidence_by_subscription.setdefault(str(subscription_id).casefold(), []).append({
                    "resource_name": str(resource_name),
                    "resource_group": str(resource_group),
                    "resource_id": str(resource_id),
                    "status": str(status),
                })
    if not isinstance(platforms, Mapping):
        platforms = {}
    result: dict[str, Any] = {}
    for platform, subscriptions in sorted(platforms.items(), key=lambda item: str(item[0]).casefold()):
        entries = []
        for subscription in subscriptions if isinstance(subscriptions, list) else ():
            if not isinstance(subscription, Mapping):
                continue
            subscription_id = str(subscription.get("subscription_id", "")).strip()
            subscription_name = str(subscription.get("subscription_name", "")).strip()
            matching_ids = [
                resource_id for resource_id in ids
                if f"/subscriptions/{subscription_id}/".casefold() in resource_id.casefold()
            ]
            groups: dict[str, list[str]] = {}
            for resource_id in matching_ids:
                match = re.search(r"/resourceGroups/([^/]+)", resource_id, re.IGNORECASE)
                group = match.group(1) if match else "<unknown>"
                groups.setdefault(group, []).append(resource_id)
            for item in evidence_by_subscription.get(subscription_id.casefold(), ()):
                group = item["resource_group"] or "<unknown>"
                if item["resource_id"]:
                    groups.setdefault(group, []).append(item["resource_id"])
                else:
                    groups.setdefault(group, [])
            group_values = []
            for group, values in sorted(groups.items(), key=lambda item: item[0].casefold()):
                names = sorted({
                    item["resource_name"]
                    for item in evidence_by_subscription.get(subscription_id.casefold(), ())
                    if item["resource_group"] == group and item["resource_name"]
                }, key=str.casefold)
                group_values.append({
                    "resource_group": group,
                    "resource_ids": sorted(set(values), key=str.casefold),
                    **({"resource_names": names} if names else {}),
                })
            details = evidence_by_subscription.get(subscription_id.casefold(), ())
            entries.append({
                "subscription_id": subscription_id,
                "subscription_name": subscription_name,
                "resource_groups": group_values,
                "resource_detail": "verified" if matching_ids or any(item["status"] == "matched" for item in details) else next((item["status"] for item in details if item["status"]), "unavailable"),
            })
        result[str(platform)] = {"subscriptions": entries}
    if row.get("is_global") == "true":
        return {"ALL": {"scope": "global", "resource_detail": "not_applicable"}}
    return result


def _impact_scope(row: Mapping[str, str]) -> str:
    if row.get("is_global") == "true":
        return "global"
    subscriptions = _json_value(row, "affected_subscription_names_json", [])
    services = _json_value(row, "impacted_services_json", [])
    regions = _json_value(row, "impacted_regions_json", [])
    parts = []
    if subscriptions:
        parts.append(f"subscriptions: {_readable(subscriptions)}")
    if services:
        parts.append(f"services: {_readable(services)}")
    if regions:
        parts.append(f"regions: {_readable(regions)}")
    return "; ".join(parts) or "unresolved impact"


@dataclass(frozen=True, slots=True)
class SlideRecord(Mapping[str, str]):
    values: tuple[tuple[str, str], ...]

    @classmethod
    def from_aggregate(cls, aggregate, *, status: str) -> "SlideRecord":
        editorial = _editorial(aggregate)
        item_id = str(aggregate["aggregate_id"])
        title = str(editorial.get("title") or aggregate["technology_or_service"] or aggregate["retiring_feature"] or "Unknown change")
        description = str(editorial.get("description") or f"Draft: {aggregate['retiring_feature'] or aggregate['technology_or_service'] or 'source item'}")
        original_description = _source_text(aggregate, (
            ("Advisor", "advisor_problem_descriptions_json"),
            ("Service Health", "service_health_problem_descriptions_json"),
        ))
        original_action = _source_text(aggregate, (
            ("Advisor", "advisor_actions_json"),
            ("Service Health", "service_health_actions_json"),
        ))
        source_values = _json_value(aggregate, "source_systems_json", [])
        sources = _readable([_source_name(str(value)) for value in source_values])
        links = _readable(_json_value(aggregate, "source_links_json", []))
        record_types = _json_value(aggregate, "record_types_json", [])
        change_type = _readable(record_types) or "unknown"
        editorial_state = "source-derived; human review not recorded"
        values = {
            "id_elemento": item_id,
            "titolo_breve": title,
            "descrizione_breve": description,
            "comitato_priorità": "",
            "comitato_descrizione": "",
            "comitato_retirement_date": "",
            "comitato_piattaforme": _readable(_json_value(aggregate, "platforms_json", [])),
            "retirement_date": str(aggregate["retirement_date"]),
            "stato_data": status,
            "tipo_cambiamento": change_type,
            "stato_editoriale": editorial_state,
            "descrizione_originale_completa": _overflow(original_description, item_id, "descrizione_originale_completa"),
            "azione_originale": _overflow(original_action, item_id, "azione_originale"),
            "fonti": sources,
            "link_fonti": links,
            "ambito_impatto": _impact_scope(aggregate),
            "id_advisor": _readable(_json_value(aggregate, "advisor_recommendation_ids_json", [])),
            "id_service_health": _readable(_json_value(aggregate, "service_health_tracking_ids_json", [])),
            "risorse_json": json.dumps(_resource_hierarchy(aggregate), ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        }
        values["risorse_json"] = _overflow(values["risorse_json"], item_id, "risorse_json")
        return cls(tuple((column, values[column]) for column in HEADER))

    def __getitem__(self, key: str) -> str:
        return dict(self.values)[key]

    def __iter__(self) -> Iterator[str]:
        return (column for column, _ in self.values)

    def __len__(self) -> int:
        return len(self.values)


class SlidesV1Contract(TsvContract[SlideRecord]):
    def validate(self, artifact, context):
        base = super().validate(artifact, context)
        diagnostics: list[Diagnostic] = []
        previous: tuple[str, str] | None = None
        seen: set[str] = set()
        for row in artifact.records:
            if tuple(row) != HEADER:
                diagnostics.append(Diagnostic("error", "invalid_slide_columns", "validation", "slides", context.run_id))
                continue
            aggregate_id = row["id_elemento"]
            if aggregate_id in seen:
                diagnostics.append(Diagnostic("error", "duplicate_slide_aggregate_id", "validation", "slides", context.run_id, record_ref=aggregate_id))
            seen.add(aggregate_id)
            order = (row["retirement_date"] or "9999-99-99", aggregate_id)
            if previous is not None and order < previous:
                diagnostics.append(Diagnostic("error", "slide_order_mismatch", "validation", "slides", context.run_id, record_ref=aggregate_id))
            previous = order
            if row["stato_data"] not in {
                "upcoming", "elapsed", "beyond_committee_window", "missing", "partial", "conflicting", "invalid",
            }:
                diagnostics.append(Diagnostic("error", "invalid_slide_date_status", "validation", "slides", context.run_id, record_ref=aggregate_id))
            if row["comitato_priorità"]:
                diagnostics.append(Diagnostic("error", "external_priority_required", "validation", "slides", context.run_id, record_ref=aggregate_id))
            if row["comitato_descrizione"] or row["comitato_retirement_date"]:
                diagnostics.append(Diagnostic("error", "editorial_committee_fields_must_be_empty", "validation", "slides", context.run_id, record_ref=aggregate_id))
        if diagnostics:
            return ValidationResult.invalid(tuple(diagnostics))
        return base


SLIDES_V1 = SlidesV1Contract(name="slides", header=HEADER, path="03_azure_retirements_slide.tsv")


def encode(artifact):
    return SLIDES_V1.encode(artifact)


def decode(data: bytes):
    return SLIDES_V1.decode(data)


def validate(artifact, context):
    return SLIDES_V1.validate(artifact, context)


__all__ = ["HEADER", "SLIDES_V1", "SlideRecord", "decode", "encode", "validate"]
