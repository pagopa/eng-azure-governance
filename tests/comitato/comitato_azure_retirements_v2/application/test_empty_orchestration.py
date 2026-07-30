from dataclasses import dataclass, field
from datetime import datetime, timezone

import pytest

from src.comitato.comitato_azure_retirements_v2.acquisition.model import (
    AcquisitionReceipt,
    SourceAcquisition,
)
from src.comitato.comitato_azure_retirements_v2.application.orchestration import (
    ApplicationError,
    RetirementsApplication,
)
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    ReportSelector,
    RunRequest,
    Scope,
)


SUBSCRIPTION_ID = "11111111-1111-1111-1111-111111111111"


@dataclass
class EventLog:
    events: list[str] = field(default_factory=list)


@dataclass
class FakeScopeSource:
    log: EventLog

    def resolve(self, request: RunRequest) -> Scope:
        self.log.events.append("scope")
        return Scope(mode="explicit", subscription_ids=(SUBSCRIPTION_ID,))


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
    staged: list[object] = field(default_factory=list)
    committed: list[object] = field(default_factory=list)

    def stage(self, candidate):
        self.staged.append(candidate)
        return candidate

    def commit(self, generation):
        self.committed.append(generation)
        return "committed"


def build_application(log: EventLog, publication: FakePublicationStore, **source_kwargs):
    return RetirementsApplication(
        scope_source=FakeScopeSource(log),
        catalog_source=FakeCatalogSource(log),
        advisor_source=FakeSource("advisor", log, **source_kwargs),
        service_health_source=FakeSource("service-health", log, **source_kwargs),
        publication_store=publication,
        clock=FakeClock(),
        run_id_factory=FakeRunIdFactory(),
    )


def test_complete_empty_all_acquires_each_source_once_and_publishes_six_artifacts() -> None:
    log = EventLog()
    publication = FakePublicationStore()

    result = build_application(log, publication).run(RunRequest(ReportSelector.ALL))

    assert log.events == ["scope", "catalog", "advisor", "service-health"]
    assert result.exit_status == 0
    assert [artifact.logical_path for artifact in publication.staged[0].artifacts] == [
        "01_azure_advisor_retirements_raw.tsv",
        "01_azure_advisor_retirements_raw.jsonl",
        "01_azure_service_health_advisories_raw.tsv",
        "01_azure_service_health_advisories_raw.jsonl",
        "02_azure_retirements_aggregate.tsv",
        "03_azure_retirements_slide.tsv",
    ]
    assert len(publication.committed) == 1


def test_incomplete_receipt_blocks_staging() -> None:
    log = EventLog()
    publication = FakePublicationStore()

    with pytest.raises(ApplicationError, match="incomplete advisor acquisition"):
        build_application(log, publication, complete=False).run(
            RunRequest(ReportSelector.ALL)
        )

    assert publication.staged == []
    assert publication.committed == []


def test_non_empty_scripted_source_is_not_claimed_complete() -> None:
    log = EventLog()
    publication = FakePublicationStore()

    with pytest.raises(ApplicationError, match="invalid advisor raw contract"):
        build_application(
            log,
            publication,
            records=({"advisor_recommendation_id": "rec-1"},),
        ).run(RunRequest(ReportSelector.ALL))

    assert publication.staged == []


def test_non_empty_raw_publication_waits_for_evidence_union_coverage() -> None:
    log = EventLog()
    publication = FakePublicationStore()

    with pytest.raises(ApplicationError, match="evidence-union coverage"):
        build_application(
            log,
            publication,
            records=(
                {
                    "id": "advisor-1",
                    "subscriptionId": SUBSCRIPTION_ID,
                    "properties": {"recommendationStatus": "New"},
                },
            ),
        ).run(RunRequest(ReportSelector.ADVISOR))

    assert publication.staged == []
    assert publication.committed == []
