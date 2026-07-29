"""Path and scope helpers for Azure retirements runtime orchestration."""

from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

from .config import RuntimeConfig


def build_output_dir(root: Path, as_of_date: date) -> Path:
    return root / as_of_date.strftime("%Y") / as_of_date.strftime("%m")


def build_runtime_dir(script_path: Path, as_of_date: date) -> Path:
    repo_root = script_path.resolve().parents[3]
    return (
        repo_root
        / "tmp"
        / "comitato"
        / "comitato_azure_retirements"
        / "run"
        / as_of_date.strftime("%Y")
        / as_of_date.strftime("%m")
    )


def build_debug_log_path(
    runtime_dir: Path,
    run_id: str,
    *,
    started_at: datetime | None = None,
) -> Path:
    resolved_start = started_at or datetime.now(timezone.utc)
    timestamp_prefix = resolved_start.astimezone(timezone.utc).strftime("%Y%m%d%H%M")
    return runtime_dir / f"{timestamp_prefix}_{run_id}_debug.log"


def scope_mode(cfg: RuntimeConfig) -> str:
    if cfg.mode == "fixture":
        return "fixture"
    if cfg.mode == "schema-only":
        return "schema_only"
    if cfg.subscriptions:
        return "subscriptions"
    return "management_groups"
