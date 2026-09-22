from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field, is_dataclass, replace
import re
from typing import Any

from ..acquisition.model import SourceAcquisition
from ..adapters.advisor_enrichment import AdvisorEnrichmentError
from ..contracts import (
    AGGREGATE_V1,
    SLIDES_V1,
)
from ..contracts.model import Artifact, EncodedArtifact
from ..contracts.aggregate_v1 import build_aggregate
from ..domain.platforms import PlatformCatalogSnapshot
from ..domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
)
from ..domain.coverage import validate_platform_coverage
from ..domain.diagnostics import Diagnostic
from ..domain.slides import SlideSelection, select_slides
from ..domain.retirements import build_source_events
from ..publication.model import PublicationCandidate, PublicationError, RunResult
from ..ports import NullRunObserver, RunObserver, RuntimeEvent
from ..reports.catalog import (
    DEFAULT_REPORT_CATALOG,
    DEFAULT_EDITORIAL_YAML,
    EditorialCatalog,
    EDITORIAL_YAML_PATH,
    build_editorial_work_list,
    render_editorial_yaml,
    ReportCatalog,
    SelectedReportClosure,
)
from ..reports.advisor import ADVISOR_REPORT, prepare_advisor_report
from ..reports.model import PreparedRawReport
from ..reports.service_health import (
    SERVICE_HEALTH_REPORT,
    prepare_service_health_report,
)
from ..domain.evidence import AdvisorEnrichments, ServiceHealthSupplementalEvidence
from .orchestration_errors import (
    ApplicationError,
    ContractValidationError,
    PlatformCoverageError,
)


class _LegacyEmptyCatalog:
    def lookup(self, subscription_id: str):
        return None


def _empty_catalog_for_legacy_check() -> _LegacyEmptyCatalog:
    return _LegacyEmptyCatalog()


def _record_payload(record: Any) -> Mapping[str, Any]:
    payload = getattr(record, "payload", record)
    return payload if isinstance(payload, Mapping) else {}


def _record_subscription_id(record: Any, event: Mapping[str, Any]) -> str:
    return str(
        event.get("subscriptionId")
        or event.get("subscription_id")
        or event.get("_subscriptionId")
        or getattr(record, "subscription_id", "")
        or ""
    ).strip()


def _resource_graph_tracking_id(resource_id: str) -> str:
    segments = [segment for segment in resource_id.split("/") if segment]
    lowered = [segment.casefold() for segment in segments]
    if "events" not in lowered:
        return ""
    index = lowered.index("events")
    return segments[index + 1] if index + 1 < len(segments) else ""


def _normalize_resource_id(resource_id: str) -> str:
    return re.sub(r"/+", "/", resource_id.strip()).casefold().rstrip("/")


def _json_safe(value: Any) -> Any:
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _saved_acquisition(acquisition: SourceAcquisition) -> dict[str, Any]:
    return {
        "receipt": _json_safe(acquisition.receipt),
        "records": _json_safe(acquisition.records),
        "companion_records": _json_safe(acquisition.companion_records),
        "accounting": _json_safe(acquisition.accounting),
        "collection_context": _json_safe(acquisition.collection_context),
        "response_context": _json_safe(acquisition.response_context),
    }


def _source_yaml(source: Any) -> str:
    source_path = getattr(source, "path", None)
    if source_path is None:
        return ""
    try:
        return source_path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _saved_catalog(catalog: Any, source: Any = None) -> dict[str, Any]:
    assignments = []
    for assignment in getattr(catalog, "assignments", ()):
        assignments.append({
            "subscription_id": str(getattr(getattr(assignment, "subscription_id", None), "value", "")),
            "platform": str(getattr(assignment, "platform", "")),
            "subscription_name": str(getattr(assignment, "subscription_name", "")),
        })
    return {
        "schema_version": int(getattr(catalog, "schema_version", 1)),
        "sha256": str(getattr(catalog, "sha256", "")),
        "assignments": assignments,
        "yaml": _source_yaml(source),
    }


