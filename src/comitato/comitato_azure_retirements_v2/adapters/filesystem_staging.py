from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from ..contracts.codecs import canonical_json
from ..contracts.cross_artifact import (
    validate_candidate_paths,
    validate_manifest,
    validate_selected_set,
)
from ..contracts.model import Artifact, EncodedArtifact
from ..domain.diagnostics import Diagnostic, sort_diagnostics
from ..publication.model import (
    PublicationCandidate,
    PublicationError,
    PublicationManifest,
)
from ..reports.catalog import DEFAULT_REPORT_CATALOG
from ..reports.model import StagedDecodeFailure


@dataclass(frozen=True, slots=True)
class _ValidatedStagedGeneration:
    generation_dir: Path
    manifest: dict[str, Any]
    artifacts: tuple[EncodedArtifact, ...]


def _error(code: str, candidate: PublicationCandidate, *, artifact: str = "", message: str | None = None) -> PublicationError:
    diagnostic = Diagnostic(
        severity="error",
        code=code,
        stage="staging",
        report=candidate.context.request.selector.value,
        run_id=candidate.context.run_id,
        artifact=artifact,
        message=message or code.replace("_", " "),
    )
    return PublicationError(diagnostic)


def _fsync_file(path: Path, data: bytes, fault_injector: Any = None, logical_path: str = "") -> None:
    with path.open("wb") as handle:
        handle.write(data)
        if fault_injector:
            fault_injector("flush", logical_path)
        handle.flush()
        if fault_injector:
            fault_injector("sync", logical_path)
        os.fsync(handle.fileno())
    if fault_injector:
        fault_injector("close", logical_path)


def _decode_and_validate(
    candidate: PublicationCandidate,
    artifacts: tuple[EncodedArtifact, ...],
    generation_dir: Path,
) -> tuple[Diagnostic, ...]:
    diagnostics: list[Diagnostic] = []
    payloads = {artifact.logical_path: artifact.data for artifact in artifacts}
    original_by_path = {artifact.logical_path: artifact for artifact in candidate.artifacts}
    for artifact in artifacts:
        target = generation_dir / PurePosixPath(artifact.logical_path)
        try:
            data = target.read_bytes()
            if data != original_by_path[artifact.logical_path].data:
                diagnostics.append(
                    _error(
                        "staged_bytes_changed",
                        candidate,
                        artifact=artifact.logical_path,
                        message="reread staged bytes differ from the encoded candidate",
                    ).diagnostics[0]
                )
        except OSError:
            diagnostics.append(_error("staged_artifact_missing", candidate, artifact=artifact.logical_path).diagnostics[0])
            continue
        try:
            definition = DEFAULT_REPORT_CATALOG.owner_of(artifact.logical_path)
        except KeyError:
            diagnostics.append(_error("undeclared_artifact", candidate, artifact=artifact.logical_path).diagnostics[0])
            continue
        try:
            diagnostics.extend(
                definition.verify_staged_artifact(
                    artifact.logical_path, payloads, candidate.context
                )
            )
        except StagedDecodeFailure as exc:
            diagnostics.append(_error("invalid_staged_header" if exc.logical_path.endswith(".tsv") else "invalid_staged_jsonl", candidate, artifact=exc.logical_path, message="staged bytes do not satisfy the owning contract").diagnostics[0])
    return tuple(diagnostics)


def _measured_artifacts(candidate: PublicationCandidate, generation_dir: Path, fault_injector: Any = None) -> tuple[EncodedArtifact, ...]:
    measured: list[EncodedArtifact] = []
    for artifact in candidate.artifacts:
        target = generation_dir / PurePosixPath(artifact.logical_path)
        if fault_injector:
            fault_injector("reread", artifact.logical_path)
        data = target.read_bytes()
        if artifact.logical_path.endswith(".tsv"):
            rows = max(0, len(data.decode("utf-8").splitlines()) - 1)
        elif artifact.logical_path.endswith(".jsonl"):
            rows = len(data.decode("utf-8").splitlines()) if data else 0
        else:
            rows = artifact.rows
        if fault_injector:
            fault_injector("hash", artifact.logical_path)
        measured.append(EncodedArtifact(
            logical_path=artifact.logical_path,
            data=data,
            rows=rows,
            media_type=artifact.media_type,
            schema_version=artifact.schema_version,
            run_id=artifact.run_id,
        ))
    return tuple(measured)


