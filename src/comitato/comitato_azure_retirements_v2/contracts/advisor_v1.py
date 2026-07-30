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

ADVISOR_V1 = TsvContract(
    name="advisor",
    header=HEADER,
    path="01_azure_advisor_retirements_raw.tsv",
    companion_path="01_azure_advisor_retirements_raw.jsonl",
)
