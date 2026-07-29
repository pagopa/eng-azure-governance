"""Correlation of Service Health tracking IDs with Azure-published resources."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any

from .advisor import metadata_field
from .resource_graph import query_resource_graph


@dataclass(frozen=True)
class RetirementMetadata:
    recommendation_type_id: str
    tracking_ids: tuple[str, ...]
    data_source_query: str


@dataclass(frozen=True)
class ResourceEvidence:
    tracking_id: str
    subscription_id: str
    resource_id: str
    resource_group: str
    resource_type: str
    region: str
    source: str
    status: str
    recommendation_type_id: str = ""
    advisor_platform_state: str = ""
    current_query_match: bool = False
    resource_exists: bool = True
    info_json: str = ""


@dataclass(frozen=True)
class ResourceResolutionResult:
    resources_by_event: dict[tuple[str, str], list[ResourceEvidence]]
    status_by_tracking: dict[str, str]
    source_counts_by_tracking: dict[str, dict[str, int]]
    excluded_by_tracking: dict[str, int]


def _tracking_values(source_properties: Any) -> tuple[str, ...]:
    if not isinstance(source_properties, dict):
        return ()
    retirement = source_properties.get("serviceRetirement")
    if not isinstance(retirement, dict):
        return ()
    service_health = retirement.get("serviceHealth")
    if not isinstance(service_health, dict):
        return ()
    values = service_health.get("trackingIds")
    if not isinstance(values, (list, tuple, set)):
        return ()
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        tracking_id = str(value or "").strip()
        key = tracking_id.lower()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(tracking_id)
    return tuple(result)


def _recommendation_type_id(row: dict[str, Any]) -> str:
    value = str(row.get("id") or "").strip()
    if value:
        return value
    source_properties = metadata_field(row, "sourceProperties", {})
    if not isinstance(source_properties, dict):
        return ""
    retirement = source_properties.get("serviceRetirement")
    if not isinstance(retirement, dict):
        return ""
    return str(retirement.get("serviceId") or "").strip()


def index_retirement_metadata(
    metadata_rows: list[dict[str, Any]], tracking_ids: set[str]
) -> dict[str, list[RetirementMetadata]]:
    """Index flattened Advisor metadata by every requested tracking ID."""
    requested = {
        str(value or "").strip().lower()
        for value in tracking_ids
        if str(value or "").strip()
    }
    indexed: dict[str, list[RetirementMetadata]] = {key: [] for key in requested}
    seen: set[tuple[str, str, tuple[str, ...], str]] = set()

    for row in metadata_rows:
        if not isinstance(row, dict):
            continue
        tracking_values = _tracking_values(metadata_field(row, "sourceProperties", {}))
        if not tracking_values:
            continue
        recommendation_type_id = _recommendation_type_id(row)
        if not recommendation_type_id:
            continue
        query_value = metadata_field(row, "recommendationDataSourceQuery", "")
        data_source_query = query_value.strip() if isinstance(query_value, str) else ""
        metadata = RetirementMetadata(
            recommendation_type_id=recommendation_type_id,
            tracking_ids=tracking_values,
            data_source_query=data_source_query,
        )
        for tracking_id in tracking_values:
            key = tracking_id.lower()
            if key not in indexed:
                continue
            identity = (
                key,
                recommendation_type_id.lower(),
                tracking_values,
                data_source_query,
            )
            if identity in seen:
                continue
            seen.add(identity)
            indexed[key].append(metadata)

    return indexed


def impacted_resource_evidence(
    tracking_id: str, subscription_id: str, resource: Any
) -> ResourceEvidence:
    return ResourceEvidence(
        tracking_id=tracking_id,
        subscription_id=subscription_id,
        resource_id=str(resource.resource_id),
        resource_group=str(resource.resource_group),
        resource_type=str(resource.resource_type),
        region=str(resource.region),
        source=str(getattr(resource, "source", "service_health_arg")),
        status=str(getattr(resource, "status", "active")),
        recommendation_type_id=str(getattr(resource, "recommendation_type_id", "")),
        advisor_platform_state=str(getattr(resource, "advisor_platform_state", "")),
        current_query_match=bool(getattr(resource, "current_query_match", False)),
        resource_exists=bool(getattr(resource, "resource_exists", True)),
        info_json=str(getattr(resource, "info_json", "")),
    )


def _evidence_sources(info_json: str, source: str) -> list[str]:
    sources = [source]
    try:
        decoded = json.loads(info_json) if info_json else {}
    except (TypeError, ValueError):
        decoded = {}
    if isinstance(decoded, dict):
        existing = decoded.get("resolution_sources")
        if isinstance(existing, list):
            sources.extend(str(item) for item in existing if str(item))
    return sorted(set(sources))


def _merge_info_json(first: ResourceEvidence, second: ResourceEvidence) -> str:
    sources = _evidence_sources(first.info_json, first.source)
    sources.extend(_evidence_sources(second.info_json, second.source))
    try:
        decoded = json.loads(first.info_json) if first.info_json else {}
    except (TypeError, ValueError):
        decoded = {"source_info": first.info_json} if first.info_json else {}
    if not isinstance(decoded, dict):
        decoded = {"source_info": decoded}
    decoded["resolution_sources"] = sorted(set(sources))
    return json.dumps(
        decoded, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def _evidence_priority(item: ResourceEvidence) -> tuple[int, int]:
    source_priority = {
        "service_health_arg": 0,
        "advisor_metadata_query": 1,
        "advisor_retirement_recommendation": 2,
    }
    return (
        source_priority.get(item.source, 99),
        0 if item.status.lower() == "active" else 1,
    )


def merge_resource_evidence(
    tracking_ids: set[str], *evidence_sets: list[ResourceEvidence]
) -> ResourceResolutionResult:
    requested = {
        str(value or "").strip().lower()
        for value in tracking_ids
        if str(value or "").strip()
    }
    selected: dict[tuple[str, str, str], ResourceEvidence] = {}
    source_counts: dict[str, dict[str, int]] = {key: {} for key in requested}
    excluded: dict[str, int] = {key: 0 for key in requested}

    for evidence_set in evidence_sets:
        for raw_item in evidence_set:
            if not isinstance(raw_item, ResourceEvidence):
                continue
            tracking_key = raw_item.tracking_id.strip().lower()
            if tracking_key not in requested:
                continue
            source_counts[tracking_key][raw_item.source] = (
                source_counts[tracking_key].get(raw_item.source, 0) + 1
            )
            resource_key = raw_item.resource_id.strip().lower()
            if (
                not raw_item.resource_exists
                or not resource_key
                or resource_key == "not_available"
            ):
                excluded[tracking_key] += 1
                continue
            subscription_key = raw_item.subscription_id.strip().lower()
            identity = (tracking_key, subscription_key, resource_key)
            existing = selected.get(identity)
            if existing is None:
                selected[identity] = raw_item
                continue
            preferred = min((existing, raw_item), key=_evidence_priority)
            status = (
                "active"
                if existing.status == "active" or raw_item.status == "active"
                else "resolved"
            )
            selected[identity] = replace(
                preferred,
                status=status,
                current_query_match=existing.current_query_match
                or raw_item.current_query_match,
                recommendation_type_id=(
                    preferred.recommendation_type_id
                    or existing.recommendation_type_id
                    or raw_item.recommendation_type_id
                ),
                advisor_platform_state=(
                    preferred.advisor_platform_state
                    or existing.advisor_platform_state
                    or raw_item.advisor_platform_state
                ),
                info_json=_merge_info_json(existing, raw_item),
            )

    resources_by_event: dict[tuple[str, str], list[ResourceEvidence]] = {}
    for (tracking_key, subscription_key, _), item in selected.items():
        resources_by_event.setdefault((tracking_key, subscription_key), []).append(item)
    for rows in resources_by_event.values():
        rows.sort(key=lambda item: item.resource_id.lower())

    status_by_tracking: dict[str, str] = {}
    for tracking_key in requested:
        rows = [
            item
            for (item_tracking, _), items in resources_by_event.items()
            if item_tracking == tracking_key
            for item in items
        ]
        if any(item.status == "active" for item in rows):
            status_by_tracking[tracking_key] = "active"
        elif rows:
            status_by_tracking[tracking_key] = "resolved"
        elif excluded[tracking_key]:
            status_by_tracking[tracking_key] = "not_published"
        else:
            status_by_tracking[tracking_key] = "unsupported"

    return ResourceResolutionResult(
        resources_by_event=resources_by_event,
        status_by_tracking=status_by_tracking,
        source_counts_by_tracking=source_counts,
        excluded_by_tracking=excluded,
    )


def _event_tracking_id(event: dict[str, Any]) -> str:
    return str(event.get("name") or event.get("id") or "").strip().lower()


def _event_last_update_key(event: dict[str, Any]) -> tuple[int, str]:
    raw = str(event.get("properties", {}).get("lastUpdateTime") or "")
    try:
        value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return (1, value.isoformat())
    except ValueError:
        return (0, "")


def expand_events_for_resource_subscriptions(
    events: list[dict[str, Any]],
    resources_by_event: dict[tuple[str, str], list[ResourceEvidence]],
) -> list[dict[str, Any]]:
    result = [dict(event) for event in events]
    events_by_tracking: dict[str, list[dict[str, Any]]] = {}
    observed: set[tuple[str, str]] = set()
    for event in events:
        tracking_key = _event_tracking_id(event)
        subscription_key = str(event.get("_subscriptionId") or "").strip().lower()
        if not tracking_key:
            continue
        events_by_tracking.setdefault(tracking_key, []).append(event)
        observed.add((tracking_key, subscription_key))

    for (tracking_key, subscription_key), _resources in resources_by_event.items():
        if (tracking_key, subscription_key) in observed:
            continue
        candidates = events_by_tracking.get(tracking_key, [])
        if not candidates:
            continue
        template = max(candidates, key=_event_last_update_key)
        clone = dict(template)
        clone["_subscriptionId"] = subscription_key
        clone["_resource_resolution_subscription_synthesized"] = True
        result.append(clone)
        observed.add((tracking_key, subscription_key))
    return result


def _quote_kql(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def build_advisor_association_query(recommendation_type_ids: set[str]) -> str:
    values = sorted(
        {
            _quote_kql(str(value).strip())
            for value in recommendation_type_ids
            if str(value).strip()
        }
    )
    quoted = ", ".join(f'"{value}"' for value in values) or '"__none__"'
    return f"""
