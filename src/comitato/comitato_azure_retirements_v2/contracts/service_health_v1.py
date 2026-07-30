from collections.abc import Mapping

from ..domain.diagnostics import Diagnostic, ValidationResult
from ._base import TsvContract

HEADER = (
    "schema_version", "run_id", "as_of_date", "scope_mode", "record_type",
    "source_system", "service_health_event_id", "event_name", "tracking_id",
    "collection_subscription_id", "subscription_id", "subscription_name",
    "subscription_evidence_source", "event_type", "event_sub_type", "event_source",
    "event_level", "status", "title", "summary", "description_problem",
    "description_quality", "recommended_actions", "impact_start_time_raw",
    "impact_start_time", "impact_mitigation_time_raw", "impact_mitigation_time",
    "last_update_time_raw", "last_update_time", "retirement_date_raw", "retirement_date",
    "retirement_date_source", "retirement_date_quality", "impacted_service",
    "impacted_service_guid", "impacted_region", "normalized_impacted_region",
    "resource_evidence_source", "resource_evidence_status", "published_resource_id",
    "normalized_resource_id", "resource_name", "resource_group", "resource_type",
    "resource_location", "recommendation_type_id", "advisor_platform_state",
    "current_query_match", "resource_inventory_match_status",
    "subscription_inventory_match_status", "is_sensitive", "details_fetch_status",
    "diagnostic_flags", "provenance_json", "raw_record_ref",
)

SERVICE_HEALTH_V1_HEADER = HEADER

class ServiceHealthV1Contract(TsvContract[Mapping[str, str]]):
    def validate(self, artifact, context):
        base = super().validate(artifact, context)
        diagnostics: list[Diagnostic] = []
        event_ids: set[str] = set()
        refs: set[str] = set()
        for row in artifact.records:
            event_id = row.get("service_health_event_id", "")
            ref = row.get("raw_record_ref", "")
            if not event_id or not ref:
                diagnostics.append(Diagnostic("error", "missing_service_health_identity", "validation", "service-health", context.run_id, record_ref=event_id))
            if not ref or ref in refs:
                diagnostics.append(Diagnostic("error", "duplicate_raw_record_ref", "validation", "service-health", context.run_id, record_ref=ref))
            refs.add(ref)
            event_ids.add(event_id)
            if row.get("run_id") != context.run_id or row.get("status", "").casefold() != "active" or not row.get("tracking_id"):
                diagnostics.append(Diagnostic("error", "invalid_service_health_row", "validation", "service-health", context.run_id, record_ref=event_id))
            if row.get("record_type") != "service_health_event_global" and not row.get("subscription_id"):
                diagnostics.append(Diagnostic("error", "missing_affected_subscription", "validation", "service-health", context.run_id, record_ref=event_id))
        companion_refs = {str(item.get("raw_record_ref", "")) for item in artifact.companion_records}
        if refs != companion_refs:
            diagnostics.append(Diagnostic("error", "raw_pair_bijection_failed", "validation", "service-health", context.run_id))
        if diagnostics:
            return ValidationResult.invalid(tuple(diagnostics))
        return base


SERVICE_HEALTH_V1 = ServiceHealthV1Contract(
    name="service-health",
    header=HEADER,
    path="01_azure_service_health_advisories_raw.tsv",
    companion_path="01_azure_service_health_advisories_raw.jsonl",
)
