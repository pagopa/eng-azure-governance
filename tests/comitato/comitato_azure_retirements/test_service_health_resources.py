from __future__ import annotations

from src.comitato.comitato_azure_retirements.libs.service_health_resources import (
    index_impacted_resources,
)


def test_index_impacted_resources_uses_verified_azure_fields() -> None:
    target = (
        "/subscriptions/sub-1/resourceGroups/rg-one/"
        "providers/Microsoft.Storage/storageAccounts/account-one"
    )
    rows = [
        {
            "id": (
                "/subscriptions/sub-1/providers/Microsoft.ResourceHealth/events/"
                "TRK-1/impactedResources/item-one"
            ),
            "subscriptionId": "SUB-1",
            "properties": {
                "targetResourceId": target,
                "targetResourceType": "Microsoft.Storage/storageAccounts",
                "targetRegion": "westeurope",
            },
        }
    ]

    indexed = index_impacted_resources(rows, tracking_ids={"TRK-1"})

    assert indexed[("trk-1", "sub-1")][0].resource_id == target
    assert indexed[("trk-1", "sub-1")][0].resource_group == "rg-one"
    assert indexed[("trk-1", "sub-1")][0].resource_type == "Microsoft.Storage/storageAccounts"


def test_index_impacted_resources_ignores_unrequested_tracking_ids() -> None:
    rows = [
        {
            "id": (
                "/subscriptions/sub-1/providers/Microsoft.ResourceHealth/events/"
                "TRK-OTHER/impactedResources/item-one"
            ),
            "subscriptionId": "sub-1",
            "properties": {"targetResourceId": "/subscriptions/sub-1/resourceGroups/rg-one"},
        }
    ]
    assert index_impacted_resources(rows, tracking_ids={"TRK-1"}) == {}
