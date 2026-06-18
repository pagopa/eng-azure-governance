from __future__ import annotations

from typing import Any, cast

from src.comitato.comitato_azure_retirements.libs.advisor import (
    collect_advisor_recommendations,
    index_metadata,
    index_resource_graph,
)
from src.comitato.comitato_azure_retirements.libs.arm_client import ArmPageResult


class FakeArmClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, str] | None]] = []

    def list_with_nextlink(
        self,
        url: str,
        params: dict[str, str] | None = None,
        items_key: str = "value",
    ) -> ArmPageResult:
        self.calls.append((url, params))
        subscription = url.split("/subscriptions/")[1].split("/")[0]
        return ArmPageResult(items=[{"id": f"rec-{subscription}"}], page_count=2)


def test_collect_advisor_recommendations_tags_subscription_id() -> None:
    client = FakeArmClient()

    rows, pages = collect_advisor_recommendations(cast(Any, client), ["sub-1", "sub-2"])

    assert pages == {"sub-1": 2, "sub-2": 2}
    assert [row["_subscriptionId"] for row in rows] == ["sub-1", "sub-2"]


def test_index_metadata_maps_id_and_service_id_keys() -> None:
    metadata = {
        "id": "meta-1",
        "properties": {
            "sourceProperties": {
                "serviceRetirement": {
                    "serviceId": "service-1",
                }
            }
        },
    }

    indexed = index_metadata([metadata])

    assert indexed["meta-1"] is metadata
    assert indexed["service-1"] is metadata


def test_index_resource_graph_uses_lowercase_resource_id_key() -> None:
    rows = [
        {
            "ServiceID": "service-1",
            "resourceId": "/subscriptions/SUB-1/resourceGroups/RG/providers/Microsoft.Compute/virtualMachines/vm1",
            "name": "vm1",
        }
    ]

    indexed = index_resource_graph(rows)

    key = ("service-1", "/subscriptions/sub-1/resourcegroups/rg/providers/microsoft.compute/virtualmachines/vm1")
    assert indexed[key]["name"] == "vm1"
