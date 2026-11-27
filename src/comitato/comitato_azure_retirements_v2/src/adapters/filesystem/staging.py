from __future__ import annotations

import os
import shutil
import tempfile
from collections.abc import Callable, Mapping
from contextlib import ExitStack
from dataclasses import asdict, dataclass, is_dataclass, replace
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any

from ... import __version__
from ...contracts.codecs import canonical_json
from ...contracts.model import EncodedArtifact
from ...domain.diagnostics import Diagnostic, sort_diagnostics
from ...paths import artifact_destination
from ...publication.model import (
    PublicationCandidate,
    PublicationError,
    PublicationManifest,
)
from ...publication.validation import (
    validate_candidate_paths,
    validate_manifest,
    validate_selected_set,
)
from ...reports.model import StagedDecodeFailure

StageFault = Callable[[str, str], None]


@dataclass(frozen=True, slots=True)
class ValidatedStagedGeneration:
    generation_dir: Path
    support_generation_dir: Path
    manifest: dict[str, Any]
    artifacts: tuple[EncodedArtifact, ...]


def _error(
    code: str,
    candidate: PublicationCandidate,
    *,
    artifact: str = "",
    message: str | None = None,
) -> PublicationError:
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


def _fsync_file(
    path: Path, data: bytes, fault_injector: StageFault | None, logical_path: str
) -> None:
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
) -> tuple[Diagnostic, ...]:
    diagnostics: list[Diagnostic] = []
    payloads = {artifact.logical_path: artifact.data for artifact in artifacts}
    for original, artifact in zip(candidate.artifacts, artifacts, strict=True):
        if artifact.data != original.data:
            diagnostics.append(
                _error(
                    "staged_bytes_changed",
                    candidate,
                    artifact=artifact.logical_path,
                    message="reread staged bytes differ from the encoded candidate",
                ).diagnostics[0]
            )
        try:
            definition = candidate.report_closure.owner_of(artifact.logical_path)
        except KeyError:
            diagnostics.append(
                _error(
                    "undeclared_artifact", candidate, artifact=artifact.logical_path
                ).diagnostics[0]
            )
            continue
        try:
            diagnostics.extend(
                definition.verify_staged_artifact(
                    artifact.logical_path, payloads, candidate.context
                )
            )
        except StagedDecodeFailure as exc:
            diagnostics.append(
                _error(
                    "invalid_staged_header"
                    if exc.logical_path.endswith(".tsv")
                    else "invalid_staged_jsonl",
                    candidate,
                    artifact=exc.logical_path,
                    message="staged bytes do not satisfy the owning contract",
                ).diagnostics[0]
            )
    return tuple(diagnostics)


def _measured_artifacts(
    candidate: PublicationCandidate,
    targets: Mapping[str, Path],
    fault_injector: StageFault | None,
) -> tuple[EncodedArtifact, ...]:
    measured: list[EncodedArtifact] = []
    for artifact in candidate.artifacts:
        if fault_injector:
            fault_injector("reread", artifact.logical_path)
        data = targets[artifact.logical_path].read_bytes()
        if artifact.logical_path.endswith(".tsv"):
            rows = max(0, len(data.decode("utf-8").splitlines()) - 1)
        elif artifact.logical_path.endswith(".jsonl"):
            rows = len(data.decode("utf-8").splitlines()) if data else 0
        else:
            rows = artifact.rows
        if fault_injector:
            fault_injector("hash", artifact.logical_path)
        measured.append(replace(artifact, data=data, rows=rows))
    return tuple(measured)


def _manifest(
    candidate: PublicationCandidate, artifacts: tuple[EncodedArtifact, ...]
) -> dict[str, Any]:
    artifact_entries = [
        {
            "bytes": len(artifact.data),
            "destination": artifact_destination(artifact.logical_path),
            "media_type": artifact.media_type,
            "path": artifact.logical_path,
            "report": candidate.report_closure.owner_of(artifact.logical_path).name,
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
            "normalized_records": len(acquisition.records),
            "accounting": [
                asdict(item) if is_dataclass(item) else dict(item)
                for item in getattr(acquisition, "accounting", ())
            ],
        }
        for acquisition in sorted(
            candidate.acquisitions, key=lambda item: item.receipt.source
        )
    ]
    expected = sum(
        item.receipt.expected_subscriptions for item in candidate.acquisitions
    )
    completed = sum(
        item.receipt.completed_subscriptions for item in candidate.acquisitions
    )
    context = candidate.context
    manifest = dict(candidate.manifest_metadata or {})
    manifest.update(
        {
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
            "manifest_schema_version": 2,
            "run_id": context.run_id,
            "scope": {
                "mode": context.scope.mode,
                "subscription_ids": list(context.scope.subscription_ids),
            },
            "selector": context.request.selector.value,
            "validation": {"error_count": 0, "status": "passed"},
        }
    )
    manifest.setdefault(
        "settings",
        {
            "committee_window_months": context.request.committee_window_months,
        },
    )
    manifest.setdefault(
        "derivation",
        {
            "mode": "live",
            "program_revision": __version__,
        },
    )
    manifest.setdefault(
        "saved_inputs",
        candidate.saved_inputs
        or {
            "schema_version": 1,
            "source_acquisitions": [
                _saved_acquisition(acquisition)
                for acquisition in candidate.acquisitions
            ],
            "publication_settings": dict(manifest.get("settings", {})),
        },
    )
    if isinstance(manifest["saved_inputs"], Mapping):
        manifest["saved_inputs"] = dict(manifest["saved_inputs"])
        manifest["saved_inputs"].pop("editorial_catalog", None)
    manifest.pop("editorial_catalog", None)
    manifest.pop("editorial_work_list", None)
    manifest["saved_inputs_sha256"] = sha256(
        canonical_json(manifest["saved_inputs"]).encode("utf-8")
    ).hexdigest()
    return manifest


