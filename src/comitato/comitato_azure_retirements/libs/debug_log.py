"""Human-readable debug logging for Azure retirements runtime traces."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _text_value(value: Any) -> str:
    if value is None:
        return "none"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (str, int, float)):
        return str(value).replace("\n", "\\n")
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        entries = ", ".join(
            f"{key}: {_text_value(item)}"
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        )
        return f"{{{entries}}}"
    if isinstance(value, (list, tuple, set)):
        return f"[{', '.join(_text_value(item) for item in value)}]"
    return str(value)


class _TextLineFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = (
            datetime.fromtimestamp(record.created, timezone.utc)
            .replace(microsecond=0)
            .strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        fields = [
            timestamp,
            record.levelname,
            record.getMessage(),
            f"event={getattr(record, 'event', '')}",
            f"run_id={getattr(record, 'run_id', '')}",
            f"thread={record.threadName}",
        ]
        context = getattr(record, "context", None)
        if isinstance(context, dict):
            fields.extend(
                f"{key}={_text_value(value)}" for key, value in sorted(context.items())
            )
        rendered = " | ".join(fields)
        if record.exc_info:
            rendered = f"{rendered}\n{self.formatException(record.exc_info)}"
        return rendered


class DebugRunLogger:
    """Thread-safe text logger with stable run metadata."""

    def __init__(
        self,
        *,
        file_path: Path,
        run_id: str,
        enabled: bool = True,
        level: str = "INFO",
        include_traceback: bool = True,
    ) -> None:
        self._file_path = file_path
        self._run_id = run_id
        self._enabled = enabled
        self._include_traceback = include_traceback

        logger_name = f"comitato.azure_retirements.{run_id}"
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(level)
        self._logger.propagate = False

        self._logger.handlers.clear()
        if self._enabled:
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            handler = logging.FileHandler(self._file_path, encoding="utf-8")
            handler.setFormatter(_TextLineFormatter())
            self._logger.addHandler(handler)

    @property
    def file_path(self) -> Path:
        return self._file_path

    @property
    def enabled(self) -> bool:
        return self._enabled

    def info(self, event: str, message: str, **context: Any) -> None:
        self._emit(logging.INFO, event=event, message=message, context=context)

    def warning(self, event: str, message: str, **context: Any) -> None:
        self._emit(logging.WARNING, event=event, message=message, context=context)

    def error(self, event: str, message: str, **context: Any) -> None:
        self._emit(logging.ERROR, event=event, message=message, context=context)

    def exception(
        self,
        event: str,
        message: str,
        exc: BaseException,
        **context: Any,
    ) -> None:
        context = {
            **context,
            "exception_type": type(exc).__name__,
            "error": str(exc),
        }
        exc_info = (
            (type(exc), exc, exc.__traceback__) if self._include_traceback else None
        )
        self._emit(
            logging.ERROR,
            event=event,
            message=message,
            context=context,
            exc_info=exc_info,
        )

    def close(self) -> None:
        for handler in list(self._logger.handlers):
            handler.flush()
            handler.close()
            self._logger.removeHandler(handler)

    def _emit(
        self,
        level: int,
        *,
        event: str,
        message: str,
        context: dict[str, Any],
        exc_info: tuple[type[BaseException], BaseException, Any] | None = None,
    ) -> None:
        if not self._enabled:
            return
        self._logger.log(
            level,
            message,
            exc_info=exc_info,
            extra={
                "run_id": self._run_id,
                "event": event,
                "context": context,
            },
        )
