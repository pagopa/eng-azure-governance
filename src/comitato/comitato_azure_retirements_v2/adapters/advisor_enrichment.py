"""Advisor enrichment composition for the v2 raw report."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import re
from typing import Any

from ..domain.evidence import AdvisorEnrichments, EnrichmentValue
from ..domain.execution import RunContext
from .advisor_metadata_api import AdvisorMetadataApiSource
from .resource_graph_api import ResourceGraphApiSource


class AdvisorEnrichmentError(RuntimeError):
    """Raised when Advisor enrichment cannot be acquired or indexed safely."""


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _fold(value: Any) -> str:
    return str(value).strip().casefold() if value is not None else ""


def _normalized_arm(value: Any) -> str:
    return re.sub(r"/+", "/", str(value).strip()).casefold().rstrip("/")


def _subscription_id(recommendation: Mapping[str, Any], resource_id: str) -> str:
    direct = recommendation.get("subscriptionId") or recommendation.get("subscription_id")
    if direct:
        return _fold(direct)
    match = re.search(r"/subscriptions/([^/]+)", resource_id, re.IGNORECASE)
    return _fold(match.group(1)) if match else ""


def _resource_id(recommendation: Mapping[str, Any]) -> str:
    properties = _mapping(recommendation.get("properties"))
    metadata = _mapping(properties.get("resourceMetadata") or properties.get("resource_metadata"))
    return str(metadata.get("resourceId") or metadata.get("resource_id") or metadata.get("id") or "")


def _metadata_service_id(row: Mapping[str, Any]) -> str:
    containers = [row]
    properties = _mapping(row.get("properties"))
    source_properties = _mapping(row.get("sourceProperties"))
    containers.extend((properties, source_properties))
    containers.extend(
        (
            _mapping(properties.get("sourceProperties")),
            _mapping(properties.get("serviceRetirement")),
            _mapping(source_properties.get("serviceRetirement")),
        )
    )
    for container in containers:
        retirement = _mapping(container.get("serviceRetirement"))
        candidate = retirement.get("serviceId") or container.get("serviceId")
        if candidate:
            return _fold(candidate)
    return ""


def _metadata_id(row: Mapping[str, Any]) -> str:
    properties = _mapping(row.get("properties"))
    return _fold(row.get("id") or row.get("metadataId") or properties.get("id") or properties.get("metadataId"))


def _resource_key(row: Mapping[str, Any]) -> str:
    return _normalized_arm(row.get("resourceId") or row.get("resource_id") or row.get("id"))


def _subscription_key(row: Mapping[str, Any]) -> str:
    return _fold(row.get("subscriptionId") or row.get("subscription_id"))


def _rows(value: Any, source_name: str) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"{source_name} returned an unsupported response shape")
    rows = tuple(value)
    if any(not isinstance(row, Mapping) for row in rows):
        raise ValueError(f"{source_name} returned an unsupported response shape")
    return rows


def _add(index: dict[str, EnrichmentValue], key: str, row: Mapping[str, Any]) -> None:
    if not key:
        return
    copied = dict(row)
    current = index.get(key)
    if current is None:
        index[key] = copied
    elif isinstance(current, tuple):
        index[key] = (*current, copied)
    else:
        index[key] = (current, copied)


class AzureAdvisorEnrichmentSource:
    def __init__(
        self,
        metadata_source: AdvisorMetadataApiSource,
        resource_graph_source: ResourceGraphApiSource,
    ) -> None:
        self.metadata_source = metadata_source
        self.resource_graph_source = resource_graph_source

    def enrich(
        self,
        context: RunContext,
        recommendations: Sequence[Any],
    ) -> AdvisorEnrichments:
        try:
            recommendation_rows = tuple(_mapping(getattr(item, "payload", item)) for item in recommendations)
            if any(not row for row in recommendation_rows):
                raise ValueError("Advisor recommendation has an unsupported shape")
            metadata_rows = _rows(self.metadata_source.acquire(context), "Advisor metadata")
            resource_ids: list[str] = []
            seen_resource_ids: set[str] = set()
            for recommendation in recommendation_rows:
                resource_id = _normalized_arm(_resource_id(recommendation))
                if resource_id and resource_id not in seen_resource_ids:
                    seen_resource_ids.add(resource_id)
                    resource_ids.append(resource_id)
            resource_rows = _rows(
                self.resource_graph_source.lookup(context, tuple(resource_ids)),
                "Resource Graph resources",
            )
            subscription_rows = _rows(
                self.resource_graph_source.lookup_subscriptions(context),
                "Resource Graph subscriptions",
            )
            metadata: dict[str, EnrichmentValue] = {}
            resources: dict[str, EnrichmentValue] = {}
            subscriptions: dict[str, EnrichmentValue] = {}
            for row in metadata_rows:
                service_key = _metadata_service_id(row)
                metadata_key = _metadata_id(row)
                _add(metadata, service_key, row)
                if metadata_key != service_key:
                    _add(metadata, metadata_key, row)
            for row in resource_rows:
                _add(resources, _resource_key(row), row)
            for row in subscription_rows:
                _add(subscriptions, _subscription_key(row), row)
            return AdvisorEnrichments(
                metadata=metadata,
                resources=resources,
                subscriptions=subscriptions,
            )
        except AdvisorEnrichmentError:
            raise
        except Exception as exc:
            raise AdvisorEnrichmentError("advisor enrichment source acquisition failed") from exc


__all__ = ["AdvisorEnrichmentError", "AzureAdvisorEnrichmentSource"]
