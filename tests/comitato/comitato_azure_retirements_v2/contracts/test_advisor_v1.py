from __future__ import annotations

from datetime import date, datetime, timezone

from src.comitato.comitato_azure_retirements_v2.acquisition.model import (
    AcquisitionReceipt,
    SourceAcquisition,
)
from src.comitato.comitato_azure_retirements_v2.application.advisor import normalize_advisor
from src.comitato.comitato_azure_retirements_v2.contracts.advisor_v1 import (
    ADVISOR_V1_HEADER,
    ADVISOR_V1,
)
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)
from src.comitato.comitato_azure_retirements_v2.domain.evidence import AdvisorEnrichments


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
    assert len(ADVISOR_V1_HEADER) == 44
    assert artifact.records[0]["recommendation_status"] == "nEw"
    assert artifact.records[0]["published_resource_id"].endswith("/a")
    assert artifact.records[0]["resource_linkage_source"] == "resource_id"
    assert artifact.records[0]["actions_json"] == '[{"order":2,"text":"second"},{"order":1,"text":"first"}]'
    assert artifact.records[0]["retirement_date"] == "2027-03-31"
    assert len(artifact.companion_records) == 1
    assert artifact.records[0]["raw_record_ref"] == artifact.companion_records[0]["raw_record_ref"]

    encoded = ADVISOR_V1.encode(artifact)
    assert tuple(encoded.data.splitlines()[0].decode().split("\t")) == ADVISOR_V1_HEADER


def test_normalize_advisor_rejects_unknown_status_instead_of_silently_dropping_it() -> None:
    payload = acquisition().records[0].copy()
    payload["properties"] = dict(payload["properties"])
    payload["properties"]["recommendationStatus"] = "Unexpected"
    result = normalize_advisor(
        SourceAcquisition(
            receipt=acquisition().receipt,
            records=(payload,),
        ),
        context(),
        AdvisorEnrichments(),
    )

    assert not result.is_valid
    assert result.diagnostics[0].code == "invalid_recommendation_status"
