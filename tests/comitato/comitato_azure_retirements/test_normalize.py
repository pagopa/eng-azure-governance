from __future__ import annotations

from datetime import date

from src.comitato.comitato_azure_retirements.libs.normalize import (
    normalize_advisor_rows,
    normalize_service_health_rows,
)
from src.comitato.comitato_azure_retirements.libs.schemas import SERVICE_HEALTH_HEADERS


def _recommendation(
    *,
    recommendation_type_id: str,
    resource_id: str,
    learn_more_link: str = "",
    retirement_date: str = "2026-06-30",
) -> dict[str, object]:
    properties: dict[str, object] = {
        "recommendationTypeId": recommendation_type_id,
        "resourceMetadata": {"resourceId": resource_id},
        "learnMoreLink": learn_more_link,
    }
    if retirement_date:
        properties["extendedProperties"] = {"retirementDate": retirement_date}
    return {
        "id": "rec-1",
        "properties": properties,
        "_subscriptionId": "sub-1",
    }


def test_normalize_advisor_rows_marks_missing_metadata_as_resource_without_metadata() -> (
    None
):
    resource_id = "/subscriptions/SUB-1/resourceGroups/rg-1/providers/Microsoft.Compute/virtualMachines/vm-1"
    recommendation = _recommendation(
        recommendation_type_id="service-1", resource_id=resource_id
    )

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


def test_normalize_advisor_rows_marks_missing_resource_graph_as_metadata_without_resource() -> (
    None
):
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


def test_normalize_advisor_rows_keeps_recommendation_learn_more_link_without_metadata() -> (
    None
):
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


def test_normalize_advisor_rows_uses_extended_properties_when_metadata_is_missing() -> (
    None
):
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

    assert rows == []


def test_normalize_advisor_rows_keeps_only_retirements_in_next_year_with_resource() -> None:
    resource_id = "/subscriptions/sub-1/resourceGroups/rg-1/providers/Microsoft.Compute/virtualMachines/vm-1"
    recommendations = [
        _recommendation(
            recommendation_type_id="within-window",
            resource_id=resource_id,
            retirement_date="2027-06-18",
        ),
        _recommendation(
            recommendation_type_id="at-upper-bound",
            resource_id=resource_id,
            retirement_date="2027-06-18",
        ),
        _recommendation(
            recommendation_type_id="beyond-window",
            resource_id=resource_id,
            retirement_date="2027-06-19",
        ),
        _recommendation(
            recommendation_type_id="without-date",
            resource_id=resource_id,
            retirement_date="",
        ),
        _recommendation(
            recommendation_type_id="without-resource",
            resource_id="",
            retirement_date="2027-06-18",
        ),
    ]

    rows = normalize_advisor_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 18),
        scope_mode="fixture",
        recommendations=recommendations,
        metadata_by_key={},
        resource_graph_by_key={},
    )

    assert [row["recommendation_type_id"] for row in rows] == [
        "within-window",
        "at-upper-bound",
    ]


def test_normalize_advisor_rows_gates_raw_json_by_flag() -> None:
    recommendation = _recommendation(
        recommendation_type_id="service-1",
        resource_id="/subscriptions/sub-1/resourceGroups/rg-1/providers/Microsoft.Compute/virtualMachines/vm-1",
    )

    default_rows = normalize_advisor_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 18),
        scope_mode="fixture",
        recommendations=[recommendation],
        metadata_by_key={},
        resource_graph_by_key={},
    )
    verbose_rows = normalize_advisor_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 18),
        scope_mode="fixture",
        recommendations=[recommendation],
        metadata_by_key={},
        resource_graph_by_key={},
        include_raw_json=True,
    )

    assert default_rows[0]["raw_json"] == ""
    assert "recommendation" in verbose_rows[0]["raw_json"]


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
        event_impacted_service_regions=lambda _event: [
            {"name": "Storage", "guid": "guid-1", "region": "westeurope"},
            {"name": "Storage", "guid": "guid-1", "region": "northeurope"},
        ],
        build_recommended_actions=lambda _event: "Review mitigation plan",
    )

    assert "raw_json" not in SERVICE_HEALTH_HEADERS
    assert all("raw_json" not in row for row in rows)


