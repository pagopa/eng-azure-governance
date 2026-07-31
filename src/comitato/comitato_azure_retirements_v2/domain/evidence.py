"""Source evidence models shared by acquisition and raw contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class AdvisorEnrichments:
    metadata: Mapping[str, Mapping[str, Any]] = ()
    resources: Mapping[str, Mapping[str, Any]] = ()
    subscriptions: Mapping[str, Mapping[str, Any]] = ()


@dataclass(frozen=True, slots=True)
class ServiceHealthSupplementalEvidence:
    advisor_records: tuple[Mapping[str, Any], ...] = ()
    resource_inventory: Mapping[str, Mapping[str, Any]] = ()
    subscription_inventory: Mapping[str, Mapping[str, Any]] = ()


__all__ = ["AdvisorEnrichments", "ServiceHealthSupplementalEvidence"]
