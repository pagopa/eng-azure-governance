"""Command-line boundary: parse once, run once, emit safe machine output."""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Sequence

from .config import RuntimeConfig, parse_config
from .domain.diagnostics import Diagnostic, sort_diagnostics
from .ports import RunObserver
from .runtime_logging import RuntimeReporter


_RUNTIME_LOG_ROOT = Path(__file__).resolve().parents[3] / "tmp" / "comitato" / "comitato_azure_retirements_v2" / "exports"


def run_config(config: RuntimeConfig, reporter: RunObserver | None = None) -> Any:
    from .application.composition import build_application

    return build_application(config, observer=reporter).run(config.request)


def build_runtime_reporter(
    config: RuntimeConfig,
    *,
    stderr_is_tty: bool | None = None,
) -> RuntimeReporter:
    if stderr_is_tty is None:
        stderr_is_tty = sys.stderr.isatty()
    human_console = config.logging.output_format == "human" and stderr_is_tty
    runtime_root = config.logging.log_directory or _RUNTIME_LOG_ROOT
    return RuntimeReporter(
        settings=config.logging,
        runtime_root=runtime_root,
        human_console=human_console,
    )


def _result_payload(result: Any) -> Mapping[str, Any]:
    if callable(getattr(result, "to_dict", None)):
        return result.to_dict()
    return {
        "status": "published" if getattr(result, "exit_status", 1) == 0 else "failed",
        "exit_status": getattr(result, "exit_status", 1),
    }


def _diagnostic_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, Diagnostic):
        return value.to_dict()
    if isinstance(value, Mapping):
        return dict(value)
    return {
        "severity": "error",
        "code": "application_error",
        "stage": "validation",
        "report": "",
        "run_id": "",
        "subscription_id": "",
        "record_ref": "",
        "artifact": "",
        "message": "application failed; publication was not changed",
    }


def _diagnostics_payload(error: BaseException) -> bytes:
    values = tuple(getattr(error, "diagnostics", ()))
    dictionaries = [_diagnostic_dict(value) for value in values]
    dictionaries.sort(key=lambda item: tuple(str(item.get(key, "")) for key in ("stage", "code", "subscription_id", "record_ref", "artifact")))
    if not dictionaries:
        dictionaries = [_diagnostic_dict(error)]
    return b"".join(
        (json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        for item in dictionaries
    )


def main(argv: Sequence[str] | None = None) -> int:
    config = parse_config(argv)
    stderr_is_tty = sys.stderr.isatty()
    human_console = config.logging.output_format == "human" and stderr_is_tty
    effective_machine_mode = not human_console
    reporter = build_runtime_reporter(config, stderr_is_tty=stderr_is_tty)
    result: Any = None
    result_error: BaseException | None = None
    diagnostics_error: BaseException | None = None
    success_payload: Mapping[str, Any] | None = None
    try:
        result = run_config(config, reporter=reporter)
        reporter.finish(result)
        if getattr(result, "exit_status", 0) != 0:
            diagnostics_error = RuntimeError("application returned a non-zero result")
            diagnostics_error.diagnostics = getattr(result, "diagnostics", ())  # type: ignore[attr-defined]
            exit_status = int(result.exit_status)
        else:
            success_payload = _result_payload(result)
            exit_status = 0
    except Exception as error:  # translated once at the process boundary
        result_error = error
        exit_status = 1
        try:
            reporter.exception(error)
        except Exception:
            pass
    finally:
        try:
            reporter.close()
        except Exception as error:
            if result_error is None and diagnostics_error is None:
                result_error = error
                success_payload = None
                exit_status = 1

    if effective_machine_mode:
        if result_error is not None:
            sys.stderr.buffer.write(_diagnostics_payload(result_error))
        elif diagnostics_error is not None:
            sys.stderr.buffer.write(_diagnostics_payload(diagnostics_error))
        elif success_payload is not None:
            sys.stdout.write(json.dumps(success_payload, sort_keys=True, separators=(",", ":")) + "\n")
    return exit_status


__all__ = ["build_runtime_reporter", "main", "run_config"]
