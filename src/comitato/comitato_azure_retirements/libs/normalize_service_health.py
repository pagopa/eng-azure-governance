"""Service Health normalization for retirements exports."""

from __future__ import annotations

from collections.abc import Collection
from datetime import date
from typing import Any, Callable

from .dates import normalize_datetime
from .normalize_shared import service_health_deadlines
from .regions import ALLOWED_REGIONS, canonical_allowed_region
from .service_health_resources import ImpactedResource
from .service_health_resource_resolution import ResourceEvidence
from .service_health_text import html_to_ascii_text
from .tsv import compact_json
from .workflow_exports_utils import priority_label


def _service_description_quality(
    description: str, summary: str, sensitive: bool
) -> str:
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
    event_impacted_service_regions: Callable[[dict[str, Any]], list[dict[str, str]]],
    build_recommended_actions: Callable[[dict[str, Any]], str],
    impacted_resources_by_event: dict[
        tuple[str, str], list[ImpactedResource | ResourceEvidence]
    ]
    | None = None,
    allowed_regions: Collection[str] = ALLOWED_REGIONS,
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
        tracking_id = event_id

        title = str(properties.get("title") or properties.get("header") or "")
        summary = str(properties.get("summary") or "")
        article = properties.get("article", {})
        article_content = (
            article.get("articleContent") if isinstance(article, dict) else ""
        )
        description = str(article_content or properties.get("description") or "")
        description_problem = html_to_ascii_text(description)
        actions_text = build_recommended_actions(event)

        impact_start = normalize_datetime(str(properties.get("impactStartTime") or ""))
        impact_mitigation = normalize_datetime(
            str(properties.get("impactMitigationTime") or "")
        )
        last_update = normalize_datetime(str(properties.get("lastUpdateTime") or ""))

        is_sensitive = bool(properties.get("isSensitive") or False)
        details_fetch_status = "not_needed"
        if is_sensitive:
            details_fetch_status = "not_supported"

        qualified_deadline, resolved_date_for_window, derived_from_text = service_health_deadlines(
            title=title,
            summary=summary,
            description=description_problem,
            recommended_actions=actions_text,
            impact_mitigation=impact_mitigation,
            impact_start=impact_start,
            last_update=last_update,
        )

        service_regions = event_impacted_service_regions(event)

        if not service_regions:
            service_regions = [{"name": "", "guid": "", "region": ""}]

        subscription_key = subscription_id.strip().lower()
        subscription_name = subscription_name_map.get(subscription_key, "")
        subscription_fallback = not subscription_name
        subscription_name = subscription_name or subscription_id or "not_available"
        resource_key = (tracking_id.strip().lower(), subscription_key)
        indexed_resources = (impacted_resources_by_event or {}).get(resource_key, [])
        resource_rows: list[tuple[dict[str, str], ImpactedResource | None]] = []
        if indexed_resources:
            service_names = sorted(
                {
                    str(item.get("name") or "").strip()
                    for item in service_regions
                    if str(item.get("name") or "").strip()
                }
            )
            service_region = {
                "name": ", ".join(service_names) or "not_available",
                "guid": "",
                "region": "",
            }
            resource_rows = [(service_region, resource) for resource in indexed_resources]
        else:
            resource_rows = [(service_region, None) for service_region in service_regions]

        for service_region, resource in resource_rows:
            region = str(service_region.get("region") or "")
            if region and resource is None:
                region = canonical_allowed_region(region, allowed_regions)
                if not region:
                    continue
            if resource is not None:
                region = (
                    canonical_allowed_region(resource.region, allowed_regions)
                    if resource.region != "not_available"
                    else "not_available"
                ) or "not_available"

            flags: list[str] = []
            if not region:
                flags.append("service_health_no_region")
            if is_sensitive:
                flags.append("service_health_sensitive")
            if not description_problem and not summary:
                flags.append("missing_description")
            if derived_from_text:
                flags.append("retirement_date_derived_from_text")
            if subscription_fallback:
                flags.append("subscription_name_fallback_to_id")
            if resource is None:
                flags.append("service_health_impacted_resources_not_published")
            if event.get("_resource_resolution_subscription_synthesized") is True:
                flags.append("service_health_subscription_recovered_from_advisor")

            resource_id = resource.resource_id if resource is not None else "not_available"
            resource_group = resource.resource_group if resource is not None else "not_available"
            resource_type = resource.resource_type if resource is not None else "not_available"
            resolution_source = (
                str(getattr(resource, "source", "service_health_arg"))
                if resource is not None
                else "not_available"
            )
            resolution_status = (
                str(getattr(resource, "status", "active"))
                if resource is not None
                else "not_published"
            )
            recommendation_type_id = (
                str(getattr(resource, "recommendation_type_id", ""))
                if resource is not None
                else ""
            ) or "not_available"
            advisor_platform_state = (
                str(getattr(resource, "advisor_platform_state", ""))
                if resource is not None
                else ""
            ) or "not_available"
            current_query_match = (
                "true"
                if resource is not None
                and bool(getattr(resource, "current_query_match", False))
                else "false"
            )
            resource_granularity = (
                "resource"
                if resource is not None and resource.resource_id != "not_available"
                else "resource_metadata_only"
                if resource is not None
                else "not_available"
            )
            provenance = {
                "event_source": "resource_health_events",
                "resource_lookup_status": "found" if resource is not None else "unavailable",
            }
            if resource is not None:
                provenance["resource_source"] = resolution_source
                provenance["resource_info_json"] = resource.info_json

            row = {
                "run_id": run_id,
                "as_of_date": as_of_date.isoformat(),
                "scope_mode": scope_mode,
                "record_type": (
                    "service_health_event_resource"
                    if resource is not None
                    else "service_health_event_region"
                    if region
                    else "service_health_event_subscription"
                ),
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
                "priority": priority_label(
                    retirement_date=qualified_deadline,
                    as_of_date=as_of_date,
                ),
                "title": title,
                "short_description_solution": title,
                "summary": summary,
                "description_problem": description_problem,
                "recommended_actions": actions_text,
                "impact_start_time": impact_start,
                "impact_mitigation_time": impact_mitigation,
                "last_update_time": last_update,
                "date_for_window": resolved_date_for_window,
                "impacted_service": str(service_region.get("name") or ""),
                "impacted_service_guid": str(service_region.get("guid") or ""),
                "impacted_region": region,
                "subscription_id": subscription_id,
                "subscription_name": subscription_name,
                "resource_granularity": resource_granularity,
                "resource_id": resource_id,
                "resource_group": resource_group,
                "resource_type": resource_type,
                "resource_resolution_source": resolution_source,
                "resource_resolution_status": resolution_status,
                "recommendation_type_id": recommendation_type_id,
                "advisor_platform_state": advisor_platform_state,
                "current_query_match": current_query_match,
                "is_sensitive": "true" if is_sensitive else "false",
                "details_fetch_status": details_fetch_status,
                "description_quality": _service_description_quality(
                    description_problem, summary, is_sensitive
                ),
                "diagnostic_flags": ",".join(sorted(set(flags))),
                "provenance_json": compact_json(provenance),
            }
            rows.append(row)

    return rows
