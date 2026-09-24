"""Command-line boundary: parse once, run once, emit safe machine output."""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from datetime import date, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Sequence

from .acquisition.evidence import ObservationAccounting, SourceRecord
from .acquisition.model import AcquisitionReceipt, SourceAcquisition
from .config import RuntimeConfig, parse_config
from .domain.diagnostics import Diagnostic
from .domain.evidence import AdvisorEnrichments, ServiceHealthSupplementalEvidence
from .domain.execution import CatalogIdentity, DependencyPlan, ReportSelector, RunContext, RunRequest, Scope
from .domain.platforms import PlatformAssignment, PlatformCatalogSnapshot, SubscriptionId
from .application.orchestration import RetirementsApplication
from .contracts.codecs import canonical_json
from .publication.model import PublicationCandidate, RunResult
from .ports import RunObserver
from .reports.advisor import prepare_advisor_report
from .reports.service_health import prepare_service_health_report
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
        if not isinstance(manifest.get("saved_inputs"), Mapping):
            if manifest.get("manifest_schema_version") == 1:
                raise ValueError("legacy schema-1 replay is unsupported because saved input evidence is absent")
            raise ValueError("replay bundle requires saved inputs")
        saved_inputs = manifest["saved_inputs"]
        expected_saved_inputs_hash = str(manifest.get("saved_inputs_sha256", ""))
        actual_saved_inputs_hash = sha256(
            canonical_json(saved_inputs).encode("utf-8")
        ).hexdigest()
        if not expected_saved_inputs_hash or expected_saved_inputs_hash != actual_saved_inputs_hash:
            raise ValueError("replay bundle saved inputs integrity check failed")
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
        )
        closure = application.report_catalog.plan(selector)
        catalog = _catalog_from_saved_inputs(saved_inputs)
        acquisitions = _acquisitions_from_saved_inputs(saved_inputs, closure)
        prepared_by_selector = {}
        if closure.requires(ReportSelector.ADVISOR):
            advisor = acquisitions["advisor"]
            enrichments = _advisor_enrichments_from_saved_inputs(saved_inputs)
            prepared_by_selector[ReportSelector.ADVISOR] = prepare_advisor_report(advisor, context, enrichments)
        if closure.requires(ReportSelector.SERVICE_HEALTH):
            service_health = acquisitions["service-health"]
            supplemental = _service_health_evidence_from_saved_inputs(saved_inputs)
            prepared_by_selector[ReportSelector.SERVICE_HEALTH] = prepare_service_health_report(service_health, context, supplemental)
        selected_acquisitions = [
            prepared_by_selector[selector].acquisition
            for selector in (ReportSelector.ADVISOR, ReportSelector.SERVICE_HEALTH)
            if selector in prepared_by_selector
        ]
        RetirementsApplication._validate_catalog_coverage(
            context.scope.subscription_ids,
            selected_acquisitions,
            catalog,
            report=selector.value,
            run_id=context.run_id,
        )
        artifacts, slide_selection = RetirementsApplication._empty_artifacts(
            context,
            selected_acquisitions,
            prepared_by_selector,
            closure,
            catalog,
        )
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"replay bundle is invalid or incomplete: {exc}") from exc
    candidate = PublicationCandidate(
        context=context,
        report_closure=closure,
        artifacts=tuple(artifacts),
        acquisitions=tuple(selected_acquisitions),
        slide_selection=slide_selection,
        manifest_metadata=manifest,
        saved_inputs=saved_inputs,
    )
    receipt = application.publication_store.publish(candidate)
    return RunResult(0, context, candidate, receipt)


def _catalog_from_saved_inputs(saved_inputs: Mapping[str, Any]) -> PlatformCatalogSnapshot:
    payload = saved_inputs.get("platform_catalog")
    if not isinstance(payload, Mapping) or not isinstance(payload.get("assignments"), list):
        raise ValueError("replay bundle is missing saved platform catalog")
    assignments = tuple(
        PlatformAssignment(
            SubscriptionId(str(item["subscription_id"])),
            str(item["platform"]),
            str(item["subscription_name"]),
        )
        for item in payload["assignments"]
        if isinstance(item, Mapping)
    )
    return PlatformCatalogSnapshot(int(payload["schema_version"]), str(payload["sha256"]), assignments)


