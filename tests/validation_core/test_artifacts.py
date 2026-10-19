from __future__ import annotations

import json
from pathlib import Path

from tools.validation_core import (
    CommandEvidence,
    RepositoryDelta,
    RepositorySnapshot,
    RunContext,
    RunReport,
    UnitResult,
    ValidationUnit,
)
from tools.validation_core.artifacts import write_run_result, write_unit_log


def _report(tmp_path: Path) -> RunReport:
    unit = ValidationUnit("python", "Python checks", lambda _context: 1)
    result = UnitResult(
        unit,
        1,
        0.25,
        commands=(
            CommandEvidence(
                "tool --token=artifact-secret",
                1,
                stdout="Authorization: Bearer artifact-secret",
                stderr="secret=artifact-secret",
                duration_seconds=0.25,
            ),
        ),
        artifacts=("python.log",),
        status="failed",
        queue_seconds=0.05,
        category="python",
    )
    before = RepositorySnapshot(tmp_path, "main", "before", True, "before-digest")
    after = RepositorySnapshot(tmp_path, "main", "after", False, "after-digest")
    delta = RepositoryDelta(
        True, False, True, True, True, "before-digest", "after-digest"
    )
    return RunReport(
        request="validate-code --token=artifact-secret",
        selectors=("python",),
        planned_units=("python",),
        results=(result,),
        context=RunContext(tmp_path, tmp_path / "tmp", False, False),
        concurrency=2,
        fail_fast=False,
        artifact_root=tmp_path / "artifacts",
        tool_versions={"python": "3.13"},
        repository_before=before,
        repository_after=after,
        repository_delta=delta,
        wall_clock_seconds=0.3,
        serial_equivalent_seconds=0.25,
        queue_seconds=0.05,
        category_durations={"python": 0.25},
        status_counts={"failed": 1},
        problems=("python: exit code 1",),
        next_actions=("inspect python",),
        artifacts=("python.log",),
    )


def test_write_run_result_is_versioned_atomic_and_redacted(tmp_path: Path) -> None:
    path = tmp_path / "result.json"

    written = write_run_result(_report(tmp_path), path)

    assert written == path
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "validation-run/v1"
    assert payload["wall_clock_seconds"] == 0.3
    assert payload["serial_equivalent_seconds"] == 0.25
    assert payload["repository_delta"]["changed"] is True
    assert payload["units"][0]["status"] == "failed"
    assert "artifact-secret" not in path.read_text(encoding="utf-8")
    assert not path.with_name(path.name + ".tmp").exists()


def test_write_unit_log_redacts_and_keeps_reference_inside_artifact_root(
    tmp_path: Path,
) -> None:
    artifact_dir = tmp_path / "artifacts"

    reference = write_unit_log(
        "python/actions",
        "Authorization: Bearer log-secret\n" + ("x" * 20_000),
        artifact_dir,
    )

    assert reference == artifact_dir / "unit-python-actions.log"
    assert reference.is_file()
    content = reference.read_text(encoding="utf-8")
    assert "log-secret" not in content
    assert len(content) <= 12_000
    assert reference.resolve().is_relative_to(artifact_dir.resolve())
