from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from ..contracts.codecs import canonical_json
from ..contracts.cross_artifact import validate_candidate_paths
from ..publication.model import PublicationCandidate


class PublicationError(RuntimeError):
    """A candidate cannot be safely staged or committed."""


@dataclass(frozen=True, slots=True)
class StagedGeneration:
    generation_dir: Path
    manifest: dict[str, Any]


def _fsync_file(path: Path, data: bytes) -> None:
    with path.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def _artifact_report(path: str) -> str:
    if "service_health" in path:
        return "service-health"
    if "advisor" in path:
        return "advisor"
    if path.startswith("02_"):
        return "aggregate"
    return "slides"


def _manifest(candidate: PublicationCandidate, generation_dir: Path) -> dict[str, Any]:
    artifact_entries = []
    for artifact in candidate.artifacts:
        target = generation_dir / PurePosixPath(artifact.logical_path)
        data = target.read_bytes()
        if data != artifact.data:
            raise PublicationError(f"staged bytes changed for {artifact.logical_path}")
        artifact_entries.append(
            {
                "artifact": _artifact_report(artifact.logical_path),
                "bytes": len(data),
                "media_type": artifact.media_type,
                "path": artifact.logical_path,
                "rows": artifact.rows,
                "schema_version": artifact.schema_version,
                "sha256": artifact.digest,
            }
        )
    sources = [
        {
            "api_version": acquisition.receipt.api_version,
            "complete": acquisition.receipt.complete,
            "name": acquisition.receipt.source,
            "pages": acquisition.receipt.pages,
            "source_records": acquisition.receipt.source_records,
        }
        for acquisition in candidate.acquisitions
    ]
    expected = sum(item.receipt.expected_subscriptions for item in candidate.acquisitions)
    completed = sum(item.receipt.completed_subscriptions for item in candidate.acquisitions)
    context = candidate.context
    return {
        "acquisition": {
            "completed_subscriptions": completed,
            "expected_subscriptions": expected,
            "sources": sources,
        },
        "artifacts": artifact_entries,
        "as_of_date": context.as_of_date.isoformat(),
        "catalog": {
            "schema_version": context.catalog_identity.schema_version,
            "sha256": context.catalog_identity.sha256,
        },
        "created_at": context.created_at.isoformat().replace("+00:00", "Z"),
        "dependency_closure": list(context.dependency_plan.stages),
        "manifest_schema_version": 1,
        "run_id": context.run_id,
        "scope": {
            "mode": context.scope.mode,
            "subscription_ids": list(context.scope.subscription_ids),
        },
        "selector": context.request.selector.value,
        "validation": {"error_count": 0, "status": "passed"},
    }


def stage_candidate(candidate: PublicationCandidate, destination: Path) -> StagedGeneration:
    path_diagnostics = validate_candidate_paths(candidate)
    if path_diagnostics:
        raise PublicationError(path_diagnostics[0].message)
    destination.mkdir(parents=True, exist_ok=True)
    staging_root = destination / ".staging"
    staging_root.mkdir(parents=True, exist_ok=True)
    generation_dir = Path(tempfile.mkdtemp(prefix=f"{candidate.context.run_id}-", dir=staging_root))
    try:
        for artifact in candidate.artifacts:
            target = generation_dir / PurePosixPath(artifact.logical_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            _fsync_file(target, artifact.data)
        manifest = _manifest(candidate, generation_dir)
        _fsync_file(
            generation_dir / "publication-manifest.json",
            (canonical_json(manifest) + "\n").encode("utf-8"),
        )
        return StagedGeneration(generation_dir=generation_dir, manifest=manifest)
    except Exception as exc:
        if isinstance(exc, PublicationError):
            raise
        raise PublicationError(f"failed to stage publication: {exc}") from exc
