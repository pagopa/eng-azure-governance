from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.comitato.comitato_azure_retirements_v2.acquisition.model import AcquisitionReceipt, SourceAcquisition
from src.comitato.comitato_azure_retirements_v2.application.orchestration import RetirementsApplication
from src.comitato.comitato_azure_retirements_v2.domain.execution import ReportSelector, RunRequest, Scope
from src.comitato.comitato_azure_retirements_v2.domain.platforms import PlatformAssignment, PlatformCatalogSnapshot, SubscriptionId
from src.comitato.comitato_azure_retirements_v2.publication.model import PublicationCandidate, PublicationReceipt


SUBSCRIPTION = "11111111-1111-1111-1111-111111111111"


def advisor_payload() -> dict[str, object]:
    return {
        "id": f"/subscriptions/{SUBSCRIPTION}/providers/Microsoft.Advisor/recommendations/rec-1",
        "subscriptionId": SUBSCRIPTION,
        "properties": {
            "recommendationStatus": "New",
            "recommendationTypeId": "retirement-type",
            "resourceMetadata": {"resourceId": f"/subscriptions/{SUBSCRIPTION}/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm"},
        },
    }


class ScopeSource:
    def resolve(self, request):
        return Scope((SUBSCRIPTION,), mode="explicit")


class CatalogSource:
    def load(self):
        return PlatformCatalogSnapshot(
            schema_version=1,
            sha256="a" * 64,
            assignments=(PlatformAssignment(SubscriptionId(SUBSCRIPTION), "Platform A", "Subscription A"),),
        )


@dataclass
class Source:
    name: str
    records: tuple[object, ...]

    def acquire(self, context):
        return SourceAcquisition(
            receipt=AcquisitionReceipt(self.name, "test-v1", 1, 1, 1, len(self.records), True),
            records=self.records,
        )


class Clock:
    def now(self):
        return datetime(2026, 7, 30, tzinfo=timezone.utc)


class RunId:
    def new_id(self):
        return "aggregate-run"


@dataclass
class Publication:
    staged: list[PublicationCandidate] = field(default_factory=list)

    def publish(self, candidate: PublicationCandidate) -> PublicationReceipt:
        self.staged.append(candidate)
        return PublicationReceipt(
            generation="test-generation",
            current_reference="generations/test-generation",
        )


def test_aggregate_selector_publishes_aggregate_from_run_local_raw_dependencies() -> None:
    publication = Publication()
    app = RetirementsApplication(
        scope_source=ScopeSource(),
        catalog_source=CatalogSource(),
        advisor_source=Source("advisor", (advisor_payload(),)),
        service_health_source=Source("service-health", ()),
        publication_store=publication,
        clock=Clock(),
        run_id_factory=RunId(),
    )

    app.run(RunRequest(ReportSelector.AGGREGATE))

    assert [artifact.logical_path for artifact in publication.staged[0].artifacts] == [
        "02_azure_retirements_aggregate.tsv",
    ]
    assert publication.staged[0].artifacts[0].rows == 1
