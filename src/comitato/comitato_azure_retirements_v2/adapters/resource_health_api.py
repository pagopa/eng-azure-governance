"""Azure Resource Health / Service Health source adapter."""

from __future__ import annotations

from ..acquisition.model import SourceAcquisition
from ..domain.execution import RunContext
from .arm_http import ArmHttpClient
from .subscription_list import acquire_subscription_list


RESOURCE_HEALTH_API_VERSION = "2025-05-01"


class ResourceHealthApiSource:
    def __init__(self, http: ArmHttpClient, *, api_version: str = RESOURCE_HEALTH_API_VERSION) -> None:
        self.http = http
        self.api_version = api_version

    def acquire(self, context: RunContext) -> SourceAcquisition:
        return acquire_subscription_list(
            self.http,
            context,
            source="service-health",
            api_version=self.api_version,
            response_name="Resource Health",
            url_for=lambda subscription_id: (
                "https://management.azure.com/subscriptions/"
                f"{subscription_id}/providers/Microsoft.ResourceHealth/events"
            ),
            params={"api-version": self.api_version},
            annotate=lambda item, subscription_id: {
                **item,
                "_subscriptionId": item.get("_subscriptionId", subscription_id),
            },
        )


ServiceHealthApiSource = ResourceHealthApiSource

__all__ = ["RESOURCE_HEALTH_API_VERSION", "ResourceHealthApiSource", "ServiceHealthApiSource"]
