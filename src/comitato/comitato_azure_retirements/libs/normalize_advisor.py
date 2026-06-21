"""Advisor normalization for retirements exports."""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from .dates import days_to_retirement, months_to_retirement, normalize_datetime, parse_possible_date
from .tsv import compact_json

RESOURCE_TYPE_LABELS = {
    "microsoft.cache/redis": "Redis Cache Server",
    "microsoft.cdn/profiles": "Front Door Profile",
    "microsoft.compute/disks": "Disk",
    "microsoft.compute/virtualmachines": "Virtual machine",
    "microsoft.containerregistry/registries": "Container registry",
    "microsoft.containerservice/managedclusters": "Kubernetes service",
    "microsoft.documentdb/databaseaccounts": "Cosmos DB account",
    "microsoft.insights/webtests": "Availability test",
    "microsoft.keyvault/vaults": "Key vault",
    "microsoft.network/applicationgateways": "Application gateway",
    "microsoft.network/networkwatchers/flowlogs": "Flow Log",
    "microsoft.network/publicipaddresses": "Public IP address",
    "microsoft.network/virtualnetworkgateways": "Virtual network gateway",
    "microsoft.storage/storageaccounts": "Storage Account",
    "microsoft.synapse/workspaces/bigdatapools": "Apache Spark pool",
    "microsoft.web/sites": "App service",
    "microsoft.apimanagement/service": "API Management",
}


def _extract_resource_name(resource_id: str) -> str:
    if not resource_id:
        return ""
    parts = [part for part in resource_id.split("/") if part]
    return parts[-1] if parts else ""


def _extract_resource_group(resource_id: str) -> str:
    if not resource_id:
        return ""
    parts = [part for part in resource_id.split("/") if part]
    for idx, part in enumerate(parts):
        if part.lower() == "resourcegroups" and idx + 1 < len(parts):
            return parts[idx + 1]
    return ""


def _description_quality(description: str, short_problem: str, feature: str, link: str) -> str:
    if description:
        return "full"
    if short_problem:
        return "short"
    if feature:
        return "feature_only"
    if link:
        return "link_only"
    return "missing"


def _resource_type_from_resource_id(resource_id: str) -> str:
    if not resource_id:
        return ""

    parts = [part for part in resource_id.split("/") if part]
    for idx, part in enumerate(parts):
        if part.lower() != "providers" or idx + 2 >= len(parts):
            continue
        return f"{parts[idx + 1]}/{parts[idx + 2]}".lower()
    return ""


def _humanize_provider_segment(segment: str) -> str:
    if not segment:
        return ""

    normalized = segment.split(".", 1)[-1]
    words = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", normalized).replace("_", " ")
    return words.strip().title()


def _fallback_service_name(*, resource_type: str, impacted_field: str, resource_id: str) -> str:
    normalized_resource_type = resource_type.strip().lower() or _resource_type_from_resource_id(resource_id)
    if normalized_resource_type in RESOURCE_TYPE_LABELS:
        return RESOURCE_TYPE_LABELS[normalized_resource_type]

    normalized_impacted_field = impacted_field.strip().lower()
    if normalized_impacted_field in RESOURCE_TYPE_LABELS:
        return RESOURCE_TYPE_LABELS[normalized_impacted_field]

    if normalized_resource_type:
        return _humanize_provider_segment(normalized_resource_type.split("/", 1)[0])
    if normalized_impacted_field:
        return _humanize_provider_segment(normalized_impacted_field.split("/", 1)[0])
    return ""


