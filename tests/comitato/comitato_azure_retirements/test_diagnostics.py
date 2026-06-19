from __future__ import annotations

from src.comitato.comitato_azure_retirements.libs.diagnostics import (
    DiagnosticsCollector,
    build_manifest,
)


def test_diagnostics_summary_counts_by_severity() -> None:
    diagnostics = DiagnosticsCollector("run-1")
    diagnostics.add("info", "check-a", "global", "scope-a", "message", "none")
    diagnostics.add("warning", "check-b", "global", "scope-b", "message", "none")
    diagnostics.add("error", "check-c", "global", "scope-c", "message", "none")

    assert diagnostics.summary() == {"info": 1, "warning": 1, "error": 1}
    assert diagnostics.rows()[0]["run_id"] == "run-1"


def test_build_manifest_preserves_runtime_summary() -> None:
    manifest = build_manifest(
        run_id="run-1",
        started_at_utc="2026-06-18T08:00:00Z",
        finished_at_utc="2026-06-18T08:05:00Z",
        as_of_date="2026-06-18",
        output_dir="/tmp/output",
        scope_mode="subscriptions",
        subscriptions=["sub-1"],
        management_groups=["mg-1"],
        query_start_time="2025-01-01",
        api_versions={"resource_health_events": "2025-05-01"},
        counts_by_file={"a.tsv": 1},
        counts_by_source={"service_health": 2},
        diagnostic_summary={"info": 1, "warning": 0, "error": 0},
        degraded_mode=False,
        command_line="python tool.py",
    )

    assert manifest["run_id"] == "run-1"
    assert manifest["counts_by_source"]["service_health"] == 2
    assert manifest["diagnostic_summary"]["info"] == 1
