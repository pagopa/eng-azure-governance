from __future__ import annotations

import importlib.util
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


def _runtime_config(output_root: Path) -> RuntimeConfig:
    return RuntimeConfig(
        mode="schema-only",
        subscriptions=[],
        management_groups=[],
        output_root=output_root,
        as_of_date=date(2026, 6, 18),
        health_query_start=date(2025, 1, 1),
        fixture_dir=None,
        write_raw_jsonl=False,
        allow_degraded=False,
        verbose=False,
    )


def test_main_fails_when_error_diagnostic_exists(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    script_path = Path("src/comitato/comitato_azure_retirements/comitato-azure-retirements.py").resolve()
    monkeypatch.syspath_prepend(str(script_path.parent))

    module = _load_entrypoint_module(script_path, "comitato_azure_retirements_entrypoint_error")
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
            "azure_service_health_advisories_aggregate.tsv": 0,
            "azure_retirements_run_diagnostics.tsv": 1,
        }
        return [], [], counts_by_source, counts_by_file

    monkeypatch.setattr(module, "_schema_only", fake_schema_only)
    monkeypatch.setattr(module, "write_tsv", lambda *args, **kwargs: None)
    monkeypatch.setattr(module, "write_json", lambda *args, **kwargs: None)

    assert module.main() == 1


def test_main_succeeds_when_diagnostics_have_no_errors(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    script_path = Path("src/comitato/comitato_azure_retirements/comitato-azure-retirements.py").resolve()
    monkeypatch.syspath_prepend(str(script_path.parent))

    module = _load_entrypoint_module(script_path, "comitato_azure_retirements_entrypoint_success")
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
            "azure_service_health_advisories_aggregate.tsv": 0,
            "azure_retirements_run_diagnostics.tsv": 1,
        }
        return [], [], counts_by_source, counts_by_file

    monkeypatch.setattr(module, "_schema_only", fake_schema_only)
    monkeypatch.setattr(module, "write_tsv", lambda *args, **kwargs: None)
    monkeypatch.setattr(module, "write_json", lambda *args, **kwargs: None)

    assert module.main() == 0