def _saved_editorial_catalog(
    catalog: Any,
    source: Any = None,
    yaml_text: str | None = None,
) -> Any:
    if catalog is None:
        return None
    return {
        "schema_version": int(catalog.schema_version),
        "sha256": str(catalog.sha256),
        "items": [_json_safe(item) for item in catalog.items],
        "yaml": yaml_text if yaml_text is not None else _source_yaml(source),
    }


def _effective_editorial_yaml(publication_store: Any, source: Any, as_of_date: Any) -> str:
    reader = getattr(publication_store, "effective_editorial_yaml", None)
    if callable(reader):
        value = reader(as_of_date)
        if value is not None:
            return value.decode("utf-8") if isinstance(value, bytes) else str(value)
    return _source_yaml(source) or DEFAULT_EDITORIAL_YAML


def _load_editorial_catalog(source: Any, yaml_text: str) -> EditorialCatalog:
    loader = getattr(source, "load_text", None)
    if callable(loader):
        return loader(yaml_text)
    return source.load()


def _saved_service_health_evidence(evidence: ServiceHealthSupplementalEvidence) -> dict[str, Any]:
    return {
        "advisor_records": _json_safe(evidence.advisor_records),
        "resource_inventory": _json_safe(evidence.resource_inventory),
        "subscription_inventory": _json_safe(evidence.subscription_inventory),
        "resource_associations": [
            {
                "tracking_id": key[0],
                "subscription_id": key[1],
                "resources": _json_safe(values),
            }
            for key, values in sorted(evidence.resource_associations.items())
        ],
        "subscription_name_sources": _json_safe(evidence.subscription_name_sources),
    }


