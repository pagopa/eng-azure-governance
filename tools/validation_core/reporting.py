"""Deterministic operator and machine reports for validation runs."""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .events import redact
from .models import CommandEvidence, RunContext, RunReport, UnitResult

REPORT_SCHEMA_VERSION = "validation-run/v1"
RENDER_FORMATS = frozenset({"auto", "terminal", "ci", "json", "markdown"})
TERMINAL_STATUSES = frozenset(
    {"passed", "failed", "skipped", "cancelled", "incomplete"}
)
MAX_DIAGNOSTIC_LINES = 5
HOSTED_PATH_MARKERS = ("/runner/", "RUNNER_TEMP", "GITHUB_WORKSPACE")


def _safe_value(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _safe_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe_value(item) for item in value]
    if isinstance(value, str):
        return redact(value)
    return value


def _snapshot_dict(snapshot: Any) -> dict[str, Any] | None:
    if snapshot is None:
        return None
    if hasattr(snapshot, "as_dict"):
        return _safe_value(snapshot.as_dict())
    if isinstance(snapshot, Mapping):
        return _safe_value(snapshot)
    return {"value": _safe_value(snapshot)}


def _delta_dict(delta: Any, before: Any, after: Any) -> dict[str, Any] | None:
    if (
        delta is None
        and before is not None
        and after is not None
        and hasattr(before, "delta")
    ):
        delta = before.delta(after)
    if delta is None:
        return None
    if hasattr(delta, "as_dict"):
        return _safe_value(delta.as_dict())
    if isinstance(delta, Mapping):
        return _safe_value(delta)
    return {"value": _safe_value(delta)}


def _event_dict(event: Any) -> dict[str, Any]:
    if hasattr(event, "as_dict"):
        return _safe_value(event.as_dict())
    if isinstance(event, Mapping):
        return _safe_value(event)
    return {"detail": redact(str(event))}


def _command_dict(command: CommandEvidence) -> dict[str, Any]:
    return {
        "command": redact(command.command),
        "exit_code": command.exit_code,
        "stdout": redact(command.stdout),
        "stderr": redact(command.stderr),
        "duration_seconds": command.duration_seconds,
        "simulated": command.simulated,
    }


def _result_status(result: UnitResult) -> str:
    if result.status in TERMINAL_STATUSES:
        return result.status
    return "passed" if result.exit_code == 0 else "failed"


def _unit_dict(result: UnitResult) -> dict[str, Any]:
    return {
        "unit_id": result.unit.unit_id,
        "title": redact(result.unit.title),
        "status": _result_status(result),
        "exit_code": result.exit_code,
        "duration_seconds": result.duration_seconds,
        "queue_seconds": result.queue_seconds,
        "category": redact(result.category),
        "started_at": result.started_at,
        "completed_at": result.completed_at,
        "commands": [_command_dict(command) for command in result.commands],
        "artifacts": [redact(str(artifact)) for artifact in result.artifacts],
    }


def report_to_payload(report: RunReport) -> dict[str, Any]:
    """Build the single redacted JSON contract used by every projection."""

    results = tuple(report.results)
    statuses = [_result_status(result) for result in results]
    status_counts = dict(report.status_counts) or dict(Counter(statuses))
    planned_units = list(report.planned_units) or [
        result.unit.unit_id for result in results
    ]
    before = _snapshot_dict(report.repository_before)
    after = _snapshot_dict(report.repository_after)
    repository_delta = _delta_dict(
        report.repository_delta, report.repository_before, report.repository_after
    )
    artifacts = list(
        dict.fromkeys(redact(str(artifact)) for artifact in report.artifacts)
    )
    for result in results:
        for artifact in result.artifacts:
            reference = redact(str(artifact))
            if reference not in artifacts:
                artifacts.append(reference)
    branch = (after or before or {}).get("branch")
    commit = (after or before or {}).get("commit")
    clean = (after or before or {}).get("clean")
    payload: dict[str, Any] = {
        "schema_version": report.schema_version or REPORT_SCHEMA_VERSION,
        "request": redact(report.request),
        "selectors": [redact(selector) for selector in report.selectors],
        "planned_units": [redact(unit_id) for unit_id in planned_units],
        "concurrency": report.concurrency,
        "fail_fast": report.fail_fast,
        "artifact_root": _safe_value(report.artifact_root),
        "tool_versions": _safe_value(report.tool_versions),
        "branch": branch,
        "commit": commit,
        "clean": clean,
        "repository": {
            "before": before,
            "after": after,
            "delta": repository_delta,
        },
        "repository_delta": repository_delta,
        "wall_clock_seconds": report.wall_clock_seconds,
        "serial_equivalent_seconds": report.serial_equivalent_seconds,
        "queue_seconds": report.queue_seconds,
        "category_durations": _safe_value(report.category_durations),
        "timing": {
            "wall_clock_seconds": report.wall_clock_seconds,
            "serial_equivalent_seconds": report.serial_equivalent_seconds,
            "queue_seconds": report.queue_seconds,
            "category_durations": _safe_value(report.category_durations),
        },
        "status_counts": status_counts,
        "problems": [redact(problem) for problem in report.problems],
        "next_actions": [redact(action) for action in report.next_actions],
        "artifacts": artifacts,
        "units": [_unit_dict(result) for result in results],
        "events": [_event_dict(event) for event in report.events],
    }
    return _safe_value(payload)


