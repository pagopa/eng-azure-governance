from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import date, datetime
from hashlib import sha256
from typing import Any

from ..acquisition.evidence import ObservationAccounting
from ..acquisition.model import AcquisitionReceipt, SourceAcquisition
from ..config import RuntimeConfig
from ..contracts.codecs import canonical_json
from ..domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)
from ..publication.model import PublicationCandidate, RunResult
from ..reports.advisor.normalize import prepare_advisor_report
from ..reports.service_health.normalize import prepare_service_health_report
from .orchestration import RetirementsApplication
from .saved_inputs import (
    acquisitions_from_saved_inputs,
    advisor_enrichments_from_saved_inputs,
    catalog_from_saved_inputs,
    service_health_evidence_from_saved_inputs,
)


def run_replay(config: RuntimeConfig, application: Any) -> RunResult:
    bundle = config.replay_bundle_path
    if bundle is None:
        raise ValueError("replay bundle is required")
    try:
        manifest = json.loads(
            (bundle / "publication-manifest.json").read_text(encoding="utf-8")
        )
        if not isinstance(manifest.get("saved_inputs"), Mapping):
            if manifest.get("manifest_schema_version") == 1:
                raise ValueError(
                    "legacy schema-1 replay is unsupported because saved input evidence is absent"
                )
            raise ValueError("replay bundle requires saved inputs")
        saved_inputs = manifest["saved_inputs"]
        expected_saved_inputs_hash = str(manifest.get("saved_inputs_sha256", ""))
        actual_saved_inputs_hash = sha256(
            canonical_json(saved_inputs).encode("utf-8")
        ).hexdigest()
        if (
            not expected_saved_inputs_hash
            or expected_saved_inputs_hash != actual_saved_inputs_hash
        ):
            raise ValueError("replay bundle saved inputs integrity check failed")
        as_of_date = date.fromisoformat(str(manifest["as_of_date"]))
        created_at = datetime.fromisoformat(
            str(manifest["created_at"]).replace("Z", "+00:00")
        )
        catalog_payload = manifest["catalog"]
        selector = ReportSelector(str(manifest["selector"]))
        committee_window_months = int(
            manifest.get("settings", {}).get("committee_window_months", 12)
        )
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
            scope=Scope(
                tuple(manifest["scope"]["subscription_ids"]),
                str(manifest["scope"]["mode"]),
            ),
            catalog_identity=CatalogIdentity(
                int(catalog_payload["schema_version"]), str(catalog_payload["sha256"])
            ),
            dependency_plan=DependencyPlan(tuple(manifest["dependency_closure"])),
        )
        closure = application.report_catalog.plan(selector)
        catalog = catalog_from_saved_inputs(saved_inputs)
        acquisitions = acquisitions_from_saved_inputs(saved_inputs, closure)
        prepared_by_selector = {}
        if closure.requires(ReportSelector.ADVISOR):
            advisor = acquisitions["advisor"]
            enrichments = advisor_enrichments_from_saved_inputs(saved_inputs)
            prepared_by_selector[ReportSelector.ADVISOR] = prepare_advisor_report(
                advisor, context, enrichments
            )
        if closure.requires(ReportSelector.SERVICE_HEALTH):
            service_health = acquisitions["service-health"]
            supplemental = service_health_evidence_from_saved_inputs(saved_inputs)
            prepared_by_selector[ReportSelector.SERVICE_HEALTH] = (
                prepare_service_health_report(service_health, context, supplemental)
            )
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