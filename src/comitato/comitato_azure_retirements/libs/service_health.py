"""Service Health collectors."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .arm_client import ArmClient

RESOURCE_HEALTH_API_VERSION = "2025-05-01"

SubscriptionProgressCallback = Callable[[str, int, int, str, str | None], None]


def _impact_items(event: dict[str, Any]) -> list[dict[str, Any]]:
    properties = event.get("properties", {})
    impact = properties.get("impact", {})

    if isinstance(impact, dict):
        return [impact]
    if isinstance(impact, list):
        return [item for item in impact if isinstance(item, dict)]
    return []


def _append_service(
    output: list[dict[str, str]],
    seen: set[tuple[str, str]],
    *,
    name: str,
    guid: str,
) -> None:
    candidate = (name, guid)
    if candidate in seen:
        return
    seen.add(candidate)
    output.append({"name": name, "guid": guid})


def _append_region(output: list[str], seen: set[str], region: str) -> None:
    if region in seen:
        return
    seen.add(region)
    output.append(region)


def collect_events_for_subscriptions(
    client: ArmClient,
    *,
    subscriptions: list[str],
    query_start_time: str,
    allow_degraded: bool = False,
    on_subscription_update: SubscriptionProgressCallback | None = None,
) -> tuple[list[dict[str, Any]], dict[str, int], list[dict[str, str]]]:
    rows: list[dict[str, Any]] = []
    page_by_subscription: dict[str, int] = {}
    failures: list[dict[str, str]] = []
    total_subscriptions = len(subscriptions)

    for index, subscription in enumerate(subscriptions, start=1):
        url = (
            "https://management.azure.com/subscriptions/"
            f"{subscription}/providers/Microsoft.ResourceHealth/events"
        )
        params = {
            "api-version": RESOURCE_HEALTH_API_VERSION,
            "queryStartTime": query_start_time,
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
        for event in page.items:
            event["_subscriptionId"] = subscription
        rows.extend(page.items)
        if on_subscription_update is not None:
            on_subscription_update(subscription, index, total_subscriptions, "ok", None)

    return rows, page_by_subscription, failures


def filter_health_advisory_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []

    for event in events:
        properties = event.get("properties", {})
        event_type = str(properties.get("eventType") or "").strip().lower()
        if event_type != "healthadvisory":
            continue

        event_level = str(properties.get("level") or "").strip().lower()
        if event_level not in {"warning", "critical"}:
            continue

        status = str(properties.get("status") or "").strip().lower()
        if status == "resolved":
            continue

        filtered.append(event)

    return filtered


def event_impacted_services(event: dict[str, Any]) -> list[dict[str, str]]:
    properties = event.get("properties", {})

    output: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for impact_item in _impact_items(event):
        services = impact_item.get("impactedService", [])
        if isinstance(services, list):
            for service in services:
                if not isinstance(service, dict):
                    continue
                _append_service(
                    output,
                    seen,
                    name=str(service.get("serviceName") or service.get("name") or ""),
                    guid=str(service.get("serviceGuid") or service.get("id") or ""),
                )
            continue

        if isinstance(services, dict):
            _append_service(
                output,
                seen,
                name=str(services.get("serviceName") or services.get("name") or ""),
                guid=str(services.get("serviceGuid") or services.get("id") or ""),
            )
            continue

        service_name = str(services or impact_item.get("serviceName") or impact_item.get("name") or "")
        service_guid = str(impact_item.get("serviceGuid") or impact_item.get("id") or "")
        if service_name:
            _append_service(output, seen, name=service_name, guid=service_guid)

    if output:
        return output

    single_name = properties.get("service") or properties.get("serviceName") or ""
    if single_name:
        return [{"name": str(single_name), "guid": ""}]
    return [{"name": "", "guid": ""}]


def event_impacted_regions(event: dict[str, Any]) -> list[str]:
    properties = event.get("properties", {})
    output: list[str] = []
    seen: set[str] = set()

    for impact_item in _impact_items(event):
        regions = impact_item.get("impactedRegions")
        if regions is None:
            regions = impact_item.get("impactedRegion", [])

        if isinstance(regions, list):
            for region in regions:
                if isinstance(region, dict):
                    candidate = (
                        region.get("impactedRegion")
                        or region.get("regionName")
                        or region.get("name")
                        or region.get("location")
                        or ""
                    )
                    if candidate:
                        _append_region(output, seen, str(candidate))
                elif region:
                    _append_region(output, seen, str(region))
            continue

        if isinstance(regions, dict):
            candidate = (
                regions.get("impactedRegion")
                or regions.get("regionName")
                or regions.get("name")
                or regions.get("location")
                or ""
            )
            if candidate:
                _append_region(output, seen, str(candidate))
            continue

        if regions:
            _append_region(output, seen, str(regions))

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
