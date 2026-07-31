from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

from rich.console import Console

from src.comitato.comitato_azure_retirements_v2.config import RuntimeLoggingSettings
from src.comitato.comitato_azure_retirements_v2.ports import RuntimeEvent
from src.comitato.comitato_azure_retirements_v2.runtime_logging import (
    RuntimeReporter,
    TextRunLogger,
    build_debug_log_path,
)


def test_build_debug_log_path_uses_exports_month_partition(tmp_path: Path) -> None:
    started_at = datetime(2026, 7, 31, 14, 22, tzinfo=timezone.utc)

    assert build_debug_log_path(tmp_path, "run-1", started_at=started_at) == (
        tmp_path / "2026" / "07" / "202607311422_run-1_debug.log"
    )


def test_text_logger_writes_sorted_human_context(tmp_path: Path) -> None:
    event = RuntimeEvent(
        level="INFO",
        event="acquisition_completed",
        message="Advisor acquisition completed",
        run_id="run-1",
        context={"records": 42, "report": "advisor"},
    )
    logger = TextRunLogger(tmp_path / "run.log", level="INFO")

    logger.emit(event)
    logger.close()

    content = (tmp_path / "run.log").read_text(encoding="utf-8")
    assert " | INFO | Advisor acquisition completed | " in content
    assert "event=acquisition_completed" in content
    assert "run_id=run-1" in content
    assert content.index("records=42") < content.index("report=advisor")
    assert not content.lstrip().startswith("{")


def test_text_logger_redacts_sensitive_context_and_query_strings(tmp_path: Path) -> None:
    logger = TextRunLogger(tmp_path / "run.log", level="INFO")
    logger.emit(
        RuntimeEvent(
            "WARNING",
            "http_retry",
            "Retrying request",
            "run-1",
            {
                "url": "https://management.azure.com/resource?api-version=secret",
                "Authorization": "Bearer hidden-token",
                "response_body": "private body",
            },
        )
    )
    logger.close()

    content = (tmp_path / "run.log").read_text(encoding="utf-8")
    assert "management.azure.com/resource" in content
    assert "api-version=secret" not in content
    assert "hidden-token" not in content
    assert "private body" not in content


def test_text_logger_exception_includes_traceback(tmp_path: Path) -> None:
    logger = TextRunLogger(tmp_path / "run.log", include_traceback=True)

    try:
        raise RuntimeError("expected failure")
    except RuntimeError as error:
        logger.exception("run_failed", "Run failed", "run-1", error)
    finally:
        logger.close()

    content = (tmp_path / "run.log").read_text(encoding="utf-8")
    assert "Traceback (most recent call last)" in content
    assert "RuntimeError: expected failure" in content


def test_disabled_text_logger_creates_no_file_or_parent(tmp_path: Path) -> None:
    file_path = tmp_path / "nested" / "run.log"
    logger = TextRunLogger(file_path, enabled=False)

    logger.emit(RuntimeEvent("INFO", "run_started", "Run started", "run-1"))
    logger.close()

    assert not file_path.exists()
    assert not file_path.parent.exists()


def test_human_reporter_renders_v1_style_sections_and_summary(tmp_path: Path) -> None:
    stream = StringIO()
    reporter = RuntimeReporter(
        settings=RuntimeLoggingSettings(output_format="human"),
        runtime_root=tmp_path,
        human_console=True,
        console=Console(file=stream, color_system=None, force_terminal=False, width=120),
        now=lambda: datetime(2026, 7, 31, 14, 22, tzinfo=timezone.utc),
    )

    reporter.emit(RuntimeEvent("INFO", "run_started", "Run started", "run-1", {"report": "all"}))
    reporter.emit(RuntimeEvent("INFO", "scope_resolved", "Scope resolved", "run-1", {"subscriptions": 2}))
    reporter.emit(RuntimeEvent("INFO", "run_completed", "Run completed", "run-1", {"artifacts": 6}))
    reporter.close()

    output = stream.getvalue()
    assert "Azure Retirements Export" in output
    assert "Scope" in output
    assert "Run Summary" in output
    assert "run-1" in output
    assert list((tmp_path / "2026" / "07").glob("*_debug.log"))


def test_non_tty_reporter_never_writes_human_console(tmp_path: Path) -> None:
    stream = StringIO()
    reporter = RuntimeReporter(
        settings=RuntimeLoggingSettings(output_format="human"),
        runtime_root=tmp_path,
        human_console=False,
        console=Console(file=stream),
        now=lambda: datetime(2026, 7, 31, 14, 22, tzinfo=timezone.utc),
    )
    reporter.emit(RuntimeEvent("INFO", "run_started", "Run started", "run-1"))
    reporter.close()

    assert stream.getvalue() == ""
    assert list((tmp_path / "2026" / "07").glob("*_debug.log"))


def test_reporter_filters_console_level_and_renders_verbose_unknown_events(
    tmp_path: Path,
) -> None:
    stream = StringIO()
    reporter = RuntimeReporter(
        settings=RuntimeLoggingSettings(
            output_format="human",
            console_level="WARNING",
            verbose=True,
        ),
        runtime_root=tmp_path,
        human_console=True,
        console=Console(file=stream, color_system=None, force_terminal=False, width=120),
    )

    reporter.emit(RuntimeEvent("INFO", "run_started", "hidden info", "run-1"))
    reporter.emit(RuntimeEvent("WARNING", "mystery_event", "visible warning", "run-1"))
    reporter.close()

    output = stream.getvalue()
    assert "hidden info" not in output
    assert "mystery_event" in output


def test_reporter_disabled_debug_logging_creates_no_file(tmp_path: Path) -> None:
    reporter = RuntimeReporter(
        settings=RuntimeLoggingSettings(debug_log_enabled=False),
        runtime_root=tmp_path,
        human_console=False,
    )

    reporter.emit(RuntimeEvent("INFO", "run_started", "Run started", "run-1"))
    reporter.close()

    assert list(tmp_path.rglob("*.log")) == []


def test_reporter_exception_writes_traceback_without_sensitive_context(tmp_path: Path) -> None:
    reporter = RuntimeReporter(
        settings=RuntimeLoggingSettings(),
        runtime_root=tmp_path,
        human_console=False,
    )
    reporter.emit(RuntimeEvent("INFO", "run_started", "Run started", "run-1"))

    try:
        raise RuntimeError("private body Bearer hidden-token")
    except RuntimeError as error:
        reporter.exception(error)
    finally:
        reporter.close()

    log_files = list(tmp_path.rglob("*.log"))
    assert len(log_files) == 1
    content = log_files[0].read_text(encoding="utf-8")
    assert "Traceback (most recent call last)" in content
    assert "hidden-token" not in content
    assert "private body" not in content