def _json_safe(value: Any) -> Any:
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _saved_acquisition(acquisition: Any) -> dict[str, Any]:
    receipt = getattr(acquisition, "receipt", None)
    return {
        "receipt": _json_safe(receipt),
        "records": _json_safe(getattr(acquisition, "records", ())),
        "companion_records": _json_safe(getattr(acquisition, "companion_records", ())),
        "accounting": _json_safe(getattr(acquisition, "accounting", ())),
        "collection_context": _json_safe(
            getattr(acquisition, "collection_context", {})
        ),
        "response_context": _json_safe(getattr(acquisition, "response_context", ())),
    }


def stage_candidate(
    candidate: PublicationCandidate,
    destination: Path,
    support_destination: Path | None = None,
    *,
    staged_byte_mutator: Callable[[Path, Path], None] | None = None,
    fault_injector: StageFault | None = None,
) -> ValidatedStagedGeneration:
    path_diagnostics = validate_candidate_paths(candidate)
    if path_diagnostics:
        raise PublicationError(path_diagnostics[0])
    selected_diagnostics = validate_selected_set(
        candidate.report_closure,
        candidate.artifacts,
        context=candidate.context,
    )
    if selected_diagnostics:
        raise PublicationError(selected_diagnostics[0])
    for acquisition in candidate.acquisitions:
        if not acquisition.receipt.is_complete:
            raise _error(
                "incomplete_acquisition",
                candidate,
                message=f"{acquisition.receipt.source} acquisition is incomplete",
            )
    support_destination = (
        support_destination
        if support_destination is not None
        else destination.with_name(f"{destination.name}-support")
    )
    if support_destination.resolve() == destination.resolve():
        raise _error(
            "support_destination_collides_with_exports",
            candidate,
            message="support destination must be separate from publication exports",
        )
    try:
        with ExitStack() as cleanup:
            staged_roots: dict[str, Path] = {}
            for name, root in (
                ("exports", destination),
                ("support", support_destination),
            ):
                staging_root = root / ".staging"
                staging_root.mkdir(parents=True, exist_ok=True)
                staged = Path(
                    tempfile.mkdtemp(
                        prefix=f"{candidate.context.run_id}-", dir=staging_root
                    )
                )
                cleanup.callback(shutil.rmtree, staged, ignore_errors=True)
                staged_roots[name] = staged

            targets = {}
            for artifact in candidate.artifacts:
                path = artifact.logical_path
                target = staged_roots[artifact_destination(path)] / PurePosixPath(path)
                targets[path] = target
                target.parent.mkdir(parents=True, exist_ok=True)
                _fsync_file(target, artifact.data, fault_injector, path)

            exports = staged_roots["exports"]
            support = staged_roots["support"]
            if staged_byte_mutator is not None:
                staged_byte_mutator(exports, support)
            expected = set(targets.values())
            actual = {
                path
                for root in staged_roots.values()
                for path in root.rglob("*")
                if path.is_file()
            }
            if actual != expected:
                unexpected = sorted(actual - expected) or sorted(expected - actual)
                path = unexpected[0]
                logical_path = next(
                    path.relative_to(root).as_posix()
                    for root in staged_roots.values()
                    if path.is_relative_to(root)
                )
                raise _error(
                    "staged_file_closure_mismatch", candidate, artifact=logical_path
                )

            measured = _measured_artifacts(candidate, targets, fault_injector)
            diagnostics = _decode_and_validate(candidate, measured)
            if diagnostics:
                raise PublicationError(
                    "staged bytes validation failed", sort_diagnostics(diagnostics)
                )
            manifest = _manifest(candidate, measured)
            manifest_diagnostics = validate_manifest(candidate, manifest, measured)
            if manifest_diagnostics:
                raise PublicationError(
                    "publication manifest validation failed", manifest_diagnostics
                )
            saved_inputs = manifest.pop("saved_inputs")
            manifest["saved_inputs_path"] = "saved-acquisition-inputs.json"
            expected_bytes = {
                artifact.logical_path: artifact.data for artifact in measured
            }
            for name, data in (
                (
                    "saved-acquisition-inputs.json",
                    (canonical_json(saved_inputs) + "\n").encode("utf-8"),
                ),
                ("publication-manifest.json", PublicationManifest(manifest).to_bytes()),
            ):
                target = support / name
                _fsync_file(target, data, fault_injector, name)
                targets[name] = target
                expected_bytes[name] = data

            for name, expected_data in expected_bytes.items():
                if targets[name].read_bytes() != expected_data:
                    raise _error("staged_bytes_changed", candidate, artifact=name)

            result = ValidatedStagedGeneration(
                generation_dir=exports,
                support_generation_dir=support,
                manifest=manifest,
                artifacts=measured,
            )
            cleanup.pop_all()
            return result
    except (OSError, ValueError) as exc:
        raise _error("staging_failure", candidate) from exc
