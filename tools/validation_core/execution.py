"""Subprocess execution, bounded scheduling, and evidence capture."""

from __future__ import annotations

import contextvars
import os
import re
import shlex
import subprocess
import time
from collections import Counter
from collections.abc import Mapping, Sequence
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import replace
from pathlib import Path
from typing import Any

from .events import EventSink, redact
from .models import CommandEvidence, RunContext, RunReport, UnitResult, ValidationUnit

MAX_OUTPUT_PREVIEW = 8000


class _EvidenceBuffer:
    def __init__(self) -> None:
        self.commands: list[CommandEvidence] = []
        self.artifacts: list[str] = []


_ACTIVE_BUFFER: contextvars.ContextVar[_EvidenceBuffer | None] = contextvars.ContextVar(
    "validation_evidence", default=None
)


def _preview(value: str) -> str:
    bounded = redact(value)
    if len(bounded) <= MAX_OUTPUT_PREVIEW:
        return bounded
    head = MAX_OUTPUT_PREVIEW // 2
    tail = MAX_OUTPUT_PREVIEW - head - 3
    return bounded[:head] + "..." + bounded[-tail:]


def _render_command(args: Sequence[str | Path]) -> str:
    return _preview(shlex.join(str(arg) for arg in args))


def _event_sink(context: RunContext) -> Any | None:
    sink = context.event_sink
    return sink if sink is not None and hasattr(sink, "emit") else None


def _emit(
    context: RunContext,
    *,
    phase: str,
    unit_id: str | None,
    status: str,
    detail: str = "",
    metadata: Mapping[str, str] | None = None,
):
    sink = _event_sink(context)
    if sink is None:
        return None
    return sink.emit(
        phase=phase,
        unit_id=unit_id,
        status=status,
        detail=detail,
        metadata=metadata or {},
    )


def _context_unit_id(context: RunContext) -> str | None:
    unit_id = context.metadata.get("unit_id")
    return str(unit_id) if unit_id else None


def run_command(
    context: RunContext,
    args: Sequence[str | Path],
    *,
    env: Mapping[str, str] | None = None,
    cwd: Path | None = None,
) -> int:
    """Run one command and attach bounded, redacted evidence to the active unit."""

    command = _render_command(args)
    unit_id = _context_unit_id(context)
    _emit(
        context,
        phase="command-start",
        unit_id=unit_id,
        status="running",
        detail=command,
    )
    started = time.monotonic()
    if context.dry_run:
        completed = CommandEvidence(command, 0, duration_seconds=0.0, simulated=True)
        buffer = _ACTIVE_BUFFER.get()
        if buffer is not None:
            buffer.commands.append(completed)
        _emit(
            context,
            phase="command-complete",
            unit_id=unit_id,
            status="passed",
            detail=f"{command} exit_code=0 simulated",
        )
        return 0

    merged_env = os.environ.copy()
    if env:
        merged_env.update({str(key): str(value) for key, value in env.items()})
    completed_process = subprocess.run(
        [str(arg) for arg in args],
        cwd=str(cwd or context.root),
        env=merged_env,
        capture_output=True,
        text=True,
        check=False,
    )
    exit_code = completed_process.returncode
    if exit_code < 0:
        exit_code = 128 + abs(exit_code)
    stdout = _preview(completed_process.stdout)
    stderr = _preview(completed_process.stderr)
    duration = time.monotonic() - started
    evidence = CommandEvidence(
        command=command,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        duration_seconds=duration,
    )
    buffer = _ACTIVE_BUFFER.get()
    if buffer is not None:
        buffer.commands.append(evidence)
    detail_parts = [command, f"exit_code={exit_code}"]
    if stdout.strip():
        detail_parts.append(f"stdout={stdout}")
    if stderr.strip():
        detail_parts.append(f"stderr={stderr}")
    _emit(
        context,
        phase="command-complete",
        unit_id=unit_id,
        status="passed" if exit_code == 0 else "failed",
        detail=" ".join(detail_parts),
    )
    return exit_code


