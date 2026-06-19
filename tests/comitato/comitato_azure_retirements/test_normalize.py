from __future__ import annotations

from datetime import date

from src.comitato.comitato_azure_retirements.libs.normalize import (
    normalize_advisor_rows,
    normalize_service_health_rows,
)
from src.comitato.comitato_azure_retirements.libs.schemas import SERVICE_HEALTH_HEADERS


def _recommendation(*, recommendation_type_id: str, resource_id: str, learn_more_link: str = "") -> dict[str, object]:
    return {
        "id": "rec-1",
        "properties": {
            "recommendationTypeId": recommendation_type_id,
            "resourceMetadata": {"resourceId": resource_id},
            "learnMoreLink": learn_more_link,
        },
        "_subscriptionId": "sub-1",
    }


def test_normalize_advisor_rows_marks_missing_metadata_as_resource_without_metadata() -> None:
    resource_id = "/subscriptions/SUB-1/resourceGroups/rg-1/providers/Microsoft.Compute/virtualMachines/vm-1"
    recommendation = _recommendation(recommendation_type_id="service-1", resource_id=resource_id)

    rows = normalize_advisor_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 18),
        scope_mode="fixture",
        recommendations=[recommendation],
        metadata_by_key={},
        resource_graph_by_key={
            ("service-1", resource_id.lower()): {
                "resourceId": resource_id.lower(),
                "type": "Microsoft.Compute/virtualMachines",
            }
        },
    )

    flags = set(filter(None, rows[0]["diagnostic_flags"].split(",")))
    assert "resource_without_metadata" in flags
    assert "metadata_without_resource" not in flags


def test_normalize_advisor_rows_marks_missing_resource_graph_as_metadata_without_resource() -> None:
    recommendation = _recommendation(
        recommendation_type_id="service-1",
        resource_id="/subscriptions/sub-1/resourceGroups/rg-1/providers/Microsoft.Storage/storageAccounts/stg1",
    )
    metadata = {
        "id": "meta-1",
        "properties": {
            "sourceProperties": {"serviceRetirement": {"serviceId": "service-1"}},
            "resourceMetadata": {"singular": "Storage account"},
        },
    }

    rows = normalize_advisor_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 18),
        scope_mode="fixture",
        recommendations=[recommendation],
        metadata_by_key={"service-1": metadata},
        resource_graph_by_key={},
    )

    flags = set(filter(None, rows[0]["diagnostic_flags"].split(",")))
    assert "metadata_without_resource" in flags
    assert "resource_without_metadata" not in flags


def test_normalize_advisor_rows_keeps_recommendation_learn_more_link_without_metadata() -> None:
    recommendation = _recommendation(
        recommendation_type_id="service-1",
        resource_id="/subscriptions/sub-1/resourceGroups/rg-1/providers/Microsoft.Compute/virtualMachines/vm-1",
        learn_more_link="https://learn.example/retirement",
    )

    rows = normalize_advisor_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 18),
        scope_mode="fixture",
        recommendations=[recommendation],
        metadata_by_key={},
        resource_graph_by_key={},
    )

    assert rows[0]["learn_more_link"] == "https://learn.example/retirement"


def test_normalize_advisor_rows_uses_extended_properties_when_metadata_is_missing() -> None:
    resource_id = "/subscriptions/sub-1/resourceGroups/rg-1/providers/Microsoft.KeyVault/vaults/kv-1"
    recommendation = {
        "id": "rec-1",
        "properties": {
            "recommendationTypeId": "service-1",
            "resourceMetadata": {"resourceId": resource_id},
            "impactedField": "MICROSOFT.KEYVAULT/VAULTS",
            "extendedProperties": {
                "retirementFeatureName": "API versions prior to 2026-02-01",
                "retirementDate": "2027-02-27",
            },
            "shortDescription": {
                "problem": "Azure Key Vault API versions prior to 2026-02-01 are being retired",
            },
        },
        "_subscriptionId": "sub-1",
    }

    rows = normalize_advisor_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 18),
        scope_mode="live",
        recommendations=[recommendation],
        metadata_by_key={},
        resource_graph_by_key={
            ("service-1", resource_id.lower()): {
                "resourceId": resource_id.lower(),
                "type": "Microsoft.KeyVault/vaults",
            }
        },
    )

    assert rows[0]["service_name"] == "Key vault"
    assert rows[0]["retiring_feature"] == "API versions prior to 2026-02-01"
    assert rows[0]["retirement_date"] == "2027-02-27"


def test_normalize_advisor_rows_emits_single_catalog_row_per_metadata_id() -> None:
    metadata = {
        "id": "meta-1",
        "properties": {
            "sourceProperties": {
                "serviceRetirement": {
                    "serviceId": "service-1",
                    "retirementFeatureName": "Legacy feature",
                }
            },
            "resourceMetadata": {"singular": "Compute"},
        },
    }

    rows = normalize_advisor_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 18),
        scope_mode="schema_only",
        recommendations=[],
        metadata_by_key={"meta-1": metadata, "service-1": metadata},
        resource_graph_by_key={},
    )

    assert len(rows) == 1
    assert rows[0]["record_type"] == "advisor_catalog_retirement"
    assert rows[0]["advisor_metadata_id"] == "meta-1"
    assert rows[0]["recommendation_type_id"] == "service-1"


