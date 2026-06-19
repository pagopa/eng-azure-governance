from __future__ import annotations

import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from types import ModuleType

import pytest

from src.comitato.comitato_azure_retirements.libs.config import RuntimeConfig


def _load_entrypoint_module(script_path: Path, module_name: str) -> ModuleType:
    if module_name in sys.modules:
        del sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, script_path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _entrypoint_path() -> Path:
    return Path("src/comitato/comitato_azure_retirements/comitato-azure-retirements.py").resolve()


def _load_entrypoint(monkeypatch: pytest.MonkeyPatch, module_name: str) -> ModuleType:
    script_path = _entrypoint_path()
    monkeypatch.syspath_prepend(str(script_path.parent))
    return _load_entrypoint_module(script_path, module_name)


def _runtime_config(
    output_root: Path,
    *,
    mode: str = "schema-only",
    subscriptions: list[str] | None = None,
    management_groups: list[str] | None = None,
    fixture_dir: Path | None = None,
) -> RuntimeConfig:
    return RuntimeConfig(
        mode=mode,
        subscriptions=subscriptions or [],
        management_groups=management_groups or [],
        output_root=output_root,
        as_of_date=date(2026, 6, 18),
        health_query_start=date(2025, 1, 1),
        fixture_dir=fixture_dir,
        write_raw_jsonl=False,
        allow_degraded=False,
        verbose=False,
    )


