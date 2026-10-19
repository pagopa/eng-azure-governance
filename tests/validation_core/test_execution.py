from __future__ import annotations

import inspect
import threading
import time
from pathlib import Path

from tools.validation_core import EventSink
from tools.validation_core.execution import MAX_OUTPUT_PREVIEW, run_command, run_units
from tools.validation_core.models import RunContext, ValidationUnit


def test_run_units_respects_outer_parallel_cap_and_preserves_input_order(
    tmp_path: Path,
) -> None:
    active = 0
    maximum = 0

    def make_unit(name: str) -> ValidationUnit:
        def run(_context: RunContext) -> int:
            nonlocal active, maximum
            active += 1
            maximum = max(maximum, active)
            time.sleep(0.03)
            active -= 1
            return 0

        return ValidationUnit(name, name.title(), run)

    context = RunContext(tmp_path, tmp_path / "run", False, False)
    results = run_units(
        [make_unit("first"), make_unit("second"), make_unit("third")],
        context,
        max_parallel=2,
    )

    assert [result.unit.unit_id for result in results] == [
        "first",
        "second",
        "third",
    ]
    assert maximum == 2


def test_run_units_retains_every_started_failure_and_isolates_unit_directories(
    tmp_path: Path,
) -> None:
    directories: list[Path] = []

    def make_unit(name: str, status: int) -> ValidationUnit:
        def run(context: RunContext) -> int:
            directories.append(context.tmp_dir)
            return status

        return ValidationUnit(name, name, run)

    context = RunContext(tmp_path, tmp_path / "run", False, False)
    results = run_units(
        [make_unit("first", 7), make_unit("second", 3)],
        context,
        max_parallel=2,
    )

    assert [result.exit_code for result in results] == [7, 3]
    assert len(directories) == 2
    assert directories[0] != directories[1]
    assert all(path.parent == context.tmp_dir for path in directories)


def test_run_units_dry_run_records_simulated_command_evidence(tmp_path: Path) -> None:
    context = RunContext(tmp_path, tmp_path / "run", True, False)

    result = run_units(
        [
            ValidationUnit(
                "dry",
                "Dry run",
                lambda current: run_command(current, ["child-command"]),
            )
        ],
        context,
    )[0]

    assert result.exit_code == 0
    assert result.commands[0].simulated is True


def test_run_units_emits_preflight_before_collection_and_plans_every_unit(
    tmp_path: Path,
) -> None:
    observations: list[str] = []
    sink = EventSink("run-order")

    def collect(_context: RunContext) -> int:
        observations.append("collection")
        return 0

    context = RunContext(tmp_path, tmp_path / "run", False, False, event_sink=sink)
    run_units([ValidationUnit("collect", "Collect", collect)], context)

    events = sink.close()

    assert events[0].phase == "preflight"
    assert events[0].status == "planned"
    assert events[0].sequence < next(
        event.sequence
        for event in events
        if event.unit_id == "collect" and event.status == "running"
    )
    assert observations == ["collection"]


def test_run_units_serializes_event_writer_under_concurrent_completion(
    tmp_path: Path,
) -> None:
    written: list[int] = []
    writer_lock = threading.Lock()

    def writer(event) -> None:
        with writer_lock:
            written.append(event.sequence)

    sink = EventSink("run-writer", writer)
    context = RunContext(tmp_path, tmp_path / "run", False, False, event_sink=sink)
    run_units(
        [
            ValidationUnit("slow", "Slow", lambda _context: (time.sleep(0.04), 0)[1]),
            ValidationUnit("fast", "Fast", lambda _context: (time.sleep(0.01), 0)[1]),
        ],
        context,
        max_parallel=2,
    )

    sink.close()

    assert written == sorted(written)
    assert len(written) == len(set(written))


