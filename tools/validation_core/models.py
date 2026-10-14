"""Typed, domain-neutral values shared by validation entrypoints."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CommandEvidence:
    command: str
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    duration_seconds: float = 0.0
    simulated: bool = False


@dataclass(frozen=True)
class RunContext:
    root: Path
    tmp_dir: Path
    dry_run: bool
    no_color: bool
    event_sink: Any | None = None
    invocation_id: str = ""
    category: str = ""
    selectors: tuple[str, ...] = ()
    artifact_dir: Path | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    compact: bool = False


@dataclass(frozen=True)
class ValidationUnit:
    unit_id: str
    title: str
    run: Callable[[RunContext], int]
    parallelizable: bool = True


@dataclass(frozen=True)
class UnitResult:
    unit: ValidationUnit
    exit_code: int
    duration_seconds: float
    commands: tuple[CommandEvidence, ...] = ()
    artifacts: tuple[str, ...] = ()
    status: str = ""
    queue_seconds: float = 0.0
    category: str = ""
    started_at: str = ""
    completed_at: str = ""


@dataclass(frozen=True)
class RunReport:
    """Versioned, domain-neutral data for all validation output projections.

    Every field added after the original execution models has a default so
    existing validation callers can migrate to the shared report incrementally.
    """

    schema_version: str = "validation-run/v1"
    request: str = ""
    selectors: tuple[str, ...] = ()
    planned_units: tuple[str, ...] = ()
    results: tuple[UnitResult, ...] = ()
    events: tuple[Any, ...] = ()
    context: RunContext | None = None
    concurrency: int = 1
    fail_fast: bool = False
    artifact_root: Path | None = None
    tool_versions: dict[str, str] = field(default_factory=dict)
    repository_before: Any | None = None
    repository_after: Any | None = None
    repository_delta: Any | None = None
    wall_clock_seconds: float = 0.0
    serial_equivalent_seconds: float = 0.0
    queue_seconds: float = 0.0
    category_durations: dict[str, float] = field(default_factory=dict)
    status_counts: dict[str, int] = field(default_factory=dict)
    problems: tuple[str, ...] = ()
    next_actions: tuple[str, ...] = ()
    artifacts: tuple[str, ...] = ()
