"""Versioned lifecycle events and safe, serialized event delivery."""

from __future__ import annotations

import re
import sys
import threading
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal, TextIO

EVENT_SCHEMA_VERSION = "validation-event/v1"
MAX_EVENT_DETAIL = 512
EVENT_STATUSES = frozenset(
    {
        "planned",
        "queued",
        "running",
        "passed",
        "failed",
        "skipped",
        "cancelled",
        "incomplete",
    }
)
EventStatus = Literal[
    "planned",
    "queued",
    "running",
    "passed",
    "failed",
    "skipped",
    "cancelled",
    "incomplete",
]

_SENSITIVE_NAME = (
    r"password|passwd|token|secret|access[_-]?key|api[_-]?key|"
    r"client[_-]?secret|credential|aws[_-]?session[_-]?token|"
    r"aws[_-]?secret[_-]?access[_-]?key|github[_-]?token"
)
_AUTHORIZATION_RE = re.compile(
    r"(?im)(?P<name>\b(?:authorization|proxy-authorization))"
    r"(?P<separator>\s*[:=]\s*)[^\r\n]*"
)
_INLINE_SECRET_RE = re.compile(
    rf"(?i)(?P<name>\b(?:{_SENSITIVE_NAME})\b)"
    r"(?P<separator>\s*[:=]\s*)(?P<value>[^\s,;]+)"
)
_OPTION_SECRET_RE = re.compile(
    rf"(?i)(?P<name>--?(?:{_SENSITIVE_NAME.replace('|', '|')})"
    r"(?P<separator>\s+))(?P<value>[^\s,;]+)"
)
_URL_USERINFO_RE = re.compile(r"(?i)(?P<scheme>https?://)(?P<userinfo>[^/@\s]+@)")


def redact(value: str) -> str:
    """Redact credentials before a value reaches any event consumer."""

    redacted = str(value)
    redacted = _URL_USERINFO_RE.sub(r"\g<scheme>[REDACTED]@", redacted)
    redacted = _AUTHORIZATION_RE.sub(
        lambda match: (
            f"{match.group('name').rstrip()}{match.group('separator').rstrip()} [REDACTED]"
        ),
        redacted,
    )
    redacted = _INLINE_SECRET_RE.sub(
        lambda match: f"{match.group('name')}{match.group('separator')}[REDACTED]",
        redacted,
    )
    redacted = _OPTION_SECRET_RE.sub(
        lambda match: f"{match.group('name')}[REDACTED]",
        redacted,
    )
    return redacted


def _bounded_detail(value: str, limit: int = MAX_EVENT_DETAIL) -> str:
    normalized = redact(value).replace("\r\n", "\n").replace("\r", "\n")
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."


def _wall_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class RunEvent:
    """A bounded, versioned observation of one validation lifecycle change."""

    invocation_id: str
    sequence: int
    wall_timestamp: str
    phase: str
    unit_id: str | None
    status: EventStatus
    detail: str = ""
    schema_version: str = EVENT_SCHEMA_VERSION
    monotonic_seconds: float = 0.0
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status not in EVENT_STATUSES:
            raise ValueError(f"unsupported event status: {self.status}")
        if self.sequence < 1:
            raise ValueError("event sequence must be positive")
        if not self.invocation_id.strip():
            raise ValueError("event invocation_id must be non-empty")
        if not self.phase.strip():
            raise ValueError("event phase must be non-empty")
        if self.schema_version != EVENT_SCHEMA_VERSION:
            raise ValueError(f"unsupported event schema: {self.schema_version}")
        object.__setattr__(self, "detail", _bounded_detail(self.detail))
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def monotonic_sequence(self) -> int:
        """Compatibility name for consumers that use the contract wording."""

        return self.sequence

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "invocation_id": self.invocation_id,
            "sequence": self.sequence,
            "monotonic_sequence": self.sequence,
            "wall_timestamp": self.wall_timestamp,
            "monotonic_seconds": self.monotonic_seconds,
            "phase": self.phase,
            "unit_id": self.unit_id,
            "status": self.status,
            "detail": self.detail,
            "metadata": dict(self.metadata),
        }


