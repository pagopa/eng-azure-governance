import json
from dataclasses import dataclass, field
from typing import Any

import pytest

from src.comitato.comitato_azure_retirements_v2 import cli


@dataclass
class FakeResult:
    exit_status: int
    diagnostics: tuple[dict[str, str], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {"status": "published" if self.exit_status == 0 else "failed"}


@dataclass
class FakeReporter:
    human_console: bool = True
    finished: list[Any] = field(default_factory=list)
    exceptions: list[BaseException] = field(default_factory=list)
    closed: bool = False

    def emit(self, event: Any) -> None:
        return None

    def finish(self, result: Any) -> None:
        self.finished.append(result)

    def exception(self, error: BaseException) -> None:
        self.exceptions.append(error)

    def close(self) -> None:
        self.closed = True


def test_main_writes_one_success_result_to_stdout(monkeypatch, capsys) -> None:
    class Result(FakeResult):
        def to_dict(self):
            return {"status": "published", "artifacts": ["one.tsv"]}

    reporter = FakeReporter(human_console=False)

    monkeypatch.setattr(cli, "build_runtime_reporter", lambda config, **_: reporter)
    monkeypatch.setattr(cli, "run_config", lambda config, reporter=None: Result(0))

    assert cli.main(["--output-path", "out"]) == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out) == Result(0).to_dict()
    assert captured.err == ""
    assert reporter.finished[0].exit_status == 0
    assert reporter.closed is True


def test_main_writes_sorted_diagnostics_to_jsonl_stderr_and_returns_nonzero(monkeypatch, capsys) -> None:
    class Failure(Exception):
        diagnostics = (
            {"code": "z", "stage": "validation"},
            {"code": "a", "stage": "acquisition"},
        )

    def fail(config, reporter=None):
        raise Failure("safe failure")

    reporter = FakeReporter(human_console=False)
    monkeypatch.setattr(cli, "build_runtime_reporter", lambda config, **_: reporter)
    monkeypatch.setattr(cli, "run_config", fail)

    assert cli.main([]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert [json.loads(line)["code"] for line in captured.err.splitlines()] == ["a", "z"]
    assert reporter.exceptions
    assert reporter.closed is True


def test_python_module_help_is_available() -> None:
    assert callable(cli.main)


def test_json_success_keeps_stdout_only_and_closes_reporter(monkeypatch, capsys) -> None:
    reporter = FakeReporter(human_console=False)
    result = FakeResult(exit_status=0)
    monkeypatch.setattr(cli, "build_runtime_reporter", lambda config, **_: reporter)
    monkeypatch.setattr(cli, "run_config", lambda config, reporter=None: result)
    monkeypatch.setattr(cli.sys.stderr, "isatty", lambda: False)

    assert cli.main(["--output-format", "json"]) == 0

    captured = capsys.readouterr()
    assert json.loads(captured.out) == result.to_dict()
    assert captured.err == ""
    assert reporter.finished == [result]
    assert reporter.closed is True


def test_human_tty_uses_reporter_without_json_payload(monkeypatch, capsys) -> None:
    reporter = FakeReporter(human_console=True)
    monkeypatch.setattr(cli, "build_runtime_reporter", lambda config, **_: reporter)
    monkeypatch.setattr(cli, "run_config", lambda config, reporter=None: FakeResult(0))
    monkeypatch.setattr(cli.sys.stderr, "isatty", lambda: True)

    assert cli.main(["--output-format", "human"]) == 0

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
    assert reporter.human_console is True
    assert reporter.closed is True


def test_human_non_tty_falls_back_to_machine_success(monkeypatch, capsys) -> None:
    result = FakeResult(exit_status=0)
    reporter = FakeReporter(human_console=False)
    monkeypatch.setattr(cli, "build_runtime_reporter", lambda config, **_: reporter)
    monkeypatch.setattr(cli, "run_config", lambda config, reporter=None: result)
    monkeypatch.setattr(cli.sys.stderr, "isatty", lambda: False)

    assert cli.main(["--output-format", "human"]) == 0

    captured = capsys.readouterr()
    assert json.loads(captured.out) == result.to_dict()
    assert captured.err == ""
    assert reporter.closed is True


def test_human_non_tty_failure_keeps_stderr_jsonl(monkeypatch, capsys) -> None:
    reporter = FakeReporter(human_console=False)

    def fail_with_diagnostics(config, reporter=None):
        error = RuntimeError("safe failure")
        error.diagnostics = ({"code": "a", "stage": "validation"},)  # type: ignore[attr-defined]
        raise error

    monkeypatch.setattr(cli, "build_runtime_reporter", lambda config, **_: reporter)
    monkeypatch.setattr(cli, "run_config", fail_with_diagnostics)
    monkeypatch.setattr(cli.sys.stderr, "isatty", lambda: False)

    assert cli.main(["--output-format", "human"]) == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert all(json.loads(line)["code"] for line in captured.err.splitlines())
    assert reporter.closed is True
