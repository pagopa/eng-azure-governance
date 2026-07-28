"""Advisor collectors and joins."""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import perf_counter
from typing import Any

from .arm_client import ArmClient
from .concurrency import effective_worker_count
from .debug_log import DebugRunLogger
from .resource_graph import query_resource_graph

ADVISOR_API_VERSION = "2025-01-01"

SubscriptionProgressCallback = Callable[[str, int, int, str, str | None], None]


def _with_subscription_id(item: dict[str, Any], subscription: str) -> dict[str, Any]:
    # Avoid mutating API payloads in-place; downstream still receives subscription context.
    with_subscription = dict(item)
    with_subscription["_subscriptionId"] = subscription
    return with_subscription


def _collect_subscription_recommendations(
    client: ArmClient,
    subscription: str,
) -> tuple[list[dict[str, Any]], int, int]:
    started_at = perf_counter()
    url = (
        "https://management.azure.com/subscriptions/"
        f"{subscription}/providers/Microsoft.Advisor/recommendations"
    )
    params = {
        "api-version": ADVISOR_API_VERSION,
        "$filter": "SubCategory eq 'ServiceUpgradeAndRetirement'",
    }
    page = client.list_with_nextlink(url, params=params)

    elapsed_ms = int((perf_counter() - started_at) * 1000)
    return page.items, page.page_count, elapsed_ms


def collect_advisor_metadata(client: ArmClient) -> tuple[list[dict[str, Any]], int]:
    url = "https://management.azure.com/providers/Microsoft.Advisor/metadata"
    params = {
        "api-version": ADVISOR_API_VERSION,
        "$filter": "recommendationCategory eq 'HighAvailability' and recommendationSubCategory eq 'ServiceUpgradeAndRetirement'",
        "$expand": "ibiza",
    }
    page = client.list_with_nextlink(url, params=params)
    return flatten_advisor_metadata_items(page.items), page.page_count


def flatten_advisor_metadata_items(
    items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    for item in items:
        supported = metadata_field(item, "supportedValues")
        if isinstance(supported, list):
            flattened.extend(row for row in supported if isinstance(row, dict))
        else:
            flattened.append(item)
    return flattened


def collect_advisor_recommendations(
    client: ArmClient,
    subscriptions: list[str],
    *,
    allow_degraded: bool = False,
    on_subscription_update: SubscriptionProgressCallback | None = None,
    max_workers: int | None = None,
    resolved_worker_count: int | None = None,
    debug_logger: DebugRunLogger | None = None,
) -> tuple[list[dict[str, Any]], dict[str, int], list[dict[str, str]]]:
    all_rows: list[dict[str, Any]] = []
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
            "advisor_parallel_collection_started",
            "Advisor recommendation collection started",
            subscriptions_count=total_subscriptions,
            max_workers=worker_count,
            allow_degraded=allow_degraded,
        )

    completed = 0
    with ThreadPoolExecutor(
        max_workers=worker_count, thread_name_prefix="advisor-sub"
    ) as executor:
        future_to_subscription = {
            executor.submit(
                _collect_subscription_recommendations, client, subscription
            ): subscription
            for subscription in subscriptions
        }

        for future in as_completed(future_to_subscription):
            subscription = future_to_subscription[future]
            completed += 1
            try:
                rows, page_count, elapsed_ms = future.result()
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
                        "advisor_subscription_failed",
                        "Advisor recommendation collection failed for subscription",
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
                _with_subscription_id(item, subscription) for item in rows
            ]
            if on_subscription_update is not None:
                on_subscription_update(
                    subscription, completed, total_subscriptions, "ok", None
                )
            if debug_logger is not None:
                debug_logger.info(
                    "advisor_subscription_completed",
                    "Advisor recommendation collection completed for subscription",
                    subscription_id=subscription,
                    page_count=page_count,
                    rows_count=len(rows),
                    elapsed_ms=elapsed_ms,
                    completed=completed,
                    total=total_subscriptions,
                )

    for subscription in subscriptions:
        all_rows.extend(rows_by_subscription.get(subscription, []))

    if debug_logger is not None:
        debug_logger.info(
            "advisor_parallel_collection_finished",
            "Advisor recommendation collection finished",
            success_subscriptions=len(page_by_subscription),
            failures=len(failures),
            total_rows=len(all_rows),
        )

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


def metadata_field(item: dict[str, Any], field_name: str, default: Any = None) -> Any:
    """Read a metadata field from expanded live rows or legacy nested rows."""
    if field_name in item:
        return item[field_name]

    properties = item.get("properties")
    if isinstance(properties, dict):
        return properties.get(field_name, default)
    return default


def metadata_shape_issues(
    metadata_rows: list[dict[str, Any]],
) -> list[dict[str, str]]:
    """Return structural metadata issues without copying source payload values."""
    issues: list[dict[str, str]] = []
    expected_types: tuple[tuple[str, tuple[type[Any], ...]], ...] = (
        ("properties", (dict, list, type(None))),
        ("sourceProperties", (dict, type(None))),
        ("resourceMetadata", (dict, type(None))),
    )
    for item in metadata_rows:
        metadata_id = str(item.get("id") or "")
        for field_name, allowed_types in expected_types:
            if field_name not in item:
                continue
            value = item[field_name]
            if isinstance(value, allowed_types):
                continue
            issues.append(
                {
                    "metadata_id": metadata_id,
                    "field": field_name,
                    "actual_type": type(value).__name__,
                }
            )
    return issues


def _extract_metadata_recommendation_type_id(item: dict[str, Any]) -> str:
    source_properties = metadata_field(item, "sourceProperties", {})
    if not isinstance(source_properties, dict):
        source_properties = {}
    service_retirement = source_properties.get("serviceRetirement", {})
    if not isinstance(service_retirement, dict):
        service_retirement = {}
    candidate = service_retirement.get("serviceId")
    if candidate:
        return str(candidate)

    supported_values = metadata_field(item, "supportedValues", [])
    if isinstance(supported_values, list):
        for supported in supported_values:
            if not isinstance(supported, dict):
                continue
            value_id = supported.get("id")
            if value_id:
                return str(value_id)
    return ""


def index_metadata_with_collisions(
    metadata_rows: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    indexed: dict[str, dict[str, Any]] = {}
    collisions: dict[str, int] = {}
    for row in metadata_rows:
        keys = {
            _extract_metadata_id(row),
            _extract_metadata_recommendation_type_id(row),
        }
        for key in keys:
            if not key:
                continue
            if key in indexed and indexed[key] is not row:
                collisions[key] = collisions.get(key, 0) + 1
            indexed[key] = row
    return indexed, collisions


def index_metadata(metadata_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed, _ = index_metadata_with_collisions(metadata_rows)
    return indexed


def index_resource_graph(
    resource_rows: list[dict[str, Any]],
) -> dict[tuple[str, str], dict[str, Any]]:
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    for row in resource_rows:
        recommendation_type_id = str(row.get("ServiceID") or "").strip()
        resource_id = str(row.get("resourceId") or "").strip().lower()
        if recommendation_type_id and resource_id:
            indexed[(recommendation_type_id, resource_id)] = row
    return indexed
