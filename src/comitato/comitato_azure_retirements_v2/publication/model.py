from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from ..contracts.model import EncodedArtifact
from ..domain.execution import RunContext
from ..domain.diagnostics import Diagnostic
from ..reports.catalog import SelectedReportClosure


@dataclass(frozen=True, slots=True)
class PublicationCandidate:
    context: RunContext
    report_closure: SelectedReportClosure
    artifacts: tuple[EncodedArtifact, ...]
    acquisitions: tuple[Any, ...]
    slide_selection: Any = None


@dataclass(frozen=True, slots=True)
class PublicationReceipt:
    generation: str
    current_reference: str


class PublicationError(RuntimeError):
    """A candidate cannot be safely published."""

    def __init__(
        self,
        message: str | Diagnostic,
        diagnostics: tuple[Diagnostic, ...] = (),
    ) -> None:
        if isinstance(message, Diagnostic):
            diagnostics = (message,)
            message = message.message
        self.diagnostics = tuple(diagnostics)
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class PublicationManifest:
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return self.payload

    def to_bytes(self) -> bytes:
        return (json.dumps(self.payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


@dataclass(frozen=True, slots=True)
class RunResult:
    exit_status: int
    context: RunContext
    candidate: PublicationCandidate
    publication_receipt: PublicationReceipt
