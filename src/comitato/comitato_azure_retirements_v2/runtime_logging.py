"""Runtime observation sinks for the Azure retirements v2 runner."""

from __future__ import annotations

import logging
import re
import traceback
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from .config import RuntimeLoggingSettings
from .ports import RuntimeEvent
from .publication.model import RunResult


_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
_SENSITIVE_KEY_PARTS = (
    "authorization",
    "access_token",
    "api_key",
    "bearer",
    "cookie",
    "credential",
    "password",
    "payload",
    "request_body",
    "request_headers",
    "response_body",
    "secret",
    "token",
)
_BEARER_PATTERN = re.compile(r"(?i)\bbearer\s+[^\s,;]+")
_TOKEN_PARAMETER_PATTERN = re.compile(
    r"(?i)(\b(?:access_token|api[_-]?key|token|sig)=)[^\s&#,;]+"
)
_BODY_PATTERN = re.compile(
    r"(?i)\b(?:private|request|response)?[\s_-]*body\b[^\n]*"
)
_MAX_CONTEXT_VALUE_LENGTH = 1000


def build_debug_log_path(
    runtime_root: Path,
    run_id: str,
    *,
    started_at: datetime,
) -> Path:
    timestamp = started_at
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    timestamp = timestamp.astimezone(timezone.utc)
    return (
        runtime_root
        / timestamp.strftime("%Y")
        / timestamp.strftime("%m")
        / f"{timestamp:%Y%m%d%H%M}_{run_id}_debug.log"
    )


class _UtcFormatter(logging.Formatter):
    converter = staticmethod(lambda value: datetime.fromtimestamp(value, tz=timezone.utc).timetuple())

    def formatException(self, exc_info: tuple[type[BaseException], BaseException, Any]) -> str:
        return _redact_free_text(super().formatException(exc_info))


class TextRunLogger:
    def __init__(
        self,
        file_path: Path,
        *,
        level: str = "INFO",
        include_traceback: bool = True,
        enabled: bool = True,
    ) -> None:
        self.file_path = file_path
        self.include_traceback = include_traceback
        self.enabled = enabled
        self._level = _LEVELS.get(level.upper(), logging.INFO)
        self._logger = logging.getLogger(f"comitato.azure_retirements_v2.runtime.{id(self)}")
        self._logger.setLevel(self._level)
        self._logger.propagate = False
        self._handler: logging.FileHandler | None = None

    def emit(self, event: RuntimeEvent) -> None:
        if not self.enabled:
            return
        level = _LEVELS.get(event.level.upper(), logging.INFO)
        context = _format_context(event.context)
        self._write(
            level,
            _escape_text(event.message),
            event=event.event,
            run_id=event.run_id,
            context=context,
        )

    def exception(
        self,
        event: str,
        message: str,
        run_id: str,
        error: BaseException,
        **context: object,
    ) -> None:
        if not self.enabled:
            return
        self._write(
            logging.ERROR,
            _escape_text(message),
            event=event,
            run_id=run_id,
            context=_format_context(
                {
                    **context,
                    "error": str(error),
                    "exception_type": type(error).__name__,
                }
            ),
            exc_info=(type(error), error, error.__traceback__)
            if self.include_traceback
            else None,
        )

    def close(self) -> None:
        if self._handler is None:
            return
        self._logger.removeHandler(self._handler)
        self._handler.close()
        self._handler = None

    def _write(
        self,
        level: int,
        message: str,
        *,
        event: str,
        run_id: str,
        context: str,
        exc_info: tuple[type[BaseException], BaseException, Any] | None = None,
    ) -> None:
        if not self._logger.isEnabledFor(level):
            return
        handler = self._ensure_handler()
        if exc_info is not None:
            message = f"{message}\n{_redact_free_text(''.join(traceback.format_exception(*exc_info)))}"
            exc_info = None
        self._logger.log(
            level,
            message,
            extra={
                "runtime_event": _escape_text(event),
                "runtime_run_id": _escape_text(run_id),
                "runtime_context": context,
            },
            exc_info=exc_info,
        )
        handler.flush()

    def _ensure_handler(self) -> logging.FileHandler:
        if self._handler is None:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            handler = logging.FileHandler(self.file_path, encoding="utf-8")
            handler.setFormatter(
                _UtcFormatter(
                    "%(asctime)s | %(levelname)s | %(message)s | "
                    "event=%(runtime_event)s | run_id=%(runtime_run_id)s | "
                    "%(runtime_context)s"
                )
            )
            self._logger.addHandler(handler)
            self._handler = handler
        return self._handler


