from dataclasses import FrozenInstanceError

import pytest

from src.comitato.comitato_azure_retirements_v2.contracts import AGGREGATE_V1, SLIDES_V1
from src.comitato.comitato_azure_retirements_v2.domain.execution import ReportSelector
from src.comitato.comitato_azure_retirements_v2.reports.advisor import ADVISOR_REPORT
from src.comitato.comitato_azure_retirements_v2.reports.catalog import (
    DEFAULT_REPORT_CATALOG,
    ReportCatalog,
    SelectedReportClosure,
)
from src.comitato.comitato_azure_retirements_v2.reports.model import (
    ReportDefinition,
    StagedDecodeFailure,
)
from src.comitato.comitato_azure_retirements_v2.reports.service_health import (
    SERVICE_HEALTH_REPORT,
)
from tests.comitato.comitato_azure_retirements_v2.publication.test_empty_publication import (
    empty_candidate,
)


def _renamed_catalog() -> ReportCatalog:
    return ReportCatalog(
        (
            ReportDefinition(
                ReportSelector.ADVISOR,
                "custom-advisor",
                "advisor",
                (),
                ADVISOR_REPORT.contract,
            ),
            ReportDefinition(
                ReportSelector.SERVICE_HEALTH,
                "custom-service-health",
                "service-health",
                (),
                SERVICE_HEALTH_REPORT.contract,
            ),
            ReportDefinition(
                ReportSelector.AGGREGATE,
                "custom-aggregate",
                "aggregate",
                (ReportSelector.ADVISOR, ReportSelector.SERVICE_HEALTH),
                AGGREGATE_V1,
            ),
            ReportDefinition(
                ReportSelector.SLIDES,
                "custom-slides",
                "slides",
                (ReportSelector.AGGREGATE,),
                SLIDES_V1,
            ),
        )
    )


def test_plan_returns_one_immutable_selected_closure() -> None:
    closure = DEFAULT_REPORT_CATALOG.plan(ReportSelector.SLIDES)

    assert isinstance(closure, SelectedReportClosure)
    assert closure.expected_paths == ("03_azure_retirements_slide.tsv",)
    assert closure.owner_of("03_azure_retirements_slide.tsv").name == "slides"
    with pytest.raises(FrozenInstanceError):
        closure.selector = ReportSelector.ALL


def test_non_default_catalog_closure_preserves_custom_ownership() -> None:
    closure = _renamed_catalog().plan(ReportSelector.ALL)

    assert closure.expected_paths == DEFAULT_REPORT_CATALOG.plan(ReportSelector.ALL).expected_paths
    assert closure.owner_of("01_azure_advisor_retirements_raw.tsv").name == "custom-advisor"
    assert closure.owner_of("03_azure_retirements_slide.tsv").name == "custom-slides"


@pytest.mark.parametrize(
    ("selector", "stages", "published"),
    (
        (
            ReportSelector.ALL,
            ("scope", "catalog", "advisor", "service-health", "aggregate", "slides", "publication"),
            ("advisor", "service-health", "aggregate", "slides"),
        ),
        (
            ReportSelector.ADVISOR,
            ("scope", "catalog", "advisor", "publication"),
            ("advisor",),
        ),
        (
            ReportSelector.SERVICE_HEALTH,
            ("scope", "catalog", "service-health", "publication"),
            ("service-health",),
        ),
        (
            ReportSelector.AGGREGATE,
            ("scope", "catalog", "advisor", "service-health", "aggregate", "publication"),
            ("aggregate",),
        ),
        (
            ReportSelector.SLIDES,
            ("scope", "catalog", "advisor", "service-health", "aggregate", "slides", "publication"),
            ("slides",),
        ),
    ),
)
def test_plan_preserves_dependency_and_publication_order(selector, stages, published):
    plan = DEFAULT_REPORT_CATALOG.plan(selector)
    assert plan.stages == stages
    assert tuple(item.name for item in plan.published) == published


def test_every_declared_path_has_exactly_one_owner():
    paths = DEFAULT_REPORT_CATALOG.all_paths
    assert len(paths) == len(set(paths))
    assert tuple(DEFAULT_REPORT_CATALOG.owner_of(path).name for path in paths) == (
        "advisor",
        "advisor",
        "service-health",
        "service-health",
        "aggregate",
        "slides",
    )


def test_report_definition_verifies_staged_artifacts():
    candidate = empty_candidate()
    definition = DEFAULT_REPORT_CATALOG.owner_of(
        "01_azure_advisor_retirements_raw.tsv"
    )
    payloads = {
        item.logical_path: item.data for item in candidate.artifacts
    }

    assert definition.verify_staged_artifact(
        definition.contract.path, payloads, candidate.context
    ) == ()

    payloads[definition.contract.companion_path] = b"not-json\n"
    with pytest.raises(StagedDecodeFailure) as raised:
        definition.verify_staged_artifact(
            definition.contract.companion_path, payloads, candidate.context
        )
    assert raised.value.logical_path == definition.contract.companion_path
