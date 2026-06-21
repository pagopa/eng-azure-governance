from __future__ import annotations

from datetime import date

from src.comitato.comitato_azure_retirements.libs.normalize_advisor import (
    normalize_advisor_rows,
)


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
