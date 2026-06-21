from __future__ import annotations

from datetime import date

from src.comitato.comitato_azure_retirements.libs.normalize_service_health import (
    normalize_service_health_rows,
)


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
        event_impacted_services=lambda _event: [{"name": "Storage", "guid": "guid-1"}],
        event_impacted_regions=lambda _event: ["westeurope"],
        build_recommended_actions=lambda _event: "Review guidance",
    )

    assert len(rows) == 1
    assert rows[0]["description_quality"] == "sensitive_blocked"
    flags = rows[0]["diagnostic_flags"].split(",")
    assert "service_health_sensitive" in flags
    assert "missing_description" in flags
