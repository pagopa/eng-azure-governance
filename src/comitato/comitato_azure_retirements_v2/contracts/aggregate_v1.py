from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date
import json
from typing import Any, Iterator

from ..domain.correlation import correlate_source_events
from ..domain.dates import parse_retirement_date
from ..domain.diagnostics import Diagnostic, ValidationResult
from ..domain.platforms import PlatformCatalogSnapshot, SubscriptionId, project_platforms
from ..domain.retirements import (
    AggregateId,
    SourceEventKey,
    aggregate_id_for,
    build_source_events,
)
from ._base import TsvContract
from .codecs import canonical_json


HEADER = (
    "schema_version", "run_id", "as_of_date", "aggregate_id", "correlation_status",
    "correlation_basis", "source_event_keys_json", "correlation_candidates_json",
    "source_systems_json", "record_types_json", "raw_record_refs_json",
    "advisor_recommendation_ids_json", "advisor_recommendation_type_ids_json",
    "service_health_event_ids_json", "service_health_tracking_ids_json",
    "technology_or_service", "retiring_feature", "advisor_problem_descriptions_json",
    "service_health_problem_descriptions_json", "advisor_actions_json",
    "service_health_actions_json", "retirement_date", "retirement_date_quality",
    "retirement_dates_json", "retirement_date_sources_json",
    "affected_subscription_ids_json", "affected_subscription_names_json", "is_global",
    "platforms_json", "platforms_subscriptions_json", "published_resource_ids_json",
    "normalized_resource_ids_json", "impacted_services_json", "impacted_regions_json",
    "source_links_json", "diagnostic_flags", "provenance_json",
)


def _values(value: object) -> tuple[Mapping[str, Any], ...]:
    artifact = getattr(value, "artifact", None)
    if artifact is not None:
        return _values(artifact)
    records = getattr(value, "records", None)
    if records is not None:
        return _values(records)
    if isinstance(value, Mapping):
        return (value,)
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        return tuple(row for item in value for row in _values(item))
    return ()


def _json(value: Any) -> str:
    return canonical_json(value)


def _strings(rows: Iterable[Mapping[str, Any]], field: str) -> tuple[str, ...]:
    values = {str(row.get(field, "")).strip() for row in rows}
    return tuple(sorted(value for value in values if value))


def _json_array(rows: Iterable[Mapping[str, Any]], field: str) -> str:
    values: set[str] = set()
    for row in rows:
        raw = row.get(field, "")
        if isinstance(raw, (list, tuple)):
            values.update(str(item).strip() for item in raw if str(item).strip())
        elif raw:
            try:
                parsed = json.loads(str(raw))
            except json.JSONDecodeError:
                parsed = [raw]
            if isinstance(parsed, list):
                values.update(str(item).strip() for item in parsed if str(item).strip())
            elif str(parsed).strip():
                values.add(str(parsed).strip())
    return _json(sorted(values))


def _unique_values(rows: Iterable[Mapping[str, Any]], fields: tuple[str, ...]) -> tuple[str, ...]:
    values: set[str] = set()
    for row in rows:
        for field in fields:
            value = str(row.get(field, "")).strip()
            if value:
                values.add(value)
    return tuple(sorted(values, key=lambda item: (item.casefold(), item)))


@dataclass(frozen=True, slots=True)
class AggregateRecord(Mapping[str, str]):
    values: tuple[tuple[str, str], ...]

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any]) -> "AggregateRecord":
        return cls(tuple((column, "" if row.get(column) is None else str(row.get(column))) for column in HEADER))

    def __getitem__(self, key: str) -> str:
        return dict(self.values)[key]

    def __iter__(self) -> Iterator[str]:
        return (key for key, _ in self.values)

    def __len__(self) -> int:
        return len(self.values)

    def __getattr__(self, key: str) -> str:
        if key in HEADER:
            return self[key]
        raise AttributeError(key)


def _display_projection(rows: tuple[Mapping[str, Any], ...], fields: tuple[str, ...]) -> str:
    values = _unique_values(rows, fields)
    return values[0] if len(values) == 1 else ""