def _unit_tmp_dir(root: Path, unit_id: str, index: int) -> Path:
    safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "-", unit_id).strip(".") or "unit"
    path = root / f"{index:03d}-{safe_id}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _run_one(
    unit: ValidationUnit,
    context: RunContext,
    index: int,
    queued_at: float,
) -> UnitResult:
    unit_context = replace(
        context,
        tmp_dir=_unit_tmp_dir(context.tmp_dir, unit.unit_id, index),
        metadata={
            **context.metadata,
            "unit_id": unit.unit_id,
            "unit_title": unit.title,
        },
    )
    buffer = _EvidenceBuffer()
    token = _ACTIVE_BUFFER.set(buffer)
    started = time.monotonic()
    running_event = _emit(
        unit_context,
        phase="running",
        unit_id=unit.unit_id,
        status="running",
        detail=unit.title,
    )
    # An initial heartbeat guarantees that even short units have an observable
    # active interval; the scheduler emits additional heartbeats while waiting.
    _emit(
        unit_context,
        phase="heartbeat",
        unit_id=unit.unit_id,
        status="running",
        detail="unit active",
    )
    exit_code = 1
    try:
        try:
            exit_code = int(unit.run(unit_context))
        except BaseException as error:  # a unit must not hide sibling failures
            exit_code = 1
            buffer.commands.append(
                CommandEvidence(
                    command=f"{unit.unit_id}: {type(error).__name__}",
                    exit_code=1,
                    stderr=_preview(str(error)),
                    duration_seconds=0.0,
                )
            )
    finally:
        _ACTIVE_BUFFER.reset(token)
    completed_at = time.monotonic()
    status = "passed" if exit_code == 0 else "failed"
    return UnitResult(
        unit,
        exit_code,
        completed_at - started,
        tuple(buffer.commands),
        tuple(buffer.artifacts),
        status=status,
        queue_seconds=max(0.0, started - queued_at),
        category=str(context.metadata.get("category", "")),
        started_at=running_event.wall_timestamp if running_event is not None else "",
        completed_at="",
    )


def _terminal_result(
    unit: ValidationUnit,
    context: RunContext,
    *,
    status: str,
    detail: str,
) -> UnitResult:
    _emit(
        context,
        phase="unit-complete",
        unit_id=unit.unit_id,
        status=status,
        detail=detail,
    )
    return UnitResult(
        unit,
        0,
        0.0,
        status=status,
        category=str(context.metadata.get("category", "")),
    )


class UnitResults(list[UnitResult]):
    """Backward-compatible list carrying the completed run report."""

    def __init__(self, values: Sequence[UnitResult], report: RunReport) -> None:
        super().__init__(values)
        self.report = report

    @property
    def wall_clock_seconds(self) -> float:
        return self.report.wall_clock_seconds

    @property
    def serial_equivalent_seconds(self) -> float:
        return self.report.serial_equivalent_seconds

    @property
    def queue_seconds(self) -> float:
        return self.report.queue_seconds


def _metadata_for(
    unit: ValidationUnit,
    values: Mapping[str, Sequence[str]] | None,
) -> tuple[str, ...]:
    if values is None:
        return ()
    return tuple(str(value) for value in values.get(unit.unit_id, ()))


def _dependency_state(
    index: int,
    selected: Sequence[ValidationUnit],
    result_by_index: Mapping[int, UnitResult],
    dependencies: Mapping[str, tuple[str, ...]],
    index_by_id: Mapping[str, int],
) -> tuple[str, str]:
    unit = selected[index]
    for dependency in dependencies.get(unit.unit_id, ()):
        dependency_index = index_by_id.get(dependency)
        if dependency_index is None:
            return "incomplete", f"unknown dependency: {dependency}"
        dependency_result = result_by_index.get(dependency_index)
        if dependency_result is None:
            return "pending", ""
        if dependency_result.status != "passed":
            return "skipped", f"dependency did not pass: {dependency}"
    return "ready", ""


