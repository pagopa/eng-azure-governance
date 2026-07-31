from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..acquisition.model import SourceAcquisition
from ..contracts import (
    AGGREGATE_V1,
    SLIDES_V1,
)
from ..contracts.model import Artifact
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
from ..publication.model import PublicationCandidate, PublicationError, RunResult
from ..ports import NullRunObserver, RunObserver, RuntimeEvent
from ..reports.catalog import DEFAULT_REPORT_CATALOG, ReportCatalog, ReportPlan
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


@dataclass(slots=True)
class RetirementsApplication:
    scope_source: Any
    catalog_source: Any
    advisor_source: Any
    service_health_source: Any
    publication_store: Any
    clock: Any
    run_id_factory: Any
    report_catalog: ReportCatalog = DEFAULT_REPORT_CATALOG
    observer: RunObserver = field(default_factory=NullRunObserver)

    def run(self, request: RunRequest) -> RunResult:
        report_plan = self.report_catalog.plan(request.selector)
        plan = DependencyPlan(report_plan.stages)
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
        context = RunContext(
            run_id=run_id,
            as_of_date=self._as_of_date(request),
            created_at=created_at,
            request=request,
            scope=scope,
            catalog_identity=self._catalog_identity(catalog),
            dependency_plan=plan,
        )

        prepared_by_selector: dict[ReportSelector, PreparedRawReport] = {}
        if report_plan.requires(ReportSelector.ADVISOR):
            self._emit(
                "INFO",
                "acquisition_started",
                "Starting Advisor acquisition",
                context.run_id,
                source="advisor",
            )
            advisor_acquisition = self.advisor_source.acquire(context)
            self._emit_acquisition_completed(context.run_id, advisor_acquisition)
            prepared_by_selector[ReportSelector.ADVISOR] = prepare_advisor_report(
                advisor_acquisition, context, AdvisorEnrichments()
            )
        if report_plan.requires(ReportSelector.SERVICE_HEALTH):
            self._emit(
                "INFO",
                "acquisition_started",
                "Starting Service Health acquisition",
                context.run_id,
                source="service-health",
            )
            service_health_acquisition = self.service_health_source.acquire(context)
            self._emit_acquisition_completed(context.run_id, service_health_acquisition)
            prepared_by_selector[ReportSelector.SERVICE_HEALTH] = prepare_service_health_report(
                service_health_acquisition,
                context,
                ServiceHealthSupplementalEvidence(),
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

        self._emit(
            "INFO",
            "artifact_preparation_started",
            "Preparing publication artifacts",
            context.run_id,
        )
        artifacts, slide_selection = self._empty_artifacts(
            context, acquisitions, prepared_by_selector, report_plan, catalog
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
            artifacts=tuple(artifacts),
            acquisitions=tuple(acquisitions),
            slide_selection=slide_selection,
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
        report_plan: ReportPlan,
        catalog: Any,
    ):
        by_source = {acquisition.receipt.source: acquisition for acquisition in acquisitions}
        selected = []
        slide_selection: SlideSelection | None = None
        aggregate: Artifact | None = None
        if report_plan.publishes(ReportSelector.ADVISOR):
            selected.extend(prepared_by_selector[ReportSelector.ADVISOR].artifacts)
        if report_plan.publishes(ReportSelector.SERVICE_HEALTH):
            selected.extend(prepared_by_selector[ReportSelector.SERVICE_HEALTH].artifacts)
        if report_plan.requires(ReportSelector.AGGREGATE):
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
            if report_plan.publishes(ReportSelector.AGGREGATE):
                selected.append(AGGREGATE_V1.encode(aggregate))
        if report_plan.publishes(ReportSelector.SLIDES):
            if aggregate is None:
                raise ApplicationError("slides requires an aggregate artifact")
            projected = select_slides(aggregate, context)
            if not projected.is_valid or projected.value is None:
                raise ContractValidationError(projected.diagnostics, "invalid slide contract")
            slide_selection = projected.value
            selected.append(SLIDES_V1.encode(slide_selection.artifact))
        return selected, slide_selection
