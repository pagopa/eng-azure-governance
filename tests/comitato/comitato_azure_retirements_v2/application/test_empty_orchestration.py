from dataclasses import dataclass, field
from datetime import datetime, timezone

import pytest

from src.comitato.comitato_azure_retirements_v2.acquisition.model import (
    AcquisitionReceipt,
    SourceAcquisition,
)
from src.comitato.comitato_azure_retirements_v2.application.orchestration import RetirementsApplication
from src.comitato.comitato_azure_retirements_v2.application.orchestration_errors import ApplicationError
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    ReportSelector,
    RunRequest,
    Scope,
)
from src.comitato.comitato_azure_retirements_v2.ports import RuntimeEvent
from src.comitato.comitato_azure_retirements_v2.publication.model import (
    PublicationCandidate,
    PublicationReceipt,
)
from src.comitato.comitato_azure_retirements_v2.reports.catalog import (
    DEFAULT_REPORT_CATALOG,
)


SUBSCRIPTION_ID = "11111111-1111-1111-1111-111111111111"
UNMAPPED_SUBSCRIPTION_ID = "22222222-2222-2222-2222-222222222222"


def advisor_payload(subscription_id: str = SUBSCRIPTION_ID) -> dict[str, object]:
    return {
        "id": f"/subscriptions/{subscription_id}/providers/Microsoft.Advisor/recommendations/rec-1",
        "subscriptionId": subscription_id,
        "properties": {
            "recommendationStatus": "New",
            "recommendationTypeId": "retirement-type",
            "resourceMetadata": {
                "resourceId": f"/subscriptions/{subscription_id}/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm"
            },
        },
    }


@dataclass
class EventLog:
    events: list[str] = field(default_factory=list)


@dataclass
class RecordingRunObserver:
    events: list[RuntimeEvent] = field(default_factory=list)

    def emit(self, event: RuntimeEvent) -> None:
        self.events.append(event)


@dataclass
class FakeScopeSource:
    log: EventLog

    def resolve(self, request: RunRequest, *, run_id: str = "") -> Scope:
        self.log.events.append("scope")
        return Scope(mode="explicit", subscription_ids=(SUBSCRIPTION_ID,))


class FailingScopeSource:
    def resolve(self, request: RunRequest, *, run_id: str = "") -> Scope:
        raise ApplicationError("scope resolution failed")


@dataclass(frozen=True)
class FakeCatalog:
    identity: CatalogIdentity = CatalogIdentity(schema_version=1, sha256="d" * 64)
    subscription_ids: tuple[str, ...] = (SUBSCRIPTION_ID,)


@dataclass
class FakeCatalogSource:
    log: EventLog

    def load(self) -> FakeCatalog:
        self.log.events.append("catalog")
        return FakeCatalog()


class FakeClock:
    def now(self) -> datetime:
        return datetime(2026, 7, 30, tzinfo=timezone.utc)


class FakeRunIdFactory:
    def new_id(self) -> str:
        return "s06-empty"


@dataclass
class FakeSource:
    name: str
    log: EventLog
    complete: bool = True
    records: tuple[dict[str, str], ...] = ()

    def acquire(self, context) -> SourceAcquisition:
        self.log.events.append(self.name)
        return SourceAcquisition(
            receipt=AcquisitionReceipt(
                source=self.name,
                api_version="test-v1",
                expected_subscriptions=len(context.scope.subscription_ids),
                completed_subscriptions=(
                    len(context.scope.subscription_ids) if self.complete else 0
                ),
                pages=1,
                source_records=len(self.records),
                complete=self.complete,
            ),
            records=self.records,
            companion_records=(),
        )


@dataclass
class FakePublicationStore:
    published: list[PublicationCandidate] = field(default_factory=list)

    def publish(self, candidate: PublicationCandidate) -> PublicationReceipt:
        self.published.append(candidate)
        return PublicationReceipt(
            generation="test-generation",
            current_reference="2026/07",
        )


class RecordingCatalog:
    def __init__(self):
        self.selectors = []

    def plan(self, selector):
        self.selectors.append(selector)
        return DEFAULT_REPORT_CATALOG.plan(selector)


def build_application(
    log: EventLog,
    publication: FakePublicationStore,
    *,
    report_catalog=DEFAULT_REPORT_CATALOG,
    observer=None,
    scope_source=None,
    **source_kwargs,
):
    application_kwargs = dict(
        scope_source=scope_source or FakeScopeSource(log),
        catalog_source=FakeCatalogSource(log),
        advisor_source=FakeSource("advisor", log, **source_kwargs),
        service_health_source=FakeSource("service-health", log, **source_kwargs),
        publication_store=publication,
        clock=FakeClock(),
        run_id_factory=FakeRunIdFactory(),
        report_catalog=report_catalog,
    )
    if observer is not None:
        application_kwargs["observer"] = observer
    return RetirementsApplication(**application_kwargs)


