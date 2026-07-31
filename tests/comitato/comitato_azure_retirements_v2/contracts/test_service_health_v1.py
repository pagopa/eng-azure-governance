from __future__ import annotations

from datetime import date, datetime, timezone

from src.comitato.comitato_azure_retirements_v2.acquisition.model import (
    AcquisitionReceipt,
    SourceAcquisition,
)
from src.comitato.comitato_azure_retirements_v2.application.service_health import normalize_service_health
from src.comitato.comitato_azure_retirements_v2.contracts.service_health_v1 import (
    SERVICE_HEALTH_V1,
    SERVICE_HEALTH_V1_HEADER,
)
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)
from src.comitato.comitato_azure_retirements_v2.domain.evidence import ServiceHealthSupplementalEvidence


def context() -> RunContext:
    return RunContext(
        run_id="run-health",
        as_of_date=date(2026, 7, 30),
        created_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
        request=RunRequest(ReportSelector.SERVICE_HEALTH),
        scope=Scope(mode="explicit", subscription_ids=("sub-a",)),
        catalog_identity=CatalogIdentity(1, "a" * 64),
        dependency_plan=DependencyPlan(("scope", "catalog", "service-health", "publication")),
    )


def acquisition() -> SourceAcquisition:
    return SourceAcquisition(
        receipt=AcquisitionReceipt("service-health", "2024-10-01", 1, 1, 1, 1, True),
        records=(
            {
                "id": "/subscriptions/sub-a/providers/Microsoft.ResourceHealth/events/event-1",
                "name": "TRACK-1",
                "properties": {
                    "trackingId": "TRACK-1",
                    "eventType": "HealthAdvisory",
                    "level": "Warning",
                    "status": "Active",
                    "eventSubType": "Retirement",
                    "eventSource": "ServiceHealth",
                    "title": "Title",
                    "summary": "Summary",
                    "article": {"articleContent": '<p>Read <a href="https://example.test">details</a>.</p>'},
                    "recommendedActions": "Act now",
                    "impactStartTime": "2026-07-01T00:00:00Z",
                    "impactMitigationTime": "2027-03-31T00:00:00Z",
                    "lastUpdateTime": "2026-07-29T12:00:00Z",
                    "impactedServices": [{"serviceName": "Storage", "serviceGuid": "guid-1", "impactedRegions": [{"regionName": "West Europe"}]}],
                    "impactedResources": [{"subscriptionId": "sub-a", "resourceId": "/subscriptions/sub-a/resourceGroups/RG/providers/Microsoft.Storage/storageAccounts/a"}],
                },
            },
        ),
    )


def test_normalize_service_health_renders_complete_article_and_preserves_association() -> None:
    result = normalize_service_health(
        acquisition(), context(), ServiceHealthSupplementalEvidence()
    )

    assert result.is_valid
    assert result.value is not None
    artifact = result.value
    assert len(SERVICE_HEALTH_V1_HEADER) == 55
    row = artifact.records[0]
    assert row["record_type"] == "service_health_event_resource"
    assert row["description_problem"] == "Read details (https://example.test)."
    assert row["retirement_date"] == "2027-03-31"
    assert row["published_resource_id"].endswith("/a")
    assert row["subscription_id"] == "sub-a"
    assert row["raw_record_ref"] == artifact.companion_records[0]["raw_record_ref"]

    encoded = SERVICE_HEALTH_V1.encode(artifact)
    assert tuple(encoded.data.splitlines()[0].decode().split("\t")) == SERVICE_HEALTH_V1_HEADER


def test_normalize_service_health_rejects_unknown_classification() -> None:
    payload = acquisition().records[0].copy()
    payload["properties"] = dict(payload["properties"])
    payload["properties"]["level"] = "Notice"
    result = normalize_service_health(
        SourceAcquisition(receipt=acquisition().receipt, records=(payload,)),
        context(),
        ServiceHealthSupplementalEvidence(),
    )

    assert not result.is_valid
    assert result.diagnostics[0].code == "invalid_service_health_classification"


def test_normalize_service_health_preserves_explicit_recommendation_type_edge() -> None:
    payload = acquisition().records[0].copy()
    payload["properties"] = dict(payload["properties"])
    payload["properties"]["recommendationTypeId"] = "retirement-1"

    result = normalize_service_health(
        SourceAcquisition(receipt=acquisition().receipt, records=(payload,)),
        context(),
        ServiceHealthSupplementalEvidence(),
    )

    assert result.is_valid
    assert result.value is not None
    assert result.value.records[0]["recommendation_type_id"] == "retirement-1"