class EventSink:
    """Assign sequence numbers and serialize one consumer's event writes."""

    def __init__(
        self,
        invocation_id: str | None = None,
        writer: Callable[[RunEvent], None] | None = None,
        *,
        max_detail: int = MAX_EVENT_DETAIL,
    ) -> None:
        if max_detail < 1:
            raise ValueError("max_detail must be positive")
        self.invocation_id = invocation_id or uuid.uuid4().hex
        self._writer = writer
        self._max_detail = max_detail
        self._lock = threading.RLock()
        self._events: list[RunEvent] = []
        self._sequence = 0
        self._closed = False

    def emit(
        self,
        event: RunEvent | None = None,
        *,
        phase: str | None = None,
        unit_id: str | None = None,
        status: str | None = None,
        detail: str = "",
        wall_timestamp: str | None = None,
        monotonic_seconds: float | None = None,
        metadata: Mapping[str, str] | None = None,
    ) -> RunEvent:
        with self._lock:
            if self._closed:
                raise RuntimeError("cannot emit after EventSink.close()")
            self._sequence += 1
            if event is not None:
                phase = event.phase
                unit_id = event.unit_id
                status = event.status
                detail = event.detail
                wall_timestamp = event.wall_timestamp
                monotonic_seconds = event.monotonic_seconds
                metadata = event.metadata
            if phase is None or status is None:
                raise ValueError("phase and status are required to emit an event")
            emitted = RunEvent(
                invocation_id=self.invocation_id,
                sequence=self._sequence,
                wall_timestamp=wall_timestamp or _wall_timestamp(),
                phase=phase,
                unit_id=unit_id,
                status=status,  # type: ignore[arg-type]
                detail=_bounded_detail(detail, self._max_detail),
                monotonic_seconds=(
                    time.monotonic() if monotonic_seconds is None else monotonic_seconds
                ),
                metadata=metadata or {},
            )
            self._events.append(emitted)
            if self._writer is not None:
                self._writer(emitted)
            return emitted

    @property
    def events(self) -> tuple[RunEvent, ...]:
        with self._lock:
            return tuple(self._events)

    def close(self) -> tuple[RunEvent, ...]:
        with self._lock:
            self._closed = True
            return tuple(self._events)


class LiveEventWriter:
    """Render a bounded human lifecycle projection from versioned events."""

    _STATUS_MARKERS = {
        "passed": "✅",
        "failed": "❌",
        "skipped": "⏭️",
        "cancelled": "⏭️",
        "incomplete": "⚠️",
    }

    def __init__(
        self,
        stream: TextIO | None = None,
        *,
        heartbeat_interval_seconds: float = 15.0,
    ) -> None:
        if heartbeat_interval_seconds <= 0:
            raise ValueError("heartbeat_interval_seconds must be positive")
        self.stream = stream or sys.stderr
        self.heartbeat_interval_seconds = heartbeat_interval_seconds
        self._planned: list[str] = []
        self._titles: dict[str, str] = {}
        self._started: dict[str, float] = {}
        self._last_heartbeat: dict[str, float] = {}
        self._plan_rendered = False

    def _index(self, unit_id: str) -> str:
        try:
            index = self._planned.index(unit_id) + 1
        except ValueError:
            self._planned.append(unit_id)
            index = len(self._planned)
        return f"[{index:02d}/{len(self._planned):02d}]"

    def _write(self, line: str) -> None:
        print(line, file=self.stream)

    def _render_plan(self) -> None:
        if self._plan_rendered or not self._planned:
            return
        self._write("📋 PLAN")
        total = len(self._planned)
        for index, unit_id in enumerate(self._planned, start=1):
            self._write(
                f"  [{index:02d}/{total:02d}] {unit_id} · "
                f"{self._titles.get(unit_id, unit_id)}"
            )
        self._plan_rendered = True

    def write(self, event: RunEvent) -> None:
        if event.phase == "preflight" and event.unit_id is None:
            self._write(f"preflight: {event.detail}")
            return
        if event.phase == "plan" and event.unit_id:
            if event.unit_id not in self._planned:
                self._planned.append(event.unit_id)
            self._titles[event.unit_id] = event.detail
            return
        if not event.unit_id:
            return

        if event.phase in {"running", "unit-complete"}:
            if event.unit_id not in self._planned:
                self._planned.append(event.unit_id)
                self._titles[event.unit_id] = event.detail
            self._render_plan()

        index = self._index(event.unit_id)
        title = self._titles.get(event.unit_id, event.detail)
        if event.phase == "running":
            self._started[event.unit_id] = event.monotonic_seconds
            self._last_heartbeat[event.unit_id] = event.monotonic_seconds
            self._write(f"▶️ {index} {event.unit_id} · {title}")
            return
        if event.phase == "heartbeat":
            last = self._last_heartbeat.get(event.unit_id, event.monotonic_seconds)
            if event.monotonic_seconds - last >= self.heartbeat_interval_seconds:
                self._last_heartbeat[event.unit_id] = event.monotonic_seconds
                self._write(f"⏱️ {index} {event.unit_id} · {event.detail}")
            return
        if event.phase != "unit-complete":
            return

        marker = self._STATUS_MARKERS.get(event.status, "⚠️")
        started = self._started.get(event.unit_id, event.monotonic_seconds)
        duration = max(0.0, event.monotonic_seconds - started)
        self._write(f"{marker} {index} {event.unit_id} · {duration:.2f}s")
