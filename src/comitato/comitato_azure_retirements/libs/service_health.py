"""Service Health collectors."""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date
from time import perf_counter
from typing import Any

from .arm_client import ArmClient
from .concurrency import effective_worker_count
from .dates import parse_possible_date
from .debug_log import DebugRunLogger

RESOURCE_HEALTH_API_VERSION = "2025-05-01"

SubscriptionProgressCallback = Callable[[str, int, int, str, str | None], None]


@dataclass(frozen=True)
class HealthAdvisoryFilterResult:
    events: list[dict[str, Any]]
    expired_event_ids: list[str]


def _with_subscription_id(event: dict[str, Any], subscription: str) -> dict[str, Any]:
    # Keep source payload immutable while preserving subscription context for normalization.
    with_subscription = dict(event)
    with_subscription["_subscriptionId"] = subscription
    return with_subscription


def _collect_subscription_events(
    client: ArmClient,
    *,
    subscription: str,
    query_start_time: str,
) -> tuple[list[dict[str, Any]], int, int]:
    started_at = perf_counter()
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
        # Some subscriptions intermittently fail with 502 only when queryStartTime is present.
        # Retrying once without that filter usually restores collection without masking other errors.
        if not query_start_time or "http 502" not in str(exc).lower():
            raise
        page = client.list_with_nextlink(
            url,
            params={"api-version": RESOURCE_HEALTH_API_VERSION},
        )

    elapsed_ms = int((perf_counter() - started_at) * 1000)
    return page.items, page.page_count, elapsed_ms


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