advisorresources
| extend recommendationTypeId=tostring(properties.recommendationTypeId)
| where recommendationTypeId in~ ({quoted})
| extend resourceId=tolower(tostring(properties.resourceMetadata.resourceId))
| extend advisorPlatformState=tostring(properties.platformState)
| project id, subscriptionId, recommendationTypeId, resourceId, advisorPlatformState
| join kind=leftouter (
    resources
    | extend resourceId=tolower(id)
    | project resourceId, currentResourceGroup=resourceGroup,
              currentResourceType=type, currentRegion=location
  ) on resourceId
| extend resourceExists=isnotempty(currentResourceType)
""".strip()


def validate_metadata_data_source_query(query: str) -> str:
    candidate = query.strip()
    if not candidate:
        raise ValueError("metadata data source query is empty")
    if (
        ";" in candidate
        or not re.match(r"^resources\b", candidate, re.IGNORECASE)
        or re.search(
            r"\b(?:union|join|externaldata|invoke|servicehealthresources|"
            r"advisorresources|resourcecontainers)\b",
            candidate,
            re.IGNORECASE,
        )
    ):
        raise ValueError("metadata query must be a read-only Resources inventory query")
    return candidate


def _as_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    if value is None:
        return default
    return bool(value)


def _resource_fields(resource_id: str) -> tuple[str, str, str, bool]:
    cleaned = resource_id.strip()
    segments = [segment for segment in cleaned.split("/") if segment]
    lowered = [segment.lower() for segment in segments]
    try:
        subscription_index = lowered.index("subscriptions")
        group_index = lowered.index("resourcegroups")
        provider_index = lowered.index("providers")
    except ValueError:
        return "not_available", "not_available", "not_available", False
    if (
        subscription_index + 1 >= len(segments)
        or group_index + 1 >= len(segments)
        or provider_index + 2 >= len(segments)
        or not segments[subscription_index + 1]
        or not segments[group_index + 1]
    ):
        return "not_available", "not_available", "not_available", False
    resource_type = f"{segments[provider_index + 1]}/{segments[provider_index + 2]}"
    return (
        segments[group_index + 1],
        resource_type,
        cleaned,
        True,
    )


def _diagnostic_entry() -> dict[str, object]:
    return {
        "status": "unsupported",
        "source_counts": {},
        "excluded_deleted": 0,
        "query_failed": False,
        "truncated": False,
        "advisor_pages": 0,
        "metadata_pages": 0,
        "query_failures": [],
        "malformed_resource_ids": 0,
    }


def _add_source_count(diagnostic: dict[str, object], source: str) -> None:
    counts = diagnostic.setdefault("source_counts", {})
    if isinstance(counts, dict):
        counts[source] = int(counts.get(source, 0)) + 1


def _tracking_for_recommendation(
    metadata_by_tracking: dict[str, list[RetirementMetadata]],
) -> dict[str, list[str]]:
    by_recommendation: dict[str, list[str]] = {}
    for tracking_id, metadata_items in metadata_by_tracking.items():
        for metadata in metadata_items:
            key = metadata.recommendation_type_id.lower()
            if key:
                by_recommendation.setdefault(key, []).append(tracking_id.lower())
    return by_recommendation


def _evidence_from_row(
    row: dict[str, Any],
    *,
    tracking_id: str,
    source: str,
    recommendation_type_id: str = "",
    current_query_match: bool = False,
) -> ResourceEvidence | None:
    raw_resource_id = str(row.get("resourceId") or row.get("id") or "").strip()
    group, resource_type, parsed_id, valid_id = _resource_fields(raw_resource_id)
    resource_exists = _as_bool(row.get("resourceExists"), default=True)
    if not valid_id:
        return ResourceEvidence(
            tracking_id=tracking_id,
            subscription_id=str(row.get("subscriptionId") or "").strip(),
            resource_id="not_available",
            resource_group=str(row.get("currentResourceGroup") or "not_available"),
            resource_type=str(row.get("currentResourceType") or "not_available"),
            region=str(row.get("currentRegion") or "not_available"),
            source=source,
            status="active",
            recommendation_type_id=recommendation_type_id,
            advisor_platform_state=str(row.get("advisorPlatformState") or ""),
            current_query_match=current_query_match,
            resource_exists=False,
        )
    if row.get("currentResourceGroup"):
        group = str(row["currentResourceGroup"])
    if row.get("currentResourceType"):
        resource_type = str(row["currentResourceType"])
    state = str(row.get("advisorPlatformState") or "").strip()
    return ResourceEvidence(
        tracking_id=tracking_id,
        subscription_id=str(row.get("subscriptionId") or "").strip(),
        resource_id=parsed_id,
        resource_group=group,
        resource_type=resource_type,
        region=str(row.get("currentRegion") or row.get("location") or "not_available"),
        source=source,
        status="resolved" if state.lower() == "resolved" else "active",
        recommendation_type_id=recommendation_type_id,
        advisor_platform_state=state,
        current_query_match=current_query_match,
        resource_exists=resource_exists,
    )


def collect_advisor_retirement_evidence(
    client: Any,
    *,
    metadata_by_tracking: dict[str, list[RetirementMetadata]],
    subscriptions: list[str],
    management_groups: list[str],
) -> tuple[list[ResourceEvidence], dict[str, dict[str, object]]]:
    diagnostics = {
        tracking_id.lower(): _diagnostic_entry() for tracking_id in metadata_by_tracking
    }
    evidence: list[ResourceEvidence] = []
    by_recommendation = _tracking_for_recommendation(metadata_by_tracking)
    recommendation_type_ids = set(by_recommendation)

    if recommendation_type_ids:
        try:
            advisor_rows, truncated, pages = query_resource_graph(
                client,
                query=build_advisor_association_query(recommendation_type_ids),
                subscriptions=subscriptions,
                management_groups=management_groups,
            )
        except Exception as exc:
            for diagnostic in diagnostics.values():
                diagnostic["query_failed"] = True
                failures = diagnostic.setdefault("query_failures", [])
                if isinstance(failures, list):
                    failures.append(f"advisor association: {exc}")
            advisor_rows, truncated, pages = [], False, 0
        for tracking_id, diagnostic in diagnostics.items():
            diagnostic["advisor_pages"] = pages
            diagnostic["truncated"] = bool(truncated)
        for row in advisor_rows:
            if not isinstance(row, dict):
                continue
            recommendation_id = (
                str(row.get("recommendationTypeId") or "").strip().lower()
            )
            for tracking_id in by_recommendation.get(recommendation_id, []):
                item = _evidence_from_row(
                    row,
                    tracking_id=tracking_id,
                    source="advisor_retirement_recommendation",
                    recommendation_type_id=str(row.get("recommendationTypeId") or ""),
                )
                if item is None:
                    continue
                evidence.append(item)
                diagnostic = diagnostics[tracking_id]
                _add_source_count(diagnostic, item.source)
                if not item.resource_exists:
                    diagnostic["excluded_deleted"] = (
                        int(diagnostic["excluded_deleted"]) + 1
                    )
                if item.resource_id == "not_available":
                    diagnostic["malformed_resource_ids"] = (
                        int(diagnostic["malformed_resource_ids"]) + 1
                    )

    seen_queries: set[tuple[str, str]] = set()
    for tracking_id, metadata_items in metadata_by_tracking.items():
        diagnostic = diagnostics[tracking_id.lower()]
        for metadata in metadata_items:
            if not metadata.data_source_query:
                continue
            query_key = (
                metadata.recommendation_type_id.lower(),
                metadata.data_source_query,
            )
            if query_key in seen_queries:
                continue
            seen_queries.add(query_key)
            try:
                query = validate_metadata_data_source_query(metadata.data_source_query)
                rows, truncated, pages = query_resource_graph(
                    client,
                    query=query,
                    subscriptions=subscriptions,
                    management_groups=management_groups,
                )
            except Exception as exc:
                for affected_tracking_id in metadata.tracking_ids:
                    affected = diagnostics.get(affected_tracking_id.lower())
                    if affected is None:
                        continue
                    affected["query_failed"] = True
                    failures = affected.setdefault("query_failures", [])
                    if isinstance(failures, list):
                        failures.append(f"metadata query: {exc}")
                continue
            for affected_tracking_id in metadata.tracking_ids:
                affected = diagnostics.get(affected_tracking_id.lower())
                if affected is not None:
                    affected["metadata_pages"] = int(affected["metadata_pages"]) + pages
                    affected["truncated"] = bool(affected["truncated"]) or bool(
                        truncated
                    )
            for row in rows:
                if not isinstance(row, dict):
                    continue
                resource_id = str(row.get("id") or "").strip()
                if not resource_id:
                    continue
                for affected_tracking_id in metadata.tracking_ids:
                    key = affected_tracking_id.lower()
                    if key not in diagnostics:
                        continue
                    item = _evidence_from_row(
                        row,
                        tracking_id=key,
                        source="advisor_metadata_query",
                        recommendation_type_id=metadata.recommendation_type_id,
                        current_query_match=True,
                    )
                    if item is None:
                        continue
                    evidence.append(item)
                    _add_source_count(diagnostics[key], item.source)

    for diagnostic in diagnostics.values():
        if diagnostic["source_counts"]:
            diagnostic["status"] = "active"
        elif diagnostic["query_failed"]:
            diagnostic["status"] = "query_failed"
    return evidence, diagnostics
