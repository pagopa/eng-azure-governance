from collections.abc import Mapping

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
        for row in artifact.records:
            recommendation_id = row.get("advisor_recommendation_id", "")
            ref = row.get("raw_record_ref", "")
            if not recommendation_id or recommendation_id in recommendation_ids:
                diagnostics.append(Diagnostic("error", "duplicate_or_missing_recommendation_id", "validation", "advisor", context.run_id, record_ref=recommendation_id))
            recommendation_ids.add(recommendation_id)
            if not ref or ref in refs:
                diagnostics.append(Diagnostic("error", "duplicate_or_missing_raw_record_ref", "validation", "advisor", context.run_id, record_ref=ref))
            refs.add(ref)
            if row.get("run_id") != context.run_id or row.get("recommendation_status", "").casefold() != "new" or not row.get("subscription_id"):
                diagnostics.append(Diagnostic("error", "invalid_advisor_row", "validation", "advisor", context.run_id, record_ref=recommendation_id))
        companion_refs = {str(item.get("raw_record_ref", "")) for item in artifact.companion_records}
        if refs != companion_refs:
            diagnostics.append(Diagnostic("error", "raw_pair_bijection_failed", "validation", "advisor", context.run_id))
        if diagnostics:
            return ValidationResult.invalid(tuple(diagnostics))
        return base


ADVISOR_V1 = AdvisorV1Contract(
    name="advisor",
    header=HEADER,
    path="01_azure_advisor_retirements_raw.tsv",
    companion_path="01_azure_advisor_retirements_raw.jsonl",
)
