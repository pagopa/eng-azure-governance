from __future__ import annotations

from datetime import date
from pathlib import Path

from src.comitato.comitato_azure_retirements.libs import runtime_runner
from src.comitato.comitato_azure_retirements.libs.diagnostics import DiagnosticsCollector
from src.comitato.comitato_azure_retirements.libs.workflow_exports import (
    AggregateBuildResult,
    SERVICE_HEALTH_SUPPLEMENTAL_FILENAME,
)


def test_default_counts_by_source_contains_expected_collectors() -> None:
    assert runtime_runner._default_counts_by_source() == {
        "advisor_metadata": 0,
        "advisor_recommendations": 0,
        "resource_graph_advisorresources": 0,
        "resource_health_events": 0,
        "resource_health_events_collected": 0,
        "resource_health_events_retained": 0,
        "resource_health_events_expired": 0,
    }


def test_platforms_source_path_resolves_source_of_truth_location() -> None:
    script_path = Path(
        "src/comitato/comitato_azure_retirements/comitato-azure-retirements.py"
    ).resolve()

    assert runtime_runner._platforms_source_path(script_path) == (
        script_path.parents[2] / "_source_of_truth" / "platforms.yaml"
    )


class _StageReporter:
    def section(self, *_args: object, **_kwargs: object) -> None:
        return None

    def step(self, *_args: object, **_kwargs: object) -> None:
        return None


class _StageLogger:
    def info(self, *_args: object, **_kwargs: object) -> None:
        return None


def test_aggregate_stage_persists_split_sources_and_returns_advisor_rows(
    monkeypatch, tmp_path: Path
) -> None:  # type: ignore[no-untyped-def]
    build_result = AggregateBuildResult(
        advisor_rows=[{"advice_type": "advisor_retirement"}],
        service_health_rows=[{"advice_type": "service_health_retirement"}],
        excluded_by_reason={},
    )
    monkeypatch.setattr(runtime_runner, "load_active_subscription_platform_map", lambda _path: {})
    monkeypatch.setattr(runtime_runner, "build_aggregate_rows", lambda **_kwargs: build_result)

    result = runtime_runner._run_aggregate_stage(
        cfg=type("Config", (), {"as_of_date": date(2026, 7, 28)})(),
        output_dir=tmp_path,
        platforms_source_path=tmp_path / "platforms.yaml",
        diagnostics=DiagnosticsCollector("run-1"),
        reporter=_StageReporter(),
        debug_logger=_StageLogger(),
        advisor_rows=[],
        service_rows=[],
        counts_by_file={},
    )

    assert result[0]["advice_type"] == "advisor_retirement"
    assert (tmp_path / runtime_runner.AGGREGATE_FILENAME).exists()
    assert (tmp_path / SERVICE_HEALTH_SUPPLEMENTAL_FILENAME).exists()
