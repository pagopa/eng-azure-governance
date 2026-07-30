"""Azure Advisor REST source adapter."""

from __future__ import annotations

from typing import Any

from ..acquisition.evidence import SourcePage
from ..acquisition.model import AcquisitionReceipt, SourceAcquisition
from ..acquisition.paging import ScriptedRequest, collect_complete_pages
from ..domain.execution import RunContext
from .arm_http import ArmHttpClient


ADVISOR_API_VERSION = "2025-01-01"


class AdvisorApiSource:
    def __init__(self, http: ArmHttpClient, *, api_version: str = ADVISOR_API_VERSION) -> None:
        self.http = http
        self.api_version = api_version

    def acquire(self, context: RunContext) -> SourceAcquisition:
        requests: list[ScriptedRequest] = []
        for subscription_id in context.scope.subscription_ids:
            url = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Advisor/recommendations"
            pages = self.http.list_pages(
                url,
                params={
                    "api-version": self.api_version,
                    "$filter": "Category eq 'HighAvailability' and SubCategory eq 'ServiceUpgradeAndRetirement'",
                },
            )
            requests.append(
                ScriptedRequest(
                    subscription_id,
                    tuple(SourcePage(subscription_id, tuple(self._with_scope(item, subscription_id) for item in page.items), page.continuation_url) for page in pages),
                )
            )
        collected = collect_complete_pages(requests, lambda item: str(item.get("id", "")))
        return SourceAcquisition(
            receipt=AcquisitionReceipt(
                source="advisor",
                api_version=self.api_version,
                expected_subscriptions=collected.receipt.expected_subscriptions,
                completed_subscriptions=collected.receipt.completed_subscriptions,
                pages=collected.receipt.pages,
                source_records=collected.receipt.source_records,
                complete=collected.receipt.complete,
                continuation_tokens=collected.receipt.continuation_tokens,
            ),
            records=collected.records,
        )

    @staticmethod
    def _with_scope(item: Any, subscription_id: str) -> dict[str, Any]:
        if not isinstance(item, dict):
            raise ValueError("Advisor response item must be an object")
        copy = dict(item)
        copy.setdefault("subscriptionId", subscription_id)
        return copy


AzureAdvisorSource = AdvisorApiSource

__all__ = ["ADVISOR_API_VERSION", "AdvisorApiSource", "AzureAdvisorSource"]