def _select_format(output_format: str, *, compact: bool = False) -> str:
    if output_format not in RENDER_FORMATS:
        raise ValueError(f"unsupported report format: {output_format}")
    if output_format != "auto":
        return output_format
    if compact:
        return "terminal"
    if os.environ.get("GITHUB_ACTIONS", "").lower() == "true":
        return "ci"
    return "terminal" if sys.stdout.isatty() else "ci"


def _unit_category(result: Mapping[str, Any]) -> str:
    category = str(result.get("category") or "")
    if not category:
        category = str(result.get("unit_id", "")).split(":", 1)[0]
    return category.upper() or "VALIDATION"


def _display_unit_id(result: Mapping[str, Any]) -> str:
    return str(result.get("unit_id", "")).split(":", 1)[-1]


def _diagnostic_lines(result: Mapping[str, Any]) -> list[str]:
    output: list[str] = []
    for command in result.get("commands", []):
        for field in ("stdout", "stderr"):
            value = str(command.get(field, ""))
            if value.strip():
                output.extend(redact(value).splitlines())
    return [line.strip() for line in output if line.strip()][:MAX_DIAGNOSTIC_LINES]


def _extract_diagnostics(result: Mapping[str, Any]) -> list[dict[str, str]]:
    lines = _diagnostic_lines(result)
    if not lines:
        return []
    locations: list[str] = []
    for line in lines:
        terraform_location = re.search(r"\bon\s+(\S+)\s+line\s+(\d+)", line, re.I)
        if terraform_location:
            locations.append(
                f"{terraform_location.group(1)}:{terraform_location.group(2)}"
            )
        elif re.search(r"(?:^|\s)[^\s:]+:\d+(?::\d+)?(?:\b|$)", line):
            locations.append(line)
    tests = [
        line
        for line in lines
        if line.startswith("FAILED ") or re.search(r'\brun\s+"[^"]+"', line)
    ]
    causes = [
        line
        for line in lines
        if re.search(r"(?:AssertionError|Error:|Exception|failed)", line, re.I)
    ]
    expected = [line for line in lines if re.search(r"\bexpected\s*[:=]", line, re.I)]
    actual = [line for line in lines if re.search(r"\bactual\s*[:=]", line, re.I)]
    resources = [
        line
        for line in lines
        if re.search(r"\b(?:resource|aws_[a-z0-9_]+)\b", line, re.I)
    ]
    if not any((locations, tests, causes, expected, actual, resources)):
        context = (lines[:1] + lines[-11:])[:12]
    else:
        context = lines[-12:]
    diagnostic = {
        "location": locations[0] if locations else "",
        "test": tests[0] if tests else "",
        "cause": causes[0] if causes else "",
        "expected": expected[0] if expected else "",
        "actual": actual[0] if actual else "",
        "resource": resources[0] if resources else "",
        "context": "\n".join(context),
    }
    return [diagnostic]


