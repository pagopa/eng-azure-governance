from __future__ import annotations

import json
from pathlib import Path

from src.comitato.comitato_azure_retirements.libs.debug_log import DebugRunLogger


def test_debug_logger_writes_jsonl_with_required_fields(tmp_path: Path) -> None:
    log_file = tmp_path / "azure_retirements_debug.log"
    logger = DebugRunLogger(file_path=log_file, run_id="run-1")

    logger.info("collector_start", "Collector started", subscription_id="sub-1", retries=0)
    logger.warning("collector_warning", "Collector warning", error="HTTP 429")
    logger.close()

    lines = [line for line in log_file.read_text(encoding="utf-8").splitlines() if line]
    assert len(lines) == 2

    first = json.loads(lines[0])
    second = json.loads(lines[1])

    assert first["run_id"] == "run-1"
    assert first["event"] == "collector_start"
    assert first["severity"] == "info"
    assert first["context"]["subscription_id"] == "sub-1"
    assert first["timestamp_utc"].endswith("Z")

    assert second["event"] == "collector_warning"
    assert second["severity"] == "warning"
    assert second["context"]["error"] == "HTTP 429"
