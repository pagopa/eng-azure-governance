from __future__ import annotations

from datetime import date, datetime, timezone

from src.comitato.comitato_azure_retirements_v2.acquisition.model import (
    AcquisitionReceipt,
    SourceAcquisition,
)
from src.comitato.comitato_azure_retirements_v2.application.advisor import (
    AdvisorEnrichments,
    normalize_advisor,
)
from src.comitato.comitato_azure_retirements_v2.application.service_health import (
    ServiceHealthSupplementalEvidence,
    normalize_service_health,
)
from src.comitato.comitato_azure_retirements_v2.contracts.advisor_v1 import ADVISOR_V1
from src.comitato.comitato_azure_retirements_v2.contracts.model import Artifact
from src.comitato.comitato_azure_retirements_v2.contracts.service_health_v1 import (
    SERVICE_HEALTH_V1,
)
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)


def _context(selector: ReportSelector, source: str) -> RunContext:
    return RunContext(
        run_id=f"raw-{source}",
        as_of_date=date(2026, 7, 30),
        created_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
        request=RunRequest(selector),
        scope=Scope(mode="explicit", subscription_ids=("sub-a",)),
        catalog_identity=CatalogIdentity(1, "a" * 64),
        dependency_plan=DependencyPlan(("scope", "catalog", source, "publication")),
    )


def _advisor_payload() -> dict[str, object]:
    return {
        "id": "/subscriptions/sub-a/providers/Microsoft.Advisor/recommendations/rec-1",
        "properties": {
            "recommendationTypeId": "retirement-1",
            "recommendationStatus": "New",
            "resourceMetadata": {
                "resourceId": "/subscriptions/sub-b/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/a"
            },
        },
    }


def _advisor_acquisition(payload: dict[str, object]) -> SourceAcquisition:
    return SourceAcquisition(
        receipt=AcquisitionReceipt("advisor", "test-v1", 1, 1, 1, 1, True),
        records=(payload,),
    )


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


def test_advisor_rejects_resource_subscription_disagreement() -> None:
    result = normalize_advisor(
        _advisor_acquisition(_advisor_payload()),
        _context(ReportSelector.ADVISOR, "advisor"),
        AdvisorEnrichments(),
    )

    assert not result.is_valid
    assert {diagnostic.code for diagnostic in result.diagnostics} == {
        "resource_subscription_mismatch"
    }


def test_service_health_preserves_each_resource_without_service_cross_product() -> None:
    result = normalize_service_health(
        _health_acquisition(
            _health_event(
                impactedServices=[
                    {
                        "serviceName": "Storage",
                        "serviceGuid": "storage-guid",
                        "impactedRegions": [{"regionName": "West Europe"}],
                    },
                    {
                        "serviceName": "Compute",
                        "serviceGuid": "compute-guid",
                        "impactedRegions": [{"regionName": "North Europe"}],
                    },
                ],
                impactedResources=[
                    {"subscriptionId": "sub-a", "resourceId": "/subscriptions/sub-a/r1"},
                    {"subscriptionId": "sub-a", "resourceId": "/subscriptions/sub-a/r2"},
                ],
            )
        ),
        _context(ReportSelector.SERVICE_HEALTH, "service-health"),
        ServiceHealthSupplementalEvidence(),
    )

    assert result.is_valid
    assert result.value is not None
    rows = result.value.artifact.records
    assert len(rows) == 2
    assert {row["published_resource_id"] for row in rows} == {
        "/subscriptions/sub-a/r1",
        "/subscriptions/sub-a/r2",
    }


def test_service_health_global_requires_explicit_global_evidence() -> None:
    result = normalize_service_health(
        _health_acquisition(_health_event(isGlobal=True)),
        _context(ReportSelector.SERVICE_HEALTH, "service-health"),
        ServiceHealthSupplementalEvidence(),
    )

    assert result.is_valid
    assert result.value is not None
    row = result.value.artifact.records[0]
    assert row["record_type"] == "service_health_event_global"
    assert row["subscription_evidence_source"] == "explicit_global"


def test_service_health_keeps_direct_and_supplemental_resource_associations() -> None:
    event = _health_event(
        trackingId="TRACK-1",
        impactedResources=[
            {"subscriptionId": "sub-a", "resourceId": "/subscriptions/sub-a/direct"}
        ],
    )
    result = normalize_service_health(
        _health_acquisition(event),
        _context(ReportSelector.SERVICE_HEALTH, "service-health"),
        ServiceHealthSupplementalEvidence(
            advisor_records=(
                {
                    "tracking_id": "TRACK-1",
                    "subscription_id": "sub-a",
                    "resource_id": "/subscriptions/sub-a/supplemental",
                    "recommendation_type_id": "retirement-1",
                    "platform_state": "New",
                },
            )
        ),
    )

    assert result.is_valid
    assert result.value is not None
    rows = result.value.artifact.records
    assert {row["published_resource_id"] for row in rows} == {
        "/subscriptions/sub-a/direct",
        "/subscriptions/sub-a/supplemental",
    }
    assert {row["resource_evidence_source"] for row in rows} == {
        "service_health_resource",
        "advisor_recommendation",
    }


def test_advisor_contract_rejects_duplicate_companion_reference() -> None:
    context = _context(ReportSelector.ADVISOR, "advisor")
    row = {column: "" for column in ADVISOR_V1.header}
    row.update({"run_id": context.run_id, "advisor_recommendation_id": "rec-1", "recommendation_status": "New", "subscription_id": "sub-a", "raw_record_ref": "ref-1"})
    artifact = Artifact(
        contract=ADVISOR_V1.name,
        schema_version=1,
        run_id=context.run_id,
        records=(row,),
        companion_records=(
            {"raw_record_ref": "ref-1"},
            {"raw_record_ref": "ref-1"},
        ),
    )

    result = ADVISOR_V1.validate(artifact, context)

    assert not result.is_valid
    assert any(d.code == "raw_pair_bijection_failed" for d in result.diagnostics)
