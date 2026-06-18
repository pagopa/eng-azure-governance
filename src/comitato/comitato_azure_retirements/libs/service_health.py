"""Service Health collectors."""

from __future__ import annotations

from typing import Any

from .arm_client import ArmClient

RESOURCE_HEALTH_API_VERSION = "2025-05-01"


def collect_events_for_subscriptions(
    client: ArmClient,
    *,
    subscriptions: list[str],
    query_start_time: str,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    rows: list[dict[str, Any]] = []
    page_by_subscription: dict[str, int] = {}

    for subscription in subscriptions:
        url = (
            "https://management.azure.com/subscriptions/"
            f"{subscription}/providers/Microsoft.ResourceHealth/events"
        )
        params = {
            "api-version": RESOURCE_HEALTH_API_VERSION,
            "queryStartTime": query_start_time,
        }
        page = client.list_with_nextlink(url, params=params)
        page_by_subscription[subscription] = page.page_count
        for event in page.items:
            event["_subscriptionId"] = subscription
        rows.extend(page.items)

    return rows, page_by_subscription


def event_impacted_services(event: dict[str, Any]) -> list[dict[str, str]]:
    properties = event.get("properties", {})
    impact = properties.get("impact", {})
    services = impact.get("impactedService", [])

    output: list[dict[str, str]] = []
    if isinstance(services, list):
        for service in services:
            if not isinstance(service, dict):
                continue
            output.append(
                {
                    "name": str(service.get("serviceName") or service.get("name") or ""),
                    "guid": str(service.get("serviceGuid") or service.get("id") or ""),
                }
            )
    if output:
        return output

    single_name = properties.get("service") or properties.get("serviceName") or ""
    if single_name:
        return [{"name": str(single_name), "guid": ""}]
    return [{"name": "", "guid": ""}]


def event_impacted_regions(event: dict[str, Any]) -> list[str]:
    properties = event.get("properties", {})
    impact = properties.get("impact", {})

    regions = impact.get("impactedRegion", [])
    output: list[str] = []
    if isinstance(regions, list):
        for region in regions:
            if isinstance(region, dict):
                candidate = region.get("regionName") or region.get("name") or ""
                if candidate:
                    output.append(str(candidate))
            elif region:
                output.append(str(region))

    if output:
        return output

    fallback = properties.get("region") or properties.get("location") or ""
    if fallback:
        return [str(fallback)]
    return [""]


def build_recommended_actions(event: dict[str, Any]) -> str:
    properties = event.get("properties", {})
    values = properties.get("recommendedActions") or properties.get("recommendedAction") or []
    if isinstance(values, list):
        clean_values = []
        for value in values:
            if isinstance(value, dict):
                text = value.get("actionText") or value.get("description") or value.get("name")
                if text:
                    clean_values.append(str(text))
            elif value:
                clean_values.append(str(value))
        return " | ".join(clean_values)
    if values:
        return str(values)
    return ""
