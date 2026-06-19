from __future__ import annotations

from src.comitato.comitato_azure_retirements.libs.arm_client import ArmPageResult
from src.comitato.comitato_azure_retirements.libs.service_health import (
    build_recommended_actions,
    collect_events_for_subscriptions,
    event_impacted_regions,
    event_impacted_services,
    filter_health_advisory_events,
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

    rows, pages, failures = collect_events_for_subscriptions(
        client,
        subscriptions=["sub-1", "sub-2"],
        query_start_time="2025-01-01T00:00:00",
    )

    assert pages == {"sub-1": 2, "sub-2": 2}
    assert [row["_subscriptionId"] for row in rows] == ["sub-1", "sub-2"]
    assert failures == []


class FailingServiceHealthClient(FakeArmClient):
    def list_with_nextlink(
        self,
        url: str,
        params: dict[str, str] | None = None,
        items_key: str = "value",
    ) -> ArmPageResult:
        del params, items_key
        self.calls.append((url, None))
        if url.endswith("/subscriptions/sub-2/providers/Microsoft.ResourceHealth/events"):
            raise RuntimeError("HTTP 502 for sub-2")
        return ArmPageResult(items=[{"name": "event-a"}], page_count=1)


def test_collect_events_for_subscriptions_records_failures_in_degraded_mode() -> None:
    client = FailingServiceHealthClient()

    rows, pages, failures = collect_events_for_subscriptions(
        client,
        subscriptions=["sub-1", "sub-2"],
        query_start_time="2025-01-01T00:00:00",
        allow_degraded=True,
    )

    assert [row["_subscriptionId"] for row in rows] == ["sub-1"]
    assert pages == {"sub-1": 1}
    assert failures == [{"subscription_id": "sub-2", "error": "HTTP 502 for sub-2"}]


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


def test_event_impacted_services_supports_live_impact_list_shape() -> None:
    event = {
        "properties": {
            "impact": [
                {
                    "impactedService": "Azure Front Door",
                    "impactedRegions": [{"impactedRegion": "Global"}],
                },
                {
                    "impactedService": "Azure CDN",
                    "impactedRegions": [{"impactedRegion": "eastus"}],
                },
            ]
        }
    }

    assert event_impacted_services(event) == [
        {"name": "Azure Front Door", "guid": ""},
        {"name": "Azure CDN", "guid": ""},
    ]


def test_event_impacted_regions_supports_live_impact_list_shape() -> None:
    event = {
        "properties": {
            "impact": [
                {
                    "impactedService": "Azure Front Door",
                    "impactedRegions": [
                        {"impactedRegion": "Global"},
                        {"impactedRegion": "eastus"},
                    ],
                },
                {
                    "impactedService": "Azure CDN",
                    "impactedRegions": [{"impactedRegion": "Global"}],
                },
            ]
        }
    }

    assert event_impacted_regions(event) == ["Global", "eastus"]


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


def test_filter_health_advisory_events_keeps_only_active_warning_or_critical_advisories() -> None:
    events = [
        {"name": "keep-warning", "properties": {"eventType": "HealthAdvisory", "level": "Warning", "status": "Active"}},
        {"name": "keep-critical", "properties": {"eventType": "HealthAdvisory", "level": "Critical", "status": "Active"}},
        {"name": "drop-info", "properties": {"eventType": "HealthAdvisory", "level": "Informational", "status": "Active"}},
        {"name": "drop-resolved", "properties": {"eventType": "HealthAdvisory", "level": "Warning", "status": "Resolved"}},
        {"name": "drop-issue", "properties": {"eventType": "ServiceIssue", "level": "Critical", "status": "Active"}},
    ]

    filtered = filter_health_advisory_events(events)

    assert [event["name"] for event in filtered] == ["keep-warning", "keep-critical"]