def run_units(
    units: Sequence[ValidationUnit],
    context: RunContext,
    *,
    fail_fast: bool = False,
    max_parallel: int = 1,
    dependencies: Mapping[str, Sequence[str]] | None = None,
    resources: Mapping[str, Sequence[str]] | None = None,
    dependency_map: Mapping[str, Sequence[str]] | None = None,
    resource_map: Mapping[str, Sequence[str]] | None = None,
    heartbeat_interval_seconds: float = 15.0,
) -> UnitResults:
    """Run selected units with bounded, dependency/resource-aware scheduling.

    The returned object remains list-compatible for existing callers and
    exposes the versioned :class:`RunReport` through ``.report``.
    """

    if max_parallel < 1:
        raise ValueError("max_parallel must be at least 1")
    if heartbeat_interval_seconds <= 0:
        raise ValueError("heartbeat_interval_seconds must be positive")

    selected = list(units)
    sink = _event_sink(context)
    owns_sink = sink is None
    if owns_sink:
        sink = EventSink(context.invocation_id or None)
    effective_context = replace(
        context,
        event_sink=sink,
        invocation_id=sink.invocation_id,
    )
    started_at = time.monotonic()
    _emit(
        effective_context,
        phase="preflight",
        unit_id=None,
        status="planned",
        detail=(
            f"units={len(selected)} max_parallel={max_parallel} "
            f"fail_fast={str(fail_fast).lower()}"
        ),
    )
    _emit(
        effective_context,
        phase="plan",
        unit_id=None,
        status="planned",
        detail="selected validation units",
    )
    for unit in selected:
        _emit(
            effective_context,
            phase="plan",
            unit_id=unit.unit_id,
            status="planned",
            detail=unit.title,
        )

    dependency_values = dependencies or dependency_map or {}
    resource_values = resources or resource_map or {}
    dependency_by_id = {
        str(unit_id): tuple(str(value) for value in values)
        for unit_id, values in dependency_values.items()
    }
    index_by_id = {unit.unit_id: index for index, unit in enumerate(selected)}
    result_by_index: dict[int, UnitResult] = {}
    pending = set(range(len(selected)))
    active: dict[Future[UnitResult], tuple[int, tuple[str, ...]]] = {}
    active_resources: set[str] = set()
    queued_at: dict[int, float] = {}
    failure_seen = False
    executor = ThreadPoolExecutor(
        max_workers=max(1, min(max_parallel, len(selected) or 1))
    )

    try:
        while pending or active:
            progress = False

            # Dependency failures and malformed dependency references are
            # explicit terminal states, never silently dropped from results.
            for index in sorted(tuple(pending)):
                state, detail = _dependency_state(
                    index,
                    selected,
                    result_by_index,
                    dependency_by_id,
                    index_by_id,
                )
                if state not in {"skipped", "incomplete"}:
                    continue
                result_by_index[index] = _terminal_result(
                    selected[index],
                    effective_context,
                    status=state,
                    detail=detail,
                )
                pending.remove(index)
                progress = True

            if fail_fast and failure_seen:
                for index in sorted(tuple(pending)):
                    result_by_index[index] = _terminal_result(
                        selected[index],
                        effective_context,
                        status="cancelled",
                        detail="not started after fail-fast failure",
                    )
                    pending.remove(index)
                progress = True
            else:
                ready: list[int] = []
                for index in sorted(pending):
                    state, _ = _dependency_state(
                        index,
                        selected,
                        result_by_index,
                        dependency_by_id,
                        index_by_id,
                    )
                    if state == "ready":
                        ready.append(index)

                serial_ready = [
                    index for index in ready if not selected[index].parallelizable
                ]
                if serial_ready:
                    # A non-parallelizable unit owns the whole execution lane.
                    # It may start only after currently active parallel work has
                    # drained, preserving the business validator boundary.
                    candidates = [] if active else [min(serial_ready)]
                else:
                    candidates = []
                    for index in ready:
                        if len(active) + len(candidates) >= max_parallel:
                            break
                        unit_resources = _metadata_for(selected[index], resource_values)
                        if active_resources.intersection(unit_resources):
                            continue
                        if any(
                            set(unit_resources).intersection(
                                _metadata_for(selected[other], resource_values)
                            )
                            for other in candidates
                        ):
                            continue
                        candidates.append(index)

                for index in candidates:
                    unit = selected[index]
                    unit_resources = _metadata_for(unit, resource_values)
                    queued_at[index] = time.monotonic()
                    _emit(
                        effective_context,
                        phase="queued",
                        unit_id=unit.unit_id,
                        status="queued",
                        detail="unit queued for execution",
                    )
                    pending.remove(index)
                    active_resources.update(unit_resources)
                    future = executor.submit(
                        _run_one,
                        unit,
                        effective_context,
                        index,
                        queued_at[index],
                    )
                    active[future] = (index, unit_resources)
                    progress = True

            if active:
                done, _ = wait(
                    tuple(active),
                    timeout=heartbeat_interval_seconds,
                    return_when=FIRST_COMPLETED,
                )
                if not done:
                    for future, (index, _) in sorted(
                        active.items(), key=lambda item: item[1][0]
                    ):
                        _emit(
                            effective_context,
                            phase="heartbeat",
                            unit_id=selected[index].unit_id,
                            status="running",
                            detail="unit still running",
                        )
                    continue
                for future in sorted(done, key=lambda item: active[item][0]):
                    index, unit_resources = active.pop(future)
                    active_resources.difference_update(unit_resources)
                    result = future.result()
                    result = replace(
                        result,
                        completed_at=(
                            sink.events[-1].wall_timestamp
                            if sink.events
                            else result.completed_at
                        ),
                    )
                    result_by_index[index] = result
                    _emit(
                        effective_context,
                        phase="unit-complete",
                        unit_id=result.unit.unit_id,
                        status=result.status
                        or ("passed" if result.exit_code == 0 else "failed"),
                        detail=f"exit_code={result.exit_code}",
                    )
                    if result.exit_code != 0:
                        failure_seen = True
                continue

            if pending and not progress:
                # A cycle or an otherwise unresolvable dependency is an
                # observable incomplete result rather than an infinite wait.
                for index in sorted(tuple(pending)):
                    result_by_index[index] = _terminal_result(
                        selected[index],
                        effective_context,
                        status="incomplete",
                        detail="dependencies could not be resolved",
                    )
                    pending.remove(index)
    finally:
        executor.shutdown(wait=True, cancel_futures=False)

    ordered_results = [result_by_index[index] for index in range(len(selected))]
    finished_at = time.monotonic()
    serial_equivalent = sum(result.duration_seconds for result in ordered_results)
    category_durations: Counter[str] = Counter()
    for result in ordered_results:
        category = result.category or str(effective_context.category or "default")
        category_durations[category] += result.duration_seconds
    report = RunReport(
        request=str(effective_context.metadata.get("request", "")),
        selectors=tuple(effective_context.selectors),
        planned_units=tuple(unit.unit_id for unit in selected),
        results=tuple(ordered_results),
        events=tuple(sink.events),
        context=effective_context,
        concurrency=max_parallel,
        fail_fast=fail_fast,
        artifact_root=effective_context.artifact_dir,
        wall_clock_seconds=max(0.0, finished_at - started_at),
        serial_equivalent_seconds=serial_equivalent,
        queue_seconds=sum(result.queue_seconds for result in ordered_results),
        category_durations=dict(category_durations),
        status_counts=dict(Counter(result.status for result in ordered_results)),
        problems=tuple(
            f"{result.unit.unit_id}: exit code {result.exit_code}"
            for result in ordered_results
            if result.exit_code != 0
        ),
        next_actions=tuple(
            f"inspect {result.unit.unit_id}"
            for result in ordered_results
            if result.exit_code != 0
        ),
        artifacts=tuple(
            artifact for result in ordered_results for artifact in result.artifacts
        ),
    )
    if owns_sink:
        sink.close()
    return UnitResults(ordered_results, report)
