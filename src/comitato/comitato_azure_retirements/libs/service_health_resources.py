"""Azure-published impacted resources for Service Health events."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .arm_client import ArmClient
from .resource_graph import query_resource_graph
from .tsv import compact_json


IMPACTED_RESOURCES_QUERY = """
servicehealthresources
| where type =~ "microsoft.resourcehealth/events/impactedresources"
| project id, subscriptionId, properties
""".strip()


@dataclass(frozen=True)
class ImpactedResource:
    resource_id: str
    resource_group: str
    resource_type: str
    region: str
    info_json: str
    source: str = "service_health_arg"
    status: str = "active"
    recommendation_type_id: str = ""
    advisor_platform_state: str = ""
    current_query_match: bool = False
    resource_exists: bool = True


def collect_impacted_resources(
    client: ArmClient,
    *,
    subscriptions: list[str],
    management_groups: list[str],
) -> tuple[list[dict[str, Any]], bool, int]:
    return query_resource_graph(
        client,
        query=IMPACTED_RESOURCES_QUERY,
        subscriptions=subscriptions,
        management_groups=management_groups,
    )


def _event_tracking_id(resource_id: str) -> str:
    segments = [segment for segment in resource_id.split("/") if segment]
    lowered = [segment.lower() for segment in segments]
    try:
        event_index = lowered.index("events")
    except ValueError:
        return ""
    if event_index + 1 >= len(segments):
        return ""
    return segments[event_index + 1]


def _resource_group(resource_id: str) -> str:
    segments = [segment for segment in resource_id.split("/") if segment]
    lowered = [segment.lower() for segment in segments]
    try:
        group_index = lowered.index("resourcegroups")
    except ValueError:
        return "not_available"
    if group_index + 1 >= len(segments):
        return "not_available"
    return segments[group_index + 1] or "not_available"


def index_impacted_resources(
    rows: list[dict[str, Any]], *, tracking_ids: set[str]
) -> dict[tuple[str, str], list[ImpactedResource]]:
    requested_tracking_ids = {value.strip().lower() for value in tracking_ids if value.strip()}
    indexed: dict[tuple[str, str], list[ImpactedResource]] = {}
    seen: set[tuple[str, str, str, str, str, str]] = set()

    for row in rows:
        source_id = str(row.get("id") or "")
        tracking_id = _event_tracking_id(source_id)
        subscription_id = str(row.get("subscriptionId") or "").strip()
        if not tracking_id or tracking_id.lower() not in requested_tracking_ids:
            continue

        properties = row.get("properties")
        if not isinstance(properties, dict):
            properties = {}
        resource_id = str(properties.get("targetResourceId") or "").strip() or "not_available"
        resource_type = str(properties.get("targetResourceType") or "").strip() or "not_available"
        region = str(properties.get("targetRegion") or "").strip() or "not_available"
        info = properties.get("info", [])
        resource = ImpactedResource(
            resource_id=resource_id,
            resource_group=(
                _resource_group(resource_id)
                if resource_id != "not_available"
                else "not_available"
            ),
            resource_type=resource_type,
            region=region,
            info_json=compact_json(info),
            source="service_health_arg",
            status="active",
            resource_exists=True,
        )
        key = (tracking_id.lower(), subscription_id.lower())
        fingerprint = (
            key[0],
            key[1],
            resource.resource_id,
            resource.resource_group,
            resource.resource_type,
            resource.region,
        )
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        indexed.setdefault(key, []).append(resource)

    return indexed
