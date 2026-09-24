"""Azure Advisor REST source adapter."""

from __future__ import annotations

from ..acquisition.model import SourceAcquisition
from ..domain.execution import RunContext
from .arm_http import ArmHttpClient
from .subscription_list import acquire_subscription_list


ADVISOR_API_VERSION = "2025-01-01"


class AdvisorApiSource:
    def __init__(self, http: ArmHttpClient, *, api_version: str = ADVISOR_API_VERSION) -> None:
        self.http = http
        self.api_version = api_version

    def acquire(self, context: RunContext) -> SourceAcquisition:
        return acquire_subscription_list(
            self.http,
            context,
            source="advisor",
            api_version=self.api_version,
            response_name="Advisor",
            url_for=lambda subscription_id: (
                "https://management.azure.com/subscriptions/"
                f"{subscription_id}/providers/Microsoft.Advisor/recommendations"
            ),
            params={
                "api-version": self.api_version,
                "$filter": "Category eq 'HighAvailability' and SubCategory eq 'ServiceUpgradeAndRetirement'",
            },
            annotate=lambda item, subscription_id: {
                **item,
                "subscriptionId": item.get("subscriptionId", subscription_id),
            },
        )


AzureAdvisorSource = AdvisorApiSource

__all__ = ["ADVISOR_API_VERSION", "AdvisorApiSource", "AzureAdvisorSource"]
