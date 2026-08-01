from datetime import date, datetime, timezone

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
from src.comitato.comitato_azure_retirements_v2.reports.catalog import (
    DEFAULT_REPORT_CATALOG,
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


def test_selected_set_uses_catalog_publication_paths():
    plan = DEFAULT_REPORT_CATALOG.plan(ReportSelector.SLIDES)
    assert plan.expected_paths == ("03_azure_retirements_slide.tsv",)


def test_selected_set_rejects_mixed_run_ids_and_evaluation_dates() -> None:
    artifacts = (
        _artifact(EXPECTED_PATHS[ReportSelector.ALL][0]),
        _artifact(EXPECTED_PATHS[ReportSelector.ALL][1], run_id="run-2"),
        _artifact(EXPECTED_PATHS[ReportSelector.ALL][2], as_of_date="2026-08-01"),
    )

    closure = DEFAULT_REPORT_CATALOG.plan(ReportSelector.ALL)
    diagnostics = validate_selected_set(closure, artifacts, context=_context())

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

    closure = DEFAULT_REPORT_CATALOG.plan(ReportSelector.ADVISOR)
    diagnostics = validate_selected_set(closure, artifacts, context=_context())

    assert {item.code for item in diagnostics} >= {
        "undeclared_artifact",
        "dependency_artifact_selected",
    }


def test_selected_set_rejects_missing_raw_companion() -> None:
    closure = DEFAULT_REPORT_CATALOG.plan(ReportSelector.ADVISOR)
    diagnostics = validate_selected_set(
        closure,
        (_artifact("01_azure_advisor_retirements_raw.tsv"),),
        context=_context(),
    )

    assert any(item.code == "missing_companion_artifact" for item in diagnostics)
