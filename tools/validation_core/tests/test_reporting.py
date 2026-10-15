from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools.validation_core import (
    CommandEvidence,
    RepositorySnapshot,
    RunContext,
    RunReport,
    UnitResult,
    ValidationUnit,
)
from tools.validation_core.events import EventSink
from tools.validation_core.reporting import render_report, render_run


def _report(tmp_path: Path) -> RunReport:
    units = [
        ValidationUnit("passed", "Passed", lambda _context: 0),
        ValidationUnit("skipped", "Skipped", lambda _context: 0),
        ValidationUnit("cancelled", "Cancelled", lambda _context: 0),
        ValidationUnit("incomplete", "Incomplete", lambda _context: 1),
    ]
    results = tuple(
        UnitResult(
            unit,
            1 if unit.unit_id == "incomplete" else 0,
            0.1,
            commands=(
                CommandEvidence(
                    "check --password=report-secret",
                    0,
                    stdout="token=report-secret",
                ),
            ),
            status=("incomplete" if unit.unit_id == "incomplete" else unit.unit_id),
        )
        for unit in units
    )
    before = RepositorySnapshot(tmp_path, "main", "abc", True, "before")
    after = RepositorySnapshot(tmp_path, "main", "abc", True, "before")
    return RunReport(
        request="validate",
        selectors=("all",),
        planned_units=tuple(unit.unit_id for unit in units),
        results=results,
        context=RunContext(tmp_path, tmp_path / "tmp", False, False),
        concurrency=1,
        fail_fast=False,
        repository_before=before,
        repository_after=after,
        repository_delta=before.delta(after),
        wall_clock_seconds=0.4,
        serial_equivalent_seconds=0.4,
        queue_seconds=0.02,
        category_durations={"default": 0.4},
        status_counts={"passed": 1, "skipped": 1, "cancelled": 1, "incomplete": 1},
        problems=("incomplete: exit code 1",),
        next_actions=("inspect incomplete",),
    )


@pytest.mark.parametrize("output_format", ["terminal", "ci", "json", "markdown"])
def test_render_run_has_explicit_machine_and_human_projections(
    tmp_path: Path, output_format: str
) -> None:
    rendered = render_run(_report(tmp_path), output_format)

    assert rendered
    if output_format == "json":
        payload = json.loads(rendered)
        assert payload["schema_version"] == "validation-run/v1"
        assert payload["planned_units"] == [
            "passed",
            "skipped",
            "cancelled",
            "incomplete",
        ]
        assert payload["status_counts"]["cancelled"] == 1
        assert payload["repository"]["before"]["branch"] == "main"
        assert payload["repository_delta"]["changed"] is False
    else:
        assert "report-secret" not in rendered
        assert "passed" in rendered
        assert "skipped" in rendered
        assert "cancelled" in rendered
        assert "incomplete" in rendered


def test_ci_keeps_failed_command_diagnostics_after_truncated_events(
    tmp_path: Path,
) -> None:
    unit = ValidationUnit("python:retirements-v2", "Retirements", lambda _context: 1)
    output = "." * 600 + "\nFAILED tests/test_entrypoint.py::test_tty\ntoken=ci-secret"
    sink = EventSink()
    sink.emit(
        phase="command-complete",
        unit_id=unit.unit_id,
        status="failed",
        detail=output,
    )
    report = RunReport(
        results=(
            UnitResult(
                unit,
                1,
                0.1,
                status="failed",
                commands=(CommandEvidence("pytest -q", 1, stdout=output),),
            ),
        ),
        events=tuple(sink.events),
        context=RunContext(tmp_path, tmp_path / "tmp", False, False),
    )

    rendered = render_run(report, "ci")

    assert "FAILED tests/test_entrypoint.py::test_tty" in rendered
    assert "ci-secret" not in rendered
    assert "phase=final status=failed" in rendered


def test_render_run_json_keeps_unit_order_and_timing_labels_distinct(
    tmp_path: Path,
) -> None:
    payload = json.loads(render_run(_report(tmp_path), "json"))

    assert [unit["unit_id"] for unit in payload["units"]] == [
        "passed",
        "skipped",
        "cancelled",
        "incomplete",
    ]
    assert payload["wall_clock_seconds"] == 0.4
    assert payload["serial_equivalent_seconds"] == 0.4
    assert payload["queue_seconds"] == 0.02


