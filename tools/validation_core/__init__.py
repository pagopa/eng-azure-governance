"""Infrastructure-only execution and reporting primitives for validation CLIs."""

from .artifacts import write_run_result, write_unit_log
from .events import EVENT_STATUSES, EventSink, RunEvent, redact
from .execution import UnitResults, run_command, run_units
from .models import (
    CommandEvidence,
    RunContext,
    RunReport,
    UnitResult,
    ValidationUnit,
)
from .reporting import render_report, render_run, report_to_payload
from .snapshots import RepositoryDelta, RepositorySnapshot

__all__ = [
    "CommandEvidence",
    "EVENT_STATUSES",
    "EventSink",
    "RunContext",
    "RunEvent",
    "RunReport",
    "RepositoryDelta",
    "RepositorySnapshot",
    "UnitResult",
    "UnitResults",
    "ValidationUnit",
    "redact",
    "render_report",
    "render_run",
    "report_to_payload",
    "run_command",
    "run_units",
    "write_run_result",
    "write_unit_log",
]
