"""Diagnostics and manifest collectors."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass
class DiagnosticRow:
    run_id: str
    severity: str
    check_id: str
    source_system: str
    scope: str
    observed_count: str
    expected_count: str
    message: str
    action_required: str
    raw_context_json: str


class DiagnosticsCollector:
    def __init__(self, run_id: str) -> None:
        self._run_id = run_id
        self._rows: list[DiagnosticRow] = []

    def add(
        self,
        severity: str,
        check_id: str,
        source_system: str,
        scope: str,
        message: str,
        action_required: str,
        observed_count: int | None = None,
        expected_count: int | None = None,
        raw_context_json: str = "",
    ) -> None:
        self._rows.append(
            DiagnosticRow(
                run_id=self._run_id,
                severity=severity,
                check_id=check_id,
                source_system=source_system,
                scope=scope,
                observed_count="" if observed_count is None else str(observed_count),
                expected_count="" if expected_count is None else str(expected_count),
                message=message,
                action_required=action_required,
                raw_context_json=raw_context_json,
            )
        )

    def rows(self) -> list[dict[str, str]]:
        return [asdict(row) for row in self._rows]

    def summary(self) -> dict[str, int]:
        output = {"info": 0, "warning": 0, "error": 0}
        for row in self._rows:
            output[row.severity] = output.get(row.severity, 0) + 1
        return output


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_manifest(
    *,
    run_id: str,
    started_at_utc: str,
    finished_at_utc: str,
    as_of_date: str,
    output_dir: str,
    scope_mode: str,
    subscriptions: list[str],
    management_groups: list[str],
    query_start_time: str,
    api_versions: dict[str, str],
    counts_by_file: dict[str, int],
    counts_by_source: dict[str, int],
    diagnostic_summary: dict[str, int],
    degraded_mode: bool,
    command_line: str,
    debug_log_path: str = "",
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "started_at_utc": started_at_utc,
        "finished_at_utc": finished_at_utc,
        "as_of_date": as_of_date,
        "output_dir": output_dir,
        "scope_mode": scope_mode,
        "subscriptions": subscriptions,
        "management_groups": management_groups,
        "query_start_time": query_start_time,
        "api_versions": api_versions,
        "counts_by_file": counts_by_file,
        "counts_by_source": counts_by_source,
        "diagnostic_summary": diagnostic_summary,
        "degraded_mode": degraded_mode,
        "command_line": command_line,
        "debug_log_path": debug_log_path,
    }
