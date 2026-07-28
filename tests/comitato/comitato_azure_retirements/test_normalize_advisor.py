from __future__ import annotations

from datetime import date

from src.comitato.comitato_azure_retirements.libs.normalize_advisor import (
    _resource_type_from_resource_id,
    normalize_advisor_rows,
)


def test_resource_type_fallback_reconstructs_nested_arm_type() -> None:
    resource_id = (
        "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Network/"
        "networkWatchers/watcher/flowLogs/flow"
    )

    assert _resource_type_from_resource_id(resource_id) == (
        "microsoft.network/networkwatchers/flowlogs"
    )


def test_resource_type_fallback_reconstructs_ordinary_arm_type() -> None:
    resource_id = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Web/sites/app"

    assert _resource_type_from_resource_id(resource_id) == "microsoft.web/sites"


def test_subscription_scoped_resource_keeps_blank_group_and_flag() -> None:
    resource_id = "/subscriptions/sub/providers/Microsoft.Blueprint/blueprints/security"
    recommendation = {
        "id": "rec-1",
        "properties": {
            "recommendationTypeId": "service-1",
            "resourceMetadata": {"resourceId": resource_id},
        },
        "_subscriptionId": "sub",
    }

    rows = normalize_advisor_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 21),
        scope_mode="live",
        recommendations=[recommendation],
        metadata_by_key={},
        resource_graph_by_key={},
    )

    assert rows[0]["resource_group"] == ""
    assert rows[0]["resource_type"] == "microsoft.blueprint/blueprints"
    assert "subscription_scope" in rows[0]["diagnostic_flags"].split(",")


def test_resource_graph_type_overrides_arm_type_fallback() -> None:
    resource_id = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Web/sites/app"
    recommendation = {
        "id": "rec-1",
        "properties": {
            "recommendationTypeId": "service-1",
            "resourceMetadata": {"resourceId": resource_id},
        },
        "_subscriptionId": "sub",
    }

    rows = normalize_advisor_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 21),
        scope_mode="live",
        recommendations=[recommendation],
        metadata_by_key={},
        resource_graph_by_key={
            ("service-1", resource_id.lower()): {"type": "Custom.Provider/widgets"}
        },
    )

    assert rows[0]["resource_type"] == "custom.provider/widgets"


def test_normalize_advisor_rows_fallback_service_name_from_impacted_field() -> None:
    recommendation = {
        "id": "rec-1",
        "properties": {
            "recommendationTypeId": "service-1",
            "resourceMetadata": {
                "resourceId": "/subscriptions/sub-1/resourceGroups/rg-1/providers/Microsoft.Web/sites/app-1"
            },
            "impactedField": "MICROSOFT.WEB/SITES",
            "shortDescription": {"problem": "Upgrade before retirement"},
        },
        "_subscriptionId": "sub-1",
    }

    rows = normalize_advisor_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 21),
        scope_mode="live",
        recommendations=[recommendation],
        metadata_by_key={},
        resource_graph_by_key={},
    )

    assert rows[0]["service_name"] == "App service"
    assert rows[0]["join_quality"] == "recommendation_only"
    assert "recommendation_without_metadata" in rows[0]["diagnostic_flags"].split(",")


def test_normalize_advisor_rows_backfills_subscription_name_from_scope_map() -> None:
    recommendation = {
        "id": "rec-1",
        "properties": {
            "recommendationTypeId": "service-1",
            "resourceMetadata": {
                "resourceId": "/subscriptions/sub-1/resourceGroups/rg-1/providers/Microsoft.KeyVault/vaults/kv-1"
            },
            "shortDescription": {"problem": "Upgrade SDK"},
        },
        "_subscriptionId": "sub-1",
    }

    rows = normalize_advisor_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 21),
        scope_mode="live",
        recommendations=[recommendation],
        metadata_by_key={},
        resource_graph_by_key={},
        subscription_name_map={"sub-1": "PROD-IO"},
    )

    assert rows[0]["subscription_id"] == "sub-1"
    assert rows[0]["subscription_name"] == "PROD-IO"


def test_normalize_advisor_rows_filters_regions_and_extracts_problem_description() -> None:
    recommendation = {
        "id": "rec-1",
        "properties": {
            "recommendationTypeId": "service-1",
            "resourceMetadata": {
                "resourceId": "/subscriptions/sub-1/resourceGroups/rg-1/providers/Microsoft.Web/sites/app-1"
            },
            "shortDescription": {"problem": "Short problem", "solution": "Short solution"},
            "description": {"problem": "The complete problem description", "solution": "Do not export"},
        },
        "_subscriptionId": "sub-1",
    }

    rows = normalize_advisor_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 21),
        scope_mode="live",
        recommendations=[recommendation],
        metadata_by_key={},
        resource_graph_by_key={
            ("service-1", recommendation["properties"]["resourceMetadata"]["resourceId"].lower()): {
                "location": "Italy North",
            }
        },
    )

    assert rows[0]["location"] == "italynorth"
    assert rows[0]["description"] == "The complete problem description"

    excluded_rows = normalize_advisor_rows(
        run_id="run-1",
        as_of_date=date(2026, 6, 21),
        scope_mode="live",
        recommendations=[recommendation],
        metadata_by_key={},
        resource_graph_by_key={
            ("service-1", recommendation["properties"]["resourceMetadata"]["resourceId"].lower()): {
                "location": "eastus",
            }
        },
    )

    assert excluded_rows == []