def test_render_report_preserves_validation_exit_when_renderer_fails(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    from tools.validation_core import reporting

    def fail_renderer(_report, _format):
        raise RuntimeError("renderer failed")

    monkeypatch.setattr(reporting, "render_run", fail_renderer)
    report = _report(tmp_path)

    exit_code = render_report(report.results, report.context)

    assert exit_code == 1
    assert "renderer failed" in capsys.readouterr().err


def test_render_run_dense_terminal_groups_python_failure_and_observed_diagnostics(
    tmp_path: Path,
) -> None:
    unit = ValidationUnit(
        "python:integration", "Python shard integration", lambda _context: 1
    )
    result = UnitResult(
        unit,
        1,
        2.5,
        commands=(
            CommandEvidence(
                "python -m pytest -q tests/test_policy.py",
                1,
                stderr=(
                    "FAILED tests/test_policy.py::test_policy - AssertionError\n"
                    "E       assert 'Allow' == 'Deny'\n"
                    "E       expected: Allow\n"
                    "E       actual: Deny\n"
                    "tests/test_policy.py:117: AssertionError\n"
                ),
            ),
        ),
        status="failed",
        category="python",
    )
    report = RunReport(
        request="python --group integration",
        planned_units=(unit.unit_id,),
        results=(result,),
        context=RunContext(tmp_path, tmp_path / "tmp", False, False),
        problems=("python:integration: exit code 1",),
    )

    rendered = render_run(report, "terminal")

    assert "❌ [01/01] [PYTHON] integration" in rendered
    assert "tests/test_policy.py:117" in rendered
    assert "expected: Allow" in rendered
    assert "actual: Deny" in rendered
    assert "python -m pytest -q tests/test_policy.py" in rendered


def test_extract_diagnostics_handles_repeated_slash_prefix_without_backtracking() -> (
    None
):
    script = (
        "from tools.validation_core.reporting import _extract_diagnostics\n"
        "diagnostics = _extract_diagnostics({'commands': [{'stderr': '!/' * 40}]})\n"
        "assert diagnostics[0]['location'] == ''\n"
    )
    try:
        completed = subprocess.run(
            [sys.executable, "-c", script],
            cwd=Path(__file__).resolve().parents[3],
            capture_output=True,
            check=False,
            text=True,
            timeout=2.0,
        )
    except subprocess.TimeoutExpired:
        pytest.fail("diagnostic extraction backtracked on repeated '!/' segments")

    assert completed.returncode == 0, completed.stderr


def test_render_run_terraform_failure_and_unknown_output_use_bounded_observed_context(
    tmp_path: Path,
) -> None:
    terraform = ValidationUnit(
        "terraform:shared", "Terraform lane shared", lambda _context: 1
    )
    fallback = ValidationUnit("static:lint", "Static lint", lambda _context: 1)
    results = (
        UnitResult(
            terraform,
            1,
            3.0,
            commands=(
                CommandEvidence(
                    "terraform -chdir=src/shared test -no-color",
                    1,
                    stderr=(
                        "Error: Test assertion failed\n"
                        "on tests/catalog.tftest.hcl line 42\n"
                        "resource is aws_iam_policy.shared\n"
                    ),
                ),
            ),
            status="failed",
            category="terraform",
        ),
        UnitResult(
            fallback,
            1,
            1.0,
            commands=(
                CommandEvidence("lint", 1, stderr="opaque failure\n" + "x\n" * 20),
            ),
            status="failed",
            category="static",
        ),
    )
    report = RunReport(
        planned_units=("terraform:shared", "static:lint"),
        results=results,
        context=RunContext(tmp_path, tmp_path / "tmp", False, False),
        problems=("terraform:shared: exit code 1", "static:lint: exit code 1"),
    )

    rendered = render_run(report, "terminal")

    assert "[TERRAFORM] shared" in rendered
    assert "tests/catalog.tftest.hcl:42" in rendered
    assert "Error: Test assertion failed" in rendered
    assert "opaque failure" in rendered
    assert "[STATIC] lint" in rendered


def test_render_run_compact_is_terminal_only_and_machine_formats_win(
    tmp_path: Path,
) -> None:
    report = _report(tmp_path)
    compact_context = RunContext(tmp_path, tmp_path / "tmp", False, False, compact=True)
    compact_report = report.__class__(**{**report.__dict__, "context": compact_context})

    compact = render_run(compact_report, "terminal")
    payload = json.loads(render_run(compact_report, "json"))

    assert "── PREFLIGHT" not in compact
    assert "passed" in compact
    assert "validation-run/v1" in json.dumps(payload)
    assert "── PREFLIGHT" not in render_run(compact_report, "ci")


def test_render_run_keeps_raw_diagnostics_bounded_and_does_not_invent_fields(
    tmp_path: Path,
) -> None:
    unit = ValidationUnit(
        "python:integration", "Python shard integration", lambda _context: 1
    )
    result = UnitResult(
        unit,
        1,
        2.5,
        commands=(
            CommandEvidence(
                "python -m pytest -q tests/test_policy.py",
                1,
                stderr=(
                    "FAILED tests/test_policy.py::test_policy - AssertionError\n"
                    "observed: [Allow]\n"
                    "hosted path: /runner/_work/_temp/secret\n"
                    "line 1\nline 2\nline 3\nline 4\nline 5\n"
                ),
            ),
        ),
        status="failed",
        category="python",
    )
    report = RunReport(
        request="python --group integration",
        planned_units=(unit.unit_id,),
        results=(result,),
        context=RunContext(tmp_path, tmp_path / "tmp", False, False),
        problems=("python:integration: exit code 1",),
    )

    rendered = render_run(report, "terminal")

    assert "FAILED tests/test_policy.py::test_policy - AssertionError" in rendered
    assert "hosted path: /runner/_work/_temp/secret" in rendered
    assert "expected:" not in rendered
    assert "actual:" not in rendered
    assert rendered.count("line ") <= 5
    assert "No safe local rerun is available" in rendered


def test_render_run_does_not_emit_hosted_temp_path_as_rerun(tmp_path: Path) -> None:
    unit = ValidationUnit(
        "python:integration", "Python shard integration", lambda _context: 1
    )
    result = UnitResult(
        unit,
        1,
        1.0,
        commands=(
            CommandEvidence("/runner/_work/_temp/run-tests", 1, stderr="failure"),
        ),
        status="failed",
        category="python",
    )
    report = RunReport(
        request="/runner/_work/_temp/run-tests",
        planned_units=(unit.unit_id,),
        results=(result,),
        context=RunContext(tmp_path, tmp_path / "tmp", False, False),
        problems=("python:integration: exit code 1",),
    )

    rendered = render_run(report, "terminal")

    assert "rerun: /runner/_work/_temp/run-tests" not in rendered
    assert "No safe local rerun is available" in rendered
