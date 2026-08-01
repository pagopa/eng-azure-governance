"""Source evidence models shared by acquisition and raw contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


EnrichmentValue = Mapping[str, Any] | tuple[Mapping[str, Any], ...]


@dataclass(frozen=True, slots=True)
class AdvisorEnrichments:
    metadata: Mapping[str, EnrichmentValue] = field(default_factory=dict)
    resources: Mapping[str, EnrichmentValue] = field(default_factory=dict)
    subscriptions: Mapping[str, EnrichmentValue] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ServiceHealthSupplementalEvidence:
    advisor_records: tuple[Mapping[str, Any], ...] = ()
    resource_inventory: Mapping[str, Mapping[str, Any]] = ()
    subscription_inventory: Mapping[str, Mapping[str, Any]] = ()
    resource_associations: Mapping[tuple[str, str], tuple[Mapping[str, Any], ...]] = field(default_factory=dict)
    subscription_name_sources: Mapping[str, str] = field(default_factory=dict)


__all__ = ["AdvisorEnrichments", "EnrichmentValue", "ServiceHealthSupplementalEvidence"]
