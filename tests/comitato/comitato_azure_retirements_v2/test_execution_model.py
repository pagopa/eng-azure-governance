from datetime import date, datetime, timezone

import pytest

from src.comitato.comitato_azure_retirements_v2.domain.diagnostics import (
    Diagnostic,
    sort_diagnostics,
)
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)


def test_run_context_rejects_naive_created_at() -> None:
    request = RunRequest(selector=ReportSelector.ALL)
    scope = Scope(subscription_ids=())

    with pytest.raises(ValueError, match="created_at must be UTC-aware"):
        RunContext(
            run_id="run-1",
            as_of_date=date(2026, 7, 30),
            created_at=datetime(2026, 7, 30),
            request=request,
            scope=scope,
            catalog_identity=CatalogIdentity(schema_version=1, sha256="a" * 64),
            dependency_plan=DependencyPlan(stages=("scope",)),
        )


def test_run_context_accepts_utc_created_at() -> None:
    context = RunContext(
        run_id="run-1",
        as_of_date=date(2026, 7, 30),
        created_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
        request=RunRequest(selector=ReportSelector.ALL),
        scope=Scope(subscription_ids=()),
        catalog_identity=CatalogIdentity(schema_version=1, sha256="b" * 64),
        dependency_plan=DependencyPlan(stages=("scope",)),
    )

    assert context.created_at.tzinfo is timezone.utc


def test_diagnostics_have_deterministic_order() -> None:
    diagnostics = (
        Diagnostic(
            severity="error",
            code="z_code",
            stage="validation",
            report="all",
            run_id="run-1",
            subscription_id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            record_ref="record-2",
            artifact="02-aggregate.tsv",
            message="second",
        ),
        Diagnostic(
            severity="error",
            code="a_code",
            stage="acquisition",
            report="all",
            run_id="run-1",
            subscription_id="",
            record_ref="",
            artifact="",
            message="first",
        ),
    )

    assert [item.code for item in sort_diagnostics(diagnostics)] == [
        "a_code",
        "z_code",
    ]