def _rerun_command(report: RunReport, result: Mapping[str, Any]) -> str | None:
    prefix = ""
    if report.context is not None:
        prefix = str(report.context.metadata.get("rerun_prefix", "")).strip()
    request = report.request.strip()
    observed = " ".join(
        [request, prefix, str(result.get("unit_id", "")), *(_diagnostic_lines(result))]
    )
    if (
        not prefix
        or not request
        or any(marker in observed for marker in HOSTED_PATH_MARKERS)
    ):
        return None
    return f"{prefix} {request}".strip()


def _append_rerun(
    lines: list[str], report: RunReport, result: Mapping[str, Any]
) -> None:
    rerun = _rerun_command(report, result)
    if rerun is None:
        lines.append("No safe local rerun is available")
    else:
        lines.append(f"rerun: {rerun}")


def _render_compact_terminal(report: RunReport, payload: Mapping[str, Any]) -> str:
    lines: list[str] = []
    total = len(payload["units"])
    for index, result in enumerate(payload["units"], start=1):
        status = str(result["status"])
        marker = {"passed": "✅", "failed": "❌", "skipped": "⏭️", "cancelled": "⏭️"}.get(
            status, "⚠️"
        )
        line = (
            f"{marker} [{index:02d}/{total:02d}] [{_unit_category(result)}] {_display_unit_id(result)} "
            f"· {status} · {result['duration_seconds']:.2f}s"
        )
        if status == "failed":
            diagnostics = _extract_diagnostics(result)
            if diagnostics:
                line += f" · observed: {diagnostics[0]}"
            rerun = _rerun_command(report, result)
            line += (
                f" · rerun: {rerun}" if rerun else " · No safe local rerun is available"
            )
        lines.append(line)
    statuses = Counter(str(result["status"]) for result in payload["units"])
    lines.append(
        "summary: "
        f"{statuses.get('passed', 0)} passed · "
        f"{statuses.get('failed', 0)} failed · "
        f"{statuses.get('skipped', 0) + statuses.get('cancelled', 0) + statuses.get('incomplete', 0)} incomplete/skipped · "
        f"{payload['wall_clock_seconds']:.2f}s"
    )
    return "\n".join(lines)


def _render_terminal(report: RunReport, payload: Mapping[str, Any]) -> str:
    if report.context is not None and report.context.compact:
        return _render_compact_terminal(report, payload)

    lines: list[str] = []
    total = len(payload["units"])
    for index, result in enumerate(payload["units"], start=1):
        status = str(result["status"])
        marker = {"passed": "✅", "failed": "❌", "skipped": "⏭️", "cancelled": "⏭️"}.get(
            status, "⚠️"
        )
        lines.append(
            f"{marker} [{index:02d}/{total:02d}] [{_unit_category(result)}] {_display_unit_id(result)} "
            f"{result['duration_seconds']:.2f}s"
        )
        if status != "failed":
            continue
        for command in result.get("commands", []):
            lines.extend(
                [
                    "",
                    "💻 Comando",
                    f"   {command['command']} [{command['exit_code']}]",
                    "",
                    "🧪 Risultato",
                ]
            )
        diagnostics = _extract_diagnostics(result)
        for index, diagnostic in enumerate(diagnostics[:3], start=1):
            lines.extend(["", f"💥 ERRORE {index}/{min(3, len(diagnostics))}"])
            for label, prefix in (
                ("location", "📍"),
                ("test", "🧪"),
                ("resource", "🧭"),
                ("cause", "🧩"),
                ("expected", "↔️"),
                ("actual", "↔️"),
            ):
                if diagnostic[label]:
                    lines.append(f"{prefix} {diagnostic[label]}")
            if diagnostic["context"]:
                lines.extend(["🔎 Contesto", diagnostic["context"]])
        if not diagnostics:
            lines.extend(
                ["", "🔎 Contesto", "\n".join(_diagnostic_lines(result)[-12:])]
            )
        lines.extend(["", "🔁 Riesecuzione", "   "])
        _append_rerun(lines, report, result)
    statuses = Counter(str(result["status"]) for result in payload["units"])
    lines.extend(
        [
            "",
            "── SUMMARY",
            f"passed: {statuses.get('passed', 0)} · failed: {statuses.get('failed', 0)} · "
            f"skipped/incomplete: {statuses.get('skipped', 0) + statuses.get('cancelled', 0) + statuses.get('incomplete', 0)}",
            f"duration: {payload['wall_clock_seconds']:.2f}s",
        ]
    )
    return "\n".join(lines)