def _impact_item_services(impact_item: dict[str, Any]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

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
        return output

    if isinstance(services, dict):
        _append_service(
            output,
            seen,
            name=str(services.get("serviceName") or services.get("name") or ""),
            guid=str(services.get("serviceGuid") or services.get("id") or ""),
        )
        return output

    service_name = str(
        services or impact_item.get("serviceName") or impact_item.get("name") or ""
    )
    service_guid = str(impact_item.get("serviceGuid") or impact_item.get("id") or "")
    if service_name:
        _append_service(output, seen, name=service_name, guid=service_guid)
    return output


def _impact_item_regions(impact_item: dict[str, Any]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()

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
        return output

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
        return output

    if regions:
        _append_region(output, seen, str(regions))
    return output


def collect_events_for_subscriptions(
    client: ArmClient,
    *,
    subscriptions: list[str],
    query_start_time: str,
    allow_degraded: bool = False,
    on_subscription_update: SubscriptionProgressCallback | None = None,
    max_workers: int | None = None,
    resolved_worker_count: int | None = None,
    debug_logger: DebugRunLogger | None = None,
) -> tuple[list[dict[str, Any]], dict[str, int], list[dict[str, str]]]:
    rows: list[dict[str, Any]] = []
    rows_by_subscription: dict[str, list[dict[str, Any]]] = {}
    page_by_subscription: dict[str, int] = {}
    failures: list[dict[str, str]] = []
    total_subscriptions = len(subscriptions)

    worker_count = effective_worker_count(
        total_subscriptions,
        resolved_worker_count if resolved_worker_count is not None else max_workers,
    )
    if debug_logger is not None:
        debug_logger.info(
            "service_health_parallel_collection_started",
            "Service Health collection started",
            subscriptions_count=total_subscriptions,
            max_workers=worker_count,
            allow_degraded=allow_degraded,
        )

    completed = 0
    with ThreadPoolExecutor(
        max_workers=worker_count, thread_name_prefix="health-sub"
    ) as executor:
        future_to_subscription = {
            executor.submit(
                _collect_subscription_events,
                client,
                subscription=subscription,
                query_start_time=query_start_time,
            ): subscription
            for subscription in subscriptions
        }

        for future in as_completed(future_to_subscription):
            subscription = future_to_subscription[future]
            completed += 1
            try:
                subscription_rows, page_count, elapsed_ms = future.result()
            except RuntimeError as exc:
                status = "warning" if allow_degraded else "error"
                error_text = str(exc)
                if on_subscription_update is not None:
                    on_subscription_update(
                        subscription,
                        completed,
                        total_subscriptions,
                        status,
                        error_text,
                    )
                if debug_logger is not None:
                    debug_logger.warning(
                        "service_health_subscription_failed",
                        "Service Health collection failed for subscription",
                        subscription_id=subscription,
                        status=status,
                        error=error_text,
                        completed=completed,
                        total=total_subscriptions,
                    )
                if not allow_degraded:
                    # ThreadPoolExecutor cannot reliably stop already-running tasks.
                    # Re-raising preserves strict behavior while the executor drains.
                    raise
                failures.append({"subscription_id": subscription, "error": error_text})
                continue

            page_by_subscription[subscription] = page_count
            rows_by_subscription[subscription] = [
                _with_subscription_id(event, subscription)
                for event in subscription_rows
            ]
            if on_subscription_update is not None:
                on_subscription_update(
                    subscription, completed, total_subscriptions, "ok", None
                )
            if debug_logger is not None:
                debug_logger.info(
                    "service_health_subscription_completed",
                    "Service Health collection completed for subscription",
                    subscription_id=subscription,
                    page_count=page_count,
                    rows_count=len(subscription_rows),
                    elapsed_ms=elapsed_ms,
                    completed=completed,
                    total=total_subscriptions,
                )

    for subscription in subscriptions:
        rows.extend(rows_by_subscription.get(subscription, []))

    if debug_logger is not None:
        debug_logger.info(
            "service_health_parallel_collection_finished",
            "Service Health collection finished",
            success_subscriptions=len(page_by_subscription),
            failures=len(failures),
            total_rows=len(rows),
        )

    return rows, page_by_subscription, failures


def filter_health_advisory_events(
    events: list[dict[str, Any]], *, as_of_date: date
) -> HealthAdvisoryFilterResult:
    filtered: list[dict[str, Any]] = []
    expired_event_ids: list[str] = []

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

        mitigation_date = parse_possible_date(
            str(properties.get("impactMitigationTime") or "")
        )
        if mitigation_date is not None and mitigation_date < as_of_date:
            event_id = str(event.get("name") or event.get("id") or "")
            if event_id:
                expired_event_ids.append(event_id)
            continue

        filtered.append(event)

    return HealthAdvisoryFilterResult(filtered, expired_event_ids)


def event_impacted_services(event: dict[str, Any]) -> list[dict[str, str]]:
    properties = event.get("properties", {})

    output: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for impact_item in _impact_items(event):
        for service in _impact_item_services(impact_item):
            _append_service(
                output,
                seen,
                name=service.get("name", ""),
                guid=service.get("guid", ""),
            )

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
        for region in _impact_item_regions(impact_item):
            _append_region(output, seen, region)

    if output:
        return output

    fallback = properties.get("region") or properties.get("location") or ""
    if fallback:
        return [str(fallback)]
    return [""]


def event_impacted_service_regions(event: dict[str, Any]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    for impact_item in _impact_items(event):
        services = _impact_item_services(impact_item)
        regions = _impact_item_regions(impact_item)

        if not services:
            services = [{"name": "", "guid": ""}]
        if not regions:
            regions = [""]

        for service in services:
            for region in regions:
                pair = (service.get("name", ""), service.get("guid", ""), region)
                if pair in seen:
                    continue
                seen.add(pair)
                output.append({"name": pair[0], "guid": pair[1], "region": pair[2]})

    if output:
        return output

    for service in event_impacted_services(event):
        for region in event_impacted_regions(event):
            pair = (service.get("name", ""), service.get("guid", ""), region)
            if pair in seen:
                continue
            seen.add(pair)
            output.append({"name": pair[0], "guid": pair[1], "region": pair[2]})

    return output


def build_recommended_actions(event: dict[str, Any]) -> str:
    properties = event.get("properties", {})
    values = (
        properties.get("recommendedActions")
        or properties.get("recommendedAction")
        or []
    )
    if isinstance(values, list):
        clean_values = []
        for value in values:
            if isinstance(value, dict):
                text = (
                    value.get("actionText")
                    or value.get("description")
                    or value.get("name")
                )
                if text:
                    clean_values.append(str(text))
            elif value:
                clean_values.append(str(value))
        return " | ".join(clean_values)
    if values:
        return str(values)
    return ""