def _write_json_payload(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_main_fails_when_error_diagnostic_exists(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_entrypoint(monkeypatch, "comitato_azure_retirements_entrypoint_error")
    monkeypatch.setattr(module, "parse_args", lambda: _runtime_config(tmp_path))

    def fake_schema_only(*, cfg, run_id, output_dir, diagnostics):  # type: ignore[no-untyped-def]
        diagnostics.add(
            severity="error",
            check_id="forced_error",
            source_system="global",
            scope="global",
            message="forced test error",
            action_required="fix test fixture",
        )
        counts_by_source = {
            "advisor_metadata": 0,
            "advisor_recommendations": 0,
            "resource_graph_advisorresources": 0,
            "resource_health_events": 0,
        }
        counts_by_file = {
            "azure_advisor_retirements_aggregate.tsv": 0,
            "azure_retirements_run_diagnostics.tsv": 1,
        }
        return [], [], counts_by_source, counts_by_file

    monkeypatch.setattr(module, "_schema_only", fake_schema_only)
    monkeypatch.setattr(module, "write_tsv", lambda *args, **kwargs: None)
    monkeypatch.setattr(module, "write_json", lambda *args, **kwargs: None)

    assert module.main() == 1


def test_main_succeeds_when_diagnostics_have_no_errors(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_entrypoint(monkeypatch, "comitato_azure_retirements_entrypoint_success")
    monkeypatch.setattr(module, "parse_args", lambda: _runtime_config(tmp_path))

    def fake_schema_only(*, cfg, run_id, output_dir, diagnostics):  # type: ignore[no-untyped-def]
        diagnostics.add(
            severity="warning",
            check_id="forced_warning",
            source_system="global",
            scope="global",
            message="forced warning",
            action_required="none",
        )
        counts_by_source = {
            "advisor_metadata": 0,
            "advisor_recommendations": 0,
            "resource_graph_advisorresources": 0,
            "resource_health_events": 0,
        }
        counts_by_file = {
            "azure_advisor_retirements_aggregate.tsv": 0,
            "azure_retirements_run_diagnostics.tsv": 1,
        }
        return [], [], counts_by_source, counts_by_file

    monkeypatch.setattr(module, "_schema_only", fake_schema_only)
    monkeypatch.setattr(module, "write_tsv", lambda *args, **kwargs: None)
    monkeypatch.setattr(module, "write_json", lambda *args, **kwargs: None)

    assert module.main() == 0


def test_build_output_dir_uses_year_and_month(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_entrypoint(monkeypatch, "comitato_azure_retirements_output_dir")

    output_dir = module._build_output_dir(tmp_path, date(2026, 6, 18))

    assert output_dir == tmp_path / "2026" / "06"


def test_build_runtime_dir_uses_repo_tmp_tree(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_entrypoint(monkeypatch, "comitato_azure_retirements_runtime_dir")

    runtime_dir = module._build_runtime_dir(date(2026, 6, 18))

    assert runtime_dir == Path("tmp/comitato/comitato_azure_retirements/run/2026/06").resolve()


def test_build_debug_log_path_uses_run_id(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_entrypoint(monkeypatch, "comitato_azure_retirements_debug_log_path")

    debug_log_path = module._build_debug_log_path(tmp_path, "azure-retirements-run-1")

    assert debug_log_path == tmp_path / "azure-retirements-run-1_debug.log"


def test_scope_mode_handles_fixture_schema_and_live_scope(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_entrypoint(monkeypatch, "comitato_azure_retirements_scope_mode")

    fixture_cfg = _runtime_config(tmp_path, mode="fixture", fixture_dir=tmp_path / "fixtures")
    schema_cfg = _runtime_config(tmp_path, mode="schema-only")
    live_subscriptions_cfg = _runtime_config(tmp_path, mode="live", subscriptions=["sub-1"])
    live_management_groups_cfg = _runtime_config(tmp_path, mode="live", management_groups=["mg-1"])

    assert module._scope_mode(fixture_cfg) == "fixture"
    assert module._scope_mode(schema_cfg) == "schema_only"
    assert module._scope_mode(live_subscriptions_cfg) == "subscriptions"
    assert module._scope_mode(live_management_groups_cfg) == "management_groups"


def test_load_fixture_supports_list_and_value_payloads(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_entrypoint(monkeypatch, "comitato_azure_retirements_load_fixture")

    missing = tmp_path / "missing.json"
    list_payload = tmp_path / "list_payload.json"
    value_payload = tmp_path / "value_payload.json"
    invalid_payload = tmp_path / "invalid_payload.json"

    _write_json_payload(list_payload, [{"id": "row-list"}])
    _write_json_payload(value_payload, {"value": [{"id": "row-value"}]})
    _write_json_payload(invalid_payload, {"items": [{"id": "row-invalid"}]})

    assert module._load_fixture(missing) == []
    assert module._load_fixture(list_payload) == [{"id": "row-list"}]
    assert module._load_fixture(value_payload) == [{"id": "row-value"}]
    assert module._load_fixture(invalid_payload) == []


def test_schema_only_returns_empty_rows_and_info_diagnostic(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_entrypoint(monkeypatch, "comitato_azure_retirements_schema_only")
    diagnostics = module.DiagnosticsCollector("run-1")

    advisor_rows, service_rows, counts_by_source, counts_by_file = module._schema_only(
        cfg=_runtime_config(tmp_path, mode="schema-only"),
        run_id="run-1",
        output_dir=tmp_path,
        diagnostics=diagnostics,
    )

    assert advisor_rows == []
    assert service_rows == []
    assert counts_by_source == {
        "advisor_metadata": 0,
        "advisor_recommendations": 0,
        "resource_graph_advisorresources": 0,
        "resource_health_events": 0,
    }
    assert counts_by_file == {
        "azure_advisor_retirements_aggregate.tsv": 0,
        "azure_service_health_advisories_aggregate.tsv": 0,
        "azure_retirements_run_diagnostics.tsv": 1,
    }

    diagnostic_rows = diagnostics.rows()
    assert len(diagnostic_rows) == 1
    assert diagnostic_rows[0]["check_id"] == "schema_only_mode"


def test_live_empty_output_guardrails_error_when_source_rows_exist(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_entrypoint(monkeypatch, "comitato_azure_retirements_live_guardrail_error")
    diagnostics = module.DiagnosticsCollector("run-1")

    module._add_live_empty_output_diagnostics(
        diagnostics=diagnostics,
        reporter=module.ExecutionReporter(verbose=False),
        advisor_rows=[],
        service_rows=[],
        counts_by_source={
            "advisor_metadata": 1,
            "advisor_recommendations": 1,
            "resource_graph_advisorresources": 1,
            "resource_health_events": 1,
        },
    )

    assert diagnostics.summary()["error"] == 2
    assert {row["check_id"] for row in diagnostics.rows()} == {
        "advisor_rows_empty",
        "service_rows_empty",
    }


def test_live_empty_output_guardrails_warn_when_source_rows_are_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_entrypoint(monkeypatch, "comitato_azure_retirements_live_guardrail_warning")
    diagnostics = module.DiagnosticsCollector("run-1")

    module._add_live_empty_output_diagnostics(
        diagnostics=diagnostics,
        reporter=module.ExecutionReporter(verbose=False),
        advisor_rows=[],
        service_rows=[],
        counts_by_source={
            "advisor_metadata": 0,
            "advisor_recommendations": 0,
            "resource_graph_advisorresources": 0,
            "resource_health_events": 0,
        },
    )

    assert diagnostics.summary()["warning"] == 2
    assert diagnostics.summary()["error"] == 0


def test_fixture_mode_reads_files_and_builds_outputs(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_entrypoint(monkeypatch, "comitato_azure_retirements_fixture_mode")
    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()

    recommendation_resource_id = (
        "/subscriptions/sub-1/resourceGroups/rg-test/providers/Microsoft.Storage/storageAccounts/storage01"
    )

    _write_json_payload(
        fixture_dir / "advisor_metadata.json",
        [
            {
                "id": "metadata-1",
                "properties": {
                    "sourceProperties": {
                        "serviceRetirement": {
                            "serviceId": "rec-type-1",
                            "retirementFeatureName": "Storage Feature",
                            "retirementDate": "2026-12-31",
                        }
                    },
                    "resourceMetadata": {"singular": "Storage Account"},
                    "learnMoreLink": "https://example.com/metadata",
                },
            }
        ],
    )
    _write_json_payload(
        fixture_dir / "advisor_recommendations.json",
        [
            {
                "id": "recommendation-1",
                "_subscriptionId": "sub-1",
                "properties": {
                    "recommendationTypeId": "rec-type-1",
                    "resourceMetadata": {"resourceId": recommendation_resource_id},
                    "description": "Retirement detected",
                },
            }
        ],
    )
    _write_json_payload(
        fixture_dir / "advisor_resource_graph.json",
        [
            {
                "ServiceID": "rec-type-1",
                "resourceId": recommendation_resource_id.lower(),
                "subscriptionName": "Subscription One",
                "resourceGroup": "rg-test",
                "type": "microsoft.storage/storageaccounts",
                "location": "westeurope",
                "name": "storage01",
                "platformState": "New",
                "tags": {"env": "prod"},
            }
        ],
    )
    _write_json_payload(
        fixture_dir / "service_health_events.json",
        [
            {
                "id": "/subscriptions/sub-1/providers/Microsoft.ResourceHealth/events/event-1",
                "name": "event-1",
                "_subscriptionId": "sub-1",
                "properties": {
                    "eventType": "HealthAdvisory",
                    "level": "Warning",
                    "status": "Active",
                    "title": "Planned maintenance",
                    "summary": "Service maintenance event",
                    "lastUpdateTime": "2026-06-17T10:00:00Z",
                    "impact": {
                        "impactedService": [{"serviceName": "Storage", "serviceGuid": "guid-1"}],
                        "impactedRegion": [{"regionName": "westeurope"}],
                    },
                    "recommendedActions": [{"actionText": "Review mitigation plan"}],
                },
            }
        ],
    )
    _write_json_payload(
        fixture_dir / "subscriptions.json",
        [{"subscriptionId": "sub-1", "subscriptionName": "Subscription One"}],
    )

    diagnostics = module.DiagnosticsCollector("run-1")

    advisor_rows, service_rows, counts_by_source, counts_by_file, advisor_raw, service_raw = module._fixture_mode(
        cfg=_runtime_config(
            tmp_path,
            mode="fixture",
            fixture_dir=fixture_dir,
            subscriptions=["sub-1"],
        ),
        run_id="run-1",
        output_dir=tmp_path,
        diagnostics=diagnostics,
    )

    assert len(advisor_rows) == 1
    assert len(service_rows) == 1
    assert counts_by_source == {
        "advisor_metadata": 1,
        "advisor_recommendations": 1,
        "resource_graph_advisorresources": 1,
        "resource_health_events": 1,
    }
    assert counts_by_file["azure_advisor_retirements_aggregate.tsv"] == 1
    assert counts_by_file["azure_service_health_advisories_aggregate.tsv"] == 1
    assert counts_by_file["azure_retirements_run_diagnostics.tsv"] == 1

    assert {item["kind"] for item in advisor_raw} == {"advisor_metadata", "advisor_recommendation"}
    assert {item["kind"] for item in service_raw} == {"service_health_event"}

    diagnostic_rows = diagnostics.rows()
    assert len(diagnostic_rows) == 1
    assert diagnostic_rows[0]["check_id"] == "fixture_mode"


def test_main_writes_runtime_failure_diagnostic_on_unhandled_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_entrypoint(monkeypatch, "comitato_azure_retirements_runtime_failure")
    monkeypatch.setattr(module, "parse_args", lambda: _runtime_config(tmp_path))

    def fake_schema_only(*, cfg, run_id, output_dir, diagnostics):  # type: ignore[no-untyped-def]
        raise RuntimeError("forced runtime failure")

    writes: dict[str, list[dict[str, str]]] = {}

    def fake_write_tsv(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
        del headers
        writes[path.name] = rows

    monkeypatch.setattr(module, "_schema_only", fake_schema_only)
    monkeypatch.setattr(module, "write_tsv", fake_write_tsv)

    assert module.main() == 1
    assert "azure_retirements_run_diagnostics.tsv" in writes
    assert any(
        row["check_id"] == "runtime_failure"
        for row in writes["azure_retirements_run_diagnostics.tsv"]
    )


def test_main_writes_runtime_artifacts_under_tmp_and_service_health_aggregate(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_entrypoint(monkeypatch, "comitato_azure_retirements_runtime_paths")
    monkeypatch.setattr(module, "parse_args", lambda: _runtime_config(tmp_path))

    tsv_paths: list[Path] = []
    json_paths: list[Path] = []

    def fake_write_tsv(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
        del headers, rows
        tsv_paths.append(path)

    def fake_write_json(path: Path, payload: object) -> None:
        del payload
        json_paths.append(path)

    monkeypatch.setattr(module, "write_tsv", fake_write_tsv)
    monkeypatch.setattr(module, "write_json", fake_write_json)

    assert module.main() == 0

    tsv_names = {path.name for path in tsv_paths}
    assert "azure_advisor_retirements_aggregate.tsv" in tsv_names
    assert "azure_service_health_advisories_aggregate.tsv" in tsv_names
    assert "azure_retirements_run_diagnostics.tsv" in tsv_names

    advisor_path = next(path for path in tsv_paths if path.name == "azure_advisor_retirements_aggregate.tsv")
    service_health_path = next(
        path for path in tsv_paths if path.name == "azure_service_health_advisories_aggregate.tsv"
    )
    diagnostics_path = next(path for path in tsv_paths if path.name == "azure_retirements_run_diagnostics.tsv")
    manifest_path = next(path for path in json_paths if path.name == "azure_retirements_run_manifest.json")

    assert advisor_path == tmp_path / "2026" / "06" / "azure_advisor_retirements_aggregate.tsv"
    assert service_health_path == tmp_path / "2026" / "06" / "azure_service_health_advisories_aggregate.tsv"
    assert diagnostics_path == Path("tmp/comitato/comitato_azure_retirements/run/2026/06/azure_retirements_run_diagnostics.tsv").resolve()
    assert manifest_path == Path("tmp/comitato/comitato_azure_retirements/run/2026/06/azure_retirements_run_manifest.json").resolve()
