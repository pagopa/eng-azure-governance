"""Subscription scope resolution helpers."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .arm_client import ArmClient
from .resource_graph import query_resource_graph

SUBSCRIPTION_INVENTORY_QUERY = """
resourcecontainers
| where type =~ "microsoft.resources/subscriptions"
| project subscriptionId, subscriptionName=name
""".strip()


def discover_subscriptions_for_management_group(
    client: ArmClient, management_group_id: str
) -> list[str]:
    url = (
        "https://management.azure.com/providers/Microsoft.Management/managementGroups/"
        f"{management_group_id}/descendants?api-version=2023-04-01"
    )
    page = client.list_with_nextlink(url)
    output: list[str] = []
    for item in page.items:
        if (
            str(item.get("type", "")).lower()
            != "microsoft.management/managementgroups/subscriptions"
        ):
            continue
        name = item.get("name") or ""
        if name:
            output.append(str(name))
    return output


def resolve_scope_subscriptions(
    client: ArmClient,
    *,
    explicit_subscriptions: list[str],
    management_groups: list[str],
) -> tuple[list[str], dict[str, list[str]]]:
    merged: set[str] = set(explicit_subscriptions)
    from_management_groups: dict[str, list[str]] = {}

    for mg in management_groups:
        subs = discover_subscriptions_for_management_group(client, mg)
        from_management_groups[mg] = subs
        for sub in subs:
            merged.add(sub)

    return sorted(merged), from_management_groups


def build_subscription_name_map(rows: Iterable[dict[str, Any]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for row in rows:
        subscription_id = str(row.get("subscriptionId", "")).strip()
        subscription_name = str(row.get("subscriptionName", "")).strip()
        key = subscription_id.lower()
        if key and subscription_name and key not in mapping:
            mapping[key] = subscription_name
    return mapping


def collect_subscription_inventory(
    client: ArmClient,
    *,
    subscriptions: list[str],
    management_groups: list[str],
) -> tuple[list[dict[str, Any]], bool, int]:
    return query_resource_graph(
        client,
        query=SUBSCRIPTION_INVENTORY_QUERY,
        subscriptions=subscriptions,
        management_groups=management_groups,
    )
