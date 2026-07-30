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
from ..domain.execution import CatalogIdentity, ReportSelector, RunContext, RunRequest
from ..publication.model import PublicationCandidate, RunResult
from .planning import build_dependency_plan


class ApplicationError(RuntimeError):
    """A stable application boundary failure before publication."""


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
        self._validate_catalog_coverage(scope.subscription_ids, catalog)
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

        if any(acquisition.records for acquisition in acquisitions):
            raise ApplicationError(
                "non-empty raw publication requires evidence-union coverage"
            )

        artifacts = self._empty_artifacts(context, acquisitions, request)
        candidate = PublicationCandidate(
            context=context,
            dependency_plan=plan,
            artifacts=tuple(artifacts),
            acquisitions=tuple(acquisitions),
        )
        generation = self.publication_store.stage(candidate)
        receipt = self.publication_store.commit(generation)
        return RunResult(
            exit_status=0,
            context=context,
            candidate=candidate,
            publication_receipt=receipt,
        )

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
            raise ApplicationError("catalog does not expose a valid identity")
        return identity

    @staticmethod
    def _validate_catalog_coverage(subscription_ids: tuple[str, ...], catalog: Any) -> None:
        covered = set(getattr(catalog, "subscription_ids", ()))
        missing = sorted(set(subscription_ids) - covered)
        if missing:
            raise ApplicationError(f"catalog does not cover scope: {', '.join(missing)}")

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
            code = result.diagnostics[0].code if result.diagnostics else "unknown_raw_contract_error"
            raise ApplicationError(f"invalid {source_name} raw contract: {code}")
        contract = ADVISOR_V1 if source_name == "advisor" else SERVICE_HEALTH_V1
        contract_result = contract.validate(result.value.artifact, context)
        if not contract_result.is_valid:
            code = contract_result.diagnostics[0].code
            raise ApplicationError(f"invalid {source_name} raw contract: {code}")
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
    ):
        by_source = {acquisition.receipt.source: acquisition for acquisition in acquisitions}
        selected = []
        if request.selector in (ReportSelector.ALL, ReportSelector.ADVISOR):
            advisor = ADVISOR_V1.empty_artifact(context)
            if "advisor" in by_source:
                advisor = advisor.__class__(
                    contract=advisor.contract,
                    schema_version=advisor.schema_version,
                    run_id=advisor.run_id,
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
                    companion_records=by_source["service-health"].companion_records,
                )
            selected.extend((SERVICE_HEALTH_V1.encode(health), SERVICE_HEALTH_V1.encode_companion(health)))
        if request.selector in (ReportSelector.ALL, ReportSelector.AGGREGATE, ReportSelector.SLIDES):
            selected.append(AGGREGATE_V1.encode(AGGREGATE_V1.empty_artifact(context)))
        if request.selector in (ReportSelector.ALL, ReportSelector.SLIDES):
            selected.append(SLIDES_V1.encode(SLIDES_V1.empty_artifact(context)))
        return selected
