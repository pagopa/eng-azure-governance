from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

import pytest

from src.comitato.comitato_azure_retirements_v2.acquisition.model import (
    AcquisitionReceipt,
    SourceAcquisition,
)
from src.comitato.comitato_azure_retirements_v2.application import orchestration as orchestration_module
from src.comitato.comitato_azure_retirements_v2.application.orchestration import RetirementsApplication
from src.comitato.comitato_azure_retirements_v2.application.orchestration_errors import ApplicationError
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)
from src.comitato.comitato_azure_retirements_v2.domain.platforms import PlatformCatalogSnapshot
from src.comitato.comitato_azure_retirements_v2.publication.model import PublicationReceipt


SUBSCRIPTION_ID = "sub-a"
RESOURCE_ID = "/subscriptions/sub-a/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm-1"


def context() -> RunContext:
    return RunContext(
        run_id="run-health-evidence",
        as_of_date=date(2026, 7, 31),
        created_at=datetime(2026, 7, 31, tzinfo=timezone.utc),
        request=RunRequest(ReportSelector.SERVICE_HEALTH, (SUBSCRIPTION_ID,), date(2026, 7, 31)),
        scope=Scope((SUBSCRIPTION_ID,), mode="explicit"),
        catalog_identity=CatalogIdentity(1, "a" * 64),
        dependency_plan=DependencyPlan(("scope", "catalog", "service-health", "publication")),
    )


def acquisition() -> SourceAcquisition:
    return SourceAcquisition(
        receipt=AcquisitionReceipt("service-health", "2025-05-01", 1, 1, 1, 1, True),
        records=(
            {
                "id": "/subscriptions/sub-a/providers/Microsoft.ResourceHealth/events/event-1",
                "name": "track-1",
                "subscriptionId": SUBSCRIPTION_ID,
                "properties": {
                    "trackingId": "track-1",
                    "eventType": "HealthAdvisory",
                    "level": "Informational",
                    "status": "Active",
                    "title": "Title",
                    "summary": "Summary",
                    "description": "Description",
                    "impactedServices": [],
                    "impactedResources": [],
                },
            },
        ),
    )


@dataclass
class FakeResourceGraph:
    subscription_rows: tuple[dict[str, Any], ...] = (
        {"subscriptionId": SUBSCRIPTION_ID, "subscriptionName": "Live Subscription"},
    )
    service_health_rows: tuple[dict[str, Any], ...] = (
        {
            "id": "/subscriptions/sub-a/providers/Microsoft.ResourceHealth/events/track-1/impactedResources/1",
            "subscriptionId": SUBSCRIPTION_ID,
            "properties": {
                "targetResourceId": RESOURCE_ID,
                "targetResourceType": "Microsoft.Compute/virtualMachines",
                "targetRegion": "West Europe",
            },
        },
    )
    resource_rows: tuple[dict[str, Any], ...] = (
        {
            "id": RESOURCE_ID,
            "name": "vm-1",
            "type": "Microsoft.Compute/virtualMachines",
            "location": "westeurope",
            "resourceGroup": "rg",
            "subscriptionId": SUBSCRIPTION_ID,
        },
    )
    fail_on: str = ""
    calls: list[str] | None = None

    def __post_init__(self) -> None:
        self.calls = []

    def _record(self, name: str) -> None:
        self.calls.append(name)
        if self.fail_on == name:
            raise RuntimeError(f"{name} query failed")

    def lookup_subscription_inventory(self, context: RunContext) -> tuple[dict[str, Any], ...]:
        self._record("subscription_inventory")
        return self.subscription_rows

    def lookup_service_health_resources(self, context: RunContext) -> tuple[dict[str, Any], ...]:
        self._record("service_health_resources")
        return self.service_health_rows

    def lookup_resources(self, context: RunContext, resource_ids: tuple[str, ...]) -> tuple[dict[str, Any], ...]:
        self._record("resources")
        return self.resource_rows


@dataclass(frozen=True)
class FakeCatalog:
    name: str = "Catalog Subscription"
    identity: CatalogIdentity = CatalogIdentity(1, "b" * 64)
    subscription_ids: tuple[str, ...] = (SUBSCRIPTION_ID,)

    def lookup(self, subscription_id: str) -> tuple[str, str] | None:
        return "pagoPA", self.name


