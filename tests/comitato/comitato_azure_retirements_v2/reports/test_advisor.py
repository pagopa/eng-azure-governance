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
from src.comitato.comitato_azure_retirements_v2.domain.evidence import AdvisorEnrichments
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)
from src.comitato.comitato_azure_retirements_v2.reports.advisor import (
    ADVISOR_REPORT,
    normalize_advisor,
    prepare_advisor_report,
)


def context() -> RunContext:
    return RunContext(
        run_id="run-advisor",
        as_of_date=date(2026, 7, 30),
        created_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
        request=RunRequest(ReportSelector.ADVISOR),
        scope=Scope(mode="explicit", subscription_ids=("sub-a",)),
        catalog_identity=CatalogIdentity(1, "a" * 64),
        dependency_plan=DependencyPlan(("scope", "catalog", "advisor", "publication")),
    )


def acquisition() -> SourceAcquisition:
    return SourceAcquisition(
        receipt=AcquisitionReceipt(
            source="advisor",
            api_version="2025-01-01",
            expected_subscriptions=1,
            completed_subscriptions=1,
            pages=1,
            source_records=1,
            complete=True,
        ),
        records=(
            {
                "id": "/subscriptions/sub-a/providers/Microsoft.Advisor/recommendations/rec-1",
                "properties": {
                    "recommendationTypeId": "retirement-1",
                    "recommendationStatus": "nEw",
                    "resourceMetadata": {
                        "resourceId": "/subscriptions/sub-a/resourceGroups/RG/providers/Microsoft.Storage/storageAccounts/a"
                    },
                    "shortDescription": {"problem": "problem", "solution": "solution"},
                    "actions": [{"order": 2, "text": "second"}, {"order": 1, "text": "first"}],
                    "retirementDate": "2027-03-31",
                    "category": "Reliability",
                    "impact": "High",
                    "lastUpdated": "2026-07-29T12:00:00Z",
                },
            },
        ),
    )


def test_normalize_advisor_preserves_the_complete_recommendation_evidence_pair() -> None:
    result = normalize_advisor(acquisition(), context(), AdvisorEnrichments())

    assert result.is_valid
    assert result.value is not None
    artifact = result.value
    assert len(ADVISOR_REPORT.contract.header) == 44
    assert artifact.records[0]["recommendation_status"] == "nEw"
    assert artifact.records[0]["published_resource_id"].endswith("/a")
    assert artifact.records[0]["resource_linkage_source"] == "resource_id"
    assert artifact.records[0]["actions_json"] == '[{"order":2,"text":"second"},{"order":1,"text":"first"}]'
    assert artifact.records[0]["retirement_date"] == "2027-03-31"
    assert len(artifact.companion_records) == 1
    assert artifact.records[0]["raw_record_ref"] == artifact.companion_records[0]["raw_record_ref"]

    encoded = ADVISOR_REPORT.contract.encode(artifact)
    assert tuple(encoded.data.splitlines()[0].decode().split("\t")) == ADVISOR_REPORT.contract.header


def test_normalize_advisor_rejects_unknown_status_instead_of_silently_dropping_it() -> None:
    payload = acquisition().records[0].copy()
    payload["properties"] = dict(payload["properties"])
    payload["properties"]["recommendationStatus"] = "Unexpected"
    result = normalize_advisor(
        SourceAcquisition(receipt=acquisition().receipt, records=(payload,)),
        context(),
        AdvisorEnrichments(),
    )

    assert not result.is_valid
    assert result.diagnostics[0].code == "invalid_recommendation_status"


def test_normalize_advisor_defaults_missing_live_status_to_new() -> None:
    payload = acquisition().records[0].copy()
    payload["properties"] = dict(payload["properties"])
    del payload["properties"]["recommendationStatus"]

    result = normalize_advisor(
        SourceAcquisition(receipt=acquisition().receipt, records=(payload,)),
        context(),
        AdvisorEnrichments(),
    )

    assert result.is_valid
    assert result.value is not None
    assert result.value.records[0]["recommendation_status"] == "New"


