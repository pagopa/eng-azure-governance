from datetime import date, datetime, timezone

import pytest

from src.comitato.comitato_azure_retirements_v2.contracts import (
    AGGREGATE_V1,
    SLIDES_V1,
)
from src.comitato.comitato_azure_retirements_v2.reports.advisor import ADVISOR_REPORT
from src.comitato.comitato_azure_retirements_v2.reports.service_health import SERVICE_HEALTH_REPORT
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)


EXPECTED_HEADERS = {
    "advisor": "schema_version\trun_id\tas_of_date\tscope_mode\trecord_type\tsource_system\tadvisor_recommendation_id\trecommendation_type_id\trecommendation_status\tsubscription_id\tsubscription_name\tresource_linkage_source\tpublished_resource_id\tnormalized_resource_id\tresource_name\tresource_group\tresource_type\tlocation\ttags_json\tadvisor_metadata_id\tservice_name\tretiring_feature\tretirement_date_raw\tretirement_date\tretirement_date_source\tretirement_date_quality\timpact\trisk\tcategory\tsub_category\tlast_updated\tlabel\tshort_description_problem\tshort_description_solution\tdescription\tpotential_benefits\tlearn_more_link\tactions_json\tmetadata_match_status\tresource_inventory_match_status\tsubscription_inventory_match_status\tdiagnostic_flags\tprovenance_json\traw_record_ref",
    "service-health": "schema_version\trun_id\tas_of_date\tscope_mode\trecord_type\tsource_system\tservice_health_event_id\tevent_name\ttracking_id\tcollection_subscription_id\tsubscription_id\tsubscription_name\tsubscription_evidence_source\tevent_type\tevent_sub_type\tevent_source\tevent_level\tstatus\ttitle\tsummary\tdescription_problem\tdescription_quality\trecommended_actions\timpact_start_time_raw\timpact_start_time\timpact_mitigation_time_raw\timpact_mitigation_time\tlast_update_time_raw\tlast_update_time\tretirement_date_raw\tretirement_date\tretirement_date_source\tretirement_date_quality\timpacted_service\timpacted_service_guid\timpacted_region\tnormalized_impacted_region\tresource_evidence_source\tresource_evidence_status\tpublished_resource_id\tnormalized_resource_id\tresource_name\tresource_group\tresource_type\tresource_location\trecommendation_type_id\tadvisor_platform_state\tcurrent_query_match\tresource_inventory_match_status\tsubscription_inventory_match_status\tis_sensitive\tdetails_fetch_status\tdiagnostic_flags\tprovenance_json\traw_record_ref",
    "aggregate": "schema_version\trun_id\tas_of_date\taggregate_id\tcorrelation_status\tcorrelation_basis\tsource_event_keys_json\tcorrelation_candidates_json\tsource_systems_json\trecord_types_json\traw_record_refs_json\tadvisor_recommendation_ids_json\tadvisor_recommendation_type_ids_json\tservice_health_event_ids_json\tservice_health_tracking_ids_json\ttechnology_or_service\tretiring_feature\tadvisor_problem_descriptions_json\tservice_health_problem_descriptions_json\tadvisor_actions_json\tservice_health_actions_json\tretirement_date\tretirement_date_quality\tretirement_dates_json\tretirement_date_sources_json\taffected_subscription_ids_json\taffected_subscription_names_json\tis_global\tplatforms_json\tplatforms_subscriptions_json\tpublished_resource_ids_json\tnormalized_resource_ids_json\timpacted_services_json\timpacted_regions_json\tsource_links_json\tdiagnostic_flags\tprovenance_json",
    "slides": "schema_version\taggregate_schema_version\trun_id\tas_of_date\taggregate_id\tcorrelation_status\tcorrelation_basis\tsource_event_keys_json\tcorrelation_candidates_json\tsource_systems_json\trecord_types_json\traw_record_refs_json\tadvisor_recommendation_ids_json\tadvisor_recommendation_type_ids_json\tservice_health_event_ids_json\tservice_health_tracking_ids_json\ttechnology_or_service\tretiring_feature\tadvisor_problem_descriptions_json\tservice_health_problem_descriptions_json\tadvisor_actions_json\tservice_health_actions_json\tretirement_date\tretirement_date_quality\tretirement_dates_json\tretirement_date_sources_json\taffected_subscription_ids_json\taffected_subscription_names_json\tis_global\tplatforms_json\tplatforms_subscriptions_json\t published_resource_ids_json\tnormalized_resource_ids_json\timpacted_services_json\timpacted_regions_json\tsource_links_json\tdiagnostic_flags\tprovenance_json\tcomitato_priorità\tcomitato_descrizione_completa\tcomitato_retirement_date\tcomitato_piattaforme".replace("\t published", "\tpublished"),
}

ALL_V1_CONTRACTS = (ADVISOR_REPORT.contract, SERVICE_HEALTH_REPORT.contract, AGGREGATE_V1, SLIDES_V1)
RAW_V1_CONTRACTS = (ADVISOR_REPORT.contract, SERVICE_HEALTH_REPORT.contract)


@pytest.fixture
def run_context() -> RunContext:
    return RunContext(
        run_id="s06-empty",
        as_of_date=date(2026, 7, 30),
        created_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
        request=RunRequest(selector=ReportSelector.ALL),
        scope=Scope(subscription_ids=()),
        catalog_identity=CatalogIdentity(schema_version=1, sha256="c" * 64),
        dependency_plan=DependencyPlan(stages=("scope",)),
    )


@pytest.mark.parametrize("contract", ALL_V1_CONTRACTS, ids=lambda item: item.name)
def test_empty_tsv_is_exact_header_plus_lf(contract, run_context: RunContext) -> None:
    artifact = contract.empty_artifact(run_context)

    encoded = contract.encode(artifact)

    assert encoded.data == (EXPECTED_HEADERS[contract.name] + "\n").encode("utf-8")
    assert encoded.rows == 0


@pytest.mark.parametrize("contract", RAW_V1_CONTRACTS, ids=lambda item: item.name)
def test_empty_raw_companion_is_zero_bytes(contract, run_context: RunContext) -> None:
    artifact = contract.empty_artifact(run_context)

    assert contract.encode_companion(artifact).data == b""


@pytest.mark.parametrize("contract", ALL_V1_CONTRACTS, ids=lambda item: item.name)
def test_empty_contract_round_trips(contract, run_context: RunContext) -> None:
    artifact = contract.empty_artifact(run_context)
    encoded = contract.encode(artifact)

    assert contract.decode(encoded.data).records == ()