def application(resource_graph_source: FakeResourceGraph, catalog: FakeCatalog) -> RetirementsApplication:
    return RetirementsApplication(
        scope_source=object(),
        catalog_source=object(),
        advisor_source=object(),
        service_health_source=object(),
        publication_store=object(),
        clock=object(),
        run_id_factory=object(),
        resource_graph_source=resource_graph_source,
    )


def test_collect_service_health_evidence_prefers_resource_graph_inventory() -> None:
    graph = FakeResourceGraph()
    evidence = application(graph, FakeCatalog())._collect_service_health_evidence(
        context(), acquisition(), FakeCatalog()
    )

    assert evidence.subscription_inventory["sub-a"]["name"] == "Live Subscription"
    assert evidence.subscription_name_sources["sub-a"] == "resource_graph_inventory"
    assert evidence.resource_associations[("track-1", "sub-a")][0]["resourceId"].endswith("/vm-1")
    normalized_resource_id = RESOURCE_ID.casefold()
    assert evidence.resource_inventory[normalized_resource_id]["name"] == "vm-1"
    assert graph.calls == ["subscription_inventory", "service_health_resources", "resources"]


def test_collect_service_health_evidence_falls_back_to_platform_catalog() -> None:
    graph = FakeResourceGraph(subscription_rows=(), service_health_rows=(), resource_rows=())
    catalog = FakeCatalog(name="UAT-pagoPA")
    evidence = application(graph, catalog)._collect_service_health_evidence(
        context(), acquisition(), catalog
    )

    assert evidence.subscription_inventory["sub-a"]["name"] == "UAT-pagoPA"
    assert evidence.subscription_name_sources["sub-a"] == "platform_catalog"


def test_collect_service_health_evidence_does_not_turn_query_failure_into_not_published() -> None:
    graph = FakeResourceGraph(fail_on="service_health_resources")

    with pytest.raises(ApplicationError, match="supplemental evidence acquisition failed"):
        application(graph, FakeCatalog())._collect_service_health_evidence(
            context(), acquisition(), FakeCatalog()
        )


@dataclass(frozen=True)
class FakeScopeSource:
    def resolve(self, request: RunRequest, *, run_id: str = "") -> Scope:
        return Scope((SUBSCRIPTION_ID,), mode="explicit")


@dataclass(frozen=True)
class FakeCatalogSource:
    catalog: FakeCatalog

    def load(self) -> FakeCatalog:
        return self.catalog


@dataclass(frozen=True)
class FakeServiceHealthSource:
    def acquire(self, context: RunContext) -> SourceAcquisition:
        return acquisition()


class FakeClock:
    def now(self) -> datetime:
        return datetime(2026, 7, 31, tzinfo=timezone.utc)


class FakeRunIdFactory:
    def new_id(self) -> str:
        return "run-health-evidence"


class FakePublicationStore:
    def publish(self, candidate) -> PublicationReceipt:
        return PublicationReceipt("generation", "2026/07")


def test_application_passes_collected_evidence_to_service_health_report(monkeypatch) -> None:
    graph = FakeResourceGraph()
    catalog = FakeCatalog()
    captured: list[object] = []
    original_prepare = orchestration_module.prepare_service_health_report

    def capture(acquired, run_context, supplemental):
        captured.append(supplemental)
        return original_prepare(acquired, run_context, supplemental)

    monkeypatch.setattr(orchestration_module, "prepare_service_health_report", capture)
    app = RetirementsApplication(
        scope_source=FakeScopeSource(),
        catalog_source=FakeCatalogSource(catalog),
        advisor_source=object(),
        service_health_source=FakeServiceHealthSource(),
        publication_store=FakePublicationStore(),
        clock=FakeClock(),
        run_id_factory=FakeRunIdFactory(),
        resource_graph_source=graph,
    )

    app.run(RunRequest(ReportSelector.SERVICE_HEALTH, (SUBSCRIPTION_ID,), date(2026, 7, 31)))

    assert len(captured) == 1
    evidence = captured[0]
    assert evidence.subscription_name_sources["sub-a"] == "resource_graph_inventory"
