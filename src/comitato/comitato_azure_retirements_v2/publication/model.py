from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..contracts.model import EncodedArtifact
from ..domain.execution import DependencyPlan, RunContext


@dataclass(frozen=True, slots=True)
class PublicationCandidate:
    context: RunContext
    dependency_plan: DependencyPlan
    artifacts: tuple[EncodedArtifact, ...]
    acquisitions: tuple[Any, ...]
    slide_selection: Any = None


@dataclass(frozen=True, slots=True)
class RunResult:
    exit_status: int
    context: RunContext
    candidate: PublicationCandidate
    publication_receipt: Any
