from __future__ import annotations

from src.comitato.comitato_azure_retirements.libs.arm_client import ArmPageResult
from src.comitato.comitato_azure_retirements.libs.service_health import (
    build_recommended_actions,
    collect_events_for_subscriptions,
    event_impacted_regions,
    event_impacted_service_regions,
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


def test_collect_events_for_subscriptions_emits_progress_updates() -> None:
    client = FakeArmClient()
    updates: list[tuple[str, int, int, str, str | None]] = []

    collect_events_for_subscriptions(
        client,
        subscriptions=["sub-1", "sub-2"],
        query_start_time="2025-01-01T00:00:00",
        on_subscription_update=lambda subscription, completed, total, status, error: (
            updates.append((subscription, completed, total, status, error))
        ),
    )

    assert len(updates) == 2
    assert {subscription for subscription, *_ in updates} == {"sub-1", "sub-2"}
    assert sorted(
        (completed, total, status, error)
        for _, completed, total, status, error in updates
    ) == [
        (1, 2, "ok", None),
        (2, 2, "ok", None),
    ]


class FailingServiceHealthClient(FakeArmClient):
    def list_with_nextlink(
        self,
        url: str,
        params: dict[str, str] | None = None,
        items_key: str = "value",
    ) -> ArmPageResult:
        del params, items_key
        self.calls.append((url, None))
        if url.endswith(
            "/subscriptions/sub-2/providers/Microsoft.ResourceHealth/events"
        ):
            raise RuntimeError("HTTP 502 for sub-2")
        return ArmPageResult(items=[{"name": "event-a"}], page_count=1)


class QueryStartRetryClient(FakeArmClient):
    def list_with_nextlink(
        self,
        url: str,
        params: dict[str, str] | None = None,
        items_key: str = "value",
    ) -> ArmPageResult:
        del items_key
        self.calls.append((url, params))
        if params and "queryStartTime" in params:
            raise RuntimeError("HTTP 502 for test-sub")
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


def test_collect_events_for_subscriptions_retries_without_query_start_time_on_502() -> None:
    client = QueryStartRetryClient()

    rows, pages, failures = collect_events_for_subscriptions(
        client,
        subscriptions=["sub-1"],
        query_start_time="2025-01-01T00:00:00",
    )

    assert failures == []
    assert pages == {"sub-1": 1}
    assert [row["_subscriptionId"] for row in rows] == ["sub-1"]
    assert len(client.calls) == 2
    assert "queryStartTime" in (client.calls[0][1] or {})
    assert client.calls[1][1] == {"api-version": "2025-05-01"}


class StablePayloadServiceHealthClient(FakeArmClient):
    def __init__(self) -> None:
        super().__init__()
        self.payload = [{"name": "event-a"}]

    def list_with_nextlink(
        self,
        url: str,
        params: dict[str, str] | None = None,
        items_key: str = "value",
    ) -> ArmPageResult:
        del url, params, items_key
        return ArmPageResult(items=self.payload, page_count=1)


def test_collect_events_for_subscriptions_does_not_mutate_payload_items() -> None:
    client = StablePayloadServiceHealthClient()

    rows, _, _ = collect_events_for_subscriptions(
        client,
        subscriptions=["sub-1"],
        query_start_time="2025-01-01T00:00:00",
    )

    assert rows[0]["_subscriptionId"] == "sub-1"
    assert "_subscriptionId" not in client.payload[0]


def test_collect_events_for_subscriptions_marks_degraded_failures_as_warning() -> None:
    client = FailingServiceHealthClient()
    updates: list[tuple[str, int, int, str, str | None]] = []

    collect_events_for_subscriptions(
        client,
        subscriptions=["sub-1", "sub-2"],
        query_start_time="2025-01-01T00:00:00",
        allow_degraded=True,
        on_subscription_update=lambda subscription, completed, total, status, error: (
            updates.append((subscription, completed, total, status, error))
        ),
    )

    assert len(updates) == 2
    status_by_subscription = {
        subscription: (status, error) for subscription, _, _, status, error in updates
    }
    assert status_by_subscription["sub-1"] == ("ok", None)
    assert status_by_subscription["sub-2"] == ("warning", "HTTP 502 for sub-2")
    assert sorted(completed for _, completed, *_ in updates) == [1, 2]


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


def test_event_impacted_service_regions_preserves_live_pairs() -> None:
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

    assert event_impacted_service_regions(event) == [
        {"name": "Azure Front Door", "guid": "", "region": "Global"},
        {"name": "Azure CDN", "guid": "", "region": "eastus"},
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


def test_filter_health_advisory_events_keeps_only_active_warning_or_critical_advisories() -> (
    None
):
    events = [
        {
            "name": "keep-warning",
            "properties": {
                "eventType": "HealthAdvisory",
                "level": "Warning",
                "status": "Active",
            },
        },
        {
            "name": "keep-critical",
            "properties": {
                "eventType": "HealthAdvisory",
                "level": "Critical",
                "status": "Active",
            },
        },
        {
            "name": "drop-info",
            "properties": {
                "eventType": "HealthAdvisory",
                "level": "Informational",
                "status": "Active",
            },
        },
        {
            "name": "drop-resolved",
            "properties": {
                "eventType": "HealthAdvisory",
                "level": "Warning",
                "status": "Resolved",
            },
        },
        {
            "name": "drop-issue",
            "properties": {
                "eventType": "ServiceIssue",
                "level": "Critical",
                "status": "Active",
            },
        },
    ]

    filtered = filter_health_advisory_events(events)

    assert [event["name"] for event in filtered] == ["keep-warning", "keep-critical"]
