from __future__ import annotations

from src.comitato.comitato_azure_retirements.libs.service_health_resource_resolution import (
    build_advisor_association_query,
    collect_advisor_retirement_evidence,
    index_retirement_metadata,
    merge_resource_evidence,
    expand_events_for_resource_subscriptions,
    ResourceEvidence,
    validate_metadata_data_source_query,
)
import pytest


def test_index_retirement_metadata_maps_every_requested_tracking_id() -> None:
    rows = [
        {
            "id": "rec-type-1",
            "recommendationDataSourceQuery": "resources | project id, subscriptionId",
            "sourceProperties": {
                "serviceRetirement": {
                    "serviceHealth": {"trackingIds": ["XTKT-BW8", "OTHER-ID"]}
                }
            },
        }
    ]

    indexed = index_retirement_metadata(rows, {"XTKT-BW8", "MISSING"})

    assert indexed["xtkt-bw8"][0].recommendation_type_id == "rec-type-1"
    assert indexed["xtkt-bw8"][0].data_source_query.startswith("resources")
    assert indexed["missing"] == []


def test_index_retirement_metadata_is_tolerant_and_deduplicates_recommendations() -> None:
    rows = [
        {
            "id": "rec-type-1",
            "properties": {
                "recommendationDataSourceQuery": "resources | project id",
                "sourceProperties": {
                    "serviceRetirement": {
                        "serviceHealth": {"trackingIds": ["xtkt-bw8"]}
                    }
                },
            },
        },
        {
            "id": "rec-type-1",
            "recommendationDataSourceQuery": "",
            "sourceProperties": {"serviceRetirement": {"serviceHealth": {}}},
        },
        {"id": "malformed", "sourceProperties": []},
    ]

    indexed = index_retirement_metadata(rows, {"XTKT-BW8", "OTHER"})

    assert len(indexed["xtkt-bw8"]) == 1
    assert indexed["other"] == []


def test_advisor_query_keeps_new_and_resolved_existing_resources() -> None:
    query = build_advisor_association_query({"rec-type-1"})

    assert 'properties.platformState == "New"' not in query
    assert "join kind=leftouter" in query
    assert "resourceExists" in query


def test_metadata_query_rejects_non_inventory_tables() -> None:
    with pytest.raises(ValueError, match="read-only Resources"):
        validate_metadata_data_source_query("servicehealthresources | take 1")


def test_metadata_query_rejects_inventory_queries_that_union_other_tables() -> None:
    with pytest.raises(ValueError, match="read-only Resources"):
        validate_metadata_data_source_query("resources | union servicehealthresources")


def test_metadata_query_rejects_empty_query() -> None:
    with pytest.raises(ValueError, match="empty"):
        validate_metadata_data_source_query("  ")


class _GraphClient:
    pass


