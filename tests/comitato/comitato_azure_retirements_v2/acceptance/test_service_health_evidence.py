from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime, timezone
from io import StringIO
import json
from pathlib import Path
from typing import Any

from src.comitato.comitato_azure_retirements_v2.acquisition.model import (
    AcquisitionReceipt,
    SourceAcquisition,
)
from src.comitato.comitato_azure_retirements_v2.acquisition.evidence import (
    ObservationAccounting,
    SourceRecord,
)
from src.comitato.comitato_azure_retirements_v2.application.orchestration import (
    RetirementsApplication,
)
from src.comitato.comitato_azure_retirements_v2.contracts import AGGREGATE_V1
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    ReportSelector,
    RunRequest,
    Scope,
)
from src.comitato.comitato_azure_retirements_v2.domain.platforms import (
    PlatformAssignment,
    PlatformCatalogSnapshot,
    SubscriptionId,
)
from src.comitato.comitato_azure_retirements_v2.reports.service_health import (
    SERVICE_HEALTH_REPORT,
)
from tests.comitato.comitato_azure_retirements_v2.acceptance.harness import (
    FixedClock,
    FixedRunIdFactory,
    ScriptedAdvisorSource,
    TemporaryAtomicPublicationStore,
    _FixedScopeSource,
)


SUBSCRIPTIONS = (
    "11111111-1111-1111-1111-111111111111",
    "22222222-2222-2222-2222-222222222222",
    "33333333-3333-3333-3333-333333333333",
)
REGIONS = tuple(f"region-{index:02d}" for index in range(65))
SERVICE_GUID = "2f15c16c-f172-4947-961f-7291994ba791"
TRACKING_ID = "8Q2_-MK8"


@dataclass(frozen=True, slots=True)
class FixedCatalogSource:
    snapshot: PlatformCatalogSnapshot

    def load(self) -> PlatformCatalogSnapshot:
        return self.snapshot


@dataclass(frozen=True, slots=True)
class FixedServiceHealthSource:
    acquisition: SourceAcquisition

    def acquire(self, context: Any) -> SourceAcquisition:
        return self.acquisition


class EmptyResourceGraphSource:
    def __init__(self) -> None:
        self.subscription_inventory_calls = 0
        self.service_health_resource_calls = 0
        self.resource_inventory_calls: list[tuple[str, ...]] = []

    def lookup_subscription_inventory(self, context: Any) -> tuple[dict[str, str], ...]:
        self.subscription_inventory_calls += 1
        return (
            {"subscriptionId": SUBSCRIPTIONS[0], "subscriptionName": "UAT-pagoPA"},
            {"subscriptionId": SUBSCRIPTIONS[1], "subscriptionName": "PROD-pagoPA"},
        )

    def lookup_service_health_resources(self, context: Any) -> tuple[dict[str, Any], ...]:
        self.service_health_resource_calls += 1
        return ()

    def lookup_resources(
        self, context: Any, resource_ids: tuple[str, ...]
    ) -> tuple[dict[str, Any], ...]:
        self.resource_inventory_calls.append(tuple(resource_ids))
        return ()


def _event(subscription_id: str) -> dict[str, Any]:
    return {
        "id": f"/subscriptions/{subscription_id}/providers/Microsoft.ResourceHealth/events/{TRACKING_ID}",
        "name": TRACKING_ID,
        "subscriptionId": subscription_id,
        "properties": {
            "eventType": "HealthAdvisory",
            "level": "Informational",
            "status": "Active",
            "trackingId": TRACKING_ID,
            "isGlobal": False,
            "title": "Action recommended: Migrate your Azure Service Bus SDKs by 30 September 2026\u202f",
            "summary": "<p><em>You\u2019re receiving this notice.</em></p>",
            "description": "<p>We\u2019ll retire the SDKs.&nbsp;</p>",
            "recommendedActions": {},
            "impact": [
                {
                    "impactedService": "Service Bus",
                    "impactedServiceGuid": SERVICE_GUID,
                    "impactedRegions": [
                        {"impactedRegion": region} for region in REGIONS
                    ],
                }
            ],
            "impactedServices": [],
            "impactedResources": [],
        },
    }


def _catalog() -> PlatformCatalogSnapshot:
    assignments = (
        PlatformAssignment(SubscriptionId(SUBSCRIPTIONS[0]), "pagoPA", "UAT-pagoPA"),
        PlatformAssignment(SubscriptionId(SUBSCRIPTIONS[1]), "pagoPA", "PROD-pagoPA"),
        PlatformAssignment(SubscriptionId(SUBSCRIPTIONS[2]), "pagoPA", "DEV-pagoPA"),
    )
    return PlatformCatalogSnapshot(1, "a" * 64, assignments)


