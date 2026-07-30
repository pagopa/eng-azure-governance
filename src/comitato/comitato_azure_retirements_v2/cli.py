"""Command-line boundary: parse once, run once, emit safe machine output."""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from typing import Any, Sequence

from .config import RuntimeConfig, parse_config
from .domain.diagnostics import Diagnostic, sort_diagnostics


def run_config(config: RuntimeConfig) -> Any:
    from .application.composition import build_application

    return build_application(config).run(config.request)


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
    try:
        result = run_config(config)
    except Exception as error:  # translated once at the process boundary
        sys.stderr.buffer.write(_diagnostics_payload(error))
        return 1
    if getattr(result, "exit_status", 0) != 0:
        diagnostics = getattr(result, "diagnostics", ())
        error = RuntimeError("application returned a non-zero result")
        error.diagnostics = diagnostics  # type: ignore[attr-defined]
        sys.stderr.buffer.write(_diagnostics_payload(error))
        return int(result.exit_status)
    sys.stdout.write(json.dumps(_result_payload(result), sort_keys=True, separators=(",", ":")) + "\n")
    return 0


__all__ = ["main", "run_config"]
