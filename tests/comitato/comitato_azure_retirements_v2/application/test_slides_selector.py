from tests.comitato.comitato_azure_retirements_v2.application.test_aggregate_selectors import (
    CatalogSource,
    Clock,
    Publication,
    RunId,
    ScopeSource,
    Source,
    SUBSCRIPTION,
)
from src.comitato.comitato_azure_retirements_v2.application.orchestration import RetirementsApplication
from src.comitato.comitato_azure_retirements_v2.domain.execution import ReportSelector, RunRequest


def test_slides_selector_publishes_only_slide_target_while_using_run_local_aggregate() -> None:
    publication = Publication()
    app = RetirementsApplication(
        scope_source=ScopeSource(),
        catalog_source=CatalogSource(),
        advisor_source=Source("advisor", ()),
        service_health_source=Source("service-health", ()),
        publication_store=publication,
        clock=Clock(),
        run_id_factory=RunId(),
    )

    app.run(RunRequest(ReportSelector.SLIDES, (SUBSCRIPTION,)))

    assert [artifact.logical_path for artifact in publication.staged[0].artifacts] == [
        "03_azure_retirements_slide.tsv",
    ]