def test_normalize_service_health_rows_filters_regions_and_uses_event_id_for_tracking() -> None:
    event = {
        "id": "/subscriptions/sub-1/providers/Microsoft.ResourceHealth/events/event-1",
        "name": "event-1",
        "_subscriptionId": "sub-1",
        "properties": {
            "eventType": "HealthAdvisory",
            "level": "Warning",
            "status": "Active",
            "trackingId": "different-tracking-id",
            "title": "Regional advisory",
            "impact": {
                "impactedService": "Storage",
                "impactedRegions": ["Italy North", "Global", "eastus"],
            },
        },
    }

    rows = normalize_service_health_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 18),
        scope_mode="fixture",
        events=[event],
        subscription_name_map={"sub-1": "Subscription One"},
        event_impacted_service_regions=lambda _event: [
            {"name": "Storage", "guid": "guid-1", "region": "Italy North"},
            {"name": "Storage", "guid": "guid-1", "region": "Global"},
            {"name": "Storage", "guid": "guid-1", "region": "eastus"},
        ],
        build_recommended_actions=lambda _event: "Review mitigation plan",
    )

    assert {(row["impacted_service"], row["impacted_region"]) for row in rows} == {
        ("Storage", "italynorth"),
        ("Storage", "global"),
    }
    assert all(row["tracking_id"] == row["event_id"] == "event-1" for row in rows)
    assert all(row["short_description_solution"] == "Regional advisory" for row in rows)


def test_normalize_service_health_rows_prefers_explicit_deadline_over_impact_dates() -> (
    None
):
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
        event_impacted_service_regions=lambda _event: [
            {"name": "AKS", "guid": "guid-1", "region": "westeurope"}
        ],
        build_recommended_actions=lambda _event: "Upgrade the node image.",
    )

    assert rows[0]["date_for_window"] == "2027-06-30"
    assert "retirement_date_derived_from_text" in rows[0]["diagnostic_flags"].split(",")


def test_normalize_service_health_rows_uses_mitigation_time_before_impact_start() -> (
    None
):
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
        event_impacted_service_regions=lambda _event: [
            {"name": "AKS", "guid": "guid-1", "region": "westeurope"}
        ],
        build_recommended_actions=lambda _event: "Track migration guidance.",
    )

    assert rows[0]["date_for_window"] == "2027-01-15"


def test_normalize_service_health_rows_ignores_version_like_tokens_as_dates() -> None:
    event = {
        "id": "/subscriptions/sub-1/providers/Microsoft.ResourceHealth/events/event-2b",
        "name": "event-2b",
        "_subscriptionId": "sub-1",
        "properties": {
            "eventType": "HealthAdvisory",
            "level": "Warning",
            "status": "Active",
            "title": "AKS node image version 2.0 retirement guidance",
            "summary": "Version 2.0 rollout guidance without a real deadline.",
            "description": "No explicit retirement date in this advisory.",
            "lastUpdateTime": "2026-06-18T12:00:00Z",
        },
    }

    rows = normalize_service_health_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 18),
        scope_mode="fixture",
        events=[event],
        subscription_name_map={"sub-1": "Subscription One"},
        event_impacted_service_regions=lambda _event: [
            {"name": "AKS", "guid": "guid-1", "region": "westeurope"}
        ],
        build_recommended_actions=lambda _event: "Track migration guidance.",
    )

    assert rows[0]["date_for_window"] == "2026-06-18"
    assert "retirement_date_derived_from_text" not in rows[0]["diagnostic_flags"].split(",")


def test_normalize_service_health_rows_preserves_service_region_pairs_from_callback() -> (
    None
):
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
        event_impacted_service_regions=lambda _event: [
            {"name": "Azure Front Door", "guid": "", "region": "Global"},
            {"name": "Azure CDN", "guid": "", "region": "eastus"},
        ],
        build_recommended_actions=lambda _event: "Review impact.",
    )

    assert len(rows) == 1
    assert {(row["impacted_service"], row["impacted_region"]) for row in rows} == {
        ("Azure Front Door", "global"),
    }
