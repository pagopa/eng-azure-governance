"""Advisor collectors and joins."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .arm_client import ArmClient
from .resource_graph import query_resource_graph

ADVISOR_API_VERSION = "2025-01-01"

SubscriptionProgressCallback = Callable[[str, int, int, str, str | None], None]


def collect_advisor_metadata(client: ArmClient) -> tuple[list[dict[str, Any]], int]:
    url = "https://management.azure.com/providers/Microsoft.Advisor/metadata"
    params = {
        "api-version": ADVISOR_API_VERSION,
        "$filter": "recommendationCategory eq 'HighAvailability' and recommendationSubCategory eq 'ServiceUpgradeAndRetirement'",
        "$expand": "ibiza",
    }
    page = client.list_with_nextlink(url, params=params)
    return page.items, page.page_count


def collect_advisor_recommendations(
    client: ArmClient,
    subscriptions: list[str],
    *,
    allow_degraded: bool = False,
    on_subscription_update: SubscriptionProgressCallback | None = None,
) -> tuple[list[dict[str, Any]], dict[str, int], list[dict[str, str]]]:
    all_rows: list[dict[str, Any]] = []
    page_by_subscription: dict[str, int] = {}
    failures: list[dict[str, str]] = []
    total_subscriptions = len(subscriptions)

    for index, subscription in enumerate(subscriptions, start=1):
        url = (
            "https://management.azure.com/subscriptions/"
            f"{subscription}/providers/Microsoft.Advisor/recommendations"
        )
        params = {
            "api-version": ADVISOR_API_VERSION,
            "$filter": "SubCategory eq 'ServiceUpgradeAndRetirement'",
        }
        try:
            page = client.list_with_nextlink(url, params=params)
        except RuntimeError as exc:
            if on_subscription_update is not None:
                on_subscription_update(
                    subscription,
                    index,
                    total_subscriptions,
                    "warning" if allow_degraded else "error",
                    str(exc),
                )
            if not allow_degraded:
                raise
            failures.append({"subscription_id": subscription, "error": str(exc)})
            continue

        page_by_subscription[subscription] = page.page_count
        for item in page.items:
            item["_subscriptionId"] = subscription
        all_rows.extend(page.items)
        if on_subscription_update is not None:
            on_subscription_update(subscription, index, total_subscriptions, "ok", None)

    return all_rows, page_by_subscription, failures


def collect_advisor_resource_graph(
    client: ArmClient,
    *,
    subscriptions: list[str],
    management_groups: list[str],
) -> tuple[list[dict[str, Any]], bool, int]:
    query = """
advisorresources
| where properties.extendedProperties.recommendationSubCategory == "ServiceUpgradeAndRetirement"
| where tostring(properties.category) has "HighAvailability"
| where isempty(properties.tracked)
| where properties.platformState == "New"
| extend resourceId = tolower(tostring(properties.resourceMetadata.resourceId))
| project id, subscriptionId, resourceGroup, location, resourceId, ServiceID = tostring(properties.recommendationTypeId), platformState=tostring(properties.platformState)
| join kind=leftouter (
    resources
    | project resourceId=tolower(id), rgLocation=location, type, tags, name
  ) on resourceId
| join kind=leftouter (
    resourcecontainers
    | where type =~ "microsoft.resources/subscriptions"
    | extend subscriptionName=name
    | project subscriptionId, subscriptionName
  ) on subscriptionId
| extend location = coalesce(rgLocation, location)
""".strip()
    return query_resource_graph(
        client,
        query=query,
        subscriptions=subscriptions,
        management_groups=management_groups,
    )


def _extract_metadata_id(item: dict[str, Any]) -> str:
    return str(item.get("id") or "")


def _extract_metadata_recommendation_type_id(item: dict[str, Any]) -> str:
    source_properties = item.get("properties", {}).get("sourceProperties", {})
    service_retirement = source_properties.get("serviceRetirement", {})
    candidate = service_retirement.get("serviceId")
    if candidate:
        return str(candidate)

    supported_values = item.get("properties", {}).get("supportedValues", [])
    if isinstance(supported_values, list):
        for supported in supported_values:
            if not isinstance(supported, dict):
                continue
            value_id = supported.get("id")
            if value_id:
                return str(value_id)
    return ""


def index_metadata(metadata_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in metadata_rows:
        keys = {
            _extract_metadata_id(row),
            _extract_metadata_recommendation_type_id(row),
        }
        for key in keys:
            if key:
                indexed[key] = row
    return indexed


def index_resource_graph(resource_rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    for row in resource_rows:
        recommendation_type_id = str(row.get("ServiceID") or "").strip()
        resource_id = str(row.get("resourceId") or "").strip().lower()
        if recommendation_type_id and resource_id:
            indexed[(recommendation_type_id, resource_id)] = row
    return indexed
