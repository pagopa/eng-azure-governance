from datetime import date, datetime, timezone
import json

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


def context(*subscription_ids: str) -> RunContext:
    scoped_subscriptions = subscription_ids or ("sub-a",)
    return RunContext(
        run_id="run-health",
        as_of_date=date(2026, 7, 30),
        created_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
        request=RunRequest(ReportSelector.SERVICE_HEALTH),
        scope=Scope(mode="explicit", subscription_ids=scoped_subscriptions),
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


def test_normalize_service_health_skips_unrelated_resource_health_events() -> None:
    payload = acquisition().records[0].copy()
    payload["properties"] = dict(payload["properties"])
    payload["properties"].update(
        {
            "eventType": "PlannedMaintenance",
            "level": "Informational",
            "status": "Resolved",
        }
    )

    result = normalize_service_health(
        SourceAcquisition(receipt=acquisition().receipt, records=(payload,)),
        context(),
        ServiceHealthSupplementalEvidence(),
    )

    assert result.is_valid
    assert result.value is not None
    assert result.value.records == ()


def test_normalize_service_health_accepts_informational_retirement_advisory() -> None:
    payload = acquisition().records[0].copy()
    payload["properties"] = dict(payload["properties"])
    payload["properties"]["level"] = "Informational"

    result = normalize_service_health(
        SourceAcquisition(receipt=acquisition().receipt, records=(payload,)),
        context(),
        ServiceHealthSupplementalEvidence(),
    )

    assert result.is_valid
    assert result.value is not None
    assert result.value.records[0]["event_level"] == "Informational"


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


def _health_acquisition(
    event: dict[str, object] | tuple[dict[str, object], ...],
) -> SourceAcquisition:
    records = (event,) if isinstance(event, dict) else event
    count = len(records)
    return SourceAcquisition(
        receipt=AcquisitionReceipt("service-health", "test-v1", count, count, count, count, True),
        records=records,
    )


def _impact_event(
    *,
    regions: tuple[str, ...] = ("West US",),
    subscription_id: str = "sub-a",
    include_unrelated: bool = False,
) -> dict[str, object]:
    impacts: list[dict[str, object]] = [
        {
            "impactedService": "Service Bus",
            "impactedServiceGuid": "2f15c16c-f172-4947-961f-7291994ba791",
            "impactedRegions": [{"impactedRegion": region} for region in regions],
        },
    ]
    if include_unrelated:
        impacts.append(
            {
                "impactedService": "Compute",
                "impactedServiceGuid": "compute-guid",
                "impactedRegions": [{"impactedRegion": "West US"}],
            }
        )
    event = {
        "id": f"/subscriptions/{subscription_id}/providers/Microsoft.ResourceHealth/events/8Q2_-MK8",
        "name": "8Q2_-MK8",
        "subscriptionId": subscription_id,
        "properties": {
            "eventType": "HealthAdvisory",
            "level": "Informational",
            "status": "Active",
            "trackingId": "8Q2_-MK8",
            "title": "Action recommended: Migrate your Azure Service Bus SDKs by 30 September 2026\u202f",
            "summary": "<p><em>You\u2019re receiving this notice.</em></p>",
            "description": "<p>We\u2019ll retire the SDKs.&nbsp;</p>",
            "recommendedActions": {},
            "impact": impacts,
            "impactedServices": [],
            "impactedResources": [],
        },
    }
    return event


def test_normalize_service_health_reads_impact_and_canonicalizes_published_text() -> None:
    result = normalize_service_health(
        _health_acquisition(
            _impact_event(regions=("West US", "North Europe"), include_unrelated=True)
        ),
        context(),
        ServiceHealthSupplementalEvidence(
            subscription_inventory={"sub-a": {"name": "UAT-pagoPA"}},
        ),
    )

    assert result.is_valid
    assert result.value is not None
    rows = result.value.records
    assert len(rows) == 3
    assert {(row["impacted_service"], row["impacted_service_guid"], row["impacted_region"]) for row in rows} == {
        ("Service Bus", "2f15c16c-f172-4947-961f-7291994ba791", "West US"),
        ("Service Bus", "2f15c16c-f172-4947-961f-7291994ba791", "North Europe"),
        ("Compute", "compute-guid", "West US"),
    }
    row = rows[0]
    assert all(item["record_type"] == "service_health_event_service_region" for item in rows)
    assert row["title"].isascii()
    assert row["summary"] == "You're receiving this notice."
    assert row["description_problem"] == "We'll retire the SDKs."
    assert row["recommended_actions"] == ""
    assert "<" not in row["title"] + row["summary"] + row["description_problem"]


def test_normalize_service_health_consumes_resource_graph_association_and_provenance() -> None:
    resource_id = "/subscriptions/sub-a/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm-1"
    result = normalize_service_health(
        _health_acquisition(_impact_event()),
        context(),
        ServiceHealthSupplementalEvidence(
            resource_associations={
                ("8q2_-mk8", "sub-a"): (
                    {
                        "resourceId": resource_id,
                        "resourceType": "Microsoft.Compute/virtualMachines",
                        "region": "West US",
                        "resource_evidence_source": "service_health_resource_graph",
                    },
                ),
            },
            resource_inventory={
                resource_id.casefold(): {
                    "id": resource_id,
                    "name": "vm-1",
                    "resourceGroup": "rg",
                    "type": "Microsoft.Compute/virtualMachines",
                },
            },
            subscription_inventory={"sub-a": {"name": "UAT-pagoPA"}},
            subscription_name_sources={"sub-a": "platform_catalog"},
        ),
    )

    assert result.is_valid
    assert result.value is not None
    assert len(result.value.records) == 1
    row = result.value.records[0]
    assert row["published_resource_id"] == resource_id
    assert row["resource_name"] == "vm-1"
    assert row["resource_evidence_source"] == "service_health_resource_graph"
    provenance = json.loads(row["provenance_json"])
    assert provenance["subscription_name_source"] == "platform_catalog"
    assert provenance["resource_evidence_source"] == "service_health_resource_graph"
    assert provenance["resource_graph_queries"] == [
        "subscription_inventory",
        "service_health_impacted_resources",
        "resource_inventory",
    ]


def test_normalize_service_health_marks_completed_resource_no_match_as_not_published() -> None:
    result = normalize_service_health(
        _health_acquisition(_impact_event()),
        context(),
        ServiceHealthSupplementalEvidence(
            subscription_inventory={"sub-a": {"name": "UAT-pagoPA"}},
            subscription_name_sources={"sub-a": "resource_graph_inventory"},
        ),
    )

    assert result.is_valid
    assert result.value is not None
    row = result.value.records[0]
    assert row["published_resource_id"] == ""
    assert row["resource_name"] == ""
    assert row["resource_group"] == ""
    assert row["resource_type"] == ""
    assert row["resource_evidence_status"] == "not_published"
    assert row["resource_inventory_match_status"] == "not_applicable"
    assert "resource_not_published" in row["diagnostic_flags"]


def test_normalize_service_health_expands_all_65_impact_regions() -> None:
    regions = tuple(f"region-{index:02d}" for index in range(65))
    result = normalize_service_health(
        _health_acquisition(_impact_event(regions=regions)),
        context(),
        ServiceHealthSupplementalEvidence(
            subscription_inventory={"sub-a": {"name": "UAT-pagoPA"}},
        ),
    )

    assert result.is_valid
    assert result.value is not None
    assert len(result.value.records) == 65
    assert {row["impacted_region"] for row in result.value.records} == set(regions)


def test_normalize_service_health_expands_65_regions_for_three_subscriptions() -> None:
    subscription_ids = ("sub-a", "sub-b", "sub-c")
    regions = tuple(f"region-{index:02d}" for index in range(65))
    result = normalize_service_health(
        _health_acquisition(
            tuple(
                _impact_event(regions=regions, subscription_id=subscription_id)
                for subscription_id in subscription_ids
            )
        ),
        context(*subscription_ids),
        ServiceHealthSupplementalEvidence(
            subscription_inventory={
                "sub-a": {"name": "UAT-pagoPA"},
                "sub-b": {"name": "PROD-pagoPA"},
                "sub-c": {"name": "DEV-pagoPA"},
            },
        ),
    )

    assert result.is_valid
    assert result.value is not None
    assert len(result.value.records) == 195
    assert {row["subscription_name"] for row in result.value.records} == {
        "UAT-pagoPA",
        "PROD-pagoPA",
        "DEV-pagoPA",
    }
    assert {row["impacted_region"] for row in result.value.records} == set(regions)


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


def _validate_service_health_row(row: dict[str, str]):
    artifact = Artifact(
        contract=SERVICE_HEALTH_REPORT.contract.name,
        schema_version=1,
        run_id=row["run_id"],
        records=(row,),
        companion_records=({"raw_record_ref": row["raw_record_ref"]},),
    )
    return SERVICE_HEALTH_REPORT.contract.validate(artifact, context())


def _service_health_contract_row() -> dict[str, str]:
    result = normalize_service_health(
        _health_acquisition(_impact_event()),
        context(),
        ServiceHealthSupplementalEvidence(
            subscription_inventory={"sub-a": {"name": "UAT-pagoPA"}},
            subscription_name_sources={"sub-a": "resource_graph_inventory"},
        ),
    )
    assert result.is_valid and result.value is not None
    return dict(result.value.records[0])


def test_service_health_contract_requires_non_global_subscription_name() -> None:
    row = _service_health_contract_row()
    row["subscription_name"] = ""

    checked = _validate_service_health_row(row)

    assert not checked.is_valid
    assert any(item.code == "missing_subscription_name" for item in checked.diagnostics)


def test_service_health_contract_requires_empty_fields_for_not_published() -> None:
    row = _service_health_contract_row()
    row["resource_name"] = "invented-name"

    checked = _validate_service_health_row(row)

    assert not checked.is_valid
    assert any(item.code == "invalid_not_published_resource_fields" for item in checked.diagnostics)


def test_service_health_contract_requires_resource_id_for_published_status() -> None:
    row = _service_health_contract_row()
    row["resource_evidence_status"] = "published"

    checked = _validate_service_health_row(row)

    assert not checked.is_valid
    assert any(item.code == "published_resource_missing_id" for item in checked.diagnostics)


@pytest.mark.parametrize(
    ("field", "value"),
    (("title", "Résumé"), ("summary", "<p>summary</p>"), ("description_problem", "<p>description</p>"), ("recommended_actions", "<p>act</p>")),
)
def test_service_health_contract_rejects_noncanonical_published_text(field: str, value: str) -> None:
    row = _service_health_contract_row()
    row[field] = value

    checked = _validate_service_health_row(row)

    assert not checked.is_valid
    assert any(item.code == "noncanonical_service_health_text" for item in checked.diagnostics)


def test_service_health_contract_rejects_unknown_resource_graph_query_label() -> None:
    row = _service_health_contract_row()
    provenance = json.loads(row["provenance_json"])
    provenance["resource_graph_queries"] = ["unknown_query"]
    row["provenance_json"] = json.dumps(provenance, separators=(",", ":"), sort_keys=True)

    checked = _validate_service_health_row(row)

    assert not checked.is_valid
    assert any(item.code == "invalid_resource_graph_query_label" for item in checked.diagnostics)


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
        acquisition(),
        context(),
        ServiceHealthSupplementalEvidence(
            subscription_inventory={"sub-a": {"name": "UAT-pagoPA"}},
        ),
    )
    assert prepared.acquisition.records == prepared.artifact.records
    assert prepared.acquisition.companion_records == prepared.artifact.companion_records
    assert tuple(item.logical_path for item in prepared.artifacts) == SERVICE_HEALTH_REPORT.paths
    assert SERVICE_HEALTH_REPORT.verify_staged_artifact(
        SERVICE_HEALTH_REPORT.contract.path,
        {item.logical_path: item.data for item in prepared.artifacts},
        context(),
    ) == ()
