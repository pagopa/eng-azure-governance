from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
import json

from ..domain.dates import CommitteeWindow, SlideEligibility, classify_retirement_date
from ..domain.diagnostics import Diagnostic, ValidationResult
from ._base import TsvContract


HEADER = (
    "schema_version", "aggregate_schema_version", "run_id", "as_of_date",
    "aggregate_id", "correlation_status", "correlation_basis", "source_event_keys_json",
    "correlation_candidates_json", "source_systems_json", "record_types_json",
    "raw_record_refs_json", "advisor_recommendation_ids_json",
    "advisor_recommendation_type_ids_json", "service_health_event_ids_json",
    "service_health_tracking_ids_json", "technology_or_service", "retiring_feature",
    "advisor_problem_descriptions_json", "service_health_problem_descriptions_json",
    "advisor_actions_json", "service_health_actions_json", "retirement_date",
    "retirement_date_quality", "retirement_dates_json", "retirement_date_sources_json",
    "affected_subscription_ids_json", "affected_subscription_names_json", "is_global",
    "platforms_json", "platforms_subscriptions_json", "published_resource_ids_json",
    "normalized_resource_ids_json", "impacted_services_json", "impacted_regions_json",
    "source_links_json", "diagnostic_flags", "provenance_json", "comitato_priorità",
    "comitato_descrizione_completa", "comitato_retirement_date", "comitato_piattaforme",
)


@dataclass(frozen=True, slots=True)
class SlideRecord(Mapping[str, str]):
    values: tuple[tuple[str, str], ...]

    @classmethod
    def from_aggregate(cls, aggregate, aggregate_schema_version: int) -> "SlideRecord":
        values = {}
        for column in HEADER:
            if column == "schema_version":
                values[column] = "1"
            elif column == "aggregate_schema_version":
                values[column] = str(aggregate_schema_version)
            elif column.startswith("comitato_"):
                values[column] = ""
            else:
                values[column] = str(aggregate[column])
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
        window = CommitteeWindow(context.as_of_date)
        for row in artifact.records:
            if tuple(row) != HEADER:
                diagnostics.append(Diagnostic("error", "invalid_slide_columns", "validation", "slides", context.run_id))
                continue
            aggregate_id = row["aggregate_id"]
            if aggregate_id in seen:
                diagnostics.append(Diagnostic("error", "duplicate_slide_aggregate_id", "validation", "slides", context.run_id, record_ref=aggregate_id))
            seen.add(aggregate_id)
            order = (row["retirement_date"], aggregate_id)
            if previous is not None and order < previous:
                diagnostics.append(Diagnostic("error", "slide_order_mismatch", "validation", "slides", context.run_id, record_ref=aggregate_id))
            previous = order
            if row["schema_version"] != "1" or row["aggregate_schema_version"] != "1":
                diagnostics.append(Diagnostic("error", "invalid_slide_schema_version", "validation", "slides", context.run_id, record_ref=aggregate_id))
            if row["run_id"] != context.run_id or row["as_of_date"] != context.as_of_date.isoformat():
                diagnostics.append(Diagnostic("error", "slide_context_mismatch", "validation", "slides", context.run_id, record_ref=aggregate_id))
            if classify_retirement_date(row, window) is not SlideEligibility.ELIGIBLE:
                diagnostics.append(Diagnostic("error", "ineligible_slide_record", "validation", "slides", context.run_id, record_ref=aggregate_id))
            for column in HEADER:
                if column.endswith("_json"):
                    try:
                        json.loads(row[column])
                    except json.JSONDecodeError:
                        diagnostics.append(Diagnostic("error", f"invalid_{column}", "validation", "slides", context.run_id, record_ref=aggregate_id))
            if any(row[column] for column in HEADER[-4:]):
                diagnostics.append(Diagnostic("error", "non_empty_committee_refinement", "validation", "slides", context.run_id, record_ref=aggregate_id))
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
