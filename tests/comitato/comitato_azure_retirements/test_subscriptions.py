from __future__ import annotations

from src.comitato.comitato_azure_retirements.libs.arm_client import ArmPageResult
from src.comitato.comitato_azure_retirements.libs.subscriptions import (
    build_subscription_name_map,
    collect_subscription_inventory,
    discover_subscriptions_for_management_group,
    resolve_scope_subscriptions,
)


class FakeResourceGraphClient:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def post_json(self, url: str, payload: dict[str, object]) -> dict[str, object]:
        assert "Microsoft.ResourceGraph/resources" in url
        assert "resourcecontainers" in str(payload["query"])
        return {"data": self.rows, "resultTruncated": False}


class FakeArmClient:
    def list_with_nextlink(
        self,
        url: str,
        params: dict[str, str] | None = None,
        items_key: str = "value",
    ) -> ArmPageResult:
        return ArmPageResult(
            items=[
                {
                    "type": "microsoft.management/managementgroups/subscriptions",
                    "name": "sub-b",
                },
                {
                    "type": "microsoft.management/managementGroups/subscriptions",
                    "name": "sub-a",
                },
                {"type": "microsoft.management/managementgroups", "name": "mg-child"},
            ],
            page_count=1,
        )


def test_discover_subscriptions_for_management_group_filters_descendants() -> None:
    subscriptions = discover_subscriptions_for_management_group(FakeArmClient(), "mg-1")
    assert subscriptions == ["sub-b", "sub-a"]


def test_resolve_scope_subscriptions_deduplicates_and_sorts() -> None:
    subscriptions, from_management_groups = resolve_scope_subscriptions(
        FakeArmClient(),
        explicit_subscriptions=["sub-c", "sub-a"],
        management_groups=["mg-1"],
    )

    assert subscriptions == ["sub-a", "sub-b", "sub-c"]
    assert from_management_groups == {"mg-1": ["sub-b", "sub-a"]}


def test_build_subscription_name_map_keeps_first_name() -> None:
    mapping = build_subscription_name_map(
        [
            {"subscriptionId": "sub-1", "subscriptionName": "First"},
            {"subscriptionId": "sub-1", "subscriptionName": "Second"},
            {"subscriptionId": "sub-2", "subscriptionName": "Other"},
        ]
    )

    assert mapping == {"sub-1": "First", "sub-2": "Other"}


def test_collect_subscription_inventory_is_independent_from_advisor_rows() -> None:
    client = FakeResourceGraphClient(
        [{"subscriptionId": "SUB-1", "subscriptionName": "Production"}]
    )

    rows, truncated, pages = collect_subscription_inventory(
        client,
        subscriptions=["sub-1"],
        management_groups=[],
    )

    assert rows == [{"subscriptionId": "SUB-1", "subscriptionName": "Production"}]
    assert truncated is False
    assert pages == 1


def test_build_subscription_name_map_matches_ids_case_insensitively() -> None:
    mapping = build_subscription_name_map(
        [{"subscriptionId": "SUB-1", "subscriptionName": "Production"}]
    )
    assert mapping == {"sub-1": "Production"}