def _render_ci(report: RunReport, payload: Mapping[str, Any]) -> str:
    lines: list[str] = []
    for event in payload["events"]:
        unit = event.get("unit_id") or "run"
        detail = event.get("detail", "")
        lines.append(
            f"[{event.get('wall_timestamp', '')}] validation "
            f"phase={event.get('phase', '')} status={event.get('status', '')} "
            f"unit={unit} detail={detail}"
        )
    if not lines:
        for result in payload["units"]:
            lines.append(
                f"validation unit={result['unit_id']} status={result['status']} "
                f"exit_code={result['exit_code']}"
            )
    for result in payload["units"]:
        for command in result.get("commands", []):
            if command["exit_code"] == 0:
                continue
            lines.append(f"Failed command [{result['unit_id']}]: {command['command']}")
            for field in ("stdout", "stderr"):
                if command[field].strip():
                    lines.extend([f"{field}:", command[field]])
    failed = bool(payload["problems"]) or any(
        result["exit_code"] != 0 or result["status"] in {"failed", "incomplete"}
        for result in payload["units"]
    )
    lines.append(
        f"validation phase=final status={'failed' if failed else 'passed'} "
        f"wall_clock_seconds={payload['wall_clock_seconds']:.6f} "
        f"serial_equivalent_seconds={payload['serial_equivalent_seconds']:.6f}"
    )
    return "\n".join(lines)


def _render_markdown(report: RunReport, payload: Mapping[str, Any]) -> str:
    lines = [
        "# Validation report",
        "",
        f"- Request: `{payload['request']}`",
        f"- Wall-clock: `{payload['wall_clock_seconds']:.2f}s`",
        f"- Serial-equivalent: `{payload['serial_equivalent_seconds']:.2f}s`",
        f"- Queue: `{payload['queue_seconds']:.2f}s`",
        "",
        "| Unit | Status | Exit code | Duration |",
        "| --- | --- | ---: | ---: |",
    ]
    for result in payload["units"]:
        lines.append(
            f"| `{result['unit_id']}` | {result['status']} | "
            f"{result['exit_code']} | {result['duration_seconds']:.2f}s |"
        )
    lines.extend(["", "## Problems"])
    lines.extend(f"- {problem}" for problem in payload["problems"] or ["None"])
    if payload["next_actions"]:
        lines.extend(["", "## Next actions"])
        lines.extend(f"- {action}" for action in payload["next_actions"])
    return "\n".join(lines)


def render_run(report: RunReport, output_format: str = "auto") -> str:
    """Render a run as terminal, CI lines, JSON, or Markdown."""

    selected_format = _select_format(
        output_format,
        compact=bool(report.context is not None and report.context.compact),
    )
    payload = report_to_payload(report)
    if selected_format == "json":
        return json.dumps(payload, indent=2, sort_keys=True)
    if selected_format == "terminal":
        return _render_terminal(report, payload)
    if selected_format == "ci":
        return _render_ci(report, payload)
    return _render_markdown(report, payload)


def _compatibility_report(
    results: Sequence[UnitResult], context: RunContext
) -> RunReport:
    existing = getattr(results, "report", None)
    if isinstance(existing, RunReport):
        return existing
    return RunReport(
        request=str(context.metadata.get("request", "")),
        selectors=tuple(context.selectors),
        planned_units=tuple(result.unit.unit_id for result in results),
        results=tuple(results),
        context=context,
        concurrency=1,
        fail_fast=False,
        artifact_root=context.artifact_dir,
        serial_equivalent_seconds=sum(result.duration_seconds for result in results),
        wall_clock_seconds=sum(result.duration_seconds for result in results),
        queue_seconds=sum(result.queue_seconds for result in results),
    )


def render_report(results: Sequence[UnitResult], context: RunContext) -> int:
    """Keep the legacy terminal exit boundary independent of renderer health."""

    report = _compatibility_report(results, context)
    validation_exit = (
        1
        if any(
            result.exit_code != 0 or _result_status(result) in {"failed", "incomplete"}
            for result in report.results
        )
        else 0
    )
    try:
        rendered = render_run(report, "terminal")
        print(rendered)
    except Exception as error:  # rendering cannot replace validation authority
        print(f"validation renderer failure: {redact(str(error))}", file=sys.stderr)
    return validation_exit
