from datetime import date, datetime, timezone

import pytest

from src.comitato.comitato_azure_retirements_v2.application.planning import (
    build_dependency_plan,
)
from src.comitato.comitato_azure_retirements_v2.contracts.cross_artifact import (
    validate_selected_set,
)
from src.comitato.comitato_azure_retirements_v2.contracts.model import EncodedArtifact
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)


EXPECTED_PATHS = {
    ReportSelector.ALL: (
        "01_azure_advisor_retirements_raw.tsv",
        "01_azure_advisor_retirements_raw.jsonl",
        "01_azure_service_health_advisories_raw.tsv",
        "01_azure_service_health_advisories_raw.jsonl",
        "02_azure_retirements_aggregate.tsv",
        "03_azure_retirements_slide.tsv",
    ),
    ReportSelector.ADVISOR: (
        "01_azure_advisor_retirements_raw.tsv",
        "01_azure_advisor_retirements_raw.jsonl",
    ),
    ReportSelector.SERVICE_HEALTH: (
        "01_azure_service_health_advisories_raw.tsv",
        "01_azure_service_health_advisories_raw.jsonl",
    ),
    ReportSelector.AGGREGATE: ("02_azure_retirements_aggregate.tsv",),
    ReportSelector.SLIDES: ("03_azure_retirements_slide.tsv",),
}


def _context(run_id: str = "run-1", as_of_date: date = date(2026, 7, 30)) -> RunContext:
    return RunContext(
        run_id=run_id,
        as_of_date=as_of_date,
        created_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
        request=RunRequest(ReportSelector.ALL),
        scope=Scope(("11111111-1111-1111-1111-111111111111",)),
        catalog_identity=CatalogIdentity(1, "a" * 64),
        dependency_plan=DependencyPlan(("scope",)),
    )


def _artifact(path: str, *, run_id: str = "run-1", as_of_date: str = "2026-07-30") -> EncodedArtifact:
    if path.endswith(".jsonl"):
        data = (
            '{"as_of_date":"%s","raw_record_ref":"ref-1","run_id":"%s"}\n'
            % (as_of_date, run_id)
        ).encode()
        media_type = "application/x-ndjson"
    else:
        data = ("schema_version\trun_id\tas_of_date\n1\t%s\t%s\n" % (run_id, as_of_date)).encode()
        media_type = "text/tab-separated-values"
    return EncodedArtifact(path, data, 1, media_type, 1, run_id)


@pytest.mark.parametrize("selector", tuple(ReportSelector))
def test_dependency_plan_declares_exact_selected_artifact_closure(selector: ReportSelector) -> None:
    plan = build_dependency_plan(selector)

    assert plan.selected_paths == EXPECTED_PATHS[selector]


def test_all_selector_acquires_each_raw_source_once() -> None:
    plan = build_dependency_plan(ReportSelector.ALL)

    assert tuple(stage for stage in plan.stages if stage in {"advisor", "service-health"}) == (
        "advisor",
        "service-health",
    )


def test_selected_set_rejects_mixed_run_ids_and_evaluation_dates() -> None:
    artifacts = (
        _artifact(EXPECTED_PATHS[ReportSelector.ALL][0]),
        _artifact(EXPECTED_PATHS[ReportSelector.ALL][1], run_id="run-2"),
        _artifact(EXPECTED_PATHS[ReportSelector.ALL][2], as_of_date="2026-08-01"),
    )

    diagnostics = validate_selected_set(ReportSelector.ALL, artifacts, context=_context())

    assert {item.code for item in diagnostics} >= {
        "mixed_run_ids",
        "mixed_evaluation_dates",
        "missing_selected_artifact",
    }


def test_selected_set_rejects_undeclared_and_dependency_artifacts() -> None:
    artifacts = (
        _artifact("01_azure_advisor_retirements_raw.tsv"),
        _artifact("01_azure_advisor_retirements_raw.jsonl"),
        _artifact("02_azure_retirements_aggregate.tsv"),
    )

    diagnostics = validate_selected_set(ReportSelector.ADVISOR, artifacts, context=_context())

    assert {item.code for item in diagnostics} >= {
        "undeclared_artifact",
        "dependency_artifact_selected",
    }


def test_selected_set_rejects_missing_raw_companion() -> None:
    diagnostics = validate_selected_set(
        ReportSelector.ADVISOR,
        (_artifact("01_azure_advisor_retirements_raw.tsv"),),
        context=_context(),
    )

    assert any(item.code == "missing_companion_artifact" for item in diagnostics)
