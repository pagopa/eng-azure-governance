from __future__ import annotations

from datetime import date

import pytest

from src.comitato.comitato_azure_retirements.libs.config import parse_args
from src.comitato.comitato_azure_retirements.libs.dates import add_calendar_months


def test_parse_args_defaults_to_live_when_scope_is_provided(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AZURE_RETIREMENTS_MODE", raising=False)
    monkeypatch.delenv("AZURE_RETIREMENTS_OUTPUT_ROOT", raising=False)
    monkeypatch.setenv("AZURE_RETIREMENTS_AS_OF_DATE", "2026-06-18")

    cfg = parse_args(["--subscriptions", "sub-1"])

    assert cfg.mode == "live"
    assert cfg.workflows == ["raw", "aggregate", "slide"]
    assert cfg.subscriptions == ["sub-1"]
    assert cfg.output_root.as_posix().endswith("/src/comitato/comitato_azure_retirements/exports")
    assert cfg.as_of_date == date(2026, 6, 18)
    assert cfg.health_query_start == add_calendar_months(date(2026, 6, 18), -18)


def test_parse_args_requires_scope_when_mode_is_implicit_live(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AZURE_RETIREMENTS_MODE", raising=False)

    with pytest.raises(SystemExit):
        parse_args([])


def test_parse_args_keeps_schema_only_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AZURE_RETIREMENTS_MODE", raising=False)

    cfg = parse_args(["--mode", "schema-only"])

    assert cfg.mode == "schema-only"


def test_parse_args_accepts_workflow_csv() -> None:
    cfg = parse_args(["--mode", "schema-only", "--workflow", "raw,slide"])

    assert cfg.workflows == ["raw", "slide"]


def test_parse_args_expands_full_workflow() -> None:
    cfg = parse_args(["--mode", "schema-only", "--workflow", "full"])

    assert cfg.workflows == ["raw", "aggregate", "slide"]


def test_parse_args_rejects_full_combined_with_other_workflows() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--mode", "schema-only", "--workflow", "full,raw"])


def test_parse_args_rejects_unsupported_workflow_value() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--mode", "schema-only", "--workflow", "raw,unknown"])


def test_parse_args_reads_boolean_env_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AZURE_RETIREMENTS_WRITE_RAW_JSONL", "true")
    monkeypatch.setenv("AZURE_RETIREMENTS_ALLOW_DEGRADED", "yes")
    monkeypatch.setenv("AZURE_RETIREMENTS_VERBOSE", "1")

    cfg = parse_args(["--mode", "schema-only"])

    assert cfg.write_raw_jsonl is True
    assert cfg.allow_degraded is True
    assert cfg.verbose is True


def test_parse_args_live_mode_requires_scope() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--mode", "live"])


def test_parse_args_fixture_mode_requires_fixture_dir() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--mode", "fixture"])


def test_parse_args_accepts_max_workers_from_cli() -> None:
    cfg = parse_args(["--mode", "schema-only", "--max-workers", "4"])

    assert cfg.max_workers == 4


def test_parse_args_reads_max_workers_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AZURE_RETIREMENTS_MAX_WORKERS", "6")

    cfg = parse_args(["--mode", "schema-only"])

    assert cfg.max_workers == 6


def test_parse_args_rejects_non_positive_max_workers() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--mode", "schema-only", "--max-workers", "0"])
