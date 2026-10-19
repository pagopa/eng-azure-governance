from __future__ import annotations

import threading
from io import StringIO

import pytest

from tools.validation_core import EventSink, RunEvent, redact
from tools.validation_core.events import LiveEventWriter


def test_event_sink_assigns_unique_monotonic_sequences_and_preserves_statuses() -> None:
    sink = EventSink("run-123")
    statuses = (
        "planned",
        "queued",
        "running",
        "passed",
        "failed",
        "skipped",
        "cancelled",
        "incomplete",
    )

    for status in statuses:
        sink.emit(phase="unit", unit_id=status, status=status, detail=status)

    events = sink.close()

    assert [event.sequence for event in events] == list(range(1, 9))
    assert [event.status for event in events] == list(statuses)
    assert all(event.invocation_id == "run-123" for event in events)
    assert all(event.wall_timestamp for event in events)


def test_event_sink_serializes_concurrent_emission_without_duplicate_sequences() -> (
    None
):
    sink = EventSink("run-concurrent")
    barrier = threading.Barrier(8)

    def emit(index: int) -> None:
        barrier.wait()
        sink.emit(
            phase="unit",
            unit_id=f"unit-{index}",
            status="running",
            detail=f"worker {index}",
        )

    threads = [threading.Thread(target=emit, args=(index,)) for index in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    events = sink.close()

    assert [event.sequence for event in events] == list(range(1, 9))
    assert len({event.sequence for event in events}) == 8


def test_run_event_rejects_unknown_status() -> None:
    with pytest.raises(ValueError, match="unsupported event status"):
        RunEvent(
            invocation_id="run",
            sequence=1,
            wall_timestamp="2026-09-17T12:00:00Z",
            phase="unit",
            unit_id="unit",
            status="unknown",
            detail="",
        )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("token=top-secret", "token=[REDACTED]"),
        ("Authorization: Bearer abc123", "Authorization: [REDACTED]"),
        (
            "https://alice:password@example.test/path",
            "https://[REDACTED]@example.test/path",
        ),
        (
            "client_secret: multiline-secret\nAWS_SECRET_ACCESS_KEY=another-secret",
            "client_secret: [REDACTED]\nAWS_SECRET_ACCESS_KEY=[REDACTED]",
        ),
    ],
)
def test_redact_covers_inline_headers_urls_and_multiline_credentials(
    value: str, expected: str
) -> None:
    assert redact(value) == expected


def test_event_sink_redacts_before_captured_consumers_see_detail() -> None:
    sink = EventSink("run-safe")
    sink.emit(
        phase="command-complete",
        unit_id="unit",
        status="passed",
        detail="Authorization: Bearer never-persist-this",
    )

    event = sink.close()[0]

    assert "never-persist-this" not in event.detail
    assert event.detail == "Authorization: [REDACTED]"


def test_live_event_writer_renders_indexed_lifecycle_and_suppresses_technical_events() -> (
    None
):
    output = StringIO()
    writer = LiveEventWriter(output)
    writer.write(
        RunEvent(
            "run",
            1,
            "now",
            "plan",
            None,
            "planned",
            "selected units",
            monotonic_seconds=0.0,
        )
    )
    writer.write(
        RunEvent(
            "run",
            2,
            "now",
            "plan",
            "python:one",
            "planned",
            "One",
            monotonic_seconds=0.0,
        )
    )
    writer.write(
        RunEvent(
            "run",
            3,
            "now",
            "running",
            "python:one",
            "running",
            "One",
            monotonic_seconds=0.0,
        )
    )
    writer.write(
        RunEvent(
            "run",
            4,
            "now",
            "command-start",
            "python:one",
            "running",
            "pytest",
            monotonic_seconds=0.0,
        )
    )
    writer.write(
        RunEvent(
            "run",
            5,
            "now",
            "unit-complete",
            "python:one",
            "passed",
            "exit_code=0",
            monotonic_seconds=1.0,
        )
    )

    lines = output.getvalue().splitlines()
    assert lines == [
        "📋 PLAN",
        "  [01/01] python:one · One",
        "▶️ [01/01] python:one · One",
        "✅ [01/01] python:one · 1.00s",
    ]


def test_live_event_writer_bounds_heartbeat_updates_per_unit() -> None:
    output = StringIO()
    writer = LiveEventWriter(output, heartbeat_interval_seconds=15.0)
    writer.write(
        RunEvent(
            "run", 1, "now", "plan", "unit", "planned", "Unit", monotonic_seconds=0.0
        )
    )
    writer.write(
        RunEvent(
            "run", 2, "now", "running", "unit", "running", "Unit", monotonic_seconds=0.0
        )
    )
    writer.write(
        RunEvent(
            "run",
            3,
            "now",
            "heartbeat",
            "unit",
            "running",
            "still running",
            monotonic_seconds=1.0,
        )
    )
    writer.write(
        RunEvent(
            "run",
            4,
            "now",
            "heartbeat",
            "unit",
            "running",
            "still running",
            monotonic_seconds=16.0,
        )
    )

    assert output.getvalue().splitlines() == [
        "📋 PLAN",
        "  [01/01] unit · Unit",
        "▶️ [01/01] unit · Unit",
        "⏱️ [01/01] unit · still running",
    ]
