"""Source evidence models shared by acquisition and raw contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class AdvisorRecommendationEvidence:
    recommendation_id: str
    payload: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class ServiceHealthEventEvidence:
    event_id: str
    payload: Mapping[str, Any]
    collection_subscription_id: str = ""

    @property
    def is_explicit_global(self) -> bool:
        properties = self.payload.get("properties", {})
        if not isinstance(properties, Mapping):
            return False
        marker = properties.get("isGlobal")
        return marker is True or (
            isinstance(marker, str) and marker.casefold() == "true"
        )


__all__ = ["AdvisorRecommendationEvidence", "ServiceHealthEventEvidence"]
