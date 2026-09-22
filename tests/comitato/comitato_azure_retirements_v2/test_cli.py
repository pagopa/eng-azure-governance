import json
from dataclasses import dataclass, field
from datetime import date
from typing import Any

import pytest

from src.comitato.comitato_azure_retirements_v2 import cli
from src.comitato.comitato_azure_retirements_v2.config import RuntimeConfig
from src.comitato.comitato_azure_retirements_v2.domain.execution import ReportSelector, RunRequest
from src.comitato.comitato_azure_retirements_v2.reports.catalog import DEFAULT_REPORT_CATALOG


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


def test_replay_reads_bundle_without_live_sources(tmp_path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    expected_paths = DEFAULT_REPORT_CATALOG.plan(ReportSelector.ALL).expected_paths
    manifest = {
        "as_of_date": "2026-09-22",
        "catalog": {"schema_version": 1, "sha256": "a" * 64},
        "created_at": "2026-09-22T10:00:00Z",
        "dependency_closure": ["advisor", "service-health", "aggregate", "slides"],
        "editorial_catalog": {"schema_version": 1, "sha256": "b" * 64},
        "run_id": "replay-run",
        "scope": {"mode": "explicit", "subscription_ids": ["sub-1"]},
        "selector": "all",
        "settings": {"committee_window_months": 6},
        "artifacts": [],
    }
    for path in expected_paths:
        (bundle / path).write_bytes(b"header\nvalue\n")
        manifest["artifacts"].append({"media_type": "text/plain", "path": path, "schema_version": 1})
    (bundle / "publication-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    class NoLiveSource:
        def resolve(self, *args, **kwargs):
            raise AssertionError("replay invoked a live source")

    class Store:
        def __init__(self):
            self.candidate = None

        def publish(self, candidate):
            self.candidate = candidate
            return type("Receipt", (), {"generation": "2026/09", "current_reference": "2026/09"})()

    store = Store()
    application = type(
        "Application",
        (),
        {
            "report_catalog": DEFAULT_REPORT_CATALOG,
            "publication_store": store,
            "scope_source": NoLiveSource(),
            "advisor_source": NoLiveSource(),
            "service_health_source": NoLiveSource(),
        },
    )()
    config = RuntimeConfig.from_request(
        RunRequest(ReportSelector.ADVISOR, as_of_date=date(2026, 9, 22)),
        replay_bundle_path=bundle,
    )

    result = cli._run_replay(config, application)

    assert result.exit_status == 0
    assert store.candidate.context.request.selector is ReportSelector.ALL
    assert store.candidate.context.request.committee_window_months == 6
    assert store.candidate.context.editorial_catalog_identity.sha256 == "b" * 64
    assert tuple(artifact.logical_path for artifact in store.candidate.artifacts) == expected_paths
    assert store.candidate.manifest_metadata["run_id"] == "replay-run"


def test_replay_preserves_inputs_and_distinguishes_changed_settings_and_revision(tmp_path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    expected_paths = DEFAULT_REPORT_CATALOG.plan(ReportSelector.ALL).expected_paths
    manifest = {
        "as_of_date": "2026-09-22",
        "catalog": {"schema_version": 1, "sha256": "a" * 64},
        "created_at": "2026-09-22T10:00:00Z",
        "dependency_closure": ["advisor", "service-health", "aggregate", "slides"],
        "editorial_catalog": {"schema_version": 1, "sha256": "b" * 64},
        "run_id": "replay-run",
        "scope": {"mode": "explicit", "subscription_ids": ["sub-1"]},
        "selector": "all",
        "settings": {"committee_window_months": 6},
        "derivation": {"program_revision": "rev-a", "mode": "live"},
        "artifacts": [],
    }
    for path in expected_paths:
        (bundle / path).write_bytes(b"header\nvalue\n")
        manifest["artifacts"].append({"media_type": "text/plain", "path": path, "schema_version": 1})
    (bundle / "publication-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    class Store:
        def __init__(self):
            self.candidate = None

        def publish(self, candidate):
            self.candidate = candidate
            return type("Receipt", (), {"generation": "2026/09", "current_reference": "2026/09"})()

    store = Store()
    application = type("Application", (), {"report_catalog": DEFAULT_REPORT_CATALOG, "publication_store": store})()
    config = RuntimeConfig.from_request(
        RunRequest(ReportSelector.ALL, as_of_date=date(2026, 9, 22)),
        replay_bundle_path=bundle,
    )

    result = cli._run_replay(config, application)

    assert result.candidate.context.request.committee_window_months == 6
    assert result.candidate.manifest_metadata["derivation"]["program_revision"] == "rev-a"
    assert result.candidate.context.catalog_identity.sha256 == "a" * 64
    assert result.candidate.context.editorial_catalog_identity.sha256 == "b" * 64