def _date_projection(rows: tuple[Mapping[str, Any], ...]) -> tuple[str, str, tuple[dict[str, Any], ...], tuple[str, ...]]:
    claims = []
    quality_values: set[str] = set()
    for row in rows:
        claim = parse_retirement_date(
            row.get("retirement_date"),
            source_path=str(row.get("retirement_date_source", "")),
            source_system=str(row.get("source_system", "")),
            raw_record_ref=str(row.get("raw_record_ref", "")),
        )
        quality = str(row.get("retirement_date_quality", "")) or claim.quality
        quality_values.add(quality)
        if claim.value is not None:
            claims.append({
                "date": claim.value.isoformat(),
                "quality": "exact",
                "raw_record_refs": [claim.raw_record_ref] if claim.raw_record_ref else [],
                "source_path": claim.source_path,
                "source_system": claim.source_system,
            })
    by_date: dict[str, dict[str, Any]] = {}
    for item in claims:
        current = by_date.setdefault(item["date"], {**item, "raw_record_refs": []})
        current["raw_record_refs"] = sorted(set(current["raw_record_refs"]) | set(item["raw_record_refs"]))
    dates = tuple(by_date[key] for key in sorted(by_date))
    date_values = tuple(item["date"] for item in dates)
    if len(date_values) == 1:
        return date_values[0], "exact", dates, tuple(sorted({str(row.get("retirement_date_source", "")) for row in rows if row.get("retirement_date_source", "")}))
    if len(date_values) > 1:
        return "", "conflict", dates, tuple(sorted({str(row.get("retirement_date_source", "")) for row in rows if row.get("retirement_date_source", "")}))
    return "", "invalid" if "invalid" in quality_values else "missing", dates, ()


def _row_for_group(group, context, catalog: PlatformCatalogSnapshot) -> AggregateRecord:
    keys = tuple(event.key for event in group)
    rows = tuple(row for event in group for row in event.records)
    aggregate_id = aggregate_id_for(keys)
    source_refs = tuple(sorted({str(row.get("raw_record_ref", "")) for row in rows if row.get("raw_record_ref", "")}))
    advisor_rows = tuple(row for event in group if event.source == "advisor" for row in event.records)
    health_rows = tuple(row for event in group if event.source == "service-health" for row in event.records)
    subscription_ids = tuple(sorted({str(row.get("subscription_id", "")).strip().lower() for row in rows if str(row.get("subscription_id", "")).strip()}))
    subscription_names = tuple(sorted({str(row.get("subscription_name", "")).strip() for row in rows if str(row.get("subscription_name", "")).strip()}, key=lambda value: (value.casefold(), value)))
    explicit_global = bool(rows) and all(str(row.get("subscription_evidence_source", "")) == "explicit_global" for row in rows) and not subscription_ids
    projection = project_platforms(tuple(SubscriptionId(value) for value in subscription_ids), explicit_global, catalog, report="aggregate", run_id=context.run_id, record_refs={value: source_refs for value in subscription_ids})
    if not projection.is_valid or projection.value is None:
        raise ValueError("aggregate platform projection failed: " + ",".join(item.code for item in projection.diagnostics))
    retirement_date, date_quality, retirement_dates, date_sources = _date_projection(rows)
    flags = set(_unique_values(rows, ("diagnostic_flags",)))
    flags = {flag for value in flags for flag in value.split(",") if flag}
    if len(_unique_values(rows, ("service_name", "impacted_service"))) > 1:
        flags.add("conflicting_technology_or_service")
    if len(_unique_values(rows, ("retiring_feature",))) > 1:
        flags.add("conflicting_retiring_feature")
    record = {
        "schema_version": "1", "run_id": context.run_id, "as_of_date": context.as_of_date.isoformat(), "aggregate_id": aggregate_id.value,
        "correlation_status": "single_source", "correlation_basis": "",
        "source_event_keys_json": _json([key.value for key in sorted(keys)]), "correlation_candidates_json": _json([]),
        "source_systems_json": _json(_strings(rows, "source_system")), "record_types_json": _json(_strings(rows, "record_type")), "raw_record_refs_json": _json(source_refs),
        "advisor_recommendation_ids_json": _json(_strings(advisor_rows, "advisor_recommendation_id")), "advisor_recommendation_type_ids_json": _json(_strings(advisor_rows, "recommendation_type_id")),
        "service_health_event_ids_json": _json(_strings(health_rows, "service_health_event_id")), "service_health_tracking_ids_json": _json(_strings(health_rows, "tracking_id")),
        "technology_or_service": _display_projection(rows, ("service_name", "impacted_service")), "retiring_feature": _display_projection(rows, ("retiring_feature",)),
        "advisor_problem_descriptions_json": _json(list(_unique_values(advisor_rows, ("short_description_problem", "description")))), "service_health_problem_descriptions_json": _json(list(_unique_values(health_rows, ("description_problem",)))),
        "advisor_actions_json": _json_array(advisor_rows, "actions_json"), "service_health_actions_json": _json(list(_unique_values(health_rows, ("recommended_actions",)))),
        "retirement_date": retirement_date, "retirement_date_quality": date_quality, "retirement_dates_json": _json(retirement_dates), "retirement_date_sources_json": _json(date_sources),
        "affected_subscription_ids_json": _json(subscription_ids), "affected_subscription_names_json": _json(subscription_names), "is_global": "true" if explicit_global else "false",
        "platforms_json": _json(projection.value.platforms), "platforms_subscriptions_json": _json(projection.value.platforms_subscriptions),
        "published_resource_ids_json": _json(list(_unique_values(rows, ("published_resource_id",)))), "normalized_resource_ids_json": _json(list(_unique_values(rows, ("normalized_resource_id",)))),
        "impacted_services_json": _json(list(_unique_values(rows, ("impacted_service", "service_name")))), "impacted_regions_json": _json(list(_unique_values(rows, ("impacted_region",)))),
        "source_links_json": _json(list(_unique_values(rows, ("learn_more_link", "source_link")))), "diagnostic_flags": ",".join(sorted(flags)),
        "provenance_json": _json({"raw_record_refs": source_refs, "source_event_keys": [key.value for key in sorted(keys)]}),
    }
    return AggregateRecord.from_mapping(record)