def test_service_health_acceptance_preserves_region_cardinality_and_evidence(tmp_path: Path) -> None:
    events = tuple(_event(subscription_id) for subscription_id in SUBSCRIPTIONS)
    acquisition = SourceAcquisition(
        receipt=AcquisitionReceipt(
            "service-health",
            "2025-05-01",
            expected_subscriptions=3,
            completed_subscriptions=3,
            pages=3,
            source_records=3,
            complete=True,
        ),
        records=events,
    )
    scope = Scope(mode="explicit", subscription_ids=SUBSCRIPTIONS)
    resource_graph = EmptyResourceGraphSource()
    publication = TemporaryAtomicPublicationStore(tmp_path / "exports")
    application = RetirementsApplication(
        scope_source=_FixedScopeSource(scope),
        catalog_source=FixedCatalogSource(_catalog()),
        advisor_source=ScriptedAdvisorSource((), True),
        service_health_source=FixedServiceHealthSource(acquisition),
        publication_store=publication,
        clock=FixedClock(datetime(2026, 7, 31, tzinfo=timezone.utc)),
        run_id_factory=FixedRunIdFactory("service-health-evidence"),
        resource_graph_source=resource_graph,
    )

    result = application.run(
        RunRequest(
            selector=ReportSelector.ALL,
            subscription_ids=SUBSCRIPTIONS,
            as_of_date=date(2026, 7, 31),
        )
    )

    service_health_artifact = next(
        artifact
        for artifact in result.candidate.artifacts
        if artifact.logical_path == SERVICE_HEALTH_REPORT.contract.path
    )
    service_health_rows = list(
        csv.DictReader(
            StringIO(service_health_artifact.data.decode("utf-8")), delimiter="\t"
        )
    )
    assert len(service_health_rows) == 195
    assert {row["impacted_service"] for row in service_health_rows} == {"Service Bus"}
    assert {row["impacted_service_guid"] for row in service_health_rows} == {SERVICE_GUID}
    assert {row["subscription_name"] for row in service_health_rows} == {
        "UAT-pagoPA",
        "PROD-pagoPA",
        "DEV-pagoPA",
    }
    assert all(row["resource_evidence_status"] == "not_published" for row in service_health_rows)
    assert all(row["resource_inventory_match_status"] == "not_applicable" for row in service_health_rows)
    assert {row["description_problem"] for row in service_health_rows} == {"We’ll retire the SDKs."}
    assert all("<" not in row["title"] and ">" not in row["title"] for row in service_health_rows)
    assert {row["impacted_region"] for row in service_health_rows} == set(REGIONS)

    aggregate_artifact = next(
        artifact
        for artifact in result.candidate.artifacts
        if artifact.logical_path == AGGREGATE_V1.path
    )
    aggregate_rows = list(
        csv.DictReader(StringIO(aggregate_artifact.data.decode("utf-8")), delimiter="\t")
    )
    assert len(aggregate_rows) == 1
    assert json.loads(aggregate_rows[0]["service_health_tracking_ids_json"]) == [TRACKING_ID]
    assert set(json.loads(aggregate_rows[0]["impacted_regions_json"])) == set(REGIONS)
    assert resource_graph.subscription_inventory_calls == 1
    assert resource_graph.service_health_resource_calls == 1
    assert resource_graph.resource_inventory_calls == [()]


def test_acquisition_preserves_collection_context_and_observation_accounting() -> None:
    record = SourceRecord(
        subscription_id=SUBSCRIPTIONS[0],
        identity="event-1",
        payload={"id": "event-1", "properties": {"status": "Active"}},
        source="service-health",
        page_number=2,
        continuation_token="page-2",
    )
    acquisition = SourceAcquisition(
        receipt=AcquisitionReceipt(
            source="service-health",
            api_version="2025-05-01",
            expected_subscriptions=3,
            completed_subscriptions=2,
            pages=2,
            source_records=1,
            complete=False,
            failed_subscriptions=(SUBSCRIPTIONS[2],),
        ),
        records=(record,),
        companion_records=({"event-1": "enrichment-used"},),
        accounting=(
            ObservationAccounting(
                source="service-health",
                subscription_id=SUBSCRIPTIONS[0],
                source_identity="event-1",
                destination="used",
                reason="health_advisory",
                raw_record_ref="event-1",
            ),
            ObservationAccounting(
                source="service-health",
                subscription_id=SUBSCRIPTIONS[1],
                source_identity="event-2",
                destination="excluded",
                reason="event_type:incident",
                raw_record_ref="event-2",
            ),
            ObservationAccounting(
                source="service-health",
                subscription_id=SUBSCRIPTIONS[2],
                source_identity="event-3",
                destination="error",
                reason="request_failed",
                raw_record_ref="event-3",
            ),
        ),
        collection_context={
            "subscription_ids": SUBSCRIPTIONS,
            "query": {"api-version": "2025-05-01"},
            "collected_at": "2026-09-22T10:00:00Z",
        },
        response_context=(
            {
                "subscription_id": SUBSCRIPTIONS[0],
                "page_number": 2,
                "continuation_token": "page-2",
                "complete": False,
            },
        ),
    )

    assert acquisition.collection_context["subscription_ids"] == SUBSCRIPTIONS
    assert acquisition.collection_context["query"]["api-version"] == "2025-05-01"
    assert acquisition.response_context[0]["continuation_token"] == "page-2"
    assert [item.destination for item in acquisition.accounting] == [
        "used",
        "excluded",
        "error",
    ]
    assert acquisition.companion_records[0]["event-1"] == "enrichment-used"
