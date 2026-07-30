from __future__ import annotations

from pathlib import PurePosixPath

from ..domain.diagnostics import Diagnostic, sort_diagnostics
from ..publication.model import PublicationCandidate


def validate_candidate_paths(candidate: PublicationCandidate) -> tuple[Diagnostic, ...]:
    diagnostics: list[Diagnostic] = []
    seen: set[str] = set()
    for artifact in candidate.artifacts:
        path = PurePosixPath(artifact.logical_path)
        if path.is_absolute() or ".." in path.parts or artifact.logical_path in seen:
            diagnostics.append(
                Diagnostic(
                    severity="error",
                    code="unsafe_publication_path",
                    stage="staging",
                    report=candidate.context.request.selector.value,
                    run_id=candidate.context.run_id,
                    artifact=artifact.logical_path,
                    message="publication path must be relative, unique, and confined to the generation",
                )
            )
        seen.add(artifact.logical_path)
    return sort_diagnostics(diagnostics)