def test_service_health_schema_and_rows_do_not_embed_raw_json() -> None:
    large_raw_payload = "x" * 10_000
    event = {
        "id": "/subscriptions/sub-1/providers/Microsoft.ResourceHealth/events/event-1",
        "name": "event-1",
        "_subscriptionId": "sub-1",
        "properties": {
            "eventType": "HealthAdvisory",
            "level": "Warning",
            "status": "Active",
            "title": "Regional advisory",
            "summary": "A regional advisory is active.",
            "description": "Review the advisory.",
            "impact": {"largeEvidence": large_raw_payload},
        },
    }

    rows = normalize_service_health_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 18),
        scope_mode="fixture",
        events=[event],
        subscription_name_map={"sub-1": "Subscription One"},
        event_impacted_services=lambda _event: [{"name": "Storage", "guid": "guid-1"}],
        event_impacted_regions=lambda _event: ["westeurope", "northeurope"],
        build_recommended_actions=lambda _event: "Review mitigation plan",
    )

    assert "raw_json" not in SERVICE_HEALTH_HEADERS
    assert all("raw_json" not in row for row in rows)


def test_normalize_service_health_rows_prefers_explicit_deadline_over_impact_dates() -> None:
    event = {
        "id": "/subscriptions/sub-1/providers/Microsoft.ResourceHealth/events/event-1",
        "name": "event-1",
        "_subscriptionId": "sub-1",
        "properties": {
            "eventType": "HealthAdvisory",
            "level": "Warning",
            "status": "Active",
            "title": "AKS Ubuntu 22.04 node image will be retired on 30 June 2027",
            "summary": "Plan your migration before retirement.",
            "description": "Impact starts in 2026 but the retirement deadline remains in 2027.",
            "impactStartTime": "2026-10-01T00:00:00Z",
            "impactMitigationTime": "2027-05-15T00:00:00Z",
            "lastUpdateTime": "2026-06-18T12:00:00Z",
        },
    }

    rows = normalize_service_health_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 18),
        scope_mode="fixture",
        events=[event],
        subscription_name_map={"sub-1": "Subscription One"},
        event_impacted_services=lambda _event: [{"name": "AKS", "guid": "guid-1"}],
        event_impacted_regions=lambda _event: ["westeurope"],
        build_recommended_actions=lambda _event: "Upgrade the node image.",
    )

    assert rows[0]["date_for_window"] == "2027-06-30"


def test_normalize_service_health_rows_uses_mitigation_time_before_impact_start() -> None:
    event = {
        "id": "/subscriptions/sub-1/providers/Microsoft.ResourceHealth/events/event-2",
        "name": "event-2",
        "_subscriptionId": "sub-1",
        "properties": {
            "eventType": "HealthAdvisory",
            "level": "Warning",
            "status": "Active",
            "title": "Retirement notice",
            "summary": "Migration details will follow.",
            "description": "No explicit retirement date is available yet.",
            "impactStartTime": "2026-09-01T00:00:00Z",
            "impactMitigationTime": "2027-01-15T00:00:00Z",
            "lastUpdateTime": "2026-06-18T12:00:00Z",
        },
    }

    rows = normalize_service_health_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 18),
        scope_mode="fixture",
        events=[event],
        subscription_name_map={"sub-1": "Subscription One"},
        event_impacted_services=lambda _event: [{"name": "AKS", "guid": "guid-1"}],
        event_impacted_regions=lambda _event: ["westeurope"],
        build_recommended_actions=lambda _event: "Track migration guidance.",
    )

    assert rows[0]["date_for_window"] == "2027-01-15"


def test_normalize_service_health_rows_preserves_service_region_pairs_from_callback() -> None:
    event = {
        "id": "/subscriptions/sub-1/providers/Microsoft.ResourceHealth/events/event-3",
        "name": "event-3",
        "_subscriptionId": "sub-1",
        "properties": {
            "eventType": "HealthAdvisory",
            "level": "Warning",
            "status": "Active",
            "title": "Regional advisory",
            "summary": "Pairing should be preserved.",
            "description": "Do not generate cross-product rows.",
        },
    }

    rows = normalize_service_health_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 18),
        scope_mode="fixture",
        events=[event],
        subscription_name_map={"sub-1": "Subscription One"},
        event_impacted_services=lambda _event: [
            {"name": "Azure Front Door", "guid": ""},
            {"name": "Azure CDN", "guid": ""},
        ],
        event_impacted_regions=lambda _event: ["Global", "eastus"],
        event_impacted_service_regions=lambda _event: [
            {"name": "Azure Front Door", "guid": "", "region": "Global"},
            {"name": "Azure CDN", "guid": "", "region": "eastus"},
        ],
        build_recommended_actions=lambda _event: "Review impact.",
    )

    assert len(rows) == 2
    assert {(row["impacted_service"], row["impacted_region"]) for row in rows} == {
        ("Azure Front Door", "Global"),
        ("Azure CDN", "eastus"),
    }
