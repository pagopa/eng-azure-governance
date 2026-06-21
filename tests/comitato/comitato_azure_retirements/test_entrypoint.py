from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path
from types import ModuleType

import pytest

from src.comitato.comitato_azure_retirements.libs.config import RuntimeConfig
from src.comitato.comitato_azure_retirements.libs.runtime_router import build_runtime_route


def _entrypoint_path() -> Path:
    return Path(
        "src/comitato/comitato_azure_retirements/comitato-azure-retirements.py"
    ).resolve()


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


def _load_entrypoint(monkeypatch: pytest.MonkeyPatch, module_name: str) -> ModuleType:
    script_path = _entrypoint_path()
    monkeypatch.syspath_prepend(str(script_path.parent))
    return _load_entrypoint_module(script_path, module_name)


def _runtime_config(output_root: Path) -> RuntimeConfig:
    return RuntimeConfig(
        mode="schema-only",
        workflows=["raw", "aggregate", "slide"],
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


def test_main_delegates_to_run_export_with_expected_arguments(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_entrypoint(monkeypatch, "comitato_azure_retirements_entrypoint_args")
    cfg = _runtime_config(tmp_path)
    route = build_runtime_route(cfg.workflows)

    captured: dict[str, object] = {}

    def fake_run_export(*, cfg, argv, script_path, route):  # type: ignore[no-untyped-def]
        captured["cfg"] = cfg
        captured["argv"] = argv
        captured["script_path"] = script_path
        captured["route"] = route
        return 0

    monkeypatch.setattr(module, "parse_args", lambda: cfg)
    monkeypatch.setattr(module, "build_runtime_route", lambda _workflows: route)
    monkeypatch.setattr(module, "_load_run_export", lambda: fake_run_export)
    monkeypatch.setattr(sys, "argv", ["comitato-azure-retirements.py", "--mode", "schema-only"])

    assert module.main() == 0
    assert captured["cfg"] is cfg
    assert captured["argv"] == ["comitato-azure-retirements.py", "--mode", "schema-only"]
    assert captured["script_path"] == _entrypoint_path()
    assert captured["route"] == route


def test_main_returns_non_zero_exit_code_from_runtime_runner(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_entrypoint(monkeypatch, "comitato_azure_retirements_entrypoint_exit_code")
    cfg = _runtime_config(tmp_path)
    route = build_runtime_route(cfg.workflows)

    monkeypatch.setattr(module, "parse_args", lambda: cfg)
    monkeypatch.setattr(module, "build_runtime_route", lambda _workflows: route)
    monkeypatch.setattr(module, "_load_run_export", lambda: (lambda **_: 7))

    assert module.main() == 7