@dataclass(slots=True)
class RetirementsApplication:
    scope_source: Any
    catalog_source: Any
    advisor_source: Any
    service_health_source: Any
    publication_store: Any
    clock: Any
    run_id_factory: Any
    resource_graph_source: Any | None = None
    report_catalog: ReportCatalog = DEFAULT_REPORT_CATALOG
    observer: RunObserver = field(default_factory=NullRunObserver)
    advisor_enrichment_source: Any | None = None
    editorial_catalog_source: Any | None = None

    def run(self, request: RunRequest) -> RunResult:
        report_closure = self.report_catalog.plan(request.selector)
        plan = DependencyPlan(report_closure.stages)
        run_id = self.run_id_factory.new_id()
        created_at = self.clock.now()
        self._emit(
            "INFO",
            "run_started",
            "Run started",
            run_id,
            report=request.selector.value,
        )
        self._emit(
            "INFO",
            "scope_resolution_started",
            "Resolving subscription scope",
            run_id,
        )
        scope = self.scope_source.resolve(request, run_id=run_id)
        self._emit(
            "INFO",
            "scope_resolved",
            "Subscription scope resolved",
            run_id,
            subscriptions=len(scope.subscription_ids),
            mode=scope.mode,
        )
        self._emit(
            "INFO",
            "catalog_load_started",
            "Loading platform catalog",
            run_id,
        )
        catalog = self.catalog_source.load()
        self._emit(
            "INFO",
            "catalog_loaded",
            "Platform catalog loaded",
            run_id,
            schema_version=getattr(catalog, "schema_version", ""),
        )
        editorial_yaml = DEFAULT_EDITORIAL_YAML
        editorial_catalog = None
        if self.editorial_catalog_source is not None:
            editorial_yaml = _effective_editorial_yaml(
                self.publication_store,
                self.editorial_catalog_source,
                self._as_of_date(request),
            )
            editorial_catalog = _load_editorial_catalog(
                self.editorial_catalog_source,
                editorial_yaml,
            )
        context = RunContext(
            run_id=run_id,
            as_of_date=self._as_of_date(request),
            created_at=created_at,
            request=request,
            scope=scope,
            catalog_identity=self._catalog_identity(catalog),
            dependency_plan=plan,
            editorial_catalog_identity=(
                self._catalog_identity(editorial_catalog) if editorial_catalog is not None else None
            ),
        )

        prepared_by_selector: dict[ReportSelector, PreparedRawReport] = {}
        saved_inputs: dict[str, Any] = {
            "schema_version": 1,
            "source_acquisitions": {},
            "platform_catalog": _saved_catalog(catalog, self.catalog_source),
            "editorial_catalog": _saved_editorial_catalog(
                editorial_catalog,
                self.editorial_catalog_source,
                editorial_yaml,
            ),
            "publication_settings": {
                "committee_window_months": request.committee_window_months,
            },
        }
        if report_closure.requires(ReportSelector.ADVISOR):
            self._emit(
                "INFO",
                "acquisition_started",
                "Starting Advisor acquisition",
                context.run_id,
                source="advisor",
            )
            advisor_acquisition = self.advisor_source.acquire(context)
            saved_inputs["source_acquisitions"]["advisor"] = _saved_acquisition(advisor_acquisition)
            self._emit_acquisition_completed(context.run_id, advisor_acquisition)
            advisor_enrichments = AdvisorEnrichments()
            if self.advisor_enrichment_source is not None:
                try:
                    advisor_enrichments = self.advisor_enrichment_source.enrich(
                        context,
                        advisor_acquisition.records,
                    )
                except AdvisorEnrichmentError as exc:
                    raise ApplicationError(
                        "advisor enrichment failed; existing monthly bundle was not changed"
                    ) from exc
            saved_inputs["advisor_enrichments"] = _json_safe(advisor_enrichments)
            prepared_by_selector[ReportSelector.ADVISOR] = prepare_advisor_report(
                advisor_acquisition, context, advisor_enrichments
            )
        if report_closure.requires(ReportSelector.SERVICE_HEALTH):
            self._emit(
                "INFO",
                "acquisition_started",
                "Starting Service Health acquisition",
                context.run_id,
                source="service-health",
            )
            service_health_acquisition = self.service_health_source.acquire(context)
            saved_inputs["source_acquisitions"]["service-health"] = _saved_acquisition(service_health_acquisition)
            self._emit_acquisition_completed(context.run_id, service_health_acquisition)
            service_health_evidence = self._collect_service_health_evidence(
                context, service_health_acquisition, catalog
            )
            saved_inputs["service_health_evidence"] = _saved_service_health_evidence(service_health_evidence)
            prepared_by_selector[ReportSelector.SERVICE_HEALTH] = prepare_service_health_report(
                service_health_acquisition,
                context,
                service_health_evidence,
            )
        acquisitions = [
            prepared_by_selector[selector].acquisition
            for selector in (ReportSelector.ADVISOR, ReportSelector.SERVICE_HEALTH)
            if selector in prepared_by_selector
        ]

        self._emit(
            "INFO",
            "coverage_validation_started",
            "Validating platform coverage",
            context.run_id,
        )
        self._validate_catalog_coverage(
            scope.subscription_ids,
            acquisitions,
            catalog,
            report=request.selector.value,
            run_id=context.run_id,
        )
        self._emit(
            "INFO",
            "coverage_validated",
            "Platform coverage validated",
            context.run_id,
        )

        editorial_work_list = ()
        if editorial_catalog is not None:
            source_events, _ = build_source_events(
                next((item.records for item in acquisitions if item.receipt.source == "advisor"), ()),
                next((item.records for item in acquisitions if item.receipt.source == "service-health"), ()),
            )
            editorial_work_list = build_editorial_work_list(editorial_catalog, source_events)
            if report_closure.publishes(ReportSelector.SLIDES):
                editorial_yaml = render_editorial_yaml(
                    editorial_yaml,
                    editorial_catalog,
                    editorial_work_list,
                )
                editorial_catalog = _load_editorial_catalog(
                    self.editorial_catalog_source,
                    editorial_yaml,
                )
                context = replace(
                    context,
                    editorial_catalog_identity=self._catalog_identity(editorial_catalog),
                )
            saved_inputs["editorial_catalog"] = _saved_editorial_catalog(
                editorial_catalog,
                self.editorial_catalog_source,
                editorial_yaml,
            )

        self._emit(
            "INFO",
            "artifact_preparation_started",
            "Preparing publication artifacts",
            context.run_id,
        )
        artifacts, slide_selection = self._empty_artifacts(
            context,
            acquisitions,
            prepared_by_selector,
            report_closure,
            catalog,
            editorial_catalog,
            editorial_yaml=editorial_yaml,
        )
        self._emit(
            "INFO",
            "artifacts_prepared",
            "Publication artifacts prepared",
            context.run_id,
            artifact_paths=[artifact.logical_path for artifact in artifacts],
            rows=sum(artifact.rows for artifact in artifacts),
            bytes=sum(artifact.bytes for artifact in artifacts),
        )
        candidate = PublicationCandidate(
            context=context,
            report_closure=report_closure,
            artifacts=tuple(artifacts),
            acquisitions=tuple(acquisitions),
            slide_selection=slide_selection,
            editorial_work_list=editorial_work_list,
            saved_inputs=saved_inputs,
        )
        try:
            self._emit(
                "INFO",
                "publication_started",
                "Publishing monthly bundle",
                context.run_id,
            )
            receipt = self.publication_store.publish(candidate)
        except PublicationError as exc:
            diagnostic_stage = (
                exc.diagnostics[0].stage
                if exc.diagnostics
                else "publication"
            )
            raise self._translate_publication_error(
                exc,
                context,
                stage=diagnostic_stage,
            ) from exc
        self._emit(
            "INFO",
            "publication_completed",
            "Monthly bundle published",
            context.run_id,
            generation=receipt.generation,
            current_reference=receipt.current_reference,
        )
        self._emit(
            "INFO",
            "run_completed",
            "Run completed",
            context.run_id,
            artifacts=len(candidate.artifacts),
        )
        return RunResult(
            exit_status=0,
            context=context,
            candidate=candidate,
            publication_receipt=receipt,
        )

    def _collect_service_health_evidence(
        self,
        context: RunContext,
        acquisition: SourceAcquisition,
        catalog: Any,
    ) -> ServiceHealthSupplementalEvidence:
        if not acquisition.records:
            return ServiceHealthSupplementalEvidence()
        if self.resource_graph_source is None:
            raise ApplicationError("service-health supplemental evidence requires Resource Graph")

        try:
            subscription_inventory: dict[str, Mapping[str, Any]] = {}
            subscription_name_sources: dict[str, str] = {}
            for raw_row in self.resource_graph_source.lookup_subscription_inventory(context):
                if not isinstance(raw_row, Mapping):
                    raise ValueError("Resource Graph subscription inventory row has unsupported shape")
                subscription_id = str(
                    raw_row.get("subscriptionId") or raw_row.get("subscription_id") or ""
                ).strip()
                subscription_name = str(
                    raw_row.get("subscriptionName") or raw_row.get("name") or ""
                ).strip()
                if not subscription_id or not subscription_name:
                    continue
                normalized_subscription_id = subscription_id.casefold()
                inventory_row = dict(raw_row)
                inventory_row.update({"id": subscription_id, "name": subscription_name})
                subscription_inventory[normalized_subscription_id] = inventory_row
                subscription_name_sources[normalized_subscription_id] = "resource_graph_inventory"

            for subscription_id in context.scope.subscription_ids:
                normalized_subscription_id = subscription_id.casefold()
                if normalized_subscription_id in subscription_inventory:
                    continue
                lookup = getattr(catalog, "lookup", None)
                assignment = lookup(subscription_id) if callable(lookup) else None
                if not assignment or len(assignment) < 2:
                    raise ApplicationError(
                        f"service-health subscription name unavailable: {subscription_id}"
                    )
                platform, subscription_name = assignment[0], str(assignment[1]).strip()
                if not subscription_name:
                    raise ApplicationError(
                        f"service-health subscription name unavailable: {subscription_id}"
                    )
                subscription_inventory[normalized_subscription_id] = {
                    "id": subscription_id,
                    "name": subscription_name,
                    "platform": str(platform),
                }
                subscription_name_sources[normalized_subscription_id] = "platform_catalog"

            event_keys: set[tuple[str, str]] = set()
            for raw_record in acquisition.records:
                event = _record_payload(raw_record)
                properties = event.get("properties")
                properties_map = properties if isinstance(properties, Mapping) else {}
                tracking_id = str(properties_map.get("trackingId") or event.get("name") or "").strip()
                subscription_id = _record_subscription_id(raw_record, event)
                if tracking_id and subscription_id:
                    event_keys.add((tracking_id.casefold(), subscription_id.casefold()))

            associations: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
            for raw_row in self.resource_graph_source.lookup_service_health_resources(context):
                if not isinstance(raw_row, Mapping):
                    raise ValueError("Resource Graph service-health row has unsupported shape")
                properties = raw_row.get("properties")
                if not isinstance(properties, Mapping):
                    raise ValueError("Resource Graph service-health properties have unsupported shape")
                tracking_id = _resource_graph_tracking_id(str(raw_row.get("id") or ""))
                subscription_id = str(
                    raw_row.get("subscriptionId") or raw_row.get("subscription_id") or ""
                ).strip()
                if not tracking_id or not subscription_id:
                    raise ValueError("Resource Graph service-health row has incomplete identity")
                key = (tracking_id.casefold(), subscription_id.casefold())
                if key not in event_keys:
                    continue
                resource_id = str(properties.get("targetResourceId") or "").strip()
                if not resource_id:
                    continue
                associations.setdefault(key, []).append(
                    {
                        "resourceId": resource_id,
                        "resourceType": str(properties.get("targetResourceType") or ""),
                        "region": str(properties.get("targetRegion") or ""),
                        "subscriptionId": subscription_id,
                        "resource_evidence_source": "service_health_resource_graph",
                    }
                )

            resource_ids = tuple(
                sorted(
                    {
                        str(item["resourceId"])
                        for values in associations.values()
                        for item in values
                        if item.get("resourceId")
                    },
                    key=str.casefold,
                )
            )
            resource_inventory: dict[str, Mapping[str, Any]] = {}
            for raw_row in self.resource_graph_source.lookup_resources(context, resource_ids):
                if not isinstance(raw_row, Mapping):
                    raise ValueError("Resource Graph resource inventory row has unsupported shape")
                resource_id = str(raw_row.get("id") or raw_row.get("resourceId") or "").strip()
                if resource_id:
                    resource_inventory[_normalize_resource_id(resource_id)] = raw_row

            return ServiceHealthSupplementalEvidence(
                resource_associations={
                    key: tuple(values) for key, values in associations.items()
                },
                resource_inventory=resource_inventory,
                subscription_inventory=subscription_inventory,
                subscription_name_sources=subscription_name_sources,
            )
        except ApplicationError:
            raise
        except Exception as exc:
            raise ApplicationError(
                "service-health supplemental evidence acquisition failed"
            ) from exc

    def _emit(
        self,
        level: str,
        event: str,
        message: str,
        run_id: str,
        **context: object,
    ) -> None:
        self.observer.emit(RuntimeEvent(level, event, message, run_id, context))

    def _emit_acquisition_completed(self, run_id: str, acquisition: SourceAcquisition) -> None:
        receipt = acquisition.receipt
        self._emit(
            "INFO",
            "acquisition_completed",
            f"{receipt.source} acquisition completed",
            run_id,
            source=receipt.source,
            subscriptions=receipt.completed_subscriptions,
            pages=receipt.pages,
            records=receipt.source_records,
            complete=receipt.complete,
        )

    @staticmethod
    def _translate_publication_error(
        error: PublicationError,
        context: RunContext,
        *,
        stage: str,
    ) -> ApplicationError:
        diagnostics = error.diagnostics
        if not diagnostics:
            diagnostics = (
                Diagnostic(
                    severity="error",
                    code="publication_error",
                    stage=stage,
                    report=context.request.selector.value,
                    run_id=context.run_id,
                    message="publication failed before the monthly bundle replacement",
                ),
            )
        return ApplicationError("publication failed; existing monthly bundle was not changed", diagnostics)

    @staticmethod
    def _as_of_date(request: RunRequest):
        if request.as_of_date is not None:
            return request.as_of_date
        from datetime import date

        return date.today()

    @staticmethod
    def _catalog_identity(catalog: Any) -> CatalogIdentity:
        identity = getattr(catalog, "identity", None)
        if not isinstance(identity, CatalogIdentity):
            try:
                identity = CatalogIdentity(catalog.schema_version, catalog.sha256)
            except (AttributeError, TypeError, ValueError) as exc:
                raise ApplicationError("catalog does not expose a valid identity") from exc
        return identity

    @staticmethod
    def _validate_catalog_coverage(
        subscription_ids: tuple[str, ...],
        acquisitions: list[SourceAcquisition],
        catalog: Any,
        *,
        report: str,
        run_id: str,
    ) -> None:
        records = tuple(
            record
            for acquisition in acquisitions
            for record in acquisition.records
        )
        if callable(getattr(catalog, "lookup", None)):
            result = validate_platform_coverage(
                subscription_ids, records, catalog, report=report, run_id=run_id
            )
            if not result.is_valid:
                raise PlatformCoverageError(result.diagnostics)
            return

        # Keep the narrow test/catalog port used by the earlier empty-run gate.
        covered = set(getattr(catalog, "subscription_ids", ()))
        required = set(subscription_ids)
        for record in records:
            raw_id = str(record.get("subscription_id", ""))
            if raw_id:
                required.add(raw_id)
        missing = sorted(required - covered)
        if missing:
            raise PlatformCoverageError(
                tuple(
                    validate_platform_coverage(
                        (item,), (), _empty_catalog_for_legacy_check(), report=report, run_id=run_id
                    ).diagnostics[0]
                    for item in missing
                )
            )

    @staticmethod
    def _empty_artifacts(
        context: RunContext,
        acquisitions: list[SourceAcquisition],
        prepared_by_selector: dict[ReportSelector, PreparedRawReport],
        report_closure: SelectedReportClosure,
        catalog: Any,
        editorial_catalog: EditorialCatalog | None = None,
        editorial_yaml: str = "",
    ):
        by_source = {acquisition.receipt.source: acquisition for acquisition in acquisitions}
        selected = []
        slide_selection: SlideSelection | None = None
        aggregate: Artifact | None = None
        if report_closure.publishes(ReportSelector.ADVISOR):
            selected.extend(prepared_by_selector[ReportSelector.ADVISOR].artifacts)
        if report_closure.publishes(ReportSelector.SERVICE_HEALTH):
            selected.extend(prepared_by_selector[ReportSelector.SERVICE_HEALTH].artifacts)
        if report_closure.requires(ReportSelector.AGGREGATE):
            aggregate = AGGREGATE_V1.empty_artifact(context)
            if any(acquisition.records for acquisition in acquisitions):
                if not isinstance(catalog, PlatformCatalogSnapshot):
                    raise ApplicationError("aggregate requires a validated platform catalog snapshot")
                def records_for(source: str):
                    acquisition = by_source.get(source)
                    return acquisition.records if acquisition is not None else ()

                aggregate_records = build_aggregate(
                    records_for("advisor"),
                    records_for("service-health"),
                    context=context,
                    catalog=catalog,
                    editorial_catalog=editorial_catalog,
                )
                aggregate = Artifact(
                    contract=aggregate.contract,
                    schema_version=aggregate.schema_version,
                    run_id=aggregate.run_id,
                    records=aggregate_records,
                )
                checked = AGGREGATE_V1.validate(aggregate, context)
                if not checked.is_valid:
                    raise ContractValidationError(checked.diagnostics, "invalid aggregate contract")
            if report_closure.publishes(ReportSelector.AGGREGATE):
                selected.append(AGGREGATE_V1.encode(aggregate))
        if report_closure.publishes(ReportSelector.SLIDES):
            if aggregate is None:
                raise ApplicationError("slides requires an aggregate artifact")
            projected = select_slides(aggregate, context)
            if not projected.is_valid or projected.value is None:
                raise ContractValidationError(projected.diagnostics, "invalid slide contract")
            slide_selection = projected.value
            selected.append(SLIDES_V1.encode(slide_selection.artifact))
            selected.append(
                EncodedArtifact(
                    logical_path=EDITORIAL_YAML_PATH,
                    data=(editorial_yaml or DEFAULT_EDITORIAL_YAML).encode("utf-8"),
                    rows=0,
                    media_type="application/yaml",
                    schema_version=1,
                    run_id=context.run_id,
                )
            )
        return selected, slide_selection