def test_run_units_honors_dependencies_and_shared_resources(tmp_path: Path) -> None:
    active_resources: set[str] = set()
    resource_overlap = False
    order: list[str] = []
    lock = threading.Lock()

    def make_unit(name: str) -> ValidationUnit:
        def run(_context: RunContext) -> int:
            nonlocal resource_overlap
            with lock:
                if "shared" in active_resources:
                    resource_overlap = True
                active_resources.add("shared")
                order.append(name)
            time.sleep(0.03)
            with lock:
                active_resources.remove("shared")
            return 0

        return ValidationUnit(name, name, run)

    context = RunContext(tmp_path, tmp_path / "run", False, False)
    results = run_units(
        [make_unit("first"), make_unit("second"), make_unit("third")],
        context,
        max_parallel=3,
        dependencies={"third": ("second",)},
        resources={"first": ("shared",), "second": ("shared",), "third": ("shared",)},
    )

    assert [result.unit.unit_id for result in results] == ["first", "second", "third"]
    assert order == ["first", "second", "third"]
    assert resource_overlap is False


def test_run_units_fail_fast_marks_unstarted_work_and_retains_started_siblings(
    tmp_path: Path,
) -> None:
    started: list[str] = []

    def failing(_context: RunContext) -> int:
        started.append("failing")
        time.sleep(0.02)
        return 9

    def sibling(_context: RunContext) -> int:
        started.append("sibling")
        time.sleep(0.05)
        return 0

    def unstarted(_context: RunContext) -> int:
        started.append("unstarted")
        return 0

    context = RunContext(tmp_path, tmp_path / "run", False, False)
    results = run_units(
        [
            ValidationUnit("failing", "Failing", failing),
            ValidationUnit("sibling", "Sibling", sibling),
            ValidationUnit("unstarted", "Unstarted", unstarted),
        ],
        context,
        max_parallel=2,
        fail_fast=True,
    )

    assert set(started) == {"failing", "sibling"}
    assert "unstarted" not in started
    assert [result.unit.unit_id for result in results] == [
        "failing",
        "sibling",
        "unstarted",
    ]
    assert results[0].status == "failed"
    assert results[1].status == "passed"
    assert results[2].status in {"skipped", "cancelled"}


def test_run_units_emits_heartbeats_and_distinguishes_wall_clock_from_serial_time(
    tmp_path: Path,
) -> None:
    context = RunContext(tmp_path, tmp_path / "run", False, False)
    results = run_units(
        [
            ValidationUnit("one", "One", lambda _context: (time.sleep(0.08), 0)[1]),
            ValidationUnit("two", "Two", lambda _context: (time.sleep(0.08), 0)[1]),
        ],
        context,
        max_parallel=2,
        heartbeat_interval_seconds=0.01,
    )

    report = results.report
    assert any(event.phase == "heartbeat" for event in report.events)
    assert report.wall_clock_seconds >= 0
    assert report.serial_equivalent_seconds >= report.wall_clock_seconds
    assert report.serial_equivalent_seconds == sum(
        result.duration_seconds for result in results
    )
    assert all(result.queue_seconds >= 0 for result in results)


def test_run_command_emits_redacted_start_and_completion_events(tmp_path: Path) -> None:
    sink = EventSink("run-command")
    context = RunContext(tmp_path, tmp_path / "run", False, False, event_sink=sink)

    exit_code = run_command(
        context,
        [
            "python3",
            "-c",
            "print('Authorization: Bearer command-secret')",
        ],
    )

    events = sink.close()
    assert exit_code == 0
    assert [event.phase for event in events] == ["command-start", "command-complete"]
    assert events[-1].status == "passed"
    assert all("command-secret" not in event.detail for event in events)


def test_run_units_uses_production_heartbeat_interval_without_changing_test_override() -> (
    None
):
    assert (
        inspect.signature(run_units).parameters["heartbeat_interval_seconds"].default
        == 15.0
    )


def test_run_command_preserves_bounded_redacted_head_and_tail_evidence(
    tmp_path: Path,
) -> None:
    context = RunContext(tmp_path, tmp_path / "run", False, False)
    head = "HEAD-" + ("a" * 1400)
    tail = "TAIL-" + ("b" * 1400)
    results = run_units(
        [
            ValidationUnit(
                "evidence",
                "Evidence",
                lambda current: run_command(
                    current,
                    [
                        "python3",
                        "-c",
                        f"print('token=secret-value'); print({head!r}); print({tail!r})",
                    ],
                ),
            )
        ],
        context,
    )

    evidence = results[0].commands[0]
    assert len(evidence.stdout) <= MAX_OUTPUT_PREVIEW
    assert "HEAD-" in evidence.stdout
    assert "TAIL-" in evidence.stdout
    assert "secret-value" not in evidence.stdout
