from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

import pytest

from src.comitato.comitato_azure_retirements_v2.adapters.advisor_enrichment import (
    AdvisorEnrichmentError,
    AzureAdvisorEnrichmentSource,
)
from src.comitato.comitato_azure_retirements_v2.domain.evidence import AdvisorEnrichments
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)


def context() -> RunContext:
    request = RunRequest(ReportSelector.ADVISOR, ("sub",), date(2026, 7, 31))
    return RunContext(
        run_id="run-enrichment",
        as_of_date=date(2026, 7, 31),
        created_at=datetime(2026, 7, 31, tzinfo=timezone.utc),
        request=request,
        scope=Scope(("sub",), mode="explicit"),
        catalog_identity=CatalogIdentity(1, "0" * 64),
        dependency_plan=DependencyPlan(("scope", "catalog", "advisor")),
    )


def recommendation(service_id: str, resource_id: str) -> dict[str, Any]:
    return {
        "id": "/subscriptions/SUB/providers/Microsoft.Advisor/recommendations/rec-1",
        "subscriptionId": "SUB",
        "properties": {
            "recommendationTypeId": service_id,
            "resourceMetadata": {"resourceId": resource_id},
        },
    }


@dataclass
class FakeMetadataSource:
    rows: tuple[dict[str, Any], ...] = ()
    error: Exception | None = None

    def acquire(self, run_context: RunContext) -> tuple[dict[str, Any], ...]:
        if self.error is not None:
            raise self.error
        return self.rows


@dataclass
class FakeResourceGraphSource:
    resources: tuple[dict[str, Any], ...] = ()
    subscriptions: tuple[dict[str, Any], ...] = ()
    resource_error: Exception | None = None
    subscription_error: Exception | None = None

    def lookup(
        self,
        run_context: RunContext,
        resource_ids: tuple[str, ...] = (),
    ) -> tuple[dict[str, Any], ...]:
        if self.resource_error is not None:
            raise self.resource_error
        return self.resources

    def lookup_subscriptions(self, run_context: RunContext) -> tuple[dict[str, Any], ...]:
        if self.subscription_error is not None:
            raise self.subscription_error
        return self.subscriptions


def test_enrichment_indexes_metadata_resource_and_subscription_keys_case_insensitively() -> None:
    resource_id = "/subscriptions/SUB/resourceGroups/RG/providers/Microsoft.Web/sites/app"
    source = AzureAdvisorEnrichmentSource(
        FakeMetadataSource(
            rows=(
                {"id": "SERVICE-A", "serviceRetirement": {"serviceId": "SERVICE-A"}},
            )
        ),
        FakeResourceGraphSource(
            resources=(
                {
                    "resourceId": resource_id,
                    "name": "app",
                    "subscriptionId": "SUB",
                },
            ),
            subscriptions=({"subscriptionId": "SUB", "name": "DEV"},),
        ),
    )

    result = source.enrich(context(), (recommendation("service-a", resource_id.casefold()),))

    assert result.metadata["service-a"]["id"] == "SERVICE-A"
    assert result.resources[resource_id.casefold()]["name"] == "app"
    assert result.subscriptions["sub"]["name"] == "DEV"


def test_enrichment_preserves_duplicate_matches_for_normalization() -> None:
    resource_id = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Web/sites/app"
    source = AzureAdvisorEnrichmentSource(
        FakeMetadataSource(
            rows=(
                {"id": "SERVICE-A", "serviceRetirement": {"serviceId": "SERVICE-A"}},
                {"id": "service-a", "serviceRetirement": {"serviceId": "service-a"}},
            )
        ),
        FakeResourceGraphSource(
            resources=(
                {"resourceId": resource_id, "name": "app-1"},
                {"resourceId": resource_id, "name": "app-2"},
            ),
            subscriptions=(
                {"subscriptionId": "sub", "name": "DEV"},
                {"subscriptionId": "SUB", "name": "DEV-2"},
            ),
        ),
    )

    result = source.enrich(context(), (recommendation("service-a", resource_id),))

    assert isinstance(result.metadata["service-a"], tuple)
    assert len(result.metadata["service-a"]) == 2
    assert isinstance(result.resources[resource_id.casefold()], tuple)
    assert len(result.resources[resource_id.casefold()]) == 2
    assert isinstance(result.subscriptions["sub"], tuple)
    assert len(result.subscriptions["sub"]) == 2


@pytest.mark.parametrize("failure", ("metadata", "resource", "subscription"))
def test_enrichment_wraps_source_failures(failure: str) -> None:
    source = AzureAdvisorEnrichmentSource(
        FakeMetadataSource(error=RuntimeError("metadata failure") if failure == "metadata" else None),
        FakeResourceGraphSource(
            resource_error=RuntimeError("resource failure") if failure == "resource" else None,
            subscription_error=RuntimeError("subscription failure") if failure == "subscription" else None,
        ),
    )

    with pytest.raises(AdvisorEnrichmentError, match="source acquisition failed"):
        source.enrich(context(), (recommendation("service-a", "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Web/sites/app"),))
