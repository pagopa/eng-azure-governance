from __future__ import annotations

from src.comitato.comitato_azure_retirements.libs.arm_client import ArmPageResult
from src.comitato.comitato_azure_retirements.libs.subscriptions import (
    build_subscription_name_map,
    discover_subscriptions_for_management_group,
    resolve_scope_subscriptions,
)


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
