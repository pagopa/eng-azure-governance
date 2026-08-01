"""Azure Resource Graph enrichment adapter."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Sequence

from ..domain.execution import RunContext
from .arm_http import ArmHttpClient


RESOURCE_GRAPH_API_VERSION = "2024-04-01"


class ResourceGraphApiSource:
    def __init__(self, http: ArmHttpClient, *, api_version: str = RESOURCE_GRAPH_API_VERSION) -> None:
        self.http = http
        self.api_version = api_version

    def query(self, context: RunContext, query: str) -> tuple[dict[str, Any], ...]:
        body: dict[str, Any] = {
            "subscriptions": list(context.scope.subscription_ids),
            "query": query,
            "options": {"resultFormat": "objectArray"},
        }
        results: list[dict[str, Any]] = []
        seen_tokens: set[str] = set()
        while True:
            payload = self.http.post_json(
                f"https://management.azure.com/providers/Microsoft.ResourceGraph/resources?api-version={self.api_version}",
                body,
            )
            data = payload.get("data")
            if not isinstance(data, list) or any(not isinstance(item, Mapping) for item in data):
                raise ValueError("Resource Graph response has unsupported data shape")
            results.extend(dict(item) for item in data)
            token = payload.get("$skipToken") if "$skipToken" in payload else payload.get("skipToken")
            if token is None:
                break
            if not isinstance(token, str) or not token:
                raise ValueError("Resource Graph continuation token has unsupported shape")
            if token in seen_tokens:
                raise ValueError("Resource Graph continuation token repeated")
            seen_tokens.add(token)
            body["options"] = {"resultFormat": "objectArray", "$skipToken": token}
        return tuple(results)

    def lookup(self, context: RunContext, resource_ids: Sequence[str] = ()) -> tuple[dict[str, Any], ...]:
        return self.lookup_resources(context, resource_ids)

    def lookup_subscriptions(self, context: RunContext) -> tuple[dict[str, Any], ...]:
        return self.query(
            context,
            "resourcecontainers | where type =~ \"microsoft.resources/subscriptions\" | project subscriptionId = tolower(subscriptionId), name",
        )

    def lookup_subscription_inventory(self, context: RunContext) -> tuple[dict[str, Any], ...]:
        return self.query(
            context,
            "resourcecontainers | where type =~ \"microsoft.resources/subscriptions\" | project subscriptionId, subscriptionName=name",
        )

    def lookup_service_health_resources(self, context: RunContext) -> tuple[dict[str, Any], ...]:
        return self.query(
            context,
            "servicehealthresources | where type =~ \"microsoft.resourcehealth/events/impactedresources\" | project id, subscriptionId, properties",
        )

    def lookup_resources(
        self,
        context: RunContext,
        resource_ids: Sequence[str],
    ) -> tuple[dict[str, Any], ...]:
        normalized_ids = tuple(
            dict.fromkeys(
                str(resource_id).strip().casefold()
                for resource_id in resource_ids
                if str(resource_id).strip()
            )
        )
        if not normalized_ids:
            return ()
        results: list[dict[str, Any]] = []
        for offset in range(0, len(normalized_ids), 100):
            batch = normalized_ids[offset : offset + 100]
            quoted = ", ".join(json_quote(resource_id) for resource_id in batch)
            results.extend(
                self.query(
                    context,
                    f"resources | where tolower(id) in ({quoted}) | project id, name, type, location, resourceGroup, subscriptionId, tags, resourceId = tolower(id)",
                )
            )
        return tuple(results)


def json_quote(value: str) -> str:
    import json

    return json.dumps(value, ensure_ascii=False)


__all__ = ["RESOURCE_GRAPH_API_VERSION", "ResourceGraphApiSource"]
