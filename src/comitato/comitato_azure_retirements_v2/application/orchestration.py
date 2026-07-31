from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..acquisition.model import SourceAcquisition
from ..application.advisor import AdvisorEnrichments, normalize_advisor
from ..application.service_health import (
    ServiceHealthSupplementalEvidence,
    normalize_service_health,
)
from ..contracts import (
    ADVISOR_V1,
    AGGREGATE_V1,
    SERVICE_HEALTH_V1,
    SLIDES_V1,
)
from ..contracts.model import Artifact
from ..contracts.aggregate_v1 import build_aggregate
from ..domain.platforms import PlatformCatalogSnapshot
from ..domain.execution import CatalogIdentity, ReportSelector, RunContext, RunRequest
from ..domain.coverage import validate_platform_coverage
from ..domain.diagnostics import Diagnostic
from ..domain.slides import SlideSelection, select_slides
from ..publication.model import PublicationCandidate, PublicationError, RunResult
from .planning import build_dependency_plan


class ApplicationError(RuntimeError):
    """A stable application boundary failure before publication."""

    def __init__(self, message: str, diagnostics=()) -> None:
        self.diagnostics = tuple(diagnostics)
        super().__init__(message)


class PlatformCoverageError(ApplicationError):
    def __init__(self, diagnostics) -> None:
        self.diagnostics = tuple(diagnostics)
        count = len(self.diagnostics)
        super().__init__(
            f"platform_mapping_unmapped_subscription: {count} unmapped subscription(s); "
            "publication not changed",
            self.diagnostics,
        )


class ContractValidationError(ApplicationError):
    def __init__(self, diagnostics, message: str) -> None:
        self.diagnostics = tuple(diagnostics)
        code = self.diagnostics[0].code if self.diagnostics else "unknown"
        super().__init__(f"{message}: {code}", self.diagnostics)


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

    def run(self, request: RunRequest) -> RunResult:
        plan = build_dependency_plan(request.selector)
        scope = self.scope_source.resolve(request)
        catalog = self.catalog_source.load()
        context = RunContext(
            run_id=self.run_id_factory.new_id(),
            as_of_date=self._as_of_date(request),
            created_at=self.clock.now(),
            request=request,
            scope=scope,
            catalog_identity=self._catalog_identity(catalog),
            dependency_plan=plan,
        )

        acquisitions: list[SourceAcquisition] = []
        if "advisor" in plan.stages:
            acquisitions.append(self._prepare_raw_acquisition("advisor", self.advisor_source.acquire(context), context))
        if "service-health" in plan.stages:
            acquisitions.append(self._prepare_raw_acquisition("service-health", self.service_health_source.acquire(context), context))

        self._validate_catalog_coverage(
            scope.subscription_ids,
            acquisitions,
            catalog,
            report=request.selector.value,
            run_id=context.run_id,
        )

        artifacts, slide_selection = self._empty_artifacts(context, acquisitions, request, catalog)
        candidate = PublicationCandidate(
            context=context,
            dependency_plan=plan,
            artifacts=tuple(artifacts),
            acquisitions=tuple(acquisitions),
            slide_selection=slide_selection,
        )
        try:
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
        return RunResult(
            exit_status=0,
            context=context,
            candidate=candidate,
            publication_receipt=receipt,
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
                    message="publication failed before the current-generation switch",
                ),
            )
        return ApplicationError("publication failed; current publication was not changed", diagnostics)

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
    def _complete_empty_acquisition(
        source_name: str, acquisition: SourceAcquisition, context: RunContext
    ) -> SourceAcquisition:
        if not acquisition.receipt.is_complete:
            raise ApplicationError(f"incomplete {source_name} acquisition")
        if acquisition.records:
            raise ApplicationError(f"non-empty {source_name} path is not supported")
        if acquisition.receipt.source_records != 0:
            raise ApplicationError(f"non-empty {source_name} path is not supported")
        return acquisition

    @staticmethod
    def _prepare_raw_acquisition(
        source_name: str, acquisition: SourceAcquisition, context: RunContext
    ) -> SourceAcquisition:
        if not acquisition.receipt.is_complete:
            raise ApplicationError(f"incomplete {source_name} acquisition")
        if not acquisition.records:
            if acquisition.receipt.source_records != 0:
                raise ApplicationError(f"inconsistent {source_name} acquisition receipt")
            return acquisition
        if source_name == "advisor":
            result = normalize_advisor(acquisition, context, AdvisorEnrichments())
        else:
            result = normalize_service_health(
                acquisition, context, ServiceHealthSupplementalEvidence()
            )
        if not result.is_valid or result.value is None:
            raise ContractValidationError(
                result.diagnostics,
                f"invalid {source_name} raw contract",
            )
        contract = ADVISOR_V1 if source_name == "advisor" else SERVICE_HEALTH_V1
        contract_result = contract.validate(result.value.artifact, context)
        if not contract_result.is_valid:
            raise ContractValidationError(
                contract_result.diagnostics,
                f"invalid {source_name} raw contract",
            )
        return SourceAcquisition(
            receipt=acquisition.receipt,
            records=result.value.artifact.records,
            companion_records=result.value.artifact.companion_records,
        )

    @staticmethod
    def _empty_artifacts(
        context: RunContext,
        acquisitions: list[SourceAcquisition],
        request: RunRequest,
        catalog: Any,
    ):
        by_source = {acquisition.receipt.source: acquisition for acquisition in acquisitions}
        selected = []
        slide_selection: SlideSelection | None = None
        if request.selector in (ReportSelector.ALL, ReportSelector.ADVISOR):
            advisor = ADVISOR_V1.empty_artifact(context)
            if "advisor" in by_source:
                advisor = advisor.__class__(
                    contract=advisor.contract,
                    schema_version=advisor.schema_version,
                    run_id=advisor.run_id,
                    records=by_source["advisor"].records,
                    companion_records=by_source["advisor"].companion_records,
                )
            selected.extend((ADVISOR_V1.encode(advisor), ADVISOR_V1.encode_companion(advisor)))
        if request.selector in (ReportSelector.ALL, ReportSelector.SERVICE_HEALTH):
            health = SERVICE_HEALTH_V1.empty_artifact(context)
            if "service-health" in by_source:
                health = health.__class__(
                    contract=health.contract,
                    schema_version=health.schema_version,
                    run_id=health.run_id,
                    records=by_source["service-health"].records,
                    companion_records=by_source["service-health"].companion_records,
                )
            selected.extend((SERVICE_HEALTH_V1.encode(health), SERVICE_HEALTH_V1.encode_companion(health)))
        if request.selector in (ReportSelector.ALL, ReportSelector.AGGREGATE, ReportSelector.SLIDES):
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
            if request.selector in (ReportSelector.ALL, ReportSelector.AGGREGATE):
                selected.append(AGGREGATE_V1.encode(aggregate))
        if request.selector in (ReportSelector.ALL, ReportSelector.SLIDES):
            if aggregate is None:
                raise ApplicationError("slides requires an aggregate artifact")
            projected = select_slides(aggregate, context)
            if not projected.is_valid or projected.value is None:
                raise ContractValidationError(projected.diagnostics, "invalid slide contract")
            slide_selection = projected.value
            selected.append(SLIDES_V1.encode(slide_selection.artifact))
        return selected, slide_selection
