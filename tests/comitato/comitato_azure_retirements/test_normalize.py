from __future__ import annotations

from datetime import date

from src.comitato.comitato_azure_retirements.libs.normalize import normalize_advisor_rows


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