def _manifest(candidate: PublicationCandidate, artifacts: tuple[EncodedArtifact, ...]) -> dict[str, Any]:
    artifact_entries = [
        {
            "bytes": len(artifact.data),
            "media_type": artifact.media_type,
            "path": artifact.logical_path,
            "report": DEFAULT_REPORT_CATALOG.owner_of(artifact.logical_path).name,
            "rows": artifact.rows,
            "schema_version": artifact.schema_version,
            "sha256": artifact.digest,
        }
        for artifact in artifacts
    ]
    sources = [
        {
            "api_version": acquisition.receipt.api_version,
            "complete": acquisition.receipt.complete,
            "name": acquisition.receipt.source,
            "pages": acquisition.receipt.pages,
            "source_records": acquisition.receipt.source_records,
        }
        for acquisition in sorted(candidate.acquisitions, key=lambda item: item.receipt.source)
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


def stage_candidate(
    candidate: PublicationCandidate,
    destination: Path,
    *,
    staged_byte_mutator: Any = None,
    fault_injector: Any = None,
) -> _ValidatedStagedGeneration:
    path_diagnostics = validate_candidate_paths(candidate)
    if path_diagnostics:
        raise PublicationError(path_diagnostics[0])
    selected_diagnostics = validate_selected_set(
        candidate.context.request.selector,
        candidate.artifacts,
        context=candidate.context,
    )
    if selected_diagnostics:
        raise PublicationError(selected_diagnostics[0])
    for acquisition in candidate.acquisitions:
        if not acquisition.receipt.is_complete:
            raise _error("incomplete_acquisition", candidate, message=f"{acquisition.receipt.source} acquisition is incomplete")
    destination.mkdir(parents=True, exist_ok=True)
    staging_root = destination / ".staging"
    staging_root.mkdir(parents=True, exist_ok=True)
    generation_dir = Path(tempfile.mkdtemp(prefix=f"{candidate.context.run_id}-", dir=staging_root))
    try:
        for artifact in candidate.artifacts:
            target = generation_dir / PurePosixPath(artifact.logical_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            _fsync_file(target, artifact.data, fault_injector, artifact.logical_path)
        if staged_byte_mutator is not None:
            staged_byte_mutator(generation_dir)
        expected_payloads = {artifact.logical_path for artifact in candidate.artifacts}
        actual_payloads = {
            path.relative_to(generation_dir).as_posix()
            for path in generation_dir.rglob("*")
            if path.is_file()
        }
        if actual_payloads != expected_payloads:
            extra = sorted(actual_payloads - expected_payloads)
            missing = sorted(expected_payloads - actual_payloads)
            artifact = (extra or missing or [""])[0]
            raise _error("staged_file_closure_mismatch", candidate, artifact=artifact)
        measured = _measured_artifacts(candidate, generation_dir, fault_injector)
        diagnostics = _decode_and_validate(candidate, measured, generation_dir)
        if diagnostics:
            ordered = sort_diagnostics(diagnostics)
            raise PublicationError("staged bytes validation failed", ordered)
        manifest = _manifest(candidate, measured)
        manifest_diagnostics = validate_manifest(candidate, manifest, measured)
        if manifest_diagnostics:
            raise PublicationError("publication manifest validation failed", manifest_diagnostics)
        _fsync_file(
            generation_dir / "publication-manifest.json",
            PublicationManifest(manifest).to_bytes(),
        )
        return _ValidatedStagedGeneration(
            generation_dir=generation_dir,
            manifest=manifest,
            artifacts=measured,
        )
    except Exception as exc:
        shutil.rmtree(generation_dir, ignore_errors=True)
        if isinstance(exc, PublicationError):
            raise
        raise _error("staging_failure", candidate) from exc
