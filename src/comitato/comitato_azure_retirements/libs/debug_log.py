"""Structured debug logging for Azure retirements runtime traces."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _normalize(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _normalize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_normalize(item) for item in value]
    return str(value)


class _JsonLineFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp_utc": datetime.fromtimestamp(record.created, timezone.utc)
            .replace(microsecond=0)
            .strftime("%Y-%m-%dT%H:%M:%SZ"),
            "severity": record.levelname.lower(),
            "message": record.getMessage(),
            "run_id": getattr(record, "run_id", ""),
            "event": getattr(record, "event", ""),
            "thread": record.threadName,
        }
        context = getattr(record, "context", None)
        if isinstance(context, dict):
            payload["context"] = _normalize(context)
        return json.dumps(payload, ensure_ascii=True, sort_keys=True)


class DebugRunLogger:
    """Thread-safe JSONL logger with stable run metadata."""

    def __init__(self, *, file_path: Path, run_id: str) -> None:
        self._file_path = file_path
        self._run_id = run_id
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

        logger_name = f"comitato.azure_retirements.{run_id}"
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False

        # Keep one handler per run logger to avoid duplicate lines in repeated test imports.
        self._logger.handlers.clear()
        handler = logging.FileHandler(self._file_path, encoding="utf-8")
        handler.setFormatter(_JsonLineFormatter())
        self._logger.addHandler(handler)

    @property
    def file_path(self) -> Path:
        return self._file_path

    def info(self, event: str, message: str, **context: Any) -> None:
        self._emit(logging.INFO, event=event, message=message, context=context)

    def warning(self, event: str, message: str, **context: Any) -> None:
        self._emit(logging.WARNING, event=event, message=message, context=context)

    def error(self, event: str, message: str, **context: Any) -> None:
        self._emit(logging.ERROR, event=event, message=message, context=context)

    def close(self) -> None:
        for handler in list(self._logger.handlers):
            handler.flush()
            handler.close()
            self._logger.removeHandler(handler)

    def _emit(
        self, level: int, *, event: str, message: str, context: dict[str, Any]
    ) -> None:
        self._logger.log(
            level,
            message,
            extra={
                "run_id": self._run_id,
                "event": event,
                "context": context,
            },
        )
