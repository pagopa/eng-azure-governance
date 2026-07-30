from collections.abc import Mapping
from datetime import date, datetime
import json
import re

from ..domain.diagnostics import Diagnostic, ValidationResult
from ._base import TsvContract

HEADER = (
    "schema_version", "run_id", "as_of_date", "scope_mode", "record_type",
    "source_system", "advisor_recommendation_id", "recommendation_type_id",
    "recommendation_status", "subscription_id", "subscription_name",
    "resource_linkage_source", "published_resource_id", "normalized_resource_id",
    "resource_name", "resource_group", "resource_type", "location", "tags_json",
    "advisor_metadata_id", "service_name", "retiring_feature", "retirement_date_raw",
    "retirement_date", "retirement_date_source", "retirement_date_quality", "impact",
    "risk", "category", "sub_category", "last_updated", "label",
    "short_description_problem", "short_description_solution", "description",
    "potential_benefits", "learn_more_link", "actions_json", "metadata_match_status",
    "resource_inventory_match_status", "subscription_inventory_match_status",
    "diagnostic_flags", "provenance_json", "raw_record_ref",
)

ADVISOR_V1_HEADER = HEADER

class AdvisorV1Contract(TsvContract[Mapping[str, str]]):
    def validate(self, artifact, context):
        base = super().validate(artifact, context)
        diagnostics: list[Diagnostic] = []
        recommendation_ids: set[str] = set()
        refs: set[str] = set()
        row_refs: list[str] = []
        expected_keys = set(self.header)
        for row in artifact.records:
            if set(row) != expected_keys:
                diagnostics.append(Diagnostic("error", "invalid_advisor_columns", "validation", "advisor", context.run_id))
                continue
            recommendation_id = row.get("advisor_recommendation_id", "")
            ref = row.get("raw_record_ref", "")
            if not recommendation_id or recommendation_id in recommendation_ids:
                diagnostics.append(Diagnostic("error", "duplicate_or_missing_recommendation_id", "validation", "advisor", context.run_id, record_ref=recommendation_id))
            recommendation_ids.add(recommendation_id)
            if not ref or ref in refs:
                diagnostics.append(Diagnostic("error", "duplicate_or_missing_raw_record_ref", "validation", "advisor", context.run_id, record_ref=ref))
            refs.add(ref)
            row_refs.append(ref)
            if row.get("run_id") != context.run_id or row.get("schema_version") != "1" or row.get("record_type") != "advisor_retirement_recommendation" or row.get("source_system") != "azure_advisor" or row.get("recommendation_status", "").casefold() != "new" or not row.get("subscription_id"):
                diagnostics.append(Diagnostic("error", "invalid_advisor_row", "validation", "advisor", context.run_id, record_ref=recommendation_id))
            linkage = row.get("resource_linkage_source", "")
            if linkage not in {"resource_id", "legacy_id", "missing"}:
                diagnostics.append(Diagnostic("error", "invalid_resource_linkage_source", "validation", "advisor", context.run_id, record_ref=recommendation_id))
            published = row.get("published_resource_id", "")
            normalized = re.sub(r"/+", "/", published.strip()).casefold().rstrip("/") if published else ""
            if normalized != row.get("normalized_resource_id", ""):
                diagnostics.append(Diagnostic("error", "resource_normalization_mismatch", "validation", "advisor", context.run_id, record_ref=recommendation_id))
            if row.get("retirement_date_quality") not in {"exact", "missing", "invalid"}:
                diagnostics.append(Diagnostic("error", "invalid_retirement_date_quality", "validation", "advisor", context.run_id, record_ref=recommendation_id))
            if row.get("retirement_date"):
                try:
                    date.fromisoformat(row["retirement_date"])
                except ValueError:
                    diagnostics.append(Diagnostic("error", "invalid_retirement_date", "validation", "advisor", context.run_id, record_ref=recommendation_id))
            if row.get("last_updated"):
                try:
                    datetime.fromisoformat(row["last_updated"].replace("Z", "+00:00"))
                except ValueError:
                    diagnostics.append(Diagnostic("error", "invalid_last_updated", "validation", "advisor", context.run_id, record_ref=recommendation_id))
            for field in ("tags_json", "actions_json", "provenance_json"):
                if row.get(field):
                    try:
                        json.loads(row[field])
                    except json.JSONDecodeError:
                        diagnostics.append(Diagnostic("error", f"invalid_{field}", "validation", "advisor", context.run_id, record_ref=recommendation_id))
            for field, allowed in {
                "metadata_match_status": {"matched", "missing", "ambiguous"},
                "resource_inventory_match_status": {"matched", "missing", "ambiguous"},
                "subscription_inventory_match_status": {"matched", "missing"},
            }.items():
                if row.get(field) not in allowed:
                    diagnostics.append(Diagnostic("error", f"invalid_{field}", "validation", "advisor", context.run_id, record_ref=recommendation_id))
        companion_refs = tuple(str(item.get("raw_record_ref", "")) for item in artifact.companion_records if isinstance(item, Mapping))
        if len(companion_refs) != len(artifact.records) or tuple(row_refs) != companion_refs or len(set(companion_refs)) != len(companion_refs):
            diagnostics.append(Diagnostic("error", "raw_pair_bijection_failed", "validation", "advisor", context.run_id))
        for row, companion in zip(artifact.records, artifact.companion_records, strict=False):
            if not isinstance(companion, Mapping) or companion.get("raw_record_ref") != row.get("raw_record_ref") or companion.get("advisor_recommendation_id") != row.get("advisor_recommendation_id"):
                diagnostics.append(Diagnostic("error", "raw_evidence_not_reproducible", "validation", "advisor", context.run_id, record_ref=row.get("advisor_recommendation_id", "")))
        if diagnostics:
            return ValidationResult.invalid(tuple(diagnostics))
        return base


ADVISOR_V1 = AdvisorV1Contract(
    name="advisor",
    header=HEADER,
    path="01_azure_advisor_retirements_raw.tsv",
    companion_path="01_azure_advisor_retirements_raw.jsonl",
)


def encode(artifact):
    return ADVISOR_V1.encode(artifact)


def decode(data: bytes):
    return ADVISOR_V1.decode(data)


def validate(artifact, context):
    return ADVISOR_V1.validate(artifact, context)
