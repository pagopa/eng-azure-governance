from pathlib import Path

import pytest

from src.comitato.comitato_azure_retirements_v2.application.orchestration_errors import ApplicationError
from src.comitato.comitato_azure_retirements_v2.publication.model import PublicationError
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


class PublishProbe:
    def __init__(self, path: Path, fail: bool = False) -> None:
        self.path = path
        self.fail = fail

    def publish(self, candidate):
        assert not self.path.exists()
        if self.fail:
            raise PublicationError("publication failed")
        return type("Receipt", (), {"generation": "2026/07", "current_reference": "2026/07"})()


def _committee_app(path: Path | None, publication):
    return RetirementsApplication(
        scope_source=ScopeSource(),
        catalog_source=CatalogSource(),
        advisor_source=Source("advisor", ()),
        service_health_source=Source("service-health", ()),
        publication_store=publication,
        clock=Clock(),
        run_id_factory=RunId(),
        committee_yaml_path=path,
    )


def test_committee_yaml_is_written_only_after_publish_returns(tmp_path: Path) -> None:
    path = tmp_path / "committee.yaml"
    _committee_app(path, PublishProbe(path)).run(RunRequest(ReportSelector.SLIDES, (SUBSCRIPTION,)))
    assert path.is_file()


def test_committee_yaml_is_not_written_when_publication_fails(tmp_path: Path) -> None:
    path = tmp_path / "committee.yaml"
    with pytest.raises(ApplicationError, match="publication failed"):
        _committee_app(path, PublishProbe(path, fail=True)).run(
            RunRequest(ReportSelector.SLIDES, (SUBSCRIPTION,))
        )
    assert not path.exists()


def test_application_without_committee_path_does_not_access_yaml(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src.comitato.comitato_azure_retirements_v2.domain import committee

    def fail(*args, **kwargs):
        raise AssertionError("committee YAML should not be accessed")

    monkeypatch.setattr(committee, "load", fail)
    monkeypatch.setattr(committee, "write", fail)
    _committee_app(None, PublishProbe(tmp_path / "unused.yaml")).run(
        RunRequest(ReportSelector.SLIDES, (SUBSCRIPTION,))
    )