def _acquisitions_from_saved_inputs(
    saved_inputs: Mapping[str, Any],
    closure: Any,
) -> dict[str, SourceAcquisition]:
    payload = saved_inputs.get("source_acquisitions")
    if not isinstance(payload, Mapping):
        raise ValueError("replay bundle is missing saved acquisitions")
    result: dict[str, SourceAcquisition] = {}
    required = []
    if closure.requires(ReportSelector.ADVISOR):
        required.append("advisor")
    if closure.requires(ReportSelector.SERVICE_HEALTH):
        required.append("service-health")
    for source in required:
        item = payload.get(source)
        if not isinstance(item, Mapping) or not isinstance(item.get("receipt"), Mapping):
            raise ValueError(f"replay bundle is missing saved {source} acquisition")
        receipt_payload = item["receipt"]
        receipt = AcquisitionReceipt(
            source=str(receipt_payload["source"]),
            api_version=str(receipt_payload["api_version"]),
            expected_subscriptions=int(receipt_payload["expected_subscriptions"]),
            completed_subscriptions=int(receipt_payload["completed_subscriptions"]),
            pages=int(receipt_payload["pages"]),
            source_records=int(receipt_payload["source_records"]),
            complete=bool(receipt_payload["complete"]),
            continuation_tokens=tuple(str(value) for value in receipt_payload.get("continuation_tokens", ())),
            failed_subscriptions=tuple(str(value) for value in receipt_payload.get("failed_subscriptions", ())),
            completeness_reason=str(receipt_payload.get("completeness_reason", "")),
        )
        accounting = tuple(
            ObservationAccounting(
                source=str(value["source"]),
                subscription_id=str(value["subscription_id"]),
                source_identity=str(value["source_identity"]),
                destination=str(value["destination"]),
                reason=str(value.get("reason", "")),
                raw_record_ref=str(value.get("raw_record_ref", "")),
            )
            for value in item.get("accounting", ())
            if isinstance(value, Mapping)
        )
        result[source] = SourceAcquisition(
            receipt=receipt,
            records=tuple(_source_record(value) for value in item.get("records", ())),
            companion_records=tuple(item.get("companion_records", ())),
            accounting=accounting,
            collection_context=item.get("collection_context", {}),
            response_context=tuple(item.get("response_context", ())),
        )
    return result


def _source_record(value: Any) -> Any:
    if not isinstance(value, Mapping) or not isinstance(value.get("payload"), Mapping):
        return value
    return SourceRecord(
        subscription_id=str(value.get("subscription_id", "")),
        identity=str(value.get("identity", "")),
        payload=value["payload"],
        source=str(value.get("source", "")),
        page_number=int(value.get("page_number", 0)),
        continuation_token=value.get("continuation_token"),
    )


def _advisor_enrichments_from_saved_inputs(saved_inputs: Mapping[str, Any]) -> AdvisorEnrichments:
    payload = saved_inputs.get("advisor_enrichments", {})
    if not isinstance(payload, Mapping):
        raise ValueError("replay bundle has invalid Advisor enrichment inputs")
    return AdvisorEnrichments(
        metadata=payload.get("metadata", {}),
        resources=payload.get("resources", {}),
        subscriptions=payload.get("subscriptions", {}),
    )


def _service_health_evidence_from_saved_inputs(saved_inputs: Mapping[str, Any]) -> ServiceHealthSupplementalEvidence:
    payload = saved_inputs.get("service_health_evidence", {})
    if not isinstance(payload, Mapping):
        raise ValueError("replay bundle has invalid Service Health evidence inputs")
    associations = {
        (str(item["tracking_id"]).casefold(), str(item["subscription_id"]).casefold()): tuple(item.get("resources", ()))
        for item in payload.get("resource_associations", ())
        if isinstance(item, Mapping)
    }
    return ServiceHealthSupplementalEvidence(
        advisor_records=tuple(payload.get("advisor_records", ())),
        resource_inventory=payload.get("resource_inventory", {}),
        subscription_inventory=payload.get("subscription_inventory", {}),
        resource_associations=associations,
        subscription_name_sources=payload.get("subscription_name_sources", {}),
    )


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