def build_aggregate(
    advisor_records: object = (),
    service_health_records: object = (),
    *,
    context,
    catalog: PlatformCatalogSnapshot,
) -> tuple[AggregateRecord, ...]:
    events, _ = build_source_events(advisor_records, service_health_records)
    correlation = correlate_source_events(events, ())
    by_first_key = {group[0].key: group for group in correlation.groups}
    records: list[AggregateRecord] = []
    for group in correlation.groups:
        row = _row_for_group(group, context, catalog)
        decision = correlation.decision_by_event[group[0].key]
        values = dict(row.values)
        values["correlation_status"] = decision.status
        values["correlation_basis"] = decision.basis
        values["correlation_candidates_json"] = _json([key.value for key in decision.candidate_keys])
        records.append(AggregateRecord.from_mapping(values))
    return tuple(sorted(records, key=lambda row: row["aggregate_id"]))


class AggregateV1Contract(TsvContract[AggregateRecord]):
    def validate(self, artifact, context):
        base = super().validate(artifact, context)
        diagnostics: list[Diagnostic] = []
        previous = ""
        for row in artifact.records:
            if set(row) != set(HEADER):
                diagnostics.append(Diagnostic("error", "invalid_aggregate_columns", "validation", "aggregate", context.run_id))
                continue
            if row["aggregate_id"] < previous:
                diagnostics.append(Diagnostic("error", "aggregate_order_mismatch", "validation", "aggregate", context.run_id))
            previous = row["aggregate_id"]
            for field in (column for column in HEADER if column.endswith("_json")):
                try:
                    json.loads(row[field])
                except json.JSONDecodeError:
                    diagnostics.append(Diagnostic("error", f"invalid_{field}", "validation", "aggregate", context.run_id, record_ref=row["aggregate_id"]))
            if row["is_global"] not in {"true", "false"}:
                diagnostics.append(Diagnostic("error", "invalid_is_global", "validation", "aggregate", context.run_id, record_ref=row["aggregate_id"]))
            try:
                keys = tuple(SourceEventKey(*value.split(":", 1)) for value in json.loads(row["source_event_keys_json"]))
                if aggregate_id_for(keys).value != row["aggregate_id"]:
                    diagnostics.append(Diagnostic("error", "aggregate_id_mismatch", "validation", "aggregate", context.run_id, record_ref=row["aggregate_id"]))
            except (ValueError, TypeError, json.JSONDecodeError):
                diagnostics.append(Diagnostic("error", "invalid_source_event_keys", "validation", "aggregate", context.run_id, record_ref=row["aggregate_id"]))
            platforms = json.loads(row["platforms_json"])
            breakdown = json.loads(row["platforms_subscriptions_json"])
            if row["is_global"] == "true" and (platforms != ["ALL"] or breakdown != {"ALL": []}):
                diagnostics.append(Diagnostic("error", "invalid_global_platform_projection", "validation", "aggregate", context.run_id, record_ref=row["aggregate_id"]))
        if diagnostics:
            return ValidationResult.invalid(tuple(diagnostics))
        return base


AGGREGATE_V1 = AggregateV1Contract(name="aggregate", header=HEADER, path="02_azure_retirements_aggregate.tsv")


def encode(artifact):
    return AGGREGATE_V1.encode(artifact)


def decode(data: bytes):
    return AGGREGATE_V1.decode(data)


def validate(artifact, context):
    return AGGREGATE_V1.validate(artifact, context)


__all__ = ["AGGREGATE_V1", "AggregateRecord", "HEADER", "build_aggregate", "decode", "encode", "validate"]