class RuntimeReporter:
    def __init__(
        self,
        *,
        settings: RuntimeLoggingSettings,
        runtime_root: Path,
        human_console: bool,
        console: Console | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._settings = settings
        self._runtime_root = runtime_root
        self._human_console = human_console
        self._console = console or (
            Console(stderr=True, soft_wrap=True) if human_console else None
        )
        self._now = now or (lambda: datetime.now(timezone.utc))
        self._run_id: str | None = None
        self._started_at: datetime | None = None
        self._text_logger: TextRunLogger | None = None
        self._completed = False
        self._summary_rendered = False
        self._console_level = _LEVELS.get(settings.console_level.upper(), logging.INFO)

    def emit(self, event: RuntimeEvent) -> None:
        self._ensure_text_logger(event.run_id)
        if self._text_logger is not None:
            self._text_logger.emit(event)
        if self._completed and event.event != "run_completed":
            return
        if event.event == "run_completed":
            self._completed = True
        if not self._allows_console(event.level):
            return
        self._render_event(event)

    def exception(self, error: BaseException) -> None:
        run_id = self._run_id or "unknown"
        self._ensure_text_logger(run_id)
        if self._text_logger is not None:
            self._text_logger.exception("run_failed", "Run failed", run_id, error)
        if self._human_console and self._allows_console("ERROR") and self._console is not None:
            self._console.print(
                f"[bold red]Error:[/] {escape(_redact_free_text(str(error)))}"
            )

    def finish(self, result: RunResult) -> None:
        context = getattr(result, "context", None)
        run_id = getattr(context, "run_id", None) or self._run_id or "unknown"
        exit_status = int(getattr(result, "exit_status", 1))
        candidate = getattr(result, "candidate", None)
        artifacts = getattr(candidate, "artifacts", ())
        event_context: dict[str, object] = {
            "artifacts": len(artifacts) if hasattr(artifacts, "__len__") else 0,
            "status": "published" if exit_status == 0 else "failed",
        }
        if not self._completed:
            self.emit(
                RuntimeEvent(
                    "INFO" if exit_status == 0 else "ERROR",
                    "run_completed",
                    "Run completed" if exit_status == 0 else "Run failed",
                    run_id,
                    event_context,
                )
            )
        if self._human_console and not self._summary_rendered and self._allows_console("INFO"):
            self._render_summary(run_id, event_context)

    def close(self) -> None:
        if self._text_logger is not None:
            self._text_logger.close()

    def _ensure_text_logger(self, run_id: str) -> None:
        if self._run_id is None:
            self._run_id = run_id or "unknown"
        if self._started_at is None:
            self._started_at = self._now()
        if self._text_logger is None:
            file_path = build_debug_log_path(
                self._runtime_root,
                self._run_id,
                started_at=self._started_at,
            )
            self._text_logger = TextRunLogger(
                file_path,
                level=self._settings.log_level,
                include_traceback=self._settings.include_traceback,
                enabled=self._settings.debug_log_enabled,
            )

    def _allows_console(self, level: str) -> bool:
        return _LEVELS.get(level.upper(), logging.INFO) >= self._console_level

    def _render_event(self, event: RuntimeEvent) -> None:
        if not self._human_console or self._console is None:
            return
        if event.event == "run_started":
            self._render_banner(event)
            return
        if event.event == "run_completed":
            self._render_summary(event.run_id, event.context)
            return

        title = _SECTION_TITLES.get(event.event)
        if title is not None:
            self._console.rule(f"[bold cyan]{escape(title)}[/bold cyan]")

        if event.level.upper() in {"WARNING", "ERROR", "CRITICAL"}:
            style = "yellow" if event.level.upper() == "WARNING" else "red"
            self._console.print(
                f"[{style}]{escape(event.event)}: {escape(event.message)}[/] "
                f"{escape(_format_context(event.context))}"
            )
            return

        if title is None and self._settings.verbose:
            self._console.print(
                f"• {escape(event.event)}: {escape(event.message)}"
            )
            return
        self._console.print(escape(event.message))

    def _render_banner(self, event: RuntimeEvent) -> None:
        if self._console is None:
            return
        summary = Table.grid(padding=(0, 2))
        summary.add_row("Run ID", escape(event.run_id))
        for key in ("report", "subscriptions", "management_groups"):
            if key in event.context:
                summary.add_row(key.replace("_", " ").title(), escape(str(event.context[key])))
        self._console.print(
            Panel.fit(summary, title="Azure Retirements Export", border_style="cyan")
        )

    def _render_summary(self, run_id: str, context: Mapping[str, object]) -> None:
        if self._console is None:
            return
        self._summary_rendered = True
        self._console.rule("[bold cyan]Run Summary[/bold cyan]")
        summary = Table(show_header=False)
        summary.add_column("Field", style="bold")
        summary.add_column("Value")
        summary.add_row("Run ID", escape(run_id))
        for key in ("status", "artifacts", "diagnostics"):
            if key in context:
                summary.add_row(key.title(), escape(str(context[key])))
        self._console.print(summary)


_SECTION_TITLES = {
    "scope_resolution_started": "Scope",
    "scope_resolved": "Scope",
    "catalog_load_started": "Catalog",
    "catalog_loaded": "Catalog",
    "acquisition_started": "Acquisition",
    "acquisition_completed": "Acquisition",
    "coverage_validation_started": "Validation",
    "coverage_validated": "Validation",
    "artifact_preparation_started": "Artifacts",
    "artifacts_prepared": "Artifacts",
    "publication_started": "Publication",
    "publication_completed": "Publication",
}


def _format_context(context: dict[str, object] | Any) -> str:
    fields: list[str] = []
    for key in sorted(context, key=str):
        value = _safe_context_value(str(key), context[key])
        if value is None:
            continue
        fields.append(f"{_escape_text(str(key))}={value}")
    return " ".join(fields)


def _safe_context_value(key: str, value: object) -> str | None:
    key_lower = key.lower()
    if any(part in key_lower for part in _SENSITIVE_KEY_PARTS):
        return "[REDACTED]"

    text = _escape_text(str(value))
    if key_lower in {"url", "uri", "endpoint"}:
        text = _remove_url_query(text)
    text = _BEARER_PATTERN.sub("Bearer [REDACTED]", text)
    text = _TOKEN_PARAMETER_PATTERN.sub(r"\1[REDACTED]", text)
    text = _redact_free_text(text)
    return text[:_MAX_CONTEXT_VALUE_LENGTH]


def _remove_url_query(value: str) -> str:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return value
    if not parsed.scheme or not parsed.netloc:
        return value
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))


def _escape_text(value: str) -> str:
    return value.replace("\r", "\\r").replace("\n", "\\n")


def _redact_free_text(value: str) -> str:
    value = _BEARER_PATTERN.sub("Bearer [REDACTED]", value)
    value = _TOKEN_PARAMETER_PATTERN.sub(r"\1[REDACTED]", value)
    return _BODY_PATTERN.sub("[REDACTED_BODY]", value)


__all__ = ["RuntimeReporter", "TextRunLogger", "build_debug_log_path"]