def test_collect_advisor_retirement_evidence_classifies_all_advisor_states(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    metadata_by_tracking = {
        "trk-1": [
            type(
                "Metadata",
                (),
                {
                    "recommendation_type_id": "rec-type-1",
                    "tracking_ids": ("TRK-1",),
                    "data_source_query": "",
                },
            )()
        ]
    }

    monkeypatch.setattr(
        "src.comitato.comitato_azure_retirements.libs.service_health_resource_resolution.query_resource_graph",
        lambda *_args, **_kwargs: (
            [
                {
                    "id": "advisor-row-1",
                    "subscriptionId": "sub-1",
                    "recommendationTypeId": "rec-type-1",
                    "resourceId": "/subscriptions/sub-1/resourceGroups/rg/providers/Microsoft.Web/sites/app",
                    "advisorPlatformState": "New",
                    "resourceExists": True,
                    "currentResourceGroup": "rg",
                    "currentResourceType": "Microsoft.Web/sites",
                    "currentRegion": "westeurope",
                },
                {
                    "id": "advisor-row-2",
                    "subscriptionId": "sub-1",
                    "recommendationTypeId": "rec-type-1",
                    "resourceId": "/subscriptions/sub-1/resourceGroups/rg/providers/Microsoft.Web/sites/old",
                    "advisorPlatformState": "Resolved",
                    "resourceExists": True,
                },
                {
                    "id": "advisor-row-3",
                    "subscriptionId": "sub-1",
                    "recommendationTypeId": "rec-type-1",
                    "resourceId": "/subscriptions/sub-1/resourceGroups/rg/providers/Microsoft.Web/sites/deleted",
                    "advisorPlatformState": "New",
                    "resourceExists": False,
                },
            ],
            False,
            2,
        ),
    )

    evidence, diagnostics = collect_advisor_retirement_evidence(
        _GraphClient(),
        metadata_by_tracking=metadata_by_tracking,
        subscriptions=["sub-1"],
        management_groups=[],
    )

    assert [item.status for item in evidence] == ["active", "resolved", "active"]
    assert evidence[2].resource_exists is False
    assert diagnostics["trk-1"]["advisor_pages"] == 2


def test_collect_advisor_retirement_evidence_does_not_use_association_id_as_resource(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    metadata_by_tracking = {
        "trk-1": [
            type(
                "Metadata",
                (),
                {
                    "recommendation_type_id": "rec-type-1",
                    "tracking_ids": ("TRK-1",),
                    "data_source_query": "",
                },
            )()
        ]
    }

    monkeypatch.setattr(
        "src.comitato.comitato_azure_retirements.libs.service_health_resource_resolution.query_resource_graph",
        lambda *_args, **_kwargs: (
            [
                {
                    "id": "advisor-association-1",
                    "subscriptionId": "sub-1",
                    "recommendationTypeId": "rec-type-1",
                    "resourceId": "malformed-resource-id",
                    "advisorPlatformState": "New",
                    "resourceExists": True,
                }
            ],
            False,
            1,
        ),
    )

    evidence, diagnostics = collect_advisor_retirement_evidence(
        _GraphClient(),
        metadata_by_tracking=metadata_by_tracking,
        subscriptions=["sub-1"],
        management_groups=[],
    )

    assert evidence[0].resource_id == "not_available"
    assert evidence[0].resource_exists is False
    assert diagnostics["trk-1"]["malformed_resource_ids"] == 1


def _health_event(tracking_id: str, subscription_id: str, last_update: str = "") -> dict[str, object]:
    return {
        "name": tracking_id,
        "_subscriptionId": subscription_id,
        "properties": {"lastUpdateTime": last_update},
    }


def _resource(subscription_id: str, name: str, *, status: str = "active", source: str = "advisor_retirement_recommendation") -> ResourceEvidence:
    return ResourceEvidence(
        tracking_id="XTKT-BW8",
        subscription_id=subscription_id,
        resource_id=f"/subscriptions/{subscription_id}/resourceGroups/rg/providers/Microsoft.Web/sites/{name}",
        resource_group="rg",
        resource_type="Microsoft.Web/sites",
        region="westeurope",
        source=source,
        status=status,
    )


def test_merge_resource_evidence_prefers_direct_and_active_and_excludes_deleted() -> None:
    direct = _resource("sub-a", "a", source="service_health_arg")
    advisor = _resource("SUB-A", "A", status="resolved")
    deleted = ResourceEvidence(
        tracking_id="XTKT-BW8",
        subscription_id="sub-a",
        resource_id="/subscriptions/sub-a/resourceGroups/rg/providers/Microsoft.Web/sites/deleted",
        resource_group="rg",
        resource_type="Microsoft.Web/sites",
        region="westeurope",
        source="advisor_retirement_recommendation",
        status="active",
        resource_exists=False,
    )

    result = merge_resource_evidence({"XTKT-BW8"}, [advisor, direct, deleted])

    rows = result.resources_by_event[("xtkt-bw8", "sub-a")]
    assert len(rows) == 1
    assert rows[0].source == "service_health_arg"
    assert rows[0].status == "active"
    assert result.excluded_by_tracking["xtkt-bw8"] == 1


def test_expand_events_recovers_an_advisor_only_subscription() -> None:
    expanded = expand_events_for_resource_subscriptions(
        [_health_event("XTKT-BW8", "sub-a", "2026-07-28T12:00:00Z")],
        {
            ("xtkt-bw8", "sub-a"): [_resource("sub-a", "a")],
            ("xtkt-bw8", "sub-b"): [_resource("sub-b", "b")],
        },
    )

    assert {event["_subscriptionId"] for event in expanded} == {"sub-a", "sub-b"}
    recovered = next(event for event in expanded if event["_subscriptionId"] == "sub-b")
    assert recovered["_resource_resolution_subscription_synthesized"] is True


def test_merge_resource_evidence_reports_tracking_ids_without_evidence() -> None:
    result = merge_resource_evidence({"XTKT-BW8", "MISSING"}, [])

    assert result.status_by_tracking["missing"] == "unsupported"
    assert result.resources_by_event == {}
