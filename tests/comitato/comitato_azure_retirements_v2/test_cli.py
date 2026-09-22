import json
from hashlib import sha256
from dataclasses import dataclass, field
from datetime import date
from typing import Any

import pytest

from src.comitato.comitato_azure_retirements_v2 import cli
from src.comitato.comitato_azure_retirements_v2.config import RuntimeConfig
from src.comitato.comitato_azure_retirements_v2.domain.execution import ReportSelector, RunRequest
from src.comitato.comitato_azure_retirements_v2.application.orchestration import RetirementsApplication
from src.comitato.comitato_azure_retirements_v2.reports.catalog import (
    DEFAULT_REPORT_CATALOG,
    EDITORIAL_YAML_PATH,
)


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


def _replay_slide_fixture(title: str) -> tuple[dict[str, Any], str]:
    subscription_id = "11111111-1111-1111-1111-111111111111"
    editorial_yaml = f"""schema_version: 1
items:
  - id: item-1
    associations:
      advisor:
        recommendation_type_ids: [retirement-1]
    title: {title}
    description: Move the workload.
    suggested_action: Migrate the workload.
"""
    saved_inputs = {
        "schema_version": 1,
        "platform_catalog": {
            "schema_version": 1,
            "sha256": "a" * 64,
            "assignments": [{
                "subscription_id": subscription_id,
                "platform": "Platform A",
                "subscription_name": "Subscription A",
            }],
        },
        "source_acquisitions": {
            "advisor": {
                "receipt": {
                    "source": "advisor",
                    "api_version": "test-v1",
                    "expected_subscriptions": 1,
                    "completed_subscriptions": 1,
                    "pages": 1,
                    "source_records": 1,
                    "complete": True,
                    "continuation_tokens": [],
                    "failed_subscriptions": [],
                },
                "records": [{
                    "subscription_id": subscription_id,
                    "identity": "advisor-1",
                    "payload": {
                        "id": f"/subscriptions/{subscription_id}/providers/Microsoft.Advisor/recommendations/rec-1",
                        "subscriptionId": subscription_id,
                        "properties": {
                            "recommendationStatus": "New",
                            "recommendationTypeId": "retirement-1",
                            "detailedDescription": "Move the workload.",
                        },
                    },
                    "source": "advisor",
                    "page_number": 1,
                    "continuation_token": None,
                }],
                "companion_records": [],
                "accounting": [],
                "collection_context": {},
                "response_context": [],
            },
            "service-health": {
                "receipt": {
                    "source": "service-health",
                    "api_version": "test-v1",
                    "expected_subscriptions": 1,
                    "completed_subscriptions": 1,
                    "pages": 1,
                    "source_records": 0,
                    "complete": True,
                    "continuation_tokens": [],
                    "failed_subscriptions": [],
                },
                "records": [],
                "companion_records": [],
                "accounting": [],
                "collection_context": {},
                "response_context": [],
            },
        },
        "advisor_enrichments": {"metadata": {}, "resources": {}, "subscriptions": {}},
        "service_health_evidence": {
            "advisor_records": [],
            "resource_inventory": {},
            "subscription_inventory": {},
            "resource_associations": [],
            "subscription_name_sources": {},
        },
        "editorial_catalog": {
            "schema_version": 1,
            "sha256": sha256(editorial_yaml.encode("utf-8")).hexdigest(),
            "items": [{
                "item_id": "item-1",
                "associations": [["advisor", ["retirement-1"]]],
                "title": title,
                "description": "Move the workload.",
                "suggested_action": "Migrate the workload.",
                "retirement_date": "",
            }],
            "yaml": editorial_yaml,
        },
    }
    manifest = {
        "as_of_date": "2026-09-22",
        "catalog": {"schema_version": 1, "sha256": "a" * 64},
        "created_at": "2026-09-22T10:00:00Z",
        "dependency_closure": ["scope", "catalog", "advisor", "service-health", "aggregate", "slides", "publication"],
        "editorial_catalog": {
            "schema_version": 1,
            "sha256": sha256(editorial_yaml.encode("utf-8")).hexdigest(),
        },
        "run_id": "replay-run",
        "scope": {"mode": "explicit", "subscription_ids": [subscription_id]},
        "selector": "slides",
        "settings": {"committee_window_months": 6},
        "saved_inputs": saved_inputs,
        "artifacts": [],
    }
    manifest["saved_inputs_sha256"] = sha256(
        json.dumps(saved_inputs, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return manifest, editorial_yaml


def _replay_application(store: Any) -> Any:
    return type(
        "Application",
        (),
        {
            "report_catalog": DEFAULT_REPORT_CATALOG,
            "publication_store": store,
        },
    )()


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


def test_replay_rejects_bundle_without_replay_inputs(tmp_path) -> None:
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
        "saved_inputs": {"schema_version": 1, "source_acquisitions": []},
        "artifacts": [],
    }
    for path in expected_paths:
        (bundle / path).write_bytes(b"header\nvalue\n")
        manifest["artifacts"].append({"media_type": "text/plain", "path": path, "schema_version": 1})
    manifest["saved_inputs_sha256"] = sha256(
        json.dumps(manifest["saved_inputs"], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
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

    with pytest.raises(ValueError, match="replay bundle"):
        cli._run_replay(config, application)


def test_replay_rejects_bundle_without_saved_catalog_and_acquisitions(tmp_path) -> None:
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
        "saved_inputs": {"schema_version": 1, "source_acquisitions": []},
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

    with pytest.raises(ValueError, match="replay bundle"):
        cli._run_replay(config, application)


def test_replay_rejects_artifact_only_bundle(tmp_path) -> None:
    bundle = tmp_path / "artifact-only"
    bundle.mkdir()
    manifest = {
        "as_of_date": "2026-09-22",
        "catalog": {"schema_version": 1, "sha256": "a" * 64},
        "created_at": "2026-09-22T10:00:00Z",
        "dependency_closure": ["advisor", "service-health", "aggregate", "slides"],
        "run_id": "artifact-only",
        "scope": {"mode": "explicit", "subscription_ids": ["sub-1"]},
        "selector": "all",
        "artifacts": [],
    }
    for path in DEFAULT_REPORT_CATALOG.plan(ReportSelector.ALL).expected_paths:
        (bundle / path).write_bytes(b"header\nvalue\n")
        manifest["artifacts"].append({"media_type": "text/plain", "path": path, "schema_version": 1})
    (bundle / "publication-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    application = type("Application", (), {"report_catalog": DEFAULT_REPORT_CATALOG})()
    config = RuntimeConfig.from_request(
        RunRequest(ReportSelector.ALL, as_of_date=date(2026, 9, 22)),
        replay_bundle_path=bundle,
    )

    with pytest.raises(ValueError, match="replay bundle"):
        cli._run_replay(config, application)


def test_replay_recomputes_empty_advisor_from_saved_inputs_without_live_sources(tmp_path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    subscription_id = "11111111-1111-1111-1111-111111111111"
    manifest = {
        "as_of_date": "2026-09-22",
        "catalog": {"schema_version": 1, "sha256": "a" * 64},
        "created_at": "2026-09-22T10:00:00Z",
        "dependency_closure": ["scope", "catalog", "advisor", "publication"],
        "run_id": "replay-run",
        "scope": {"mode": "explicit", "subscription_ids": [subscription_id]},
        "selector": "advisor",
        "settings": {"committee_window_months": 6},
        "saved_inputs": {
            "schema_version": 1,
            "platform_catalog": {
                "schema_version": 1,
                "sha256": "a" * 64,
                "assignments": [{
                    "subscription_id": subscription_id,
                    "platform": "Platform A",
                    "subscription_name": "Subscription A",
                }],
            },
            "source_acquisitions": {
                "advisor": {
                    "receipt": {
                        "source": "advisor",
                        "api_version": "test-v1",
                        "expected_subscriptions": 1,
                        "completed_subscriptions": 1,
                        "pages": 1,
                        "source_records": 0,
                        "complete": True,
                        "continuation_tokens": [],
                        "failed_subscriptions": [],
                        "completeness_reason": "complete_empty",
                    },
                    "records": [],
                    "companion_records": [],
                    "accounting": [],
                    "collection_context": {},
                    "response_context": [],
                },
            },
            "advisor_enrichments": {"metadata": {}, "resources": {}, "subscriptions": {}},
            "editorial_catalog": None,
        },
        "artifacts": [],
    }
    manifest["saved_inputs_sha256"] = sha256(
        json.dumps(manifest["saved_inputs"], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    (bundle / "publication-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

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
            "_validate_catalog_coverage": RetirementsApplication._validate_catalog_coverage,
            "_empty_artifacts": RetirementsApplication._empty_artifacts,
        },
    )()
    config = RuntimeConfig.from_request(
        RunRequest(ReportSelector.ADVISOR, as_of_date=date(2026, 9, 22)),
        replay_bundle_path=bundle,
    )

    result = cli._run_replay(config, application)

    assert result.exit_status == 0
    assert store.candidate.artifacts[0].data.startswith(b"schema_version\trun_id\t")
    assert store.candidate.saved_inputs == manifest["saved_inputs"]


def test_replay_slides_consumes_physical_sidecar_and_changed_yaml_changes_tsv(tmp_path) -> None:
    class Store:
        def __init__(self):
            self.candidate = None

        def publish(self, candidate):
            self.candidate = candidate
            return type("Receipt", (), {"generation": "2026/09", "current_reference": "2026/09"})()

    bundle = tmp_path / "bundle"
    bundle.mkdir()
    manifest, editorial_yaml = _replay_slide_fixture("Old title")
    (bundle / EDITORIAL_YAML_PATH).write_text(editorial_yaml, encoding="utf-8")
    (bundle / "publication-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    store = Store()
    config = RuntimeConfig.from_request(
        RunRequest(ReportSelector.SLIDES, as_of_date=date(2026, 9, 22)),
        replay_bundle_path=bundle,
    )
    result = cli._run_replay(config, _replay_application(store))

    slide = next(item for item in store.candidate.artifacts if item.logical_path == "03_azure_retirements_slide.tsv")
    sidecar = next(item for item in store.candidate.artifacts if item.logical_path == EDITORIAL_YAML_PATH)
    assert result.exit_status == 0
    assert b"Old title" in slide.data
    assert sidecar.data == editorial_yaml.encode("utf-8")

    changed_bundle = tmp_path / "changed-bundle"
    changed_bundle.mkdir()
    changed_manifest, changed_yaml = _replay_slide_fixture("New title")
    (changed_bundle / EDITORIAL_YAML_PATH).write_text(changed_yaml, encoding="utf-8")
    (changed_bundle / "publication-manifest.json").write_text(
        json.dumps(changed_manifest),
        encoding="utf-8",
    )
    changed_store = Store()
    changed_config = RuntimeConfig.from_request(
        RunRequest(ReportSelector.SLIDES, as_of_date=date(2026, 9, 22)),
        replay_bundle_path=changed_bundle,
    )
    cli._run_replay(changed_config, _replay_application(changed_store))
    changed_slide = next(
        item
        for item in changed_store.candidate.artifacts
        if item.logical_path == "03_azure_retirements_slide.tsv"
    )
    assert b"New title" in changed_slide.data
    assert b"Old title" not in changed_slide.data


def test_replay_rejects_physical_sidecar_that_differs_from_saved_yaml(tmp_path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    manifest, editorial_yaml = _replay_slide_fixture("Saved title")
    (bundle / EDITORIAL_YAML_PATH).write_text(
        editorial_yaml.replace("Saved title", "Different title"),
        encoding="utf-8",
    )
    (bundle / "publication-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    config = RuntimeConfig.from_request(
        RunRequest(ReportSelector.SLIDES, as_of_date=date(2026, 9, 22)),
        replay_bundle_path=bundle,
    )

    with pytest.raises(ValueError, match="replay bundle"):
        cli._run_replay(config, _replay_application(object()))
