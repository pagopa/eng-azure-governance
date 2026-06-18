from __future__ import annotations

from src.comitato.comitato_azure_retirements.libs.resource_graph import query_resource_graph


class FakeArmClient:
    def __init__(self, responses: list[dict[str, object]]) -> None:
        self._responses = responses
        self.calls: list[tuple[str, dict[str, object]]] = []

    def post_json(self, url: str, payload: dict[str, object]) -> dict[str, object]:
        self.calls.append((url, payload))
        return self._responses.pop(0)


def test_query_resource_graph_paginates_and_tracks_truncation() -> None:
    client = FakeArmClient(
        [
            {
                "data": [{"id": "row-1"}],
                "$skipToken": "next-token",
                "resultTruncated": True,
            },
            {
                "data": [{"id": "row-2"}],
            },
        ]
    )

    rows, truncated, page_count = query_resource_graph(
        client,
        query="resources | limit 5",
        subscriptions=["sub-1"],
        management_groups=["mg-1"],
        first=25,
    )

    assert [row["id"] for row in rows] == ["row-1", "row-2"]
    assert truncated is True
    assert page_count == 2

    first_payload = client.calls[0][1]
    assert first_payload["subscriptions"] == ["sub-1"]
    assert first_payload["managementGroups"] == ["mg-1"]
    assert first_payload["options"] == {"$top": 25}

    second_payload = client.calls[1][1]
    assert second_payload["options"] == {"$top": 25, "$skipToken": "next-token"}