def test_normalize_advisor_reads_live_retirement_fields_from_extended_properties() -> None:
    payload = acquisition().records[0].copy()
    payload["properties"] = dict(payload["properties"])
    payload["properties"].pop("retirementDate")
    payload["properties"]["extendedProperties"] = {
        "retirementDate": "2028-04-15",
        "retirementFeatureName": "Legacy feature",
    }

    result = normalize_advisor(
        SourceAcquisition(receipt=acquisition().receipt, records=(payload,)),
        context(),
        AdvisorEnrichments(),
    )

    assert result.is_valid
    assert result.value is not None
    row = result.value.records[0]
    assert row["retiring_feature"] == "Legacy feature"
    assert row["retirement_date"] == "2028-04-15"
    assert row["retirement_date_source"] == "properties.extendedProperties.retirementDate"


def _integrity_context() -> RunContext:
    return RunContext(
        run_id="raw-advisor",
        as_of_date=date(2026, 7, 30),
        created_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
        request=RunRequest(ReportSelector.ADVISOR),
        scope=Scope(mode="explicit", subscription_ids=("sub-a",)),
        catalog_identity=CatalogIdentity(1, "a" * 64),
        dependency_plan=DependencyPlan(("scope", "catalog", "advisor", "publication")),
    )


def test_advisor_rejects_resource_subscription_disagreement() -> None:
    payload = {
        "id": "/subscriptions/sub-a/providers/Microsoft.Advisor/recommendations/rec-1",
        "properties": {
            "recommendationTypeId": "retirement-1",
            "recommendationStatus": "New",
            "resourceMetadata": {
                "resourceId": "/subscriptions/sub-b/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/a"
            },
        },
    }
    result = normalize_advisor(
        SourceAcquisition(
            receipt=AcquisitionReceipt("advisor", "test-v1", 1, 1, 1, 1, True),
            records=(payload,),
        ),
        _integrity_context(),
        AdvisorEnrichments(),
    )

    assert not result.is_valid
    assert {diagnostic.code for diagnostic in result.diagnostics} == {
        "resource_subscription_mismatch"
    }


def test_advisor_contract_rejects_duplicate_companion_reference() -> None:
    current = _integrity_context()
    row = {column: "" for column in ADVISOR_REPORT.contract.header}
    row.update(
        {
            "run_id": current.run_id,
            "advisor_recommendation_id": "rec-1",
            "recommendation_status": "New",
            "subscription_id": "sub-a",
            "raw_record_ref": "ref-1",
        }
    )
    artifact = Artifact(
        contract=ADVISOR_REPORT.contract.name,
        schema_version=1,
        run_id=current.run_id,
        records=(row,),
        companion_records=(
            {"raw_record_ref": "ref-1"},
            {"raw_record_ref": "ref-1"},
        ),
    )

    result = ADVISOR_REPORT.contract.validate(artifact, current)

    assert not result.is_valid
    assert any(item.code == "raw_pair_bijection_failed" for item in result.diagnostics)


def _empty_acquisition(*, complete: bool) -> SourceAcquisition:
    return SourceAcquisition(
        receipt=AcquisitionReceipt(
            source="advisor",
            api_version="test-v1",
            expected_subscriptions=1,
            completed_subscriptions=1 if complete else 0,
            pages=1,
            source_records=0,
            complete=complete,
        )
    )


def test_prepare_advisor_report_preserves_complete_empty_source() -> None:
    prepared = prepare_advisor_report(
        _empty_acquisition(complete=True), _integrity_context(), AdvisorEnrichments()
    )

    assert prepared.acquisition.records == ()
    assert tuple(item.logical_path for item in prepared.artifacts) == ADVISOR_REPORT.paths
    assert prepared.artifacts[0].data == ("\t".join(ADVISOR_REPORT.contract.header) + "\n").encode()


def test_prepare_advisor_report_rejects_incomplete_receipt() -> None:
    with pytest.raises(ApplicationError, match="incomplete advisor acquisition"):
        prepare_advisor_report(
            _empty_acquisition(complete=False), _integrity_context(), AdvisorEnrichments()
        )


def test_prepare_advisor_report_returns_normalized_acquisition_and_encoded_pair():
    prepared = prepare_advisor_report(acquisition(), context(), AdvisorEnrichments())
    assert prepared.acquisition.records == prepared.artifact.records
    assert prepared.acquisition.companion_records == prepared.artifact.companion_records
    assert tuple(item.logical_path for item in prepared.artifacts) == ADVISOR_REPORT.paths
    assert ADVISOR_REPORT.verify_staged_artifact(
        ADVISOR_REPORT.contract.path,
        {item.logical_path: item.data for item in prepared.artifacts},
        context(),
    ) == ()
