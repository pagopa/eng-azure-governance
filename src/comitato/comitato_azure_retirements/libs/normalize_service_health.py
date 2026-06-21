"""Service Health normalization for retirements exports."""

from __future__ import annotations

from datetime import date
from typing import Any, Callable

from .dates import normalize_datetime
from .normalize_shared import service_health_date_for_window
from .tsv import compact_json


def _service_description_quality(description: str, summary: str, sensitive: bool) -> str:
    if sensitive and not description:
        return "sensitive_blocked"
    if description:
        return "full"
    if summary:
        return "short"
    return "missing"


def normalize_service_health_rows(
    *,
    run_id: str,
    as_of_date: date,
    scope_mode: str,
    events: list[dict[str, Any]],
    subscription_name_map: dict[str, str],
    event_impacted_services: Callable[[dict[str, Any]], list[dict[str, str]]],
    event_impacted_regions: Callable[[dict[str, Any]], list[str]],
    event_impacted_service_regions: Callable[[dict[str, Any]], list[dict[str, str]]] | None = None,
    build_recommended_actions: Callable[[dict[str, Any]], str],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for event in events:
        properties = event.get("properties", {})
        subscription_id = str(event.get("_subscriptionId") or "")
        event_id = str(event.get("name") or event.get("id") or "")
        source_id = str(event.get("id") or event_id)

        event_level = str(properties.get("level") or "")
        status = str(properties.get("status") or "")
        event_type = str(properties.get("eventType") or "")
        event_sub_type = str(properties.get("eventSubType") or "")
        event_source = str(properties.get("eventSource") or "")
        tracking_id = str(properties.get("trackingId") or "")

        title = str(properties.get("title") or properties.get("header") or "")
        summary = str(properties.get("summary") or "")
        article = properties.get("article", {})
        description = str(article.get("articleContent") or properties.get("description") or "")
        actions_text = build_recommended_actions(event)

        impact_start = normalize_datetime(str(properties.get("impactStartTime") or ""))
        impact_mitigation = normalize_datetime(str(properties.get("impactMitigationTime") or ""))
        last_update = normalize_datetime(str(properties.get("lastUpdateTime") or ""))

        is_sensitive = bool(properties.get("isSensitive") or False)
        details_fetch_status = "not_needed"
        if is_sensitive:
            details_fetch_status = "not_supported"

        date_for_window = service_health_date_for_window(
            title=title,
            summary=summary,
            description=description,
            recommended_actions=actions_text,
            impact_mitigation=impact_mitigation,
            impact_start=impact_start,
            last_update=last_update,
        )
        resolved_date_for_window, derived_from_text = date_for_window

        service_regions: list[dict[str, str]] = []
        if event_impacted_service_regions is not None:
            service_regions = event_impacted_service_regions(event)

        if not service_regions:
            services = event_impacted_services(event)
            regions = event_impacted_regions(event)
            for service in services:
                for region in regions:
                    service_regions.append(
                        {
                            "name": str(service.get("name") or ""),
                            "guid": str(service.get("guid") or ""),
                            "region": str(region or ""),
                        }
                    )

        for service_region in service_regions:
            region = str(service_region.get("region") or "")

            flags: list[str] = []
            if not region:
                flags.append("service_health_no_region")
            if is_sensitive:
                flags.append("service_health_sensitive")
            if not description and not summary:
                flags.append("missing_description")
            if derived_from_text:
                flags.append("retirement_date_derived_from_text")

            row = {
                "run_id": run_id,
                "as_of_date": as_of_date.isoformat(),
                "scope_mode": scope_mode,
                "record_type": "service_health_event_region" if region else "service_health_event_subscription",
                "source_system": "resource_health_events",
                "source_id": source_id,
                "event_id": event_id,
                "tracking_id": tracking_id,
                "event_type": event_type,
                "event_sub_type": event_sub_type,
                "event_source": event_source,
                "event_level": event_level,
                "level": event_level,
                "status": status,
                "priority": "",
                "title": title,
                "summary": summary,
                "description": description,
                "recommended_actions": actions_text,
                "impact_start_time": impact_start,
                "impact_mitigation_time": impact_mitigation,
                "last_update_time": last_update,
                "date_for_window": resolved_date_for_window,
                "impacted_service": str(service_region.get("name") or ""),
                "impacted_service_guid": str(service_region.get("guid") or ""),
                "impacted_region": region,
                "subscription_id": subscription_id,
                "subscription_name": subscription_name_map.get(subscription_id, ""),
                "resource_granularity": "not_available",
                "resource_id": "",
                "resource_group": "",
                "resource_type": "",
                "is_sensitive": "true" if is_sensitive else "false",
                "details_fetch_status": details_fetch_status,
                "description_quality": _service_description_quality(description, summary, is_sensitive),
                "diagnostic_flags": ",".join(sorted(set(flags))),
                "provenance_json": compact_json({"event_source": "resource_health_events"}),
            }
            rows.append(row)

    return rows
