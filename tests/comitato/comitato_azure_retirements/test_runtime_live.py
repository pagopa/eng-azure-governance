from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from src.comitato.comitato_azure_retirements.libs.config import RuntimeConfig
from src.comitato.comitato_azure_retirements.libs.diagnostics import DiagnosticsCollector
from src.comitato.comitato_azure_retirements.libs import runtime_live


class _Reporter:
    def section(self, *_args, **_kwargs) -> None:
        return None

    def step(self, *_args, **_kwargs) -> None:
        return None

    def success(self, *_args, **_kwargs) -> None:
        return None

    def observe_request(self, *_args, **_kwargs) -> None:
        return None


class _ProgressCallback:
    def __call__(self, *_args, **_kwargs) -> None:
        return None

    def __enter__(self) -> _ProgressCallback:
        return self

    def __exit__(self, *_args, **_kwargs) -> None:
        return None


class _LiveReporter(_Reporter):
    def detail(self, *_args, **_kwargs) -> None:
        return None

    def mapping(self, *_args, **_kwargs) -> None:
        return None

    def warning(self, *_args, **_kwargs) -> None:
        return None

    def problem_determination_report(self, *_args, **_kwargs) -> None:
        return None

    def subscription_progress(self, *_args, **_kwargs) -> _ProgressCallback:
        return _ProgressCallback()


class _DebugLogger:
    def info(self, *_args, **_kwargs) -> None:
        return None

    def warning(self, *_args, **_kwargs) -> None:
        return None


def _runtime_config(output_root: Path) -> RuntimeConfig:
    return RuntimeConfig(
        mode="live",
        workflows=["raw"],
        subscriptions=[],
        management_groups=["mg-core"],
        output_root=output_root,
        as_of_date=date(2026, 6, 21),
        health_query_start=date(2025, 1, 1),
        fixture_dir=None,
        write_raw_jsonl=False,
        allow_degraded=False,
        verbose=False,
        max_workers=4,
    )


def test_live_mode_raises_when_scope_resolves_to_no_subscriptions(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(runtime_live, "get_management_token", lambda: "token")
    monkeypatch.setattr(runtime_live, "ArmClient", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(
        runtime_live,
        "resolve_scope_subscriptions",
        lambda *_args, **_kwargs: ([], {}),
    )

    with pytest.raises(RuntimeError, match="No subscriptions resolved"):
        runtime_live.live_mode(
            cfg=_runtime_config(tmp_path),
            run_id="run-1",
            output_dir=tmp_path,
            diagnostics=DiagnosticsCollector("run-1"),
            reporter=_Reporter(),
            debug_logger=object(),
        )


def test_live_mode_preserves_run_id_for_normalization(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: dict[str, str] = {}
    diagnostics = DiagnosticsCollector("run-preserved")

    monkeypatch.setattr(runtime_live, "get_management_token", lambda: "token")
    monkeypatch.setattr(runtime_live, "ArmClient", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(
        runtime_live,
        "resolve_scope_subscriptions",
        lambda *_args, **_kwargs: (["sub-1"], {}),
    )
    monkeypatch.setattr(runtime_live, "collect_advisor_metadata", lambda *_args, **_kwargs: ([], 1))
    monkeypatch.setattr(
        runtime_live,
        "collect_advisor_recommendations",
        lambda *_args, **_kwargs: ([], {"sub-1": 0}, []),
    )
    monkeypatch.setattr(
        runtime_live,
        "collect_advisor_resource_graph",
        lambda *_args, **_kwargs: ([], False, 0),
    )
    monkeypatch.setattr(
        runtime_live,
        "collect_events_for_subscriptions",
        lambda *_args, **_kwargs: (
            [
                {
                    "name": "9HB8-C00",
                    "properties": {
                        "eventType": "HealthAdvisory",
                        "level": "Warning",
                        "status": "Active",
                        "impactMitigationTime": "2026-03-31T13:51:10Z",
                    },
                }
            ],
            {"sub-1": 1},
            [],
        ),
    )
    monkeypatch.setattr(runtime_live, "index_metadata_with_collisions", lambda *_args, **_kwargs: ({}, {}))
    monkeypatch.setattr(runtime_live, "index_resource_graph", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(runtime_live, "build_subscription_name_map", lambda *_args, **_kwargs: {})

    def _capture_advisor_run_id(**kwargs):
        captured["advisor"] = kwargs["run_id"]
        return []

    def _capture_service_run_id(**kwargs):
        captured["service"] = kwargs["run_id"]
        captured["service_events"] = kwargs["events"]
        return []

    monkeypatch.setattr(runtime_live, "normalize_advisor_rows", _capture_advisor_run_id)
    monkeypatch.setattr(runtime_live, "normalize_service_health_rows", _capture_service_run_id)

    runtime_live.live_mode(
        cfg=_runtime_config(tmp_path),
        run_id="run-preserved",
        output_dir=tmp_path,
        diagnostics=diagnostics,
        reporter=_LiveReporter(),
        debug_logger=_DebugLogger(),
    )

    assert captured == {
        "advisor": "run-preserved",
        "service": "run-preserved",
        "service_events": [],
    }
    expired_diagnostic = next(
        row
        for row in diagnostics.rows()
        if row["check_id"] == "service_health_expired_events_filtered"
    )
    assert expired_diagnostic["observed_count"] == "1"
    assert "9HB8-C00" in expired_diagnostic["raw_context_json"]