def test_complete_empty_all_acquires_each_source_once_and_publishes_six_artifacts() -> None:
    log = EventLog()
    publication = FakePublicationStore()

    result = build_application(log, publication).run(RunRequest(ReportSelector.ALL))

    assert log.events == ["scope", "catalog", "advisor", "service-health"]
    assert result.exit_status == 0
    assert [artifact.logical_path for artifact in publication.published[0].artifacts] == [
        "01_azure_advisor_retirements_raw.tsv",
        "01_azure_advisor_retirements_raw.jsonl",
        "01_azure_service_health_advisories_raw.tsv",
        "01_azure_service_health_advisories_raw.jsonl",
        "02_azure_retirements_aggregate.tsv",
        "03_azure_retirements_slide.tsv",
    ]
    assert len(publication.published) == 1
    assert result.publication_receipt.current_reference == "2026/07"


def test_incomplete_receipt_blocks_staging() -> None:
    log = EventLog()
    publication = FakePublicationStore()

    with pytest.raises(ApplicationError, match="incomplete advisor acquisition"):
        build_application(log, publication, complete=False).run(
            RunRequest(ReportSelector.ALL)
        )

    assert publication.published == []


def test_non_empty_scripted_source_is_not_claimed_complete() -> None:
    log = EventLog()
    publication = FakePublicationStore()

    with pytest.raises(ApplicationError, match="invalid advisor raw contract"):
        build_application(
            log,
            publication,
            records=({"advisor_recommendation_id": "rec-1"},),
        ).run(RunRequest(ReportSelector.ALL))

    assert publication.published == []


def test_non_empty_raw_publication_is_allowed_after_coverage() -> None:
    log = EventLog()
    publication = FakePublicationStore()

    result = build_application(
        log, publication, records=(advisor_payload(),)
    ).run(RunRequest(ReportSelector.ADVISOR))

    assert result.exit_status == 0
    assert len(publication.published) == 1


def test_covered_advisor_selector_publishes_only_raw_pair() -> None:
    log = EventLog()
    publication = FakePublicationStore()

    result = build_application(
        log, publication, records=(advisor_payload(),)
    ).run(RunRequest(ReportSelector.ADVISOR))

    assert result.exit_status == 0
    assert [artifact.logical_path for artifact in publication.published[0].artifacts] == [
        "01_azure_advisor_retirements_raw.tsv",
        "01_azure_advisor_retirements_raw.jsonl",
    ]
    assert len(publication.published) == 1


def test_unmapped_evidence_subscription_blocks_before_staging() -> None:
    log = EventLog()
    publication = FakePublicationStore()

    with pytest.raises(ApplicationError, match="platform_mapping_unmapped_subscription"):
        build_application(
            log, publication, records=(advisor_payload(UNMAPPED_SUBSCRIPTION_ID),)
        ).run(RunRequest(ReportSelector.ADVISOR))

    assert publication.published == []


def test_application_uses_one_publish_operation() -> None:
    log = EventLog()
    publication = FakePublicationStore()

    result = build_application(log, publication).run(
        RunRequest(ReportSelector.ADVISOR)
    )

    assert len(publication.published) == 1
    assert result.publication_receipt.current_reference == "2026/07"


def test_application_asks_catalog_for_one_plan() -> None:
    log = EventLog()
    publication = FakePublicationStore()
    catalog = RecordingCatalog()
    application = build_application(log, publication, report_catalog=catalog)
    application.run(RunRequest(ReportSelector.SLIDES))
    assert catalog.selectors == [ReportSelector.SLIDES]


def test_application_emits_ordered_events_with_one_run_id() -> None:
    observer = RecordingRunObserver()
    application = build_application(
        EventLog(),
        FakePublicationStore(),
        observer=observer,
    )

    result = application.run(RunRequest(ReportSelector.ALL))

    assert result.exit_status == 0
    assert observer.events[0].event == "run_started"
    assert [event.event for event in observer.events[-2:]] == [
        "publication_completed",
        "run_completed",
    ]
    assert len({event.run_id for event in observer.events}) == 1
    assert observer.events[0].run_id == result.context.run_id


def test_application_emits_events_before_scope_failure() -> None:
    observer = RecordingRunObserver()
    application = build_application(
        EventLog(),
        FakePublicationStore(),
        observer=observer,
        scope_source=FailingScopeSource(),
    )

    with pytest.raises(ApplicationError, match="scope resolution failed"):
        application.run(RunRequest(ReportSelector.ALL))

    assert observer.events[0].event == "run_started"
    assert observer.events[0].run_id
