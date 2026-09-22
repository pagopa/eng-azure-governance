"""Command-line boundary: parse once, run once, emit safe machine output."""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from datetime import date, datetime
from pathlib import Path
from typing import Any, Sequence

from .config import RuntimeConfig, parse_config
from .domain.diagnostics import Diagnostic, sort_diagnostics
from .domain.execution import CatalogIdentity, DependencyPlan, ReportSelector, RunContext, RunRequest, Scope
from .contracts.model import EncodedArtifact
from .publication.model import PublicationCandidate, RunResult
from .ports import RunObserver
from .runtime_logging import RuntimeReporter


_RUNTIME_LOG_ROOT = Path(__file__).resolve().parents[3] / "tmp" / "comitato" / "comitato_azure_retirements_v2" / "exports"


def run_config(config: RuntimeConfig, reporter: RunObserver | None = None) -> Any:
    from .application.composition import build_application

    application = build_application(config, observer=reporter)
    if config.replay_bundle_path is not None:
        return _run_replay(config, application)
    return application.run(config.request)


def _run_replay(config: RuntimeConfig, application: Any) -> RunResult:
    bundle = config.replay_bundle_path
    if bundle is None:
        raise ValueError("replay bundle is required")
    try:
        manifest = json.loads((bundle / "publication-manifest.json").read_text(encoding="utf-8"))
        as_of_date = date.fromisoformat(str(manifest["as_of_date"]))
        created_at = datetime.fromisoformat(str(manifest["created_at"]).replace("Z", "+00:00"))
        catalog_payload = manifest["catalog"]
        selector = ReportSelector(str(manifest["selector"]))
        committee_window_months = int(manifest.get("settings", {}).get("committee_window_months", 12))
        request = RunRequest(
            selector=selector,
            subscription_ids=tuple(manifest["scope"]["subscription_ids"]),
            as_of_date=as_of_date,
            committee_window_months=committee_window_months,
        )
        context = RunContext(
            run_id=str(manifest["run_id"]),
            as_of_date=as_of_date,
            created_at=created_at,
            request=request,
            scope=Scope(tuple(manifest["scope"]["subscription_ids"]), str(manifest["scope"]["mode"])),
            catalog_identity=CatalogIdentity(int(catalog_payload["schema_version"]), str(catalog_payload["sha256"])),
            dependency_plan=DependencyPlan(tuple(manifest["dependency_closure"])),
            editorial_catalog_identity=(
                CatalogIdentity(
                    int(manifest["editorial_catalog"]["schema_version"]),
                    str(manifest["editorial_catalog"]["sha256"]),
                )
                if "editorial_catalog" in manifest
                else None
            ),
        )
        closure = application.report_catalog.plan(selector)
        artifacts: list[EncodedArtifact] = []
        entries = {str(item["path"]): item for item in manifest["artifacts"]}
        for path in closure.expected_paths:
            data = (bundle / path).read_bytes()
            entry = entries[path]
            artifacts.append(
                EncodedArtifact(
                    logical_path=path,
                    data=data,
                    rows=max(0, len(data.decode("utf-8").splitlines()) - 1) if path.endswith(".tsv") else len(data.decode("utf-8").splitlines()),
                    media_type=str(entry["media_type"]),
                    schema_version=int(entry["schema_version"]),
                    run_id=context.run_id,
                )
            )
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("replay bundle is invalid or incomplete") from exc
    candidate = PublicationCandidate(
        context=context,
        report_closure=closure,
        artifacts=tuple(artifacts),
        acquisitions=(),
        manifest_metadata=manifest,
    )
    receipt = application.publication_store.publish(candidate)
    return RunResult(0, context, candidate, receipt)


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
