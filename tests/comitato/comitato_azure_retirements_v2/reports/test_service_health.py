from datetime import date, datetime, timezone

import pytest

from src.comitato.comitato_azure_retirements_v2.acquisition.model import (
    AcquisitionReceipt,
    SourceAcquisition,
)
from src.comitato.comitato_azure_retirements_v2.application.orchestration_errors import (
    ApplicationError,
)
from src.comitato.comitato_azure_retirements_v2.contracts.model import Artifact
from src.comitato.comitato_azure_retirements_v2.domain.evidence import (
    ServiceHealthSupplementalEvidence,
)
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)
from src.comitato.comitato_azure_retirements_v2.reports.service_health import (
    SERVICE_HEALTH_REPORT,
    normalize_service_health,
    prepare_service_health_report,
)


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
                "subscriptionId": "sub-a",
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
    assert len(SERVICE_HEALTH_REPORT.contract.header) == 55
    row = artifact.records[0]
    assert row["record_type"] == "service_health_event_resource"
    assert row["description_problem"] == "Read details (https://example.test)."
    assert row["retirement_date"] == "2027-03-31"
    assert row["published_resource_id"].endswith("/a")
    assert row["subscription_id"] == "sub-a"
    assert row["raw_record_ref"] == artifact.companion_records[0]["raw_record_ref"]

    encoded = SERVICE_HEALTH_REPORT.contract.encode(artifact)
    assert tuple(encoded.data.splitlines()[0].decode().split("\t")) == SERVICE_HEALTH_REPORT.contract.header


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


def _health_event(**properties: object) -> dict[str, object]:
    base = {
        "id": "/subscriptions/sub-a/providers/Microsoft.ResourceHealth/events/event-1",
        "name": "TRACK-1",
        "subscriptionId": "sub-a",
        "properties": {
            "trackingId": "TRACK-1",
            "eventType": "HealthAdvisory",
            "level": "Warning",
            "status": "Active",
            "isGlobal": False,
            "impactedServices": [],
            "impactedResources": [],
        },
    }
    base["properties"] = {**base["properties"], **properties}
    return base


def _health_acquisition(event: dict[str, object]) -> SourceAcquisition:
    return SourceAcquisition(
        receipt=AcquisitionReceipt("service-health", "test-v1", 1, 1, 1, 1, True),
        records=(event,),
    )


def test_service_health_preserves_each_resource_without_service_cross_product() -> None:
    result = normalize_service_health(
        _health_acquisition(_health_event(
            impactedServices=[
                {"serviceName": "Storage", "serviceGuid": "storage-guid", "impactedRegions": [{"regionName": "West Europe"}]},
                {"serviceName": "Compute", "serviceGuid": "compute-guid", "impactedRegions": [{"regionName": "North Europe"}]},
            ],
            impactedResources=[
                {"subscriptionId": "sub-a", "resourceId": "/subscriptions/sub-a/r1"},
                {"subscriptionId": "sub-a", "resourceId": "/subscriptions/sub-a/r2"},
            ],
        )),
        context(),
        ServiceHealthSupplementalEvidence(),
    )

    assert result.is_valid
    assert result.value is not None
    assert len(result.value.records) == 2
    assert {row["published_resource_id"] for row in result.value.records} == {
        "/subscriptions/sub-a/r1", "/subscriptions/sub-a/r2"
    }


def test_service_health_global_requires_explicit_global_evidence() -> None:
    result = normalize_service_health(
        _health_acquisition(_health_event(isGlobal=True)),
        context(),
        ServiceHealthSupplementalEvidence(),
    )

    assert result.is_valid
    assert result.value is not None
    row = result.value.records[0]
    assert row["record_type"] == "service_health_event_global"
    assert row["subscription_evidence_source"] == "explicit_global"


def test_service_health_non_global_without_affected_subscription_is_blocked() -> None:
    event = _health_event()
    event.pop("subscriptionId")
    result = normalize_service_health(
        _health_acquisition(event), context(), ServiceHealthSupplementalEvidence()
    )
    assert not result.is_valid
    assert result.diagnostics[0].code == "missing_affected_subscription"
    assert result.diagnostics[0].record_ref == "/subscriptions/sub-a/providers/Microsoft.ResourceHealth/events/event-1"


def test_service_health_global_projection_rejects_affected_subscription_or_resource() -> None:
    result = normalize_service_health(
        _health_acquisition(_health_event(isGlobal=True)),
        context(),
        ServiceHealthSupplementalEvidence(),
    )
    assert result.is_valid and result.value is not None
    row = dict(result.value.records[0])
    row["subscription_id"] = "sub-a"
    invalid = Artifact(
        contract=SERVICE_HEALTH_REPORT.contract.name,
        schema_version=1,
        run_id=result.value.run_id,
        records=(row,),
        companion_records=result.value.companion_records,
    )
    checked = SERVICE_HEALTH_REPORT.contract.validate(invalid, context())
    assert not checked.is_valid
    assert any(item.code == "global_evidence_has_subscription" for item in checked.diagnostics)


def test_service_health_keeps_direct_and_supplemental_resource_associations() -> None:
    result = normalize_service_health(
        _health_acquisition(_health_event(
            trackingId="TRACK-1",
            impactedResources=[{"subscriptionId": "sub-a", "resourceId": "/subscriptions/sub-a/direct"}],
        )),
        context(),
        ServiceHealthSupplementalEvidence(advisor_records=(
            {"tracking_id": "TRACK-1", "subscription_id": "sub-a", "resource_id": "/subscriptions/sub-a/supplemental", "recommendation_type_id": "retirement-1", "platform_state": "New"},
        )),
    )

    assert result.is_valid
    assert result.value is not None
    assert {row["published_resource_id"] for row in result.value.records} == {
        "/subscriptions/sub-a/direct", "/subscriptions/sub-a/supplemental"
    }
    assert {row["resource_evidence_source"] for row in result.value.records} == {
        "service_health_resource", "advisor_recommendation"
    }


def _empty_acquisition(*, complete: bool) -> SourceAcquisition:
    return SourceAcquisition(
        receipt=AcquisitionReceipt("service-health", "test-v1", 1, 1 if complete else 0, 1, 0, complete)
    )


def test_prepare_service_health_report_preserves_complete_empty_source() -> None:
    prepared = prepare_service_health_report(
        _empty_acquisition(complete=True), context(), ServiceHealthSupplementalEvidence()
    )

    assert prepared.acquisition.records == ()
    assert tuple(item.logical_path for item in prepared.artifacts) == SERVICE_HEALTH_REPORT.paths
    assert prepared.artifacts[0].data == ("\t".join(SERVICE_HEALTH_REPORT.contract.header) + "\n").encode()


def test_prepare_service_health_report_rejects_incomplete_receipt() -> None:
    with pytest.raises(ApplicationError, match="incomplete service-health acquisition"):
        prepare_service_health_report(
            _empty_acquisition(complete=False), context(), ServiceHealthSupplementalEvidence()
        )


def test_prepare_service_health_report_returns_normalized_acquisition_and_encoded_pair():
    prepared = prepare_service_health_report(
        acquisition(), context(), ServiceHealthSupplementalEvidence()
    )
    assert prepared.acquisition.records == prepared.artifact.records
    assert prepared.acquisition.companion_records == prepared.artifact.companion_records
    assert tuple(item.logical_path for item in prepared.artifacts) == SERVICE_HEALTH_REPORT.paths
    assert SERVICE_HEALTH_REPORT.verify_staged_artifact(
        SERVICE_HEALTH_REPORT.contract.path,
        {item.logical_path: item.data for item in prepared.artifacts},
        context(),
    ) == ()
