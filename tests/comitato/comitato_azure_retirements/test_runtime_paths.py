from __future__ import annotations

from datetime import date
from pathlib import Path

from src.comitato.comitato_azure_retirements.libs.config import RuntimeConfig
from src.comitato.comitato_azure_retirements.libs.runtime_paths import (
    build_debug_log_path,
    build_output_dir,
    build_runtime_dir,
    scope_mode,
)


def _runtime_config(*, mode: str, subscriptions: list[str]) -> RuntimeConfig:
    return RuntimeConfig(
        mode=mode,
        workflows=["raw"],
        subscriptions=subscriptions,
        management_groups=[] if subscriptions else ["mg-core"],
        output_root=Path("/tmp/output"),
        as_of_date=date(2026, 6, 21),
        health_query_start=date(2025, 1, 1),
        fixture_dir=None,
        write_raw_jsonl=False,
        allow_degraded=False,
        verbose=False,
    )


def test_build_output_dir_uses_year_month_partition() -> None:
    root = Path("/tmp/exports")

    assert build_output_dir(root, date(2026, 7, 2)) == Path("/tmp/exports/2026/07")


def test_build_runtime_dir_targets_tmp_comitato_runtime_tree() -> None:
    script_path = Path(
        "src/comitato/comitato_azure_retirements/comitato-azure-retirements.py"
    ).resolve()

    runtime_dir = build_runtime_dir(script_path, date(2026, 7, 2))

    assert runtime_dir == (
        script_path.parents[3]
        / "tmp"
        / "comitato"
        / "comitato_azure_retirements"
        / "run"
        / "2026"
        / "07"
    )


def test_build_debug_log_path_appends_run_identifier() -> None:
    runtime_dir = Path("/tmp/runtime")

    assert build_debug_log_path(runtime_dir, "run-123") == Path(
        "/tmp/runtime/run-123_debug.log"
    )


def test_scope_mode_reflects_runtime_context() -> None:
    assert scope_mode(_runtime_config(mode="fixture", subscriptions=[])) == "fixture"
    assert scope_mode(_runtime_config(mode="schema-only", subscriptions=[])) == "schema_only"
    assert scope_mode(_runtime_config(mode="live", subscriptions=["sub-1"])) == "subscriptions"
    assert scope_mode(_runtime_config(mode="live", subscriptions=[])) == "management_groups"
