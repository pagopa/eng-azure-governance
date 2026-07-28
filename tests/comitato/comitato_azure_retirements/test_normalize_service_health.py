from __future__ import annotations

from datetime import date

from src.comitato.comitato_azure_retirements.libs.normalize_service_health import (
    normalize_service_health_rows,
)
from src.comitato.comitato_azure_retirements.libs.service_health_resources import (
    ImpactedResource,
)
from src.comitato.comitato_azure_retirements.libs.service_health_resource_resolution import (
    ResourceEvidence,
)


def health_event(tracking_id: str, subscription_id: str, description: str) -> dict[str, object]:
    return {
        "id": (
            f"/subscriptions/{subscription_id}/providers/"
            f"Microsoft.ResourceHealth/events/{tracking_id}"
        ),
        "name": tracking_id,
        "_subscriptionId": subscription_id,
        "properties": {
            "eventType": "HealthAdvisory",
            "eventSubType": "Retirement",
            "level": "Warning",
            "status": "Active",
            "title": "Retirement advisory",
            "description": description,
            "impact": {
                "impactedService": "Storage",
                "impactedRegions": ["westeurope"],
            },
        },
    }


def test_normalized_resource_row_has_ascii_description_priority_and_resource() -> None:
    rows = normalize_service_health_rows(
        run_id="run-1",
        as_of_date=date(2026, 7, 28),
        scope_mode="fixture",
        events=[
            health_event(
                "TRK-1",
                "sub-1",
                '<p>Migrate by 30 September 2026. <a href="https://aka.ms/migrate">Guide</a></p>',
            )
        ],
        subscription_name_map={"sub-1": "Production"},
        impacted_resources_by_event={
            ("trk-1", "sub-1"): [
                ImpactedResource(
                    resource_id="/subscriptions/sub-1/resourceGroups/rg-one/providers/Microsoft.Storage/storageAccounts/a",
                    resource_group="rg-one",
                    resource_type="Microsoft.Storage/storageAccounts",
                    region="westeurope",
                    info_json="[]",
                )
            ]
        },
        event_impacted_service_regions=lambda event: [{"name": "Storage", "guid": "", "region": "westeurope"}],
        build_recommended_actions=lambda event: "",
    )

    assert len(rows) == 1
    assert rows[0]["description_problem"].endswith("Guide (https://aka.ms/migrate)")
    assert rows[0]["priority"] == "Critico"
    assert rows[0]["resource_granularity"] == "resource"
    assert rows[0]["resource_group"] == "rg-one"
    assert rows[0]["record_type"] == "service_health_event_resource"
    assert rows[0]["resource_resolution_source"] == "service_health_arg"
    assert rows[0]["resource_resolution_status"] == "active"


def test_normalized_row_never_leaves_subscription_or_resource_fields_blank() -> None:
    row = normalize_service_health_rows(
        run_id="run-1",
        as_of_date=date(2026, 7, 28),
        scope_mode="fixture",
        events=[health_event("TRK-1", "sub-1", "No qualified deadline")],
        subscription_name_map={},
        impacted_resources_by_event={},
        event_impacted_service_regions=lambda event: [{"name": "Storage", "guid": "", "region": "westeurope"}],
        build_recommended_actions=lambda event: "",
    )[0]

    assert row["subscription_name"] == "sub-1"
    assert row["priority"] == "Debito"
    assert [row[key] for key in ("resource_granularity", "resource_id", "resource_group", "resource_type")] == [
        "not_available",
        "not_available",
        "not_available",
        "not_available",
    ]
    assert row["resource_resolution_source"] == "not_available"
    assert row["resource_resolution_status"] == "not_published"


def test_normalize_service_health_rows_emits_advisor_provenance_and_recovery_flag() -> None:
    event = health_event("TRK-1", "sub-2", "Advisor recovered")
    event["_resource_resolution_subscription_synthesized"] = True
    rows = normalize_service_health_rows(
        run_id="run-1",
        as_of_date=date(2026, 7, 28),
        scope_mode="fixture",
        events=[event],
        subscription_name_map={"sub-2": "Recovered"},
        impacted_resources_by_event={
            ("trk-1", "sub-2"): [
                ResourceEvidence(
                    tracking_id="TRK-1",
                    subscription_id="sub-2",
                    resource_id="/subscriptions/sub-2/resourceGroups/rg/providers/Microsoft.Web/sites/app",
                    resource_group="rg",
                    resource_type="Microsoft.Web/sites",
                    region="westeurope",
                    source="advisor_metadata_query",
                    status="active",
                    recommendation_type_id="rec-1",
                    current_query_match=True,
                )
            ]
        },
        event_impacted_service_regions=lambda _event: [{"name": "Web", "guid": "", "region": "westeurope"}],
        build_recommended_actions=lambda _event: "",
    )

    assert rows[0]["resource_resolution_source"] == "advisor_metadata_query"
    assert rows[0]["recommendation_type_id"] == "rec-1"
    assert rows[0]["current_query_match"] == "true"
    assert "service_health_subscription_recovered_from_advisor" in rows[0]["diagnostic_flags"]


def test_normalize_service_health_rows_marks_sensitive_without_description() -> None:
    event = {
        "id": "/subscriptions/sub-1/providers/Microsoft.ResourceHealth/events/event-1",
        "name": "event-1",
        "_subscriptionId": "sub-1",
        "properties": {
            "eventType": "HealthAdvisory",
            "eventSubType": "Retirement",
            "level": "Warning",
            "status": "Active",
            "title": "Sensitive event",
            "summary": "",
            "description": "",
            "isSensitive": True,
        },
    }

    rows = normalize_service_health_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 21),
        scope_mode="live",
        events=[event],
        subscription_name_map={"sub-1": "Subscription One"},
        event_impacted_service_regions=lambda _event: [
            {"name": "Storage", "guid": "guid-1", "region": "westeurope"}
        ],
        build_recommended_actions=lambda _event: "Review guidance",
    )

    assert len(rows) == 1
    assert rows[0]["description_quality"] == "sensitive_blocked"
    flags = rows[0]["diagnostic_flags"].split(",")
    assert "service_health_sensitive" in flags
    assert "missing_description" in flags


def test_normalize_service_health_rows_accepts_empty_article_list() -> None:
    event = {
        "id": "/subscriptions/sub-1/providers/Microsoft.ResourceHealth/events/event-1",
        "name": "event-1",
        "_subscriptionId": "sub-1",
        "properties": {
            "eventType": "HealthAdvisory",
            "level": "Warning",
            "status": "Active",
            "article": [],
            "description": "Fallback description",
        },
    }

    rows = normalize_service_health_rows(
        run_id="run-1",
        as_of_date=date(2026, 7, 28),
        scope_mode="live",
        events=[event],
        subscription_name_map={"sub-1": "Subscription One"},
        event_impacted_service_regions=lambda _event: [
            {"name": "Storage", "guid": "", "region": "westeurope"}
        ],
        build_recommended_actions=lambda _event: "",
    )

    assert len(rows) == 1
    assert rows[0]["description_problem"] == "Fallback description"
