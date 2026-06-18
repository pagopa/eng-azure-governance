"""Resource Graph collection helpers."""

from __future__ import annotations

from typing import Any

from .arm_client import ArmClient


RESOURCE_GRAPH_URL = "https://management.azure.com/providers/Microsoft.ResourceGraph/resources?api-version=2024-04-01"


def query_resource_graph(
    client: ArmClient,
    *,
    query: str,
    subscriptions: list[str],
    management_groups: list[str],
    first: int = 1000,
) -> tuple[list[dict[str, Any]], bool, int]:
    skip_token: str | None = None
    rows: list[dict[str, Any]] = []
    page_count = 0
    result_truncated = False

    while True:
        payload: dict[str, Any] = {
            "query": query,
            "options": {"$top": first},
        }
        if subscriptions:
            payload["subscriptions"] = subscriptions
        if management_groups:
            payload["managementGroups"] = management_groups
        if skip_token:
            payload["options"]["$skipToken"] = skip_token

        response = client.post_json(RESOURCE_GRAPH_URL, payload)
        page_count += 1

        page_rows = response.get("data", [])
        if isinstance(page_rows, list):
            rows.extend(page_rows)

        skip_token = response.get("$skipToken") or response.get("skipToken")
        result_truncated = result_truncated or bool(response.get("resultTruncated"))

        if not skip_token:
            break

    return rows, result_truncated, page_count
