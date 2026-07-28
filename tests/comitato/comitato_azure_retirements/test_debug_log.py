from __future__ import annotations

import re
from pathlib import Path

from src.comitato.comitato_azure_retirements.libs.debug_log import DebugRunLogger


def test_debug_logger_writes_human_readable_text_with_context(tmp_path: Path) -> None:
    log_file = tmp_path / "azure_retirements_debug.log"
    logger = DebugRunLogger(file_path=log_file, run_id="run-1")

    logger.info(
        "collector_start", "Collector started", subscription_id="sub-1", retries=0
    )
    logger.warning("collector_warning", "Collector warning", error="HTTP 429")
    logger.close()

    lines = [line for line in log_file.read_text(encoding="utf-8").splitlines() if line]
    assert len(lines) == 2
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z \| INFO \|", lines[0])
    assert "event=collector_start" in lines[0]
    assert "run_id=run-1" in lines[0]
    assert "subscription_id=sub-1" in lines[0]
    assert "retries=0" in lines[0]
    assert not lines[0].startswith("{")
    assert "WARNING" in lines[1]
    assert "error=HTTP 429" in lines[1]


def test_debug_logger_exception_includes_traceback_and_context(
    tmp_path: Path,
) -> None:
    log_file = tmp_path / "azure_retirements_debug.log"
    logger = DebugRunLogger(
        file_path=log_file,
        run_id="run-1",
        include_traceback=True,
    )

    try:
        raise ValueError("invalid payload")
    except ValueError as exc:
        logger.exception(
            "run_failed",
            "Unhandled runtime failure",
            exc,
            stage="raw",
        )
    logger.close()

    content = log_file.read_text(encoding="utf-8")
    assert "event=run_failed" in content
    assert "stage=raw" in content
    assert "exception_type=ValueError" in content
    assert "Traceback (most recent call last):" in content
    assert "ValueError: invalid payload" in content
