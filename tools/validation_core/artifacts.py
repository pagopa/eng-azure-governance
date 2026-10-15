"""Atomic, bounded, redacted validation result and unit-log writers."""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

from .events import redact
from .models import RunReport

MAX_UNIT_LOG_LENGTH = 12_000


def _bounded_text(text: str) -> str:
    normalized = redact(text).replace("\r\n", "\n").replace("\r", "\n")
    if len(normalized) <= MAX_UNIT_LOG_LENGTH:
        return normalized
    return normalized[: MAX_UNIT_LOG_LENGTH - 3] + "..."


def _atomic_write(path: Path, content: str) -> Path:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return path


def write_run_result(report: RunReport, path: Path) -> Path:
    """Atomically write the versioned JSON report and return its final path."""

    from .reporting import render_run

    return _atomic_write(path, render_run(report, "json") + "\n")


def write_unit_log(unit_id: str, text: str, artifact_dir: Path) -> Path:
    """Write one bounded redacted unit log below ``artifact_dir``."""

    safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(unit_id)).strip(".-") or "unit"
    root = artifact_dir.resolve()
    path = (root / f"unit-{safe_id}.log").resolve()
    if not path.is_relative_to(root):
        raise ValueError("unit log path escapes artifact root")
    return _atomic_write(path, _bounded_text(text))
