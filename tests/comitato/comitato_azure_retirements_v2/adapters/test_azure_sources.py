from __future__ import annotations

from datetime import date, datetime, timezone

from src.comitato.comitato_azure_retirements_v2.adapters.advisor_api import AdvisorApiSource
from src.comitato.comitato_azure_retirements_v2.adapters.resource_graph_api import ResourceGraphApiSource
from src.comitato.comitato_azure_retirements_v2.adapters.resource_health_api import ResourceHealthApiSource
from src.comitato.comitato_azure_retirements_v2.adapters.subscription_api import SubscriptionApiSource
from src.comitato.comitato_azure_retirements_v2.adapters.arm_http import ArmPageEnvelope
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)


class Http:
    def __init__(self):
        self.list_calls = []
        self.post_calls = []

    def list_pages(self, url, **kwargs):
        self.list_calls.append((url, kwargs))
        if "Microsoft.Advisor/" in url:
            return (ArmPageEnvelope(url, ({"id": "/advisor/1", "properties": {"recommendationStatus": "New"}},)),)
        if "ResourceHealth" in url:
            return (ArmPageEnvelope(url, ({"id": "/health/1", "properties": {"status": "Active"}},)),)
        return (ArmPageEnvelope(url, ({"id": "sub-a", "displayName": "A"},)),)

    def post_json(self, url, payload):
        self.post_calls.append((url, payload))
        return {"data": [{"id": "/subscriptions/sub-a/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm"}]}


def context() -> RunContext:
    request = RunRequest(ReportSelector.ALL, ("sub-a",), date(2026, 7, 31))
    return RunContext(
        run_id="run-1",
        as_of_date=date(2026, 7, 31),
        created_at=datetime(2026, 7, 31, tzinfo=timezone.utc),
        request=request,
        scope=Scope(("sub-a",), mode="explicit"),
        catalog_identity=CatalogIdentity(1, "0" * 64),
        dependency_plan=DependencyPlan(("scope", "catalog", "advisor")),
    )


def test_advisor_source_preserves_recommendation_evidence_and_receipt() -> None:
    http = Http()
    acquisition = AdvisorApiSource(http).acquire(context())

    assert acquisition.receipt.source == "advisor"
    assert acquisition.receipt.api_version == "2025-01-01"
    assert acquisition.receipt.expected_subscriptions == 1
    assert acquisition.receipt.is_complete
    assert acquisition.records[0].payload["id"] == "/advisor/1"
    assert http.list_calls[0][1]["params"]["$filter"]


def test_service_health_source_uses_resource_health_endpoint() -> None:
    http = Http()
    acquisition = ResourceHealthApiSource(http).acquire(context())

    assert acquisition.receipt.source == "service-health"
    assert acquisition.records[0].payload["id"] == "/health/1"
    assert "Microsoft.ResourceHealth/events" in http.list_calls[0][0]


def test_resource_graph_source_posts_query_without_normalizing_rows() -> None:
    http = Http()
    result = ResourceGraphApiSource(http).lookup(context(), ("/resource/1",))

    assert result[0]["id"].endswith("/vm")
    assert http.post_calls[0][1]["subscriptions"] == ["sub-a"]
    assert "resources" in http.post_calls[0][1]["query"]


def test_subscription_source_preserves_explicit_scope_without_network_call() -> None:
    http = Http()
    scope = SubscriptionApiSource(http).resolve(context().request)

    assert scope.subscription_ids == ("sub-a",)
    assert scope.mode == "explicit"
    assert http.list_calls == []
