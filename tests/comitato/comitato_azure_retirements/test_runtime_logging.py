from __future__ import annotations

from io import StringIO
from pathlib import Path

from rich.console import Console

from src.comitato.comitato_azure_retirements.libs.arm_client import ArmRequestTrace
from src.comitato.comitato_azure_retirements.libs.runtime_logging import (
    ExecutionReporter,
)


def build_reporter(*, verbose: bool = False) -> tuple[ExecutionReporter, StringIO]:
    buffer = StringIO()
    console = Console(file=buffer, color_system=None, force_terminal=False, width=120)
    return ExecutionReporter(verbose=verbose, console=console), buffer


def test_reporter_banner_and_sections_include_expected_labels() -> None:
    reporter, buffer = build_reporter(verbose=True)

    reporter.banner(
        run_id="run-1",
        mode="live",
        scope_mode="subscriptions",
        output_dir=Path("/tmp/output"),
        subscriptions=["sub-1"],
        management_groups=[],
        write_raw_jsonl=True,
    )
    reporter.section("🔐", "Authentication", "Prepare Azure access")
    reporter.step("Requesting token")

    output = buffer.getvalue()
    assert "Azure Retirements Export" in output
    assert "Authentication" in output
    assert "Requesting token" in output


def test_reporter_logs_retry_warning() -> None:
    reporter, buffer = build_reporter()

    reporter.observe_request(
        ArmRequestTrace(
            method="GET",
            url="https://management.azure.com/subscriptions/sub-1/providers/Microsoft.ResourceHealth/events",
            status_code=200,
            retry_count=2,
        )
    )

    assert "HTTP retry applied 2 time(s)" in buffer.getvalue()


def test_reporter_summary_renders_tables() -> None:
    reporter, buffer = build_reporter()

    reporter.summary(
        output_dir=Path("/tmp/output"),
        counts_by_file={"a.tsv": 1},
        counts_by_source={"advisor": 2},
        diagnostic_summary={"info": 1, "warning": 0, "error": 0},
    )

    output = buffer.getvalue()
    assert "Run Summary" in output
    assert "a.tsv" in output
    assert "advisor" in output


def test_subscription_progress_renders_bar_updates() -> None:
    reporter, buffer = build_reporter()

    with reporter.subscription_progress("Advisor recommendations", 2) as update:
        update("sub-1", 1, 2, "ok", None)
        update("sub-2", 2, 2, "warning", "HTTP 502")

    output = buffer.getvalue()
    assert "Advisor recommendations" in output
    assert "100%" in output


def test_problem_determination_report_renders_rows() -> None:
    reporter, buffer = build_reporter()

    reporter.problem_determination_report(
        "Problem Determination",
        [
            {
                "collector": "advisor_recommendations",
                "subscription": "sub-1",
                "severity": "warning",
                "detail": "HTTP 502",
            }
        ],
    )

    output = buffer.getvalue()
    assert "Problem Determination" in output
    assert "advisor_recommendations" in output
    assert "sub-1" in output
    assert "warning" in output
