from __future__ import annotations

from pathlib import PurePosixPath
import re

from ..domain.diagnostics import Diagnostic, sort_diagnostics
from ..domain.execution import ReportSelector, RunContext
from ..reports.catalog import DEFAULT_REPORT_CATALOG
from .model import EncodedArtifact
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


def _field_values(artifact: EncodedArtifact, field: str) -> set[str]:
    values: set[str] = set()
    text = artifact.data.decode("utf-8")
    lines = text.splitlines()
    if artifact.logical_path.endswith(".tsv") and lines:
        header = lines[0].split("\t")
        if field in header:
            index = header.index(field)
            values.update(
                row.split("\t")[index]
                for row in lines[1:]
                if len(row.split("\t")) > index
            )
    elif artifact.logical_path.endswith(".jsonl"):
        values.update(
            match.group(1)
            for line in lines
            for match in [re.search(rf'"{field}"\s*:\s*"([^"]*)"', line)]
            if match
        )
    return {value for value in values if value}


def _diagnostic(code: str, selector: ReportSelector, context: RunContext | None, artifact: str = "") -> Diagnostic:
    return Diagnostic(
        severity="error",
        code=code,
        stage="validation",
        report=selector.value,
        run_id=context.run_id if context else "",
        artifact=artifact,
        message=code.replace("_", " "),
    )


def validate_selected_set(
    selector: ReportSelector,
    artifacts: tuple[EncodedArtifact, ...],
    *,
    context: RunContext | None = None,
) -> tuple[Diagnostic, ...]:
    plan = DEFAULT_REPORT_CATALOG.plan(selector)
    expected = plan.expected_paths
    known_paths = set(DEFAULT_REPORT_CATALOG.all_paths)
    by_path: dict[str, EncodedArtifact] = {}
    diagnostics: list[Diagnostic] = []
    for artifact in artifacts:
        if artifact.logical_path in by_path:
            diagnostics.append(_diagnostic("duplicate_artifact", selector, context, artifact.logical_path))
        by_path[artifact.logical_path] = artifact
        if artifact.logical_path not in expected:
            diagnostics.append(_diagnostic("undeclared_artifact", selector, context, artifact.logical_path))
            if artifact.logical_path in known_paths:
                diagnostics.append(_diagnostic("dependency_artifact_selected", selector, context, artifact.logical_path))
    for path in expected:
        if path not in by_path:
            diagnostics.append(_diagnostic("missing_selected_artifact", selector, context, path))
    for definition in plan.published:
        if len(definition.paths) > 1:
            present = {path for path in definition.paths if path in by_path}
            if present and len(present) != len(definition.paths):
                missing = next(path for path in definition.paths if path not in present)
                diagnostics.append(_diagnostic("missing_companion_artifact", selector, context, missing))

    run_ids = {artifact.run_id for artifact in artifacts if artifact.run_id}
    run_ids.update(value for artifact in artifacts for value in _field_values(artifact, "run_id"))
    if context:
        run_ids.discard(context.run_id)
    if len(run_ids) > 1 or (context and run_ids and run_ids != {context.run_id}):
        diagnostics.append(_diagnostic("mixed_run_ids", selector, context))
    dates = {
        value
        for artifact in artifacts
        for value in _field_values(artifact, "as_of_date")
    }
    if context:
        dates.discard(context.as_of_date.isoformat())
    if len(dates) > 1 or (context and dates):
        diagnostics.append(_diagnostic("mixed_evaluation_dates", selector, context))
    return sort_diagnostics(diagnostics)


def validate_manifest(
    candidate: PublicationCandidate,
    manifest: dict[str, object],
    measured_artifacts: tuple[EncodedArtifact, ...],
) -> tuple[Diagnostic, ...]:
    diagnostics: list[Diagnostic] = []
    expected_paths = DEFAULT_REPORT_CATALOG.plan(
        candidate.context.request.selector
    ).expected_paths
    entries = manifest.get("artifacts")
    if not isinstance(entries, list) or tuple(item.get("path") for item in entries if isinstance(item, dict)) != expected_paths:
        diagnostics.append(_diagnostic("manifest_artifact_closure_mismatch", candidate.context.request.selector, candidate.context))
        return sort_diagnostics(diagnostics)
    for artifact, entry in zip(measured_artifacts, entries, strict=True):
        if not isinstance(entry, dict):
            diagnostics.append(_diagnostic("invalid_manifest_artifact", candidate.context.request.selector, candidate.context))
            continue
        expected = {
            "path": artifact.logical_path,
            "rows": artifact.rows,
            "bytes": len(artifact.data),
            "sha256": artifact.digest,
            "schema_version": artifact.schema_version,
            "media_type": artifact.media_type,
        }
        if any(entry.get(key) != value for key, value in expected.items()):
            diagnostics.append(_diagnostic("manifest_measured_fact_mismatch", candidate.context.request.selector, candidate.context, artifact.logical_path))
    if manifest.get("run_id") != candidate.context.run_id:
        diagnostics.append(_diagnostic("manifest_run_id_mismatch", candidate.context.request.selector, candidate.context))
    if manifest.get("selector") != candidate.context.request.selector.value:
        diagnostics.append(_diagnostic("manifest_selector_mismatch", candidate.context.request.selector, candidate.context))
    return sort_diagnostics(diagnostics)
