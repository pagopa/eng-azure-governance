from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from src.comitato.comitato_azure_retirements.libs.config import RuntimeConfig
from src.comitato.comitato_azure_retirements.libs.diagnostics import DiagnosticsCollector
from src.comitato.comitato_azure_retirements.libs import runtime_live
from src.comitato.comitato_azure_retirements.libs.service_health_resource_resolution import (
    ResourceEvidence,
)


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


def _runtime_config(output_root: Path, *, allow_degraded: bool = False) -> RuntimeConfig:
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
        allow_degraded=allow_degraded,
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
    monkeypatch.setattr(
        runtime_live,
        "collect_subscription_inventory",
        lambda *_args, **_kwargs: ([], False, 1),
    )
    monkeypatch.setattr(
        runtime_live,
        "collect_impacted_resources",
        lambda *_args, **_kwargs: ([], False, 1),
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


def test_live_mode_expands_events_from_advisor_resource_resolution(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: dict[str, object] = {}
    diagnostics = DiagnosticsCollector("run-resolution")
    event = {
        "name": "XTKT-BW8",
        "_subscriptionId": "sub-a",
        "properties": {
            "eventType": "HealthAdvisory",
            "eventSubType": "Retirement",
            "level": "Warning",
            "status": "Active",
            "title": "Retirement advisory",
        },
    }

    monkeypatch.setattr(runtime_live, "get_management_token", lambda: "token")
    monkeypatch.setattr(runtime_live, "ArmClient", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(runtime_live, "resolve_scope_subscriptions", lambda *_args, **_kwargs: (["sub-a", "sub-b"], {}))
    monkeypatch.setattr(runtime_live, "collect_subscription_inventory", lambda *_args, **_kwargs: ([], False, 1))
    monkeypatch.setattr(runtime_live, "collect_advisor_metadata", lambda *_args, **_kwargs: ([
        {
            "id": "rec-1",
            "sourceProperties": {"serviceRetirement": {"serviceHealth": {"trackingIds": ["XTKT-BW8"]}}},
        }
    ], 1))
    monkeypatch.setattr(runtime_live, "collect_advisor_recommendations", lambda *_args, **_kwargs: ([], {"sub-a": 0, "sub-b": 0}, []))
    monkeypatch.setattr(runtime_live, "collect_advisor_resource_graph", lambda *_args, **_kwargs: ([], False, 0))
    monkeypatch.setattr(runtime_live, "collect_events_for_subscriptions", lambda *_args, **_kwargs: ([event], {"sub-a": 1}, []))
    monkeypatch.setattr(runtime_live, "collect_impacted_resources", lambda *_args, **_kwargs: ([], False, 1))
    monkeypatch.setattr(runtime_live, "index_metadata_with_collisions", lambda *_args, **_kwargs: ({}, {}))
    monkeypatch.setattr(runtime_live, "index_resource_graph", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(runtime_live, "build_subscription_name_map", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(
        runtime_live,
        "collect_advisor_retirement_evidence",
        lambda *_args, **_kwargs: (
            [
                ResourceEvidence(
                    tracking_id="XTKT-BW8",
                    subscription_id="sub-b",
                    resource_id="/subscriptions/sub-b/resourceGroups/rg/providers/Microsoft.Web/sites/app",
                    resource_group="rg",
                    resource_type="Microsoft.Web/sites",
                    region="westeurope",
                    source="advisor_retirement_recommendation",
                    status="active",
                )
            ],
            {"xtkt-bw8": {"query_failed": False, "truncated": False, "status": "active"}},
        ),
    )
    monkeypatch.setattr(runtime_live, "event_impacted_service_regions", lambda _event: [])
    monkeypatch.setattr(runtime_live, "build_recommended_actions", lambda _event: "")
    monkeypatch.setattr(runtime_live, "normalize_advisor_rows", lambda **_kwargs: [])
    monkeypatch.setattr(
        runtime_live,
        "normalize_service_health_rows",
        lambda **kwargs: captured.update(kwargs) or [],
    )

    runtime_live.live_mode(
        cfg=_runtime_config(tmp_path),
        run_id="run-resolution",
        output_dir=tmp_path,
        diagnostics=diagnostics,
        reporter=_LiveReporter(),
        debug_logger=_DebugLogger(),
    )

    expanded_events = captured["events"]
    assert {event["_subscriptionId"] for event in expanded_events} == {"sub-a", "sub-b"}
    assert next(event for event in expanded_events if event["_subscriptionId"] == "sub-b")[
        "_resource_resolution_subscription_synthesized"
    ] is True
    resolution_diagnostic = next(
        row for row in diagnostics.rows() if row["check_id"] == "service_health_resource_resolution"
    )
    assert "sub-b" in resolution_diagnostic["raw_context_json"]


def test_live_mode_degrades_when_resource_resolution_collector_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: dict[str, object] = {}
    diagnostics = DiagnosticsCollector("run-degraded-resolution")
    event = {
        "name": "XTKT-BW8",
        "_subscriptionId": "sub-a",
        "properties": {
            "eventType": "HealthAdvisory",
            "eventSubType": "Retirement",
            "level": "Warning",
            "status": "Active",
            "title": "Retirement advisory",
        },
    }

    monkeypatch.setattr(runtime_live, "get_management_token", lambda: "token")
    monkeypatch.setattr(runtime_live, "ArmClient", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(
        runtime_live,
        "resolve_scope_subscriptions",
        lambda *_args, **_kwargs: (["sub-a"], {}),
    )
    monkeypatch.setattr(
        runtime_live,
        "collect_subscription_inventory",
        lambda *_args, **_kwargs: ([], False, 1),
    )
    monkeypatch.setattr(runtime_live, "collect_advisor_metadata", lambda *_args, **_kwargs: ([], 1))
    monkeypatch.setattr(
        runtime_live,
        "collect_advisor_recommendations",
        lambda *_args, **_kwargs: ([], {"sub-a": 0}, []),
    )
    monkeypatch.setattr(
        runtime_live,
        "collect_advisor_resource_graph",
        lambda *_args, **_kwargs: ([], False, 0),
    )
    monkeypatch.setattr(
        runtime_live,
        "collect_events_for_subscriptions",
        lambda *_args, **_kwargs: ([event], {"sub-a": 1}, []),
    )
    monkeypatch.setattr(
        runtime_live,
        "collect_impacted_resources",
        lambda *_args, **_kwargs: ([], False, 1),
    )
    monkeypatch.setattr(runtime_live, "index_metadata_with_collisions", lambda *_args, **_kwargs: ({}, {}))
    monkeypatch.setattr(runtime_live, "index_resource_graph", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(runtime_live, "build_subscription_name_map", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(
        runtime_live,
        "collect_advisor_retirement_evidence",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("ARG unavailable")),
    )
    monkeypatch.setattr(runtime_live, "event_impacted_service_regions", lambda _event: [])
    monkeypatch.setattr(runtime_live, "build_recommended_actions", lambda _event: "")
    monkeypatch.setattr(runtime_live, "normalize_advisor_rows", lambda **_kwargs: [])
    monkeypatch.setattr(
        runtime_live,
        "normalize_service_health_rows",
        lambda **kwargs: captured.update(kwargs) or [],
    )

    runtime_live.live_mode(
        cfg=_runtime_config(tmp_path, allow_degraded=True),
        run_id="run-degraded-resolution",
        output_dir=tmp_path,
        diagnostics=diagnostics,
        reporter=_LiveReporter(),
        debug_logger=_DebugLogger(),
    )

    assert captured["events"] == [event]
    resolution_diagnostic = next(
        row
        for row in diagnostics.rows()
        if row["check_id"] == "service_health_resource_resolution"
    )
    assert resolution_diagnostic["severity"] == "warning"
    assert "query_failed" in resolution_diagnostic["raw_context_json"]
