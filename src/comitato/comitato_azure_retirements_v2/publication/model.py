from __future__ import annotations

from dataclasses import dataclass
import json
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
class PublicationManifest:
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return self.payload

    def to_bytes(self) -> bytes:
        return (json.dumps(self.payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


@dataclass(frozen=True, slots=True)
class ValidatedStagedGeneration:
    generation_dir: Any
    manifest: dict[str, Any]
    artifacts: tuple[EncodedArtifact, ...]


@dataclass(frozen=True, slots=True)
class RunResult:
    exit_status: int
    context: RunContext
    candidate: PublicationCandidate
    publication_receipt: Any