def normalize_advisor_rows(
    *,
    run_id: str,
    as_of_date: date,
    scope_mode: str,
    recommendations: list[dict[str, Any]],
    metadata_by_key: dict[str, dict[str, Any]],
    resource_graph_by_key: dict[tuple[str, str], dict[str, Any]],
    subscription_name_map: dict[str, str] | None = None,
    include_raw_json: bool = False,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    used_metadata_keys: set[str] = set()

    for recommendation in recommendations:
        properties = recommendation.get("properties", {})
        recommendation_type_id = str(properties.get("recommendationTypeId") or "")
        resource_id = str(
            properties.get("resourceMetadata", {}).get("resourceId")
            or properties.get("resourceMetadata", {}).get("id")
            or ""
        ).lower()

        metadata = metadata_by_key.get(recommendation_type_id) or metadata_by_key.get(
            recommendation.get("id", "")
        )
        if metadata:
            meta_id = str(metadata.get("id") or "")
            if meta_id:
                used_metadata_keys.add(meta_id)

        resource_graph = resource_graph_by_key.get((recommendation_type_id, resource_id))

        source_properties = (
            metadata.get("properties", {}).get("sourceProperties", {}) if metadata else {}
        )
        service_retirement = (
            source_properties.get("serviceRetirement", {}) if isinstance(source_properties, dict) else {}
        )
        extended_properties = properties.get("extendedProperties", {})
        if not isinstance(extended_properties, dict):
            extended_properties = {}

        retirement_raw = (
            str(service_retirement.get("retirementDate") or "")
            or str(extended_properties.get("retirementDate") or "")
            or str(properties.get("retirementDate") or "")
            or ""
        )
        retirement_date = parse_possible_date(retirement_raw)
        retirement_date_text = retirement_date.isoformat() if retirement_date else ""

        date_quality = "exact"
        if not retirement_raw:
            date_quality = "missing"
        elif retirement_date is None:
            date_quality = "unparseable"
        elif retirement_date < as_of_date:
            date_quality = "past"

        d_days = days_to_retirement(as_of_date, retirement_date)
        d_months = months_to_retirement(as_of_date, retirement_date)

        short_problem = str(properties.get("shortDescription", {}).get("problem") or "")
        short_solution = str(properties.get("shortDescription", {}).get("solution") or "")
        description = str(properties.get("description") or "")
        feature_name = str(
            service_retirement.get("retirementFeatureName")
            or extended_properties.get("retirementFeatureName")
            or ""
        )
        recommendation_link = str(properties.get("learnMoreLink") or "")
        metadata_link = str(metadata.get("properties", {}).get("learnMoreLink") or "") if metadata else ""
        learn_more_link = recommendation_link or metadata_link

        row_flags: list[str] = []
        join_quality = "metadata_and_resource"
        if metadata is None and resource_graph is None:
            join_quality = "recommendation_only"
            row_flags.append("recommendation_without_metadata")
        elif metadata is None:
            join_quality = "arg_only"
            row_flags.append("resource_without_metadata")
        elif resource_graph is None:
            join_quality = "recommendation_only"
            row_flags.append("metadata_without_resource")

        if not description and not short_problem and not feature_name:
            row_flags.append("missing_description")
        if not retirement_date_text:
            row_flags.append("missing_retirement_date")
        if retirement_raw and not retirement_date_text:
            row_flags.append("unparseable_date")

        subscription_id = str(recommendation.get("_subscriptionId") or "")
        tags_json = ""
        resource_type = ""
        location = ""
        subscription_name = ""
        resource_name = _extract_resource_name(resource_id)
        resource_group = _extract_resource_group(resource_id)
        platform_state = ""

        if resource_graph:
            tags_json = compact_json(resource_graph.get("tags", {}))
            resource_type = str(resource_graph.get("type") or "")
            location = str(resource_graph.get("location") or "")
            subscription_name = str(resource_graph.get("subscriptionName") or "")
            resource_name = str(resource_graph.get("name") or resource_name)
            resource_group = str(resource_graph.get("resourceGroup") or resource_group)
            platform_state = str(resource_graph.get("platformState") or "")

        if not subscription_name and subscription_name_map:
            subscription_name = subscription_name_map.get(subscription_id, "")

        actions = properties.get("actions", [])
        action_link = ""
        action_caption = ""
        if isinstance(actions, list) and actions:
            first_action = actions[0]
            if isinstance(first_action, dict):
                action_link = str(first_action.get("link") or first_action.get("url") or "")
                action_caption = str(first_action.get("caption") or first_action.get("name") or "")

        service_name = ""
        if metadata:
            service_name = str(metadata.get("properties", {}).get("resourceMetadata", {}).get("singular") or "")
        if not service_name:
            service_name = str(properties.get("resourceMetadata", {}).get("singular") or "")
        if not service_name:
            service_name = _fallback_service_name(
                resource_type=resource_type,
                impacted_field=str(properties.get("impactedField") or ""),
                resource_id=resource_id,
            )

        row = {
            "run_id": run_id,
            "as_of_date": as_of_date.isoformat(),
            "scope_mode": scope_mode,
            "record_type": "advisor_resource_retirement" if resource_id else "advisor_subscription_retirement",
            "source_system": "advisor_joined",
            "source_id": str(recommendation.get("id") or recommendation.get("name") or ""),
            "recommendation_type_id": recommendation_type_id,
            "advisor_recommendation_id": str(recommendation.get("id") or ""),
            "advisor_metadata_id": str(metadata.get("id") or "") if metadata else "",
            "service_name": service_name,
            "retiring_feature": feature_name,
            "retirement_date": retirement_date_text,
            "days_to_retirement": "" if d_days is None else str(d_days),
            "months_to_retirement": "" if d_months is None else str(d_months),
            "retirement_date_quality": date_quality,
            "subscription_id": subscription_id,
            "subscription_name": subscription_name,
            "resource_id": resource_id,
            "resource_name": resource_name,
            "resource_group": resource_group,
            "resource_type": resource_type.lower(),
            "location": location,
            "tags_json": tags_json,
            "environment_hint": "",
            "platform_hint": "",
            "impact": str(properties.get("impact") or ""),
            "risk": str(properties.get("risk") or ""),
            "category": str(properties.get("category") or ""),
            "sub_category": str(properties.get("subCategory") or ""),
            "platform_state": platform_state,
            "last_updated": normalize_datetime(str(properties.get("lastUpdated") or "")),
            "label": str(properties.get("label") or ""),
            "short_description_problem": short_problem,
            "short_description_solution": short_solution,
            "description": description,
            "potential_benefits": str(properties.get("potentialBenefits") or ""),
            "learn_more_link": learn_more_link,
            "action_link": action_link,
            "action_caption": action_caption,
            "description_quality": _description_quality(description, short_problem, feature_name, learn_more_link),
            "join_quality": join_quality,
            "diagnostic_flags": ",".join(sorted(set(row_flags))),
            "provenance_json": compact_json(
                {
                    "recommendation_source": "advisor_recommendations",
                    "metadata_joined": metadata is not None,
                    "resource_graph_joined": resource_graph is not None,
                    "resource_graph_key": [recommendation_type_id, resource_id],
                }
            ),
            "raw_json": (
                compact_json(
                    {
                        "recommendation": recommendation,
                        "metadata": metadata,
                        "resource_graph": resource_graph,
                    }
                )
                if include_raw_json
                else ""
            ),
        }
        rows.append(row)

    emitted_catalog_metadata_ids: set[str] = set()
    for metadata in metadata_by_key.values():
        meta_id = str(metadata.get("id") or "")
        if not meta_id or meta_id in used_metadata_keys or meta_id in emitted_catalog_metadata_ids:
            continue
        emitted_catalog_metadata_ids.add(meta_id)

        source_properties = metadata.get("properties", {}).get("sourceProperties", {})
        service_retirement = (
            source_properties.get("serviceRetirement", {}) if isinstance(source_properties, dict) else {}
        )
        if not service_retirement:
            continue

        recommendation_type_id = str(service_retirement.get("serviceId") or meta_id)
        retirement_raw = str(service_retirement.get("retirementDate") or "")
        feature_name = str(service_retirement.get("retirementFeatureName") or "")
        learn_more_link = str(metadata.get("properties", {}).get("learnMoreLink") or "")
        if not any([feature_name, retirement_raw, learn_more_link]):
            continue

        retirement_date = parse_possible_date(retirement_raw)

        rows.append(
            {
                "run_id": run_id,
                "as_of_date": as_of_date.isoformat(),
                "scope_mode": scope_mode,
                "record_type": "advisor_catalog_retirement",
                "source_system": "advisor_metadata",
                "source_id": meta_id,
                "recommendation_type_id": recommendation_type_id,
                "advisor_recommendation_id": "",
                "advisor_metadata_id": meta_id,
                "service_name": str(metadata.get("properties", {}).get("resourceMetadata", {}).get("singular") or ""),
                "retiring_feature": feature_name,
                "retirement_date": retirement_date.isoformat() if retirement_date else "",
                "days_to_retirement": "",
                "months_to_retirement": "",
                "retirement_date_quality": "exact" if retirement_date else ("missing" if not retirement_raw else "unparseable"),
                "subscription_id": "",
                "subscription_name": "",
                "resource_id": "",
                "resource_name": "",
                "resource_group": "",
                "resource_type": "",
                "location": "",
                "tags_json": "",
                "environment_hint": "",
                "platform_hint": "",
                "impact": "",
                "risk": "",
                "category": "HighAvailability",
                "sub_category": "ServiceUpgradeAndRetirement",
                "platform_state": "",
                "last_updated": "",
                "label": "",
                "short_description_problem": "",
                "short_description_solution": "",
                "description": "",
                "potential_benefits": "",
                "learn_more_link": learn_more_link,
                "action_link": "",
                "action_caption": "",
                "description_quality": _description_quality("", "", feature_name, learn_more_link),
                "join_quality": "catalog_only",
                "diagnostic_flags": "catalog_only_without_subscription",
                "provenance_json": compact_json({"metadata_source": "advisor_metadata"}),
                "raw_json": compact_json({"metadata": metadata}) if include_raw_json else "",
            }
        )

    return rows
