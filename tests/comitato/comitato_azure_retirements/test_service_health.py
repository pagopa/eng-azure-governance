from __future__ import annotations

from src.comitato.comitato_azure_retirements.libs.arm_client import ArmPageResult
from src.comitato.comitato_azure_retirements.libs.service_health import (
    build_recommended_actions,
    collect_events_for_subscriptions,
    event_impacted_regions,
    event_impacted_services,
)


class FakeArmClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, str] | None]] = []

    def list_with_nextlink(
        self,
        url: str,
        params: dict[str, str] | None = None,
        items_key: str = "value",
    ) -> ArmPageResult:
        self.calls.append((url, params))
        return ArmPageResult(items=[{"name": "event-a"}], page_count=2)


def test_collect_events_for_subscriptions_tags_rows_with_subscription() -> None:
    client = FakeArmClient()

    rows, pages = collect_events_for_subscriptions(
        client,
        subscriptions=["sub-1", "sub-2"],
        query_start_time="2025-01-01T00:00:00",
    )

    assert pages == {"sub-1": 2, "sub-2": 2}
    assert [row["_subscriptionId"] for row in rows] == ["sub-1", "sub-2"]


def test_event_impacted_services_uses_structured_service_list() -> None:
    event = {
        "properties": {
            "impact": {
                "impactedService": [
                    {"serviceName": "Storage", "serviceGuid": "guid-1"},
                    {"name": "Compute", "id": "guid-2"},
                ]
            }
        }
    }

    assert event_impacted_services(event) == [
        {"name": "Storage", "guid": "guid-1"},
        {"name": "Compute", "guid": "guid-2"},
    ]


def test_event_impacted_regions_falls_back_to_location() -> None:
    event = {"properties": {"location": "westeurope"}}
    assert event_impacted_regions(event) == ["westeurope"]


def test_build_recommended_actions_joins_multiple_entries() -> None:
    event = {
        "properties": {
            "recommendedActions": [
                {"actionText": "Migrate now"},
                {"description": "Review impact"},
            ]
        }
    }

    assert build_recommended_actions(event) == "Migrate now | Review impact"
