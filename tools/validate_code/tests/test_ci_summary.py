import os
import subprocess
import sys
from pathlib import Path

from tools.validate_code.ci_summary import render_summary


def _job(name: str, conclusion: str | None) -> dict:
    return {
        "name": name,
        "conclusion": conclusion,
        "status": "completed" if conclusion else "in_progress",
        "html_url": "https://github.com/org/repo/actions/runs/1/job/2",
        "started_at": "2026-10-15T09:18:39Z",
        "completed_at": "2026-10-15T09:19:56Z" if conclusion else None,
        "steps": [{"name": "Install dependencies", "conclusion": conclusion}],
    }


def test_summary_shows_failed_setup_job_and_keeps_gate_separate() -> None:
    rendered = render_summary(
        {"python": {"result": "failure"}},
        [_job("python / retirements-v2", "failure"), _job("code-analysis", None)],
        "https://github.com/org/repo/actions/runs/1",
    )

    assert "NOT PASSED" in rendered
    assert "1 checks: 0 passed, 1 failed" in rendered
    assert "Install dependencies" in rendered
    assert rendered.index("Attention required") < rendered.index("## Categories")
    assert "1m 17s" in rendered
    assert "Open job" in rendered
    assert "validation-*" in rendered
    assert "in_progress" not in rendered


def test_summary_does_not_count_skipped_cancelled_or_running_jobs_as_passed() -> None:
    rendered = render_summary(
        {"static": {"result": "cancelled"}},
        [_job("lint", "skipped"), _job("tests", "cancelled"), _job("tf", None)],
        "https://github.com/org/repo/actions/runs/1",
    )

    assert "NOT PASSED" in rendered
    assert (
        "3 checks: 0 passed, 0 failed, 1 cancelled, 2 other/not completed" in rendered
    )


def test_summary_keeps_category_results_when_api_details_are_unavailable() -> None:
    rendered = render_summary(
        {"static": {"result": "success"}},
        [],
        "https://github.com/org/repo/actions/runs/1",
    )

    assert "PASS - All validation categories succeeded" in rendered
    assert "Job details are unavailable" in rendered
    assert "| static | **success** |" in rendered


def test_summary_escapes_job_names_and_orders_checks() -> None:
    rendered = render_summary(
        {"static": {"result": "success"}},
        [_job("z | <script>", "success"), _job("a", "success")],
        "https://github.com/org/repo/actions/runs/1",
    )

    assert "2 checks: 2 passed" in rendered
    assert "z &#124; &lt;script&gt;" in rendered
    assert rendered.index("| a |") < rendered.index("| z &#124;")


def test_summary_cli_preserves_results_when_jobs_file_is_unavailable(
    tmp_path: Path,
) -> None:
    environment = {
        **os.environ,
        "VALIDATION_RESULTS": '{"python":{"result":"failure"}}',
        "GITHUB_SERVER_URL": "https://github.com",
        "GITHUB_REPOSITORY": "org/repo",
        "GITHUB_RUN_ID": "1",
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.validate_code.ci_summary",
            "--jobs",
            str(tmp_path / "missing.json"),
        ],
        env=environment,
        cwd=Path(__file__).resolve().parents[3],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "NOT PASSED" in result.stdout
    assert "Job details are unavailable" in result.stdout
    assert "https://github.com/org/repo/actions/runs/1" in result.stdout
