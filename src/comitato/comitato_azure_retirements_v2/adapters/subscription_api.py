"""Azure subscription scope resolution adapter."""

from __future__ import annotations

from ..domain.execution import RunRequest, Scope
from .arm_http import ArmHttpClient


SUBSCRIPTIONS_API_VERSION = "2022-12-01"


class SubscriptionApiSource:
    def __init__(self, http: ArmHttpClient, *, api_version: str = SUBSCRIPTIONS_API_VERSION) -> None:
        self.http = http
        self.api_version = api_version

    def resolve(self, request: RunRequest, *, run_id: str = "") -> Scope:
        if request.subscription_ids:
            return Scope(tuple(sorted(set(request.subscription_ids))), mode="explicit")
        pages = self.http.list_pages(
            f"https://management.azure.com/subscriptions",
            params={"api-version": self.api_version},
            run_id=run_id,
        )
        subscription_ids = tuple(
            sorted(
                {
                    str(item.get("subscriptionId") or item.get("id", "").rsplit("/", 1)[-1])
                    for page in pages
                    for item in page.items
                    if str(item.get("subscriptionId") or item.get("id", "")).strip()
                }
            )
        )
        if not subscription_ids:
            raise ValueError("Azure resolved an empty subscription scope")
        return Scope(subscription_ids, mode="resolved")


__all__ = ["SUBSCRIPTIONS_API_VERSION", "SubscriptionApiSource"]
