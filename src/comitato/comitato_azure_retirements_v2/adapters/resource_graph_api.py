"""Azure Resource Graph enrichment adapter."""

from __future__ import annotations

from typing import Any, Sequence

from ..domain.execution import RunContext
from .arm_http import ArmHttpClient


RESOURCE_GRAPH_API_VERSION = "2024-04-01"


class ResourceGraphApiSource:
    def __init__(self, http: ArmHttpClient, *, api_version: str = RESOURCE_GRAPH_API_VERSION) -> None:
        self.http = http
        self.api_version = api_version

    def lookup(self, context: RunContext, resource_ids: Sequence[str] = ()) -> tuple[dict[str, Any], ...]:
        query = "resources | project id, name, type, location, resourceGroup, subscriptionId, tags"
        body: dict[str, Any] = {
            "subscriptions": list(context.scope.subscription_ids),
            "query": query,
            "options": {"resultFormat": "objectArray"},
        }
        if resource_ids:
            quoted = ", ".join(json_quote(value.casefold()) for value in resource_ids)
            body["query"] = f"resources | where tolower(id) in ({quoted}) | project id, name, type, location, resourceGroup, subscriptionId, tags"
        results: list[dict[str, Any]] = []
        seen_tokens: set[str] = set()
        while True:
            payload = self.http.post_json(
                f"https://management.azure.com/providers/Microsoft.ResourceGraph/resources?api-version={self.api_version}",
                body,
            )
            data = payload.get("data")
            if not isinstance(data, list) or any(not isinstance(item, dict) for item in data):
                raise ValueError("Resource Graph response has unsupported data shape")
            results.extend(data)
            token = payload.get("$skipToken") or payload.get("skipToken")
            if not token:
                break
            if not isinstance(token, str) or token in seen_tokens:
                raise ValueError("Resource Graph continuation token repeated")
            seen_tokens.add(token)
            body["options"] = {"resultFormat": "objectArray", "$skipToken": token}
        return tuple(results)


def json_quote(value: str) -> str:
    import json

    return json.dumps(value, ensure_ascii=False)


__all__ = ["RESOURCE_GRAPH_API_VERSION", "ResourceGraphApiSource"]
