import pytest

from src.comitato.comitato_azure_retirements_v2.domain.execution import ReportSelector
from src.comitato.comitato_azure_retirements_v2.reports.catalog import (
    DEFAULT_REPORT_CATALOG,
)
from src.comitato.comitato_azure_retirements_v2.reports.model import (
    StagedDecodeFailure,
)
from tests.comitato.comitato_azure_retirements_v2.publication.test_empty_publication import (
    empty_candidate,
)


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
