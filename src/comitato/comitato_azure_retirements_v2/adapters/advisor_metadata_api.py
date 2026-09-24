"""Azure Advisor metadata source adapter."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..domain.execution import RunContext
from .arm_http import ArmHttpClient


ADVISOR_METADATA_API_VERSION = "2025-01-01"
ADVISOR_METADATA_URL = "https://management.azure.com/providers/Microsoft.Advisor/metadata"


def flatten_metadata_items(items: Sequence[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
    rows: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, Mapping):
            raise ValueError("Advisor metadata item has unsupported shape")
        supported_values: Any = item.get("supportedValues")
        if supported_values is None:
            properties = item.get("properties")
            if isinstance(properties, Mapping):
                supported_values = properties.get("supportedValues")
        if supported_values is None:
            rows.append(dict(item))
            continue
        if not isinstance(supported_values, list):
            raise ValueError("Advisor metadata supportedValues has unsupported shape")
        for child in supported_values:
            if not isinstance(child, Mapping):
                raise ValueError("Advisor metadata supportedValues child has unsupported shape")
            rows.append(dict(child))
    return tuple(rows)


class AdvisorMetadataApiSource:
    def __init__(self, http: ArmHttpClient, *, api_version: str = ADVISOR_METADATA_API_VERSION) -> None:
        self.http = http
        self.api_version = api_version

    def acquire(self, context: RunContext) -> tuple[dict[str, Any], ...]:
        pages = self.http.list_pages(
            ADVISOR_METADATA_URL,
            params={
                "api-version": self.api_version,
                "$filter": "recommendationCategory eq 'HighAvailability' and recommendationSubCategory eq 'ServiceUpgradeAndRetirement'",
                "$expand": "ibiza",
            },
            run_id=context.run_id,
        )
        rows: list[dict[str, Any]] = []
        for page in pages:
            rows.extend(flatten_metadata_items(page.items))
        return tuple(rows)


__all__ = ["ADVISOR_METADATA_API_VERSION", "AdvisorMetadataApiSource", "flatten_metadata_items"]
