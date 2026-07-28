from __future__ import annotations

from typing import Any, cast

from src.comitato.comitato_azure_retirements.libs.advisor import (
    collect_advisor_recommendations,
    index_metadata,
    index_resource_graph,
)
from src.comitato.comitato_azure_retirements.libs.arm_client import ArmPageResult


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
        subscription = url.split("/subscriptions/")[1].split("/")[0]
        return ArmPageResult(items=[{"id": f"rec-{subscription}"}], page_count=2)


def test_collect_advisor_recommendations_tags_subscription_id() -> None:
    client = FakeArmClient()

    rows, pages, failures = collect_advisor_recommendations(
        cast(Any, client), ["sub-1", "sub-2"]
    )

    assert pages == {"sub-1": 2, "sub-2": 2}
    assert [row["_subscriptionId"] for row in rows] == ["sub-1", "sub-2"]
    assert failures == []


def test_collect_advisor_recommendations_emits_progress_updates() -> None:
    client = FakeArmClient()
    updates: list[tuple[str, int, int, str, str | None]] = []

    collect_advisor_recommendations(
        cast(Any, client),
        ["sub-1", "sub-2"],
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


class FailingAdvisorArmClient(FakeArmClient):
    def list_with_nextlink(
        self,
        url: str,
        params: dict[str, str] | None = None,
        items_key: str = "value",
    ) -> ArmPageResult:
        del params, items_key
        self.calls.append((url, None))
        if url.endswith(
            "/subscriptions/sub-2/providers/Microsoft.Advisor/recommendations"
        ):
            raise RuntimeError("HTTP 502 for sub-2")
        return ArmPageResult(items=[{"id": "rec-sub-1"}], page_count=1)


def test_collect_advisor_recommendations_records_failures_in_degraded_mode() -> None:
    client = FailingAdvisorArmClient()

    rows, pages, failures = collect_advisor_recommendations(
        cast(Any, client),
        ["sub-1", "sub-2"],
        allow_degraded=True,
    )

    assert [row["_subscriptionId"] for row in rows] == ["sub-1"]
    assert pages == {"sub-1": 1}
    assert failures == [{"subscription_id": "sub-2", "error": "HTTP 502 for sub-2"}]


def test_collect_advisor_recommendations_marks_degraded_failures_as_warning() -> None:
    client = FailingAdvisorArmClient()
    updates: list[tuple[str, int, int, str, str | None]] = []

    collect_advisor_recommendations(
        cast(Any, client),
        ["sub-1", "sub-2"],
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


def test_index_metadata_maps_id_and_service_id_keys() -> None:
    metadata = {
        "id": "meta-1",
        "properties": {
            "sourceProperties": {
                "serviceRetirement": {
                    "serviceId": "service-1",
                }
            }
        },
    }

    indexed = index_metadata([metadata])

    assert indexed["meta-1"] is metadata
    assert indexed["service-1"] is metadata


def test_index_resource_graph_uses_lowercase_resource_id_key() -> None:
    rows = [
        {
            "ServiceID": "service-1",
            "resourceId": "/subscriptions/SUB-1/resourceGroups/RG/providers/Microsoft.Compute/virtualMachines/vm1",
            "name": "vm1",
        }
    ]

    indexed = index_resource_graph(rows)

    key = (
        "service-1",
        "/subscriptions/sub-1/resourcegroups/rg/providers/microsoft.compute/virtualmachines/vm1",
    )
    assert indexed[key]["name"] == "vm1"
